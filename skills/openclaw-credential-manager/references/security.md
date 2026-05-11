# Security Best Practices

## File Permissions

### Unix/Linux/macOS
```bash
# .env should be readable/writable only by owner
chmod 600 ~/.openclaw/.env

# Verify
ls -la ~/.openclaw/.env
# Should show: -rw------- (600)
```

### Windows
```powershell
# Remove inheritance and grant only owner access
icacls .env /inheritance:r /grant:r "%USERNAME%:F"
```

## Version Control

### Always Ignore Credentials
```gitignore
# In .gitignore
.env
*.env
.env.*
!.env.example

# Credential files
*credentials*.json
*-creds.json
*.key
*.pem

# Config directories
.config/
```

### Check Before Committing
```bash
# Scan for secrets before commit
git diff --cached | grep -i "api_key\|secret\|password\|token"

# Use git-secrets or similar tools
git secrets --scan
```

## Credential Rotation

### Regular Rotation Schedule
- **Critical services:** Every 30 days
- **Standard services:** Every 90 days
- **Low-risk services:** Every 6 months

### After Rotation
1. Update `.env` with new credentials
2. Test applications
3. Revoke old credentials
4. Document rotation date

## Separation of Environments

### Use Separate Credentials
```bash
# Development
~/.openclaw/.env.development

# Production
~/.openclaw/.env.production

# Never mix environments
```

### Load Appropriate Environment
```python
import os
env = os.getenv('OPENCLAW_ENV', 'development')
env_file = f"~/.openclaw/.env.{env}"
```

## Secret Exposure Prevention

### Never Log Full Credentials
```python
# ❌ BAD
print(f"Using API key: {api_key}")

# ✅ GOOD
print(f"Using API key: {api_key[:8]}...")
```

### Sanitize Error Messages
```python
# ❌ BAD
raise Exception(f"Auth failed with key {api_key}")

# ✅ GOOD
raise Exception("Authentication failed")
```

### Avoid Shell History
```bash
# ❌ BAD
export API_KEY=secret123

# ✅ GOOD - Load from file
set -a && source ~/.openclaw/.env && set +a
```

## Encrypted Storage

### For Extra Security
```bash
# Encrypt .env with GPG
gpg -c ~/.openclaw/.env

# Decrypt when needed
gpg -d ~/.openclaw/.env.gpg > /tmp/.env
```

### Use Secret Managers
- **1Password:** OpenClaw 1password skill
- **System Keyring:** gnome-keyring, macOS Keychain
- **Cloud:** AWS Secrets Manager, Google Secret Manager

## Access Control

### Minimize Access
- Only necessary processes
- Only necessary users
- Only necessary duration

### Audit Access
```bash
# Check who can read .env
getfacl ~/.openclaw/.env

# Check recent access
stat ~/.openclaw/.env
```

## Backup Security

### Encrypt Backups
```bash
# Encrypt before backup
tar czf - ~/.openclaw | gpg -c > backup.tar.gz.gpg

# Restore
gpg -d backup.tar.gz.gpg | tar xzf -
```

### Exclude from General Backups
```bash
# In backup scripts, exclude sensitive dirs
rsync -av --exclude='.openclaw/.env' ~/ /backup/
```

## Network Security

### Never Transmit Unencrypted
- ✅ HTTPS only
- ❌ Never HTTP
- ❌ Never in URL params
- ✅ Always in headers

### API Best Practices
```python
# ✅ GOOD - In headers
headers = {'Authorization': f'Bearer {token}'}
requests.get(url, headers=headers)

# ❌ BAD - In URL
requests.get(f'{url}?api_key={token}')
```

## Incident Response

### If Credentials Leaked

1. **Immediately:** Revoke leaked credentials
2. **Rotate:** Generate new credentials
3. **Audit:** Check for unauthorized access
4. **Update:** Replace in `.env` and all systems
5. **Monitor:** Watch for abuse

### Example
```bash
# 1. Revoke old key in service dashboard
# 2. Generate new key
# 3. Update .env
sed -i 's/old_key/new_key/' ~/.openclaw/.env
# 4. Test
./test_credentials.sh
# 5. Monitor logs
```

## Compliance

### Know Your Requirements
- **GDPR:** Data protection regulations
- **HIPAA:** Healthcare data
- **PCI DSS:** Payment card data
- **SOC 2:** Security controls

### Audit Trail
```bash
# Log credential access
echo "$(date): .env accessed by $USER" >> ~/.openclaw/access.log
```

## Checklist

Before going to production:

- [ ] `.env` has 600 permissions
- [ ] `.env` is in `.gitignore`
- [ ] No credentials in code
- [ ] No credentials in logs
- [ ] Separate dev/prod credentials
- [ ] Rotation schedule established
- [ ] Backups are encrypted
- [ ] Access is minimized
- [ ] Incident response plan exists
- [ ] Team trained on security

## Resources

- [OWASP: API Security](https://owasp.org/www-project-api-security/)
- [12-Factor App: Config](https://12factor.net/config)
- [GitHub: Removing Sensitive Data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
