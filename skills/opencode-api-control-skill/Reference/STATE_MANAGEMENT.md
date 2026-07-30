# State Management Guide

## Overview

OpenCode skill maintains session state in `./state/` directory. State persistence allows continuing work across multiple tool invocations since bash variables don't persist between calls.

## State Directory Structure
```
./state/
├── current.json           # Active session
├── project-name.json      # Saved project states
└── init.json             # Initial configuration
```

## State File Format
```json
{
  "base_url": "http://127.0.0.1:4099",
  "project_path": "/home/user/projects/my-app",
  "session_id": "ses_abc123xyz",

  "provider_id": "opencode",
  "model_id": "gpt-5.1-codex",
  "timestamp": "2026-02-16T10:30:00Z"
}
```

## Core Operations

### Save Current Session

After creating or switching sessions:
```bash
bash ./scripts/save_state.sh "$SESSION_ID" "$PROJECT_PATH"
```

**What it does**:
- Saves session ID and project path

- Records current provider/model
- Adds timestamp

### Load Current Session

Before any operation requiring session context:
```bash
source ./scripts/load_state.sh
```

**What it sets**:
- `$BASE_URL` - API endpoint
- `$SESSION_ID` - Active session
- `$PROJECT_PATH` - Project directory

- `$PROVIDER_ID` - Current provider
- `$MODEL_ID` - Current model

**Important**: Use `source` not `bash` to export variables to current shell.

### Save Project State

Create named checkpoint:
```bash
bash ./scripts/save_project.sh "project-name"
```

Saves `current.json` → `project-name.json`

### Load Project State

Restore named checkpoint:
```bash
bash ./scripts/load_project.sh "project-name"
```

Copies `project-name.json` → `current.json`

## Usage Patterns

### Pattern 1: New Session
```bash
# Create session
SESSION_ID=$(bash ./scripts/create_session.sh "$PROJECT_PATH" "Title")

# State is automatically saved
# No need to call save_state.sh manually
```

**Note**: `create_session.sh` automatically calls `save_state.sh`.

### Pattern 2: Continue Existing Session
```bash
# Load state from previous session
source ./scripts/load_state.sh

# Now use $SESSION_ID, $PROJECT_PATH, etc.
bash ./scripts/send_message.sh "Continue work"
```

### Pattern 3: Multiple Projects
```bash
# Project A
bash ./scripts/create_session.sh "$PROJECTS_DIR/app-a" "App A"
bash ./scripts/save_project.sh "app-a"

# Project B
bash ./scripts/create_session.sh "$PROJECTS_DIR/app-b" "App B"
bash ./scripts/save_project.sh "app-b"

# Switch back to A
bash ./scripts/load_project.sh "app-a"
source ./scripts/load_state.sh
# Now working with App A

# Switch to B
bash ./scripts/load_project.sh "app-b"
source ./scripts/load_state.sh
# Now working with App B
```

### Pattern 4: Check Active Session
```bash
# View current state
cat ./state/current.json | jq

# Or load and echo
source ./scripts/load_state.sh
echo "Session: $SESSION_ID"
echo "Project: $PROJECT_PATH"
```

## State Lifecycle
```
1. Create Session
   ↓
   create_session.sh
   ↓
   Automatically saves to current.json

2. Work with Session
   ↓
   source load_state.sh
   ↓
   Variables available in shell

3. Save Checkpoint (optional)
   ↓
   save_project.sh "name"
   ↓
   Named backup created

4. Load Checkpoint (later)
   ↓
   load_project.sh "name"
   ↓
   Restores to current.json
```

## Best Practices

### ✅ DO

1. **Load state at workflow start**:
```bash
   source ./scripts/load_state.sh
```

2. **Save checkpoints for important projects**:
```bash
   bash ./scripts/save_project.sh "important-project"
```

3. **Use descriptive project names**:
```bash
   save_project.sh "frontend-dashboard"  # Good
   save_project.sh "proj1"               # Bad
```

4. **Check if state exists before loading**:
```bash
   if [ -f ./state/current.json ]; then
     source ./scripts/load_state.sh
   else
     echo "No active session"
   fi
```

### ❌ DON'T

1. **Don't assume variables persist**:
```bash
   # Wrong - variables lost in new tool call
   SESSION_ID="ses_123"
   # ... new tool call ...
   echo $SESSION_ID  # Empty!
```

2. **Don't manually edit state files**:
   - Use scripts to ensure consistency
   - Manual edits can break format

3. **Don't forget to source load_state.sh**:
```bash
   bash ./scripts/load_state.sh  # Wrong - doesn't export
   source ./scripts/load_state.sh  # Correct
```

4. **Don't mix projects without loading**:
```bash
   # Wrong
   create_session.sh "$PROJECT_A"
   send_message.sh "task"  # Uses wrong project!
   
   # Correct
   create_session.sh "$PROJECT_A"
   source ./scripts/load_state.sh
   send_message.sh "task"
```

## Troubleshooting

### "No active session"

**Cause**: No `current.json` file

**Solution**:
```bash
# Create new session first
bash ./scripts/create_session.sh "$PROJECT_PATH" "Session Title"
```

### Variables are empty after loading

**Cause**: Used `bash` instead of `source`

**Solution**:
```bash
source ./scripts/load_state.sh  # Correct
```

### State file corrupted

**Cause**: Manual editing or incomplete save

**Solution**:
```bash
# If you have project backup
bash ./scripts/load_project.sh "project-name"

# Otherwise, create new session
bash ./scripts/create_session.sh "$PROJECT_PATH" "New Session"
```

### Multiple sessions interfering

**Cause**: Not loading state between operations

**Solution**:
```bash
# Always load before operations
source ./scripts/load_state.sh
bash ./scripts/send_message.sh "prompt"
```

## Advanced: State Inspection

### List all saved projects
```bash
ls -1 ./state/*.json | \
  grep -v 'current.json\|init.json' | \
  xargs -n1 basename -s .json
```

### View project details
```bash
cat ./state/project-name.json | jq '{
  session: .session_id,
  project: .project_path,
  provider: .provider_id,
  model: .model_id,
  time: .timestamp
}'
```

### Find old sessions
```bash
# Sessions older than 7 days
find ./state -name "*.json" -mtime +7 | \
  grep -v 'current.json'
```

### Clean old states
```bash
# Backup first!
mkdir -p ./state/archive
mv ./state/old-project.json ./state/archive/
```

## State File Size

Typical state file: **< 1KB**

State files are tiny JSON files containing only:
- URLs and paths
- Session IDs
- Configuration values
- Timestamps

**No large data stored** - actual session content lives in OpenCode server.

---
**Author:** [Malek RSH](https://github.com/malek262) | **Repository:** [OpenCode-CLI-Controller](https://github.com/malek262/opencode-api-control-skill)
