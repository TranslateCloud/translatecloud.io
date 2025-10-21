"""
Files API - Translation of localization files (JSON, XML, strings, ARB)
Supports: React Native, Android, iOS, Flutter
"""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from typing import List, Optional
import json
import zipfile
import io
import os

from src.core.file_parser import FileParser, FileFormat, TranslationStatistics
from src.core.placeholder_protector import PlaceholderProtector, PlaceholderStats
from src.core.translation_service import TranslationService
from src.api.dependencies import get_current_user


router = APIRouter(prefix="/api/files", tags=["files"])


@router.post("/translate")
async def translate_file(
    file: UploadFile = File(...),
    source_lang: str = Form(...),
    target_langs: str = Form(...),  # Comma-separated: "es,fr,de"
    current_user = Depends(get_current_user)
):
    """
    Translate localization files to multiple target languages

    Supported formats:
    - JSON (React Native, i18n)
    - XML (Android strings.xml)
    - strings (iOS Localizable.strings)
    - ARB (Flutter)

    Returns:
    - Single file: translated file
    - Multiple languages: ZIP file with all translations

    Example:
        POST /api/files/translate
        file: en.json
        source_lang: en
        target_langs: es,fr,de

        Returns: translations.zip containing:
        - es.json
        - fr.json
        - de.json
    """

    try:
        # Parse target languages
        target_lang_list = [lang.strip() for lang in target_langs.split(',')]

        if not target_lang_list:
            raise HTTPException(status_code=400, detail="No target languages specified")

        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8')

        # Detect file format
        file_format = FileParser.detect_format(file.filename, content_str)

        if file_format == FileFormat.UNKNOWN:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Supported: .json, .xml, .strings, .arb"
            )

        # Parse file to extract strings
        strings = FileParser.parse(content_str, file_format)

        if not strings:
            raise HTTPException(status_code=400, detail="No translatable strings found in file")

        # Get statistics
        stats = TranslationStatistics.analyze(strings)

        # Check DeepL quota (estimate)
        # Each target language will consume stats['total_characters']
        total_chars_needed = stats['total_characters'] * len(target_lang_list)

        # Protect placeholders before translation
        protected_strings, placeholder_maps = PlaceholderProtector.protect_batch(strings)

        # Initialize translation service
        translation_service = TranslationService()

        # Translate to each target language
        translations_by_lang = {}

        for target_lang in target_lang_list:
            # Translate all strings
            translated_strings = {}

            for key, protected_value in protected_strings.items():
                try:
                    # Translate using translation service
                    result = await translation_service.translate(
                        text=protected_value,
                        source_lang=source_lang,
                        target_lang=target_lang
                    )

                    if result['success']:
                        translated_strings[key] = result['text']
                    else:
                        # If translation fails, keep original
                        translated_strings[key] = strings[key]

                except Exception as e:
                    # If individual translation fails, keep original
                    translated_strings[key] = strings[key]

            # Restore placeholders
            restored_strings = PlaceholderProtector.restore_batch(
                translated_strings,
                placeholder_maps
            )

            # Reconstruct file in original format
            reconstructed_content = FileParser.reconstruct(
                restored_strings,
                file_format,
                content_str  # Pass original to preserve structure
            )

            translations_by_lang[target_lang] = reconstructed_content

        # Return results
        if len(target_lang_list) == 1:
            # Single file - return directly
            target_lang = target_lang_list[0]
            filename = _get_output_filename(file.filename, target_lang, file_format)

            return {
                "success": True,
                "source_language": source_lang,
                "target_language": target_lang,
                "filename": filename,
                "content": translations_by_lang[target_lang],
                "statistics": stats
            }
        else:
            # Multiple files - create ZIP
            zip_buffer = io.BytesIO()

            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for target_lang, content in translations_by_lang.items():
                    filename = _get_output_filename(file.filename, target_lang, file_format)
                    zip_file.writestr(filename, content)

            zip_buffer.seek(0)

            return {
                "success": True,
                "source_language": source_lang,
                "target_languages": target_lang_list,
                "filename": "translations.zip",
                "content": zip_buffer.getvalue().decode('latin1'),  # Base64 alternative
                "statistics": stats,
                "file_count": len(target_lang_list)
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@router.post("/analyze")
async def analyze_file(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """
    Analyze localization file without translating

    Returns statistics:
    - Total keys
    - Total characters
    - Estimated translation cost
    - Placeholder complexity
    - Detected format
    """

    try:
        # Read file
        content = await file.read()
        content_str = content.decode('utf-8')

        # Detect format
        file_format = FileParser.detect_format(file.filename, content_str)

        if file_format == FileFormat.UNKNOWN:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        # Parse file
        strings = FileParser.parse(content_str, file_format)

        # Get statistics
        stats = TranslationStatistics.analyze(strings)

        # Analyze placeholders
        placeholder_types = PlaceholderStats.count_by_type(strings)
        complexity_score = PlaceholderStats.get_complexity_score(strings)

        return {
            "success": True,
            "filename": file.filename,
            "format": file_format.value,
            "statistics": stats,
            "placeholders": {
                "types": placeholder_types,
                "complexity_score": complexity_score
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/formats")
async def get_supported_formats():
    """
    Get list of supported file formats

    Returns information about each format:
    - Extension
    - Platform
    - Example
    """

    formats = [
        {
            "format": "json",
            "extension": ".json",
            "platforms": ["React Native", "React", "Vue", "Angular", "Generic i18n"],
            "example": '{"welcome": "Welcome!", "user": {"name": "Name"}}',
            "supports_nesting": True
        },
        {
            "format": "xml",
            "extension": ".xml",
            "platforms": ["Android"],
            "example": '<resources><string name="app_name">MyApp</string></resources>',
            "supports_nesting": False
        },
        {
            "format": "strings",
            "extension": ".strings",
            "platforms": ["iOS", "macOS"],
            "example": '"app_name" = "MyApp";',
            "supports_nesting": False
        },
        {
            "format": "arb",
            "extension": ".arb",
            "platforms": ["Flutter"],
            "example": '{"@@locale": "en", "title": "Title"}',
            "supports_nesting": False
        }
    ]

    return {
        "success": True,
        "formats": formats
    }


def _get_output_filename(original_filename: str, target_lang: str, file_format: FileFormat) -> str:
    """
    Generate output filename based on target language

    Examples:
        en.json + es → es.json
        Localizable.strings + fr → Localizable_fr.strings
        strings.xml + de → values-de/strings.xml (Android convention)
    """

    name, ext = os.path.splitext(original_filename)

    if file_format == FileFormat.XML:
        # Android convention: values-es/strings.xml
        return f"values-{target_lang}/strings.xml"
    elif file_format == FileFormat.JSON:
        # Simple replacement: en.json → es.json
        return f"{target_lang}.json"
    elif file_format == FileFormat.STRINGS:
        # iOS convention: Localizable_es.strings or es.lproj/Localizable.strings
        return f"{target_lang}.lproj/{original_filename}"
    elif file_format == FileFormat.ARB:
        # Flutter convention: intl_es.arb
        return f"intl_{target_lang}.arb"
    else:
        return f"{name}_{target_lang}{ext}"
