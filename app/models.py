from __future__ import annotations

import enum
from datetime import datetime

from pydantic import BaseModel, Field


class JobStatus(str, enum.Enum):
    NEW = "new"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"


class JobPosting(BaseModel):
    id: int | None = None
    title: str
    company: str
    location: str = ""
    description: str = ""
    url: str = ""
    source: str = ""
    salary: str = ""
    date_posted: str = ""
    date_scraped: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    status: JobStatus = JobStatus.NEW
    keywords: str = ""

    # Generated documents
    tailored_resume: str = ""
    cover_letter: str = ""


class Resume(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    summary: str = ""
    experience: list[Experience] = []
    education: list[Education] = []
    skills: list[str] = []
    certifications: list[str] = []
    raw_text: str = ""  # verbatim text extracted from the uploaded file


class Experience(BaseModel):
    title: str
    company: str
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    bullets: list[str] = []


class Education(BaseModel):
    degree: str
    school: str
    graduation_date: str = ""
    gpa: str = ""
