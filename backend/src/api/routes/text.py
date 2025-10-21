"""
Text API - Simple text-to-text translation
For quick translations without file uploads
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from src.core.translation_service import TranslationService
from src.core.placeholder_protector import PlaceholderProtector
from src.api.dependencies import get_current_user


router = APIRouter(prefix="/api/text", tags=["text"])


class TextTranslateRequest(BaseModel):
    """Request model for text translation"""

    text: str = Field(..., min_length=1, max_length=10000, description="Text to translate")
    source_lang: str = Field(..., min_length=2, max_length=5, description="Source language code (e.g., 'en')")
    target_langs: List[str] = Field(..., min_items=1, max_items=10, description="List of target language codes")
    preserve_placeholders: bool = Field(default=True, description="Preserve code placeholders (%s, {name}, etc.)")


class TranslationResult(BaseModel):
    """Single translation result"""

    target_lang: str
    translated_text: str
    original_length: int
    translated_length: int
    placeholders_preserved: Optional[int] = None


class TextTranslateResponse(BaseModel):
    """Response model for text translation"""

    success: bool
    source_language: str
    original_text: str
    translations: List[TranslationResult]
    total_characters: int


class BatchTextTranslateRequest(BaseModel):
    """Request model for batch text translation"""

    texts: List[str] = Field(..., min_items=1, max_items=100)
    source_lang: str
    target_lang: str
    preserve_placeholders: bool = Field(default=True)


class BatchTranslationResult(BaseModel):
    """Result for batch translation"""

    original: str
    translated: str
    index: int


class BatchTextTranslateResponse(BaseModel):
    """Response for batch translation"""

    success: bool
    source_language: str
    target_language: str
    results: List[BatchTranslationResult]
    total_characters: int


@router.post("/translate", response_model=TextTranslateResponse)
async def translate_text(
    request: TextTranslateRequest,
    current_user = Depends(get_current_user)
):
    """
    Translate text to one or multiple target languages

    Features:
    - Automatic placeholder preservation (optional)
    - Multiple target languages in one request
    - Character count tracking

    Example:
        POST /api/text/translate
        {
            "text": "Welcome {name}! You have %d messages.",
            "source_lang": "en",
            "target_langs": ["es", "fr"],
            "preserve_placeholders": true
        }

        Returns:
        {
            "success": true,
            "source_language": "en",
            "original_text": "Welcome {name}! You have %d messages.",
            "translations": [
                {
                    "target_lang": "es",
                    "translated_text": "¡Bienvenido {name}! Tienes %d mensajes.",
                    "original_length": 38,
                    "translated_length": 40,
                    "placeholders_preserved": 2
                },
                {
                    "target_lang": "fr",
                    "translated_text": "Bienvenue {name} ! Vous avez %d messages.",
                    "original_length": 38,
                    "translated_length": 42,
                    "placeholders_preserved": 2
                }
            ],
            "total_characters": 76
        }
    """

    try:
        translation_service = TranslationService()
        translations = []

        # Protect placeholders if requested
        if request.preserve_placeholders:
            protected_text, placeholder_map = PlaceholderProtector.protect(request.text)
        else:
            protected_text = request.text
            placeholder_map = {}

        # Translate to each target language
        for target_lang in request.target_langs:
            try:
                # Translate
                result = await translation_service.translate(
                    text=protected_text,
                    source_lang=request.source_lang,
                    target_lang=target_lang
                )

                if not result['success']:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Translation to {target_lang} failed: {result.get('error', 'Unknown error')}"
                    )

                translated_text = result['text']

                # Restore placeholders
                if request.preserve_placeholders and placeholder_map:
                    translated_text = PlaceholderProtector.restore(translated_text, placeholder_map)

                # Create result
                result = TranslationResult(
                    target_lang=target_lang,
                    translated_text=translated_text,
                    original_length=len(request.text),
                    translated_length=len(translated_text),
                    placeholders_preserved=len(placeholder_map) if placeholder_map else None
                )

                translations.append(result)

            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Translation to {target_lang} failed: {str(e)}"
                )

        # Calculate total characters
        total_chars = sum(len(request.text) for _ in request.target_langs)

        return TextTranslateResponse(
            success=True,
            source_language=request.source_lang,
            original_text=request.text,
            translations=translations,
            total_characters=total_chars
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@router.post("/translate/batch", response_model=BatchTextTranslateResponse)
async def translate_batch(
    request: BatchTextTranslateRequest,
    current_user = Depends(get_current_user)
):
    """
    Translate multiple texts to a single target language

    Useful for:
    - Translating UI strings in bulk
    - Processing large translation lists
    - Batch operations

    Limitations:
    - Max 100 texts per request
    - Each text max 10,000 characters
    - Single target language only

    Example:
        POST /api/text/translate/batch
        {
            "texts": ["Hello", "Goodbye", "Welcome {name}"],
            "source_lang": "en",
            "target_lang": "es",
            "preserve_placeholders": true
        }
    """

    try:
        if len(request.texts) > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 texts per batch")

        translation_service = TranslationService()
        results = []
        total_chars = 0

        for index, text in enumerate(request.texts):
            if len(text) > 10000:
                raise HTTPException(
                    status_code=400,
                    detail=f"Text at index {index} exceeds 10,000 characters"
                )

            # Protect placeholders
            if request.preserve_placeholders:
                protected_text, placeholder_map = PlaceholderProtector.protect(text)
            else:
                protected_text = text
                placeholder_map = {}

            # Translate
            try:
                result = await translation_service.translate(
                    text=protected_text,
                    source_lang=request.source_lang,
                    target_lang=request.target_lang
                )

                if not result['success']:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Translation failed at index {index}: {result.get('error', 'Unknown error')}"
                    )

                translated_text = result['text']

                # Restore placeholders
                if request.preserve_placeholders and placeholder_map:
                    translated_text = PlaceholderProtector.restore(translated_text, placeholder_map)

                # Add result
                results.append(BatchTranslationResult(
                    original=text,
                    translated=translated_text,
                    index=index
                ))

                total_chars += len(text)

            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Translation failed at index {index}: {str(e)}"
                )

        return BatchTextTranslateResponse(
            success=True,
            source_language=request.source_lang,
            target_language=request.target_lang,
            results=results,
            total_characters=total_chars
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch translation failed: {str(e)}")


@router.post("/detect-language")
async def detect_language(
    text: str,
    current_user = Depends(get_current_user)
):
    """
    Detect the language of input text

    Useful for:
    - Auto-detecting source language
    - Language verification
    - Pre-translation validation

    Example:
        POST /api/text/detect-language
        {
            "text": "Bonjour le monde"
        }

        Returns:
        {
            "success": true,
            "detected_language": "fr",
            "confidence": 0.99
        }
    """

    try:
        # Note: DeepL API supports language detection
        # For now, return placeholder - can be implemented with langdetect library
        # or DeepL's detection endpoint

        return {
            "success": True,
            "message": "Language detection coming soon",
            "text_sample": text[:100]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Language detection failed: {str(e)}")


@router.get("/languages")
async def get_supported_languages():
    """
    Get list of supported languages

    Returns:
    - Language codes
    - Language names
    - Source/target availability
    """

    # DeepL supported languages (as of 2025)
    languages = [
        {"code": "en", "name": "English", "source": True, "target": True},
        {"code": "es", "name": "Spanish", "source": True, "target": True},
        {"code": "fr", "name": "French", "source": True, "target": True},
        {"code": "de", "name": "German", "source": True, "target": True},
        {"code": "it", "name": "Italian", "source": True, "target": True},
        {"code": "pt", "name": "Portuguese", "source": True, "target": True},
        {"code": "ru", "name": "Russian", "source": True, "target": True},
        {"code": "ja", "name": "Japanese", "source": True, "target": True},
        {"code": "zh", "name": "Chinese", "source": True, "target": True},
        {"code": "nl", "name": "Dutch", "source": True, "target": True},
        {"code": "pl", "name": "Polish", "source": True, "target": True},
        {"code": "sv", "name": "Swedish", "source": True, "target": True},
        {"code": "da", "name": "Danish", "source": True, "target": True},
        {"code": "fi", "name": "Finnish", "source": True, "target": True},
        {"code": "no", "name": "Norwegian", "source": True, "target": True},
        {"code": "cs", "name": "Czech", "source": True, "target": True},
        {"code": "ro", "name": "Romanian", "source": True, "target": True},
        {"code": "sk", "name": "Slovak", "source": True, "target": True},
        {"code": "tr", "name": "Turkish", "source": True, "target": True},
        {"code": "el", "name": "Greek", "source": True, "target": True},
        {"code": "hu", "name": "Hungarian", "source": True, "target": True},
        {"code": "bg", "name": "Bulgarian", "source": True, "target": True},
        {"code": "et", "name": "Estonian", "source": True, "target": True},
        {"code": "lv", "name": "Latvian", "source": True, "target": True},
        {"code": "lt", "name": "Lithuanian", "source": True, "target": True},
        {"code": "sl", "name": "Slovenian", "source": True, "target": True},
        {"code": "uk", "name": "Ukrainian", "source": True, "target": True},
        {"code": "ko", "name": "Korean", "source": True, "target": True},
        {"code": "id", "name": "Indonesian", "source": True, "target": True},
        {"code": "ar", "name": "Arabic", "source": True, "target": True},
    ]

    return {
        "success": True,
        "languages": languages,
        "total": len(languages)
    }
