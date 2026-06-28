from fastapi import FastAPI

from app.routes import router

app = FastAPI(title="Simple RAG API")

app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "Simple RAG API Running"
    }