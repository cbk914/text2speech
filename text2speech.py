import argparse
import json
import os
from datetime import datetime
from functools import partial
from typing import List
import re
import pathlib
from dotenv import load_dotenv, set_key
from google.cloud import texttospeech
from termcolor import colored
import glob
from langdetect import detect

load_dotenv()

def str_lower(s):
    return s.lower()

# variable to store the "all" choice
replace_all = None

parser = argparse.ArgumentParser(description='Convert text files to speech.')
parser.add_argument('-l', '--language', type=str, help='The language code.')
parser.add_argument('-v', '--voice', type=str, help='The name or number of the voice.')
parser.add_argument('-f', '--format', type=str_lower, choices=['mp3', 'wav', 'ogg'], default='mp3', help='The audio output format.')
parser.add_argument('-p', '--path', type=str, default='./', help='The path to the input file (use wildcard * for multiple files).')
parser.add_argument('-s', '--save', type=str, help='Save current settings to a profile.')
parser.add_argument('-r', '--load', type=str, help='Load settings from a profile.')
parser.add_argument('-c', '--convert', action='store_true', help='Convert text to SSML.')
args = parser.parse_args()

config = {}
if args.load:
    with open(args.load, 'r') as f:
        config = json.load(f)
    args.language = config.get('language', args.language)
    args.voice = config.get('voice', args.voice)
    args.format = config.get('format', args.format)
    args.path = config.get('path', args.path)

# Prompt the user for Google credentials if not found
def get_credentials():
    while True:
        path = input(colored("Please enter the path to your Google Cloud credentials file: ", "blue"))
        if os.path.isfile(path):
            return path
        print(colored("Invalid file path. Please try again.", "red"))

# Load Google credentials
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or get_credentials()
set_key(".env", "GOOGLE_APPLICATION_CREDENTIALS", GOOGLE_APPLICATION_CREDENTIALS)
client = texttospeech.TextToSpeechClient.from_service_account_json(GOOGLE_APPLICATION_CREDENTIALS)

# mapping between ISO 639-1 codes to BCP-47 codes.
iso_to_bcp = {
    'zh': 'zh-CN',  # Mandarin
    'es': 'es-ES',  # Spanish
    'en': 'en-US',  # English
    'hi': 'hi-IN',  # Hindi
    'bn': 'bn-IN',  # Bengali
    'pt': 'pt-BR',  # Portuguese (Brazilian variant)
    'ru': 'ru-RU',  # Russian
    'ja': 'ja-JP',  # Japanese
    'pa': 'pa-Guru-IN',  # Punjabi (Gurmukhi script, Indian variant)
    'mr': 'mr-IN'  # Marathi
    # add more language mappings here    
}

def prompt_for_file():
    while True:
        try:
            user_input = input("Please enter a file path or 'q' to quit: ")
        except UnicodeDecodeError:
            print("Invalid input. Please try again.")
            continue

        if user_input.lower() == 'q':
            exit(0)
        elif os.path.isfile(user_input):
            return [user_input]
        else:
            print(f"No file found for the path: {user_input}")

def list_voices() -> None:
    response = client.list_voices()
    for voice in response.voices:
        print(voice)

def get_voices(language_code):
    request = texttospeech.ListVoicesRequest(language_code=language_code)
    response = client.list_voices(request)
    return response.voices

def get_voice_choice(language_code):
    for i, v in enumerate(get_voices(language_code), 1):
        print(f"{i}. {v.name}")
        print(f"\tLanguage: {v.language_codes[0]}")
        print(f"\tGender: {texttospeech.SsmlVoiceGender(v.ssml_gender).name}")
    while True:
        user_input = input("Please enter a number or 'q' to quit: ")
        if user_input.lower() == 'q':
            exit(0)
        elif user_input.isdigit() and 0 < int(user_input) <= len(get_voices(language_code)):
            return get_voices(language_code)[int(user_input)-1].name

def get_language_code(text):
    if not text.strip():  # checking if the text is not empty
        return 'en-US'  # returning a default value when text is empty
    iso_code = detect(text)
    bcp_code = iso_to_bcp.get(iso_code, 'en-US')  # default to English if not found
    return bcp_code

def str_lower(s):
    return s.lower()

def process_timestamped_lines(lines):
    pattern = r'\[(\d{2}:\d{2}:\d{2})\]\n\((.*?)\)\n\n"(.*?)"'
    timestamped_lines = []
    # Join lines into a single string
    text = ''.join(lines)
    matches = re.findall(pattern, text, re.DOTALL)
    if matches:
        for timestamp, transition, line_text in matches:
            timestamped_lines.append((timestamp, line_text))
    return timestamped_lines

def process_file_input(file_path):
    with open(file_path, 'r') as file:
        file_content = file.read()
    return process_timestamped_lines(file_content)

def process_output(output, input_file, line_number, voice_name):
    date = datetime.today().strftime('%Y-%m-%d')
    file_name_without_ext = os.path.splitext(os.path.basename(input_file))[0]
    dir_name = file_name_without_ext  # directory name is same as input file name
    pathlib.Path(dir_name).mkdir(parents=True, exist_ok=True)  # create directory if it doesn't exist
    
    # Modify the file_name to include the voice_name
    file_name = file_name_without_ext + "_" + date + "_line_" + str(line_number) + "_" + voice_name.replace(" ","_") + "." + args.format
    file_path = os.path.join(dir_name, file_name)  # join the directory name with file name

    with open(file_path, 'wb') as out:
        out.write(output.audio_content)
    print(f"Audio content written to file {file_path}")

def synthesize_speech(text, language_code, voice_name, convert=False):
    if convert:
        input_text = texttospeech.SynthesisInput(ssml=text_to_ssml(text))
    else:
        input_text = texttospeech.SynthesisInput(text=text)
    voice_params = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=voice_name
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=getattr(texttospeech.AudioEncoding, args.format.upper())
    )
    response = client.synthesize_speech(input=input_text, voice=voice_params, audio_config=audio_config)
    return response

def create_audio_files(input_files):
    for file in input_files:
        input_text = process_file_input(file)
        if not input_text:  # checking if input_text is not empty
            print(f"No valid lines found in file: {file}")
            continue
        text_to_detect = ' '.join(line[1] for line in input_text[:10] if line[1].strip())  # skipping empty lines
        language_code = get_language_code(text_to_detect)
        voice_name = get_voice_choice(language_code) if args.voice is None else args.voice
        print(f"Processing file: {file}")
        for i, (timestamp, line) in enumerate(input_text):
            print(f"Processing line {i+1} of {len(input_text)}")
            response = synthesize_speech(line, language_code, voice_name, args.convert)
            process_output(response, file, i+1, voice_name)  # pass voice_name as an argument

def text_to_ssml(input_text):
    # Regular expression pattern
    pattern = r'\[(\d{2}:\d{2}:\d{2})\]\n\((.*?)\)\n\n"(.*?)"'
    
    # Match the pattern in the input_text
    matches = re.findall(pattern, input_text, re.DOTALL)
    
    ssml_lines = []

    for timestamp, transition, line_text in matches:
        # Wrap the timestamp in a <mark> tag
        mark = f"<mark name='{timestamp}'/>"
        
        # Wrap the transition in a <break> tag
        break_tag = f"<break strength='medium' time='{transition}'/>"
        
        # Add the line of dialogue
        line = f"<prosody rate='medium' pitch='medium'>{line_text}</prosody>"
        
        # Combine the mark, break, and line into a single SSML string
        ssml_line = mark + break_tag + line
        
        ssml_lines.append(ssml_line)
    
    # Combine all SSML lines into a single string, wrapped in <speak> tags
    ssml = "<speak>" + " ".join(ssml_lines) + "</speak>"
    
    return ssml

if __name__ == "__main__":
    input_files = glob.glob(args.path) if '*' in args.path else [args.path]
    if len(input_files) == 0 or not all(map(os.path.isfile, input_files)):
        input_files = prompt_for_file()
    create_audio_files(input_files)

    if args.save:
        config = {
            'language': args.language,
            'voice': args.voice,
            'format': args.format,
            'path': args.path
        }
        with open(args.save, 'w') as f:
            json.dump(config, f)
