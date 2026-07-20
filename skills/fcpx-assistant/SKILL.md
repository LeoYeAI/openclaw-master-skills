---
name: fcpx-assistant
description: "Final Cut Pro X (FCPX) assistant — auto video production, TTS voiceover, media management, batch export | AI 自动成片、TTS 配音、素材管理、批量导出. Triggers: FCPX, FCP, Final Cut, make video, auto video, voiceover, import media, export"
author: Steve & Steven
version: 2.0.0
metadata:
  openclaw:
    emoji: 🎬
    requires:
      bins: [osascript, ffmpeg, ffprobe, curl, jq, bash]
      services:
        - name: Qwen TTS WebUI
          url: http://localhost:7860
          description: Local TTS service for voiceover generation
    external:
      - name: Pexels API
        url: https://www.pexels.com/api/
        description: Free stock video search (optional API key)
      - name: Bilibili
        url: https://www.bilibili.com
        description: Video upload platform (requires biliup login)
---

# Final Cut Pro Assistant

A fully automated video production pipeline — from topic to published video. Also your everyday FCP editing assistant.

---

## 🔥 Core Feature: One-Click Video Production

**From topic to published video — fully automated.**

### Full Workflow

```
Topic 💡 → AI Script 📝 → Fetch Media 🔍 → TTS Voiceover 🎤 → Auto Assemble 🎞️ → Auto Publish 🚀
```

### 🚀 Quick Start: One Command

```bash
# Generate and publish to Bilibili
bash scripts/auto-video-from-topic.sh \
    --topic "如何制作一杯完美的咖啡" \
    --publish bilibili \
    --title "咖啡教程" \
    --tags "咖啡，教程"
```

### 📝 Step 1: AI Script Generation

Auto-generate video script from topic using AI.

```bash
bash scripts/ai-script-generator.sh \
    --topic "如何制作一杯完美的咖啡" \
    --style 教程 \
    --duration 90 \
    --keywords
```

**Features:**
- AI-powered script generation
- Platform-specific optimization (TikTok, YouTube, Bilibili)
- Style presets: vlog, 科普，教程，带货，故事
- Auto-generate material search keywords
- Output includes storyboard + TTS-ready text

### 🔍 Step 2: Fetch Video Assets

Auto-search and download free stock footage from Pexels by keywords.

```bash
bash scripts/media-collector.sh \
    --keywords "nature ocean sunset" \
    --count 5 --output ./my-project
```

- Multi-keyword search (searches each word separately, then merges)
- Orientation (landscape/portrait/square), quality (SD/HD/4K), duration filtering
- Saves metadata and license info automatically
- Set `PEXELS_API_KEY` for expanded search

### 🎵 Step 3: Add Background Music

Drop your BGM files (mp3/wav/m4a) into the project's `music/` folder. The assembler auto-detects them.

```
my-project/
├── videos/     ← Stock footage (auto-filled by Step 2)
├── music/      ← Your BGM goes here
└── meta/       ← Metadata (auto-generated)
```

### 🎤 Step 4: TTS Voiceover

Generate per-paragraph voiceover using Qwen TTS.

```bash
bash scripts/tts-voiceover.sh \
    --script "First paragraph
Second paragraph
Third paragraph" \
    --output ./my-project/voiceover
```

- Per-paragraph generation with automatic silence trimming
- Customizable voice via `--instruct` (e.g., "warm female voice, moderate pace")
- Also reads from file: `--script-file ./script.txt`
- Requires Qwen TTS WebUI running at `localhost:7860`

### 🎞️ Step 5: Auto Assemble

Combines footage, voiceover, subtitles, and BGM into a finished video.

```bash
bash scripts/auto-video-maker.sh \
    --project ./my-project \
    --script-file ./script.txt \
    --voiceover ./my-project/voiceover \
    --style vlog \
    --output final.mp4
```

**Smart Features:**
- 📝 Script split by paragraph, each mapped to a video clip
- 🎤 Clip duration auto-syncs to voiceover timing when available
- 📝 Burn-in subtitles with PingFang SC font (position/size adjustable)
- 🎵 Smart audio mixing — voiceover + BGM (BGM auto-ducked to 15%)
- 🎬 Fade transitions between clips
- 📐 Uniform resolution (default 1920x1080, supports portrait 1080x1920)

**Style Presets:**

| Style | Pacing | Font Size | Transition | Best For |
|-------|--------|-----------|------------|----------|
| `default` | Medium | 42 | 0.5s | General |
| `vlog` | Upbeat | 38 | 0.3s | Daily vlogs |
| `cinematic` | Slow | 48 | 1.0s | Scenic/story |
| `fast` | Rapid | 36 | 0.2s | Shorts/TikTok |

**More Options:**
```bash
--resolution 1080x1920    # Portrait mode
--no-subtitle             # No subtitles
--subtitle-pos center     # Center subtitles (default: bottom)
--font-size 50            # Custom font size
--music ./specific.mp3    # Specify BGM file
--transition none         # No transitions
```

### 🚀 Step 6: Auto Publish

Upload finished video to platforms (Bilibili, YouTube, TikTok, Xiaohongshu).

```bash
bash scripts/auto-publish.sh \
    --video final.mp4 \
    --platform bilibili \
    --title "我的视频" \
    --tags "vlog，日常" \
    --description "视频描述"
```

**Supported Platforms:**
- `bilibili` - B 站 (requires `biliup` or web upload)
- `youtube` - YouTube (requires Google API setup)
- `tiktok` - 抖音 (requires cookie auth)
- `xiaohongshu` - 小红书 (requires cookie auth)

**Configure Accounts:**
```bash
bash scripts/auto-publish.sh --config
```

Creates config files in `~/.fcpx-assistant/publish/`

---

## 📂 FCP Project Management

Automate everyday Final Cut Pro tasks.

```bash
osascript scripts/check-fcp.scpt          # Check FCP status
osascript scripts/list-projects.scpt       # List all projects
osascript scripts/open-project.scpt "Name" # Open a project
osascript scripts/import-temp-media.scpt   # Import temp media
osascript scripts/project-time-tracking.scpt  # Time tracking
```

---

## ✂️ Editing Assistance

```bash
bash scripts/scene-detect.sh video.mp4          # Scene detection
bash scripts/auto-rough-cut.sh video.mp4         # Auto rough cut (silence removal)
bash scripts/smart-tagger.sh ./media/            # AI smart tagging
bash scripts/auto-chapter-marker.sh video.mp4    # Auto chapter markers
```

---

## 🔊 Audio Processing

```bash
bash scripts/audio-normalizer.sh video.mp4       # Normalize to -23 LUFS
bash scripts/auto-voiceover.sh "text" out.wav    # Single-file voiceover
```

---

## 🌍 Subtitles

```bash
bash scripts/multi-lang-subtitles.sh video.mp4 en   # Multi-language (en/ja/ko/fr/de/es)
```

---

## 🖼️ Other Tools

```bash
bash scripts/auto-thumbnail.sh video.mp4 ./thumbs   # Keyframe thumbnails + contact sheet
osascript scripts/create-script.scpt "Title" "Content"  # Create script in Notes
osascript scripts/list-scripts.scpt                  # List scripts
```

---

## Requirements

### 必需依赖

| 工具 | 用途 | 安装方式 |
|------|------|----------|
| `ffmpeg` | 视频剪辑、转场、字幕烧入 | `brew install homebrew-ffmpeg/ffmpeg/ffmpeg` |
| `osascript` | FCPX AppleScript 控制 | macOS 自带 |
| `curl` | API 调用 | macOS 自带 |
| `jq` | JSON 处理 | `brew install jq` |
| `bash` | 脚本运行 | macOS 自带 |

### 可选依赖

| 工具 | 用途 | 安装方式 |
|------|------|----------|
| `biliup` | B 站视频上传 | `pip3 install --break-system-packages biliup` |
| `trash` | 安全删除文件 | `brew install trash` |

### 外部服务

| 服务 | 用途 | 配置方式 |
|------|------|----------|
| **Qwen TTS WebUI** | 文字转语音配音 | 本地部署，运行在 `localhost:7860` |
| **Pexels API** | 免费视频素材搜索 | 无需 API key（可选设置 `PEXELS_API_KEY` 提高限额） |
| **B 站账号** | 视频上传发布 | 运行 `biliup login` 扫码登录 |

---

## 🔧 Qwen TTS WebUI 部署指南

本技能的 TTS 配音功能依赖 **Qwen TTS WebUI**，这是一个本地部署的语音合成服务。

### 部署步骤

1. **克隆项目**
```bash
git clone https://github.com/your-org/qwen-tts-webui.git
cd qwen-tts-webui
```

2. **安装依赖**
```bash
pip3 install -r requirements.txt
```

3. **下载模型**
```bash
# 下载 Qwen3-TTS 模型
python3 scripts/download_model.py --model Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice
```

4. **启动服务**
```bash
python3 app.py --port 7860
```

5. **验证服务**
```bash
curl http://localhost:7860/gradio_api/info
```

### 配置说明

在 `tts-voiceover.sh` 中修改以下参数（如果需要）：

```bash
TTS_HOST="http://127.0.0.1:7860"  # TTS 服务地址
INSTRUCT="活泼开朗的年轻男声，语调轻快有活力"  # 默认声音特征
MODEL="Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice"  # 模型名称
```

### 资源需求

- **内存**: 至少 8GB（推荐 16GB+）
- **GPU**: 可选（有 GPU 时生成速度更快）
- **磁盘**: 约 5GB（模型文件）

### 替代方案

如果不想部署 Qwen TTS，可以：
1. 使用其他 TTS 服务（修改 `tts-voiceover.sh` 中的 API 调用）
2. 使用本地录音文件代替 TTS 配音
3. 跳过配音步骤，仅生成字幕视频

---

*From script to screen — let AI make your videos! 🎬*

---
---

# 中文版

# Final Cut Pro 助手

从主题到发布的全自动视频生产线，同时也是你的 FCP 剪辑助手。

---

## 🔥 核心能力：一键视频生产

**从主题到发布，全自动完成。**

### 完整工作流

```
主题 💡 → AI 文案 📝 → 搜素材 🔍 → TTS 配音 🎤 → 自动成片 🎞️ → 自动发布 🚀
```

### 🚀 快速开始：一条命令

```bash
# 生成并发布到 B 站
bash scripts/auto-video-from-topic.sh \
    --topic "如何制作一杯完美的咖啡" \
    --publish bilibili \
    --title "咖啡教程" \
    --tags "咖啡，教程"
```

### 📝 Step 1: AI 文案生成

根据主题自动生成视频脚本。

```bash
bash scripts/ai-script-generator.sh \
    --topic "如何制作一杯完美的咖啡" \
    --style 教程 \
    --duration 90 \
    --keywords
```

**功能:**
- AI 自动生成文案
- 平台优化（抖音、YouTube、B 站）
- 风格预设：vlog, 科普，教程，带货，故事
- 自动生成素材搜索关键词
- 输出包含分镜脚本 + TTS 配音文本

### 🔍 Step 2: 搜集视频素材

从 Pexels 免费素材库自动搜索下载，按关键词匹配。

```bash
bash scripts/media-collector.sh \
    --keywords "nature ocean sunset" \
    --count 5 --output ./my-project
```

- 多关键词自动逐词搜索
- 支持方向（横屏/竖屏）、质量（SD/HD/4K）、时长范围筛选
- 自动保存素材元数据和版权信息
- 设置 `PEXELS_API_KEY` 解锁更多搜索能力

### 🎵 Step 3: 准备背景音乐

把你找的 BGM 放到项目的 `music/` 目录即可，成片时自动检测。

```
my-project/
├── videos/     ← 素材（Step 2 自动填充）
├── music/      ← 你的 BGM 放这里（mp3/wav/m4a）
└── meta/       ← 元数据（自动生成）
```

### 🎤 Step 4: TTS 配音

用 Qwen TTS 为每段文案生成配音。

```bash
bash scripts/tts-voiceover.sh \
    --script "第一段文案
第二段文案
第三段文案" \
    --output ./my-project/voiceover
```

- 逐段生成，自动修剪首尾静音
- 声音特征可自定义（`--instruct`）
- 也支持从文件读取：`--script-file ./script.txt`
- 需要 Qwen TTS WebUI 运行在 `localhost:7860`

### 🎞️ Step 5: 自动成片

把素材、配音、字幕、BGM 全部组装成完整视频。

```bash
bash scripts/auto-video-maker.sh \
    --project ./my-project \
    --script-file ./script.txt \
    --voiceover ./my-project/voiceover \
    --style vlog \
    --output final.mp4
```

**智能特性：**
- 📝 文案按段落拆分，每段对应一个视频片段
- 🎤 有配音时，片段时长自动匹配配音节奏
- 📝 PingFang SC 简体中文字幕烧入（位置/大小可调）
- 🎵 配音 + BGM 智能混合（BGM 自动降低到 15% 音量）
- 🎬 fade 转场效果
- 📐 统一分辨率（默认 1920x1080，支持竖屏 1080x1920）

**风格预设：**

| 风格 | 节奏 | 字号 | 转场 | 适合 |
|------|------|------|------|------|
| `default` | 中等 | 42 | 0.5s | 通用 |
| `vlog` | 轻快 | 38 | 0.3s | 日常 Vlog |
| `cinematic` | 缓慢 | 48 | 1.0s | 电影感 |
| `fast` | 快速 | 36 | 0.2s | 短视频/抖音 |

### 🚀 Step 6: 自动发布

将成品视频上传到各大平台（B 站、YouTube、抖音、小红书）。

```bash
bash scripts/auto-publish.sh \
    --video final.mp4 \
    --platform bilibili \
    --title "我的视频" \
    --tags "vlog，日常" \
    --description "视频描述"
```

**支持平台:**
- `bilibili` - B 站（需要 `biliup` 或网页上传）
- `youtube` - YouTube（需要 Google API 配置）
- `tiktok` - 抖音（需要 cookie 认证）
- `xiaohongshu` - 小红书（需要 cookie 认证）

**配置账号:**
```bash
bash scripts/auto-publish.sh --config
```

在 `~/.fcpx-assistant/publish/` 创建配置文件

---

## 📂 FCP 项目管理

```bash
osascript scripts/check-fcp.scpt          # 检查 FCP 状态
osascript scripts/list-projects.scpt       # 列出所有项目
osascript scripts/open-project.scpt "名称"  # 打开项目
osascript scripts/import-temp-media.scpt   # 导入临时素材
osascript scripts/project-time-tracking.scpt  # 时间追踪
```

## ✂️ 剪辑辅助

```bash
bash scripts/scene-detect.sh video.mp4     # 场景分析
bash scripts/auto-rough-cut.sh video.mp4   # 自动粗剪
bash scripts/smart-tagger.sh ./media/      # 智能标签
bash scripts/auto-chapter-marker.sh video.mp4  # 自动章节标记
```

## 🔊 音频处理

```bash
bash scripts/audio-normalizer.sh video.mp4 # 音频标准化 (-23 LUFS)
bash scripts/auto-voiceover.sh "文本" out.wav  # 单文件配音
```

## 🌍 字幕

```bash
bash scripts/multi-lang-subtitles.sh video.mp4 en  # 多语言字幕
```

## 🖼️ 其他工具

```bash
bash scripts/auto-thumbnail.sh video.mp4 ./thumbs  # 自动缩略图
osascript scripts/create-script.scpt "标题" "内容"   # 创建文案
osascript scripts/list-scripts.scpt                 # 列出文案
```

---

## 依赖

### 必需依赖

| 工具 | 用途 | 安装方式 |
|------|------|----------|
| `ffmpeg` | 视频剪辑、转场、字幕烧入 | `brew install homebrew-ffmpeg/ffmpeg/ffmpeg` |
| `osascript` | FCPX AppleScript 控制 | macOS 自带 |
| `curl` | API 调用 | macOS 自带 |
| `jq` | JSON 处理 | `brew install jq` |
| `bash` | 脚本运行 | macOS 自带 |

### 可选依赖

| 工具 | 用途 | 安装方式 |
|------|------|----------|
| `biliup` | B 站视频上传 | `pip3 install --break-system-packages biliup` |
| `trash` | 安全删除文件 | `brew install trash` |

### 外部服务

| 服务 | 用途 | 配置方式 |
|------|------|----------|
| **Qwen TTS WebUI** | 文字转语音配音 | 本地部署，运行在 `localhost:7860` |
| **Pexels API** | 免费视频素材搜索 | 无需 API key（可选设置 `PEXELS_API_KEY` 提高限额） |
| **B 站账号** | 视频上传发布 | 运行 `biliup login` 扫码登录 |

---

## 🔧 Qwen TTS WebUI 部署指南

本技能的 TTS 配音功能依赖 **Qwen TTS WebUI**，这是一个本地部署的语音合成服务。

### 部署步骤

1. **克隆项目**
```bash
git clone https://github.com/your-org/qwen-tts-webui.git
cd qwen-tts-webui
```

2. **安装依赖**
```bash
pip3 install -r requirements.txt
```

3. **下载模型**
```bash
# 下载 Qwen3-TTS 模型
python3 scripts/download_model.py --model Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice
```

4. **启动服务**
```bash
python3 app.py --port 7860
```

5. **验证服务**
```bash
curl http://localhost:7860/gradio_api/info
```

### 配置说明

在 `tts-voiceover.sh` 中修改以下参数（如果需要）：

```bash
TTS_HOST="http://127.0.0.1:7860"  # TTS 服务地址
INSTRUCT="活泼开朗的年轻男声，语调轻快有活力"  # 默认声音特征
MODEL="Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice"  # 模型名称
```

### 资源需求

- **内存**: 至少 8GB（推荐 16GB+）
- **GPU**: 可选（有 GPU 时生成速度更快）
- **磁盘**: 约 5GB（模型文件）

### 替代方案

如果不想部署 Qwen TTS，可以：
1. 使用其他 TTS 服务（修改 `tts-voiceover.sh` 中的 API 调用）
2. 使用本地录音文件代替 TTS 配音
3. 跳过配音步骤，仅生成字幕视频

---

*从文案到成片，让 AI 帮你做视频！🎬*

*Made by Steve & Steven 🤝*
