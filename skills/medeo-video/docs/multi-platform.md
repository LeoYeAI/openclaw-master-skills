# Multi-Platform Video Delivery

After a video is generated, deliver it natively via the user's IM channel for the best experience.

## Delivery Scripts

| Platform | Script | Key Args |
|----------|--------|----------|
| Feishu | `scripts/feishu_send_video.py` | `--video`, `--to` (open_id), `--cover-url`, `--duration` (ms) |
| Telegram | `scripts/telegram_send_video.py` | `--video`, `--to` (chat_id), `--cover-url`, `--duration` (seconds), `--caption` |
| Discord | OpenClaw `message` tool | `action="send"`, `channel="discord"`, `target`, `filePath` |

## Platform Notes

### Feishu
- Reads credentials from `~/.openclaw/openclaw.json` (never hardcode).
- Supports cover image and duration metadata.
- See [feishu-send.md](feishu-send.md) for full details.

### Telegram
- Pass bot token via env var: `TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN python3 scripts/telegram_send_video.py ...`
- Duration is in **seconds** (not milliseconds).
- Max file size: 50 MB via Bot API.

### Discord
- Use the OpenClaw `message` tool directly: `message(action="send", channel="discord", target="<channel_id>", message="🎬 Video ready!", filePath="/tmp/medeo_result.mp4")`
- Download the video to a local path first via `curl -sL -o /tmp/medeo_result.mp4 "<video_url>"`.
- Max file size: 25 MB (8 MB for non-Nitro servers). For larger files, share `video_url` as a link.

### WhatsApp / Signal / Other
- Use the OpenClaw `message` tool with `media` parameter.
- Fallback: share `video_url` as a plain link.

## Security

- **Never pass bot tokens as CLI arguments** — they are visible in `ps` output.
- Always use environment variables: `TELEGRAM_BOT_TOKEN`, `DISCORD_BOT_TOKEN`.
- Feishu credentials are read from config file automatically.
