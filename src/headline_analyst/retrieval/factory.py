from .llm_relevance_checker import LLMArticleRelevanceChecker
from .gemini_relevance_checker import GeminiArticleRelevanceChecker

def create_relevance_checker(relevance_checker_config: dict) -> LLMArticleRelevanceChecker:
    """Factory function to create a LLMArticleRelevanceChecker based on config settings."""

    provider_name = relevance_checker_config["provider"]

    if provider_name == "gemini":
        return GeminiArticleRelevanceChecker(api_key=relevance_checker_config["api_key"], model=relevance_checker_config.get("model", "gemini-3.1-flash-lite-preview"))
    # add other providers here as needed in elif branches, maybe a local llm option in the future ?
    else:
        raise ValueError(f"Unknown provider: {provider_name}")