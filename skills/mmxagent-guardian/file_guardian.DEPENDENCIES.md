# file-guardian dependency notes

## Python dependencies

| Dependency | Source | Purpose |
|------|------|------|
| os | standard library | Path handling, directory creation, environment paths |
| sys | standard library | Platform detection, CLI entry |
| json | standard library | Read/write MiniVCS log records |
| time | standard library | Record IDs and timestamps |
| shutil | standard library | Move/copy files for trash and backup flows |
| difflib | standard library | Generate text diffs |
| argparse | standard library | CLI argument parsing |
| datetime | standard library | Human-readable timestamps |
| typing | standard library | Type annotations |

Only the Python standard library is used. There are no `pip` dependencies and no project-internal Python dependencies.

## External runtime requirement

| Dependency | Version | Purpose |
|------|------|------|
| Python 3 | required | Run `file-guardian/scripts/minivcs/minivcs.py` |

Notes:

- On macOS/Linux, the command is typically `python3`
- On some Windows environments, the command may be `python`
- This dependency file documents the runtime requirement only. It does not authorize installation or shell-environment changes from within the Skill

## Bundled files

| File | Purpose |
|------|------|
| `file-guardian/SKILL.md` | Skill instructions and operating constraints |
| `file-guardian/scripts/minivcs/minivcs.py` | Local MiniVCS implementation used by the Skill |

## Local storage behavior

When protection is used, MiniVCS stores local data under `~/.openclaw/minivcs/`, including:

- `logs.json`
- `diffs/`
- `bases/`
- `snapshots/`
- `trash/`
- `backups/`

This is local runtime data, not an additional package dependency.
