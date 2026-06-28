# RAG Playground 🚀

A lightweight **Retrieval-Augmented Generation (RAG)** API built with **FastAPI**, **LangChain**, **ChromaDB**, and **NVIDIA AI Endpoints**. Upload PDF documents and ask questions — the system retrieves relevant context and generates accurate, grounded answers.

---

## 🧠 How It Works

```
PDF Upload → Document Loading → Text Splitting → Embedding (HuggingFace BGE)
                                                          ↓
User Question → Embed Query → ChromaDB Similarity Search → Retrieved Context
                                                          ↓
                              NVIDIA LLM (Llama 3.3 Nemotron) → Answer
```

---

## 🗂️ Project Structure

```
Rag_Playground/
├── app/
│   ├── __init__.py
│   ├── config.py           # Env vars, model names, DB path
│   ├── document_loader.py  # PDF loading via LangChain
│   ├── embeddings.py       # HuggingFace BGE embeddings
│   ├── llm.py              # NVIDIA ChatNVIDIA LLM client
│   ├── main.py             # FastAPI app entry point
│   ├── models.py           # Pydantic request models
│   ├── prompts.py          # RAG prompt template
│   ├── rag.py              # RAG chain logic
│   ├── routes.py           # API route handlers
│   ├── text_splitter.py    # Document chunking
│   └── vectorstore.py      # ChromaDB vector store
├── .env.example
├── .gitignore
└── pyproject.toml
```

---

## ⚙️ Tech Stack

| Component        | Library / Model                          |
|------------------|------------------------------------------|
| API Framework    | FastAPI                                  |
| LLM              | `nvidia/llama-3.3-nemotron-super-49b-v1` |
| Embeddings       | `BAAI/bge-small-en-v1.5` (HuggingFace)  |
| Vector Store     | ChromaDB                                 |
| Document Loader  | LangChain `PyPDFLoader`                  |
| LLM Integration  | `langchain-nvidia-ai-endpoints`          |

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Bharath-amanchi/Rag_Playground.git
cd Rag_Playground
```

### 2. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your NVIDIA API key:

```env
NVIDIA_API_KEY=your_nvidia_api_key_here
```

> Get your free API key at [build.nvidia.com](https://build.nvidia.com)

### 3. Create a virtual environment

Using `uv` (recommended):

```bash
uv venv
```

Or with standard Python:

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux / Mac:**
```bash
source .venv/bin/activate
```

### 5. Install dependencies

Using `uv`:

```bash
uv sync
```

Or with `pip`:

```bash
pip install -e .
```

### 6. Run the server

```bash
uvicorn app.main:app --reload
```

The API will be live at `http://localhost:8000`

---

## 📡 API Endpoints

### `GET /`
Health check — confirms the API is running.

**Response:**
```json
{ "message": "Simple RAG API Running" }
```

### `POST /upload`
Upload a PDF document to be indexed into the vector store.

**Request:** `multipart/form-data` with a PDF file

### `POST /chat`
Ask a question against the uploaded documents.

**Request:**
```json
{ "question": "What is the main topic of the document?" }
```

**Response:**
```json
{ "answer": "The document discusses ..." }
```

---

## 🔧 Configuration

Key settings in `app/config.py`:

| Variable          | Default Value                              | Description                   |
|-------------------|--------------------------------------------|-------------------------------|
| `EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5`                   | HuggingFace embedding model   |
| `LLM_MODEL`       | `nvidia/llama-3.3-nemotron-super-49b-v1`   | NVIDIA LLM model              |
| `CHROMA_DB_DIR`   | `db/chroma`                                | Local ChromaDB storage path   |

---

## 📦 Dependencies

Key packages (see `pyproject.toml` for full list):

- `fastapi`
- `uvicorn`
- `langchain`
- `langchain-community`
- `langchain-huggingface`
- `langchain-nvidia-ai-endpoints`
- `chromadb`
- `pypdf`
- `python-dotenv`
- `pydantic`

---

## 📝 Notes

- Uploaded PDFs are saved temporarily under `uploads/` (git-ignored).
- ChromaDB persists vectors under `chroma/` (git-ignored).
- The LLM temperature is set to `0.2` for more deterministic, factual responses.

---
