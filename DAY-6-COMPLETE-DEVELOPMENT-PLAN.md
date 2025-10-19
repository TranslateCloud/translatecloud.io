# Day 6 - Complete Development Plan
**Date:** October 19, 2025
**Objective:** Fix Critical Issues + Complete MVP Features
**Total Time:** 6-8 hours

---

## 🚨 CRITICAL FIXES (Must Do First - 1.5 hours)

### **1. Fix Dark Mode Contrast on Policy Pages** (30 mins)
**Priority:** CRITICAL - Users cannot read content
**Issue:** Dark mode changes background but not text color (white text on white bg)

**Affected Pages:**
- `/en/cookies-policy.html`
- `/en/privacy-policy.html`
- `/en/terms-of-service.html`
- `/es/politica-cookies.html`
- `/es/politica-privacidad.html`
- `/es/terminos-servicio.html`

**Solution:**
```css
/* Add to dark mode styles in dark-mode.js */
body.dark-mode {
    background-color: #1a1a1a;
    color: #e5e5e5; /* Light text for dark background */
}

body.dark-mode h1,
body.dark-mode h2,
body.dark-mode h3 {
    color: #ffffff;
}

body.dark-mode p,
body.dark-mode li {
    color: #d1d5db; /* Gray-300 */
}

body.dark-mode .content-container {
    background-color: #262626;
    color: #e5e5e5;
}
```

**Testing:**
- Toggle dark mode on each policy page
- Verify all text is readable
- Check headings, paragraphs, lists, links

---

### **2. Add Footer to All Pages** (30 mins)
**Priority:** HIGH - Consistency across site
**Issue:** Footer only on some pages (pricing, signup), missing on index, policy pages, etc.

**Footer HTML:**
```html
<footer class="footer">
    <p class="footer-text">© 2025 TranslateCloud. All rights reserved.</p>
</footer>
```

**Footer CSS:**
```css
.footer {
    background-color: var(--color-gray-900);
    color: var(--color-gray-400);
    padding: var(--space-12) var(--space-8);
    text-align: center;
}

.footer-text {
    font-size: var(--text-sm);
}
```

**Pages Missing Footer:**
- `/en/index.html`
- `/en/cookies-policy.html`
- `/en/privacy-policy.html`
- `/en/terms-of-service.html`
- `/en/login.html`
- `/en/dashboard.html`
- `/en/translate.html`
- All Spanish versions (`/es/*`)

**Steps:**
1. Add footer HTML before `</body>` tag
2. Add footer CSS in `<style>` section
3. Deploy all updated pages to S3
4. Verify footer appears on all pages

---

### **3. Fix Signup Authentication** (30 mins)
**Priority:** CRITICAL - Core functionality broken
**Current Error:** "Signup failed"

**Root Cause:** Database missing `password_hash` column

**Solution - Run Database Migration:**

```sql
-- Connect to RDS database as master user
-- Database: translatecloud-db-prod.c3asoiwiy0l1.eu-west-1.rds.amazonaws.com

-- Add password authentication columns
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS words_used_this_month INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS stripe_subscription_id VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_tier VARCHAR(50) DEFAULT 'free';

-- Make cognito_sub optional (we're using password auth now)
ALTER TABLE users ALTER COLUMN cognito_sub DROP NOT NULL;

-- Create index for faster password lookups
CREATE INDEX IF NOT EXISTS idx_users_password_hash ON users(password_hash);

-- Verify migration
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY ordinal_position;
```

**How to Run:**
1. **Option A:** AWS RDS Query Editor
   - Go to AWS Console → RDS → Query Editor
   - Select `translatecloud-db-prod`
   - Connect with master credentials
   - Paste SQL above
   - Execute

2. **Option B:** pgAdmin/DBeaver
   - Connect to RDS endpoint
   - Open SQL editor
   - Run migration script

**Testing After Migration:**
1. Clear browser cache (Ctrl + Shift + Delete)
2. Go to signup page
3. Create test account:
   - First Name: Test
   - Last Name: User
   - Email: test@example.com
   - Password: TestPassword123!
4. Should receive JWT token and redirect to dashboard
5. Verify token in localStorage: `translatecloud_token`

---

## 🔧 PHASE 1: Complete Authentication Flow (2 hours)

### **4. Add Email Verification** (1.5 hours)
**Priority:** MEDIUM - Security best practice

**Requirements:**
- Users must verify email before accessing dashboard
- Send verification link via AWS SES
- 24-hour token expiry
- Resend verification option

**Implementation:**

**4.1. Set up AWS SES** (15 mins)
```bash
# Verify sender email
aws ses verify-email-identity \
  --email-address noreply@translatecloud.io \
  --region eu-west-1

# Check verification status
aws ses get-identity-verification-attributes \
  --identities noreply@translatecloud.io \
  --region eu-west-1
```

**4.2. Database Schema Update** (5 mins)
```sql
ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN verification_token VARCHAR(255);
ALTER TABLE users ADD COLUMN verification_token_expires TIMESTAMP;
CREATE INDEX idx_users_verification_token ON users(verification_token);
```

**4.3. Create Email Service** (30 mins)
File: `backend/src/services/email.py`

```python
import boto3
from datetime import datetime, timedelta
import secrets

ses_client = boto3.client('ses', region_name='eu-west-1')

def send_verification_email(email: str, token: str):
    verification_url = f"http://translatecloud-frontend-prod.s3-website-eu-west-1.amazonaws.com/en/verify.html?token={token}"

    ses_client.send_email(
        Source='noreply@translatecloud.io',
        Destination={'ToAddresses': [email]},
        Message={
            'Subject': {'Data': 'Verify Your TranslateCloud Account'},
            'Body': {
                'Html': {
                    'Data': f'''
                    <!DOCTYPE html>
                    <html>
                    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #111827;">Welcome to TranslateCloud!</h2>
                        <p>Please verify your email address by clicking the button below:</p>
                        <p style="text-align: center; margin: 30px 0;">
                            <a href="{verification_url}"
                               style="background-color: #0EA5E9; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                                Verify Email
                            </a>
                        </p>
                        <p style="color: #6B7280; font-size: 14px;">
                            This link expires in 24 hours. If you didn't create this account, you can safely ignore this email.
                        </p>
                        <p style="color: #6B7280; font-size: 14px;">
                            Or copy and paste this link: {verification_url}
                        </p>
                    </body>
                    </html>
                    '''
                }
            }
        }
    )

def generate_verification_token() -> tuple[str, datetime]:
    token = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(hours=24)
    return token, expires
```

**4.4. Update Signup Endpoint** (20 mins)
File: `backend/src/api/routes/auth.py`

```python
from src.services.email import send_verification_email, generate_verification_token

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate, cursor: RealDictCursor = Depends(get_db)):
    # ... existing code ...

    # Generate verification token
    verification_token, expires = generate_verification_token()

    cursor.execute('''
        UPDATE users
        SET verification_token = %s, verification_token_expires = %s
        WHERE id = %s
    ''', (verification_token, expires, user_id))

    # Send verification email
    try:
        send_verification_email(user.email, verification_token)
    except Exception as e:
        print(f"Failed to send verification email: {e}")

    return {
        "message": "Account created. Please check your email to verify your account.",
        "email": user.email
    }
```

**4.5. Add Verification Endpoint** (15 mins)
```python
@router.get("/verify")
async def verify_email(token: str, cursor: RealDictCursor = Depends(get_db)):
    cursor.execute('''
        SELECT id FROM users
        WHERE verification_token = %s
        AND verification_token_expires > NOW()
    ''', (token,))

    user = cursor.fetchone()

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification token"
        )

    cursor.execute('''
        UPDATE users
        SET email_verified = TRUE, verification_token = NULL
        WHERE id = %s
    ''', (user['id'],))

    return {"message": "Email verified successfully"}
```

**4.6. Create Verification Pages** (15 mins)
Files:
- `frontend/public/en/verify.html`
- `frontend/public/es/verificar.html`

---

### **5. Add Password Strength Requirements** (30 mins)
**Priority:** MEDIUM - Security improvement

**Frontend Validation:**
```javascript
function validatePassword(password) {
    const requirements = {
        length: password.length >= 8,
        uppercase: /[A-Z]/.test(password),
        lowercase: /[a-z]/.test(password),
        number: /[0-9]/.test(password),
        special: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)
    };

    return {
        isValid: Object.values(requirements).every(Boolean),
        requirements
    };
}
```

**Backend Validation:**
File: `backend/src/schemas/user.py`

```python
from pydantic import field_validator
import re

class UserCreate(UserBase):
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain number')
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', v):
            raise ValueError('Password must contain special character')
        return v
```

---

## 🛡️ PHASE 2: Security Hardening (1.5 hours)

### **6. Add Rate Limiting** (1 hour)
**Priority:** HIGH - Prevent brute force attacks

**Option A: API Gateway Throttling** (Easiest - 15 mins)
```bash
aws apigateway create-usage-plan \
  --name "auth-rate-limit" \
  --throttle burstLimit=10,rateLimit=5 \
  --api-stages apiId=e5yug00gdc,stage=prod \
  --region eu-west-1
```

**Option B: Application-Level (slowapi)** (45 mins)

Add to `requirements.txt`:
```
slowapi==0.1.9
```

Update `backend/src/main.py`:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

Update `backend/src/api/routes/auth.py`:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

limiter = Limiter(key_func=get_remote_address)

@router.post("/signup")
@limiter.limit("5/minute")
async def signup(request: Request, user: UserCreate, ...):
    # ... existing code

@router.post("/login")
@limiter.limit("10/minute")
async def login(request: Request, email: str, ...):
    # ... existing code
```

---

### **7. Remove Hardcoded JWT Secret Fallback** (30 mins)
**Priority:** HIGH - Security vulnerability

**Current Code (backend/src/api/routes/auth.py:17):**
```python
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")  # BAD
```

**Fixed Code:**
```python
SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not SECRET_KEY:
    raise ValueError(
        "JWT_SECRET_KEY environment variable is required. "
        "Configure it in Lambda environment variables."
    )
```

**Deploy:**
1. Update auth.py
2. Redeploy Lambda
3. Test: Remove env var → Lambda should fail to start

---

## 📱 PHASE 3: Frontend Polish (1.5 hours)

### **8. Improve Password Strength Indicator** (30 mins)
**Current:** Basic 5-level meter
**Improvement:** Real-time feedback with requirements checklist

**Update signup pages:**
```javascript
<div class="password-requirements">
    <div class="requirement" id="req-length">
        <i data-lucide="circle" class="req-icon"></i>
        <span>At least 8 characters</span>
    </div>
    <div class="requirement" id="req-uppercase">
        <i data-lucide="circle" class="req-icon"></i>
        <span>One uppercase letter</span>
    </div>
    <div class="requirement" id="req-lowercase">
        <i data-lucide="circle" class="req-icon"></i>
        <span>One lowercase letter</span>
    </div>
    <div class="requirement" id="req-number">
        <i data-lucide="circle" class="req-icon"></i>
        <span>One number</span>
    </div>
    <div class="requirement" id="req-special">
        <i data-lucide="circle" class="req-icon"></i>
        <span>One special character (!@#$...)</span>
    </div>
</div>

<script>
passwordInput.addEventListener('input', () => {
    const password = passwordInput.value;
    const validation = validatePassword(password);

    // Update each requirement indicator
    Object.keys(validation.requirements).forEach(key => {
        const element = document.getElementById(`req-${key}`);
        const icon = element.querySelector('.req-icon');

        if (validation.requirements[key]) {
            element.classList.add('met');
            icon.setAttribute('data-lucide', 'check-circle');
        } else {
            element.classList.remove('met');
            icon.setAttribute('data-lucide', 'circle');
        }
    });

    lucide.createIcons();
});
</script>
```

---

### **9. Add Loading States to Forms** (30 mins)
**Pages:** Signup, Login, Checkout

**Current Issue:** No visual feedback during API calls

**Solution:**
```javascript
async function handleSubmit(e) {
    e.preventDefault();

    // Show loading state
    submitBtn.disabled = true;
    submitBtn.classList.add('loading');
    submitBtn.innerHTML = `
        <span class="spinner"></span>
        <span>Creating account...</span>
    `;

    try {
        const response = await API.post('/auth/signup', data);
        // Success handling
    } catch (error) {
        // Error handling
    } finally {
        // Reset button
        submitBtn.disabled = false;
        submitBtn.classList.remove('loading');
        submitBtn.innerHTML = 'Create Account';
    }
}
```

---

### **10. Improve Error Messages** (30 mins)
**Current:** Generic "Signup failed"
**Improvement:** Specific, actionable error messages

**Error Message Map:**
```javascript
const ERROR_MESSAGES = {
    'already exists': 'An account with this email already exists. Please sign in instead.',
    'invalid email': 'Please enter a valid email address.',
    'weak password': 'Password does not meet security requirements.',
    'network error': 'Unable to connect. Please check your internet connection.',
    'server error': 'Something went wrong on our end. Please try again in a few moments.',
    'validation error': 'Please check your input and try again.'
};

function getErrorMessage(error) {
    const message = error.message.toLowerCase();

    for (const [key, value] of Object.entries(ERROR_MESSAGES)) {
        if (message.includes(key)) {
            return value;
        }
    }

    return 'Unable to create account. Please try again or contact support.';
}
```

---

## 🚀 PHASE 4: Translation MVP (Optional - 2 hours)

### **11. Implement Basic Translation Service** (2 hours)
**Priority:** LOW - Can be Day 7

**Not including full implementation here - will create separate plan if needed**

---

## ✅ DAY 6 CHECKLIST

### **Morning Session (2 hours)**
- [ ] Fix dark mode contrast on all policy pages
- [ ] Add footer to all missing pages
- [ ] Deploy all frontend updates to S3
- [ ] Run database migration for password_hash column
- [ ] Test signup end-to-end

### **Midday Session (2 hours)**
- [ ] Add email verification system
- [ ] Create verification email template
- [ ] Add password strength requirements
- [ ] Test verification flow

### **Afternoon Session (2 hours)**
- [ ] Implement rate limiting (API Gateway)
- [ ] Remove hardcoded JWT secret
- [ ] Improve password strength UI
- [ ] Add loading states to forms
- [ ] Improve error messages

### **Evening Session (1 hour)**
- [ ] Test all authentication flows
- [ ] Test dark mode on all pages
- [ ] Verify footer on all pages
- [ ] Create Day 7 plan
- [ ] Commit all changes to git

---

## 📊 Success Metrics

**By End of Day 6:**
1. ✅ Dark mode readable on ALL pages
2. ✅ Footer visible on ALL pages
3. ✅ Signup working 100%
4. ✅ Login working 100%
5. ✅ Email verification functional
6. ✅ Password requirements enforced
7. ✅ Rate limiting active
8. ✅ No security vulnerabilities (hardcoded secrets)

---

## 🐛 Known Issues to Fix

### **CRITICAL (Today)**
1. Dark mode white text on white background - **UNREADABLE**
2. Signup failing - database missing password_hash
3. Missing footer on most pages

### **HIGH (Today)**
4. No email verification - security risk
5. Weak password validation
6. No rate limiting - brute force vulnerability
7. Hardcoded JWT secret fallback

### **MEDIUM (Today if time)**
8. Generic error messages
9. No loading states
10. Password strength indicator basic

### **LOW (Can wait for Day 7)**
11. Translation service not implemented
12. Dashboard empty
13. No user profile editing
14. No password reset

---

## 📁 Files to Modify Today

### **Frontend (S3)**
```
frontend/public/en/
├── index.html                 # Add footer
├── cookies-policy.html        # Fix dark mode + add footer
├── privacy-policy.html        # Fix dark mode + add footer
├── terms-of-service.html      # Fix dark mode + add footer
├── login.html                 # Add footer
├── signup.html                # Improve password validation
├── verify.html                # CREATE NEW
├── dashboard.html             # Add footer
└── translate.html             # Add footer

frontend/public/es/
├── index.html                 # Add footer
├── politica-cookies.html      # Fix dark mode + add footer
├── politica-privacidad.html   # Fix dark mode + add footer
├── terminos-servicio.html     # Fix dark mode + add footer
├── iniciar-sesion.html        # Add footer
├── registro.html              # Improve password validation
├── verificar.html             # CREATE NEW
└── tablero.html               # Add footer

frontend/public/assets/js/
└── dark-mode.js               # Fix text colors for dark mode
```

### **Backend (Lambda)**
```
backend/src/api/routes/
└── auth.py                    # Remove hardcoded secret, add rate limiting, add verification

backend/src/schemas/
└── user.py                    # Add password validation

backend/src/services/
└── email.py                   # CREATE NEW - email verification

backend/
└── requirements.txt           # Add slowapi (if using app-level rate limiting)
```

### **Database (RDS)**
```sql
-- Run migration to add:
-- - password_hash
-- - email_verified
-- - verification_token
-- - verification_token_expires
-- - words_used_this_month
-- - stripe_subscription_id
-- - subscription_tier
```

---

## ⏰ Time Breakdown

| Task | Time | Priority |
|------|------|----------|
| Fix dark mode contrast | 30 min | CRITICAL |
| Add footer to all pages | 30 min | HIGH |
| Fix signup (DB migration) | 30 min | CRITICAL |
| Email verification | 1.5 hrs | MEDIUM |
| Password strength | 30 min | MEDIUM |
| Rate limiting | 1 hr | HIGH |
| Remove hardcoded secret | 30 min | HIGH |
| Frontend polish | 1.5 hrs | LOW |
| **TOTAL** | **6 hours** | - |

---

## 🔄 Git Commits Plan

**After Critical Fixes:**
```bash
git commit -m "Day 6: Fix dark mode contrast and add footer to all pages

- Fix dark mode text colors on policy pages (white → gray-300)
- Add footer HTML + CSS to all missing pages
- Deploy all frontend updates to S3
- UTF-8 without BOM

🤖 Generated with Claude Code"
```

**After Auth Fixes:**
```bash
git commit -m "Day 6: Complete authentication system with verification

- Run database migration (password_hash, email_verified columns)
- Add email verification via AWS SES
- Implement password strength requirements
- Add rate limiting to auth endpoints
- Remove hardcoded JWT secret fallback

🤖 Generated with Claude Code"
```

---

## 🎯 Day 7 Preview

**Focus:** Translation MVP + Dashboard
**Goals:**
- Implement web crawler (BeautifulSoup)
- Add MarianMT translation service
- Create ZIP export functionality
- Build functional dashboard
- Add usage statistics
- Implement project management

---

**Last Updated:** October 19, 2025 - 01:00 GMT
**Created By:** Claude Code
**Status:** Ready to Execute
