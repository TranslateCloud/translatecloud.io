# TranslateCloud - Deployment Protocol

## 🎯 CRITICAL RULE: Always Invalidate CloudFront

**NEVER deploy frontend changes without invalidating CloudFront cache.**

Users will continue seeing old cached content for up to 24 hours if you don't invalidate.

---

## 📋 Standard Deployment Procedures

### 1️⃣ Frontend Deployment (Recommended Method)

**Use the automated script:**

```powershell
.\deploy-frontend.ps1
```

This script automatically:
- ✅ Syncs files to S3
- ✅ Sets proper cache headers
- ✅ Invalidates CloudFront distribution
- ✅ Waits for invalidation to complete
- ✅ Verifies deployment

**What it does:**
1. Verifies AWS credentials
2. Syncs frontend files to S3 with optimized cache headers:
   - HTML: 5 minutes (`max-age=300`)
   - JS/CSS: 1 hour (`max-age=3600`)
   - Images: 1 day (`max-age=86400`)
3. Creates CloudFront invalidation for `/*`
4. Waits for invalidation to complete (1-3 minutes)
5. Verifies critical files are present

---

### 2️⃣ Manual Frontend Deployment (Emergency Only)

If script fails, use manual commands:

```powershell
# Step 1: Sync files to S3
aws s3 sync frontend/public s3://translatecloud-frontend-prod/ --region eu-west-1 --delete

# Step 2: CRITICAL - Invalidate CloudFront
aws cloudfront create-invalidation `
  --distribution-id E1PKVM5C703IXO `
  --paths "/*" `
  --region us-east-1

# Step 3: Check invalidation status
aws cloudfront get-invalidation `
  --distribution-id E1PKVM5C703IXO `
  --id <INVALIDATION_ID> `
  --region us-east-1 `
  --query "Invalidation.Status"
```

**⚠️ DO NOT forget Step 2 - CloudFront invalidation is MANDATORY**

---

### 3️⃣ Backend Deployment

**Lambda function deployment:**

```powershell
cd backend

# Create deployment package
pip install -r requirements.txt `
  -t lambda-deploy/ `
  --platform manylinux2014_x86_64 `
  --only-binary=:all:

# Copy source code
Copy-Item -Recurse src/* lambda-deploy/src/

# Package
cd lambda-deploy
Compress-Archive -Path * -DestinationPath ../translatecloud-api.zip -Force
cd ..

# Deploy to Lambda
aws lambda update-function-code `
  --function-name translatecloud-api `
  --zip-file fileb://translatecloud-api.zip `
  --region eu-west-1

# Wait for deployment
aws lambda wait function-updated `
  --function-name translatecloud-api `
  --region eu-west-1
```

**Backend deployments DO NOT require CloudFront invalidation** (API Gateway handles this automatically).

---

## 🔍 Troubleshooting Cache Issues

### Problem: Users seeing old content after deployment

**Diagnosis:**
```powershell
# Check CloudFront distribution status
aws cloudfront get-distribution --id E1PKVM5C703IXO --query "Distribution.Status"

# List recent invalidations
aws cloudfront list-invalidations --distribution-id E1PKVM5C703IXO --max-items 5
```

**Solution:**
```powershell
# Create manual invalidation
aws cloudfront create-invalidation `
  --distribution-id E1PKVM5C703IXO `
  --paths "/*" `
  --region us-east-1
```

### Problem: CloudFront invalidation stuck

**Diagnosis:**
```powershell
# Check invalidation status
aws cloudfront get-invalidation `
  --distribution-id E1PKVM5C703IXO `
  --id <ID> `
  --query "Invalidation.{Status:Status,CreateTime:CreateTime}"
```

**Normal behavior:**
- InProgress: 30 seconds - 3 minutes
- Completed: Done

**If stuck >5 minutes:**
- Create new invalidation
- Check AWS Service Health Dashboard
- Contact AWS Support

---

## 📊 Cache Headers Strategy

| File Type | Cache Duration | Reason |
|-----------|---------------|--------|
| `*.html` | 5 minutes | Content changes frequently |
| `*.js`, `*.css` | 1 hour | Can change with releases |
| `*.jpg`, `*.png`, `*.svg` | 1 day | Static assets rarely change |

**Why these durations?**
- HTML: Short cache ensures users get latest content quickly
- JS/CSS: Medium cache balances performance and freshness
- Images: Long cache improves performance significantly

---

## ✅ Pre-Deployment Checklist

Before deploying, verify:

- [ ] Changes tested locally
- [ ] Git commit created with descriptive message
- [ ] No sensitive data in code (API keys, passwords)
- [ ] Breaking changes documented
- [ ] CloudFront invalidation budget checked (1000 free/month)

---

## 🚨 Emergency Rollback

If deployment breaks production:

### Frontend Rollback:
```powershell
# Get previous version from git
git checkout HEAD~1 frontend/public/

# Deploy previous version
.\deploy-frontend.ps1

# Restore latest version when fixed
git checkout main frontend/public/
```

### Backend Rollback:
```powershell
# Get previous Lambda version
aws lambda list-versions-by-function `
  --function-name translatecloud-api `
  --query "Versions[-2].Version"

# Rollback to previous version
aws lambda update-function-configuration `
  --function-name translatecloud-api `
  --runtime python3.11
```

---

## 📝 Deployment Log Template

Keep track of deployments:

```
Date: 2025-10-19 15:00 GMT
Deployed by: Virginia
Type: Frontend
Changes:
  - Fixed login endpoint path (/api/auth/login)
  - Updated auth.js with correct API routes
CloudFront Invalidation: I7W5I96SEYOP86HNABXERNAB7U
Status: ✅ Success
Notes: Fixed 404 error on login
```

---

## 🔧 Configuration

### AWS Resources:
- **S3 Bucket:** `translatecloud-frontend-prod` (eu-west-1)
- **CloudFront Distribution:** `E1PKVM5C703IXO`
- **CloudFront Domain:** `d3cx7bmpezd18p.cloudfront.net`
- **Custom Domain:** `www.translatecloud.io`
- **Lambda Function:** `translatecloud-api` (eu-west-1)
- **API Gateway:** `e5yug00gdc` (eu-west-1)

### Important URLs:
- **Production Site:** https://www.translatecloud.io
- **API Endpoint:** https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod
- **S3 Website:** http://translatecloud-frontend-prod.s3-website-eu-west-1.amazonaws.com

---

## 📚 Related Documentation

- AWS CloudFront Invalidation Docs: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Invalidation.html
- CloudFront Pricing (Invalidations): https://aws.amazon.com/cloudfront/pricing/
- S3 Cache-Control Headers: https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingMetadata.html

---

**Last Updated:** October 19, 2025 - 15:45 GMT
**Created by:** Claude Code
**Maintained by:** Virginia Posadas
