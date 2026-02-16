from app.scrapers.base import BaseScraper
from app.scrapers.indeed import IndeedScraper
from app.scrapers.linkedin import LinkedInScraper
from app.scrapers.glassdoor import GlassdoorScraper
from app.scrapers.adzuna import AdzunaScraper

ALL_SCRAPERS: list[type[BaseScraper]] = [
    IndeedScraper,
    LinkedInScraper,
    GlassdoorScraper,
    AdzunaScraper,
]

__all__ = [
    "BaseScraper",
    "IndeedScraper",
    "LinkedInScraper",
    "GlassdoorScraper",
    "AdzunaScraper",
    "ALL_SCRAPERS",
]
