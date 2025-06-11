import logging
from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
import app.config as config
from app.api import export, transcribe, test, user
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import SessionLocal, init_db

logger = logging.getLogger(__name__)

app = FastAPI(
    title=config.APP_NAME,
    description="Video transcription service using OpenAI Whisper API",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL, e.g., ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again."}
    )

# Dependency to get the database session
async def get_db():
    async with SessionLocal() as session:
        yield session

# Include routers
app.include_router(export.router)
app.include_router(transcribe.router)
app.include_router(test.router)
app.include_router(user.router)

@app.on_event("startup")
async def on_startup():
    await init_db()