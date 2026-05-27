import os
import re
import sys
import asyncio
import argparse

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Argument to print pipeline steps details (queries, articles gathered, analysis...)
_parser = argparse.ArgumentParser(add_help=False)
_parser.add_argument("--verbose", 
                     action="store_true", 
                     default=False,
                     help="Print pipeline verbose output to terminal (generated queries, articles retrieved, analysis details...)")
_args, _ = _parser.parse_known_args()
VERBOSE = _args.verbose

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

load_dotenv()

try:
    from huggingface_hub import login
    token = os.getenv("HF_TOKEN")
    if token:
        login(token=token)
except Exception:
    pass

from headline_analyst.retrieval_pipeline import gather_articles
from database.managment.firebase_manager import FirebaseManager
from headline_analyst.analyzer_pipeline import analyze_headlines
from database.analysis.feedback_stats import generate_report

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static"
)

CORS(app)

FIREBASE_CERT_PATH = os.path.join(BASE_DIR, "firebase-credentials.json")
firebase_manager = None

if os.path.exists(FIREBASE_CERT_PATH):
    try:
        firebase_manager = FirebaseManager(FIREBASE_CERT_PATH)
        print("Firebase connected successfully.")
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
else:
    print(f"Firebase credentials not found in {FIREBASE_CERT_PATH}")


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analytics")
def analytics_page():
    return render_template("analytics.html")

@app.route("/about")
def about_page():
    return render_template("about.html")

def sanitize_query(raw: str) -> str:
    """Strip noisy characters, keeping only letters, digits, and spaces, so that the 
       raw query can also be appended to the list of generated queries."""
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", raw)
    return re.sub(r"\s+", " ", cleaned).strip()


@app.route("/search", methods=["GET", "POST"])
def search():
    """Gathers and analyzes articles based on the search query."""
    if request.method == "POST":
        data = request.get_json() or {}
        # Fetching 'event' instead of 'q' to match the frontend request
        event = sanitize_query(data.get("event", data.get("q", "")))
    else:
        event = sanitize_query(request.args.get("event", request.args.get("q", "")))

    if not event:
        return jsonify({"error": "Missing search parameter"}), 400

    try:
        articles = asyncio.run(gather_articles(
            event=event,
            num_queries=5,
            page_size_per_query=5,
            embedding_threshold=0.4,
            use_query_expansion=True,
            use_clustering=False,
            use_llm_filter=True,
            verbose=VERBOSE
        ))

        if not articles:
            return jsonify({"articles": []})

        analyses = asyncio.run(analyze_headlines(articles, useEmotionClassifier=True, verbose=VERBOSE))

        result = []
        for i, a in enumerate(articles):
            analysis = analyses[i] if i < len(analyses) else None

            frame_val = "OTHER" # generic frame of the headline among the 5 main types
            actors_val = [] # actors in the headline
            biases_val = {} # types of biases identified in the headline
            focuses_val = [] # focuses (category of the perspective) among economy, policy, etc...
            genre_val = "OTHER" # main genre of the headline among informative, editorial etc...
            sentiment_val = "NEUTRAL" # main emotion
            intensity_val = 3 # tone intensity score from 1 to 5

            if analysis:
                if hasattr(analysis, "frame") and analysis.frame:
                    frame_val = analysis.frame.name
                if hasattr(analysis, "agencies") and analysis.agencies:
                    actors_val = [{"name": e.name, "role": e.role.name} for e in analysis.agencies]
                if hasattr(analysis, "focus") and analysis.focus:
                    focuses_val = [f.name for f in analysis.focus]
                if hasattr(analysis, "genre") and analysis.genre:
                    genre_val = analysis.genre.name
                if hasattr(analysis, "tone_intensity"):
                    intensity_val = analysis.tone_intensity
                if hasattr(analysis, "main_emotion") and analysis.main_emotion:
                    sentiment_val = analysis.main_emotion.label.name
                if hasattr(analysis, "biases") and analysis.biases:
                    biases_val = {b.name: score for b, score in analysis.biases.items()} if analysis.biases else {}

                # has_biases = bool(hasattr(analysis, "biases") and analysis.biases)

                # if intensity_val >= 4 and has_biases:
                #     sentiment_val = "negative"
                # elif intensity_val <= 2 and not has_biases:
                #     sentiment_val = "positive"
                # elif tone_val.lower() == "conflict":
                #     sentiment_val = "negative"
                # else:
                #     sentiment_val = "neutral"

            result.append({
                "title":        a.title,
                "source":       a.source,
                "description":  a.description or "",
                "url":          a.url,
                "published_at": a.published_at.isoformat() if a.published_at else None,
                "sentiment":    sentiment_val,
                "frame":        frame_val,
                "tone_intensity": intensity_val,
                "actors":       actors_val,
                "biases":       biases_val,
                "focuses":        focuses_val,
                "genre":        genre_val
            })

        return jsonify({"articles": result})

    except Exception as e:
        print("SEARCH ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route("/feedback", methods=["POST"])
def feedback():
    """Saves user feedback to Firestore."""
    if firebase_manager is None:
        return jsonify({"error": "Database not available"}), 503

    try:
        data    = request.get_json()
        event   = data.get("event")
        rating  = data.get("rating")
        comment = data.get("comment", "")

        if not event or rating is None:
            return jsonify({"error": "Incomplete data"}), 400

        firebase_manager.save_feedback(event, rating, comment)
        return jsonify({"status": "success"}), 201

    except Exception as e:
        print("FEEDBACK ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route("/api/analytics-data")
def get_analytics_data():
    """Endpoint for the analytics dashboard."""
    if firebase_manager is None:
        print("DIAGNOSTIC: firebase_manager is None!")
        return jsonify({"error": "Database not available"}), 503

    try:
        raw_data = firebase_manager.get_all_feedbacks()
        report = generate_report(raw_data)

        if not report:
            return jsonify({
                "total": 0,
                "average_rating": 0,
                "topic_stats": [],
                "top_reviews": []
            })

        import pandas as pd
        df = pd.DataFrame(raw_data)

        topic_stats = report['by_topic'].reset_index().to_dict(orient="records")

        top_reviews = []
        if not df.empty and 'comment' in df.columns:
            mask = (df['rating'] >= 8) & (df['comment'].notna()) & (df['comment'].str.strip() != "")
            top_reviews = df[mask].sort_values(by='rating', ascending=False).head(10).to_dict(orient="records")

        return jsonify({
            "total": int(report['total']),
            "average_rating": round(float(report['average_rating']), 2),
            "topic_stats": topic_stats,
            "top_reviews": top_reviews
        })

    except Exception as e:
        print("ANALYTICS BACKEND ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
