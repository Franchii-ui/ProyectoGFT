from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
from typing import Optional
from app.utils import document_converter
import app.config as config
import logging
from enum import Enum

logger = logging.getLogger(__name__)
router = APIRouter()

class DocumentFormat(str, Enum):
    TXT = "txt"
    DOCX = "docx"
    PDF = "pdf"
    HTML = "html"

@router.get("/download/{file_id}")
async def download_transcription(file_id: str):
    file_path = config.RESULTS_DIR / f"{file_id}.txt"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Transcription not found")
    return FileResponse(
        path=str(file_path),
        filename=f"transcription_{file_id}.txt",
        media_type="text/plain"
    )

@router.get("/export/{file_id}")
async def export_transcription(file_id: str, format: DocumentFormat = DocumentFormat.PDF):
    txt_path = config.RESULTS_DIR / f"{file_id}.txt"
    if not txt_path.exists():
        raise HTTPException(status_code=404, detail="Transcription not found")
    with open(txt_path, 'r') as f:
        transcription_text = f.read()
    output_filename = f"{file_id}.{format}"
    output_path = config.RESULTS_DIR / output_filename
    if format == DocumentFormat.DOCX:
        output_path = document_converter.text_to_docx(transcription_text, output_path)
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif format == DocumentFormat.PDF:
        output_path = document_converter.text_to_pdf(transcription_text, output_path)
        media_type = "application/pdf"
    elif format == DocumentFormat.HTML:
        output_path = document_converter.text_to_html(transcription_text, output_path)
        media_type = "text/html"
    else:
        output_path = txt_path
        media_type = "text/plain"
    return FileResponse(
        path=str(output_path),
        filename=f"transcription_{file_id}.{format}",
        media_type=media_type
    )

@router.post("/edit/{file_id}")
async def edit_transcription(file_id: str, text: str = Form(...)):
    txt_path = config.RESULTS_DIR / f"{file_id}.txt"
    if not txt_path.exists():
        raise HTTPException(status_code=404, detail="Transcription not found")
    with open(txt_path, "w") as f:
        f.write(text)
    return JSONResponse(content={"success": True, "message": "Transcription updated."})

@router.post("/save/{file_id}")
async def save_transcription(file_id: str, request: Request):
    data = await request.json()
    text = data.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="No text provided")
    txt_path = config.RESULTS_DIR / f"{file_id}.txt"
    with open(txt_path, "w") as f:
        f.write(text)
    return JSONResponse(content={"success": True, "message": "Transcription saved."})