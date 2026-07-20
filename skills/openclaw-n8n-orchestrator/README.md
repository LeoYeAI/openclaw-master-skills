# openclaw-n8n-orchestrator v2

A Claude Skill for building secure integrations between OpenClaw agents and n8n workflow automation. Generates production-ready OpenClaw skill directories with proper YAML frontmatter, Security Manifests, shell injection mitigation, and ClawHub publishing compliance.

## What Changed from v1

**v2 fixes ten critical gaps** identified from deep research into OpenClaw's skill architecture:

1. **Correct skill format** — Generates proper skill directories with `SKILL.md` + YAML frontmatter (v1 used the wrong `.mmd` format)
2. **YAML frontmatter compliance** — `metadata.clawdbot` namespace, `requires.env` (singular), `files` declarations, single-line values only
3. **Security Manifest Headers** — Every script declares env vars, endpoints, files accessed (required by ClawHub scanners)
4. **Shell injection mitigation** — `urllib.parse.quote` sanitization, `--data-urlencode`, Node.js alternative (v1 had raw string interpolation)
5. **`set -euo pipefail`** — Non-negotiable strict error handling in all bash scripts
6. **Mandatory transparency sections** — External Endpoints, Security & Privacy, Model Invocation Note, Trust Statement
7. **ClawHub publishing pipeline** — `clawhub` CLI authentication, packaging, automated security scans, version management
8. **Node.js trigger template** — Zero-dependency, zero shell injection surface (Node.js 22+ always available in OpenClaw)
9. **System hardening** — `exec.approval: true`, `soul.md` guardrails, multi-model cost routing
10. **SkillPointer pattern** — Scales 20+ webhook skills from ~8,000 startup tokens to ~200

## Skill Architecture

```
openclaw-n8n-orchestrator-v2/
├── SKILL.md                              ← Core orchestration logic (341 lines)
├── references/
│   ├── deployment.md                     ← Docker Compose, topologies, env vars
│   ├── gateway-api.md                    ← Gateway endpoints, WebSocket, payloads
│   ├── security.md                       ← Shell injection, ClawHavoc, hardening
│   ├── n8n-claw-architecture.md          ← Supabase, RAG, MCP Builder
│   └── publishing.md                     ← NEW: ClawHub pipeline, security scans
├── templates/
│   ├── skill-template-SKILL.md           ← NEW: Proper YAML frontmatter template
│   ├── trigger-template.sh               ← NEW: Sanitized bash trigger
│   ├── trigger-template.js               ← NEW: Node.js trigger (zero injection surface)
│   └── docker-compose.yml                ← Co-located stack
└── scripts/
    └── validate_integration.py           ← NEW: Validates YAML, manifests, injection patterns
```

## Five Operating Modes

1. **Egress** — Generate OpenClaw skill directories that trigger n8n webhooks
2. **Ingress** — Configure n8n → OpenClaw Gateway data injection
3. **Bidirectional** — Full proxy orchestration with credential isolation
4. **n8n-claw** — Agent rebuilt entirely inside n8n + Supabase + Claude
5. **Publish** — Package and publish skills to ClawHub registry
