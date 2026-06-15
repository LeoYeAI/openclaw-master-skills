---
name: "vectcut-skill"
description: "AI 视频导演与自动化剪辑专家。能够理解视频素材内容、视频创作指令，自主规划脚本结构，并通过调用 VectCut API 实现创建剪映草稿、编排素材（B-roll/转场/特效）、生成 AI 配音与字幕，实现端到端的视频创作流程。"
homepage: "https://www.vectcut.com/"
metadata:
  openclaw:
    emoji: "🎬"
    requires:
      env: ["VECTCUT_API_KEY"]
    primaryEnv: "VECTCUT_API_KEY"
dependency:
---

# VectCut Skill（自主规划型 AI 视频架构师）

本技能赋予 AI 像专业剪辑师一样**“思考与执行”**的能力。它不仅能调用 API，还能通过分析用户意图和素材内容，自主规划视频的节奏、视觉风格和逻辑结构，最终产出可直接在剪映 中二次编辑的专业草稿。

## 核心智能行为

* **素材感知**：分析用户提供的视频/图片/音频 URL，理解画面内容与剪辑指令；优先调用现有服务 `get_duration`、`get_resolution`、`video_detail`、`asr_basic`、`asr_nlp`、`asr_llm` 完成时长获取、分辨率判断、画面理解与语音内容解析。`video_detail` 可提取细粒度语义（画面主体关系、人物朝向、物体位置、声音音调与风格等）。
* **ASR 按需策略**：默认优先级 `asr_llm > asr_nlp > asr_basic`，优先使用更高能力接口，仅在明确只需基础识别或时延敏感场景下降级。
  - `asr_basic`：速度最快，返回完整文案、句级时间、字级时间；中文/英文效果好，支持粤语、上海话、闽南语、四川/陕西方言；更适合横屏字幕或素材初步理解。
  - `asr_nlp`：速度中等，在 basic 基础上增加语义分句（每句不超过 12 字），更适合竖屏字幕。
  - `asr_llm`：速度最慢，在 nlp 基础上增加 AI 关键词提取，优先用于竖屏与短视频字幕。
  - 三个 ASR 接口均支持传入 `content`（正确文案）以显著提升匹配准确率与处理速度。
  - 三种回包结构不同，必须按端点解析：`asr_basic -> result.raw.result.utterances`；`asr_nlp -> segments`；`asr_llm -> segments(含 keywords/en)`。
* **脚本规划**：根据主题（如“成语故事”、“产品评测”）自动拆解分镜，确定各片段时长。
* **草稿生命周期管理**：先创建并维护草稿，再进入编排流程；优先调用 `create_draft` 初始化草稿，按需使用 `modify_draft` 修改草稿名/封面，任务异常或清理阶段使用 `remove_draft` 删除草稿。
* **反思自查**：在关键步骤后调用 `query_script` 回看当前草稿结构，核对轨道、素材与时间段是否符合预期；若不一致，先定位问题再执行修正操作。
* **视觉编排**：基于已创建草稿自主选择并添加转场（Transitions）、特效（Effects）、滤镜（Filters）和文本（Text）。
* **AI 资源补全**：当素材不足时，主动调用 `generate_image`、`generate_speech` 或 `generate_ai_video` 生成 B-roll 填充；其中 `generate_image` 支持 `nano_banana_2`、`nano_banana_pro`、`jimeng-4.5` 等聚合模型，`generate_speech` 通过 `text + provider + model + voice_id` 合成配音，可配合 `volume`、`target_start`、`effect_type/effect_params` 控制入轨位置与音色效果。
* **文本编排生命周期**：通过 `add_text` 创建文本素材，使用 `modify_text` 调整文案与样式，使用 `remove_text` 清理无效文本；文本动画、字体与局部样式优先从枚举中选取，保证可用性与一致性。
* **图片编排生命周期**：通过 `add_image` 添加图片素材，使用 `modify_image` 调整图片源、时间段、位置与动画，使用 `remove_image` 清理无效图片；动画与蒙版类型优先从枚举中选取，保证编排稳定性。
* **视频编排生命周期**：通过 `add_video` 添加视频素材，使用 `modify_video` 调整素材源、裁切区间、位置与速度，使用 `remove_video` 清理无效视频；转场在片段首尾紧邻时生效，且需加在前一个元素上。
* **AI 视频生成能力**：通过 `generate_ai_video` 调用聚合视频模型生成异步任务，再通过 `aivideo/task_status` 查询进度与视频结果；支持文生视频、图生视频与部分模型的首尾帧模式。
* **数字人能力**：通过 `digital_human/create` 发起音频驱动数字人任务，再通过 `digital_human/task_status` 查询生成状态与结果。
* **关键帧编排能力**：通过 `add_video_keyframe` 为文字、图片、视频设置位置、大小、透明度、旋转等关键帧，支持单点与批量关键帧写入。
* **云渲染与结果核验**：通过 `generate_video` 发起云渲染，再用 `task_status` 轮询任务状态。云渲染用于两类目标：创作中渲染中间结果核对预期；流程结束渲染最终成片并输出可直接播放的视频链接。
* **音画同步**：如果需要，可以利用 `get_duration` 计算素材时长，精确对齐视频轨道与音频轨道。
* **音视频预处理工具**：在编排前可优先使用基础处理端点清洗素材。`extract_audio` 可从视频中提取音频（`POST /process/extract_audio`，入参 `video_url`）；`split_video` 可按时间段切分视频或音频（`POST /process/split_video`，入参 `video_url`、`start`、`end`）。适用于替换现有视频 B-roll、素材混剪、先切段再入草稿等场景。

## 环境变量配置

所有调用均依赖于远程服务，需在环境中配置：

```bash
export VECTCUT_API_KEY="<your_token>"
```

快捷规则与请求模板见：

- `rules/`：决策规则与调用顺序
- `scripts/`：curl 请求模板与执行脚本
- `examples/`：curl 端到端示例
- `prompts/`：请求路由与命令生成提示词
- `references/`：端点参数与字段契约
- `references/references.md`：References 总索引（端点文档、回包解读、样例入口）

## 执行路由

按“能力域”路由。每个能力域复用同一条五层调用链：

1. 规则层（rules）
   - 全局：`rules/rules.md`
   - 领域：`rules/<domain>_rules.md`
2. 参数层（references）
   - 总索引：`references/references.md`
   - 端点总览：`references/endpoint_params.md`
   - 端点：`references/endpoints/<domain>.md`
   - 枚举：`references/enums/*.json`
3. 提示层（prompts）
   - 路由与请求体生成：`prompts/<domain>_ops.md`
4. 执行层（scripts）
   - 通过 curl 发起 API 请求：`scripts/<domain>_ops.sh`
5. 验证层（examples）
   - 基于 curl 的最小闭环验证：`examples/<domain>_ops_demo.sh`

### 当前已落地能力域：filter
- 规则：`rules/filter_rules.md`
- 参数：`references/endpoints/filter.md`
- 提示：`prompts/filter_ops.md`

### 当前已落地能力域：effect
- 规则：`rules/effect_rules.md`
- 参数：`references/endpoints/effect.md`
- 提示：`prompts/effect_ops.md`

### 当前已落地能力域：material
- 规则：`rules/material_rules.md`
- 参数：`references/endpoints/material.md`
- 提示：`prompts/material_ops.md`

### 当前已落地能力域：draft
- 规则：`rules/draft_rules.md`
- 参数：`references/endpoints/draft.md`
- 提示：`prompts/draft_ops.md`

### 当前已落地能力域：asr
- 规则：`rules/asr_rules.md`
- 参数：`references/endpoints/asr.md`
- 提示：`prompts/asr_ops.md`

### 当前已落地能力域：process
- 规则：`rules/process_rules.md`
- 参数：`references/endpoints/process.md`
- 提示：`prompts/process_ops.md`

### 当前已落地能力域：generate_video
- 规则：`rules/generate_video_rules.md`
- 参数：`references/endpoints/generate_video.md`
- 提示：`prompts/generate_video_ops.md`

### 当前已落地能力域：generate_speech
- 规则：`rules/generate_speech_rules.md`
- 参数：`references/endpoints/generate_speech.md`
- 提示：`prompts/generate_speech_ops.md`
- 端点：`POST /cut_jianying/generate_speech`
- 关键入参：`text`、`provider`、`model`、`voice_id`、`volume`、`target_start`、`effect_type`、`effect_params`
- 关键出参：`audio_url`、`draft_id`、`draft_url`、`material_id`

### 当前已落地能力域：generate_ai_image
- 规则：`rules/generate_ai_image_rules.md`
- 参数：`references/endpoints/generate_ai_image.md`
- 提示：`prompts/generate_ai_image_ops.md`
- 端点：`POST /cut_jianying/generate_image`
- 关键入参：`prompt`、`model`、`reference_image`、`size`、`draft_id`
- 关键出参：`output.image_url`、`output.draft_id`、`output.draft_url`

### 当前已落地能力域：generate_ai_video
- 规则：`rules/generate_ai_video_rules.md`
- 参数：`references/endpoints/generate_ai_video.md`
- 提示：`prompts/generate_ai_video_ops.md`
- 端点：`POST /cut_jianying/generate_ai_video`、`GET /cut_jianying/aivideo/task_status`
- 关键入参：
  - generate：`prompt`、`model`、`resolution`
  - status：`task_id`
- 关键出参：
  - generate：`task_id`
  - status：`status`、`progress`、`video_url`、`draft_id`、`draft_url`

### 当前已落地能力域：digital_human
- 规则：`rules/digital_human_rules.md`
- 参数：`references/endpoints/digital_human.md`
- 提示：`prompts/digital_human_ops.md`
- 端点：`POST /cut_jianying/digital_human/create`、`GET /cut_jianying/digital_human/task_status`
- 关键入参：
  - create：`audio_url`、`video_url`
  - status：`task_id`
- 关键出参：
  - create：`task_id` 或 `id`
  - status：`status`、`progress`、`video_url`

### 当前已落地能力域：video
- 规则：`rules/video_rules.md`
- 参数：`references/endpoints/video.md`
- 提示：`prompts/video_ops.md`
- 端点：`POST /cut_jianying/add_video`、`POST /cut_jianying/modify_video`、`POST /cut_jianying/remove_video`
- 关键入参：
  - add：`video_url`
  - modify/remove：`draft_id`、`material_id`
- 关键出参：`output.draft_id`、`output.draft_url`、`output.material_id`（add/modify）

### 当前已落地能力域：image
- 规则：`rules/image_rules.md`
- 参数：`references/endpoints/image.md`
- 提示：`prompts/image_ops.md`
- 端点：`POST /cut_jianying/add_image`、`POST /cut_jianying/modify_image`、`POST /cut_jianying/remove_image`
- 关键入参：
  - add：`image_url`
  - modify/remove：`draft_id`、`material_id`
- 关键出参：`output.draft_id`、`output.draft_url`、`output.material_id`（add/modify）

### 当前已落地能力域：text
- 规则：`rules/text_rules.md`
- 参数：`references/endpoints/text.md`
- 提示：`prompts/text_ops.md`
- 端点：`POST /cut_jianying/add_text`、`POST /cut_jianying/modify_text`、`POST /cut_jianying/remove_text`
- 关键入参：
  - add：`text`、`start`、`end`
  - modify：`draft_id`、`material_id`、`text`、`start`、`end`
  - remove：`draft_id`、`material_id`
- 关键出参：
  - add：`output.material_id`
  - modify/remove：`output.draft_id`、`output.draft_url`

### 当前已落地能力域：keyframe
- 规则：`rules/keyframe_rules.md`
- 参数：`references/endpoints/keyframe.md`
- 提示：`prompts/keyframe_ops.md`
- 端点：`POST /cut_jianying/add_video_keyframe`
- 关键入参：`draft_id`、`track_name`、`property_types`、`times`、`values`
- 关键出参：`output.added_keyframes_count`、`output.draft_id`、`output.draft_url`

### 新增能力域时的约定
- 域命名统一使用小写下划线：`text` / `audio` / `subtitle` / `effect` / `keyframe` / `digital_human`。
- 根文件只维护“能力域索引”，端点细节只写在对应 `<domain>.md`。
- 任意域新增端点时，只改该域文件，不改其他域。

## 交互约定（输出格式）

当你使用本技能完成“创建/编辑/渲染”类任务时，输出优先包含这些字段，便于后续继续编辑或查询：

- `draft_id`：草稿 ID
- `draft_url`：可打开的剪映/CapCut 草稿 URL，应封装为 markdown 超链接格式：`[草稿名称](draft_url)`
- `material_id`: 添加进草稿后的素材（图片、视频、音频、字幕、滤镜、贴纸、特效）的ID，方便后面继续操作

## 常用能力（可组合）

### 1) 创建草稿

调用：`POST /create_draft`

示例（1080x1920 竖屏）：

```bash
curl -X POST http://open.vectcut.com/cut_jianying/create_draft \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"width":1080,"height":1920,"name":"demo"}'
```

### 2) 添加素材与时间线编排

你可以按需组合以下操作（都为 `POST` JSON）：

- `/add_video`：添加视频（支持裁切、速度、变换、蒙版、混合、转场等）
- `/modify_video`：修改视频（基于 `material_id` 更新视频源、裁切区间、位置与速度）
- `/remove_video`：删除视频（基于 `material_id` 删除视频素材）
- `/add_image`：添加图片（支持入/出场动画、转场、蒙版、混合等）
- `/modify_image`：修改图片（基于 `material_id` 更新图片源、时长、位置、动画与样式）
- `/remove_image`：删除图片（基于 `material_id` 删除图片素材）
- `/add_audio`：添加音频（支持音量、变速、淡入淡出、音效等）
- `/add_text`：添加文字（支持字体、描边、阴影、背景、动画、多样式范围等）
- `/modify_text`：修改文字（基于 `material_id` 更新文案、时间段与样式）
- `/remove_text`：删除文字（基于 `material_id` 删除文本素材）
- `/add_sticker`：添加贴纸
- `/add_effect`：添加特效（scene/character）
- `/add_filter`：添加滤镜
- `/add_video_keyframe`：添加关键帧（支持位置、大小、透明度、旋转等属性）
- `/get_video_scene_effect_types`：获取场景特效（用于 effect_category=scene）
- `/get_video_character_effect_types`：获取人物特效（用于 effect_category=character）
- `/get_filter_types`：添加滤镜

### 3) 高级能力（AI 与搜索）

- `/generate_image`：AI 图片生成并添加到草稿（支持文生图/图生图，聚合模型：nano_banana_2、nano_banana_pro、jimeng-4.5）
- `/generate_ai_video`：AI 视频生成（支持文生视频/图生视频/部分模型首尾帧，异步任务）
- `/aivideo/task_status`：查询 AI 视频生成任务状态与视频结果
- `/digital_human/create`：创建数字人口播任务（音频 + 视频输入）
- `/digital_human/task_status`：查询数字人任务状态与结果
- `/generate_speech`：TTS 语音合成并添加到草稿
- `/llm/tts/fish/clone_voice`：克隆音色并返回 `voice_id`（可用于后续 `generate_speech`）
- `/llm/tts/voice_assets`：查询已克隆音色资产（支持 `provider=minimax|fish|NULL`）
- `/remove_bg`：智能抠像（移除背景）并生成合成预设
- `/search_sticker`：搜索在线贴纸素材

### 4) 获取可用枚举（动画/转场/特效/滤镜/字体）

用于让 AI 在可用范围内选型：

- `GET /get_transition_types`
- `GET /get_mask_types`
- `GET /get_intro_animation_types`、`/get_outro_animation_types`、`/get_combo_animation_types`
- `GET /get_text_intro_types`、`/get_text_outro_types`、`/get_text_loop_anim_types`
- `GET /get_video_scene_effect_types`、`/get_video_character_effect_types`
- `GET /get_filter_types`
- `GET /get_font_types`
- `GET /get_audio_effect_types`

示例（以转场枚举为例）：

```bash
curl -X GET "http://open.vectcut.com/cut_jianying/get_transition_types" \
  -H "Authorization: Bearer $VECTCUT_API_KEY"
```

### 4) 云渲染（中间核验 + 最终交付）

- `POST /generate_video`：对草稿 `draft_id` 发起云渲染（返回 `task_id`）。
- `POST /task_status`：轮询 `task_id` 获取渲染进度与结果。
- 创作过程中：可按关键里程碑发起渲染，核对当前画面、节奏、字幕与预期是否一致。
- 任务结束时：必须轮询到完成态，并把结果中的可播放视频链接作为最终输出返回。

### 5. 典型场景示例

#### 场景 A：成语故事/绘本视频制作（文生图 + 配音 + 自动对齐）

当用户需要制作“亡羊补牢”这样的故事视频时，建议按以下逻辑编排：

1.  **分镜拆解**：将故事拆分为 N 个片段（图片 Prompt + 旁白文本）。
2.  **生成循环**（对每个片段）：
    *   调用 `generate_image` 生成插图，获得 `image_url`。
    *   调用 `generate_speech` 生成配音，获得 `audio_url`。
    *   **关键点**：调用 `get_duration(url=audio_url)` 获取配音时长 `duration`。
    *   调用 `add_image`，将 `image_url` 加入草稿，并设置 `duration` 等于配音时长，确保音画同步。
    *   （如果 `generate_speech` 未自动添加）调用 `add_audio` 添加配音。

参考 Prompt 模板：`assets/prompts/story_creation_zh.md`

#### 场景 B：素材混剪

1) 创建草稿 → 2) add_video/add_audio/add_text → 3) generate_video 发起云渲染 → 4) task_status 轮询直到可取播放链接

```bash
curl -X POST http://open.vectcut.com/cut_jianying/create_draft \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -d '{"name":"my short"}'
```

假设返回 `draft_id=xxx` 后：

```bash
curl -X POST http://open.vectcut.com/cut_jianying/add_video \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"draft_id":"xxx","video_url":"https://example.com/a.mp4","start":0,"end":10,"target_start":0}'
```

发起渲染：

```bash
curl -X POST http://open.vectcut.com/cut_jianying/generate_video \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"draft_id":"xxx","resolution":"1080P","framerate":"30"}'
```

轮询：

```bash
curl -X POST http://open.vectcut.com/cut_jianying/task_status \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"task_id":"TASK_ID"}'
```

## 使用提示（让 AI 更“会剪”）

- 让用户提供素材 URL、期望时长、画面比例（9:16/16:9/1:1）、字幕风格、BGM 风格
- 需要更细粒度理解时，调用 `video_detail` 理解（关系/朝向/位置/声音风格），再据此做镜头衔接、特效与字幕排版决策
- 需要严格可控的效果时，先拉取枚举（转场/特效/滤镜/字体），再进行选择与组装
- 复杂需求可以在上层自己组织调用顺序，这里只负责暴露基础视频编辑与渲染接口
