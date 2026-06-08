# Project Notes for Claude

## Reference Documentation

Before answering any question about ClawHub commands, SKILL.md format, or skill configuration — fetch and read the relevant documentation page first:

- https://docs.openclaw.ai/ - OpenClaw documentation
- https://docs.openclaw.ai/tools/clawhub — ClawHub CLI commands (install, update, list, publish, etc.)
- https://docs.openclaw.ai/tools/skills — SKILL.md structure and frontmatter spec
- https://docs.openclaw.ai/tools/skills-config — skill configuration and openclaw.json
- https://docs.pyrogram.org/ — Pyrogram API reference; fetch before answering any question about Pyrogram behaviour, errors, or usage
- https://tl.telethon.dev/ — Telethon TL reference; fetch before answering any question about Telethon behaviour, errors, or usage

### ClawHub CLI reference (from docs)

```
clawhub install <slug>
clawhub update <slug>
clawhub update --all
clawhub update --version <version>   # single slug only
clawhub update --force               # overwrite when local files don't match published version
clawhub list                         # reads .clawhub/lock.json
```

## Key conventions

- **Language:** All code comments, CHANGELOG entries, and commit messages must be in **English**
- **CHANGELOG style:** Lead with a user-friendly description (what changed and why it matters). Technical details (function names, error types, etc.) are allowed after the plain-language summary.
- `SKILL.md` frontmatter `metadata` must be a **single-line JSON** with the `openclaw` namespace:
  ```
  metadata: {"openclaw": {"requires": {"bins": [...], "env": [...]}, "primaryEnv": "..."}}
  ```
- `name` in SKILL.md frontmatter is the registry package ID (e.g. `sergei-mikhailov-stt`), not a display name
- Display name is the `#` heading in the body of SKILL.md

---

## Project: sergei-mikhailov-tg-channel-reader

**Type:** OpenClaw skill (Python package published to ClawHub registry)
**Registry slug:** `sergei-mikhailov-tg-channel-reader`
**ClawHub display name:** `Telegram Channel Reader` (pass `--name "Telegram Channel Reader"` when publishing)
**Current version:** 0.9.2
**License:** MIT

### What it does

Reads posts from Telegram channels via MTProto (official protocol). Supports Pyrogram (default) and Telethon as interchangeable backends. Outputs JSON or plain text.

### Key files

| File | Purpose |
|------|---------|
| `SKILL.md` | OpenClaw skill definition — frontmatter + agent instructions |
| `setup.py` | Python package config, entry points, dependencies |
| `reader.py` | Pyrogram implementation |
| `reader_telethon.py` | Telethon implementation |
| `tg_reader_unified.py` | Unified entry point — auto-selects backend |
| `tg_check.py` | Offline diagnostic script (`tg-reader-check`) |
| `tg_state.py` | Read-tracking state management (load/save per-channel last_read_id) |
| `CHANGELOG.md` | Version history |
| `DISCLAIMER.md` | Legal disclaimer |
| `README_TELETHON.md` | Telethon-specific docs |
| `TESTING_GUIDE.md` | Troubleshooting & test scenarios |

### Entry points (from setup.py)

```
tg-reader              → tg_reader_unified:main   (auto-selects backend)
tg-reader-pyrogram     → reader:main              (force Pyrogram)
tg-reader-telethon     → reader_telethon:main     (force Telethon)
tg-reader-check        → tg_check:main            (offline diagnostic)
```

### Dependencies

```
pyrogram>=2.0.0
tgcrypto>=1.2.0
telethon>=1.24.0
python>=3.9
```

### Environment variables

| Var | Required | Notes |
|-----|----------|-------|
| `TG_API_ID` | Yes | Numeric ID from my.telegram.org |
| `TG_API_HASH` | Yes | Secret — treat like a password, never commit |
| `TG_SESSION` | No | Path to session file (default: `~/.tg-reader-session`) |
| `TG_USE_TELETHON` | No | Set to `"true"` to use Telethon instead of Pyrogram |
| `TG_READ_UNREAD` | No | Set to `"true"` to enable read_unread mode (env overrides config) |
| `TG_STATE_FILE` | No | Path to state file (default: `~/.tg-reader-state.json`) |

### .gitignore (critical — never commit these)

```
*.session
*.session-journal
.tg-reader.json
.env
```

### SKILL.md frontmatter note

`metadata` is single-line JSON as required by spec (fixed 2026-02-23).

### Publishing workflow

1. Update version in `setup.py`
2. Update `CHANGELOG.md`
3. Ensure `SKILL.md` is valid per registry spec
4. Publish via ClawHub CLI (check docs for exact command)

### Security constraints

- **Never** commit `TG_API_HASH`, `TG_API_ID`, or `*.session` files
- Session file (`~/.tg-reader-session.session`) grants full Telegram account access
- Credentials belong in env vars or `~/.tg-reader.json` (outside the repo)
