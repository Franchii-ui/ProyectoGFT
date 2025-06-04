import os
import json
import uuid
import openai
import asyncio
from ..config import settings
from ..models import TaskStatus, TranscriptionResult, TranscriptionRequest
from ..utils.file_handler import get_file_path

# Set OpenAI API key
openai.api_key = settings.OPENAI_API_KEY

# Store tasks in memory (for simplicity - use a database in production)
tasks = {}

async def transcribe_audio(file_id: str, request: TranscriptionRequest) -> TranscriptionResult:
    """
    Process a transcription request asynchronously
    """
    task_id = str(uuid.uuid4())
    
    # Initialize task
    task = TranscriptionResult(
        task_id=task_id,
        status=TaskStatus.PENDING
    )
    tasks[task_id] = task
    
    # Start transcription in background
    asyncio.create_task(process_transcription(task_id, file_id, request))
    
    return task

async def process_transcription(task_id: str, file_id: str, request: TranscriptionRequest) -> None:
    """
    Process the transcription using OpenAI Whisper API
    """
    task = tasks[task_id]
    task.status = TaskStatus.PROCESSING
    
    try:
        # Get file path
        file_path = get_file_path(file_id)
        
        # Update with actual API call
        with open(file_path, "rb") as audio_file:
            # Call OpenAI Whisper API
            response = await openai.Audio.atranscribe(
                model="whisper-1",
                file=audio_file,
                language=request.language,
                prompt=request.prompt,
                response_format=request.response_format,
                temperature=request.temperature
            )
        
        # Save the transcription result
        result_filename = f"{task_id}.json"
        result_path = os.path.join(settings.RESULTS_DIR, result_filename)
        
        with open(result_path, "w") as f:
            json.dump(response, f)
        
        # Update task with result
        task.status = TaskStatus.COMPLETED
        task.text = response.get("text", "")
        task.file_path = result_filename
        
    except Exception as e:
        # Handle errors
        task.status = TaskStatus.FAILED
        task.error = str(e)

async def get_task_status(task_id: str) -> TranscriptionResult:
    """Get the status of a transcription task"""
    if task_id not in tasks:
        raise Exception("Task not found")
    
    return tasks[task_id]