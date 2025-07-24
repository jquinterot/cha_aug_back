from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import MONGO_URI

client = AsyncIOMotorClient(MONGO_URI)
db = client["chat_aug"]
users_collection = db["users"]

async def create_user(user_data: dict) -> str:
    result = await users_collection.insert_one(user_data)
    return str(result.inserted_id)
