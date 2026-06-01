from typing import List
import asyncio

from headline_analyst.utils.config_loader import load_config

from headline_analyst.data import Article, Analysis
from headline_analyst.analyzer import *

def print_analyses(analyses: List[Analysis], articles: List[Article]):
    for analysis in analyses:
        idx = analysis.headline_index
        article = articles[idx] if idx < len(articles) else None

        print(f"\n[{idx}] {article.source if article else f'Article {idx} not found'}")
        if article:
            print(f"    Headline : {article.title}")

        print(f"    Frame  : {analysis.frame.name}")
        print(f"    Genre  : {analysis.genre.name}")
        print(f"    Focus  : {', '.join(f.name for f in analysis.focus) or '—'}")
        print(f"    Tone   : {analysis.tone_intensity}/5")

        if analysis.biases:
            print(f"    Biases : {', '.join(f'{b.name} ({s}/3)' for b, s in analysis.biases.items())}")
        else:
            print(f"    Biases : none")

        if analysis.agencies:
            entities = ', '.join(f"{e.name} [{e.role.name}]" for e in analysis.agencies)
            print(f"    Entities: {entities}")

        if analysis.emotions:
            emotions_str = " / ".join([str(e.label.name) for e in analysis.emotions])
            print(f"    Emotions : {emotions_str}")

        print()

async def analyze_headlines(articles: List[Article], useEmotionClassifier: bool = True, verbose: bool = False) -> List[Analysis]:
    config = load_config()

    llm_config = config["llm_framing_analyzer"]
    emotions_config = config["hf_emotions_detector"]

    analyses = await llm_framing_analysis(llm_config, articles)
    if not analyses:
        if verbose: print("Analysis failed. LLM providers may be temporarily unavailable.")
        return []

    if verbose: print(f"{len(analyses)} analyses retrieved via LLM call. \n")

    if(useEmotionClassifier):
        analyze_emotions(emotions_config, articles, analyses)

    if verbose: print_analyses(analyses, articles)
    return analyses


# Test
if __name__ == "__main__":
    titles = ["Trump to give primetime address on Iran war as questions swirl over his next move",
            "Iran war: What’s happening on day 59 amid diplomatic push to end conflict?",
            "‘We are not your enemy’: Iran President Pezeshkian’s open letter to Americans after Trump speech",
            "Iran war: What does Tehran expect from fresh talks with US?",
            "Can Trump get a better Iran nuclear deal than Obama?",
            "No end in sight’ if Trump acts on threat to destroy Iran infrastructure",
            "US-Iran peace talks may take place in Islamabad but Trump says Vance may skip meet",
            "Iran war: US military to blockade Iranian ports",
            "ECB’s Lane says ‘too early to tell’ impact of Iran war",
            "US Senate rejects another war powers resolution to limit Trump on Iran",
            "Trump’s May 1 deadline: Can he continue war on Iran after that?",
            "Trump's rhetoric inappropriate for a US president, Albanese says",
            "‘Terrible for foreign policy’: Trump attacks Pope Leo after peace appeal"]


    articles = [Article(title=t, description="", source="none.com", query_origin="test") for t in titles]

    asyncio.run(analyze_headlines(articles, useEmotionClassifier=True))

