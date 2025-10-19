"""
TranslateCloud - Web Content Extractor
Extrae contenido traducible de sitios web manteniendo estructura
"""

from bs4 import BeautifulSoup
import requests
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse
import logging

logger = logging.getLogger(__name__)


class WebExtractor:
    """
    Extractor de contenido web para traducción
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TranslateCloud-Bot/1.0'
        })
    
    def crawl_page(self, url: str) -> Optional[Dict]:
        """
        Crawlea una página y extrae contenido traducible
        
        Args:
            url: URL de la página a crawlear
            
        Returns:
            Dict con estructura de la página y contenido
        """
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer metadatos
            title = soup.find('title')
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            
            # Extraer elementos traducibles
            elements = self._extract_translatable_elements(soup)
            
            # Contar palabras
            word_count = sum(len(el['text'].split()) for el in elements)
            
            return {
                'url': url,
                'title': title.string if title else '',
                'meta_description': meta_desc.get('content', '') if meta_desc else '',
                'elements': elements,
                'word_count': word_count,
                'html_original': str(soup)
            }
            
        except Exception as e:
            logger.error(f'Error crawling {url}: {str(e)}')
            return None
    
    def _extract_translatable_elements(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Extrae elementos traducibles del HTML
        
        Returns:
            Lista de elementos con su contenido y metadata
        """
        elements = []
        
        # Tags que contienen texto traducible
        text_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'span', 'div', 'a']
        
        for tag in soup.find_all(text_tags):
            text = tag.get_text(strip=True)
            
            if text and len(text) > 3:  # Ignorar textos muy cortos
                elements.append({
                    'tag': tag.name,
                    'text': text,
                    'attrs': dict(tag.attrs),
                    'xpath': self._get_xpath(tag)
                })
        
        # Extraer alt text de imágenes
        for img in soup.find_all('img'):
            alt = img.get('alt', '')
            if alt:
                elements.append({
                    'tag': 'img',
                    'text': alt,
                    'attrs': {'alt': alt, 'src': img.get('src', '')},
                    'xpath': self._get_xpath(img)
                })
        
        return elements
    
    def _get_xpath(self, element) -> str:
        """
        Genera XPath simplificado para ubicar el elemento
        """
        components = []
        child = element if element.name else element.parent
        
        for parent in child.parents:
            siblings = parent.find_all(child.name, recursive=False)
            components.append(
                child.name if len(siblings) == 1
                else f'{child.name}[{siblings.index(child) + 1}]'
            )
            child = parent
        
        components.reverse()
        return '/' + '/'.join(components)


def normalize_url(url: str) -> str:
    """Remove fragments and trailing slashes"""
    parsed = urlparse(url)
    path = parsed.path.rstrip('/') if parsed.path != '/' else '/'
    return f"{parsed.scheme}://{parsed.netloc}{path}"


async def crawl_website(base_url: str, max_pages: int = 50) -> Dict:
    """
    Crawl website starting from base_url

    Args:
        base_url: Starting URL
        max_pages: Maximum pages to crawl

    Returns:
        Dict with pages_count, word_count, and pages list
    """
    visited = set()
    to_visit = [normalize_url(base_url)]
    pages_data = []
    total_words = 0

    base_domain = urlparse(base_url).netloc

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)

        if url in visited:
            continue

        # Only crawl same domain
        if urlparse(url).netloc != base_domain:
            continue

        visited.add(url)
        logger.info(f"Crawling {len(visited)}/{max_pages}: {url}")

        # Crawl page
        page_data = extractor.crawl_page(url)

        if page_data:
            # Get URL path for filename
            parsed_url = urlparse(url)
            url_path = parsed_url.path.rstrip('/') or '/index'
            if not url_path.endswith('.html'):
                url_path += '.html'
            url_path = url_path.lstrip('/')

            pages_data.append({
                'url': url,
                'url_path': url_path,
                'title': page_data['title'],
                'word_count': page_data['word_count'],
                'meta_description': page_data['meta_description']
            })
            total_words += page_data['word_count']

            # Extract links for further crawling
            if len(visited) < max_pages:
                soup = BeautifulSoup(page_data['html_original'], 'html.parser')
                for link in soup.find_all('a', href=True):
                    next_url = urljoin(url, link['href'])
                    next_url = normalize_url(next_url)

                    # Filter: same domain, http/https only, not already queued
                    parsed = urlparse(next_url)
                    if (parsed.netloc == base_domain and
                        parsed.scheme in ['http', 'https'] and
                        next_url not in visited and
                        next_url not in to_visit and
                        not any(next_url.endswith(ext) for ext in ['.pdf', '.jpg', '.png', '.zip', '.css', '.js'])):
                        to_visit.append(next_url)

    logger.info(f"Crawl complete: {len(pages_data)} pages, {total_words} words")

    return {
        'pages_count': len(pages_data),
        'word_count': total_words,
        'pages': pages_data
    }


# Instancia global
extractor = WebExtractor()
