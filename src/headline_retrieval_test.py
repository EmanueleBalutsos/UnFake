import os
from dotenv import load_dotenv
from newsapi import NewsApiClient


"""
See doc : https://newsapi.org/docs/endpoints/
"""

# load the api
load_dotenv()
newsApi_key = os.environ.get('NEWSAPI_KEY')
newsApi = NewsApiClient(newsApi_key)

headlines = newsApi.get_everything(
    qintitle="climate",  # get only articles with "climate" in the headline
    sort_by="publishedAt", # newest articles come first
    language='en',     # english articles
    page_size=20       # number of results (max 100)
)

# extract and print headlines
articles = headlines.get('articles', [])

for i, article in enumerate(articles, start=1):
    print(f"{i}. {article['title']} - Source : {article['source'].get('name')}")
