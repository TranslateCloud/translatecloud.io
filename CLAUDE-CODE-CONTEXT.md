# TRANSLATECLOUD - CLAUDE CODE CONTEXT
Last Updated: 2025-10-18 11:55:26

## PROJECT OVERVIEW
- **Name**: TranslateCloud
- **Type**: B2B SaaS - AI Translation Platform
- **Tech Stack**: FastAPI (Python) + PostgreSQL + AWS Lambda + Static HTML/CSS/JS
- **Region**: EU (eu-west-1 Ireland)
- **Status**: Day 5 - Legal pages completed, starting frontend interactivity

---

## CURRENT PROGRESS

### ✅ COMPLETED (Days 1-5)
1. **Infrastructure** (Day 1-2)
   - Domain: translatecloud.com (Route53)
   - SSL Certificate (ACM)
   - S3 + CloudFront for frontend
   - RDS PostgreSQL 15.14 (db.t3.micro)
   - Security Groups configured

2. **Backend API** (Day 3-4)
   - FastAPI deployed on Lambda
   - API Gateway: https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod
   - 12 endpoints across 4 routers (users, projects, translations, payments)
   - JWT authentication with Cognito
   - Database connection working

3. **Legal Pages** (Day 5)
   - Privacy Policy (EN/ES)
   - Terms of Service (EN/ES)
   - Cookie Policy (EN/ES)
   - Cookie banner (functional JS)
   - GDPR compliant

### ⏳ IN PROGRESS (Day 5)
- Frontend JavaScript to connect with API
- Login/Signup forms (functional)
- JWT token management
- User dashboard

### 📋 TODO (Week 2)
- Stripe payment integration
- Translation UI (file upload)
- Document processing
- Admin panel

---

## PROJECT STRUCTURE

\\\
translatecloud/
├── backend/                          # Python FastAPI
│   ├── src/
│   │   ├── api/
│   │   │   ├── routers/             # users, projects, translations, payments
│   │   │   └── dependencies/        # JWT auth middleware
│   │   ├── config/                  # settings.py, database.py
│   │   └── schemas/                 # Pydantic models
│   ├── lambda_handler.py
│   ├── requirements.txt
│   └── translatecloud-api-full.zip  # Lambda deployment package
│
├── frontend/                         # Static HTML/CSS/JS
│   ├── css/
│   │   └── shared.css               # Main stylesheet
│   └── public/
│       ├── assets/
│       │   ├── css/
│       │   │   └── legal.css        # ✅ NEW (Day 5)
│       │   └── js/
│       │       └── cookies.js       # ✅ NEW (Day 5)
│       ├── en/
│       │   ├── index.html
│       │   ├── login.html
│       │   ├── pricing.html
│       │   ├── privacy-policy.html  # ✅ NEW (Day 5)
│       │   ├── terms-of-service.html # ✅ NEW (Day 5)
│       │   └── cookie-policy.html   # ✅ NEW (Day 5)
│       └── es/
│           ├── index.html
│           ├── iniciar-sesion.html
│           ├── precios.html
│           ├── politica-privacidad.html    # ✅ NEW (Day 5)
│           ├── terminos-condiciones.html   # ✅ NEW (Day 5)
│           └── politica-cookies.html       # ✅ NEW (Day 5)
│
├── scripts/                          # Deployment automation
│   ├── deploy-lambda.ps1
│   └── database/
│       ├── schema.sql
│       └── create-api-user.sql
│
├── docs/                             # Documentation
│   ├── PROJECT-STATUS.md
│   ├── TODO.md
│   └── COMPLIANCE.md (GDPR)
│
└── .gitignore
\\\

---

## AWS RESOURCES

### Lambda Function
- **Name**: translatecloud-api
- **Runtime**: Python 3.11
- **Memory**: 512 MB
- **Timeout**: 30s
- **Environment Variables**:
  - DATABASE_URL (from Secrets Manager)
  - JWT_SECRET (from Secrets Manager)

### API Gateway
- **ID**: e5yug00gdc
- **Stage**: prod
- **Endpoint**: https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod
- **Routes**: /, /health, /docs, /api/*

### RDS PostgreSQL
- **Identifier**: translatecloud-db-prod
- **Endpoint**: translatecloud-db-prod.c3asoiwiy0l1.eu-west-1.rds.amazonaws.com
- **Port**: 5432
- **Database**: postgres
- **User (API)**: translatecloud_api
- **Password**: Stored in Secrets Manager (prod/translatecloud/db)

### Cognito
- **User Pool ID**: eu-west-1_FH51nx4II
- **App Client ID**: 6he757k99vkr15llk139usiub6

### S3 + CloudFront
- **Bucket**: translatecloud-frontend-prod
- **CloudFront ID**: E1PKVM5C703IXO
- **Distribution**: d3sa5i2s0uyozh.cloudfront.net

---

## DATABASE SCHEMA

\\\sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    company_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Projects table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    source_language VARCHAR(10),
    target_language VARCHAR(10),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Translations table
CREATE TABLE translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    source_text TEXT NOT NULL,
    translated_text TEXT,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Payments table
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',
    status VARCHAR(50),
    stripe_payment_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);
\\\

---

## API ENDPOINTS

### Public
- \GET  /\ - API info
- \GET  /health\ - Health check
- \GET  /docs\ - Swagger UI

### Users (Auth required)
- \POST   /api/users/signup\ - Register new user
- \POST   /api/users/login\ - Login (returns JWT)
- \GET    /api/users/me\ - Get current user profile
- \DELETE /api/users/me\ - Delete account (GDPR)
- \GET    /api/users/me/export\ - Export data (GDPR)

### Projects (Auth required)
- \POST /api/projects\ - Create project
- \GET  /api/projects\ - List user projects
- \GET  /api/projects/{id}\ - Get project details

### Translations (Auth required)
- \POST /api/translations\ - Create translation
- \GET  /api/translations\ - List translations
- \GET  /api/translations/{id}\ - Get translation

### Payments (Auth required)
- \POST /api/payments/create-intent\ - Create Stripe payment intent
- \POST /api/payments/webhook\ - Stripe webhook handler

---

## DESIGN SYSTEM

### Colors
- **Primary**: #111827 (Dark gray/black)
- **Accent**: #0EA5E9 (Sky blue)
- **Grays**: #F9FAFB to #111827 (9 levels)

### Typography
- **Font**: IBM Plex Sans
- **Weights**: 300 (light), 400 (normal), 500 (medium), 600 (semibold)
- **NO BOLD/EXTRABOLD** (max 600)
- **Sizes**: 12px to 44px (max for titles)

### Spacing
- Base: 8px scale
- Generous spacing (breathing room)

### Style
- Minimalista enterprise/fintech
- Sombras sutiles (opacity 0.08)
- Border radius max 12px
- Sin gradientes
- Inspiración: IBM, Stripe, AWS

---

## DEVELOPMENT WORKFLOW

### 1. Local Development
\\\powershell
# Backend (local testing)
cd backend
python lambda_handler.py

# Frontend (just open HTML files)
# No build process - static files
\\\

### 2. Deployment
\\\powershell
# Backend (Lambda)
cd backend
.\scripts\deploy-lambda.ps1

# Frontend (S3 + CloudFront)
aws s3 sync frontend/public/ s3://translatecloud-frontend-prod/
aws cloudfront create-invalidation --distribution-id E1PKVM5C703IXO --paths "/*"
\\\

### 3. Git Workflow
\\\powershell
git status
git add .
git commit -m "Description"
# No remote configured yet
\\\

---

## CODING STANDARDS

### Python (Backend)
- FastAPI with async/await
- Type hints everywhere
- Pydantic for validation
- No hardcoded secrets (use Secrets Manager)
- UTF-8 encoding (no BOM)

### JavaScript (Frontend)
- Vanilla JS (no frameworks)
- ES6+ syntax
- Async/await for API calls
- Store JWT in localStorage
- UTF-8 encoding (no BOM)

### CSS
- Use Design System variables
- Mobile-first responsive
- No preprocessors (pure CSS)
- UTF-8 encoding (no BOM)

### HTML
- Semantic HTML5
- Accessibility (ARIA labels)
- SEO meta tags
- hreflang for i18n
- UTF-8 encoding (no BOM)

---

## NEXT TASKS (Priority Order)

### Immediate (Day 5 - Today)
1. **Create auth.js** - JWT management, localStorage
2. **Create api.js** - Fetch wrapper for API calls
3. **Update login.html** - Wire up real authentication
4. **Update iniciar-sesion.html** - Spanish version
5. **Create dashboard.html** - Basic user dashboard
6. **Test end-to-end** - Signup → Login → Dashboard

### Next (Day 6)
1. **Stripe Integration**
   - Create Stripe account
   - Add Stripe.js to frontend
   - Checkout page
   - Webhook handler

### Week 2
1. **Translation Feature**
   - File upload UI
   - MarianMT integration
   - Progress indicator
   - Download results

---

## IMPORTANT NOTES

### Security
- All passwords hashed (Cognito)
- JWT tokens expire after 24h
- HTTPS everywhere (CloudFront + API Gateway)
- Database encrypted at rest (RDS)
- Secrets in AWS Secrets Manager

### GDPR Compliance
- ✅ Privacy Policy (EN/ES)
- ✅ Terms of Service (EN/ES)
- ✅ Cookie Policy (EN/ES)
- ✅ Cookie banner (functional)
- ⏳ Data export endpoint
- ⏳ Data deletion endpoint
- ⏳ Consent checkboxes

### File Encoding
- **CRITICAL**: All files MUST be UTF-8 without BOM
- PowerShell: Use \$utf8NoBom = New-Object System.Text.UTF8Encoding \False\
- Reason: BOM causes issues with Lambda and browsers

### Git
- Local repository only (no remote yet)
- Latest commit: b451db3 (Day 5: Legal pages)
- Files NOT in Git: local-backups/, Audits/, *.zip, CLAUDE.md

---

## COMMON COMMANDS

### Database
\\\powershell
# Connect to RDS
\ = "ApiUser2025Secure!"
psql -h translatecloud-db-prod.c3asoiwiy0l1.eu-west-1.rds.amazonaws.com -U translatecloud_api -d postgres
Remove-Item Env:\PGPASSWORD
\\\

### API Testing
\\\powershell
# Health check
curl https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod/health

# Swagger docs
start https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod/docs
\\\

### Lambda Update
\\\powershell
aws lambda update-function-code --function-name translatecloud-api --zip-file fileb://backend/translatecloud-api-full.zip --region eu-west-1
\\\

---

## TROUBLESHOOTING

### Issue: Lambda cold start slow
- Solution: Increase memory to 512MB (done)

### Issue: CORS errors from frontend
- Solution: API Gateway has CORS enabled
- Check: OPTIONS method returns proper headers

### Issue: JWT token invalid
- Solution: Check token expiry, verify secret matches

### Issue: Database connection timeout
- Solution: Check Lambda VPC config, Security Group rules

---

**For Claude Code**: You now have full context. When working on frontend interactivity:
1. Read existing files first
2. Follow Design System strictly
3. Use UTF-8 without BOM
4. Test locally before deploying
5. Commit to Git after each feature

**Current task**: Create auth.js and api.js for frontend-backend connection.