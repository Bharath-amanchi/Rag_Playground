from langchain_chroma import Chroma

from app.embeddings import embeddings
from app.config import CHROMA_DB_DIR

vectorstore = Chroma(
    persist_directory=CHROMA_DB_DIR,
    embedding_function=embeddings,
)

retriever = vectorstore.as_retriever(
    search_kwargs={"k": 4}
)