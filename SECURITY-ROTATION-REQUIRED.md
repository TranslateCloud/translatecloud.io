# 🚨 SECURITY: Credential Rotation Required

**Date:** October 19, 2025 - 17:00 GMT
**Reason:** Database password and secrets were exposed in Git history (session logs)
**Status:** ⚠️ URGENT - Rotate within 24 hours

---

## 🔴 Exposed Credentials (Found in Git History)

### 1. **Database Password**
```
EXPOSED: ApiUser2025Secure!
Location: CLAUDE-CODE-SESSION-LOG.md (commits 0a95b21, 0bc87dd)
User: translatecloud_api
Host: translatecloud-db-prod.c3asoiwiy0l1.eu-west-1.rds.amazonaws.com
```

**Action Required:**
```sql
-- Connect to RDS as master user
ALTER USER translatecloud_api WITH PASSWORD 'NEW_SECURE_PASSWORD_HERE';
```

Then update Lambda environment variable:
```bash
aws lambda update-function-configuration \
  --function-name translatecloud-api \
  --environment "Variables={DB_PASSWORD=NEW_SECURE_PASSWORD_HERE,...}" \
  --region eu-west-1
```

### 2. **JWT Secret Key**
```
EXPOSED: translatecloud-jwt-secret-2025-prod-secure-key-do-not-share
Location: .env file (shown in session logs)
```

**Action Required:**
```bash
# Generate new JWT secret
NEW_JWT_SECRET=$(openssl rand -base64 32)

# Update Lambda
aws lambda update-function-configuration \
  --function-name translatecloud-api \
  --environment "Variables={JWT_SECRET_KEY=$NEW_JWT_SECRET,...}" \
  --region eu-west-1
```

**Impact:** All existing JWT tokens will be invalidated. Users will need to login again.

### 3. **DeepL API Key**
```
EXPOSED: 65b6838b-3831-44e5-927d-385730a20973:fx
Location: .env file
Status: ACTIVE (needs rotation if possible)
```

**Action Required:**
- Login to DeepL account: https://www.deepl.com/pro-account
- Generate new API key
- Revoke old key
- Update Lambda environment variable

---

## ✅ NOT Exposed / Safe

### Stripe Keys
```
✓ Backend uses: os.getenv('STRIPE_SECRET_KEY', 'sk_test_...')
✓ Placeholder only, no real key exposed
✓ SETUP-STRIPE.md only has examples
```

### AWS Credentials
```
✓ No AWS access keys found in repository
✓ Lambda uses IAM roles (no keys needed)
```

---

## 📋 Rotation Checklist

- [ ] **Step 1:** Change RDS database password for `translatecloud_api` user
- [ ] **Step 2:** Generate new JWT secret key
- [ ] **Step 3:** Rotate DeepL API key
- [ ] **Step 4:** Update Lambda environment variables with all new credentials
- [ ] **Step 5:** Test API endpoints after rotation
- [ ] **Step 6:** Update local `.env` file with new credentials
- [ ] **Step 7:** Delete this file after rotation complete

---

## 🔧 Quick Rotation Script

```bash
#!/bin/bash
# Save as: rotate-credentials.sh

echo "=== TranslateCloud Credential Rotation ==="

# 1. Generate new JWT secret
echo "[1/4] Generating new JWT secret..."
NEW_JWT_SECRET=$(openssl rand -base64 32)
echo "New JWT Secret: $NEW_JWT_SECRET"

# 2. Prompt for new DB password
echo "[2/4] Enter new database password:"
read -s NEW_DB_PASSWORD

# 3. Update RDS (manual - requires master user)
echo "[3/4] Update RDS password manually with:"
echo "ALTER USER translatecloud_api WITH PASSWORD '$NEW_DB_PASSWORD';"

# 4. Update Lambda
echo "[4/4] Updating Lambda environment variables..."
aws lambda update-function-configuration \
  --function-name translatecloud-api \
  --environment "Variables={\
    DB_HOST=translatecloud-db-prod.c3asoiwiy0l1.eu-west-1.rds.amazonaws.com,\
    DB_PORT=5432,\
    DB_NAME=postgres,\
    DB_USER=translatecloud_api,\
    DB_PASSWORD=$NEW_DB_PASSWORD,\
    JWT_SECRET_KEY=$NEW_JWT_SECRET,\
    DEEPL_API_KEY=YOUR_NEW_DEEPL_KEY\
  }" \
  --region eu-west-1

echo "✓ Rotation complete!"
echo "⚠ Test endpoints before deleting old credentials"
```

---

## 🛡️ Prevention for Future

### Updated .gitignore
```
✓ .env files excluded
✓ Session logs excluded (CLAUDE-CODE-SESSION*.md)
✓ DAY planning docs excluded
✓ Credentials files excluded
```

### Best Practices Going Forward
1. **Never commit secrets** - Use environment variables
2. **Use AWS Secrets Manager** for production credentials
3. **Rotate credentials quarterly** as standard practice
4. **Enable GitHub secret scanning** (already active)
5. **Review commits** before pushing

---

## 📞 Emergency Contact

If credentials are actively being exploited:
1. Immediately revoke all exposed credentials
2. Check RDS logs for unauthorized access
3. Review application logs for suspicious activity
4. Contact AWS support if needed

---

**Created:** October 19, 2025 - 17:00 GMT
**Priority:** HIGH
**Deadline:** Rotate within 24 hours
**Delete after:** Rotation complete and verified
