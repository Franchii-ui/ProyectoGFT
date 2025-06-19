from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from openai import OpenAI
import app.config as config
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.models.user import User
from app.db import get_db
logger = logging.getLogger(__name__)
router = APIRouter()

client = OpenAI(api_key=config.OPENAI_API_KEY)

@router.get("/test-openai")
async def test_openai():
    """
    Test OpenAI API connectivity.
    """
    try:
        # This is a lightweight call to check API status (list models)
        models = client.models.list()
        logger.info("OpenAI API test successful.")
        return JSONResponse(content={"success": True, "message": "OpenAI API is reachable.", "model_count": len(models.data)})
    except Exception as e:
        logger.error(f"OpenAI API test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OpenAI API test failed: {str(e)}")

#@router.get("/test-db")
#async def test_db(db: AsyncSession = Depends(get_db)):
    # Create a test user
    user = User(username="testuser", email="test@example.com")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"id": user.id, "username": user.username, "email": user.email}