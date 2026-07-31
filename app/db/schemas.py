from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime,timezone

# --- User ---
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str                    # plain, will be hashed before saving
    role: str = "user"               # "user" or "admin"

class UserInDB(BaseModel):
    username: str
    email: str
    hashed_password: str
    role: str
    created_at: datetime = datetime.now(timezone.utc)

# --- Chat Message ---
class Message(BaseModel):
    role: str                        # "user" or "assistant"
    content: str
    timestamp: datetime = datetime.now(timezone.utc)

# --- Chat Session ---
class ChatSession(BaseModel):
    session_id: str
    user_id: str                     # links to user
    is_persistent: bool = False      # True = saved to MongoDB, False = temp (in-memory only)
    messages: List[Message] = []
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)