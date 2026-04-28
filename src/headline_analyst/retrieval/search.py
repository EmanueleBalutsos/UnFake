import asyncio
from datetime import datetime
import httpx
from headline_analyst.data import Article
from headline_analyst.utils.requests import httpx_request_with_retries

TRUSTED_DOMAINS = [
    # Wire services
    "reuters.com", "apnews.com", "afp.com",

    # UK
    "bbc.co.uk", "bbc.com", "theguardian.com", "ft.com",
    "telegraph.co.uk", "independent.co.uk",

    # US
    "nytimes.com", "washingtonpost.com", "wsj.com",
    "cnn.com", "nbcnews.com", "abcnews.go.com",
    "cbsnews.com", "bloomberg.com",

    # International
    "aljazeera.com", "dw.com", "france24.com", "economist.com",

    # Canada
    "cbc.ca", "theglobeandmail.com",

    # Australia
    "abc.net.au", "smh.com.au",

    # India
    "thehindu.com", "indianexpress.com", "hindustantimes.com"
]

async def search_newsapi(query: str, api_key: str, page_size: int = 5) -> list[Article]:
    """
    Search for news articles related to the query using NewsAPI.
    We restrict to trusted domains and only search in title and description to increase relevance of results.
    Limitation : NewsAPI indexes articles from maximum 5 years ago.
    100 requests/day for free tier but also split in 50 per 12 hours.
    """
    # NewsAPI doesn't handle async requests natively, so we use httpx.AsyncClient to make the request asynchronously
    # instead of using NewsAPI's official python client which is synchronous.
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await httpx_request_with_retries(
            method="GET",
            url="https://newsapi.org/v2/everything",
            client=client, # reuse client
            params={
                "q": query,           # search query (does by default a boolean AND search between keywords)
                "language": "en",     # only English articles
                "sortBy": "relevancy", # sort by relevancy to the query
                "pageSize": min(page_size,100),    # approximately the number of results to return (max 100)
                "apiKey": api_key,
                "searchIn": "title,description", # only search in the title or description to increase relevance of results (not in content)
                "domains": ",".join(TRUSTED_DOMAINS) # restrict to trusted domains
            },
            max_retries=3,
            timeout=30.0)
        
        data = response.json()
    
    articles = []
    for a in data.get("articles", []):
        articles.append(Article(
            title=a.get("title", ""),
            url=a.get("url", ""),
            source=a.get("source", {}).get("name", ""),
            published_at=datetime.fromisoformat(a.get("publishedAt", "").replace("Z", "+00:00")),
            description=a.get("description", ""),
            query_origin=query,
            content=a.get("content", ""),
        ))
    return articles

async def search_gnews(query: str, api_key: str, page_size: int = 5) -> list[Article]:
    """
    Search for news articles related to the query using GNews.
    We restrict to trusted domains and only search in title and description to increase relevance of results.
    Can't restrict search though, no option for that in gnews API.
    We could filter results after retrieval,
    but that would be less efficient as it would require retrieving more results to then filter them, 
    and gnews free tier only allows 100 requests/day
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await httpx_request_with_retries(
            method="GET",
            url="https://gnews.io/api/v4/search",
            client=client, # reuse client
            params={
                "q": query,           # search query (does by default a boolean AND search between keywords)
                "lang": "en",           # only English articles
                "sortBy": "relevance", # sort by relevancy to the query
                "max": min(page_size,10),    # number of results to return (max 10 per requests for free tier)
                "apikey": api_key,
                "in": "title,description", # only search in the title or description to increase relevance of results (not in content)
            },
            max_retries=3,
            timeout=30.0)
        
        data = response.json()
    
    articles = []
    for a in data.get("articles", []):
        articles.append(Article(
            title=a.get("title", ""),
            url=a.get("url", ""),
            source=a.get("source", {}).get("name", ""),
            published_at=datetime.fromisoformat(a.get("publishedAt", "").replace("Z", "+00:00")),
            description=a.get("description", ""),
            query_origin=query,
            content=a.get("content", ""),
        ))
    return articles

# add other search functions for different APIs here as needed

# Add other API keys in params as needed when more news search APIs are added
async def multi_search(queries: list[str], newsapi_key: str, gnews_key: str, page_size: int = 10) -> list[Article]:
    """Search multiple queries in parallel (on multiple APIs if more are added) and aggregate results."""

    tasks = []
    for q in queries:
        # actually, instead of making a request for each query, 
        # we could also make a single request with all queries combined with OR operator if the API supports it, 
        # to save on number of API calls and rate limits. 
        # But for now we do one request per query for testing purposes and better control over which query retrieved which article
        tasks.append(search_newsapi(q, newsapi_key, page_size//2))
        tasks.append(search_gnews(q, gnews_key, page_size//2))
        # add other search functions here as needed in the future like gnews
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    articles = []

    for r in results:
        if isinstance(r, list):
            articles.extend(r)

    return articles

