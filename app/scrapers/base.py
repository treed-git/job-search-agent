from __future__ import annotations

import abc
import asyncio
import logging

import httpx

from app.models import JobPosting
from app.config import settings

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


class BaseScraper(abc.ABC):
    """Base class for all job scrapers."""

    name: str = "base"

    def __init__(self):
        self.delay = settings.scrape_delay_seconds
        self.max_results = settings.max_results_per_source

    @abc.abstractmethod
    async def scrape(self, keywords: str, location: str) -> list[JobPosting]:
        """Scrape job postings and return a list of JobPosting objects."""

    async def fetch_page(self, url: str, params: dict | None = None) -> str | None:
        """Fetch a page with rate limiting and error handling."""
        await asyncio.sleep(self.delay)
        try:
            async with httpx.AsyncClient(
                headers=HEADERS, follow_redirects=True, timeout=30.0
            ) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                return resp.text
        except httpx.HTTPError as e:
            logger.warning(f"[{self.name}] Failed to fetch {url}: {e}")
            return None

    async def fetch_json(self, url: str, params: dict | None = None) -> dict | None:
        """Fetch JSON from an API endpoint."""
        await asyncio.sleep(self.delay)
        try:
            async with httpx.AsyncClient(
                headers=HEADERS, follow_redirects=True, timeout=30.0
            ) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPError as e:
            logger.warning(f"[{self.name}] Failed to fetch {url}: {e}")
            return None
