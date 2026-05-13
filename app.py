import os
import sys
import asyncio

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from huggingface_hub import login

# ---------------------------------
# Setup Python path
# ---------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Adds ./src to the path to import internal modules
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

# ---------------------------------
# Load environment
# ---------------------------------
load_dotenv()

# Login to HuggingFace Hub if token provided (to make requests faster)
token = os.getenv("HF_TOKEN")
if(token):
    login(token=token)

# ---------------------------------
# Project imports
# ---------------------------------
from headline_analyst.retrieval_pipeline import gather_articles
from database.managment.firebase_manager import FirebaseManager

# ---------------------------------
# Firebase Initialization
# ---------------------------------
FIREBASE_CERT_PATH = os.path.join(BASE_DIR, "firebase-credentials.json")

try:
    if os.path.exists(FIREBASE_CERT_PATH):
        firebase_manager = FirebaseManager(FIREBASE_CERT_PATH)
        print("Firebase initialized successfully.")
    else:
        print(f"CRITICAL: Firebase credentials not found at {FIREBASE_CERT_PATH}")
        firebase_manager = None
except Exception as e:
    print(f"Firebase initialization error: {e}")
    firebase_manager = None

# ---------------------------------
# Flask app
# ---------------------------------
app = Flask(
    __name__,
    template_folder="templates"
)

@app.route("/")
def index():
    return render_template("index.html")

def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@app.route("/search", methods=["POST"])
def search():
    try:
        data = request.get_json()

        if not data or "event" not in data:
            return jsonify({"error": "Missing event"}), 400

        event = data["event"].strip()

        if not event:
            return jsonify({"error": "Empty event"}), 400

        articles = run_async(
            gather_articles(
                event=event,
                num_queries=10,
                page_size_per_query=5,
                embedding_threshold=0.4,
                use_clustering=False,
                use_llm_filter=True
            )
        )

        result = []
        for a in articles:
            result.append({
                "title": a.title,
                "source": a.source,
                "query_origin": a.query_origin,
                "url": a.url,
                "description": a.description or "",
                "published_at": a.published_at.isoformat() if a.published_at else None
            })

        return jsonify({"articles": result})

    except Exception as e:
        print("SEARCH ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/feedback", methods=["POST"])
def feedback():
    """Public endpoint to save user feedback to Firestore."""
    if firebase_manager is None:
        return jsonify({"error": "Database service unavailable"}), 503

    try:
        data = request.get_json()

        event = data.get("event")
        rating = data.get("rating")
        comment = data.get("comment", "")

        if not event or rating is None:
            return jsonify({"error": "Incomplete feedback data"}), 400

        # Delegate the saving process to the Manager
        firebase_manager.save_feedback(event, rating, comment)

        return jsonify({
            "status": "success",
            "message": "Feedback saved successfully"
        }), 201

    except Exception as e:
        print("FIREBASE ERROR:", str(e))
        return jsonify({"error": "Internal server error while saving feedback"}), 500

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
import os
import sys
import asyncio

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv


# ---------------------------------
# Setup Python path
# ---------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))


# ---------------------------------
# Load environment
# ---------------------------------

load_dotenv()


# ---------------------------------
# Project imports
# ---------------------------------

from headline_analyst.retrieval_pipeline import gather_articles


# ---------------------------------
# Flask app
# ---------------------------------

app = Flask(
    __name__,
    template_folder="templates"
)


@app.route("/")
def index():
    return render_template("index.html")


def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        return loop.run_until_complete(coro)

    finally:
        loop.close()


@app.route("/search", methods=["POST"])
def search():

    try:

        data = request.get_json()

        if not data or "event" not in data:
            return jsonify({
                "error": "Missing event"
            }), 400

        event = data["event"].strip()

        if not event:
            return jsonify({
                "error": "Empty event"
            }), 400


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


        result = []

        for a in articles:

            result.append({
                "title": a.title,
                "source": a.source,
                "query_origin": a.query_origin,
                "url": a.url,
                "description": a.description or "",
                "content": a.content or "",
                "published_at":
                    a.published_at.isoformat()
                    if a.published_at else None
            })


        return jsonify({
            "articles": result
        })


    except Exception as e:

        print("ERROR:", str(e))

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
