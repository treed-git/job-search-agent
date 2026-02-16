from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.database import get_jobs, get_job, insert_job, update_job_status
from app.models import JobStatus
from app.scrapers import ALL_SCRAPERS

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def job_list(
    request: Request,
    status: str = "",
    search: str = "",
):
    """Main dashboard — lists all scraped jobs."""
    filter_status = JobStatus(status) if status else None
    jobs = await get_jobs(status=filter_status, search=search)
    return templates.TemplateResponse(
        "jobs.html",
        {
            "request": request,
            "jobs": jobs,
            "current_status": status,
            "search": search,
            "statuses": [s.value for s in JobStatus],
        },
    )


@router.get("/jobs/{job_id}", response_class=HTMLResponse)
async def job_detail(request: Request, job_id: int):
    """View a single job's full details, tailored resume, and cover letter."""
    job = await get_job(job_id)
    if not job:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse(
        "job_detail.html",
        {"request": request, "job": job},
    )


@router.post("/jobs/{job_id}/status")
async def set_job_status(job_id: int, status: str = Form(...)):
    """Update a job's review status."""
    await update_job_status(job_id, JobStatus(status))
    return RedirectResponse(f"/jobs/{job_id}", status_code=302)


@router.post("/scrape", response_class=HTMLResponse)
async def scrape_jobs(
    request: Request,
    keywords: str = Form(default=""),
    location: str = Form(default=""),
):
    """Run scrapers and store results in the database."""
    kw = keywords or settings.job_search_keywords
    loc = location or settings.job_search_location

    async def run_scraper(scraper_cls):
        scraper = scraper_cls()
        try:
            return await scraper.scrape(kw, loc)
        except Exception as e:
            logger.error(f"[{scraper.name}] Scraper failed: {e}")
            return []

    results = await asyncio.gather(*[run_scraper(cls) for cls in ALL_SCRAPERS])
    inserted = 0
    for job_list in results:
        for job in job_list:
            row_id = await insert_job(job)
            if row_id:
                inserted += 1

    logger.info(f"Scraping complete: {inserted} new jobs inserted")
    return RedirectResponse(f"/?search={kw}", status_code=302)
