from fastapi import APIRouter, Depends, HTTPException, status
from psycopg2.extras import RealDictCursor
from src.config.database import get_db
from src.schemas.translation import TranslationCreate, TranslationResponse
from typing import List
import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

# Import translation service from main.py
def get_translation_service():
    """Get translation service instance"""
    from src.main import get_translation_service as _get_translation_service
    return _get_translation_service()

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
    """
    Create a new translation using DeepL API

    1. Validates project exists
    2. Calls DeepL API to translate text
    3. Stores translation in database
    4. Returns translation result
    """
    # Verify project exists
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

    # Get translation service
    try:
        service = get_translation_service()

        # Translate text using DeepL
        logger.info(f"Translating text from {translation.source_lang} to {translation.target_lang}")
        translated_text = service.translate(
            text=translation.source_text,
            source_lang=translation.source_lang,
            target_lang=translation.target_lang
        )

        # Determine which engine was used
        engine = service.get_status()['primary_provider'] or 'fallback'
        translation_status = 'completed'
        translated_at = datetime.utcnow()

        logger.info(f"Translation completed successfully using {engine}")

    except Exception as e:
        logger.error(f"Translation failed: {str(e)}")
        # Store translation as failed
        translated_text = None
        engine = 'error'
        translation_status = 'failed'
        translated_at = None

    # Store translation in database
    cursor.execute(
        '''
        INSERT INTO translations
        (id, project_id, source_lang, target_lang, source_text, translated_text,
         word_count, engine, status, translated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *
        ''',
        (
            translation_id,
            str(translation.project_id),
            translation.source_lang,
            translation.target_lang,
            translation.source_text,
            translated_text,
            word_count,
            engine,
            translation_status,
            translated_at
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