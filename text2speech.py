import os
import re
from dotenv import load_dotenv, set_key
from google.cloud import texttospeech
from termcolor import colored
from typing import List
import pathlib
import glob
import nltk

load_dotenv()

GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if GOOGLE_APPLICATION_CREDENTIALS is None or not os.path.isfile(GOOGLE_APPLICATION_CREDENTIALS):
    print(colored("Google Cloud credentials file path not found.", "red"))
    while True:
        GOOGLE_APPLICATION_CREDENTIALS = input(colored("Please enter the path to your Google Cloud credentials file: ", "blue"))
        if os.path.isfile(GOOGLE_APPLICATION_CREDENTIALS):
            break
        else:
            print(colored("Invalid file path. Please try again.", "red"))
    set_key(".env", "GOOGLE_APPLICATION_CREDENTIALS", GOOGLE_APPLICATION_CREDENTIALS)

client = texttospeech.TextToSpeechClient.from_service_account_json(GOOGLE_APPLICATION_CREDENTIALS)

def get_files():
    while True:
        file_path_input = input(colored("Enter the path to the input file (use wildcard * for multiple files): ", "blue"))
        file_paths = glob.glob(file_path_input)  # Handle wildcards in file paths
        if file_paths:
            return file_paths
        else:
            print(colored("No files found. Please try again.", "red"))

def list_voices() -> None:
    voices = client.list_voices().voices
    return voices

def filter_voices_by_language(voices, language_code):
    filtered_voices = [voice for voice in voices if language_code in voice.language_codes]
    return filtered_voices

def print_voices(voices):
    voice_dict = {i + 1: voice for i, voice in enumerate(voices)}
    for num, voice in voice_dict.items():
        print(colored(f"{num}. Name: {voice.name}, Gender: {voice.ssml_gender}, Natural Sample Rate Hertz: {voice.natural_sample_rate_hertz}", "green"))
    return voice_dict

def get_text_and_voice() -> tuple:
    default_language_code = os.getenv('LANGUAGE_CODE', 'en-US')
    language_code = input(colored(f"Enter the language code (default: {default_language_code}): ", "blue")) or default_language_code
    set_key('.env', 'LANGUAGE_CODE', language_code)

    voices = list_voices()
    filtered_voices = filter_voices_by_language(voices, language_code)
    print(colored(f"Available voices for language {language_code}:", "green"))
    voice_dict = print_voices(filtered_voices)

    default_voice_name = os.getenv('VOICE_NAME', list(voice_dict.values())[0].name)

    while True:
        voice_input = input(colored(f"Enter the number or name of the voice you want to use (default: {default_voice_name}): ", "blue")) or default_voice_name
        try:
            if voice_input.isdigit():
                voice_name = voice_dict[int(voice_input)].name
                ssml_gender = voice_dict[int(voice_input)].ssml_gender.name  # Use .name to get the name of the enum value
            else:
                voice_name = voice_input
                ssml_gender = next((v.ssml_gender.name for v in voice_dict.values() if v.name == voice_input), None) 
            if ssml_gender is None:
                raise KeyError()
            break
        except KeyError:
            print(colored("Invalid selection. Please try again.", "red"))
    
    set_key('.env', 'VOICE_NAME', voice_name)
    set_key('.env', 'SSML_GENDER', ssml_gender)

    return language_code, texttospeech.SsmlVoiceGender[ssml_gender], voice_name  # Convert back to enum for use with the API

def process_file_input(path: str, max_length: int = 5000) -> List[str]:
    # Open the file and read the content
    with open(path, "r") as f:
        content = f.read()

    # Split the text based on timestamps
    segments = re.split(r'(\[\d{2}:\d{2}:\d{2}\])', content)
    text_chunks = []

    # Process each segment
    for segment in segments:
        # Further split large segments into smaller chunks
        if len(segment) > max_length:
            sentences = nltk.tokenize.sent_tokenize(segment)
            chunk = ""
            for sentence in sentences:
                if len(chunk) + len(sentence) <= max_length:
                    chunk += " " + sentence
                else:
                    text_chunks.append(chunk.strip())
                    chunk = sentence
            if chunk:
                text_chunks.append(chunk)
        else:
            text_chunks.append(segment)
    
    return text_chunks

# Make sure to download the punkt tokenizer
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def synthesize_speech(text_chunks: List[str], language_code: str, ssml_gender: str, name: str, filename: str, output_format: str) -> None:
    output_dir = pathlib.Path(filename)
    output_dir.mkdir(exist_ok=True)

    for i, chunk in enumerate(text_chunks):
        input_text = texttospeech.SynthesisInput(text=chunk)
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code, ssml_gender=ssml_gender, name=name
        )
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding[output_format])
        response = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)

        with open(output_dir / f"{filename}_{i}.{output_format.lower()}", "wb") as out:
            out.write(response.audio_content)

def get_output_format():
    default_format = os.getenv('OUTPUT_FORMAT', 'MP3')
    while True:
        format_option = input(colored(f"Enter the audio output format (MP3, WAV, OGG, default: {default_format}): ", "blue")).upper() or default_format
        if format_option in ['MP3', 'WAV', 'OGG']:
            set_key('.env', 'OUTPUT_FORMAT', format_option)
            return format_option
        else:
            print(colored("Invalid selection. Please try again.", "red"))        

def main():
    try:
        language_code, ssml_gender, voice_name = get_text_and_voice()
        output_format = get_output_format()

        file_paths = get_files()
        for file_path in file_paths:
            text_chunks = process_file_input(file_path)
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            synthesize_speech(text_chunks, language_code, ssml_gender, voice_name, file_name, output_format)

        print(colored("Speech synthesis completed, check the created audio files.", "green"))
    except Exception as e:
        print(colored(f"An error occurred: {e}", "red"))

if __name__ == "__main__":
    main()
