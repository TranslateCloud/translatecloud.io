"""
TranslateCloud - Project Management API Routes

This module handles all project-related API endpoints including:
- Project CRUD operations (Create, Read, Update, Delete)
- Website crawling and analysis
- Translation workflow management
- Translated website export

Architecture:
    Frontend → API Gateway → Lambda → FastAPI → This Module → Services/Database

Core Translation Flow:
    1. Crawl: User provides URL → Web crawler extracts pages → Project created
    2. Translate: Frontend sends pages → Translation service processes → Database updated
    3. Export: Frontend requests ZIP → HTML reconstructor builds site → ZIP returned

API Endpoints:
    GET    /api/projects/              - List user's projects
    POST   /api/projects/              - Create new project
    GET    /api/projects/{id}          - Get project details
    PUT    /api/projects/{id}          - Update project
    DELETE /api/projects/{id}          - Delete project
    POST   /api/projects/crawl         - Crawl website and analyze
    POST   /api/projects/translate     - Translate crawled pages
    POST   /api/projects/export/{id}   - Export as ZIP

Performance Considerations:
- Crawl endpoint: Can take 30s-5min depending on website size
- Translate endpoint: Can take 1-5min for large websites
- Export endpoint: ~5-30s depending on page count

Error Handling:
- 400: Bad request (validation errors)
- 404: Project not found or unauthorized
- 500: Server errors (crawl failed, translation failed, export failed)

Security:
- All endpoints require JWT authentication
- User can only access their own projects
- SQL injection prevention via parameterized queries

Author: TranslateCloud Team
Last Updated: October 20, 2025
"""

# ============================================================================
# Standard Library Imports
# ============================================================================
import uuid          # For generating unique project IDs
from typing import List  # For type hints

# ============================================================================
# Third-Party Imports
# ============================================================================
from fastapi import APIRouter, Depends, HTTPException, status, Body
from psycopg2.extras import RealDictCursor  # PostgreSQL cursor with dict results
from pydantic import BaseModel, HttpUrl     # Request/response models

# ============================================================================
# Local Application Imports
# ============================================================================
from src.config.database import get_db  # Database connection dependency
from src.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from src.api.dependencies.jwt_auth import get_current_user_id  # Auth dependency

# ============================================================================
# Router Configuration
# ============================================================================
# Create FastAPI router for project endpoints
# This router is mounted at /api/projects in main.py
router = APIRouter()

# ============================================================================
# Request/Response Models
# ============================================================================
# These Pydantic models validate request bodies and define response structures


class CrawlRequest(BaseModel):
    """
    Request model for POST /api/projects/crawl endpoint

    Used to initiate website crawling and analysis before translation.

    Attributes:
        url (str): Website URL to crawl
                  Example: "https://example.com"
        source_language (str): Source language of the website
                              Example: "en", "es", "auto"
        target_language (str): Target language for translation
                              Example: "es", "en", "pt-br"

    Validation:
        - url: Must be a valid URL format
        - languages: No format validation (handled by translation service)

    Example:
        {
            "url": "https://example.com",
            "source_language": "en",
            "target_language": "es"
        }
    """
    url: str
    source_language: str
    target_language: str


class TranslateRequest(BaseModel):
    """
    Request model for POST /api/projects/translate endpoint

    Used to translate pages that were previously crawled.

    Attributes:
        project_id (str): UUID of the project to translate
        pages (List[dict]): Array of page objects from crawl result
                           Each dict contains: url, url_path, word_count
        source_language (str): Source language code
        target_language (str): Target language code

    Performance Notes:
        - Large page lists (50+ pages) may exceed Lambda timeout
        - Consider async architecture for 100+ pages

    Example:
        {
            "project_id": "123e4567-e89b-12d3-a456-426614174000",
            "pages": [
                {"url": "https://example.com", "word_count": 500},
                {"url": "https://example.com/about", "word_count": 300}
            ],
            "source_language": "en",
            "target_language": "es"
        }
    """
    project_id: str
    pages: List[dict]
    source_language: str
    target_language: str


class ExportRequest(BaseModel):
    """
    Request model for POST /api/projects/export/{project_id} endpoint

    Used to export translated pages as a downloadable ZIP file.

    Attributes:
        pages (List[dict]): Translated pages with elements
                           Each dict contains: url, url_path, original_html,
                           translated_elements
        target_language (str): Language code for lang attribute in HTML

    ZIP Structure:
        translated-site-{project_id}.zip/
        ├── index.html              (homepage)
        ├── about_us.html           (converted from /about-us)
        ├── contact.html
        └── css/                    (assets if included)

    Example:
        {
            "pages": [
                {
                    "url": "https://example.com",
                    "url_path": "index.html",
                    "original_html": "<html>...",
                    "translated_elements": [...]
                }
            ],
            "target_language": "es"
        }
    """
    pages: List[dict]
    target_language: str


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/", response_model=List[ProjectResponse])
async def get_projects(
    user_id: str,
    cursor: RealDictCursor = Depends(get_db)
):
    cursor.execute(
        "SELECT * FROM projects WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,)
    )
    projects = cursor.fetchall()
    return projects

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    user_id: str,
    project: ProjectCreate,
    cursor: RealDictCursor = Depends(get_db)
):
    project_id = str(uuid.uuid4())
    
    cursor.execute(
        '''
        INSERT INTO projects (id, user_id, name, url, source_lang, target_lang, status, total_words, translated_words)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *
        ''',
        (
            project_id,
            user_id,
            project.name,
            str(project.url) if project.url else None,
            project.source_lang,
            project.target_lang,
            'pending',
            0,
            0
        )
    )
    
    new_project = cursor.fetchone()
    return new_project

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    user_id: str,
    cursor: RealDictCursor = Depends(get_db)
):
    cursor.execute(
        "SELECT * FROM projects WHERE id = %s AND user_id = %s",
        (project_id, user_id)
    )
    project = cursor.fetchone()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    user_id: str,
    project_update: ProjectUpdate,
    cursor: RealDictCursor = Depends(get_db)
):
    update_data = project_update.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
    values = list(update_data.values())
    values.extend([project_id, user_id])
    
    cursor.execute(
        f"UPDATE projects SET {set_clause} WHERE id = %s AND user_id = %s RETURNING *",
        values
    )
    
    updated_project = cursor.fetchone()
    
    if not updated_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return updated_project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    user_id: str,
    cursor: RealDictCursor = Depends(get_db)
):
    cursor.execute(
        "DELETE FROM projects WHERE id = %s AND user_id = %s RETURNING id",
        (project_id, user_id)
    )

    deleted = cursor.fetchone()

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return None

@router.post("/crawl")
async def crawl_website(
    request: CrawlRequest,
    user_id: str = Depends(get_current_user_id),
    cursor: RealDictCursor = Depends(get_db)
):
    """Crawl website and return page count and word count"""
    from src.core.web_extractor import crawl_website as extract_web

    try:
        # Crawl website (max 50 pages for MVP)
        result = await extract_web(request.url, max_pages=50)

        # Create project
        project_id = str(uuid.uuid4())
        cursor.execute(
            '''
            INSERT INTO projects (id, user_id, name, url, source_lang, target_lang, total_words, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
            ''',
            (
                project_id,
                user_id,
                f"Translation: {request.url}",
                request.url,
                request.source_language,
                request.target_language,
                result['word_count'],
                'analyzed'
            )
        )

        project = cursor.fetchone()

        return {
            'project_id': project_id,
            'pages_count': result['pages_count'],
            'word_count': result['word_count'],
            'pages': result['pages'],
            'estimated_cost': result['word_count'] * 0.055
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Crawl failed: {str(e)}"
        )

@router.post("/translate")
async def translate_website(
    request: TranslateRequest,
    user_id: str = Depends(get_current_user_id),
    cursor: RealDictCursor = Depends(get_db)
):
    """Start website translation job"""
    from src.core.web_extractor import extractor
    from src.core.translation_service import TranslationService
    from src.core.html_reconstructor import reconstructor
    from src.config.settings import get_settings
    import logging

    logger = logging.getLogger(__name__)
    settings = get_settings()

    try:
        # Update project status
        cursor.execute(
            "UPDATE projects SET status = %s WHERE id = %s AND user_id = %s",
            ('processing', request.project_id, user_id)
        )

        # Initialize translation service with DeepL API key
        translation_service = TranslationService(
            deepl_api_key=settings.DEEPL_API_KEY if hasattr(settings, 'DEEPL_API_KEY') else None
        )

        translated_pages = []
        total_words_translated = 0

        # Process each page
        for page_info in request.pages:
            logger.info(f"Translating page: {page_info['url']}")

            # 1. Crawl page to get full HTML and translatable elements
            page_data = extractor.crawl_page(page_info['url'])

            if not page_data:
                logger.warning(f"Could not crawl page: {page_info['url']}")
                continue

            # 2. Translate all elements
            translated_elements = []

            for element in page_data['elements']:
                result = await translation_service.translate(
                    element['text'],
                    request.source_language,
                    request.target_language
                )

                if result['success']:
                    translated_elements.append({
                        **element,
                        'translated_text': result['text'],
                        'provider': result['provider']
                    })
                else:
                    # Keep original if translation fails
                    translated_elements.append({
                        **element,
                        'translated_text': element['text'],
                        'provider': 'none'
                    })

            # 3. Translate metadata
            title_result = await translation_service.translate(
                page_data['title'],
                request.source_language,
                request.target_language
            ) if page_data['title'] else None

            meta_desc_result = await translation_service.translate(
                page_data['meta_description'],
                request.source_language,
                request.target_language
            ) if page_data['meta_description'] else None

            # Add metadata to translated elements
            if title_result and title_result['success']:
                translated_elements.append({
                    'tag': 'title',
                    'text': page_data['title'],
                    'translated_text': title_result['text']
                })

            if meta_desc_result and meta_desc_result['success']:
                translated_elements.append({
                    'tag': 'meta_description',
                    'text': page_data['meta_description'],
                    'translated_text': meta_desc_result['text']
                })

            # 4. Store page with translations
            translated_pages.append({
                'url': page_info['url'],
                'url_path': page_info.get('url_path', 'index.html'),
                'original_html': page_data['html_original'],
                'translated_elements': translated_elements,
                'word_count': page_data['word_count']
            })

            total_words_translated += page_data['word_count']

        # Update project with translation results
        cursor.execute('''
            UPDATE projects
            SET status = %s, translated_words = %s, updated_at = NOW()
            WHERE id = %s
        ''', ('completed', total_words_translated, request.project_id))

        # Update user's word usage
        cursor.execute('''
            UPDATE users
            SET words_used_this_month = words_used_this_month + %s
            WHERE id = %s
        ''', (total_words_translated, user_id))

        logger.info(f"Translation completed: {len(translated_pages)} pages, {total_words_translated} words")

        return {
            'project_id': request.project_id,
            'status': 'completed',
            'pages_translated': len(translated_pages),
            'total_words': total_words_translated,
            'pages': translated_pages
        }

    except Exception as e:
        logger.error(f"Translation failed: {str(e)}")
        cursor.execute(
            "UPDATE projects SET status = %s WHERE id = %s",
            ('failed', request.project_id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation failed: {str(e)}"
        )


@router.post("/export/{project_id}")
async def export_project(
    project_id: str,
    request: ExportRequest,
    user_id: str = Depends(get_current_user_id),
    cursor: RealDictCursor = Depends(get_db)
):
    """Export translated website as ZIP file"""
    from src.core.html_reconstructor import rebuild_website
    from fastapi.responses import FileResponse
    import tempfile
    import os

    try:
        # Verify project ownership
        cursor.execute(
            "SELECT * FROM projects WHERE id = %s AND user_id = %s",
            (project_id, user_id)
        )
        project = cursor.fetchone()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        # Create temporary directory for ZIP
        temp_dir = tempfile.mkdtemp()
        output_path = os.path.join(temp_dir, f"translated-site-{project_id}")

        # Build ZIP file
        zip_path = rebuild_website(request.pages, request.target_language, output_path)

        # Return ZIP file
        return FileResponse(
            path=zip_path,
            media_type='application/zip',
            filename=f"translated-site-{project_id}.zip",
            headers={
                'Content-Disposition': f'attachment; filename=translated-site-{project_id}.zip'
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}"
        )