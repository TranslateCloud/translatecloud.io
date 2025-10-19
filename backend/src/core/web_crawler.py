"""
TranslateCloud - Web Crawler Service
Crawls websites and extracts translatable content
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
from typing import List, Dict, Set, Optional
import logging
import re

logger = logging.getLogger(__name__)


class WebCrawler:
    """
    Web crawler that extracts pages from websites for translation

    Features:
    - Respects same-domain policy
    - Avoids duplicate pages
    - Extracts text content and structure
    - Word count calculation
    - Configurable page limit
    """

    def __init__(self, max_pages: int = 50, timeout: int = 10):
        """
        Initialize crawler

        Args:
            max_pages: Maximum pages to crawl (default: 50)
            timeout: HTTP request timeout in seconds (default: 10)
        """
        self.max_pages = max_pages
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.visited_urls: Set[str] = set()
        self.pages_data: List[Dict] = []

    def normalize_url(self, url: str) -> str:
        """
        Normalize URL to avoid duplicates

        - Remove fragments (#section)
        - Remove trailing slashes
        - Normalize scheme (http/https)
        """
        parsed = urlparse(url)
        # Remove fragment
        normalized = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path.rstrip('/') or '/',
            parsed.params,
            parsed.query,
            ''  # No fragment
        ))
        return normalized

    def is_same_domain(self, url: str, base_url: str) -> bool:
        """Check if URL is same domain as base"""
        url_domain = urlparse(url).netloc
        base_domain = urlparse(base_url).netloc
        return url_domain == base_domain

    def should_skip_url(self, url: str) -> bool:
        """
        Check if URL should be skipped

        Skip:
        - Non-HTML files (images, PDFs, etc.)
        - Social media links
        - Mailto/tel links
        """
        skip_extensions = [
            '.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp',  # Images
            '.pdf', '.doc', '.docx', '.xls', '.xlsx',  # Documents
            '.zip', '.tar', '.gz',  # Archives
            '.mp3', '.mp4', '.avi',  # Media
            '.css', '.js', '.json', '.xml'  # Assets
        ]

        skip_patterns = [
            r'mailto:',
            r'tel:',
            r'javascript:',
            r'#',  # Anchor-only links
            r'facebook\.com',
            r'twitter\.com',
            r'linkedin\.com',
            r'instagram\.com'
        ]

        url_lower = url.lower()

        # Check extensions
        if any(url_lower.endswith(ext) for ext in skip_extensions):
            return True

        # Check patterns
        if any(re.search(pattern, url_lower) for pattern in skip_patterns):
            return True

        return False

    def extract_links(self, html: str, base_url: str) -> List[str]:
        """
        Extract all valid links from HTML

        Args:
            html: HTML content
            base_url: Base URL for resolving relative links

        Returns:
            List of absolute URLs
        """
        soup = BeautifulSoup(html, 'html.parser')
        links = []

        for anchor in soup.find_all('a', href=True):
            href = anchor['href']

            # Convert to absolute URL
            absolute_url = urljoin(base_url, href)

            # Normalize
            normalized_url = self.normalize_url(absolute_url)

            # Skip if invalid
            if self.should_skip_url(normalized_url):
                continue

            # Skip if different domain
            if not self.is_same_domain(normalized_url, base_url):
                continue

            # Skip if already visited or queued
            if normalized_url not in self.visited_urls:
                links.append(normalized_url)

        return links

    def extract_text_content(self, html: str) -> tuple[str, int]:
        """
        Extract translatable text from HTML

        Args:
            html: HTML content

        Returns:
            tuple: (text_content, word_count)
        """
        soup = BeautifulSoup(html, 'html.parser')

        # Remove script and style elements
        for element in soup(['script', 'style', 'noscript']):
            element.decompose()

        # Get text
        text = soup.get_text(separator=' ', strip=True)

        # Count words (split by whitespace)
        words = text.split()
        word_count = len([w for w in words if len(w) > 0])

        return text, word_count

    def extract_metadata(self, html: str) -> Dict[str, Optional[str]]:
        """
        Extract page metadata (title, description, etc.)

        Args:
            html: HTML content

        Returns:
            dict: metadata
        """
        soup = BeautifulSoup(html, 'html.parser')

        # Extract title
        title_tag = soup.find('title')
        title = title_tag.string if title_tag else None

        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content') if meta_desc else None

        # Extract meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        keywords = meta_keywords.get('content') if meta_keywords else None

        return {
            'title': title,
            'description': description,
            'keywords': keywords
        }

    async def fetch_page(self, session: aiohttp.ClientSession, url: str) -> Optional[Dict]:
        """
        Fetch single page and extract data

        Args:
            session: aiohttp session
            url: URL to fetch

        Returns:
            dict with page data or None if failed
        """
        try:
            async with session.get(url, timeout=self.timeout) as response:
                # Only process HTML
                content_type = response.headers.get('Content-Type', '')
                if 'text/html' not in content_type:
                    logger.warning(f"Skipping non-HTML: {url} ({content_type})")
                    return None

                html = await response.text()

                # Extract content
                text_content, word_count = self.extract_text_content(html)
                metadata = self.extract_metadata(html)
                links = self.extract_links(html, url)

                # Get URL path for filename
                parsed_url = urlparse(url)
                url_path = parsed_url.path.rstrip('/') or '/index'
                if not url_path.endswith('.html'):
                    url_path += '.html'
                url_path = url_path.lstrip('/')

                return {
                    'url': url,
                    'url_path': url_path,
                    'html': html,
                    'text': text_content,
                    'word_count': word_count,
                    'title': metadata['title'],
                    'meta_description': metadata['description'],
                    'links': links
                }

        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching: {url}")
            return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    async def crawl(self, start_url: str) -> Dict:
        """
        Crawl website starting from URL

        Args:
            start_url: Starting URL

        Returns:
            dict: {
                'pages': List of page data,
                'pages_count': Total pages crawled,
                'word_count': Total words,
                'base_url': Starting URL
            }
        """
        # Normalize start URL
        start_url = self.normalize_url(start_url)

        # Initialize
        to_visit = [start_url]
        total_words = 0

        # Create session with proper headers
        headers = {
            'User-Agent': 'TranslateCloud-Bot/1.0 (Website Translation Service)'
        }

        async with aiohttp.ClientSession(headers=headers, timeout=self.timeout) as session:
            while to_visit and len(self.pages_data) < self.max_pages:
                url = to_visit.pop(0)

                # Skip if already visited
                if url in self.visited_urls:
                    continue

                logger.info(f"Crawling: {url} ({len(self.pages_data) + 1}/{self.max_pages})")

                # Mark as visited
                self.visited_urls.add(url)

                # Fetch page
                page_data = await self.fetch_page(session, url)

                if page_data:
                    self.pages_data.append(page_data)
                    total_words += page_data['word_count']

                    # Add new links to queue
                    for link in page_data['links']:
                        if link not in self.visited_urls and link not in to_visit:
                            to_visit.append(link)

                # Small delay to be polite
                await asyncio.sleep(0.5)

        logger.info(f"Crawl complete: {len(self.pages_data)} pages, {total_words} words")

        return {
            'pages': self.pages_data,
            'pages_count': len(self.pages_data),
            'word_count': total_words,
            'base_url': start_url
        }


# Convenience function for routes
async def crawl_website(url: str, max_pages: int = 50) -> Dict:
    """
    Crawl a website and return page data

    Args:
        url: Starting URL
        max_pages: Maximum pages to crawl

    Returns:
        Crawl results dictionary
    """
    crawler = WebCrawler(max_pages=max_pages)
    return await crawler.crawl(url)
