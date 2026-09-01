import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
import email.utils
from typing import List

from ddgs import DDGS
from headline_analyst.data import Article

def fetch_from_google_news(query: str, lang: str = "it", country: str = "IT") -> List[Article]:
    """
    Interrogate Google news RSS
    """
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl={lang}-{country}&gl={country}&ceid={country}:{lang}"

    articles = []

    try:
        # Need to simulate a browser request so it doesn't get blocked'
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )

        with urllib.request.urlopen(req) as response:
            xml_data = response.read()

        root = ET.fromstring(xml_data)

        for item in root.findall('.//item'):
            title_raw = item.find('title').text if item.find('title') is not None else ""
            url_link = item.find('link').text if item.find('link') is not None else ""
            pub_date_raw = item.find('pubDate').text if item.find('pubDate') is not None else None
            description = item.find('description').text if item.find('description') is not None else ""

            source_tag = item.find('source')
            source_name = source_tag.text if source_tag is not None else "Google News"

            # Title polishing, remove append
            title = title_raw
            if f" - {source_name}" in title_raw:
                title = title_raw.rsplit(f" - {source_name}", 1)[0].strip()

            published_at = None
            if pub_date_raw:
                try:
                    tuple_date = email.utils.parsedate_tz(pub_date_raw)
                    if tuple_date:
                        timestamp = email.utils.mktime_tz(tuple_date)
                        published_at = datetime.fromtimestamp(timestamp)
                except Exception:
                    published_at = datetime.utcnow()

            article = Article(
                title=title,
                source=source_name,
                query_origin=query,
                published_at=published_at,
                url=url_link,
                description=description,
                content=None # RSSes don't return any content'
            )
            articles.append(article)

    except Exception as e:
        print(f"Error during fetch from google news: {e}")

    return articles

def fetch_from_duckduckgo(query: str, lang: str = "wt", country: str = "WT", max_results: int = 40) -> List[Article]:
    """
    Interrogate DuckDuckGo News Search, eventually fallback Google News.
    """
    region = f"{lang.lower()}-{country.lower()}" if country and lang else "wt-wt"
    articles = []

    try:
        with DDGS(timeout=40) as ddgs:
            # Corretto: 'query' passato come primo parametro posizionale
            results = ddgs.news(query, region=region, max_results=max_results)

            for item in results:
                published_at = None
                if item.get("date"):
                    try:
                        published_at = datetime.fromisoformat(item["date"].replace("Z", "+00:00"))
                    except ValueError:
                        published_at = datetime.utcnow()

                article = Article(
                    title=item.get("title", ""),
                    source=item.get("source", "DuckDuckGo"),
                    query_origin=query,
                    published_at=published_at,
                    url=item.get("url", ""),
                    description=item.get("body", ""),
                    content=None
                )
                articles.append(article)

    except Exception as e:
        print(f"DuckDuckGo error ({e}). Fallback su Google News...")
        from headline_analyst.fetchers import fetch_from_google_news
        return fetch_from_google_news(query=query, lang=lang, country=country)

    return articles
