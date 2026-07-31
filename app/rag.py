from app.document_loader import load_pdf
from app.text_splitter import text_splitter
from app.vectorstore import vectorstore
from langchain_core.output_parsers import StrOutputParser

from app.vectorstore import retriever
from app.prompts import RAG_PROMPT
from app.llm import llm
from fastapi import HTTPException
from app.memory import (
    add_message,
    get_history
)

parser = StrOutputParser()


def ask_question( session_id: str,question: str,):



    try:
        docs = retriever.invoke(question)

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )
    history = "\n".join(
        [
            f"{msg['role']}: {msg['content']}"
            for msg in get_history(session_id)
        ]
    )
    chain = RAG_PROMPT | llm | parser

    answer = chain.invoke(
        {
            "context": context,
            "question": question,
            "history":history,
        }
    )
    add_message(
        session_id,
        "user",
        question,
    )

    add_message(
        session_id,
        "assistant",
        answer,
    )
    return {
        "answer": answer,
        "sources": [
            {
                "page": doc.metadata.get("page"),
                "source": doc.metadata.get("source"),
            }
            for doc in docs
        ],
    }

def ingest_document(pdf_path: str):
    documents = load_pdf(pdf_path)
    chunks = text_splitter.split_documents(documents)
    vectorstore.add_documents(chunks)

    return len(chunks)