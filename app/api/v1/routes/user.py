from fastapi import APIRouter, HTTPException, Depends
from app.schemas.user import UserCreate, UserInDB, UserResponse, UserLogin, Token
from app.services.mongo_service import create_user, get_user_by_id, get_all_users, delete_user_by_id, get_user_by_username, get_user_by_login
from app.services.jwt_service import create_access_token
from datetime import datetime
from fastapi import status
from app.deps import get_current_user
from passlib.context import CryptContext

router = APIRouter(redirect_slashes=False)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    db_user = await get_user_by_login(user.login)
    if not db_user or not pwd_context.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": db_user["id"]})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/register", response_model=Token)
async def register_user(user: UserCreate):
    # Check if username already exists
    if await get_user_by_username(user.username):
        raise HTTPException(status_code=400, detail="Username already created")
    # Check if email already exists
    if await get_user_by_login(user.email):
        raise HTTPException(status_code=400, detail="Email already created")
    user_data = user.dict()
    now = datetime.utcnow()
    user_data["createdAt"] = now
    user_data["modifiedAt"] = now
    user_data["password"] = pwd_context.hash(user_data["password"])
    inserted_id = await create_user(user_data)
    token = create_access_token({"sub": inserted_id})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/users", response_model=list[UserResponse], dependencies=[Depends(get_current_user)])
async def list_users():
    users = await get_all_users()
    # Remove password from each user
    for user in users:
        user.pop("password", None)
    return users

@router.get("/users/{user_id}", response_model=UserResponse, dependencies=[Depends(get_current_user)])
async def get_user(user_id: str):
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.pop("password", None)
    return user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_user)])
async def delete_user(user_id: str):
    deleted = await delete_user_by_id(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return
