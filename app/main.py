from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Callable, Awaitable, Any
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

# Middleware guard function
async def auth_guard(request: Request, call_next: Callable[[Request], Awaitable[Any]]) -> Any:
    """
    Middleware guard for authentication/authorization.
    Currently a no-op implementation that can be extended later.
    """
    # Add your authentication/authorization logic here
    # Example (commented out):
    # if not is_authenticated(request):
    #     return JSONResponse(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         content={"detail": "Not authenticated"}
    #     )
    
    # Continue to the next middleware/route handler
    response = await call_next(request)
    return response

# Apply the middleware guard
app.middleware("http")(auth_guard)

app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(user.router, prefix="/api/v1/user", tags=["user"])
# NOTE: Route is defined as "/" (no trailing slash), so prefix should not end with a slash.
