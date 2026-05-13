import httpx
from typing import List

from .framing_analyzer import FramingAnalyzer
from headline_analyst.utils.requests import httpx_request_with_retries
from headline_analyst.data import *

class DeepseekFramingAnalyzer(FramingAnalyzer):
    """Deepseek cloud LLM for headline framing analysis"""

    def __init__(self, api_key: str, model: str, url: str):
        super().__init__(AnalysisResponse)
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

    async def annotate_headline(self, articles: list[Article]) -> List[Analysis]:
        if self.client is None:
            raise RuntimeError("Client not initialized. Use async with.")

        prompt = self._build_prompt(articles)

        json_req = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": "AnalysisResponse", "schema": self.schema},
            },
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
