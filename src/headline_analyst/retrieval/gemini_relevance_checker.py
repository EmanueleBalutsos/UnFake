import httpx

from .llm_relevance_checker import LLMArticleRelevanceChecker, PROMPT
from headline_analyst.data import Article

class GeminiArticleRelevanceChecker(LLMArticleRelevanceChecker):
    """Free Gemini cloud LLM for relevance checking if retrieved article matches queried event (1500 req/day free tier)"""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def _check_batch(self, articles: list[Article], event: str, batch_size: int = 20) -> list[bool]:
        # Pass parameters into the prompt template
        prompt = self._build_prompt(articles, event)
        
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

        print(response.json())
        raw = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        return self._parse_response(raw, expected_length=len(articles))