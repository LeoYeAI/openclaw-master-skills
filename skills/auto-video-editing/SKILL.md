---
name: video-editing
description: "Automated video editing skill for talk/vlog/standup videos. Use when: cutting video, splitting video into sentences, merging video clips, extracting audio, transcribing speech, auto-editing oral presentation videos, combining selected sentence clips into a final video, generating video cover/thumbnail with title. Requires ffmpeg and whisper."
argument-hint: "Provide the path(s) to video file(s) to process"
metadata: { "openclaw": { "emoji": "🎬", "os": ["darwin", "linux", "win32"], "requires": { "bins": ["ffmpeg", "python3"] }, "install": [{ "id": "ffmpeg-brew", "kind": "brew", "formula": "ffmpeg", "bins": ["ffmpeg"], "label": "Install FFmpeg (brew)" }] } }
---

# Auto Video Editing（自动视频剪辑）

根据语音内容，将口播/脱口秀类视频按句子自动切分，然后按用户选择合成带字幕的最终视频。

## Prerequisites（前置要求）

在执行任何操作之前，先运行环境检测：

```bash
python3 scripts/utils.py
```

这会自动检测平台（macOS/Linux/WSL/Windows）、GPU 类型、可用编码器、Whisper 引擎，并给出诊断报告。

如果缺少依赖，提示用户安装：
- **ffmpeg**: `brew install ffmpeg`（macOS）或 `apt install ffmpeg`（Linux/WSL）或下载 Windows 版本
- **whisper**: `pip install faster-whisper`（推荐，速度快 4 倍）或 `pip install openai-whisper`
- **中国用户**加速安装：`pip install faster-whisper -i https://pypi.tuna.tsinghua.edu.cn/simple`

如果项目根目录有 `.venv` 虚拟环境，运行 Python 脚本前先激活：
```bash
source .venv/bin/activate  # macOS/Linux/WSL
# Windows: .venv\Scripts\activate
```

### 平台说明

- **macOS (Apple Silicon)**: 自动使用 VideoToolbox 硬件编码加速，Whisper 推荐 large-v3-turbo 模型
- **macOS (Intel)**: 使用 VideoToolbox 编码，Whisper 使用 CPU 模式
- **Linux**: 自动检测 NVIDIA GPU (NVENC)、Intel QSV、AMD AMF
- **WSL**: 支持，自动检测 Windows 字体路径 (`/mnt/c/Windows/Fonts/`)
- **Windows**: 建议使用 WSL2 环境运行；支持 QSV/AMF 硬件编码
- **无独显 (集成显卡)**: Intel iGPU 使用 QSV 编码，AMD iGPU 使用 AMF 编码；Whisper 建议 medium 模型（而非 large）
- **中国用户**: 自动检测中国区域，使用清华 pip 镜像和 HuggingFace 镜像下载模型，也可通过 `--mirror` 参数强制启用

## Workflow（工作流程）

### Phase 1: Audio Extraction（音频提取）

对每个输入视频文件，使用 [extract_audio.py](./scripts/extract_audio.py) 提取音频：

```bash
python3 scripts/extract_audio.py "<video_path>"
```

输出：与视频同目录下的 `<video_name>_audio.wav` 文件。

### Phase 2: Speech Recognition（语音识别）

使用 [transcribe.py](./scripts/transcribe.py) 对音频进行语音识别，生成带时间戳的逐句文本：

```bash
python3 scripts/transcribe.py "<audio_path>" --model auto --language zh
```

- `--model auto`：根据硬件自动选择最佳模型（NVIDIA GPU → large-v3，Apple Silicon → large-v3-turbo，集成显卡 → medium，纯 CPU → small）
- 也可手动指定：`tiny`, `base`, `small`, `medium`, `large-v3`, `large-v3-turbo`
- `--engine auto`：自动检测 faster-whisper（推荐）或 openai-whisper
- `--mirror`：中国用户使用镜像源下载模型
- `--language`：`zh`（中文），`en`（英文），`ja`（日文）等，也可省略让 whisper 自动检测

输出：与音频同目录下的 `<video_name>_transcript.json` 文件，格式如下：

```json
{
  "segments": [
    {"id": 1, "start": 0.0, "end": 2.5, "text": "大家好"},
    {"id": 2, "start": 2.5, "end": 5.1, "text": "今天我们来聊一个话题"}
  ]
}
```

**转录后检查**：如果文本中有明显的识别错误（如产品名、专有名词），应修正 transcript.json 中的文字后再进行后续步骤。

### Phase 3: Video Splitting（视频切分）

使用 [split_video.py](./scripts/split_video.py) 根据转录结果将视频切分为独立片段：

```bash
python3 scripts/split_video.py "<video_path>" "<transcript_json_path>"
```

输出：在视频同目录下创建 `<video_name>_clips/` 文件夹，包含按句子编号命名的片段文件，如 `clip_001.mp4`, `clip_002.mp4` 等。

**注意**：
- 默认 padding 为 0（片段间无重叠），避免合成时出现重复音频。
- 使用精确重编码切割（`-ss` 后置 + re-encode），确保音频在句子边界精确切断。

### Phase 3.5: Subtitle Burning（字幕烧录）

使用 [burn_subtitles.py](./scripts/burn_subtitles.py) 为每个片段烧录字幕：

```bash
python3 scripts/burn_subtitles.py "<clips_dir>" "<transcript_json_path>"
```

字幕行为：
- **自动检测语言**：中文内容自动使用中文字幕，英文内容使用英文字幕。
- **自动折行**：长字幕自动分成两行，不会超出屏幕边界。
- **竖屏优化**：字体大小按短边（宽度）缩放，字幕位置在画面 72% 高度处，适配小红书等竖屏平台。
- **中文字体优先级**：
  1. 首先尝试从 Google Fonts 下载 **Noto Sans SC**（会缓存到 skill 的 `fonts/` 目录）
  2. 如果下载失败，macOS 使用 **PingFang SC**（苹方）；Windows 使用 **Microsoft YaHei**（微软雅黑）
- 可用 `--font-path` 指定自定义字体文件
- 可用 `--font-size` 调整字号（默认 48，基于 1080p 自动缩放）

输出：`<video_name>_clips_subtitled/` 目录，包含带字幕的片段。

**注意**：此步骤完成后，Phase 4-5 中应使用 `_clips_subtitled/` 目录而非 `_clips/` 目录。

### Phase 4: User Interaction（用户交互）

**展示片段列表给用户**，格式如下：

```
视频片段列表：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  #   | 时间区间          | 内容
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1   | 00:00.0 - 00:02.5 | 大家好
  2   | 00:02.5 - 00:05.1 | 今天我们来聊一个话题
  3   | 00:05.1 - 00:08.3 | 这个话题非常有意思
  ...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

请选择要合成的片段（示例）：
  - 连续范围：1-10
  - 多个片段：1,3,5,7
  - 混合选择：1-4,6,8-10
```

如果有多个视频文件，分别展示每个视频的片段列表，让用户跨视频选择。
选好后可将来自不同视频的片段复制到同一个临时目录中，按顺序重新编号后合成。

等待用户回复选择后，进入 Phase 5。

### Phase 5: Merge & Export（合成导出）

使用 [merge_clips.py](./scripts/merge_clips.py) 将用户选择的片段合成为最终视频：

```bash
python3 scripts/merge_clips.py "<clips_dir>" --select "1-4,6,8" --output "<output_path>"
```

- `--select`：用户选择的片段编号，支持 `1-4`（范围）、`1,3,5`（逐个）、`1-4,6,8-10`（混合）。
- `--output`：输出文件路径，默认为 `<clips_dir>/../<video_name>_final.mp4`。

输出：合成后的最终视频文件。

### Phase 6: Cover Generation（封面生成）

合成完成后，为视频生成封面图片。

**交互流程**：
1. 询问用户是否要为视频命名以及封面标题怎么写。
2. 如果用户提供了标题，直接使用该标题。
3. 如果用户没有特别要求，先从 transcript JSON 中读取所有句子文本，然后 **站在观众的角度** 总结出一个吸引人的封面标题：
   - 标题应简短有力（建议 6-15 个字）
   - 从观众视角出发，突出视频的核心看点或价值
   - 例如：「3 分钟学会拍小红书封面」而非「我今天教大家拍封面」
4. 确认标题后，使用 [generate_cover.py](./scripts/generate_cover.py) 将封面写入视频：

```bash
python3 scripts/generate_cover.py "<final_video_path>" --title "封面标题文字" --transcript "<transcript_json_path>"
```

- `--title`：封面上显示的标题文字
- `--transcript`：转录 JSON 路径（当未提供 --title 时，脚本会输出全文供 AI 总结）
- `--font-path`：可选，指定自定义字体
- `--output`：可选，指定输出路径，默认为 `<video_name>_with_cover.mp4`

**注意**：
- 封面标题会自动过滤特殊字符和 emoji，避免乱码。
- 脚本会提取视频第一帧，叠加白色粗体标题文字（带黑色描边和阴影），然后将这一帧替换回视频的第一帧，生成新的视频文件。原视频不会被修改。
- 中文字体使用与字幕相同的查找逻辑（Google Noto Sans SC > 系统字体）。

输出：`<video_name>_with_cover.mp4`

### Phase 7: Chapter Timeline Bar（章节时间轴）

为最终视频添加可视化的章节进度条。

使用 [add_chapter_bar.py](./scripts/add_chapter_bar.py) 在视频上叠加章节时间轴：

```bash
python3 scripts/add_chapter_bar.py "<video_path>" --transcript "<transcript_json_path>"
```

**自动行为**：
- 根据 transcript 自动将视频分为若干章节（每章约 15-30 秒，最多 8 章）
- 每章使用不同颜色的色块，带白色播放进度指示
- 章节切换时自动显示章节标题（3 秒后淡出）
- **横屏视频**：时间轴在视频底部，章节标题在时间轴上方
- **竖屏视频**：时间轴在视频顶部（避开底部平台 UI），章节标题在时间轴下方

也可以提供自定义章节 JSON：

```bash
python3 scripts/add_chapter_bar.py "<video_path>" --chapters chapters.json
```

chapters.json 格式：
```json
{
  "chapters": [
    {"title": "开场", "start": 0.0, "end": 15.0},
    {"title": "正题", "start": 15.0, "end": 60.0}
  ]
}
```

参数说明：
- `--transcript`：从转录 JSON 自动生成章节
- `--chapters`：使用自定义章节 JSON
- `--style color`（默认）：彩色分段，每章不同颜色
- `--style mono`：单色风格，灰白交替，更简约
- `--max-chapters`：自动分章的最大章节数（默认 8）
- `--font-path`：自定义字体
- `--output`：输出路径，默认为 `<video_name>_chapters.mp4`

输出：`<video_name>_chapters.mp4`，同时在终端打印 YouTube 兼容的章节时间戳。

### Phase 8: Post-merge Validation（合成后验证）

合成完成后，对最终视频执行一次验证流程：

1. 提取最终视频的音频
2. 重新进行语音识别
3. 检查识别结果中是否存在相邻片段的文字重复（前一句末尾 2-3 个字与后一句开头重复）
4. 如发现技术性重复（非自然语言重复），需要回到 Phase 3 重新切分相关片段

## Important Notes（注意事项）

1. **精确切割**：视频切分使用重编码模式（非 stream copy），确保音频在句子边界精确切断，避免相邻片段出现重复的尾音。
2. **多视频处理**：如果用户提供多个视频，对每个视频独立执行 Phase 1-3.5，然后在 Phase 4 统一展示所有视频的片段列表，支持跨视频混合选择片段。
3. **识别模型选择**：中文视频建议使用 `large` 模型，`base`/`small` 模型中文识别率较低。`large` 模型约需 2.9GB 下载空间。
4. **工作目录**：所有中间文件（音频、转录、片段）都保存在视频文件所在目录下，便于管理。
5. **错误处理**：如果某一步失败，向用户报告具体错误信息，并建议可能的解决方案。
6. **字幕字体**：ffmpeg 需要编译包含 `libass` 和 `libfreetype`。macOS 可通过 `brew install ffmpeg` 获取。
7. **竖屏适配**：字幕位置和字体大小已针对 9:16 竖屏视频（如小红书、抖音）优化。横屏视频同样支持。
8. **速度调整**：如需调整播放速度，可使用 ffmpeg：
   ```bash
   ffmpeg -i input.mp4 -filter_complex "[0:v]setpts=PTS/1.25[v];[0:a]atempo=1.25[a]" -map "[v]" -map "[a]" -c:v libx264 -preset fast -crf 18 -c:a aac -b:a 192k output_1.25x.mp4
   ```

## FAQ / Troubleshooting（常见问题诊断）

遇到错误时，先运行环境诊断：
```bash
python3 scripts/utils.py
```

### Q1: `No such filter: 'drawtext'` 或 `No such filter: 'ass'`

**原因**：ffmpeg 编译时未包含 `libfreetype`（drawtext 所需）或 `libass`（字幕所需）。

**诊断**：
```bash
ffmpeg -hide_banner -filters 2>/dev/null | grep -E "drawtext|ass|subtitles"
```
如果无输出，说明缺少对应滤镜。

**解决**：
- **macOS**：标准 `brew install ffmpeg` 可能不包含这些库。使用第三方 tap 安装完整版：
  ```bash
  brew tap homebrew-ffmpeg/ffmpeg
  brew install homebrew-ffmpeg/ffmpeg/ffmpeg --with-fdk-aac
  ```
  该 tap 默认启用 `--enable-libfreetype --enable-libass --enable-libfontconfig`。
- **Linux/WSL**：`apt install ffmpeg` 通常已包含。如果缺少，安装开发依赖后从源码编译：
  ```bash
  sudo apt install libfreetype6-dev libfontconfig1-dev libass-dev
  ```
- **影响范围**：缺少 drawtext 时，字幕烧录（burn_subtitles.py）、封面文字（generate_cover.py）和章节标题标签会失败或自动降级。章节进度条的色块和播放头不受影响（仅使用 drawbox）。

### Q2: `Undefined constant or missing '(' in 'iw*0.5-tw/2'`

**原因**：ffmpeg drawtext 的 `x` 表达式中使用了 `tw`（text width），但某些 ffmpeg 版本中 `tw` 在 `x` 参数的上下文中不可用。

**解决**：脚本已修复此问题（使用像素值 `{pixel_x}-text_w/2` 代替 `iw*{frac}-tw/2`）。如果你修改了脚本并遇到此错误，请使用 `text_w` 而非 `tw`，并确保 `x` 表达式中不包含 `iw*` 动态计算。

### Q3: `Invalid alpha value specifier '%{eif:...}'` (drawtext fontcolor)

**原因**：试图在 `fontcolor` 参数中嵌入 `%{eif}` 表达式来实现透明度渐变，但 ffmpeg 不支持在颜色值中使用此语法。

**解决**：使用 drawtext 的 `alpha` 参数（独立于 fontcolor），而非试图在 `fontcolor=white@'%{eif:...}'` 中嵌入表达式。正确写法：
```
drawtext=text='hello':fontcolor=white:alpha='if(lt(t,1),t,1)'
```
错误写法（会报错）：
```
drawtext=text='hello':fontcolor=white@'%{eif:if(lt(t,1),t,1):d:2}'
```

### Q4: ffmpeg 硬件编码器失败 (`h264_videotoolbox` / `h264_nvenc` / `h264_qsv` 报错)

**原因**：检测到的硬件编码器不支持当前的视频参数（如特殊分辨率、色彩空间），或驱动版本不兼容。

**诊断**：
```bash
ffmpeg -encoders 2>/dev/null | grep -E "nvenc|videotoolbox|qsv|amf"
```

**解决**：在脚本命令后添加 `--force-cpu` 参数（如脚本支持），或手动替换编码参数。也可以在 `scripts/utils.py` 中临时修改 `get_ffmpeg_encoder()` 函数，让它直接返回 `("libx264", ["-preset", "fast", "-crf", "18"])`。

### Q5: 中文字幕显示为方框（豆腐块）

**原因**：系统中没有可用的中文字体文件。

**诊断**：
```bash
python3 -c "from scripts.utils import find_chinese_font; print(find_chinese_font())"
```
如果返回 `(None, ...)`，说明未找到中文字体。

**解决**：
- **macOS**：系统自带 PingFang SC，一般不会出现此问题。
- **Linux/WSL**：安装中文字体包：
  ```bash
  sudo apt install fonts-noto-cjk
  ```
- **WSL 备选**：脚本会自动尝试 `/mnt/c/Windows/Fonts/msyh.ttc`（微软雅黑），前提是 Windows 已安装该字体。
- **手动指定**：使用 `--font-path /path/to/your/font.ttf` 参数。
- **自动下载**：脚本首次运行时会尝试从 Google Fonts（中国用户使用 jsDelivr CDN）下载 Noto Sans SC，缓存到 `fonts/` 目录。

### Q6: Whisper 模型下载失败 / 超时

**原因**：网络问题，尤其是中国用户无法访问 HuggingFace。

**解决**：
- 使用 `--mirror` 参数：`python3 scripts/transcribe.py audio.wav --mirror --model auto`
- 或手动设置环境变量：
  ```bash
  export HF_ENDPOINT=https://hf-mirror.com
  ```
- 使用 faster-whisper 时，模型从 HuggingFace 下载；设置 `HF_ENDPOINT` 后会自动走镜像。
- 使用 openai-whisper 时，模型从 GitHub 下载，中国用户可能需要代理。建议改用 faster-whisper。

### Q7: `pip install faster-whisper` 安装失败 / 超时

**解决**：中国用户使用清华镜像：
```bash
pip install faster-whisper -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
```

### Q8: WSL 环境下 ffmpeg 找不到或版本过旧

**诊断**：
```bash
which ffmpeg && ffmpeg -version | head -1
```

**解决**：
```bash
sudo apt update && sudo apt install ffmpeg
```
如果系统源的 ffmpeg 版本过旧（< 4.0），使用 PPA：
```bash
sudo add-apt-repository ppa:savoury1/ffmpeg4
sudo apt update && sudo apt install ffmpeg
```
