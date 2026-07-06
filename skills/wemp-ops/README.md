# WeMP Ops

WeChat Official Account (公众号) full-stack operations skill for OpenClaw.

## Features

- 📝 **Topic Selection**: Auto-suggest topics from your topic pool
- 🔍 **Content Collection**: Search web, fetch articles, gather materials
- ✍️ **AI Writing**: Generate articles following style guides and templates
- 🎨 **Image Generation**: Create cover images and illustrations
- 📐 **Layout Formatting**: Convert Markdown to WeChat-compatible HTML
- 📊 **Analytics**: Track article performance and engagement
- 💬 **Comment Management**: Monitor and respond to reader comments

## Prerequisites

- OpenClaw agent environment
- Node.js 16+ and Python 3.8+
- WeChat Official Account API credentials (for publishing features)

## Installation

### Via ClawHub (Recommended)

```bash
clawhub install wemp-ops
```

### Manual Installation

1. Clone to `~/.openclaw/skills/wemp-ops`
2. Run setup:
   ```bash
   cd ~/.openclaw/skills/wemp-ops
   node scripts/setup.mjs
   ```

## Usage

Talk to your OpenClaw agent:

```
写一篇关于 AI 产品设计的文章
帮我采集今日热点
查看公众号日报
检查新评论
```

The skill guides you through: topic selection → material collection → writing → layout → publishing.

## Configuration

- `persona.md`: Define your writing persona
- `references/`: Style guides, templates, and techniques
- `config/`: API credentials for WeChat and image generation services

## License

MIT License - see [LICENSE](LICENSE) file
