import os
import uuid
import shutil
from fastapi import UploadFile, HTTPException
from ..config import settings

async def save_upload_file(file: UploadFile) -> str:
    """
    Save an uploaded file to the uploads directory
    Returns the file path
    """
    # Validate file size
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE/1024/1024}MB"
        )
    
    # Generate a unique filename to prevent collisions
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    # Validate file extension
    if (file_extension not in settings.SUPPORTED_VIDEO_FORMATS and 
        file_extension not in settings.SUPPORTED_AUDIO_FORMATS):
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file format. Supported formats are: {', '.join(settings.SUPPORTED_VIDEO_FORMATS + settings.SUPPORTED_AUDIO_FORMATS)}"
        )
    
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    # Save the file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return unique_filename

def get_file_path(file_id: str) -> str:
    """Get the full path to a file by its ID"""
    for filename in os.listdir(settings.UPLOAD_DIR):
        if filename.startswith(file_id):
            return os.path.join(settings.UPLOAD_DIR, filename)
    
    raise HTTPException(status_code=404, detail="File not found")