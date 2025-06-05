import os
import uuid
import logging
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse  # Add HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from pydantic import BaseModel
from openai import OpenAI  # Import this way for newer versions
from moviepy.editor import VideoFileClip
from pathlib import Path
import uvicorn
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings
from pydub import AudioSegment
from app.utils.document_converter import text_to_docx, text_to_pdf, text_to_html
from enum import Enum

# Import configuration
import app.config as config

# Set environment variables for Uvicorn
os.environ["UVICORN_MAX_REQUEST_SIZE"] = "200000000"  # 200 MB in bytes
os.environ["UVICORN_LIMIT_CONCURRENCY"] = "5"
os.environ["UVICORN_TIMEOUT_KEEP_ALIVE"] = "120"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Models
class TranscriptionResponse(BaseModel):
    success: bool
    file_id: str
    transcription: Optional[str] = None
    message: str

class DocumentFormat(str, Enum):
    DOCX = "docx"
    PDF = "pdf"
    HTML = "html"
    TXT = "txt"

# Initialize FastAPI app
app = FastAPI(
    title=config.APP_NAME,
    description="Video transcription service using OpenAI Whisper API",
    version="0.1.0"
)

# Add CORS middleware right here, after initializing the app
# Only use this in development, not in production!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = OpenAI(api_key=config.OPENAI_API_KEY)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return {"message": f"Welcome to {config.APP_NAME}"}

@app.post("/transcribe/", response_model=TranscriptionResponse)
async def transcribe_video(
    file: UploadFile = File(...),
    language: Optional[str] = Form(None)
):
    """
    Upload and transcribe a video/audio file
    """
    file_path = None
    audio_path = None
    compressed_path = None
    is_video = False
    
    try:
        logger.info(f"Received file: {file.filename}")
        
        # Read file content
        file_contents = await file.read()
        file_size = len(file_contents)
        
        # Reset file pointer
        await file.seek(0)
        
        # Validate file size (your app's limit)
        if file_size > config.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {config.MAX_FILE_SIZE/1024/1024}MB"
            )
        
        # Get file extension and validate
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in config.SUPPORTED_FORMATS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Supported formats: {', '.join(config.SUPPORTED_FORMATS)}"
            )
        
        # Generate unique ID and save file
        unique_id = str(uuid.uuid4())
        file_path = config.UPLOAD_DIR / f"{unique_id}{file_ext}"
        
        logger.info(f"Saving file to: {file_path}")
        with open(file_path, "wb") as buffer:
            buffer.write(file_contents)
        
        # Process based on file type
        is_video = file_ext in config.SUPPORTED_VIDEO_FORMATS
        audio_path = file_path
        
        # Extract audio from video if needed
        if is_video:
            logger.info(f"Extracting audio from video: {file_path}")
            audio_path = config.UPLOAD_DIR / f"{unique_id}.mp3"
            
            try:
                video = VideoFileClip(str(file_path))
                video.audio.write_audiofile(
                    str(audio_path),
                    logger=None
                )
                video.close()
                logger.info(f"Audio extracted to: {audio_path}")
            except Exception as e:
                logger.error(f"Error extracting audio: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error extracting audio: {str(e)}"
                )
        
        # Check audio file size for OpenAI API limit (25MB)
        OPENAI_SIZE_LIMIT = 25 * 1024 * 1024
        audio_size = os.path.getsize(audio_path)
        
        # If file is larger than OpenAI's limit, compress it
        if audio_size > OPENAI_SIZE_LIMIT:
            logger.info(f"Audio file size ({audio_size/(1024*1024):.2f} MB) exceeds OpenAI limit. Compressing...")
            
            compressed_path = config.UPLOAD_DIR / f"{unique_id}_compressed.mp3"
            
            # Load the audio file with pydub
            audio = AudioSegment.from_file(str(audio_path))
            
            # Try different bitrates until file is small enough
            for bitrate in ["64k", "48k", "32k", "24k", "16k"]:
                logger.info(f"Trying compression with bitrate: {bitrate}")
                
                # Export with reduced bitrate
                audio.export(
                    str(compressed_path),
                    format="mp3",
                    bitrate=bitrate
                )
                
                # Check if file is now small enough
                compressed_size = os.path.getsize(compressed_path)
                logger.info(f"Compressed size: {compressed_size/(1024*1024):.2f} MB")
                
                if compressed_size <= OPENAI_SIZE_LIMIT:
                    logger.info(f"Compression successful with bitrate {bitrate}")
                    # Use the compressed file for transcription
                    audio_path = compressed_path
                    break
            
            # If still too large after compression, inform the user
            if os.path.getsize(audio_path) > OPENAI_SIZE_LIMIT:
                raise HTTPException(
                    status_code=413,
                    detail="File too large for transcription even after compression. Please use a smaller file."
                )
        
        # Transcribe using OpenAI API
        logger.info(f"Transcribing audio: {audio_path}")
        try:
            with open(audio_path, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language if language else None
                )
            
            # Access transcription text
            transcription_text = transcription.text
            
            # Save transcription result
            result_path = config.RESULTS_DIR / f"{unique_id}.txt"
            with open(result_path, "w") as f:
                f.write(transcription_text)
            
            logger.info(f"Transcription saved to: {result_path}")
            
            return TranscriptionResponse(
                success=True,
                file_id=unique_id,
                transcription=transcription_text,
                message="Transcription completed successfully"
            )
            
        except Exception as e:
            logger.error(f"Error during transcription: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Transcription error: {str(e)}"
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )
        
    finally:
        # Clean up files
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Removed uploaded file: {file_path}")
                
            if is_video and audio_path and audio_path != file_path and os.path.exists(audio_path):
                os.remove(audio_path)
                logger.info(f"Removed temporary audio file: {audio_path}")
                
            if compressed_path and compressed_path != audio_path and os.path.exists(compressed_path):
                os.remove(compressed_path)
                logger.info(f"Removed compressed audio file: {compressed_path}")
                
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

@app.get("/download/{file_id}")
async def download_transcription(file_id: str):
    """
    Download a transcription result
    """
    file_path = config.RESULTS_DIR / f"{file_id}.txt"
    
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Transcription not found"
        )
    
    return FileResponse(
        path=str(file_path),
        filename=f"transcription_{file_id}.txt",
        media_type="text/plain"
    )

@app.get("/export/{file_id}")
async def export_transcription(file_id: str, format: DocumentFormat = DocumentFormat.DOCX):
    """
    Export a transcription to various document formats
    """
    # Check if transcription exists
    txt_path = config.RESULTS_DIR / f"{file_id}.txt"
    
    if not txt_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Transcription not found"
        )
    
    try:
        # Read the transcription text
        with open(txt_path, 'r') as f:
            transcription_text = f.read()
        
        # Generate output path based on format
        output_filename = f"{file_id}.{format}"
        output_path = config.RESULTS_DIR / output_filename
        
        # Convert to requested format
        if format == DocumentFormat.DOCX:
            output_path = text_to_docx(transcription_text, output_path)
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif format == DocumentFormat.PDF:
            output_path = text_to_pdf(transcription_text, output_path)
            media_type = "application/pdf"
        elif format == DocumentFormat.HTML:
            output_path = text_to_html(transcription_text, output_path)
            media_type = "text/html"
        else:  # TXT - already supported
            output_path = txt_path
            media_type = "text/plain"
        
        return FileResponse(
            path=str(output_path),
            filename=f"transcription_{file_id}.{format}",
            media_type=media_type
        )
    
    except Exception as e:
        logger.error(f"Error exporting transcription: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error exporting transcription: {str(e)}"
        )

# Add a web-based editor endpoint (optional)
@app.get("/edit/{file_id}", response_class=HTMLResponse)
async def edit_transcription(file_id: str, request: Request):
    """
    Provide a web-based editor for transcriptions
    """
    # Check if transcription exists
    txt_path = config.RESULTS_DIR / f"{file_id}.txt"
    
    if not txt_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Transcription not found"
        )
    
    # Read the transcription text
    with open(txt_path, 'r') as f:
        transcription_text = f.read()
    
    # Create a simple HTML editor
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Edit Transcription</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
            h1 {{ color: #333; text-align: center; }}
            textarea {{ width: 100%; height: 400px; padding: 10px; font-family: Arial, sans-serif; margin-bottom: 20px; }}
            .actions {{ display: flex; justify-content: space-between; }}
            button {{ padding: 10px 15px; background-color: #4CAF50; color: white; border: none; cursor: pointer; }}
            .export-options {{ margin-top: 20px; }}
            .export-options a {{ margin-right: 15px; text-decoration: none; color: #0066cc; }}
        </style>
    </head>
    <body>
        <h1>Edit Transcription</h1>
        <form id="editForm">
            <input type="hidden" id="fileId" value="{file_id}">
            <textarea id="transcriptionText">{transcription_text}</textarea>
            <div class="actions">
                <button type="submit">Save Changes</button>
            </div>
        </form>
        
        <div class="export-options">
            <h3>Export as:</h3>
            <a href="/export/{file_id}?format=docx" target="_blank">DOCX</a>
            <a href="/export/{file_id}?format=pdf" target="_blank">PDF</a>
            <a href="/export/{file_id}?format=html" target="_blank">HTML</a>
            <a href="/download/{file_id}" target="_blank">TXT</a>
        </div>
        
        <script>
            document.getElementById('editForm').addEventListener('submit', async function(e) {{
                e.preventDefault();
                
                const fileId = document.getElementById('fileId').value;
                const text = document.getElementById('transcriptionText').value;
                
                try {{
                    const response = await fetch('/save/{file_id}', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify({{ text: text }})
                    }});
                    
                    const result = await response.json();
                    
                    if (response.ok) {{
                        alert('Transcription saved successfully!');
                    }} else {{
                        alert(`Error: ${{result.detail || 'Unknown error'}}`);
                    }}
                }} catch (error) {{
                    alert(`Error: ${{error.message}}`);
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

# Add this endpoint to save edited transcriptions
@app.post("/save/{file_id}")
async def save_transcription(file_id: str, data: dict):
    """
    Save edited transcription
    """
    txt_path = config.RESULTS_DIR / f"{file_id}.txt"
    
    if not txt_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Transcription not found"
        )
    
    try:
        # Get the text from the request
        text = data.get("text", "")
        
        # Save to file
        with open(txt_path, 'w') as f:
            f.write(text)
        
        return {"success": True, "message": "Transcription saved successfully"}
    
    except Exception as e:
        logger.error(f"Error saving transcription: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error saving transcription: {str(e)}"
        )

@app.get("/test-openai")
async def test_openai():
    """Test OpenAI API connection"""
    try:
        # Just a simple test to check if client is working
        models = client.models.list()
        return {"success": True, "message": "OpenAI API connection successful"}
    except Exception as e:
        logger.error(f"OpenAI API test failed: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}

# Error handler for graceful error responses
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again."}
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        limit_concurrency=5,
        timeout_keep_alive=120,
        limit_max_requests=1000,
        # The most important setting for large files:
        http="h11",
        loop="asyncio"
    )