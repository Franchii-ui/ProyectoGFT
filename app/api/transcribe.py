from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pydantic import BaseModel
from typing import Optional
import uuid
import os
from pathlib import Path
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
from openai import OpenAI
import app.config as config
import logging
from app.db import get_db
logger = logging.getLogger(__name__)
router = APIRouter()

client = OpenAI(api_key=config.OPENAI_API_KEY)

class TranscriptionResponse(BaseModel):
    success: bool
    file_id: str
    transcription: Optional[str] = None
    message: str

@router.post("/transcribe/", response_model=TranscriptionResponse)
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

        # Validate file size
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