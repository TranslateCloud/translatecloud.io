from fastapi import APIRouter, Depends, HTTPException, status
from psycopg2.extras import RealDictCursor
from src.config.database import get_db
from src.schemas.translation import TranslationCreate, TranslationResponse
from typing import List
import uuid

router = APIRouter()

@router.get("/", response_model=List[TranslationResponse])
async def get_translations(
    project_id: str,
    cursor: RealDictCursor = Depends(get_db)
):
    cursor.execute(
        '''
        SELECT t.* FROM translations t
        JOIN projects p ON t.project_id = p.id
        WHERE t.project_id = %s
        ORDER BY t.created_at DESC
        ''',
        (project_id,)
    )
    translations = cursor.fetchall()
    return translations

@router.post("/", response_model=TranslationResponse, status_code=status.HTTP_201_CREATED)
async def create_translation(
    translation: TranslationCreate,
    cursor: RealDictCursor = Depends(get_db)
):
    cursor.execute(
        "SELECT id FROM projects WHERE id = %s",
        (str(translation.project_id),)
    )
    project = cursor.fetchone()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    translation_id = str(uuid.uuid4())
    word_count = len(translation.source_text.split())
    
    cursor.execute(
        '''
        INSERT INTO translations 
        (id, project_id, source_lang, target_lang, source_text, word_count, engine, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *
        ''',
        (
            translation_id,
            str(translation.project_id),
            translation.source_lang,
            translation.target_lang,
            translation.source_text,
            word_count,
            'marianmt',
            'pending'
        )
    )
    
    new_translation = cursor.fetchone()
    return new_translation

@router.get("/{translation_id}", response_model=TranslationResponse)
async def get_translation(
    translation_id: str,
    cursor: RealDictCursor = Depends(get_db)
):
    cursor.execute(
        "SELECT * FROM translations WHERE id = %s",
        (translation_id,)
    )
    translation = cursor.fetchone()
    
    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation not found"
        )
    
    return translation