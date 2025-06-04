import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    APP_NAME: str = "GFT Video Converter"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static/uploads")
    RESULTS_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static/results")
    
    # Create directories if they don't exist
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    # File size limits (10MB for testing, increase as needed)
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Supported file formats
    SUPPORTED_VIDEO_FORMATS: list = [".mp4", ".avi", ".mov", ".mkv"]
    SUPPORTED_AUDIO_FORMATS: list = [".mp3", ".wav", ".m4a"]

settings = Settings()