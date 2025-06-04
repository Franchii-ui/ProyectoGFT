from pydantic import BaseModel
from enum import Enum
from typing import Optional

class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TranscriptionModel(str, Enum):
    WHISPER_1 = "whisper-1"

class TaskResponse(BaseModel):
    task_id: str
    status: TaskStatus
    message: str

class TranscriptionRequest(BaseModel):
    file_id: str
    language: Optional[str] = None
    prompt: Optional[str] = None
    response_format: Optional[str] = "json"
    temperature: Optional[float] = 0
    
class TranscriptionResult(BaseModel):
    task_id: str
    status: TaskStatus
    text: Optional[str] = None
    file_path: Optional[str] = None
    error: Optional[str] = None