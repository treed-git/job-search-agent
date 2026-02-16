from __future__ import annotations

import logging
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from app.models import JobPosting
from app.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class IndeedScraper(BaseScraper):
    name = "Indeed"
    BASE_URL = "https://www.indeed.com/jobs"

    async def scrape(self, keywords: str, location: str) -> list[JobPosting]:
        jobs: list[JobPosting] = []
        params = {
            "q": keywords,
            "l": location,
            "sort": "date",
            "limit": str(min(self.max_results, 25)),
        }

        html = await self.fetch_page(self.BASE_URL, params=params)
        if not html:
            logger.warning("[Indeed] No HTML returned")
            return jobs

        soup = BeautifulSoup(html, "lxml")
        cards = soup.select("div.job_seen_beacon, div.jobsearch-ResultsList > div")

        for card in cards[: self.max_results]:
            try:
                title_el = card.select_one("h2.jobTitle a, h2 a")
                company_el = card.select_one("[data-testid='company-name'], span.companyName")
                location_el = card.select_one("[data-testid='text-location'], div.companyLocation")
                salary_el = card.select_one(
                    "div.salary-snippet-container, div.metadata.salary-snippet-container"
                )
                snippet_el = card.select_one("div.job-snippet, td.resultContent div.css-9446fg")

                if not title_el:
                    continue

                title = title_el.get_text(strip=True)
                href = title_el.get("href", "")
                url = f"https://www.indeed.com{href}" if href.startswith("/") else href

                jobs.append(
                    JobPosting(
                        title=title,
                        company=company_el.get_text(strip=True) if company_el else "Unknown",
                        location=location_el.get_text(strip=True) if location_el else "",
                        description=snippet_el.get_text(strip=True) if snippet_el else "",
                        url=url,
                        source=self.name,
                        salary=salary_el.get_text(strip=True) if salary_el else "",
                    )
                )
            except Exception as e:
                logger.debug(f"[Indeed] Error parsing card: {e}")
                continue

        logger.info(f"[Indeed] Scraped {len(jobs)} jobs for '{keywords}'")
        return jobs
