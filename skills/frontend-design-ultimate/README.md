# Frontend Design Ultimate

🎨 Create distinctive, production-grade static sites with React, Tailwind CSS, and shadcn/ui — no mockups needed.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![ClawHub](https://img.shields.io/badge/ClawHub-frontend--design--ultimate-purple)](https://clawhub.ai/skills/frontend-design-ultimate)

## What is this?

An OpenClaw/Claude Code skill that generates bold, memorable web designs from plain text requirements. No Figma, no wireframes — just describe what you want.

**Key Features:**
- 🚫 **Anti-AI-slop** — Explicit guidance to avoid generic designs (no Inter, no purple gradients, no centered layouts)
- 📱 **Mobile-first patterns** — Responsive CSS that actually works
- ⚡ **Two workflows** — Vite (pure static) or Next.js (Vercel deploy)
- 🧩 **shadcn/ui components** — 10 common components pre-installed, add more with CLI
- 📦 **Single-file bundling** — Bundle entire sites to one HTML file

## Quick Start

### Install the Skill

```bash
# OpenClaw
openclaw skill install frontend-design-ultimate

# Claude Code (copy to .claude/skills/)
git clone https://github.com/kesslerio/frontend-design-ultimate-clawhub-skill.git ~/.claude/skills/frontend-design-ultimate
```

### Use It

Just describe what you want:

```
Build a SaaS landing page for an AI writing tool. Dark theme, 
editorial typography, subtle grain texture. Pages: hero with 
animated demo, features grid, pricing table, FAQ accordion, footer.
```

The skill will:
1. Commit to a bold aesthetic direction
2. Choose distinctive typography (no Inter!)
3. Build with React + Tailwind + shadcn/ui
4. Apply mobile-first responsive patterns
5. Output production-ready code

## What Makes This Different?

### vs. Generic AI Design
| Generic AI | This Skill |
|------------|------------|
| Inter font everywhere | Distinctive typography choices |
| Purple gradients | Context-appropriate palettes |
| Centered layouts | Intentional spatial composition |
| No animations | Orchestrated motion |
| Solid backgrounds | Atmospheric textures |

### Based On
- **Anthropic's frontend-design** — Design philosophy, anti-AI-slop guidance
- **Anthropic's web-artifacts-builder** — React+Tailwind+shadcn scaffolding
- **Community frontend-design-v2** — Mobile-first responsive patterns

## Workflows

### Option A: Vite (Pure Static)
```bash
bash scripts/init-vite.sh my-site
cd my-site
npm run dev

# Build
npm run build

# Bundle to single HTML
bash scripts/bundle-artifact.sh
```

### Option B: Next.js (Vercel)
```bash
bash scripts/init-nextjs.sh my-site
cd my-site
npm run dev

# Deploy
vercel
```

## Documentation

- [SKILL.md](SKILL.md) — Main skill instructions
- [references/design-philosophy.md](references/design-philosophy.md) — Anti-AI-slop manifesto
- [references/mobile-patterns.md](references/mobile-patterns.md) — Responsive CSS patterns
- [references/shadcn-components.md](references/shadcn-components.md) — Component quick reference
- [templates/site-config.ts](templates/site-config.ts) — Editable content config example

## Requirements

- Node.js 18+
- npm

## License

Apache 2.0 — See [LICENSE](LICENSE)

## Credits

Built on the shoulders of:
- [Anthropic's Claude Skills](https://github.com/anthropics/skills)
- [shadcn/ui](https://ui.shadcn.com)
- [Tailwind CSS](https://tailwindcss.com)
- [nhatmobile1's frontend-design-v2](https://github.com/nhatmobile1/claude-skills)

---

Made with 🎨 by [Kessler.io](https://kessler.io)
