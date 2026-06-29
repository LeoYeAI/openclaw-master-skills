---
name: neodomain-ai
description: Generate images and videos via Neodomain AI API. Supports text-to-image, image-to-video, text-to-video, universal multi-modal video, motion control video, and batch storyboard video generation. Use when user wants to create AI-generated images or videos using the Neodomain platform.
metadata:
  {
    "openclaw":
      {
        "emoji": "🎨",
        "requires": { "bins": ["python3"], "env": ["NEODOMAIN_ACCESS_TOKEN"] },
        "primaryEnv": "NEODOMAIN_ACCESS_TOKEN",
      },
  }
---

# Neodomain AI Content Generator

## 核心行为规范

- **Token 检查**：每次执行前确认 `NEODOMAIN_ACCESS_TOKEN` 已设置。若未设置或遇到 token 过期错误（errCode 2001），立即走 [认证流程](#authentication)，动态询问用户手机号/邮箱，不要硬编码保存。
- **模型选择**：根据用户需求按 [模型选择逻辑](#model-selection-logic) 自主选择，无需询问用户（除非用户明确指定）。
- **提示词规范**：必须遵循各模式的提示词公式，尤其是 UNIVERSAL_TO_VIDEO 必须用 `@图片 1`/`@视频 1` 等明确引用素材。
- **输出目录**：默认使用 `./output`，若用户未指定则不需询问。
- **`--generate-audio`** 是布尔 flag，写 `--generate-audio` 即可，不要写 `--generate-audio true`。

---

## ⚠️ 常见问题与解决方案 (FAQ)

### 1. Token has been revoked (errCode 2001)

**现象**：视频生成 API 返回 `Token has been revoked`，但图片 API 可能正常。

**原因**：
- 企业版 token 的视频服务权限被撤销
- Token 已过期
- 服务端认证系统临时故障

**解决方案**：
1. 先用图片 API 测试 token 是否有效：`curl -H "accessToken: $TOKEN" https://story.neodomain.cn/agent/ai-image-generation/models`
2. 如果图片 API 正常但视频 API 失败 → 联系管理员确认视频服务权限
3. 如果全部失败 → 重新登录获取新 token（走认证流程）

### 2. 模型不支持某 generationType

**现象**：`❌ Failed: 模型 xxx 不支持 YYY 类型`

**原因**：不是所有模型都支持所有生成类型。

**解决方案**：
- `neo-video-2-0` / `neo-video-2-0-fast` → 仅支持 `UNIVERSAL_TO_VIDEO`
- `kling-video-o1` / `kling-v3-omni` → 仅支持 `UNIVERSAL_TO_VIDEO`
- `veo-3.1-*` → 支持 `REFERENCE_TO_VIDEO`（多图参考）
- 其他模型 → 通常支持 `TEXT_TO_VIDEO` 和 `IMAGE_TO_VIDEO`

**正确选择**：
- 多张角色图 → 用 `neo-video-2-0` + `UNIVERSAL_TO_VIDEO`
- 单张首帧 → 用 `doubao-seedance-1-5-pro` + `IMAGE_TO_VIDEO`
- 纯文字 → 用 `doubao-seedance-1-5-pro` + `TEXT_TO_VIDEO`

### 3. UNIVERSAL_TO_VIDEO 提示词写法错误

**错误示例**：`--prompt "蓝白校服的男生和穿碎花裙子的女生在校园里散步"`

**正确示例**：`--prompt "参考@图片 1 的男生和@图片 2 的女生，两人在阳光明媚的校园里并肩散步，镜头缓慢跟随"`

**规则**：
- `--image-urls` 中第 1 个 URL → 用 `@图片 1` 引用
- `--image-urls` 中第 2 个 URL → 用 `@图片 2` 引用
- `--video-urls` 中第 1 个 URL → 用 `@视频 1` 引用
- `--audio-urls` 中第 1 个 URL → 用 `@音频 1` 引用
- **必须**在 prompt 中明确引用每个素材，不要用"那张图"等模糊表达

### 4. 认证服务不可用

**现象**：`Authentication service unavailable, please try again`

**原因**：Neodomain 服务端认证系统临时故障（可能在重启）

**解决方案**：等待 5-10 分钟后重试

---

## 意图识别与路径选择

根据用户意图选择正确路径：

| 用户意图 | 路径 |
|---------|------|
| 生成图片（无参考图） | `generate_image.py` → TEXT_TO_IMAGE |
| 生成图片（有参考图/角色一致性） | `generate_image_ref.py` |
| 生成视频（纯文字描述） | `generate_video.py` → `TEXT_TO_VIDEO` |
| 生成视频（有参考图/首帧） | `generate_video.py` → `IMAGE_TO_VIDEO` |
| 生成视频（多张参考图保持一致性） | `generate_video.py` → `REFERENCE_TO_VIDEO`（仅 Veo 3.1） |
| 生成视频（多模态：图 + 视频 + 音频组合） | `generate_video.py` → `UNIVERSAL_TO_VIDEO`（Universal 模型） |
| 动作迁移（把参考视频动作转移到图片人物上） | `motion_control.py` |
| 故事板/分镜批量生视频 | `batch_video.py` |

---

## Model Selection Logic

### 图片模型选择

```
有参考图？
├─ 是 → generate_image_ref.py，模型用 doubao-seedream-5-0-260128
└─ 否 → generate_image.py
        ├─ 追求高性价比 → doubao-seedream-5-0-260128 (25pts)
        ├─ 追求最高质量 → gemini-3-pro-image-preview (100pts)
        └─ 默认/普通需求 → gemini-3.1-flash-image-preview (90pts)
```

### 视频模型选择

```
有多模态素材（视频/音频参考）？
└─ 是 → UNIVERSAL_TO_VIDEO
        ├─ 追求最高品质 → neo-video-2-0
        ├─ 追求速度/性价比 → neo-video-2-0-fast
        └─ 需要高分辨率 (1080p) → kling-v3-omni 或 kling-video-o1

有多张参考图（保持角色一致性）？
└─ 是 → REFERENCE_TO_VIDEO，模型用 veo-3.1-generate-preview

有参考图（图生视频）？
└─ 是 → IMAGE_TO_VIDEO
        ├─ 需要音频 → doubao-seedance-1-5-pro-251215 或 kling-v3
        ├─ 需要首尾帧精确控制 → kling-v3 或 kling-v2-6
        ├─ 需要超高清 4K → veo-3.1-generate-preview
        ├─ 需要超长时长 (15s+) → kling-v3(最长 15s) 或 vidu-q3-pro(最长 16s)
        └─ 默认 → doubao-seedance-1-5-pro-251215

纯文字生视频？
└─ 是 → TEXT_TO_VIDEO
        ├─ 需要音频 → doubao-seedance-1-5-pro-251215 或 kling-v3
        ├─ 高性价比 → doubao-seedance-1-0-pro-fast-251015
        └─ 默认 → doubao-seedance-1-5-pro-251215
```

### 视频参数选择规则

- **resolution**：用户未指定时默认 `720p`；明确要求高清用 `1080p`；明确要求超清用 `4K`（仅 Veo 3.1 支持）
- **duration**：用户未指定时默认 `8s`；需注意各模型上限（见下表），不要超出范围
- **aspect-ratio**：根据用途自主判断——竖屏内容用 `9:16`，横屏用 `16:9`，方形用 `1:1`；IMAGE_TO_VIDEO 模式下此参数无效，无需传入
- **generate-audio**：用户提到"有声音"/"带音频"/"有背景音乐"时自动加上

---

## Authentication

```bash
# Step 1：发送验证码（询问用户手机号或邮箱后执行）
python3 {baseDir}/scripts/login.py --send-code --contact "手机号或邮箱"

# Step 2：用户提供验证码后登录
python3 {baseDir}/scripts/login.py --login --contact "手机号或邮箱" --code "验证码"
```

**Step 2 可能出现两种结果：**

- **单一身份**：直接输出 `accessToken`，告知用户设置到 `NEODOMAIN_ACCESS_TOKEN` 环境变量。

- **多身份**：输出身份列表（含编号、类型、昵称、企业名、userId），需执行 Step 3 选择身份：

```bash
# Step 3：选择身份（仅在 Step 2 返回多身份时执行）
python3 {baseDir}/scripts/login.py --select-identity --contact "手机号或邮箱" --user-id "选中的userId"
```

Step 3 成功后输出 `accessToken`，告知用户设置到 `NEODOMAIN_ACCESS_TOKEN` 环境变量。

---

## Image Generation

### generate_image.py（文生图 / 图生图）

```bash
python3 {baseDir}/scripts/generate_image.py \
  --prompt "A beautiful mountain landscape, golden hour, cinematic" \
  --model "doubao-seedream-5-0-260128" \
  --aspect-ratio "16:9" \
  --size "2K" \
  --token $NEODOMAIN_ACCESS_TOKEN
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--prompt` | 图片描述 | 必填 |
| `--model` | 模型 ID | `gemini-3.1-flash-image-preview` |
| `--aspect-ratio` | `1:1`, `16:9`, `9:16`, `4:3`, `3:4` | `1:1` |
| `--num-images` | `1` 或 `4` | `1` |
| `--size` | `1K`, `2K`, `4K` | `2K` |
| `--negative-prompt` | 负向提示词 | - |
| `--guidance-scale` | 提示词遵循度 (1.0-20.0) | `7.5` |
| `--seed` | 随机种子 | 随机 |
| `--output-format` | `jpeg`, `png`, `webp` | `jpeg` |
| `--output-dir` | 保存目录 | `./output` |

**可用模型：**

| 模型 ID | 费用 | 支持尺寸 | 特点 |
|--------|------|----------|------|
| `gemini-2.5-flash-image` | 30 pts | 1K | 快速低价 |
| `gemini-3.1-flash-image-preview` | 90 pts | 1K, 2K, 4K | 均衡 |
| `gemini-3-pro-image-preview` | 100 pts | 2K, 4K | 最高质量 |
| `doubao-seedream-5-0-260128` | 25 pts | 2K, 3K | 最高性价比，推荐参考图用 |
| `doubao-seedream-4-5-251128` | 30 pts | 2K, 4K | - |
| `doubao-seedream-4-0-250828` | 25 pts | 2K, 4K | - |
| `gpt-image-1.5` | 100 pts | 1K | GPT 风格 |
| `Midjourney-niji 7` | 30 pts | 1K | 二次元/动漫 |
| `Midjourney-v 7` | 30 pts | 1K | 艺术风格 |

### generate_image_ref.py（参考图生图 / 角色一致性）

```bash
python3 {baseDir}/scripts/generate_image_ref.py \
  --prompt "A woman walking in a forest" \
  --reference-image "https://example.com/character1.jpg" \
  --reference-image "https://example.com/character2.jpg" \
  --model "doubao-seedream-5-0-260128" \
  --aspect-ratio "16:9" \
  --token $NEODOMAIN_ACCESS_TOKEN
```

`--reference-image` 可多次指定，上限 10 张。其余参数同 `generate_image.py`，默认模型为 `doubao-seedream-5-0-260128`。

---

## Video Generation

### generate_video.py

统一入口，通过 `--generation-type` 区分模式。

#### TEXT_TO_VIDEO（文生视频）

```bash
python3 {baseDir}/scripts/generate_video.py \
  --prompt "A serene lake at dawn, mist rising, cinematic wide shot" \
  --model "doubao-seedance-1-5-pro-251215" \
  --generation-type "TEXT_TO_VIDEO" \
  --aspect-ratio "16:9" \
  --resolution "720p" \
  --duration "8s" \
  --generate-audio \
  --token $NEODOMAIN_ACCESS_TOKEN
```

#### IMAGE_TO_VIDEO（图生视频）

```bash
# 首帧必填，尾帧可选（需模型支持首尾帧）；宽高比自动按参考图，无需指定
python3 {baseDir}/scripts/generate_video.py \
  --prompt "The camera slowly pans across the landscape" \
  --model "kling-v3" \
  --generation-type "IMAGE_TO_VIDEO" \
  --first-frame "https://example.com/image.jpg" \
  --last-frame "https://example.com/end.jpg" \
  --resolution "1080p" \
  --duration "5s" \
  --generate-audio \
  --token $NEODOMAIN_ACCESS_TOKEN
```

#### REFERENCE_TO_VIDEO（多图参考生视频）

仅 `veo-3.1-generate-preview` / `veo-3.1-fast-generate-preview` 支持。

```bash
python3 {baseDir}/scripts/generate_video.py \
  --prompt "Characters interacting in a scene" \
  --model "veo-3.1-generate-preview" \
  --generation-type "REFERENCE_TO_VIDEO" \
  --image-urls "https://example.com/ref1.jpg,https://example.com/ref2.jpg" \
  --aspect-ratio "16:9" \
  --resolution "1080p" \
  --duration "8s" \
  --generate-audio \
  --token $NEODOMAIN_ACCESS_TOKEN
```

#### UNIVERSAL_TO_VIDEO（多模态组合生视频）

支持图片、视频、音频混合参考。**必须**在 prompt 中用 `@图片 1`/`@图片 2`/`@视频 1`/`@音频 1` 精确引用对应素材（顺序即编号）。

```bash
python3 {baseDir}/scripts/generate_video.py \
  --prompt "参考@图片 1 的男生和@图片 2 的女生，两人在阳光明媚的校园里并肩散步，镜头缓慢跟随" \
  --model "neo-video-2-0" \
  --generation-type "UNIVERSAL_TO_VIDEO" \
  --image-urls "https://example.com/boy.jpg,https://example.com/girl.jpg" \
  --resolution "720p" \
  --duration "5s" \
  --token $NEODOMAIN_ACCESS_TOKEN
```

**Universal 提示词公式：** `@素材引用 + 主体描述 + 动作/场景 + 镜头语言 + 风格美学`

**@素材引用规则（重要！）**：
- `--image-urls` 中第 1 个 URL → 用 `@图片 1` 引用
- `--image-urls` 中第 2 个 URL → 用 `@图片 2` 引用
- `--video-urls` 中第 1 个 URL → 用 `@视频 1` 引用
- `--audio-urls` 中第 1 个 URL → 用 `@音频 1` 引用
- **必须**在 prompt 开头明确引用每个素材，不要用"那张图""这个角色"等模糊表达

**错误示例** ❌：
```bash
--prompt "蓝白校服的男生和穿碎花裙子的女生在校园里散步"
--image-urls "boy.jpg,girl.jpg"
```

**正确示例** ✅：
```bash
--prompt "参考@图片 1 的蓝白校服男生和@图片 2 的碎花裙子女生，两人在阳光明媚的校园里并肩散步，镜头缓慢跟随"
--image-urls "boy.jpg,girl.jpg"
```

**适用模型**：`neo-video-2-0`, `neo-video-2-0-fast`, `kling-video-o1`, `kling-v3-omni`

#### generate_video.py 完整参数表

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--prompt` | 视频描述 | 必填 |
| `--model` | 模型 ID | `doubao-seedance-1-5-pro-251215` |
| `--generation-type` | `TEXT_TO_VIDEO` / `IMAGE_TO_VIDEO` / `REFERENCE_TO_VIDEO` / `UNIVERSAL_TO_VIDEO` | `TEXT_TO_VIDEO` |
| `--first-frame` | 首帧图片 URL（I2V 必填） | - |
| `--last-frame` | 尾帧图片 URL（可选，需模型支持） | - |
| `--image-urls` | 参考图 URL 逗号分隔（R2V 必填；U2V 可选，→ `imageUrls`） | - |
| `--video-urls` | 参考视频 URL 逗号分隔（U2V 可选，→ `referenceVideoUrls`） | - |
| `--audio-urls` | 参考音频 URL 逗号分隔（U2V 可选，→ `audioUrl`） | - |
| `--aspect-ratio` | `16:9`/`9:16`/`1:1`/`4:3`/`3:4`/`21:9`/`9:21`（T2V/R2V 有效；I2V 无效） | `16:9` |
| `--resolution` | `480p`/`720p`/`768p`/`1080p`/`2k`/`4K`（各模型范围不同） | `720p` |
| `--duration` | 时长如 `5s`/`8s`/`10s`（各模型范围不同） | `8s` |
| `--fps` | 帧率 | `24` |
| `--seed` | 随机种子 | 随机 |
| `--generate-audio` | 生成音频（flag） | false |
| `--enhance-prompt` | 增强提示词（flag） | false |
| `--negative-prompt` | 负向提示词 | - |
| `--output-dir` | 保存目录 | `./output` |

#### 各模型支持范围（Cascading）

| 模型 ID | 类型 | 分辨率 | 时长 | 音频 | 首尾帧 |
|--------|------|--------|------|------|--------|
| `doubao-seedance-1-5-pro-251215` | T2V/I2V | 480p, 720p, 1080p | 4–12s | ✅ | ✅ |
| `doubao-seedance-1-0-pro-250528` | T2V/I2V | 720p, 1080p | 2–10s | ❌ | ✅ |
| `doubao-seedance-1-0-pro-fast-251015` | T2V/I2V | 720p, 1080p | 3–10s | ❌ | ❌ |
| `kling-v3` | T2V/I2V | 720p, 1080p | 3–15s | ✅ | ✅ |
| `kling-v2-6` | T2V/I2V | 1080p | 5s, 10s | ✅ | ✅ |
| `kling-v2-5-turbo` | T2V/I2V | 720p, 1080p | 5s, 10s | ❌ | ✅ |
| `kling-v2-1` | **I2V 仅** | 720p, 1080p | 5s, 10s | ❌ | ✅ |
| `vidu-q3-pro` | T2V/I2V | 720p, 1080p, 2k¹ | 5–16s | ✅ | ✅ |
| `vidu-q2-pro` | **I2V 仅** | 720p, 1080p | 5s, 8s | ❌ | ✅ |
| `wan2.6` | T2V/I2V | 720p, 1080p | 5s, 10s, 15s | ✅ | ❌ |
| `wan2.6-i2v-flash` | **I2V 仅** | 720p, 1080p | 5s, 10s, 15s | ✅ | ❌ |
| `MiniMax-Hailuo-2.3` | T2V/I2V | 768p, 1080p | 6s, 10s | ❌ | ❌ |
| `MiniMax-Hailuo-2.3-Fast` | T2V/I2V | 768p, 1080p | 6s, 10s | ❌ | ❌ |
| `MiniMax-Hailuo-02` | T2V/I2V | 768p, 1080p | 6s, 10s | ❌ | ✅ |
| `veo-3.1-generate-preview` | T2V/I2V/**R2V** | 720p, 1080p, 4K | 4s, 6s, 8s | ✅ | ✅ |
| `veo-3.1-fast-generate-preview` | T2V/I2V/**R2V** | 720p, 1080p, 4K | 4s, 6s, 8s | ✅ | ✅ |

> ¹ Vidu Q3 Pro 的 2k 仅在 I2V 模式下支持。
> T2V 宽高比：Doubao 支持 `16:9/9:16/1:1/4:3/3:4/21:9/9:21`；Kling/Vidu/Wan 支持 `16:9/9:16/1:1`；Hailuo 仅 `16:9`；Veo 支持 `16:9/9:16`。

#### 各模型支持范围（Universal，--generation-type UNIVERSAL_TO_VIDEO）

| 模型 ID | 分辨率 | 时长 | 音频 | 首尾帧 | 最大参考数 |
|--------|--------|------|------|--------|-----------|
| `neo-video-2-0` | 480p, 720p | 4–15s | ✅ | ✅ | 图×9, 视频×3, 音频×3 |
| `neo-video-2-0-fast` | 480p, 720p | 4–12s | ✅ | ✅ | 图×9, 视频×3, 音频×3 |
| `kling-video-o1` | 720p, 1080p | 3–10s | ❌ | ❌ | 图×12, 视频×1 |
| `kling-v3-omni` | 720p, 1080p | 3–15s | ✅ | ❌ | 图×12, 视频×1 |

### motion_control.py（动作迁移）

将参考视频的人物动作迁移到参考图片上：

```bash
python3 {baseDir}/scripts/motion_control.py \
  --image "https://example.com/ref_image.jpg" \
  --video "https://example.com/ref_video.mp4" \
  --prompt "Make the character dance" \
  --mode "pro" \
  --duration 5000 \
  --token $NEODOMAIN_ACCESS_TOKEN
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--image` | 参考图片 URL | 必填 |
| `--video` | 参考动作视频 URL | 必填 |
| `--prompt` | 附加文字控制 | - |
| `--mode` | `std`（标准）/ `pro`（专业） | `std` |
| `--orientation` | 角色朝向来源：`image` / `video` | `image` |
| `--keep-original-sound` | 保留原视频声音：`yes` / `no` | `yes` |
| `--duration` | 时长（毫秒） | `5000` |
| `--output-dir` | 保存目录 | `./output` |

### batch_video.py（批量分镜生视频）

> 需要 `pip install oss2`（用于上传本地图片到 OSS）。默认使用 `doubao-seedance-1-5-pro-251215`，IMAGE_TO_VIDEO，720p/5s。

```bash
python3 {baseDir}/scripts/batch_video.py \
  --storyboard-dir ./storyboards \
  --output-dir ./output/videos \
  --start 1 \
  --end 17 \
  --token $NEODOMAIN_ACCESS_TOKEN
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--storyboard-dir` | 分镜图片目录（命名格式：`shot_01_*.jpeg`） | 必填 |
| `--output-dir` | 视频输出目录 | 必填 |
| `--start` | 起始镜头编号 | `1` |
| `--end` | 结束镜头编号 | `17` |

---

## Output

所有脚本完成后自动下载到输出目录：
- 图片：`image_1.jpg` / `.png` / `.webp`
- 视频：`video.mp4` + `thumbnail.jpg`
- 批量视频：`video_01.mp4`, `video_02.mp4`, ...
- `metadata.json`：任务 ID、参数、文件 URL 等详情
