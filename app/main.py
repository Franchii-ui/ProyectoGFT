import os
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional

from .config import settings
from .models import TaskResponse, TaskStatus, TranscriptionRequest, TranscriptionResult
from .utils.file_handler import save_upload_file, get_file_path
from .services.transcription import transcribe_audio, get_task_status

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Video conversion and transcription service using OpenAI Whisper API",
    version="0.1.0"
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return {"message": f"Welcome to {settings.APP_NAME}"}

@app.post("/upload/", response_model=TaskResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload a video or audio file for processing"""
    try:
        file_id = await save_upload_file(file)
        return TaskResponse(
            task_id=file_id,
            status=TaskStatus.PENDING,
            message="File uploaded successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transcribe/", response_model=TranscriptionResult)
async def transcribe_file(request: TranscriptionRequest):
    """Start transcription for an uploaded file"""
    try:
        # Verify file exists
        get_file_path(request.file_id)
        
        # Start transcription process
        task = await transcribe_audio(request.file_id, request)
        return task
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/task/{task_id}", response_model=TranscriptionResult)
async def check_task(task_id: str):
    """Check the status of a transcription task"""
    try:
        return await get_task_status(task_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/download/{file_id}")
async def download_result(file_id: str):
    """Download a transcription result file"""
    file_path = os.path.join(settings.RESULTS_DIR, f"{file_id}.json")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Result file not found")
    
    return FileResponse(
        path=file_path,
        filename=f"transcription_{file_id}.json",
        media_type="application/json"
    )

# For debugging purposes
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)