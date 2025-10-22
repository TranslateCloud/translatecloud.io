"""
TranslateCloud - HTML Reconstructor
Reconstruye HTML traducido manteniendo estructura original
"""

from bs4 import BeautifulSoup
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class HTMLReconstructor:
    """
    Reconstruye páginas HTML con contenido traducido
    manteniendo estructura, estilos y scripts originales
    """
    
    def __init__(self):
        self.parser = 'lxml'
    
    def reconstruct_page(
        self,
        original_html: str,
        translated_elements: List[Dict],
        target_lang: str
    ) -> str:
        """
        Reconstruye HTML con traducciones aplicadas
        
        Args:
            original_html: HTML original completo
            translated_elements: Lista de elementos con traducciones
            target_lang: Código del idioma destino
            
        Returns:
            str: HTML traducido completo
        """
        try:
            soup = BeautifulSoup(original_html, self.parser)
            
            # Actualizar lang attribute
            if soup.html:
                soup.html['lang'] = target_lang
            
            # Aplicar traducciones a cada elemento
            for element in translated_elements:
                self._apply_translation(soup, element)
            
            # Actualizar meta tags
            self._update_meta_tags(soup, translated_elements)
            
            # Generar sitemap entry
            self._add_hreflang_tags(soup, target_lang)
            
            return str(soup.prettify())
            
        except Exception as e:
            logger.error(f'Error reconstructing HTML: {str(e)}')
            return original_html
    
    def _apply_translation(self, soup: BeautifulSoup, element: Dict):
        """
        Aplica traducción a un elemento específico usando XPath
        """
        try:
            xpath = element.get('xpath', '')
            translated_text = element.get('translated_text', '')
            tag_name = element.get('tag', '')
            
            if not translated_text:
                return
            
            # Para imágenes, actualizar alt text
            if tag_name == 'img':
                img_elements = soup.find_all('img', attrs=element.get('attrs', {}))
                for img in img_elements:
                    img['alt'] = translated_text
            
            # Para otros elementos, reemplazar contenido de texto
            else:
                # Buscar elemento por atributos originales
                elements = soup.find_all(
                    tag_name,
                    attrs=element.get('attrs', {})
                )
                
                for elem in elements:
                    # Preservar tags hijos (como <strong>, <em>, etc)
                    if elem.string:
                        elem.string.replace_with(translated_text)
                    
        except Exception as e:
            logger.warning(f'Could not apply translation to element: {str(e)}')
    
    def _update_meta_tags(self, soup: BeautifulSoup, translated_elements: List[Dict]):
        """
        Actualiza meta tags con contenido traducido
        """
        # Buscar title traducido
        title_element = next(
            (el for el in translated_elements if el.get('tag') == 'title'),
            None
        )
        if title_element and soup.title:
            soup.title.string = title_element.get('translated_text', '')
        
        # Buscar meta description traducida
        meta_desc = next(
            (el for el in translated_elements if 'meta_description' in el),
            None
        )
        if meta_desc:
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_tag:
                meta_tag['content'] = meta_desc.get('translated_text', '')
    
    def _add_hreflang_tags(self, soup: BeautifulSoup, target_lang: str):
        """
        Añade tags hreflang para SEO multilingüe
        """
        if not soup.head:
            return
        
        # Crear link tag para idioma alternativo
        hreflang_tag = soup.new_tag(
            'link',
            rel='alternate',
            hreflang=target_lang,
            href=f'/{target_lang}/'
        )
        soup.head.append(hreflang_tag)
    
    def generate_sitemap_entry(
        self,
        original_url: str,
        target_lang: str,
        translated_pages: List[Dict]
    ) -> str:
        """
        Genera entrada de sitemap XML para SEO

        Args:
            original_url: URL de la página original
            target_lang: Idioma destino
            translated_pages: Lista de páginas traducidas

        Returns:
            str: XML del sitemap entry
        """
        sitemap = ['<?xml version="1.0" encoding="UTF-8"?>']
        sitemap.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"')
        sitemap.append('        xmlns:xhtml="http://www.w3.org/1999/xhtml">')

        for page in translated_pages:
            sitemap.append('  <url>')
            sitemap.append(f'    <loc>{page["url"]}</loc>')
            sitemap.append(f'    <lastmod>{page.get("lastmod", "")}</lastmod>')

            # Agregar alternativas de idioma
            for lang in page.get('alternate_langs', []):
                sitemap.append(
                    f'    <xhtml:link rel="alternate" hreflang="{lang}" '
                    f'href="{page["url"].replace(target_lang, lang)}" />'
                )

            sitemap.append('  </url>')

        sitemap.append('</urlset>')

        return '\n'.join(sitemap)

    def build_translated_site(
        self,
        pages: List[Dict],
        translated_elements: List[Dict],
        source_lang: str,
        target_lang: str
    ) -> bytes:
        """
        Build complete translated website as ZIP file

        Args:
            pages: List of pages from crawl (with 'html' and 'url_path')
            translated_elements: List of translated elements
            source_lang: Source language code
            target_lang: Target language code

        Returns:
            bytes: ZIP file content
        """
        import zipfile
        import io

        # Create in-memory ZIP
        zip_buffer = io.BytesIO()

        try:
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Process each page
                for page in pages:
                    # Get elements for this page
                    page_elements = [
                        el for el in translated_elements
                        if el.get('page_url') == page.get('url')
                    ]

                    # Reconstruct HTML with translations
                    translated_html = self.reconstruct_page(
                        page.get('html', ''),
                        page_elements,
                        target_lang
                    )

                    # Add to ZIP
                    url_path = page.get('url_path', 'index.html')
                    zipf.writestr(url_path, translated_html)

            # Return ZIP bytes
            zip_buffer.seek(0)
            return zip_buffer.getvalue()

        except Exception as e:
            logger.error(f'Error building translated site: {str(e)}')
            raise


def rebuild_website(pages_data: List[Dict], target_lang: str, output_path: str) -> str:
    """
    Rebuild entire website with translations and create ZIP

    Args:
        pages_data: List of pages with original HTML and translated content
        target_lang: Target language code
        output_path: Path to save ZIP file

    Returns:
        Path to generated ZIP file
    """
    import zipfile
    import os
    from pathlib import Path

    # Create temp directory for translated files
    temp_dir = Path(output_path).parent / 'temp_translated'
    temp_dir.mkdir(exist_ok=True)

    try:
        # Process each page
        for page in pages_data:
            # Reconstruct HTML
            translated_html = reconstructor.reconstruct_page(
                page['original_html'],
                page['translated_elements'],
                target_lang
            )

            # Save to temp directory
            # Extract path from URL
            url_path = page.get('url_path', 'index.html')
            file_path = temp_dir / url_path

            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(translated_html, encoding='utf-8')

        # Create ZIP file
        zip_path = f"{output_path}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)

        # Cleanup temp directory
        import shutil
        shutil.rmtree(temp_dir)

        return zip_path

    except Exception as e:
        logger.error(f'Error rebuilding website: {str(e)}')
        # Cleanup on error
        if temp_dir.exists():
            import shutil
            shutil.rmtree(temp_dir)
        raise


# Instancia global
reconstructor = HTMLReconstructor()
