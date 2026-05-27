# UnFake

# Setup the environment

*Python version : 3.12.3*

### Windows

```
python -m venv .venv
```

Then, activate the virtual environment.

Through Powershell :
```
.\venv\Scripts\Activate.ps1
```

Through cmd :
```
.\venv\Scripts\activate.bat
```

### Linux/MacOS

```
python3 -m venv .venv
```
Then, activate the virtual environment.
```
source .venv/bin/activate
```

### VSCode
After having activated the virtual environment in the terminal, if using VSCode, also make sure to select the right interpreter in VSCode :

```
Ctrl + Shift + P → Python: Select Interpreter → .venv
```

Otherwise VS Code may run global Python and not the virtual environment.

## Managing dependencies

### Dependencies
After having activated the virtual environment, make sure to have `pip` installed.

Do this once after activation :

```
python -m pip install --upgrade pip
```

To install dependencies already used in the project :
```
pip install -r requirements.txt
```
**Run this command everytime `requirements.txt` gets updated with new dependencies to make sure to have the same dependencies as everyone else.**

### Updating requirements
If you installed new dependencies, update `requirements.txt` so everyone else can have the updated environment.

```
pip freeze > requirements.txt
```

## Environment variables & API keys
The `.env` file should be located at the base of the project's folder, and it contains all the API tokens necessary for API dependencies. **It should never be committed to the remote repository.**

To add environment variables in your own `.env` file :
```
KEY_NAME=value
```

The following environment variables are necessary to be set up to run the code :

### `NEWSAPI_KEY`

The API key for the NewsAPI Python library to fetch headline articles.

Inside `.env` file :
```
NEWSAPI_KEY=... (your api key for NewsAPI)
```

To get one, just create an account on : https://newsapi.org/

### `GNEWS_KEY`

The API key for the GNews API fetch headline articles with Google News.

Inside `.env` file :
```
GNEWS_KEY=... (your api key for GNews)
```

To get one, just create an account on : https://gnews.io/

### `GEMINI_API_KEY`

The API key for Google's Gemini LLM models.

Inside `.env` file :
```
GEMINI_API_KEY=... (your api key for Gemini)
```

To get one, connect to a google account and generate an API key on : https://aistudio.google.com/api-keys

## Config at run time

Models used at run time for the different AI-based tasks can be easily specified by only changing the `config.yaml` file.

*Note: Currently, Only Gemini & Deepseek are available. While this tool is planned to be modular, concrete implementations for other LLM providers are not yet made.*

## Firebase Configuration

For the project to work correctly, you need a credentials file for administrative access to the Firebase database.

### What is `firebase-credentials.json`?

This file is a private key in JSON format that authorizes the Python backend to securely and programmatically read and write poll data to Firebase.

### File Location

The `firebase-credentials.json` file must be placed in the **base folder** of the `UnFake` project, at the same level as:
- `.env`
- `requirements.txt`
- `config.yaml`

### How to Get the File (Step-by-Step Guide)

1. **Log in to Firebase Console**
   - Go to [https://console.firebase.google.com/](https://console.firebase.google.com/)
   - Sign in with your Google account

2. **Select your project**
   - Choose the Firebase project you're using for "UnFake"

3. **Open Project Settings**
   - Click the gear icon next to "Project Overview"
   - Select **"Project settings"**

4. **Go to the "Service accounts" tab**
   - In the horizontal menu at the top, click on **"Service accounts"**

5. **Generate a new private key**
   - In the "Firebase Admin SDK" section, click **"Generate new private key"**
   - In the dialog window, click **"Generate key"** to confirm

6. **Rename and place the file**
   - Your browser will download a file with a name similar to:  
     `your-project-id-firebase-adminsdk-xxxxx-xxxxxxxxxx.json`
   - **Rename** the file to: `firebase-credentials.json`
   - **Move** the renamed file to the base folder of the `UnFake` project

### ⚠️ Important – Security

> **This file must never be committed to the Git repository.**

The file contains a private key that would grant full access to your Firebase database.
