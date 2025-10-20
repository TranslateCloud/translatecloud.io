# Stripe Payment Integration Setup Guide

## 🔑 Get Stripe API Keys (FREE - Test mode)

### Step 1: Create Stripe Account
1. Go to: https://dashboard.stripe.com/register
2. Fill in the form:
   - Email: v.posadasbiazutti@gmail.com
   - Password: (your secure password)
   - Business name: TranslateCloud
3. Verify email

### Step 2: Get API Keys
1. Login to: https://dashboard.stripe.com
2. Go to "Developers" → "API keys"
3. You'll see two keys:
   - **Publishable key** (starts with `pk_test_...`) - For frontend
   - **Secret key** (starts with `sk_test_...`) - For backend (click "Reveal")

### Step 3: Get Webhook Secret
1. Go to "Developers" → "Webhooks"
2. Click "+ Add endpoint"
3. Enter endpoint URL:
   ```
   https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod/api/payments/webhook
   ```
4. Select events to listen to:
   - `checkout.session.completed`
   - `invoice.payment_succeeded`
   - `customer.subscription.deleted`
5. Click "Add endpoint"
6. Copy the **Signing secret** (starts with `whsec_...`)

### Step 4: Configure in TranslateCloud

#### Option A: .env File (Local Development)
Add to `.env`:
```env
# Stripe Payment Processing
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
FRONTEND_URL=http://localhost:3000
```

#### Option B: Lambda Environment Variables (Production)
```bash
aws lambda update-function-configuration \
  --function-name translatecloud-api \
  --environment "Variables={
    DEEPL_API_KEY=your_deepl_api_key_here,
    JWT_SECRET_KEY=your_jwt_secret_here,
    STRIPE_SECRET_KEY=sk_test_your_key_here,
    STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here,
    STRIPE_WEBHOOK_SECRET=whsec_your_secret_here,
    FRONTEND_URL=https://translatecloud.io
  }" \
  --region eu-west-1
```

## 📦 Create Stripe Products & Prices

### Step 1: Create Products
1. Go to "Products" → "+ Add product"
2. Create three products:

#### Professional Plan
- Name: Professional
- Description: For small businesses
- Pricing:
  - Monthly: €29/month
  - Annual: €290/year (save €58)
- Copy the **Price ID** (starts with `price_...`)

#### Business Plan
- Name: Business
- Description: For growing companies
- Pricing:
  - Monthly: €99/month
  - Annual: €990/year (save €198)

#### Enterprise Plan
- Name: Enterprise
- Description: For large organizations
- Pricing:
  - Custom pricing
  - Contact sales

### Step 2: Update Frontend with Price IDs
Edit `frontend/public/assets/js/pricing.js`:
```javascript
const STRIPE_PRICES = {
  professional: {
    monthly: 'price_xxxxxxxxxxxxx',
    annual: 'price_xxxxxxxxxxxxx'
  },
  business: {
    monthly: 'price_xxxxxxxxxxxxx',
    annual: 'price_xxxxxxxxxxxxx'
  }
};
```

## ✅ Test Stripe Integration

### Test Card Numbers (Test Mode)
```
# Success
Card: 4242 4242 4242 4242
Expiry: Any future date (e.g., 12/25)
CVC: Any 3 digits (e.g., 123)
ZIP: Any 5 digits (e.g., 12345)

# Decline
Card: 4000 0000 0000 0002

# Requires Authentication
Card: 4000 0025 0000 3155
```

### Test Payment Flow
1. Go to your frontend
2. Click "Subscribe" on a plan
3. You'll be redirected to Stripe Checkout
4. Use test card `4242 4242 4242 4242`
5. Complete payment
6. Verify webhook received:
   ```bash
   aws logs tail /aws/lambda/translatecloud-api --follow --region eu-west-1
   ```

## 📊 Monitor Payments

### View Test Payments
```
Dashboard → Payments → All payments
```

### View Webhook Events
```
Dashboard → Developers → Webhooks → [Your endpoint]
```

## 💡 Stripe Test Mode vs Live Mode

- **Test Mode**: Free, use test cards, no real money
- **Live Mode**: Real payments, requires business verification

**Start with Test Mode** until you're ready to go live.

## 🚀 Go Live (When Ready)

### Prerequisites
1. Complete Stripe business verification
2. Add bank account for payouts
3. Update terms of service & privacy policy

### Switch to Live Mode
1. Go to "Developers" → "API keys"
2. Toggle to "Live mode"
3. Copy live keys (start with `sk_live_...` and `pk_live_...`)
4. Update Lambda environment variables
5. Update webhook endpoint URL

## ⚠️ Security

**NEVER** commit API keys to git:
```bash
# .gitignore already includes:
.env
*.env
```

**Rotate keys** every 90 days for security.

## 🔧 Troubleshooting

### Error: "Invalid API Key"
- Verify you copied the full key
- Check you're using the correct mode (test vs live)
- Ensure no extra spaces

### Error: "Webhook signature verification failed"
- Verify webhook secret is correct
- Check webhook endpoint URL is correct
- Ensure you're sending raw request body (not parsed JSON)

### Payment Not Creating Subscription
- Check CloudWatch logs for errors
- Verify webhook events are being sent
- Check database for subscription updates

## 📚 Official Documentation

- Stripe Docs: https://stripe.com/docs
- Checkout: https://stripe.com/docs/payments/checkout
- Webhooks: https://stripe.com/docs/webhooks
- Test Cards: https://stripe.com/docs/testing

## 💰 Pricing (Current Plan - Free)

- No monthly fees
- 2.9% + €0.25 per successful card charge
- No setup fee
- No cancellation fee

**Upgrade to Stripe Plus** (€25/month) for lower fees when doing high volume.
