# 脚本参数说明

> 所有脚本均支持 `--help` 和 `--dry-run`（预览参数，不调用 API）。
> 完整用法示例见 [`scripts-detail.md`](scripts-detail.md)。

## 本地文件处理参数映射

当需要将本地文件上传到 COS 后执行处理时，使用以下参数：

| 脚本 | COS 路径参数 | 说明 |
|------|-------------|------|
| `mps_transcode.py` | `--cos-object <key>` | 使用环境变量中的 bucket/region |
| `mps_enhance.py` | `--cos-object <key>` | 使用环境变量中的 bucket/region |
| `mps_erase.py` | `--cos-object <key>` | 使用环境变量中的 bucket/region |
| `mps_subtitle.py` | `--cos-object <key>` | 使用环境变量中的 bucket/region |
| `mps_imageprocess.py` | `--cos-object <key>` | 使用环境变量中的 bucket/region |
| `mps_qualitycontrol.py` | `--cos-object <key>` | 使用环境变量中的 bucket/region |
| `mps_av_understand.py` | `--cos-object <key>` | 使用环境变量中的 bucket/region |
| `mps_vremake.py` | `--cos-object <key>` | 使用环境变量中的 bucket/region |
| `mps_narrate.py` | `--cos-object <key>` | 使用环境变量中的 bucket/region |
| `mps_aigc_image.py` | `--cos-input-bucket <b> --cos-input-region <r> --cos-input-key <k>` | 需完整 COS 信息 |
| `mps_aigc_video.py` | `--cos-input-bucket <b> --cos-input-region <r> --cos-input-key <k>` | 需完整 COS 信息 |

**重要规则**：
- 使用 `--cos-object` 的脚本依赖环境变量 `TENCENTCLOUD_COS_BUCKET` 和 `TENCENTCLOUD_COS_REGION`
- **禁止**使用拼接的 URL（如 `https://bucket.cos.region.myqcloud.com/key`）作为输入
- 本地上传的文件可能没有公开读取权限，必须使用 COS 路径方式

## 目录

- [通用参数（所有脚本）](#通用参数所有脚本)
- [音视频 / 图片处理类脚本通用参数](#音视频--图片处理类脚本通用参数)
- [AIGC 类脚本通用参数](#aigc-类脚本通用参数)
- [转码参数 mps_transcode.py](#转码参数-mps_transcodepy)
- [视频增强参数 mps_enhance.py](#视频增强参数-mps_enhancepy)
- [智能字幕参数 mps_subtitle.py](#智能字幕参数-mps_subtitlepy)
- [擦除/去水印参数 mps_erase.py](#擦除去水印参数-mps_erasepy)
- [图片处理参数 mps_imageprocess.py](#图片处理参数-mps_imageprocesspy)
- [查询音视频任务参数 mps_get_video_task.py](#查询音视频任务参数-mps_get_video_taskpy)
- [查询图片任务参数 mps_get_image_task.py](#查询图片任务参数-mps_get_image_taskpy)
- [AIGC 生图参数 mps_aigc_image.py](#aigc-生图参数-mps_aigc_imagepy)
- [AIGC 生视频参数 mps_aigc_video.py](#aigc-生视频参数-mps_aigc_videopy)
- [COS 文件上传参数 mps_cos_upload.py](#cos-文件上传参数-mps_cos_uploadpy)
- [COS 文件下载参数 mps_cos_download.py](#cos-文件下载参数-mps_cos_downloadpy)
- [COS 文件列表参数 mps_cos_list.py](#cos-文件列表参数-mps_cos_listpy)
- [大模型音视频理解参数 mps_av_understand.py](#大模型音视频理解参数-mps_av_understandpy)
- [视频去重参数 mps_vremake.py](#视频去重参数-mps_vremakepy)
- [AI 解说二创参数 mps_narrate.py](#ai-解说二创参数-mps_narratepy)
- [媒体质检参数 mps_qualitycontrol.py](#媒体质检参数-mps_qualitycontrolpy)
- [用量统计参数 mps_usage.py](#用量统计参数-mps_usagepy)

---

## 通用参数（所有脚本）

| 参数 | 说明 |
|------|------|
| `--help` | 显示完整的帮助文档 |
| `--dry-run` | 仅打印请求参数，不实际调用 API |
| `--region` | 腾讯云区域，默认 `ap-guangzhou` |

## 音视频 / 图片处理类脚本通用参数

适用脚本：`mps_transcode.py`、`mps_enhance.py`、`mps_subtitle.py`、`mps_erase.py`、`mps_imageprocess.py`

| 参数 | 说明 |
|------|------|
| `--url` | 输入文件的 URL 地址 |
| `--cos-object` | COS 输入对象路径（使用环境变量中的 Bucket） |
| `--cos-bucket` | 指定输入 COS Bucket（覆盖环境变量） |
| `--cos-region` | 指定输入 COS 区域 |
| `--output-bucket` | 输出 COS Bucket |
| `--output-region` | 输出 COS Bucket 区域（默认取环境变量） |
| `--output-dir` | 输出目录，各脚本默认值不同：<br>- `mps_transcode.py`: `/output/transcode/`<br>- `mps_enhance.py`: `/output/enhance/`<br>- `mps_erase.py`: `/output/erase/`<br>- `mps_subtitle.py`: `/output/subtitle/`<br>- `mps_imageprocess.py`: `/output/image/` |
| `--output-object-path` | 输出文件路径模板，如 `/output/{inputName}_transcode.{format}`（适用：`mps_transcode.py`、`mps_enhance.py`、`mps_subtitle.py`、`mps_erase.py`） |
| `--output-path` | 输出文件路径模板（仅适用：`mps_imageprocess.py`） |
| `--notify-url` | 任务完成回调 URL（**仅适用音视频脚本**：`mps_transcode.py`、`mps_enhance.py`、`mps_subtitle.py`、`mps_erase.py`；**不适用** `mps_imageprocess.py`） |
| `--no-wait` | 仅提交任务，不等待结果（返回 TaskId 后退出） |
| `--poll-interval` | 轮询间隔（秒），音视频类默认 `10`，图片处理默认 `5` |
| `--max-wait` | 最长等待时间（秒），音视频类默认 `1800`（30分钟），图片处理默认 `300` |

## AIGC 类脚本通用参数

适用脚本：`mps_aigc_image.py`、`mps_aigc_video.py`

| 参数 | 说明 |
|------|------|
| `--no-wait` | 仅提交任务，不等待结果 |
| `--task-id` | 查询已有任务的结果 |
| `--poll-interval` | 轮询间隔（秒），生图默认 5，生视频默认 10 |
| `--max-wait` | 最长等待时间（秒），生图默认 300，生视频默认 1800 |
| `--cos-bucket-name` | 结果存储 COS Bucket（可选，不配置则使用 MPS 临时存储 12 小时） |
| `--cos-bucket-region` | 结果存储 COS 区域 |
| `--cos-bucket-path` | 结果存储 COS 路径前缀，各脚本默认值不同：<br>- `mps_aigc_image.py`: `/output/aigc-image/`<br>- `mps_aigc_video.py`: `/output/aigc-video/` |
| `--operator` | 操作者名称（可选） |

## 转码参数（mps_transcode.py）

| 参数 | 说明 |
|------|------|
| `--url` | 视频 URL 地址（HTTP/HTTPS）|
| `--cos-object` | COS 对象路径（需配置 `TENCENTCLOUD_COS_BUCKET`）|
| `--codec` | 编码格式：`h264` / `h265` / `h266` / `av1` / `vp9` |
| `--width` | 视频宽度/长边（px），如 1920、1280 |
| `--height` | 视频高度/短边（px），0=按比例缩放 |
| `--bitrate` | 视频码率（kbps），0=自动 |
| `--fps` | 视频帧率（Hz），0=保持原始 |
| `--container` | 封装格式：`mp4` / `hls` / `flv` / `mp3` / `m4a` |
| `--audio-codec` | 音频编码：`aac` / `mp3` / `copy` |
| `--audio-bitrate` | 音频码率（kbps）|
| `--compress-type` | 压缩类型：`ultra_compress` / `standard_compress` / `high_compress` / `low_compress` |
| `--scene-type` | 场景类型：`normal` / `pgc` / `ugc` / `e-commerce_video` / `educational_video` / `materials_video` 等 |
| `--region` | MPS 服务区域（默认 `ap-guangzhou`）|
| `--notify-url` | 任务完成回调 URL |
| `--dry-run` | 只打印参数，不调用 API |

## 视频增强参数（mps_enhance.py）

> **两种使用模式**：
> 1. **模板模式**（推荐）：使用 `--template` 参数指定大模型增强模板 ID（327001-327020），快速应用预设增强效果
> 2. **自定义参数模式**：通过 `--preset`、`--diffusion-type` 等参数自定义增强配置
>
> **注意**：两种模式互斥，使用 `--template` 时其他增强参数将被忽略。

| 参数 | 说明 |
|------|------|
| `--url` | 视频 URL 地址 |
| `--cos-object` | COS 对象路径 |
| `--template` | **大模型增强模板 ID**（模板模式）：`327001`-`327020`，对应不同场景（真人/漫剧/抖动优化/细节最强/人脸保真，720P至4K）|
| `--preset` | 大模型增强预设（自定义模式）：`diffusion`（扩散模型） / `comprehensive`（综合） / `artifact`（去伪影）|
| `--diffusion-type` | 扩散增强强度（自定义模式）：`weak` / `normal` / `strong` |
| `--comprehensive-type` | 综合增强强度（自定义模式）：`weak` / `normal` / `strong` |
| `--artifact-type` | 去伪影强度（自定义模式）：`weak` / `strong` |
| `--scene-type` | 增强场景：`common` / `AIGC` / `short_play` / `short_video` / `game` / `HD_movie_series` / `LQ_material` / `lecture` |
| `--super-resolution` | 开启超分辨率（2倍，不可与大模型增强同时使用）|
| `--sr-type` | 超分类型：`lq`（低清有噪，默认）/ `hq`（高清）|
| `--sr-size` | 超分倍数，目前仅支持 `2` |
| `--denoise` | 开启视频降噪（不可与大模型增强同时使用）|
| `--denoise-type` | 降噪强度：`weak`（默认）/ `strong` |
| `--color-enhance` | 开启色彩增强 |
| `--color-enhance-type` | 色彩增强强度：`weak`（默认）/ `normal` / `strong` |
| `--low-light-enhance` | 开启低光照增强 |
| `--scratch-repair` | 划痕修复强度（浮点数 0.0 至 1.0，如 `0.5`、`0.8`），适合老片修复 |
| `--hdr` | 开启 HDR 增强，可选 `HDR10` / `HLG`（需 h264/h265 编码，编码位深 10）|
| `--frame-rate` | 开启插帧，目标帧率（Hz），如 `60`。源帧率≥目标帧率时不生效 |
| `--audio-denoise` | 开启音频降噪 |
| `--audio-separate` | 音频分离：`vocal`（提取人声）、`background`（提取背景声）、`accompaniment`（提取伴奏） |
| `--volume-balance` | 开启音量均衡 |
| `--volume-balance-type` | 音量均衡类型：`loudNorm`（响度标准化，默认）/ `gainControl`（减小突变）|
| `--audio-beautify` | 开启音频美化（杂音去除 + 齿音压制）|
| `--codec` | 输出视频编码：`h264` / `h265`（默认）/ `h266` / `av1` / `vp9` |
| `--width` | 输出视频宽度/长边（像素），如 `1920` |
| `--height` | 输出视频高度/短边（像素），`0` 表示按比例缩放 |
| `--bitrate` | 输出视频码率（kbps），`0` 表示自动 |
| `--fps` | 输出视频帧率（Hz），`0` 表示保持原始 |
| `--container` | 输出封装格式：`mp4`（默认）/ `hls` / `flv` |
| `--audio-codec` | 输出音频编码：`aac`（默认）/ `mp3` / `copy` |
| `--audio-bitrate` | 输出音频码率（kbps），默认 `128` |
| `--region` | MPS 服务区域（默认 `ap-guangzhou`）|
| `--dry-run` | 只打印参数，不调用 API |

**模板 ID 速查表**：

| 模板 ID | 适用场景 | 720P | 1080P | 2K | 4K |
|---------|---------|------|-------|----|----|
| 真人（Real，人脸与文字区域保护） | — | 327001 | 327003 | 327005 | 327007 |
| 漫剧（Anime，动漫线条色块增强） | — | 327002 | 327004 | 327006 | 327008 |
| 抖动优化（JitterOpt，减少帧间抖动） | — | 327009 | 327010 | 327011 | 327012 |
| 细节最强（DetailMax，最大化纹理细节） | — | 327013 | 327014 | 327015 | 327016 |
| 人脸保真（FaceFidelity，保留人脸五官） | — | 327017 | 327018 | 327019 | 327020 |

## 智能字幕参数（mps_subtitle.py）

| 参数 | 说明 |
|------|------|
| `--url` | 视频 URL 地址 |
| `--cos-object` | COS 对象路径 |
| `--process-type` | 处理类型：`asr`（语音识别）/ `ocr`（画面文字识别）/ `translate`（翻译）|
| `--src-lang` | 视频源语言：**ASR 模式**：`zh`（简体中文）、`en`（英语）、`ja`（日语）、`ko`（韩语）、`zh-PY`（中英粤）、`yue`（粤语）、`zh_dialect`（中文方言）、`prime_zh`（中英方言）、`vi`（越南语）、`ms`（马来语）、`id`（印尼语）、`th`（泰语）、`fr`（法语）、`de`（德语）、`es`（西班牙语）、`pt`（葡萄牙语）、`ru`（俄语）、`ar`（阿拉伯语）等；**OCR 模式**：`zh_en`（中英，默认）、`multi`（多语种） |
| `--subtitle-type` | 字幕类型：`0`=源语言、`1`=翻译语言、`2`=双语（有翻译时默认） |
| `--subtitle-format` | 字幕格式：`vtt` / `srt` / `original` |
| `--translate` | 翻译目标语言，支持多语言用 `/` 分隔，如 `en/ja`。支持：`zh`（中文）、`en`（英语）、`ja`（日语）、`ko`（韩语）、`fr`（法语）、`es`（西班牙语）、`de`（德语）、`it`（意大利语）、`ru`（俄语）、`pt`（葡萄牙语）、`ar`（阿拉伯语）、`th`（泰语）、`vi`（越南语）、`id`（印尼语）、`ms`（马来语）、`tr`（土耳其语）、`nl`（荷兰语）、`pl`（波兰语）、`sv`（瑞典语）等 30+ 种语言 |
| `--hotwords-id` | ASR 热词库 ID，提高专业术语识别准确率，如 `hwd-xxxxx` |
| `--ocr-area` | OCR 识别区域（百分比坐标 0 至 1），格式 `x1,y1,x2,y2`，可多次指定 |
| `--sample-width` | 示例视频/图片的宽度（像素），配合 `--ocr-area` 使用，帮助 OCR 精确定位区域 |
| `--sample-height` | 示例视频/图片的高度（像素），配合 `--ocr-area` 使用 |
| `--template` | 智能字幕预设模板 ID（如 `110167`）|
| `--user-ext-para` | 用户扩展字段，一般场景不用填 |
| `--ext-info` | 自定义扩展参数（JSON 字符串） |
| `--region` | MPS 服务区域（默认 `ap-guangzhou`）|
| `--dry-run` | 只打印参数，不调用 API |

## 擦除/去水印参数（mps_erase.py）

> 职责：**擦除/遮挡画面中的视觉元素**（字幕、水印、人脸、车牌等），不涉及画面质量检测。

| 参数 | 说明 |
|------|------|
| `--url` | 视频 URL 地址 |
| `--cos-object` | COS 对象路径 |
| `--template` | 模板 ID（优先级高于自定义参数）|
| `--method` | 擦除方式：`auto`（自动）/ `custom`（自定义区域）|
| `--model` | 擦除模型：`standard`（标准）/ `area`（区域）|
| `--position` | 预设位置：`fullscreen`（全屏幕）、`top-half`（上半屏幕）、`bottom-half`（下半屏幕）、`center`（屏幕中间）、`left`（屏幕左边）、`right`（屏幕右边），共 6 种；不传则默认识别视频**中下部**区域 |
| `--area` | 自动擦除区域（百分比坐标 `X1,Y1,X2,Y2`，0~1）|
| `--custom-area` | 自定义区域（`BEGIN,END,X1,Y1,X2,Y2`）|
| `--ocr` | 开启 OCR 字幕提取（自动识别字幕区域文字）|
| `--subtitle-lang` | 字幕语言：`zh_en`（中英，默认）、`multi`（多语种） |
| `--subtitle-format` | 字幕文件格式：`vtt`（默认）、`srt` |
| `--translate` | 字幕翻译目标语言（**必须同时开启 `--ocr`**）。支持：`zh`（中文）、`en`（英语）、`ja`（日语）、`ko`（韩语）、`fr`（法语）、`es`（西班牙语）、`it`（意大利语）、`de`（德语）、`tr`（土耳其语）、`ru`（俄语）、`pt`（葡萄牙语）、`vi`（越南语）、`id`（印尼语）、`ms`（马来语）、`th`（泰语）、`ar`（阿拉伯语）、`hi`（印地语），共 17 种 |
| `--region` | MPS 服务区域（默认 `ap-guangzhou`）|
| `--dry-run` | 只打印参数，不调用 API |

## 图片处理参数（mps_imageprocess.py）

| 参数 | 说明 |
|------|------|
| `--url` | 图片 URL 地址 |
| `--cos-object` | COS 对象路径 |
| `--format` | 输出格式：`JPEG` / `PNG` / `BMP` / `WebP` |
| `--quality` | 图片质量 [1-100] |
| `--super-resolution` | 启用超分辨率（2 倍） |
| `--sr-type` | 超分类型：`lq`（低清晰度有噪声，默认）、`hq`（高清晰度） |
| `--advanced-sr` | 启用高级超分 |
| `--adv-sr-type` | 高级超分类型：`standard`（通用，默认）、`super`（高级super）、`ultra`（高级ultra） |
| `--sr-mode` | 高级超分输出模式：`percent`（倍率）、`aspect`（等比，默认）、`fixed`（固定） |
| `--sr-percent` | 高级超分倍率（配合 `--sr-mode percent`，如 `3.0`） |
| `--sr-width` / `--sr-height` | 高级超分目标宽/高（不超过 4096） |
| `--sr-long-side` | 高级超分目标长边（不超过 4096） |
| `--sr-short-side` | 高级超分目标短边（不超过 4096） |
| `--denoise` | 降噪强度：`weak`（轻度）、`strong`（强力） |
| `--quality-enhance` | 综合增强强度：`weak`（轻度）、`normal`（中度）、`strong`（强力） |
| `--color-enhance` | 色彩增强：`weak`、`normal`、`strong` |
| `--sharp-enhance` | 细节增强（0.0 至 1.0） |
| `--face-enhance` | 人脸增强强度（0.0 至 1.0） |
| `--lowlight-enhance` | 启用低光照增强 |
| `--beauty` | 美颜效果，格式 `类型:强度`（强度 0 至 100），可多次指定。口红可附加颜色值：`FaceFeatureLipsLut:50:#ff0000`。类型：`Whiten`（美白）、`BlackAlpha1`（美黑）、`BlackAlpha2`（较强美黑）、`FoundationAlpha2`（粉白）、`Clear`（清晰度）、`Sharpen`（锐化）、`Smooth`（磨皮）、`BeautyThinFace`（瘦脸）、`NatureFace`（自然脸型）、`VFace`（V脸）、`EnlargeEye`（大眼）、`EyeLighten`（亮眼）、`RemoveEyeBags`（祛眼袋）、`ThinNose`（瘦鼻）、`RemoveLawLine`（祛法令纹）、`CheekboneThin`（瘦颧骨）、`FaceFeatureLipsLut`（口红）、`ToothWhiten`（牙齿美白）、`FaceFeatureSoftlight`（柔光）、`Makeup`（美妆），共 20 种 |
| `--filter` | 滤镜效果，格式 `类型:强度`，如 `Qingjiaopian:70`。类型：`Dongjing`（东京）、`Qingjiaopian`（轻胶片）、`Meiwei`（美味） |
| `--erase-detect` | 自动擦除类型（可多选）：`logo`（图标）、`text`（文字）、`watermark`（水印） |
| `--erase-area` | 指定擦除区域（像素坐标），格式 `x1,y1,x2,y2`，可多次指定 |
| `--erase-box` | 指定擦除区域（百分比坐标 0 至 1），格式 `x1,y1,x2,y2`，可多次指定 |
| `--erase-area-type` | 指定区域擦除的类型：`logo`（图标，默认）、`text`（文字） |
| `--add-watermark` | 添加盲水印，指定水印文字（最多 4 字节，约 1 个中文字或 4 个 ASCII 字符，超出会被截断） |
| `--extract-watermark` | 提取盲水印 |
| `--remove-watermark` | 移除盲水印 |
| `--resize-percent` | 百分比缩放倍率（如 `2.0` 表示放大 2 倍） |
| `--resize-mode` | 缩放模式：`percent`、`mfit`、`lfit`、`fill`、`pad`、`fixed` |
| `--resize-width` / `--resize-height` | 目标宽/高（像素） |
| `--resize-long-side` | 目标长边（像素），未指定宽高时使用 |
| `--resize-short-side` | 目标短边（像素），未指定宽高时使用 |
| `--definition` | 图片处理模板 ID（使用预设模板时指定） |
| `--schedule-id` | 编排场景 ID：`30000`（文字水印擦除）、`30010`（图片扩展）、`30100`（换装） |
| `--resource-id` | 资源 ID（默认为账号主资源 ID） |
| `--output-path` | 输出文件路径模板（如 `/output/{inputName}_processed.{format}`）|
| `--region` | MPS 服务区域（默认 `ap-guangzhou`）|
| `--dry-run` | 只打印参数，不调用 API |

## 查询音视频任务参数（mps_get_video_task.py）

> 适用于 `ProcessMedia` 提交的任务（TaskId 格式：`1234567890-WorkflowTask-xxxxxx`）

| 参数 | 说明 |
|------|------|
| `--task-id` | 任务 ID（必填）|
| `--verbose` / `-v` | 输出完整 JSON 响应（含所有子任务详情）|
| `--json` | 只输出原始 JSON，不打印格式化摘要 |
| `--region` | MPS 服务区域（默认 `ap-guangzhou`）|

## 查询图片任务参数（mps_get_image_task.py）

> 适用于 `ProcessImage` 提交的任务

| 参数 | 说明 |
|------|------|
| `--task-id` | 任务 ID（必填）|
| `--verbose` / `-v` | 输出完整 JSON 响应 |
| `--json` | 只输出原始 JSON |
| `--region` | MPS 服务区域（默认 `ap-guangzhou`）|

## AIGC 生图参数（mps_aigc_image.py）

| 参数 | 说明 |
|------|------|
| `--prompt` | 图片描述文本（最多 1000 字符，未传参考图时必填）|
| `--model` | 模型：`Hunyuan` / `GEM` / `Qwen` |
| `--model-version` | 模型版本，如 GEM `2.5` / `3.0` |
| `--negative-prompt` | 负向提示词 |
| `--enhance-prompt` | 开启提示词增强 |
| `--image-url` | 参考图 URL |
| `--image-ref-type` | 参考图类型：`asset`（内容参考）/ `style`（风格参考）|
| `--aspect-ratio` | 宽高比（如 `16:9`、`1:1`）|
| `--resolution` | 分辨率：`720P` / `1080P` / `2K` / `4K` |
| `--no-wait` | 只提交任务，不等待结果 |
| `--task-id` | 查询已有任务结果 |
| `--cos-bucket-name` | 结果存储 COS Bucket |
| `--cos-bucket-region` | 结果存储 COS 区域 |
| `--cos-bucket-path` | 结果存储 COS 路径前缀，各脚本默认值不同：<br>- `mps_aigc_image.py`: `/output/aigc-image/`<br>- `mps_aigc_video.py`: `/output/aigc-video/` |
| `--operator` | 操作者名称（可选） |
| `--poll-interval` | 轮询间隔（秒），默认 5 |
| `--max-wait` | 最长等待时间（秒），默认 300 |
| `--region` | MPS 服务区域（默认 `ap-guangzhou`）|
| `--dry-run` | 只打印参数，不调用 API |

## AIGC 生视频参数（mps_aigc_video.py）

| 参数 | 说明 |
|------|------|
| `--prompt` | 视频描述文本（最多 2000 字符，未传图片时必填）|
| `--model` | 模型：`Hunyuan` / `Hailuo` / `Kling` / `Vidu` / `OS` / `GV` |
| `--model-version` | 模型版本，如 Kling `2.5`/`O1`，Hailuo `2.3`，Vidu `q2-pro` |
| `--scene-type` | 场景类型（部分模型支持）：`motion_control`（Kling 动作控制）、`land2port`（明眸横转竖）、`template_effect`（Vidu 特效模板） |
| `--multi-shot` | **Kling 专属**。启用分镜功能（单分镜模式：系统自动智能拆分；多分镜模式：需配合 `--multi-prompts-json` 自定义每个分镜） |
| `--multi-prompts-json` | **Kling 专属**。多分镜配置（JSON 数组格式）。每个分镜包含 `index`（序号）、`prompt`（提示词）、`duration`（时长）。示例：`'[{"index":1,"prompt":"分镜1描述","duration":"5"},...]'`。限制：分镜数量 1-6 个，每个提示词最长 512 字符，每个时长≥1秒，所有时长之和必须等于总时长 |
| `--negative-prompt` | 负向提示词 |
| `--enhance-prompt` | 开启提示词增强 |
| `--image-url` | 参考图（首帧）URL |
| `--last-image-url` | 参考图（尾帧）URL |
| `--duration` | 视频时长（秒）|
| `--resolution` | 分辨率：`720P` / `1080P` / `2K` / `4K` |
| `--aspect-ratio` | 宽高比 |
| `--no-logo` | 去除水印（Hailuo/Kling/Vidu 支持）|
| `--enable-bgm` | 启用背景音乐（部分模型版本支持）|
| `--enable-audio` | 是否为视频生成音频（GV/OS 支持，默认 `true`）|
| `--no-wait` | 只提交任务，不等待结果 |
| `--task-id` | 查询已有任务结果 |
| `--cos-bucket-name` | 结果存储 COS Bucket |
| `--cos-bucket-region` | 结果存储 COS 区域 |
| `--cos-bucket-path` | 结果存储 COS 路径前缀，各脚本默认值不同：<br>- `mps_aigc_image.py`: `/output/aigc-image/`<br>- `mps_aigc_video.py`: `/output/aigc-video/` |
| `--operator` | 操作者名称（可选） |
| `--poll-interval` | 轮询间隔（秒），默认 10 |
| `--max-wait` | 最长等待时间（秒），默认 1800 |
| `--ref-video-url` | 参考视频 URL（仅 Kling O1 支持）|
| `--ref-video-type` | 参考视频类型：`feature`（特征参考）、`base`（待编辑视频，默认）|
| `--keep-original-sound` | 保留原声：`yes`、`no` |
| `--off-peak` | 错峰模式（仅 Vidu），任务 48 小时内生成 |
| `--additional-params` | JSON 格式附加参数，用于传递模型专属扩展参数。如 Kling 的相机控制（**仅 Kling 支持**）：`'{"camera_control":{"type":"simple"}}'` |
| `--region` | MPS 服务区域（默认 `ap-guangzhou`）|
| `--dry-run` | 只打印参数，不调用 API |

### 分镜功能说明（Kling 专属）

Kling 模型支持分镜生成功能，可通过 `AdditionalParameters` 中的 `multi_shot`、`shot_type`、`multi_prompt` 参数控制。

#### 单分镜模式

用户输入一段文字，没有指明要求多个分镜或指明只要 1 个分镜时：

```bash
python mps_aigc_video.py --prompt "旅行日记，记录美好瞬间" --model Kling --multi-shot
```

参数配置：
- `multi_shot`: `true`
- `shot_type`: `intelligence`
- `multi_prompt`: 不填写（系统自动拆分）

#### 多分镜模式

用户需要明确定义每个分镜的信息：

```bash
python mps_aigc_video.py --model Kling --multi-shot --duration 12 \
    --multi-prompts-json '[
      {"index": 1, "prompt": "日出时分，从酒店窗户看城市天际线", "duration": "3"},
      {"index": 2, "prompt": "在咖啡馆享用早餐，窗外街道行人", "duration": "4"},
      {"index": 3, "prompt": "公园里散步，阳光透过树叶", "duration": "5"}
    ]'
```

参数配置：
- `multi_shot`: `true`
- `shot_type`: `intelligence`
- `multi_prompt`: 分镜数组，每个分镜包含：
  - `index`: 镜头号（整数）
  - `prompt`: 镜头提示词（字符串，最多 512 字符）
  - `duration`: 时间长度（字符串或数字，≥1 秒）

#### 校验规则

1. **分镜数量**：最多支持 6 个分镜，最小支持 1 个分镜
2. **提示词长度**：每个分镜相关内容的最大长度不超过 512 字符
3. **时长限制**：每个分镜的时长不大于当前任务的总时长，不小于 1 秒
4. **总时长匹配**：所有分镜的时长之和必须等于当前任务的总时长

## COS 文件上传参数（mps_cos_upload.py）

| 参数 | 说明 |
|------|------|
| `--local-file` / `-f` | 本地文件路径（必填） |
| `--cos-key` / `-k` | COS 对象键（Key），如 `input/video.mp4`（必填），**默认前缀使用 `input/`** |
| `--bucket` / `-b` | COS Bucket 名称（默认使用环境变量 `TENCENTCLOUD_COS_BUCKET`） |
| `--region` / `-r` | COS Bucket 区域（默认使用环境变量 `TENCENTCLOUD_COS_REGION` 或 `ap-guangzhou`） |
| `--secret-id` | 腾讯云 SecretId（默认使用环境变量 `TENCENTCLOUD_SECRET_ID`） |
| `--secret-key` | 腾讯云 SecretKey（默认使用环境变量 `TENCENTCLOUD_SECRET_KEY`） |
| `--verbose` / `-v` | 显示详细日志（文件大小、Bucket、Region、Key、ETag、URL 等） |

## COS 文件下载参数（mps_cos_download.py）

| 参数 | 说明 |
|------|------|
| `--cos-key` / `-k` | COS 对象键（Key），如 `output/result.mp4`（必填） |
| `--local-file` / `-f` | 本地保存路径（必填），建议保存到工作目录 `/data/workspace/` 下 |
| `--bucket` / `-b` | COS Bucket 名称（默认使用环境变量 `TENCENTCLOUD_COS_BUCKET`） |
| `--region` / `-r` | COS Bucket 区域（默认使用环境变量 `TENCENTCLOUD_COS_REGION` 或 `ap-guangzhou`） |
| `--secret-id` | 腾讯云 SecretId（默认使用环境变量 `TENCENTCLOUD_SECRET_ID`） |
| `--secret-key` | 腾讯云 SecretKey（默认使用环境变量 `TENCENTCLOUD_SECRET_KEY`） |
| `--verbose` / `-v` | 显示详细日志（Bucket、Region、Key、本地路径、文件大小、URL 等） |

## COS 文件列表参数（mps_cos_list.py）

| 参数 | 说明 |
|------|------|
| `--prefix` / `-p` | 路径前缀，用于过滤指定目录下的文件（如 `output/transcode/`），默认为空（根目录） |
| `--search` / `-s` | 文件名搜索关键字，支持模糊匹配（不区分大小写） |
| `--exact` | 精确匹配模式，只返回文件名完全匹配的文件 |
| `--limit` / `-l` | 最大返回文件数量（默认 1000，最大 1000） |
| `--bucket` / `-b` | COS Bucket 名称（默认使用环境变量 `TENCENTCLOUD_COS_BUCKET`） |
| `--region` / `-r` | COS Bucket 区域（默认使用环境变量 `TENCENTCLOUD_COS_REGION` 或 `ap-guangzhou`） |
| `--secret-id` | 腾讯云 SecretId（默认使用环境变量 `TENCENTCLOUD_SECRET_ID`） |
| `--secret-key` | 腾讯云 SecretKey（默认使用环境变量 `TENCENTCLOUD_SECRET_KEY`） |
| `--verbose` / `-v` | 显示详细日志（Bucket、Region、Prefix、搜索条件等） |
| `--show-url` | 显示文件完整 URL |

## 大模型音视频理解参数（mps_av_understand.py）

> **核心机制**：通过 `AiAnalysisTask` 的 `Definition=33`（预设视频理解模板）
> 和 `ExtendedParameter` 中的 `mvc.mode` + `mvc.prompt` 控制大模型理解行为。
>
> **`--mode` 和 `--prompt` 是最重要的参数**，强烈建议每次调用都明确填写。

| 参数 | 说明 |
|------|------|
| `--url` | 音视频 URL（HTTP/HTTPS），与 `--cos-object` / `--task-id` 互斥 |
| `--cos-object` | COS 对象路径（如 `input/video.mp4`），需配置 `TENCENTCLOUD_COS_BUCKET` |
| `--task-id` | 直接查询已有任务结果，跳过创建 |
| `--mode` | 理解模式：`video`（理解视频画面内容，默认）/ `audio`（仅处理音频，视频会自动提取音频）|
| `--prompt` | 大模型提示词，决定理解侧重点和输出格式（强烈建议填写，如"请对视频进行语音识别"）|
| `--extend-url` | 第二段对比音视频 URL（用于对比分析，最多 1 条）|
| `--definition` | AiAnalysisTask 模板 ID（默认 `33`，即预设视频理解模板）|
| `--no-wait` | 异步模式：只提交任务，不等待结果，打印 TaskId 后退出 |
| `--json` | 以 JSON 格式输出结果 |
| `--dry-run` | 只打印参数预览（含 ExtendedParameter 构建结果），不调用 API |
| `--output-dir` | 将结果 JSON 保存到指定目录 |
| `--region` | 处理地域，默认 `ap-guangzhou` |
| `--verbose` / `-v` | 显示详细日志信息 |

> **核心机制**：`AiAnalysisTask.Definition=29` + `ExtendedParameter(vremake.mode + 模式参数)`。
> 脚本**默认异步**（只提交任务返回 TaskId），加 `--wait` 才等待完成。

| 参数 | 说明 |
|------|------|
| `--url` | 视频 URL（HTTP/HTTPS），与 `--cos-object` / `--task-id` 互斥 |
| `--cos-object` | COS 对象路径，需配置 `TENCENTCLOUD_COS_BUCKET` |
| `--task-id` | 查询已有任务结果，跳过创建 |
| `--mode` | **必填**。去重模式：`PicInPic`（画中画）/ `BackgroundExtend`（视频扩展）/ `VerticalExtend`（垂直填充）/ `HorizontalExtend`（水平填充）/ `AB`（视频交错）/ `SwapFace`（换脸）/ `SwapCharacter`（换人）|
| `--wait` | 等待任务完成后退出（默认只提交，异步）|
| `--llm-prompt` | 大模型提示词（生成背景**图片**，适用 PicInPic/AB）|
| `--llm-video-prompt` | 大模型提示词（生成背景**视频**，优先于 `--llm-prompt`，适用 PicInPic/VerticalExtend/HorizontalExtend/AB）|
| `--min-scene-secs` | [BackgroundExtend] 插入扩展画面最小间隔（秒，默认 2.0）|
| `--random-move` | [PicInPic] 随机移动画中画位置 |
| `--random-cut` | 随机裁剪 |
| `--random-speed` | 随机加速 |
| `--random-flip` | 随机镜像（`true`/`false`，默认 `true`）|
| `--append-image` | [VerticalExtend/HorizontalExtend] 在视频开头/结尾插入图片（1.5秒）|
| `--append-image-prompt` | 开头/结尾图片生成提示词 |
| `--ext-mode` | [HorizontalExtend/AB] 扩展模式 `1`/`2`/`3`（效果依次增强，AB 模式：1=ABAB/2=BABA）|
| `--src-faces` | [SwapFace] 原视频人脸 URL 列表（支持多值，与 `--dst-faces` 一一对应，最多 6 张）|
| `--dst-faces` | [SwapFace] 目标人脸 URL 列表（支持多值，与 `--src-faces` 一一对应）|
| `--src-character` | [SwapCharacter] 原视频人物 URL（正面全身图）|
| `--dst-character` | [SwapCharacter] 目标人物 URL（正面全身图）|
| `--custom-json` | 自定义 vremake 扩展参数 JSON（与 `--mode` 自动合并）|
| `--definition` | AiAnalysisTask 模板 ID（默认 `29`，即视频去重模板）|
| `--json` | JSON 格式输出 |
| `--dry-run` | 只打印参数预览（含 ExtendedParameter），不调用 API |
| `--region` | 处理地域，默认 `ap-guangzhou` |

**SwapFace 限制**：视频分辨率 ≤ 4K；单张图片 < 10MB（jpg/png）；图片中有多个人脸时取最大；人脸总数 ≤ 6 张。  
**SwapCharacter 限制**：视频时长 ≤ 20 分钟；需正面全身图。

## AI 解说二创参数（mps_narrate.py）

> **核心机制**：`AiAnalysisTask.Definition=35` + `ExtendedParameter(reel.processType=narrate + 场景参数)`。
> 脚本**默认同步等待**任务完成，加 `--no-wait` 只提交任务返回 TaskId。

### 预设场景

| 场景值 | 说明 | 擦除设置 |
|--------|------|----------|
| `short-drama` | 短剧视频，画面上有字幕（默认） | 开启擦除 |
| `short-drama-no-erase` | 短剧视频，画面上没有字幕 | 关闭擦除 |

### 参数说明

| 参数 | 说明 |
|------|------|
| `--url` | 输入视频 URL（HTTP/HTTPS），第一集视频 |
| `--cos-object` | COS 对象路径（第一集视频），需配置 `TENCENTCLOUD_COS_BUCKET` |
| `--cos-input-bucket` | COS 输入 Bucket 名称（完整路径方式）|
| `--cos-input-region` | COS 输入 Bucket 区域 |
| `--cos-input-key` | COS 输入 Object Key |
| `--cos-bucket` | 指定输入 COS Bucket（覆盖环境变量，用于 `--cos-object`）|
| `--cos-region` | 指定输入 COS 区域（用于 `--cos-object`）|
| `--extra-urls` | 第2集及之后的视频 URL 列表（按顺序，分辨率须与第一集一致）|
| `--scene` | **必填**。预设场景：`short-drama` / `short-drama-no-erase` |
| `--output-count` | 输出视频数量，默认 1，最大 5（超过 5 将截断为 5）|
| `--output-bucket` | 输出 COS Bucket |
| `--output-region` | 输出 COS Region |
| `--output-dir` | 输出目录，默认 `/output/narrate/` |
| `--region` | MPS 服务区域，默认 `ap-guangzhou` |
| `--notify-url` | 任务完成回调 URL |
| `--no-wait` | 仅提交任务，不等待结果（返回 TaskId 后退出）|
| `--poll-interval` | 轮询间隔（秒），默认 10 |
| `--max-wait` | 最长等待时间（秒），默认 1800 |
| `--dry-run` | 只打印参数预览（含 ExtendedParameter），不调用 API |
| `--verbose` / `-v` | 输出详细信息 |

### ExtendedParameter 结构

脚本根据 `--scene` 自动构建 ExtendedParameter：

**short-drama（含擦除）**：
```json
{
  "reel": {
    "processType": "narrate",
    "narrateParam": {
      "onlyNarration": 1,
      "concatTransition": "flashwhite",
      "concatTransitionDuration": 0.3
    },
    "outputLanguage": "zh",
    "ttsParam": {
      "engine": "auto"
    },
    "outputVideoCount": 1
  }
}
```

**short-drama-no-erase（无擦除）**：
```json
{
  "reel": {
    "processType": "narrate",
    "narrateParam": {
      "onlyNarration": 1,
      "concatTransition": "flashwhite",
      "concatTransitionDuration": 0.3
    },
    "outputLanguage": "zh",
    "eraseParam": {
      "eraseOff": 1
    },
    "ttsParam": {
      "engine": "auto"
    },
    "outputVideoCount": 1
  }
}
```

### 注意事项

1. **不支持自定义脚本**：本次实现不支持输入自定义解说脚本（`scriptUrls`），仅支持由 MPS 自动生成解说脚本
2. **多集视频分辨率**：使用 `--extra-urls` 追加多集视频时，所有视频的分辨率须保持一致
3. **场景选择规则**：
   - 用户说"有字幕"/"带硬字幕"时 → 使用 `short-drama`
   - 用户说"没有字幕"/"原片无字幕"/"不擦除"时 → 使用 `short-drama-no-erase`

## 媒体质检参数（mps_qualitycontrol.py）

### 质检模板

| 模板 ID | 名称 | 适用场景 |
|---------|------|---------|
| `50` | Audio Detection | 音频质量/音频事件检测 |
| `60` | 格式质检-Pro版（**默认**） | 画面模糊、花屏、画面受损等内容问题 |
| `70` | 内容质检-Pro版 | 播放卡顿、播放异常、播放兼容性问题 |

### 参数说明

| 参数 | 说明 |
|------|------|
| `--url` | 视频 URL 地址 |
| `--cos-object` | COS 对象路径 |
| `--definition` | 质检模板 ID（默认 `60`）。`50`：音频质检；`60`：格式质检（画面模糊/花屏等）；`70`：内容质检（播放兼容性） |
| `--channel-ext-para` | 渠道扩展参数（JSON 字符串），一般场景不用填。如：`'{"OutputDir":"/test/output/"}'` |
| `--region` | MPS 服务区域（默认 `ap-guangzhou`）|
| `--no-wait` | 仅提交任务，不等待结果（返回 TaskId 后退出） |
| `--task-id` | 查询已有任务的结果 |
| `--json` | 以 JSON 格式输出结果 |
| `--dry-run` | 只打印参数，不调用 API |

## 用量统计参数（mps_usage.py）

| 参数 | 说明 |
|------|------|
| `--days` | 查询最近 N 天（默认 7 天，最大 90），与 `--start` 互斥 |
| `--start` | 开始日期，格式 `YYYY-MM-DD`（与 `--end` 配合使用）|
| `--end` | 结束日期，格式 `YYYY-MM-DD`（默认今天）|
| `--type` | 任务类型（可多选），默认 `Transcode`。可选值：`Transcode`（转码）/ `Enhance`（增强）/ `AIAnalysis`（智能分析）/ `AIRecognition`（智能识别）/ `AIReview`（内容审核）/ `Snapshot`（截图）/ `AnimatedGraphics`（转动图）/ `AiQualityControl`（质检）/ `Evaluation`（视频评测）/ `ImageProcess`（图片处理）/ `AddBlindWatermark`（数字水印）/ `AIGC`（生图/生视频）|
| `--all-types` | 查询所有任务类型（与 `--type` 互斥）|
| `--region` | MPS 服务区域（可多选），默认 `ap-guangzhou` |
| `--json` | 以 JSON 格式输出结果 |
| `--dry-run` | 仅打印请求参数，不实际调用 |

## 精彩集锦参数（mps_highlight.py）

> **核心机制**：`AiAnalysisTask.Definition=26`（智能分析模板）+ `ExtendedParameter(hht 场景参数)`。
> 脚本**默认同步等待**任务完成，加 `--no-wait` 只提交任务返回 TaskId。
> ⚠️ **重要限制**：仅支持离线文件，不支持直播流；ExtendedParameter 必须从预设场景参数中选择，禁止自行拼装。

### 预设场景

| 场景值 | 说明 | 计费版本 | 支持 --top-clip |
|--------|------|---------|----------------|
| `vlog` | VLOG、风景、无人机视频 | 大模型版 | ✅ |
| `vlog-panorama` | 全景相机（开启全景优化） | 大模型版 | ✅ |
| `short-drama` | 短剧、影视剧，提取主角出场/BGM高光 | 大模型版 | ❌ |
| `football` | 足球赛事，识别射门/进球/红黄牌/回放 | 高级版 | ❌ |
| `basketball` | 篮球赛事 | 高级版 | ❌ |
| `custom` | 自定义场景，可传 --prompt 和 --scenario | 大模型版 | ✅ |

### 参数说明

| 参数 | 说明 |
|------|------|
| `--url` | 输入视频 URL（HTTP/HTTPS） |
| `--cos-object` | COS 对象路径，需配置 `TENCENTCLOUD_COS_BUCKET` |
| `--cos-input-bucket` | COS 输入 Bucket 名称（完整路径方式）|
| `--cos-input-region` | COS 输入 Bucket 区域 |
| `--cos-input-key` | COS 输入 Object Key |
| `--cos-bucket` | 指定输入 COS Bucket（覆盖环境变量，用于 `--cos-object`）|
| `--cos-region` | 指定输入 COS 区域（用于 `--cos-object`）|
| `--scene` | **必填**。预设场景：`vlog` / `vlog-panorama` / `short-drama` / `football` / `basketball` / `custom` |
| `--prompt` | 自定义场景时使用，`multimodal_prompt` 内容，描述需要提取的高光内容（仅 `--scene custom` 生效）|
| `--scenario` | 自定义场景时使用，场景名称描述（仅 `--scene custom` 生效）|
| `--top-clip` | 最多输出集锦片段数（仅 `vlog` / `vlog-panorama` / `custom` 场景可用，默认 5）|
| `--output-bucket` | 输出 COS Bucket |
| `--output-region` | 输出 COS Region |
| `--output-dir` | 输出目录，默认 `/output/highlight/` |
| `--region` | MPS 服务区域，默认 `ap-guangzhou` |
| `--notify-url` | 任务完成回调 URL |
| `--no-wait` | 仅提交任务，不等待结果（返回 TaskId 后退出）|
| `--poll-interval` | 轮询间隔（秒），默认 10 |
| `--max-wait` | 最长等待时间（秒），默认 1800（30分钟，精彩集锦耗时较长）|
| `--dry-run` | 只打印参数预览（含 ExtendedParameter），不调用 API |
| `--verbose` / `-v` | 输出详细信息 |

### ExtendedParameter 结构

脚本根据 `--scene` 自动构建 ExtendedParameter，**禁止自行拼装或扩展字段**：

**vlog**：
```json
{
  "hht": {
    "top_clip": 5,
    "force_cls": 10020,
    "model_segment_limit": [3, 6]
  }
}
```

**vlog-panorama**：
```json
{
  "hht": {
    "top_clip": 5,
    "force_cls": 10020,
    "model_segment_limit": [3, 6],
    "use_panorama_direct": 1,
    "panorama_video": 1
  }
}
```

**short-drama**：
```json
{
  "hht": {
    "force_cls": "10010",
    "merge_type": 0,
    "need_vad": 1,
    "top_clip": 100,
    "res_save_type": 1,
    "scenario": "电视剧高光"
  }
}
```

**football**：
```json
{
  "hht": {
    "force_cls": "4001",
    "merge_type": 0,
    "need_vad": 1,
    "top_clip": 100,
    "res_save_type": 1
  }
}
```

**basketball**：
```json
{
  "hht": {
    "force_cls": "4002",
    "merge_type": 0,
    "need_vad": 1,
    "top_clip": 100,
    "res_save_type": 1
  }
}
```

**custom**（带 prompt 和 scenario）：
```json
{
  "hht": {
    "top_clip": 5,
    "force_cls": 10020,
    "prompts": {
      "multimodal_prompt": "滑雪场景，输出人物高光"
    },
    "scenario": "滑雪",
    "model_segment_limit": [3, 6]
  }
}
```
