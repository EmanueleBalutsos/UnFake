from typing import List

from .framing_analyzer import FramingAnalyzer
from .gemini_framing_analyzer import GeminiFramingAnalyzer
from .deepseek_framing_analyzer import DeepseekFramingAnalyzer
from headline_analyst.data import Article

def create_framing_analyzer(analyzer_config: dict) -> FramingAnalyzer:
    """Factory function to create a FramingAnalyzer based on config settings."""

    provider_name = analyzer_config["provider"]
    url = analyzer_config["url"]
    api_key = analyzer_config["api_key"]

    if provider_name == "gemini":
        model = analyzer_config.get("model", "gemini-3.1-flash-lite-preview")
        url = url if url else f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        return GeminiFramingAnalyzer(api_key=api_key, model=model, url=url)
    elif provider_name == "deepseek":
        model = analyzer_config.get("model", "deepseek-v4-flash")
        url = url if url else "https://api.deepseek.com/chat/completions"
        return DeepseekFramingAnalyzer(api_key=api_key, model=model, url=url)
    # add other providers here as needed in elif branches, maybe a local llm option in the future ?
    else:
        raise ValueError(f"Unknown provider: {provider_name}")
    

async def annotate_headline(analyzer_config: dict, articles: List[Article]) -> list[str]:
    """Helper function to create a framing analyzer and generates an analysis for each article."""

    outputs = []
    framing_analyzer = create_framing_analyzer(analyzer_config)
    async with framing_analyzer:
        outputs = await framing_analyzer.annotate_headline(articles=articles)
    return outputs