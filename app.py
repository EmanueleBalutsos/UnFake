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
