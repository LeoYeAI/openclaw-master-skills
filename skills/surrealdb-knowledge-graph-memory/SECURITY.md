# Security Notes — SurrealDB Knowledge Graph Memory

This document explains what this skill does, what access it requires, and what to review before enabling each feature. Read this before installing.

---

## What This Skill Does (Summary)

| Behavior | Expected? | Opt-out? |
|----------|-----------|----------|
| Reads `MEMORY.md` and `memory/*.md` and sends content to OpenAI | ✅ Yes — required for extraction | Disable extraction cron or keep files secrets-free |
| Generates vector embeddings via OpenAI API | ✅ Yes — required for semantic search | Disable auto-injection in Mode UI |
| Injects facts into the agent system prompt on each turn | ✅ Yes — the core memory feature | Toggle in Mode UI → Memory section |
| Registers 2 cron jobs in the main agent session | ⚠️ Expected but elevated | Disable via OpenClaw cron manager |
| Patches OpenClaw source files via sed | ❌ Optional / not default | Only runs with `--apply` flag |
| Runs `curl \| sh` to install SurrealDB | ❌ Not recommended | Use `--skip-surreal` and install manually |
| Uses default credentials `root/root` | ⚠️ Dev only | Change before any networked deployment |

---

## Required Credentials

| Variable | Required | Purpose |
|----------|----------|---------|
| `OPENAI_API_KEY` | **Yes** | Embeddings (text-embedding-3-small) + fact extraction (GPT-4) |
| `SURREAL_USER` | No (default: root) | SurrealDB auth — change from default |
| `SURREAL_PASS` | No (default: root) | SurrealDB auth — change from default |
| `SURREAL_URL` | No (default: localhost:8000) | SurrealDB connection |

No AWS, GCP, Azure, or unrelated credentials are requested.

---

## Required Binaries

- `surreal` — SurrealDB server (local, binds to localhost)
- `python3` (>=3.10)
- `pip` packages: `surrealdb`, `openai`, `pyyaml`

---

## Detailed Risk Notes

### 1. Memory Files Sent to OpenAI

`scripts/extract-knowledge.py` reads your memory files and sends their content to OpenAI for LLM-based fact extraction and embedding generation.

**What gets sent:** `MEMORY.md` and all `memory/YYYY-MM-DD.md` files in your workspace.

**What to do before enabling:**
- Audit those files for any secrets, API keys, passwords, or private data
- If you find secrets, remove them from the files before running extraction
- Consider using a minimal-scope OpenAI key for this purpose

### 2. Auto-Injection Modifies the System Prompt

When enabled, `memory_inject` is called on every user message and the result is appended to the agent system prompt. This means the knowledge graph contents directly influence agent behavior.

**What to do:** Review what's in the knowledge graph (`mcporter call surrealdb-memory.knowledge_stats`) before enabling auto-injection. Start with a low `max_facts` limit (3–5) and increase once you're comfortable.

### 3. Cron Jobs in Main Session

Two cron jobs are registered in the main agent session:
- **Extraction** (every 6h): reads memory files → sends to OpenAI → stores facts
- **Relation discovery** (daily 3 AM): queries graph → asks LLM to find relationships

Both run as `systemEvent` in `sessionTarget: "main"`. This means they fire in your primary agent session and can read workspace files and contact external APIs on a schedule.

**What to do:** After installation, verify both jobs in the OpenClaw cron manager. Disable either or both if you want to run extraction manually first.

### 4. Source Patching (Optional)

`scripts/integrate-openclaw.sh` uses `sed` to patch OpenClaw source files to add the Memory UI tab. **This is entirely optional** — the MCP server and extraction scripts work without it.

**Default behavior:** The script runs in dry-run mode and prints what it would do. Nothing is changed unless you pass `--apply`.

**If you do apply:**
- Automatic backups are created for each patched file
- You should have a clean git commit before running
- Test on a development copy of OpenClaw before applying to production

### 5. SurrealDB Network Installer

`scripts/install.sh` can run `curl -sSf https://install.surrealdb.com | sh`. This is a network script piped to your shell.

**Recommendation:** Do NOT use this path. Install SurrealDB manually from the official releases: https://surrealdb.com/install

Use `./install.sh --skip-surreal` to install only the Python dependencies without touching SurrealDB.

### 6. Default Credentials

SurrealDB is configured with `root/root` by default. This is fine for a local dev instance bound to `127.0.0.1`, but should be changed immediately for:
- Any deployment on a shared machine
- Any deployment accessible on a network
- Production use

---

## Recommended Setup Checklist

- [ ] Install SurrealDB manually (not via curl|sh)
- [ ] Bind SurrealDB to `127.0.0.1` only
- [ ] Change default `root/root` credentials
- [ ] Audit `MEMORY.md` and `memory/*.md` for secrets before enabling extraction
- [ ] Use a minimal-scope OpenAI key
- [ ] Enable extraction cron and verify it runs once manually before scheduling
- [ ] Enable auto-injection only after reviewing knowledge graph contents
- [ ] If applying the integration script, run `--dry-run` first and review all diffs
- [ ] Have a git backup of OpenClaw source before running `--apply`
