from __future__ import annotations

import logging

from app.config import settings
from app.models import JobPosting
from app.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class AdzunaScraper(BaseScraper):
    """Uses the Adzuna public API — the most reliable source since it's an official API.

    Get free API credentials at https://developer.adzuna.com/
    """

    name = "Adzuna"
    BASE_URL = "https://api.adzuna.com/v1/api/jobs"

    async def scrape(self, keywords: str, location: str) -> list[JobPosting]:
        jobs: list[JobPosting] = []

        if not settings.adzuna_app_id or not settings.adzuna_app_key:
            logger.info("[Adzuna] Skipping — no API credentials configured")
            return jobs

        # Adzuna uses country codes; map common locations
        country = self._resolve_country(location)

        params = {
            "app_id": settings.adzuna_app_id,
            "app_key": settings.adzuna_app_key,
            "results_per_page": str(min(self.max_results, 50)),
            "what": keywords,
            "where": location,
            "sort_by": "date",
            "content-type": "application/json",
        }

        url = f"{self.BASE_URL}/{country}/search/1"
        data = await self.fetch_json(url, params=params)

        if not data or "results" not in data:
            logger.warning("[Adzuna] No results returned")
            return jobs

        for item in data["results"][: self.max_results]:
            jobs.append(
                JobPosting(
                    title=item.get("title", ""),
                    company=item.get("company", {}).get("display_name", "Unknown"),
                    location=item.get("location", {}).get("display_name", ""),
                    description=item.get("description", ""),
                    url=item.get("redirect_url", ""),
                    source=self.name,
                    salary=self._format_salary(item),
                    date_posted=item.get("created", ""),
                )
            )

        logger.info(f"[Adzuna] Fetched {len(jobs)} jobs for '{keywords}'")
        return jobs

    @staticmethod
    def _resolve_country(location: str) -> str:
        loc = location.lower()
        if any(kw in loc for kw in ("united states", "us", "usa", "remote")):
            return "us"
        if any(kw in loc for kw in ("united kingdom", "uk", "england")):
            return "gb"
        if "canada" in loc:
            return "ca"
        if "australia" in loc:
            return "au"
        if "germany" in loc or "deutschland" in loc:
            return "de"
        if "france" in loc:
            return "fr"
        return "us"

    @staticmethod
    def _format_salary(item: dict) -> str:
        min_sal = item.get("salary_min")
        max_sal = item.get("salary_max")
        if min_sal and max_sal:
            return f"${int(min_sal):,} – ${int(max_sal):,}"
        if min_sal:
            return f"From ${int(min_sal):,}"
        if max_sal:
            return f"Up to ${int(max_sal):,}"
        return ""
