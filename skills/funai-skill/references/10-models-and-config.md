# 模型与配置参考

## 核心原则

1. **所有配置都以 `select-options` 的实时返回为准。**
2. 不要硬编码风格、模型、比例、剧本类型。
3. 不要把历史 `isDefault` 视为固定常量；它可能因请求参数不同而变化。

---

## 获取配置的权威接口

```http
POST /service/workflow/project/story/select-options
```

示例：

```json
{
  "appCode": "ai-story",
  "generateType": "1"
}
```

返回中常见字段：

- `ratios`
- `generateTypes`
- `models`
- `videoModels`
- `styles`
- `scriptTypes`

---

## 画面比例

常见返回值示例：

- `16:9`
- `9:16`
- `4:3`
- `3:4`

是否支持某个比例，必须以 live 返回为准。

### 用户交互规则

`aspect` 不能静默默认。

即使 `select-options` 返回了默认比例，创建真实用户项目时仍然必须让用户明确选择画面比例。

---

## 图片生成类型

常见返回值示例：

| 值 | 说明 |
|------|------|
| `1` | 文生图 |
| `2` | 多参生图 |
| `3` | 多参生视频 |

### 重要说明

- 如果用户没有明确要求，Agent 一般可默认用 `generateType: "1"` 去拉取文生图配置项。
- 但最终 `imgGenType` 仍应以本次接口返回结果中的可选值为准。
- 如果用户没有特别要求，不需要主动把“当前默认使用文生图模式”解释给用户；直接静默使用默认值即可。

---

## 图片模型 / 视频模型 / 风格

这些列表会随平台更新而变化。

因此：

- 不要把文档里的示例列表当成完整白名单
- 不要把示例里的 `doubao-seedream-3.0`、`doubao-pro`、`现代写实` 当成固定默认
- 创建项目时必须直接复用当前 `select-options` 返回值

### 用户交互规则

- `style` 不能静默默认，必须让用户明确选择
- `model / videoModel` 若用户没有额外要求，可使用 `select-options` 返回的当前默认值

---

## 剧本类型

`scriptTypes` 也应从 `select-options` 返回中读取。

live 返回值可能与旧文档示意不同，Agent 不应假设只有 `0/1` 这类老枚举。

如果用户没有特别要求，不需要主动把“当前默认使用解说漫模式”作为配置项解释给用户；直接使用当次接口返回的默认剧本模式即可。

---

## 项目创建配置示例

```json
{
  "workflowId": "695f25b74c510d48b10c4345",
  "name": "我的漫剧项目",
  "extras": {
    "aspect": "来自 select-options 的实时值",
    "imgGenType": "来自 select-options 的实时值",
    "model": "来自 select-options 的实时值",
    "videoModel": "来自 select-options 的实时值",
    "style": "来自 select-options 的实时值",
    "content": "",
    "workflowTemplate": 0,
    "scriptType": "来自 select-options 的实时值"
  }
}
```

---

## workflow 总览（按真实行为理解）

| 步骤 | 标识 | 备注 |
|------|------|------|
| 1 | `novel_config` | 通常自动完成 |
| 2 | `novel_input` | 提交剧本，返回 `resultId` |
| 3 | `novel_opt` | 智能分集，返回 `resultId` |
| 4 | `novel_extract_roles` | 需要角色图 ready + live `tts` 输入 |
| 5 | `novel_scene_captions` | 需要先等 `sceneCaptionsTaskStatus=SUCCESS`，返回 `dialogTaskId` |
| 6 | `novel_chapter_scenes` | 需要先等 `sceneTaskStatus=SUCCESS` |
| 7 | `novel_chapter_video` | 读取成片设置并执行合成 |

---

## 最重要的配置建议

如果 Agent 只能记住一条规则，那就是：

> **先调 `select-options`，后建项目；其中 `generateType / scriptType` 可静默默认，但 `aspect / style` 必须用户明确选择；其余值用 live 值，不用记忆值。**
