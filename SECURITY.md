# Security Checklist

## 🚨 NEVER Commit These Files:
- `service-account-key.json` - Google Cloud credentials
- `.env` files - Environment variables
- Any `.key`, `.pem`, `.p12`, `.pfx` files - Private keys
- `secrets/`, `credentials/`, `keys/` directories
- Any files ending with `.secret`

## ✅ Safe to Commit:
- `render.yaml` - Deployment configuration (no secrets)
- `requirements.txt` - Python dependencies
- `server.py` - Application code
- `utils/` - Utility functions
- `data/` - Application data (non-sensitive)

## 🔐 Credentials Management:
1. **Local Development**: Use `cloud_storage_config.env` (not committed)
2. **Production**: Set environment variables in Render dashboard
3. **Never**: Hardcode credentials in code or commit them to git

## 🚀 Deployment Security:
1. Set `GOOGLE_APPLICATION_CREDENTIALS_JSON` in Render environment
2. Set `GCS_BUCKET_NAME` and `GOOGLE_CLOUD_PROJECT` in Render
3. Keep `service-account-key.json` only on your local machine

## 📋 Pre-commit Checklist:
- [ ] No `.env` files staged
- [ ] No credential files staged
- [ ] No private keys staged
- [ ] Check `git status` for sensitive files
- [ ] Verify `.gitignore` is working

## 🆘 If You Accidentally Commit Credentials:
1. **Immediately**: Revoke the credentials in Google Cloud Console
2. **Create new credentials** with a new service account
3. **Remove from git history** using `git filter-branch` or GitHub's tools
4. **Update environment variables** in Render
5. **Notify team** if working with others
