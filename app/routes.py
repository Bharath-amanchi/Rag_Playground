from pathlib import Path
from fastapi import Depends, HTTPException
from fastapi import APIRouter
from fastapi import File
from fastapi import UploadFile
from app.memory import clear_history_persistent, clear_history_temp, get_history_persistent, get_history_temp
from app.vectorstore import vectorstore
from app.rag import ingest_document
from app.models import ChatRequest
from app.rag import ask_question
from app.auth.dependencies import get_current_user, require_admin
from app.url_loader import load_url
from app.models import ChatRequest, URLIngestRequest
from app.vectorstore import vectorstore

router = APIRouter()

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: dict = Depends(require_admin)
):
    pdf_path = UPLOAD_FOLDER / file.filename

    with open(pdf_path, "wb") as f:
        f.write(await file.read())

    chunks = ingest_document(str(pdf_path))

    return {
        "filename": file.filename,
        "chunks": chunks,
        "message": "Document indexed successfully",
        "uploaded_by": current_user["username"]
    }


@router.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    result = await ask_question(                        
        session_id=request.session_id,
        question=request.question,
        user_id=current_user["username"],
        persistent=request.persistent
    )
    return {**result, "user": current_user["username"]}

@router.get("/chat/history/{session_id}")
async def get_chat_history(
    session_id: str,
    persistent: bool = False,
    current_user: dict = Depends(get_current_user)
):
    if persistent:
        history = await get_history_persistent(session_id)
    else:
        history = get_history_temp(session_id)
    return {"session_id": session_id, "messages": history, "persistent": persistent}


@router.delete("/chat/history/{session_id}")
async def clear_chat_history(
    session_id: str,
    persistent: bool = False,
    current_user: dict = Depends(get_current_user)
):
    if persistent:
        await clear_history_persistent(session_id)
    else:
        clear_history_temp(session_id)
    return {"message": f"History cleared for session {session_id}", "persistent": persistent}

@router.get("/documents")
def documents(
    current_user: dict = Depends(get_current_user)
):
    collection = vectorstore._collection

    return {
        "count": collection.count(),
        "requested_by": current_user["username"]
    }


@router.delete("/documents")
def clear_documents(
    current_user: dict = Depends(require_admin)
):
    collection = vectorstore._collection
    ids = collection.get()["ids"]
    collection.delete(ids)

    return {
        "message": "Database cleared",
        "deleted_by": current_user["username"]
    }

@router.post("/ingest-url")
async def ingest_url(
    request: URLIngestRequest,
    current_user: dict = Depends(require_admin)    # admin only
):
    try:
        chunks = load_url(request.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to load URL: {str(e)}")

    vectorstore.add_documents(chunks)

    return {
        "url": request.url,
        "chunks_stored": len(chunks),
        "message": "URL content indexed successfully",
        "ingested_by": current_user["username"]
    }