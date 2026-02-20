from __future__ import annotations

import json
import logging
from pathlib import Path

import fitz  # PyMuPDF
from docx import Document
from openai import AsyncOpenAI

from app.config import settings, BASE_DIR
from app.models import Resume

logger = logging.getLogger(__name__)

EXTRACT_PROMPT = """\
You are a resume parser. Given the raw text of a resume, extract structured data \
and return ONLY valid JSON (no markdown, no explanation) matching this exact schema:

{
  "name": "",
  "email": "",
  "phone": "",
  "location": "",
  "summary": "",
  "raw_text": "",
  "experience": [
    {
      "title": "",
      "company": "",
      "location": "",
      "start_date": "",
      "end_date": "",
      "bullets": [""]
    }
  ],
  "education": [
    {
      "degree": "",
      "school": "",
      "graduation_date": "",
      "gpa": ""
    }
  ],
  "skills": [""],
  "certifications": [""]
}

Rules:
- Extract ALL experience entries, education, and skills from the resume.
- Preserve wording from the resume verbatim whenever possible; do not summarize or paraphrase bullets.
- Set "raw_text" to the full unmodified resume text exactly as provided.
- For dates, use formats like "2022-01" or "Present".
- If a field isn't found, use an empty string or empty list.
- Return ONLY the JSON object, nothing else.\
"""


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file using PyMuPDF."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text_parts = []
    for page in doc:
        text_parts.append(page.get_text())
    doc.close()
    return "\n".join(text_parts)


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX file using python-docx."""
    import io
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join(para.text for para in doc.paragraphs if para.text.strip())


def extract_text(filename: str, file_bytes: bytes) -> str:
    """Route to the correct parser based on file extension."""
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_bytes)
    elif ext in (".docx", ".doc"):
        return extract_text_from_docx(file_bytes)
    elif ext == ".txt":
        return file_bytes.decode("utf-8", errors="replace")
    else:
        raise ValueError(f"Unsupported file type: {ext}. Use PDF, DOCX, or TXT.")


async def parse_resume_with_ai(raw_text: str) -> Resume:
    """Use OpenAI to extract structured resume data from raw text."""
    key = settings.openai_api_key
    if not key or key.startswith("PASTE") or key in ("your-api-key", "sk-xxx"):
        logger.warning("No valid OpenAI API key configured, using fallback parser")
        return _fallback_parse(raw_text)

    client = AsyncOpenAI(api_key=settings.openai_api_key)

    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": EXTRACT_PROMPT},
            {"role": "user", "content": raw_text},
        ],
        temperature=0.0,
    )

    content = response.choices[0].message.content or "{}"
    # Strip markdown code fences if the model wraps the JSON
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1] if "\n" in content else content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()

    data = json.loads(content)
    data.setdefault("raw_text", raw_text)
    return Resume(**data)


def _fallback_parse(raw_text: str) -> Resume:
    """Basic fallback: preserve raw resume text without truncation."""
    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
    return Resume(
        name=lines[0] if lines else "",
        summary="",
        raw_text=raw_text,
        skills=[],
    )


def save_resume(resume: Resume) -> Path:
    """Save parsed resume to the configured JSON path."""
    path = Path(BASE_DIR) / settings.resume_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(resume.model_dump(), f, indent=2)
    return path
