---
title: CLI Commands
description: All shiploop commands and options
---

## Global Options

```bash
shiploop [-c CONFIG] [-v] [--version] <command>
```

| Option | Description |
|--------|-------------|
| `-c, --config` | Path to SHIPLOOP.yml (default: `./SHIPLOOP.yml`) |
| `-v, --verbose` | Enable debug logging |
| `--version` | Show version and exit |

## Commands

### `shiploop init`

Create a new `SHIPLOOP.yml` in the current directory.

```bash
cd /path/to/project
shiploop init
```

Auto-detects:
- **Framework:** Node.js, Python, Rust, Go (from package.json, pyproject.toml, Cargo.toml, go.mod)
- **Deploy provider:** Vercel, Netlify (from vercel.json, netlify.toml)
- **Git remote:** from `git remote get-url origin`

Prompts for project name, site URL, and agent selection.

### `shiploop run`

Start or resume the pipeline.

```bash
shiploop run
shiploop -v run          # With debug logging
shiploop -c custom.yml run  # Custom config
```

Processes segments in dependency order. Resumes from the last checkpoint if interrupted.

### `shiploop status`

Show the current state of all segments.

```bash
shiploop status
```

Output:

```
🚢 Ship Loop: My App
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. ✅ dark-mode: shipped [a1b2c3d]
  2. 🔧 contact-form: repairing (depends: dark-mode)
  3. ⏳ search: pending

  1/3 shipped, 0 failed, 1 pending
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### `shiploop reset <segment>`

Reset a segment back to `pending`.

```bash
shiploop reset contact-form
```

Clears the segment's commit, tag, and deploy URL. Use this to retry a failed segment.

### `shiploop learnings list`

Show all recorded learnings.

```bash
shiploop learnings list
```

### `shiploop learnings search <query>`

Search learnings by keyword.

```bash
shiploop learnings search "build import module"
```

### `shiploop budget`

Show cost summary for the current run.

```bash
shiploop budget
```

Output:

```
💰 Budget Summary: My App
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total cost:       $3.84
  Budget remaining:  $46.16
  Total records:    8

  By segment:
    dark-mode: $0.42
    contact-form: $3.42
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
