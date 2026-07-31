from collections import defaultdict
from datetime import datetime
from app.db.mongodb import chat_collection

# ── TEMPORARY (in-memory, lost on restart) ──────────────────
chat_history = defaultdict(list)

def add_message_temp(session_id: str, role: str, content: str):
    chat_history[session_id].append({
        "role": role,
        "content": content
    })

def get_history_temp(session_id: str) -> list:
    return chat_history.get(session_id, [])

def clear_history_temp(session_id: str):
    chat_history.pop(session_id, None)


# ── PERSISTENT (MongoDB, survives restart) ───────────────────
async def add_message_persistent(session_id: str, user_id: str, role: str, content: str):
    await chat_collection.update_one(
        {"session_id": session_id},
        {
            "$set": {
                "user_id": user_id,
                "updated_at": datetime.utcnow()
            },
            "$push": {
                "messages": {
                    "role": role,
                    "content": content,
                    "timestamp": datetime.utcnow()
                }
            },
            "$setOnInsert": {
                "created_at": datetime.utcnow()
            }
        },
        upsert=True     # create if session doesn't exist yet
    )

async def get_history_persistent(session_id: str) -> list:
    doc = await chat_collection.find_one({"session_id": session_id})
    if not doc:
        return []
    return doc.get("messages", [])

async def clear_history_persistent(session_id: str):
    await chat_collection.delete_one({"session_id": session_id})