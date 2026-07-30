# Skywork Music Maker 1.0.0

AI-powered music generation skill for Claude Code and other AI agent frameworks. Create professional songs, instrumentals, and lyrics using Mureka AI API with natural language descriptions in any language.

## Quick Links

- **[SKILL.md](SKILL.md)** - Complete agent guide (start here)
- **[references/prompt_guide.md](references/prompt_guide.md)** - Music craftsmanship guide (MANDATORY reading for lyrics tasks)
- **[scripts/mureka.py](scripts/mureka.py)** - Unified CLI tool for all operations

## Installation

### For Claude Code / Codex
```bash
# Option 1: Use directly from this repo
# Reference as: @skywork-music-maker-1.0.0

# Option 2: Install to ~/.claude/skills
cp -r skywork-music-maker-1.0.0 ~/.claude/skills/
```

### For Gemini CLI
```bash
# Install to skills directory (check your platform's docs)
cp -r skywork-music-maker-1.0.0 /path/to/gemini/skills/
```

### For Other AI Frameworks
Copy the directory to your framework's skills location. The skill follows standard conventions and should work with any framework supporting tool-based agents.

## Key Features

✅ **Natural language to music** - Describe in any language, get structured prompts
✅ **Smart validation** - Quality checks before generation
✅ **Complete workflow** - Lyrics → Song/Instrumental → Analysis → Extension
✅ **Unified CLI** - Single `mureka.py` script for all operations
✅ **Agent-optimized** - Self-documenting code, clear documentation structure
✅ **Production-ready** - Best practices from real music production practitioners

## Quick Start

### 1. Set up API key

```bash
# Get your API key from https://platform.mureka.ai
export MUREKA_API_KEY="your_api_key"
```

### 2. Generate music with natural language

```bash
# The AI agent will convert your description to a structured prompt
User: "create an upbeat summer pop song with female vocals"
AI: [Converts to structured prompt, validates, generates]

# Or use the CLI directly
cd scripts/
python mureka.py song \
  --lyrics "[Verse]\nWalking down the beach..." \
  --prompt "indie pop, 110 BPM, acoustic guitar, female vocal, warm and nostalgic" \
  --output ./my_song
```

### 3. Check the results

```bash
# Generated files will be in the output directory:
ls ./my_song/
# output_0.mp3  output_1.mp3  lyrics.txt
```

## CLI Tool

All operations use a single unified script: `scripts/mureka.py`

```
mureka.py song           Generate a song with lyrics and vocals
mureka.py instrumental   Generate an instrumental track
mureka.py lyrics         Generate or extend lyrics using AI
mureka.py upload         Upload reference audio, vocals, melodies
```

**Usage:**
```bash
python scripts/mureka.py --help              # Show all commands
python scripts/mureka.py song --help         # Song-specific options
python scripts/mureka.py instrumental --help # Instrumental options
python scripts/mureka.py lyrics --help       # Lyrics generation options
python scripts/mureka.py upload --help       # Upload options
```

**Important:** Use `-n 2` (single dash) to generate multiple choices, not `--n`.

## Common Scenarios

### Background music for videos
```bash
python scripts/mureka.py instrumental \
  --prompt "ambient electronic, calm, 80 BPM, soft pads, no percussion" \
  --output ./bg_music
```

### Song without lyrics yet
```bash
# Step 1: Generate lyrics
python scripts/mureka.py lyrics generate \
  "a nostalgic summer love song, bittersweet, looking back at memories"

# Step 2: Use the generated lyrics for your song
python scripts/mureka.py song \
  --lyrics "[Verse]\n(paste generated lyrics here)\n[Chorus]\n..." \
  --prompt "indie pop, warm, 110 BPM, acoustic guitar, male vocal" \
  --output ./summer_song
```

### With reference track (style transfer)
```bash
# Upload 30-second reference track
python scripts/mureka.py upload my_reference.mp3 --purpose reference
# Returns: File ID: 542321

# Generate song using that style
python scripts/mureka.py song \
  --lyrics "[Verse]\n..." \
  --reference-id 542321 \
  --output ./song_with_style
```

### Vocal cloning
```bash
# Upload 15-30 second vocal sample
python scripts/mureka.py upload my_voice.mp3 --purpose vocal
# Returns: File ID: 789012

# Generate song with cloned voice
python scripts/mureka.py song \
  --lyrics "[Verse]\n..." \
  --vocal-id 789012 \
  --prompt "R&B, smooth, 90 BPM, emotional" \
  --output ./cloned_voice_song
```

## File Structure

```
skywork-music-maker-1.0.0/
├── SKILL.md                    # Complete agent guide
├── README.md                   # This file
├── references/
│   └── prompt_guide.md        # Music craftsmanship guide (MANDATORY for lyrics)
└── scripts/
    └── mureka.py              # Unified CLI tool (use --help for docs)
```

## Smart Prompt Conversion

When you describe music in natural language (in any language), the AI agent automatically:

1. **Extracts structured parameters** - Genres, moods, instruments, BPM, vocals, key
2. **Validates quality** - Checks against quality checklist to prevent generation failures
3. **Presents for confirmation** - Shows you the structured prompt before generation
4. **Executes generation** - Runs the API call with the validated prompt

This prevents 80% of common generation failures and ensures high-quality results.

## Control Options & Requirements

### Song Generation Combinations

| Combo | prompt | reference_id | vocal_id | melody_id |
|-------|--------|-------------|----------|-----------|
| Style only | ✅ | | | |
| Reference only | | ✅ | | |
| Voice only | | | ✅ | |
| Melody only | | | | ✅ |
| Style + Voice | ✅ | | ✅ | |
| Reference + Voice | | ✅ | ✅ | |

**Important:**
- `melody_id` does NOT support any combination — use it alone
- `prompt` and `reference_id` are mutually exclusive

### File Upload Requirements

| Purpose | Format | Duration | Notes |
|---------|--------|----------|-------|
| `reference` | mp3/m4a | exactly 30s | Excess trimmed |
| `vocal` | mp3/m4a | 15-30s | Excess trimmed |
| `melody` | mp3/m4a/mid | 5-60s | MIDI recommended |
| `instrumental` | mp3/m4a | exactly 30s | For instrumental reference |

### Model Selection

Always use `mureka-8` — it is the latest and highest quality model (default in scripts).

## Error Handling

Common errors and solutions:

| Error | Cause | Action |
|-------|-------|--------|
| `401 Unauthorized` | Invalid/expired API key | Verify `MUREKA_API_KEY` |
| `429 Too Many Requests` | Rate limit exceeded | Wait 30-60 seconds, retry |
| `402 / Insufficient balance` | Account depleted | Top up at https://platform.mureka.ai |
| `Task failed` | Bad prompt/server error | Check Quality Checklist, retry |
| `Task timeouted` | Generation took too long | Simplify prompt, retry |
| `ConnectionError` | Network issue | Retry after a few seconds |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Task failed or timeouted | • Check prompt meets quality checklist<br>• Verify lyrics have structure tags<br>• Retry |
| Vocals sound rushed | • Shorten lyric lines (≤10 words)<br>• Reduce syllables per line |
| Instruments not audible | • Name each instrument explicitly<br>• Add specific descriptors (e.g., "acoustic guitar strumming") |
| Output doesn't match prompt | • Increase specificity (exact genre, BPM)<br>• Add mood progression ("sparse → full")<br>• Generate n=3 choices |
| melody_id error | • melody_id MUST be used alone<br>• Remove --prompt, --reference-id, --vocal-id |
| Invalid file_id | • File IDs only valid for uploading account<br>• Re-upload if from another session |

## Environment Requirements

- **Python**: 3.7+
- **Dependencies**: `requests` library (`pip install requests`)
- **API Key**: `MUREKA_API_KEY` environment variable (required)
- **API Base URL**: `https://api.mureka.ai`

## Support & Resources

- **Issues & Feedback**: [github.com/anthropics/claude-code/issues](https://github.com/anthropics/claude-code/issues)
- **Mureka API Docs**: [platform.mureka.ai](https://platform.mureka.ai)
- **Get API Key**: [platform.mureka.ai](https://platform.mureka.ai) → Register → API Keys → Generate
- **Check Balance**: `curl -H "Authorization: Bearer $MUREKA_API_KEY" https://api.mureka.ai/v1/account/billing`

## Examples

### Traditional Chinese Music
```bash
python scripts/mureka.py song \
  --lyrics "[Verse]\n春风拂面..." \
  --prompt "Chinese traditional guofeng, 90 BPM, bamboo flute (dizi), guzheng, erhu, misty atmosphere, ancient poetry aesthetic" \
  --output ./chinese_style
```

### Electronic Dance Music
```bash
python scripts/mureka.py instrumental \
  --prompt "progressive house, 128 BPM, synth leads, deep bass, atmospheric pads, building energy" \
  -n 3 \
  --output ./edm_track
```

### Jazz Ballad
```bash
python scripts/mureka.py song \
  --lyrics "[Verse]\nUnder the midnight sky..." \
  --prompt "jazz ballad, slow groove, piano, upright bass, soft brushed drums, female husky vocal, intimate" \
  --output ./jazz_ballad
```

## License

Same as parent repository.

---

**For detailed music production guidance, prompt crafting examples, and lyric writing best practices, see [references/prompt_guide.md](references/prompt_guide.md).**
