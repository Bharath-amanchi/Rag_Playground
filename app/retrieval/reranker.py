from sentence_transformers import CrossEncoder
from langchain_core.documents import Document

# loads once at startup — no repeated downloads
_reranker = None

def get_reranker() -> CrossEncoder:
    global _reranker
    if _reranker is None:
        # free, runs locally, no API key needed
        _reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    return _reranker


def rerank(query: str, docs: list[Document], top_k: int = 5) -> list[Document]:
    """
    Re-score docs against query using CrossEncoder.
    Returns top_k most relevant docs in order.
    """
    if not docs:
        return []

    reranker = get_reranker()

    # build (query, doc_content) pairs
    pairs = [(query, doc.page_content) for doc in docs]

    # score all pairs — CrossEncoder reads both together
    scores = reranker.predict(pairs)

    # attach scores to docs and sort descending
    scored_docs = sorted(
        zip(scores, docs),
        key=lambda x: x[0],
        reverse=True
    )

    # return top_k with score in metadata for transparency
    results = []
    for score, doc in scored_docs[:top_k]:
        doc.metadata["rerank_score"] = round(float(score), 4)
        results.append(doc)

    return results