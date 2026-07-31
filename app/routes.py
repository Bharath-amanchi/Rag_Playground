from pathlib import Path

from fastapi import APIRouter
from fastapi import File
from fastapi import UploadFile
from app.vectorstore import vectorstore
from app.rag import ingest_document
from app.models import ChatRequest
from app.rag import ask_question

router = APIRouter()

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    pdf_path = UPLOAD_FOLDER / file.filename

    with open(pdf_path, "wb") as f:
        f.write(await file.read())

    chunks = ingest_document(str(pdf_path))

    return {
        "filename": file.filename,
        "chunks": chunks,
        "message": "Document indexed successfully"
    }

@router.post("/chat")
def chat(request: ChatRequest):

    answer = ask_question(request.session_id,
        request.question)

    return {
        "question": request.question,
        "answer": answer,
        
    }
@router.get("/documents")
def documents():

    collection = vectorstore._collection

    return {
        "count": collection.count()
    }

@router.delete("/documents")
def clear_documents():

    collection = vectorstore._collection

    ids = collection.get()["ids"]

    collection.delete(ids)

    return {
        "message":"Database cleared"
    }   