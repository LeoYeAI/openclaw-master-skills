<div align="center">

**English** | [中文](README.zh-CN.md)

# nblm

### Your AI Coding Agent's Gateway to NotebookLM

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Agent Skill](https://img.shields.io/badge/Agent-Skill-purple.svg)](https://github.com/vercel-labs/add-skill)
[![License](https://img.shields.io/github/license/magicseek/nblm)](LICENSE)

<br/>

🧠 **Zero Hallucinations** — Answers grounded exclusively in your documents
<br/>
⚡ **Zero Context Switching** — Ask, upload, generate podcasts & slides from your editor
<br/>
🔌 **Infinite Sources** — Z-Library today, arXiv / Notion / Confluence tomorrow

<br/>

<sub>Works with **Claude Code** · **Cursor** · **Windsurf** · **Codex** · and any [Agent Skills](https://github.com/vercel-labs/add-skill) compatible agent</sub>

<br/>

[Installation](#installation) · [Quick Start](#quick-start) · [Commands](#commands) · [Architecture](#architecture)

</div>

---

## Installation

### Recommended: Using add-skill CLI

```bash
npx add-skill magicseek/nblm
```

This works with any supported agent. To install for a specific agent:

```bash
# Claude Code only
npx add-skill magicseek/nblm -a claude-code

# Global installation (available across all projects)
npx add-skill magicseek/nblm --global

# Multiple agents
npx add-skill magicseek/nblm -a claude-code -a cursor -a opencode
```

### Alternative: Platform-specific initialization

If symlinks created by `add-skill` don't work well in your environment (e.g., Cursor, Windows), you can generate platform-specific files directly:

**macOS / Linux:**
```bash
# Clone the repo
git clone https://github.com/magicseek/nblm ~/.nblm

# Initialize for your AI assistant (run from your project directory)
python ~/.nblm/scripts/run.py init --ai cursor       # Cursor
python ~/.nblm/scripts/run.py init --ai claude       # Claude Code
python ~/.nblm/scripts/run.py init --ai codex        # Codex CLI
python ~/.nblm/scripts/run.py init --ai antigravity  # Antigravity
python ~/.nblm/scripts/run.py init --ai windsurf     # Windsurf
python ~/.nblm/scripts/run.py init --ai copilot      # GitHub Copilot
python ~/.nblm/scripts/run.py init --ai all          # All platforms

# List available platforms
python ~/.nblm/scripts/run.py init --list
```

**Windows (PowerShell):**
```powershell
# Clone the repo
git clone https://github.com/magicseek/nblm $env:USERPROFILE\.nblm

# Initialize for your AI assistant (run from your project directory)
python $env:USERPROFILE\.nblm\scripts\run.py init --ai cursor       # Cursor
python $env:USERPROFILE\.nblm\scripts\run.py init --ai claude       # Claude Code
python $env:USERPROFILE\.nblm\scripts\run.py init --ai codex        # Codex CLI
python $env:USERPROFILE\.nblm\scripts\run.py init --ai antigravity  # Antigravity
python $env:USERPROFILE\.nblm\scripts\run.py init --ai windsurf     # Windsurf
python $env:USERPROFILE\.nblm\scripts\run.py init --ai copilot      # GitHub Copilot
python $env:USERPROFILE\.nblm\scripts\run.py init --ai all          # All platforms

# List available platforms
python $env:USERPROFILE\.nblm\scripts\run.py init --list
```

This generates the appropriate skill/command files in your project directory (e.g., `.cursor/commands/nblm.md`).

### First Run

On first use, nblm automatically:
- Creates an isolated Python environment (`.venv`)
- Installs Python and Node.js dependencies
- Starts the agent-browser daemon as needed

No manual setup required. If Playwright browsers are missing, run `npm run install-browsers` in the skill folder.

---

## Quick Start

### 1. Authenticate with Google (one-time)

```
/nblm login
```

A browser window opens for Google login. This is required once.

### 2. Add a notebook to your library

Go to [notebooklm.google.com](https://notebooklm.google.com) → Create notebook → Upload your docs → Share with "Anyone with link"

```
/nblm add <notebook-url-or-id>
```

nblm automatically queries the notebook to discover its content and metadata.

### 3. Ask questions

```
/nblm ask "What does the documentation say about authentication?"
```

Answers are source-grounded with citations from your uploaded documents.

### 4. Manage your notebooks

```
/nblm local          # List notebooks in your library
/nblm remote         # List all notebooks from NotebookLM API
/nblm status         # Show auth and library status
```

### 5. Upload sources

```
/nblm upload ./document.pdf           # Local file
/nblm upload-url https://example.com  # Web URL
/nblm upload-zlib <z-library-url>     # Z-Library book
```

---

## Commands

<details>
<summary><strong>📚 Notebook Management</strong></summary>

| Command | Description |
|---------|-------------|
| `/nblm login` | Authenticate with Google |
| `/nblm accounts` | List all Google accounts |
| `/nblm accounts add` | Add a new Google account |
| `/nblm accounts switch <id>` | Switch active account (by index or email) |
| `/nblm accounts remove <id>` | Remove an account |
| `/nblm status` | Show auth and library status |
| `/nblm local` | List notebooks in local library |
| `/nblm remote` | List all notebooks from NotebookLM API |
| `/nblm create <name>` | Create a new notebook |
| `/nblm delete [--id ID]` | Delete a notebook |
| `/nblm rename <name> [--id ID]` | Rename a notebook |
| `/nblm summary [--id ID]` | Get AI-generated summary |
| `/nblm describe [--id ID]` | Get description and suggested topics |
| `/nblm add <url-or-id>` | Add notebook to local library |
| `/nblm activate <id>` | Set active notebook |

</details>

<details>
<summary><strong>📄 Source Management</strong></summary>

| Command | Description |
|---------|-------------|
| `/nblm sources [--id ID]` | List sources in notebook |
| `/nblm upload <file>` | Upload local file (PDF, TXT, MD, DOCX) |
| `/nblm upload-zlib <url>` | Download from Z-Library and upload |
| `/nblm upload-url <url>` | Add URL as source |
| `/nblm upload-youtube <url>` | Add YouTube video as source |
| `/nblm upload-text <title> [--content TEXT]` | Add text as source |
| `/nblm source-text <source-id>` | Get full indexed text |
| `/nblm source-guide <source-id>` | Get AI summary and keywords |
| `/nblm source-rename <source-id> <name>` | Rename a source |
| `/nblm source-refresh <source-id>` | Re-fetch URL content |
| `/nblm source-delete <source-id>` | Delete a source |

</details>

<details>
<summary><strong>💬 Chat & Query</strong></summary>

| Command | Description |
|---------|-------------|
| `/nblm ask <question>` | Query NotebookLM |

</details>

<details>
<summary><strong>🎙️ Media Generation</strong></summary>

| Command | Description |
|---------|-------------|
| `/nblm podcast [--instructions TEXT]` | Generate audio podcast (deep-dive) |
| `/nblm podcast-status <task-id>` | Check podcast generation status |
| `/nblm podcast-download [output-path]` | Download latest podcast |
| `/nblm briefing [--instructions TEXT]` | Generate brief audio summary |
| `/nblm debate [--instructions TEXT]` | Generate debate-style audio |
| `/nblm slides [--instructions TEXT]` | Generate slide deck |
| `/nblm slides-download [output-path]` | Download slide deck as PDF |
| `/nblm infographic [--instructions TEXT]` | Generate infographic |
| `/nblm infographic-download [output-path]` | Download infographic |
| `/nblm media-list [--type TYPE]` | List generated media |
| `/nblm media-delete <id>` | Delete a generated media item |

**Media generation options:**

| Option | Values |
|--------|--------|
| `--length` | `SHORT`, `DEFAULT`, `LONG` |
| `--instructions` | Custom instructions for content |
| `--wait` | Wait for generation to complete |
| `--output` | Download path (requires `--wait`) |

</details>

---

## Architecture

nblm uses a hybrid approach combining API-first operations with browser automation fallback:

```
┌─────────────────────────────────────────────────────────────┐
│                        Your Agent                           │
│              (Claude Code / Cursor / OpenCode)              │
└─────────────────────┬───────────────────────────────────────┘
                      │ /nblm commands
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                         nblm                                │
├─────────────────────┬───────────────────────────────────────┤
│   notebooklm-py     │         agent-browser                 │
│   (API operations)  │      (browser automation)             │
│                     │                                       │
│ • Create notebooks  │ • Google authentication               │
│ • Add sources       │ • File uploads (fallback)             │
│ • Chat queries      │ • Z-Library downloads                 │
│ • Generate media    │ • Future non-API sources              │
└─────────────────────┴───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   Google NotebookLM                         │
│            (Gemini-powered document Q&A)                    │
└─────────────────────────────────────────────────────────────┘
```

**Key components:**

| Component | Role |
|-----------|------|
| **[notebooklm-py](https://github.com/teng-lin/notebooklm-py)** | Async Python client for NotebookLM API operations |
| **[agent-browser](https://github.com/vercel-labs/agent-browser)** | Headless browser daemon for auth and non-API sources |
| **scripts/run.py** | Entry point that auto-manages venv and dependencies |

**Data storage** (in `data/`):
- `library.json` — Your notebook metadata (with account associations)
- `auth/google/` — Multi-account Google authentication
  - `index.json` — Account index and active account
  - `<n>-<email>.json` — Per-account credentials
- `auth/zlibrary.json` — Z-Library authentication state

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Skill not found | Verify installation: `ls ~/.claude/skills/nblm/` |
| `ModuleNotFoundError` | Always use `/nblm` commands — they auto-manage the environment |
| Authentication fails | Run `/nblm login` with a visible browser |
| `DAEMON_UNAVAILABLE` | Ensure Node.js is installed, then run `npm install` in the skill folder |
| Rate limit (50/day) | Wait 24 hours or use a different Google account |
| Browser crashes | Run `python scripts/run.py cleanup_manager.py --preserve-library` |

For more details, see [references/troubleshooting.md](references/troubleshooting.md).

---

## Acknowledgments

nblm builds upon the excellent work of these projects:

- **[notebooklm-skill](https://github.com/PleasePrompto/notebooklm-skill)** by PleasePrompto — The original Claude Code skill for NotebookLM integration with browser automation
- **[zlibrary-to-notebooklm](https://github.com/zstmfhy/zlibrary-to-notebooklm)** by zstmfhy — Z-Library to NotebookLM pipeline
- **[notebooklm-py](https://github.com/teng-lin/notebooklm-py)** by teng-lin — Async Python API client for NotebookLM

Additional dependencies:
- **[agent-browser](https://github.com/vercel-labs/agent-browser)** — Headless browser daemon for AI agents
- **[add-skill](https://github.com/vercel-labs/add-skill)** — Universal skill installer for AI coding agents

---

## Limitations

- **Rate limits** — Free tier allows ~50 queries/day per Google account (use multiple accounts to increase limits)
- **No session persistence** — Each query is independent (no "previous answer" context)
- **Manual notebook creation** — You must create notebooks and upload docs via [notebooklm.google.com](https://notebooklm.google.com)

## License

MIT

---

<div align="center">

**nblm** — Source-grounded answers from your documents, directly in your coding agent.

[Report Issue](https://github.com/magicseek/nblm/issues) · [View on GitHub](https://github.com/magicseek/nblm)

</div>
