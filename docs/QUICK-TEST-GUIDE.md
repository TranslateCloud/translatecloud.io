# Quick Translation Test Guide

**Purpose:** Test the translation system with a small website to verify all components work.

**Test Site:** https://example.com (1 page, ~200 words, completes in < 10 seconds)

---

## Prerequisites

- [ ] Logged in to https://www.translatecloud.io
- [ ] JWT token in localStorage (check browser DevTools → Application → Local Storage)
- [ ] Internet connection stable

---

## Test Steps

### 1. Navigate to Translation Page

```
URL: https://www.translatecloud.io/translate.html
```

### 2. Enter Website URL

```
Website URL: https://example.com
Source Language: en (or auto)
Target Language: es
```

### 3. Click "Analyze Website"

**Expected Behavior:**
- Request sent to `/api/projects/crawl`
- Completes in ~3-5 seconds
- Returns:
  ```json
  {
    "project_id": "uuid-here",
    "pages_count": 1,
    "word_count": ~200,
    "pages": [...],
    "estimated_cost": ~11
  }
  ```

**What to Check:**
- ✅ No timeout errors
- ✅ Page count displayed
- ✅ Word count displayed
- ✅ Translate button enabled

### 4. Click "Start Translation"

**Expected Behavior:**
- Request sent to `/api/projects/translate`
- Completes in ~5-10 seconds
- Progress bar updates
- Returns:
  ```json
  {
    "project_id": "uuid-here",
    "status": "completed",
    "pages_translated": 1,
    "total_words": ~200,
    "pages": [
      {
        "url": "https://example.com",
        "translated_elements": [...],
        "word_count": ~200
      }
    ]
  }
  ```

**What to Check:**
- ✅ No timeout errors (should complete before 30s)
- ✅ Success message displayed
- ✅ Download button enabled
- ✅ Translation provider shown (should be "DeepL")

### 5. Download Translated Site

**Expected Behavior:**
- Request sent to `/api/projects/export/{project_id}`
- ZIP file downloads immediately
- Filename: `translated-site-{project_id}.zip`

**What to Check:**
- ✅ ZIP file downloads
- ✅ ZIP contains `index.html`
- ✅ HTML is valid (can open in browser)
- ✅ Content is in Spanish
- ✅ HTML structure preserved

### 6. Verify Translation Quality

**Open the translated `index.html` in browser:**

**Original (English):**
```html
<h1>Example Domain</h1>
<p>This domain is for use in illustrative examples in documents...</p>
```

**Translated (Spanish):**
```html
<h1>Dominio de Ejemplo</h1>
<p>Este dominio es para uso en ejemplos ilustrativos en documentos...</p>
```

**What to Check:**
- ✅ Title translated correctly
- ✅ Paragraphs translated correctly
- ✅ Links still work
- ✅ No broken HTML
- ✅ Professional translation quality (DeepL should be excellent)

---

## Browser Console Monitoring

**Open DevTools (F12) → Console tab**

### Expected Logs (Success Path)

```
[API] POST /api/projects/crawl
[API] Request successful (200)
Crawl successful: 1 pages, 200 words

[API] POST /api/projects/translate
[API] Request successful (200)
Translation completed: 1 pages

[API] POST /api/projects/export/...
[API] Request successful (200)
Download started
```

### Error Logs to Watch For

**❌ Bad:**
```
504 Gateway Timeout
Request timeout - please try again
Failed to load resource: the server responded with a status of 504
```
If you see these with example.com → something is wrong with the backend.

**✅ Good (for large sites):**
```
504 Gateway Timeout
```
This is expected for large sites (50+ pages) - we'll fix with async architecture.

---

## Network Tab Monitoring

**Open DevTools → Network tab**

### Expected Requests

1. **POST /api/projects/crawl**
   - Status: 200 OK
   - Time: ~3-5 seconds
   - Size: ~2-5 KB

2. **POST /api/projects/translate**
   - Status: 200 OK
   - Time: ~5-10 seconds
   - Size: ~10-20 KB

3. **POST /api/projects/export/...**
   - Status: 200 OK
   - Time: ~1-2 seconds
   - Size: ~5-10 KB (ZIP file)

### Troubleshooting

**If crawl fails:**
- Check API Gateway URL in api.js
- Verify JWT token is valid
- Check CORS headers

**If translate fails:**
- Check DeepL API key in Lambda environment
- Check Lambda CloudWatch logs
- Verify language mapping

**If export fails:**
- Check HTML reconstructor logic
- Verify ZIP file generation
- Check temp directory permissions

---

## Success Criteria

### Minimum Viable Test (MVP)

- [x] Crawl completes without timeout
- [x] Translation completes without timeout
- [x] Export generates valid ZIP file
- [x] HTML renders in browser
- [x] Translation is in target language

### Quality Checks

- [ ] Translation is accurate (not gibberish)
- [ ] Translation is professional quality
- [ ] HTML structure is preserved
- [ ] Links are not broken
- [ ] No extra spaces or formatting issues
- [ ] Provider shows "DeepL" (not "none" or "error")

---

## Next Steps After Successful Test

### If Test Passes ✅

1. **Document results** - Take screenshots
2. **Test with 2-3 more small sites** - Verify consistency
3. **Proceed to async architecture** - For large website support

### If Test Fails ❌

**Analyze error logs:**
1. Check browser console
2. Check Network tab
3. Check CloudWatch logs (Lambda)
4. Check specific error message

**Common Issues:**

| Error | Likely Cause | Fix |
|-------|--------------|-----|
| 504 Timeout | Site too large OR Lambda crashed | Check CloudWatch logs |
| 422 Validation | Missing fields in request | Check request body format |
| 401 Unauthorized | Invalid JWT token | Re-login to get new token |
| 500 Server Error | Lambda error | Check CloudWatch logs |
| CORS Error | Missing headers | Check API Gateway CORS |

---

## Alternative Test Sites (If example.com doesn't work)

1. **https://www.w3.org/** - W3C homepage (simple, 1 page)
2. **http://motherfuckingwebsite.com/** - Minimal HTML (fast test)
3. **https://www.google.com/** - Google homepage (but may have dynamic content)
4. **Any personal blog** - Your own simple website

**Criteria for good test site:**
- 1-3 pages maximum
- Static content (no JavaScript-rendered content)
- Simple HTML structure
- Public access (no login required)

---

## Test Report Template

After testing, fill this out:

```
Date: ___________
Tester: ___________
Test Site: https://example.com

RESULTS:
┌─────────────────────────────────────────┐
│ Crawl:      [ ] Pass  [ ] Fail          │
│ Translate:  [ ] Pass  [ ] Fail          │
│ Export:     [ ] Pass  [ ] Fail          │
│ Quality:    [ ] Pass  [ ] Fail          │
└─────────────────────────────────────────┘

METRICS:
- Pages found: _____
- Word count: _____
- Crawl time: _____ seconds
- Translation time: _____ seconds
- Provider used: _____

TRANSLATION QUALITY (1-5 stars):
- Accuracy: ☆☆☆☆☆
- Fluency: ☆☆☆☆☆
- Formatting: ☆☆☆☆☆

NOTES:
_________________________________
_________________________________
_________________________________

NEXT STEPS:
[ ] Test passed - proceed to async architecture
[ ] Test failed - debug and retry
[ ] Need to investigate specific issue: ___________
```

---

**Created:** October 20, 2025
**Last Updated:** October 20, 2025
**Maintainer:** Virginia Posadas
