---
name: ms-todo-sync
description: >
  A CLI skill to manage Microsoft To Do tasks via Microsoft Graph API.
  Supports listing, creating, completing, deleting, searching tasks and lists,
  viewing overdue/today/pending tasks, and exporting data.
metadata:
  version: 1.0.2
  author: xiaoski@qq.com
  license: MIT License
  tags: [productivity, task-management, microsoft-todo, cli]
  category: productivity
---

# ms-todo-sync

A Microsoft To Do command-line client for managing tasks and lists via Microsoft Graph API.

## Prerequisites

1. **Python >= 3.9** must be installed.
2. **uv** (Python package manager) must be installed. Install via `pip install uv` or see https://docs.astral.sh/uv/.
3. **Working directory**: All commands MUST be run from the root of this skill (the directory containing this SKILL.md file).
4. **Network access**: Requires internet access to Microsoft Graph API endpoints.
5. **Authentication**: First-time use requires interactive login via browser. See [Authentication](#authentication) section.
   - **Token cache**: `~/.mstodo_token_cache.json` (persists across sessions, auto-refreshed)
   - **Device flow cache**: `~/.mstodo_device_flow.json` (temporary)

## Installation & Setup

### First-Time Setup

Before using this skill for the first time, dependencies must be installed:

```bash
# Navigate to skill directory
cd <path-to-ms-todo-sync>

# Install dependencies using uv (recommended - creates isolated environment)
uv sync

# Alternative: Install dependencies with pip (uses global/active Python environment)
pip install -r requirements.txt
```

**Dependencies:**
- Requires `msal` (Microsoft Authentication Library) and `requests`
- Specified in `requirements.txt`
- `uv` creates an isolated virtual environment to avoid conflicts

### Environment Verification

After installation, verify the setup:

```bash
# Check if uv can find the script
uv run scripts/ms-todo-sync.py --help

# Expected: Command help text should be displayed
```

**Troubleshooting:**
- If `uv: command not found`, install uv: `pip install uv`
- If `Python not found`, install Python 3.9 or higher from https://python.org
- If script fails with import errors, ensure dependencies are installed: `uv sync` or `pip install -r requirements.txt`

### Security Notes

- Uses official Microsoft Graph API via Microsoft's `msal` library
- All code is plain Python (.py files), readable and auditable
- Tokens stored locally in `~/.mstodo_token_cache.json`
- All API calls go directly to Microsoft endpoints

## Command Reference

All commands follow this pattern:

```
uv run scripts/ms-todo-sync.py [GLOBAL_OPTIONS] <command> [COMMAND_OPTIONS]
```

### Global Options

| Option | Description |
|--------|-------------|
| `-v, --verbose` | Show detailed information (IDs, dates, notes). **Must be placed BEFORE the subcommand.** |
| `--debug` | Enable debug mode to display API requests and responses. Useful for troubleshooting. **Must be placed BEFORE the subcommand.** |

> ⚠️ **Common mistake**: Global options MUST come before the subcommand.
> - ✅ `uv run scripts/ms-todo-sync.py -v lists`
> - ✅ `uv run scripts/ms-todo-sync.py --debug add "Task"`
> - ❌ `uv run scripts/ms-todo-sync.py lists -v`

---

### Authentication

Authentication uses a two-step device code flow designed for non-interactive/agent environments.

#### `login get` — Get verification code

```bash
uv run scripts/ms-todo-sync.py login get
```

**Output example:**
```
✓ Verification code generated

Please visit the following link to log in:
https://microsoft.com/devicelogin

Enter verification code: ABC123XYZ

Verify with command: ms-todo-sync.py login verify
```

**Agent behavior**: Present the URL and verification code to the user. Wait for the user to confirm they have completed the browser login before proceeding.

#### `login verify` — Complete login

```bash
uv run scripts/ms-todo-sync.py login verify
```

**Output on success:**
```
✓ Authentication successful! Login information saved, you will be logged in automatically next time.
```

**Output on failure:**
```
✗ Authentication failed: <error description>
```

> ⚠️ **This command blocks** until Microsoft's server confirms the user completed browser authentication. Do NOT run this until the user confirms they have completed the browser step.

**Exit code**: 0 on success, 1 on failure.

#### `logout` — Clear saved login

```bash
uv run scripts/ms-todo-sync.py logout
```

Only use when the user explicitly asks to switch accounts or clear login data. Under normal circumstances, the token is cached and login is automatic.

---

### List Management

#### `lists` — List all task lists

```bash
uv run scripts/ms-todo-sync.py lists
uv run scripts/ms-todo-sync.py -v lists  # with IDs and dates
```

**Output example:**
```
📋 Task Lists (3 total):

1. Tasks
2. Work
3. Shopping
```

#### `create-list` — Create a new list

```bash
uv run scripts/ms-todo-sync.py create-list "<name>"
```

| Argument | Required | Description |
|----------|----------|-------------|
| `name` | Yes | Name of the new list |

Output: `✓ List created: <name>`

#### `delete-list` — Delete a list

```bash
uv run scripts/ms-todo-sync.py delete-list "<name>" [-y]
```

| Argument/Option | Required | Description |
|-----------------|----------|-------------|
| `name` | Yes | Name of the list to delete |
| `-y, --yes` | No | Skip confirmation prompt |

> ⚠️ **This is a destructive operation**. Without `-y`, the command will prompt for confirmation. Consider asking the user before deleting important lists.

Output: `✓ List deleted: <name>`

---

### Task Operations

#### `add` — Add a new task

```bash
uv run scripts/ms-todo-sync.py add "<title>" [options]
```

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `title` | Yes | — | Task title (positional argument) |
| `-l, --list` | No | (default list) | Target list name. If not specified, uses your Microsoft To Do default list. |
| `-p, --priority` | No | `normal` | Priority: `low`, `normal`, `high` |
| `-d, --due` | No | — | Due date. Accepts days from now (`3` or `3d`) or date (`2026-02-15`). **Note:** Only date is supported, not time. |
| `-r, --reminder` | No | — | Reminder datetime. Formats: `3h` (hours), `2d` (days), `2026-02-15 14:30` (date+time with space, needs quotes), `2026-02-15T14:30:00` (ISO format), `2026-02-15` (date only, defaults to 09:00). |
| `-R, --recurrence` | No | — | Recurrence pattern. Formats: `daily` (every day), `weekdays` (Mon-Fri), `weekly` (every week), `monthly` (every month). With interval: `daily:2` (every 2 days), `weekly:3` (every 3 weeks), `monthly:2` (every 2 months). **Note:** Automatically sets start date. |
| `-D, --description` | No | — | Task description/notes |
| `-t, --tags` | No | — | Comma-separated tags (e.g., `"work,urgent"`) |

**Behavior:** If the specified list doesn't exist, it will be automatically created.

**Output example:**
```
✓ List created: Work
✓ Task added: Complete report
```

#### `complete` — Mark a task as completed

```bash
uv run scripts/ms-todo-sync.py complete "<title>" [-l "<list>"]
```

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `title` | Yes | — | Exact task title |
| `-l, --list` | No | (default list) | List name where the task resides. If not specified, uses your default list. |

Output: `✓ Task completed: <title>`

#### `delete` — Delete a task

```bash
uv run scripts/ms-todo-sync.py delete "<title>" [-l "<list>"] [-y]
```

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `title` | Yes | — | Exact task title |
| `-l, --list` | No | (default list) | List name. If not specified, uses your default list. |
| `-y, --yes` | No | — | Skip confirmation prompt |

> ⚠️ **This is a destructive operation**. Without `-y`, the command will prompt for confirmation. For routine cleanup or when user intent is clear, `-y` can be used to avoid blocking.

Output: `✓ Task deleted: <title>`

---

### Task Views

#### `tasks` — List tasks in a specific list

```bash
uv run scripts/ms-todo-sync.py tasks "<list>" [-a]
```

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `list` | Yes | — | List name (positional argument) |
| `-a, --all` | No | — | Include completed tasks (default: only incomplete) |

**Output example:**
```
📋 Tasks in list "Work" (2 total):

1. [In Progress] Write documentation ⭐
2. [In Progress] Review PR
```

#### `pending` — All incomplete tasks across all lists

```bash
uv run scripts/ms-todo-sync.py pending [-g]
```

| Option | Required | Description |
|--------|----------|-------------|
| `-g, --group` | No | Group results by list |

**Output example (with `-g`):**
```
📋 All incomplete tasks (3 total):

📂 Work:
  [In Progress] Write documentation ⭐
  [In Progress] Review PR

📂 Shopping:
  [In Progress] Buy groceries
```

#### `today` — Tasks due today

```bash
uv run scripts/ms-todo-sync.py today
```

Lists incomplete tasks with due date matching today. Output: `📅 No tasks due today` if none found.

#### `overdue` — Overdue tasks

```bash
uv run scripts/ms-todo-sync.py overdue
```

**Output example:**
```
⚠️  Overdue tasks (1 total):

[In Progress] Submit report ⭐
   List: Work
   Overdue: 3 days
```

#### `detail` — View full task details

```bash
uv run scripts/ms-todo-sync.py detail "<title>" [-l "<list>"]
```

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `title` | Yes | — | Task title (supports **partial/fuzzy match**) |
| `-l, --list` | No | (default list) | List name. If not specified, uses your default list. |

When multiple tasks match, returns the most recently modified **incomplete** task. If all matches are completed, returns the most recently modified completed task.

#### `search` — Search tasks by keyword

```bash
uv run scripts/ms-todo-sync.py search "<keyword>"
```

Searches across all lists in both task titles and notes (case-insensitive).

**Output example:**
```
🔍 Search results (1 found):

[In Progress] Write documentation ⭐
   List: Work
```

#### `stats` — Task statistics

```bash
uv run scripts/ms-todo-sync.py stats
```

**Output example:**
```
📊 Task Statistics:

  Total lists: 3
  Total tasks: 15
  Completed: 10
  Pending: 5
  High priority: 2
  Overdue: 1

  Completion rate: 66.7%
```

#### `export` — Export all tasks to JSON

```bash
uv run scripts/ms-todo-sync.py export [-o "<filename>"]
```

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `-o, --output` | No | `todo_export.json` | Output file path |

Output: `✓ Tasks exported to: <filename>`

---

## Error Handling

### Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Failure (not logged in, API error, invalid arguments, etc.) |

### Common Error Messages

| Error | Cause | Resolution |
|-------|-------|------------|
| `❌ Not logged in` | No cached token or token expired | Run `login get` then `login verify` |
| `ModuleNotFoundError: No module named 'msal'` | Dependencies not installed | Run `uv sync` or `pip install -r requirements.txt` |
| `❌ List not found: <name>` | Specified list does not exist | Check list name with `lists` command |
| `❌ Task not found: <name>` | No task with exact matching title | Check task title with `tasks` or `search` |
| `❌ Error: <message>` | API or network error | Retry; check network; use `--debug` for details |

---

## Agent Usage Guidelines

### Critical Rules

1. **Working directory**: Always `cd` to the directory containing this SKILL.md before running commands.
2. **Dependency installation**: Before first use or when encountering import errors, run `uv sync` to ensure all dependencies are installed.
3. **Task list organization**: When adding tasks:
   - First, run `lists` to see available task lists
   - If user doesn't specify a list, tasks will be added to their **default list** (wellknownListName: "defaultList")
   - Intelligently categorize tasks into appropriate lists (e.g., "Work", "Personal", "Shopping")
   - If user mentions a context (work, home, shopping, etc.), use or create an appropriate list
   - Lists will be auto-created if they don't exist, so feel free to use meaningful list names
4. **Destructive operations**: For `delete` and `delete-list` commands:
   - These commands will prompt for confirmation by default (blocking behavior)
   - Use `-y` flag to skip confirmation ONLY when:
     - User has explicitly requested to delete without confirmation
     - The deletion intent is unambiguous and confirmed through conversation
   - When in doubt, ask the user for confirmation instead of using `-y`
5. **Global option placement**: `-v` and `--debug` must come BEFORE the subcommand, not after.
6. **Do not retry `login verify` automatically**: This command blocks waiting for user browser interaction. Only call it after the user confirms completion.
7. **Check login status first**: Before performing any task operations, run a lightweight command (e.g., `lists`) to verify authentication. Handle the "Not logged in" error gracefully.

### Recommended Workflow for Agents

```
1. cd <skill_directory>
2. uv sync                                       # Ensure dependencies are installed (first time or after updates)
3. uv run scripts/ms-todo-sync.py lists          # Test auth & see available lists
   → If fails with exit code 1 ("Not logged in"):
     a. uv run scripts/ms-todo-sync.py login get  # Get code
     b. Present URL + code to user
     c. Wait for user confirmation
     d. uv run scripts/ms-todo-sync.py login verify
4. When adding tasks:
   → Analyze task context from user's description
   → Choose or create appropriate list name:
     - Work-related → "Work" list
     - Personal errands → "Personal" list  
     - Shopping items → "Shopping" list
     - Project-specific → Use project name as list
   → Add task with appropriate list via `-l` option
5. Verify results (e.g., list tasks after adding)
```

**Example task categorization:**
- \"Buy milk\" → Shopping list (or default list if no context)
- \"Prepare report for meeting\" → Work list
- \"Call dentist\" → Personal list (or default list)
- \"Review PR for auth service\" → Work or project-specific list

**Note:** If no list is specified, tasks are added to the user's default Microsoft To Do list.

### Task Title Matching

- `complete` and `delete` require **exact title match**.
- `detail` and `search` support **partial/fuzzy keyword match** (case-insensitive).
- When in doubt, use `search` first to find the exact title, then use it in subsequent commands.

### Default List Behavior

When `-l` is not specified, the tool uses your Microsoft To Do default list (typically "Tasks"). To target a specific list, provide the `-l` option.

---

## Quick Examples

```bash
# Check existing lists first
uv run scripts/ms-todo-sync.py lists

# Add task to specific list (list auto-created if needed)
uv run scripts/ms-todo-sync.py add "Report" -l "Work" -p high -d 3 -D "Q4 financials"

# Add task to default list (no -l option)
uv run scripts/ms-todo-sync.py add "Buy milk"

# Add task with reminder in 2 hours
uv run scripts/ms-todo-sync.py add "Call client" -r 2h

# Add task with specific reminder date and time
uv run scripts/ms-todo-sync.py add "Meeting" -d 2026-03-15 -r "2026-03-15 14:30"

# Add recurring tasks
uv run scripts/ms-todo-sync.py add "Daily standup" -l "Work" -R daily -d 7
uv run scripts/ms-todo-sync.py add "Weekly review" -R weekly -d 2026-02-17
uv run scripts/ms-todo-sync.py add "Gym" -R weekdays -l "Personal"  
uv run scripts/ms-todo-sync.py add "Monthly report" -R monthly -p high -d 30

# Search then complete (use exact title from search results)
uv run scripts/ms-todo-sync.py search "report"
uv run scripts/ms-todo-sync.py complete "Report" -l "Work"

# Delete (use -y only when user intent is clear)
uv run scripts/ms-todo-sync.py delete "Old task" -y

# Views
uv run scripts/ms-todo-sync.py -v pending -g          # all pending, grouped
uv run scripts/ms-todo-sync.py -v detail "report"      # task detail with fuzzy match
uv run scripts/ms-todo-sync.py export -o "backup.json"  # export all
```




