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
            
            soup = BeautifulSoup(response.content, 'lxml')
            
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


# Instancia global
extractor = WebExtractor()
