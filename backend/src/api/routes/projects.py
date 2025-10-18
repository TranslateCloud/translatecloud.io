from fastapi import APIRouter, Depends, HTTPException, status
from psycopg2.extras import RealDictCursor
from src.config.database import get_db
from src.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from typing import List
import uuid

router = APIRouter()

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
    url: str,
    source_language: str,
    target_language: str,
    user_id: str,
    cursor: RealDictCursor = Depends(get_db)
):
    """Crawl website and return page count and word count"""
    from src.core.web_extractor import crawl_website as extract_web

    try:
        # Crawl website (max 50 pages for MVP)
        result = await extract_web(url, max_pages=50)

        # Create project
        project_id = str(uuid.uuid4())
        cursor.execute(
            '''
            INSERT INTO projects (id, user_id, name, source_url, source_language, target_language,
                                pages_count, word_count, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
            ''',
            (
                project_id,
                user_id,
                f"Translation: {url}",
                url,
                source_language,
                target_language,
                result['pages_count'],
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
    project_id: str,
    url: str,
    source_language: str,
    target_language: str,
    word_count: int,
    user_id: str,
    cursor: RealDictCursor = Depends(get_db)
):
    """Start website translation job"""
    from src.core.marian_translator import translate_content
    from src.core.html_reconstructor import rebuild_website
    import boto3

    try:
        # Update project status
        cursor.execute(
            "UPDATE projects SET status = %s WHERE id = %s AND user_id = %s",
            ('processing', project_id, user_id)
        )

        # This would normally be a background job via SQS
        # For MVP, we'll process synchronously (with timeout limits)

        # TODO: Implement actual translation pipeline
        # 1. Extract HTML from crawled pages
        # 2. Translate content using MarianMT or Claude API
        # 3. Rebuild HTML with translated content
        # 4. Generate ZIP file
        # 5. Upload to S3
        # 6. Update project with download URL

        # For now, return pending status
        return {
            'project_id': project_id,
            'status': 'processing',
            'progress': 0,
            'status_message': 'Translation queued'
        }

    except Exception as e:
        cursor.execute(
            "UPDATE projects SET status = %s WHERE id = %s",
            ('failed', project_id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation failed: {str(e)}"
        )