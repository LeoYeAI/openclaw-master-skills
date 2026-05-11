# doubao-asr

> Agent Skill for transcribing audio files via ByteDance Volcengine **Seed-ASR 2.0** (豆包录音文件识别模型2.0)

Best-in-class Chinese speech recognition — Mandarin, Cantonese, Sichuan dialect, and 13+ languages. With speaker diarization, up to 5 hours / 512MB per file.

中文语音识别准确率业界领先——支持普通话、粤语、四川话等方言及 13+ 种语言。自带说话人分离，单文件最长 5 小时 / 512MB。

## Why this skill?

Setting up Volcengine's Doubao Audio File Recognition 2.0 (豆包录音文件识别模型2.0, recorded audio → text) from scratch involves **4 environment variables across 3 different console pages** (Speech console, IAM, TOS). Without guidance, this typically takes 1-2 hours of doc-hunting and trial-and-error.

This skill provides **step-by-step bilingual setup instructions** (中英双语) baked into `SKILL.md`, so your AI agent can walk you through the entire process in ~10 minutes.

从零配置火山引擎豆包录音文件识别模型2.0（录音转文字）涉及 **3 个不同控制台页面的 4 个环境变量**。没有引导的话通常需要 1-2 小时翻文档踩坑。本 skill 在 `SKILL.md` 中内置了**中英双语分步引导**，AI agent 可以在约 10 分钟内带你完成全部配置。

## Install

### Claude Code

```bash
claude /install-skill https://github.com/vahnxu/doubao-asr
```

Or manually copy to `~/.claude/skills/doubao-asr/`.

### OpenClaw / ClawHub

Available on [ClawHub](https://clawhub.com) as `doubao-asr`.

### Manual

```bash
git clone https://github.com/vahnxu/doubao-asr.git
cd doubao-asr
pip install requests
python3 scripts/transcribe.py /path/to/audio.m4a
```

## Quick start

```bash
# Basic transcription
python3 scripts/transcribe.py /path/to/audio.m4a

# Save to file
python3 scripts/transcribe.py /path/to/audio.m4a --out /tmp/transcript.txt

# JSON output
python3 scripts/transcribe.py /path/to/audio.m4a --json --out /tmp/result.json

# Direct URL (skip upload)
python3 scripts/transcribe.py https://example.com/audio.mp3

# Disable speaker diarization
python3 scripts/transcribe.py /path/to/audio.m4a --no-speakers
```

## Credentials

See the detailed setup guide in [SKILL.md](./SKILL.md#credentials-setup) — with step-by-step instructions for each environment variable.

| Variable | Required | Description |
|---|---|---|
| `VOLCENGINE_API_KEY` | Yes | ASR API key (UUID) from Speech console |
| `VOLCENGINE_ACCESS_KEY_ID` | Yes | IAM Access Key ID (starts with `AKLT`) |
| `VOLCENGINE_SECRET_ACCESS_KEY` | Yes | IAM Secret Access Key |
| `VOLCENGINE_TOS_BUCKET` | Yes | TOS bucket name |
| `VOLCENGINE_TOS_REGION` | Yes | TOS region code, must match bucket region. Overseas: e.g. `cn-hongkong`, `ap-southeast-1`; China: `cn-beijing` |

## Supported formats

WAV, MP3, MP4, M4A, OGG, FLAC — up to 5 hours, 512MB max.

## License

Apache-2.0
