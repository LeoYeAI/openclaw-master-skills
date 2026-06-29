# Sending Video via Feishu

After video generation completes, if running in a Feishu environment, send the actual video file to the user instead of just a link.

## Prerequisites

- `feishu_send_video.py` script (included in `scripts/`)
- Feishu app credentials configured in `~/.openclaw/openclaw.json`

## Quick Start

```bash
# Video only
python3 {baseDir}/scripts/feishu_send_video.py \
  --video /tmp/video.mp4 \
  --to "ou_user_open_id" \
  --cover-url "https://thumbnail_url" \
  --duration 20875

# Video + text (rich post)
python3 {baseDir}/scripts/feishu_send_video.py \
  --video /tmp/video.mp4 \
  --to "oc_group_chat_id" \
  --cover-url "https://thumbnail_url" \
  --duration 20875 \
  --title "My Video" \
  --text "Description text here"
```

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--video` | Yes | Local video file path |
| `--to` | Yes | Recipient open_id (ou_xxx) or group chat_id (oc_xxx) |
| `--cover` / `--cover-url` | No | Cover image local path or URL |
| `--duration` | No | Video duration in milliseconds |
| `--title` | No | Post title (triggers rich text mode) |
| `--text` | No | Text content (triggers rich text mode, supports \n) |

## Two Modes

**Mode 1: Video only** (no `--title` or `--text`)
- Sends as `msg_type: "media"` — video card with play button
- Best for: quick video delivery

**Mode 2: Video + text** (with `--title` and/or `--text`)
- Sends as `msg_type: "post"` — rich text with embedded video
- Best for: sharing to groups with context/description

## Full Workflow (After Generation)

1. Get `video_url` and `thumbnail_url` from generation result
2. Download video: `curl -o /tmp/video.mp4 <video_url>`
3. Send with cover: `python3 feishu_send_video.py --video /tmp/video.mp4 --to ou_xxx --cover-url <thumbnail_url> --duration <ms>`

## Important Notes

- **ALWAYS include a cover image** — without it, the video shows a blank/black thumbnail
- If no thumbnail URL is available, extract the first frame with ffmpeg:
  ```bash
  ffmpeg -i video.mp4 -vframes 1 -q:v 2 cover.jpg -y
  ```
- **Duration is in milliseconds** — omitting it causes the player to show 00:00
- **File size limit ~25MB** — compress large videos with:
  ```bash
  ffmpeg -i input.mp4 -c:v libx264 -crf 28 -preset fast -c:a aac -b:a 128k output.mp4
  ```

## Technical Details

- Feishu video messages use `msg_type: "media"` (not "video" or "file")
- Upload video with `file_type: "mp4"` via `POST /im/v1/files`
- Upload cover with `image_type: "message"` via `POST /im/v1/images`
- Rich text uses `msg_type: "post"` with `{"tag": "media"}` and `{"tag": "text"}` content rows
