from app.document_loader import load_pdf
from app.text_splitter import text_splitter
from app.vectorstore import vectorstore
from langchain_core.output_parsers import StrOutputParser

from app.vectorstore import retriever
from app.prompts import RAG_PROMPT
from app.llm import llm


parser = StrOutputParser()


def ask_question(question: str):

    docs = retriever.invoke(question)

    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    chain = RAG_PROMPT | llm | parser

    answer = chain.invoke(
        {
            "context": context,
            "question": question,
        }
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