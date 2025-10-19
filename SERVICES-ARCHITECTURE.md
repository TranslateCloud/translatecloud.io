# TranslateCloud - Services Architecture & Implementation Plan
**Date:** October 19, 2025 - 23:30 GMT
**Purpose:** Define EXACTLY what services we offer and how they work

---

## 🎯 CORE VALUE PROPOSITION

**TranslateCloud provides 3 main services:**
1. **Website Translation** - Upload URL, get translated HTML files
2. **API Translation** - Direct API calls for custom integrations
3. **Project Management** - Store, manage, and download translation projects

---

## 📦 SERVICE 1: WEBSITE TRANSLATION (MVP)

### What It Does
User provides a website URL → We crawl, translate all pages → User downloads ZIP with translated site

### User Flow (Frontend)
```
User logged in → /en/translate.html
  ↓
1. Enter URL (e.g., "https://example.com")
2. Select source language (e.g., "English")
3. Select target language (e.g., "Spanish")
4. Click "Analyze Website"
  ↓
BACKEND: Crawls website, extracts pages
  ↓
5. Show preview:
   - Number of pages found
   - Total words count
   - Cost estimate (€0.055 * words)
   - List of pages (URL + word count per page)
6. User clicks "Confirm & Translate"
  ↓
BACKEND: Translates all pages using DeepL
  ↓
7. Show progress bar (fake for now, later WebSocket)
8. When complete, show "Download ZIP" button
9. User downloads translated website
```

### Backend Flow (Lambda)
```python
# Step 1: Crawl endpoint
POST /api/projects/crawl
Request:
{
  "url": "https://example.com",
  "source_language": "en",
  "target_language": "es"
}

Response:
{
  "project_id": "uuid-here",
  "pages_count": 5,
  "word_count": 2500,
  "estimated_cost": 137.50,
  "pages": [
    {
      "url": "https://example.com/",
      "url_path": "index.html",
      "word_count": 500
    },
    {
      "url": "https://example.com/about",
      "url_path": "about.html",
      "word_count": 300
    },
    ...
  ]
}

# Step 2: Translate endpoint
POST /api/projects/translate
Request:
{
  "project_id": "uuid-here",
  "pages": [...array from crawl...],
  "source_language": "en",
  "target_language": "es"
}

Response:
{
  "project_id": "uuid-here",
  "status": "completed",
  "pages_translated": 5,
  "total_words": 2500,
  "pages": [
    {
      "url": "https://example.com/",
      "url_path": "index.html",
      "original_html": "<html>...</html>",
      "translated_elements": [
        {
          "tag": "h1",
          "text": "Welcome",
          "translated_text": "Bienvenido"
        },
        ...
      ],
      "word_count": 500
    },
    ...
  ]
}

# Step 3: Export endpoint
POST /api/projects/export/{project_id}
Request:
{
  "pages": [...array from translate...],
  "target_language": "es"
}

Response: ZIP file download
```

### Database Schema (Needs Verification)
```sql
-- projects table
CREATE TABLE projects (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  name VARCHAR(255),
  url TEXT,
  source_lang VARCHAR(10),
  target_lang VARCHAR(10),
  total_words INTEGER,
  translated_words INTEGER,
  status VARCHAR(50), -- 'pending', 'analyzing', 'analyzed', 'translating', 'completed', 'failed'
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- translations table (for individual text translations via API)
CREATE TABLE translations (
  id UUID PRIMARY KEY,
  project_id UUID REFERENCES projects(id),
  source_lang VARCHAR(10),
  target_lang VARCHAR(10),
  source_text TEXT,
  translated_text TEXT,
  word_count INTEGER,
  engine VARCHAR(50), -- 'deepl', 'marianmt', 'fallback'
  status VARCHAR(50), -- 'pending', 'completed', 'failed'
  translated_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Implementation Status
- ✅ **Frontend UI:** Exists (translate.html) - 100%
- ⚠️ **Backend Crawl:** Exists but UNTESTED - 70%
- ⚠️ **Backend Translate:** Exists but UNTESTED - 70%
- ⚠️ **Backend Export:** Exists but UNTESTED - 70%
- ❌ **Database Schema:** May have mismatches - 50%
- ❌ **Error Handling:** Minimal - 20%
- ❌ **Progress Tracking:** Not implemented - 0%

### What Needs to be Built (Day 6-7)
1. **Test end-to-end flow** with real website
2. **Fix database schema** if mismatches found
3. **Add proper error handling** (what if website is unreachable?)
4. **Add progress tracking** (WebSocket or polling)
5. **Add word limit enforcement** (check user plan before translating)
6. **Store translated files in S3** (not just in memory)

---

## 📡 SERVICE 2: DIRECT API ACCESS (Future - NOT MVP)

### What It Does
Developers can call our API directly to translate text/HTML without using the web interface

### Example Use Case
```javascript
// A developer wants to translate their blog posts
const response = await fetch('https://api.translatecloud.io/v1/translate', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer API_KEY_HERE',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    text: 'Hello, world!',
    source: 'en',
    target: 'es',
    preserve_html: true
  })
});

const data = await response.json();
console.log(data.translated_text); // "¡Hola, mundo!"
```

### Implementation Requirements
1. **API Key System** ❌ NOT BUILT
   - Generate API keys in dashboard
   - Store in `api_keys` table
   - Authenticate requests via `Bearer {api_key}`
   - Rate limiting per key

2. **Endpoint:** `POST /api/v1/translate` ❌ NOT BUILT
   ```python
   @router.post("/v1/translate")
   async def translate_text(
       request: TranslateRequest,
       api_key: str = Depends(verify_api_key)
   ):
       # 1. Verify API key
       # 2. Check user's word limit
       # 3. Translate text
       # 4. Increment user's word count
       # 5. Return translation
       pass
   ```

3. **Batch Translation:** `POST /api/v1/translate/batch` ❌ NOT BUILT
   ```python
   {
     "texts": ["Hello", "Goodbye", "Thank you"],
     "target": "es"
   }
   → Returns array of translations
   ```

### Implementation Status
- ❌ **NOT STARTED** - 0%
- **Reason:** Focused on MVP (web interface first)
- **Timeline:** After MVP launch (Week 2-3)

---

## 🔌 SERVICE 3: SDK/PLUGINS (Future - NOT MVP)

### What It Does
Pre-built integrations for popular platforms

### 3.1 JavaScript/npm SDK
```javascript
import TranslateCloud from '@translatecloud/sdk';

const client = new TranslateCloud({
  apiKey: 'your-api-key'
});

const result = await client.translate({
  text: 'Your content',
  target: 'es'
});
```

**Status:** ❌ NOT BUILT
**Timeline:** Post-launch (Month 2)

### 3.2 WordPress Plugin
**Features:**
- Auto-detect new posts
- Translate on publish
- SEO-friendly URLs (/es/post-slug)
- hreflang tags

**Status:** ❌ NOT BUILT
**Timeline:** Post-launch (Month 3)

### 3.3 React Component
```jsx
import { TranslateProvider, useTranslate } from '@translatecloud/react';

function App() {
  return (
    <TranslateProvider apiKey="...">
      <MyComponent />
    </TranslateProvider>
  );
}
```

**Status:** ❌ NOT BUILT
**Timeline:** Post-launch (Month 4)

---

## 🛠️ TECHNICAL ARCHITECTURE

### Current Stack (MVP)
```
Frontend (Static):
  ├── Vanilla JS + HTML + CSS
  ├── Hosted: S3 + CloudFront
  └── URL: https://www.translatecloud.io

Backend (Serverless):
  ├── Python 3.11 + FastAPI
  ├── Hosted: AWS Lambda
  ├── API: https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod
  └── Timeout: 30 seconds (may need increase for large sites)

Database:
  ├── PostgreSQL 15.4 on RDS
  ├── Tables: users, projects, translations, payments
  └── Endpoint: translatecloud-db-prod.c3asoiwiy0l1.eu-west-1.rds.amazonaws.com

Storage:
  ├── S3 buckets (6 total)
  │   ├── translatecloud-frontend-prod (website)
  │   ├── translatecloud-uploads-prod (original files)
  │   ├── translatecloud-translations-prod (translated files)
  │   ├── translatecloud-web-projects (complete projects)
  │   ├── translatecloud-backups-prod (DB backups)
  │   └── translatecloud-logs-prod (access logs)

Translation Engines:
  ├── Primary: DeepL API (paid, high quality)
  ├── Fallback: MarianMT (free, lower quality)
  └── Cost: €20 per 1M characters (DeepL)
```

### Scaling Considerations
| Component | Current | Max Capacity | Bottleneck | Solution |
|-----------|---------|--------------|------------|----------|
| Lambda | 512MB, 30s | 10GB, 15min | Large websites timeout | Split into multiple invocations |
| RDS | db.t3.micro | Limited | High concurrent users | Upgrade to larger instance |
| DeepL API | Free tier | 500k chars/month | Translation volume | Paid tier or alternative API |
| S3 | Unlimited | Unlimited | None | N/A |

---

## 💰 PRICING & LIMITS

### Free Plan (5,000 words/month)
- **What user gets:**
  - Translate small websites (1-2 pages)
  - Test the service
  - No credit card required

- **Backend enforcement:**
  ```python
  # Before translating
  if user.words_used_this_month + new_words > user.word_limit:
      raise HTTPException(
          status_code=402,
          detail=f"Limit exceeded. Used: {user.words_used_this_month}, Limit: {user.word_limit}"
      )
  ```

- **Status:** ⚠️ Enforcement NOT implemented

### Professional Plan (€699/month - 50,000 words)
- **What user gets:**
  - Translate medium websites (10-15 pages)
  - Priority support
  - API access (future)

- **Stripe Product ID:** `price_professional_monthly`

### Business Plan (€1,799/month - 150,000 words)
- **What user gets:**
  - Translate large websites (30-50 pages)
  - Dedicated support
  - API access + SDK (future)

### Enterprise Plan (€4,999/month - 500,000 words)
- **What user gets:**
  - Unlimited pages
  - Custom integrations
  - SLA guarantees
  - Dedicated account manager

### Pay-as-you-go (€0.055/word)
- **When it applies:** User exceeds monthly limit
- **How it works:**
  1. User reaches word limit
  2. System asks: "Pay €X to continue?"
  3. If yes → Stripe checkout → Continue translating
  4. If no → Show limit exceeded error

- **Status:** ❌ NOT implemented

---

## 🔄 SERVICE WORKFLOWS

### Workflow 1: New User → First Translation

```
1. User visits https://www.translatecloud.io
2. User clicks "Sign Up" → /en/signup.html
3. User enters email + password
4. Backend creates account:
   - Plan: "free"
   - Words limit: 5000
   - Words used: 0
5. User redirected to /en/dashboard.html
6. User clicks "Translate Website" → /en/translate.html
7. User enters URL + languages
8. Backend crawls website (checks word count)
9. IF word_count > user's remaining limit:
   → Show "Upgrade to Professional" button
   ELSE:
   → Show "Confirm & Translate" button
10. User clicks confirm
11. Backend translates pages
12. User downloads ZIP
13. Backend increments user.words_used_this_month += word_count
```

### Workflow 2: Paid User → Subscription

```
1. User on Free plan → Dashboard shows usage
2. Usage bar: "4,800 / 5,000 words (96%)"
3. User clicks "Upgrade" → /en/pricing.html
4. User selects Professional plan
5. Redirected to /en/checkout.html?plan=professional
6. Stripe checkout loads
7. User enters card details
8. Stripe processes payment
9. Webhook received: /api/payments/webhook
10. Backend updates:
    - user.plan = "professional"
    - user.subscription_status = "active"
    - user.word_limit = 50000
    - user.words_used_this_month = 0 (reset)
11. User redirected to /en/checkout-success.html
12. User can now translate larger websites
```

### Workflow 3: Monthly Reset

```
CRON job (AWS EventBridge):
  Every 1st of month at 00:00 UTC:
    UPDATE users SET words_used_this_month = 0
```

**Status:** ❌ NOT implemented
**Priority:** HIGH (needed before accepting payments)

---

## 🚀 MVP CHECKLIST (Launch Readiness)

### Must-Have (Week 1)
- [x] User signup/login
- [x] Stripe payments
- [ ] **Test translation end-to-end** ← CRITICAL
- [ ] Word limit enforcement
- [ ] Monthly reset cron job
- [ ] Email system (password reset)
- [ ] Error handling in translation flow

### Should-Have (Week 2)
- [ ] API key generation (dashboard)
- [ ] Direct API endpoint (`/api/v1/translate`)
- [ ] Progress tracking (WebSocket or polling)
- [ ] Store translated files in S3
- [ ] Admin panel (view all users, projects)

### Nice-to-Have (Week 3-4)
- [ ] JavaScript SDK
- [ ] WordPress plugin
- [ ] React integration
- [ ] Batch translation endpoint
- [ ] Translation memory (cache common phrases)
- [ ] Language detection (auto-detect source)

---

## 📋 IMPLEMENTATION PRIORITIES (Next 3 Days)

### Day 6 (Tomorrow) - CRITICAL PATH
**Goal:** Make translation feature actually work

1. **Morning: Test & Fix Translation (4 hours)**
   - [ ] Login as real user
   - [ ] Test crawl endpoint with small website
   - [ ] Test translate endpoint
   - [ ] Fix any errors that occur
   - [ ] Verify ZIP download works

2. **Afternoon: Word Limits (3 hours)**
   - [ ] Add limit check before translation
   - [ ] Show "Upgrade" if limit exceeded
   - [ ] Test with free user (5k limit)
   - [ ] Test with pro user (50k limit)

3. **Evening: Error Handling (2 hours)**
   - [ ] Add try-catch to all endpoints
   - [ ] Return user-friendly errors
   - [ ] Log errors to CloudWatch
   - [ ] Test error scenarios

### Day 7 - STABILIZATION
**Goal:** Prepare for soft launch

1. **Email System (3 hours)**
   - Setup AWS SES
   - Create templates (welcome, password reset)
   - Test sending emails

2. **Monthly Reset (2 hours)**
   - Create Lambda function for cron
   - Setup EventBridge trigger
   - Test reset logic

3. **Documentation Cleanup (2 hours)**
   - Remove SDK/plugin promises
   - Update docs with only working features
   - Add API examples that actually work

### Day 8 - POLISH
**Goal:** Ready for first paying customer

1. **Frontend UX (3 hours)**
   - Improve translate page design
   - Add better loading states
   - Improve error messages

2. **Testing (2 hours)**
   - Test all user flows
   - Test payment flow
   - Test translation with various websites

3. **Monitoring (2 hours)**
   - Setup error tracking (Sentry)
   - Create health check endpoint
   - Setup CloudWatch alarms

---

## 🎯 SUCCESS METRICS

### Technical Metrics
- [ ] Translation success rate > 95%
- [ ] API response time < 2 seconds (for crawl)
- [ ] Translation time < 1 second per page
- [ ] Zero downtime deployments
- [ ] Error rate < 1%

### Business Metrics
- [ ] User signup conversion > 10%
- [ ] Free → Paid conversion > 2%
- [ ] Monthly recurring revenue > €1,000
- [ ] Customer support tickets < 5/week
- [ ] User retention rate > 80%

---

## 📞 SUPPORT & MAINTENANCE

### How Users Get Help
1. **Email:** support@translatecloud.io (needs setup)
2. **Contact Form:** /en/contact.html (exists)
3. **Documentation:** /en/documentation.html (exists, needs cleanup)
4. **FAQ:** /en/faq.html (exists)

### Monitoring
- **CloudWatch Logs:** `/aws/lambda/translatecloud-api`
- **Error Tracking:** Sentry (needs setup)
- **Uptime Monitoring:** UptimeRobot (needs setup)
- **Performance:** AWS X-Ray (needs setup)

### Backup Strategy
- **Database:** RDS automated backups (7-day retention)
- **Files:** S3 with versioning enabled
- **Code:** GitHub repository

---

## 🔐 SECURITY CONSIDERATIONS

### Authentication
- [x] JWT tokens (24h expiry needed)
- [ ] API key authentication (for API access)
- [ ] Rate limiting (prevent abuse)
- [ ] CAPTCHA on signup (prevent spam)

### Data Protection
- [x] Passwords hashed with bcrypt
- [x] HTTPS everywhere
- [x] Environment variables for secrets
- [ ] Encrypt files in S3 at rest
- [ ] Encrypt files in transit (TLS)

### Compliance
- [x] Privacy policy (exists)
- [x] Terms of service (exists)
- [x] Cookie policy (exists)
- [ ] GDPR compliance (data export, deletion)
- [ ] PCI DSS (Stripe handles this)

---

## 📚 DOCUMENTATION NEEDS

### For Users
- [x] Homepage (explains what we do)
- [x] Pricing page (shows plans)
- [ ] **Quick Start Guide** (needs creation)
- [ ] **Video Tutorial** (needs creation)
- [ ] **FAQ** (exists, needs expansion)

### For Developers (Future)
- [ ] **API Reference** (detailed endpoint docs)
- [ ] **SDK Documentation** (when built)
- [ ] **Integration Guides** (WordPress, React, etc.)
- [ ] **Webhook Documentation** (for events)

---

**Next Steps:**
1. Test translation flow manually
2. Document any errors found
3. Create fix plan for Day 6

**Document Created:** October 19, 2025 - 23:30 GMT
**Author:** Claude Code
**Version:** 1.0
