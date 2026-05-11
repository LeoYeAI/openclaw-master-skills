# Voice Memo Sync - Architecture

## Overview

This skill provides a complete pipeline for processing Apple Voice Memos:

```
Input Sources          Transcription           Processing            Output
─────────────────────────────────────────────────────────────────────────────
                                              ┌─────────────┐
Voice Memos ──────────▶ Apple Native ────────▶│             │──▶ Apple Notes
                            │                 │    LLM      │
Audio Files ──────────▶ Whisper Local ───────▶│  Analysis   │──▶ Reminders
                            │                 │             │
Text Input ───────────▶ (skip) ──────────────▶│ + User      │──▶ Local Files
                                              │   Context   │
URL/Video ────────────▶ Download + Whisper ──▶│             │
                                              └─────────────┘
```

## Components

### 1. Transcript Extraction (`extract-apple-transcript.py`)

Extracts native transcription from Apple Voice Memos files.

**How it works:**
- Apple stores transcripts in the QuickTime file's `meta` atom
- The transcript is JSON-formatted with `attributedString.runs`
- Each word has associated timestamp information

**File structure:**
```
.qta/.m4a file
├── ftyp (file type)
├── wide
├── mdat (media data - actual audio)
└── moov (movie metadata)
    ├── mvhd
    ├── trak (audio track)
    │   └── meta ◀─── Transcript JSON here!
    ├── trak (spatial audio)
    ├── trak (metadata track 1)
    ├── trak (metadata track 2)
    └── udta (user data)
```

**JSON format:**
```json
{
  "locale": {"identifier": "zh-Hans_CN", "current": 1},
  "attributedString": {
    "runs": ["Hello", 0, "world", 1, ...],
    "attributeTable": [
      {"timeRange": [0, 1.5]},
      {"timeRange": [1.5, 2.0]},
      ...
    ]
  }
}
```

### 2. Whisper Fallback

For recordings without native transcription:

```bash
whisper audio.m4a --model small --language zh --output_format txt
```

**Model selection:**
- `tiny`: Fastest, lower accuracy (~1GB VRAM)
- `small`: Good balance (~2GB VRAM) ✓ Default
- `medium`: Better accuracy (~5GB VRAM)
- `large`: Best accuracy (~10GB VRAM)

### 3. LLM Analysis

The skill leverages OpenClaw's LLM capabilities to:

1. **Reconstruct** garbled transcriptions into coherent text
2. **Summarize** key points and main topics
3. **Analyze** content in context of user's background (from USER.md)
4. **Extract** action items and TODOs
5. **Connect** to user's existing projects and memories (from MEMORY.md)

### 4. Apple Notes Integration

Uses AppleScript to create notes:

```applescript
tell application "Notes"
    tell account "iCloud"
        make new note at folder "语音备忘录" with properties {
            name: "Title",
            body: "<html content>"
        }
    end tell
end tell
```

**Note structure:**
1. Header (title, time, duration, tags)
2. Core Summary
3. Key Points
4. Deep Analysis (personalized)
5. Action Items
6. Related Connections
7. Original Transcript (at bottom, grayed)

### 5. Reminders Integration

Uses `remindctl` CLI:

```bash
remindctl add --title "Task from recording" --list "Reminders" --due tomorrow
```

## Privacy Considerations

1. **No hardcoded paths**: Uses `~/` and environment variables
2. **No API keys in code**: All keys from environment
3. **Local-first**: Default to local processing
4. **User context isolation**: Each user has their own USER.md/MEMORY.md
5. **No telemetry**: No usage data collected

## Extending

### Adding new input sources

Implement in `voice-memo-processor.py`:

```python
def process_url(url: str) -> dict:
    # Download audio
    # Transcribe
    # Return standard format
    pass
```

### Adding new output targets

Create new script in `scripts/`:

```bash
# scripts/export-to-notion.sh
# scripts/export-to-obsidian.sh
```

### Custom analysis prompts

Override in config:

```yaml
analysis:
  custom_prompt: |
    As a {user_role}, analyze this recording focusing on...
```
