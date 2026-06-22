# virtual-desktop

🖥️ **Full Computer Use layer for OpenClaw v3 — authenticated, anti-bot, vision-enabled**

## Ce que ça fait

Donne à Wesley un Chrome Desktop complet, authentifié, anti-bot, avec vision IA.
Si un humain peut le faire dans Chrome, Wesley peut le faire — 24h/24, sans toi.

## 3 moteurs combinés

- **OpenClaw browser (CDP natif)** — commandes directes, token-efficient
- **browser_control.py (Playwright)** — logging AUDIT.md, workflows JSON, CAPTCHA auto
- **Claude Vision** — analyse screenshots, images IA, comprend les layouts visuels

## Nouvelles fonctionnalités v3

- ✅ **CAPTCHA automatique** — CapSolver résout reCAPTCHA/hCaptcha/Turnstile seul
- ✅ **Proxy résidentiel** — Browserbase pour bypasser Cloudflare/DataDome
- ✅ **Vision Claude** — analyse n'importe quelle image ou page web

## Setup

Wesley exécute `virtual_desktop.setup` — installe tout, notifie le principal.
Principal se connecte une fois via noVNC. Sessions sauvegardées à vie.

## Clés optionnelles (dans .env)

```
CAPSOLVER_API_KEY=xxx     → CAPTCHA autonome (~0.001$/résolution)
BROWSERBASE_API_KEY=xxx   → proxy résidentiel + stealth (free tier dispo)
```

## Auteur

Georges Andronescu (Wesley Armando) — Veritas Corporate
