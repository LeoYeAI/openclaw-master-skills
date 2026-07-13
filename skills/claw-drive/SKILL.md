---
name: claw-drive
description: "Claw Drive — AI-managed personal drive for OpenClaw. Auto-categorize, tag, deduplicate, and retrieve files with natural language. Backed by Google Drive for cloud sync and security. Use when receiving files to store, or when asked to find/retrieve a previously stored file."
homepage: https://github.com/dissaozw/claw-drive
metadata:
  {
    "openclaw":
      {
        "emoji": "📂",
        "requires": { "bins": ["claw-drive"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "dissaozw/tap/claw-drive",
              "bins": ["claw-drive"],
              "label": "Install Claw Drive (brew)",
            },
          ],
      },
  }
---

# Claw Drive

Organize and retrieve personal files with auto-categorization and a searchable index.

## ⚠️ Privacy — Read This First

**File contents are personal data. Treat them accordingly.**

- **NEVER read file contents without explicit user consent.** Always ask first. Always.
- **If the user doesn't reply → default to SENSITIVE.** Silence = no consent.
- **`identity/` files are ALWAYS sensitive** — never read, never extract, never log contents.
- **Extracted content enters the conversation transcript** which is logged permanently to `.jsonl` files. Once you read a file, its contents are in the logs forever.
- **Descriptions in INDEX.jsonl are also persistent.** Don't put sensitive details (SSNs, account numbers, passwords) in descriptions even for non-sensitive files — use redacted/partial forms (e.g. "account ending ****4321").
- **When in doubt, don't read.** A vague index entry is better than leaked personal data.

**Data locality:** All data stays on your machine. INDEX.jsonl, stored files, and hash ledger are local. Conversation transcripts (`.jsonl`) are also local to your OpenClaw instance. Nothing is sent to external servers unless you explicitly enable Google Drive sync (optional, and only syncs the files you choose).

## Dependencies

- **claw-drive CLI** — `brew install dissaozw/tap/claw-drive` (or `make install` from skill directory for manual setup)
- **pymupdf** — PDF text extraction (`uv run --with pymupdf` — no global install needed)
- **rclone** — Google Drive sync (optional): `brew install rclone`
- **fswatch** — file watch daemon (optional): `brew install fswatch`

## ⚠️ CLI Usage — Read This Before Running Anything

**ALWAYS use the `claw-drive` CLI. NEVER use `cp`, `mv`, or direct file writes to `~/claw-drive/`.**

The CLI handles copying, hashing, deduplication, and index updates atomically. Bypassing it causes:
- Files stored without hash registration → dedup breaks silently
- INDEX.jsonl out of sync with actual files
- Version confusion when replacing files

**PATH note:** If installed via Homebrew (`brew install dissaozw/tap/claw-drive`), the binary is in `/opt/homebrew/bin/` and should be in PATH automatically. If installed manually, `~/.local/bin` may not be in the agent shell's PATH — use the full path:
```bash
claw-drive store ...
```
If the manual symlink is broken, re-run `make install` from `~/.openclaw/skills/claw-drive/` to fix it.

## Setup

```bash
claw-drive init [path]
```

This creates the directory structure, INDEX.jsonl, and hash ledger. Default path: `~/claw-drive`.

## Workflow

### Storing a file

When receiving a file (email attachment, Telegram upload, etc.):

1. **Privacy check** — ask the user gracefully if the file contains sensitive/personal data:
   - Something like: "Should I read the contents to index it better, or would you prefer I keep it private and just use the filename?"
   - **If user says sensitive**, or **if user doesn't reply** → treat as **sensitive** (default-safe)
   - **If user confirms it's fine to read** → proceed with full extraction
   - Files going to `identity/` are **always sensitive** — never read contents
   - Sensitive flow: classify by filename/metadata only. If that's not enough for a good description, ask the user for a brief description. Never read file contents into the conversation.

2. **Extract** (normal files only) — read file contents:
   - **PDFs:** extract text via `uv run --with pymupdf python3 -c "import pymupdf; ..."` or use the image tool
   - **Images:** use the image tool to read/describe contents
   - **Other formats:** read directly if possible
   - Pull out key entities: names, dates, amounts, account/policy numbers, addresses, etc.
3. **Classify** — determine the best category from the categories table below
4. **Inspect category structure** — after choosing a category, examine existing subfolders in that category (e.g. with `tree`/`find`) before finalizing destination
5. **Choose destination path**
   - If an existing subfolder is a clear semantic match, store there
   - If multiple existing subfolders could match (conflicting/ambiguous), store at category root
   - Store at category root when the file is only generally related to the category and lacks specific detail
   - Create a new subfolder only when no existing subfolder fits and the file has clear specific detail that justifies one
6. **Name** — choose a descriptive filename: `<subject>-<detail>-<YYYY-MM-DD>.<ext>`
7. **Describe** — write a rich description using extracted content (or user-provided description for sensitive files). Include key details (dates, amounts, IDs, names) so the file is findable by any relevant search term. Don't be vague — "insurance card" is bad, "Acme Insurance ID cards - 2024 Honda Civic, Policy ****3441, effective 1/21/2026–7/21/2026" is good.
8. **Tag** — include specific tags from extracted content (model names, policy numbers, VINs, entity names) in addition to category tags
9. **Store** — run the CLI (use full path if `claw-drive` not in PATH):
   ```bash
   claw-drive store <file> --category <cat> --name 'clean-name.ext' --desc 'Rich description with key details' --tags 'tag1, tag2' --source telegram
   ```
   - **Shell quoting safety:** Prefer single quotes for `--desc`/`--tags`/`--name` when constructing shell commands. This avoids `$` expansion (e.g. currency amounts like `$941.39`) and prevents metadata corruption.
   ⚠️ **Do NOT use `cp` or write files directly to `~/claw-drive/`.** The CLI is the only correct way to store files — it handles copying, hashing, dedup, and index updates atomically.
10. **Report** — tell the user: path, category, tags, key extracted details, and what was indexed

The CLI handles copying, hashing, deduplication, and index updates automatically. If the file is a duplicate, it will be rejected.

The `--name` flag lets you override the original filename (which may be ugly like `file_17---8c1ee63d-...`) with a clean, descriptive name.

### Retrieving a file

**Do NOT read INDEX.jsonl directly in the main session.** Spawn a search sub-agent instead. This keeps the index out of your context window and scales to large file collections.

#### Why sub-agent?

The index grows with every stored file (~300 bytes/entry). At 1000+ files, reading the full index into the main agent's context wastes tokens and may hit context limits. A sub-agent runs in its own isolated session with a cheap model, reads the index, and returns only the matching entries.

#### How to spawn

Use `sessions_spawn` with:
- `mode`: `run`
- `model`: A lightweight model is recommended (the search task is simple). Resolution order:
  1. Explicit `model` param on `sessions_spawn` (if provided)
  2. `agents.defaults.subagents.model` in config (if set)
  3. Falls back to the main agent's model
- `task`: The prompt below, with the user's query filled in

```
You are a file search agent. Read ~/claw-drive/INDEX.jsonl and find entries matching this query:

"<USER_QUERY>"

Return ONLY valid JSON, no explanation:

{
  "matches": [
    {
      "path": "<path from index>",
      "desc": "<desc from index>",
      "date": "<date from index>",
      "tags": ["<tags from index>"],
      "confidence": "high|medium|low"
    }
  ],
  "total_indexed": <number of entries in index>,
  "query": "<original query>"
}

Rules:
- Max 5 matches, sorted by relevance
- confidence: high = exact match, medium = likely relevant, low = tangential
- If no matches, return {"matches": [], "total_indexed": N, "query": "..."}
- Only read INDEX.jsonl, never read file contents
```

#### Receive and deliver

1. The sub-agent auto-announces its result back to your session
2. Parse the JSON from the announce message
3. Prepend `~/claw-drive/` to each `path` to get the full file path
4. **Send the file:** The claw-drive directory may not be in the message tool's allowed paths. If sending fails with "not under an allowed directory", copy the file to a temp location first (e.g. workspace), send it, then clean up:
   ```bash
   cp ~/claw-drive/<path> ~/.openclaw/workspace/
   # send via message tool
   rm ~/.openclaw/workspace/<filename>
   ```
5. **Never show raw sub-agent JSON to the user.** The announce message is internal — immediately process it and deliver the file. The user should only see the file and a brief description, not search internals.
6. For multiple matches, send the most relevant one and list the rest — let the user pick

#### Troubleshooting: pairing required

If `sessions_spawn` returns `pairing required`, the sub-agent's exec harness needs device pairing approval. Run:

```bash
openclaw devices list        # find the pending request
openclaw devices approve <request-id>
```

This is a one-time setup — once approved, subsequent spawns work without re-pairing.

#### Index format

INDEX.jsonl is a JSONL file — one JSON object per line. Each entry has: `date`, `path`, `desc`, `tags` (array), `source`, and optional fields `metadata` (JSON), `original_name`, `correspondent`.

### Updating an entry

```bash
claw-drive update <path> --desc "new description" --tags "new, tags"
```

Both `--desc` and `--tags` are optional (at least one required). Uses `jq` for atomic rewrite.

### Deleting a file

```bash
claw-drive delete <path> --force
```

Without `--force`, shows what would be deleted (dry run). With `--force`, removes file + index entry + dedup hash.

### Tagging

Tags add cross-category searchability. A file lives in one folder but can have multiple tags.

**Guidelines:**
- 1-5 tags per file, comma-separated
- Lowercase, single words or short hyphenated phrases
- Always include the category name as a tag (e.g. `medical` for files in `medical/`)
- Add cross-cutting tags for things like: entity names (`my-cat`), document type (`invoice`, `receipt`, `report`), context (`emergency`, `tax-2025`)
- Reuse existing tags when possible — read INDEX.jsonl to see existing tags before inventing new ones

**Examples:**
```bash
# Insurance PDF — after extracting: policy number, vehicle, VIN, dates, agent
claw-drive store file.pdf -c insurance -n "acme-auto-id-cards.pdf" \
  -d "Acme Insurance ID cards - 2024 Honda Civic, VIN 1HGBH41JXMN109186, Policy ****3441, effective 1/21/2026–7/21/2026, agent Jane Smith (555) 123-4567" \
  -t "insurance, auto, acme, id-card, honda-civic, california" -s telegram

# Vet invoice — after extracting: clinic, amount, diagnosis, pet name
claw-drive store invoice.pdf -c medical -n "my-cat-vet-invoice-2026-02-15.pdf" \
  -d "VEG emergency visit invoice - Max (cat), $1,234.56, bronchial pattern diagnosis, prednisolone prescribed" \
  -t "medical, invoice, max, emergency, vet" -s email

# W-2 — after extracting: employer, tax year, wages
claw-drive store w2.pdf -c finance -n "w2-2025.pdf" \
  -d "W-2 tax form 2025 - Employer: Acme Corp, wages $120,000" \
  -t "finance, tax-2025, w2" -s email

# Sensitive file — user said "keep it private" or didn't reply
claw-drive store scan.pdf -c identity -n "passport-scan-2026.pdf" \
  -d "Passport scan" \
  -t "identity, passport" -s telegram

# Sensitive file — user provided brief description
claw-drive store doc.pdf -c contracts -n "apartment-lease-2026.pdf" \
  -d "Apartment lease agreement, signed Jan 2026" \
  -t "contracts, lease, housing" -s email
```

### Naming conventions

- Lowercase, hyphens between words: `my-cat-vet-invoice-2026-02-15.pdf`
- Include date when relevant
- Include subject/entity name for clarity
- Keep it human-readable — no UUIDs or timestamps

### Categories

Categories are **not fixed** — the agent can create any category that makes sense. The CLI does `mkdir -p` automatically. These are the defaults created by `init`, but use whatever fits:

| Category | Use for |
|----------|---------|
| documents | General docs, letters, forms, manuals |
| finance | Tax returns, bank statements, investment docs, pay stubs |
| insurance | Insurance policies, claims, coverage documents |
| medical | Health records, lab results, prescriptions, pet health |
| travel | Boarding passes, itineraries, hotel bookings, visas |
| identity | Passport scans, birth certs, SSN docs (⚠️ sensitive) |
| receipts | Purchase receipts, warranties, service invoices |
| contracts | Leases, employment agreements, legal docs |
| photos | Personal photos, document scans |
| misc | Anything that doesn't fit above |

Need `housing/`, `work/`, `pets/`? Just use it — the directory is created on first store.

**When in doubt:** `misc/` is fine. Better to store it somewhere than not at all.

## Migration

Bulk-import files from an existing directory:

```bash
# 1. Scan source directory into a plan
claw-drive migrate scan ~/messy-folder plan.json

# 2. Agent classifies each file (fills in category, name, tags, description in the JSON)

# 3. Review
claw-drive migrate summary plan.json

# 4. Dry run
claw-drive migrate apply plan.json --dry-run

# 5. Execute
claw-drive migrate apply plan.json
```

The plan JSON contains one entry per file with `category`, `name`, `tags`, `description` fields (initially null). The agent fills these in using the same extract-first approach, then `apply` copies files with full dedup and indexing.

## Sync (Optional)

Claw Drive can auto-sync to Google Drive (or any rclone-supported backend) via a background daemon.

### Prerequisites

```bash
brew install rclone fswatch
```

### Authorization

Run `claw-drive sync auth`. It opens a browser on the machine for Google sign-in.

**What happens:**
- rclone requests **Google Drive file access only** (not full Google account)
- OAuth token is stored locally at `~/.config/rclone/rclone.conf` — never sent to any third party
- Data flows directly from your machine to Google Drive — no intermediary servers
- You can revoke access anytime via Google Account → Security → Third-party apps

**Agent behavior during auth:**
1. Run `claw-drive sync auth` in background
2. Try the OpenClaw browser tool to click through the Google consent screen
3. If browser tool is unavailable, send the auth URL to the user and ask them to complete sign-in on the machine (e.g. via Screen Sharing)
4. Wait for rclone to capture the token

### Commands

```bash
claw-drive sync setup   # verify deps and config
claw-drive sync start   # start background daemon (fswatch + rclone)
claw-drive sync stop    # stop daemon
claw-drive sync push    # manual one-shot sync
claw-drive sync status  # show sync status
```

The daemon watches the drive directory for file changes and syncs to the remote within seconds. It runs as a launchd service — starts on login, restarts on failure.

Logs: `~/Library/Logs/claw-drive/sync.log`

### Per-category privacy

Use the `exclude` list in `.sync-config` to keep sensitive directories local-only. `identity/` is excluded by default.

## Verify

Check index ↔ disk ↔ hash consistency:

```bash
claw-drive verify          # report issues
claw-drive verify --fix    # auto-repair what's fixable
```

**Auto-fixable:** missing on disk (removes stale index entry), missing hash (re-registers).
**Manual review:** orphan files (no metadata to index), hash mismatches (possible corruption).

Run `verify` after manual file operations or when something seems off.

## Tips

- The CLI maintains INDEX.jsonl automatically — don't edit it manually
- PDF text extraction: `uv run --with pymupdf python3 -c "import pymupdf; ..."`
- Use `claw-drive status` to see file counts, size, and sync status

## Privacy Checklist (every store)

Before storing any file, verify:

- [ ] Did I ask the user about privacy? (not optional)
- [ ] If no reply: am I treating it as sensitive? (must be yes)
- [ ] If sensitive: am I skipping content extraction? (must be yes)
- [ ] If `identity/`: am I skipping extraction regardless? (must be yes)
- [ ] Are there SSNs, full account numbers, or passwords in my description? (must be no)
- [ ] Would I be comfortable if this INDEX.jsonl entry leaked? (must be yes)
