from transformers import pipeline

from headline_analyst.data import Article, Analysis, Emotion, EmotionsEnum
from headline_analyst.analyzer.factory import create_framing_analyzer

def analyze_emotions(model_config: dict, articles: list[Article], analyses: list[Analysis]):
    """
    Analyze the emotions expressed in each headlines using a pre-trained model
    fine-tuned on the GoEmotions dataset, which classifies text into 28 emotion categories + neutral.
    Updates the main identified Emotion object (label + score) for each headline Analysis object.
    """

    model_name = model_config["model"]
    classifier = pipeline("text-classification", model=model_name, top_k=None)

    headlines = [a.title for a in articles]
    model_outputs = classifier(headlines)

    for a in analyses:
        output = model_outputs[a.headline_index]
        top_emotions = []
        for i in range(min(2, len(output))):
            label_str = output[i]["label"].upper()
            score = output[i]["score"]
            top_emotions.append(Emotion(label=EmotionsEnum[label_str], score=score))

        a.emotions = top_emotions

async def llm_framing_analysis(analyzer_config: dict, articles: list[Article]) -> list[Analysis]:
    """
    Use an LLM to perform a framing analysis on the given articles' headlines. 
    Bathces articles for efficiency.
    """
    llm_analyzer = create_framing_analyzer(analyzer_config)

    async with llm_analyzer:
        analyses = await llm_analyzer.annotate_headline(articles)

    return analyses
