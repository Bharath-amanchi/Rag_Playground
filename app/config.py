from dotenv import load_dotenv
import os
load_dotenv()
NVIDIA_API_KEY=os.getenv("NVIDIA_API_KEY")
CHROMA_DB_DIR="db/chroma"
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
LLM_MODEL = "nvidia/llama-3.3-nemotron-super-49b-v1"