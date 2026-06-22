# Virtual Desktop — Configuration

## noVNC Access

After setup, open Chrome Desktop from your browser:

```
URL      : https://YOUR_VPS_IP:6901
Login    : kasm_user
Password : your VNC_PW (set in .env)
```

To find your VPS IP:
```bash
curl -s ifconfig.me
```

## Required .env Variables

Add these to your OpenClaw `.env` file before running setup:

```bash
VNC_PW=YourSecurePassword        # noVNC access password
BROWSER_CDP_URL=http://browser:9222
CAPSOLVER_API_KEY=               # optional — enables autonomous CAPTCHA solving
BROWSERBASE_API_KEY=             # optional — enables residential proxy + stealth
```

## Initial Login — Once Per Platform

Open Chrome via noVNC and log in to all platforms you want the agent to access.
Sessions are saved automatically in the Docker volume `browser-profile`.
They survive container restarts and remain valid indefinitely.

## Session Expired

The agent will notify you via Telegram with the noVNC link.
Reconnect, log in again, reply DONE. The agent resumes immediately.

## Enable CapSolver (Autonomous CAPTCHA)

```bash
# 1. Create account at https://capsolver.com
# 2. Add to .env:
CAPSOLVER_API_KEY=your_key_here
# ~$0.001 per CAPTCHA solved
```

Supported: reCAPTCHA v2/v3, hCaptcha, Cloudflare Turnstile, AWS WAF

## Enable Browserbase (Residential Proxy + Stealth)

```bash
# 1. Create account at https://browserbase.com
# 2. Free tier: 1 concurrent session, 1h/month
# 3. Add to .env:
BROWSERBASE_API_KEY=your_key_here
```

Use when a site blocks your VPS:
```bash
openclaw browser --browser-profile browserbase open https://blocked-site.com
```

## Reset Sessions

```bash
CONTAINER=$(docker ps --format '{{.Names}}' | grep openclaw | head -1)
docker volume rm browser-profile
# Restart only the browser container
docker compose up -d --no-deps browser
# Log in again via noVNC
```

## Change noVNC Password

```bash
# In your .env file:
VNC_PW=NewSecurePassword
# Restart only the browser container — OpenClaw keeps running
docker compose up -d --no-deps browser
```

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
✅ capsolver       (if key configured)
✅ browserbase     (if key configured)
✅ claude_vision   (if ANTHROPIC_API_KEY present)
```

## Open Port 6901

If noVNC is not accessible, open port 6901 (TCP) in your VPS firewall/security group.
