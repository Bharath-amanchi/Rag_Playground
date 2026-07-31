from app.document_loader import load_pdf
from app.text_splitter import text_splitter
from app.vectorstore import vectorstore
from langchain_core.output_parsers import StrOutputParser

from app.vectorstore import retriever
from app.prompts import RAG_PROMPT
from app.llm import llm
from fastapi import HTTPException
from app.memory import (
    add_message_temp, get_history_temp,
    add_message_persistent, get_history_persistent
)

parser = StrOutputParser()


from langchain_core.output_parsers import StrOutputParser
from app.vectorstore import retriever
from app.prompts import RAG_PROMPT
from app.llm import llm
from fastapi import HTTPException
from app.memory import (
    add_message_temp, get_history_temp,
    add_message_persistent, get_history_persistent
)
from app.document_loader import load_pdf
from app.text_splitter import text_splitter
from app.vectorstore import vectorstore

parser = StrOutputParser()

async def ask_question(session_id: str, question: str, user_id: str = "anonymous", persistent: bool = False):
    try:
        docs = retriever.invoke(question)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    context = "\n\n".join(doc.page_content for doc in docs)

    # ── get history based on mode ──
    if persistent:
        raw_history = await get_history_persistent(session_id)
    else:
        raw_history = get_history_temp(session_id)

    history = "\n".join(
        f"{msg['role']}: {msg['content']}"
        for msg in raw_history
    )

    chain = RAG_PROMPT | llm | parser

    answer = chain.invoke({
        "context": context,
        "question": question,
        "history": history,
    })

    # ── save history based on mode ──
    if persistent:
        await add_message_persistent(session_id, user_id, "user", question)
        await add_message_persistent(session_id, user_id, "assistant", answer)
    else:
        add_message_temp(session_id, "user", question)
        add_message_temp(session_id, "assistant", answer)

    return {
        "answer": answer,
        "history":history,
        "sources": [
            {
                "page": doc.metadata.get("page"),
                "source": doc.metadata.get("source"),
                # "chunks":doc
            }
            for doc in docs
        ],
    }

def ingest_document(pdf_path: str):
    documents = load_pdf(pdf_path)
    chunks = text_splitter.split_documents(documents)
    vectorstore.add_documents(chunks)

    return len(chunks)