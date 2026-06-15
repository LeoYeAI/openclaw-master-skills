# 故事/绘本视频制作 Prompt

当你需要制作一个成语故事、绘本或叙事短视频时，请遵循以下 SOP（标准作业程序）进行编排：

## 1. 故事拆解与分镜设计

首先，将用户的主题（如“亡羊补牢”）拆解为 4-6 个关键情节。
对于每个情节，生成以下内容：
- **画面描述 (Image Prompt)**：用于 AI 生图的英文提示词，包含主体、环境、动作、风格（如 "illustration style, flat design, a broken sheepfold with a hole, sheep missing"）。
- **旁白文本 (Voiceover Text)**：用于 TTS 的中文文本（如“从前有个人，养了几只羊。一天早上他发现少了一只羊，原来羊圈破了个窟窿。”）。

## 2. 执行循环 (Step-by-Step Execution)

对每个分镜，按顺序执行以下工具调用。请确保上一步的输出作为下一步的输入：

### Step 2.1: 生成素材
1. **生成图片**：
   - 调用 `generate_image(prompt="...", draft_id=CURRENT_DRAFT_ID)`
   - 记录返回的 `image_url`。
2. **生成配音**：
   - 调用 `generate_speech(text="...", draft_id=CURRENT_DRAFT_ID)`
   - 记录返回的 `audio_url`。

### Step 2.2: 获取时长 (关键步骤)
由于图片是静态的，必须让图片的显示时长完全覆盖配音的时长。
1. **获取音频时长**：
   - 调用 `get_duration(url=audio_url)`
   - 记录返回的 `duration` (秒)。

### Step 2.3: 合成到草稿
1. **添加图片到轨道**：
   - 调用 `add_image`
   - 参数：
     - `draft_id`: CURRENT_DRAFT_ID
     - `image_url`: Step 2.1 获得的图片 URL
     - `track_name`: "image_main"
     - `duration`: Step 2.2 获得的 `duration` (这会确保图片展示时长与配音一致)
     - `intro_animation`: 可选，添加简单的入场动画如 "fadeIn"
2. **添加音频到轨道**（注：generate_speech 若已自动添加到草稿，此步可跳过；若仅返回 URL，则需手动添加）：
   - 调用 `add_audio`
   - 参数：
     - `audio_url`: Step 2.1 获得的音频 URL
     - `duration`: Step 2.2 获得的 `duration`

## 3. 示例流程 (伪代码)

```python
# 1. 创建草稿
draft = create_draft(name="亡羊补牢")
draft_id = draft.id

# 2. 分镜循环
scenes = [
  { "text": "从前...", "prompt": "..." },
  { "text": "第二天...", "prompt": "..." }
]

for scene in scenes:
    # 并行生成素材
    img_res = generate_image(prompt=scene.prompt, draft_id=draft_id)
    speech_res = generate_speech(text=scene.text, draft_id=draft_id)
    
    # 获取配音时长用于控制图片
    # 注意：generate_speech 如果已经把音频加进去了，我们只需要拿它的时长来调整图片
    # 或者我们先不让 generate_speech 自动加(如果不传draft_id)，手动加以便排版
    
    duration_res = get_duration(url=speech_res.audio_url)
    duration = duration_res.duration
    
    # 添加图片，时长 = 配音时长
    add_image(
        draft_id=draft_id,
        image_url=img_res.image_url,
        duration=duration
    )
    
    # 如果 generate_speech 没自动加，手动加音频
    # add_audio(...)
```
