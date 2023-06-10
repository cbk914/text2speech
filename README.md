# text2speech
Script to interact with Google Cloud Text-to-Speech API. Conversion to SSML, export to WAV, MP3 and OGG and other cool functions.

# Installation and usage

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

Now, to use the program, navigate to the directory containing text2speech.py and run:

  `python text2speech.py`

The program will guide you through a series of prompts to configure language, gender of the voice, and to select the text file to convert to speech.
It will split the file by time marks in format '[00:00:00]', generating as many files as tags found, under corresponding directory.

# Disclaimer

This script is provided as is without any guarantees or warranty. In connection with the product, the author makes no warranties of any kind, either express or implied, including but not limited to warranties of merchantability, fitness for a particular purpose, of title, or of noninfringement of third party rights. Use of the product by a user is at the user’s risk. In no event will the author be liable to you for any loss of use, interruption of business, or any direct, indirect, special, incidental, or consequential damages of any kind (including lost profits) regardless of the form of action whether in contract, tort (including negligence), strict product liability or otherwise, even if the author has been advised of the possibility of such damages.
