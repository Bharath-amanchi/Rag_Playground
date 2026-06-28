from langchain_nvidia_ai_endpoints import ChatNVIDIA

from app.config import NVIDIA_API_KEY, LLM_MODEL

llm = ChatNVIDIA(
    model=LLM_MODEL,
    api_key=NVIDIA_API_KEY,
    temperature=0.2,
)