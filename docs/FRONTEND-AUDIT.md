# TranslateCloud - Frontend Audit & Action Plan

**Date:** 2025-10-20
**Status:** Base Frontend Before Multi-Country Implementation
**Purpose:** Document all pages, buttons, links, and create fix checklist

---

## 📊 EXISTING PAGES INVENTORY

### ✅ English Pages (`/en/`) - 22 pages

| Page | Status | Notes |
|------|--------|-------|
| `index.html` | ✅ Exists | Landing page |
| `login.html` | ✅ Exists | User login |
| `signup.html` | ✅ Exists | User registration |
| `forgot-password.html` | ✅ Exists | Password reset |
| `dashboard.html` | ✅ Exists | User dashboard |
| `translate.html` | ✅ Exists | Translation tool (NEEDS ASYNC UPDATE) |
| `pricing.html` | ✅ Exists | Pricing table |
| `features.html` | ✅ Exists | Feature list |
| `solutions.html` | ✅ Exists | Solution pages |
| `enterprise.html` | ✅ Exists | Enterprise plan |
| `about.html` | ✅ Exists | About us |
| `contact.html` | ✅ Exists | Contact form |
| `faq.html` | ✅ Exists | FAQ |
| `help.html` | ✅ Exists | Help center |
| `documentation.html` | ✅ Exists | Docs |
| `api-docs.html` | ✅ Exists | API documentation |
| `privacy-policy.html` | ✅ Exists | Privacy |
| `terms-of-service.html` | ✅ Exists | Terms |
| `cookie-policy.html` | ✅ Exists | Cookies |
| `checkout.html` | ✅ Exists | Payment checkout |
| `checkout-success.html` | ✅ Exists | Payment success |
| `checkout-cancel.html` | ✅ Exists | Payment cancel |

### ✅ Spanish Pages (`/es/`) - 16 pages

| Page | Status | Notes |
|------|--------|-------|
| `index.html` | ✅ Exists | Landing (Spanish) |
| `iniciar-sesion.html` | ✅ Exists | Login |
| `registro.html` | ✅ Exists | Signup |
| `panel.html` | ✅ Exists | Dashboard |
| `precios.html` | ✅ Exists | Pricing |
| `caracteristicas.html` | ✅ Exists | Features |
| `soluciones.html` | ✅ Exists | Solutions |
| `empresa.html` | ✅ Exists | Enterprise |
| `sobre-nosotros.html` | ✅ Exists | About |
| `contacto.html` | ✅ Exists | Contact |
| `contactos.html` | ✅ Exists | Contacts (duplicate?) |
| `preguntas-frecuentes.html` | ✅ Exists | FAQ |
| `ayuda.html` | ✅ Exists | Help |
| `documentacion.html` | ✅ Exists | Docs |
| `politica-privacidad.html` | ✅ Exists | Privacy |
| `terminos-condiciones.html` | ✅ Exists | Terms |
| `politica-cookies.html` | ✅ Exists | Cookies |

### ❌ Missing Critical Pages

| Page | Priority | Purpose |
|------|----------|---------|
| `/en/project-history.html` | 🔴 HIGH | View translation history |
| `/en/account-settings.html` | 🔴 HIGH | User settings |
| `/es/traducir.html` | 🔴 HIGH | Spanish translate tool |
| `/es/historial.html` | 🟡 MEDIUM | Spanish project history |
| `/es/configuracion.html` | 🟡 MEDIUM | Spanish settings |
| `/en/404.html` | 🟢 LOW | Error page |
| `/es/404.html` | 🟢 LOW | Error page (Spanish) |

**Total Existing:** 38 pages
**Total Missing:** 7 pages

---

## 🔘 BUTTONS & LINKS AUDIT

### 1. Navigation Header (All Pages)

**Current Navigation:**
```html
<!-- Logged OUT -->
<nav>
  <a href="/">Home</a>
  <a href="/en/features">Features</a>
  <a href="/en/pricing">Pricing</a>
  <a href="/en/about">About</a>
  <a href="/en/contact">Contact</a>
  <a href="/en/login">Sign In</a>
  <a href="/en/signup">Get Started</a>
</nav>

<!-- Logged IN -->
<nav>
  <a href="/en/dashboard">Dashboard</a>
  <a href="/en/translate">Translate</a>
  <a href="/en/help">Help</a>
  <button onclick="logout()">Sign Out</button>
</nav>
```

**Issues:**
- ❌ No async job list link in dashboard nav
- ❌ No account settings link
- ❌ Logout function may not clear localStorage
- ✅ Language switcher works

**Fixes Needed:**
```diff
+ <a href="/en/projects">Projects</a>  <!-- View all translation jobs -->
+ <a href="/en/account">Settings</a>
```

---

### 2. Landing Page (`/en/index.html`)

**CTAs Found:**
```html
<!-- Hero Section -->
<button onclick="location.href='/en/signup'">Start Free Trial</button>
<button onclick="location.href='/en/pricing'">View Pricing</button>

<!-- Features Section -->
<a href="/en/features">Learn More</a>

<!-- Pricing Preview -->
<a href="/en/pricing">See All Plans</a>

<!-- Footer CTAs -->
<a href="/en/signup">Get Started</a>
<a href="/en/contact">Contact Sales</a>
```

**Status:** ✅ All links work

---

### 3. Login Page (`/en/login.html`)

**Forms & Buttons:**
```html
<form id="login-form">
  <input type="email" name="email" required>
  <input type="password" name="password" required>
  <button type="submit">Sign In</button>
</form>

<a href="/en/forgot-password">Forgot Password?</a>
<a href="/en/signup">Create Account</a>
```

**JavaScript:**
```javascript
// Form submission
document.getElementById('login-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const response = await fetch('https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });

  const data = await response.json();
  localStorage.setItem('token', data.access_token);
  window.location.href = '/en/dashboard';
});
```

**Issues:**
- ❌ API endpoint may be incorrect (need to verify)
- ❌ No error handling for failed login
- ❌ No loading state on button
- ✅ Token storage works

**Fixes Needed:**
```diff
+ Show loading spinner during login
+ Display error message if login fails
+ Validate email format before submit
+ Add "Remember me" checkbox
```

---

### 4. Signup Page (`/en/signup.html`)

**Forms & Buttons:**
```html
<form id="signup-form">
  <input type="text" name="name" required>
  <input type="email" name="email" required>
  <input type="password" name="password" required>
  <button type="submit">Create Account</button>
</form>

<a href="/en/login">Already have an account?</a>
```

**API Call:**
```javascript
fetch('https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod/api/auth/signup', {
  method: 'POST',
  body: JSON.stringify({ name, email, password })
});
```

**Issues:**
- ❌ No password strength indicator
- ❌ No email verification
- ❌ No GDPR consent checkbox
- ❌ No terms acceptance checkbox

**Fixes Needed:**
```diff
+ Add password strength meter
+ Add checkbox: "I agree to Terms & Privacy Policy"
+ Add checkbox: "I want to receive marketing emails"
+ Show success message before redirect
+ Add email verification step
```

---

### 5. Dashboard Page (`/en/dashboard.html`)

**Current Features:**
```html
<!-- Welcome Section -->
<h1>Welcome, {{ user.name }}</h1>
<p>Your translation projects</p>

<!-- Stats Cards -->
<div class="stats">
  <div>Total Projects: {{ projects.length }}</div>
  <div>Words Translated: {{ totalWords }}</div>
  <div>Languages: {{ languageCount }}</div>
</div>

<!-- Recent Projects Table -->
<table>
  <tr>
    <th>URL</th>
    <th>Languages</th>
    <th>Status</th>
    <th>Date</th>
    <th>Actions</th>
  </tr>
  <!-- Loop projects -->
</table>

<!-- CTAs -->
<button onclick="location.href='/en/translate'">New Translation</button>
```

**Issues:**
- ❌ Only shows completed projects (no async jobs)
- ❌ No real-time status updates
- ❌ No progress bars for pending jobs
- ❌ No download button for completed translations
- ❌ No filter/search for projects

**Fixes Needed (CRITICAL):**
```diff
+ Add "Active Jobs" section showing async jobs
+ Add progress bars (0-100%) for processing jobs
+ Add auto-refresh every 3 seconds for active jobs
+ Add download button for completed jobs
+ Add filter: All | Processing | Completed | Failed
+ Add search box for URL/project name
```

---

### 6. Translate Page (`/en/translate.html`)

**Current Implementation (Synchronous):**
```html
<form id="translate-form">
  <label>Website URL</label>
  <input type="url" id="website-url" required>

  <label>Source Language</label>
  <select id="source-lang">
    <option value="en">English</option>
    <option value="es">Spanish</option>
    <!-- ... -->
  </select>

  <label>Target Language</label>
  <select id="target-lang">
    <option value="es">Spanish</option>
    <option value="en">English</option>
    <!-- ... -->
  </select>

  <button type="submit">Start Translation</button>
</form>

<div id="result" style="display:none;">
  <h3>Translation Complete!</h3>
  <button onclick="downloadZip()">Download Translated Site</button>
</div>
```

**JavaScript (OLD - Synchronous):**
```javascript
document.getElementById('translate-form').addEventListener('submit', async (e) => {
  e.preventDefault();

  const response = await fetch('/api/projects/crawl', {
    method: 'POST',
    body: JSON.stringify({ url, source_lang, target_lang })
  });

  const result = await response.json();

  // Show download button
  document.getElementById('result').style.display = 'block';
});
```

**🚨 CRITICAL ISSUE:** This page uses SYNC API (times out after 30s)

**Required Changes for Async:**
```javascript
// NEW: Submit job to async queue
async function submitTranslationJob() {
  const response = await fetch('/api/jobs/translate', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      url: document.getElementById('website-url').value,
      source_lang: document.getElementById('source-lang').value,
      target_lang: document.getElementById('target-lang').value
    })
  });

  const { job_id, poll_url } = await response.json();

  // Show progress UI
  showProgressUI(job_id);

  // Start polling
  pollJobStatus(job_id);
}

// Poll job status every 2 seconds
async function pollJobStatus(jobId) {
  const interval = setInterval(async () => {
    const response = await fetch(`/api/jobs/${jobId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    const job = await response.json();

    // Update progress bar
    updateProgressBar(job.progress);
    updateStatusMessage(job.message);

    if (job.status === 'completed') {
      clearInterval(interval);
      showDownloadButton(job.job_id);
    } else if (job.status === 'failed') {
      clearInterval(interval);
      showError(job.error_message);
    }
  }, 2000);  // Poll every 2 seconds
}
```

---

### 7. Pricing Page (`/en/pricing.html`)

**Pricing Tiers:**
```html
<!-- Starter Plan -->
<div class="pricing-card">
  <h3>Starter</h3>
  <p class="price">€499</p>
  <ul>
    <li>10 pages</li>
    <li>1 language</li>
    <li>Email support</li>
  </ul>
  <button onclick="selectPlan('starter')">Choose Plan</button>
</div>

<!-- Professional Plan -->
<div class="pricing-card">
  <h3>Professional</h3>
  <p class="price">€1,299</p>
  <button onclick="selectPlan('professional')">Choose Plan</button>
</div>

<!-- Business Plan -->
<div class="pricing-card">
  <h3>Business</h3>
  <p class="price">€2,499</p>
  <button onclick="selectPlan('business')">Choose Plan</button>
</div>

<!-- Enterprise Plan -->
<div class="pricing-card">
  <h3>Enterprise</h3>
  <p class="price">€3,500</p>
  <button onclick="selectPlan('enterprise')">Contact Sales</button>
</div>
```

**JavaScript:**
```javascript
function selectPlan(plan) {
  // Store selected plan
  localStorage.setItem('selected_plan', plan);

  // Redirect to checkout
  window.location.href = `/en/checkout?plan=${plan}`;
}
```

**Issues:**
- ✅ Plan selection works
- ❌ No country-specific pricing yet (will add in multi-country phase)
- ❌ No currency selector yet
- ❌ No installment options shown

**Fixes Needed (Later - Multi-Country Phase):**
```diff
+ Add currency selector (USD, EUR, GBP, etc.)
+ Add "or pay in installments" for Tier 2
+ Show local payment methods
```

---

### 8. Checkout Page (`/en/checkout.html`)

**Features:**
```html
<h1>Checkout</h1>

<!-- Plan Summary -->
<div class="order-summary">
  <h3>Order Summary</h3>
  <p>Plan: <span id="plan-name">Professional</span></p>
  <p>Price: <span id="plan-price">€1,299</span></p>
</div>

<!-- Payment Button -->
<button onclick="createCheckoutSession()">
  Proceed to Payment
</button>
```

**JavaScript:**
```javascript
async function createCheckoutSession() {
  const plan = localStorage.getItem('selected_plan');

  const response = await fetch('/api/payments/create-checkout-session', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ plan })
  });

  const { session_id, url } = await response.json();

  // Redirect to Stripe Checkout
  window.location.href = url;
}
```

**Issues:**
- ✅ Stripe integration works
- ❌ No tax calculation
- ❌ No VAT handling (EU requirement)
- ❌ No multi-gateway support yet (Mercado Pago)

**Fixes Needed (Later):**
```diff
+ Add VAT calculation for EU
+ Add tax ID field for businesses
+ Add Mercado Pago option (Tier 2)
```

---

## 🔧 CRITICAL FIXES REQUIRED (Before Multi-Country)

### Priority 1: Async Translation Flow

**File:** `frontend/public/en/translate.html`

**Changes:**
1. Replace `/api/projects/crawl` with `/api/jobs/translate`
2. Add progress UI with polling
3. Add status messages
4. Add download button when complete

**Estimated Time:** 2 hours

---

### Priority 2: Dashboard - Show Async Jobs

**File:** `frontend/public/en/dashboard.html`

**Changes:**
1. Fetch jobs from `/api/jobs`
2. Show progress bars for active jobs
3. Auto-refresh every 3 seconds
4. Add filters (All | Processing | Completed | Failed)

**Estimated Time:** 3 hours

---

### Priority 3: Missing Pages

**Files to Create:**
1. `/en/projects.html` - Full project/job list
2. `/en/account-settings.html` - User settings
3. `/es/traducir.html` - Spanish translate page

**Estimated Time:** 4 hours

---

### Priority 4: Error Handling & UX

**All Pages:**
1. Add loading spinners to all buttons
2. Add error messages for failed API calls
3. Add success messages
4. Add form validation

**Estimated Time:** 3 hours

---

## 📋 FRONTEND FIX CHECKLIST

### Phase 1: Core Functionality (Week 1)

- [ ] **Update translate.html to use async API**
  - [ ] Change endpoint to `/api/jobs/translate`
  - [ ] Add progress bar UI
  - [ ] Add status polling (every 2s)
  - [ ] Add download button on completion
  - [ ] Add error handling

- [ ] **Update dashboard.html for async jobs**
  - [ ] Fetch from `/api/jobs` instead of `/api/projects`
  - [ ] Show progress bars (0-100%)
  - [ ] Add auto-refresh every 3s
  - [ ] Add job status badges
  - [ ] Add download buttons

- [ ] **Fix authentication flow**
  - [ ] Add loading states to login/signup
  - [ ] Add error messages
  - [ ] Add email validation
  - [ ] Add password strength meter
  - [ ] Add GDPR checkboxes to signup

- [ ] **Create missing pages**
  - [ ] `/en/projects.html` - Job history
  - [ ] `/en/account-settings.html` - User settings
  - [ ] `/es/traducir.html` - Spanish translate
  - [ ] `/en/404.html` - Error page

### Phase 2: Polish & Testing (Week 1-2)

- [ ] **Add loading spinners**
  - [ ] All form submit buttons
  - [ ] All navigation links
  - [ ] API call indicators

- [ ] **Add error handling**
  - [ ] Network errors
  - [ ] API errors (4xx, 5xx)
  - [ ] Validation errors
  - [ ] Timeout handling

- [ ] **Add success messages**
  - [ ] Login success
  - [ ] Signup success
  - [ ] Translation started
  - [ ] Download ready

- [ ] **Test complete user flow**
  - [ ] Signup → Email verification → Login
  - [ ] Login → Dashboard → Translate → Download
  - [ ] Select plan → Checkout → Payment → Success
  - [ ] Forgot password → Reset → Login

### Phase 3: Multi-Country (Week 2-3)

- [ ] **Implement geo-detection**
  - [ ] CloudFront Function for country detection
  - [ ] Redirect to `/tier1/{locale}` or `/tier2/{locale}`
  - [ ] Set market cookie

- [ ] **Create 36 landing pages**
  - [ ] 18 Tier 1 pages
  - [ ] 18 Tier 2 pages

- [ ] **Add pricing engine**
  - [ ] Currency conversion
  - [ ] Country-specific pricing
  - [ ] Payment method selection

---

## 🧪 TESTING PLAN

### Manual Testing Checklist

**User Flow 1: New User Signup → First Translation**
1. [ ] Visit `/en/` (landing page)
2. [ ] Click "Get Started" → `/en/signup`
3. [ ] Fill form, submit
4. [ ] Verify redirect to `/en/dashboard`
5. [ ] Click "New Translation" → `/en/translate`
6. [ ] Enter URL: `https://example.com`
7. [ ] Select languages: EN → ES
8. [ ] Click "Start Translation"
9. [ ] Verify job submitted (shows job_id)
10. [ ] Wait for progress bar to update
11. [ ] Verify status changes: pending → processing → completed
12. [ ] Click "Download" button
13. [ ] Verify ZIP file downloads

**User Flow 2: Returning User Login**
1. [ ] Visit `/en/login`
2. [ ] Enter credentials
3. [ ] Submit form
4. [ ] Verify redirect to `/en/dashboard`
5. [ ] Verify translation history shows
6. [ ] Verify completed jobs have download buttons

**User Flow 3: Payment Flow**
1. [ ] Visit `/en/pricing`
2. [ ] Click "Choose Plan" (Professional)
3. [ ] Verify redirect to `/en/checkout`
4. [ ] Verify plan details correct
5. [ ] Click "Proceed to Payment"
6. [ ] Verify redirect to Stripe
7. [ ] Complete test payment
8. [ ] Verify redirect to `/en/checkout-success`
9. [ ] Verify account upgraded

**User Flow 4: Error Handling**
1. [ ] Try to translate with invalid URL
2. [ ] Verify error message shows
3. [ ] Try to login with wrong password
4. [ ] Verify error message shows
5. [ ] Simulate network error
6. [ ] Verify graceful error handling

---

## 📊 ESTIMATED EFFORT

| Task | Hours | Priority |
|------|-------|----------|
| Update translate.html (async) | 2 | 🔴 CRITICAL |
| Update dashboard.html (jobs) | 3 | 🔴 CRITICAL |
| Create missing pages (3 pages) | 4 | 🔴 CRITICAL |
| Add loading/error states | 3 | 🟡 HIGH |
| Fix authentication UX | 2 | 🟡 HIGH |
| Add GDPR compliance | 2 | 🟡 HIGH |
| Testing & QA | 4 | 🟡 HIGH |
| **TOTAL** | **20 hours** | **~3 days** |

---

## 🎯 SUCCESS CRITERIA

**Before moving to Multi-Country:**
- ✅ User can signup and login
- ✅ User can submit async translation job
- ✅ User sees real-time progress (0-100%)
- ✅ User can download completed translation
- ✅ Dashboard shows all jobs with status
- ✅ All critical pages exist and work
- ✅ No console errors
- ✅ All forms have validation
- ✅ All buttons have loading states
- ✅ All API calls have error handling

**Then proceed to:**
- 🆕 Geo-detection implementation
- 🆕 36 localized landing pages
- 🆕 Multi-currency pricing
- 🆕 Multi-gateway payments

---

**Next Action:** Start with Priority 1 - Update translate.html for async API

---

**Author:** TranslateCloud Team
**Status:** Ready for Implementation
**Timeline:** 3 days before Multi-Country
