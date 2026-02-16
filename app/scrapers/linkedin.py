from __future__ import annotations

import logging
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from app.models import JobPosting
from app.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class LinkedInScraper(BaseScraper):
    """Scrapes LinkedIn's public (guest) job search page — no login required."""

    name = "LinkedIn"
    BASE_URL = "https://www.linkedin.com/jobs/search"

    async def scrape(self, keywords: str, location: str) -> list[JobPosting]:
        jobs: list[JobPosting] = []
        params = {
            "keywords": keywords,
            "location": location,
            "position": "1",
            "pageNum": "0",
            "sortBy": "DD",
        }

        html = await self.fetch_page(self.BASE_URL, params=params)
        if not html:
            logger.warning("[LinkedIn] No HTML returned")
            return jobs

        soup = BeautifulSoup(html, "lxml")
        cards = soup.select("div.base-card, li.result-card")

        for card in cards[: self.max_results]:
            try:
                title_el = card.select_one("h3.base-search-card__title, h3")
                company_el = card.select_one("h4.base-search-card__subtitle, h4")
                location_el = card.select_one("span.job-search-card__location, span.location")
                link_el = card.select_one("a.base-card__full-link, a")
                date_el = card.select_one("time")

                if not title_el:
                    continue

                jobs.append(
                    JobPosting(
                        title=title_el.get_text(strip=True),
                        company=company_el.get_text(strip=True) if company_el else "Unknown",
                        location=location_el.get_text(strip=True) if location_el else "",
                        url=link_el["href"] if link_el and link_el.get("href") else "",
                        source=self.name,
                        date_posted=date_el.get("datetime", "") if date_el else "",
                    )
                )
            except Exception as e:
                logger.debug(f"[LinkedIn] Error parsing card: {e}")
                continue

        logger.info(f"[LinkedIn] Scraped {len(jobs)} jobs for '{keywords}'")
        return jobs
