from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    # Adzuna
    adzuna_app_id: str = ""
    adzuna_app_key: str = ""

    # Job search defaults
    job_search_keywords: str = "software engineer"
    job_search_location: str = "United States"
    job_search_remote_only: bool = False

    # Paths
    resume_path: str = "data/sample_resume.json"
    database_path: str = "data/jobs.db"

    # Scraper settings
    scrape_delay_seconds: float = 2.0
    max_results_per_source: int = 25

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()


def reload_settings() -> None:
    """Reload environment-backed settings into the shared settings object."""
    refreshed = Settings()
    for key, value in refreshed.model_dump().items():
        setattr(settings, key, value)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
