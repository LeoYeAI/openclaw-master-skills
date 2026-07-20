# OpenClaw Security Hardening - Quick Start

**Complete Security Framework for OpenClaw Agents**

---

## 🚀 5-Minute Quick Start

### Step 1: Fix File Permissions (30 seconds)
```bash
chmod 600 ~/.openclaw/workspace/*.md
```

### Step 2: Create .env File (1 minute)
```bash
cat > ~/.openclaw/workspace/.env << 'EOF'
# 敏感信息 - 请勿分享或提交到Git

# 飞书配置
FEISHU_APP_ID=your_app_id_here
FEISHU_APP_SECRET=your_app_secret_here
FEISHU_APP_TOKEN=your_token_here

# 其他敏感信息
# API_KEY=xxx
# DATABASE_URL=xxx
EOF

chmod 600 ~/.openclaw/workspace/.env
```

### Step 3: Update .gitignore (30 seconds)
```bash
echo ".env" >> ~/.openclaw/workspace/.gitignore
echo "*.secret" >> ~/.openclaw/workspace/.gitignore
echo "*.key" >> ~/.openclaw/workspace/.gitignore
```

### Step 4: Create Security Check Script (2 minutes)
```bash
# See SKILL.md Part 1, Layer 4 for full script
mkdir -p ~/.openclaw/workspace/scripts

cat > ~/.openclaw/workspace/scripts/security-check.sh << 'SCRIPT'
#!/bin/bash
echo "🔒 Security Check..."

for file in MEMORY.md USER.md SOUL.md TOOLS.md; do
    path="$HOME/.openclaw/workspace/$file"
    [ -f "$path" ] && chmod 600 "$path" 2>/dev/null
done

[ -f "$HOME/.openclaw/workspace/.env" ] && chmod 600 "$HOME/.openclaw/workspace/.env"

echo "✅ Done"
SCRIPT

chmod +x ~/.openclaw/workspace/scripts/security-check.sh
```

### Step 5: Update MEMORY.md (1 minute)
Replace sensitive info with:
```markdown
- **App Secret**: 见.env文件（FEISHU_APP_SECRET）
```

### Step 6: Run Security Check
```bash
~/.openclaw/workspace/scripts/security-check.sh
```

---

## ✅ Verification Checklist

- [ ] Core files have 600 permission
- [ ] .env file created with 600 permission
- [ ] .env added to .gitignore
- [ ] MEMORY.md updated with .env references
- [ ] Security check script created
- [ ] SOUL.md contains security rules

---

## 📊 Security Layers

```
Layer 1: File Permissions    (chmod 600)
   ↓
Layer 2: Data Isolation      (.env files)
   ↓
Layer 3: Git Protection      (.gitignore)
   ↓
Layer 4: Automated Monitoring (security-check.sh)
   ↓
Layer 5: Runtime Protection  (Content vs Intent)
```

---

## 🎯 Ongoing Maintenance

**Weekly**:
```bash
~/.openclaw/workspace/scripts/security-check.sh
```

**Monthly**:
- Review and update .env file
- Audit temporary files
- Check Git history for secrets

**Quarterly**:
- Full security audit
- Review and rotate keys
- Update this skill

---

## 🆘 Emergency Procedures

**If keys are leaked**:
1. Revoke compromised keys immediately
2. Generate new keys
3. Update .env file
4. Rotate all credentials

**If command was mistakenly executed**:
1. Assess damage
2. Restore from backup if needed
3. Update SOUL.md rules
4. Test with security test cases

**If secrets were pushed to Git**:
```bash
# Remove from history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" --prune-empty --tag-name-filter cat -- --all

# Force push
git push origin --force --all
```

---

## 📚 Full Documentation

See `SKILL.md` for complete documentation including:
- Detailed threat model
- Advanced GPG encryption
- Runtime security (Prompt Injection)
- Testing procedures
- Incident response

---

**Created**: 2026-03-16
**Version**: 1.0
**Maintainer**: R2-D2 AI Assistant 🦞
