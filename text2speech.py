#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: cbk914

import os
import re
import argparse
import glob
import pathlib
from typing import List

import nltk
import logging
from dotenv import load_dotenv, set_key
from google.cloud import texttospeech
from termcolor import colored

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

def get_google_credentials():
    """Prompt for Google Cloud credentials if not found."""
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path or not os.path.isfile(credentials_path):
        logging.error("Google Cloud credentials file path not found.")
        while True:
            credentials_path = input(colored("Please enter the path to your Google Cloud credentials file: ", "blue"))
            if os.path.isfile(credentials_path):
                set_key(".env", "GOOGLE_APPLICATION_CREDENTIALS", credentials_path)
                break
            else:
                logging.error("Invalid file path. Please try again.")
    return credentials_path

def initialize_tts_client(credentials_path):
    """Initialize the Text-to-Speech client."""
    try:
        client = texttospeech.TextToSpeechClient.from_service_account_json(credentials_path)
        return client
    except Exception as e:
        logging.error(f"Failed to initialize Text-to-Speech client: {e}")
        raise

def get_files():
    """Prompt the user to enter the path to input files."""
    while True:
        file_path_input = input(colored("Enter the path to the input file (use wildcard * for multiple files): ", "blue"))
        file_paths = glob.glob(file_path_input)
        if file_paths:
            return file_paths
        else:
            logging.error("No files found. Please try again.")

def list_voices(client) -> List:
    """List available voices."""
    try:
        voices = client.list_voices().voices
        return voices
    except Exception as e:
        logging.error(f"Failed to list voices: {e}")
        raise

def filter_voices_by_language(voices, language_code):
    """Filter voices by language code."""
    return [voice for voice in voices if language_code in voice.language_codes]

def print_voices(voices):
    """Print available voices."""
    voice_dict = {i + 1: voice for i, voice in enumerate(voices)}
    for num, voice in voice_dict.items():
        print(colored(f"{num}. Name: {voice.name}, Gender: {voice.ssml_gender.name}, Natural Sample Rate Hertz: {voice.natural_sample_rate_hertz}", "green"))
    return voice_dict

def get_text_and_voice(client) -> tuple:
    """Prompt the user for language and voice selection."""
    default_language_code = os.getenv('LANGUAGE_CODE', 'en-US')
    language_code = input(colored(f"Enter the language code (default: {default_language_code}): ", "blue")) or default_language_code
    set_key('.env', 'LANGUAGE_CODE', language_code)

    voices = list_voices(client)
    filtered_voices = filter_voices_by_language(voices, language_code)
    print(colored(f"Available voices for language {language_code}:", "green"))
    voice_dict = print_voices(filtered_voices)

    default_voice_name = os.getenv('VOICE_NAME', list(voice_dict.values())[0].name)

    while True:
        voice_input = input(colored(f"Enter the number or name of the voice you want to use (default: {default_voice_name}): ", "blue")) or default_voice_name
        try:
            if voice_input.isdigit():
                voice_name = voice_dict[int(voice_input)].name
                ssml_gender = voice_dict[int(voice_input)].ssml_gender.name
            else:
                voice_name = voice_input
                ssml_gender = next((v.ssml_gender.name for v in voice_dict.values() if v.name == voice_input), None)
            if ssml_gender is None:
                raise KeyError()
            break
        except KeyError:
            logging.error("Invalid selection. Please try again.")

    set_key('.env', 'VOICE_NAME', voice_name)
    set_key('.env', 'SSML_GENDER', ssml_gender)

    return language_code, texttospeech.SsmlVoiceGender[ssml_gender], voice_name

def process_file_input(path: str, max_length: int = 5000) -> List[str]:
    """Process input file and split text into manageable chunks."""
    try:
        with open(path, "r") as f:
            content = f.read()

        segments = re.split(r'(\[\d{2}:\d{2}:\d{2}\])', content)
        text_chunks = []

        for segment in segments:
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
    except Exception as e:
        logging.error(f"Failed to process file input: {e}")
        raise

def synthesize_speech(text_chunks: List[str], language_code: str, ssml_gender: str, name: str, filename: str, output_format: str, client) -> None:
    """Synthesize speech from text chunks."""
    try:
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
    except Exception as e:
        logging.error(f"Failed to synthesize speech: {e}")
        raise

def get_output_format():
    """Prompt the user for output format selection."""
    default_format = os.getenv('OUTPUT_FORMAT', 'MP3')
    while True:
        format_option = input(colored(f"Enter the audio output format (MP3, WAV, OGG, default: {default_format}): ", "blue")).upper() or default_format
        if format_option in ['MP3', 'WAV', 'OGG']:
            set_key('.env', 'OUTPUT_FORMAT', format_option)
            return format_option
        else:
            logging.error("Invalid selection. Please try again.")

def main():
    try:
        # Initialize the Text-to-Speech client
        credentials_path = get_google_credentials()
        client = initialize_tts_client(credentials_path)

        # Get language and voice settings from user
        language_code, ssml_gender, voice_name = get_text_and_voice(client)
        output_format = get_output_format()

        # Get the list of files to process
        file_paths = get_files()
        for file_path in file_paths:
            text_chunks = process_file_input(file_path)
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            synthesize_speech(text_chunks, language_code, ssml_gender, voice_name, file_name, output_format, client)

        logging.info("Speech synthesis completed, check the created audio files.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    # Make sure to download the punkt tokenizer
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    main()
