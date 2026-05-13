from abc import ABC, abstractmethod
import json

EXPANSION_PROMPT = """
You are a research assistant that generates diverse phrase search queries to find articles covering a news event from multiple perspectives.

Given this described news event : "{event}"
Generate exactly {num_queries} short and distinct search queries to retrieve articles about this SAME event from different outlets.
Vary keywords (actors, locations, actions) with synonyms, related terms, and different angles of the story. 
Consider those queries will be used to do phrase search (retrieved documents either contain this exact sequence or not), or logical AND search between keywords,
so keep the queries concise (some may only have 2 keywords, up to 3 keywords MAXIMUM). Avoid queries that would pull in tangentially related but different events.

Return only a JSON array of strings. Example : ['query 1', 'query 2', 'query 3']
Return ONLY the JSON array, no other text.
"""

class QueryGenerator(ABC):
    """
    Abstract class to implement LLM models for query expansion.
    Concrete implementations must inherit from this class.
    """
    @abstractmethod
    async def generate_queries(self, event: str, num_queries: int = 10) -> list[str]:
        pass
    def parse(self, raw: str) -> list[str]:
        try:
            # Strip markdown code block markers if the model adds them, then parse JSON
            raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            return json.loads(raw)
        except json.JSONDecodeError:
            raise ValueError(f"Failed to parse query expansion JSON: {raw}")