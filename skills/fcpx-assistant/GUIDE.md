# FCP Assistant — Quick Start Guide

> From script to final video, one-stop production toolkit.

---

## 🚀 Quick Start: Make a Video in 5 Minutes

### 1. Write Your Script

Write your video script, one paragraph per line:

```
This is a story about the ocean
Waves crash against the rocks with a thunderous roar
A sailboat drifts slowly across the sunset horizon
Let's take in the calm of this endless blue
```

Save as `script.txt`, or pass it directly in the command.

### 2. Fetch Video Assets

```bash
bash scripts/media-collector.sh \
    --keywords "ocean wave sunset" \
    --count 5 \
    --output ./my-project
```

Downloads free stock footage from Pexels into `./my-project/videos/`.

### 3. Add Background Music

Drop your BGM files (mp3/wav/m4a) into `./my-project/music/`. That's it.

### 4. Generate TTS Voiceover

```bash
bash scripts/tts-voiceover.sh \
    --script-file ./script.txt \
    --output ./my-project/voiceover
```

> ⚠️ Requires Qwen TTS WebUI running at `localhost:7860`

### 5. Auto Assemble

```bash
bash scripts/auto-video-maker.sh \
    --project ./my-project \
    --script-file ./script.txt \
    --voiceover ./my-project/voiceover \
    --style vlog \
    --output final.mp4
```

🎉 Done! `final.mp4` is your finished video.

---

## 📁 Project Directory Structure

```
my-project/
├── videos/          ← Stock footage (auto-downloaded)
│   ├── clip_01_xxx.mp4
│   ├── clip_02_xxx.mp4
│   └── ...
├── music/           ← Your BGM (manually added)
│   └── chill-bgm.mp3
├── voiceover/       ← TTS voiceover (auto-generated)
│   ├── vo_000.wav
│   ├── vo_001.wav
│   └── full_voiceover.wav
└── meta/            ← Metadata (auto-generated)
    ├── project-info.json
    └── clips-meta.jsonl
```

---

## 🎨 Style Presets

Use `--style` to set the mood:

| Style | Pacing | Font Size | Transition | Best For |
|-------|--------|-----------|------------|----------|
| `default` | Medium | 42 | 0.5s | General content |
| `vlog` | Upbeat | 38 | 0.3s | Daily vlogs |
| `cinematic` | Slow | 48 | 1.0s | Scenic/stories |
| `fast` | Rapid | 36 | 0.2s | TikTok/Shorts |

---

## 📐 Parameter Reference

### media-collector.sh

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--keywords` | Search keywords (required) | — |
| `--count` | Number of clips to download | 5 |
| `--orientation` | landscape/portrait/square | landscape |
| `--quality` | sd/hd/4k | hd |
| `--min-duration` | Min clip duration (sec) | 3 |
| `--max-duration` | Max clip duration (sec) | 30 |
| `--output` | Output directory | ./project-media |

### tts-voiceover.sh

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--script` | Script text (one paragraph per line) | — |
| `--script-file` | Script file path | — |
| `--instruct` | Voice description | Energetic young male voice |
| `--speaker` | Speaker name | default |
| `--no-trim` | Don't trim silence | false |
| `--output` | Output directory | ./voiceover |

### auto-video-maker.sh

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--project` | Media directory (required) | — |
| `--script` | Script text | — |
| `--script-file` | Script file path | — |
| `--voiceover` | Voiceover directory | — |
| `--music` | BGM file path | Auto-detect music/ |
| `--style` | Style preset | default |
| `--resolution` | Resolution | 1920x1080 |
| `--subtitle-pos` | Subtitle position: bottom/center/top | bottom |
| `--font-size` | Subtitle font size | 42 |
| `--no-subtitle` | No subtitles | false |
| `--transition` | Transition: fade/none | fade |
| `--output` | Output file | output.mp4 |

---

## 💡 Tips & Tricks

### Portrait / Vertical Video

```bash
bash scripts/media-collector.sh \
    --keywords "city" --orientation portrait --output ./short

bash scripts/auto-video-maker.sh \
    --project ./short --script "..." \
    --resolution 1080x1920 --style fast --output short.mp4
```

### Voiceover Only (No Subtitles)

```bash
bash scripts/auto-video-maker.sh \
    --project ./my-project --script "..." \
    --voiceover ./my-project/voiceover \
    --no-subtitle --output clean.mp4
```

### Change Voice

```bash
bash scripts/tts-voiceover.sh \
    --script "Your script here" \
    --instruct "Gentle female voice, moderate pace" \
    --output ./voiceover
```

### BGM Only (No Voiceover)

Simply omit the `--voiceover` parameter:

```bash
bash scripts/auto-video-maker.sh \
    --project ./my-project --script "..." \
    --music ./chill.mp3 --output bgm-only.mp4
```

---

## ⚙️ Requirements

| Dependency | Purpose | Install |
|------------|---------|---------|
| ffmpeg (drawtext) | Video processing + subtitles | `brew install homebrew-ffmpeg/ffmpeg/ffmpeg` |
| osascript | FCP automation | Built-in on macOS |
| curl + jq | API calls | Built-in / `brew install jq` |
| Qwen TTS WebUI | TTS voiceover | Manual start at `localhost:7860` |

### Verify Setup

```bash
# Confirm ffmpeg has drawtext
ffmpeg -filters 2>&1 | grep drawtext
# Expected: T. drawtext V->V Draw text...

# Confirm TTS service
curl -s http://127.0.0.1:7860/gradio_api/info | jq '.named_endpoints | keys'
```

---

*Made by Steve & Steven 🤝*

---
---

# 中文版

# FCP Assistant 使用指南

> 从文案到成片，一站式视频生产工具。

---

## 🚀 快速开始：5 分钟做一个视频

### 1. 准备文案

写好你的视频文案，每段一行：

```
这是一个关于大海的故事
海浪拍打着礁石，发出阵阵轰鸣
远处的帆船在夕阳下缓缓驶过
让我们一起感受这片蔚蓝的宁静
```

保存为 `script.txt`，或者直接在命令里写。

### 2. 搜集视频素材

```bash
bash scripts/media-collector.sh \
    --keywords "ocean wave sunset" \
    --count 5 \
    --output ./my-project
```

脚本会从 Pexels 免费素材库下载视频到 `./my-project/videos/`。

### 3. 放入背景音乐

把你找的 BGM 文件（mp3/wav/m4a）丢进 `./my-project/music/` 就行。

### 4. 生成 TTS 配音

```bash
bash scripts/tts-voiceover.sh \
    --script-file ./script.txt \
    --output ./my-project/voiceover
```

> ⚠️ 需要 Qwen TTS WebUI 运行中（`localhost:7860`）

### 5. 自动成片

```bash
bash scripts/auto-video-maker.sh \
    --project ./my-project \
    --script-file ./script.txt \
    --voiceover ./my-project/voiceover \
    --style vlog \
    --output final.mp4
```

🎉 完成！`final.mp4` 就是你的成品视频。

---

## 📁 项目目录结构

运行完后你的项目目录长这样：

```
my-project/
├── videos/          ← 视频素材（media-collector 自动下载）
│   ├── clip_01_xxx.mp4
│   ├── clip_02_xxx.mp4
│   └── ...
├── music/           ← 背景音乐（你手动放进来）
│   └── chill-bgm.mp3
├── voiceover/       ← TTS 配音（tts-voiceover 自动生成）
│   ├── vo_000.wav
│   ├── vo_001.wav
│   └── full_voiceover.wav
└── meta/            ← 元数据（自动生成）
    ├── project-info.json
    └── clips-meta.jsonl
```

---

## 🎨 风格选择

成片器支持 4 种风格预设，用 `--style` 指定：

| 风格 | 节奏感 | 字号 | 转场时长 | 推荐场景 |
|------|--------|------|----------|----------|
| `default` | 适中 | 42 | 0.5s | 通用内容 |
| `vlog` | 轻快 | 38 | 0.3s | 日常 Vlog |
| `cinematic` | 慢节奏 | 48 | 1.0s | 风景/故事 |
| `fast` | 快节奏 | 36 | 0.2s | 抖音/短视频 |

---

## 📐 常用参数速查

### media-collector.sh

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--keywords` | 搜索关键词（必需） | — |
| `--count` | 下载数量 | 5 |
| `--orientation` | 方向：landscape/portrait/square | landscape |
| `--quality` | 质量：sd/hd/4k | hd |
| `--min-duration` | 最短秒数 | 3 |
| `--max-duration` | 最长秒数 | 30 |
| `--output` | 输出目录 | ./project-media |

### tts-voiceover.sh

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--script` | 文案文本（每行一段） | — |
| `--script-file` | 文案文件路径 | — |
| `--instruct` | 声音特征描述 | 活泼开朗的年轻男声 |
| `--speaker` | 发言人 | default |
| `--no-trim` | 不修剪静音 | false |
| `--output` | 输出目录 | ./voiceover |

### auto-video-maker.sh

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--project` | 素材目录（必需） | — |
| `--script` | 文案文本 | — |
| `--script-file` | 文案文件路径 | — |
| `--voiceover` | 配音目录 | — |
| `--music` | BGM 文件路径 | 自动检测 music/ |
| `--style` | 风格预设 | default |
| `--resolution` | 分辨率 | 1920x1080 |
| `--subtitle-pos` | 字幕位置：bottom/center/top | bottom |
| `--font-size` | 字幕字号 | 42 |
| `--no-subtitle` | 不加字幕 | false |
| `--transition` | 转场：fade/none | fade |
| `--output` | 输出文件 | output.mp4 |

---

## 💡 实用技巧

### 竖屏短视频

```bash
bash scripts/media-collector.sh \
    --keywords "city" --orientation portrait --output ./short

bash scripts/auto-video-maker.sh \
    --project ./short --script "..." \
    --resolution 1080x1920 --style fast --output short.mp4
```

### 不要字幕，只要配音

```bash
bash scripts/auto-video-maker.sh \
    --project ./my-project --script "..." \
    --voiceover ./my-project/voiceover \
    --no-subtitle --output clean.mp4
```

### 换个声音

```bash
bash scripts/tts-voiceover.sh \
    --script "文案内容" \
    --instruct "温柔知性的女声，语速适中" \
    --output ./voiceover
```

### 只要 BGM 不要配音

不传 `--voiceover` 参数就行：

```bash
bash scripts/auto-video-maker.sh \
    --project ./my-project --script "..." \
    --music ./chill.mp3 --output bgm-only.mp4
```

---

## ⚙️ 环境要求

| 依赖 | 用途 | 安装方式 |
|------|------|----------|
| ffmpeg (drawtext) | 视频处理+字幕 | `brew install homebrew-ffmpeg/ffmpeg/ffmpeg` |
| osascript | FCP 控制 | macOS 自带 |
| curl + jq | API 调用 | macOS 自带 / `brew install jq` |
| Qwen TTS WebUI | TTS 配音 | 需手动启动 `localhost:7860` |

### 检查环境

```bash
# 确认 ffmpeg 支持 drawtext
ffmpeg -filters 2>&1 | grep drawtext
# 应输出: T. drawtext V->V Draw text...

# 确认 TTS 服务
curl -s http://127.0.0.1:7860/gradio_api/info | jq '.named_endpoints | keys' 
```

---

## 🎬 FCP 日常操作

除了自动成片，这个工具也能帮你管理 Final Cut Pro：

```bash
osascript scripts/check-fcp.scpt          # 检查 FCP 状态
osascript scripts/list-projects.scpt       # 列出所有项目
osascript scripts/open-project.scpt "名称"  # 打开项目
osascript scripts/import-temp-media.scpt   # 导入临时素材
osascript scripts/create-script.scpt "标题" "内容"  # 创建文案
osascript scripts/list-scripts.scpt        # 列出文案
osascript scripts/project-time-tracking.scpt  # 时间追踪

bash scripts/scene-detect.sh video.mp4     # 场景分析
bash scripts/auto-rough-cut.sh video.mp4   # 自动粗剪
bash scripts/smart-tagger.sh ./media/      # 智能标签
bash scripts/audio-normalizer.sh video.mp4 # 音频标准化
bash scripts/auto-thumbnail.sh video.mp4   # 自动缩略图
bash scripts/multi-lang-subtitles.sh video.mp4 en  # 多语言字幕
```

---

