import httpx

from .query_generator import QueryGenerator, EXPANSION_PROMPT

class GeminiQueryGenerator(QueryGenerator):
    """Free Gemini cloud LLM for query expansion (1500 req/day free tier)"""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def generate_queries(self, event: str, num_queries: int = 10) -> list[str]:
        # Pass parameters into the prompt template
        prompt = EXPANSION_PROMPT.format(event=event, num_queries=num_queries)
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

        json_req = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }

        response = httpx.post(url, json=json_req)
        response.raise_for_status()
        raw = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        return self.parse(raw)
