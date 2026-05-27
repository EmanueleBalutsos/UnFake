import os
import asyncio

from dotenv import load_dotenv

from headline_analyst.query_expansion import generate_queries
from headline_analyst.utils.config_loader import load_config

from headline_analyst.data import Article
from headline_analyst.retrieval import *

def print_article_list(articles: list[Article]):
        for i, article in enumerate(articles, start=1):
                print(f"{i}. {article.title} - Source : {article.source} - Query Origin : {article.query_origin}")

async def gather_articles(event: str,
                          num_queries: int = 10,
                          page_size_per_query: int = 10,
                          embedding_threshold: float = 0.75,
                          use_query_expansion: bool = True,
                          use_clustering: bool = True,
                          use_llm_filter: bool = True,
                          verbose: bool = False) -> list[Article]:
        """
        Full pipeline to gather articles about a news event, given a short event description.
        1. Expand queries for the event
        2. Retrieve articles for each query
        3. Deduplicate articles
        4. Filter by coherence with the original event description, using both cosine similarity and an LLM relevance checker.
        """

        if(use_query_expansion):
                # Step 1. Expand queries for a given news event
                query_gen_config = load_config()["query_generator"] # load llm provider for query expansion specified in the yaml config
                try:
                        queries = await generate_queries(query_gen_config=query_gen_config, event=event, num_queries=num_queries)
                        queries.append(event) # add the raw event description as a query to make sure we don't miss relevant articles in case of failed expansion or overly creative expansion
                        if verbose: print(f"Generated {len(queries)} queries: \n {queries}")
                except Exception as e:
                        if verbose: print(f"Query expansion failed ({e}), falling back to raw event input.")
                        queries = [event]
        else: # query expansion disabled -> only rely on raw user input
               queries = [event]

        if verbose: print("\n\n----------------------------------------------\n\n")

        # Step 2. Multi-source search
        load_dotenv()
        newsApi_key = os.environ.get('NEWSAPI_KEY')
        gnews_key = os.environ.get('GNEWS_KEY')
        if newsApi_key is None:
            raise ValueError("NEWSAPI_KEY environment variable is not set")
        if gnews_key is None:
            raise ValueError("GNEWS_KEY environment variable is not set")

        articles = await multi_search(queries, newsapi_key=newsApi_key, gnews_key=gnews_key, page_size=page_size_per_query)
        if not articles:
            if verbose: print("No articles matching query found. Event might be too old to still be indexed by our search APIs, or API requests might have failed/reached rate limits.")
            return []

        if verbose:
                print(f"Retrieved {len(articles)} articles across all queries : \n")
                print_article_list(articles)
                print("\n\n----------------------------------------------\n\n")

        # Step 3. URL + TitleDeduplication
        articles = deduplicate_articles(articles)
        if not articles:
                if verbose: print("No articles matching query found after deduplication.")
                return []

        if verbose:
                print(f"{len(articles)} articles after deduplication : \n")
                print_article_list(articles)
                print("\n\n----------------------------------------------\n\n")

        # Step 4.1. Embedding-based coherence filtering (using cosine distance) (cheap, first pass)
        articles = filter_by_event_coherence(articles, event, threshold=embedding_threshold)
        if not articles:
                if verbose: print("No articles matching query found after embedding filter.")
                return []

        if verbose:
                print(f"{len(articles)} articles after embedding filter : \n")
                print_article_list(articles)
                print("\n\n----------------------------------------------\n\n")

        # Step 4.2. Cluster to isolate main event (catches sub-event drift)
        # OPTIONAL
        if use_clustering:
                clusters = cluster_by_subevent(articles)
                articles = pick_dominant_cluster(clusters)
                if not articles:
                        if verbose: print("No articles matching query found after clustering.")
                        return []

                if verbose:
                        print(f"{len(articles)} articles after picking dominant cluster : \n")
                        print_article_list(articles)
                        print("\n\n----------------------------------------------\n\n")

        # Step 4.3. LLM relevance filter (for better precision)
        if use_llm_filter:
                relevance_checker_config = load_config()["llm_relevance_checker"] # load llm provider for relevance checking specified in the yaml config
                articles = await llm_relevance_filter(relevance_checker_config, articles, event)
                if not articles:
                        if verbose: print("No articles matching query found after LLM relevance filter.")
                        return []

                if verbose:
                        print(f"{len(articles)} articles after LLM relevance filter : \n")
                        print_article_list(articles)

        return articles


# Test
if __name__ == "__main__":
        asyncio.run(gather_articles("Trump on the Iran war", 
                                    num_queries=10, 
                                    page_size_per_query=5, 
                                    embedding_threshold=0.4,
                                    use_query_expansion=True,
                                    use_clustering=False, 
                                    use_llm_filter=True))



