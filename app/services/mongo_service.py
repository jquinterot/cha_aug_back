from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import MONGO_URI, MONGO_DB_NAME
from bson import ObjectId
from datetime import datetime
from typing import List, Optional

# Create a global client and database connection
client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB_NAME]
users_collection = db["users"]
chat_sessions_collection = db["chat_sessions"]

async def create_user(user_data: dict) -> str:
    result = await users_collection.insert_one(user_data)
    return str(result.inserted_id)

async def get_user_by_id(user_id: str) -> dict | None:
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        user["id"] = str(user["_id"])
        user.pop("_id", None)
        return user
    return None

async def get_user_by_username(username: str) -> dict | None:
    user = await users_collection.find_one({"username": username})
    if user:
        user["id"] = str(user["_id"])
        user.pop("_id", None)
        return user
    return None

async def get_user_by_login(login: str) -> dict | None:
    user = await users_collection.find_one({"username": login})
    if not user:
        user = await users_collection.find_one({"email": login})
    if user:
        user["id"] = str(user["_id"])
        user.pop("_id", None)
        return user
    return None

async def get_all_users() -> list[dict]:
    users = []
    async for user in users_collection.find():
        user["id"] = str(user["_id"])
        user.pop("_id", None)
        users.append(user)
    return users

async def delete_user_by_id(user_id: str) -> bool:
    result = await users_collection.delete_one({"_id": ObjectId(user_id)})
    return result.deleted_count == 1

# Chat Session Methods
async def create_chat_session(user_id: Optional[str] = None) -> str:
    session_data = {
        "user_id": ObjectId(user_id) if user_id else None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "messages": []
    }
    result = await chat_sessions_collection.insert_one(session_data)
    return str(result.inserted_id)

async def get_chat_session(session_id: str) -> Optional[dict]:
    session = await chat_sessions_collection.find_one({"_id": ObjectId(session_id)})
    if session:
        session["id"] = str(session["_id"])
        session.pop("_id", None)
    return session

async def add_message_to_session(session_id: str, role: str, content: str) -> bool:
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.utcnow()
    }
    result = await chat_sessions_collection.update_one(
        {"_id": ObjectId(session_id)},
        {
            "$push": {"messages": message},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    return result.modified_count == 1

async def get_session_messages(session_id: str) -> List[dict]:
    session = await chat_sessions_collection.find_one(
        {"_id": ObjectId(session_id)},
        {"messages": 1}
    )
    return session.get("messages", []) if session else []

async def delete_chat_session(session_id: str) -> bool:
    result = await chat_sessions_collection.delete_one({"_id": ObjectId(session_id)})
    return result.deleted_count == 1
