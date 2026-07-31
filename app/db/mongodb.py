from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_DB,MONGO_URI
client=AsyncIOMotorClient(MONGO_URI)
db=client[MONGO_DB]
users_collection = db["users"]
chat_collection = db["chat_history"]
documents_collection = db["documents"]