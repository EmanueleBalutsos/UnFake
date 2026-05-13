from transformers import pipeline

from headline_analyst.data import Article, Analysis, Emotion
from headline_analyst.analyzer.factory import create_framing_analyzer

def analyze_emotions(model_config: dict, articles: list[Article]) -> list[list[Emotion]]:
    """
    Analyze the emotions expressed in each headlines using a pre-trained model
    fine-tuned on the GoEmotions dataset, which classifies text into 28 emotion categories + neutral.
    Returns the top-3 Emotion objects (label + score) for each headline.
    """

    model_name = model_config["model"]
    classifier = pipeline("text-classification", model=model_name, top_k=None)

    headlines = [a.title for a in articles]
    model_outputs = classifier(headlines)

    return [
        [Emotion(label=e["label"], score=e["score"]) for e in output[:3]]
        for output in model_outputs
    ]


async def llm_framing_analysis(analyzer_config: dict, articles: list[Article]) -> list[Analysis]:
    """
    Use an LLM to perform a framing analysis on the given articles' headlines. 
    Bathces articles for efficiency.
    """
    llm_analyzer = create_framing_analyzer(analyzer_config)

    async with llm_analyzer:
        analyses = await llm_analyzer.annotate_headline(articles)

    return analyses