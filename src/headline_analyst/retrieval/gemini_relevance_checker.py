import httpx

from headline_analyst.utils.requests import httpx_request_with_retries
from .llm_relevance_checker import LLMArticleRelevanceChecker
from headline_analyst.data import Article

class GeminiArticleRelevanceChecker(LLMArticleRelevanceChecker):
    """Free Gemini cloud LLM for relevance checking if retrieved article matches queried event (1500 req/day free tier)"""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.client = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.client.aclose()
        self.client = None

    async def _check_batch(self, articles: list[Article], event: str) -> list[bool]:
        if self.client is None:
            raise RuntimeError("Client not initialized. Use async with.")

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

        response = await httpx_request_with_retries(
            method="POST",
            url=url,
            client=self.client,
            json=json_req,
            timeout=30.0,
            max_retries=3)

        raw = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        return self._parse_response(raw, expected_length=len(articles))