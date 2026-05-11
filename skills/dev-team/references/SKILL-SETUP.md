# dev_team — first-time setup (for beginners)

**Guided team setup (recommended):** Start with **[OPENCLAW_TEAM_SETUP_GUIDE.md](OPENCLAW_TEAM_SETUP_GUIDE.md)** — there: **master prompt** for OpenClaw, **variable** (Mode A/B, desired `agentId`s, roles), **phases** through routing. This page is mainly the **exact folder tree**.

**No coding required:** You need **no script**. Everything is **folders**, **Markdown**, and **`board.json`**, which **you create yourself** or have OpenClaw do. Schema: [BOARD_SCHEMA.md](BOARD_SCHEMA.md).

**Important:** `TEAM_ROOT` is the **shared team memory** (customers, tasks, handoffs) — **not** automatically your code repo. Details: [SKILL.md — OpenClaw workspace mapping](../SKILL.md#openclaw-workspace-mapping).

---

## The approach in three sentences

1. **`TEAM_ROOT`:** Pick the path on the machine where the OpenClaw gateway runs.
2. **Under `TEAM_ROOT/team/`** create exactly the folders and starter files as in **“File scaffold”** below — **no** top-level `team/tasks/` folder.
3. In your **workspace** (`AGENTS.md`), enter the same absolute `TEAM_ROOT` path ([OPENCLAW_LAYOUT.md — snippet](OPENCLAW_LAYOUT.md)); for multiple agents use the **same** path everywhere.

Then: first customer (`CONTEXT.md`) and first tasks (`customers/.../tasks/...`) — when work starts.

---

## Step 0 — Resolve `TEAM_ROOT`

| What | How to get it |
|-----|----------------|
| **`stateDir`** | Environment variable **`OPENCLAW_STATE_DIR`** if set — else **`~/.openclaw`** (Linux/macOS home `.openclaw`). |
| **`TEAM_ROOT`** | If **`DEV_TEAM_ROOT`** is set → that absolute path. **Else:** `<stateDir>/dev-team` |

**Example:** No `DEV_TEAM_ROOT`, home default → `TEAM_ROOT` = `~/.openclaw/dev-team`.

Everything we create lives under **`TEAM_ROOT/team/`** (not under `TEAM_ROOT` alone without `team`).

---

## File scaffold: create exactly like this

**Folders** (all under `TEAM_ROOT` — replace `TEAM_ROOT` with your real path):

```text
team/
├── GOALS.md              ← file (see text below)
├── DECISIONS.md          ← file
├── PROJECT_STATUS.md     ← file (short index only — see SKILL “Portfolio index”)
├── board.json            ← portfolio index (JSON), start empty — [BOARD_SCHEMA.md](BOARD_SCHEMA.md)
├── AGENTS.md             ← file (routing / which agent is which role)
├── customers/            ← empty, or later one folder per customer
│   └── (per customer: <customer_id>/CONTEXT.md and later tasks/<task_id>/)
├── shared/
│   ├── reviews/
│   └── security/
└── agents/
    ├── pm/
    ├── dev/
    ├── qa/
    ├── security/
    └── lead/
```

**Important:**

- **Do not** create `team/tasks/` at the top level. Tasks only live under `team/customers/<customer_id>/tasks/<task_id>/` when work begins ([SKILL.md — Customer context](../SKILL.md#customer-context-required-before-coding)).
- The **`team/agents/pm`** folders etc. are **role notes** in the shared tree — **not** the OpenClaw workspaces. OpenClaw workspaces live elsewhere (per `openclaw.json`).

**Minimum content** in the `team/` root (the agent can apply this as-is):

| File | Example content |
|------|-----------------|
| `GOALS.md` | `# GOALS` + short paragraph: priorities / OKRs. |
| `DECISIONS.md` | `# DECISIONS` + short paragraph: decision log with dates. |
| `PROJECT_STATUS.md` | `# PROJECT_STATUS` + **note:** **short index** only (2–5 team bullets + per active customer 1–3 lines with path to task folder). **No** long detail here — see [SKILL.md — Portfolio index](../SKILL.md#portfolio-index-project_status-and-boardjson). |
| `board.json` | Empty board per [BOARD_SCHEMA.md](BOARD_SCHEMA.md) (“Empty bootstrap”). |
| `AGENTS.md` | `# Team routing` + paragraph: which agent is PM, Dev, QA, … |

---

## Optional: `.gitignore` under `TEAM_ROOT`

If you want **`git init`** in `TEAM_ROOT`:

```gitignore
.DS_Store
.env
**/*.pem
**/secrets*
```

**Never** put real passwords or API keys in `CONTEXT.md` or other team files — only references to secret **names**.

---

## Path A — One agent (main agent, good to start)

One OpenClaw agent; you switch roles (PM, Dev, …) **in conversation**. The **on-disk layout** stays the same as above.

### A1. One message to OpenClaw

```text
I'm setting up dev_team for the first time. Read references/SKILL-SETUP.md (sections “File scaffold: create exactly like this” and “Step 0”). Under the correct TEAM_ROOT, create all folders and files at the team/ root including board.json (empty customers per BOARD_SCHEMA.md); no secrets. TEAM_ROOT = DEV_TEAM_ROOT if set, else <stateDir>/dev-team. Ask me once whether DEV_TEAM_ROOT or another path is wanted if unclear.
```

**Short variant:**

```text
Bootstrap dev_team: resolve TEAM_ROOT per SKILL, then team/ tree exactly as references/SKILL-SETUP.md “File scaffold” including board.json (BOARD_SCHEMA “Empty bootstrap”). No top-level team/tasks/.
```

### A2. Put `TEAM_ROOT` in your workspace

So the agent (and you) use the same path: add to **`AGENTS.md`** in the **OpenClaw workspace** — snippet under [OPENCLAW_LAYOUT.md](OPENCLAW_LAYOUT.md).

### A3. First customer

```text
Create team/customers/<CUSTOMER-SLUG>/CONTEXT.md from CUSTOMER_CONTEXT.template.md. No passwords in the file.
```

### A4. Role content (tone, boundaries)

Templates: [ROLE_TEMPLATES.md](ROLE_TEMPLATES.md).

---

## Path B — Multiple OpenClaw agents (real team)

1. **First** the file scaffold as above (Path A) — otherwise agents have no shared `team/`.
2. **Add** extra agents and set **`openclaw.json`** **per agent** `workspace` + `agentDir` — see [Multi-agent routing](https://docs.openclaw.ai/concepts/multi-agent).
3. **In each** new workspace: the same **`TEAM_ROOT` line** in `AGENTS.md` as [OPENCLAW_LAYOUT.md](OPENCLAW_LAYOUT.md).
4. Per agent fill **`SOUL.md` / `AGENTS.md`** with [ROLE_TEMPLATES.md](ROLE_TEMPLATES.md).
5. Update **`team/AGENTS.md`** under `TEAM_ROOT`: which real agent covers which role.

---

## Copy-paste cheat sheet

| Situation | Text |
|-----------|------|
| First install | See **A1** above. |
| New customer | See **A3** above. |
| Wording roles | `Use ROLE_TEMPLATES.md in the dev_team skill; propose SOUL/AGENTS per role.` |

---

## Common issues

| Problem | Fix |
|---------|-----|
| Agent doesn’t know `TEAM_ROOT` | Write absolute path once in **workspace `AGENTS.md`**; for a team, **identical everywhere**. |
| No shared folder between agents | Same `TEAM_ROOT` logic for all on **one** gateway host; with Docker: same mount — [Sandboxing](https://docs.openclaw.ai/gateway/sandboxing). |

---

## Further reading

- [OPENCLAW_TEAM_SETUP_GUIDE.md](OPENCLAW_TEAM_SETUP_GUIDE.md) — **walkthrough for OpenClaw** (master prompt, variables, Mode A/B)
- [ORG_CHART_EXAMPLE.md](ORG_CHART_EXAMPLE.md) — org chart (4 agents: Lead, PM, Dev, QA)
- [SKILL.md](../SKILL.md) — handoffs, Shopware, full layout diagram
- [BOARD_SCHEMA.md](BOARD_SCHEMA.md) — `board.json` for many customers
- [OPENCLAW_LAYOUT.md](OPENCLAW_LAYOUT.md)
- [CUSTOMER_CONTEXT.template.md](CUSTOMER_CONTEXT.template.md)
