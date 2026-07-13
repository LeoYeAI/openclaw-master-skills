# Sync

Claw Drive can auto-sync to Google Drive (or any rclone-supported backend) via a background daemon.

## Architecture

```
~/claw-drive/  (local, source of truth)
      │
      ├── fswatch (file watcher)
      │       │
      │       └── rclone sync → Google Drive (cloud backup)
      │
      └── launchd (keeps daemon alive)
```

Local is always the source of truth. Cloud sync is optional backup + cross-device access.

## Prerequisites

```bash
brew install rclone fswatch
rclone config  # set up a remote (e.g. "gdrive")
```

## Configuration

Create `~/claw-drive/.sync-config`:

```yaml
backend: google-drive
remote: gdrive:claw-drive
exclude:
  - identity/
  - .hashes
```

### Fields

| Field | Description |
|-------|-------------|
| `backend` | Backend name (informational) |
| `remote` | rclone remote:path |
| `exclude` | List of paths/patterns to never sync |

## Commands

```bash
claw-drive sync setup    # verify deps and config
claw-drive sync start    # start background daemon
claw-drive sync stop     # stop daemon
claw-drive sync push     # manual one-shot sync
claw-drive sync status   # show daemon state + last sync time
```

## Daemon

`claw-drive sync start` installs a launchd service (`com.claw-drive.sync`) that:

1. Watches `~/claw-drive/` with fswatch
2. On any file change, waits 3 seconds (debounce)
3. Runs `rclone sync` to the configured remote
4. Records the sync timestamp in `.sync-state`

The daemon starts on login and restarts on failure.

**Logs:** `~/Library/Logs/claw-drive/sync.log`

## Privacy

Use the `exclude` list to keep sensitive directories local-only:

```yaml
exclude:
  - identity/     # never leaves the machine
  - .hashes       # internal ledger
```

Files in excluded directories are fully functional locally — they just don't sync.
