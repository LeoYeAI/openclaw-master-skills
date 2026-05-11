# 角色管理 API

## 目录

- [获取角色列表](#获取角色列表)
- [获取单个角色候选图片列表](#获取单个角色候选图片列表)
- [生成新的角色形象图片](#生成新的角色形象图片)
- [应用新的角色形象图片](#应用新的角色形象图片)
- [获取待生成 IP 角色信息](#获取待生成-ip-角色信息)
- [发布 IP 角色](#发布-ip-角色)

---

## 获取角色列表

### 请求

```http
GET /service/workflow/comic/roles/{presetResourceId}
```

### 重要说明

这个接口不只是“看角色”，还是 **`novel_extract_roles` 的前置检查接口**。

Agent 应该用它来做三件事：

1. 判断角色图是否已经生成完成
2. 获取 live 的 `voiceInputs`
3. 读取每个角色的 `tts`、`voiceCode`、`imgUrl` 等信息

### 响应关键字段

| 字段 | 说明 |
|------|------|
| `data.roles[]` | 当前章节提取出的角色列表 |
| `data.roles[].taskStatus` | 角色图生成状态 |
| `data.roles[].imgUrl` | 角色图 URL，成功后应非空 |
| `data.roles[].inputs[]` | 角色级音色配置输入 |
| `data.voiceInputs[]` | 章节级音色配置输入，通常可直接复用 |

### `taskStatus` 状态值

| 状态 | 说明 |
|------|------|
| `PENDING` | 等待生成 |
| `RUNNING` | 正在生成 |
| `SUCCESS` | 生成完成 |
| `FAILED` | 生成失败 |

### Agent 必须遵守的规则

1. **不要在角色图未完成时推进 `novel_extract_roles`**。
2. **不要硬编码 `tts` 默认值**，例如不要写死 `10008`、`10025`。
3. 应优先使用 `data.voiceInputs[0]`，如果不存在，再退回 `data.roles[0].inputs[0]`。

### 正确检查方式

只有满足以下条件，才可以继续：

- 所有关键角色 `taskStatus == SUCCESS`
- 所有关键角色 `imgUrl` 非空

否则容易报：

```text
角色 [xxx] 图片未完成
```

---

## 获取待生成 IP 角色信息

### 请求

```http
POST /service/workflow/ipRole/getIpRolesToGen
```

### 请求体

```json
{
  "model": "doubao-seedream-3.0",
  "projectId": "项目ID"
}
```

### 用途

用于查看是否还有待生成的角色图资源。

### 重要说明

如果角色图已经由后端自动补齐，这个接口可能返回：

```json
{
  "resourceIds": [],
  "chargePoint": 0
}
```

这意味着当前没有额外待生成角色图，不是错误。

---

## 获取单个角色候选图片列表

### 请求

```http
GET /service/workflow/comic/role/{roleResourceId}/resources
```

### 用途

用于读取某个角色当前可选的图片资源列表，包括：

- 当前已选中的角色主图
- 新生成但尚未应用的候选图
- 每张候选图的生成状态、URL、描述、是否选中

### 关键字段

| 字段 | 说明 |
|------|------|
| `data[].resourceId` | 单张角色图资源 ID |
| `data[].imgUrl` | 角色图 URL，生成完成后非空 |
| `data[].description` | 该张图对应的角色外观描述 |
| `data[].taskStatus` | 当前角色图生成状态 |
| `data[].selected` | 是否是当前被应用中的角色主图 |

### 重要规则

1. 新生成的候选图即使 `SUCCESS`，也可能仍然是 `selected=false`。
2. 因此**不能**把“生图成功”误判为“角色已经修改完成”。
3. 必须再执行应用新图的步骤，角色主图才会真正切换。

---

## 生成新的角色形象图片

### 请求

```http
POST /service/workflow/ipRole/generateIpRole
```

### 请求体

```json
{
  "name": "顾念念",
  "age": 3,
  "description": "这里是测试更改角色形象",
  "styleId": 10543,
  "model": "doubao-seedream-3.0",
  "projectId": "项目ID",
  "roleId": "角色资源ID",
  "id": 322419
}
```

### 字段说明

| 字段 | 说明 |
|------|------|
| `name` | 角色名 |
| `age` | 年龄段 ID，见下方年龄映射 |
| `description` | 新的角色外观描述 |
| `styleId` | 当前项目 / 角色使用的风格 ID |
| `model` | 当前项目使用的生图模型 |
| `projectId` | 项目 ID |
| `roleId` | 角色资源 ID（不是数字 roleId） |
| `id` | 当前角色的 `ipRoleId` |

### 重要规则

1. 只能在 `workflow.currentStep = novel_extract_roles` 时发起。
2. 返回里的 `resourceId` 仍然是角色资源 ID，不是新图片资源 ID。
3. 发起后必须继续轮询角色候选图列表，直到出现新的 `resourceId`，且其 `taskStatus=SUCCESS`、`imgUrl` 非空。

---

## 应用新的角色形象图片

### 请求

```http
POST /service/workflow/ipRole/applyImage
```

### 请求体

```json
{
  "name": "顾念念",
  "age": 3,
  "gender": 2,
  "imageResourceId": "新生成的角色图资源ID",
  "isPublic": 1,
  "userProject": "项目ID",
  "roleId": "角色资源ID"
}
```

### 重要规则

1. `imageResourceId` 必须使用新生成并已 `SUCCESS` 的那张角色图资源 ID。
2. 只生图但不 `applyImage`，不算角色形象修改完成。
3. `applyImage` 成功后，还要再读 `GET /comic/roles/{presetResourceId}`，确认角色的 `appearance`、`imageResourceId`、`imgUrl` 已切到新图。
4. 只有这一步完成后，才能把新的角色图片 URL 返回给用户。

---

## 发布 IP 角色

### 请求

```http
POST /service/workflow/ipRole/publicIpList
```

### 请求体

```text
ipIds=295398%2C295399
```

### 说明

这是可选动作，只在需要把角色发布到公共库时使用。

---

## 与 `novel_extract_roles` 的关系

在真实流程中，推荐执行顺序是：

```text
提交剧本
→ 智能分集
→ 获取角色列表
→ 等待角色图全部 SUCCESS
→ 读取 voiceInputs
→ 再执行 novel_extract_roles
```

## 角色完成后的用户确认要求

角色阶段完成后，Agent 必须立即停下来等待用户确认，不能自动继续进入场景 / 分镜步骤。

回给用户的内容至少包括：

1. 每个角色的角色图片
2. 角色名称（用于区分图片对应的角色）

然后明确询问用户：

- 是否确认继续进入下一步

如果当前仍处于 `novel_extract_roles`（角色与配音）步骤，还应额外询问：

- 是否需要修改某个角色的形象

如果用户要求修改，则必须走：

```text
确认当前在角色与配音步骤
→ 发起 generateIpRole
→ 等候新图 SUCCESS
→ applyImage 显式应用
→ 再读 comic/roles 验证主图已切换
→ 把新图 URL 返回给用户
```

### 当前限制

角色形象修改只允许在 **角色与配音** 步骤执行。

一旦项目继续推进到 `novel_scene_captions` 或后续步骤，就不能再按这条链路修改角色形象。

如果只返回角色名称而不返回角色图片，属于信息不足。

### 可直接复用到步骤请求中的输入示例

```json
[
  {"type": "number", "name": "chapterNum", "value": 1},
  {
    "label": "选择音色",
    "name": "tts",
    "type": "voice-clone-select",
    "required": true,
    "options": [
      {"label": "推荐音色", "value": "1"},
      {"label": "我的克隆音色", "value": "2"}
    ],
    "props": {
      "emotion": "",
      "ttsType": 1,
      "speed": {
        "max": 2,
        "min": 0.8,
        "value": 1.2,
        "options": [0.8, 1, 1.2, 1.5, 1.8, 2]
      }
    },
    "value": 10025
  }
]
```

> 注意：`value` 的真实值必须来自 live 响应，不要从文档示例里抄常量。
