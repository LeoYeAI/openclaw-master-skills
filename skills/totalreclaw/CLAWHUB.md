# ClawHub Publishing

Internal notes for publishing the TotalReclaw skill on [clawhub.ai](https://clawhub.ai).

## Published

- **Published:** 2026-03-26
- **Version:** 1.4.0
- **Package ID:** k978pv4b9nyrx4bt968vqyzpa983mbx3
- **URL:** https://clawhub.ai/skills/totalreclaw

---

## How ClawHub Works

ClawHub is the official skill registry for OpenClaw agents. Key facts:

- **SKILL.md IS the listing page** — the full markdown body is rendered as the listing content
- **Publishing is instant via CLI** — no manual review queue
- **Automated security scan runs post-publish** — flags suspicious patterns, undeclared env vars, dynamic code execution
- **No screenshots/video hosted on ClawHub** — embed as markdown image links in SKILL.md if desired
- **Discovery via vector search** — embedding similarity + slug/name boosts + popularity prior

---

## Readiness Status

### Published (v1.4.0, 2026-03-26)

- [x] `skill.json` — Metadata, hooks, tools, config, and ClawHub fields populated
- [x] `SKILL.md` — YAML frontmatter with full metadata; tools, hooks, prompts, and LLM instructions documented
- [x] `README.md` — Public-facing documentation with quick start, benchmarks, configuration, and architecture
- [x] Hooks defined: `before_agent_start`, `agent_end`, `pre_compaction`
- [x] Tools defined: `totalreclaw_remember`, `totalreclaw_recall`, `totalreclaw_forget`, `totalreclaw_export`, `totalreclaw_status`, `totalreclaw_generate_recovery_phrase`
- [x] Environment variables documented (`TOTALRECLAW_SERVER_URL`, `TOTALRECLAW_RECOVERY_PHRASE`)
- [x] Benchmark comparison table (98.1% recall@8 with 100% privacy)
- [x] License declared (MIT)
- [x] Keywords and OS compatibility specified
- [x] E2E onboarding tests passing (4/4)
- [x] E2E subgraph tests passing (9/9)

### Not Yet Done

- [ ] **Screenshots** (optional — linked from external hosting as markdown images in SKILL.md)
  - Suggested:
    1. Agent remembering a user preference (tool call + response)
    2. Agent recalling memories at conversation start (context injection)
    3. Memory export in JSON format
    4. Encryption in action (showing encrypted vs plaintext data)
- [ ] **Demo video** (optional, 30-90 seconds)
  - Show a full cycle: store a memory, start a new conversation, recall it automatically
  - Highlight that the server never sees plaintext

---

## SKILL.md Frontmatter

Ensure the SKILL.md starts with this frontmatter for ClawHub:

```yaml
---
name: TotalReclaw
description: "End-to-end encrypted memory for AI agents — portable, yours forever. AES-256-GCM E2EE. One recovery phrase, full portability."
version: 1.4.0
metadata:
  openclaw:
    requires:
      env:
        - TOTALRECLAW_SERVER_URL
        - TOTALRECLAW_RECOVERY_PHRASE
    primaryEnv: TOTALRECLAW_RECOVERY_PHRASE
    emoji: "\U0001F9E0"
    homepage: https://totalreclaw.xyz
    os: ["macos", "linux", "windows"]
---
```

---

## Publish Command

```bash
# Login
clawhub login

# Publish (update version as needed)
clawhub publish ./skill \
  --slug totalreclaw \
  --name "TotalReclaw" \
  --version 1.4.0 \
  --tags latest,memory,encryption,e2ee,e2e-encryption,privacy,agent-memory,persistent-context \
  --changelog "v1.4.0: ClawHub as primary install method, LLM-guided dedup, dual-chain billing, Qwen3-Embedding-0.6B."
```

---

## Security Scan Notes

The `TOTALRECLAW_RECOVERY_PHRASE` env var will likely trigger extra scrutiny from the automated security scanner. The E2EE architecture explanation in SKILL.md should help it pass as `clean`:

- The password is a 12-word BIP-39 mnemonic used to derive encryption keys
- It never leaves the client device
- The server only ever receives encrypted blobs
- All crypto code is open-source and auditable

---

## Competitor Context

ClawHub has one similar listing: **Everclaw** (also AES-256-GCM encrypted cloud memory, ~2,959 downloads). It is flagged as `suspicious` by the moderation system. TotalReclaw differentiates by:

- Fully open-source (server + client)
- On-chain data anchoring (Gnosis Chain + The Graph)
- Seed-phrase portability (no accounts)
- Competitive benchmark data (98.1% recall@8)
- Clean security scan (no suspicious patterns)

---

## Post-Publishing

- **Version updates**: Bump version in `skill.json` and SKILL.md frontmatter, then `clawhub publish` again
- **Monitor**: Check downloads, stars, and comments on the listing
- **Respond to feedback**: Monitor the ClawHub listing for user comments
