from __future__ import annotations

import json
import logging
from pathlib import Path

from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import settings, BASE_DIR
from app.models import Resume
from app.ai.resume_parser import extract_text, parse_resume_with_ai, save_resume

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def _load_current_resume() -> Resume | None:
    path = Path(BASE_DIR) / settings.resume_path
    if not path.exists():
        return None
    try:
        with open(path) as f:
            data = json.load(f)
        return Resume(**data)
    except Exception as e:
        logger.error(f"Failed to load resume from {path}: {e}")
        return None


@router.get("/resume", response_class=HTMLResponse)
async def resume_page(request: Request, message: str = "", error: str = ""):
    """Resume upload and preview page."""
    resume = _load_current_resume()
    has_resume = resume is not None
    return templates.TemplateResponse(
        "resume.html",
        {
            "request": request,
            "resume": resume,
            "has_resume": has_resume,
            "message": message,
            "error": error,
        },
    )


@router.post("/resume/upload")
async def upload_resume(request: Request, file: UploadFile = File(...)):
    """Handle resume file upload, parse it, and save structured JSON."""
    # Validate file extension
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return RedirectResponse(
            f"/resume?error=Unsupported file type: {ext}. Please upload a PDF, DOCX, or TXT file.",
            status_code=302,
        )

    # Read file
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        return RedirectResponse("/resume?error=File too large. Maximum size is 10 MB.", status_code=302)

    if len(file_bytes) == 0:
        return RedirectResponse("/resume?error=File appears to be empty.", status_code=302)

    try:
        # Extract text from file
        raw_text = extract_text(file.filename or "file.pdf", file_bytes)

        if not raw_text.strip():
            return RedirectResponse(
                "/resume?error=Could not extract text from the file. Try a different format.",
                status_code=303,
            )

        # Use AI to parse into structured resume
        resume = await parse_resume_with_ai(raw_text)

        # Always preserve the verbatim extracted text
        resume.raw_text = raw_text

        # Save to disk
        save_resume(resume)

        logger.info(f"Resume uploaded and parsed: {resume.name}")

        # Render page directly with the parsed resume so it displays
        # immediately, rather than redirecting and re-loading from disk.
        return templates.TemplateResponse(
            "resume.html",
            {
                "request": request,
                "resume": resume,
                "has_resume": True,
                "message": "Resume uploaded and parsed successfully!",
                "error": "",
            },
        )

    except Exception as e:
        logger.error(f"Resume upload failed: {e}")
        return RedirectResponse(f"/resume?error=Failed to parse resume: {e}", status_code=303)
