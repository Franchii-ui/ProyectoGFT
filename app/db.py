import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import Base
from app.models.transcription import Transcription  # if needed

# Old local database URL (for reference)
# DATABASE_URL = "postgresql+asyncpg://postgres:12345678@localhost:5432/franchi"

# Use DATABASE_URL from environment variable for Railway and production
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with SessionLocal() as session:
        yield session