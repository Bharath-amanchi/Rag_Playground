from rank_bm25 import BM25Okapi
from langchain_core.documents import Document
from app.vectorstore import vectorstore
import numpy as np


def reciprocal_rank_fusion(
    semantic_docs: list[Document],
    bm25_docs: list[Document],
    k: int = 60
) -> list[Document]:
    """Merge two ranked lists using RRF scoring."""
    scores = {}
    doc_map = {}

    for rank, doc in enumerate(semantic_docs):
        key = doc.page_content
        scores[key] = scores.get(key, 0) + 1 / (k + rank + 1)
        doc_map[key] = doc

    for rank, doc in enumerate(bm25_docs):
        key = doc.page_content
        scores[key] = scores.get(key, 0) + 1 / (k + rank + 1)
        doc_map[key] = doc

    # sort by combined RRF score descending
    sorted_keys = sorted(scores, key=lambda x: scores[x], reverse=True)
    return [doc_map[k] for k in sorted_keys]


def hybrid_search(query: str, user_id: str = None, top_k: int = 10) -> list[Document]:
    """
    Run semantic + BM25 search and fuse results.
    user_id → filters to that user's collection (multi-tenant, Step C)
    """

    # ── 1. Semantic search via ChromaDB ──────────────────────
    where_filter = {"user_id": user_id} if user_id else None

    semantic_results = vectorstore.similarity_search(
        query,
        k=top_k,
        filter=where_filter
    )

    if not semantic_results:
        return []

    # ── 2. BM25 on the same candidate pool ───────────────────
    # get all docs from collection for BM25 index
    collection = vectorstore._collection
    all_data = collection.get(
        where=where_filter,
        include=["documents", "metadatas"]
    )

    if not all_data["documents"]:
        return semantic_results

    # tokenize for BM25
    corpus = all_data["documents"]
    tokenized_corpus = [doc.lower().split() for doc in corpus]
    bm25 = BM25Okapi(tokenized_corpus)

    # score query against corpus
    tokenized_query = query.lower().split()
    bm25_scores = bm25.get_scores(tokenized_query)

    # get top_k BM25 results
    top_indices = np.argsort(bm25_scores)[::-1][:top_k]
    bm25_results = [
        Document(
            page_content=corpus[i],
            metadata=all_data["metadatas"][i]
        )
        for i in top_indices
        if bm25_scores[i] > 0   # skip zero-score docs
    ]

    # ── 3. Fuse with RRF ─────────────────────────────────────
    fused = reciprocal_rank_fusion(semantic_results, bm25_results)
    return fused[:top_k]