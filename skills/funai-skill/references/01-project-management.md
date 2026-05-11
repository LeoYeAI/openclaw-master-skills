# 项目管理 API

## 目录

- [获取配置选项](#获取配置选项)
- [创建项目](#创建项目)
- [获取项目详情](#获取项目详情)
- [查询计费点](#查询计费点)
- [获取用户 VIP 信息](#获取用户-vip-信息)

---

## 获取配置选项

创建项目之前，必须先通过这个接口拿到**当前后端真实支持**的比例、模型、风格和剧本类型。

### 请求

```http
POST /service/workflow/project/story/select-options
```

### 请求体

```json
{
  "appCode": "ai-story",
  "generateType": "1"
}
```

### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `appCode` | string | 是 | 固定值 `ai-story` |
| `generateType` | string | 否 | `1`=文生图，`2`=多参生图，`3`=多参生视频 |

### 重要说明

1. **创建项目前必须先调这个接口**。
2. 必须使用接口返回的 `ratios`、`generateTypes`、`models`、`videoModels`、`styles`、`scriptTypes`。
3. 不要把历史默认值写死。`isDefault` 可能受本次请求形状影响。
4. 面向真实用户交互时，如果用户没有明确要求切换模式，则可静默使用当次接口返回的默认 `generateType / scriptType`，不要主动把“默认文生图 / 默认解说漫模式”当作一个需要解释的配置项。
5. 但 `aspect`（画面比例）与 `style`（风格）不能静默默认，必须展示对应实时可选项并让用户明确选择。
6. `model / videoModel` 若用户没有额外要求，可继续使用 `select-options` 返回的当前默认值。

### 响应关键字段

| 字段 | 说明 |
|------|------|
| `data.ratios[]` | 可用画幅比例 |
| `data.generateTypes[]` | 可用生图/生视频模式 |
| `data.models[]` | 当前可用生图模型 |
| `data.videoModels[]` | 当前可用视频模型 |
| `data.styles[]` | 当前可用风格 |
| `data.scriptTypes[]` | 当前可用剧本类型 |

---

## 创建项目

### 请求

```http
POST /service/workflow/project/create
```

### 请求体

```json
{
  "workflowId": "695f25b74c510d48b10c4345",
  "name": "我的漫剧项目",
  "extras": {
    "aspect": "16:9",
    "imgGenType": "1",
    "model": "doubao-seedream-3.0",
    "videoModel": "doubao-pro",
    "style": "古风写实",
    "content": "",
    "workflowTemplate": 0,
    "scriptType": "0"
  }
}
```

### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `workflowId` | string | 是 | 固定值 `695f25b74c510d48b10c4345` |
| `name` | string | 是 | 项目名称 |
| `extras.aspect` | string | 是 | 必须来自 `select-options` 返回值 |
| `extras.imgGenType` | string | 是 | 必须来自 `select-options` 返回值 |
| `extras.model` | string | 是 | 必须来自 `select-options` 返回值 |
| `extras.videoModel` | string | 是 | 必须来自 `select-options` 返回值 |
| `extras.style` | string | 是 | 必须来自 `select-options` 返回值 |
| `extras.scriptType` | string | 建议 | 建议直接复用 `select-options` 返回值 |

### 重要说明

1. **不要硬编码风格、模型、比例、剧本类型。**
2. **不要替用户静默决定 `aspect / style`。** 这两个字段必须先征得用户确认。
3. 创建项目后，live 后端常见的 `workflow.currentStep` 是 `novel_input`，因为 `novel_config` 已自动完成。
4. 项目创建成功后应立即向用户展示项目链接。
5. 项目创建完成后，不要默认自动跑完整条链路；应先向用户汇报当前结果，并等待用户确认下一步。

### 响应关键字段

| 字段 | 说明 |
|------|------|
| `data.id` | 项目 ID |
| `data.presetResourceId` | 后续查询角色 / 章节隐藏状态时会用到 |
| `data.workflow.currentStep` | 项目级当前步骤 |
| `data.workflow.produceSteps` | 步骤列表 |

---

## 获取项目详情

### 请求

```http
GET /service/workflow/project/{projectId}
```

### 重要说明

`workflow.currentStep` 只表示**项目级**状态，不代表章节级隐藏任务一定已完成。

例如：

- `currentStep = novel_scene_captions` 时，不一定已经可以立刻发起智能分镜
- `currentStep = novel_chapter_scenes` 时，不一定已经可以立刻推进到成片

还要同时检查：

```http
GET /service/workflow/resource/comicPreset/{presetResourceId}
```

中的：

- `chapters[].sceneCaptionsTaskStatus`
- `chapters[].dialogTaskStatus`
- `chapters[].sceneTaskStatus`

### 响应关键字段

| 字段 | 说明 |
|------|------|
| `data.workflow.currentStep` | 项目级步骤 |
| `data.presetResourceId` | 章节级隐藏状态查询入口 |
| `data.status` | 项目整体状态 |

---

## 查询计费点

### 请求

```http
POST /service/workflow/project/queryAppChargePoint
```

### 用途

用于查询某个生成动作大概会消耗多少梦想值。

### 适用场景

- 重绘分镜图前
- 单张图转视频前
- 其他有梦想值消耗的动作前

---

## 获取用户 VIP 信息

### 请求

```http
GET /service/pay/user/vip
```

### 响应关键字段

| 字段 | 说明 |
|------|------|
| `data.isVip` | 是否 VIP |
| `data.coinAmount` | 当前梦想值余额 |
| `data.validEndTime` | VIP 到期时间 |

### 建议

在执行高消耗操作前，可先确认用户余额是否足够。
