from .query_generator import QueryGenerator
from .gemini_query_gen import GeminiQueryGenerator
from .deepseek_query_gen import DeepseekQueryGenerator

def create_query_generator(query_gen_config: dict) -> QueryGenerator:
    """Factory function to create a QueryGenerator based on config settings."""

    provider_name = query_gen_config["provider"]
    url = query_gen_config.get("url")
    api_key = query_gen_config["api_key"]

    if provider_name == "gemini":
        model = query_gen_config.get("model", "gemini-3.1-flash-lite-preview")
        url = url if url else f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        return GeminiQueryGenerator(api_key=api_key, model=model, url=url)
    elif provider_name == "deepseek":
        model = query_gen_config.get("model", "deepseek-v4-flash")
        url = url if url else "https://api.deepseek.com/chat/completions"
        return DeepseekQueryGenerator(api_key=api_key, model=model, url=url)
    # add other providers here as needed in elif branches, maybe a local llm option in the future ?
    else:
        raise ValueError(f"Unknown provider: {provider_name}")
    

async def generate_queries(query_gen_config: dict, event: str, num_queries: int = 10) -> list[str]:
    """Helper function to create a query generator and generates queries for an event."""

    queries = []
    query_gen = create_query_generator(query_gen_config)
    async with query_gen:
        queries = await query_gen.generate_queries(event=event, num_queries=num_queries)
    return queries