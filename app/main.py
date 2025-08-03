from fastapi import FastAPI, Request, HTTPException, status, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import Callable, Awaitable, Any, List, Dict
import os
from pathlib import Path
from fastapi.routing import APIRoute

from app.api.v1.routes import chat, rag
from app.api.v1.routes import user

app = FastAPI(title="Chat API", redirect_slashes=False)


# Allow all origins for development. Restrict in production!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(rag.router, prefix="/api/v1/rag", tags=["rag"])
app.include_router(user.router, prefix="/api/v1/user", tags=["user"])

# Create data directory if it doesn't exist
os.makedirs("data/vector_store", exist_ok=True)

@app.get("/api/v1/health", status_code=200, tags=["health"])
async def health_check():
    """
    Health check endpoint for the application.
    Returns 200 OK if the application is running.
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "api": "operational",
            "database": "connected"  # Add more detailed checks as needed
        }
    }
# NOTE: Route is defined as "/" (no trailing slash), so prefix should not end with a slash.
