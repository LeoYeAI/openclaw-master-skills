# Content Collector

Personal content collection and knowledge management system for OpenClaw.

## Features

- 📚 **Multi-source Collection**: Save content from blogs, X/Twitter, videos (YouTube, Bilibili, TikTok), webpages
- 🎯 **Automatic Transcription**: Extract subtitles from videos with faster-whisper
- 🏷️ **Smart Tagging**: Auto-generate tags and maintain searchable index
- 📊 **Visual Overview**: Generate Mermaid diagrams for long articles
- 🔍 **Full-text Search**: Find content by keywords or tags
- 📝 **Obsidian Sync**: Optional sync to Obsidian vault for manual browsing
- 🎨 **Image Extraction**: Save valuable illustrations from articles

## Prerequisites

- OpenClaw agent environment
- Python 3.8+
- (Optional) yt-dlp + faster-whisper for video transcription
- (Optional) Obsidian vault for sync feature

## Installation

### Via ClawHub (Recommended)

```bash
clawhub install content-collector
```

### Manual Installation

1. Clone this repository to `~/.openclaw/skills/content-collector`
2. Install Python dependencies:
   ```bash
   pip3 install pyyaml
   ```
3. (Optional) For video transcription:
   ```bash
   pip3 install yt-dlp
   uv pip install faster-whisper opencc-python-reimplemented
   ```

## Usage

Simply talk to your OpenClaw agent:

```
收藏这个链接：https://example.com/article
Save this URL: https://example.com/blog-post
搜索关键词：AI产品设计
Search for: machine learning
```

The skill automatically detects collection requests and saves content to `<WORKSPACE>/collections/`.

## Configuration

Set environment variables in your OpenClaw TOOLS.md:

- `SUPADATA_API_KEY`: For web content extraction (optional, falls back to web_fetch)
- `COLLECTIONS_DIR`: Custom collections directory (default: `~/.openclaw/workspace/collections`)
- `OBSIDIAN_DIR`: Obsidian vault sync path (optional)

## License

MIT License - see [LICENSE](LICENSE) file for details
