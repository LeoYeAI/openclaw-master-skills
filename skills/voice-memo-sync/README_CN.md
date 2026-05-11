# Voice Memo Sync 🎙️

[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://github.com/openclaw/openclaw)
[![macOS](https://img.shields.io/badge/macOS-仅限-lightgrey)](https://www.apple.com/macos/)
[![Apple Silicon](https://img.shields.io/badge/Apple%20Silicon-Metal%20GPU-orange)](https://support.apple.com/zh-cn/116943)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**智能同步、转录、整理语音备忘录、音视频文件和视频链接。**

> 🍎 **苹果生态全覆盖**: 支持iPhone、iPad、Mac。在任何苹果设备上录制的语音备忘录通过iCloud自动同步，处理后的笔记和提醒事项也会同步回所有设备。不支持Linux/Windows。

将你的语音录音、YouTube视频、会议转录自动转化为结构化、可执行的笔记 — 自动同步到 Apple Notes 和提醒事项。

[English Documentation](README.md)

## ✨ 功能特性

- 🎙️ **Apple原生转录** — 提取语音备忘录内置转录（零延迟）
- 🔄 **Whisper备选** — 本地AI转录，适用于无原生文本的录音
- 🎬 **YouTube/B站支持** — 下载并转录视频内容
- 📄 **多格式输入** — 支持 .m4a, .mp3, .mp4, .txt, .md, .doc, .docx, .json, .csv
- 🧠 **智能摘要** — LLM驱动的分析，结合个性化洞察
- 📝 **Apple Notes同步** — 自动创建带 #标签 的结构化笔记
- ⏰ **提醒事项集成** — 自动提取TODO并创建提醒
- 🔒 **隐私优先** — 所有处理默认在本地完成

## 🚀 快速开始

### 安装

```bash
# 通过ClawHub安装（推荐）
clawhub install ying-wen/voice-memo-sync

# 或手动安装
cd ~/.openclaw/workspace/skills
git clone https://github.com/ying-wen/voice-memo-sync.git
cd voice-memo-sync
./scripts/install.sh
```

### 依赖

```bash
# 必需
brew install ffmpeg

# 转录引擎（选择一个或两个都装）
brew install whisper-cpp        # 推荐：Metal GPU加速（快15-20倍）
brew install openai-whisper     # 备选：CPU转录

# 可选（增强功能）
brew install yt-dlp            # YouTube/B站下载
brew install steipete/tap/remindctl   # 提醒事项集成
brew install steipete/tap/summarize   # YouTube转录提取
```

### ⚡ Metal GPU 加速

在 Apple Silicon Mac 上，`whisper-cpp` 使用 Metal 实现显著更快的转录：

| 音频时长 | CPU (openai-whisper) | Metal GPU (whisper-cpp) |
|----------|---------------------|------------------------|
| 5 分钟 | ~5 分钟 | ~20 秒 |
| 30 分钟 | ~30 分钟 | ~2 分钟 |
| 60 分钟 | ~60 分钟 | ~4 分钟 |

Skill 会自动检测并优先使用 `whisper-cpp`。

## 📖 使用方法

直接告诉你的 OpenClaw agent：

```
「同步语音备忘录」
「处理这个录音：[文件]」
「整理这个视频：[YouTube/B站链接]」
「转录并总结这段音频」
```

或直接使用脚本：

```bash
# 处理任意输入
./scripts/process.sh /path/to/audio.mp3
./scripts/process.sh "https://www.bilibili.com/video/BVxxx"
./scripts/process.sh /path/to/transcript.txt

# 同步iCloud录音
./scripts/sync-icloud-recordings.sh
```

## 📁 支持的格式

| 类型 | 格式 | 处理方式 |
|------|------|----------|
| 语音备忘录 | .qta, .m4a | Apple原生 → Whisper备选 |
| 音频 | .mp3, .wav, .aac, .flac | Whisper本地转录 |
| 视频 | .mp4, .mov, .mkv, .webm | ffmpeg提取 → Whisper |
| YouTube | URL | summarize CLI → yt-dlp备选 |
| Bilibili | URL | yt-dlp下载 → Whisper |
| 文本 | .txt, .md | 直接读取 |
| 文档 | .doc, .docx | textutil转换 |
| 结构化数据 | .json, .csv | 解析提取 |

## 🔧 配置

编辑 `~/.openclaw/workspace/config/voice-memo-sync.yaml`:

```yaml
sources:
  voice_memos:
    enabled: true
  icloud:
    enabled: true
    paths:
      - "~/Library/Mobile Documents/com~apple~CloudDocs/Recordings"

transcription:
  priority: ["apple", "text", "summarize", "whisper-local"]
  whisper_model: "small"
  language: "auto"

notes:
  folder: "语音备忘录"
  include_quotes: true
  include_original: true

reminders:
  enabled: true
  list: "Reminders"
```

## 📝 输出格式

笔记以以下结构创建：

```
🎙️ [智能生成的标题]

📅 日期 | ⏱️ 时长 | 👤 来源
🏷️ #标签1 #标签2 #标签3

━━━━━━━━━━━━━━━━━━━━━━

📌 核心摘要
[一段话总结核心内容]

🎯 关键要点
• 要点1
• 要点2
• 要点3

💡 深度分析与反思
[结合用户背景的个性化分析]

📋 行动建议
☐ TODO 1（已同步到提醒事项）
☐ TODO 2

💬 金句摘录
• "引用1"
• "引用2"

━━━━━━━━━━━━━━━━━━━━━━

📝 原始转录（已整理）
[完整转录文本，已整理口语表达]
```

## 🔒 隐私说明

- 所有转录默认在本地完成
- Apple原生转录从本地文件提取
- Whisper完全在本地运行
- 不向外部服务器发送任何数据（除非你明确配置外部API）
- 所有数据存储在本地 `memory/voice-memos/` 目录

## 📂 数据结构

```
memory/voice-memos/
├── INDEX.md          # 处理记录索引
├── sources/          # 原始文件元数据
├── transcripts/      # 原始转录
├── processed/        # LLM处理后内容
└── synced/           # 同步记录
```

## 🛠️ 故障排除

### 转录太慢
```bash
# 安装 whisper-cpp 启用 Metal GPU 加速
brew install whisper-cpp
# 比 CPU 版 openai-whisper 快 15-20 倍
```

### Whisper未找到
```bash
brew install whisper-cpp    # 推荐（Metal GPU）
# 或
brew install openai-whisper # 备选（CPU）
```

### yt-dlp下载失败
```bash
brew upgrade yt-dlp
# 或使用代理
export ALL_PROXY=http://127.0.0.1:7890
```

### Apple Notes文件夹未创建
```bash
osascript -e 'tell application "Notes" to tell account "iCloud" to make new folder with properties {name:"语音备忘录"}'
```

## 📜 更新日志

### v1.3.0 (2026-03-08)
- **Metal GPU 加速** — 通过 whisper-cpp 实现（快15-20倍）
- 自动检测并优先使用 whisper-cli
- Apple Notes 输出包含完整原始转录
- 强调苹果全生态支持（iPhone/iPad/Mac）
- 性能实测：41分钟音频，6分42秒完成转录

### v1.2.0 (2026-03-08)
- 新增统一处理脚本
- 新增YouTube/B站支持
- 新增 .doc/.docx/.json/.csv 支持
- 双语SKILL.md（中/英）
- 改进安装脚本

### v1.0.0 (2026-03-08)
- 初始版本
- Apple语音备忘录转录
- Apple Notes同步
- Whisper备选

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 🤝 贡献

欢迎贡献！请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)

---

为 OpenClaw 社区用 ❤️ 制作
