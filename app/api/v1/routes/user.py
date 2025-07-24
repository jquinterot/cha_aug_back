from fastapi import APIRouter, HTTPException
from app.schemas.user import UserCreate, UserInDB, UserResponse
from app.services.mongo_service import create_user, get_user_by_id, get_all_users, delete_user_by_id
from datetime import datetime
from fastapi import status

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

@router.get("/users", response_model=list[UserResponse])
async def list_users():
    users = await get_all_users()
    # Remove password from each user
    for user in users:
        user.pop("password", None)
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.pop("password", None)
    return user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str):
    deleted = await delete_user_by_id(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return
