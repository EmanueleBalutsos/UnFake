# PM-unbubble

# Setup the environment

*Python version : 3.12.3*

Project structure should look like this :

```
.
├── README.md
├── app.py
├── .env
├── .gitignore
├── config.yaml
├── firebase-credentials.json
├── requirements.txt
├── src
│   ├── database
│       └──...
│   └── headline_analyst
│       └──...
└── templates
    └── index.html
```

The virtual environment folder should **not** be committed to the Git repo. If dependencies are added, please update the `requirements.txt`.

The `.env` files containing API keys should **not** be committed to the Git repo. Make it is listed in the `.gitignore`.



## Clone repo

```
git clone https://github.com/EmanueleBalutsos/PM-unbubble.git
```

## Create virtual environment
Navigate to the base of the `PM-unbubble` repository.

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

## Environment variables
The `.env` file should be located at the base of the `PM-unbubble` folder, and it contains all the API tokens necessary for API dependencies. **It should never be committed to the remote repository.**

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

### `firebase-credentials.json`

This file is the private key for the firebase database where the satisfaction/neutrality poll answers are stored.
