from langchain_core.prompts import ChatPromptTemplate

RAG_PROMPT = ChatPromptTemplate.from_template(
"""
You are a helpful assistant.

Use ONLY the provided context.

Previous Conversation:
{history}

Context:
{context}

Question:
{question}

Answer:
"""
)