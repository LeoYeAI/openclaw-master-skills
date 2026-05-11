---
name: nblm
description: Use this skill to query your Google NotebookLM notebooks directly from Claude Code for source-grounded, citation-backed answers from Gemini. Browser automation, library management, persistent auth. Drastically reduced hallucinations through document-only responses.
---

# NotebookLM Quick Commands

Query Google NotebookLM for source-grounded, citation-backed answers.

## Environment

All dependencies and authentication are handled automatically by `run.py`:
- First run creates `.venv` and installs Python/Node.js dependencies
- If Google auth is missing or expired, a browser window opens automatically
- No manual pre-flight steps required

---

## Usage

`/nblm <command> [args]`

## Commands

### Notebook Management
| Command | Description |
|---------|-------------|
| `login` | Authenticate with Google |
| `status` | Show auth and library status |
| `accounts` | List all Google accounts |
| `accounts add` | Add a new Google account |
| `accounts switch <id>` | Switch active account (by index or email) |
| `accounts remove <id>` | Remove an account |
| `local` | List notebooks in local library |
| `remote` | List all notebooks from NotebookLM API |
| `create <name>` | Create a new notebook |
| `delete [--id ID]` | Delete a notebook |
| `rename <name> [--id ID]` | Rename a notebook |
| `summary [--id ID]` | Get AI-generated summary |
| `describe [--id ID]` | Get description and suggested topics |
| `add <url-or-id>` | Add notebook to local library (auto-detects URL vs notebook ID) |
| `activate <id>` | Set active notebook |

### Source Management
| Command | Description |
|---------|-------------|
| `sources [--id ID]` | List sources in notebook |
| `upload <file>` | Upload a single file |
| `upload <folder>` | Sync a folder of files to NotebookLM |
| `upload-zlib <url>` | Download from Z-Library and upload |
| `upload-url <url>` | Add URL as source |
| `upload-youtube <url>` | Add YouTube video as source |
| `upload-text <title> [--content TEXT]` | Add text as source |
| `source-text <source-id>` | Get full indexed text |
| `source-guide <source-id>` | Get AI summary and keywords |
| `source-rename <source-id> <name>` | Rename a source |
| `source-refresh <source-id>` | Re-fetch URL content |
| `source-delete <source-id>` | Delete a source |

**Upload options:**
- `--use-active` - Upload to the currently active notebook
- `--create-new` - Create a new notebook named after the file/folder
- `--notebook-id <id>` - Upload to a specific notebook
- `--dry-run` - Show sync plan without executing (folder sync)
- `--rebuild` - Force rebuild tracking file (folder sync)

**Important:** When user runs upload without specifying a target, ASK them first:
> "Would you like to upload to the active notebook, or create a new notebook?"
Then pass the appropriate flag (`--use-active` or `--create-new`).

### Chat & Audio/Media
| Command | Description |
|---------|-------------|
| `ask <question>` | Query NotebookLM |
| `podcast [--instructions TEXT]` | Generate audio podcast |
| `podcast-status <task-id>` | Check podcast generation status |
| `podcast-download [output-path]` | Download latest podcast |
| `briefing [--instructions TEXT]` | Generate brief audio summary |
| `debate [--instructions TEXT]` | Generate debate-style audio |
| `slides [--instructions TEXT]` | Generate slide deck |
| `slides-download [output-path]` | Download slide deck as PDF |
| `infographic [--instructions TEXT]` | Generate infographic |
| `infographic-download [output-path]` | Download infographic |
| `media-list [--type TYPE]` | List generated media (audio/video/slides/infographic) |
| `media-delete <id>` | Delete a generated media item |

## Command Routing

Based on `$ARGUMENTS`, execute the appropriate command:

$IF($ARGUMENTS,
  Parse the command from: "$ARGUMENTS"

  **login** → `python scripts/run.py auth_manager.py setup --service google`

  **accounts** → `python scripts/run.py auth_manager.py accounts list`

  **accounts add** → `python scripts/run.py auth_manager.py accounts add`

  **accounts switch <id>** → `python scripts/run.py auth_manager.py accounts switch "<id>"`

  **accounts remove <id>** → `python scripts/run.py auth_manager.py accounts remove "<id>"`

  **status** → Run both:
  - `python scripts/run.py auth_manager.py status`
  - `python scripts/run.py notebook_manager.py list`

  **local** → `python scripts/run.py notebook_manager.py list`

  **remote** → `python scripts/run.py nblm_cli.py notebooks`

  **create <name>** → `python scripts/run.py nblm_cli.py create "<name>"`

  **delete [--id ID]** → `python scripts/run.py nblm_cli.py delete <args>`

  **rename <name> [--id ID]** → `python scripts/run.py nblm_cli.py rename "<name>" <args>`

  **summary [--id ID]** → `python scripts/run.py nblm_cli.py summary <args>`

  **describe [--id ID]** → `python scripts/run.py nblm_cli.py describe <args>`

  **add <url-or-id>** → Smart add workflow (auto-detects URL vs notebook ID)

  **activate <id>** → `python scripts/run.py notebook_manager.py activate --id "<id>"`

  **sources [--id ID]** → `python scripts/run.py nblm_cli.py sources <args>`

  **upload <file>** → First ASK user: "Upload to active notebook or create new?" Then:
    - Active: `python scripts/run.py source_manager.py add --file "<file>" --use-active`
    - New: `python scripts/run.py source_manager.py add --file "<file>" --create-new`

  **upload <folder>** → Sync a folder:
    - First ASK user: "Sync to active notebook, create new, or specify notebook?"
    - Active: `python scripts/run.py source_manager.py sync "<folder>" --use-active`
    - New: `python scripts/run.py source_manager.py sync "<folder>" --create-new`
    - Specific: `python scripts/run.py source_manager.py sync "<folder>" --notebook-id ID`
    - Dry-run: `python scripts/run.py source_manager.py sync "<folder>" --dry-run`
    - Rebuild: `python scripts/run.py source_manager.py sync "<folder>" --rebuild`

  **upload-zlib <url>** → First ASK user: "Upload to active notebook or create new?" Then:
    - Active: `python scripts/run.py source_manager.py add --url "<url>" --use-active`
    - New: `python scripts/run.py source_manager.py add --url "<url>" --create-new`

  **upload-url <url>** → `python scripts/run.py nblm_cli.py upload-url "<url>"`

  **upload-youtube <url>** → `python scripts/run.py nblm_cli.py upload-youtube "<url>"`

  **upload-text <title>** → `python scripts/run.py nblm_cli.py upload-text "<title>" <args>`

  **source-text <id>** → `python scripts/run.py nblm_cli.py source-text "<id>"`

  **source-guide <id>** → `python scripts/run.py nblm_cli.py source-guide "<id>"`

  **source-rename <id> <name>** → `python scripts/run.py nblm_cli.py source-rename "<id>" "<name>"`

  **source-refresh <id>** → `python scripts/run.py nblm_cli.py source-refresh "<id>"`

  **source-delete <id>** → `python scripts/run.py nblm_cli.py source-delete "<id>"`

  **ask <question>** → `python scripts/run.py nblm_cli.py ask "<question>"`

  **podcast** → `python scripts/run.py artifact_manager.py generate --format DEEP_DIVE <args>`

  **podcast-status <task-id>** → `python scripts/run.py artifact_manager.py status --task-id "<task-id>"`

  **podcast-download [output-path]** → `python scripts/run.py artifact_manager.py download "<output-path>"`

  **briefing** → `python scripts/run.py artifact_manager.py generate --format BRIEF <args>`

  **debate** → `python scripts/run.py artifact_manager.py generate --format DEBATE <args>`

  **slides** → `python scripts/run.py artifact_manager.py generate-slides <args>`

  **slides-download [output-path]** → `python scripts/run.py artifact_manager.py download "<output-path>" --type slide-deck`

  **infographic** → `python scripts/run.py artifact_manager.py generate-infographic <args>`

  **infographic-download [output-path]** → `python scripts/run.py artifact_manager.py download "<output-path>" --type infographic`

  **media-list [--type TYPE]** → `python scripts/run.py artifact_manager.py list <args>`

  **media-delete <id>** → `python scripts/run.py artifact_manager.py delete "<id>"`

  If command not recognized, show usage help.,

  Show available commands with `/nblm` (no arguments)
)

## Podcast Options

```
/nblm podcast --length DEFAULT --wait --output ./podcast.mp3
/nblm podcast --instructions "Focus on the key findings"
/nblm briefing --wait --output ./summary.mp3
/nblm debate --instructions "Compare the two approaches"
```

| Option | Values |
|--------|--------|
| `--length` | `SHORT`, `DEFAULT`, `LONG` |
| `--instructions` | Custom instructions for the content |
| `--wait` | Wait for generation to complete |
| `--output` | Download path (requires `--wait`) |

## Slide Deck Options

```
/nblm slides --format DETAILED_DECK --wait --output ./presentation.pdf
/nblm slides --instructions "Focus on key diagrams" --format PRESENTER_SLIDES
```

| Option | Values |
|--------|--------|
| `--format` | `DETAILED_DECK`, `PRESENTER_SLIDES` |
| `--length` | `SHORT`, `DEFAULT` |
| `--instructions` | Custom instructions for the content |
| `--wait` | Wait for generation to complete |
| `--output` | Download path (requires `--wait`) |

## Infographic Options

```
/nblm infographic --orientation LANDSCAPE --wait --output ./visual.png
/nblm infographic --instructions "Highlight comparison" --detail-level DETAILED
```

| Option | Values |
|--------|--------|
| `--orientation` | `LANDSCAPE`, `PORTRAIT`, `SQUARE` |
| `--detail-level` | `CONCISE`, `STANDARD`, `DETAILED` |
| `--instructions` | Custom instructions for the content |
| `--wait` | Wait for generation to complete |
| `--output` | Download path (requires `--wait`) |

## Media Generation

| Command | Description | Output |
|---------|-------------|--------|
| `/nblm podcast` | Deep-dive audio discussion | MP3 |
| `/nblm briefing` | Brief audio summary | MP3 |
| `/nblm debate` | Debate-style audio | MP3 |
| `/nblm slides` | Slide deck presentation | PDF |
| `/nblm infographic` | Visual infographic | PNG |

### Examples
```
/nblm podcast --wait --output ./deep-dive.mp3
/nblm briefing --instructions "Focus on chapter 3" --wait
/nblm debate --length LONG --wait --output ./debate.mp3
/nblm slides --instructions "Include key diagrams" --format DETAILED_DECK --wait --output ./presentation.pdf
/nblm infographic --orientation LANDSCAPE --detail-level DETAILED --wait --output ./summary.png
```

### Download & Manage
```
/nblm podcast-download ./my-podcast.mp3
/nblm slides-download ./presentation.pdf
/nblm infographic-download ./visual.png
/nblm media-list                     # List all generated media
/nblm media-list --type audio        # List only audio
/nblm media-delete <id>              # Delete a media item
```

---

# Extended Documentation

## When to Use This Skill

Trigger when user:
- Mentions NotebookLM explicitly
- Shares NotebookLM URL (`https://notebooklm.google.com/notebook/...`)
- Asks to query their notebooks/documentation
- Wants to add documentation to NotebookLM library
- Uses phrases like "ask my NotebookLM", "check my docs", "query my notebook"

## ⚠️ CRITICAL: Add Command - Smart Discovery

The add command now **automatically discovers metadata** from the notebook:

```bash
# Smart Add (auto-discovers name, description, topics)
python scripts/run.py notebook_manager.py add <notebook-id-or-url>

# With optional overrides
python scripts/run.py notebook_manager.py add <id> --name "Custom Name" --topics "custom,topics"
```

**What Smart Add does:**
1. Fetches notebook title from NotebookLM API
2. Queries the notebook content to generate description and topics
3. Adds to local library with discovered metadata

**Supported input formats:**
- Notebook ID: `5fd9f36b-8000-401d-a7a0-7aa3f7832644`
- Full URL: `https://notebooklm.google.com/notebook/5fd9f36b-8000-401d-a7a0-7aa3f7832644`

NEVER manually specify `--name`, `--description`, or `--topics` unless the user explicitly provides them.

## Critical: Always Use run.py Wrapper

**NEVER call scripts directly. ALWAYS use `python scripts/run.py [script]`:**

```bash
# ✅ CORRECT - Always use run.py:
python scripts/run.py auth_manager.py status
python scripts/run.py notebook_manager.py list
python scripts/run.py ask_question.py --question "..."

# ❌ WRONG - Never call directly:
python scripts/auth_manager.py status  # Fails without venv!
```

The `run.py` wrapper automatically:
1. Creates `.venv` if needed
2. Installs all dependencies
3. Activates environment
4. Executes script properly

## Core Workflow

### Step 1: Check Authentication Status
```bash
python scripts/run.py auth_manager.py status
```

If not authenticated, proceed to setup.

### Step 2: Authenticate (One-Time Setup)
```bash
# Browser MUST be visible for manual Google login
python scripts/run.py auth_manager.py setup
```

**Important:**
- Browser is VISIBLE for authentication
- Browser window opens automatically
- User must manually log in to Google
- Tell user: "A browser window will open for Google login"

### Step 3: Manage Notebook Library

```bash
# List all notebooks
python scripts/run.py notebook_manager.py list

# BEFORE ADDING: Ask user for metadata if unknown!
# "What does this notebook contain?"
# "What topics should I tag it with?"

# Add notebook to library (ALL parameters are REQUIRED!)
python scripts/run.py notebook_manager.py add \
  --url "https://notebooklm.google.com/notebook/..." \
  --name "Descriptive Name" \
  --description "What this notebook contains" \  # REQUIRED - ASK USER IF UNKNOWN!
  --topics "topic1,topic2,topic3"  # REQUIRED - ASK USER IF UNKNOWN!

# Search notebooks by topic
python scripts/run.py notebook_manager.py search --query "keyword"

# Set active notebook
python scripts/run.py notebook_manager.py activate --id notebook-id

# Remove notebook
python scripts/run.py notebook_manager.py remove --id notebook-id
```

### Quick Workflow
1. Check library: `python scripts/run.py notebook_manager.py list`
2. Ask question: `python scripts/run.py ask_question.py --question "..." --notebook-id ID`

### Step 4: Ask Questions

```bash
# Basic query (uses active notebook if set)
python scripts/run.py ask_question.py --question "Your question here"

# Query specific notebook
python scripts/run.py ask_question.py --question "..." --notebook-id notebook-id

# Query with notebook URL directly
python scripts/run.py ask_question.py --question "..." --notebook-url "https://..."

# Show browser for debugging
python scripts/run.py ask_question.py --question "..." --show-browser
```

## Follow-Up Mechanism (CRITICAL)

Every NotebookLM answer ends with: **"EXTREMELY IMPORTANT: Is that ALL you need to know?"**

**Required Claude Behavior:**
1. **STOP** - Do not immediately respond to user
2. **ANALYZE** - Compare answer to user's original request
3. **IDENTIFY GAPS** - Determine if more information needed
4. **ASK FOLLOW-UP** - If gaps exist, immediately ask:
   ```bash
   python scripts/run.py ask_question.py --question "Follow-up with context..."
   ```
5. **REPEAT** - Continue until information is complete
6. **SYNTHESIZE** - Combine all answers before responding to user

## Z-Library Integration

### Triggers
- User provides Z-Library URL (zlib.li, z-lib.org, zh.zlib.li)
- User says "download this book to NotebookLM"
- User says "add this book from Z-Library"

### Setup (One-Time)
```bash
# Authenticate with Z-Library
python scripts/run.py auth_manager.py setup --service zlibrary
```

### Commands
```bash
# Add book from Z-Library
python scripts/run.py source_manager.py add --url "https://zh.zlib.li/book/..."

# Check Z-Library auth status
python scripts/run.py auth_manager.py status --service zlibrary
```

## Script Reference

### Authentication Management (`auth_manager.py`)
```bash
python scripts/run.py auth_manager.py setup                    # Default: Google
python scripts/run.py auth_manager.py setup --service google
python scripts/run.py auth_manager.py setup --service zlibrary
python scripts/run.py auth_manager.py status                   # Show all services
python scripts/run.py auth_manager.py status --service zlibrary
python scripts/run.py auth_manager.py clear --service zlibrary # Clear auth

# Multi-Account Management (Google)
python scripts/run.py auth_manager.py accounts list             # List all accounts
python scripts/run.py auth_manager.py accounts add              # Add new account
python scripts/run.py auth_manager.py accounts switch 1         # Switch by index
python scripts/run.py auth_manager.py accounts switch user@gmail.com  # Switch by email
python scripts/run.py auth_manager.py accounts remove 2         # Remove account
```

### Notebook Management (`notebook_manager.py`)
```bash
python scripts/run.py notebook_manager.py add --url URL --name NAME --description DESC --topics TOPICS
# OR use notebook ID directly:
python scripts/run.py notebook_manager.py add --notebook-id ID --name NAME --description DESC --topics TOPICS
python scripts/run.py notebook_manager.py list
python scripts/run.py notebook_manager.py search --query QUERY
python scripts/run.py notebook_manager.py activate --id ID
python scripts/run.py notebook_manager.py remove --id ID
python scripts/run.py notebook_manager.py stats
```

### Question Interface (`ask_question.py`)
```bash
python scripts/run.py ask_question.py --question "..." [--notebook-id ID] [--notebook-url URL] [--show-browser]
```

### Source Manager (`source_manager.py`)
```bash
# Upload to active notebook
python scripts/run.py source_manager.py add --file "/path/to/book.pdf" --use-active

# Create new notebook for upload
python scripts/run.py source_manager.py add --file "/path/to/book.pdf" --create-new

# Upload to specific notebook
python scripts/run.py source_manager.py add --file "/path/to/book.pdf" --notebook-id NOTEBOOK_ID

# Z-Library download and upload
python scripts/run.py source_manager.py add --url "https://zh.zlib.li/book/..." --use-active
python scripts/run.py source_manager.py add --url "https://zh.zlib.li/book/..." --create-new

# Sync a folder (new!)
python scripts/run.py source_manager.py sync "/path/to/docs" --use-active
python scripts/run.py source_manager.py sync "/path/to/docs" --create-new
python scripts/run.py source_manager.py sync "/path/to/docs" --notebook-id NOTEBOOK_ID

# Sync options (new!)
python scripts/run.py source_manager.py sync "/path/to/docs" --dry-run    # Preview only
python scripts/run.py source_manager.py sync "/path/to/docs" --rebuild   # Force re-hash all files
```

**Folder Sync:**
- Scans folder for supported types: PDF, TXT, MD, DOCX, HTML, EPUB
- Tracks sync state internally (no per-folder tracking file to manage)
- Sync strategy: add new, update modified (delete + re-upload), skip unchanged
- Multi-account aware (tracks which Google account was used)
**Note:** One of `--use-active`, `--create-new`, or `--notebook-id` is REQUIRED.
Uploads wait for NotebookLM processing and print progress as `Ready: N/T`. Press Ctrl+C to stop waiting.
Local file uploads use browser automation and require Google authentication.
If browser automation is unavailable, set `NOTEBOOKLM_UPLOAD_MODE=text` to upload extracted text instead (PDFs require `pypdf`).

### Data Cleanup (`cleanup_manager.py`)
```bash
python scripts/run.py cleanup_manager.py                    # Preview cleanup
python scripts/run.py cleanup_manager.py --confirm          # Execute cleanup
python scripts/run.py cleanup_manager.py --preserve-library # Keep notebooks
```

### Watchdog Status (`auth_manager.py`)
```bash
python scripts/run.py auth_manager.py watchdog-status
```

## Environment Management

The virtual environment is automatically managed:
- First run creates `.venv` automatically
- Dependencies install automatically
- Node.js dependencies install automatically
- agent-browser daemon starts on demand and keeps browser state in memory
- daemon stops after 10 minutes of inactivity (any agent-browser command resets the timer)
- set `AGENT_BROWSER_OWNER_PID` to auto-stop when the agent process exits
- `scripts/run.py` sets `AGENT_BROWSER_OWNER_PID` to its parent PID by default
- Everything isolated in skill directory

Manual setup (only if automatic fails):
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
npm install
npm run install-browsers
```

## Data Storage

All data stored in `~/.claude/skills/notebooklm/data/`:
- `library.json` - Notebook metadata (with account associations)
- `auth/google/` - Multi-account Google auth
  - `index.json` - Account index (active account, list)
  - `<n>-<email>.json` - Per-account credentials
- `auth/zlibrary.json` - Z-Library auth state
- `agent_browser/session_id` - Current daemon session ID
- `agent_browser/last_activity.json` - Last activity timestamp for idle shutdown
- `agent_browser/watchdog.pid` - Idle watchdog process ID

**Security:** Protected by `.gitignore`, never commit to git.

## Configuration

Optional `.env` file in skill directory:
```env
HEADLESS=false           # Browser visibility
SHOW_BROWSER=false       # Default browser display
STEALTH_ENABLED=true     # Human-like behavior
TYPING_WPM_MIN=160       # Typing speed
TYPING_WPM_MAX=240
DEFAULT_NOTEBOOK_ID=     # Default notebook
```

## Decision Flow

```
User mentions NotebookLM
    ↓
Check auth → python scripts/run.py auth_manager.py status
    ↓
If not authenticated → python scripts/run.py auth_manager.py setup
    ↓
Check/Add notebook → python scripts/run.py notebook_manager.py list/add (with --description)
    ↓
Activate notebook → python scripts/run.py notebook_manager.py activate --id ID
    ↓
Ask question → python scripts/run.py ask_question.py --question "..."
    ↓
See "Is that ALL you need?" → Ask follow-ups until complete
    ↓
Synthesize and respond to user
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| ModuleNotFoundError | Use `run.py` wrapper |
| Authentication fails | Browser must be visible for setup! --show-browser |
| DAEMON_UNAVAILABLE | Ensure Node.js/npm installed, run `npm install`, retry |
| AUTH_REQUIRED | Run `python scripts/run.py auth_manager.py setup` |
| ELEMENT_NOT_FOUND | Verify notebook URL and re-run with fresh page load |
| Rate limit (50/day) | Wait or add another Google account with `accounts add` |
| Browser crashes | `python scripts/run.py cleanup_manager.py --preserve-library` |
| Notebook not found | Check with `notebook_manager.py list` |

## Best Practices

1. **Always use run.py** - Handles environment automatically
2. **Check auth first** - Before any operations
3. **Follow-up questions** - Don't stop at first answer
4. **Browser visible for auth** - Required for manual login
5. **Include context** - Each question is independent
6. **Synthesize answers** - Combine multiple responses

## Limitations

- No session persistence (each question = new browser)
- Rate limits on free Google accounts (50 queries/day per account; use multiple accounts to increase)
- Manual upload required (user must add docs to NotebookLM)
- Browser overhead (few seconds per question)

## Resources (Skill Structure)

**Important directories and files:**

- `scripts/` - All automation scripts (ask_question.py, notebook_manager.py, etc.)
- `data/` - Local storage for authentication and notebook library
- `references/` - Extended documentation:
  - `api_reference.md` - Detailed API documentation for all scripts
  - `troubleshooting.md` - Common issues and solutions
  - `usage_patterns.md` - Best practices and workflow examples
- `.venv/` - Isolated Python environment (auto-created on first run)
- `.gitignore` - Protects sensitive data from being committed
