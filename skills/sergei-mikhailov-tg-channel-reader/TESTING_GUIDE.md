# 🧪 Testing Guide for Telethon Version

## Quick Start Testing

### 1. Verify Installation
```bash
# Check that both commands are available
which tg-reader
which tg-reader-telethon

# Check Telethon version
python3 -c "import telethon; print('Telethon version:', telethon.__version__)"
```

### 2. Verify Environment Variables
```bash
# Make sure API credentials are set
echo $TG_API_ID
echo $TG_API_HASH

# If empty, set them:
export TG_API_ID=your_api_id
export TG_API_HASH=your_api_hash
```

### 3. Authenticate with Telethon
```bash
tg-reader-telethon auth
```

**What to expect:**
- Prompt for phone number (format: `+79991234567`)
- Code sent to Telegram app (check all devices)
- If 2FA enabled, prompt for password
- Success message with session file location

**Session file location:** `~/.telethon-reader.session`

### 4. Test Fetching Posts

#### Test 1: Single channel, 24 hours
```bash
tg-reader-telethon fetch @durov --since 24h
```

#### Test 2: Multiple channels
```bash
tg-reader-telethon fetch @durov @telegram --since 7d --limit 50
```

#### Test 3: Human-readable format
```bash
tg-reader-telethon fetch @durov --since 24h --format text
```

#### Test 4: With media information
```bash
tg-reader-telethon fetch @durov --since 24h --media
```

## Alternative: Direct Python Execution

If the command doesn't work, run directly:

```bash
# Authenticate
python3 -m reader_telethon auth

# Fetch posts
python3 -m reader_telethon fetch @durov --since 24h
```

## Troubleshooting

### Code not arriving
1. Check all Telegram devices (phone, desktop, web)
2. Look in "Telegram" service chat or "Saved Messages"
3. Wait 2-3 minutes
4. If still nothing, wait 10-15 minutes and try again (rate limiting)

### Session file issues
```bash
# Check if session exists
ls -la ~/.telethon-reader.session*

# Remove old session and re-authenticate
rm ~/.telethon-reader.session*
tg-reader-telethon auth
```

### Import errors
```bash
# Reinstall dependencies
pip3 install --upgrade telethon

# Verify installation
python3 -c "from telethon import TelegramClient; print('OK')"
```

### Permission errors
```bash
# Check file permissions
ls -la ~/.telethon-reader.session

# Fix if needed
chmod 600 ~/.telethon-reader.session
```

## Expected Output Format

### JSON format (default)
```json
{
  "channel": "@durov",
  "fetched_at": "2026-02-22T16:00:00+00:00",
  "since": "2026-02-21T16:00:00+00:00",
  "count": 5,
  "messages": [
    {
      "id": 123,
      "date": "2026-02-22T10:30:00+00:00",
      "text": "Message content...",
      "views": 50000,
      "forwards": 1200,
      "link": "https://t.me/durov/123"
    }
  ]
}
```

### Text format
```
=== @durov (5 posts since 24h) ===

[2026-02-22T10:30:00+00:00] https://t.me/durov/123
Message content here...

[2026-02-22T08:15:00+00:00] https://t.me/durov/122
Another message...
```

## Performance Comparison

| Metric | Pyrogram | Telethon |
|--------|----------|----------|
| Auth reliability | ⚠️ Variable | ✅ Excellent |
| Speed | ✅ Fast | ✅ Fast |
| Memory usage | ✅ Low | ✅ Low |
| Session compatibility | Pyrogram only | Telethon only |

## Next Steps

After successful testing:
1. ✅ Verify both `auth` and `fetch` commands work
2. ✅ Test with multiple channels
3. ✅ Test different time ranges (`24h`, `7d`, `2w`)
4. ✅ Test both JSON and text output formats
5. ✅ Document any issues or edge cases

## Integration with OpenClaw

Once tested, you can configure OpenClaw to use the Telethon version by default:

```bash
# In your OpenClaw skill configuration
SKILL_COMMAND="tg-reader-telethon"
```

Or keep both versions available and let the agent choose based on context.