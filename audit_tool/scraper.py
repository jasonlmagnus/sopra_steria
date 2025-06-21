"""
This module is responsible for scraping web content.
"""
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from .models import PageData
from typing import List
import logging
import os
import pickle
from urllib.parse import urlparse

CACHE_DIR = "cache"

class Scraper:
    """
    A class to handle web scraping operations using Playwright and BeautifulSoup.
    It includes a caching mechanism to avoid re-fetching pages.
    """
    def __init__(self):
        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR)

    def _get_cache_path(self, url: str) -> str:
        """Generates a safe filename for the cache from a URL."""
        # Use a simple sanitized version of the URL as the filename
        filename = urlparse(url).netloc + urlparse(url).path
        safe_filename = "".join(c for c in filename if c.isalnum() or c in ('_','-')).rstrip()
        return os.path.join(CACHE_DIR, f"{safe_filename}.pkl")

    def _save_to_cache(self, url: str, page_data: PageData):
        """Saves a PageData object to the cache."""
        cache_path = self._get_cache_path(url)
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(page_data, f)
            logging.info(f"Saved page data for {url} to cache.")
        except Exception as e:
            logging.error(f"Could not save cache for {url}. Error: {e}")

    def _load_from_cache(self, url: str) -> PageData | None:
        """Loads a PageData object from the cache if it exists."""
        cache_path = self._get_cache_path(url)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    logging.info(f"Loading page data for {url} from cache.")
                    return pickle.load(f)
            except Exception as e:
                logging.error(f"Could not load cache for {url}. Error: {e}")
        return None

    def _check_tagline(self, soup: BeautifulSoup) -> bool:
        """Checks if the corporate tagline is present on the page."""
        tagline = "The world is how we shape it"
        return tagline.lower() in soup.get_text().lower()

    def _check_placeholder_content(self, soup: BeautifulSoup) -> bool:
        """Checks for lorem ipsum placeholder text."""
        return "lorem ipsum" in soup.get_text().lower()

    def _get_h1_text(self, soup: BeautifulSoup) -> str:
        """Gets the text of the first h1 tag, lowercased."""
        h1 = soup.find('h1')
        return h1.get_text(strip=True).lower() if h1 else ""

    def _get_nav_links(self, soup: BeautifulSoup) -> List[str]:
        """Gets a list of all link texts within <nav> elements, lowercased."""
        nav_links = []
        for nav in soup.find_all('nav'):
            for link in nav.find_all('a'):
                nav_links.append(link.get_text(strip=True).lower())
        return nav_links

    def fetch_page(self, url: str) -> PageData:
        """
        Fetches the page, extracts text, and performs objective checks.
        It first checks the cache for the page data before fetching it live.
        
        Returns:
            PageData: A dataclass containing the scraped information.
        """
        # Check cache first
        cached_data = self._load_from_cache(url)
        if cached_data:
            return cached_data

        # If not in cache, fetch live
        logging.info(f"No cache found for {url}. Fetching live.")
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(url, wait_until='networkidle')
                
                html_content = page.content()
                soup = BeautifulSoup(html_content, 'html.parser')
                
                raw_text = soup.get_text(separator=' ', strip=True)

                findings = {
                    "has_tagline": self._check_tagline(soup),
                    "has_placeholder_content": self._check_placeholder_content(soup),
                    "h1_text": self._get_h1_text(soup),
                    "nav_links": self._get_nav_links(soup),
                }

                browser.close()
                page_data_obj = PageData(
                    url=url,
                    raw_text=raw_text,
                    is_404=False,
                    objective_findings=findings
                )
                
                # Save to cache before returning
                self._save_to_cache(url, page_data_obj)
                
                return page_data_obj

        except Exception as e:
            logging.error(f"An error occurred while fetching {url}: {e}")
            return PageData(url=url, raw_text="", is_404=True, objective_findings={}) 