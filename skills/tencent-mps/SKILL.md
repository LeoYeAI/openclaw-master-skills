---
name: tencent-mps
description: "腾讯云 MPS 媒体处理服务。只要用户的请求涉及音视频或图片的处理、生成、增强、用量查询、内容理解、媒体质检，必须使用此 Skill。覆盖：转码/压缩/格式转换、画质增强/老片修复/超分、字幕提取/翻译/语音识别、去字幕/擦除水印/人脸模糊、图片超分/美颜/降噪、音频分离/人声提取/伴奏提取、AI生图/生视频（含分镜）、大模型音视频理解、媒体质检、用量统计。视频增强支持专用模板（真人/漫剧/抖动优化/细节最强/人脸保真，720P至4K）。无论是视频转码、去水印、提取人声、画质修复、内容理解、质量检测，还是AI生成图片视频，都应调用此 Skill。"
metadata:
  version: "1.1.2"
---

# 腾讯云媒体处理服务（MPS）

> 💰 **费用提示**：本 Skill 调用腾讯云 MPS 服务会产生相应费用，包括转码费、AI 处理费、存储费等。具体计费标准请参考 [腾讯云 MPS 定价](https://cloud.tencent.com/document/product/862/36180)。每次使用MPS的媒体处理/图片处理/生图/生视频功能，一定要给出提示。

通过腾讯云官方 Python SDK 调用 MPS API，所有脚本位于 `scripts/` 目录，均支持 `--help` 和 `--dry-run`。

> **详细参数**：见 [`references/params.md`](references/params.md)
> **完整示例集**：见 [`references/scripts-detail.md`](references/scripts-detail.md)

## 环境配置

检查环境变量：
```bash
python scripts/load_env.py --check-only
```

配置（`~/.profile` 或 `~/.bashrc`）：
```bash
# 必须（所有脚本）
export TENCENTCLOUD_SECRET_ID="your-secret-id"
export TENCENTCLOUD_SECRET_KEY="your-secret-key"

# 以下场景必须配置 COS 变量：
#   1. 输入源为 --cos-object（即 COS 对象路径，非 URL）
#   2. 使用 mps_cos_upload.py / mps_cos_download.py 上传/下载本地文件
#   3. 脚本需要将处理结果写回 COS（OutputStorage）
export TENCENTCLOUD_COS_BUCKET="your-bucket"        # COS 存储桶名
export TENCENTCLOUD_COS_REGION="your-bucket-region" # 存储桶地域，如 ap-guangzhou
```

安装依赖：
```bash
pip install tencentcloud-sdk-python cos-python-sdk-v5
```

## 本地文件处理流程

MPS 只接受 URL 或 COS 对象作为输入，**本地文件必须先上传**。

### 用户输入本地文件时的自动处理流程

当用户请求涉及本地文件路径（如 `./video.mp4`、`/path/to/image.jpg`）时，按以下步骤**自动处理**：

**步骤 1：上传文件到 COS**
```bash
python scripts/mps_cos_upload.py --local-file <本地文件路径> --cos-key <目标路径>
```
- 使用 `--cos-key` 指定合理的存储路径（默认路径 `input/`）
- 记录上传返回的 COS 信息：bucket、region、key

**步骤 2：使用 COS 路径参数执行脚本**
根据脚本类型，使用各个脚本中 传递 COS 路径的方式，如下：
| 脚本 | COS 路径参数方式 | 示例 |
|------|----------------|------|
| `mps_transcode.py` | `--cos-object <key>` | `--cos-object input/video.mp4` |
| `mps_enhance.py` | `--cos-object <key>` | `--cos-object input/video.mp4` |
| `mps_erase.py` | `--cos-object <key>` | `--cos-object input/video.mp4` |
| `mps_subtitle.py` | `--cos-object <key>` | `--cos-object input/video.mp4` |
| `mps_imageprocess.py` | `--cos-object <key>` | `--cos-object input/image.jpg` |
| `mps_qualitycontrol.py` | `--cos-object <key>` | `--cos-object input/video.mp4` |
| `mps_av_understand.py` | `--cos-object <key>` | `--cos-object input/video.mp4` |
| `mps_vremake.py` | `--cos-object <key>` | `--cos-object input/video.mp4` |
| `mps_narrate.py` | `--cos-object <key>` | `--cos-object input/video.mp4` |
| `mps_highlight.py` | `--cos-object <key>` | `--cos-object input/video.mp4` |
| `mps_aigc_image.py` | `--cos-input-bucket <b> --cos-input-region <r> --cos-input-key <k>` | `--cos-input-bucket xxx --cos-input-region ap-guangzhou --cos-input-key input/img.jpg` |
| `mps_aigc_video.py` | `--cos-input-bucket <b> --cos-input-region <r> --cos-input-key <k>` | `--cos-input-bucket xxx --cos-input-region ap-guangzhou --cos-input-key input/img.jpg` |

> **注意**：使用 `--cos-object` 的脚本依赖环境变量 `TENCENTCLOUD_COS_BUCKET` 和 `TENCENTCLOUD_COS_REGION`；AIGC 类脚本需要显式传递完整的 COS 信息。

**步骤 3：下载处理结果（如需要）**
```bash
python scripts/mps_cos_download.py --cos-key <输出key> --local-file <本地保存路径>
```

### 输入方式说明

根据输入来源不同，支持两种方式：

#### 方式一：COS 路径方式（推荐用于本地上传文件）
使用 `--cos-object <key>` 参数（或 `--cos-input-bucket/--cos-input-region/--cos-input-key`）

- 适用场景：用户上传本地文件到 COS 后处理
- 原因：本地上传的文件可能没有公开读取权限，直接使用 URL 可能会失败
- 示例：`--cos-object input/video.mp4`

#### 方式二：URL 方式（适用于已有 URL）
使用 `--url <url>` 参数

- 适用场景：用户直接提供文件 URL（包括其他账号/来源的 COS URL、外部链接等）
- 要求：URL 必须可公开访问或已携带有效签名
- 示例：`--url https://example-bucket.cos.ap-guangzhou.myqcloud.com/video.mp4`

> ⚠️ **注意**：如果 URL 来自本地上传的 COS 文件且没有公开权限，请使用方式一（COS 路径方式），脚本会自动生成带签名的 URL。

### 手动处理示例

如需手动执行，完整流程如下：
```bash
# 1. 上传
python scripts/mps_cos_upload.py --local-file ./video.mp4 --cos-key input/video.mp4
# 2. 执行任务（使用 COS 路径）
python scripts/mps_transcode.py --cos-object input/video.mp4
# 3. 下载结果
python scripts/mps_cos_download.py --cos-key output/result.mp4 --local-file ./result.mp4
```

返回结果含链接时，用 Markdown 格式返回给用户：`[文件名](URL)`

## 异步任务说明

所有脚本默认自动轮询等待完成。
- 只提交不等待：加 `--no-wait`，脚本返回 TaskId
- 手动查询：音视频用 `mps_get_video_task.py`，图片用 `mps_get_image_task.py`

## 脚本功能映射（职责边界）

> 💰 以下操作将调用腾讯云 MPS 服务并产生费用。

选择脚本时必须严格按照映射关系，**不得混用**：

| 用户需求类型 | 使用脚本 | 说明 |
|---|---|---|
| 检查画面质量、检测模糊/花屏 | `mps_qualitycontrol.py` | **唯一质检脚本**，`--definition 60`（默认） |
| 检测播放兼容性、卡顿、播放异常 | `mps_qualitycontrol.py` | **唯一质检脚本**，`--definition 70` |
| 音频质量检测、音频事件检测 | `mps_qualitycontrol.py` | **唯一质检脚本**，`--definition 50` |
| 去除字幕、擦除水印、人脸/车牌模糊 | `mps_erase.py` | 仅用于画面内容擦除/遮挡 |
| 画质增强、老片修复、超分辨率 | `mps_enhance.py` | 视频画质提升 |
| 转码、压缩、格式转换 | `mps_transcode.py` | 编码格式处理 |
| 字幕提取、翻译、字幕类语音识别 | `mps_subtitle.py` | 字幕相关 |
| 图片处理（超分/美颜/降噪） | `mps_imageprocess.py` | 图片增强 |
| AI 生图（文生图/图生图） | `mps_aigc_image.py` | AIGC 图片生成 |
| AI 生视频（文生视频/图生视频/分镜生成） | `mps_aigc_video.py` | AIGC 视频生成，**Kling 模型支持分镜功能** |
| 音视频内容理解（场景/摘要/分析/语音识别） | `mps_av_understand.py` | 大模型理解，**必须提供 `--mode` 和 `--prompt`** |
| 视频去重（画中画/视频扩展/换脸/换人等） | `mps_vremake.py` | VideoRemake，**必须提供 `--mode`** |
| 用量统计查询 | `mps_usage.py` | 调用次数/时长查询 |
| AI解说二创 / 短剧解说 / 自动生成短剧解说视频 / 短剧解说混剪 | `mps_narrate.py` | 必须从预设 `--scene` 中选择；不支持输入自定义脚本；多集视频按顺序通过 `--extra-urls` 追加 |
| 精彩集锦 / 高光提取 / 自动剪辑精彩片段 / 足球进球集锦 / 篮球集锦 / 短剧高光 | `mps_highlight.py` | 必须从预设 `--scene` 中选择，禁止自拼 ExtendedParameter；不支持直播流 |
| 查询音视频处理任务状态 | `mps_get_video_task.py` | ProcessMedia 任务查询 |
| 查询图片处理任务状态 | `mps_get_image_task.py` | ProcessImage 任务查询 |
| 上传本地文件到 COS | `mps_cos_upload.py` | 本地→COS 前置步骤 |
| 从 COS 下载文件 | `mps_cos_download.py` | COS→本地 后置步骤 |
| 列出 COS Bucket 文件 | `mps_cos_list.py` | 查看 COS 文件列表，支持路径过滤和文件名搜索 |

> **重要**：`mps_erase.py` 职责是**擦除/遮挡画面视觉元素**，不涉及质量检测。
> "画质检测"、"模糊"、"花屏"、"播放兼容性"、"音频质检" → 必须用 `mps_qualitycontrol.py`。

## 生成命令的强制规则

1. **脚本路径前缀**：所有生成的 python 命令必须包含 `scripts/` 路径前缀，格式为 `python scripts/mps_xxx.py ...`。禁止生成 `python mps_xxx.py ...`（缺少 scripts/ 前缀）的命令。

2. **禁止占位符**：所有参数值必须是真实值。若用户未提供必需值，**先询问**，不得用 `<视频URL>`、`YOUR_URL` 等占位符。

3. **`mps_qualitycontrol.py` 必须含 `--definition`**：
   - 音频质检：`--definition 50`
   - 画面质检（默认）：`--definition 60`
   - 播放兼容性：`--definition 70`

4. **`mps_av_understand.py` 必须含 `--mode` 和 `--prompt`**：
   - `--mode video`（理解视频画面）或 `--mode audio`（仅音频，视频自动提取音频）
   - `--prompt` 控制大模型理解侧重点，缺失时结果可能为空

5. **`mps_narrate.py` 必须含 `--scene`**：
   - 值必须是预设枚举之一：`short-drama` | `short-drama-no-erase`
   - 用户说"有字幕"/"带硬字幕"时默认选含擦除场景（`short-drama`）
   - 用户说"没有字幕"/"原片无字幕"/"不擦除"时选 `-no-erase` 场景（`short-drama-no-erase`）
   - 多集视频时，第一集用 `--url`/`--cos-object`，后续集用 `--extra-urls` 按顺序追加
   - 禁止传入 `scriptUrls` 相关参数（本次不支持输入自定义脚本）

6. **`mps_highlight.py` 必须含 `--scene`**：
   - 值必须是预设枚举之一：`vlog` | `vlog-panorama` | `short-drama` | `football` | `basketball` | `custom`
   - 用户提到"篮球"/"足球"/"短剧"/"VLOG"等关键词时直接映射到对应 `--scene`，无需二次询问
   - `--prompt` 和 `--scenario` 仅在 `--scene custom` 时生效，但二者非必填
   - `--top-clip` 仅允许在 `vlog` / `vlog-panorama` / `custom` 场景下使用
   - 禁止生成预设表以外的 ExtendedParameter 字段或值
   - 用户请求处理直播流集锦时，告知当前 skill 不支持直播流，需使用 MPS API 直接调用

## 关键脚本说明

### 视频增强 (`mps_enhance.py`)

大模型增强模板（`--template`），按场景+目标分辨率选择：

| 场景 | 720P | 1080P | 2K | 4K |
|------|------|-------|----|----|
| 真人（Real） | 327001 | 327003 | 327005 | 327007 |
| 漫剧（Anime） | 327002 | 327004 | 327006 | 327008 |
| 抖动优化 | 327009 | 327010 | 327011 | 327012 |
| 细节最强 | 327013 | 327014 | 327015 | 327016 |
| 人脸保真 | 327017 | 327018 | 327019 | 327020 |

### 去字幕擦除 (`mps_erase.py`)

预设模板：`101` 去字幕 | `102` 去字幕+OCR | `201` 去水印高级版 | `301` 人脸模糊 | `302` 人脸+车牌模糊

### 大模型音视频理解 (`mps_av_understand.py`)

通过 `AiAnalysisTask.Definition=33` + `ExtendedParameter(mvc.mode + mvc.prompt)` 控制。

```bash
# 视频内容理解
python scripts/mps_av_understand.py \
    --url https://example.com/video.mp4 \
    --mode video \
    --prompt "请分析这个视频的主要内容、场景和关键信息"

# 音频模式（视频自动提取音频）
python scripts/mps_av_understand.py \
    --url https://example.com/video.mp4 \
    --mode audio \
    --prompt "请进行语音识别，输出完整文字内容"

# 对比分析（两段音视频）
python scripts/mps_av_understand.py \
    --url https://example.com/v1.mp4 \
    --extend-url https://example.com/v2.mp4 \
    --mode audio \
    --prompt "对比两段音频，分析差异"

# 查询任务
python scripts/mps_av_understand.py --task-id 2600011633-WorkflowTask-xxxxx --json
```

### 媒体质检 (`mps_qualitycontrol.py`)

脚本支持以下 3 种系统预设模板（`--definition` 参数）：

**预设模板：**
- `60`（默认）：格式质检-Pro版，检测画面模糊、花屏、画面受损等内容问题
- `50`：Audio Detection，音频质量/音频事件检测
- `70`：内容质检-Pro版，检测播放卡顿、播放异常、播放兼容性问题

```bash
# 画面质检（默认，使用预设模板 60）
python scripts/mps_qualitycontrol.py --url https://example.com/video.mp4 --definition 60

# 播放兼容性质检（预设模板 70）
python scripts/mps_qualitycontrol.py --url https://example.com/video.mp4 --definition 70

# 音频质检（预设模板 50）
python scripts/mps_qualitycontrol.py --url https://example.com/audio.mp3 --definition 50

# 异步提交
python scripts/mps_qualitycontrol.py --url https://example.com/video.mp4 --definition 60 --no-wait
```

### 视频去重 (`mps_vremake.py`)

```bash
# 画中画去重（等待结果）
python scripts/mps_vremake.py --url https://example.com/video.mp4 --mode PicInPic --wait

# 视频扩展去重
python scripts/mps_vremake.py --url https://example.com/video.mp4 --mode BackgroundExtend --wait

# 换脸模式
python scripts/mps_vremake.py --url https://example.com/video.mp4 --mode SwapFace \
    --src-faces https://example.com/src.png --dst-faces https://example.com/dst.png --wait

# 换人模式
python scripts/mps_vremake.py --url https://example.com/video.mp4 --mode SwapCharacter \
    --src-character https://example.com/src_full.png \
    --dst-character https://example.com/dst_full.png --wait

# 画中画 + LLM 提示词
python scripts/mps_vremake.py --url https://example.com/video.mp4 --mode PicInPic \
    --llm-prompt "生成一个唯美的自然风景背景图片" --wait

# 异步提交（默认，不加 --wait）
python scripts/mps_vremake.py --url https://example.com/video.mp4 --mode PicInPic

# 查询任务
python scripts/mps_vremake.py --task-id 2600011633-WorkflowTask-xxxxx --json
```

**去重模式**：`PicInPic`（画中画）`BackgroundExtend`（视频扩展）`VerticalExtend`（垂直填充）`HorizontalExtend`（水平填充）`AB`（视频交错）`SwapFace`（换脸）`SwapCharacter`（换人）  
**主要参数**：`--url` / `--cos-object` / `--task-id` / `--mode`（必填）/ `--wait` / `--llm-prompt` / `--llm-video-prompt` / `--src-faces`+`--dst-faces`（换脸）/ `--src-character`+`--dst-character`（换人）/ `--json` / `--dry-run`

### AI 解说二创 (`mps_narrate.py`)

输入原始视频，一站式自动完成解说脚本生成、脚本匹配成片、AI 配音、去字幕等操作，输出带有解说文案、配音和字幕的新视频。

```bash
# 短剧单集解说（默认含擦除，输出1个视频）
python scripts/mps_narrate.py --url https://example.com/drama.mp4 --scene short-drama

# COS对象输入
python scripts/mps_narrate.py --cos-object /input/drama.mp4 --scene short-drama

# 原视频无字幕，关闭擦除
python scripts/mps_narrate.py --url https://example.com/drama.mp4 --scene short-drama-no-erase

# 短剧三集合并解说，输出3个不同版本
python scripts/mps_narrate.py \
    --url https://example.com/ep01.mp4 \
    --extra-urls https://example.com/ep02.mp4 https://example.com/ep03.mp4 \
    --scene short-drama \
    --output-count 3

# Dry Run（预览转义后的 ExtendedParameter）
python scripts/mps_narrate.py --url https://example.com/drama.mp4 --scene short-drama --dry-run
```

**预设场景**：`short-drama`（短剧，含擦除） | `short-drama-no-erase`（短剧，无擦除）  
**主要参数**：`--url` / `--cos-object`（第一集，必填） / `--scene`（必填） / `--extra-urls`（第2集起） / `--output-count`（输出数量，默认1，最大5） / `--no-wait` / `--dry-run`

### 精彩集锦 (`mps_highlight.py`)

使用 MPS 智能分析功能，通过 AI 算法自动捕捉并生成视频中的精彩片段（高光集锦）。固定使用 26 号预设模板，支持 VLOG、短剧、足球赛事、篮球赛事等多种场景。

```bash
# 足球赛事精彩集锦
python scripts/mps_highlight.py --cos-object /input/football.mp4 --scene football

# 短剧影视高光
python scripts/mps_highlight.py --cos-object /input/drama.mp4 --scene short-drama

# VLOG 全景相机
python scripts/mps_highlight.py --url https://example.com/vlog.mp4 --scene vlog-panorama

# 自定义场景（大模型版）
python scripts/mps_highlight.py --url https://example.com/skiing.mp4 \
    --scene custom --prompt "滑雪场景，输出人物高光" --scenario "滑雪"

# 篮球赛事
python scripts/mps_highlight.py --cos-object /input/basketball.mp4 --scene basketball

# 指定输出片段数（仅 vlog/vlog-panorama/custom 支持）
python scripts/mps_highlight.py --cos-object /input/vlog.mp4 --scene vlog --top-clip 10

# Dry Run（仅打印请求参数）
python scripts/mps_highlight.py --cos-object /input/game.mp4 --scene football --dry-run
```

**预设场景**：
- `vlog`：VLOG、风景、无人机视频（大模型版）
- `vlog-panorama`：全景相机（开启全景优化，大模型版）
- `short-drama`：短剧、影视剧，提取主角出场/BGM高光（大模型版）
- `football`：足球赛事，识别射门/进球/红黄牌/回放（高级版）
- `basketball`：篮球赛事（高级版）
- `custom`：自定义场景，可传 `--prompt` 和 `--scenario`（大模型版）

**主要参数**：`--url` / `--cos-object`（必填） / `--scene`（必填） / `--prompt`（custom场景） / `--scenario`（custom场景） / `--top-clip`（vlog/vlog-panorama/custom场景可用） / `--no-wait` / `--dry-run`

⚠️ **重要限制**：
- 本脚本仅支持处理离线文件，不支持直播流
- `--top-clip` 仅允许在 `vlog` / `vlog-panorama` / `custom` 场景下使用
- `--prompt` 和 `--scenario` 仅在 `--scene custom` 时生效，但二者非必填
- ExtendedParameter 必须从预设场景参数中选择，禁止自行拼装

### 用量统计 (`mps_usage.py`)

```bash
python scripts/mps_usage.py --days 30 --all-types
python scripts/mps_usage.py --start 2026-01-01 --end 2026-01-31
python scripts/mps_usage.py --type Transcode Enhance AIGC AIAnalysis
```

`--type` 支持：`Transcode` `Enhance` `AIAnalysis` `AIRecognition` `AIReview` `Snapshot` `AnimatedGraphics` `AiQualityControl` `Evaluation` `ImageProcess` `AddBlindWatermark` `AddNagraWatermark` `ExtractBlindWatermark` `AIGC`

## API 参考

| 脚本 | 文档 |
|------|------|
| `mps_transcode.py` / `mps_enhance.py` / `mps_subtitle.py` / `mps_erase.py` | [ProcessMedia](https://cloud.tencent.com/document/api/862/37578) |
| `mps_qualitycontrol.py` | [ProcessMedia AiQualityControlTask](https://cloud.tencent.com/document/product/862/37578) |
| `mps_imageprocess.py` | [ProcessImage](https://cloud.tencent.com/document/api/862/112896) |
| `mps_av_understand.py` | [VideoComprehension AiAnalysisTask](https://cloud.tencent.com/document/product/862/126094) |
| `mps_vremake.py` | [VideoRemake AiAnalysisTask](https://cloud.tencent.com/document/product/862/124394) |
| `mps_narrate.py` | [ProcessMedia AiAnalysisTask](https://cloud.tencent.com/document/product/862/37578) |
| `mps_highlight.py` | [ProcessMedia AiAnalysisTask](https://cloud.tencent.com/document/product/862/37578) |
| `mps_aigc_image.py` | [CreateAigcImageTask](https://cloud.tencent.com/document/api/862/114562) |
| `mps_aigc_video.py` | [CreateAigcVideoTask](https://cloud.tencent.com/document/api/862/126965) |
| `mps_usage.py` | [DescribeUsageData](https://cloud.tencent.com/document/product/862/125919) |
| `mps_get_video_task.py` | [DescribeTaskDetail](https://cloud.tencent.com/document/api/862/37614) |
| `mps_get_image_task.py` | [DescribeImageTaskDetail](https://cloud.tencent.com/document/api/862/112897) |
