from __future__ import annotations

import json
import logging

from openai import AsyncOpenAI

from app.config import settings
from app.models import Resume

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are an expert career coach who writes compelling, concise cover letters. \
Write a cover letter that:

1. Opens with a strong hook specific to the company and role.
2. Connects the candidate's most relevant experience to the job requirements.
3. Uses natural language — avoid clichés like "I am writing to express my interest".
4. Mirrors key terminology from the job description without sounding forced.
5. Is 250–350 words (three to four paragraphs).
6. Closes with a confident call to action.

Return the cover letter as plain text (not Markdown). Include a placeholder \
"[Today's Date]" at the top and "[Your Name]" at the bottom.\
"""


async def draft_cover_letter(
    resume: Resume, job_title: str, company: str, job_description: str
) -> str:
    """Use OpenAI to draft a cover letter tailored to the job."""
    if not settings.openai_api_key:
        return _fallback_letter(resume, job_title, company)

    client = AsyncOpenAI(api_key=settings.openai_api_key)

    resume_content = resume.raw_text if resume.raw_text else json.dumps(resume.model_dump(), indent=2)

    user_prompt = f"""\
## Target Position
**Title:** {job_title}
**Company:** {company}

**Job Description:**
{job_description}

## Candidate Background
{resume_content}

Please write a concise, tailored cover letter.\
"""

    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=1500,
    )

    return response.choices[0].message.content or ""


def _fallback_letter(resume: Resume, job_title: str, company: str) -> str:
    """Basic template fallback when no API key is configured."""
    return f"""\
[Today's Date]

Dear Hiring Manager,

I am excited to apply for the {job_title} position at {company}. With my background \
as {resume.experience[0].title if resume.experience else 'a professional'} at \
{resume.experience[0].company if resume.experience else 'my current organization'}, \
I bring a strong foundation in {', '.join(resume.skills[:5])}.

{resume.summary}

I look forward to discussing how my experience aligns with your team's goals. \
Thank you for considering my application.

Sincerely,
{resume.name}
"""
