# 🗄️ Claw Drive

**Google Drive stores your files. Claw Drive understands them.**

[![License: MIT](https://img.shields.io/badge/License-MIT-ffd60a?style=flat-square)](https://opensource.org/licenses/MIT)
[![macOS](https://img.shields.io/badge/macOS-supported-0078d7?logo=apple&logoColor=white&style=flat-square)](https://www.apple.com/macos/)
[![Shell](https://img.shields.io/badge/Shell-bash-4EAA25?logo=gnubash&logoColor=white&style=flat-square)](https://www.gnu.org/software/bash/)
[![CI](https://github.com/dissaozw/claw-drive/actions/workflows/ci.yml/badge.svg)](https://github.com/dissaozw/claw-drive/actions/workflows/ci.yml)

<p align="center">
  <img src="assets/demo-before.png" width="480" alt="Before: navigating 7 layers of folders">
  <br><em>😩 Before — 7 layers deep, 3 "final" versions</em>
</p>

<p align="center">
  <img src="assets/demo-after.png" width="480" alt="After: one message in Telegram, file returned instantly">
  <br><em>✨ After — one sentence, file in hand</em>
</p>

Claw Drive is an AI-managed personal drive. It auto-categorizes your files, tags them for cross-cutting search, deduplicates by content, and retrieves them in natural language — all backed by Google Drive for cloud sync and security.

**Privacy is not a feature — it's the foundation.** Your agent never reads file contents without asking. If you don't respond, it defaults to private. Sensitive categories like `identity/` are never read, never synced. Your data stays yours.

## Features

- 📂 **Auto-categorize** — files sorted into the right folder without you thinking about it
- 🏷️ **Smart tagging** — cross-category search (a vet invoice is both `medical` and `invoice`)
- 🔍 **Natural language retrieval** — "find my cat's vet records" just works
- 🧬 **Content-aware dedup** — SHA-256 hash check prevents storing the same file twice
- ☁️ **Google Drive sync** — optional real-time backup via fswatch + rclone
- 🔒 **Privacy-first** — local-first by default, sensitive categories excluded from sync, default-safe content handling
- 🛡️ **Sensitive file protection** — agent asks before reading contents; defaults to private if no reply
- 📋 **Custom metadata** — attach structured data (expiry dates, policy numbers, amounts) to any file
- 👤 **Correspondent tracking** — record who sent or issued each file
- 🔄 **Reindex** — batch re-enrich old files as your agent gets smarter
- 📛 **Original name tracking** — renames are recorded, both names searchable
- 🤖 **AI-native** — designed for [OpenClaw](https://github.com/openclaw/openclaw) agents, with a CLI under the hood

## Install

### Homebrew (recommended)

```bash
brew install dissaozw/tap/claw-drive
claw-drive init
```

### As an OpenClaw Skill

Clone into your OpenClaw skills directory — OpenClaw picks it up automatically on the next session:

```bash
git clone https://github.com/dissaozw/claw-drive.git ~/.openclaw/skills/claw-drive
cd ~/.openclaw/skills/claw-drive
make install   # symlinks claw-drive to ~/.local/bin (or PREFIX=/usr/local make install)
claw-drive init
```

That's it. Your agent will see the skill and can start storing files immediately.

> **Updating:** `cd ~/.openclaw/skills/claw-drive && git pull`

### Optional: Google Drive Sync

```bash
brew install rclone fswatch   # sync dependencies
claw-drive sync auth          # one-time — opens browser for Google auth
claw-drive sync start         # start background sync daemon
```

### Optional: PDF Extraction

PDF content extraction uses [PyMuPDF](https://pymupdf.readthedocs.io/) via `uv` — no global install needed. It runs automatically when the agent stores a PDF with content reading enabled.

## Usage

Claw Drive is designed to be used through your AI agent. You don't organize files — your agent does.

### Storing files

Send a file to your agent (Telegram, email, etc.) and it handles everything:

1. **Asks about privacy** — "Should I read the contents, or keep it private?"
2. **Extracts content** (if permitted) — reads PDFs, images, docs to pull out key details
3. **Categorizes** the file into the right folder
4. **Names** it with a descriptive, date-stamped filename
5. **Checks for duplicates** by content hash
6. **Tags** it for cross-category search with specific identifiers
7. **Indexes** it in INDEX.jsonl with a rich, searchable description
8. **Reports** back what it did

> 📎 *"Here's my auto insurance card"*
>
> 🔒 *"Should I read the contents to index it better, or keep it private?"*
>
> 👤 *"Go ahead"*
>
> ✅ Stored: `insurance/acme-auto-id-cards.pdf`
> Policy ****3441 · 2024 Honda Civic · Effective 1/21/2026–7/21/2026
> Tags: insurance, auto, acme, honda-civic, california

If you don't reply or say it's sensitive, the agent classifies by filename only and asks for a brief description if needed. Your data is never read without consent.

### Retrieving files

Just ask in natural language:

> *"Find my cat's medical records"*
> *"Show me all invoices from January"*
> *"Do I have a copy of my W-2?"*

The agent reads INDEX.jsonl directly — its semantic understanding beats any grep. It finds files by meaning, not string matching.

### What you never have to do

- Pick a folder
- Think of a filename
- Remember where you put something
- Manually organize anything

## CLI Reference

The CLI handles **write operations** — store, sync, migrate — where atomicity matters (dedup + index updates). For **read operations** (search, list, tags), the agent reads INDEX.jsonl directly.

| Command | Description |
|---------|-------------|
| `claw-drive init` | Initialize drive directory and INDEX.jsonl |
| `claw-drive store <file> [opts]` | Store a file with categorization, tags, dedup, rename (`--name`), metadata (`--metadata`), correspondent (`--correspondent`) |
| `claw-drive update <path> [opts]` | Update description, tags, metadata, correspondent, and/or source on an existing entry |
| `claw-drive delete <path> [--force]` | Delete a file, its index entry, and dedup hash |
| `claw-drive rm <path> [--force]` | Alias for `delete` |
| `claw-drive status` | Show drive status (files, size, sync) |
| `claw-drive sync auth` | Authorize Google Drive (one-time, opens browser) |
| `claw-drive sync setup` | Check sync dependencies and config |
| `claw-drive sync start` | Start background sync daemon |
| `claw-drive sync stop` | Stop sync daemon |
| `claw-drive sync push` | Manual one-shot sync |
| `claw-drive sync status` | Show sync daemon state |
| `claw-drive reindex scan [--output plan.json]` | Scan drive for orphans + export existing entries for re-enrichment |
| `claw-drive reindex apply <plan.json> [--dry-run]` | Apply enriched reindex plan (add orphans, update existing) |
| `claw-drive migrate scan <dir> [plan.json]` | Scan a directory into a migration plan |
| `claw-drive migrate summary [plan.json]` | Show migration plan breakdown |
| `claw-drive migrate apply [plan.json] [--dry-run]` | Execute migration plan |
| `claw-drive version` | Show version |

## Sync

Optional real-time sync to Google Drive (or any rclone backend). Files sync within seconds of any change. Sensitive directories stay local-only.

See [docs/sync.md](docs/sync.md) for details.

## Migration

Got a messy folder full of unsorted files? Claw Drive's migration workflow handles it:

```bash
# 1. Scan the source directory
claw-drive migrate scan ~/messy-folder migration-plan.json

# 2. AI agent classifies each file (fills in category, name, tags, description)

# 3. Review the plan
claw-drive migrate summary migration-plan.json

# 4. Dry run first
claw-drive migrate apply migration-plan.json --dry-run

# 5. Execute
claw-drive migrate apply migration-plan.json
```

The scan outputs a JSON plan with file metadata (path, size, mime type, extension). The agent fills in classification fields, then `apply` copies files into Claw Drive with full dedup, indexing, and tagging.

## Custom Metadata

Store structured data alongside your files — expiry dates, policy numbers, amounts, anything the agent can answer questions about without reading the original file.

```bash
# Add metadata when storing
claw-drive store insurance-card.pdf -c insurance -d "Auto insurance" \
  --metadata '{"policy":"****3441","expiry":"2026-08","provider":"Farmers"}'

# Add metadata to existing files
claw-drive update insurance/card.pdf --metadata '{"deductible":"$500"}'
```

Metadata merges on update — existing fields are preserved, new fields are added. The agent can now answer "when does my insurance expire?" directly from the index, without opening the file.

## Correspondent Tracking

Track who sent or issued each file — the person, company, or organization it came from:

```bash
# Set on store
claw-drive store invoice.pdf -c finance -d "Q4 invoice" --correspondent "Acme Corp"

# Add to existing file
claw-drive update finance/invoice.pdf --correspondent "Acme Corp"
```

This lets the agent answer questions like "show me everything from Farmers Insurance" or "what did VEG send me?" by filtering on correspondent.

## Reindex

Already have files in Claw Drive but want richer descriptions, better tags, or custom metadata? The reindex workflow lets the agent re-analyze everything:

```bash
# 1. Scan — exports a plan with all files + current index entries
claw-drive reindex scan --output reindex-plan.json

# 2. Agent enriches the plan:
#    - Orphan files: fills in desc, tags, source, metadata
#    - Existing entries: adds new_desc, new_tags, new_metadata to update

# 3. Preview changes
claw-drive reindex apply reindex-plan.json --dry-run

# 4. Apply
claw-drive reindex apply reindex-plan.json
```

As your agent gets smarter, your old files benefit too.

## Original Filename Preservation

When you rename a file on store (`--name`), Claw Drive records the original filename in the index. This means you can search by either name:

```bash
claw-drive store messy-scan-001.pdf -c medical --name "blood-work-2026-02.pdf" -d "..."
# Index records: original_name: "messy-scan-001.pdf"
# Searchable by both "messy-scan" and "blood-work"
```

## Architecture

```
You ← natural language → AI Agent (OpenClaw)
                              │
                        claw-drive CLI
                              │
                        ~/claw-drive/        ← local, source of truth
                              │
                        fswatch + rclone     ← optional real-time sync
                              │
                        Google Drive          ← cloud backup
```

## Categories

Categories are open-ended — agents create new ones as needed. These are the defaults:

| Category | Use for |
|----------|---------|
| `documents/` | General docs, letters, forms, manuals |
| `finance/` | Tax returns, bank statements, pay stubs |
| `insurance/` | Policies, ID cards, claims, coverage docs |
| `medical/` | Health records, prescriptions, pet health |
| `travel/` | Boarding passes, itineraries, visas |
| `identity/` | ID scans, certificates (⚠️ sensitive — excluded from sync) |
| `receipts/` | Purchase receipts, warranties, invoices |
| `contracts/` | Leases, employment, legal agreements |
| `photos/` | Personal photos, document scans |
| `misc/` | Anything that doesn't fit above |

## Privacy & Security

**Claw Drive treats your files as personal data by default.** This isn't an afterthought — it's a core design decision.

### The Problem

AI agents that read your files put those contents into conversation transcripts — which are logged permanently. A "helpful" agent that reads your passport scan, tax return, or medical record has now copied that data into a `.jsonl` log file. That's a leak, not a feature.

### The Solution

Claw Drive's agent **always asks before reading**. And if you don't answer, it assumes the answer is no.

| Scenario | Behavior |
|----------|----------|
| User says "go ahead" | Full content extraction → rich description + specific tags |
| User says "keep it private" | Filename-only classification, asks for brief description |
| **User doesn't reply** | **Defaults to sensitive** — no content reading |
| **File goes to `identity/`** | **Always sensitive** — contents never read, never synced |

### What "sensitive" means in practice

- File contents are **never read** by the agent
- Classification uses **filename and user input only**
- INDEX.jsonl descriptions are kept **generic** (no SSNs, account numbers, etc.)
- `identity/` is **excluded from cloud sync** by default
- The file is still stored, hashed (for dedup), tagged, and indexed — just without content extraction

### Defense in depth

| Layer | Protection |
|-------|-----------|
| Consent | Agent asks before reading any file |
| Default-safe | No reply = sensitive |
| Category rules | `identity/` always sensitive, excluded from sync |
| Sync exclusion | `.sync-config` exclude list for any category |
| Index hygiene | No raw sensitive data in descriptions |
| Local-first | Cloud sync is optional, not default |

## Documentation

- [Tags](docs/tags.md) — tagging guidelines and examples
- [Sync](docs/sync.md) — Google Drive sync setup and daemon
- [Security](docs/security.md) — threat model and privacy controls

## Roadmap

- [x] `update` command — modify description/tags on existing entries
- [x] `delete` command — remove files with atomic index cleanup
- [x] `verify --fix` — self-healing integrity checks
- [x] `reindex` — batch re-enrichment of existing files
- [x] Custom metadata fields — structured data per file
- [x] Correspondent tracking — source person/organization per file
- [x] Original filename preservation on rename
- [ ] Watch folder ingestion (auto-import from Downloads)
- [ ] Encrypted storage for sensitive categories
- [ ] Linux support (inotifywait + systemd)
- [ ] Web dashboard for browsing and search
- [ ] Homebrew tap distribution

## License

[MIT](LICENSE)
