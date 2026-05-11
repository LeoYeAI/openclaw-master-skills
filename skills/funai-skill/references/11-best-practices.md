# 最佳实践指南

## 1. 先把真实后端理解成“两层状态机”

### 第一层：项目级步骤

看：

```http
GET /service/workflow/project/{projectId}
```

关注：

- `workflow.currentStep`

### 第二层：章节级隐藏任务

看：

```http
GET /service/workflow/resource/comicPreset/{presetResourceId}
```

关注：

- `sceneCaptionsTaskStatus`
- `dialogTaskStatus`
- `sceneTaskStatus`

### 结论

只有这两层都满足，才可以安全推进到下一步。

---

## 2. 创建项目前必须先走 select-options

```http
POST /service/workflow/project/story/select-options
```

Agent 应该这样做：

1. 读取实时可选项
2. 如果用户没有明确要求切换模式，则静默使用默认 `generateType / scriptType`
3. 但必须让用户明确选择 `aspect / style`
4. `model / videoModel` 若用户没有额外要求，可继续使用 API 返回的当前默认值
5. 面向自检脚本时，用返回结果中的默认值自动构造 payload

不要这样做：

- 直接写死 `现代写实`
- 直接写死 `doubao-seedream-3.0`
- 直接写死 `16:9`

也不要这样做：

- 在用户没问的情况下主动解释“现在默认是文生图 / 解说漫模式”
- 在用户没确认时替他决定 `aspect / style`

---

## 3. 提交剧本时要安全构造 JSON

剧本内容通常包含：

- 多行换行
- 中文引号 / 英文引号
- 冒号、括号、场景说明

因此：

- 要使用 `jq -n`、结构化 JSON builder 或语言内 JSON 编码器
- 不要做 shell 字符串拼接 JSON

### 复杂场景下的更稳做法

如果同时满足以下任一情况：

- 多行正文
- 中文 prompt
- 带 `jq` 过滤器的嵌套命令
- `bash -lc` 再嵌套 `source ... && ...`
- 批量循环多个 scene

优先考虑：

- 用 JSON 临时文件承载输入
- 或直接用 Python 包一层，再调用 shell helper

不要把大量中文 prompt、引号、括号、`@[人物](id:xxxx)` 和 `jq` 表达式硬拼在一条 shell 命令里。

### 如果是 AI 代写剧本

当当前走的是解说剧 / 解说漫模式时，AI 代写剧本必须写成**旁白叙述式小说体**，而不是分镜脚本。

避免：

- `镜头1`
- `旁白：...`
- `某某说：...`
- `【音效：脚步声】` / `砰！` / `哗啦——`
- 条目式镜头表

要写成：

- 连续的故事正文
- 以旁白讲述式叙事推进
- 允许少量自然对白，但不要出现台本标签与音效描述
- 适合平台后续自动拆角色、分镜、解说

---

## 4. 角色步骤前先等角色图完成

先调：

```http
GET /service/workflow/comic/roles/{presetResourceId}
```

只有当：

- `roles[].taskStatus == SUCCESS`
- `roles[].imgUrl` 非空

才继续 `novel_extract_roles`。

然后把 live 返回的 `voiceInputs[0]` 一起传进去。

---

## 5. 智能分镜和推进成片都存在隐藏章节门槛

### 执行 `novel_scene_captions` 前

先等：

```text
sceneCaptionsTaskStatus == SUCCESS
```

### 执行 `novel_chapter_scenes` 前

先等：

```text
sceneTaskStatus == SUCCESS
```

### 常见误区

误区：

```text
dialogTaskId 轮询成功了 -> 一定可以下一步
```

正确做法：

```text
dialogTaskId 轮询成功
→ 再看 comicPreset 章节字段
→ sceneTaskStatus=SUCCESS 后再推进
```

---

## 6. `sceneUuid` 不是 `sceneId`

如果要调分镜图 / 视频相关 API，必须使用完整 `sceneId`。

正确获取流程：

```text
GET /resource/comicPreset/{presetResourceId}
→ chapters[].sceneTaskId

GET /task/{sceneTaskId}
→ resourceId = storyboardId

GET /resource/{storyboardId}
→ scenes[].id = 完整 sceneId
```

---

## 7. 成片配置用 `getVideoSetting` 作为权威来源

在保存成片配置前，推荐顺序：

1. `POST /storyboard/prepareVideoComposite`
2. `GET /storyboard/getVideoSetting?...`
3. 用 `getVideoSetting` 返回的 `coverList` / `selectCover` / `selectMusicId` 等字段构造保存请求
4. `POST /storyboard/saveVideoComposeConfig`

### 这一步只是“成片设置”，不是最终视频已完成

进入 `novel_chapter_video` 后，先要分清两件事：

1. **成片设置阶段**：封面、字幕、背景音乐、标题等配置
2. **视频合成阶段**：真正调用 `project/step/action` 触发合成任务

不要把这两个阶段混成一个步骤。

只有视频合成任务成功后，用户才真正能看到最终成片。

### 回退后的最佳实践

如果从 `novel_chapter_video` 回退去调整分镜图或视频路径：

- 不要把旧的视频结果当作仍然有效
- 回退后重新进入成片步骤时，按“设置 → 合成”重新走一遍
- 把“需要重新合成视频”明确告诉用户

最容易漏掉的字段是：

- `coverList`
- `selectCover`
- `selectCoverUrl`

---

## 8. 梦想值相关动作必须先确认

必须先征得用户同意的动作：

1. 批量转视频
2. 单张图转视频
3. 重绘分镜图

### 推荐确认文案

```markdown
⚠️ 以下操作会消耗梦想值：
- 操作：批量转视频
- 数量：14 个场景

是否继续？[确定/取消]
```

---

## 9. 对用户输出要像“简报”，不是流水账

每完成一个大步骤，应告诉用户：

1. 刚刚完成了什么
2. 产出了什么关键结果
3. 下一步准备做什么
4. 如果当前步骤支持修改，是否需要修改当前结果
5. 是否确认继续下一步

如果项目已创建，优先附上项目链接。

### 不要默认一路自动执行到底

正确节奏：

```text
完成一步
→ 汇报结果
→ 等用户确认
→ 再继续下一步
```

只有以下技术动作可以不单独停下：

- task 轮询
- 资源读取
- `sceneId` / `storyboardId` 解析
- readiness 检查
- 必要的步骤回退

但任何新的用户可感知结果出来后，都必须停下来。

---

## 10. 审图时优先检查这几类视觉偏差

如果当前 Agent / 模型具备多模态看图能力，建议每次在重生图或重生视频后，优先检查：

1. **主体是否抢戏 / 跑偏**
   - 旁白主角是否被路人、背景人物、道具夺走视觉重心
2. **角色年龄是否跑偏**
   - 明明应是青年，却被画得偏幼或偏老
3. **角色设定是否被误画成真人/路人**
   - 例如 AI 助手 / 系统类角色是否应该更像全息投影，而不是真人站桩
4. **场景主体是否和旁白一致**
   - 开场应是城景，却被画成海报感摆拍；重点动作被忽略
5. **视频问题到底来自图还是来自动作/运镜**
   - 如果基础图不对，先回到图片侧改 `sceneDescription/prompt`
   - 如果基础图是对的，再改视频侧 `prompt/cameraPrompt`

把问题先归类，再改 prompt，通常比盲目多试几次更稳。

### 三个必须停下来的确认节点

1. **小说 / 剧本完成后**
   - 把剧本正文回给用户
   - 询问是否修改剧情、风格、节奏

2. **角色完成后**
   - 把角色图片回给用户
   - 如果当前仍停留在 `novel_extract_roles`，应允许用户提出修改角色形象
   - 若用户要求修改，必须先生成新图、等待新图成功、再显式 apply，并把新的图片 URL 返回给用户
   - 用户确认无误后，再继续下一步

3. **场景 / 分镜完成后**
   - 把场景描述回给用户
   - 若有图像结果，则一并给出图像或项目链接查看方式
   - 明确询问是“继续转视频”还是“直接进入成片”
   - 不要默认替用户选择其中一条路径

这三个节点都不能跳过确认直接继续。

---

## 10. 视频返回优先使用 `videoPlayUrl`

如果 scene 视频或最终成片资源里已经返回：

- `videoPlayUrl`

则应把这个 `videoPlayUrl` 作为唯一的对外视频链接回给用户。

不要在高层 helper、示例脚本或模型可见输出里继续暴露原始视频 `url`。

---

## 11. 图转视频时优先使用 scene 当前基准分镜图

最佳做法：

```text
GET /storyboard/scene/{sceneId}/prompt/detail?sceneId={sceneId}
→ 取 video.imageId

GET /storyboard/scene/{sceneId}/resources
→ 找到 resourceId == video.imageId 的 image
→ firstImage = image.url
→ imageId = image.resourceId
```

不要这样做：

```text
GET /comic/roles/{presetResourceId}
→ firstImage = roles[].imgUrl
→ imageId = roles[].imageResourceId
```

原因不是“后端一定会拒绝”，而是更糟糕：

- 后端可能返回 `200 success`
- 但生成出来的是和当前分镜不匹配的视频

换句话说，这属于**语义错误**，不是可靠的参数校验错误。

---

## 12. 回退后的正确继续方式

如果用户在成片步骤要求继续做生图 / 生视频：

1. 先 `step/prev` 回退到 `novel_chapter_scenes`
2. 再确认 `sceneTaskStatus == SUCCESS`
3. 再确认当前 scene 有可用的基准 image（优先 `video.imageId` 对应项）
4. 然后才发起 `scene/ai/image` 或 `scene/ai/video`

live 测试中，回退后章节的 `currentSubStep` 仍可能保留在 `video`，这不代表失败。

真正要看的仍然是：

- `workflow.currentStep`
- `sceneTaskStatus`
- scene 当前 image 资源
