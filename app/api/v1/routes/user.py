from fastapi import APIRouter, HTTPException
from app.schemas.user import UserCreate, UserInDB
from app.services.mongo_service import create_user
from datetime import datetime

router = APIRouter()

@router.post("/register", response_model=UserInDB)
async def register_user(user: UserCreate):
    user_data = user.dict()
    now = datetime.utcnow()
    user_data["createdAt"] = now
    user_data["modifiedAt"] = now
    # WARNING: In production, hash the password before storing!
    inserted_id = await create_user(user_data)
    return UserInDB(id=inserted_id, **user_data)
