---
name: youtube-transcript
description: Fetch and summarize YouTube video transcripts. Use when asked to summarize, transcribe, or extract content from YouTube videos. Handles transcript fetching via residential IP proxy to bypass YouTube's cloud IP blocks.
---

# YouTube Transcript

Fetch transcripts from YouTube videos and optionally summarize them.

## Quick Start

```bash
python3 scripts/fetch_transcript.py <video_id_or_url> [languages]
```

**Examples:**
```bash
python3 scripts/fetch_transcript.py dQw4w9WgXcQ
python3 scripts/fetch_transcript.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
python3 scripts/fetch_transcript.py dQw4w9WgXcQ "fr,en,de"
```

**Output:** JSON with `video_id`, `title`, `author`, `full_text`, and timestamped `transcript` array.

## Workflow

1. Run `fetch_transcript.py` with video ID or URL
2. Script checks VPN, brings it up if needed
3. Returns JSON with full transcript text
4. Summarize the `full_text` field as needed

## Language Codes

Default priority: `en, fr, de, es, it, pt, nl`

Override with second argument: `python3 scripts/fetch_transcript.py VIDEO_ID "ja,ko,zh"`

## Setup & Configuration

See [references/SETUP.md](references/SETUP.md) for:
- Python dependencies installation
- WireGuard VPN configuration (required for cloud VPS)
- Troubleshooting common errors
- Alternative proxy options
