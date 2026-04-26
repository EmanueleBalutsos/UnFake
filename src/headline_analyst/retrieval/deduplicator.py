from urllib.parse import urlparse, urlencode, parse_qs
from headline_analyst.data import Article
import re # for regular expressions

def _normalize_url(url: str) -> str:
    """Normalize URLs by removing query parameters and fragments."""

    parsed = urlparse(url)

    # Rempove common tracking params
    tracking = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "ref", "source"}

    params = {k: v for k, v in parse_qs(parsed.query).items() if k not in tracking}
    normalized = parsed._replace(query=urlencode(params, doseq=True), fragment="")
    return normalized.geturl().rstrip("/")

def _normalize_title(title: str) -> str:
    """Normalize titles by lowercasing, removing punctuation, and extra whitespace."""
    title = title.lower()
    title = re.sub(r'[^\w\s]', '', title) # strips out punctuation and whitespaces
    return re.sub(r'\s+', ' ', title).strip() # removes trailing whitespace and collapses multiple spaces into one

def deduplicate_articles(articles: list[Article]) -> list[Article]:
    """
    Deduplicate articles based on normalized URLs and normalized titles. 
    This is a simple heuristic that can be improved with more advanced NLP techniques if needed.
    """
    # can improve this deduplicator with NLP as some articles basically are copies of each other from same source with slight word change
    
    seen_urls = set()
    seen_titles = set()
    unique = []

    for a in articles:
        norm_url = _normalize_url(a.url)
        norm_title = _normalize_title(a.title)

        if norm_url not in seen_urls and norm_title not in seen_titles:
            unique.append(a)
            seen_urls.add(norm_url)
            seen_titles.add(norm_title)
    return unique

