import os
import sys
import asyncio

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from huggingface_hub import login

# ---------------------------------
# Setup Percorsi
# ---------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Aggiunge ./src al path per importare i moduli interni
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

load_dotenv()

# Login to HuggingFace Hub if token provided (to make requests faster)
token = os.getenv("HF_TOKEN")
if(token):
    login(token=token)

# Import del progetto
from headline_analyst.retrieval_pipeline import gather_articles
from database.managment.firebase_manager import FirebaseManager

# ---------------------------------
# Configurazione Flask
# ---------------------------------
# Assumendo che il build di React vada in templates/dist
app = Flask(
    __name__,
    static_folder="templates/dist",      # Cartella dei file compilati (JS, CSS, immagini)
    static_url_path="/",                 # Serve i file dalla root
    template_folder="templates/dist"     # Dove si trova l'index.html finale
)

# Abilita CORS per lo sviluppo locale
CORS(app)

# ---------------------------------
# Inizializzazione Firebase
# ---------------------------------
FIREBASE_CERT_PATH = os.path.join(BASE_DIR, "firebase-credentials.json")
firebase_manager = None

try:
    if os.path.exists(FIREBASE_CERT_PATH):
        firebase_manager = FirebaseManager(FIREBASE_CERT_PATH)
        print("Firebase inizializzato correttamente.")
    else:
        print(f"ATTENZIONE: Credenziali Firebase non trovate in {FIREBASE_CERT_PATH}")
except Exception as e:
    print(f"Errore inizializzazione Firebase: {e}")

# ---------------------------------
# Helper per Asincronia
# ---------------------------------
def run_async(coro):
    """Esegue una coroutine in un loop sincrono."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

# ---------------------------------
# Endpoint API
# ---------------------------------

@app.route("/search", methods=["POST"])
def search():
    """Endpoint per la ricerca articoli usato da App.tsx."""
    try:
        data = request.get_json()
        if not data or "event" not in data:
            return jsonify({"error": "Evento mancante"}), 400

        event = data["event"].strip()
        if not event:
            return jsonify({"error": "Evento vuoto"}), 400

        # Esecuzione della pipeline di recupero
        articles = run_async(
            gather_articles(
                event=event,
                num_queries=10,
                page_size_per_query=5,
                embedding_threshold=0.4,
                use_query_expansion=True, # we could make a button to disable it on the UI perhaps ?
                use_clustering=False,
                use_llm_filter=True
            )
        )

        # Mappatura dei campi per il frontend React
        result = []
        for a in articles:
            result.append({
                "title": a.title,
                "source": a.source,
                "description": a.description or "",
                "url": a.url,
                "published_at": a.published_at.isoformat() if a.published_at else None,
                # I campi sentiment, actors e tone vengono gestiti come placeholder nel frontend
            })

        return jsonify({"articles": result})

    except Exception as e:
        print("ERRORE RICERCA:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/feedback", methods=["POST"])
def feedback():
    """Salva il feedback globale dell'utente su Firestore."""
    if firebase_manager is None:
        return jsonify({"error": "Database non disponibile"}), 503

    try:
        data = request.get_json()
        event = data.get("event")
        rating = data.get("rating")
        comment = data.get("comment", "")
        # Estraiamo la lingua, se non c'è mettiamo "en" di default
        language = data.get("language", "en")

        if not event or rating is None:
            return jsonify({"error": "Dati feedback incompleti"}), 400

        # Passiamo anche la lingua al manager
        firebase_manager.save_feedback(event, rating, comment, language)

        return jsonify({"status": "success"}), 201
    except Exception as e:
        print("FIREBASE ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

# ---------------------------------
# Catch-all Route per React
# ---------------------------------
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Gestisce il routing della Single Page Application."""
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        # Se la rotta non è un file statico o un'API, serve l'index.html di React
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
