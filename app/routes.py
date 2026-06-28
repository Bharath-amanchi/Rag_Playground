from pathlib import Path

from fastapi import APIRouter
from fastapi import File
from fastapi import UploadFile

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

    answer = ask_question(request.question)

    return {
        "question": request.question,
        "answer": answer,
        
    }