from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from openai import OpenAI
import app.config as config
import logging

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