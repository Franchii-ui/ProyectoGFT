import os
import json
from pathlib import Path
from docx import Document
from fpdf import FPDF
from jinja2 import Template
import logging

logger = logging.getLogger(__name__)

def text_to_docx(text: str, output_path: Path) -> Path:
    """Convert plain text to DOCX format"""
    try:
        # Create new Document
        doc = Document()
        
        # Add title
        doc.add_heading('Transcription', level=1)
        
        # Split by paragraphs and add each paragraph
        paragraphs = text.split('\n\n')
        for para in paragraphs:
            if para.strip():
                doc.add_paragraph(para.strip())
        
        # Save document
        doc.save(output_path)
        return output_path
    
    except Exception as e:
        logger.error(f"Error creating DOCX document: {str(e)}")
        raise

def text_to_pdf(text: str, output_path: Path) -> Path:
    """Convert plain text to PDF format"""
    try:
        # Create PDF object
        pdf = FPDF()
        pdf.add_page()
        
        # Set font
        pdf.set_font("Arial", size=12)
        
        # Add title
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="Transcription", ln=True, align='C')
        pdf.ln(10)
        
        # Reset to normal font
        pdf.set_font("Arial", size=12)
        
        # Split by paragraphs and add each paragraph
        paragraphs = text.split('\n\n')
        for para in paragraphs:
            if para.strip():
                # Handle multi-line text
                pdf.multi_cell(0, 10, txt=para.strip())
                pdf.ln(5)
        
        # Save PDF
        pdf.output(output_path)
        return output_path
    
    except Exception as e:
        logger.error(f"Error creating PDF document: {str(e)}")
        raise

def text_to_html(text: str, output_path: Path) -> Path:
    """Convert plain text to HTML format"""
    try:
        # Simple HTML template
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Transcription</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1 { color: #333; text-align: center; }
                p { margin-bottom: 16px; }
            </style>
        </head>
        <body>
            <h1>Transcription</h1>
            {% for paragraph in paragraphs %}
                <p>{{ paragraph }}</p>
            {% endfor %}
        </body>
        </html>
        """
        
        # Prepare template
        template = Template(html_template)
        
        # Split text into paragraphs
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        # Render HTML
        html_content = template.render(paragraphs=paragraphs)
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error creating HTML document: {str(e)}")
        raise