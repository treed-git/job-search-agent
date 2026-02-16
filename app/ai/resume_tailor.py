from __future__ import annotations

import json
import logging

from openai import AsyncOpenAI

from app.config import settings
from app.models import Resume

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are an expert resume writer. Your job is to tailor a candidate's resume to \
match a specific job description. You should:

1. Rewrite the professional summary to align with the target role.
2. Reorder and rephrase experience bullet points to emphasize relevant skills \
   and accomplishments that map to the job description.
3. Incorporate key terminology, tools, and frameworks mentioned in the job posting \
   naturally into the resume — do NOT fabricate experience the candidate doesn't have.
4. Highlight the most relevant skills from the candidate's skill list and add any \
   that are implied by their experience but missing.
5. Keep the resume concise (aim for one to two pages worth of content).

Return the tailored resume as well-formatted Markdown.\
"""


async def tailor_resume(resume: Resume, job_title: str, job_description: str) -> str:
    """Use OpenAI to tailor the resume to a specific job description."""
    if not settings.openai_api_key:
        return _fallback_tailor(resume, job_description)

    client = AsyncOpenAI(api_key=settings.openai_api_key)

    user_prompt = f"""\
## Target Job
**Title:** {job_title}

**Description:**
{job_description}

## Candidate Resume (raw data)
{json.dumps(resume.model_dump(), indent=2)}

Please produce a tailored resume in Markdown format.\
"""

    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
        max_tokens=3000,
    )

    return response.choices[0].message.content or ""


def _fallback_tailor(resume: Resume, job_description: str) -> str:
    """Simple keyword-matching fallback when no API key is set."""
    jd_lower = job_description.lower()
    matched_skills = [s for s in resume.skills if s.lower() in jd_lower]

    lines = [
        f"# {resume.name}",
        f"{resume.email} | {resume.phone} | {resume.location}",
        "",
        "## Summary",
        resume.summary,
        "",
        "## Relevant Skills",
        ", ".join(matched_skills) if matched_skills else ", ".join(resume.skills[:10]),
        "",
        "## Experience",
    ]
    for exp in resume.experience:
        lines.append(f"### {exp.title} — {exp.company}")
        lines.append(f"*{exp.start_date} – {exp.end_date}* | {exp.location}")
        for b in exp.bullets:
            lines.append(f"- {b}")
        lines.append("")

    lines.append("## Education")
    for edu in resume.education:
        lines.append(f"**{edu.degree}** — {edu.school} ({edu.graduation_date})")

    return "\n".join(lines)
