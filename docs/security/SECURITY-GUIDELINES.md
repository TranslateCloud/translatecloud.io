# Security Guidelines for TranslateCloud

## 🔴 CRITICAL RULE: NEVER COMMIT SECRETS TO GIT

**This is a MANDATORY rule that MUST be followed at all times.**

### What counts as a secret?
- API keys (Stripe, DeepL, AWS, etc.)
- Database passwords
- JWT secret keys
- OAuth client secrets
- Private keys (.pem, .key files)
- Webhook secrets
- Encryption keys
- Access tokens
- Any credential that provides access to services

### ✅ What TO DO:

1. **Use Environment Variables**
   ```python
   # ✅ CORRECT
   api_key = os.getenv('DEEPL_API_KEY')
   db_password = os.getenv('DB_PASSWORD')
   ```

2. **Use AWS Secrets Manager (Production)**
   ```python
   import boto3
   client = boto3.client('secretsmanager', region_name='eu-west-1')
   secret = client.get_secret_value(SecretId='prod/translatecloud/db')
   ```

3. **Use Placeholders in Documentation**
   ```bash
   # ✅ CORRECT
   STRIPE_SECRET_KEY=sk_test_your_key_here
   DEEPL_API_KEY=your_deepl_api_key_here
   JWT_SECRET_KEY=your_jwt_secret_here
   ```

4. **Keep .env Files Local Only**
   - Never commit `.env` files
   - Add to `.gitignore` (already configured)
   - Share `.env.example` with placeholders instead

### ❌ What NOT TO DO:

1. **Never Hardcode Secrets**
   ```python
   # ❌ WRONG - Never do this!
   api_key = "sk_test_51abc123..."
   db_password = "MySecretPassword123"
   ```

2. **Never Commit Files Containing Secrets**
   ```bash
   # ❌ WRONG
   git add .env
   git add credentials.json
   git add SECURITY-ROTATION-REQUIRED.md  # Contains actual passwords
   ```

3. **Never Put Real Secrets in Documentation**
   ```markdown
   # ❌ WRONG
   Set your API key to: sk_test_51abc123def456...

   # ✅ CORRECT
   Set your API key to: sk_test_your_key_here
   ```

## 🛡️ Git Commit Checklist

**Before EVERY commit, verify:**

- [ ] No `.env` files staged
- [ ] No API keys in code (search for `sk_`, `pk_`, `whsec_`, etc.)
- [ ] No passwords in documentation
- [ ] Only placeholders in example configs
- [ ] No credential files (.pem, .key, credentials.json)

```bash
# Check before committing
git status
git diff --cached | grep -i "sk_test\|pk_test\|password\|secret"
```

## 🔍 Pre-Commit Checks

### Manual Check Commands
```bash
# Search for potential secrets in staged files
git diff --cached | grep -E "(sk_test|pk_test|sk_live|pk_live|whsec_|password|api_key|secret_key)" -i

# List all staged files
git diff --cached --name-only

# Check specific patterns
git grep -i "password" HEAD
git grep -i "sk_test" HEAD
```

### GitHub Push Protection

GitHub will automatically scan for secrets. If blocked:

1. **If it's a real secret:** Remove it immediately
   ```bash
   # Undo last commit
   git reset --soft HEAD~1

   # Remove the secret from files
   # Edit files to use placeholders

   # Commit again
   git add .
   git commit -m "Your message"
   ```

2. **If it's a false positive (placeholder):**
   - Use the GitHub link to allow it
   - Or update the placeholder to be more obviously fake

## 🔄 Credential Rotation Schedule

| Credential | Rotation Frequency | Last Rotated |
|-----------|-------------------|--------------|
| Database Password | Every 90 days | Oct 19, 2025 |
| JWT Secret | Every 90 days | Oct 19, 2025 |
| DeepL API Key | Yearly or if exposed | Oct 19, 2025 |
| Stripe Keys | Never (test mode) | N/A |
| AWS Keys | Not used (IAM roles) | N/A |

## 🚨 What To Do If Secrets Are Exposed

### Immediate Actions (within 1 hour):

1. **Revoke the exposed credential immediately**
   - Stripe: Dashboard → Developers → API keys → Roll key
   - DeepL: Account → API keys → Revoke
   - Database: `ALTER USER ... WITH PASSWORD 'new_password';`

2. **Generate new credential**

3. **Update production environment**
   ```bash
   # Update Lambda
   aws lambda update-function-configuration \
     --function-name translatecloud-api \
     --environment "Variables={...new credentials...}" \
     --region eu-west-1
   ```

4. **Remove from git history (if committed)**
   ```bash
   # Option 1: Remove specific file from history
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch PATH/TO/FILE" \
     --prune-empty --tag-name-filter cat -- --all

   # Option 2: Use BFG Repo-Cleaner (easier)
   bfg --delete-files FILENAME
   bfg --replace-text passwords.txt
   ```

5. **Force push (with caution)**
   ```bash
   git push --force --all
   ```

6. **Notify team** (if applicable)

### Prevention:

- Enable GitHub secret scanning (already active)
- Add pre-commit hooks to scan for secrets
- Regular security audits
- Use AWS Secrets Manager for production

## 📋 Approved Files That Can Contain Examples

These files can contain placeholder/example secrets (NOT real ones):

- `SETUP-STRIPE.md` - Stripe setup examples
- `.env.example` - Example environment variables
- `README.md` - Documentation examples
- `SECURITY-GUIDELINES.md` - This file

**Rule:** Use obviously fake placeholders:
- `your_api_key_here`
- `sk_test_your_key_here`
- `pk_test_your_publishable_key_here`
- `your_password_here`

## 🔐 Production Secret Management

### Current Setup:
- Secrets stored in Lambda environment variables
- Set via AWS CLI or AWS Console
- Not visible in code or git

### Future Improvement (Recommended):
```python
# backend/src/config/secrets.py
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager', region_name='eu-west-1')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# Usage
db_creds = get_secret('prod/translatecloud/database')
stripe_keys = get_secret('prod/translatecloud/stripe')
```

Benefits:
- Automatic rotation
- Audit logging
- Encryption at rest
- Fine-grained IAM permissions

## 📚 Additional Resources

- [GitHub Secret Scanning](https://docs.github.com/code-security/secret-scanning)
- [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/)
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [git-secrets (AWS tool)](https://github.com/awslabs/git-secrets)

---

**Last Updated:** October 20, 2025
**Compliance:** GDPR, SOC 2
**Owner:** Virginia Posadas (v.posadasbiazutti@gmail.com)
