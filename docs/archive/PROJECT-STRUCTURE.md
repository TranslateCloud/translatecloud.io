# TRANSLATECLOUD - PROJECT STRUCTURE

**Last Updated:** 2025-10-18
**Owner:** Virginia Posadas
**Status:** Day 5 - Frontend Authentication Complete

---

## 📂 DIRECTORY STRUCTURE

```
translatecloud/
│
├── backend/                          # Python FastAPI Backend
│   ├── src/
│   │   ├── api/
│   │   │   ├── routers/
│   │   │   │   ├── users.py         # User authentication & management
│   │   │   │   ├── projects.py      # Website translation projects
│   │   │   │   ├── translations.py  # Document translation
│   │   │   │   └── payments.py      # Stripe integration
│   │   │   └── dependencies/
│   │   │       └── auth.py          # JWT authentication middleware
│   │   ├── config/
│   │   │   ├── settings.py          # Environment variables
│   │   │   └── database.py          # PostgreSQL connection
│   │   ├── schemas/
│   │   │   └── (Pydantic models)
│   │   └── services/                # TO DO: Core business logic
│   │       ├── crawler.py           # Web crawler (Playwright)
│   │       ├── translator.py        # MarianMT/Claude API
│   │       ├── document_processor.py
│   │       └── zip_generator.py
│   ├── lambda_handler.py            # AWS Lambda entry point
│   ├── requirements.txt
│   └── translatecloud-api-full.zip
│
├── frontend/                         # Static HTML/CSS/JS
│   ├── css/
│   │   └── shared.css               # Shared styles (legacy)
│   └── public/
│       ├── assets/
│       │   ├── css/
│       │   │   └── legal.css
│       │   └── js/
│       │       ├── cookies.js       # Cookie banner (GDPR)
│       │       ├── auth.js          # ✅ Authentication module
│       │       ├── api.js           # ✅ HTTP client with retry
│       │       └── dark-mode.js     # ✅ Dark mode toggle
│       ├── en/                      # English pages
│       │   ├── index.html
│       │   ├── login.html           # ✅ Login page
│       │   ├── signup.html          # ✅ Signup page
│       │   ├── dashboard.html       # ✅ User dashboard
│       │   ├── privacy-policy.html
│       │   ├── terms-of-service.html
│       │   └── cookie-policy.html
│       └── es/                      # Spanish pages
│           ├── index.html
│           ├── iniciar-sesion.html  # ✅ Login (ES)
│           ├── registro.html        # ✅ Signup (ES)
│           ├── panel.html           # ✅ Dashboard (ES)
│           ├── politica-privacidad.html
│           ├── terminos-condiciones.html
│           └── politica-cookies.html
│
├── scripts/                          # Deployment automation
│   ├── deploy-lambda.ps1
│   └── database/
│       ├── schema.sql               # PostgreSQL schema
│       └── create-api-user.sql
│
├── docs/                            # Documentation
│   ├── PROJECT-STATUS.md
│   ├── TODO.md
│   └── COMPLIANCE.md
│
├── .gitignore
├── CLAUDE-CODE-CONTEXT.md           # Full project context
└── README.md
```

---

## 🏗️ BACKEND ARCHITECTURE (Current State)

### **Deployed Components:**
✅ **FastAPI API** - Deployed on AWS Lambda
✅ **API Gateway** - https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod
✅ **PostgreSQL RDS** - translatecloud-db-prod (eu-west-1)
✅ **Cognito User Pool** - eu-west-1_FH51nx4II

### **Current Endpoints (12 total):**
```
Public:
  GET  /             - API info
  GET  /health       - Health check
  GET  /docs         - Swagger UI

Users (Auth required):
  POST   /api/users/signup
  POST   /api/users/login
  GET    /api/users/me
  DELETE /api/users/me          # GDPR data deletion
  GET    /api/users/me/export   # GDPR data export

Projects:
  POST /api/projects
  GET  /api/projects
  GET  /api/projects/{id}

Translations:
  POST /api/translations
  GET  /api/translations
  GET  /api/translations/{id}

Payments:
  POST /api/payments/create-intent
  POST /api/payments/webhook
```

### **Missing Backend Services (TO DO):**
According to business model, we need:

1. **Web Crawler Service**
   - Crawl up to 50 pages
   - Extract translatable content
   - Preserve HTML structure
   - Word count calculation

2. **Translation Engine**
   - MarianMT for bulk translation
   - Claude API for quality translations
   - Batch processing
   - Language detection

3. **Document Processing**
   - PDF parser (PyPDF2)
   - DOCX parser (python-docx)
   - Text extraction
   - File reconstruction

4. **ZIP Generator**
   - Rebuild website structure
   - Inject translated content
   - Maintain CSS/JS/images
   - Create downloadable ZIP

5. **Billing & Subscription**
   - Stripe integration (complete)
   - Usage tracking (words/month)
   - Plan limits enforcement
   - Overage billing

6. **Project Queue**
   - Background job processing
   - Progress tracking
   - Simultaneous project limits
   - Status updates

---

## 🎨 FRONTEND ARCHITECTURE (Current State)

### **Completed Pages (Day 5):**
✅ **Authentication Flow**
- login.html / iniciar-sesion.html
- signup.html / registro.html
- dashboard.html / panel.html

✅ **Legal Pages (GDPR)**
- Privacy Policy (EN/ES)
- Terms of Service (EN/ES)
- Cookie Policy (EN/ES)

✅ **JavaScript Modules**
- auth.js - JWT authentication
- api.js - HTTP client with retry
- cookies.js - Cookie banner
- dark-mode.js - Developer dark mode

### **Missing Frontend Pages (TO DO):**
According to business model:

1. **Website Translation UI**
   - URL input form
   - Crawl preview (pages found, word count, cost estimate)
   - Payment/credit confirmation
   - Progress tracker (real-time)
   - Download ZIP button

2. **Document Translation UI**
   - File upload (PDF/DOCX/TXT)
   - Text paste area
   - Language selector
   - Word counter + cost preview
   - Download/copy result

3. **Dashboard Enhancements**
   - Project list with status
   - Usage stats (words used/remaining)
   - Recent translations
   - Quick actions

4. **Billing & Subscription**
   - Pricing page (4 tiers)
   - Checkout flow (Stripe)
   - Subscription management
   - Invoices & payment history

5. **Project Management**
   - Project details page
   - Translation history
   - Download past projects
   - Delete projects

---

## 💾 DATABASE SCHEMA (PostgreSQL)

```sql
-- Users table (GDPR compliant)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    company_name VARCHAR(255),
    subscription_tier VARCHAR(50) DEFAULT 'free',  -- TO ADD
    words_used_this_month INT DEFAULT 0,           -- TO ADD
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Projects table (Website translations)
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    source_url VARCHAR(500),                       -- TO ADD
    source_language VARCHAR(10),
    target_language VARCHAR(10),
    pages_count INT,                               -- TO ADD
    word_count INT,                                -- TO ADD
    status VARCHAR(50),                            -- pending, processing, completed, failed
    zip_file_url VARCHAR(500),                     -- S3 URL - TO ADD
    created_at TIMESTAMP DEFAULT NOW()
);

-- Translations table (Document translations)
CREATE TABLE translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),             -- TO ADD for direct translations
    source_text TEXT NOT NULL,
    translated_text TEXT,
    source_language VARCHAR(10),                   -- TO ADD
    target_language VARCHAR(10),                   -- TO ADD
    word_count INT,                                -- TO ADD
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Payments table (Stripe integration)
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',
    status VARCHAR(50),
    stripe_payment_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),           -- TO ADD
    plan VARCHAR(50),                              -- TO ADD
    created_at TIMESTAMP DEFAULT NOW()
);

-- TO ADD: Subscriptions table
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    stripe_subscription_id VARCHAR(255) UNIQUE,
    plan VARCHAR(50),                              -- payasyougo, professional, business, enterprise
    status VARCHAR(50),                            -- active, canceled, past_due
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    words_limit INT,
    words_used INT DEFAULT 0,
    projects_limit INT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🚀 AWS INFRASTRUCTURE

### **Production Resources:**
- **Region:** eu-west-1 (Ireland)
- **Lambda:** translatecloud-api (Python 3.11, 512 MB)
- **API Gateway:** e5yug00gdc (CORS enabled)
- **RDS PostgreSQL:** translatecloud-db-prod (db.t3.micro)
- **Cognito:** User Pool eu-west-1_FH51nx4II
- **S3 Buckets:**
  - translatecloud-uploads-prod (user uploads)
  - translatecloud-translations-prod (translated files)
  - translatecloud-web-projects (website ZIPs)
  - translatecloud-backups-prod (DB backups)
  - translatecloud-logs-prod (access logs)
  - translatecloud-frontend-prod (static website)
- **CloudFront:** E1PKVM5C703IXO (CDN for frontend)

### **Missing Infrastructure (TO DO):**
- **Lambda Functions:**
  - Web crawler function (Playwright in Lambda layer)
  - Translation processor (background jobs)
  - ZIP generator function
  - Document processor function
- **SQS:** Job queue for translation projects
- **SNS:** Notifications (project completed)
- **EventBridge:** Scheduled jobs (reset monthly usage)

---

## 🔐 SECURITY & COMPLIANCE

### **Implemented:**
✅ JWT authentication (24h expiration)
✅ Password hashing (Cognito)
✅ HTTPS everywhere
✅ GDPR compliant (data export + deletion endpoints)
✅ Cookie consent banner
✅ Privacy Policy, Terms of Service, Cookie Policy
✅ S3 encryption (AES-256)
✅ Database encryption at rest (RDS)
✅ CORS properly configured

### **Pending:**
⏳ SOC 2 Type II certification (mentioned in marketing)
⏳ API rate limiting (for Business+ plans)
⏳ 2FA optional
⏳ Session management (logout all devices)

---

## 📊 BUSINESS MODEL SUPPORT

### **Service 1: Website Translation (80% revenue)**
**Status:** ⏳ Backend NOT implemented yet

**Required Components:**
- [ ] Web crawler service
- [ ] HTML parser & reconstructor
- [ ] Batch translation API
- [ ] ZIP generator
- [ ] Project queue & status tracking
- [ ] Cost estimation (word count × €0.055)

### **Service 2: Document Translation (20% revenue)**
**Status:** ⏳ Backend NOT implemented yet

**Required Components:**
- [ ] File upload handler (PDF/DOCX/TXT)
- [ ] Document parsers
- [ ] Text translation API
- [ ] File reconstruction & download
- [ ] Cost calculation (word count × €0.05)

### **Pricing Tiers:**
**Status:** ⏳ Stripe integration partial

**Required Components:**
- [ ] Subscription management (Stripe)
- [ ] Usage tracking (words/month)
- [ ] Plan limits enforcement
- [ ] Overage billing
- [ ] API access control (Business+)

---

## 📈 NEXT PRIORITIES (Based on Business Model)

### **Week 1 (Current - Day 5 Complete):**
✅ Authentication (login/signup/dashboard)
✅ Legal pages (GDPR)
✅ Dark mode for developers

### **Week 2 (Critical Path - Revenue Enablement):**
1. **Stripe Integration** (Priority 1)
   - Pricing page (4 tiers)
   - Checkout flow
   - Subscription management
   - Webhooks (payment succeeded, subscription updated)

2. **Website Translation MVP** (Priority 2 - 80% revenue)
   - URL input form
   - Basic crawler (10 pages max for MVP)
   - MarianMT translation
   - ZIP download
   - Word count billing

3. **Document Translation MVP** (Priority 3 - 20% revenue)
   - File upload (TXT only for MVP)
   - Translation API
   - Download result
   - Pay-per-word

### **Week 3-4 (Scale & Polish):**
- Full crawler (50 pages)
- PDF/DOCX support
- API access (Business+)
- White-label (Enterprise)
- Admin panel

---

## 🎯 CRITICAL USER JOURNEYS (TO IMPLEMENT)

### **Journey 1: First-Time User (Website Translation)**
1. Land on homepage → "Translate Your Website"
2. Click "Get Started" → Signup page
3. Create account → Dashboard
4. Click "New Website Project"
5. Enter URL → System crawls → Show preview
6. Confirm payment (€0.055/word)
7. System processes (progress bar)
8. Download ZIP with translated site

### **Journey 2: Subscription User**
1. Login → Dashboard shows usage stats
2. See: "15,000 / 80,000 words used this month"
3. Click "New Project" → Already has credits
4. Process translation → Words deducted from quota
5. If over quota → Overage billing at €0.055/word

---

## 📝 TECHNICAL DEBT & IMPROVEMENTS

### **Code Quality:**
- [ ] Separate CSS from HTML (create external stylesheets)
- [ ] Minify JS/CSS for production
- [ ] Add TypeScript for frontend (optional)
- [ ] Backend unit tests (pytest)
- [ ] E2E tests (Playwright)

### **Performance:**
- [ ] CloudFront caching strategy
- [ ] Lambda cold start optimization
- [ ] Database connection pooling
- [ ] Redis for session storage

### **DevOps:**
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Automated deployments
- [ ] Monitoring (CloudWatch + Sentry)
- [ ] Backup automation

---

**END OF PROJECT STRUCTURE**
