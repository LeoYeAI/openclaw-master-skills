# Getting Started

Quick start guide for setting up and testing MiniMax Voice Maker.

## Environment setup

### 1. Install dependencies

```bash
# Navigate to project directory
cd mmVoice_Maker

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install Python packages
pip install -r requirements.txt

# Install FFmpeg (required for audio processing)
# macOS:
brew install ffmpeg

# Ubuntu/Debian:
sudo apt install ffmpeg

# Windows: Download from https://ffmpeg.org/download.html
```

### 2. Set API key

```bash
# Required for all TTS operations
export MINIMAX_VOICE_API_KEY="your-api-key-here"

# Verify it's set
echo $MINIMAX_VOICE_API_KEY
```

## Usage

### Basic synthesis

```python
from scripts import quick_tts

audio = quick_tts(
    text="Hello, this is a test of the voice synthesis system.",
    voice_id="male-qn-qingse",
    output_path="test.mp3"
)

print(f"Generated {len(audio)} bytes")
# Output: test.mp3 created
```

### Segment-based TTS (multi-voice/emotion)

Use the CLI for segment-based workflows:

```bash
# 1. Create segments.json with text, voice_id, and emotion for each segment
# 2. Validate the file
python mmvoice.py validate segments.json

# 3. Generate audio
python mmvoice.py generate segments.json
```

### Check voice availability

```python
from scripts import get_system_voices, voice_exists

# List all system voices
voices = get_system_voices()
for v in voices:
    print(f"{v['voice_id']}: {v.get('name', 'N/A')}")

# Check specific voice
if voice_exists("male-qn-qingse"):
    print("Voice available")
```

### Verify FFmpeg

```python
from scripts import check_ffmpeg_installed

if check_ffmpeg_installed():
    print("FFmpeg is installed and ready")
else:
    print("Please install FFmpeg")
```

## Next steps

- **TTS workflows**: See [tts-guide.md](tts-guide.md)
- **Emotion synthesis**: See [emotion-guide.md](emotion-guide.md)
- **Voice cloning/design**: See [voice-guide.md](voice-guide.md)
- **Audio processing**: See [audio-guide.md](audio-guide.md)
- **Troubleshooting**: See [troubleshooting.md](troubleshooting.md)
