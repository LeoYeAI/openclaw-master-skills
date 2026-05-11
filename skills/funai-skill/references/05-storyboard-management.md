# 分镜管理 API

## 目录

- [重要约束](#重要约束)
- [获取分镜场景列表](#获取分镜场景列表)
- [获取 Storyboard 资源详情](#获取-storyboard-资源详情)
- [获取场景 Prompt 详情](#获取场景-prompt-详情)
- [获取场景资源](#获取场景资源)
- [重绘分镜图](#重绘分镜图)
- [查询分镜 AI 任务状态](#查询分镜-ai-任务状态)

---

## 重要约束

### 1. 不要把 `sceneUuid` 当 `sceneId`

`scene-list` 返回的 `sceneUuid` 只是短 ID，不能直接用于需要完整 `sceneId` 的接口。

### 2. 章节分镜图 readiness 由 `sceneTaskStatus` 决定

在章节流程里，Agent 不能只看到 `currentStep = novel_chapter_scenes` 就继续推进。

还要看：

```http
GET /service/workflow/resource/comicPreset/{presetResourceId}
```

中的：

```text
chapters[].sceneTaskStatus == SUCCESS
```

只有这个字段成功后，才能安全把章节推进到成片步骤。

### 3. 生图 / 生视频必须在分镜图步骤下执行

如果 `workflow.currentStep = novel_chapter_video`，应先回退到 `novel_chapter_scenes`。

### 4. 不要把 `roles[].imgUrl` 当成图转视频的 `firstImage`

图转视频时，真正应该使用的是当前 scene 的基准分镜图资源：

```text
GET /storyboard/scene/{sceneId}/prompt/detail?sceneId={sceneId}
→ video.imageId

GET /storyboard/scene/{sceneId}/resources
→ resourceId == video.imageId 的 image 资源
```

不要用：

```text
GET /comic/roles/{presetResourceId}
→ roles[].imgUrl
```

live 测试表明，后端可能会接受角色图并返回 `200 success`，但这样生成的是**语义错误的视频**，而不是可靠地报错。

---

## 获取分镜场景列表

### 请求

```http
GET /service/workflow/storyboard/project/{projectId}/scene-list?chapterNum=1
```

### 重要说明

这个接口适合查看场景列表与字幕概览，但其中的：

```text
stories[].sceneUuid
```

不是完整 `sceneId`。

如果后续还要调用 prompt/detail、scene/ai/image、scene/ai/video 等接口，应继续解析完整 sceneId。

---

## 获取 Storyboard 资源详情

### 请求

```http
GET /service/workflow/resource/{storyboardId}
```

### `storyboardId` 的正确获取方式

```text
GET /resource/comicPreset/{presetResourceId}
→ chapters[].sceneTaskId

GET /task/{sceneTaskId}
→ data.resourceId = storyboardId

GET /resource/{storyboardId}
→ data.data.scenes[].id = 完整 sceneId
```

### 响应关键字段

| 字段 | 说明 |
|------|------|
| `data.data.scenes[]` | 场景列表 |
| `data.data.scenes[].id` | 完整 `sceneId` |
| `data.data.scenes[].image` | 当前基准分镜图 |
| `data.data.scenes[].imageResourceId` | 图片资源 ID |

---

## 获取场景 Prompt 详情

### 请求

```http
GET /service/workflow/storyboard/scene/{sceneId}/prompt/detail?sceneId={sceneId}
```

### 重要说明

这里的 `sceneId` 必须使用完整 ObjectId 格式，不能使用 `sceneUuid`。

这个接口通常用来读取：

- 图片 prompt（`image.imagePromptInfo.screen_description` + `image.imagePromptInfo.subject_description`）
- 视频 prompt（`video.prompt` = 动作，`video.cameraPrompt` = 运镜）
- 场景内角色引用（`image.roles[]`）
- 当前模型信息（`image.model` / `video.model`）

### 重生图时的真实提示词结构

分镜图页面中的图片提示词不是单字段，而是两段共同组成：

- `sceneDescription` = `image.imagePromptInfo.screen_description`
- `prompt` = `image.imagePromptInfo.subject_description`

其中 `prompt` 里可能出现：

```text
@[李明](id:1001)
```

这不是普通文本装饰，而是前端用于保持人物一致性的 live 引用。

如果要重生图：

- 应在保留这类引用结构的前提下调整描述
- 不要把它简单删掉再改成纯名字文本
- 更不能随意编造一个当前 scene 并不存在的 `id`；`@[人物](id:xxxx)` 必须与 `image.roles[]` 里的 live 角色 ID 一致，否则后端会直接报“提示词引用的角色不存在”

### 场景确认阶段如何向用户回报

当场景 / 分镜已经生成完成并准备等待用户确认时，应至少向用户回报：

- 场景名称或场景编号
- 场景描述
- 如已有可视化结果，则补充分镜图或项目链接查看方式

不能只告诉用户“场景已完成”，而不把场景描述回给用户。

### 场景确认后的下一步提问

当分镜图已经生成完成时，Agent 不能默认直接进入成片。

必须明确询问用户二选一：

1. 是否继续把分镜图转为视频
2. 还是直接进入“成片”界面，用当前分镜图直接合成

---

## 获取场景资源

### 请求

```http
GET /service/workflow/storyboard/scene/{sceneId}/resources
```

### 用途

查看该 scene 当前有哪些图片/视频资源，以及哪个资源被选中。

### 响应中常见字段

| 字段 | 说明 |
|------|------|
| `resourceId` | 图片或视频资源 ID |
| `type` | `image` / `video` |
| `url` | 资源原始 URL，仅底层资源结构可见；不要直接对外返回 |
| `videoPlayUrl` | scene 级视频可直接播放的链接，通常仅 `type=video` 时存在 |
| `taskStatus` | 资源生成状态 |
| `selected` | 是否被当前章节采用 |

### 对外返回规则

如果上层逻辑要把 scene 视频链接返回给用户：

- 只返回 `videoPlayUrl`
- 不要把 `url`、`scenes[].video` 这类原始视频地址直接回给用户

### 图转视频时的正确取值规则

- `firstImage = 与 prompt/detail.video.imageId 对应的 image.url`
- `imageId = 与 prompt/detail.video.imageId 对应的 image.resourceId`

如果当前 resources 里找不到这个基准 image，再停止图转视频，不要任意拿第一张图顶上。

---

## 重绘分镜图

### 请求

```http
POST /service/workflow/storyboard/scene/ai/image
```

### 重要说明

1. 调用前先确认项目当前位于 `novel_chapter_scenes`。
2. `sceneId` 必须是完整 ObjectId。
3. `roles` 应优先直接使用 `prompt/detail` 返回的 `image.roles[]` live 数据。
4. 这是消耗梦想值的动作，应先征得用户同意。

### 经抓包验证的请求体形态

```json
{
  "sceneId": "完整sceneId",
  "roles": [
    {
      "id": 1001,
      "resourceId": "角色资源ID",
      "realName": "李明",
      "imgUrl": "https://...",
      "gender": "male",
      "appearance": "...",
      "ipRoleId": 299098,
      "imageResourceId": "角色主图资源ID",
      "age": "青年",
      "styleId": 10543,
      "voiceId": 10025
    }
  ],
  "imgGenType": "1",
  "promptV2": {
    "screen_description": "新的场景提示词",
    "subject_description": "新的图片提示词，允许保留 @[人物](id:xxxx)"
  },
  "model": "doubao-seedream-3.0"
}
```

### live 行为补充

与角色改图不同，分镜图重生图在 live 抓包里表现为：

- 新图生成时先以 `selected=false`、`taskStatus=RUNNING` 出现
- 生成完成后，新图会自动切换为 `selected=true`
- 没看到额外的 apply/select 请求

因此在 Agent 侧的完成判定应是：

1. 新 image 资源 `SUCCESS`
2. 新 image 资源 URL 非空
3. 新 image 资源 `selected=true`

---

## 查询分镜 AI 任务状态

### 请求

```http
GET /service/workflow/storyboard/scene/ai-task/status?storyBoardId={storyBoardId}
```

### 用途

查询某个 storyboard 下，当前有哪些图片 / 视频生成任务正在运行或已完成。

### 适用场景

- 检查某个 scene 的图片是否生成完成
- 检查单张图转视频是否仍在运行
- 做 UI 侧进度展示

### live 测试补充

单场景图转视频提交后，这个接口会返回：

- `taskType = video`
- `taskId`
- `taskResourceId`
- `taskStatus`

可与 `GET /task/{taskId}` 交叉验证。
