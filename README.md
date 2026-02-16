# Job Search Agent

Scrapes job postings from multiple boards, lets you review them in a web dashboard, and — when you approve a job — uses OpenAI to tailor your resume and draft a cover letter.

## Features

- **Multi-source scraping** — Indeed, LinkedIn, Glassdoor, and Adzuna (API)
- **Web dashboard** — Browse, filter, and search scraped jobs
- **One-click approve** — Approve a job and instantly generate documents
- **AI resume tailoring** — Rewrites your resume to match the job description's terminology
- **AI cover letters** — Drafts a concise, role-specific cover letter
- **Resume upload** — Upload a PDF or Word doc, AI extracts your info automatically
- **Fallback mode** — Works without an API key using keyword matching and templates

## Getting Started (No Install Needed)

You can run this app entirely in your browser using GitHub Codespaces — nothing to install on your computer.

### Step 1: Open in Codespaces

From the GitHub repo page, click the green **"Code"** button, then the **"Codespaces"** tab, then **"Create codespace on main"**. Wait a minute or two for it to set up.

The app will start automatically and a browser tab will open with the dashboard.

### Step 2: Add your OpenAI API key

1. In the dashboard, click **Settings** in the top navigation bar
2. Paste your OpenAI API key (get one at [platform.openai.com/api-keys](https://platform.openai.com/api-keys))
3. Click **Save Settings**

### Step 3: Upload your resume

1. Click **My Resume** in the top navigation bar
2. Click the file picker and choose your resume (PDF, Word doc, or text file)
3. Click **Upload & Parse** — AI reads your file and extracts your info

### Step 4: Find jobs

1. Go to the **Dashboard** (click the logo or "Dashboard" link)
2. Enter job keywords (e.g. "marketing manager") and a location (e.g. "Remote")
3. Click **Search & Scrape**
4. Click into any job to read the full description
5. Click **Approve & Generate Resume + Cover Letter** to create tailored documents

## Running Locally (Advanced)

If you prefer to run on your own computer:

```bash
./start.sh
```

Or manually:

```bash
python -m venv .venv
source .venv/bin/activate
pip install .
cp .env.example .env
# Edit .env with your OPENAI_API_KEY
python -m app.main
```

Then open http://127.0.0.1:8000 in your browser.

## Notes

- Web scraping results depend on the current structure of job board pages. Scrapers may need updates if sites change their HTML.
- Adzuna is the most reliable source since it uses an official API.
- The app uses SQLite for storage — no external database required.
- Rate limiting is built into all scrapers to be respectful of source sites.
