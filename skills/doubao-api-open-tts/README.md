# Doubao Open TTS SKILL

## Overview

This SKILL provides text-to-speech (TTS) capabilities for AI Agents using the Doubao (Volcano Engine) API. It enables agents to convert text into natural-sounding speech with 200+ voice options.

## Skill Information

- **Name**: `doubao-open-tts`
- **Type**: Text-to-Speech Synthesis
- **Provider**: Volcano Engine (Doubao)
- **Version**: 1.0.0
- **Developer**: [xdrshjr](https://github.com/xdrshjr)

## Capabilities

### Core Functions

1. **Text-to-Speech Synthesis**
   - Convert any text to natural speech
   - Support for multiple audio formats (mp3, pcm, wav)
   - Adjustable speech speed and volume

2. **Voice Selection**
   - 200+ voices across multiple categories
   - Interactive voice selection workflow
   - Support for Chinese and multilingual voices

3. **Voice Categories**
   - General (Normal & Multilingual with emotions)
   - Roleplay (characters, personalities)
   - Video Dubbing (cartoon characters)
   - Audiobook (storytelling voices)
   - Customer Service (professional voices)
   - Fun Accents (regional dialects)

### Agent Integration

```python
# Example: Agent using this SKILL
from skills.doubao_open_tts import VolcanoTTS, get_voice_selection_prompt, find_voice_by_name

# Step 1: Show voice options to user
prompt = get_voice_selection_prompt()
# Agent displays: "Please select a voice..."

# Step 2: User selects voice (e.g., "Shiny")
user_choice = "Shiny"
voice_type, voice_name = find_voice_by_name(user_choice)

# Step 3: Agent synthesizes speech
tts = VolcanoTTS(app_id="...", access_token="...", secret_key="...")
audio_path = tts.synthesize(
    text="Hello, I'm your AI assistant",
    voice_type=voice_type,
    output_file="response.mp3"
)
```

## Configuration

### Required Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `app_id` | Volcano Engine App ID | `your_app_id` |
| `access_token` | API Access Token | `your_token` |
| `secret_key` | API Secret Key | `your_secret` |

### Optional Parameters

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| `voice_type` | Voice identifier | `zh_female_cancan_mars_bigtts` | See voice list |
| `encoding` | Audio format | `mp3` | mp3, pcm, wav |
| `speed` | Speech speed | `1.0` | 0.5 - 2.0 |
| `volume` | Volume level | `1.0` | 0.5 - 2.0 |

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Credentials**
   ```bash
   cp .env.example .env
   # Edit .env with your Volcano Engine credentials
   ```

3. **Get API Credentials**
   - Visit [Volcano Engine Console](https://console.volcengine.com/)
   - Enable "Doubao Voice" service
   - Create application to get AppID, Access Token, and Secret Key

## Usage Examples

### Basic Synthesis
```python
from skills.doubao_open_tts import VolcanoTTS

tts = VolcanoTTS()
audio = tts.synthesize("Hello world", output_file="output.mp3")
```

### Interactive Voice Selection
```python
from skills.doubao_open_tts import get_voice_selection_prompt, find_voice_by_name

# Get prompt for user
prompt = get_voice_selection_prompt()
print(prompt)

# Parse user selection
voice_type, name = find_voice_by_name("Shiny")
```

### With Custom Parameters
```python
audio = tts.synthesize(
    text="Custom speech",
    voice_type="zh_male_sunwukong_mars_bigtts",  # Monkey King voice
    speed=1.2,
    volume=0.8,
    encoding="wav"
)
```

## Voice Categories

### Popular Voices
- **灿灿/Shiny** (Default) - General purpose, Chinese/English
- **猴哥** - Monkey King character voice
- **快乐小东** - Cheerful male voice
- **霸道总裁** - Dominant CEO character

### Category Overview
- **General-Multilingual**: 20+ voices with emotion support
- **Roleplay**: 20+ character voices
- **Video Dubbing**: Cartoon and character voices
- **Audiobook**: Storytelling optimized voices
- **Customer Service**: Professional service voices
- **Fun Accents**: Regional dialects (Cantonese, Sichuan, etc.)

## File Structure

```
doubao-open-tts/
├── README.md              # This file
├── doubao-open-tts.md     # Detailed documentation
├── requirements.txt       # Python dependencies
├── .env.example          # Configuration template
└── scripts/
    ├── tts.py            # Main SKILL implementation
    └── test_tts.py       # Test and example scripts
```

## Agent Workflow Integration

### Typical Use Case

1. **User Request**: "Read this article aloud"
2. **Agent Action**: 
   - Call `get_voice_selection_prompt()`
   - Present voice options to user
3. **User Response**: "Use the cheerful female voice"
4. **Agent Action**:
   - Call `find_voice_by_name("cheerful female")`
   - Get `voice_type`
   - Call `tts.synthesize(article_text, voice_type=voice_type)`
5. **Result**: Return audio file to user

## Dependencies

- `volcengine-python-sdk` - Volcano Engine SDK
- `python-dotenv` - Environment variable management

## License

MIT License

## Support

- **Issues**: [GitHub Issues](https://github.com/xdrshjr/JR-Agent-Skills/issues)
- **Developer**: [@xdrshjr](https://github.com/xdrshjr)
- **Documentation**: See `doubao-open-tts.md` for complete API reference
