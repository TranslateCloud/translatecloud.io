# TranslateCloud - Development Roadmap

## Recent Improvements (Completed)

### Day 5-6: Critical Infrastructure Fixes
- ✅ Fixed DeepL API language code deprecation (EN → EN-US/EN-GB, PT → PT-BR/PT-PT)
- ✅ Added language mapping for 30+ most-used languages
- ✅ Increased Lambda timeout from 30s to 300s (5 minutes)
- ✅ Increased Lambda memory from 512MB to 1GB
- ✅ Fixed binary compatibility (Python 3.11 dependencies)
- ✅ Improved error display in frontend (FastAPI validation errors)
- ✅ Added comprehensive security guidelines

---

## Priority Features - Next Sprint

### 1. Website Translation Options 🌐

**Current State**: Can only translate entire website (all pages discovered by crawler)

**New Feature**: Add translation mode selector
- [ ] **Full Website Translation** (current behavior)
  - Crawls and translates all discovered pages (max 50)
  - Use case: Complete website localization

- [ ] **Single Page Translation** (new)
  - User enters specific URL
  - Only translates that one page
  - Use case: Quick translations, landing pages, specific content
  - Benefits: Faster, cheaper, more focused

**Implementation**:
```javascript
// Frontend: Add radio buttons in crawl form
<div class="translation-mode">
  <label>
    <input type="radio" name="mode" value="full" checked>
    Translate entire website (all pages)
  </label>
  <label>
    <input type="radio" name="mode" value="single">
    Translate single page only
  </label>
</div>
```

**Backend Changes**:
- Update `crawl_website` endpoint to accept `mode` parameter
- Modify `web_extractor.py` to respect single-page mode
- Skip recursive crawling when mode = "single"

**Estimated Time**: 4 hours

---

### 2. Mobile Application Translation 📱

**New Feature**: Upload mobile app files for translation

**Target Formats**:
- Android: `.xml` (strings.xml), `.arb` (Flutter)
- iOS: `.strings`, `.stringsdict`, `.xliff`
- React Native: `.json` translation files
- Flutter: `.arb` files

**User Flow**:
1. Click "Nuevo Proyecto" button
2. Select "Mobile App Translation" tab
3. Upload translation file(s)
4. Select source and target language
5. Download translated files

**Implementation**:

**Frontend**:
```html
<!-- Add to project creation modal -->
<div class="project-type-tabs">
  <button data-type="website">Website</button>
  <button data-type="mobile">Mobile App</button>
  <button data-type="document">Document</button>
  <button data-type="text">Text</button>
</div>

<div class="mobile-upload" style="display:none">
  <input type="file" accept=".xml,.strings,.arb,.json" multiple>
  <p>Supported: strings.xml, .strings, .arb, .json</p>
</div>
```

**Backend**:
- Create new endpoint: `POST /api/projects/translate-mobile`
- Parse uploaded files based on format
- Extract translatable strings
- Preserve keys, translate values only
- Return translated file(s) in same format

**File Parsers Needed**:
- `backend/src/parsers/android_xml.py` - Parse Android strings.xml
- `backend/src/parsers/ios_strings.py` - Parse iOS .strings
- `backend/src/parsers/arb_parser.py` - Parse Flutter .arb
- `backend/src/parsers/json_parser.py` - Parse React Native JSON

**Estimated Time**: 12 hours

---

### 3. Document Translation (DeepL-style) 📄

**New Feature**: Upload documents and get translated versions

**Supported Formats**:
- PDF (extract text, translate, regenerate)
- DOCX (Microsoft Word)
- PPTX (PowerPoint)
- TXT (plain text)
- MD (Markdown)

**User Interface** (Split-screen):
```
┌─────────────────────────────────────────────────┐
│  Document Translation                           │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─────────────────┐   ┌─────────────────┐    │
│  │  Drop files     │   │  Target:        │    │
│  │  here or click  │   │  [EN-US ▼]      │    │
│  │  to upload      │   │                 │    │
│  │                 │   │  [Translate]    │    │
│  │  📄 drag & drop │   │                 │    │
│  └─────────────────┘   └─────────────────┘    │
│                                                 │
│  Uploaded Files:                                │
│  ✓ contract.pdf (1.2MB) - Ready                │
│  ✓ manual.docx (450KB) - Ready                 │
│                                                 │
│  [Start Translation]                            │
└─────────────────────────────────────────────────┘
```

**Implementation**:

**Frontend**: New page `frontend/public/documents.html`
```javascript
// Drag-and-drop zone
const dropZone = document.getElementById('drop-zone');
dropZone.addEventListener('drop', handleFileDrop);
dropZone.addEventListener('dragover', (e) => e.preventDefault());

function handleFileDrop(e) {
  e.preventDefault();
  const files = Array.from(e.dataTransfer.files);
  uploadFiles(files);
}
```

**Backend**: New endpoint `/api/documents/translate`
```python
@router.post("/documents/translate")
async def translate_document(
    file: UploadFile,
    target_language: str,
    user_id: str = Depends(get_current_user_id)
):
    # 1. Detect file type
    file_type = detect_file_type(file.filename)

    # 2. Extract text based on type
    if file_type == 'pdf':
        text = extract_pdf_text(file)
    elif file_type == 'docx':
        text = extract_docx_text(file)
    # ... etc

    # 3. Translate
    translated = await translation_service.translate(
        text, 'auto', target_language
    )

    # 4. Reconstruct document
    output_file = reconstruct_document(
        file, translated, file_type
    )

    # 5. Return file
    return FileResponse(output_file)
```

**Required Libraries**:
- `PyPDF2` or `pdfplumber` for PDF extraction
- `python-docx` for DOCX handling
- `python-pptx` for PowerPoint
- `reportlab` for PDF generation

**Estimated Time**: 16 hours

---

### 4. Text Translation (Interactive Editor) ✍️

**New Feature**: Real-time text translation with split-screen editor

**User Interface**:
```
┌─────────────────────────────────────────────────────────┐
│  Text Translation                                        │
├─────────────────────────────────────────────────────────┤
│  Source: [Auto-detect ▼]  →  Target: [Spanish ▼]       │
├──────────────────────────────┬──────────────────────────┤
│ Type or paste text here...   │  Translation appears... │
│                              │                          │
│ Hello, how are you?          │  Hola, ¿cómo estás?     │
│                              │                          │
│ This is a test of the        │  Esta es una prueba del │
│ translation system.          │  sistema de traducción. │
│                              │                          │
│                              │                          │
│ [📎 Drop document here]      │  [💾 Copy]  [📥 Download]│
│                              │                          │
│ 3 / 5000 characters          │  Translation by DeepL   │
└──────────────────────────────┴──────────────────────────┘
```

**Features**:
- Real-time translation (debounced, 500ms delay)
- Character counter (show free tier limits)
- Language auto-detection
- Copy translated text button
- Download as .txt or .docx
- Drag-and-drop document to extract text
- Syntax highlighting for code blocks (optional)

**Implementation**:

**Frontend**: New page `frontend/public/text-translate.html`
```javascript
// Real-time translation with debouncing
let translationTimeout;
const sourceTextarea = document.getElementById('source-text');
const targetTextarea = document.getElementById('target-text');

sourceTextarea.addEventListener('input', () => {
  clearTimeout(translationTimeout);
  translationTimeout = setTimeout(async () => {
    const text = sourceTextarea.value;
    if (text.length > 0) {
      const result = await translateText(text);
      targetTextarea.value = result.text;
    }
  }, 500); // Wait 500ms after user stops typing
});

async function translateText(text) {
  const response = await fetch('/api/translate/text', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    },
    body: JSON.stringify({
      text: text,
      source_language: document.getElementById('source-lang').value,
      target_language: document.getElementById('target-lang').value
    })
  });
  return await response.json();
}

// Copy to clipboard
document.getElementById('copy-btn').addEventListener('click', () => {
  navigator.clipboard.writeText(targetTextarea.value);
  showToast('Copied to clipboard!');
});

// Download as file
document.getElementById('download-btn').addEventListener('click', () => {
  const blob = new Blob([targetTextarea.value], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'translation.txt';
  a.click();
});
```

**Backend**: New endpoint `/api/translate/text`
```python
class TextTranslateRequest(BaseModel):
    text: str
    source_language: str
    target_language: str

@router.post("/translate/text")
async def translate_text(
    request: TextTranslateRequest,
    user_id: str = Depends(get_current_user_id),
    cursor: RealDictCursor = Depends(get_db)
):
    """
    Real-time text translation
    """
    # Check user's quota
    cursor.execute(
        "SELECT words_used_this_month, word_limit FROM users WHERE id = %s",
        (user_id,)
    )
    user = cursor.fetchone()

    word_count = len(request.text.split())

    if user['words_used_this_month'] + word_count > user['word_limit']:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Monthly word limit exceeded"
        )

    # Translate
    translation_service = TranslationService(
        deepl_api_key=settings.DEEPL_API_KEY
    )

    result = await translation_service.translate(
        request.text,
        request.source_language,
        request.target_language
    )

    # Update usage
    cursor.execute(
        "UPDATE users SET words_used_this_month = words_used_this_month + %s WHERE id = %s",
        (word_count, user_id)
    )

    return {
        'text': result['text'],
        'provider': result['provider'],
        'detected_language': result.get('detected_language'),
        'word_count': word_count,
        'remaining_words': user['word_limit'] - user['words_used_this_month'] - word_count
    }
```

**Estimated Time**: 10 hours

---

## Navigation Updates

Add new navigation menu items:

```html
<!-- Update frontend/public/index.html and all pages -->
<nav class="main-nav">
  <a href="/">Dashboard</a>
  <a href="/projects.html">Website Translation</a>
  <a href="/text-translate.html">Text Translation</a>
  <a href="/documents.html">Documents</a>
  <a href="/mobile.html">Mobile Apps</a>
  <a href="/settings.html">Settings</a>
</nav>
```

---

## Database Schema Updates

### New Table: `mobile_projects`
```sql
CREATE TABLE mobile_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    name VARCHAR(255),
    platform VARCHAR(50), -- 'android', 'ios', 'flutter', 'react-native'
    file_format VARCHAR(50), -- 'xml', 'strings', 'arb', 'json'
    source_lang VARCHAR(10),
    target_lang VARCHAR(10),
    original_file_url TEXT,
    translated_file_url TEXT,
    word_count INTEGER,
    status VARCHAR(50), -- 'pending', 'processing', 'completed', 'failed'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### New Table: `document_projects`
```sql
CREATE TABLE document_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    name VARCHAR(255),
    file_format VARCHAR(50), -- 'pdf', 'docx', 'pptx', 'txt', 'md'
    source_lang VARCHAR(10),
    target_lang VARCHAR(10),
    original_file_url TEXT,
    translated_file_url TEXT,
    file_size_bytes INTEGER,
    word_count INTEGER,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### New Table: `text_translations`
```sql
CREATE TABLE text_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    source_text TEXT,
    translated_text TEXT,
    source_lang VARCHAR(10),
    target_lang VARCHAR(10),
    word_count INTEGER,
    provider VARCHAR(50), -- 'deepl', 'marian', 'claude'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index for user's recent translations
CREATE INDEX idx_text_translations_user_created
ON text_translations(user_id, created_at DESC);
```

---

## Architecture Improvements for Large Websites

### Current Issue
- Large websites (50+ pages, 150K+ words) exceed Lambda timeout
- Synchronous processing hits API Gateway 30-second limit
- No progress feedback for user

### Solution: Asynchronous Translation Queue

**Architecture**:
```
User Request
    ↓
API Gateway → Lambda (Quick Response)
    ↓
SQS Queue (Translation Jobs)
    ↓
Lambda Consumer (Process in background)
    ↓
DynamoDB (Progress tracking)
    ↓
WebSocket API (Real-time updates to frontend)
```

**Implementation Plan**:

1. **Create SQS Queue**:
```bash
aws sqs create-queue --queue-name translatecloud-jobs --region eu-west-1
```

2. **Update `/crawl` endpoint**:
```python
@router.post("/crawl")
async def crawl_website(request: CrawlRequest, ...):
    # 1. Quick crawl (just count pages)
    pages = await quick_crawl(request.url, max_pages=50)

    # 2. Create project
    project_id = create_project(...)

    # 3. Send to SQS queue
    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps({
            'project_id': project_id,
            'pages': pages,
            'source_lang': request.source_language,
            'target_lang': request.target_language
        })
    )

    # 4. Return immediately
    return {
        'project_id': project_id,
        'status': 'queued',
        'pages_count': len(pages)
    }
```

3. **Create Lambda consumer** (`backend/src/workers/translation_worker.py`):
```python
def lambda_handler(event, context):
    for record in event['Records']:
        message = json.loads(record['body'])

        # Process translation
        translate_project(message['project_id'], message['pages'])

        # Update progress in DynamoDB
        update_progress(message['project_id'], ...)
```

4. **Frontend polling**:
```javascript
// Poll for project status
async function checkProjectStatus(projectId) {
    const response = await fetch(`/api/projects/${projectId}/status`);
    const data = await response.json();

    if (data.status === 'completed') {
        window.location.href = `/export.html?project=${projectId}`;
    } else {
        // Update progress bar
        updateProgressBar(data.progress);

        // Poll again in 2 seconds
        setTimeout(() => checkProjectStatus(projectId), 2000);
    }
}
```

**Estimated Time**: 20 hours

---

## Deployment Checklist

### Phase 1: Translation Modes (Week 1)
- [ ] Implement single-page translation option
- [ ] Update frontend UI with radio buttons
- [ ] Test with various website sizes
- [ ] Deploy to production

### Phase 2: Mobile App Translation (Week 2)
- [ ] Create file parsers (Android, iOS, Flutter, React Native)
- [ ] Build upload interface
- [ ] Implement `/translate-mobile` endpoint
- [ ] Add mobile_projects database table
- [ ] Test with real app translation files
- [ ] Deploy to production

### Phase 3: Document Translation (Week 3)
- [ ] Install document processing libraries
- [ ] Create document extractors (PDF, DOCX, PPTX)
- [ ] Build split-screen upload interface
- [ ] Implement `/documents/translate` endpoint
- [ ] Add document_projects database table
- [ ] Test with various document formats
- [ ] Deploy to production

### Phase 4: Text Translation (Week 4)
- [ ] Build split-screen text editor
- [ ] Implement real-time translation with debouncing
- [ ] Add copy and download features
- [ ] Implement `/translate/text` endpoint
- [ ] Add text_translations database table
- [ ] Test character limits and quotas
- [ ] Deploy to production

### Phase 5: Async Architecture (Week 5-6)
- [ ] Create SQS queue
- [ ] Build Lambda consumer worker
- [ ] Implement DynamoDB progress tracking
- [ ] Add frontend polling/WebSocket
- [ ] Migrate large website translations to async
- [ ] Load test with 100+ page websites
- [ ] Deploy to production

---

## Success Metrics

### Performance Targets
- Single page translation: < 5 seconds
- Small website (1-10 pages): < 30 seconds
- Medium website (11-50 pages): < 5 minutes (async)
- Large website (50+ pages): < 15 minutes (async)
- Document translation: < 10 seconds for 10-page PDF
- Text translation: < 2 seconds (real-time feel)

### Quality Targets
- DeepL API success rate: > 99%
- Translation accuracy (user satisfaction): > 95%
- Zero deprecated language code errors
- Support for 30+ languages

### Scalability Targets
- Handle 100 concurrent users
- Process 1M words/day
- 99.9% uptime

---

## Technical Debt & Future Improvements

### Short-term (Next 3 months)
- [ ] Add MarianMT as offline fallback when DeepL quota exhausted
- [ ] Implement caching for repeated translations
- [ ] Add translation memory (reuse previous translations)
- [ ] Optimize Lambda cold starts (< 1 second)

### Medium-term (6 months)
- [ ] Add glossary support (custom terminology)
- [ ] Implement translation quality scoring
- [ ] Add collaborative translation (multiple users per project)
- [ ] Build translation review interface (edit translations before export)

### Long-term (12 months)
- [ ] Support for 100+ languages
- [ ] Custom AI model fine-tuning per customer
- [ ] Translation API for developers
- [ ] WordPress/Shopify/Wix plugins
- [ ] Browser extension for instant page translation

---

**Last Updated**: October 20, 2025
**Owner**: Virginia Posadas
**Status**: Active Development
