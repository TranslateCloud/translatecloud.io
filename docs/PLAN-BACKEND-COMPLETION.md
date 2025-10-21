# Plan de Completación - Backend TranslateCloud

**Fecha:** 21 de Octubre 2025
**Objetivo:** Completar funcionalidades backend para traducción de archivos y texto
**Timeline:** Hoy + Mañana (22 Oct)
**Deploy:** Antes del lanzamiento (27 Oct)

---

## 🎯 ESTADO ACTUAL

### ✅ YA TENEMOS
1. **Website Translation**
   - Web crawler (web_extractor.py)
   - HTML reconstructor (html_reconstructor.py)
   - Async jobs (job_manager.py)
   - DeepL integration (deepl_translator.py)

2. **Infraestructura**
   - Translation service (translation_service.py)
   - Database models
   - API routes (projects.py, jobs.py)
   - Auth system (JWT)

### ❌ FALTA IMPLEMENTAR

1. **File Translation (Apps)**
   - Parser JSON (React Native, general i18n)
   - Parser XML (Android strings.xml)
   - Parser Strings (iOS Localizable.strings)
   - Parser ARB (Flutter)
   - Placeholder preservation

2. **Text Translation**
   - Endpoint simple para traducir texto
   - Sin archivo, solo input/output de texto

3. **API Endpoints**
   - POST /api/files/translate (upload file → translate → download)
   - POST /api/text/translate (text → text translation)

---

## 📋 PLAN DE IMPLEMENTACIÓN

### FASE 1: File Parsers (2-3 horas)

#### 1.1 Crear File Parser Base

**Archivo:** `backend/src/core/file_parser.py`

```python
"""
File Parser - Parse localization files for translation

Supports:
- JSON: React Native, general i18n files
- XML: Android strings.xml
- Strings: iOS Localizable.strings
- ARB: Flutter app resource bundles

Preserves:
- Placeholders: %s, %d, {0}, {{var}}, $variable
- Structure: Keys, metadata, formatting
- Comments: XML/JSON comments
"""

import json
import xml.etree.ElementTree as ET
import re
from typing import Dict, List, Tuple, Optional
from enum import Enum

class FileFormat(Enum):
    JSON = "json"
    XML = "xml"
    STRINGS = "strings"
    ARB = "arb"
    UNKNOWN = "unknown"

class FilePars

er:
    """
    Universal parser for app localization files
    """

    @staticmethod
    def detect_format(filename: str, content: str) -> FileFormat:
        """
        Detect file format from filename and content
        """
        filename_lower = filename.lower()

        # Check by filename
        if filename_lower.endswith('.json'):
            return FileFormat.JSON
        elif filename_lower.endswith('.xml'):
            return FileFormat.XML
        elif filename_lower.endswith('.strings'):
            return FileFormat.STRINGS
        elif filename_lower.endswith('.arb'):
            return FileFormat.ARB

        # Check by content
        content_stripped = content.strip()

        if content_stripped.startswith('{'):
            return FileFormat.JSON
        elif content_stripped.startswith('<?xml') or content_stripped.startswith('<resources'):
            return FileFormat.XML
        elif '"' in content and '=' in content and ';' in content:
            return FileFormat.STRINGS

        return FileFormat.UNKNOWN

    @staticmethod
    def parse_json(content: str) -> Dict[str, str]:
        """
        Parse JSON localization file (React Native, i18n)

        Input:
            {
              "welcome": "Welcome to our app",
              "login_button": "Sign In",
              "greeting": "Hello {name}!"
            }

        Output:
            {
              "welcome": "Welcome to our app",
              "login_button": "Sign In",
              "greeting": "Hello {name}!"
            }
        """
        try:
            data = json.loads(content)
            return FileParser._flatten_json(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")

    @staticmethod
    def _flatten_json(data: dict, prefix: str = "") -> Dict[str, str]:
        """
        Flatten nested JSON structure

        Input: {"auth": {"login": "Log in"}}
        Output: {"auth.login": "Log in"}
        """
        result = {}

        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict):
                # Nested object - recurse
                result.update(FileParser._flatten_json(value, full_key))
            elif isinstance(value, str):
                # String value - add to results
                result[full_key] = value
            # Skip non-string values (numbers, arrays, etc.)

        return result

    @staticmethod
    def parse_xml(content: str) -> Dict[str, str]:
        """
        Parse Android strings.xml file

        Input:
            <resources>
                <string name="app_name">MyApp</string>
                <string name="welcome">Welcome %s!</string>
            </resources>

        Output:
            {
              "app_name": "MyApp",
              "welcome": "Welcome %s!"
            }
        """
        try:
            root = ET.fromstring(content)
            result = {}

            for string_elem in root.findall('string'):
                name = string_elem.get('name')
                text = string_elem.text or ""

                if name:
                    result[name] = text

            return result

        except ET.ParseError as e:
            raise ValueError(f"Invalid XML: {e}")

    @staticmethod
    def parse_strings(content: str) -> Dict[str, str]:
        """
        Parse iOS Localizable.strings file

        Input:
            "welcome" = "Welcome to our app";
            "login_button" = "Sign In";
            /* Comment */
            "greeting" = "Hello %@!";

        Output:
            {
              "welcome": "Welcome to our app",
              "login_button": "Sign In",
              "greeting": "Hello %@!"
            }
        """
        result = {}

        # Pattern: "key" = "value";
        pattern = r'"([^"]+)"\s*=\s*"([^"]*)";'

        for match in re.finditer(pattern, content):
            key = match.group(1)
            value = match.group(2)
            result[key] = value

        return result

    @staticmethod
    def parse_arb(content: str) -> Dict[str, str]:
        """
        Parse Flutter ARB (Application Resource Bundle) file

        Input:
            {
              "welcome": "Welcome to our app",
              "@welcome": {
                "description": "Welcome message"
              },
              "greeting": "Hello {name}!"
            }

        Output:
            {
              "welcome": "Welcome to our app",
              "greeting": "Hello {name}!"
            }
        """
        try:
            data = json.loads(content)
            result = {}

            for key, value in data.items():
                # Skip metadata keys (start with @)
                if not key.startswith('@') and isinstance(value, str):
                    result[key] = value

            return result

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid ARB (JSON): {e}")

    @staticmethod
    def reconstruct_json(translations: Dict[str, str]) -> str:
        """
        Reconstruct JSON file from flat translations

        Input: {"auth.login": "Iniciar sesión"}
        Output: {"auth": {"login": "Iniciar sesión"}}
        """
        nested = {}

        for key, value in translations.items():
            parts = key.split('.')
            current = nested

            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]

            current[parts[-1]] = value

        return json.dumps(nested, indent=2, ensure_ascii=False)

    @staticmethod
    def reconstruct_xml(translations: Dict[str, str]) -> str:
        """
        Reconstruct Android strings.xml file

        Input: {"app_name": "MiApp", "welcome": "Bienvenido"}
        Output: <resources><string name="app_name">MiApp</string>...</resources>
        """
        root = ET.Element('resources')

        for key, value in translations.items():
            string_elem = ET.SubElement(root, 'string')
            string_elem.set('name', key)
            string_elem.text = value

        # Pretty print XML
        ET.indent(root, space='    ')
        xml_str = ET.tostring(root, encoding='unicode')
        return f'<?xml version="1.0" encoding="utf-8"?>\n{xml_str}'

    @staticmethod
    def reconstruct_strings(translations: Dict[str, str]) -> str:
        """
        Reconstruct iOS Localizable.strings file

        Input: {"welcome": "Bienvenido", "login": "Iniciar sesión"}
        Output: "welcome" = "Bienvenido";\n"login" = "Iniciar sesión";
        """
        lines = []

        for key, value in translations.items():
            # Escape quotes in value
            value_escaped = value.replace('"', '\\"')
            lines.append(f'"{key}" = "{value_escaped}";')

        return '\n'.join(lines)

    @staticmethod
    def reconstruct_arb(translations: Dict[str, str]) -> str:
        """
        Reconstruct Flutter ARB file

        Input: {"welcome": "Bienvenido"}
        Output: {"welcome": "Bienvenido"}
        """
        return json.dumps(translations, indent=2, ensure_ascii=False)
```

#### 1.2 Crear Placeholder Protector

**Archivo:** `backend/src/core/placeholder_protector.py`

```python
"""
Placeholder Protector - Preserve code placeholders during translation

Protects:
- Format specifiers: %s, %d, %f, %@
- Positional: {0}, {1}, {2}
- Named: {name}, {count}, {{variable}}
- Variables: $variable, ${var}
- HTML entities: &amp;, &lt;, &nbsp;
"""

import re
from typing import Tuple, Dict

class PlaceholderProtector:
    """
    Protect placeholders from being translated
    """

    # Placeholder patterns
    PATTERNS = [
        (r'%[sdif@]', 'FORMAT'),           # %s, %d, %i, %f, %@
        (r'%\d+\$[sdif]', 'POSITIONAL'),   # %1$s, %2$d
        (r'\{\d+\}', 'POSITIONAL'),        # {0}, {1}, {2}
        (r'\{[a-zA-Z_]\w*\}', 'NAMED'),    # {name}, {count}
        (r'\{\{[a-zA-Z_]\w*\}\}', 'TEMPLATE'), # {{variable}}
        (r'\$\{?\w+\}?', 'VARIABLE'),      # $var, ${var}
        (r'&[a-z]+;', 'ENTITY'),           # &amp;, &nbsp;
        (r'<[^>]+>', 'HTML'),              # <b>, </span>
    ]

    @staticmethod
    def protect(text: str) -> Tuple[str, Dict[str, str]]:
        """
        Replace placeholders with tokens before translation

        Input: "Hello {name}! You have %d messages"
        Output: ("Hello __PH0__! You have __PH1__ messages", {
            "__PH0__": "{name}",
            "__PH1__": "%d"
        })
        """
        protected_text = text
        placeholders = {}
        counter = 0

        for pattern, placeholder_type in PlaceholderProtector.PATTERNS:
            matches = re.finditer(pattern, protected_text)

            for match in matches:
                original = match.group(0)
                token = f"__PH{counter}__"

                protected_text = protected_text.replace(original, token, 1)
                placeholders[token] = original
                counter += 1

        return protected_text, placeholders

    @staticmethod
    def restore(text: str, placeholders: Dict[str, str]) -> str:
        """
        Restore original placeholders after translation

        Input: ("Hola __PH0__! Tienes __PH1__ mensajes", {
            "__PH0__": "{name}",
            "__PH1__": "%d"
        })
        Output: "Hola {name}! Tienes %d mensajes"
        """
        restored_text = text

        for token, original in placeholders.items():
            restored_text = restored_text.replace(token, original)

        return restored_text
```

---

### FASE 2: API Endpoints (1-2 horas)

#### 2.1 File Translation Endpoint

**Archivo:** `backend/src/api/routes/files.py`

```python
"""
File Translation API Routes

Endpoints:
- POST /api/files/translate - Upload file → translate → download ZIP
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from typing import List
import io
import zipfile
import logging

from src.core.file_parser import FileParser, FileFormat
from src.core.placeholder_protector import PlaceholderProtector
from src.core.translation_service import TranslationService
from src.config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/files", tags=["files"])

# Initialize translation service
translation_service = None

def get_translation_service():
    global translation_service
    if translation_service is None:
        translation_service = TranslationService(deepl_api_key=settings.DEEPL_API_KEY)
    return translation_service


@router.post("/translate")
async def translate_file(
    file: UploadFile = File(...),
    source_lang: str = Form(...),
    target_langs: str = Form(...)  # Comma-separated: "es,fr,de"
):
    """
    Translate app localization file to multiple languages

    Request:
        - file: Localization file (JSON, XML, strings, ARB)
        - source_lang: Source language code (en, es, etc.)
        - target_langs: Comma-separated target languages (es,fr,de)

    Response:
        ZIP file containing translated files for each target language

    Example:
        Upload: en.json
        Target langs: es,fr
        Download: translations.zip
            ├── es.json
            └── fr.json
    """
    try:
        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8')

        # Detect format
        file_format = FileParser.detect_format(file.filename, content_str)

        if file_format == FileFormat.UNKNOWN:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format. Supported: JSON, XML, strings, ARB"
            )

        logger.info(f"Detected format: {file_format.value} for file: {file.filename}")

        # Parse file
        if file_format == FileFormat.JSON:
            translations_dict = FileParser.parse_json(content_str)
        elif file_format == FileFormat.XML:
            translations_dict = FileParser.parse_xml(content_str)
        elif file_format == FileFormat.STRINGS:
            translations_dict = FileParser.parse_strings(content_str)
        elif file_format == FileFormat.ARB:
            translations_dict = FileParser.parse_arb(content_str)

        logger.info(f"Parsed {len(translations_dict)} strings from file")

        # Split target languages
        target_lang_list = [lang.strip() for lang in target_langs.split(',')]

        # Get translation service
        service = get_translation_service()

        # Translate to each target language
        translated_files = {}

        for target_lang in target_lang_list:
            logger.info(f"Translating to {target_lang}...")

            translated_dict = {}

            for key, text in translations_dict.items():
                # Protect placeholders
                protected_text, placeholders = PlaceholderProtector.protect(text)

                # Translate
                result = await service.translate(protected_text, source_lang, target_lang)

                if result['success']:
                    # Restore placeholders
                    translated_text = PlaceholderProtector.restore(
                        result['text'],
                        placeholders
                    )
                    translated_dict[key] = translated_text
                else:
                    # Keep original if translation fails
                    translated_dict[key] = text
                    logger.warning(f"Translation failed for key '{key}': {result.get('error')}")

            # Reconstruct file
            if file_format == FileFormat.JSON:
                reconstructed = FileParser.reconstruct_json(translated_dict)
                filename = f"{target_lang}.json"
            elif file_format == FileFormat.XML:
                reconstructed = FileParser.reconstruct_xml(translated_dict)
                filename = f"strings-{target_lang}.xml"
            elif file_format == FileFormat.STRINGS:
                reconstructed = FileParser.reconstruct_strings(translated_dict)
                filename = f"Localizable-{target_lang}.strings"
            elif file_format == FileFormat.ARB:
                reconstructed = FileParser.reconstruct_arb(translated_dict)
                filename = f"app_{target_lang}.arb"

            translated_files[filename] = reconstructed

        # Create ZIP file in memory
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename, content in translated_files.items():
                zip_file.writestr(filename, content)

        zip_buffer.seek(0)

        # Return ZIP as download
        return StreamingResponse(
            zip_buffer,
            media_type='application/zip',
            headers={'Content-Disposition': 'attachment; filename=translations.zip'}
        )

    except Exception as e:
        logger.error(f"File translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

#### 2.2 Text Translation Endpoint

**Archivo:** `backend/src/api/routes/text.py`

```python
"""
Text Translation API Routes

Simple text-to-text translation without files
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

from src.core.translation_service import TranslationService
from src.config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/text", tags=["text"])

# Initialize translation service
translation_service = None

def get_translation_service():
    global translation_service
    if translation_service is None:
        translation_service = TranslationService(deepl_api_key=settings.DEEPL_API_KEY)
    return translation_service


class TextTranslateRequest(BaseModel):
    text: str
    source_lang: str = "auto"
    target_lang: str

class TextTranslateResponse(BaseModel):
    original_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    provider: str  # deepl or marian
    characters_used: int


@router.post("/translate", response_model=TextTranslateResponse)
async def translate_text(request: TextTranslateRequest):
    """
    Translate plain text (no file upload needed)

    Request:
        {
          "text": "Hello world",
          "source_lang": "en",
          "target_lang": "es"
        }

    Response:
        {
          "original_text": "Hello world",
          "translated_text": "Hola mundo",
          "source_lang": "en",
          "target_lang": "es",
          "provider": "deepl",
          "characters_used": 11
        }
    """
    try:
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        service = get_translation_service()

        result = await service.translate(
            request.text,
            request.source_lang,
            request.target_lang
        )

        if not result['success']:
            raise HTTPException(
                status_code=500,
                detail=f"Translation failed: {result.get('error', 'Unknown error')}"
            )

        return TextTranslateResponse(
            original_text=request.text,
            translated_text=result['text'],
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            provider=result['provider'],
            characters_used=len(request.text)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

### FASE 3: Integration (1 hora)

#### 3.1 Actualizar main.py

```python
# backend/src/main.py

# Add new routes
from src.api.routes import files, text

app.include_router(files.router)
app.include_router(text.router)
```

#### 3.2 Update requirements.txt

Ya están todas las dependencias necesarias ✅

---

## 🧪 TESTING

### Test File Translation

```bash
# Upload JSON file
curl -X POST http://localhost:8000/api/files/translate \
  -F "file=@en.json" \
  -F "source_lang=en" \
  -F "target_langs=es,fr,de" \
  --output translations.zip

# Upload Android XML
curl -X POST http://localhost:8000/api/files/translate \
  -F "file=@strings.xml" \
  -F "source_lang=en" \
  -F "target_langs=es" \
  --output translations.zip
```

### Test Text Translation

```bash
curl -X POST http://localhost:8000/api/text/translate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world! My name is {name}",
    "source_lang": "en",
    "target_lang": "es"
  }'
```

---

## 📅 CRONOGRAMA

### HOY (21 Oct) - 4 horas
- [x] Revisar backend actual
- [ ] Crear FileParser class (1.5h)
- [ ] Crear PlaceholderProtector class (0.5h)
- [ ] Crear files.py endpoint (1h)
- [ ] Crear text.py endpoint (0.5h)
- [ ] Testing local (0.5h)

### MAÑANA (22 Oct) - 2 horas
- [ ] Deploy a Lambda
- [ ] Test en AWS
- [ ] Fix any issues
- [ ] Documentation

---

## ✅ CHECKLIST FINAL

- [ ] FileParser supports JSON
- [ ] FileParser supports XML
- [ ] FileParser supports iOS strings
- [ ] FileParser supports Flutter ARB
- [ ] Placeholders preserved (%s, {0}, {{var}})
- [ ] POST /api/files/translate works
- [ ] POST /api/text/translate works
- [ ] Returns ZIP with all languages
- [ ] Error handling robust
- [ ] Deployed to Lambda
- [ ] Tested in production

---

**¿Empezamos con la implementación ahora?**
