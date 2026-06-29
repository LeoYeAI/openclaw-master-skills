---
name: mmxagent-guardian
version: 1.0.3
description: Provide file protection while users work with openclaw. All file operations are version-indexed and support delete recovery and modification rollback.
---

# File Protection and Version Management

This Skill uses MiniVCS to track all file operations with version history.

**Runtime requirement**: Python 3 is required to run `scripts/minivcs/minivcs.py`.

**Script location**: `scripts/minivcs/minivcs.py` in the same directory as this `SKILL.md`
(Before executing, first determine the directory containing this file. It is referred to as `$SKILL_DIR` below.)

**Core mechanism:**
- **Modify**: Saves an incremental diff plus a full snapshot from before the modification, **supporting rollback**
- **Delete**: Moves the full file into `~/.openclaw/minivcs/trash/`, **supporting restore**
- **All files are indexed**, with different retention periods based on importance
- **After every operation, the full record table is scanned automatically** to find expired records and ask the user for confirmation

**Usage limitations:**
- **Binary files (images, PDFs, audio/video, etc.)**: Text diffs cannot be generated. For binary-file protection, MiniVCS stores a full local `.bak` copy instead. This applies to binary-file backup/rollback protection, and deletion protection also stores a full local copy in `~/.openclaw/minivcs/trash/`. The user must be informed before the operation because storage usage may be relatively high.
- **The first record cannot be rolled back**: When a file is recorded for the first time, there is not yet any historical baseline, so that record has no snapshot. After that, each call to `record_modify` following an edit automatically saves a snapshot, allowing rollback to the state before any edit.
- **Local storage notice**: Protection data is stored locally under `~/.openclaw/minivcs/`. This Skill does not provide encryption or remote sync.

---

## Prerequisite Check: Confirm Python Is Installed

**Before performing any operation, you must first check whether Python 3 is installed in the user's environment. This Skill requires Python 3 and should not run without it.**

### How to check

```bash
# macOS / Linux
python3 --version

# Windows (PowerShell)
python --version
```

- If the output is `Python 3.x.x`, it is installed and you can continue
- If it says `command not found` or `is not recognized as an internal or external command`, stop and tell the user that this Skill requires Python 3

### Dependency boundary

If Python 3 is missing:

- Do **not** run dependency installation commands from this Skill
- Do **not** run remote install scripts such as `curl | bash`
- Do **not** write to shell config files such as `~/.zshrc` or `~/.bash_profile`
- Do **not** modify global environment variables on the user's behalf from this Skill
- Tell the user that Python 3 is required, and ask them to install it first or explicitly authorize a separate environment-setup flow

> **Note**: On some Windows systems the command is `python`, while on macOS/Linux it is `python3`.
> In all commands below that use `python`, replace it with the correct command for the actual environment.

---

## Retention Policy

| File Type | Retention Days | Decision Rule |
|---------|---------|---------|
| Important files | **14 days** | System paths (`/etc/`, `/root/`, `/usr/local/etc/`, `/opt/`), user config directories (`~/.ssh/`, `~/.gnupg/`, `~/.config/`, `~/.openclaw/`, `~/.kube/`, `~/.docker/`, `~/.aws/`, `~/.azure/`, `~/.local/share/`), Windows system directories (`C:\Windows\`, `C:\ProgramData\`, `C:\Program Files\`), config files (`.yaml/.toml/.env`, etc.), entry files (`main.py/index.ts`, etc.) |
| Normal files | **7 days** | All other files |

When each record is created, the `expireAt` (expiration timestamp) and `expireAtDatetime` (human-readable time) fields are set automatically.

---

## Excluded Paths (Auto-Skip)

Files whose path contains any of the following segments are **automatically skipped** by `record_modify` and `record_delete`. These are generated, vendored, or cache directories that should not be version-tracked:

`node_modules`, `.git`, `__pycache__`, `.venv`, `venv`, `.tox`, `.mypy_cache`, `.pytest_cache`, `.ruff_cache`, `dist`, `build`, `.next`, `.nuxt`, `.turbo`

When a file is skipped, the return value will contain `"skipped": true` and a `"reason"` field. The Agent should inform the user that the file was not tracked and explain why.

---

## Binary File Size Warning

When a binary file exceeds **50 MB**, the return value from `record_modify` (binary backup) will include:
- `"sizeWarning": true`
- `"sizeWarningMessage"`: a human-readable description of the file size and threshold

**When `sizeWarning` is present, the Agent must explicitly inform the user of the file size and ask for confirmation before proceeding with any further binary backup operations on similarly large files.**

---

## Operation Flow

### Step 1: Initialize the MiniVCS Working Directory

On first use, the storage directory is created automatically. No extra action is required:

```bash
python "$SKILL_DIR/scripts/minivcs/minivcs.py" history --project-root <project_root>
```

All data is stored uniformly in `~/.openclaw/minivcs/`:
```
~/.openclaw/minivcs/
  logs.json     # operation log (includes the expireAt field)
  diffs/        # incremental patches for text file modifications
  bases/        # baseline for the next comparison (named by full relative path, so no same-name conflicts)
  snapshots/    # full snapshots before text file modifications (used for rollback)
  trash/        # full backups of deleted files (used for restore)
  backups/      # full `.bak` copies of binary files (used for rollback)
```

---

### Step 2: Ask the User for Confirmation Before the Operation

**Before deleting or modifying a file, you must explain the following to the user and wait for confirmation:**

1. The file path to be operated on
2. The operation type (modify / delete)
3. The purpose and intent of the operation
4. The possible impact
5. **Explain the local storage behavior: this Skill stores protection data under `~/.openclaw/minivcs/`**
6. **For text-file modifications, explain that MiniVCS stores diffs and snapshots so the file can be rolled back**
7. **For deletions, explain that MiniVCS stores a full local copy in `~/.openclaw/minivcs/trash/` so the file can be restored**
8. **If the file is binary, explicitly explain that protection uses a full local copy rather than a text diff, and ask whether the user wants that local copy to be stored before deletion or binary-file protection**
9. **If a binary backup returns `sizeWarning: true`, the Agent must display the file size and warning message to the user, and ask for explicit confirmation before proceeding**

If the file is binary and the user does **not** want a local stored copy, do not treat the operation as a protected delete/rollback flow under this Skill.

If the path is auto-skipped (return contains `"skipped": true`), inform the user that the file was not tracked and state the reason.

Example before the operation:
```
I am about to operate on the following file. Please confirm:
- File: /path/to/file.py
- Operation: delete
- Reason: This file has been replaced by a newer version and is no longer used
- Impact: Need to confirm that no other module imports this file
- Local storage: A full local copy will be stored under ~/.openclaw/minivcs/trash/ so the file can be restored later
- Protection: The stored copy will be retained for 7 days (14 days for important files), and can be restored at any time during that period
Do you want to continue?
```

Example for a binary file before deletion:
```
I am about to delete the following binary file. Please confirm:
- File: /path/to/file.pdf
- Operation: delete
- Reason: This file is no longer needed
- Impact: The original file will be removed from its current location
- Local storage: To protect this binary file, I need to store one full local copy under ~/.openclaw/minivcs/trash/
- Note: Binary files are protected with full copies rather than text diffs, so this may use more disk space
Do you want me to keep that local backup before deletion?
```

After the operation completes, **you must inform the user of the record result**, for example:
```
# After a modification is completed
The modification to path/to/file.py has been completed, and this change has been recorded (Record ID: 1710000000000).
- Change summary: +5 lines, -2 lines
- Retention period: 7 days (expires at: 2026-03-20 10:00:00)
- Rollback available: yes (use restore 1710000000000 to recover the state before the modification)
If you want to view the diff or roll it back, let me know.

# After a deletion is completed
path/to/file.py has been moved to the trash and backed up (Record ID: 1710000001000).
- Retention period: 14 days (expires at: 2026-03-27 10:00:00) [important file]
If you want to restore this file, let me know.
```

---

### Step 3: Operate on Files with MiniVCS

#### Modify a file (supports rollback)

**Just call `record` once after each edit**. The snapshot chain is formed automatically and supports rolling back to any historical state:

```
First time using this file → record() → base established (no snapshot, first record cannot be rolled back)
Edit → C1                → record() → snapshot=initial content,  R1 rollback available
Edit → C2                → record() → snapshot=C1,               R2 rollback available → restoring R2 gives C1
Edit → C3                → record() → snapshot=C2,               R3 rollback available → restoring R3 gives C2 (that is, the state at time t2)
```

```bash
# Run once after each edit is completed
python "$SKILL_DIR/scripts/minivcs/minivcs.py" record <file_path> --project-root <project_root>
# Output containing "Rollback: available" means the snapshot has been saved and can be rolled back
```

Python API:
```python
import sys, os
sys.path.insert(0, os.path.join(SKILL_DIR, "scripts", "minivcs"))
from minivcs import MiniVCS

vcs = MiniVCS(project_root="/path/to/project")

# Call once after each edit
result = vcs.record_modify("path/to/file.py")
# result includes:
# {
#   "success": True,
#   "recordId": "...",
#   "summary": "+5 lines, -2 lines",
#   "canRollback": True,   # True when a snapshot exists; False for the first record
#   "snapshotFile": "...",
#   "isImportant": False,
#   "retentionDays": 7,
#   "due_for_cleanup": [...]
# }
```

#### Delete a file (supports restore)

**Do not delete the file directly**. Use `record_delete` instead, and the file is moved into `trash` automatically.

Before running `record_delete`:

- Tell the user that a full local copy will be stored in `~/.openclaw/minivcs/trash/`
- If the file is binary, explicitly ask whether they want that local copy to be stored
- Only proceed with protected deletion after the user confirms the local storage behavior

```bash
python "$SKILL_DIR/scripts/minivcs/minivcs.py" delete <file_path> --project-root <project_root>
```

Python API:
```python
result = vcs.record_delete("path/to/file.py")
# result includes:
# {
#   "success": True,
#   "recordId": "...",
#   "trashFile": "~/.openclaw/minivcs/trash/1234567_file.py.bak",
#   "isImportant": True,
#   "retentionDays": 14,
#   "due_for_cleanup": [...]
# }
```

#### Restore / Roll back

The same `restore` command handles both scenarios:

```bash
# DELETE record -> restore the file to its original path
# MODIFY record (with snapshot) -> roll back to the state before the modification
python "$SKILL_DIR/scripts/minivcs/minivcs.py" restore <record_id> --project-root <project_root>
```

Python API:
```python
result = vcs.restore_file(record_id="...")
# After DELETE succeeds: the record is marked as RESTORED and no longer appears in the trash list
# After MODIFY succeeds: the record is marked as ROLLED_BACK
# Repeated restore: returns {"success": False, "error": "already been restored/rolled_back"}
```

---

### Step 4: Handle Expired Cleanup Notifications (must be done after every operation)

After each call to `record_modify` or `record_delete`, the return value contains the `due_for_cleanup` field.

**If `due_for_cleanup` is not empty, the Agent must:**

1. Show the user the list of expired records (sorted from earliest to latest)
2. Ask which ones can be deleted and which ones need an extension

Example display format:
```
The following N historical records have expired. Please confirm whether they can be cleaned up:

[1] ID=1710000000000  File=src/old.py  Action=MODIFY
    Recorded at=2026-03-01 10:00:00  Expires at=2026-03-08 10:00:00

[2] ID=1710000001000  File=config.yaml  Action=DELETE  [important file]
    Recorded at=2026-02-28 09:00:00  Expires at=2026-03-14 09:00:00

Can these records be deleted? (delete all / specify which ones to extend)
```

Handling after the user responds:

```python
# The user confirms deleting all
result = vcs.delete_due_records(record_ids=["id1", "id2"])

# The user says not to delete one record yet -> extend by one retention cycle (7 days or 14 days)
result = vcs.extend_record_expiry(record_id="id1")
```

Command line:
```bash
# View all expired records
python "$SKILL_DIR/scripts/minivcs/minivcs.py" cleanup --project-root <project_root>

# Confirm cleanup
python "$SKILL_DIR/scripts/minivcs/minivcs.py" cleanup --confirm --project-root <project_root>

# Extend one record
python "$SKILL_DIR/scripts/minivcs/minivcs.py" extend <record_id> --project-root <project_root>
```

---

## Other Common Operations

```bash
# View operation history (records marked [rollback available] can be rolled back)
python "$SKILL_DIR/scripts/minivcs/minivcs.py" history --project-root <project_root>
python "$SKILL_DIR/scripts/minivcs/minivcs.py" history <file_path> -d --project-root <project_root>

# View files in trash that have not yet been restored
python "$SKILL_DIR/scripts/minivcs/minivcs.py" trash --project-root <project_root>

# Delete a specified record (clean both the log and the physical file)
python "$SKILL_DIR/scripts/minivcs/minivcs.py" remove <record_id> --project-root <project_root>
```

---

## Record Field Reference

| Field | Type | Description |
|------|------|------|
| `recordId` | string | Unique record ID (millisecond timestamp) |
| `filePath` | string | Relative or absolute path |
| `action` | string | `MODIFY` / `DELETE` / `BINARY_BACKUP` / `RESTORED` / `ROLLED_BACK` |
| `timestamp` | number | Creation time (milliseconds) |
| `datetime` | string | Creation time (human-readable) |
| `isImportant` | bool | Whether the file is important |
| `retentionDays` | number | Retention days (7 or 14) |
| `expireAt` | number | Expiration time (milliseconds) |
| `expireAtDatetime` | string | Expiration time (human-readable) |
| `diffFile` | string | Diff patch path (MODIFY only) |
| `snapshotFile` | string | Pre-modification snapshot path (only present when MODIFY has a snapshot) |
| `trashFile` | string | Trash backup path (DELETE only) |
| `backupFile` | string | `.bak` copy path (BINARY_BACKUP only) |
| `summary` | string | Change summary |

---

## Full Operation Flow Diagram

```
The user requests a modification/deletion
       │
       ▼
[Ask for confirmation] Explain the purpose, impact, and existing protection -> wait for user confirmation
       │
       ├─── Modify file ───────────────────────────────────────────────┐
       │    1. Perform the actual modification                         │
       │    2. record_modify (Diff + snapshot -> canRollback=True)    │
       │       snapshot = content before this modification, so        │
       │       historical states can be rolled back step by step      │
       │                                                             │
       └─── Delete file ──────────────────────────────────────────────┤
            record_delete (move to trash, do not delete directly)     │
                                                                     │
                           ┌─────────────────────────────────────────┘
                           ▼
              Tell the user: Record ID / retention period / rollback or restore availability
                           │
                           ▼
              Check the returned value `due_for_cleanup`
                           │
               ┌───────────┴───────────┐
            Expired records exist    No expired records
               │                         │
               ▼                         ▼
       Show expired records            Operation complete
       (from earliest to latest)
       Ask the user for confirmation
               │
       ┌───────┴──────────┐
     Confirm deletion    Do not delete yet
       │                  │
       ▼                  ▼
delete_due_records   extend_record_expiry
                     (extend by one retention cycle)

------- When the user needs rollback/restore -------
User: "Help me restore/roll back xxx"
       │
       ▼
restore_file(record_id)
  ├── DELETE record -> restore from trash and mark as RESTORED
  └── MODIFY record (with snapshot) -> write back snapshot content and mark as ROLLED_BACK
```
