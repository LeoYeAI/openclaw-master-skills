# deAPI AI Media Suite

[![ClawHub](https://img.shields.io/badge/ClawHub-deapi-blue)](https://clawhub.ai/skills/deapi)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**The cheapest AI media API on the market** - now as a Clawdbot/OpenClaw skill.

Transcribe YouTube videos, generate images, convert text to speech, extract text with OCR, create videos, remove backgrounds, and more - all through one unified API at a fraction of the cost.

## 🚀 Features

| Feature | Description |
|---------|-------------|
| 🎬 **Transcription** | YouTube, Twitch, Kick, X, audio/video files (Whisper) |
| 🖼️ **Image Generation** | Flux and Z-Image models |
| 🗣️ **Text-to-Speech** | 54+ voices across 8 languages |
| 📝 **OCR** | Extract text from images |
| 🎥 **Video Generation** | Text-to-video and image-to-video |
| ✂️ **Background Removal** | Remove backgrounds from images |
| 🔍 **Upscale** | 2x/4x image upscaling (RealESRGAN) |
| 🎨 **Style Transfer** | Transform images with AI |
| 🧮 **Embeddings** | Text embeddings for semantic search |

## 📦 Installation

```bash
clawdhub install deapi
```

## ⚙️ Setup

1. Get your API key at [deapi.ai](https://deapi.ai) (free $5 credit on signup)
2. Set environment variable (or simply provide the API key to your agent when needed):
   ```bash
   export DEAPI_API_KEY=your_api_key_here
   ```

## 💰 Pricing

- **Transcription:** ~$0.02/hour
- **Image Generation:** ~$0.002/image  
- **TTS:** ~$0.001/1000 chars
- **Video Generation:** ~$0.05/video

Free $5 credit = hundreds of hours of transcription or thousands of images!

## 📖 Usage

Once installed, your Clawdbot agent automatically knows how to use deAPI. Just ask:

- *"Transcribe this YouTube video: [URL]"*
- *"Generate an image of a robot in cyberpunk style"*
- *"Convert this text to speech with a British accent"*
- *"Extract text from this screenshot"*
- *"Remove the background from this photo"*
- *"Upscale this image 4x"*

## 🔒 Security & Privacy

- All requests go to `api.deapi.ai` (official endpoint)
- Media URLs you submit are sent to deAPI for processing
- Results via `result_url` may be temporarily accessible
- Review [deAPI's privacy policy](https://deapi.ai) for data handling details

## 🙏 Credits

- **API Provider:** [deAPI.ai](https://deapi.ai)
- **Original Claude Code skill:** [deapi-ai/claude-code-skills](https://github.com/deapi-ai/claude-code-skills)
- **Clawdbot conversion:** [@zrewolwerowanykaloryfer](https://github.com/zrewolwerowanykaloryfer)

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

**Links:** [ClawHub](https://clawhub.ai/skills/deapi) | [deAPI.ai](https://deapi.ai) | [API Docs](https://docs.deapi.ai)
