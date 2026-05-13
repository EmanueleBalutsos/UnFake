from .llm_relevance_checker import LLMArticleRelevanceChecker
from .gemini_relevance_checker import GeminiArticleRelevanceChecker
from .deepseek_relevance_checker import DeepseekArticleRelevanceChecker

def create_relevance_checker(relevance_checker_config: dict) -> LLMArticleRelevanceChecker:
    """Factory function to create a LLMArticleRelevanceChecker based on config settings."""

    provider_name = relevance_checker_config["provider"]
    url = relevance_checker_config.get("url")
    api_key = relevance_checker_config["api_key"]

    if provider_name == "gemini":
        model = relevance_checker_config.get("model", "gemini-3.1-flash-lite-preview")
        url = url if url else f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        return GeminiArticleRelevanceChecker(api_key=api_key, model=model, url=url)
    elif provider_name == "deepseek":
        model = relevance_checker_config.get("model", "deepseek-v4-flash")
        url = url if url else "https://api.deepseek.com/chat/completions"
        return DeepseekArticleRelevanceChecker(api_key=api_key, model=model, url=url)
    # add other providers here as needed in elif branches, maybe a local llm option in the future ?
    else:
        raise ValueError(f"Unknown provider: {provider_name}")