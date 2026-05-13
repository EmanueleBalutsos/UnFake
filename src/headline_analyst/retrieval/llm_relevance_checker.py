from abc import ABC, abstractmethod

from headline_analyst.data import Article
import json

PROMPT = """Event: {event}.
Below are news article headlines and descriptions. 
For each, respond with 'true' or 'false' : is this article specifically about the same event described above ? 
'true' = covers this event enough to consider relevant about this specific event.
'false' = tangentially related, but different event or not related at all.
Return ONLY a JSON array of booleans in order of the input articles, no other text. Example : [true, false, false, true]

Healines + descriptions:
{items}
"""

class LLMArticleRelevanceChecker(ABC):
    """
    Interface for LLM-based article relevance checkers to determine if retrieved articles are about the same event as the query.
    Subclasses implement _check_batch() for a specific LLM provider.
    """
    async def filter(self, articles: list[Article], event: str, batch_size: int=20) -> list[Article]:
        """Filter articles, returning only those relevant to the queried event."""
        relevant = []

        for i in range(0, len(articles), batch_size):
            batch = articles[i:i+batch_size]
            flags = await self._check_batch(batch,event)
            relevant.extend(a for a, f in zip(batch, flags) if f)
        return relevant


    @abstractmethod
    async def _check_batch(self, articles: list[Article], event: str) -> list[bool]:
        """
        Given a batch of articles and an event description, return a list of booleans indicating :
        True if the article is about the event, False otherwise.
        Must preserve the order and length of the input list.
        """
        pass

    def _build_prompt(self, articles: list[Article], event: str) -> str:
        """
        Format the inputs in the prompt sent to the LLM model as such :
        [Source of Article] Headline - Description: description retrieved from article
        """
        items = "\n".join(
                f"{j+1}. [{a.source}] {a.title} - Description: {a.description}" for j, a in enumerate(articles)
            )
        return PROMPT.format(event=event, items=items)

    def _parse_response(self, raw: str, expected_length: int) -> list[bool]:
        # Remove potential markdown code block markers and parse JSON
        raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        flags = json.loads(raw)
        if len(flags) != expected_length:
            raise ValueError(f"LLM relevance checker returned {len(flags)} flags, expected {expected_length}. Response: {raw}")
        return [bool(f) for f in flags]