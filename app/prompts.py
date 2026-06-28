from langchain_core.prompts import ChatPromptTemplate

RAG_PROMPT = ChatPromptTemplate.from_template(
    """
You are a helpful AI assistant.


Context:
{context}

Question:
{question}

Answer:
"""
)