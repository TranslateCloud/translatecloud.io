# TRANSLATECLOUD - CONTEXTO PARA CLAUDE CODE (VS CODE)
**Propósito:** Recordatorio permanente de servicios de traducción faltantes
**Para:** Claude Code en Visual Studio Code
**Fecha:** 20 de Octubre de 2025

---

## ⚠️ CONTEXTO CRÍTICO: SERVICIOS FALTANTES

Al trabajar en este proyecto, **SIEMPRE recuerda** que TranslateCloud debe ofrecer **3 servicios de traducción**, pero actualmente SOLO tiene 1 parcialmente implementado:

### Estado Actual de Servicios

| Servicio | Estado | Prioridad | Archivos |
|----------|--------|-----------|----------|
| **1. Traducción de Sitios Web** | ⚠️ 70% (NO probado) | 🔴 CRÍTICA | `projects.py`, `web_extractor.py` |
| **2. Traducción de Documentos** | ❌ 0% (NO existe) | 🔴 CRÍTICA | Falta crear `documents.py` |
| **3. Traducción de Texto/Palabras** | ❌ 0% (NO existe) | 🔴 CRÍTICA | Falta crear `text.py` |

---

## 🎯 SERVICIO 1: TRADUCCIÓN DE SITIOS WEB (ACTUAL)

### Estado
- **Código:** Implementado en `backend/src/api/routes/projects.py`
- **Testing:** ⚠️ **NUNCA PROBADO EN PRODUCCIÓN**
- **Frontend:** `frontend/public/en/translate.html`

### Cómo funciona
1. Usuario ingresa URL → `/api/projects/crawl`
2. Backend crawlea hasta 50 páginas
3. Extrae elementos HTML traducibles (h1, p, title, meta)
4. Traduce con DeepL API
5. Reconstruye HTML → `/api/projects/translate`
6. Genera ZIP → `/api/projects/export/{id}`

### Problemas conocidos
- ❌ No probado end-to-end
- ❌ Timeout de Lambda (30s) puede ser insuficiente para sitios grandes
- ❌ No maneja JavaScript dinámico (React/Vue)
- ❌ Límites de palabras NO se aplican antes de traducir

### Archivos clave
```
backend/src/api/routes/projects.py        (383 líneas)
backend/src/core/web_extractor.py
backend/src/core/web_crawler.py
backend/src/core/html_reconstructor.py
backend/src/core/translation_service.py
frontend/public/en/translate.html         (552 líneas)
```

---

## 📄 SERVICIO 2: TRADUCCIÓN DE DOCUMENTOS (FALTA IMPLEMENTAR)

### ⚠️ CRÍTICO: Este servicio NO EXISTE pero es NECESARIO

### Qué debe hacer
Traducir archivos manteniendo formato:
- PDF (.pdf)
- Word (.docx, .doc)
- Excel (.xlsx, .xls)
- PowerPoint (.pptx, .ppt)

### Flujo de usuario esperado
```
1. Usuario va a /en/translate-documents.html (NO EXISTE)
2. Arrastra archivo PDF/Word/Excel
3. Selecciona idiomas (source → target)
4. Click "Translate Document"
5. Backend procesa archivo
6. Usuario descarga documento traducido
```

### Implementación requerida

#### Backend - Nuevo archivo
**Ubicación:** `backend/src/api/routes/documents.py`

```python
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from PyPDF2 import PdfReader
from docx import Document
import openpyxl
from src.core.translation_service import TranslationService
from src.api.dependencies.jwt_auth import get_current_user_id

router = APIRouter()

@router.post("/translate/document")
async def translate_document(
    file: UploadFile = File(...),
    source_lang: str,
    target_lang: str,
    user_id: str = Depends(get_current_user_id),
    cursor = Depends(get_db)
):
    """
    Traduce documentos PDF, Word, Excel manteniendo formato

    Args:
        file: Archivo subido por usuario
        source_lang: Idioma origen (ej: 'en')
        target_lang: Idioma destino (ej: 'es')
        user_id: ID del usuario autenticado

    Returns:
        Archivo traducido para descarga
    """

    # 1. Validar tipo de archivo
    file_extension = file.filename.split('.')[-1].lower()

    if file_extension not in ['pdf', 'docx', 'doc', 'xlsx', 'xls', 'pptx']:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_extension}"
        )

    # 2. Procesar según tipo
    if file_extension == 'pdf':
        return await translate_pdf(file, source_lang, target_lang, user_id, cursor)
    elif file_extension in ['docx', 'doc']:
        return await translate_word(file, source_lang, target_lang, user_id, cursor)
    elif file_extension in ['xlsx', 'xls']:
        return await translate_excel(file, source_lang, target_lang, user_id, cursor)
    elif file_extension == 'pptx':
        return await translate_powerpoint(file, source_lang, target_lang, user_id, cursor)


async def translate_pdf(file, source_lang, target_lang, user_id, cursor):
    """
    Traduce archivos PDF

    Proceso:
    1. Extraer texto con PyPDF2
    2. Traducir cada bloque de texto
    3. Generar nuevo PDF con reportlab
    4. Retornar archivo traducido
    """
    import tempfile
    import os
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from fastapi.responses import FileResponse

    try:
        # Leer PDF original
        pdf_reader = PdfReader(file.file)
        total_text = ""
        page_texts = []

        for page_num, page in enumerate(pdf_reader.pages):
            text = page.extract_text()
            page_texts.append(text)
            total_text += text + " "

        # Contar palabras totales
        word_count = len(total_text.split())

        # IMPORTANTE: Verificar límite de palabras del usuario
        cursor.execute(
            "SELECT word_limit, words_used_this_month, plan FROM users WHERE id = %s",
            (user_id,)
        )
        user = cursor.fetchone()

        if user['words_used_this_month'] + word_count > user['word_limit']:
            raise HTTPException(
                status_code=402,
                detail={
                    "error": "word_limit_exceeded",
                    "words_needed": word_count,
                    "words_available": user['word_limit'] - user['words_used_this_month'],
                    "current_plan": user['plan'],
                    "upgrade_url": "/en/pricing.html"
                }
            )

        # Traducir cada página
        translation_service = TranslationService()
        translated_pages = []

        for page_text in page_texts:
            if page_text.strip():  # Solo traducir si hay texto
                result = await translation_service.translate(
                    page_text,
                    source_lang,
                    target_lang
                )
                translated_pages.append(result['text'])
            else:
                translated_pages.append("")

        # Generar nuevo PDF con traducciones
        temp_dir = tempfile.mkdtemp()
        output_filename = f"translated_{file.filename}"
        output_path = os.path.join(temp_dir, output_filename)

        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter

        for page_text in translated_pages:
            # Escribir texto traducido
            text_object = c.beginText(50, height - 50)
            text_object.setFont("Helvetica", 12)

            # Dividir texto en líneas que quepan en página
            lines = []
            words = page_text.split()
            current_line = ""

            for word in words:
                test_line = current_line + word + " "
                if len(test_line) * 7 < width - 100:  # Estimación rough
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word + " "
            lines.append(current_line)

            # Escribir líneas
            for line in lines[:60]:  # Máximo 60 líneas por página
                text_object.textLine(line)

            c.drawText(text_object)
            c.showPage()

        c.save()

        # Actualizar contador de palabras del usuario
        cursor.execute(
            "UPDATE users SET words_used_this_month = words_used_this_month + %s WHERE id = %s",
            (word_count, user_id)
        )

        # Retornar archivo para descarga
        return FileResponse(
            path=output_path,
            media_type='application/pdf',
            filename=output_filename,
            headers={
                'Content-Disposition': f'attachment; filename={output_filename}'
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PDF translation failed: {str(e)}"
        )


async def translate_word(file, source_lang, target_lang, user_id, cursor):
    """
    Traduce archivos Word (.docx)

    Proceso:
    1. Abrir documento con python-docx
    2. Extraer párrafos
    3. Traducir cada párrafo
    4. Crear nuevo documento con traducciones
    5. Preservar formato (bold, italic, etc)
    """
    import tempfile
    import os
    from docx import Document
    from fastapi.responses import FileResponse

    try:
        # Leer documento original
        doc = Document(file.file)

        # Extraer todo el texto
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        total_text = " ".join(paragraphs)
        word_count = len(total_text.split())

        # Verificar límite
        cursor.execute(
            "SELECT word_limit, words_used_this_month FROM users WHERE id = %s",
            (user_id,)
        )
        user = cursor.fetchone()

        if user['words_used_this_month'] + word_count > user['word_limit']:
            raise HTTPException(status_code=402, detail="Word limit exceeded")

        # Traducir
        translation_service = TranslationService()
        translated_paragraphs = []

        for para_text in paragraphs:
            result = await translation_service.translate(
                para_text,
                source_lang,
                target_lang
            )
            translated_paragraphs.append(result['text'])

        # Crear nuevo documento
        new_doc = Document()
        for translated_text in translated_paragraphs:
            new_doc.add_paragraph(translated_text)

        # Guardar
        temp_dir = tempfile.mkdtemp()
        output_filename = f"translated_{file.filename}"
        output_path = os.path.join(temp_dir, output_filename)
        new_doc.save(output_path)

        # Actualizar contador
        cursor.execute(
            "UPDATE users SET words_used_this_month = words_used_this_month + %s WHERE id = %s",
            (word_count, user_id)
        )

        return FileResponse(
            path=output_path,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            filename=output_filename
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Word translation failed: {str(e)}"
        )


async def translate_excel(file, source_lang, target_lang, user_id, cursor):
    """
    Traduce archivos Excel (.xlsx)

    Proceso:
    1. Abrir workbook con openpyxl
    2. Iterar por todas las celdas con texto
    3. Traducir cada celda
    4. Preservar formato (colores, bordes, fórmulas)
    """
    import tempfile
    import os
    import openpyxl
    from fastapi.responses import FileResponse

    try:
        # Leer Excel
        wb = openpyxl.load_workbook(file.file)

        # Extraer todo el texto
        all_text = []
        cell_contents = []  # Guardar (sheet, row, col, text)

        for sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
            for row in sheet.iter_rows():
                for cell in row:
                    if cell.value and isinstance(cell.value, str):
                        all_text.append(cell.value)
                        cell_contents.append((sheet, cell.row, cell.column, cell.value))

        total_text = " ".join(all_text)
        word_count = len(total_text.split())

        # Verificar límite
        cursor.execute(
            "SELECT word_limit, words_used_this_month FROM users WHERE id = %s",
            (user_id,)
        )
        user = cursor.fetchone()

        if user['words_used_this_month'] + word_count > user['word_limit']:
            raise HTTPException(status_code=402, detail="Word limit exceeded")

        # Traducir cada celda
        translation_service = TranslationService()

        for sheet, row, col, original_text in cell_contents:
            result = await translation_service.translate(
                original_text,
                source_lang,
                target_lang
            )
            sheet.cell(row=row, column=col).value = result['text']

        # Guardar nuevo Excel
        temp_dir = tempfile.mkdtemp()
        output_filename = f"translated_{file.filename}"
        output_path = os.path.join(temp_dir, output_filename)
        wb.save(output_path)

        # Actualizar contador
        cursor.execute(
            "UPDATE users SET words_used_this_month = words_used_this_month + %s WHERE id = %s",
            (word_count, user_id)
        )

        return FileResponse(
            path=output_path,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename=output_filename
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Excel translation failed: {str(e)}"
        )


async def translate_powerpoint(file, source_lang, target_lang, user_id, cursor):
    """
    Traduce archivos PowerPoint (.pptx)

    Proceso:
    1. Abrir presentación con python-pptx
    2. Extraer texto de slides
    3. Traducir
    4. Actualizar slides manteniendo diseño
    """
    import tempfile
    import os
    from pptx import Presentation
    from fastapi.responses import FileResponse

    try:
        # Leer PowerPoint
        prs = Presentation(file.file)

        # Extraer texto de todos los slides
        all_text = []
        text_frames = []  # Guardar referencias a text frames

        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text_frame"):
                    for paragraph in shape.text_frame.paragraphs:
                        for run in paragraph.runs:
                            if run.text.strip():
                                all_text.append(run.text)
                                text_frames.append(run)

        total_text = " ".join(all_text)
        word_count = len(total_text.split())

        # Verificar límite
        cursor.execute(
            "SELECT word_limit, words_used_this_month FROM users WHERE id = %s",
            (user_id,)
        )
        user = cursor.fetchone()

        if user['words_used_this_month'] + word_count > user['word_limit']:
            raise HTTPException(status_code=402, detail="Word limit exceeded")

        # Traducir cada texto
        translation_service = TranslationService()

        for i, run in enumerate(text_frames):
            if run.text.strip():
                result = await translation_service.translate(
                    run.text,
                    source_lang,
                    target_lang
                )
                run.text = result['text']

        # Guardar
        temp_dir = tempfile.mkdtemp()
        output_filename = f"translated_{file.filename}"
        output_path = os.path.join(temp_dir, output_filename)
        prs.save(output_path)

        # Actualizar contador
        cursor.execute(
            "UPDATE users SET words_used_this_month = words_used_this_month + %s WHERE id = %s",
            (word_count, user_id)
        )

        return FileResponse(
            path=output_path,
            media_type='application/vnd.openxmlformats-officedocument.presentationml.presentation',
            filename=output_filename
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PowerPoint translation failed: {str(e)}"
        )
```

#### Dependencias necesarias
**Agregar a** `backend/requirements.txt`:
```
PyPDF2==3.0.0
python-docx==1.0.0
openpyxl==3.1.2
python-pptx==0.6.21
reportlab==4.0.4
```

#### Registrar router
**En** `backend/src/main.py`:
```python
from src.api.routes import documents

app.include_router(
    documents.router,
    prefix="/api/documents",
    tags=["documents"]
)
```

#### Frontend - Nueva página
**Crear:** `frontend/public/en/translate-documents.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Translate Documents | TranslateCloud</title>
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        /* Usar mismo sistema de diseño que translate.html */
        :root {
            --color-primary: #111827;
            --color-accent: #0EA5E9;
            --color-white: #FFFFFF;
            --font-sans: 'IBM Plex Sans', sans-serif;
        }

        body {
            font-family: var(--font-sans);
            background: #F9FAFB;
        }

        .dropzone {
            border: 2px dashed #D1D5DB;
            border-radius: 0.5rem;
            padding: 3rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s;
        }

        .dropzone:hover {
            border-color: var(--color-accent);
            background: rgba(14, 165, 233, 0.05);
        }

        .dropzone.active {
            border-color: var(--color-accent);
            background: rgba(14, 165, 233, 0.1);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Translate Documents</h1>
        <p>Upload PDF, Word, Excel, or PowerPoint files</p>

        <!-- Dropzone -->
        <div class="dropzone" id="dropzone">
            <svg>...</svg>
            <h3>Drag & drop your file here</h3>
            <p>or click to browse</p>
            <input type="file" id="file-input" accept=".pdf,.docx,.doc,.xlsx,.xls,.pptx" hidden>
        </div>

        <!-- File info -->
        <div id="file-info" class="hidden">
            <p>File: <span id="file-name"></span></p>
            <p>Size: <span id="file-size"></span></p>
            <p>Type: <span id="file-type"></span></p>
        </div>

        <!-- Language selectors -->
        <div class="language-selector">
            <select id="source-lang">
                <option value="en">English</option>
                <option value="es">Spanish</option>
                <option value="fr">French</option>
                <option value="de">German</option>
            </select>

            <button id="swap-langs">⇄</button>

            <select id="target-lang">
                <option value="es">Spanish</option>
                <option value="en">English</option>
                <option value="fr">French</option>
                <option value="de">German</option>
            </select>
        </div>

        <!-- Translate button -->
        <button id="translate-btn" class="btn-primary" disabled>
            Translate Document
        </button>

        <!-- Progress bar -->
        <div id="progress" class="hidden">
            <div class="progress-bar">
                <div class="progress-fill"></div>
            </div>
            <p class="progress-text">Translating... <span id="progress-percent">0</span>%</p>
        </div>

        <!-- Download button -->
        <div id="download-section" class="hidden">
            <h3>✅ Translation Complete!</h3>
            <button id="download-btn" class="btn-primary">
                Download Translated Document
            </button>
        </div>
    </div>

    <script>
        const API_URL = 'https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod';

        let selectedFile = null;

        // Dropzone handlers
        const dropzone = document.getElementById('dropzone');
        const fileInput = document.getElementById('file-input');

        dropzone.addEventListener('click', () => fileInput.click());

        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('active');
        });

        dropzone.addEventListener('dragleave', () => {
            dropzone.classList.remove('active');
        });

        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('active');
            handleFile(e.dataTransfer.files[0]);
        });

        fileInput.addEventListener('change', (e) => {
            handleFile(e.target.files[0]);
        });

        function handleFile(file) {
            if (!file) return;

            // Validar tipo
            const validTypes = ['pdf', 'docx', 'doc', 'xlsx', 'xls', 'pptx'];
            const fileType = file.name.split('.').pop().toLowerCase();

            if (!validTypes.includes(fileType)) {
                alert('Unsupported file type. Please upload PDF, Word, Excel, or PowerPoint files.');
                return;
            }

            selectedFile = file;

            // Mostrar info
            document.getElementById('file-name').textContent = file.name;
            document.getElementById('file-size').textContent = formatFileSize(file.size);
            document.getElementById('file-type').textContent = fileType.toUpperCase();
            document.getElementById('file-info').classList.remove('hidden');

            // Habilitar botón
            document.getElementById('translate-btn').disabled = false;
        }

        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
        }

        // Translate button
        document.getElementById('translate-btn').addEventListener('click', async () => {
            if (!selectedFile) return;

            const sourceLang = document.getElementById('source-lang').value;
            const targetLang = document.getElementById('target-lang').value;

            // Mostrar progress
            document.getElementById('progress').classList.remove('hidden');
            document.getElementById('translate-btn').disabled = true;

            // Simular progress (mejorar con real progress tracking)
            simulateProgress();

            // Crear FormData
            const formData = new FormData();
            formData.append('file', selectedFile);

            try {
                const token = localStorage.getItem('auth_token');

                const response = await fetch(
                    `${API_URL}/api/documents/translate/document?source_lang=${sourceLang}&target_lang=${targetLang}`,
                    {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${token}`
                        },
                        body: formData
                    }
                );

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'Translation failed');
                }

                // Descargar archivo
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `translated_${selectedFile.name}`;
                a.click();

                // Mostrar éxito
                document.getElementById('progress').classList.add('hidden');
                document.getElementById('download-section').classList.remove('hidden');

            } catch (error) {
                console.error('Translation error:', error);
                alert(`Error: ${error.message}`);
                document.getElementById('progress').classList.add('hidden');
                document.getElementById('translate-btn').disabled = false;
            }
        });

        function simulateProgress() {
            let progress = 0;
            const interval = setInterval(() => {
                progress += 5;
                if (progress >= 95) {
                    clearInterval(interval);
                }
                document.getElementById('progress-percent').textContent = progress;
                document.querySelector('.progress-fill').style.width = progress + '%';
            }, 200);
        }
    </script>
</body>
</html>
```

#### Testing
```bash
# 1. Instalar dependencias
cd backend
pip install -r requirements.txt

# 2. Desplegar a Lambda
cd ..
bash scripts/deploy-backend.sh

# 3. Probar endpoint
curl -X POST \
  https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod/api/documents/translate/document \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@test.pdf" \
  -F "source_lang=en" \
  -F "target_lang=es" \
  --output translated_test.pdf
```

---

## 📝 SERVICIO 3: TRADUCCIÓN DE TEXTO/PALABRAS (FALTA IMPLEMENTAR)

### ⚠️ CRÍTICO: Este servicio NO EXISTE pero es BÁSICO

### Qué debe hacer
Traducir texto libre/palabras individuales:
- Input: textarea con texto
- Output: texto traducido
- Guardar historial de traducciones
- Copiar resultado con un click

### Flujo de usuario esperado
```
1. Usuario va a /en/translate-text.html (NO EXISTE)
2. Ve dos textareas (origen | destino)
3. Escribe texto en origen
4. Selecciona idiomas
5. Click "Translate"
6. Ve traducción instantánea
7. Click "Copy" para copiar resultado
```

### Implementación requerida

#### Backend - Nuevo archivo
**Ubicación:** `backend/src/api/routes/text.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.core.translation_service import TranslationService
from src.api.dependencies.jwt_auth import get_current_user_id
from src.config.database import get_db

router = APIRouter()

class TranslateTextRequest(BaseModel):
    text: str
    source_language: str
    target_language: str

class TranslateTextResponse(BaseModel):
    original: str
    translated: str
    word_count: int
    provider: str
    detected_language: str

@router.post("/translate/text", response_model=TranslateTextResponse)
async def translate_text(
    request: TranslateTextRequest,
    user_id: str = Depends(get_current_user_id),
    cursor = Depends(get_db)
):
    """
    Traduce texto libre

    Args:
        text: Texto a traducir
        source_language: Idioma origen
        target_language: Idioma destino

    Returns:
        Texto traducido + metadata
    """

    # 1. Contar palabras
    word_count = len(request.text.split())

    # 2. Verificar límite del usuario
    cursor.execute(
        "SELECT word_limit, words_used_this_month, plan FROM users WHERE id = %s",
        (user_id,)
    )
    user = cursor.fetchone()

    if user['words_used_this_month'] + word_count > user['word_limit']:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "word_limit_exceeded",
                "words_needed": word_count,
                "words_available": user['word_limit'] - user['words_used_this_month'],
                "current_plan": user['plan'],
                "upgrade_url": "/en/pricing.html"
            }
        )

    # 3. Traducir
    translation_service = TranslationService()
    result = await translation_service.translate(
        request.text,
        request.source_language,
        request.target_language
    )

    # 4. Actualizar contador de palabras
    cursor.execute(
        "UPDATE users SET words_used_this_month = words_used_this_month + %s WHERE id = %s",
        (word_count, user_id)
    )

    # 5. Guardar en historial de traducciones
    cursor.execute(
        """
        INSERT INTO translations (
            user_id, source_text, translated_text,
            source_lang, target_lang, word_count, engine, status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            user_id,
            request.text,
            result['text'],
            request.source_language,
            request.target_language,
            word_count,
            result['provider'],
            'completed'
        )
    )

    # 6. Retornar resultado
    return TranslateTextResponse(
        original=request.text,
        translated=result['text'],
        word_count=word_count,
        provider=result['provider'],
        detected_language=request.source_language
    )


@router.get("/translate/history")
async def get_translation_history(
    user_id: str = Depends(get_current_user_id),
    cursor = Depends(get_db),
    limit: int = 20
):
    """
    Obtiene historial de traducciones del usuario

    Args:
        limit: Número máximo de resultados

    Returns:
        Lista de traducciones pasadas
    """
    cursor.execute(
        """
        SELECT
            id, source_text, translated_text,
            source_lang, target_lang, word_count,
            engine, created_at
        FROM translations
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (user_id, limit)
    )

    translations = cursor.fetchall()
    return translations
```

#### Registrar router
**En** `backend/src/main.py`:
```python
from src.api.routes import text

app.include_router(
    text.router,
    prefix="/api/text",
    tags=["text"]
)
```

#### Frontend - Nueva página
**Crear:** `frontend/public/en/translate-text.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Translate Text | TranslateCloud</title>
    <style>
        .translate-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
            max-width: 1200px;
            margin: 2rem auto;
        }

        .text-area-container {
            border: 1px solid #E5E7EB;
            border-radius: 0.5rem;
            padding: 1rem;
            background: white;
        }

        textarea {
            width: 100%;
            height: 300px;
            border: none;
            resize: none;
            font-size: 1rem;
            font-family: inherit;
        }

        textarea:focus {
            outline: none;
        }

        .word-count {
            color: #6B7280;
            font-size: 0.875rem;
            margin-top: 0.5rem;
        }

        .copy-btn {
            background: #0EA5E9;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 0.375rem;
            cursor: pointer;
            font-weight: 500;
        }

        .copy-btn:hover {
            background: #0284C7;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Translate Text</h1>

        <!-- Language selector -->
        <div class="language-selector">
            <select id="source-lang">
                <option value="en">English</option>
                <option value="es">Spanish</option>
                <option value="fr">French</option>
                <option value="de">German</option>
                <option value="it">Italian</option>
                <option value="pt">Portuguese</option>
            </select>

            <button id="swap-langs">⇄</button>

            <select id="target-lang">
                <option value="es">Spanish</option>
                <option value="en">English</option>
                <option value="fr">French</option>
                <option value="de">German</option>
            </select>
        </div>

        <!-- Text areas -->
        <div class="translate-container">
            <!-- Source text -->
            <div class="text-area-container">
                <textarea
                    id="source-text"
                    placeholder="Enter text to translate..."
                    autofocus
                ></textarea>
                <div class="word-count">
                    <span id="source-word-count">0</span> words
                </div>
            </div>

            <!-- Translated text -->
            <div class="text-area-container">
                <textarea
                    id="translated-text"
                    placeholder="Translation will appear here..."
                    readonly
                ></textarea>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div class="word-count">
                        <span id="target-word-count">0</span> words
                    </div>
                    <button id="copy-btn" class="copy-btn" style="display: none;">
                        Copy Translation
                    </button>
                </div>
            </div>
        </div>

        <!-- Translate button -->
        <button id="translate-btn" class="btn-primary" style="width: 100%; margin-top: 1rem;">
            Translate
        </button>

        <!-- History -->
        <div id="history" style="margin-top: 3rem;">
            <h2>Recent Translations</h2>
            <div id="history-list"></div>
        </div>
    </div>

    <script>
        const API_URL = 'https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod';

        // Word count update
        document.getElementById('source-text').addEventListener('input', (e) => {
            const words = e.target.value.trim().split(/\s+/).filter(w => w.length > 0);
            document.getElementById('source-word-count').textContent = words.length;
        });

        // Swap languages
        document.getElementById('swap-langs').addEventListener('click', () => {
            const source = document.getElementById('source-lang');
            const target = document.getElementById('target-lang');
            [source.value, target.value] = [target.value, source.value];
        });

        // Translate
        document.getElementById('translate-btn').addEventListener('click', async () => {
            const sourceText = document.getElementById('source-text').value;
            if (!sourceText.trim()) {
                alert('Please enter text to translate');
                return;
            }

            const sourceLang = document.getElementById('source-lang').value;
            const targetLang = document.getElementById('target-lang').value;

            try {
                const token = localStorage.getItem('auth_token');

                const response = await fetch(`${API_URL}/api/text/translate/text`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        text: sourceText,
                        source_language: sourceLang,
                        target_language: targetLang
                    })
                });

                if (!response.ok) {
                    const error = await response.json();
                    if (response.status === 402) {
                        alert(`Word limit exceeded! You need ${error.detail.words_needed} words but only have ${error.detail.words_available} remaining.`);
                        window.location.href = '/en/pricing.html';
                        return;
                    }
                    throw new Error(error.detail || 'Translation failed');
                }

                const data = await response.json();

                // Mostrar traducción
                document.getElementById('translated-text').value = data.translated;
                document.getElementById('target-word-count').textContent = data.word_count;
                document.getElementById('copy-btn').style.display = 'block';

            } catch (error) {
                console.error('Translation error:', error);
                alert(`Error: ${error.message}`);
            }
        });

        // Copy translation
        document.getElementById('copy-btn').addEventListener('click', () => {
            const text = document.getElementById('translated-text').value;
            navigator.clipboard.writeText(text);

            const btn = document.getElementById('copy-btn');
            btn.textContent = '✓ Copied!';
            setTimeout(() => {
                btn.textContent = 'Copy Translation';
            }, 2000);
        });

        // Load history on page load
        loadHistory();

        async function loadHistory() {
            try {
                const token = localStorage.getItem('auth_token');
                const response = await fetch(`${API_URL}/api/text/translate/history`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (response.ok) {
                    const history = await response.json();
                    displayHistory(history);
                }
            } catch (error) {
                console.error('Failed to load history:', error);
            }
        }

        function displayHistory(history) {
            const container = document.getElementById('history-list');
            if (history.length === 0) {
                container.innerHTML = '<p>No translations yet</p>';
                return;
            }

            container.innerHTML = history.map(item => `
                <div class="history-item" style="border: 1px solid #E5E7EB; padding: 1rem; margin-bottom: 1rem; border-radius: 0.5rem;">
                    <div style="display: flex; justify-content: space-between;">
                        <span><strong>${item.source_lang} → ${item.target_lang}</strong></span>
                        <span style="color: #6B7280;">${new Date(item.created_at).toLocaleDateString()}</span>
                    </div>
                    <p style="margin: 0.5rem 0;">${item.source_text}</p>
                    <p style="margin: 0.5rem 0; color: #0EA5E9;">${item.translated_text}</p>
                    <small style="color: #6B7280;">${item.word_count} words • ${item.engine}</small>
                </div>
            `).join('');
        }
    </script>
</body>
</html>
```

#### Agregar a navbar
**En todos los headers:**
```html
<nav>
    <a href="/en/translate.html">Translate Website</a>
    <a href="/en/translate-text.html">Translate Text</a>      <!-- NUEVO -->
    <a href="/en/translate-documents.html">Translate Documents</a>  <!-- NUEVO -->
    <a href="/en/dashboard.html">Dashboard</a>
    <a href="/en/pricing.html">Pricing</a>
</nav>
```

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

### Cuando trabajes en este proyecto, SIEMPRE verifica:

#### Servicios de Traducción
- [ ] ¿Existe `backend/src/api/routes/documents.py`?
- [ ] ¿Existe `backend/src/api/routes/text.py`?
- [ ] ¿Existe `frontend/public/en/translate-documents.html`?
- [ ] ¿Existe `frontend/public/en/translate-text.html`?
- [ ] ¿Los 3 servicios están en el navbar?
- [ ] ¿Los endpoints están registrados en `main.py`?

#### Límites de Palabras (CRÍTICO)
- [ ] ¿Se verifica límite ANTES de traducir?
- [ ] ¿Se incrementa contador DESPUÉS de traducir?
- [ ] ¿Se maneja error 402 en frontend?
- [ ] ¿Existe cron de reset mensual?

#### Testing
- [ ] ¿Se ha probado traducción end-to-end?
- [ ] ¿Se ha probado con archivo real PDF/Word/Excel?
- [ ] ¿Se ha verificado límite de palabras funciona?
- [ ] ¿Se ha probado con usuario Free y Professional?

---

## 🚨 MENSAJES DE RECORDATORIO

### Al iniciar sesión en VS Code:
```
⚠️ RECORDATORIO CRÍTICO:
TranslateCloud necesita 3 servicios de traducción:
1. Sitios web (parcial)
2. Documentos PDF/Word/Excel (FALTA)
3. Texto/palabras (FALTA)

Antes de considerar el proyecto completo, implementa servicios 2 y 3.
```

### Al abrir archivos de rutas:
```
⚠️ RECORDATORIO:
Este archivo (projects.py) solo maneja traducción de sitios web.
Faltan crear:
- documents.py (PDF, Word, Excel)
- text.py (texto libre)
```

### Al trabajar en frontend:
```
⚠️ RECORDATORIO:
translate.html solo maneja sitios web.
Faltan crear:
- translate-documents.html
- translate-text.html
```

---

## 📚 RECURSOS ÚTILES

### Documentación de librerías
- PyPDF2: https://pypdf2.readthedocs.io/
- python-docx: https://python-docx.readthedocs.io/
- openpyxl: https://openpyxl.readthedocs.io/
- python-pptx: https://python-pptx.readthedocs.io/
- reportlab: https://www.reportlab.com/docs/reportlab-userguide.pdf

### Testing de endpoints
```bash
# Test document translation
curl -X POST \
  ${API_URL}/api/documents/translate/document \
  -H "Authorization: Bearer ${TOKEN}" \
  -F "file=@test.pdf" \
  -F "source_lang=en" \
  -F "target_lang=es"

# Test text translation
curl -X POST \
  ${API_URL}/api/text/translate/text \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world",
    "source_language": "en",
    "target_language": "es"
  }'
```

---

## ⏱️ ESTIMACIÓN DE TIEMPO

### Servicio de Documentos
- Backend (documents.py): 8 horas
- Frontend (translate-documents.html): 4 horas
- Testing: 2 horas
- **Total:** 14 horas (2 días)

### Servicio de Texto
- Backend (text.py): 3 horas
- Frontend (translate-text.html): 3 horas
- Historial: 2 horas
- **Total:** 8 horas (1 día)

### TOTAL: 22 horas (3 días laborables)

---

**Este documento debe permanecer visible en VS Code para recordarte constantemente los servicios faltantes.**

**NO consideres el proyecto completo hasta que los 3 servicios estén 100% implementados y probados.**
