# Security Policy

## Overview

AnveVoice OpenClaw Skill enables voice AI integration for websites. This document outlines security considerations, data handling, and external dependencies.

## ⚠️ Important Privacy Notice

**This skill handles sensitive voice data:**
- Voice recordings from website visitors
- Conversation transcripts
- Contact information (email, phone if shared)
- Browser metadata for analytics

**You MUST:**
- Use HTTPS (required for microphone access)
- Disclose voice collection in your privacy policy
- Obtain user consent before recording
- Review GDPR/CCPA/HIPAA compliance

## VirusTotal Verification

| Attribute | Value |
|-----------|-------|
| **Scan Date** | February 21, 2026 |
| **Detection Rate** | 0/62 vendors flagged as malicious |
| **Status** | ✅ CLEAN |
| **File** | SKILL.md (16.63 KB) |
| **SHA256 Hash** | f3c788a5cfa2a01b67edd6af451ee6748944818f20b7d51203ecf5cf8d4c837b |

**[View Full Scan Report on VirusTotal →](https://www.virustotal.com/gui/file/f3c788a5cfa2a01b67edd6af451ee6748944818f20b7d51203ecf5cf8d4c837b?nocache=1)**

---

## External Dependencies & Data Handling

### Infrastructure Architecture

| Component | Domain | Purpose |
|-----------|--------|---------|
| Dashboard | `anvevoice.com` | User interface, documentation |
| MCP API | `aaxlcyouksuljvmypyhy.supabase.co` | Backend edge functions (Supabase) |
| Widget CDN | `anvevoice.com/embed.js` | Client-side voice widget |

**Why Supabase?** AnveVoice uses Supabase for serverless edge functions, database, and authentication. The Supabase project ID is `aaxlcyouksuljvmypyhy`.

### API Endpoints

| Endpoint | Purpose | Data Transmitted |
|----------|---------|------------------|
| `https://aaxlcyouksuljvmypyhy.supabase.co/functions/v1/anve-mcp` | MCP server | API requests, bot configs, analytics |
| `https://anvevoice.com` | Dashboard & docs | Auth tokens, user settings |

### Widget Embed Script (Visitor-Facing)

When you deploy a voice bot, the following external script is embedded in your website:

```html
<script src="https://anvevoice.com/embed.js" 
        data-bot-id="YOUR_BOT_ID"
        async>
</script>
```

**What this script does:**
- Loads the voice widget UI in the visitor's browser
- Requests microphone permission (browser-native prompt)
- Transmits voice data to AnveVoice servers for processing
- Displays AI responses and handles conversation flow

**Data collected from visitors:**
- Voice recordings (only if enabled in bot settings)
- Conversation transcripts
- Browser metadata (user agent, page URL for analytics)
- Optional: Contact info (email, phone) if explicitly shared during conversation

---

## Authentication & API Keys

- **Required:** `ANVEVOICE_API_KEY` (starts with `anvk_`)
- **Storage:** Environment variable only — never hardcoded
- **Generation:** https://anvevoice.com/developer

### ⚠️ Recommended API Key Scopes (Minimal Privilege)

| Use Case | Recommended Scope | Avoid |
|----------|-------------------|-------|
| Read analytics | `analytics:read` | - |
| Manage bots | `bots:write` | - |
| Extract leads | `leads:read` | - |
| Deploy widgets | `embed:read` | - |
| Admin access | - | `full_access` (unless necessary) |

**Best Practices:**
- Create separate keys for dev/staging/prod
- Rotate keys every 90 days
- Revoke unused keys immediately
- Monitor usage in dashboard

---

## Security Best Practices

### For Skill Users (Developers)

1. **Use environment variables:**
   ```bash
   export ANVEVOICE_API_KEY=anvk_your_key_here
   ```

2. **Never commit keys to git:**
   ```bash
   echo ".env" >> .gitignore
   ```

3. **Use minimal scope keys:**
   - Don't use "Full Access" for production
   - Create read-only keys for analytics-only use

4. **Monitor and audit:**
   - Check dashboard for unexpected usage
   - Review conversation logs periodically
   - Set up alerts for high token usage

### For Website Owners (End Users)

1. **HTTPS Required:**
   - Widget only works on HTTPS sites
   - Browsers block microphone access on HTTP

2. **Privacy Policy Requirements:**
   - Disclose voice data collection
   - Explain how recordings are used
   - Link to AnveVoice privacy policy: https://anvevoice.com/privacy
   - Describe retention period

3. **User Consent:**
   - Widget shows browser's native permission prompt
   - Users can decline and use text instead (if configured)
   - Recordings only occur after explicit permission

4. **Data Retention:**
   - Default: 30 days (configurable in dashboard)
   - Auto-deletion after retention period
   - Export before deletion if needed

---

## Compliance

| Regulation | Status | Requirements |
|------------|--------|--------------|
| **GDPR** | ✅ Compliant | Data processing agreement available; EU data stays in EU |
| **CCPA** | ✅ Compliant | California privacy rights supported |
| **HIPAA** | ⚠️ Review Required | **Contact for BAA before handling PHI** |
| **SOX/PCI** | ❌ Not Designed | Not for financial/payment card data |

**For HIPAA compliance:**
- Email: security@anvevoice.com
- Subject: "HIPAA BAA Request"
- Do not process PHI without signed BAA

---

## Data Security

| Feature | Implementation |
|---------|----------------|
| **Encryption in Transit** | TLS 1.3 for all API calls |
| **Encryption at Rest** | AES-256 (Supabase) |
| **Voice Recordings** | Stored encrypted, auto-deleted per retention |
| **API Keys** | Hashed, never logged in plain text |
| **Access Logs** | 90 days retention |

---

## Reporting Security Issues

**Responsible Disclosure:**
1. Email: security@anvevoice.com
2. Subject: `[SECURITY] Brief description`
3. Do not publicly disclose until patched
4. Response within 24 hours
5. Bug bounty program available

---

## Badge

```markdown
[![VirusTotal](https://img.shields.io/badge/VirusTotal-0%2F62%20Clean-brightgreen?style=flat-square&logo=virustotal)](https://www.virustotal.com/gui/file/f3c788a5cfa2a01b67edd6af451ee6748944818f20b7d51203ecf5cf8d4c837b?nocache=1)
```
