import httpx

from .query_generator import QueryGenerator, EXPANSION_PROMPT
from headline_analyst.utils.requests import httpx_request_with_retries

class DeepseekQueryGenerator(QueryGenerator):
    """Deepseek cloud LLM for query expansion"""

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

    async def generate_queries(self, event: str, num_queries: int = 10) -> list[str]:
        if self.client is None:
            raise RuntimeError("Client not initialized. Use async with.")

        prompt = EXPANSION_PROMPT.format(event=event, num_queries=num_queries)

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
        return self.parse(raw)
