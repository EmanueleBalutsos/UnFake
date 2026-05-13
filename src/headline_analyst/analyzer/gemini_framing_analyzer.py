import httpx
import datetime
from typing import List, Optional

from .framing_analyzer import FramingAnalyzer
from headline_analyst.utils.requests import httpx_request_with_retries
from headline_analyst.data import *

class GeminiFramingAnalyzer(FramingAnalyzer):
    """Free Gemini cloud LLM (1500 req/day free tier) for headline framing analysis"""

    def __init__(self, api_key: str, model: str, url: str):
        super().__init__(AnalysisResponse)
        self.api_key = api_key
        self.model = model
        self.client = None
        self.cache_id: Optional[str] = None
        self.cache_expiry: Optional[datetime.datetime] = None
        self.url = url

    async def __aenter__(self):
        self.client = httpx.AsyncClient()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.client.aclose()
        self.client = None

    async def annotate_headline(self, articles: list[Article]) -> List[Analysis]:
        if self.client is None:
            raise RuntimeError("Client not initialized. Use async with.")

        # Pass parameters into the prompt template
        prompt = self._build_prompt(articles)
        
        # JSON formatting requirements
        json_req = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "response_mime_type": "application/json",
                "response_schema": self.schema # from parent class
            }
        }

        response = await httpx_request_with_retries(
            method="POST",
            url=self.url,
            client=self.client,
            json=json_req,
            timeout=30.0,
            max_retries=3
        )
        
        raw = response.json()["candidates"][0]["content"]["parts"][0]["text"]

        return self._parse_response(raw, expected_length=len(articles))