# Video Editing Skill for OpenClaw

一个基于 AI 的自动视频剪辑 Skill，专为口播/脱口秀/Vlog 类视频设计。

它可以自动将你的视频按每句话切分，去掉口误和卡壳，加上字幕，最终合成一个可以直接发布的短视频。

> 适用于：小红书、抖音、视频号等竖屏短视频平台

## 功能特性

- **语音识别切分** — 支持 faster-whisper（推荐，4x 加速）和 openai-whisper，自动按句子切分
- **GPU 硬件加速** — 自动检测 NVIDIA NVENC / Apple VideoToolbox / Intel QSV / AMD AMF
- **精确剪辑** — 重编码模式切割，音频在句子边界精确切断，无重复尾音
- **自动字幕** — 中英文自动检测，自动折行，竖屏位置优化
- **灵活合成** — 选择需要的片段，按任意顺序合成最终视频
- **自动封面** — 将视频第一帧替换为带标题的封面，自动根据内容总结标题
- **章节时间轴** — 自动分章，在视频底部/顶部叠加彩色章节进度条，横屏竖屏自适应
- **多视频支持** — 同时处理多个视频文件，跨视频混合选择片段
- **跨平台** — 支持 macOS / Linux / WSL / Windows
- **中国加速** — 自动检测中国区域，使用清华 pip 镜像和 HuggingFace 镜像

## 安装

### 方式一：通过 OpenClaw Skills 安装（推荐）

```bash
openclaw skills add https://github.com/maxazure/video-editing-skill.git
```

或手动克隆到 OpenClaw skills 目录：

```bash
git clone https://github.com/maxazure/video-editing-skill.git ~/.openclaw/skills/video-editing
```

### 方式二：手动克隆

```bash
git clone https://github.com/maxazure/video-editing-skill.git
cd video-editing-skill
```

### 安装系统依赖

**macOS：**
```bash
brew install ffmpeg
```

**Ubuntu/Debian/WSL：**
```bash
sudo apt install ffmpeg fonts-noto-cjk
```

**Windows：**
建议使用 WSL2 环境。在 WSL 中按 Ubuntu 方式安装即可。

### 安装 Python 依赖

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows WSL 同样使用此命令
pip install faster-whisper  # 推荐，速度快 4 倍
```

中国用户加速安装：
```bash
pip install faster-whisper -i https://pypi.tuna.tsinghua.edu.cn/simple
```

> Whisper 模型首次运行时会自动下载。中国用户会自动使用 HuggingFace 镜像 (hf-mirror.com)。

### 验证安装

```bash
python3 scripts/utils.py  # 运行环境诊断
```

这会输出完整的环境报告：平台、GPU、编码器、Whisper 引擎、推荐模型等。

## 使用方式

### 配合 OpenClaw / Claude Code 使用（推荐）

安装完依赖后，用自然语言告诉 AI：

```
帮我剪一下 videos/ 目录下的视频，按句子切分，去掉口误，加上字幕
```

AI 会自动调用各个脚本，完成整个剪辑流程。

### 手动使用

#### Step 1: 提取音频

```bash
python3 scripts/extract_audio.py "your_video.mp4"
# 输出: your_video_audio.wav
```

#### Step 2: 语音识别

```bash
source .venv/bin/activate
python3 scripts/transcribe.py "your_video_audio.wav" --model auto --language zh
# 输出: your_video_transcript.json
```

`--model auto` 会根据硬件自动选择最佳模型：

| 硬件 | 自动选择 | 原因 |
|------|---------|------|
| NVIDIA GPU | large-v3 | CUDA 加速，大模型也很快 |
| Apple Silicon | large-v3-turbo | 速度与质量的最佳平衡 |
| Intel/AMD 集显 | medium | CPU+iGPU 的最佳平衡 |
| 纯 CPU | small | 速度优先 |

也可手动指定：`--model large-v3` / `--model medium` 等

#### Step 3: 视频切分

```bash
python3 scripts/split_video.py "your_video.mp4" "your_video_transcript.json"
# 输出: your_video_clips/ 目录
```

#### Step 4: 烧录字幕

```bash
python3 scripts/burn_subtitles.py "your_video_clips" "your_video_transcript.json"
# 输出: your_video_clips_subtitled/ 目录
```

#### Step 5: 合成视频

```bash
python3 scripts/merge_clips.py "your_video_clips_subtitled" --select "1-5,8,10-15" --output "final.mp4"
```

#### Step 6: 生成封面

```bash
python3 scripts/generate_cover.py "final.mp4" --title "你的封面标题" --transcript "your_video_transcript.json"
# 输出: final_with_cover.mp4
```

#### Step 7: 添加章节时间轴

```bash
python3 scripts/add_chapter_bar.py "final.mp4" --transcript "your_video_transcript.json"
# 输出: final_chapters.mp4
```

自动根据转录内容分章，在视频上叠加彩色章节进度条。横屏视频放在底部，竖屏视频放在顶部（避开抖音/小红书底部 UI）。

可选参数：
- `--style mono` — 单色灰白风格（默认 `color` 彩色）
- `--chapters chapters.json` — 自定义章节 JSON

#### Step 8（可选）: 调整播放速度

```bash
ffmpeg -i final.mp4 \
  -filter_complex "[0:v]setpts=PTS/1.25[v];[0:a]atempo=1.25[a]" \
  -map "[v]" -map "[a]" \
  -c:v libx264 -preset fast -crf 18 -c:a aac -b:a 192k \
  final_1.25x.mp4
```

## 目录结构

```
video-editing-skill/
├── README.md                  # 本文件
├── SKILL.md                   # Skill 定义（OpenClaw 读取）
├── scripts/
│   ├── utils.py               # 共享工具（平台/GPU/字体/镜像检测）
│   ├── extract_audio.py       # 音频提取
│   ├── extract_audio.sh       # 音频提取（bash 版，兼容旧流程）
│   ├── transcribe.py          # 语音识别（faster-whisper / openai-whisper）
│   ├── split_video.py         # 视频切分
│   ├── burn_subtitles.py      # 字幕烧录
│   ├── merge_clips.py         # 视频合成
│   ├── generate_cover.py      # 封面生成
│   └── add_chapter_bar.py    # 章节时间轴
├── fonts/                     # 字体缓存（自动下载）
└── videos/                    # 用户视频工作目录
```

## 技术细节

| 组件 | 技术 |
|------|------|
| 语音识别 | faster-whisper (CTranslate2) / OpenAI Whisper |
| 视频编码 | NVENC / VideoToolbox / QSV / AMF / libx264（自动检测） |
| 字幕渲染 | ASS 格式 + Noto Sans SC / PingFang SC / Microsoft YaHei |
| 视频切分 | 精确重编码（非 stream copy） |
| 平台检测 | macOS / Linux / WSL / Windows 自动识别 |

### 硬件加速编码器优先级

```
NVIDIA NVENC > Apple VideoToolbox > Intel QSV > AMD AMF > CPU libx264
```

### 字幕字体优先级

```
自定义字体 > Noto Sans SC (自动下载) > PingFang SC (macOS) > Microsoft YaHei (Windows/WSL) > fc-match
```

中国用户字体下载使用 jsDelivr CDN 加速，无需访问 GitHub。

### 中国用户优化

- pip 安装自动使用清华镜像
- Whisper 模型自动使用 hf-mirror.com 下载
- 字体下载使用 jsDelivr CDN 备用源
- 可通过 `--mirror` 参数或 `USE_CN_MIRROR=1` 环境变量强制启用

## 系统要求

- macOS / Linux / WSL / Windows
- Python 3.8+
- FFmpeg（需包含 libass、libfreetype）
- 磁盘空间：约 1-3GB（取决于 Whisper 模型大小）

## License

MIT
