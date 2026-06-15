---
name: ppt-compressor
description: This skill should be used when the user wants to compress a PowerPoint (.pptx) file by reducing the size of embedded videos and large images. It handles the complete workflow of extracting media from .pptx archives, compressing videos with a bundled ffmpeg (no installation required) and images with Pillow, and repackaging into a valid .pptx file. Trigger phrases include "compress PPT", "reduce PPT size", "compress PowerPoint", "PPT too large", "shrink presentation", "compress videos in PPT", "compress images in PPT", "PPT压缩", "压缩PPT", "PPT文件太大", or any mention of reducing .pptx file sizes involving embedded media. Supports Windows, macOS, and Linux.
---

# PPT Compressor (Videos & Images)

## Overview

Compress embedded videos and large images (>1MB) in PowerPoint (.pptx) files to significantly reduce file size while maintaining playback compatibility. The skill provides a bundled Python script with **built-in ffmpeg** — no installation required.

## Prerequisites

- **Python 3.7+** must be installed
- **Pillow** — automatically installed if missing (used for image compression)
- **ffmpeg** — **bundled** in `{SKILL_DIR}/scripts/bin/`. No manual installation needed!
  - If the bundled ffmpeg is missing, run: `python {SKILL_DIR}/scripts/download_ffmpeg.py` to re-download
  - Supports automatic download for Windows, macOS, and Linux

## Architecture

```
{SKILL_DIR}/
├── SKILL.md                          # This file
└── scripts/
    ├── compress_ppt_videos.py        # Main compression script (cross-platform)
    ├── path_helper.py                # Cross-platform path utilities
    ├── download_ffmpeg.py            # FFmpeg downloader (Windows/macOS/Linux)
    └── bin/
        ├── ffmpeg[.exe]              # Bundled ffmpeg (platform-specific)
        └── ffprobe[.exe]             # Bundled ffprobe (platform-specific)
```

### FFmpeg Resolution Order

The script automatically finds ffmpeg in this priority:
1. **Bundled version** in `{SKILL_DIR}/scripts/bin/` (preferred)
2. **System PATH** as fallback

This means users **never need to install ffmpeg manually**.

## User Interaction Guide (IMPORTANT for UX)

### 获取用户的 PPT 文件路径

当用户请求压缩 PPT 但**没有提供文件路径**时，Agent 应该：

#### 方式 1: 引导用户拖拽文件（推荐，跨平台通用）

直接告诉用户：

> 📂 **请把要压缩的 PPT 文件拖拽到这里**，或者直接发送文件路径给我。

#### 方式 2: 根据用户系统提供复制路径的指引

**Windows 用户：**
> 💡 在文件资源管理器中，按住 Shift 键右键点击文件，选择"复制为路径"，然后粘贴到这里。

**macOS 用户：**
> 💡 在 Finder 中选中文件，按 `Option + Command + C` 复制文件路径，然后粘贴到这里。
> 或者：右键点击文件，按住 Option 键，选择"将xxx拷贝为路径名"。

**Linux 用户：**
> 💡 在文件管理器中右键点击文件，选择"复制路径"或"Copy Path"。
> 或者使用终端：`readlink -f /path/to/file.pptx`

#### 方式 3: 自动识别用户消息中的路径

Agent 应该智能识别用户消息中的各种路径格式：

| 系统 | 用户输入示例 | Agent 应该提取的路径 |
|------|-------------|---------------------|
| Windows | `压缩这个 C:\Users\user\Desktop\报告.pptx` | `C:/Users/user/Desktop/报告.pptx` |
| Windows | `"D:/工作文档/演示文稿.pptx" 太大了` | `D:/工作文档/演示文稿.pptx` |
| macOS | `/Users/john/Documents/presentation.pptx` | `/Users/john/Documents/presentation.pptx` |
| macOS | `~/Desktop/report.pptx 压缩一下` | `~/Desktop/report.pptx` |
| Linux | `/home/user/documents/slides.pptx` | `/home/user/documents/slides.pptx` |
| 通用 | 直接拖拽文件（显示为路径文本） | 自动提取完整路径 |

**路径识别正则表达式参考**：
```
Windows 绝对路径: [A-Za-z]:[\\\/][^\s"'<>|*?]+\.pptx
Unix 绝对路径: /[^\s"'<>|*?]+\.pptx
Home 目录路径: ~/[^\s"'<>|*?]+\.pptx
带引号的路径: ["'][^"']+\.pptx["']
```

#### 方式 4: 如果无法识别，友好询问

如果用户消息中没有明确的文件路径，**根据用户系统**使用以下模板询问：

**Windows 系统：**
```
我需要知道 PPT 文件的位置才能帮你压缩。请用以下任一方式告诉我：

1. **拖拽文件**：直接把 .pptx 文件拖到对话框
2. **复制路径**：在文件资源管理器中，按住 Shift 右键点击文件 → "复制为路径"
3. **直接输入**：例如 `C:\Users\你的用户名\Desktop\文件名.pptx`
```

**macOS 系统：**
```
我需要知道 PPT 文件的位置才能帮你压缩。请用以下任一方式告诉我：

1. **拖拽文件**：直接把 .pptx 文件拖到对话框
2. **复制路径**：在 Finder 中选中文件，按 Option + Command + C
3. **直接输入**：例如 `/Users/你的用户名/Documents/文件名.pptx` 或 `~/Desktop/文件名.pptx`
```

**Linux 系统：**
```
我需要知道 PPT 文件的位置才能帮你压缩。请用以下任一方式告诉我：

1. **拖拽文件**：直接把 .pptx 文件拖到对话框
2. **复制路径**：在文件管理器中右键点击文件 → "复制路径"
3. **直接输入**：例如 `/home/你的用户名/Documents/文件名.pptx` 或 `~/Documents/文件名.pptx`
```

### 路径清理和标准化

Agent 在获取到路径后，应该：

1. **移除首尾引号**：`"C:\path\file.pptx"` → `C:\path\file.pptx`
2. **统一为正斜杠**：`C:\Users\file.pptx` → `C:/Users/file.pptx`（Python 兼容）
3. **验证文件扩展名**：确保是 `.pptx` 文件
4. **验证文件存在**：在执行前检查文件是否存在

### 验证文件存在的方法

在执行压缩前，Agent 应该先验证文件存在：

```bash
python -c "import os; print('✓ 文件存在' if os.path.exists(r'<path>') else '✗ 文件不存在')"
```

如果文件不存在，友好提示用户检查路径是否正确。

---

## Agent 完整执行流程

当用户请求压缩 PPT 时，Agent 应该按以下步骤执行：

### Step 1: 检测用户消息中是否有路径

使用 `path_helper.py` 或正则表达式从用户消息中提取路径：

```bash
python -c "import sys; sys.path.insert(0, r'{SKILL_DIR}/scripts'); from path_helper import extract_pptx_paths; paths = extract_pptx_paths(r'''<用户的完整消息>'''); print(paths[0] if paths else 'NO_PATH_FOUND')"
```

### Step 2: 根据检测结果决定下一步

**情况 A: 找到路径** → 进入 Step 3 验证

**情况 B: 没有路径** → 根据用户的操作系统友好询问（参考上方的"用户交互指南"）

**快速版本（通用）：**
```
📂 请把要压缩的 PPT 文件路径发给我。

**最简单的方法：** 直接把文件拖拽到对话框即可！

或者复制文件路径粘贴给我。
```

### Step 3: 验证文件

```bash
python -c "import sys; sys.path.insert(0, r'{SKILL_DIR}/scripts'); from path_helper import validate_path; r = validate_path(r'<提取到的路径>'); print(f'Valid: {r[\"valid\"]}, Size: {r[\"size_mb\"]}MB' if r['valid'] else f'Error: {r[\"error\"]}')"
```

### Step 4: 执行压缩

验证通过后，执行压缩（使用 Python one-liner）：

```bash
python -c "import sys; sys.path.insert(0, r'{SKILL_DIR}/scripts'); from compress_ppt_videos import run; run(r'<验证后的路径>')"
```

### Step 5: 报告结果

压缩完成后，告诉用户：
- 原始文件大小
- 压缩后文件大小  
- 压缩比例
- 输出文件位置

---

## CRITICAL: Execution Instructions (Agent MUST Follow)

### ⚠️ IMPORTANT: Avoid Path Parsing Issues

When running the compression script, you **MUST** use the following approach to avoid shell path parsing issues on Windows:

**RECOMMENDED METHOD (Most Reliable):**

Use Python's `-c` flag with raw strings to bypass shell escaping issues:

```python
python -c "
import sys
sys.path.insert(0, r'{SKILL_DIR}/scripts')
from compress_ppt_videos import compress_pptx
compress_pptx(r'<input_path>')
"
```

**ALTERNATIVE: Use forward slashes with double-quoted paths:**

```bash
python "{SKILL_DIR}/scripts/compress_ppt_videos.py" "<input_path>"
```

### Common Pitfalls to AVOID:

1. **DON'T** use backslashes with `cd` in PowerShell - it may fail silently
2. **DON'T** use complex path concatenation in shells
3. **DON'T** attempt multiple `cd` commands in sequence
4. **DO** use raw strings (r'...') in Python for Windows paths
5. **DO** use forward slashes in paths when possible (Python accepts them on Windows)
6. **DO** double-quote paths containing spaces or non-ASCII characters

### Handling Chinese Filenames / Paths with Spaces

Chinese characters and spaces in paths are common. Always:
- Wrap file paths in quotes: `"path/to/文件.pptx"`
- Use raw strings in Python: `r"C:\Users\用户\桌面\文件.pptx"`

## Workflow

### Quick Start

To compress a PPT file with default settings (compresses both videos and images >1MB):

```bash
python "{SKILL_DIR}/scripts/compress_ppt_videos.py" "<input.pptx>"
```

This produces `<input>_compressed.pptx` in the same directory.

### How It Works

1. **Extract** — The `.pptx` file (ZIP archive) is extracted to a temporary directory
2. **Discover Videos** — All video files under `ppt/media/` are identified (supports: `.mp4`, `.avi`, `.mov`, `.wmv`, `.m4v`, `.mkv`, `.webm`, `.flv`, `.mpeg`, `.mpg`)
3. **Compress Videos** — Each video is compressed using ffmpeg with H.264 codec and AAC audio
4. **Discover Images** — All image files > 1MB under `ppt/media/` are identified (supports: `.png`, `.jpg`, `.jpeg`, `.bmp`, `.tiff`, `.tif`, `.webp`)
5. **Compress Images** — Each large image is compressed using Pillow with quality optimization and optional downscaling
6. **Smart Replace** — Compressed files only replace originals if they are actually smaller
7. **Repackage** — The modified directory is re-zipped into a valid `.pptx` file

### Command-Line Options

```
python compress_ppt_videos.py <input.pptx> [options]

General Options:
  -o, --output PATH           Output file path (default: <input>_compressed.pptx)
  --no-videos                 Skip video compression
  --no-images                 Skip image compression
  --dry-run                   Preview what would be compressed without doing it

Video Compression Options:
  --crf VALUE                 Quality factor 0-51 (default: 28, higher = smaller file)
  --preset PRESET             Encoding speed (default: medium)
  --max-height PIXELS         Max video height, 0 = no scaling (default: 720)
  --audio-bitrate BITRATE     Audio bitrate (default: 128k)

Image Compression Options:
  --image-quality VALUE       JPEG quality 1-95 (default: 80, lower = smaller file)
  --image-max-dim PIXELS      Max image dimension, 0 = no scaling (default: 1920)
  --image-threshold BYTES     Size threshold for image compression (default: 1048576 = 1MB)
```

### Video Compression Parameters Guide

| Parameter | Default | Purpose | Guidance |
|-----------|---------|---------|----------|
| `--crf` | 28 | Controls visual quality | 23 = high quality, 28 = good for PPT, 32 = aggressive compression |
| `--preset` | medium | Encoding speed vs ratio | `fast` for speed, `slow` for smaller files |
| `--max-height` | 720 | Downscale resolution | 720p is sufficient for most presentations; set 0 to keep original |
| `--audio-bitrate` | 128k | Audio quality | 96k for speech-only, 128k for general, 192k for music |

### Image Compression Parameters Guide

| Parameter | Default | Purpose | Guidance |
|-----------|---------|---------|----------|
| `--image-quality` | 80 | JPEG quality (1-95) | 60 = aggressive, 80 = balanced, 90 = high quality |
| `--image-max-dim` | 1920 | Max width or height | 1920 for Full HD, 1280 for 720p, 0 to keep original |
| `--image-threshold` | 1MB | Min size to compress | Only images larger than this are compressed |

### Recommended Presets by Use Case

- **Maximum compression** (email/sharing): `--crf 32 --preset slow --max-height 480 --audio-bitrate 96k --image-quality 60 --image-max-dim 1280`
- **Balanced** (default, good for most): `--crf 28 --preset medium --max-height 720 --image-quality 80`
- **High quality** (important presentations): `--crf 23 --preset slow --max-height 0 --image-quality 90 --image-max-dim 0`
- **Fast processing** (quick compress): `--crf 28 --preset fast --max-height 720 --image-quality 80`
- **Images only** (no video compression): `--no-videos --image-quality 75 --image-max-dim 1920`
- **Videos only** (no image compression): `--no-images --crf 28`

## Usage Examples

### Example 1: Basic Compression (RECOMMENDED METHOD - Most Reliable)

User request: "Help me compress this PPT file, it's too large to email"

**Agent should use this Python one-liner approach:**

```bash
python -c "import sys; sys.path.insert(0, r'{SKILL_DIR}/scripts'); from compress_ppt_videos import run; run(r'C:/Users/user/Desktop/presentation.pptx')"
```

Or equivalently (with forward slashes which work on Windows):

```bash
python "{SKILL_DIR}/scripts/compress_ppt_videos.py" "C:/Users/user/Desktop/presentation.pptx"
```

### Example 2: Using the Python API (for complex scenarios)

When you need more control or want to avoid shell issues entirely:

```python
# This Python code can be executed directly
import sys
sys.path.insert(0, r'{SKILL_DIR}/scripts')
from compress_ppt_videos import run

# Basic usage
run(r"C:/path/to/presentation.pptx")

# With custom settings
run(r"C:/path/to/presentation.pptx", crf=32, image_quality=70)

# High quality compression
run(r"C:/path/to/presentation.pptx", crf=23, preset='slow', max_height=0)
```

### Example 3: Custom Video Settings

User request: "Compress my PPT but keep high video quality"

```bash
python -c "import sys; sys.path.insert(0, r'{SKILL_DIR}/scripts'); from compress_ppt_videos import run; run(r'C:/path/to/file.pptx', crf=23, preset='slow', max_height=0, image_quality=90)"
```

### Example 4: Images Only

User request: "My PPT has huge screenshots, just compress the images"

```bash
python -c "import sys; sys.path.insert(0, r'{SKILL_DIR}/scripts'); from compress_ppt_videos import run; run(r'C:/path/to/file.pptx', skip_videos=True, image_quality=75)"
```

### Example 5: Preview Before Compressing (Dry Run)

User request: "I want to see what media is in my PPT before compressing"

```bash
python -c "import sys; sys.path.insert(0, r'{SKILL_DIR}/scripts'); from compress_ppt_videos import run; run(r'C:/path/to/file.pptx', dry_run=True)"
```

### Example 6: Batch Compression

User request: "Compress all PPT files in this folder"

```python
import sys
import os
sys.path.insert(0, r'{SKILL_DIR}/scripts')
from compress_ppt_videos import run

folder = r"C:/path/to/folder"
for f in os.listdir(folder):
    if f.endswith('.pptx') and not f.endswith('_compressed.pptx'):
        run(os.path.join(folder, f))
```

## Troubleshooting

### Path / Shell Issues (MOST COMMON)

- **Command doesn't execute / silent failure**: Use the Python one-liner method:
  ```bash
  python -c "import sys; sys.path.insert(0, r'{SKILL_DIR}/scripts'); from compress_ppt_videos import run; run(r'<path>')"
  ```
- **Unicode/Chinese path errors**: Always use raw strings (`r'...'`) and forward slashes
- **PowerShell path issues**: Avoid `cd` commands; use full paths or Python one-liner
- **macOS/Linux: "python" not found**: Use `python3` instead of `python`
- **Home directory (~) not expanding**: Use `os.path.expanduser('~/path')` in Python

### FFmpeg Issues

- **"ffmpeg not found"**: Run `python {SKILL_DIR}/scripts/download_ffmpeg.py` to download the bundled version
- **macOS: "ffmpeg" cannot be opened (security)**: Run this command first:
  ```bash
  xattr -d com.apple.quarantine "{SKILL_DIR}/scripts/bin/ffmpeg"
  xattr -d com.apple.quarantine "{SKILL_DIR}/scripts/bin/ffprobe"
  ```
  Or install ffmpeg via Homebrew: `brew install ffmpeg`
- **Linux: permission denied**: Make ffmpeg executable:
  ```bash
  chmod +x "{SKILL_DIR}/scripts/bin/ffmpeg"
  chmod +x "{SKILL_DIR}/scripts/bin/ffprobe"
  ```

### Compression Issues

- **"Bad zip archive"**: The file may be corrupted or not a valid .pptx file
- **No size reduction**: Media may already be well-compressed; try lower CRF/quality or skip the file
- **Video not playing after compression**: Try `crf=23, max_height=0` for conservative compression
- **Image quality too low**: Increase `image_quality` (e.g., 90) or set `image_max_dim=0`
- **Pillow not installed**: The script auto-installs it; if that fails, run `pip install Pillow` manually

## Resources

### scripts/

- **`compress_ppt_videos.py`** — Main compression script. Provides:
  - `run(input_path, **kwargs)` — Simple function for programmatic use (RECOMMENDED)
  - `compress_pptx(...)` — Full function with all parameters
  - `main(argv=None)` — CLI entry point that accepts argument list
- **`path_helper.py`** — 路径辅助工具，帮助验证和提取用户输入的路径：
  - `validate_path(path)` — 验证路径是否有效，返回详细状态
  - `extract_pptx_paths(text)` — 从用户消息中智能提取 .pptx 路径
  - `normalize_path(path)` — 标准化路径格式
- **`compress.py`** — Simplified entry point wrapper
- **`download_ffmpeg.py`** — Downloads and installs ffmpeg essentials to `scripts/bin/`. Run this if the bundled ffmpeg is missing.
- **`bin/ffmpeg.exe`** — Bundled ffmpeg binary (Windows). Auto-detected by the compression script.
- **`bin/ffprobe.exe`** — Bundled ffprobe binary (Windows). Used for video analysis.

### API Reference

```python
from compress_ppt_videos import run, compress_pptx

# Simple API (RECOMMENDED)
run(input_path, output_path=None, **kwargs)

# Full API
compress_pptx(
    input_pptx,
    output_pptx=None,
    crf=28,
    preset='medium',
    max_height=720,
    audio_bitrate='128k',
    image_quality=80,
    image_max_dim=1920,
    image_threshold=1048576,  # 1MB
    skip_images=False,
    skip_videos=False,
    dry_run=False
)
```
