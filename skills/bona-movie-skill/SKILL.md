---
name: bona-movie-production
description: "Bona Movie Production is Bona Group's film-grade production skill. It covers image generation, image editing, and video generation, using Nano Banana 2 and Nano Banana Pro for images, and Seedance plus generate_video_kling_v3 for videos."
license: MIT
compatibility: "需要 Python 3.9+，依赖 requests。默认请求 https://api.bonanai.com/v1/tencent 。"
metadata:
  author: codex
  version: "1.0.0"
  python-version: ">=3.9"
  dependencies:
    - requests
  tags:
    - ai-image
    - ai-video
    - bona
    - movie-production
  env:
    - name: BONA_API_KEY
      required: true
      desc: "Bona API Key"
    - name: TENCENT_VIDEO_TIMEOUT
      required: false
      desc: "HTTP 超时时间，默认 600 秒"
---

# Bona Movie Production

这是博纳集团电影级的制作 Skill，包含：

- 图片生成
- 图片编辑
- 视频生成

流程：

- 创建任务后，持续轮询查询任务结果
- 轮询状态为 `9` 说明生成完毕
- `-1` 为生成失败
- `1` 是正在生成中
- 图片大概 `1min`
- 视频大概 `3-5min`

当前 Skill 只使用四个模型：

- 图片：`generate_image_nano_banana_2`、`generate_image_nano_banana_pro`
- 视频：`generate_video_seedance`、`generate_video_kling_v3`

使用前先配置环境变量：

```bash
export BONA_API_KEY="your_api_key"
```

## 一、图片生成

- `Nano Banana 2`
  更偏理解能力。适合复杂指令、参考图理解、换视角、文本渲染、多图关系理解。
- `Nano Banana Pro`
  更偏最终质量。适合高质量成片、商业视觉、海报、封面、九宫格或 5x5 宫格输出。

### 1. `generate_image_nano_banana_2`

适合：

- 指令复杂
- 要求理解更强
- 文字内容多
- 多元素关系清晰

参数规则：

- 分辨率：`0.5K`、`1K`、`2K`、`4K`
- 比例：`1:1`、`1:4`、`1:8`、`2:3`、`3:2`、`3:4`、`4:1`、`4:3`、`4:5`、`5:4`、`8:1`、`9:16`、`16:9`、`21:9`

Prompt 写法：

- 必须用英文
- 用户需求清晰时，尽量保持原意
- 不清晰时，按 主体 + 场景 + 风格 + 光线 + 细节 来写
- 如果要文字渲染，直接把文字内容写进 prompt

示例：

```bash
python skills/bona-movie-production/scripts/bona_movie_production.py create-image \
  --tool-name generate_image_nano_banana_2 \
  --image-name "hero-character-design" \
  --prompt "A modern bookstore cafe interior with warm wood shelves, soft afternoon sunlight, a handwritten chalkboard menu, calm and inviting atmosphere, editorial interior photography" \
  --task-type TEXT_TO_IMAGE \
  --resolution 2K \
  --aspect-ratio 4:3
```

### 2. `generate_image_nano_banana_pro`

适合：

- 成片质量优先
- 广告图
- 质感、细节、商业感更重要

参数规则：

- 分辨率：`1K`、`2K`、`4K`
- 比例：`21:9`、`16:9`、`4:3`、`3:2`、`1:1`、`9:16`、`3:4`、`2:3`、`5:4`、`4:5`

Prompt 写法：

- 必须用英文
- 适合写高质量商业表达
- 强调材质、光线、构图、品牌感

示例：

```bash
python skills/bona-movie-production/scripts/bona_movie_production.py create-image \
  --tool-name generate_image_nano_banana_pro \
  --image-name "premium-key-visual" \
  --prompt "A premium skincare bottle on polished black stone, controlled studio side lighting, luxury beauty advertising, sharp reflections, elegant minimal composition" \
  --task-type TEXT_TO_IMAGE \
  --resolution 4K \
  --aspect-ratio 4:5
```

## 二、图片编辑

### 1. `generate_image_nano_banana_2`

适合：

- 精确编辑
- 改一处、保留其余不变
- 对指令理解要求高

Prompt 写法：

- 必须用英文
- 明确要保留什么
- 明确只改什么
- 常用句式：
  `change only X to Y`
  `add/remove X while keeping everything else unchanged`

示例：

```bash
python skills/bona-movie-production/scripts/bona_movie_production.py create-image \
  --tool-name generate_image_nano_banana_2 \
  --image-name "character-bg-edit" \
  --prompt "Change only the wall color to muted olive green while keeping the furniture, layout, lighting, and camera angle unchanged" \
  --image-url https://example.com/room.png \
  --task-type EDIT_SINGLE_IMAGE \
  --aspect-ratio 4:3 \
  --resolution 1K
```

### 2. `generate_image_nano_banana_pro`

适合：

- 成片质感优先的编辑
- 海报、封面、商业人像精修

示例：

```bash
python skills/bona-movie-production/scripts/bona_movie_production.py create-image \
  --tool-name generate_image_nano_banana_pro \
  --image-name "fashion-campaign-edit" \
  --prompt "Change only the background to a luxury hotel lobby, keeping the model pose, facial expression, clothing, and lighting direction unchanged, premium fashion campaign look" \
  --image-url https://example.com/model.png \
  --task-type EDIT_SINGLE_IMAGE \
  --aspect-ratio 3:4 \
  --resolution 2K
```

## 三、参考图生成

### 1. `generate_image_nano_banana_2`

适合：

- 参考图理解
- 角色一致性
- 多图语义关系清晰

Prompt 写法：

- 必须用英文
- 用 `the first image`、`the second image`
- 明确每张参考图负责什么
- 如果要角色一致，直接写 `keep character consistent`

示例：

```bash
python skills/bona-movie-production/scripts/bona_movie_production.py create-image \
  --tool-name generate_image_nano_banana_2 \
  --image-name "character-consistency-scene" \
  --prompt "Refer to the first image for the character appearance and the second image for the outfit details. Keep character consistent and place her in a futuristic subway station with cinematic lighting." \
  --image-url https://example.com/char.png \
  --image-url https://example.com/outfit.png \
  --task-type REFERENCE_TO_IMAGE \
  --aspect-ratio 9:16 \
  --resolution 2K
```

### 2. `generate_image_nano_banana_pro`

适合：

- 品牌 KV
- 人物、商品一致性但最终输出更重质量

示例：

```bash
python skills/bona-movie-production/scripts/bona_movie_production.py create-image \
  --tool-name generate_image_nano_banana_pro \
  --image-name "premium-reference-kv" \
  --prompt "Refer to the first image for the product shape and the second image for the lighting mood. Create a premium hero shot with clean reflections and luxury beauty campaign quality." \
  --image-url https://example.com/product.png \
  --image-url https://example.com/light.png \
  --task-type REFERENCE_TO_IMAGE \
  --aspect-ratio 1:1 \
  --resolution 4K
```

## 四、转视角

这个任务更推荐 `Nano Banana 2`。

原因：

- 它对结构理解更强
- 更适合“同一主体换角度、换视角、转三视图”

Prompt 写法：

- 必须用英文
- 明确是同一主体
- 明确要变成什么视角
- 保留哪些元素不变

示例 1：单图转侧视角

```bash
python skills/bona-movie-production/scripts/bona_movie_production.py create-image \
  --tool-name generate_image_nano_banana_2 \
  --image-name "product-side-view" \
  --prompt "Use the first image as the same product reference. Change the camera view from front view to left side view, while keeping material, color, proportions, and design details unchanged." \
  --image-url https://example.com/product-front.png \
  --task-type REFERENCE_TO_IMAGE \
  --aspect-ratio 1:1 \
  --resolution 2K
```

示例 2：角色转背视角

```bash
python skills/bona-movie-production/scripts/bona_movie_production.py create-image \
  --tool-name generate_image_nano_banana_2 \
  --image-name "character-rear-view" \
  --prompt "Use the first image as the same character reference. Generate a clean rear view of the same character, keeping hairstyle, clothing, silhouette, and proportions consistent." \
  --image-url https://example.com/character-front.png \
  --task-type REFERENCE_TO_IMAGE \
  --aspect-ratio 3:4 \
  --resolution 2K
```

示例 3：角色三视图

```bash
python skills/bona-movie-production/scripts/bona_movie_production.py create-image \
  --tool-name generate_image_nano_banana_2 \
  --image-name "character-turnaround-sheet" \
  --prompt "Use the first image as the same character reference. Create a character turnaround sheet showing front view, side view, and back view, consistent design, clean white background, concept art presentation." \
  --image-url https://example.com/character.png \
  --task-type REFERENCE_TO_IMAGE \
  --aspect-ratio 16:9 \
  --resolution 4K
```

## 五、九宫格和 5x5 宫格

这种任务更推荐 `Nano Banana Pro`。

原因：

- 最终输出质量更好
- 适合整页构图
- 更适合海报、角色表、商品矩阵图

Prompt 写法：

- 必须用英文
- 明确是几宫格
- 明确每格内容是否一致风格
- 明确整体版式和背景
- 最好逐格指定构图，至少写清每一格的景别、角度或主体动作
- 推荐写法：`panel 1 ... panel 2 ... panel 3 ...`，不要只写“九个不同画面”

示例 1：九宫格人物造型板

```bash
python skills/bona-movie-production/scripts/bona_movie_production.py create-image \
  --tool-name generate_image_nano_banana_pro \
  --image-name "character-style-board-3x3" \
  --prompt "Create a 3x3 character style board for the same girl in one image, consistent character design, clean editorial layout, white background, fashion mood board quality. Panel 1 full-body front standing pose. Panel 2 full-body left side view. Panel 3 full-body back view. Panel 4 medium shot looking up with arms crossed. Panel 5 medium shot smiling toward camera. Panel 6 medium shot turning while hair moves. Panel 7 close-up calm expression. Panel 8 close-up laughing expression. Panel 9 seated three-quarter view with elegant pose." \
  --task-type TEXT_TO_IMAGE \
  --aspect-ratio 1:1 \
  --resolution 4K
```

示例 2：九宫格商品展示图

```bash
python skills/bona-movie-production/scripts/bona_movie_production.py create-image \
  --tool-name generate_image_nano_banana_pro \
  --image-name "product-grid-3x3" \
  --prompt "Create a 3x3 product grid in one image for the same sneaker, nine clean panels showing different angles and close-up details, premium e-commerce presentation, consistent lighting, white studio background." \
  --task-type TEXT_TO_IMAGE \
  --aspect-ratio 1:1 \
  --resolution 4K
```

示例 3：5x5 表情宫格

```bash
python skills/bona-movie-production/scripts/bona_movie_production.py create-image \
  --tool-name generate_image_nano_banana_pro \
  --image-name "expression-sheet-5x5" \
  --prompt "Create a 5x5 facial expression sheet in one image for the same anime girl, twenty-five panels, consistent character design, each panel with a different expression, clean character sheet layout, white background." \
  --task-type TEXT_TO_IMAGE \
  --aspect-ratio 1:1 \
  --resolution 4K
```

示例 4：5x5 icon / sticker sheet

```bash
python skills/bona-movie-production/scripts/bona_movie_production.py create-image \
  --tool-name generate_image_nano_banana_pro \
  --image-name "sticker-sheet-5x5" \
  --prompt "Create a 5x5 sticker sheet in one image, twenty-five cute food icons, consistent illustration style, balanced spacing, bright clean colors, packaging-ready quality." \
  --task-type TEXT_TO_IMAGE \
  --aspect-ratio 1:1 \
  --resolution 4K
```

## 六、文生视频

当用户只有文本描述，没有首帧、尾帧、参考图、参考视频、参考音频时，按文生视频处理。

### 1. `generate_video_kling_v3`

适合：

- 默认首选文生视频
- 要更强镜头感
- 想要音画表现更完整
- 短时长电影感镜头

参数规则：

- 比例：`16:9`、`9:16`、`1:1`
- 时长：推荐 `5`、`10`
- 模式：`std`、`pro`
- 声音：`on`、`off`
- 支持多镜头 `shot_prompts`

Prompt 写法：

- 清楚写主体、动作、镜头运动、场景、光线
- 单镜头直接写完整 prompt
- 多镜头时优先拆成 `shot_prompts`
- 如果要声音氛围，可直接写进 prompt

示例：

```bash
python skills/bona-movie-production/scripts/bona_movie_production.py create-video \
  --tool-name generate_video_kling_v3 \
  --video-name "teaser-shot-01" \
  --prompt "A young woman walking through a rainy neon street at night, reflections on the wet ground, camera slowly tracking forward, blue and pink neon lighting, cinematic atmosphere, realistic motion" \
  --duration 5 \
  --aspect-ratio 16:9 \
  --mode pro \
  --sound on
```

### 2. `generate_video_seedance`

适合：

- 文生视频
- 更强运动质量
- 后续可能扩展到参考素材模式

参数规则：

- 比例：`21:9`、`16:9`、`4:3`、`1:1`、`3:4`、`9:16`
- 时长：`4-15`
- 分辨率：`480P`、`720P`
- 文生模式下不要同时传首尾帧或参考素材

Prompt 写法：

- 清楚描述主体、动作、镜头、光线
- 优先写成单镜头
- 不要太抽象，尽量写清动作节奏

示例：

```bash
python skills/bona-movie-production/scripts/bona_movie_production.py create-video \
  --tool-name generate_video_seedance \
  --video-name "character-motion-shot" \
  --prompt "A fashion model turns slowly toward camera, fabric moves naturally, soft cinematic backlight, stable single-shot motion" \
  --duration 6 \
  --aspect-ratio 9:16 \
  --resolution 720P
```

## 七、首帧生视频

当用户提供一张起始图片，希望把静态图做成视频时，按首帧生视频处理。

### 1. `generate_video_kling_v3`

适合：

- 首帧图转视频默认首选
- 人物轻动作
- 海报起身
- 电影感人物镜头

参数规则：

- 起始帧可传 `--start-frame`
- 支持 `16:9`、`9:16`、`1:1`
- 时长推荐 `5`、`10`

示例：

```bash
python skills/bona-movie-production/scripts/bona_movie_production.py create-video \
  --tool-name generate_video_kling_v3 \
  --video-name "character-i2v" \
  --prompt "The character slowly turns her head, blinks naturally, and breathes subtly. Keep the framing stable and cinematic." \
  --start-frame https://example.com/character-first-frame.png \
  --duration 5 \
  --aspect-ratio 9:16 \
  --mode pro
```

### 2. `generate_video_seedance`

适合：

- 起始帧驱动动画
- 更重运动质量
- 人物、服装、动态保持自然

参数规则：

- 比例：`21:9`、`16:9`、`4:3`、`1:1`、`3:4`、`9:16`
- 时长：`4-15`
- 分辨率：`480P`、`720P`

Prompt 写法：

- 如果用了起始帧，重点写动作变化，不要重复描述外观
- 清楚写镜头和动作

示例：

```bash
python skills/bona-movie-production/scripts/bona_movie_production.py create-video \
  --tool-name generate_video_seedance \
  --video-name "seedance-first-frame" \
  --prompt "The subject smiles slightly and the camera pushes in gently, preserving identity and costume details." \
  --start-frame https://example.com/char.png \
  --duration 5 \
  --aspect-ratio 9:16 \
  --resolution 720P
```

## 八、首尾帧视频

当用户同时提供起始图和结束图，希望做中间插帧和过渡时，按首尾帧视频处理。

### 1. `generate_video_kling_v3`

适合：

- 默认首选
- 标准首尾帧过渡
- 电影感过渡镜头

参数规则：

- 传尾帧时必须同时传首帧
- 若不想生成声音，建议 `--sound off`

示例：

```bash
python skills/bona-movie-production/scripts/bona_movie_production.py create-video \
  --tool-name generate_video_kling_v3 \
  --video-name "start-end-transition" \
  --prompt "A smooth cinematic transition from the first frame to the final frame, with natural body movement and stable camera motion." \
  --start-frame https://example.com/start.png \
  --end-frame https://example.com/end.png \
  --duration 5 \
  --aspect-ratio 16:9 \
  --mode pro \
  --sound off
```

### 2. `generate_video_seedance`

适合：

- 首尾帧过渡
- 更强调动作质量
- 人物、产品从 A 状态平滑过渡到 B 状态

参数规则：

- `image_end_frame` 存在时，必须有 `image_start_frame`
- 首尾帧模式和参考模式互斥

示例：

```bash
python skills/bona-movie-production/scripts/bona_movie_production.py create-video \
  --tool-name generate_video_seedance \
  --video-name "seedance-start-end" \
  --prompt "The character walks from the first pose into the final pose with continuous natural motion and matching costume dynamics." \
  --start-frame https://example.com/start-pose.png \
  --end-frame https://example.com/end-pose.png \
  --duration 6 \
  --aspect-ratio 3:4 \
  --resolution 720P
```

## 九、参考图视频

当用户希望人物、产品、IP 形象保持一致性，且提供了一张或多张参考图时，按参考图视频处理。

### 推荐模型

#### 1. `generate_video_seedance`

适合：

- 参考图较多
- 人物一致性视频
- 商品一致性视频
- 还可能接参考视频、参考音频

参数规则：

- 参考图：`1-6`
- 一旦用了参考模式，就不能同时再传首帧或尾帧

Prompt 写法：

- 不重复描述人物长相
- 重点写动作、镜头、场景和情绪

示例：

```bash
python skills/bona-movie-production/scripts/bona_movie_production.py create-video \
  --tool-name generate_video_seedance \
  --video-name "reference-image-driven-video" \
  --prompt "Keep the same character identity and create a slow cinematic walk toward camera with subtle wind in hair and coat." \
  --reference-image https://example.com/ref1.png \
  --reference-image https://example.com/ref2.png \
  --reference-image https://example.com/ref3.png \
  --duration 5 \
  --aspect-ratio 16:9 \
  --resolution 720P
```

## 十、参考视频视频

当用户提供参考视频，希望做视频风格迁移、动作参考或节奏参考时，按参考视频视频处理。

### 推荐模型

#### 1. `generate_video_seedance`

适合：

- 参考视频
- 动作节奏参考
- 镜头运动参考
- 后续还要接参考音频

参数规则：

- 参考视频：`1-3`
- 与首尾帧模式互斥

Prompt 写法：

- 重点写要保留什么运动能量、节奏、镜头感
- 不要写成和参考视频完全无关的内容

示例：

```bash
python skills/bona-movie-production/scripts/bona_movie_production.py create-video \
  --tool-name generate_video_seedance \
  --video-name "reference-video-driven-video" \
  --prompt "Keep the same motion energy as the reference and generate a stylish commercial shot, clean body rhythm, strong fashion lighting." \
  --reference-video https://example.com/motion.mp4 \
  --duration 5 \
  --aspect-ratio 16:9 \
  --resolution 720P
```

## 十一、参考音频视频

当用户提供参考音频，希望根据节拍、对白节奏或音乐做视频时，按参考音频视频处理。

### 推荐模型

#### 1. `generate_video_seedance`

适合：

- 音乐卡点视频
- 根据音频节奏做动作
- 有对白或旁白节奏参考

参数规则：

- 参考音频：`1-3`
- 与首尾帧模式互斥

Prompt 写法：

- 写清动作、节奏、beat、卡点方式
- 适合音乐感强的 prompt

示例：

```bash
python skills/bona-movie-production/scripts/bona_movie_production.py create-video \
  --tool-name generate_video_seedance \
  --video-name "audio-driven-video" \
  --prompt "Generate a stylish dance clip matching the reference beat, strong rhythmic body movement, clean timing accents, energetic stage lighting." \
  --reference-audio https://example.com/beat.mp3 \
  --duration 5 \
  --aspect-ratio 9:16 \
  --resolution 720P
```

## 十二、多镜头视频

### 1. `generate_video_kling_v3`

适合：

- 分镜式短片
- 一条任务内多个 shot
- 预告片节奏剪辑

参数规则：

- 最多 6 个 shot
- 每个 shot 要有 `index`、`prompt`、`duration`
- 所有 shot 的时长总和必须等于外层 `duration`

Prompt 写法：

- 多镜头时优先用 `shot_prompts`
- 每个 shot 单独写清场景、动作、镜头

schema 示例：

```json
{
  "tool_name": "generate_video_kling_v3",
  "video_name": "multi-shot-trailer",
  "prompt": "Trailer sequence",
  "aspect_ratio": "16:9",
  "duration": 5,
  "mode": "pro",
  "sound": "on",
  "shot_prompts": [
    {
      "index": 0,
      "prompt": "A dark cinema corridor, camera pushes forward, tense ambience",
      "duration": "2"
    },
    {
      "index": 1,
      "prompt": "The heroine turns back suddenly, dramatic backlight, cloth movement",
      "duration": "3"
    }
  ]
}
```

## 十三、查询任务

图片查询：

```bash
python skills/bona-movie-production/scripts/bona_movie_production.py query-image \
  --task-id your-task-id
```

视频查询：

```bash
python skills/bona-movie-production/scripts/bona_movie_production.py query-video \
  --task-id your-task-id
```

状态说明：

- `1`：进行中
- `9`：完成
- `-1`：失败

查询判断规则：

- 先看 `status`，不要先看 `result_url`
- `status = 1` 时，即使 `result_url` 为空，也只是任务还在跑，不能判断为失败
- `status = 9` 时，才去读取 `result_url`
- `status = -1` 时，才按失败处理，并查看 `error_code`、`error_message`
- 不要因为 `result_url` 暂时为空，就改判成“接口行为变了”或“需要重新生成”
- 只有确认 `status = -1`，或者长时间轮询后仍没有进入终态，才考虑进一步排查
- `status = 9` 但 `result_url` 仍为空时，只能说明“任务已完成，但当前回包没有返回结果地址”

推荐理解方式：

- `status = 1`：继续查询
- `status = 9`：返回结果链接
- `status = -1`：返回失败原因

和视频联动时的规则：

- 如果用户要求“先生成分镜图，再用分镜图生成视频”，这就是两段任务，不能混成一个纯文生视频任务
- 只有真正拿到分镜图 URL 或本地文件后，才能进入下一步视频生成
- 如果图片任务 `status = 9` 但没有可用图片地址，要停在这里如实汇报，而不是自动改成“直接文生视频”

## 十四、实用建议

- 默认普通文生图：先用 `Nano Banana Pro`
- 复杂理解、换视角、参考图关系、多图任务：优先 `Nano Banana 2`
- 九宫格、5x5 宫格、海报、成片质量：优先 `Nano Banana Pro`
- 默认普通文生视频：先用 `generate_video_kling_v3`
- 参考图、参考视频、参考音频、多素材一致性：优先 `generate_video_seedance`
- 如果只想先看参数，用 `--print-payload`
