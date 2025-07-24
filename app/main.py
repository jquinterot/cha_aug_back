from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routes import chat
from app.api.v1.routes import user

app = FastAPI(title="Chat API")

# Allow all origins for development. Restrict in production!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(user.router, prefix="/api/v1/user", tags=["user"])
# NOTE: Route is defined as "/" (no trailing slash), so prefix should not end with a slash.
