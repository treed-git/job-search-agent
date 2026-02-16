from __future__ import annotations

import json
import logging
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import settings, BASE_DIR
from app.database import get_job, save_generated_docs, update_job_status
from app.models import Resume, JobStatus
from app.ai.resume_tailor import tailor_resume
from app.ai.cover_letter import draft_cover_letter

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def load_resume() -> Resume:
    path = Path(BASE_DIR) / settings.resume_path
    if not path.exists():
        logger.warning(f"Resume file not found at {path}")
        return Resume()
    with open(path) as f:
        return Resume(**json.load(f))


@router.post("/jobs/{job_id}/generate")
async def generate_documents(request: Request, job_id: int):
    """Generate a tailored resume and cover letter for an approved job."""
    job = await get_job(job_id)
    if not job:
        return RedirectResponse("/", status_code=302)

    resume = load_resume()

    tailored = await tailor_resume(resume, job.title, job.description)
    letter = await draft_cover_letter(resume, job.title, job.company, job.description)

    await save_generated_docs(job_id, tailored, letter)
    await update_job_status(job_id, JobStatus.APPROVED)

    return RedirectResponse(f"/jobs/{job_id}", status_code=302)


@router.get("/jobs/{job_id}/resume", response_class=HTMLResponse)
async def view_resume(request: Request, job_id: int):
    job = await get_job(job_id)
    if not job:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse(
        "document.html",
        {"request": request, "job": job, "doc_type": "resume", "content": job.tailored_resume},
    )


@router.get("/jobs/{job_id}/cover-letter", response_class=HTMLResponse)
async def view_cover_letter(request: Request, job_id: int):
    job = await get_job(job_id)
    if not job:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse(
        "document.html",
        {"request": request, "job": job, "doc_type": "cover_letter", "content": job.cover_letter},
    )
