# OpenClaw × `dev_team` — guided team setup (variable)

This file is for **you** and for **OpenClaw**: you get **placeholders** and **copy-paste prompts** so the agent can **walk you through** setup — without memorizing all the docs.

**For the OpenClaw assistant:** OpenClaw does **not** automatically know how **your** team is structured or how each agent should behave — that is not stored in the gateway, only in this skill as **structure** and **examples**. You **must** ask the user about anything unclear (roles, responsibilities, workflow, control plane). Do **not** silently adopt Lead/PM/Dev/QA or the org chart unless the user confirms that or has already filled in the table under §1.

**See also:** [SKILL-SETUP.md](SKILL-SETUP.md) (folder tree), [OPENCLAW_LAYOUT.md](OPENCLAW_LAYOUT.md) (paths), [ROLE_TEMPLATES.md](ROLE_TEMPLATES.md) (role text), [Org chart](ORG_CHART_EXAMPLE.md).

Official multi-agent reference (CLI / `openclaw.json`): [Multi-agent routing](https://docs.openclaw.ai/concepts/multi-agent).

---

## 1) Fill in briefly (optional but helpful)

Before you send the **master prompt**, you can note values here — otherwise OpenClaw should collect them **by asking**.

| Variable | Your value / example |
|----------|----------------------|
| `MODE` | **A** = single OpenClaw agent (switch roles in chat) · **B** = multiple real OpenClaw agents |
| `DEV_TEAM_ROOT` | Empty = default `<stateDir>/dev-team` · **or** absolute path if the admin sets one |
| `ROLE_LIST` | e.g. `lead, pm, dev, qa` — optionally add `security` |
| `AGENT_IDS` | e.g. `lead, pm, dev, qa` — OpenClaw **`agentId`**, lowercase, no spaces |
| `DISPLAY_NAMES` | e.g. Lead “Ria”, PM “Paul”, … (for SOUL/identity) |
| `CONTROL_CHANNEL` | e.g. “one Telegram bot”, “Discord”, “Cursor only” — how **you** interact |
| `TEAM_WORKFLOW` (optional) | Short: who hands off to whom? One thread vs. separate chats? Handoff expectations? |

If `TEAM_WORKFLOW` and roles are open → **OpenClaw should ask**, not guess.

---

## 2) Master prompt for OpenClaw (send this first)

**Copy in full** — the agent should work through the phases below and **ask for gaps**:

```text
Setup assistant for the dev_team skill (multi-agent dev team with TEAM_ROOT and board.json).

Work step by step and follow references/OPENCLAW_TEAM_SETUP_GUIDE.md in this skill.

Steps:
0) You have no preset for how my team should work or how agents should behave — this skill only gives structure/examples. Do not invent a role split without my answers. If I provide nothing: ask explicitly whether I want to follow ORG_CHART_EXAMPLE.md in the skill or need a custom role set; ask about workflow (handoffs, who triggers whom).
1) Ask me in order if still unclear: MODE A (one agent) or B (multiple agents)? Desired roles and agentIds (slugs)? Optional custom DEV_TEAM_ROOT path? Control channel? Short: expected workflow between roles?
2) Then: explain TEAM_ROOT logic and create the file scaffold under TEAM_ROOT/team/ like SKILL-SETUP “File scaffold” — including board.json (BOARD_SCHEMA empty bootstrap). Do not write secrets.
3) MODE A: how I use roles in the same chat; add TEAM_ROOT snippet from OPENCLAW_LAYOUT to workspace AGENTS.md.
4) MODE B: table agentId → dev_team role → next config steps; link official OpenClaw multi-agent docs; do NOT output real tokens/secrets; placeholders only in examples.
5) Point to ROLE_TEMPLATES for SOUL/AGENTS per role; fill team/AGENTS.md routing.
6) Finally: short checklist “what the user must still do manually” (gateway restart, channel login, openclaw.json — as applicable).

After each major step, briefly confirm what you created (paths).
```

---

## 3) Phases in detail (logical for OpenClaw)

### Phase A — Clarify variables

**Rule:** Technical variables (mode, paths) **and** **team semantics** come from the user — OpenClaw **asks** instead of silently defaulting to the org-chart example.

OpenClaw should **at least** know:

- **MODE A or B** (one vs. multiple agents).
- **Which roles** the user **actually** wants — not auto Lead/PM/Dev/QA; note that [ROLE_TEMPLATES](ROLE_TEMPLATES.md) and [ORG_CHART_EXAMPLE](ORG_CHART_EXAMPLE.md) are only **templates**.
- **How collaboration should run:** roughly who does SPEC/review/handoff, one channel or several, whether the user switches roles in language only (A) or uses separate sessions (B).
- **Which `agentId`s** (MODE B only) — slugs, consistent with routing in **team/agents/** notes; name them **after** roles are clear.

### Phase B — `TEAM_ROOT` + `team/` scaffold

Same content as [SKILL-SETUP — File scaffold](SKILL-SETUP.md#file-scaffold-create-exactly-like-this).  
OpenClaw **creates** or **instructs** the user — always **without** passwords in files.

**Short prompt for scaffold only** (if the master prompt already ran):

```text
Bootstrap only the dev_team file scaffold: references/SKILL-SETUP.md section “File scaffold” + board.json (BOARD_SCHEMA empty). TEAM_ROOT = DEV_TEAM_ROOT or <stateDir>/dev-team. Confirm the absolute TEAM_ROOT path.
```

### Phase C — Mode **A** (one agent)

OpenClaw explains: switch roles **in language** (“Now as PM …”); all use the **same** `TEAM_ROOT` line in the **single** workspace `AGENTS.md`.

**Add-on prompt:**

```text
MODE A (one agent): Insert the TEAM_ROOT block from OPENCLAW_LAYOUT.md into my workspace AGENTS.md (fill in path). Explain in 3 bullet points how I switch PM/Dev/QA in conversation.
```

### Phase D — Mode **B** (multiple OpenClaw agents)

OpenClaw does **not** ship a production-ready `openclaw.json` with real secrets — but:

- Table **`agentId` → role (dev_team) → workspace job** (board, SPEC, HANDOFF, QA).
- Note: **`openclaw agents add`**, **`bindings`**, optionally **channel per agent** — all in [Multi-agent routing](https://docs.openclaw.ai/concepts/multi-agent).
- Optional: **JSON5 sketch** with **placeholders** only for `workspace` paths and no tokens.

**Add-on prompt for the user:**

```text
MODE B: I want these OpenClaw agents: {{AGENT_ID_1}}={{ROLE_1}}, {{AGENT_ID_2}}={{ROLE_2}}, …
Build the mapping table to dev_team ROLE_TEMPLATES and a numbered list of what I must run/configure on the gateway (openclaw.json / CLI per current OpenClaw docs). Do not output secrets.
```

Replace `{{…}}` with your values or answer the agent’s questions.

### Phase E — Role text + `team/AGENTS.md`

- Per workspace (MODE B) or once (MODE A): take sections from [ROLE_TEMPLATES.md](ROLE_TEMPLATES.md) and fill in **names**.
- **`TEAM_ROOT/team/AGENTS.md`**: record **which real agent** covers which **dev_team** role (@-tags, bot name, session routing).

**Add-on prompt:**

```text
From ROLE_TEMPLATES.md for my roles {{ROLES}}, produce a compact SOUL and AGENTS section each (Markdown to copy). Update TEAM_ROOT/team/AGENTS.md with routing: who is PM/Dev/QA/Lead.
```

---

## 4) After setup — typical first customer

```text
Create team/customers/<CUSTOMER-SLUG>/CONTEXT.md from CUSTOMER_CONTEXT.template.md. Do not put passwords in the file.
```

---

## 5) What OpenClaw **cannot** decide alone

- **Who has which role and how collaboration runs** — that comes from **user answers**; the skill only gives examples, not automatic truth.
- **Real** bot tokens, OAuth, pairing — you or your admin do that on the gateway.
- **Sandbox / tool rights** per agent — `openclaw.json`, see [Multi-agent sandbox & tools](https://docs.openclaw.ai/tools/multi-agent-sandbox-tools).

---

## Links inside the skill

- Master prompt and phases: **this file**.
- Folder details: [SKILL-SETUP.md](SKILL-SETUP.md).
- Visual overview: [ORG_CHART_EXAMPLE.md](ORG_CHART_EXAMPLE.md).
