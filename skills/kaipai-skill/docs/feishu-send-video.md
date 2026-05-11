# Sending processed video via Feishu

After a **video** task completes (`videoscreenclear`, `hdvideoallinone`), prefer **native video messages** instead of sending only a link.

## Script

```bash
python3 {baseDir}/scripts/feishu_send_video.py \
  --video /tmp/kaipai_result.mp4 \
  --to "oc_xxx_or_ou_xxx" \
  --video-url "<primary_result_url>" \
  [--cover-url "https://…"] \
  [--duration <milliseconds>]
```

Download the result first:

```bash
curl -sL -o /tmp/kaipai_result.mp4 "<primary_result_url>"
```

Pass the **same** URL to `--video-url` so the script can send a **second** text message with a clickable download link. That runs **after** the native video step (upload + `msg_type: media`), whether or not the video card send succeeds—so users still get a link if the card fails (for example some API errors).

## Parameters

| Flag | Required | Notes |
|------|----------|--------|
| `--video` | Yes | Local file path (typically `.mp4`) |
| `--to` | Yes | `oc_` group chat id or `ou_` open id; `chat:` / `user:` prefixes are stripped |
| `--video-url` | No | When set, always sends an extra **text** message with `[链接](url)` style download text |
| `--cover` / `--cover-url` | No | Cover image — **strongly recommended** (otherwise preview can look blank) |
| `--duration` | No | Duration in **milliseconds** for Feishu upload metadata |

## Modes

- **Video card** — `msg_type: media` after upload to Feishu IM files + optional image cover.
- **Link text** — optional second message when `--video-url` is set.
- Credentials are read from **`~/.openclaw/openclaw.json`** (`channels.feishu.accounts`), same as `feishu_send_image.py`.

## Stdout JSON

The script prints one JSON object: `status` is `ok` if at least one of native video or (when `--video-url` is set) text send succeeds. Fields include `media_message_id`, `text_message_id`, `file_key`, and on failure `media_error` / `text_error`. `message_id` is kept as an alias for `media_message_id` for older callers.

## Troubleshooting

- **Large files** — Feishu upload limits may apply; compress locally or rely on `--video-url` text if the file cannot be uploaded.
- **Non-mp4** — This helper uploads with `file_type=mp4`; convert to mp4 if the API returns another container and Feishu rejects the upload.

See also [multi-platform.md](multi-platform.md).
