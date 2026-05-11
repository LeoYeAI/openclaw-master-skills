# 任务状态查询 API

## 目录

- [查询任务状态](#查询任务状态)
- [任务状态值](#任务状态值)
- [轮询建议](#轮询建议)
- [哪些 ID 需要轮询](#哪些-id-需要轮询)
- [不要只依赖 task 接口](#不要只依赖-task-接口)

---

## 查询任务状态

### 请求

```http
GET /service/workflow/task/{taskId}
```

### 响应关键字段

| 字段 | 说明 |
|------|------|
| `data.id` | 任务 ID |
| `data.userProjectId` | 项目 ID |
| `data.resourceId` | 完成后产出的资源 ID |
| `data.resourceType` | 资源类型 |
| `data.status` | 任务状态 |
| `data.message` | 任务消息 |
| `data.estimateDuration` | 预计耗时 |

---

## 任务状态值

| 状态 | 说明 | 处理方式 |
|------|------|----------|
| `PENDING` | 等待中 | 继续轮询 |
| `QUEUED` | 排队中 | 继续轮询 |
| `RUNNING` | 处理中 | 继续轮询 |
| `SUCCESS` | 成功 | 读取 `resourceId` 或进入下一层检查 |
| `FAILED` | 失败 | 查看 `message` |
| `CANCELED` | 已取消 | 结束当前任务 |

---

## 轮询建议

| 场景 | 间隔 | 建议上限 |
|------|------|----------|
| 剧本处理 | 2-3 秒 | 5 分钟 |
| 智能分集 | 2-3 秒 | 5 分钟 |
| 智能分镜 dialogTask | 2-3 秒 | 5 分钟 |
| 视频合成 | 5 秒 | 15 分钟 |

---

## 哪些 ID 需要轮询

### 1. `resultId`

常见于：

- `novel_input`
- `novel_opt`
- `novel_chapter_video` 的最终合成任务

### 2. `dialogTaskId`

常见于：

- `novel_scene_captions`

### 3. `sceneTaskId`

常见于：

- `comicPreset.data.chapters[]`

它通常需要额外再查一次 `GET /task/{sceneTaskId}` 才能拿到 `storyboardId`。

---

## 不要只依赖 task 接口

这是最容易误导 Agent 的地方。

真实流程里，**有些 readiness 不只靠 `task/{taskId}` 判断**，还要结合其他接口：

### 1. 角色图 readiness

看：

```http
GET /service/workflow/comic/roles/{presetResourceId}
```

需要确认：

- `roles[].taskStatus == SUCCESS`
- `roles[].imgUrl` 非空

### 2. 智能分镜前置 readiness

看：

```http
GET /service/workflow/resource/comicPreset/{presetResourceId}
```

需要确认：

- `chapters[].sceneCaptionsTaskStatus == SUCCESS`

### 3. 推进到成片前置 readiness

仍然看：

```http
GET /service/workflow/resource/comicPreset/{presetResourceId}
```

需要确认：

- `chapters[].sceneTaskStatus == SUCCESS`

### 结论

正确思路不是：

```text
有 taskId -> 轮询成功 -> 一定可以下一步
```

而是：

```text
轮询 task 成功
→ 再检查角色 readiness / 章节隐藏状态
→ 条件满足后再调用下一步
```
