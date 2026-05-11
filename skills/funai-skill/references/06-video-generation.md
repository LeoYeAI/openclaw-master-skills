# 视频生成与成片合成 API

## 目录

- [重要约束](#重要约束)
- [获取视频模型列表](#获取视频模型列表)
- [单场景生图](#单场景生图)
- [单场景图转视频](#单场景图转视频)
- [检查批量 AI 视频状态](#检查批量-ai-视频状态)
- [准备成片](#准备成片)
- [获取视频设置](#获取视频设置)
- [保存视频合成配置](#保存视频合成配置)
- [执行视频合成](#执行视频合成)

---

## 重要约束

### 1. 生图 / 生视频必须在分镜图步骤下执行

如果项目当前位于：

- `novel_chapter_scenes` → 可以继续分镜图相关操作
- `novel_chapter_video` → 需要先回退到分镜图步骤

### 2. 推进到成片前，还要检查 `sceneTaskStatus`

仅凭 `currentStep = novel_chapter_scenes` 还不够。

要继续推进到成片，还需要：

```text
GET /resource/comicPreset/{presetResourceId}
→ chapters[].sceneTaskStatus == SUCCESS
```

如果没等这个字段成功，直接调用 `step=novel_chapter_scenes` 常见报错是：

```text
该章节分镜图任务未完成，请稍后再试
```

### 3. `check/batchAiVideo` 只是查询，不是执行

这个接口只告诉你还有多少张图没有转为动态视频。

不要把它误认为“已经开始转视频”。

### 4. 分镜图完成后，必须先问用户是“转视频”还是“直接成片”

默认更省的路径是直接进入成片合成。

但在真正调用任何图转视频相关接口前，Agent 必须先问用户：

1. 是否要把分镜图继续转为视频
2. 还是直接进入成片界面合成

只有在用户明确选择“转视频”后，才继续执行 `scene/ai/video` 或批量转视频相关流程。

### 5. 进入成片步骤后，要区分“设置阶段”和“合成阶段”

当章节进入 `novel_chapter_video` 时，通常先进入的是：

- `currentSubStep = setting`

这表示用户还处在：

- 封面设置
- 字幕设置
- 背景音乐设置
- 以及生成视频前的相关参数确认

此时还没有真正开始视频合成。

---

## 获取视频模型列表

### 请求

```http
GET /service/workflow/storyboard/scene/ai/video/modelList?app=story&style=现代写实
```

### 说明

用于获取当前 style 下可选的视频模型和时长 / 清晰度能力。

---

## 单场景生图

### 请求

```http
POST /service/workflow/storyboard/scene/ai/image
```

### 重要说明

1. `sceneId` 必须是完整 ObjectId。
2. 这是消耗梦想值的操作，先征得用户同意。
3. prompt 构造建议来源于 `prompt/detail` 的当前结果，而不是手写猜测值。

---

## 单场景图转视频

### 请求

```http
POST /service/workflow/storyboard/scene/ai/video
```

### 重要说明

1. `sceneId` 必须是完整 ObjectId。
2. `firstImage` 必须保留完整 URL，尤其是带签名的长链接不能截断。
3. 这是消耗梦想值的操作，先征得用户同意。
4. `firstImage` / `imageId` 必须来自当前 scene 的基准分镜图资源。
5. `prompt` 与 `cameraPrompt` 分别对应“动作”和“运镜”，这里应直接写纯文本，不要再使用 `@[人物](id:xxxx)` 这类图片侧引用。
6. 如果 `GET /storyboard/scene/{sceneId}/resources` 返回的 `type=video` 资源里存在 `videoPlayUrl`，应优先把它返回给用户直接播放。

live 联调补充：如果图片侧 prompt 里乱写不存在的 `@[人物](id:xxxx)`，后端会直接返回“提示词引用的角色不存在”；而视频侧应直接避免使用这类结构。

### 正确图片来源

正确来源：

```text
GET /storyboard/scene/{sceneId}/resources
→ resourceId == prompt/detail.video.imageId 的 image.url / resourceId
```

GET /storyboard/scene/{sceneId}/prompt/detail?sceneId={sceneId}
→ video.imageId

错误来源：

```text
GET /comic/roles/{presetResourceId}
→ roles[].imgUrl / roles[].imageResourceId
```

### live 测试结论

后端并不会稳定地用参数校验帮你拦住“拿错图”这类错误。

实测结果：

- 传 `roles[].imgUrl + roles[].imageResourceId` 时，接口返回了 `200 success`，并真的生成出了一条 video 资源
- 但那条视频的 `videoCover` 对应的是角色图，不是当前分镜图，因此属于**语义错误但接口成功**

因此，文档应把这件事理解为：

> 必须主动选 scene 当前的基准分镜图，否则可能成功返回 200，但视频内容错误。

更准确地说：

> 必须主动选 scene 当前的基准分镜图（优先 `video.imageId` 对应的 image 资源），否则可能成功返回 200，但视频内容错误。

### 经过 live 验证的请求体形态

```json
{
  "sceneId": "69b5645d284bb64353bb44cd",
  "prompt": "来自 prompt/detail 的视频提示词",
  "cameraPrompt": "来自 prompt/detail 的镜头提示词",
  "model": "doubao-pro",
  "duration": "-1",
  "firstImage": "https://img.ibidian.com/sdw?oid=49f7848e4fcee56e9efa97b771754043&w=0&h=0",
  "tailImage": "",
  "clarity": "720p",
  "imageId": "69b5646666705a232968df9a"
}
```

### 迭代调整时如何改提示词

如果用户对视频不满意，Agent 应优先区分问题属于：

- **动作问题** → 调整 `prompt`
- **运镜问题** → 调整 `cameraPrompt`
- **画面基础就不对** → 先回到图片侧调整 `sceneDescription / prompt` 重生图，再重新图转视频

推荐顺序：

```text
先判断问题是图的问题还是视频的问题
→ 图的问题：先重生图
→ 视频的问题：直接改动作/运镜重新生成视频
→ 再把新结果回给用户确认
```

### 多模态 Agent 的可选增强

如果当前 Agent / 模型具备看图能力，可在每次重生图或重生视频后增加一轮视觉自检：

- 对图片：看当前 `selected=true` 的 image.url
- 对视频：优先看当前 video 的 `videoCover`

若发现用户目标与画面仍有明显偏差，可针对性地调整：

- 构图 / 场景氛围 / 环境信息 → 回到 `sceneDescription`
- 主体动作 / 表情 / 姿态 / 人物位置 → 调整图片侧 `prompt`
- 连贯动作 / 运动表现 → 调整视频侧 `prompt`
- 镜头推进 / 转场 / 角度变化 → 调整 `cameraPrompt`

---

## 检查批量 AI 视频状态

### 请求

```http
POST /service/workflow/storyboard/check/batchAiVideo
```

### 请求体

```json
{
  "storyBoardId": "storyboardId"
}
```

### 响应关键字段

| 字段 | 说明 |
|------|------|
| `noVideoCount` | 还有多少场景未转为动态视频 |
| `subTitle` | 当前平台给出的文案提示 |

### 用途

用于在执行高消耗动作前，先评估代价并向用户确认。

---

## 准备成片

### 请求

```http
POST /service/workflow/storyboard/prepareVideoComposite
```

### 请求体

```json
{
  "projectId": "项目ID",
  "chapterNum": 1
}
```

### 重要说明

这个接口更像一次“合成前检查”。

当前已验证的正确请求体只有：

```json
{
  "projectId": "项目ID",
  "chapterNum": 1
}
```

不要误传：

- `storyboardId`
- `userProjectId`
- `type`

在 live 验证中，错误 payload 会返回：

```text
400 / 参数校验异常: must not be blank
```

在 live 自检中，它可能只返回轻量信息，例如：

```json
{"clarityList": []}
```

因此不要把它当作完整的成片配置来源。

---

## 获取视频设置

### 请求

```http
GET /service/workflow/storyboard/getVideoSetting?userProjectId={projectId}&type=2&chapterNum=1
```

### 这是保存成片配置的权威来源

重点读取：

- `coverList`
- `selectCover`
- `selectMusicId`
- `selectTitleFont`
- `selectSubtitleFont`
- `title`
- `bgmVolume`

这一步仍属于**成片设置阶段**。

---

## 保存视频合成配置

### 请求

```http
POST /service/workflow/storyboard/saveVideoComposeConfig
```

### 推荐请求体（权威形态）

```json
{
  "selectCover": "封面ID",
  "coverList": [
    {"coverId": "封面ID", "coverUrl": "https://..."}
  ],
  "selectMusicId": "prepared-001",
  "selectTitleFont": "font0",
  "selectSubtitleFont": "font1",
  "title": "视频标题",
  "bgmVolume": 0.15,
  "type": 2,
  "chapterNum": 1,
  "userProjectId": "项目ID",
  "selectCoverUrl": "https://..."
}
```

### 最容易漏掉的字段

- `coverList`
- `selectCover`
- `selectCoverUrl`

如果缺少这些字段，常见报错是：

```text
请选择封面
```

### 最稳妥的做法

1. 先调 `getVideoSetting`
2. 直接复用它返回的 `coverList` / `selectCover` 等字段
3. 只补齐 `userProjectId`、`chapterNum`、`type`

live 测试确认：

- `saveVideoComposeConfig` 成功后，章节仍可能保持 `currentSubStep = setting`
- 因此这一步表示“设置保存成功”，不是“视频已经开始合成”

---

## 执行视频合成

### 请求

```http
POST /service/workflow/project/step/action
```

### 请求体

```json
{
  "userProjectId": "项目ID",
  "step": "novel_chapter_video",
  "inputs": [
    {"type": "number", "name": "chapterNum", "value": 1},
    {"type": "text", "name": "needAiWatermark", "value": "1"},
    {"type": "text", "name": "clarity", "value": "720p"}
  ]
}
```

### 响应说明

通常会返回：

- `resultType = task`
- `resultId = 合成任务ID`

live 测试还确认：

- 这个新的 `resultId` 会同步成为章节新的 `videoTaskId`
- `currentSubStep` 会从 `setting` 进入 `video`

然后轮询：

```http
GET /service/workflow/task/{resultId}
```

成功后，再用 `resourceId` 去读最终视频资源。

### 只有合成成功后，最终成片才真正可见

这一步要特别写清楚：

- 进入 `novel_chapter_video` ≠ 用户已经能看到最终成片
- 保存封面 / 字幕 / 背景音乐 ≠ 用户已经能看到最终成片
- 只有 `project/step/action` 触发的视频合成任务 `SUCCESS` 后，用户才能看到最终成片

### 重要说明

如果最终视频资源 `GET /resource/{resourceId}` 里存在 `data.videoPlayUrl`，对外应只返回这个 `videoPlayUrl`。

原始 `data.url` 不应继续出现在高层 helper、示例脚本或模型可见输出中；项目链接可以作为补充入口一起返回。

---

## 回退到分镜图步骤后再执行图转视频

如果当前 `workflow.currentStep = novel_chapter_video`，先调用：

```json
POST /service/workflow/project/step/prev
{
  "userProjectId": "项目ID",
  "step": "novel_chapter_video",
  "chapterNum": 1
}
```

live 测试确认：

- 回退成功后 `workflow.currentStep` 会变成 `novel_chapter_scenes`
- 章节 `currentSubStep` 可能仍显示 `video`
- 这不影响继续执行 `scene/ai/video`
- 如果省略 `chapterNum`，live 会返回：`400 / 章节序号无效`

真正要继续执行前，应确认：

- `sceneTaskStatus == SUCCESS`
- scene 已有可用的基准 image 资源（优先 `video.imageId` 对应项）

### 回退后为什么必须重新合成

live 测试里，同一个项目在：

1. 第一次合成成功后，得到一个 `videoTaskId`
2. 回退到 `novel_chapter_scenes`
3. 再次进入 `novel_chapter_video` 并重新合成

会产生：

- 新的 `videoTaskId`
- 新的最终视频 `resourceId`

因此：

> 每次回退调整完之后，都必须重新合成视频，用户才能重新看到新的成片结果。
