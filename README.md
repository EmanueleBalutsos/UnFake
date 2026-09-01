# UNFAKE

**UNFAKE** is an innovative, machine learning and AI powered web application designed to combat misinformation, polarization, and echo chambers. Unlike traditional platforms that evaluate the overall reliability of a news outlet, UNFAKE performs a comparative, headline-level analysis, showing exactly how different media frame the same event. 

Bypassing the historical reputation of individual newspapers, the infrastructure analyzes the language used through a complex pipeline that processes data retrieved from over 80,000 global journalistic sources.

### Key Features

Our engine analyzes headlines across **7 key dimensions**:
* **Bias Detection:** 13 types of bias (e.g., political, gender, sensationalism).
* **Agency Analysis:** Identifies actors (active, passive, mentioned).
* **Generic Framing:** 5 types (conflict, thematic, episodic, etc.).
* **Evaluative Focus:** 13 perspectives (economic, legal, moral).
* **Intent Detection:** 5 editorial intents (informative, investigative, etc.).
* **Tone Intensity:** Language intensity evaluation on a 1-5 scale.
* **Emotion Detection:** Identification of the 2 main emotions among 28 categories.

### Technology Stack

* **Backend:** Python 3.12, Flask 3.1.1 (Async/await architecture).
* **AI & NLP:** Google Gemini 3.1 Flash-Lite (configurable with Deepseek), Sentence Transformers, RoBERTa (GoEmotions).
* **Data Sources:** NewsAPI, GNews API.
* **Database & Analytics:** Firebase Firestore, real-time feedback system.
* **Frontend & UI:** HTML, CSS, JavaScript (Interactive analytics dashboard).

---

## Environment Setup

**Prerequisite:** Make sure you have *Python 3.12.3* or higher installed.

### 1. Creating and Activating the Virtual Environment

**On Windows:**
```bash
python -m venv .venv
# Using PowerShell:
.\.venv\Scripts\Activate.ps1
# Using CMD:
.\.venv\Scripts\activate.bat
```
**On Linux / MacOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```
VSCode Users: After activating the environment in the terminal, ensure you select the correct interpreter via the Command Palette (Ctrl + Shift + P → Python: Select Interpreter → .venv). Otherwise, VSCode may run the global Python installation.

### 2. Managing Dependencies
Once the virtual environment is activated, upgrade pip and install the requirements:
```bash
# Windows:
python -m pip install --upgrade pip
# Linux / MacOS:
pip install -r requirements.txt
```
Note: Run pip install -r requirements.txt every time the file is updated. If you install new dependencies, remember to run pip freeze > requirements.txt to update the file.

---

## Configuration

Environment Variables (.env)

Create a .env file at the base of the project folder. This file should never be committed to the remote repository.

Add the following environment variables required to run the code:

### Get your API key at: [https://newsapi.org/](https://newsapi.org/)
```bash
NEWSAPI_KEY=your_newsapi_key
```
### Get your API key at: [https://gnews.io/](https://gnews.io/)
```bash
GNEWS_KEY=your_gnews_key
```
### Get your API key at: [https://aistudio.google.com/api-keys](https://aistudio.google.com/api-keys)
```bash
GEMINI_API_KEY=your_gemini_api_key
```
### AI Models Configuration (config.yaml)

The models used for AI-based tasks at runtime can be easily specified by changing the config.yaml file. Currently, Gemini and Deepseek are available. The tool is designed to be modular for future implementations.

### Firebase Database (firebase-credentials.json)

The backend requires a private key to securely and programmatically interact with the Firebase database.

   1. Log in to the Firebase Console.

   2. Select your "UNFAKE" project.

   3. Go to Project settings (gear icon) → Service accounts.

   4. Click Generate new private key.

   5. Rename the downloaded file to firebase-credentials.json.

   6. Place the file in the base folder of the project (at the same level as app.py and .env).

   #### IMPORTANT SECURITY NOTE: The firebase-credentials.json file grants full access to your database. Never commit this file to the Git repository.

---

## Launch
To start the local web server, run:
```bash
python app.py
```
For debugging purposes or to display the real-time output of the query expansion, retrieval, and framing analysis pipeline in the terminal, use the optional verbose argument:
```bash
python app.py --verbose
```
