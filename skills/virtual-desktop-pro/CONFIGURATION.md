# Virtual Desktop — Configuration

## noVNC Access

After setup, open Chrome Desktop from any browser:

```
URL      : https://YOUR_VPS_IP:6901
Login    : kasm_user
Password : your VNC_PW (set in .env)
```

To find your VPS IP:
```bash
curl -s ifconfig.me
```

---

## Required .env Variables

```bash
VNC_PW=YourSecurePassword          # noVNC access password — use something strong
BROWSER_CDP_URL=http://browser:9222
```

## Optional .env Variables

```bash
CAPSOLVER_API_KEY=                 # Autonomous CAPTCHA solving (~$0.001/solve)
BROWSERBASE_API_KEY=               # Residential proxy + stealth
ANTHROPIC_API_KEY=                 # Claude Vision (reuse existing key if already set)
VPS_IP=                            # Your VPS public IP — used in Telegram notifications
PROXY_URL=                         # Custom proxy: http://user:pass@host:port
```

---

## Initial Login — Once Per Platform

1. Open `https://YOUR_VPS_IP:6901` in your browser
2. Log in with `kasm_user` / your `VNC_PW`
3. Chrome Desktop opens — log in to every platform you want the agent to access
4. Sessions are saved automatically in Docker volume `browser-profile`
5. They survive container restarts and remain valid indefinitely

---

## Session Expired

The agent detects session expiry and notifies you via Telegram with the noVNC link.
Open noVNC, log in again, reply DONE. The agent resumes immediately.

---

## Enable CapSolver (Autonomous CAPTCHA)

```bash
# 1. Create account at https://capsolver.com
# 2. Add to .env:
CAPSOLVER_API_KEY=your_key_here
```

Supported types: reCAPTCHA v2/v3, hCaptcha, Cloudflare Turnstile, AWS WAF

Cost: ~$0.001 per CAPTCHA solved.

---

## Enable Browserbase (Residential Proxy + Stealth)

```bash
# 1. Create account at https://browserbase.com
# 2. Free tier: 1 concurrent session, 1h/month
# 3. Add to .env:
BROWSERBASE_API_KEY=your_key_here
```

Use when a site blocks your VPS IP:
```bash
openclaw browser --browser-profile browserbase open https://blocked-site.com
```

---

## Reset Sessions

If you want to clear all saved sessions and start fresh:

```bash
CONTAINER=$(docker ps --format '{{.Names}}' | grep openclaw | head -1)
docker volume rm browser-profile
# Restart only the browser container — OpenClaw keeps running
docker compose up -d --no-deps browser
# Log in again via noVNC
```

---

## Change noVNC Password

```bash
# In your .env file:
VNC_PW=NewSecurePassword
# Restart only the browser container
docker compose up -d --no-deps browser
```

---

## Firewall — Restrict Port 6901

Port 6901 (noVNC) should be restricted to your IP only.

**Hostinger:** Panel → VPS → Firewall → Add rule → TCP 6901 → Your IP only

**SSH tunnel (alternative — no open port needed):**
```bash
ssh -L 6901:localhost:6901 user@YOUR_VPS_IP
# Then open http://localhost:6901
```

---

## Verify Everything is Running

```bash
CONTAINER=$(docker ps --format '{{.Names}}' | grep openclaw | head -1)
docker ps | grep -E "openclaw|browser"
curl -s http://localhost:9222/json | head -3
docker exec "$CONTAINER" \
  python3 /data/.openclaw/workspace/skills/virtual-desktop/browser_control.py status
```

Expected output:
```
✅ playwright
✅ chrome_cdp
✅ screenshots_dir
✅ audit_file
✅ capsolver       (if CAPSOLVER_API_KEY set)
✅ browserbase     (if BROWSERBASE_API_KEY set)
✅ claude_vision   (if ANTHROPIC_API_KEY set)
```

---

## Open Port 6901

If noVNC is not accessible from your browser, open port 6901 (TCP) in your VPS firewall.

**Hostinger:** Panel → VPS → Firewall → Add rule → TCP 6901 → restrict to your IP only

**SSH tunnel (recommended — no open port needed):**
```bash
ssh -L 6901:localhost:6901 user@YOUR_VPS_IP
# Then open http://localhost:6901
```
