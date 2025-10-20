# TranslateCloud - Multi-Country Implementation Plan

**Version:** 1.0
**Date:** 2025-10-20
**Markets:** 35+ countries across 2 tiers
**Languages:** 18 landing page variations

---

## 🌍 Market Strategy Overview

### Tier 1: Premium SEO Markets (18 countries)
**Target:** Enterprise & established businesses
**Pricing:** €499 - €3,500
**Messaging:** SEO preservation, ownership, professional quality
**Payment:** Stripe (cards, bank transfers)
**Countries:** US, GB, CA, AU, DE, FR, NL, SE, NO, DK, FI, CH, AT, BE, IE, NZ, SG, JP

### Tier 2: Growth/Accessible Markets (18 countries)
**Target:** SMBs, startups, freelancers, PYMEs
**Pricing:** $199 - $1,499 (with installments)
**Messaging:** Democratization, affordability, global reach
**Payment:** Stripe + Mercado Pago + local methods
**Countries:** MX, CO, AR, CL, PE, BR, ES, PH, ID, VN, IN, PL, RO, HU, CZ, PT, GR, TR

---

## 📋 PHASE 1: Technical Foundation (Week 1)

### 1.1 Geo-Detection System

**Implementation:** CloudFront Function (edge computing)

```javascript
// /cloudfront-functions/geo-detect.js
function handler(event) {
  const request = event.request;
  const country = request.headers['cloudfront-viewer-country']?.value || 'US';

  const tierMapping = {
    tier1: ['US', 'GB', 'CA', 'AU', 'DE', 'FR', 'NL', 'SE', 'NO',
            'DK', 'FI', 'CH', 'AT', 'BE', 'IE', 'NZ', 'SG', 'JP'],
    tier2: ['MX', 'CO', 'AR', 'CL', 'PE', 'BR', 'ES', 'PH', 'ID',
            'VN', 'IN', 'PL', 'RO', 'HU', 'CZ', 'PT', 'GR', 'TR']
  };

  const tier = tierMapping.tier1.includes(country) ? 'tier1' : 'tier2';
  const locale = getLocale(country); // e.g., 'en-us', 'es-mx', 'pt-br'

  if (request.uri === '/') {
    return {
      statusCode: 302,
      headers: {
        'location': { value: `/${tier}/${locale}` },
        'set-cookie': { value: `tc_market=${country}; Path=/; Max-Age=31536000` }
      }
    };
  }

  return request;
}
```

**Checklist:**
- [ ] Deploy CloudFront Function to distribution
- [ ] Test geo-detection from 10+ countries (VPN)
- [ ] Add manual country selector (dropdown)
- [ ] Set cookie to remember user preference
- [ ] Handle edge cases (VPN users, privacy-focused browsers)

---

### 1.2 Pricing Engine

**Configuration File:** `/frontend/config/markets.json`

```json
{
  "markets": {
    "US": {
      "tier": 1,
      "currency": "USD",
      "locale": "en-US",
      "multiplier": 1.1,
      "payment_methods": ["stripe"],
      "installments": false,
      "whatsapp": null
    },
    "MX": {
      "tier": 2,
      "currency": "MXN",
      "locale": "es-MX",
      "multiplier": 20,
      "payment_methods": ["stripe", "mercadopago"],
      "installments": [3, 6, 9, 12],
      "whatsapp": "+52-xxx-xxx-xxxx"
    },
    "BR": {
      "tier": 2,
      "currency": "BRL",
      "locale": "pt-BR",
      "multiplier": 5.5,
      "payment_methods": ["stripe", "mercadopago"],
      "local_methods": ["pix", "boleto"],
      "installments": [3, 6, 10, 12],
      "whatsapp": "+55-xxx-xxx-xxxx"
    }
    // ... all 35+ countries
  },
  "base_prices": {
    "tier1": {
      "starter": 499,
      "professional": 1299,
      "business": 2499,
      "enterprise": 3500
    },
    "tier2": {
      "emprendedor": 199,
      "negocio": 499,
      "crecimiento": 899,
      "agencia": 1499
    }
  }
}
```

**Pricing Utility:** `/frontend/utils/pricing.js`

```javascript
function calculatePrice(plan, country) {
  const market = markets[country];
  const tier = `tier${market.tier}`;
  const basePrice = basePrices[tier][plan];

  return {
    amount: Math.round(basePrice * market.multiplier),
    currency: market.currency,
    formatted: new Intl.NumberFormat(market.locale, {
      style: 'currency',
      currency: market.currency,
      minimumFractionDigits: 0
    }).format(basePrice * market.multiplier)
  };
}

// Example usage:
// calculatePrice('emprendedor', 'MX')
// => { amount: 3980, currency: 'MXN', formatted: '$3,980' }
```

**Checklist:**
- [ ] Create markets.json with all 35+ countries
- [ ] Implement pricing calculation function
- [ ] Add currency symbol mapping
- [ ] Test pricing display for all markets
- [ ] Update volatile currencies weekly (ARS, VND, IDR)
- [ ] Add currency selector UI component

---

### 1.3 Payment Integration

#### Stripe Setup (All markets)
```bash
# Enable multi-currency in Stripe dashboard
# Currencies: USD, EUR, GBP, CAD, AUD, MXN, BRL, COP, ARS, CLP, PEN, etc.

# API Configuration
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

**Endpoint:** `/api/payments/create-checkout`

```python
@router.post("/create-checkout")
async def create_checkout(
    plan: str,
    country: str,
    installments: Optional[int] = None
):
    market = get_market_config(country)
    price = calculate_price(plan, country)

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': price['currency'].lower(),
                'product_data': {'name': f'TranslateCloud {plan}'},
                'unit_amount': price['amount'] * 100  # cents
            },
            'quantity': 1
        }],
        mode='payment',
        success_url=f'{FRONTEND_URL}/success?session_id={{CHECKOUT_SESSION_ID}}',
        cancel_url=f'{FRONTEND_URL}/pricing',
        metadata={'country': country, 'tier': market['tier']}
    )

    if market.get('installments') and installments:
        session.payment_intent_data = {
            'installments': {'enabled': True}
        }

    return {'session_id': session.id, 'url': session.url}
```

#### Mercado Pago Setup (LATAM only)
```bash
# Countries: MX, BR, AR, CL, CO, PE
MERCADOPAGO_ACCESS_TOKEN_MX=APP_USR-...
MERCADOPAGO_ACCESS_TOKEN_BR=APP_USR-...
# ... one token per country
```

**Local Payment Methods:**
- **Mexico:** OXXO (cash), cards with installments
- **Brazil:** PIX (instant), Boleto (bank slip), cards
- **Colombia:** PSE (bank transfer), cards
- **Chile:** Webpay, cards
- **Peru:** Niubiz, cards
- **Philippines:** GCash
- **Indonesia:** GoPay
- **Vietnam:** Momo

**Checklist:**
- [ ] Set up Stripe with multi-currency
- [ ] Enable installments for Tier 2
- [ ] Set up Mercado Pago accounts (6 countries)
- [ ] Integrate local payment methods (8 methods)
- [ ] Configure webhooks for each gateway
- [ ] Test payment flow for each country
- [ ] Create invoicing in local currencies

---

## 📝 PHASE 2: Content Creation (Week 2-3)

### 2.1 Landing Page Structure

```
frontend/public/
├── tier1/
│   ├── en-us/     (🇺🇸 United States)
│   ├── en-gb/     (🇬🇧 United Kingdom)
│   ├── en-ca/     (🇨🇦 Canada English)
│   ├── fr-ca/     (🇨🇦 Canada French)
│   ├── en-au/     (🇦🇺 Australia)
│   ├── de/        (🇩🇪 Germany)
│   ├── fr/        (🇫🇷 France)
│   ├── nl/        (🇳🇱 Netherlands)
│   ├── sv/        (🇸🇪 Sweden)
│   ├── no/        (🇳🇴 Norway)
│   ├── da/        (🇩🇰 Denmark)
│   ├── fi/        (🇫🇮 Finland)
│   ├── de-ch/     (🇨🇭 Switzerland)
│   ├── de-at/     (🇦🇹 Austria)
│   ├── nl-be/     (🇧🇪 Belgium)
│   ├── en-ie/     (🇮🇪 Ireland)
│   ├── en-nz/     (🇳🇿 New Zealand)
│   └── ja/        (🇯🇵 Japan)
└── tier2/
    ├── es-mx/     (🇲🇽 Mexico)
    ├── es-co/     (🇨🇴 Colombia)
    ├── es-ar/     (🇦🇷 Argentina)
    ├── es-cl/     (🇨🇱 Chile)
    ├── es-pe/     (🇵🇪 Peru)
    ├── pt-br/     (🇧🇷 Brazil)
    ├── es-es/     (🇪🇸 Spain)
    ├── en-ph/     (🇵🇭 Philippines)
    ├── id/        (🇮🇩 Indonesia)
    ├── vi/        (🇻🇳 Vietnam)
    ├── hi/        (🇮🇳 India)
    ├── pl/        (🇵🇱 Poland)
    ├── ro/        (🇷🇴 Romania)
    ├── hu/        (🇭🇺 Hungary)
    ├── cs/        (🇨🇿 Czech Republic)
    ├── pt/        (🇵🇹 Portugal)
    ├── el/        (🇬🇷 Greece)
    └── tr/        (🇹🇷 Turkey)
```

### 2.2 Content Templates

Each landing page needs:

**Common Sections:**
1. **Hero Section**
   - Tier 1: "Preserve Your SEO While Going Global"
   - Tier 2: "Tu Negocio Merece Clientes Globales"

2. **Value Propositions** (3-4 points)
   - Tier 1: SEO preservation, ownership, enterprise quality
   - Tier 2: Affordability, growth, accessibility

3. **Pricing Table**
   - Display in local currency
   - Show installment options (Tier 2 only)
   - Highlight local payment methods

4. **Social Proof** (3 case studies)
   - Same country/region as visitor
   - Specific metrics (e.g., "45% more traffic from US")

5. **FAQ Section** (10-15 questions)
   - Localized questions
   - Address local concerns (taxes, GDPR, refunds)

6. **CTA Sections** (multiple)
   - Primary: "Start Translation" / "Comenzar Traducción"
   - Secondary: WhatsApp contact (Tier 2 only)

7. **Footer**
   - Legal links (Privacy, Terms, Cookies)
   - Payment method logos
   - Country selector dropdown

---

### 2.3 Country-Specific Content Requirements

#### 🇺🇸 USA (/tier1/en-us/)
**Messaging:**
- "Maintain Your Google Rankings Across 100+ Languages"
- "Own Your Translations, Not Rent Them"

**Value Props:**
- SEO preservation (technical implementation details)
- Cost savings vs agencies ($15,000 vs $499)
- No monthly fees (vs Weglot $99/mo)

**Case Studies:**
- SaaS company: USA → Europe expansion
- Ecommerce: USA → Latin America
- B2B services: USA → Asia-Pacific

**Pricing:** USD
**Payment:** Stripe (cards, ACH)
**Keywords:** "website translation USA", "SEO translation software", "translate website keep SEO"

---

#### 🇲🇽 México (/tier2/es-mx/)
**Messaging:**
- "Tu Negocio Mexicano Merece Clientes Globales"
- "Traduce Tu Sitio Web Sin Perder Tu Presupuesto"

**Value Props:**
- Accesibilidad (meses sin intereses)
- Independencia (sin suscripciones eternas)
- Crecimiento real (casos de éxito mexicanos)

**Case Studies:**
- Tienda en línea: México → USA (vendió en dólares)
- SaaS: CDMX → Latinoamérica
- Servicios: Monterrey → Texas

**Pricing:** MXN (e.g., $3,980 emprendedor, 12 MSI)
**Payment:** Mercado Pago, OXXO, Stripe
**WhatsApp:** +52 [número local]
**Keywords:** "traducción sitio web México", "vender en Estados Unidos", "exportar servicios digitales"

---

#### 🇧🇷 Brasil (/tier2/pt-br/)
**Messaging:**
- "Seu Negócio Brasileiro Merece Clientes Internacionais"
- "Traduza Seu Site e Venda para o Mundo"

**Value Props:**
- Parcelamento sem juros (até 12x)
- PIX aceito (pagamento instantâneo)
- Cases brasileiros reais

**Case Studies:**
- Ecommerce: SP → USA/Europa
- SaaS: RJ → Mercosul
- Agência: BH → Portugal

**Pricing:** BRL (e.g., R$ 1.095 em 10x sem juros)
**Payment:** Mercado Pago, PIX, Boleto, Stripe
**WhatsApp:** +55 [número local]
**Keywords:** "tradução site Brasil", "expandir internacionalmente", "vender para gringos"

---

#### 🇦🇷 Argentina (/tier2/es-ar/)
**Messaging:**
- "Salí del Mercado Local y Vendé en Dólares"
- "Traducción de Sitios Web - Precio Dolarizado"

**Value Props:**
- Precios en USD (protection contra inflación)
- Cuotas disponibles
- Escapar del mercado local

**Case Studies:**
- Servicios profesionales: Buenos Aires → USA/España
- Freelancers: Argentina → clientes globales
- Productos digitales: AR → LATAM

**Pricing:** USD con conversión a ARS
**Payment:** Mercado Pago (cuotas), Stripe, transferencia
**WhatsApp:** +54 [número local]
**Keywords:** "traducción web Argentina", "vender servicios dólares", "escapar del mercado local"

---

#### 🇪🇸 España - PYMEs (/tier2/es-es/)
**Messaging:**
- "Traduce Tu Web y Conquista Latinoamérica"
- "Para Autónomos y PYMEs Que Quieren Crecer"

**Value Props:**
- Precio accesible para PYMEs
- Expansión a LATAM (550M hispanohablantes)
- Sin comisiones recurrentes

**Case Studies:**
- Consultoría: Madrid → México/Colombia
- Ecommerce: Barcelona → Argentina/Chile
- SaaS: Valencia → toda LATAM

**Pricing:** EUR (pero posicionado como accesible)
**Payment:** Stripe, Bizum
**WhatsApp:** +34 [número local]
**Keywords:** "traducción web PYMEs España", "expandir Latinoamérica", "autónomos internacionalización"

---

### 2.4 Content Production Checklist

**Per Landing Page (× 35+ pages):**
- [ ] Translate hero section to native language
- [ ] Localize value propositions
- [ ] Create 3 country-specific case studies
- [ ] Write 10-15 localized FAQs
- [ ] Adapt pricing table (currency, installments, methods)
- [ ] Add WhatsApp CTA (Tier 2 only)
- [ ] Optimize meta tags in local language
- [ ] Create country-specific imagery
- [ ] Legal compliance review (GDPR, local laws)

**Translation Requirements:**
- Native speakers for each language
- **NOT machine translation** for landing pages
- Professional copywriting, not literal translation
- Cultural adaptation (examples, idioms, tone)

**Estimated Effort:**
- 2-3 hours per landing page
- 35 pages × 3 hours = **105 hours**
- **Timeline:** 3 weeks with 3 copywriters

---

## 🚀 PHASE 3: Deployment & Testing (Week 4)

### 3.1 Infrastructure Deployment

```bash
# 1. Deploy geo-detection CloudFront Function
aws cloudfront create-function \
  --name translatecloud-geo-detect \
  --function-code fileb://cloudfront-functions/geo-detect.js \
  --function-config Runtime=cloudfront-js-1.0

# 2. Upload all landing pages to S3
aws s3 sync frontend/public/ s3://translatecloud-frontend-prod/

# 3. Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id d3sa5i2s0uyozh \
  --paths "/*"

# 4. Update API Lambda with market configs
aws lambda update-function-code \
  --function-name translatecloud-api \
  --zip-file fileb://backend/translatecloud-api.zip
```

### 3.2 Payment Gateway Testing

**Test Matrix:** 35 countries × 2-4 payment methods = ~80 test cases

**Priority Testing:**
1. **Tier 1 (Stripe only):** 5 countries
   - USA, UK, Germany, France, Australia

2. **Tier 2 (Multiple gateways):** 6 countries
   - Mexico (Mercado Pago + OXXO)
   - Brazil (Mercado Pago + PIX + Boleto)
   - Colombia (PSE)
   - Argentina (Mercado Pago + installments)
   - Spain (Bizum)
   - Philippines (GCash)

**Checklist:**
- [ ] Test successful payments in each currency
- [ ] Test installment calculations
- [ ] Test local payment methods (OXXO, PIX, etc.)
- [ ] Verify webhook delivery
- [ ] Test refund flows
- [ ] Verify invoice generation in local currency

---

### 3.3 Analytics Setup

**Google Analytics 4 Configuration:**

```javascript
// Custom dimensions
gtag('config', 'G-XXXXXXXXXX', {
  'custom_map': {
    'dimension1': 'country',
    'dimension2': 'tier',
    'dimension3': 'currency',
    'dimension4': 'payment_method'
  }
});

// Track market-specific events
function trackEvent(action, params) {
  gtag('event', action, {
    country: params.country,
    tier: params.tier,
    currency: params.currency,
    value: params.value || 0
  });
}
```

**Key Metrics to Track:**
- Conversion rate by country
- Revenue by market
- Preferred payment methods
- Installment vs one-time payment ratio
- Average order value by tier
- Geo-detection accuracy

**Dashboards:**
1. **Market Performance:** Revenue, conversions, AOV by country
2. **Payment Methods:** Usage distribution, success rates
3. **Tier Comparison:** Tier 1 vs Tier 2 metrics
4. **Funnel Analysis:** Country → Pricing → Checkout → Payment

---

## 📊 Success Criteria

### Week 1 (Technical Foundation)
- [ ] Geo-detection working for all 35+ countries
- [ ] Pricing engine calculating correctly in all currencies
- [ ] Payment integration tested (Stripe + Mercado Pago)

### Week 2-3 (Content)
- [ ] 18 Tier 1 landing pages complete
- [ ] 18 Tier 2 landing pages complete
- [ ] All pages SEO-optimized in local language
- [ ] Legal pages (Privacy, Terms) in 18 languages

### Week 4 (Launch)
- [ ] All pages live and indexed by Google
- [ ] Payment flows tested for all markets
- [ ] Analytics tracking all countries
- [ ] First test purchases completed

### Month 1 Goals
- **Tier 1:** 5 customers (avg €1,200) = €6,000
- **Tier 2:** 20 customers (avg $500) = €9,200
- **Total:** €15,200 revenue
- **Conversion rate:** 2% (Tier 1), 3% (Tier 2)

---

## 💰 Investment Required

### One-Time Costs

| Item | Cost | Notes |
|------|------|-------|
| **Content Creation** |
| Native copywriters (18 languages) | €8,000 | €450 per language |
| Professional translation | €3,000 | Legal pages, FAQs |
| Imagery/design localization | €2,000 | Stock photos, illustrations |
| **Development** |
| Geo-detection implementation | €500 | CloudFront Function |
| Payment gateway integration | €2,000 | Mercado Pago + local methods |
| Testing & QA | €1,500 | 80+ test cases |
| **Payment Gateway Setup** |
| Mercado Pago accounts (6 countries) | €0 | Free |
| Stripe multi-currency | €0 | Free |
| **TOTAL** | **€17,000** | |

### Monthly Operating Costs

| Item | Cost | Notes |
|------|------|-------|
| AWS infrastructure | €150 | Updated estimate |
| Payment processing (5% avg) | Variable | ~€800 on €16k revenue |
| Currency exchange API | €30 | Fixer.io |
| WhatsApp Business (6 numbers) | €60 | Tier 2 support |
| Analytics (Mixpanel) | €0 | Free tier |
| **TOTAL** | **€240 + processing** | |

### ROI Projection

**Month 1:**
- Revenue: €15,200
- Costs: €240 + €760 processing = €1,000
- **Profit: €14,200**

**Month 3:**
- Revenue: €35,000 (growth)
- Costs: €240 + €1,750 processing = €1,990
- **Profit: €33,010**

**Breakeven:** Immediate (Month 1)

---

## 🎯 Next Steps (Priority Order)

### This Week
1. ✅ Complete async translation system
2. 🆕 Create markets.json configuration
3. 🆕 Implement geo-detection CloudFront Function
4. 🆕 Set up Stripe multi-currency
5. 🆕 Hire 3 native copywriters (Spanish, Portuguese, French)

### Next Week
6. 🆕 Create 6 Tier 1 landing pages (EN markets)
7. 🆕 Create 6 Tier 2 landing pages (LATAM)
8. 🆕 Integrate Mercado Pago
9. 🆕 Test payment flows

### Week 3-4
10. 🆕 Complete remaining 23 landing pages
11. 🆕 SEO optimization (meta tags, sitemaps)
12. 🆕 Analytics setup
13. 🆕 Soft launch (10 countries)

### Month 2
14. 🆕 Full launch (all 35+ countries)
15. 🆕 A/B testing pricing variations
16. 🆕 Marketing campaigns (Google Ads, SEO)
17. 🆕 Expand to more countries (50+ total)

---

**Author:** TranslateCloud Team
**Status:** Ready for Implementation
**Last Updated:** 2025-10-20

**Total Markets:** 35+ countries
**Total Landing Pages:** 36+ (18 per tier)
**Total Languages:** 18
**Total Investment:** €17,000 one-time
**Expected Month 1 Revenue:** €15,200
**ROI Timeline:** Immediate
