# 脚本详细示例

## COS 输出路径约定

所有脚本在处理音视频/图片任务时，默认将输出文件存储到 COS 的特定目录下。各脚本的默认输出路径如下：

| 脚本 | 能力 | 默认输出路径 |
|------|------|-------------|
| `mps_transcode.py` | 极速高清转码 | `/output/transcode/` |
| `mps_enhance.py` | 视频增强 | `/output/enhance/` |
| `mps_erase.py` | 智能擦除 | `/output/erase/` |
| `mps_subtitle.py` | 智能字幕 | `/output/subtitle/` |
| `mps_imageprocess.py` | 图片处理 | `/output/image/` |
| `mps_aigc_image.py` | AIGC 生图 | `/output/aigc-image/` |
| `mps_aigc_video.py` | AIGC 生视频 | `/output/aigc-video/` |
| `mps_narrate.py` | AI 解说二创 | `/output/narrate/` |
| `mps_highlight.py` | 精彩集锦 | `/output/highlight/` |
| `mps_qualitycontrol.py` | 媒体质检 | `/output/quality_control/` |

> **说明**：
> - 所有默认路径均以 `/` 开头，表示绝对路径
> - 可通过 `--output-dir`（音视频/图片脚本）或 `--cos-bucket-path`（AIGC 脚本）参数自定义输出路径
> - 输出路径会自动拼接在 COS Bucket 后，如 `cos://bucket-name/output/transcode/`

---

## 1. 极速高清转码 — `mps_transcode.py`

```bash
# 最简用法：URL 输入 + 默认模板（100305，极速高清-H265-MP4-1080P）
python scripts/mps_transcode.py --url https://example.com/video.mp4

# COS 输入
python scripts/mps_transcode.py --cos-object /input/video/test.mp4

# 自定义参数：H265 编码 + 1080P + 3000kbps + 30fps
python scripts/mps_transcode.py --url https://example.com/video.mp4 \
    --codec h265 --width 1920 --height 1080 --bitrate 3000 --fps 30

# 极致压缩（ultra_compress）：最大程度压缩码率，适合带宽敏感场景
python scripts/mps_transcode.py --url https://example.com/video.mp4 --compress-type ultra_compress

# HLS 切片（用于流媒体播放）
python scripts/mps_transcode.py --url https://example.com/video.mp4 --container hls

# 综合最优（standard_compress）：平衡画质与码率，适合大多数场景
python scripts/mps_transcode.py --url https://example.com/video.mp4 --compress-type standard_compress

# 码率优先（high_compress）：在保证可接受画质的前提下尽量降低码率
python scripts/mps_transcode.py --url https://example.com/video.mp4 --compress-type high_compress

# 画质优先（low_compress）：在保证画质的前提下适度压缩，适合存档
python scripts/mps_transcode.py --url https://example.com/video.mp4 --compress-type low_compress

# 提交后查询任务状态（循环直到 FINISH）
python scripts/mps_get_video_task.py --task-id 1250017490-20260318152230-abcdef123456
```

## 2. 视频增强 — `mps_enhance.py`

```bash
# 默认增强（预设模板 321002）
python scripts/mps_enhance.py --url https://example.com/video.mp4

# ===== 大模型增强专用模板（327001 至 327020，推荐优先使用） =====

# 真人场景 - 升至 720P（适合真人实拍，保护人脸与文字区域）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --template 327001

# 真人场景 - 升至 1080P（推荐用于真人实拍视频）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --template 327003

# 真人场景 - 升至 2K
python scripts/mps_enhance.py --url https://example.com/video.mp4 --template 327005

# 真人场景 - 升至 4K（超高清修复）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --template 327007

# 漫剧场景 - 升至 720P（适合动漫风格，增强线条色块特征）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --template 327002

# 漫剧场景 - 升至 1080P
python scripts/mps_enhance.py --url https://example.com/video.mp4 --template 327004

# 漫剧场景 - 升至 2K
python scripts/mps_enhance.py --url https://example.com/video.mp4 --template 327006

# 漫剧场景 - 升至 4K（推荐用于动漫视频超清修复）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --template 327008

# 抖动优化 - 升至 1080P（减少帧间抖动与纹理跳变）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --template 327010

# 抖动优化 - 升至 4K
python scripts/mps_enhance.py --url https://example.com/video.mp4 --template 327012

# 细节最强 - 升至 1080P（最大化纹理细节还原）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --template 327014

# 细节最强 - 升至 4K（极致细节修复）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --template 327016

# 人脸保真 - 升至 720P（最大程度保留人脸五官细节）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --template 327017

# 人脸保真 - 升至 1080P（推荐用于人像/写真/访谈视频）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --template 327018

# 人脸保真 - 升至 2K（推荐用于高清人像修复）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --template 327019

# 人脸保真 - 升至 4K（超高清人脸修复）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --template 327020

# ===== 自定义参数模式（灵活组合增强能力） =====

# 大模型增强（效果最强）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --preset diffusion --diffusion-type strong

# 综合增强（平衡效果与效率）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --preset comprehensive --comprehensive-type normal

# 去毛刺/去伪影（针对压缩产生的伪影修复）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --preset artifact --artifact-type strong

# 超分 + 降噪 + 色彩增强（注意：--super-resolution 和 --denoise 不可与 --preset diffusion 同时使用）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --super-resolution --denoise --color-enhance

# HDR + 插帧 60fps
python scripts/mps_enhance.py --url https://example.com/video.mp4 --hdr HDR10 --frame-rate 60

# 音频分离：提取人声（去除背景音乐）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --audio-separate vocal

# 音频分离：提取背景声（去除人声）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --audio-separate background

# 音频分离：提取伴奏（去除人声，保留音乐）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --audio-separate accompaniment

# 音频增强：降噪 + 音量均衡 + 美化
python scripts/mps_enhance.py --url https://example.com/video.mp4 --audio-denoise --volume-balance --audio-beautify

# 输出编码控制：增强后输出为 H264 + 720P
python scripts/mps_enhance.py --url https://example.com/video.mp4 --preset comprehensive \
    --codec h264 --width 1280 --height 720

# 输出编码控制：增强后输出为 H265 + 1080P + 指定码率
python scripts/mps_enhance.py --url https://example.com/video.mp4 --super-resolution \
    --codec h265 --width 1920 --height 1080 --bitrate 4000

# 提交后查询任务状态（循环直到 FINISH）
python scripts/mps_get_video_task.py --task-id 1250017490-20260318152230-abcdef123456
```

## 3. 智能字幕 — `mps_subtitle.py`

```bash
# ASR 识别字幕（默认）
python scripts/mps_subtitle.py --url https://example.com/video.mp4

# ASR + 翻译为英文（双语字幕）
python scripts/mps_subtitle.py --url https://example.com/video.mp4 --src-lang zh --translate en

# OCR 识别硬字幕 + 翻译
python scripts/mps_subtitle.py --url https://example.com/video.mp4 --process-type ocr --src-lang zh_en --translate en

# 多语言翻译（英文+日文）
python scripts/mps_subtitle.py --url https://example.com/video.mp4 --src-lang zh --translate en/ja

# 提交后查询任务状态（循环直到 FINISH）
python scripts/mps_get_video_task.py --task-id 1250017490-20260318152230-abcdef123456
```

## 4. 智能去字幕与擦除 — `mps_erase.py`

```bash
# 自动擦除中下部字幕（默认模板 101）
python scripts/mps_erase.py --url https://example.com/video.mp4

# 去字幕并提取OCR字幕（模板 102）
python scripts/mps_erase.py --url https://example.com/video.mp4 --template 102

# 去水印-高级版（模板 201）
python scripts/mps_erase.py --url https://example.com/video.mp4 --template 201

# 人脸模糊（模板 301）
python scripts/mps_erase.py --url https://example.com/video.mp4 --template 301

# 人脸和车牌模糊（模板 302）
python scripts/mps_erase.py --url https://example.com/video.mp4 --template 302

# 强力擦除（区域模型，适合花体/阴影字幕）
python scripts/mps_erase.py --url https://example.com/video.mp4 --model area

# 使用区域预设 — 顶部字幕
python scripts/mps_erase.py --url https://example.com/video.mp4 --position top

# 使用区域预设 — 底部字幕
python scripts/mps_erase.py --url https://example.com/video.mp4 --position bottom

# 使用区域预设 — 右侧竖排字幕
python scripts/mps_erase.py --url https://example.com/video.mp4 --position right

# 使用区域预设 — 左下方字幕
python scripts/mps_erase.py --url https://example.com/video.mp4 --position bottom-left

# 使用区域预设 — 全屏幕
python scripts/mps_erase.py --url https://example.com/video.mp4 --position fullscreen

# 自定义区域（画面顶部0 至 25%区域）
python scripts/mps_erase.py --url https://example.com/video.mp4 --area 0,0,1,0.25

# 多区域擦除（顶部 + 底部都有字幕）
python scripts/mps_erase.py --url https://example.com/video.mp4 --area 0,0,1,0.15 --area 0,0.75,1,1

# 去字幕 + OCR 提取 + 翻译为英文
python scripts/mps_erase.py --url https://example.com/video.mp4 --ocr --translate en

# 去字幕 + OCR 提取 + 翻译为日文
python scripts/mps_erase.py --url https://example.com/video.mp4 --ocr --translate ja

# 提交后查询任务状态（循环直到 FINISH）
python scripts/mps_get_video_task.py --task-id 1250017490-20260318152230-abcdef123456
```

**区域预设（--position）说明**：

| 预设值 | 说明 | 坐标范围 |
|--------|------|----------|
| `fullscreen` | 全屏幕 | (0,0) 至 (0.9999,0.9999) |
| `top-half` | 上半屏幕 | (0,0) 至 (0.9999,0.5) |
| `bottom-half` | 下半屏幕 | (0,0.5) 至 (0.9999,0.9999) |
| `center` | 屏幕中间 | (0.1,0.3) 至 (0.9,0.7) |
| `left` | 屏幕左边 | (0,0) 至 (0.5,0.9999) |
| `right` | 屏幕右边 | (0.5,0) 至 (0.9999,0.9999) |
| `top` | 屏幕顶部 | (0,0) 至 (0.9999,0.25) |
| `bottom` | 屏幕底部 | (0,0.75) 至 (0.9999,0.9999) |
| `top-left` | 屏幕左上方 | (0,0) 至 (0.5,0.5) |
| `top-right` | 屏幕右上方 | (0.5,0) 至 (0.9999,0.5) |
| `bottom-left` | 屏幕左下方 | (0,0.5) 至 (0.5,0.9999) |
| `bottom-right` | 屏幕右下方 | (0.5,0.5) 至 (0.9999,0.9999) |

## 5. 图片处理 — `mps_imageprocess.py`

```bash
# 超分辨率 2 倍放大
python scripts/mps_imageprocess.py --url https://example.com/image.jpg --super-resolution

# 高级超分至 4K
python scripts/mps_imageprocess.py --url https://example.com/image.jpg --advanced-sr --sr-width 3840 --sr-height 2160

# 降噪 + 色彩增强 + 细节增强
python scripts/mps_imageprocess.py --url https://example.com/image.jpg \
    --denoise weak --color-enhance normal --sharp-enhance 0.8

# 综合增强（画质整体提升）
python scripts/mps_imageprocess.py --url https://example.com/image.jpg --quality-enhance normal

# 综合增强 + 超分（强力修复低质量图片）
python scripts/mps_imageprocess.py --url https://example.com/image.jpg --quality-enhance strong --super-resolution

# 美颜（美白 + 瘦脸 + 大眼）
python scripts/mps_imageprocess.py --url https://example.com/image.jpg \
    --beauty Whiten:50 --beauty BeautyThinFace:30 --beauty EnlargeEye:40

# 自动擦除水印
python scripts/mps_imageprocess.py --url https://example.com/image.jpg --erase-detect watermark

# 添加盲水印（水印文字最多 4 字节，约 1 个中文字或 4 个 ASCII 字符，超出会被截断）
python scripts/mps_imageprocess.py --url https://example.com/image.jpg --add-watermark "MPS"

# 转为 WebP 格式 + 质量 80
python scripts/mps_imageprocess.py --url https://example.com/image.jpg --format WebP --quality 80

# 滤镜（轻胶片风格，强度 70）
python scripts/mps_imageprocess.py --url https://example.com/image.jpg --filter Qingjiaopian:70

# 滤镜（东京风格）
python scripts/mps_imageprocess.py --url https://example.com/image.jpg --filter Dongjing:80

# 缩放（百分比放大 2 倍）
python scripts/mps_imageprocess.py --url https://example.com/image.jpg --resize-percent 2.0

# 缩放（等比缩放至宽 800 高 600 以内）
python scripts/mps_imageprocess.py --url https://example.com/image.jpg --resize-mode lfit --resize-width 800 --resize-height 600

# 缩放（指定长边为 1920，等比缩放）
python scripts/mps_imageprocess.py --url https://example.com/image.jpg --resize-long-side 1920

# 提交后查询任务状态（循环直到 FINISH）
python scripts/mps_get_image_task.py --task-id <TaskId>
```

## 6. 查询音视频处理任务 — `mps_get_video_task.py`

```bash
# 查询任务状态（简洁输出）
python scripts/mps_get_video_task.py --task-id 1234567890-WorkflowTask-80108cc3380155d98b2e3573a48a

# 详细输出（含子任务信息）
python scripts/mps_get_video_task.py --task-id 1234567890-WorkflowTask-80108cc3380155d98b2e3573a48a --verbose

# JSON 格式输出（便于程序解析）
python scripts/mps_get_video_task.py --task-id 1234567890-WorkflowTask-80108cc3380155d98b2e3573a48a --json

# 指定地域
python scripts/mps_get_video_task.py --task-id 1234567890-WorkflowTask-80108cc3380155d98b2e3573a48a --region ap-beijing
```

## 7. 查询图片处理任务 — `mps_get_image_task.py`

```bash
# 查询任务状态（简洁输出）
python scripts/mps_get_image_task.py --task-id 1234567890-ImageTask-80108cc3380155d98b2e3573a48a

# 详细输出（含子任务信息）
python scripts/mps_get_image_task.py --task-id 1234567890-ImageTask-80108cc3380155d98b2e3573a48a --verbose

# JSON 格式输出（便于程序解析）
python scripts/mps_get_image_task.py --task-id 1234567890-ImageTask-80108cc3380155d98b2e3573a48a --json

# 指定地域
python scripts/mps_get_image_task.py --task-id 1234567890-ImageTask-80108cc3380155d98b2e3573a48a --region ap-beijing
```

## 8. AIGC 智能生图 — `mps_aigc_image.py`

```bash
# 文生图（Hunyuan 默认）
python scripts/mps_aigc_image.py --prompt "一只可爱的橘猫在阳光下打盹"

# GEM 3.0 + 反向提示词 + 16:9 + 2K
python scripts/mps_aigc_image.py --prompt "赛博朋克城市夜景" --model GEM --model-version 3.0 \
    --negative-prompt "人物" --aspect-ratio 16:9 --resolution 2K

# 图生图（参考图片 + 描述）
python scripts/mps_aigc_image.py --prompt "将这张照片变成油画风格" \
    --image-url https://example.com/photo.jpg

# GEM 多图参考（最多3张，支持 asset/style 参考类型）
python scripts/mps_aigc_image.py --prompt "融合这些元素" --model GEM \
    --image-url https://example.com/img1.jpg --image-ref-type asset \
    --image-url https://example.com/img2.jpg --image-ref-type style

# 仅提交任务不等待
python scripts/mps_aigc_image.py --prompt "产品海报" --no-wait

# 查询任务结果
python scripts/mps_aigc_image.py --task-id <task-id>
```

## 9. AIGC 智能生视频 — `mps_aigc_video.py`

```bash
# 文生视频（Hunyuan 默认）
python scripts/mps_aigc_video.py --prompt "一只猫在阳光下伸懒腰"

# Kling 2.5 + 10秒 + 1080P + 16:9 + 去水印 + BGM
python scripts/mps_aigc_video.py --prompt "赛博朋克城市" --model Kling --model-version 2.5 \
    --duration 10 --resolution 1080P --aspect-ratio 16:9 --no-logo --enable-bgm

# 图生视频（首帧图片 + 描述）
python scripts/mps_aigc_video.py --prompt "让画面动起来" \
    --image-url https://example.com/photo.jpg

# 首尾帧生视频（GV 模型）
python scripts/mps_aigc_video.py --prompt "过渡动画" --model GV \
    --image-url https://example.com/start.jpg --last-image-url https://example.com/end.jpg

# GV 多图参考生视频（最多 3 张，支持 asset/style 参考类型）
python scripts/mps_aigc_video.py --prompt "融合风格生成视频" --model GV \
    --image-url https://example.com/img1.jpg --image-ref-type asset \
    --image-url https://example.com/img2.jpg --image-ref-type style

# Kling O1 参考视频 + 保留原声
python scripts/mps_aigc_video.py --prompt "将视频风格化" --model Kling --model-version O1 \
    --ref-video-url https://example.com/video.mp4 --ref-video-type base --keep-original-sound yes

# Vidu 错峰模式
python scripts/mps_aigc_video.py --prompt "自然风景" --model Vidu --off-peak

# 仅提交任务不等待
python scripts/mps_aigc_video.py --prompt "宣传片" --no-wait

# 查询任务结果
python scripts/mps_aigc_video.py --task-id <task-id>
```

## 10. COS 文件上传 — `mps_cos_upload.py`

```bash
# 最简用法：上传本地文件到 COS（使用环境变量中的 bucket）
python scripts/mps_cos_upload.py --local-file ./video.mp4 --cos-key input/video.mp4

# 显示详细日志（文件大小、Bucket、Region、Key、ETag、URL）
python scripts/mps_cos_upload.py --local-file ./video.mp4 --cos-key input/video.mp4 --verbose

# 指定 bucket 和 region（覆盖环境变量）
python scripts/mps_cos_upload.py --local-file ./video.mp4 --cos-key input/video.mp4 \
    --bucket mybucket-125xxx --region ap-guangzhou

# 上传图片文件
python scripts/mps_cos_upload.py --local-file ./photo.jpg --cos-key input/photo.jpg --verbose

# 使用自定义密钥（覆盖环境变量）
python scripts/mps_cos_upload.py --local-file ./video.mp4 --cos-key input/video.mp4 \
    --secret-id AKIDxxx --secret-key xxxxx

# 上传到自定义路径（非 input/ 前缀）
python scripts/mps_cos_upload.py --local-file ./my-video.mp4 --cos-key skills/tencent-mps_2.6.zip
```

## 11. COS 文件下载 — `mps_cos_download.py`

```bash
# 最简用法：下载文件到本地（使用环境变量中的 bucket）
python scripts/mps_cos_download.py --cos-key output/result.mp4 --local-file ./result.mp4

# 显示详细日志（Bucket、Region、Key、本地路径、文件大小、URL）
python scripts/mps_cos_download.py --cos-key output/result.mp4 --local-file ./result.mp4 --verbose

# 指定 bucket 和 region（覆盖环境变量）
python scripts/mps_cos_download.py --cos-key output/result.mp4 --local-file ./result.mp4 \
    --bucket mybucket-125xxx --region ap-guangzhou

# 下载到工作目录（推荐路径）
python scripts/mps_cos_download.py --cos-key output/enhanced.mp4 --local-file /data/workspace/enhanced.mp4 --verbose

# 下载图片处理结果
python scripts/mps_cos_download.py --cos-key output/photo-enhanced.jpg --local-file ./photo-enhanced.jpg

# 使用自定义密钥（覆盖环境变量）
python scripts/mps_cos_download.py --cos-key output/result.mp4 --local-file ./result.mp4 \
    --secret-id AKIDxxx --secret-key xxxxx
```

## 12. COS 文件列表 — `mps_cos_list.py`

```bash
# 列出 Bucket 根目录下的所有文件（使用环境变量中的 bucket）
python scripts/mps_cos_list.py

# 列出指定路径下的文件
python scripts/mps_cos_list.py --prefix output/transcode/

# 模糊搜索文件名包含 "video" 的文件
python scripts/mps_cos_list.py --prefix output/ --search video

# 精确匹配文件名 "result.mp4"
python scripts/mps_cos_list.py --prefix output/ --search "result.mp4" --exact

# 显示文件完整 URL
python scripts/mps_cos_list.py --prefix output/ --show-url

# 限制返回数量（最多 1000 个）
python scripts/mps_cos_list.py --prefix output/ --limit 50

# 显示详细日志
python scripts/mps_cos_list.py --prefix output/transcode/ --verbose

# 指定 bucket 和 region（覆盖环境变量）
python scripts/mps_cos_list.py --prefix input/ --bucket mybucket-125xxx --region ap-guangzhou

# 搜索转码输出目录中包含 "test" 的视频文件
python scripts/mps_cos_list.py --prefix /output/transcode/ --search test

# 列出增强后的结果文件并显示 URL
python scripts/mps_cos_list.py --prefix /output/enhance/ --show-url --limit 20
```

## 13. 大模型音视频理解 — `mps_av_understand.py`

> **核心机制**：通过 `AiAnalysisTask.Definition=33` + `ExtendedParameter` 中的 `mvc.mode` 和 `mvc.prompt` 控制理解行为。
> `--mode` 和 `--prompt` 是最重要的两个参数，强烈建议每次调用都明确填写。

```bash
# 基础：理解视频内容（--mode video + 提示词）
python scripts/mps_av_understand.py \
    --url https://example.com/video.mp4 \
    --mode video \
    --prompt "请分析这个视频的主要内容、场景和关键信息"

# 音频模式：语音识别（上传视频时自动提取音频）
python scripts/mps_av_understand.py \
    --url https://example.com/video.mp4 \
    --mode audio \
    --prompt "请对这段音频进行语音识别，输出完整文字内容"

# 纯音频文件
python scripts/mps_av_understand.py \
    --url https://example.com/audio.mp3 \
    --mode audio \
    --prompt "请识别这段音频的内容并输出文字"

# 对比分析（两段音视频，--extend-url 传第二段）
python scripts/mps_av_understand.py \
    --url https://example.com/standard.mp4 \
    --extend-url https://example.com/user.mp4 \
    --mode audio \
    --prompt "请对比这两段音频，分析演奏水平的差异，给出专业评价"

# COS 对象输入
python scripts/mps_av_understand.py \
    --cos-object input/my-video.mp4 \
    --mode video \
    --prompt "总结视频的核心内容"

# 异步模式：只提交任务，不等待结果
python scripts/mps_av_understand.py \
    --url https://example.com/video.mp4 \
    --mode video --prompt "分析视频内容" --no-wait

# 查询已有任务结果
python scripts/mps_av_understand.py --task-id 2600011633-WorkflowTask-80108cc3380155d98b2e3573a48a

# JSON 格式输出
python scripts/mps_av_understand.py \
    --url https://example.com/video.mp4 \
    --mode video --prompt "分析视频内容" --json

# dry-run 预览（含 ExtendedParameter 构建结果）
python scripts/mps_av_understand.py \
    --url https://example.com/video.mp4 \
    --mode audio --prompt "语音识别" --dry-run

# 将结果保存到本地目录
python scripts/mps_av_understand.py \
    --url https://example.com/video.mp4 \
    --mode video --prompt "分析内容" --output-dir /output/
```

## 14. 视频去重 — `mps_vremake.py`

> **核心机制**：通过 `AiAnalysisTask.Definition=29`（视频去重模板）+ `ExtendedParameter` 中的 `vremake.mode`
> 控制去重方式。脚本**默认异步**（只提交），加 `--wait` 才等待完成。

```bash
# 画中画去重（等待结果）
python scripts/mps_vremake.py \
    --url https://example.com/video.mp4 \
    --mode PicInPic \
    --wait

# 视频扩展去重（COS 输入）
python scripts/mps_vremake.py \
    --cos-object input/video.mp4 \
    --mode BackgroundExtend \
    --wait

# 画中画 + LLM 提示词（背景图片）
python scripts/mps_vremake.py \
    --url https://example.com/video.mp4 \
    --mode PicInPic \
    --llm-prompt "生成一个唯美的自然风景背景图片" \
    --wait

# 垂直填充 + LLM 提示词（背景视频）
python scripts/mps_vremake.py \
    --url https://example.com/video.mp4 \
    --mode VerticalExtend \
    --llm-video-prompt "随机生成一个自然风景视频" \
    --wait

# 换脸模式（--src-faces 和 --dst-faces 一一对应）
python scripts/mps_vremake.py \
    --url https://example.com/video.mp4 \
    --mode SwapFace \
    --src-faces https://example.com/src1.png https://example.com/src2.png \
    --dst-faces https://example.com/dst1.jpg https://example.com/dst2.jpg \
    --wait

# 换人模式（正面全身图）
python scripts/mps_vremake.py \
    --url https://example.com/video.mp4 \
    --mode SwapCharacter \
    --src-character https://example.com/src_fullbody.png \
    --dst-character https://example.com/dst_fullbody.png \
    --wait

# 水平填充 + extMode=2 + 随机镜像
python scripts/mps_vremake.py \
    --url https://example.com/video.mp4 \
    --mode HorizontalExtend \
    --ext-mode 2 \
    --wait

# 自定义 ExtendedParameter JSON 参数（与 --mode 合并）
python scripts/mps_vremake.py \
    --url https://example.com/video.mp4 \
    --mode PicInPic \
    --custom-json '{"vremake":{"picInPic":{"llmPrompt":"随机生成一张图片","randomMove":true}}}' \
    --wait

# 异步提交（默认，不加 --wait）
python scripts/mps_vremake.py \
    --url https://example.com/video.mp4 \
    --mode PicInPic

# 查询已有任务结果
python scripts/mps_vremake.py --task-id 2600011633-WorkflowTask-xxxxx

# JSON 格式输出
python scripts/mps_vremake.py \
    --url https://example.com/video.mp4 \
    --mode PicInPic --wait --json

# dry-run 预览（含 ExtendedParameter 构建结果）
python scripts/mps_vremake.py \
    --url https://example.com/video.mp4 \
    --mode BackgroundExtend --min-scene-secs 3.0 --dry-run
```

## 15. AI 解说二创 — `mps_narrate.py`

### 功能

调用 MPS `ProcessMedia` 接口的 `AiAnalysisTask`（固定使用 35 号预设模板），输入原始视频，一站式自动完成解说脚本生成、脚本匹配成片、AI 配音、去字幕等操作，输出带有解说文案、配音和字幕的新视频。

### 预设场景

| 场景值 | 说明 | 擦除设置 |
|--------|------|----------|
| `short-drama` | 短剧视频，画面上有字幕（默认） | 开启擦除 |
| `short-drama-no-erase` | 短剧视频，画面上没有字幕 | 关闭擦除 |

### 默认行为

- 解说模式：`onlyNarration=1`（纯解说视频）
- 转场效果：`flashwhite`，时长 0.3s
- 配音音色：使用 MPS 默认系统音色（`engine=auto`）
- 输出语言：`zh`（中文）
- 输出数量：默认 1 个，可通过 `--output-count` 指定，最大 5

### 示例命令

```bash
# 基础用法：短剧单集解说（默认含擦除）
python scripts/mps_narrate.py \
    --url https://example.com/drama.mp4 \
    --scene short-drama

# COS 对象输入
python scripts/mps_narrate.py \
    --cos-object /input/drama.mp4 \
    --scene short-drama

# 原视频无字幕，关闭擦除
python scripts/mps_narrate.py \
    --url https://example.com/drama.mp4 \
    --scene short-drama-no-erase

# 多集视频合并解说（第一集用 --url，后续集用 --extra-urls）
python scripts/mps_narrate.py \
    --url https://example.com/ep01.mp4 \
    --extra-urls https://example.com/ep02.mp4 https://example.com/ep03.mp4 \
    --scene short-drama

# 输出 3 个不同版本的视频
python scripts/mps_narrate.py \
    --url https://example.com/drama.mp4 \
    --scene short-drama \
    --output-count 3

# 自定义输出目录
python scripts/mps_narrate.py \
    --url https://example.com/drama.mp4 \
    --scene short-drama \
    --output-dir /custom/narrate/

# 异步提交（不等待结果）
python scripts/mps_narrate.py \
    --url https://example.com/drama.mp4 \
    --scene short-drama \
    --no-wait

# Dry Run（预览转义后的 ExtendedParameter）
python scripts/mps_narrate.py \
    --url https://example.com/drama.mp4 \
    --scene short-drama \
    --dry-run

# 查询任务状态
python scripts/mps_get_video_task.py --task-id 2600011633-WorkflowTask-xxxxx
```

### 注意事项

1. **不支持自定义脚本**：本次实现不支持输入自定义解说脚本（`scriptUrls`），仅支持由 MPS 自动生成解说脚本
2. **多集视频分辨率**：使用 `--extra-urls` 追加多集视频时，所有视频的分辨率须保持一致
3. **场景选择规则**：
   - 用户说"有字幕"/"带硬字幕"时 → 使用 `short-drama`
   - 用户说"没有字幕"/"原片无字幕"/"不擦除"时 → 使用 `short-drama-no-erase`

## 16. 媒体质检 — `mps_qualitycontrol.py`

### 功能

调用 MPS `ProcessMedia` 接口的 `AiQualityControlTask`，对音视频进行自动化质量检测。
支持 URL 或 COS 对象输入，同步等待结果或异步提交后查询。

### 质检模板

| 模板 ID | 名称 | 适用场景 |
|---------|------|---------|
| `50` | Audio Detection | 音频质量/音频事件检测 |
| `60` | 格式质检-Pro版（**默认**） | 画面模糊、花屏、画面受损等内容问题 |
| `70` | 内容质检-Pro版 | 播放卡顿、播放异常、播放兼容性问题 |

### 示例命令

```bash
# 基础：格式质检（默认模板 60）
python scripts/mps_qualitycontrol.py --url https://example.com/video.mp4

# 指定内容质检模板（播放问题）
python scripts/mps_qualitycontrol.py --url https://example.com/video.mp4 --definition 70

# 音频质检
python scripts/mps_qualitycontrol.py --url https://example.com/audio.mp3 --definition 50

# COS 输入
python scripts/mps_qualitycontrol.py --cos-object input/video.mp4

# 异步提交
python scripts/mps_qualitycontrol.py --url https://example.com/video.mp4 --no-wait

# 查询已有任务结果
python scripts/mps_qualitycontrol.py --task-id 2600011633-WorkflowTask-xxxxx --json

# dry-run
python scripts/mps_qualitycontrol.py --url https://example.com/video.mp4 --definition 70 --dry-run
```

## 17. 用量统计查询 — `mps_usage.py`

```bash
# 查询最近 7 天用量（默认）
python scripts/mps_usage.py

# 查询最近 30 天所有类型
python scripts/mps_usage.py --days 30 --all-types

# 查询指定日期范围（注意：参数名是 --start / --end，不是 --start-date / --end-date）
python scripts/mps_usage.py --start 2026-01-01 --end 2026-01-31

# 查询多个任务类型
python scripts/mps_usage.py --type Transcode Enhance AIGC

# 查询大模型音视频理解用量（AvUnderstand 属于 AIAnalysis 类型，不是独立类型）
python scripts/mps_usage.py --days 30 --type AIAnalysis

# 查询数字水印相关用量
python scripts/mps_usage.py --type AddBlindWatermark AddNagraWatermark ExtractBlindWatermark

# 查询多地域用量
python scripts/mps_usage.py --region ap-guangzhou ap-hongkong

# JSON 格式输出（方便程序解析）
python scripts/mps_usage.py --days 7 --all-types --json

# dry-run 模式
python scripts/mps_usage.py --days 30 --all-types --dry-run
```

## 18. 精彩集锦 — `mps_highlight.py`

使用 MPS 智能分析功能，通过 AI 算法自动捕捉并生成视频中的精彩片段（高光集锦）。固定使用 26 号预设模板，支持 VLOG、短剧、足球赛事、篮球赛事等多种场景。

### 预设场景

| 场景 | 说明 | 计费版本 | 支持 --top-clip |
|------|------|---------|----------------|
| `vlog` | VLOG、风景、无人机视频 | 大模型版 | ✅ |
| `vlog-panorama` | 全景相机（开启全景优化） | 大模型版 | ✅ |
| `short-drama` | 短剧、影视剧，提取主角出场/BGM高光 | 大模型版 | ❌ |
| `football` | 足球赛事，识别射门/进球/红黄牌/回放 | 高级版 | ❌ |
| `basketball` | 篮球赛事 | 高级版 | ❌ |
| `custom` | 自定义场景，可传 --prompt 和 --scenario | 大模型版 | ✅ |

### 示例命令

```bash
# ========== 足球赛事精彩集锦 ==========
python scripts/mps_highlight.py --cos-object /input/football.mp4 --scene football

# URL 输入
python scripts/mps_highlight.py --url https://example.com/football.mp4 --scene football

# ========== 短剧影视高光 ==========
python scripts/mps_highlight.py --cos-object /input/drama.mp4 --scene short-drama

# ========== VLOG 全景相机 ==========
python scripts/mps_highlight.py --url https://example.com/vlog.mp4 --scene vlog-panorama

# 普通 VLOG
python scripts/mps_highlight.py --cos-object /input/vlog.mp4 --scene vlog

# 指定输出片段数（最多10个）
python scripts/mps_highlight.py --cos-object /input/vlog.mp4 --scene vlog --top-clip 10

# ========== 篮球赛事 ==========
python scripts/mps_highlight.py --cos-object /input/basketball.mp4 --scene basketball

# ========== 自定义场景（大模型版） ==========
# 带 prompt 和 scenario
python scripts/mps_highlight.py --url https://example.com/skiing.mp4 \
    --scene custom --prompt "滑雪场景，输出人物高光" --scenario "滑雪"

# 仅指定 scenario
python scripts/mps_highlight.py --url https://example.com/skiing.mp4 \
    --scene custom --scenario "滑雪"

# 仅指定 prompt
python scripts/mps_highlight.py --url https://example.com/skiing.mp4 \
    --scene custom --prompt "滑雪场景，输出人物高光"

# 自定义场景 + 指定片段数
python scripts/mps_highlight.py --url https://example.com/skiing.mp4 \
    --scene custom --prompt "滑雪场景" --scenario "滑雪" --top-clip 8

# ========== 其他常用选项 ==========
# 指定输出目录
python scripts/mps_highlight.py --cos-object /input/football.mp4 --scene football \
    --output-dir /output/my-highlights/

# 仅提交任务，不等待结果
python scripts/mps_highlight.py --cos-object /input/football.mp4 --scene football --no-wait

# Dry Run（预览请求参数）
python scripts/mps_highlight.py --cos-object /input/football.mp4 --scene football --dry-run

# 查询任务状态
python scripts/mps_get_video_task.py --task-id 2600011633-WorkflowTask-xxxxx
```

### 重要限制

- ⚠️ 本脚本**仅支持处理离线文件，不支持直播流**
- `--top-clip` 仅允许在 `vlog` / `vlog-panorama` / `custom` 场景下使用
- `--prompt` 和 `--scenario` 仅在 `--scene custom` 时生效，但二者非必填
- ExtendedParameter 必须从预设场景参数中选择，**禁止自行拼装**
