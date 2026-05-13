import httpx

from headline_analyst.utils.requests import httpx_request_with_retries
from .llm_relevance_checker import LLMArticleRelevanceChecker
from headline_analyst.data import Article

class DeepseekArticleRelevanceChecker(LLMArticleRelevanceChecker):
    """Deepseek cloud LLM for relevance checking if retrieved article matches queried event"""

    def __init__(self, api_key: str, model: str, url: str):
        self.api_key = api_key
        self.model = model
        self.client = None
        self.url = url

    async def __aenter__(self):
        self.client = httpx.AsyncClient(headers={"Authorization": f"Bearer {self.api_key}"})
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.client.aclose()
        self.client = None

    async def _check_batch(self, articles: list[Article], event: str) -> list[bool]:
        if self.client is None:
            raise RuntimeError("Client not initialized. Use async with.")

        prompt = self._build_prompt(articles, event)

        json_req = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
        }

        response = await httpx_request_with_retries(
            method="POST",
            url=self.url,
            client=self.client,
            json=json_req,
            timeout=30.0,
            max_retries=3,
        )

        raw = response.json()["choices"][0]["message"]["content"]
        return self._parse_response(raw, expected_length=len(articles))
