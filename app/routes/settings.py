from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

ENV_PATH = BASE_DIR / ".env"


def _read_env() -> dict[str, str]:
    """Read key=value pairs from .env file."""
    values = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                values[key.strip()] = val.strip()
    return values


def _write_env(values: dict[str, str]):
    """Write key=value pairs to .env file."""
    lines = []
    for key, val in values.items():
        lines.append(f"{key}={val}")
    ENV_PATH.write_text("\n".join(lines) + "\n")


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, message: str = "", error: str = ""):
    env = _read_env()
    # Mask the API key for display
    raw_key = env.get("OPENAI_API_KEY", "")
    has_key = bool(raw_key) and raw_key not in ("sk-your-key-here", "PASTE_YOUR_NEW_KEY_HERE", "")
    masked_key = raw_key[:7] + "..." + raw_key[-4:] if has_key and len(raw_key) > 15 else ""

    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "has_key": has_key,
            "masked_key": masked_key,
            "keywords": env.get("JOB_SEARCH_KEYWORDS", "software engineer"),
            "location": env.get("JOB_SEARCH_LOCATION", "United States"),
            "message": message,
            "error": error,
        },
    )


@router.post("/settings")
async def save_settings(
    request: Request,
    openai_api_key: str = Form(default=""),
    keywords: str = Form(default="software engineer"),
    location: str = Form(default="United States"),
):
    env = _read_env()

    # Only update the key if a new one was provided
    if openai_api_key.strip() and openai_api_key.startswith("sk-"):
        env["OPENAI_API_KEY"] = openai_api_key.strip()
    elif not env.get("OPENAI_API_KEY"):
        env["OPENAI_API_KEY"] = ""

    env["JOB_SEARCH_KEYWORDS"] = keywords
    env["JOB_SEARCH_LOCATION"] = location
    env.setdefault("ADZUNA_APP_ID", "")
    env.setdefault("ADZUNA_APP_KEY", "")
    env["RESUME_PATH"] = "data/sample_resume.json"

    _write_env(env)

    logger.info("Settings saved via web UI")
    return RedirectResponse("/settings?message=Settings saved! You may need to restart the app for API key changes to take effect.", status_code=302)
