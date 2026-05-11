# 资源管理 API

## 目录

- [资源体系总览](#资源体系总览)
- [获取资源详情](#获取资源详情)
- [获取漫画预设资源](#获取漫画预设资源)
- [如何从章节解析 storyboardId 与 sceneId](#如何从章节解析-storyboardid-与-sceneid)
- [如何找到 scene 当前基准分镜图](#如何找到-scene-当前基准分镜图)
- [常见资源类型说明](#常见资源类型说明)
- [资源读取时最容易混淆的点](#资源读取时最容易混淆的点)

---

## 资源体系总览

Funai 的资源读取不能只理解成“拿一个 resourceId 看详情”。

真实流程里，最常见的资源层级是：

```text
project
└─ presetResourceId (comicPreset)
   ├─ chapters[]
   │  ├─ sceneTaskId
   │  ├─ sceneCaptionsTaskStatus / dialogTaskStatus / sceneTaskStatus
   │  └─ currentStep / currentSubStep
   └─ roleResourceIds[]

sceneTaskId
└─ GET /task/{sceneTaskId}
   └─ resourceId = storyboardId

storyboardId
└─ GET /resource/{storyboardId}
   └─ data.data.scenes[]
       ├─ id                = 完整 sceneId
       ├─ image             = 当前基准分镜图 URL
       ├─ imageResourceId   = 当前基准分镜图资源ID
       └─ video             = 当前采用的视频（如果已存在）
```

### 核心结论

1. `presetResourceId` 是章节隐藏状态的入口。
2. `sceneTaskId` 不是 `storyboardId`，中间必须再查一次 `/task/{sceneTaskId}`。
3. `sceneUuid` 不是完整 `sceneId`。
4. 图转视频时，优先使用 **`prompt/detail.video.imageId` 对应的 image 资源**，而不是角色图。

---

## 获取资源详情

### 请求

```http
GET /service/workflow/resource/{resourceId}
```

### 用途

这是读取具体资源详情的通用入口，常用于：

- 读取 storyboard 资源
- 读取 image / video 资源
- 读取最终成片资源

### 重要说明

同一个 `/resource/{resourceId}`，返回的数据结构会因资源类型不同而变化。

Agent 必须先判断：

- `type`
- `category`
- `displayType`

再决定如何读取 `data` 字段。

### storyboard 响应关键字段

| 字段 | 说明 |
|------|------|
| `id` | 当前资源 ID |
| `type` | 通常为 `storyboard` |
| `category` | 常见为 `video` |
| `userProjectId` | 所属项目 |
| `data.config` | 项目配置快照 |
| `data.videoSetting` | 成片设置快照 |
| `data.chapterNum` | 章节号 |
| `data.data.scenes[]` | scene 列表 |

### 对最终视频资源的说明

最终视频资源里如果新增了 `videoPlayUrl`，则：

- 对外只返回 `videoPlayUrl`
- 原始 `url` 只属于底层资源结构，不应继续出现在高层 helper / 模型可见输出中
- 项目链接可作为补充入口一起返回

---

## 获取漫画预设资源

### 请求

```http
GET /service/workflow/resource/comicPreset/{presetResourceId}
```

### 这是章节状态的权威来源

这个接口最重要的不是“看剧本”，而是看 `chapters[]`。

### `chapters[]` 中最关键的字段

| 字段 | 用途 |
|------|------|
| `num` | 章节号 |
| `sceneCaptionsTaskId` | 分镜场景提取任务 ID |
| `sceneCaptionsTaskStatus` | 是否可以继续执行 `novel_scene_captions` |
| `dialogTaskId` | 智能分镜任务 ID |
| `dialogTaskStatus` | 智能分镜任务状态 |
| `sceneTaskId` | 分镜图任务 ID |
| `sceneTaskStatus` | 是否可以推进成片，或继续做 scene 级操作 |
| `currentStep` | 当前章节步骤 |
| `currentSubStep` | 当前章节子步骤 |

### 回退后的真实行为

live 测试确认：

- 从 `novel_chapter_video` 回退后，`workflow.currentStep` 会回到 `novel_chapter_scenes`
- 章节 `currentSubStep` 仍可能保留 `video`

这不代表回退失败。真正要继续 scene 级操作，仍然要看：

- `sceneTaskStatus == SUCCESS`

---

## 如何从章节解析 storyboardId 与 sceneId

### 不要直接猜 sceneId

正确解析链路：

```text
GET /resource/comicPreset/{presetResourceId}
→ chapters[].sceneTaskId

GET /task/{sceneTaskId}
→ data.resourceId = storyboardId

GET /resource/{storyboardId}
→ data.data.scenes[].id = 完整 sceneId
```

### 为什么这一步必须写清楚

因为很多 Agent 会把：

- `sceneUuid`
- `storyboardId`
- `sceneId`

混成一个概念，最后导致：

```text
400 / 分镜场景资源不存在
```

### 读取 storyboard scenes 的正确路径

正确：

```bash
jq '.data.data.scenes'
```

错误：

```bash
jq '.data.scenes'
```

live 验证结果：`/resource/{storyboardId}` 的 scenes 确实位于 **`.data.data.scenes`**。

---

## 如何找到 scene 当前基准分镜图

图转视频时，不能只说“拿一张 scene 图片”。真正应该拿的是：

```text
GET /storyboard/scene/{sceneId}/prompt/detail?sceneId={sceneId}
→ video.imageId

GET /storyboard/scene/{sceneId}/resources
→ 找到 resourceId == video.imageId 的 image 资源
```

然后使用：

- `firstImage = image.url`
- `imageId = image.resourceId`

### 为什么不能任意取图

1. 角色图 `roles[].imgUrl` 不是 scene 当前基准分镜图。
2. `resources` 里的“第一张 image”也不一定是当前应使用的图。
3. live 测试表明，传错图时后端可能仍返回 `200 success`，但视频语义会错。

也就是说，这里最危险的不是“参数会报错”，而是“参数看似合法，但结果是错的”。

---

## 常见资源类型说明

### 1. `comicPreset`

章节级资源，关注：

- `chapters[]`
- `roleResourceIds[]`
- `config`

### 2. `storyboard`

分镜级资源，关注：

- `data.data.scenes[]`
- `data.videoSetting`
- `data.chapterNum`

### 3. `image`

图片资源，常见字段：

- `url`
- `thumbnail`
- `width`
- `height`

### 4. `video`

视频资源，常见字段：

- `url`
- `cover`
- `duration`
- `resolution` / `clarity`

---

## 资源读取时最容易混淆的点

### 1. `roles[].imgUrl` vs `scenes[].image`

- `roles[].imgUrl` = 角色形象图
- `scenes[].image` = 当前 scene 的基准分镜图

图转视频要优先围绕 **scene 的基准分镜图** 工作，而不是角色图。

### 2. `sceneUuid` vs `sceneId`

- `sceneUuid` = 短 ID，仅用于列表或展示语境
- `sceneId` = 完整 ObjectId，API 调用必须使用它

### 3. `selected` 不总是 image

如果某个 scene 已经生成并采用了 video，`resources` 里 `selected == true` 的可能是 video，而不是 image。

这时不要报错退出，也不要任意选第一张图。

应优先回到：

- `prompt/detail.video.imageId`

再去 `resources` 里找对应的 image。

### 5. `scene/{sceneId}/resources` 返回的是扁平数组

正确：

```bash
jq '.data[] | select(.type == "image")'
```

错误：

```bash
jq '.data.images[]'
```

live 验证结果：`/storyboard/scene/{sceneId}/resources` 的 `data` 是**扁平数组**，不是 `{images: [], videos: []}` 结构。

### 4. 回退不等于资源重建

从成片回退到分镜图步骤时，通常会复用已有资源：

- 现有 storyboard
- 现有 image
- 现有 videoSetting

所以回退后更像是“恢复可编辑状态”，不是“重新从零生成一遍”。
