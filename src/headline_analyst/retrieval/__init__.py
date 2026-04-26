# add other query generator classes here as needed
from .deduplicator import deduplicate_articles
from .search import multi_search
from .coherence_filter import filter_by_event_coherence, llm_relevance_filter, cluster_by_subevent, pick_dominant_cluster
from .llm_relevance_checker import LLMArticleRelevanceChecker

__all__ = [
    "deduplicate_articles",
    "multi_search",
    "filter_by_event_coherence",
    "llm_relevance_filter",
    "cluster_by_subevent",
    "pick_dominant_cluster",
    "LLMArticleRelevanceChecker"
]