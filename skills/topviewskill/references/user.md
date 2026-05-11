# User Module

Check your credit balance and review credit consumption history.

## When to Use

- Before running a generation task, verify you have enough credits.
- After running tasks, review usage history and costs.

## Usage

```bash
python {baseDir}/scripts/user.py <command> [options]
```

## Commands

### `credit` — Check Balance

```bash
python {baseDir}/scripts/user.py credit
```

Output:

```
Credit balance: 1000
```

With `--json`:

```bash
python {baseDir}/scripts/user.py credit --json
```

### `logs` — Usage History

```bash
python {baseDir}/scripts/user.py logs
```

With filters:

```bash
python {baseDir}/scripts/user.py logs \
  --type m2v \
  --start "2024-01-01 00:00:00" \
  --end "2024-12-31 23:59:59" \
  --page 1 \
  --size 50
```

## Options

### Global

| Option | Description |
|--------|-------------|
| `--json` | Output full JSON response |
| `-q, --quiet` | Suppress status messages |

### `logs`

| Option | Description |
|--------|-------------|
| `--type TYPE` | Filter by task type (see below) |
| `--start TIME` | UTC start time (`yyyy-MM-dd HH:mm:ss`) |
| `--end TIME` | UTC end time |
| `--page N` | Page number (default: 1) |
| `--size N` | Items per page (default: 20) |

### Task Types

| Value | Description |
|-------|-------------|
| `m2v` | Marketing video |
| `common_task_image2video` | Image to video |
| `video_avatar` | Video avatar |
| `product_avatar_image2video` | Product avatar |
| `voice_clone` | Voice clone |
| `product_anyfit` | Product AnyShoot |
