from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import MONGO_URI
from bson import ObjectId

client = AsyncIOMotorClient(MONGO_URI)
db = client["chat_aug"]
users_collection = db["users"]

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
