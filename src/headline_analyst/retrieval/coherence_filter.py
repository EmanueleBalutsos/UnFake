from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import AgglomerativeClustering

from headline_analyst.data import Article
from headline_analyst.retrieval.factory import create_relevance_checker

def filter_by_event_coherence(
        articles: list[Article],
        event_query: str,
        threshold: float = 0.75,
        model_name: str = "all-MiniLM-L6-v2"
) -> list[Article]:
    """
    Keep only articles whose headline + description is semantically close to the original event query, 
    solely using cosine similarity between embeddings.
    """

    if not articles:
        return []

    model = SentenceTransformer(model_name)
    event_emb = model.encode([event_query], normalize_embeddings=True, convert_to_tensor=False)

    text = [
        f"{a.title}. {a.description or ''}" for a in articles
    ]

    article_embs = model.encode(text, normalize_embeddings=True, convert_to_tensor=False)

    sims = cosine_similarity(event_emb, article_embs)[0]

    return [a for a, sim in zip(articles, sims) if sim >= threshold]


async def llm_relevance_filter(
        relevance_checker_config: dict,
        articles: list[Article],
        event_query: str,
        batch_size: int=20,
) -> list[Article]:
    """
    Use an LLM to judge whether each article is relevant to the same event. 
    Bathces articles for efficiency.
    This is more expensive but can catch more subtle relevance issues that simple cosine similarity might miss.
    """
    llm_checker = create_relevance_checker(relevance_checker_config)

    async with llm_checker:
        articles = await llm_checker.filter(articles, event_query, batch_size)

    return articles


def cluster_by_subevent(
    articles: list[Article],
    n_clusters: int | None = None,
    distance_threshold: float = 0.4
) -> dict[int, list[Article]]:
    """
    Cluster articles into sub-events, based on cosine distance. Useful to pick the dominant cluster
    (most articles) as the "main event" cluster.
    """
    model = SentenceTransformer("all-MiniLM-L6-v2")
    texts = [f"{a.title}. {a.description or ''}" for a in articles]
    embeddings = model.encode(texts)
    
    clustering = AgglomerativeClustering(
        n_clusters=n_clusters,
        distance_threshold=distance_threshold if n_clusters is None else None,
        metric="cosine",
        linkage="average"
    )
    labels = clustering.fit_predict(embeddings)
    
    clusters: dict[int, list[Article]] = {}
    for label, article in zip(labels, articles):
        clusters.setdefault(label, []).append(article)
    
    return clusters

def pick_dominant_cluster(clusters: dict[int, list[Article]]) -> list[Article]:
    """Return articles from the largest cluster — most likely the main event."""
    return max(clusters.values(), key=len)