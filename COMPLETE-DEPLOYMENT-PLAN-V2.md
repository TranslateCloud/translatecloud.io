# TranslateCloud - Complete Deployment Plan V2

**Version:** 2.0
**Date:** 2025-10-20
**Status:** Ready for Implementation

---

## 🎯 Business Model: Dual-Tier Pricing

### Tier 1: Premium SEO Markets
**Target:** Enterprise customers in high-GDP countries
**Value Proposition:** "Maintain your SEO rankings while going global"
**Pricing:** €499 - €3,500
**Markets:** USA, UK, Canada, Australia, Germany, France, Netherlands, Belgium
**Currency:** EUR (display in local currency with real-time conversion)
**Payment:** Stripe (cards, bank transfers)
**Messaging:** Premium, enterprise-focused, SEO preservation

### Tier 2: Growth/Accessible Markets
**Target:** SMBs, startups, individual developers
**Value Proposition:** "Democratizing website translation for everyone"
**Pricing:** $199 - $1,499 (with installments: 3, 6, 9, 12 months)
**Markets:** Mexico, Colombia, Argentina, Chile, Peru, Spain (PYMEs), Brazil, Philippines, Indonesia, Vietnam
**Currency:** USD (display in local currency)
**Payment:** Stripe + Mercado Pago + local methods (OXXO, PIX, PSE, etc.)
**Messaging:** Affordable, accessible, growth-focused

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND (Multi-Tier)                        │
├─────────────────────────────────────────────────────────────────┤
│  CloudFront CDN                                                  │
│    ↓                                                             │
│  S3 Static Hosting (18 localized landing pages)                 │
│    - /tier1/en-us  - /tier2/es-mx                              │
│    - /tier1/en-gb  - /tier2/pt-br                              │
│    - /tier1/de     - /tier2/es-es                              │
│    - ... (18 total)                                            │
│                                                                  │
│  Geo-Detection: CloudFront Function (edge computing)            │
│    → Detects country via CloudFront-Viewer-Country header       │
│    → Redirects to appropriate tier landing page                 │
│    → Sets currency and payment options                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                BACKEND API (Translation Engine)                  │
├─────────────────────────────────────────────────────────────────┤
│  API Gateway (eu-west-1)                                        │
│    ↓                                                             │
│  Lambda API Handler (translatecloud-api)                        │
│    - /api/jobs/translate → Creates job, sends to SQS           │
│    - /api/jobs/{id} → Returns job status from DynamoDB         │
│    - /api/payments/create-session → Stripe/Mercado Pago        │
│    - /api/auth/* → User authentication                          │
│                                                                  │
│  SQS Queue (translatecloud-translation-queue)                   │
│    ↓                                                             │
│  Lambda Worker (translatecloud-translation-worker)              │
│    - Processes translation jobs (up to 15 min)                  │
│    - Updates DynamoDB with progress                             │
│    - Uploads results to S3                                      │
│                                                                  │
│  DynamoDB (translation-jobs)                                    │
│    - job_id, status, progress, pages_translated                 │
│    - Real-time status tracking                                  │
│    - Auto-delete after 7 days (TTL)                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   PAYMENT PROCESSING                             │
├─────────────────────────────────────────────────────────────────┤
│  Tier 1: Stripe Checkout                                        │
│    - Cards (Visa, Mastercard, Amex)                            │
│    - Bank transfers (SEPA for EU)                              │
│    - One-time payments only                                     │
│                                                                  │
│  Tier 2: Multi-Gateway                                          │
│    Stripe:                                                       │
│      - Cards                                                     │
│      - Installments (3, 6, 9, 12 months)                        │
│    Mercado Pago (LATAM):                                        │
│      - OXXO (Mexico cash)                                        │
│      - PIX (Brazil instant)                                      │
│      - PSE (Colombia bank)                                       │
│      - Local cards with installments                            │
│                                                                  │
│  Webhook Processing:                                             │
│    - /api/payments/webhook/stripe                               │
│    - /api/payments/webhook/mercadopago                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      DATA STORAGE                                │
├─────────────────────────────────────────────────────────────────┤
│  PostgreSQL (RDS)         - Users, projects, subscriptions      │
│  DynamoDB                 - Translation jobs (async tracking)   │
│  S3 Buckets:                                                     │
│    - translatecloud-translations-prod  (results)                │
│    - translatecloud-uploads-prod       (user uploads)           │
│    - translatecloud-web-projects       (archived sites)         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 Phase 1: Core Infrastructure (Week 1)

### Day 1: Async Translation System ✅
**Status:** 80% Complete (worker Lambda pending)

- [x] DynamoDB table created
- [x] SQS queue created
- [x] Job API endpoints implemented
- [x] Job schemas defined
- [ ] Worker Lambda function
- [ ] IAM permissions
- [ ] End-to-end testing

**Deliverables:**
- Translation jobs process async (no 30s timeout)
- Real-time progress tracking
- Support for 100+ page websites

---

### Day 2-3: Dual-Tier Pricing Frontend

#### 2.1 Geo-Detection (CloudFront Function)
**File:** `cloudfront-functions/geo-redirect.js`

```javascript
function handler(event) {
  var request = event.request;
  var headers = event.request.headers;

  // Get country from CloudFront
  var country = headers['cloudfront-viewer-country']
    ? headers['cloudfront-viewer-country'].value
    : 'US';

  // Tier 1 countries
  var tier1 = ['US', 'GB', 'CA', 'AU', 'DE', 'FR', 'NL', 'BE'];

  // Map country to landing page
  var countryMap = {
    'US': '/tier1/en-us',
    'GB': '/tier1/en-gb',
    'CA': '/tier1/en-ca',
    'AU': '/tier1/en-au',
    'DE': '/tier1/de',
    'FR': '/tier1/fr',
    'MX': '/tier2/es-mx',
    'CO': '/tier2/es-co',
    'AR': '/tier2/es-ar',
    'CL': '/tier2/es-cl',
    'PE': '/tier2/es-pe',
    'ES': '/tier2/es-es',
    'BR': '/tier2/pt-br',
    'PH': '/tier2/en-ph',
    'ID': '/tier2/id',
    'VN': '/tier2/vi'
  };

  // Redirect to appropriate landing page
  if (request.uri === '/' || request.uri === '/index.html') {
    var targetPage = countryMap[country] || '/tier1/en-us';
    return {
      statusCode: 302,
      statusDescription: 'Found',
      headers: {
        'location': { value: targetPage }
      }
    };
  }

  return request;
}
```

#### 2.2 Landing Page Structure
```
frontend/public/
├── index.html (geo-redirect splash)
├── tier1/
│   ├── en-us/
│   │   ├── index.html
│   │   ├── pricing.html
│   │   ├── features.html
│   │   └── case-studies.html
│   ├── en-gb/
│   ├── en-ca/
│   ├── en-au/
│   ├── de/
│   └── fr/
└── tier2/
    ├── es-mx/
    ├── es-co/
    ├── es-ar/
    ├── es-cl/
    ├── es-pe/
    ├── es-es/
    ├── pt-br/
    ├── en-ph/
    ├── id/
    └── vi/
```

#### 2.3 Pricing Configuration
**File:** `frontend/config/pricing.json`

```json
{
  "tier1": {
    "base_currency": "EUR",
    "plans": {
      "starter": {
        "name": "Professional",
        "price_eur": 499,
        "pages": 10,
        "languages": 1,
        "support": "Email"
      },
      "business": {
        "name": "Enterprise",
        "price_eur": 1499,
        "pages": 50,
        "languages": 5,
        "support": "Priority"
      },
      "premium": {
        "name": "Custom",
        "price_eur": 3500,
        "pages": "Unlimited",
        "languages": "Unlimited",
        "support": "Dedicated"
      }
    }
  },
  "tier2": {
    "base_currency": "USD",
    "plans": {
      "starter": {
        "name": "Básico",
        "price_usd": 199,
        "installments": [3, 6],
        "pages": 10,
        "languages": 1
      },
      "business": {
        "name": "Crecimiento",
        "price_usd": 699,
        "installments": [3, 6, 9, 12],
        "pages": 50,
        "languages": 3
      },
      "premium": {
        "name": "Premium",
        "price_usd": 1499,
        "installments": [6, 12],
        "pages": 100,
        "languages": 10
      }
    }
  },
  "currency_multipliers": {
    "USD": 1.0,
    "EUR": 0.92,
    "GBP": 0.79,
    "CAD": 1.36,
    "AUD": 1.53,
    "MXN": 17.2,
    "COP": 3900,
    "ARS": 350,
    "CLP": 900,
    "PEN": 3.7,
    "BRL": 5.0,
    "PHP": 56,
    "IDR": 15600,
    "VND": 24500
  }
}
```

#### 2.4 Currency Conversion Utility
**File:** `frontend/utils/pricing.js`

```javascript
/**
 * Convert base price to target currency
 */
function convertPrice(basePrice, baseCurrency, targetCurrency, multipliers) {
  if (baseCurrency === targetCurrency) return basePrice;

  // Convert to USD first (universal base)
  let priceInUSD = basePrice;
  if (baseCurrency === 'EUR') {
    priceInUSD = basePrice / multipliers.EUR;
  }

  // Convert to target currency
  return Math.round(priceInUSD * multipliers[targetCurrency]);
}

/**
 * Format price with currency symbol
 */
function formatPrice(price, currency) {
  const symbols = {
    'USD': '$', 'EUR': '€', 'GBP': '£', 'MXN': '$',
    'COP': '$', 'ARS': '$', 'CLP': '$', 'BRL': 'R$'
  };

  const locale = {
    'USD': 'en-US', 'EUR': 'de-DE', 'GBP': 'en-GB',
    'MXN': 'es-MX', 'BRL': 'pt-BR'
  }[currency] || 'en-US';

  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(price);
}
```

---

### Day 4-5: Payment Integration

#### 4.1 Backend Payment Routes
**File:** `backend/src/api/routes/payments.py`

```python
@router.post("/create-checkout-session")
async def create_checkout_session(
    plan: str,
    tier: int,
    currency: str,
    installments: Optional[int] = None,
    user_id: str = Depends(get_current_user_id)
):
    """
    Create Stripe or Mercado Pago checkout session

    Tier 1: Stripe only, no installments
    Tier 2: Stripe or Mercado Pago, with installments
    """
    # Get pricing from config
    config = get_pricing_config()

    if tier == 1:
        # Tier 1: Stripe Checkout
        stripe.api_key = settings.STRIPE_SECRET_KEY

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': currency.lower(),
                    'product_data': {'name': f'TranslateCloud {plan}'},
                    'unit_amount': get_price_in_cents(plan, tier, currency)
                },
                'quantity': 1
            }],
            mode='payment',
            success_url=f'{settings.FRONTEND_URL}/success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'{settings.FRONTEND_URL}/pricing',
            metadata={'user_id': user_id, 'plan': plan, 'tier': tier}
        )

        return {'session_id': session.id, 'url': session.url}

    else:
        # Tier 2: Choose gateway based on country
        if currency in ['MXN', 'COP', 'ARS', 'CLP', 'BRL']:
            # Use Mercado Pago for LATAM
            return create_mercadopago_session(plan, currency, installments, user_id)
        else:
            # Use Stripe with installments
            return create_stripe_installment_session(plan, currency, installments, user_id)
```

#### 4.2 Mercado Pago Integration
**File:** `backend/src/core/mercadopago_service.py`

```python
import mercadopago

def create_mercadopago_session(plan, currency, installments, user_id):
    """Create Mercado Pago preference with installments and local methods"""
    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

    preference_data = {
        "items": [{
            "title": f"TranslateCloud {plan}",
            "quantity": 1,
            "unit_price": get_price_in_currency(plan, currency)
        }],
        "payer": {"email": get_user_email(user_id)},
        "back_urls": {
            "success": f"{settings.FRONTEND_URL}/success",
            "failure": f"{settings.FRONTEND_URL}/failure",
            "pending": f"{settings.FRONTEND_URL}/pending"
        },
        "auto_return": "approved",
        "payment_methods": {
            "installments": installments if installments else 1,
            "excluded_payment_types": [],  # Accept all (OXXO, PIX, cards, etc.)
        },
        "metadata": {
            "user_id": user_id,
            "plan": plan,
            "tier": 2
        }
    }

    preference_response = sdk.preference().create(preference_data)
    preference = preference_response["response"]

    return {
        "preference_id": preference["id"],
        "init_point": preference["init_point"]  # Redirect URL
    }
```

---

## 📊 Phase 2: Analytics & Tracking (Week 2)

### 2.1 Enhanced Analytics Schema
**PostgreSQL Tables:**

```sql
-- Track conversions by market
CREATE TABLE market_analytics (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    country VARCHAR(2) NOT NULL,
    tier INTEGER NOT NULL,
    page_views INTEGER DEFAULT 0,
    signups INTEGER DEFAULT 0,
    checkouts_started INTEGER DEFAULT 0,
    payments_completed INTEGER DEFAULT 0,
    revenue_usd DECIMAL(10,2) DEFAULT 0,
    currency VARCHAR(3),
    payment_method VARCHAR(50)
);

-- Track pricing experiments
CREATE TABLE ab_tests (
    id SERIAL PRIMARY KEY,
    country VARCHAR(2),
    tier INTEGER,
    variant VARCHAR(20),  -- 'control', 'test_a', 'test_b'
    conversions INTEGER,
    revenue_usd DECIMAL(10,2)
);
```

### 2.2 Frontend Analytics Tracking
**File:** `frontend/utils/analytics.js`

```javascript
// Track page view with tier and country
function trackPageView(tier, country, page) {
  // Google Analytics 4
  gtag('event', 'page_view', {
    tier: tier,
    country: country,
    page_path: page
  });

  // Custom backend tracking
  fetch('/api/analytics/track', {
    method: 'POST',
    body: JSON.stringify({
      event: 'page_view',
      tier: tier,
      country: country,
      timestamp: new Date().toISOString()
    })
  });
}

// Track pricing tier shown
function trackPricingView(tier, currency, plan) {
  gtag('event', 'view_pricing', {
    tier: tier,
    currency: currency,
    plan: plan
  });
}

// Track checkout initiated
function trackCheckoutStart(tier, plan, price, currency) {
  gtag('event', 'begin_checkout', {
    tier: tier,
    value: price,
    currency: currency,
    items: [{item_name: plan}]
  });
}
```

---

## 🚀 Phase 3: Deployment Steps

### Step 1: Update Backend (Lambda)
```bash
# Add new dependencies
cd backend
pip install mercadopago boto3

# Update requirements.txt
echo "mercadopago==2.2.0" >> requirements.txt
echo "boto3==1.28.0" >> requirements.txt

# Deploy to Lambda
./scripts/deploy-lambda.ps1
```

### Step 2: Create DynamoDB Tables
```bash
# Already done: translation-jobs ✅

# Create pricing config table (optional, can use JSON file)
aws dynamodb create-table \
  --table-name pricing-config \
  --attribute-definitions AttributeName=tier,AttributeType=N \
  --key-schema AttributeName=tier,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region eu-west-1
```

### Step 3: Deploy Frontend (18 Landing Pages)
```bash
# Build all landing pages
cd frontend
npm run build

# Sync to S3
aws s3 sync public/ s3://translatecloud-frontend-prod/ --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id d3sa5i2s0uyozh \
  --paths "/*"
```

### Step 4: Configure CloudFront Function
```bash
# Create geo-redirect function
aws cloudfront create-function \
  --name translatecloud-geo-redirect \
  --function-config Comment="Redirect users to tier-appropriate landing page",Runtime=cloudfront-js-1.0 \
  --function-code fileb://cloudfront-functions/geo-redirect.js

# Associate with distribution (viewer-request event)
aws cloudfront update-distribution \
  --id d3sa5i2s0uyozh \
  --function-associations ...
```

### Step 5: Configure Payment Gateways

#### Stripe Setup
```bash
# Set Stripe keys in Lambda environment
aws lambda update-function-configuration \
  --function-name translatecloud-api \
  --environment Variables="{
    STRIPE_PUBLISHABLE_KEY=pk_live_...,
    STRIPE_SECRET_KEY=sk_live_...,
    STRIPE_WEBHOOK_SECRET=whsec_...
  }"

# Create webhook endpoint in Stripe dashboard
# URL: https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod/api/payments/webhook/stripe
# Events: checkout.session.completed, payment_intent.succeeded
```

#### Mercado Pago Setup
```bash
# Set Mercado Pago keys
aws lambda update-function-configuration \
  --function-name translatecloud-api \
  --environment Variables="{
    MERCADOPAGO_ACCESS_TOKEN=APP_USR-...,
    MERCADOPAGO_PUBLIC_KEY=APP_USR-...
  }"

# Create webhook in Mercado Pago dashboard
# URL: https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod/api/payments/webhook/mercadopago
```

---

## 💰 Cost Estimate (Updated)

### Monthly Costs (Both Tiers Active)

| Service | Tier 1 | Tier 2 | Total |
|---------|--------|--------|-------|
| **Compute** |
| Lambda API | €3 | €3 | €6 |
| Lambda Worker | €5 | €5 | €10 |
| **Storage** |
| RDS PostgreSQL | €15 | - | €15 |
| DynamoDB | €1 | €1 | €2 |
| S3 | €5 | €5 | €10 |
| **Network** |
| CloudFront | €10 | €10 | €20 |
| API Gateway | €3 | €3 | €6 |
| **Other** |
| SQS | €0.01 | €0.01 | €0.02 |
| Route53 | €0.50 | - | €0.50 |
| Secrets Manager | €0.40 | - | €0.40 |
| **Payment Fees** |
| Stripe (2.9% + €0.30) | Variable | Variable | ~€50/month |
| Mercado Pago (3.5%) | - | Variable | ~€30/month |
| **TOTAL** | | | **€150/month** |

**Revenue Target (Month 1):**
- Tier 1: 10 customers × €1,000 avg = €10,000
- Tier 2: 50 customers × $400 avg = €18,400
- **Total:** €28,400/month

**Profit Margin:** 99.5% (€28,250 profit)

---

## 🎯 Success Metrics

### Week 1
- [ ] Async translation working (no timeouts)
- [ ] Can translate 100+ page websites
- [ ] Real-time progress tracking functional

### Week 2
- [ ] 18 landing pages deployed
- [ ] Geo-detection working correctly
- [ ] Both payment gateways tested

### Week 3
- [ ] Analytics tracking all tiers
- [ ] A/B testing framework ready
- [ ] First customers in both tiers

### Month 1 Goals
- Tier 1: 10 customers (€10,000 revenue)
- Tier 2: 50 customers ($20,000 revenue)
- 90% payment success rate
- 95% uptime SLA

---

## 🔄 Next Actions (Priority Order)

### Immediate (This Week)
1. ✅ Finish async Lambda worker
2. ✅ Update IAM permissions (SQS, DynamoDB)
3. ✅ Deploy and test async flow
4. 🆕 Build Tier 1 landing pages (6 countries)
5. 🆕 Build Tier 2 landing pages (10 countries)
6. 🆕 Implement geo-detection (CloudFront Function)

### Next Week
7. 🆕 Integrate Stripe checkout (Tier 1)
8. 🆕 Integrate Mercado Pago (Tier 2)
9. 🆕 Create pricing configuration system
10. 🆕 Deploy analytics tracking

### Week 3-4
11. Create legal pages (18 versions: Privacy, Terms)
12. Implement cookie consent (GDPR)
13. A/B test pricing variations
14. Launch marketing campaigns (both tiers)

---

**Author:** TranslateCloud Team
**Last Updated:** 2025-10-20
**Status:** Ready for Implementation ✅
