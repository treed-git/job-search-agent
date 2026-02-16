from __future__ import annotations

import logging
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from app.models import JobPosting
from app.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class GlassdoorScraper(BaseScraper):
    """Scrapes Glassdoor's public job listings page."""

    name = "Glassdoor"
    BASE_URL = "https://www.glassdoor.com/Job/jobs.htm"

    async def scrape(self, keywords: str, location: str) -> list[JobPosting]:
        jobs: list[JobPosting] = []
        params = {
            "sc.keyword": keywords,
            "locT": "",
            "locKeyword": location,
            "sortBy": "date_desc",
        }

        html = await self.fetch_page(self.BASE_URL, params=params)
        if not html:
            logger.warning("[Glassdoor] No HTML returned")
            return jobs

        soup = BeautifulSoup(html, "lxml")
        cards = soup.select("li.react-job-listing, li[data-test='jobListing']")

        for card in cards[: self.max_results]:
            try:
                title_el = card.select_one("a.jobTitle, a[data-test='job-title']")
                company_el = card.select_one(
                    "div.d-flex.justify-content-between a, span.EmployerProfile_compactEmployerName__LE242"
                )
                location_el = card.select_one("span.pr-xxsm, div.d-flex.flex-wrap.css-yytu5m")
                salary_el = card.select_one("span[data-test='detailSalary']")

                if not title_el:
                    continue

                href = title_el.get("href", "")
                url = (
                    f"https://www.glassdoor.com{href}" if href.startswith("/") else href
                )

                jobs.append(
                    JobPosting(
                        title=title_el.get_text(strip=True),
                        company=company_el.get_text(strip=True) if company_el else "Unknown",
                        location=location_el.get_text(strip=True) if location_el else "",
                        url=url,
                        source=self.name,
                        salary=salary_el.get_text(strip=True) if salary_el else "",
                    )
                )
            except Exception as e:
                logger.debug(f"[Glassdoor] Error parsing card: {e}")
                continue

        logger.info(f"[Glassdoor] Scraped {len(jobs)} jobs for '{keywords}'")
        return jobs
