from .query_generator import QueryGenerator
from .gemini_query_gen import GeminiQueryGenerator

def create_query_generator(query_gen_config: dict) -> QueryGenerator:
    """Factory function to create a QueryGenerator based on config settings."""

    provider_name = query_gen_config["provider"]

    if provider_name == "gemini":
        return GeminiQueryGenerator(api_key=query_gen_config["api_key"], model=query_gen_config.get("model", "gemini-3.1-flash-lite-preview"))
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