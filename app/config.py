from dotenv import load_dotenv
import os
load_dotenv()
NVIDIA_API_KEY=os.getenv("NVIDIA_API_KEY")
CHROMA_DB_DIR="db/chroma"
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
LLM_MODEL = "nvidia/llama-3.3-nemotron-super-49b-v1"
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "rag_playground")
JWT_SECRET = os.getenv("JWT_SECRET", "change_this_secret")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60