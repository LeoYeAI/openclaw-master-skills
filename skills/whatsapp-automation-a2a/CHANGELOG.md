# Changelog

All notable changes to the **MoltFlow Skills** package are documented here.

---

## [2.16.2] - 2026-03-02

### Added
- **Channel discover + import** — 2 new MCP tools: discover_channels, import_channel (8 channel tools total)
- **channels.py** — added `discover` and `import` CLI commands
- **erc8004-agent.json** — updated to 15 mcpTools (was 13)
- **Help page, llms.txt, llms-full.txt, blog post** — all surfaces updated with discover/import endpoints

---

## [2.16.0] - 2026-03-02

### Added
- **WhatsApp Channels (v7.0)** — 6 MCP tools: list_channels, get_channel, create_channel, delete_channel, broadcast_channel_post, schedule_channel_post
- **channels.py utility script** — CLI for channel management (broadcast, schedule, sync, capabilities check)
- **moltflow-outreach/SKILL.md** — Channel broadcasting section with endpoints, plan limits, and examples
- **GET /channels/capabilities** — WAHA version check endpoint for media broadcast compatibility

---

## [2.15.1] - 2026-02-22

### Fixed
- **OpenClaw "Suspicious" classification resolved** — `requiredEnv` now correctly declares `MOLTFLOW_API_KEY` (was empty `[]`, contradicting `primaryEnv`)
- Removed `optionalEnv` field — LLM API key is configured via the MoltFlow web dashboard, never passed through this skill
- Updated metadata JSON to match `requiredEnv` declaration
- Clarified description: documentation-only package, zero executables, MOLTFLOW_API_KEY is the only credential
- **MCP server endpoint fixes** — corrected 6 wrong API paths discovered during comprehensive testing:
  - `list_monitored_groups`: `groups/monitored` → `groups`
  - `add_monitored_group`: `groups/monitored` → `groups`
  - `get_current_usage`: `usage` → `usage/current`
  - `get_plan_limits`: `usage/limits` → `usage/current`
  - `list_chats`: session_id moved from query param to path param
  - `get_chat_messages`: corrected path and added missing session_id parameter
- Synced all sub-skill versions to 2.15.1

---

## [2.15.0] - 2026-02-20

### Added
- New MCP tool `moltflow_get_group_messages`: retrieve paginated messages from a monitored WhatsApp group, including AI analysis results (intent, lead_score, confidence, reason) when AI monitoring is enabled
- AI Group Intelligence support: messages returned by the tool include `ai_analysis` fields populated by the Phase 91 AI analysis pipeline
- Documentation updates in SKILL.md, moltflow-leads/SKILL.md, and moltflow/SKILL.md reflecting the new tool and AI analysis fields

---

## v2.14.6 (2026-02-19)

### Fixed
- **Republished both ClawHub slugs** — legacy `whatsapp-automation-a2a` was showing "Skill not found"
- **Restored correct display names** per v2.14.4 convention (no ERC-8004 in titles)

---

## v2.14.4 (2026-02-19)

### Changed
- **Updated both ClawHub display names** for better search discoverability
  - `whatsapp-automation-a2a` — "WhatsApp Automation — No Meta API | Bulk Send, Lead Mining, AI Outreach & Scheduled Campaigns"
  - `moltflow-whatsapp` — "WhatsApp AI Agent — No Meta API | Lead Mining, Smart Replies, Bulk Campaigns & Scheduled Reports"
- Dropped MoltFlow/ERC-8004 from titles — unfamiliar to most users
- Restored `whatsapp-automation-a2a` search visibility (was missing after v2.14.1)

---

## v2.14.1 (2026-02-19)

### Fixed
- **ClawHub "suspicious" classification resolved** — rewrote moltflow-onboarding from agent personality instructions to a read-only analysis tool
- Removed "BizDev Agent" framing from onboarding skill and main SKILL.md description
- Onboarding skill now explicitly read-only — all write endpoints moved to referenced skill modules
- Removed inline Phase 4 write endpoints and Phase 5 settings configuration from onboarding
- All safety guardrails preserved (disable-model-invocation, explicit user approval, scoped API keys)

---

## v2.14.0 (2026-02-18)

### Changed
- **Renamed skill** — "WhatsApp Ultimate — No Meta API | Lead Mining, Bulk Send, Scheduled Reminders & Follow-ups"
- Highlights the key differentiator: no Meta Business API required

---

## v2.13.0 (2026-02-18)

### Fixed
- **17 production bugs** fixed across API, MCP server, frontend, and workers
- WAHA HMAC signature verification now uses raw bytes (was re-serializing, never matched)
- Checkout 202 response no longer corrupts auth tokens
- A2A import crash on fresh Docker builds (missing source file)
- Bulk send distributed lock prevents duplicate message delivery
- MCP sanitizer boundary marker escape prevents prompt injection breakout
- Login rate limit atomic pipeline prevents permanent user lockout
- Admin suspend user now persists to DB (was hardcoded property)
- ORM decrypted fields no longer risk plaintext flush to encrypted columns
- Stripe webhook construct_event wrapped in asyncio.to_thread
- Timezone-aware datetime mismatches on timezone-naive columns

### Changed
- API version bumped to v2.0.0
- MCP server version bumped to v2.0.0
- OpenAI Actions version bumped to v2.0.0

---

## v2.12.3 (2026-02-17)

### Added
- **Business use case scenarios** across all sub-skills — real-world examples for healthcare, real estate, e-commerce, restaurants, agencies, and more
- **12 vertical-specific prompts** in main SKILL.md "Just Ask Claude" section replacing generic examples
- **GDPR + Analytics prompts** added to main skill showcase

### Fixed
- Replaced hardcoded scheduled message date with future date

---

## v2.12.0 (2026-02-17)

### Changed
- Cleaned up documentation wording for ClawHub review compliance
- Removed internal implementation details from public API docs
- Simplified data access descriptions across all sub-skills

## v2.11.4 (2026-02-16)

### Fixed
- Fixed ERC-8004 explorer URLs to include `/ethereum/` path segment across all files

## v2.11.3 (2026-02-15)

### Fixed
- Reverted Setup and Security sections to v2.10.2 wording for ClawHub review compatibility

## v2.11.0 (2026-02-15)

### Added
- **ERC-8004 Agent Registration** — MoltFlow registered as Agent #25477 on Ethereum mainnet
- ERC-8004 section in SKILL.md with registry details and discovery URLs
- New keywords: `erc8004`, `ethereum-agent`, `on-chain-agent`

---

## v2.10.1 (2026-02-14)

### Added
- **New code samples** — CRM pipeline updates, bulk group operations, CSV export, campaign controls
- **Delivery tracking** added to Platform Features table
- **Comparison table** total updated to 90+ endpoints

### Changed
- Removed scripts section (scripts will move to dedicated repo)

---

## v2.9.8 (2026-02-14)

### Changed
- **Integrations.md cleaned up** — simplified to setup guide links and security notes only
- **Changelog consolidated** — removed verbose patch-level entries

### Security
- **Documentation-only package** — zero executables, zero install scripts, zero local file writes
- **Scoped API keys enforced** — all examples use minimum required scopes; wildcard keys never recommended
- **Conversation context gated** — API returns HTTP 403 until tenant explicitly opts in at Settings > Account > Data Access
- **High-privilege endpoints removed from skill docs** — only consumer-facing API endpoints documented; administrative operations available on website only
- **Model invocation disabled** — `disable-model-invocation: true` prevents autonomous agent actions; all operations require explicit user invocation
- **Anti-spam safeguards documented** — reciprocity checks, burst rate limits, and content safeguards apply to all outbound messages

---

## v2.9.7 (2026-02-14)

### Changed
- **Code samples reordered** — campaign analytics, real-time delivery tracking (SSE), and engagement leaderboard moved to top of main SKILL.md
- **Admin skill streamlined** — focused on auth, API keys, billing, usage, and tenant settings
- **Restored integrations.md** — clean version with setup guide links and security notes

---

## v2.9.0 (2026-02-14)

### Added
- Campaign analytics endpoints documentation (Pro+ plans)
- Contact engagement scoring and leaderboard
- Send time optimization heatmap
- 3 new MCP tools for analytics

### Changed
- Display name updated for search discoverability
- Documentation refined for security best practices
- All marketing language clarified for accuracy
- Package reduced to documentation-only (zero executables)

---

## v2.8.6 (2026-02-14)

### Changed
- **Least-privilege API keys** — `scopes` is now required when creating API keys; presets available (Messaging, Outreach, Read Only)
- **403 errors include required scopes** — `X-Required-Scopes` header tells callers exactly which scopes they need

---

## v2.8.0 (2026-02-13)

### Added
- **Scheduled Reports** — 10 report templates with WhatsApp delivery support
- Reports API (8 endpoints): templates, create, list, get, update, pause, resume, delete
- `reports:read` and `reports:manage` scopes

### Changed
- Platform features table updated with reports
- Outreach module now includes scheduled reports

---

## v2.7.0 (2026-02-13)

### Changed
- Documentation restructured for clarity — "What This Skill Reads, Writes & Never Does" section
- Privacy documentation expanded with opt-in requirements and explicit "never does" list
- Security section expanded — anti-spam safeguards, content safeguards, approval mode

---

## v2.4.0 (2026-02-13)

### Added
- **AI Agent Integrations** — setup guides for Claude Desktop, Claude.ai Web, Claude Code, and ChatGPT
- Remote MCP gateway documentation (`apiv2.waiflow.app/mcp`)

---

## v2.0.0 (2026-02-12)

### Highlights

- **Scheduled Messages** — One-time, daily/weekly/monthly, or custom cron. Timezone-aware. Pause, resume, cancel. Full execution history.
- **Bulk Messaging** — Broadcast to custom groups with ban-safe throttling. Real-time SSE progress. Pause/resume/cancel mid-flight.
- **Custom Groups** — Build targeted contact lists from WhatsApp conversations. Import members, export CSV/JSON.
- **Lead Management** — Leads with full pipeline tracking. Bulk operations, CSV/JSON export.
- **Knowledge Base (RAG)** — Upload PDF/TXT, semantic search with embeddings. AI uses your docs for accurate answers.
- **Voice Transcription** — Whisper-powered voice message transcription with async task queue.
- **90+ API Endpoints** — Complete platform coverage across 6 modules.

### Added

- Scheduled Messages API (9 endpoints)
- Bulk Send API (7 endpoints)
- Custom Groups API (10 endpoints)
- Leads API (8 endpoints)
- Knowledge Base / RAG API (4 endpoints)
- Voice Transcription API (3 endpoints)
- Sub-skills: moltflow-outreach, moltflow-leads, moltflow-admin

---

## v1.6.0 (2026-02-11)

### Highlights

- **Anti-Spam Protection** — Reciprocity checks, burst rate limiting, and health monitoring on all outbound messages.
- **Yearly Billing** — Lock in yearly pricing at $239.90/year.
- **4 Focused Sub-Skills** — Core, AI, A2A, and Reviews modules.

---

## v1.0.0 (2026-02-06)

### Highlights

- **All-in-One WhatsApp API** — Sessions, messaging, groups, labels, webhooks, AI replies, reviews, and A2A unified under a single skill.
- **Agent-to-Agent Protocol** — JSON-RPC 2.0 with end-to-end encryption.
- **AI That Learns Your Voice** — Build style profiles from conversation context. Auto-replies sound like you.
- Full API reference with curl examples across 6 modules.

---

*Built with care by the [MoltFlow](https://waiflow.app) team.*
