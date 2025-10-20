# CORS Error Fix - CRITICAL

## Error Details

**Date:** 2025-10-20
**Status:** ❌ BLOCKING PRODUCTION
**Priority:** 🔴 CRITICAL

### Error Message
```
Access to fetch at 'https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod/api/projects/translate'
from origin 'https://www.translatecloud.io' has been blocked by CORS policy:
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

### Current Situation
- **Frontend Origin:** `https://www.translatecloud.io`
- **API Gateway:** `https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod`
- **Issue:** API Gateway is not sending CORS headers in responses
- **Impact:** Cannot submit translation jobs from production frontend

---

## Root Cause

API Gateway CORS configuration is missing or incomplete. The OPTIONS preflight requests are likely failing or not configured.

---

## Solution Steps

### Option 1: Enable CORS in API Gateway Console (Quick Fix)

1. **Open AWS Console → API Gateway**
   ```
   Service: API Gateway
   API Name: translatecloud-api
   Region: eu-west-1
   ```

2. **Enable CORS for all routes:**
   ```bash
   # AWS CLI command
   aws apigatewayv2 update-api \
     --api-id e5yug00gdc \
     --cors-configuration AllowOrigins=https://www.translatecloud.io,AllowMethods=GET,POST,PUT,DELETE,OPTIONS,AllowHeaders=Content-Type,Authorization \
     --region eu-west-1
   ```

3. **Verify CORS settings:**
   ```bash
   aws apigatewayv2 get-api \
     --api-id e5yug00gdc \
     --region eu-west-1 \
     --query "CorsConfiguration"
   ```

### Option 2: Add CORS Headers in Lambda Response (Alternative)

If API Gateway CORS doesn't work, add headers directly in Lambda handler:

**File:** `backend/handler.py` (API Lambda)

```python
def lambda_handler(event, context):
    # ... existing code ...

    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "https://www.translatecloud.io",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Max-Age": "86400"
        },
        "body": json.dumps(result)
    }

    return response
```

### Option 3: CloudFront Distribution (Recommended Long-term)

Add CORS headers via CloudFront response headers policy:

1. **Create Response Headers Policy:**
   ```json
   {
     "Name": "translatecloud-cors-policy",
     "CorsConfig": {
       "AccessControlAllowOrigins": {
         "Items": ["https://www.translatecloud.io"]
       },
       "AccessControlAllowMethods": {
         "Items": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
       },
       "AccessControlAllowHeaders": {
         "Items": ["Content-Type", "Authorization"]
       },
       "AccessControlMaxAgeSec": 86400,
       "OriginOverride": true
     }
   }
   ```

2. **Attach to CloudFront Distribution**

---

## Testing Commands

### Test CORS Preflight (OPTIONS request)
```bash
curl -X OPTIONS https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod/api/jobs/translate \
  -H "Origin: https://www.translatecloud.io" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type,Authorization" \
  -v
```

**Expected Response:**
```
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://www.translatecloud.io
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Max-Age: 86400
```

### Test Actual POST Request
```bash
curl -X POST https://e5yug00gdc.execute-api.eu-west-1.amazonaws.com/prod/api/jobs/translate \
  -H "Origin: https://www.translatecloud.io" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"url":"https://example.com","source_lang":"en","target_lang":"es"}' \
  -v
```

**Expected Response:**
```
HTTP/1.1 202 Accepted
Access-Control-Allow-Origin: https://www.translatecloud.io
Content-Type: application/json

{"job_id":"...","status":"pending"}
```

---

## Current API Gateway Configuration

Check current CORS config:
```bash
aws apigatewayv2 get-apis --region eu-west-1 --query "Items[?Name=='translatecloud-api'].[ApiId,Name,CorsConfiguration]" --output json
```

---

## Fix Priority

**Must fix before:**
- ❌ Production testing
- ❌ User onboarding
- ❌ Launch

**Estimated Time:** 15 minutes

**Recommended Approach:** Option 1 (API Gateway CORS) + verify with curl

---

## Additional Origins to Add Later

When ready for development/staging:
```
AllowOrigins:
  - https://www.translatecloud.io (production)
  - https://translatecloud.io (production without www)
  - http://localhost:5173 (local dev - Vite)
  - http://localhost:3000 (local dev - alternative)
  - https://staging.translatecloud.io (staging - future)
```

---

## Related Files

- `backend/handler.py` - Main API Lambda
- `backend/worker_handler.py` - Worker Lambda
- `frontend/public/assets/js/api.js` - Frontend API client
- `docs/architecture/ASYNC-TRANSLATION-ARCHITECTURE.md` - API documentation

---

**Next Action:** Run AWS CLI command to enable CORS on API Gateway
