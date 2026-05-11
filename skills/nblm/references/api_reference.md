# nblm API Reference

Complete API documentation for all NotebookLM skill modules.

## Important: Always Use run.py Wrapper

**All commands must use the `run.py` wrapper to ensure proper environment:**

```bash
# ✅ CORRECT:
python scripts/run.py [script_name].py [arguments]

# ❌ WRONG:
python scripts/[script_name].py [arguments]  # Will fail without venv!
```

## Core Scripts

### ask_question.py
Query NotebookLM with automated browser interaction.

```bash
# Basic usage
python scripts/run.py ask_question.py --question "Your question"

# With specific notebook
python scripts/run.py ask_question.py --question "..." --notebook-id notebook-id

# With direct URL
python scripts/run.py ask_question.py --question "..." --notebook-url "https://..."

# Show browser (debugging)
python scripts/run.py ask_question.py --question "..." --show-browser
```

**Parameters:**
- `--question` (required): Question to ask
- `--notebook-id`: Use notebook from library
- `--notebook-url`: Use URL directly
- `--show-browser`: Make browser visible

**Returns:** Answer text with follow-up prompt appended

### notebook_manager.py
Manage notebook library with CRUD operations.

```bash
# Smart Add (discover content first)
python scripts/run.py ask_question.py --question "What is the content of this notebook? What topics are covered? Provide a complete overview briefly and concisely" --notebook-url "[URL]"
# Then add with discovered info
python scripts/run.py notebook_manager.py add \
  --url "https://notebooklm.google.com/notebook/..." \
  --name "Name" \
  --description "Description" \
  --topics "topic1,topic2"

# Direct add (when you know the content)
python scripts/run.py notebook_manager.py add \
  --url "https://notebooklm.google.com/notebook/..." \
  --name "Name" \
  --description "What it contains" \
  --topics "topic1,topic2"

# List notebooks
python scripts/run.py notebook_manager.py list

# Search notebooks
python scripts/run.py notebook_manager.py search --query "keyword"

# Activate notebook
python scripts/run.py notebook_manager.py activate --id notebook-id

# Remove notebook
python scripts/run.py notebook_manager.py remove --id notebook-id

# Show statistics
python scripts/run.py notebook_manager.py stats
```

**Commands:**
- `add`: Add notebook (requires --url, --name, --topics)
- `list`: Show all notebooks
- `search`: Find notebooks by keyword
- `activate`: Set default notebook
- `remove`: Delete from library
- `stats`: Display library statistics

### auth_manager.py
Handle Google authentication and browser state.

```bash
# Setup (browser visible for login)
python scripts/run.py auth_manager.py setup

# Check status
python scripts/run.py auth_manager.py status

# Clear authentication
python scripts/run.py auth_manager.py clear

# Multi-account management
python scripts/run.py auth_manager.py accounts list
python scripts/run.py auth_manager.py accounts add
python scripts/run.py auth_manager.py accounts switch 1
```

**Commands:**
- `setup`: Initial authentication (browser MUST be visible)
- `status`: Check if authenticated
- `clear`: Remove all auth data
- `accounts`: Multi-account management (list, add, switch, remove)

Note: Expired credentials are automatically re-authenticated when running commands.

### cleanup_manager.py
Clean skill data with preservation options.

```bash
# Preview cleanup
python scripts/run.py cleanup_manager.py

# Execute cleanup
python scripts/run.py cleanup_manager.py --confirm

# Keep library
python scripts/run.py cleanup_manager.py --confirm --preserve-library

# Force without prompt
python scripts/run.py cleanup_manager.py --confirm --force
```

**Options:**
- `--confirm`: Actually perform cleanup
- `--preserve-library`: Keep notebook library
- `--force`: Skip confirmation prompt

### artifact_manager.py
Manage audio overviews, podcasts, and other generated artifacts.

```bash
# List all artifacts
python scripts/run.py artifact_manager.py list

# List only audio artifacts
python scripts/run.py artifact_manager.py list --type audio

# Get artifact details
python scripts/run.py artifact_manager.py get <artifact-id>

# Delete an artifact
python scripts/run.py artifact_manager.py delete <artifact-id>

# Generate audio podcast (async - returns immediately)
python scripts/run.py artifact_manager.py generate

# Generate with custom options
python scripts/run.py artifact_manager.py generate \
  --format DEEP_DIVE \
  --length DEFAULT \
  --instructions "Focus on the key findings"

# Generate and wait for completion
python scripts/run.py artifact_manager.py generate --wait

# Generate, wait, and download
python scripts/run.py artifact_manager.py generate --wait --output ./podcast.mp3

# Check generation status
python scripts/run.py artifact_manager.py status --task-id <task-id>

# Download latest audio
python scripts/run.py artifact_manager.py download ./output.mp3

# Download specific artifact
python scripts/run.py artifact_manager.py download ./output.mp3 --artifact-id <id>
```

**Commands:**
- `list`: List all artifacts (filter with `--type`)
- `get`: Get artifact details by ID
- `delete`: Delete an artifact
- `generate`: Generate audio podcast
- `status`: Check generation task status
- `download`: Download artifact to local file

**Generate Options:**
- `--format`: `DEEP_DIVE` (default), `BRIEF`, `CRITIQUE`, `DEBATE`
- `--length`: `SHORT`, `DEFAULT`, `LONG`
- `--instructions`: Custom instructions for the podcast
- `--wait`: Wait for generation to complete
- `--output`: Download path (requires `--wait`)
- `--timeout`: Timeout in seconds (default: 600)

### run.py
Script wrapper that handles environment setup.

```bash
# Usage
python scripts/run.py [script_name].py [arguments]

# Examples
python scripts/run.py auth_manager.py status
python scripts/run.py ask_question.py --question "..."
```

**Automatic actions:**
1. Creates `.venv` if missing
2. Installs dependencies
3. Activates environment
4. Executes target script

## Python API Usage

### Using subprocess with run.py

```python
import subprocess
import json

# Always use run.py wrapper
result = subprocess.run([
    "python", "scripts/run.py", "ask_question.py",
    "--question", "Your question",
    "--notebook-id", "notebook-id"
], capture_output=True, text=True)

answer = result.stdout
```

### Direct imports (after venv exists)

```python
# Only works if venv is already created and activated
from notebook_manager import NotebookLibrary
from auth_manager import AuthManager

library = NotebookLibrary()
notebooks = library.list_notebooks()

auth = AuthManager()
is_auth = auth.is_authenticated()
```

## Data Storage

Location: `~/.claude/skills/notebooklm/data/`

```
data/
├── library.json       # Notebook metadata
├── auth_info.json     # Auth status
└── agent_browser/     # Session metadata
    └── session_id
```

**Security:** Protected by `.gitignore`, never commit.

## Environment Variables

Optional `.env` file configuration is not required for normal usage.

## Error Handling

Common patterns:

```python
# Using run.py prevents most errors
result = subprocess.run([
    "python", "scripts/run.py", "ask_question.py",
    "--question", "Question"
], capture_output=True, text=True)

if result.returncode != 0:
    error = result.stderr
    if "rate limit" in error.lower():
        # Wait or switch accounts
        pass
    elif "not authenticated" in error.lower():
        # Run auth setup
        subprocess.run(["python", "scripts/run.py", "auth_manager.py", "setup"])
```

## Rate Limits

Free Google accounts: 50 queries/day

Solutions:
1. Wait for reset (midnight PST)
2. Switch accounts with `accounts switch`
3. Use multiple Google accounts

## Advanced Patterns

### Parallel Queries

```python
import concurrent.futures
import subprocess

def query(question, notebook_id):
    result = subprocess.run([
        "python", "scripts/run.py", "ask_question.py",
        "--question", question,
        "--notebook-id", notebook_id
    ], capture_output=True, text=True)
    return result.stdout

# Run multiple queries simultaneously
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    futures = [
        executor.submit(query, q, nb)
        for q, nb in zip(questions, notebooks)
    ]
    results = [f.result() for f in futures]
```

### Batch Processing

```python
def batch_research(questions, notebook_id):
    results = []
    for question in questions:
        result = subprocess.run([
            "python", "scripts/run.py", "ask_question.py",
            "--question", question,
            "--notebook-id", notebook_id
        ], capture_output=True, text=True)
        results.append(result.stdout)
        time.sleep(2)  # Avoid rate limits
    return results
```

## Module Classes

### NotebookLibrary
- `add_notebook(url, name, topics)`
- `list_notebooks()`
- `search_notebooks(query)`
- `get_notebook(notebook_id)`
- `activate_notebook(notebook_id)`
- `remove_notebook(notebook_id)`

### AuthManager
- `is_authenticated()`
- `setup_auth(headless=False)`
- `get_auth_info()`
- `clear_auth()`
- `validate_auth()`

### BrowserSession (internal)
- Handles browser automation
- Manages stealth behavior
- Not intended for direct use

## Best Practices

1. **Always use run.py** - Ensures environment
2. **Check auth first** - Before operations
3. **Handle rate limits** - Implement retries
4. **Include context** - Questions are independent
5. **Clean sessions** - Use cleanup_manager
