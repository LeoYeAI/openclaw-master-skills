# API Validation Troubleshooting Guide

Quick reference for fixing validation failures during Prediction Stack setup.

## REQUIRED SERVICES — Must Fix Before Proceeding

### Kalshi API Validation Fails

#### Error: "Authentication failed: Check API key and private key file"

**Diagnosis:** Your API credentials are invalid or mismatched.

**Fix steps:**
1. Log in at https://kalshi.com/settings/api
2. Check if you have an active API key (should show key ID)
3. If not, generate a new one
4. Download the private key file
5. Save it to `~/.openclaw/keys/kalshi-secret.pem`
6. Verify permissions: `chmod 600 ~/.openclaw/keys/kalshi-secret.pem`
7. Update `~/.openclaw/config.yaml`:
   ```yaml
   kalshi:
     enabled: true
     api_key_id: "YOUR_KEY_ID_FROM_KALSHI"
     private_key_file: "~/.openclaw/keys/kalshi-secret.pem"
   ```
8. Rerun: `python validate_setup.py --kalshi-only`

---

#### Error: "Network error: Cannot reach Kalshi API"

**Diagnosis:** Network connectivity issue or Kalshi API is down.

**Fix steps:**
1. Check internet connection: `ping 8.8.8.8`
2. Check if Kalshi is down: https://status.kalshi.com
3. If your network requires a proxy, configure it in config.yaml:
   ```yaml
   kalshi:
     http_proxy: "http://proxy.company.com:8080"
   ```
4. Try from a different network (phone hotspot) to isolate the issue
5. Rerun: `python validate_setup.py --kalshi-only`

---

#### Error: "File not found: Check private_key_file path in config"

**Diagnosis:** The path to your private key doesn't exist.

**Fix steps:**
1. Check file exists: `ls -la ~/.openclaw/keys/kalshi-secret.pem`
2. If not found, download it from https://kalshi.com/settings/api again
3. Paste into file:
   ```bash
   nano ~/.openclaw/keys/kalshi-secret.pem
   # Paste your private key (should start with -----BEGIN PRIVATE KEY-----)
   # Press Ctrl+O, Enter, Ctrl+X to save
   ```
4. Verify: `cat ~/.openclaw/keys/kalshi-secret.pem | head -5`
5. Check permissions: `chmod 600 ~/.openclaw/keys/kalshi-secret.pem`
6. Rerun: `python validate_setup.py --kalshi-only`

---

### Anthropic (Claude) API Validation Fails

#### Error: "Invalid or expired API key"

**Diagnosis:** Your API key is invalid, expired, or incorrectly formatted.

**Fix steps:**
1. Go to https://console.anthropic.com/account/keys
2. Check if you have any active keys (not revoked or expired)
3. If not, click "Create New Key"
4. Copy the full key (looks like `sk-ant-...`)
5. Update `~/.openclaw/config.yaml`:
   ```yaml
   anthropic:
     api_key: "sk-ant-YOUR_NEW_KEY_HERE"
   ```
   OR set as environment variable:
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-YOUR_NEW_KEY_HERE"
   ```
6. Verify: `echo $ANTHROPIC_API_KEY` (should show your key, not empty)
7. Rerun: `python validate_setup.py --verbose`

---

#### Error: "Network error: Cannot reach Anthropic API"

**Diagnosis:** Network connectivity issue or Anthropic API is down.

**Fix steps:**
1. Check internet connection: `ping api.anthropic.com`
2. Check if Anthropic is down: https://status.anthropic.com
3. Try from a different network
4. Check for proxy requirements
5. Rerun: `python validate_setup.py --verbose`

---

#### Error: "Rate limited: Try again in a moment"

**Diagnosis:** You've made too many API calls recently.

**Fix steps:**
1. Wait 60 seconds
2. Rerun: `python validate_setup.py`

(This is rarely a problem during initial setup.)

---

## OPTIONAL SERVICES — Can Proceed Without

These services enhance the stack but aren't required. If validation fails, the stack will work with reduced functionality.

### Polygon.io API Validation Fails

**Impact:** Kalshalyst estimates will lack recent news context. Estimates will still work (uses Claude alone).

**To fix (optional):**
1. Sign up at https://polygon.io (free tier works)
2. Navigate to your dashboard → API Keys
3. Copy your API key
4. Add to `~/.openclaw/config.yaml`:
   ```yaml
   polygon:
     api_key: "pk_YOUR_KEY_HERE"
   ```
5. Rerun: `python validate_setup.py`

**To skip this service:** Remove or set to empty:
```yaml
polygon:
  api_key: ""
```

---

### Ollama (Qwen) Validation Fails

**Impact:** Kalshalyst will use Claude for all estimates (higher cost). No offline fallback.

**To fix (optional):**

If error is "Ollama not running on localhost:11434":
1. Install Ollama: https://ollama.ai
2. Start the server: `ollama serve`
3. In another terminal, download model: `ollama pull qwen3:latest`
4. Rerun: `python validate_setup.py`

If error is "Model 'qwen3:latest' not found":
1. Download the model: `ollama pull qwen3:latest`
2. Verify it installed: `ollama list`
3. Rerun: `python validate_setup.py`

**To skip this service:** Disable in config:
```yaml
ollama:
  enabled: false
```

---

### Polymarket API Validation Fails

**Impact:** Prediction Market Arbiter skill won't find cross-platform divergences. Less useful but still runs.

**To fix (optional):**
1. Polymarket API is public (no auth needed)
2. If it fails, Polymarket infrastructure is likely down
3. Try again in 5 minutes
4. Check: https://gamma-api.polymarket.com/markets (should return JSON)

**To skip this service:** This is read-only/public, so there's nothing to configure. If Polymarket is down, we can't fix it.

---

## Advanced Diagnostics

### Run with verbose output to see actual API responses:
```bash
python validate_setup.py --verbose
```

### Test only one service:
```bash
python validate_setup.py --kalshi-only
```

### Check what config the script is reading:
```python
from scripts.validate_setup import load_config
import json
config = load_config()
print(json.dumps(config, indent=2))
```

### Test Kalshi manually:
```bash
export KALSHI_KEY_ID="your-key-id"
export KALSHI_KEY_PATH="/path/to/private.key"
python -c "from kalshi_python import Configuration, KalshiClient; c = Configuration(); c.api_key_id = os.getenv('KALSHI_KEY_ID'); print('✅ Client created')"
```

### Test Claude manually:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python -c "from anthropic import Anthropic; c = Anthropic(); m = c.messages.create(model='claude-3-5-sonnet-20241022', max_tokens=10, messages=[{'role':'user','content':'OK'}]); print('✅ Response:', m.content[0].text)"
```

### Check network connectivity:
```bash
# Kalshi
curl -I https://api.kalshi.com/

# Anthropic
curl -I https://api.anthropic.com/

# Polygon.io
curl -I https://api.polygon.io/

# Ollama
curl -I http://localhost:11434/api/tags

# Polymarket
curl -I https://gamma-api.polymarket.com/markets
```

---

## Summary of Common Fixes

| Service | Most Common Issue | Fix |
|---------|------------------|-----|
| Kalshi | Private key path wrong | Update `private_key_file` path in config |
| Claude | Invalid API key | Get new key from console.anthropic.com |
| Polygon | Not configured | Sign up free at polygon.io, add key to config |
| Ollama | Server not running | Run `ollama serve` in background |
| Polymarket | Usually network | Wait, check status, try again |

---

## Next Steps After Validation Passes

Once all required services show ✅ PASS:

1. **Proceed to Phase 3:** iMessage Delivery Setup
2. **Create cron jobs:** Phase 4 (scheduled tasks)
3. **Launch:** Phase 5 (enable heartbeat)
4. **Monitor:** Phase 6 (verify everything)

If you're still stuck, check the full troubleshooting section in the main SKILL.md.
