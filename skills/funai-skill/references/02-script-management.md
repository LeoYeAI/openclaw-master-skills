# 剧本管理与步骤推进 API

## 目录

- [步骤前进总览](#步骤前进总览)
- [提交剧本](#提交剧本)
- [智能分集](#智能分集)
- [角色与配音](#角色与配音)
- [智能分镜](#智能分镜)
- [分镜图到成片步骤](#分镜图到成片步骤)
- [步骤回退](#步骤回退)
- [切换子步骤](#切换子步骤)
- [获取漫画预设资源](#获取漫画预设资源)
- [获取资源详情](#获取资源详情)

---

## 步骤前进总览

### 请求

```http
POST /service/workflow/project/step/next
```

### 注意

这个接口虽然统一，但不同 `step` 的真实前置条件差异很大。

Agent 不能只看 `workflow.currentStep`，还要看：

- `GET /comic/roles/{presetResourceId}` 中的角色图状态
- `GET /resource/comicPreset/{presetResourceId}` 中的章节级隐藏任务状态

在真正调用 `next_step` 前，还应再多做一步：

1. `GET /project/{projectId}` 读取当前 `workflow.currentStep`
2. 如果项目已经自动前进到目标 step **之后**，就不要重复调用旧步骤
3. 否则再继续检查该步骤自己的 hidden readiness

这可以避免常见的：

```text
项目其实已经自动推进到 novel_scene_captions
→ Agent 仍然重放 novel_extract_roles
→ 后端返回 “该步骤不可执行”
```

### 用户交互节奏

对真实用户执行时，不要把这些 step 一口气全部跑完。

正确节奏是：

```text
完成一个用户可感知的大步骤
→ 汇报详细结果
→ 询问是否确认继续；如果当前步骤支持修改，再询问是否需要修改
→ 用户确认后再调用下一步的 step 接口
```

可以不单独停下来的，仍然是同一步内部的技术动作，例如：轮询、资源读取、状态检查、`sceneId` 解析。

### 必须停下来等确认的三个节点

1. **剧本生成 / 提交完成后**：把当前剧本内容回给用户确认是否需要修改
2. **角色完成后**：把角色图片回给用户确认；如果当前仍停留在 `novel_extract_roles`，还应询问用户是否要修改某个角色形象。若用户要求修改，必须走“生新图 → 等待成功 → apply 新图 → 回传新图 URL”后，才能继续下一步。
3. **场景 / 分镜完成后**：把场景描述回给用户，并明确询问“转视频”还是“直接进入成片”

这三个节点都不能跳过。

### 真实流程建议

| step | 继续前必须确认什么 |
|------|-------------------|
| `novel_input` | 项目已创建 |
| `novel_opt` | 剧本提交任务已完成 |
| `novel_extract_roles` | 角色图全部 `SUCCESS`，且有 live `tts` 输入 |
| `novel_scene_captions` | `sceneCaptionsTaskStatus=SUCCESS` |
| `novel_chapter_scenes` | `sceneTaskStatus=SUCCESS` |

---

## 提交剧本

### 请求体

```json
{
  "userProjectId": "项目ID",
  "step": "novel_input",
  "inputs": [
    {"name": "content", "type": "text", "value": "清晨的城市公园里，年轻的程序员李明正在晨跑。阳光穿过树叶，落在湿润的石板路上。"},
    {"name": "scriptType", "type": "text", "value": "0"},
    {"name": "isSplit", "type": "text", "value": "0"}
  ]
}
```

### 重要说明

1. `content` 往往包含多行与引号，构造 JSON 时必须使用安全的 JSON builder，不要做字符串硬拼接。
2. 通常会返回 `resultId`，需要轮询 `GET /task/{resultId}`。

### 如果是 AI 代写剧本

当当前走的是解说剧 / 解说漫模式时，AI 代写剧本必须写成**旁白叙述式的小说体 / 故事正文**，不要写成分镜脚本。

避免：

- `镜头1`
- `旁白：...`
- `某某说：...`
- `【音效：风声】` / `砰！` / `哗啦——`
- 条目式镜头表

要写成：

- 连续叙事
- 以旁白讲述式正文推进故事
- 可穿插少量自然对白，但整体仍然是叙述型小说体

这样平台后续才能更稳定地自动拆分角色、分镜和解说。

---

## 智能分集

### 请求体

```json
{
  "userProjectId": "项目ID",
  "step": "novel_opt",
  "inputs": []
}
```

### 响应说明

- 一般返回 `resultId`
- 需要轮询 `GET /task/{resultId}`
- 轮询成功后，项目通常进入 `novel_extract_roles`

### 重要限制

`novel_opt` 更像平台内部的“自动智能分集”，而不是一个可靠可控的“目标集数分配器”。

当前 skill 没有任何证据表明，可以仅靠这个步骤稳定指定“拆成 3 / 5 / 8 集”。

如果用户明确要求固定集数，更稳妥的做法是：

1. 先把剧本正文改成更明确的分集结构
2. 再让平台做智能分集

不要把 `novel_opt` 理解成“可精确指定目标集数”的接口。

---

## 角色与配音

### 不要只传 `chapterNum`

文档示意里常见的最小请求体只写了 `chapterNum`，但 live 流程中这通常**不够**。

如果角色图还没完成，或者没有带上 live `tts` 输入，常见报错是：

```text
角色 [xxx] 图片未完成
```

### 正确执行顺序

1. 先调：

```http
GET /service/workflow/comic/roles/{presetResourceId}
```

2. 等待：

- `roles[].taskStatus == SUCCESS`
- `roles[].imgUrl` 非空

3. 从以下任一位置取出 live 的音色输入对象：

- `data.voiceInputs[0]`
- `data.roles[0].inputs[0]`

4. 再发起角色步骤：

```json
{
  "userProjectId": "项目ID",
  "step": "novel_extract_roles",
  "inputs": [
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
}
```

### 响应说明

live 成功时可能返回：

- `resultType = resource`
- `resultId = presetResourceId`

不要把这个步骤强行当作“总是返回 task”。

### 角色步骤成功后，不要立刻继续智能分镜

还要先检查：

```http
GET /service/workflow/resource/comicPreset/{presetResourceId}
```

并等待：

```text
chapters[].sceneCaptionsTaskStatus == SUCCESS
```

---

## 智能分镜

### 请求体

```json
{
  "userProjectId": "项目ID",
  "step": "novel_scene_captions",
  "inputs": [
    {"type": "number", "name": "chapterNum", "value": 1},
    {"name": "imgGenTypeRef", "value": 1}
  ]
}
```

### 重要说明

1. 这个步骤返回的是 **`dialogTaskId`**，不是 `resultId`。
2. 如果 `sceneCaptionsTaskStatus` 还没成功，常见报错是：

```text
该章节提取分镜场景任务未完成，请稍后再试
```

3. 即使 `dialogTaskId` 轮询成功，也还不能立刻推进 `novel_chapter_scenes`。

还要继续等待：

```text
chapters[].sceneTaskStatus == SUCCESS
```

---

## 分镜图到成片步骤

### 请求体

```json
{
  "userProjectId": "项目ID",
  "step": "novel_chapter_scenes",
  "inputs": [
    {"type": "number", "name": "chapterNum", "value": 1}
  ]
}
```

### 重要说明

这个调用表示“章节分镜图已经就绪，现在推进到成片步骤”。

推进成功后，表示进入 `novel_chapter_video`，但这时通常只是进入**成片设置阶段**，不是已经完成视频合成。

它的真实前置条件不是只看 `currentStep=novel_chapter_scenes`，还必须确认：

```text
chapters[].sceneTaskStatus == SUCCESS
```

如果调早了，常见报错是：

```text
该章节分镜图任务未完成，请稍后再试
```

### 响应说明

根据后端时机不同，它可能返回：

- `resultType = resource`
- 或 `resultType = task`

因此应统一按“先读响应，再决定是否轮询”的方式处理。

### 进入 `novel_chapter_video` 后的阶段语义

live 测试中，进入成片步骤后常见状态为：

```text
currentStep = novel_chapter_video
currentSubStep = setting
```

这表示当前处于**成片设置阶段**，需要先准备并保存封面、字幕、背景音乐等设置。

只有在随后调用：

```http
POST /service/workflow/project/step/action
```

并成功返回任务后，才真正进入视频合成执行阶段。

---

## 步骤回退

### 请求

```http
POST /service/workflow/project/step/prev
```

### 用途

主要用于从 `novel_chapter_video` 回退到 `novel_chapter_scenes`，再继续生图/生视频类操作。

### live 测试确认

回退成功后，通常会看到：

- `workflow.currentStep = novel_chapter_scenes`
- `chapters[].currentStep = novel_chapter_scenes`
- `chapters[].currentSubStep` 可能仍显示为 `video`

最后这一点不是异常，Agent 不应把它误判成“回退失败”。真正是否可继续，还要看：

- `sceneTaskStatus == SUCCESS`
- scene 当前 image 资源是否可用

### 回退后的关键事实

live 测试确认：

- 回退前已经成功的视频合成任务会保留旧的 `videoTaskId`
- 但回退并重新进入成片步骤后，若再次执行合成，会生成**新的** `videoTaskId`
- 同时也会生成**新的**最终视频 `resourceId`

这说明每次回退调整后，都需要重新合成视频，不能把旧的合成结果当成新的最终结果。

### 请求体

```json
{
  "userProjectId": "项目ID",
  "step": "novel_chapter_video",
  "chapterNum": 1
}
```

---

## 切换子步骤

### 请求

```http
POST /service/workflow/project/subStep/switch
```

### 常用场景

- 在 `novel_chapter_video` 内切换到 `setting`
- 查看 composing / finished 状态

---

## 获取漫画预设资源

### 请求

```http
GET /service/workflow/resource/comicPreset/{presetResourceId}
```

### 这是章节级隐藏状态的权威来源

`chapters[]` 中常见的关键字段包括：

| 字段 | 用途 |
|------|------|
| `sceneCaptionsTaskId` | 章节分镜场景提取任务 ID |
| `sceneCaptionsTaskStatus` | 是否可以继续执行智能分镜 |
| `dialogTaskId` | 智能分镜步骤返回的任务 ID |
| `dialogTaskStatus` | 智能分镜对话任务状态 |
| `sceneTaskId` | 章节分镜图任务 ID |
| `sceneTaskStatus` | 是否可以继续推进到成片 |
| `currentStep` | 该章节当前所处步骤 |
| `currentSubStep` | 该章节当前子步骤 |

### 典型章节数据示意

```json
{
  "title": "第1集",
  "num": 1,
  "sceneCaptionsTaskId": "34482392",
  "sceneCaptionsTaskStatus": "SUCCESS",
  "dialogTaskId": "34482414",
  "dialogTaskStatus": "SUCCESS",
  "sceneTaskId": "34482415",
  "sceneTaskStatus": "SUCCESS",
  "currentStep": "novel_chapter_video",
  "currentSubStep": "setting"
}
```

---

## 获取资源详情

### 请求

```http
GET /service/workflow/resource/{resourceId}
```

### 常见用途

- 读取 `storyboardId` 对应的 scenes 列表
- 获取完整 `sceneId`
- 获取已生成的分镜图 URL
- 获取最终视频资源
