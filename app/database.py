from __future__ import annotations

import aiosqlite

from app.config import settings, DATA_DIR
from app.models import JobPosting, JobStatus

DB_PATH = DATA_DIR / settings.database_path.split("/")[-1]

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT DEFAULT '',
    description TEXT DEFAULT '',
    url TEXT DEFAULT '' UNIQUE,
    source TEXT DEFAULT '',
    salary TEXT DEFAULT '',
    date_posted TEXT DEFAULT '',
    date_scraped TEXT DEFAULT '',
    status TEXT DEFAULT 'new',
    keywords TEXT DEFAULT '',
    tailored_resume TEXT DEFAULT '',
    cover_letter TEXT DEFAULT ''
);
"""


async def get_db() -> aiosqlite.Connection:
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db


async def init_db():
    db = await get_db()
    try:
        await db.execute(CREATE_TABLE)
        await db.commit()
    finally:
        await db.close()


async def insert_job(job: JobPosting) -> int | None:
    """Insert a job, ignoring duplicates by URL. Returns the job id or None if duplicate."""
    db = await get_db()
    try:
        cursor = await db.execute(
            """INSERT OR IGNORE INTO jobs
               (title, company, location, description, url, source, salary, date_posted, date_scraped, status, keywords)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                job.title, job.company, job.location, job.description, job.url,
                job.source, job.salary, job.date_posted, job.date_scraped,
                job.status.value, job.keywords,
            ),
        )
        await db.commit()
        return cursor.lastrowid if cursor.rowcount > 0 else None
    finally:
        await db.close()


async def get_jobs(status: JobStatus | None = None, search: str = "") -> list[JobPosting]:
    db = await get_db()
    try:
        query = "SELECT * FROM jobs"
        params: list = []
        conditions = []

        if status:
            conditions.append("status = ?")
            params.append(status.value)
        if search:
            conditions.append("(title LIKE ? OR company LIKE ? OR description LIKE ?)")
            wildcard = f"%{search}%"
            params.extend([wildcard, wildcard, wildcard])

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY date_scraped DESC"

        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        return [JobPosting(**dict(row)) for row in rows]
    finally:
        await db.close()


async def get_job(job_id: int) -> JobPosting | None:
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        row = await cursor.fetchone()
        return JobPosting(**dict(row)) if row else None
    finally:
        await db.close()


async def update_job_status(job_id: int, status: JobStatus):
    db = await get_db()
    try:
        await db.execute("UPDATE jobs SET status = ? WHERE id = ?", (status.value, job_id))
        await db.commit()
    finally:
        await db.close()


async def save_generated_docs(job_id: int, tailored_resume: str, cover_letter: str):
    db = await get_db()
    try:
        await db.execute(
            "UPDATE jobs SET tailored_resume = ?, cover_letter = ? WHERE id = ?",
            (tailored_resume, cover_letter, job_id),
        )
        await db.commit()
    finally:
        await db.close()
