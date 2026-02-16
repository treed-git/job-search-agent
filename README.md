# Job Search Agent

Scrapes job postings from multiple boards, lets you review them in a web dashboard, and — when you approve a job — uses OpenAI to tailor your resume and draft a cover letter.

## Features

- **Multi-source scraping** — Indeed, LinkedIn, Glassdoor, and Adzuna (API)
- **Web dashboard** — Browse, filter, and search scraped jobs
- **One-click approve** — Approve a job and instantly generate documents
- **AI resume tailoring** — Rewrites your resume to match the job description's terminology
- **AI cover letters** — Drafts a concise, role-specific cover letter
- **Fallback mode** — Works without an API key using keyword matching and templates

## Quick Start (Easy)

Just run the startup script — it handles everything:

```bash
./start.sh
```

It will:
1. Ask for your OpenAI API key (first time only)
2. Install dependencies automatically
3. Start the app

Then open **http://127.0.0.1:8000** in your browser.

Before running, edit `data/sample_resume.json` with your real resume info.

## Manual Setup (Advanced)

If you prefer to set things up yourself:

```bash
python -m venv .venv
source .venv/bin/activate
pip install .
cp .env.example .env
# Edit .env with your OPENAI_API_KEY
python -m app.main
```

**Required for AI features:**
- `OPENAI_API_KEY` — get one at https://platform.openai.com/api-keys

**Optional (improves scraping):**
- `ADZUNA_APP_ID` / `ADZUNA_APP_KEY` — free at https://developer.adzuna.com/

## Usage

1. **Scrape jobs** — Enter keywords and location on the dashboard, then click "Search & Scrape"
2. **Review** — Click into any job to read the full description
3. **Approve** — Click "Approve & Generate Resume + Cover Letter" to create tailored documents
4. **Reject** — Mark jobs you're not interested in to keep your list clean
5. **Filter** — Use the status and search filters to focus on what matters

## Project Structure

```
app/
├── main.py              # FastAPI entry point
├── config.py            # Settings (loaded from .env)
├── database.py          # SQLite via aiosqlite
├── models.py            # Pydantic data models
├── scrapers/
│   ├── base.py          # Base scraper with rate limiting
│   ├── indeed.py        # Indeed scraper
│   ├── linkedin.py      # LinkedIn public listings
│   ├── glassdoor.py     # Glassdoor scraper
│   └── adzuna.py        # Adzuna API client
├── ai/
│   ├── resume_tailor.py # AI resume tailoring
│   └── cover_letter.py  # AI cover letter drafting
├── routes/
│   ├── jobs.py          # Job listing & scraping routes
│   └── documents.py     # Document generation routes
└── templates/           # Jinja2 HTML templates
data/
└── sample_resume.json   # Your resume (edit this)
```

## Notes

- Web scraping results depend on the current structure of job board pages. Scrapers may need updates if sites change their HTML.
- Adzuna is the most reliable source since it uses an official API.
- The app uses SQLite for storage — no external database required.
- Rate limiting is built into all scrapers to be respectful of source sites.
