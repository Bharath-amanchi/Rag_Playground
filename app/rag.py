from langchain_core.output_parsers import StrOutputParser
from fastapi import HTTPException
from app.prompts import RAG_PROMPT
from app.llm import llm
from app.vectorstore import vectorstore
from app.document_loader import load_pdf
from app.text_splitter import text_splitter
from app.retrieval.hybrid import hybrid_search
from app.retrieval.reranker import rerank
from app.memory import (
    add_message_temp, get_history_temp,
    add_message_persistent, get_history_persistent
)

parser = StrOutputParser()


def ingest_document(pdf_path: str):
    docs = load_pdf(pdf_path)
    chunks = text_splitter.split_documents(docs)
    vectorstore.add_documents(chunks)
    return {"chunks_indexed": len(chunks)}


async def ask_question(
    session_id: str,
    question: str,
    user_id: str = "anonymous",
    persistent: bool = False
):
    # ── Step 1: Hybrid search (semantic + BM25) → 10 docs ────
    candidates = hybrid_search(query=question, user_id=user_id, top_k=10)

    if not candidates:
        return {
            "answer": "No relevant documents found. Please upload documents first.",
            "sources": [],
            "persistent": persistent
        }

    # ── Step 2: Rerank → best 5 docs ─────────────────────────
    docs = rerank(query=question, docs=candidates, top_k=5)

    # ── Step 3: Build context from reranked docs ──────────────
    context = "\n\n".join(doc.page_content for doc in docs)

    # ── Step 4: Get chat history ──────────────────────────────
    if persistent:
        raw_history = await get_history_persistent(session_id)
    else:
        raw_history = get_history_temp(session_id)

    history = "\n".join(
        f"{msg['role']}: {msg['content']}"
        for msg in raw_history
    )

    # ── Step 5: Call NVIDIA LLM ───────────────────────────────
    chain = RAG_PROMPT | llm | parser
    answer = chain.invoke({
        "context": context,
        "question": question,
        "history": history,
    })

    # ── Step 6: Save history ──────────────────────────────────
    if persistent:
        await add_message_persistent(session_id, user_id, "user", question)
        await add_message_persistent(session_id, user_id, "assistant", answer)
    else:
        add_message_temp(session_id, "user", question)
        add_message_temp(session_id, "assistant", answer)

    # ── Step 7: Return with sources + rerank scores ───────────
    return {
        "answer": answer,
        "sources": [
            {
                "content": doc.page_content[:200],   # preview
                "source": doc.metadata.get("source", doc.metadata.get("filename", "")),
                "page": doc.metadata.get("page", ""),
                "rerank_score": doc.metadata.get("rerank_score", "")
            }
            for doc in docs
        ],
        "persistent": persistent
    }