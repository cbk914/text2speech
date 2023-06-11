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

# Note: How to get the API keyfile

* Go to the Google Cloud Console. Navigate to https://console.cloud.google.com/ in your web browser.
* Create a new project or select an existing one. In the Google Cloud Console, you will see a dropdown in the top bar next to the "Google Cloud Platform" logo. Click on it, then either create a new project by clicking on "NEW PROJECT" at the top right or select an existing one from the list.
* Enable the Text-to-Speech API for your project. Use the search bar at the top of the page to search for "Text-to-Speech API". On the API page, click on "ENABLE" to enable it for your project.
* Create a service account. Navigate to "IAM & Admin" > "Service Accounts" in the left-side menu. Click on "CREATE SERVICE ACCOUNT" at the top of the page.
* Set the service account details. Give your service account a name and description, then click "CREATE".
* Set the service account permissions. On the "Grant this service account access to project" page, click on "SELECT A ROLE" and choose "Cloud Text-to-Speech User" under the "Cloud Text-to-Speech" category. Then click "CONTINUE".
* Create a key for the service account. On the "Grant users access to this service account (optional)" page, click "CREATE KEY". Select "JSON" as the key type, then click "CREATE". This will automatically download a JSON key file for your service account.
* Save the key file. Store the JSON key file in a secure place and do not share it. You will use this file to authenticate your application to the Text-to-Speech API.
* Set the environment variable. Finally, you need to set an environment variable called GOOGLE_APPLICATION_CREDENTIALS to the path of your JSON key file. If you're using a Unix-like operating system, you can do this in the terminal:

  `export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/keyfile.json"`

Replace "/path/to/your/keyfile.json" with the actual path to your JSON key file. If you're using Windows, the command will be slightly different.

Remember, the service account key file acts as a password for your application to authenticate itself to Google Cloud, so treat it with the same level of care as you would any sensitive data.

# Note on the Punkt

The Punkt Sentence Tokenizer is a unsupervised machine learning algorithm that is used for sentence boundary detection. It divides a text into a list of sentence tokens. The algorithm is designed to learn what constitutes a sentence break from a corpus of text that it's trained on.

In this script, the Punkt Sentence Tokenizer is used in the split_text_into_chunks function to divide the input text into sentences. This is done so that each sentence can be processed individually when synthesizing the speech. This is especially useful when the text is too large to be processed all at once, as it allows the text to speech synthesis to be done in manageable chunks.

It's important to note that Punkt is language-dependent, which means it needs to be trained on text in the target language to work properly. The NLTK library provides pre-trained Punkt models for a number of languages, which can be loaded using the nltk.download('punkt') command, as the script does.

# Usage

To use the program, navigate to the directory containing text2speech.py and run:

`python text2speech.py -i INPUTFILE [-o OUTPUTDIR] [-f FORMAT] [-v VOICE] [--convert]`

where:

INPUTFILE is the path to the text file that you want to convert to speech.

OUTPUTDIR is the optional argument specifying the directory where the audio files should be saved. If not provided, files will be saved in the same directory as text2speech.py.

FORMAT is the optional argument specifying the format of the output audio files. It can be 'LINEAR16' (WAV), 'MP3', or 'OGG_OPUS'. If not provided, 'MP3' will be used.

VOICE is the optional argument specifying the voice to be used for the speech synthesis. It should be a valid voice name from Google's Text-to-Speech API. If not provided, the default voice for the detected language will be used.

--convert is an optional flag. If provided, the script will also convert the input text to Speech Synthesis Markup Language (SSML) and save it in a .ssml file in the same directory.

The text2speech.py script is an interactive program that synthesizes speech from text using Google's Text-to-Speech API.

The text file should contain the text you wish to convert into speech, structured in a specific way. The file should have time tags, represented in the format '[HH:MM:SS]' (hours, minutes, seconds), followed by a description, and the text that you want to be spoken.

```txt
  [timestamp]
  (description)

  "text"
```

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

So, in the provided example, two .mp3 files would be generated - one for each time tag and the corresponding text. The files will be named in a way that corresponds to the order of the segments and their respective time tags, like audio_1_00:01:00.mp3 and audio_2_00:02:30.mp3.

These audio files will be stored in the specified output directory, or if none is provided, in the same directory as your text2speech.py script.

# Note on voices

[Here](https://cloud.google.com/text-to-speech/docs/voices?hl=es-419) you can hear all available voices, in any language


# Disclaimer

This script is provided as is without any guarantees or warranty. In connection with the product, the author makes no warranties of any kind, either express or implied, including but not limited to warranties of merchantability, fitness for a particular purpose, of title, or of noninfringement of third party rights. Use of the product by a user is at the user’s risk. In no event will the author be liable to you for any loss of use, interruption of business, or any direct, indirect, special, incidental, or consequential damages of any kind (including lost profits) regardless of the form of action whether in contract, tort (including negligence), strict product liability or otherwise, even if the author has been advised of the possibility of such damages.
