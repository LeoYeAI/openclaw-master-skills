# Command Line Interface Guide

Use the unified CLI tool for all operations without writing Python code.

## Quick start

```bash
# Check environment first
python mmvoice.py check-env

# Basic TTS
python mmvoice.py tts "Hello world" -o hello.mp3

# Get help
python mmvoice.py --help
python mmvoice.py tts --help
```

## Commands

### validate - Validate segments file

Validate a segments.json file before generating audio. Model-specific validation rules apply.

```bash
python mmvoice.py validate SEGMENTS_FILE [OPTIONS]

# Examples
python mmvoice.py validate segments.json                      # Default: speech-2.8-hd
python mmvoice.py validate segments.json --model speech-2.6-hd  # Specific model
python mmvoice.py validate segments.json --verbose
python mmvoice.py validate segments.json --strict
```

**Options:**
- `SEGMENTS_FILE` (required): Path to segments.json file
- `--model`: TTS model for context-specific validation (default: speech-2.8-hd)
- `-v, --verbose`: Show segment details
- `--strict`: Treat warnings as errors

**Model-specific validation:**

| Model | Emotion Validation |
|-------|-------------------|
| **speech-2.8-hd/turbo** | Can be empty (auto) or valid emotion |
| **speech-2.6-hd/turbo** | All 9 emotions required |
| **Older models** | 7 emotions (no fluent/whisper) |

**Validates:**
- JSON format validity
- Required fields (`text`, `voice_id`) present and non-empty
- Emotion values based on model

**Output examples:**

Success (speech-2.8 with empty emotions):
```
✓ Validation passed: 3 segments
```

Error (older model with empty emotion):
```
=== Errors ===
  ✗ Segment 0: 'emotion' is required for speech-2.6-hd. 
    Valid options: happy, sad, angry, fearful, disgusted, surprised, calm, fluent, whisper
✗ Validation failed
```

### generate - Generate audio from segments

Generate audio for all segments and merge into final output.

```bash
python mmvoice.py generate SEGMENTS_FILE [-o OUTPUT] [OPTIONS]

# Examples
python mmvoice.py generate segments.json                            # Output to ./audio/output.mp3
python mmvoice.py generate segments.json -o ./audio/podcast.mp3     # Custom output path
python mmvoice.py generate segments.json --model speech-2.6-hd      # Use specific model
python mmvoice.py generate segments.json --crossfade 200            # Smooth transitions
```

**Default file placement:**
```
./                          # Current working directory
└── audio/                  # Created automatically
    ├── tmp/                # Intermediate segment files
    │   ├── segment_0000.mp3
    │   ├── segment_0001.mp3
    │   └── ...
    └── output.mp3          # Final merged audio
```

**Options:**
- `SEGMENTS_FILE` (required): Path to segments.json file
- `-o, --output`: Output audio file path (default: ./audio/output.mp3)
- `--model`: TTS model (default: speech-2.8-hd)
- `--crossfade MS`: Crossfade between segments in ms (default: 0)
- `--no-normalize`: Disable audio normalization
- `--temp-dir`: Directory for intermediate files (default: ./audio/tmp/)
- `--keep-temp`: Keep intermediate segment files (always kept by default)
- `--continue-on-error`: Continue if a segment fails

**After generation:**
- Verify output audio quality
- If satisfied, delete intermediate files: `rm -rf ./audio/tmp/`

**Behavior by Model:**

| Model | Emotion Handling | Display |
|-------|------------------|---------|
| **speech-2.8-hd/turbo** | Auto-matched (empty emotion) | `[AUTO]` |
| **speech-2.6-hd/turbo** | From segments.json | `[HAPPY]`, `[SAD]`, etc. |
| **Older models** | From segments.json | Emotion tag shown |

**Error handling:**
- If a segment fails, reports which segment and why
- Use `--continue-on-error` to generate remaining segments despite failures
- Automatically uses fallback merging if FFmpeg filter_complex fails

**segments.json format for speech-2.8 (recommended):**
```json
[
  {"text": "Welcome!", "voice_id": "male-qn-qingse", "emotion": ""},
  {"text": "Sad news...", "voice_id": "female-shaonv", "emotion": ""}
]
```

**segments.json format for older models:**
```json
[
  {"text": "Welcome!", "voice_id": "male-qn-qingse", "emotion": "happy"},
  {"text": "Sad news...", "voice_id": "female-shaonv", "emotion": "sad"}
]
```

### check-env - Environment check

Verify all dependencies and configuration before use.

```bash
# Basic check
python mmvoice.py check-env

# With API connectivity test
python mmvoice.py check-env --test-api
```

**What it checks:**
- Python version (3.8+)
- Required packages (requests, websockets, etc.)
- FFmpeg installation
- MINIMAX_VOICE_API_KEY environment variable
- Scripts directory and files
- Module imports
- Optional: API connectivity

### tts - Basic text-to-speech

```bash
python mmvoice.py tts TEXT [OPTIONS]

# Examples
python mmvoice.py tts "Hello world" -o hello.mp3
python mmvoice.py tts "你好世界" -v female-shaonv -o hello_cn.mp3
python mmvoice.py tts "Quick test" -v male-qn-qingse
```

**Options:**
- `TEXT` (required): Text to synthesize
- `-v, --voice-id`: Voice ID (default: male-qn-qingse)
- `-o, --output`: Output file path (e.g., output.mp3)

### clone - Voice cloning

Clone a voice from audio sample (10s-5min).

```bash
python mmvoice.py clone AUDIO_FILE --voice-id VOICE_ID [OPTIONS]

# Examples
python mmvoice.py clone my_voice.mp3 --voice-id my-custom-voice
python mmvoice.py clone sample.mp3 --voice-id my-voice --preview "Test preview"
python mmvoice.py clone recording.wav --voice-id narrator-1 \
    --preview "This is the narrator voice" \
    --preview-output narrator_preview.mp3
```

**Options:**
- `AUDIO_FILE` (required): Audio file (mp3/wav/m4a, 10s-5min, ≤20MB)
- `--voice-id` (required): Custom voice ID for cloned voice
- `--preview TEXT`: Generate preview with this text
- `--preview-output PATH`: Preview output path

**Requirements:**
- Audio duration: 10 seconds to 5 minutes
- File size: ≤20MB
- Format: mp3, wav, or m4a
- Voice ID: 8-256 chars, alphanumeric/-/_

### design - Voice design

Generate unique voice from text description.

```bash
python mmvoice.py design DESCRIPTION [OPTIONS]

# Examples
python mmvoice.py design "A gentle female voice for storytelling" --voice-id narrator-1
python mmvoice.py design "Professional male news anchor voice" \
    --voice-id news-voice \
    --preview "Welcome to the evening news"
```

**Options:**
- `DESCRIPTION` (required): Voice characteristics prompt
- `--voice-id`: Custom voice ID (auto-generated if not provided)
- `--preview TEXT`: Preview text (default: "This is a preview...")
- `--preview-output PATH`: Preview output path

**Prompt tips:**
Include gender, age, tone, characteristics, and use case:
```
"A confident middle-aged male voice with clear articulation 
and authoritative tone, suitable for business presentations"
```

### list-voices - List available voices

```bash
python mmvoice.py list-voices

# Output
=== System Voices ===
  male-qn-qingse: 青涩青年音色
  female-shaonv: 少女音色
  ...

=== Custom Voices ===
Cloned (2):
  my-custom-voice
  narrator-1
Designed (1):
  news-anchor
```

### merge - Merge audio files

Concatenate multiple audio files with crossfades.

```bash
python mmvoice.py merge FILE1 FILE2 [FILE3...] -o OUTPUT [OPTIONS]

# Examples
python mmvoice.py merge part1.mp3 part2.mp3 part3.mp3 -o complete.mp3
python mmvoice.py merge intro.mp3 main.mp3 outro.mp3 -o podcast.mp3 \
    --crossfade 500 --format mp3
python mmvoice.py merge *.mp3 -o merged.mp3 --no-normalize
```

**Options:**
- `FILE1 FILE2 ...` (required): Input audio files
- `-o, --output` (required): Output file path
- `--format`: Output format (default: mp3)
- `--crossfade MS`: Crossfade duration in milliseconds (default: 300)
- `--no-normalize`: Disable volume normalization

### convert - Audio format conversion

```bash
python mmvoice.py convert INPUT -o OUTPUT [OPTIONS]

# Examples
python mmvoice.py convert input.wav -o output.mp3 --format mp3
python mmvoice.py convert audio.m4a -o audio.mp3 --bitrate 192k
python mmvoice.py convert recording.wav -o optimized.mp3 \
    --format mp3 --sample-rate 22050 --channels 1 --bitrate 128k
```

**Options:**
- `INPUT` (required): Input audio file
- `-o, --output` (required): Output file path
- `--format`: Target format (default: mp3)
- `--sample-rate`: Sample rate in Hz (e.g., 32000)
- `--bitrate`: Bitrate (e.g., 192k, 320k)
- `--channels`: Number of channels (1=mono, 2=stereo)

## Complete workflow examples

### 1. Environment setup and first synthesis

```bash
# Check environment
python mmvoice.py check-env

# If API key not set:
export MINIMAX_VOICE_API_KEY="your-api-key"

# First test
python mmvoice.py tts "Hello world" -o test.mp3
```

### 2. Segment-based workflow (multi-voice, multi-emotion)

This is the recommended workflow for complex audio with multiple voices and emotions.

**Step 1: Create segments.json (Agent does this)**
```json
[
  {"text": "Welcome to our podcast!", "voice_id": "male-qn-qingse", "emotion": "happy"},
  {"text": "Today we discuss AI challenges.", "voice_id": "female-shaonv", "emotion": "calm"},
  {"text": "This is concerning...", "voice_id": "male-qn-qingse", "emotion": "fearful"},
  {"text": "But there's hope!", "voice_id": "female-shaonv", "emotion": "happy"}
]
```

**Step 2: Validate**
```bash
python mmvoice.py validate segments.json --verbose
```

**Step 3: Generate**
```bash
python mmvoice.py generate segments.json -o podcast.mp3 --crossfade 200
```

### 3. Custom voice workflow

```bash
# Clone voice
python mmvoice.py clone my_recording.mp3 --voice-id my-narrator \
    --preview "This is my custom narrator voice"

# List to verify
python mmvoice.py list-voices

# Use cloned voice with segment-based workflow
# Create segments.json with custom voice, then generate
python mmvoice.py generate segments.json
```

### 4. Audio processing pipeline

```bash
# Generate content
python mmvoice.py tts "Content 1" -o part1.wav
python mmvoice.py tts "Content 2" -o part2.wav

# Convert to high quality
python mmvoice.py convert part1.wav -o part1_hq.mp3 \
    --bitrate 320k --sample-rate 44100

python mmvoice.py convert part2.wav -o part2_hq.mp3 \
    --bitrate 320k --sample-rate 44100

# Merge
python mmvoice.py merge part1_hq.mp3 part2_hq.mp3 -o final.mp3
```

## Error handling

### API key not set
```
✗ Error: MINIMAX_VOICE_API_KEY not set
  Set it with: export MINIMAX_VOICE_API_KEY='your-key'
```
**Solution:** `export MINIMAX_VOICE_API_KEY="your-api-key"`

### FFmpeg not found
```
✗ Error: FFmpeg not found. Please install FFmpeg first.
```
**Solution:** Run `python mmvoice.py check-env` for install instructions

### Voice not found
```
✗ Error: Voice not found: invalid-voice-id
```
**Solution:** Run `python mmvoice.py list-voices` to see available voices

### File not found
```
✗ Error: File not found: input.mp3
```
**Solution:** Check file path and existence

## Integration with Agent workflows

The CLI is designed for Agent use - no Python code needed:

```bash
# Agent can directly call:
python mmvoice.py tts "User's text" -o output.mp3
python mmvoice.py validate segments.json
python mmvoice.py generate segments.json
```

**Benefits:**
- No code generation needed
- Consistent interface
- Clear error messages
- Progress feedback
- Works in any environment with Python

## See also

- **Environment setup**: [getting-started.md](getting-started.md)
- **Python API**: [tts-guide.md](tts-guide.md), [api_documentation.md](api_documentation.md)
- **Troubleshooting**: [troubleshooting.md](troubleshooting.md)
