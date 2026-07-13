# ai-video-editor

[![ClawHub Skill](https://img.shields.io/badge/ClawHub-Skill-blueviolet)](https://clawhub.io)
[![Version](https://img.shields.io/badge/version-1.2.0-blue)](SKILL.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

> **One-for-all AI video editing.**
> Copy Style ✂️ · Long to Short 🔤 · AI Caption 🎙️ · AI Commentary 📐 · Video Resizer · Highlight Reels ⚽ · Vlog · Montage · Talking-head
>
> Upload raw footage, apply AI editing with a natural-language prompt, retrieve a processed video URL — all from a shell script. Powered by [Sparki](https://sparki.io).

---

## What It Does

This ClawHub Skill wraps the [Sparki](https://sparki.io) AI video editing API into four Bash scripts:

| Script | Purpose |
|--------|---------|
| `scripts/upload_asset.sh` | Upload a video file, get an `object_key` |
| `scripts/create_project.sh` | Start AI video processing with style tips |
| `scripts/get_project_status.sh` | Poll project state and retrieve result URL |
| `scripts/edit_video.sh` | **End-to-end**: upload → process → download URL |

**Supported use cases:**

| Scenario | Keywords |
|----------|----------|
| Copy a creator's style | Copy Style, Style Transfer, Aesthetic Match |
| Cut long videos into short clips | Long to Short, Short-form, Reels, Shorts, TikTok, Clips |
| Add subtitles or narration | AI Caption, AI Commentary, Subtitles, Voice-over |
| Reformat for any platform | Video Resizer, Aspect Ratio, Vertical, Square, Landscape |
| Sports / event highlights | Highlight Reels, Sports, Best Moments |
| Daily vlog production | Vlog, Travel, Lifestyle |
| Multi-clip storytelling | Montage, Compilation, Mashup |
| Presenter / interview content | Talking-head, Interview, Explainer |
| Batch automation pipelines | Batch Processing, Content Factory, Automation |

---

## Quick Start

### 1. Install via OpenClaw

```bash
npx clawhub install ai-video-editor --force
```

### 2. Configure API key

```bash
export SPARKI_API_KEY="sk_live_your_key_here"
```

Get your key from the [Sparki Dashboard](https://sparki.io).

### 3. Process a video

```bash
# Full workflow — returns a 24-hour download URL
RESULT_URL=$(bash scripts/edit_video.sh my_video.mp4 "1,2" "energetic and trendy" "9:16")
echo "$RESULT_URL"
```

---

## Requirements

- `bash` 4.x+
- `curl`
- `jq`
- `SPARKI_API_KEY` environment variable

---

## Usage Examples

**Vertical short-form (default):**
```bash
bash scripts/edit_video.sh footage.mp4 "1,2"
```

**Square video with creative direction:**
```bash
bash scripts/edit_video.sh clip.mov "3" "cinematic slow motion" "1:1"
```

**Landscape with duration limit:**
```bash
bash scripts/edit_video.sh raw.mp4 "1" "" "16:9" 60
```

**Step-by-step (manual control):**
```bash
# Upload
OBJECT_KEY=$(bash scripts/upload_asset.sh footage.mp4)

# Create project
PROJECT_ID=$(bash scripts/create_project.sh "$OBJECT_KEY" "1,2" "dynamic" "9:16")

# Poll until done
while true; do
  STATUS=$(bash scripts/get_project_status.sh "$PROJECT_ID")
  [[ "${STATUS%% *}" == "COMPLETED" ]] && break
  sleep 5
done

RESULT_URL="${STATUS#COMPLETED }"
echo "Download: $RESULT_URL"
```

---

## Supported Parameters

| Parameter | Values | Default |
|-----------|--------|---------|
| `aspect_ratio` | `9:16`, `1:1`, `16:9` | `9:16` |
| `duration` | integer (seconds) | — |
| `tips` | comma-separated IDs | required |
| `user_prompt` | free text | — |

**Timeout overrides:**
```bash
WORKFLOW_TIMEOUT=7200 bash scripts/edit_video.sh long_video.mp4 "1"
ASSET_TIMEOUT=120 bash scripts/edit_video.sh large_file.mp4 "2"
```

---

## Error Codes

| Code | Meaning |
|------|---------|
| `401` | Invalid API key |
| `413` | File too large (> 3 GB) or storage full |
| `453` | Concurrent project limit reached |
| `500` | Server error — retry |

---

## Publishing

```bash
# Package for ClawHub
zip -r sparki-video-processor.zip SKILL.md scripts/ README.md
```

Upload via [ClawHub Dashboard](https://clawhub.io) → "Publish New Skill".

Recommended metadata:
- **Category:** `video/ai-generation`
- **Tags:** `video-editing`, `ai`, `content-creation`, `short-form`, `highlight`, `vlog`, `montage`, `caption`, `resizer`

---

Powered by [Sparki](https://sparki.io) — AI video editing for everyone.

---

## Security

- `SPARKI_API_KEY` is passed only via HTTP header — never logged or written to disk
- All user-provided arguments are double-quoted to prevent shell injection
- Scripts make outbound requests only to `agent-api-test.aicoding.live` — no local filesystem writes beyond the uploaded file read

---

## License

MIT — see [LICENSE](LICENSE).
