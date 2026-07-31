from pydantic import BaseModel


class ChatRequest(BaseModel):
    session_id: str
    question: str
    persistent: bool = False

class URLIngestRequest(BaseModel): 
    url: str