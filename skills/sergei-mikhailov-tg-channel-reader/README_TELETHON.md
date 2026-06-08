# 📡 Telethon Version Guide

> Alternative implementation using Telethon instead of Pyrogram

## Why Telethon?

If you're experiencing issues with Pyrogram (e.g., authentication codes not arriving), you can use the Telethon version instead. Telethon is a mature, stable library with excellent Telegram API support.

## Installation

The Telethon version is included in the same package:

```bash
pip3 install -e .
```

This installs both commands:
- `tg-reader` (Pyrogram version)
- `tg-reader-telethon` (Telethon version)

## Setup

### Step 1 — Use the same API credentials

You can use the same `TG_API_ID` and `TG_API_HASH` from my.telegram.org:

```bash
export TG_API_ID=12345678
export TG_API_HASH=your_api_hash_here
```

### Step 2 — Authenticate with Telethon

```bash
tg-reader-telethon auth
```

This will:
1. Ask for your phone number (e.g., `+79991234567`)
2. Send a code to your Telegram app
3. Create a session file at `~/.telethon-reader.session`

**Note:** Telethon session files are different from Pyrogram sessions, so you'll need to authenticate separately.

### Step 3 — Start reading channels

```bash
# Last 24 hours from a channel
tg-reader-telethon fetch @durov --since 24h

# Last week, multiple channels
tg-reader-telethon fetch @channel1 @channel2 --since 7d --limit 200

# Human-readable format
tg-reader-telethon fetch @channel_name --since 24h --format text
```

## Usage Examples

### Fetch from a single channel
```bash
tg-reader-telethon fetch @durov --since 24h
```

### Fetch from multiple channels
```bash
tg-reader-telethon fetch @durov @telegram --since 7d --limit 50
```

### Get posts from a specific date
```bash
tg-reader-telethon fetch @channel --since 2026-02-01
```

### Include media information
```bash
tg-reader-telethon fetch @channel --since 24h --media
```

### Human-readable output
```bash
tg-reader-telethon fetch @channel --since 24h --format text
```

## Direct Python Usage

You can also run the script directly:

```bash
python3 -m reader_telethon auth
python3 -m reader_telethon fetch @durov --since 24h
```

## Differences from Pyrogram Version

| Feature | Pyrogram | Telethon |
|---------|----------|----------|
| Session file | `~/.tg-reader-session` | `~/.telethon-reader.session` |
| Command | `tg-reader` | `tg-reader-telethon` |
| Library | pyrogram + tgcrypto | telethon |
| Maturity | Modern, async-first | Mature, battle-tested |

## Troubleshooting

**Session file not found**
- Make sure you ran `tg-reader-telethon auth` first
- Check that `~/.telethon-reader.session` exists

**Authentication fails**
- Verify your API credentials are correct
- Try creating a new application on my.telegram.org
- Wait 10-15 minutes if you've made too many auth attempts

**Channel not found**
- Ensure the channel username is correct (with @)
- For private channels, make sure you're subscribed
- Try accessing the channel in your Telegram app first

## OpenClaw Integration

Once authenticated, OpenClaw can use either version:

```bash
# Use Pyrogram version (default)
tg-reader fetch @channel --since 24h

# Use Telethon version (alternative)
tg-reader-telethon fetch @channel --since 24h
```

You can configure which version to use in your OpenClaw skill settings.

## License

MIT — same as the main project