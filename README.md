# text2speech
Script to interact with Google Cloud Text-to-Speech API. Conversion to SSML, export to WAV, MP3 and OGG and other cool functions.

# Installation

* Ensure Python 3.7 or later is installed on your machine. You can check your Python version using the command python --version in your terminal.
* Create a new virtual environment (optional, but recommended). You can do this with the following commands:

  `python -m venv env`
  
  `source env/bin/activate`
  
  On Windows use 
  
    `env\Scripts\activate`

* Install the required packages:

  `pip install -r requirements.txt`

* Save your Google Cloud Text-to-Speech API credentials JSON file to your project directory.
* Create a .env file in your project directory and set the GOOGLE_APPLICATION_CREDENTIALS variable to the path of your credentials JSON file:

  GOOGLE_APPLICATION_CREDENTIALS="path_to_your_credentials.json"


# Usage

Now, to use the program, navigate to the directory containing text2speech.py and run:

  `python text2speech.py`

The `text2speech.py` script is an interactive program that synthesizes speech from text using Google's Text-to-Speech API. When run, it will prompt you with several questions to determine the settings for the synthesized speech. These settings include:

-  **Language Code** : This is the language of the text you want to convert. You'll need to input this as a BCP-47 language tag (e.g., 'en-US' for American English, 'fr-FR' for French).


-  **SSML Gender** : This represents the gender of the voice used for the speech synthesis. You can choose from 'NEUTRAL', 'MALE', or 'FEMALE'.



After setting these configurations, the program will ask you to provide the path to a text file. This text file should contain the text you wish to convert into speech, structured in a specific way. The file should have time tags, represented in the format '[HH:MM:SS]' (hours, minutes, seconds), followed by a segment of text that you want to be spoken.

Here's an example of how the text file should look:


```txt
[00:01:00]
(Scene Transition)

"Text to be converted to speech"

[00:02:30]
(Another Scene Transition)

"More text to be converted to speech"
```
The script will process this file, splitting the text into segments based on these time tags. Each segment of text (found between the quotation marks) will be converted into a separate audio file.

So, in the provided example, two .mp3 files would be generated - one for each time tag and the corresponding text. The files will be named in a way that corresponds to the order of the segments and their respective time tags, like `audio_1_00:01:00.mp3` and `audio_2_00:02:30.mp3` .

These audio files can then be found in the same directory as your `text2speech.py` script.


# Disclaimer

This script is provided as is without any guarantees or warranty. In connection with the product, the author makes no warranties of any kind, either express or implied, including but not limited to warranties of merchantability, fitness for a particular purpose, of title, or of noninfringement of third party rights. Use of the product by a user is at the user’s risk. In no event will the author be liable to you for any loss of use, interruption of business, or any direct, indirect, special, incidental, or consequential damages of any kind (including lost profits) regardless of the form of action whether in contract, tort (including negligence), strict product liability or otherwise, even if the author has been advised of the possibility of such damages.
