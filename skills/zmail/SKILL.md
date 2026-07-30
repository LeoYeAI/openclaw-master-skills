---
name: zmail
description: >-
  Local-first email for agents: IMAP sync to maildir + SQLite (FTS5); CLI search, read, thread, who,
  attachments. Requires Node 20+, npm install (`npm install -g @cirne/zmail` or `npx @cirne/zmail`),
  native better-sqlite3 (rebuilt on first run if Node ABI mismatch), and IMAP credentials. OpenAI API
  key required for `zmail setup` / wizard, `zmail ask`, and `zmail inbox`—those features can send
  email-derived text to OpenAI. Optional `who --enrich` may call third-party search APIs. Source:
  github.com/cirne/zmail.
license: "Refer to https://github.com/cirne/zmail for project license and terms."
compatibility: >-
  Node.js 20+; npm; `zmail` on PATH after global install. Network: IMAP, OpenAI (ask/inbox/setup),
  optional enrich providers. Disk: ~/.zmail (SQLite + maildir). Native addon: better-sqlite3 (rebuilt on first run if needed).
metadata:
  version: "0.1.2"
  homepage: "https://github.com/cirne/zmail"
  repository: "https://github.com/cirne/zmail"
  openclaw:
    requires:
      bins:
        - node
        - npm
        - zmail
      config:
        - ZMAIL_EMAIL
        - ZMAIL_IMAP_PASSWORD
        - ZMAIL_OPENAI_API_KEY
---

# /zmail — agent-first email

**What zmail is:** Email reimagined for **agents and automation**—not a human-first inbox UI. It syncs mail over **IMAP**, stores messages as **files (maildir-style)** and indexes them in **local SQLite** with **FTS5**. The primary surface is the **CLI**: search, read, thread, who, attachments, and **`zmail ask`** for natural-language questions (OpenAI). Same index powers every command—queries stay **local and fast** so the assistant can treat mail like a **repository of communication artifacts** (invoices, travel, Zoom summaries, etc.) instead of paging through Gmail.

**Why use it:** Traditional webmail is slow and awkward for AI workflows. zmail’s promise is **local-first, privacy-friendly** mail you control, **agent-intuitive** commands, and room to grow toward “the agent is the interface”—plain-language prompts become searches and reads, not manual digging.

## Transparency (registries & security review)

Use this block to keep **ClawHub / OpenClaw registry fields** aligned with the skill body—avoid “no credentials required” when the CLI clearly needs secrets.

| Topic | What to declare |
|--------|------------------|
| **Provenance** | Source and issues: **[github.com/cirne/zmail](https://github.com/cirne/zmail)** |
| **Install** | **`npm install -g @cirne/zmail`** or **`npx @cirne/zmail`** (Node **20+**). Native **`better-sqlite3`**; on ABI mismatch, first **`zmail`** run rebuilds via **`ensure-better-sqlite-native`** (or run **`npm rebuild better-sqlite3`** yourself with the same `node` that runs `zmail`). |
| **On PATH** | Global npm `bin` must be on **`PATH`**, or use **`npx @cirne/zmail`** for one-off invocations. |
| **Required secrets (after setup)** | **`ZMAIL_EMAIL`**, **`ZMAIL_IMAP_PASSWORD`** (IMAP; e.g. Gmail app password). **`ZMAIL_OPENAI_API_KEY`** or **`OPENAI_API_KEY`** for setup wizard, **`zmail ask`**, **`zmail inbox`**, and optional **`zmail who --enrich`**. |
| **Privacy / data leaving the device** | **`zmail ask`**, **`zmail inbox`**, and **`who --enrich`** can send **email-derived content** (subjects, snippets, bodies, addresses) to **OpenAI** or other APIs—only use if the **mailbox owner** accepts that. Primitives **`search` / `read` / `thread` / `attachment`** (without enrich) are local index + disk only once mail is synced. |
| **Credentials on disk** | Secrets live under **`ZMAIL_HOME/.env`** (and non-secret settings in **`config.json`**). They are used only to talk to **your** IMAP host and (when configured) **OpenAI**—not to third-party analytics or the zmail project. Treat **`.env`** like any password file (permissions, backups, don’t paste into chats). |
| **IMAP / send posture** | **Read-only today:** zmail syncs and indexes mail; it does **not** implement **SMTP send** in this release. Normal sync is a **local cache** of what remains on the server—deleting local data (see below) does not remove server-side mail. |
| **MCP (optional)** | **`zmail mcp`** uses **stdio** JSON-RPC only (stdin/stdout)—**no** in-process HTTP server or listening TCP port for MCP. |
| **Persistence & local wipe** | Config and a **local** copy of mail (SQLite index + maildir cache under **`data/`**) live under **`ZMAIL_HOME`** (default **`~/.zmail`**). **`zmail setup --clean --yes`** removes that local tree and rewrites config—it does **not** delete mail on the **IMAP server**; after setup, run **`zmail sync`** to **rebuild** the local cache from IMAP. You still lose unsaved **local-only** state (e.g. extracted-attachment cache, any data not on the server). |
| **Shell safety** | Invoke **`zmail`** with **argument arrays** (or careful quoting). **Never** paste untrusted mail text or chat content into a **`sh -c "zmail …"`** string—**command-injection** risk. |

OpenClaw parses **`metadata.openclaw.requires`** per [Creating skills](https://docs.openclaw.ai/tools/creating-skills): **`bins`** = executables expected on **`PATH`** (**`zmail`** exists only **after** the global install step). **`config`** lists environment variables this workflow expects for a configured mailbox (mirror the same in ClawHub package metadata if the UI has separate fields).

---

## Agent checklist

1. Confirm **Node.js 20+** (`node -v`).
2. `npm install -g @cirne/zmail` (see [Install](#install)).
3. Choose setup: **[`zmail wizard`](#zmail-wizard-interactive-humans)** (TTY) or **[`zmail setup`](#zmail-setup-agents--automation)** (flags/env, no prompts).
4. User must have a **Gmail app password** (or compatible IMAP credentials)—[Gmail: app password](#gmail-get-an-app-password).
5. Run **`zmail sync --since …`** then **`zmail refresh`** / **`zmail status`**.
6. **Learn the CLI from the CLI:** run **`zmail`**, **`zmail --help`**, and **`zmail <command> --help`**. Read any **`hint`** (and truncation fields) in **JSON** output—zmail uses them to disclose the next capability ([Canonical docs & discovery](references/CANONICAL-DOCS.md)).
7. For questions over mail, prefer **`zmail ask`** first; use **`search` / `read` / `thread` / `who` / `attachment`** when you need fine control ([Ask vs primitives](#zmail-ask-vs-primitives)).
8. Never paste secrets into chat logs; use env or flags in the **user’s** shell.

---

## Install

```bash
node -v   # must be v20+
npm install -g @cirne/zmail
```

- If **`better-sqlite3`** fails to load (wrong Node ABI), the CLI may rebuild automatically on first run; if not, run **`npm rebuild better-sqlite3`** using the **same** `node` binary that runs `zmail`.
- **Global install note:** `npm` may install to a directory that is not on `PATH`; ensure that global `bin` is on `PATH`, or use `npx @cirne/zmail` for one-off commands.

Config and data default to **`ZMAIL_HOME`** (default **`~/.zmail`**): `config.json`, `.env`, and `data/` (SQLite + maildir).

---

## Gmail: get an app password

Gmail does **not** allow normal account passwords for IMAP clients. Use a **16‑character app password**.

1. **Turn on 2‑Step Verification** (required):  
   [Google Account → Security → 2‑Step Verification](https://myaccount.google.com/signinoptions/two-step-verification)
2. **Create an app password** (sign in with Google account):  
   [App passwords](https://myaccount.google.com/apppasswords)  
   - Choose app: **Mail** (or **Other** and name it `zmail`).  
   - Google shows a **16‑character** password (often shown in groups; enter **without spaces**).
3. Use **full Gmail address** as IMAP user (e.g. `you@gmail.com`) and the app password as **`ZMAIL_IMAP_PASSWORD`** / `--password`.

If app passwords are disabled (workspace policy, account type), the user must use whatever IMAP credentials their admin allows.

---

## `zmail wizard` (interactive humans)

- **When:** Real terminal with TTY; user is present to answer prompts.
- **Run:** `zmail wizard`  
  Optional: `--no-validate` (skip live IMAP/OpenAI checks), `--clean` (wipe local config + cached mail under `ZMAIL_HOME`; IMAP unchanged; may prompt unless `--yes`).
- **If stdin is not a TTY** (agents, CI, pipes): wizard **exits** with a message to use **`zmail setup`** instead.
- Wizard walks through email, IMAP app password, OpenAI key, default sync window, and can **start background sync** at the end.

---

## `zmail setup` (agents & automation)

**Non-interactive.** No prompts when all inputs are provided via **flags** and/or **environment variables**.

**Required today (all three):**

| Input | Flag | Environment variable |
|--------|------|----------------------|
| Email (IMAP user) | `--email` | `ZMAIL_EMAIL` |
| IMAP password (e.g. Gmail app password) | `--password` | `ZMAIL_IMAP_PASSWORD` |
| OpenAI API key | `--openai-key` | `ZMAIL_OPENAI_API_KEY` or `OPENAI_API_KEY` |

**Examples:**

```bash
zmail setup \
  --email 'user@gmail.com' \
  --password 'abcdefghijklmnop' \
  --openai-key 'sk-...'
```

```bash
export ZMAIL_EMAIL='user@gmail.com'
export ZMAIL_IMAP_PASSWORD='abcdefghijklmnop'
export ZMAIL_OPENAI_API_KEY='sk-...'
zmail setup
```

**Optional flags:**

| Flag | Meaning |
|------|--------|
| `--no-validate` | Skip IMAP and OpenAI validation (faster/offline-ish write of config only). |
| `--default-since <spec>` | Default sync window in config (e.g. `7d`, `1y`). Default if omitted: `1y`. |
| `--clean --yes` | Delete existing `config.json`, `.env`, and `data/` under `ZMAIL_HOME`, then write new config. **Local only**—IMAP mailbox unchanged; resync rebuilds the index/cache. |

If any required value is missing, `zmail setup` prints what’s missing and exits—fix env/flags and retry.

**OpenAI key:** Required for **`zmail setup`** / **`zmail wizard`** as shipped. It is stored in **`~/.zmail/.env`**. Same key powers **`zmail ask`**, **`zmail inbox`**, and related features. Search/read/thread/who/attachment **do not** need the API at query time once mail is indexed.

---

## Secrets and files (after setup)

| Secret / file | Required? | Purpose |
|---------------|-----------|---------|
| `ZMAIL_IMAP_PASSWORD` in **`.env`** | **Yes** (for sync) | IMAP login (Gmail app password). |
| `ZMAIL_OPENAI_API_KEY` (or `OPENAI_API_KEY`) in **`.env`** | **Yes** at setup; **yes** for `ask` / `inbox` | LLM features. |
| **`config.json`** | **Yes** | Non-secret: IMAP host/port/user, sync defaults (no password in this file). |
| **`ZMAIL_HOME`** | Optional | Override config root (default `~/.zmail`). |

**Security:** Treat **`.env`** like credentials—don’t commit it, don’t paste into tickets or agent transcripts. Rotate app passwords if exposed.

---

## First sync and daily use

```bash
zmail sync --since 30d    # initial backfill (often runs in background; note log path on stdout)
zmail refresh             # fetch new mail since last sync
zmail status              # local sync + index health
zmail ask "your question" # one-shot NL answer (OpenAI); good default for agents
zmail search 'query'      # FTS hits (JSON default; --text for tables)
```

- Long **`sync`:** Safe to run in background; use **`zmail status`** and the **sync log file** path the CLI prints.
- **Refresh** is the habitual “get new mail” command after the first sync.

---

## zmail ask vs primitives

**`zmail ask "<question>"`** runs zmail’s **answer pipeline** in one go: it figures out how to search and pull the right messages, then **synthesizes a complete answer** for the user. For the **calling agent**, that usually means **fewer steps** and a **ready-made summary**—best when the goal is “answer this question about my mail” rather than “give me raw hits.” Requires **`ZMAIL_OPENAI_API_KEY`** (or `OPENAI_API_KEY`). Optional **`--verbose`** if you need to trace what it did.

**Primitives** (`search`, `read`, `thread`, `who`, `attachment list` / `attachment read`) expose **structured, explicit steps**: you choose the query, which **message IDs** to open, whether you need **full body or raw**, **threads**, **contacts**, or **extracted attachment text**. They do **not** call OpenAI for the core path—good for **scripts**, **tight filters**, **verbatim quotes**, **debugging**, or when the outer agent wants to **own the reasoning** and token budget.

| Prefer **`zmail ask`** | Prefer **primitives** |
|------------------------|------------------------|
| Broad or fuzzy questions (“what did X say about the launch?”) | Exact filters, known IDs, pagination |
| You want a **single** synthesized answer quickly | You need **every** matching row or **full** message bodies |
| User asked in natural language and doesn’t care about IDs | **Attachments**, EML/raw, or **who** / address-book style lookups |

**Rule of thumb:** **Start with `ask`.** If the answer is too shallow, wrong, or you need **more detail or accuracy**, switch to **`search` → `read` / `thread`** (and **`attachment`** when documents matter). Combine both: e.g. **`ask`** for orientation, then **`read`** on specific `message_id`s from search if you must verify.

Full tradeoffs and hybrid patterns: **`docs/ASK.md`** at the package/repo root (paths in [references/CANONICAL-DOCS.md](references/CANONICAL-DOCS.md)).

---

## Install this skill folder (hosts)

Copy the **`zmail`** directory (this skill) into an **end-user** location—not into the zmail **source** repo’s `.cursor/skills/` (those are dev-only).

| Host | Typical path |
|------|----------------|
| Cursor | `~/.cursor/skills/zmail/` or another project’s `.cursor/skills/zmail/` |
| Claude Code | `~/.claude/skills/zmail/` |
| OpenClaw | `<workspace>/skills/zmail/`, `~/.openclaw/skills/zmail/`, or from this repo: **`npm run install-skill:openclaw`** ([OpenClaw creating skills](https://docs.openclaw.ai/tools/creating-skills)) |

Folder name must stay **`zmail`** to match frontmatter `name` ([Agent Skills spec](https://agentskills.io/specification.md)). Copy the **whole** `skills/zmail/` directory (includes `references/`).

### OpenClaw: heartbeat + fresh mail

For **[OpenClaw](https://docs.openclaw.ai/)**, use a **heartbeat** (not a separate cron per mailbox tick) for periodic “anything new in email?” awareness—OpenClaw’s own guide recommends heartbeat for inbox-style checks because it **batches** with other routine work and can **suppress noise** when nothing matters. See **[Cron vs heartbeat](https://docs.openclaw.ai/cron-vs-heartbeat)** and **[Heartbeat](https://docs.openclaw.ai/gateway/heartbeat)** (interval, `HEARTBEAT.md`, `HEARTBEAT_OK`, `agents.defaults.heartbeat`, etc.).

**Put zmail on the workspace `HEARTBEAT.md` checklist**, for example:

1. **Ingest new mail:** run **`zmail refresh`** (forward IMAP sync into the local index), or use **`zmail inbox <window> --refresh`** so the forward sync runs immediately before the scan (same sync path as `refresh`; optional **`--force`** if you need to skip STATUS fast-path—see **`zmail inbox --help`**).
2. **Surface what’s worth attention:** run **`zmail inbox`** over a window (e.g. **`24h`**, **`3d`**, or your **`inbox.defaultWindow`** in `config.json`) so the LLM returns **notable** recent mail in JSON (`newMail`, …). Requires **`ZMAIL_OPENAI_API_KEY`** (or `OPENAI_API_KEY`). Use **`--text`** if you want a human-readable digest. Add **`--include-noise`** only if marketing/social should count as “notable.”
3. **If nothing needs a human ping**, answer **`HEARTBEAT_OK`** so OpenClaw drops the turn quietly (per Heartbeat docs).

**Cost / habit:** `refresh` alone does **not** call OpenAI; **`inbox`** does. Keep the checklist short; widen the inbox window only when needed.

---

## More detail

- [references/CANONICAL-DOCS.md](references/CANONICAL-DOCS.md) — **CLI-first discovery** (`zmail`, `--help`, per-command help), **hints in output**, and a **table of canonical markdown** (`AGENTS.md`, `docs/VISION.md`, `docs/ASK.md`, `docs/ARCHITECTURE.md`, `docs/MCP.md`, OPP-025).
