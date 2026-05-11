---
name: ai-task-hub
description: AI Task Hub 用于图像检测与分析、去背景与抠图、语音转文字、文本转语音、文档转 Markdown 和异步任务编排。适用于用户需要通过 execute/poll/presentation 完成结果交付，且由宿主统一管理身份、积分、支付和风控的场景。
version: 3.1.4
metadata:
  openclaw:
    skillKey: ai-task-hub
    emoji: "🧩"
    homepage: https://gateway.binaryworks.app
    requires:
      bins:
        - node
      env:
        - AGENT_TASK_TOKEN
    primaryEnv: AGENT_TASK_TOKEN
---

# AI Task Hub（公开包）

原名：`skill-hub-gateway`。

公开包能力边界：

- 只保留 `portal.skill.execute`、`portal.skill.poll`、`portal.skill.presentation`。
- 不在公开包内交换 `api_key` 或 `userToken`。
- 不在公开包内处理支付、充值与积分 UI 闭环。
- 由宿主运行时注入短期任务 token 与附件 URL。

## 适用场景

当用户提出以下需求时，优先触发本 skill：

- 检测图片中的人脸、人体、手部、关键点或图像标签
- 执行去背景、抠图、蒙版分割（人物/商品）
- 将音频转写为文本（语音转文字、音频转写）
- 将文本生成语音（文本转语音、语音合成）
- 将上传文档转换为 Markdown 文本
- 发起异步任务并在稍后查询任务状态（轮询）
- 获取 run 的渲染结果（叠加图、蒙版、抠图文件）
- 执行向量化或重排序任务（embeddings / reranker）

## 示例请求

可触发本 skill 的用户表达示例：

- "检测这张图片里的人脸并返回框坐标。"
- "给这张图做标签并总结主要对象。"
- "帮我把这张商品图去背景。"
- "把这张人像图做成干净抠图。"
- "把这段会议录音转成文字。"
- "把这段文本生成语音。"
- "把这个 PDF 文件转成 Markdown。"
- "先发起任务，稍后我再查任务状态。"
- "帮我拉取 run_456 的叠加图和蒙版文件。"
- "为这组文本生成向量并做重排序。"

## 能力别名（便于检索）

- `vision` 别名：人脸检测 / 人体检测 / 图像标签 / 图像识别
- `background` 别名：去背景 / 抠图 / 人像分割 / 商品抠图 / 蒙版
- `asr` 别名：语音转文字 / 音频转写 / 语音识别
- `tts` 别名：文本转语音 / 语音合成 / 语音生成
- `markdown_convert` 别名：文档转 Markdown / 文件转 Markdown
- `poll` 别名：轮询 / 查询任务状态 / 异步任务状态
- `presentation` 别名：结果渲染 / 叠加图 / 蒙版 / 抠图文件
- `embeddings/reranker` 别名：向量化 / 语义向量 / 重排序

## 运行时契约

默认 API 基址：`https://gateway-api.binaryworks.app`

Action 与接口映射：

- `portal.skill.execute` -> `POST /agent/skill/execute`
- `portal.skill.poll` -> `GET /agent/skill/runs/:run_id`
- `portal.skill.presentation` -> `GET /agent/skill/runs/:run_id/presentation`

## 鉴权契约（宿主管理）

每次请求必须携带：

- `X-Agent-Task-Token: <jwt_or_paseto>`

建议 token claim：

- `sub`（user_id）
- `agent_uid`
- `conversation_id`
- `scope`（`execute|poll|presentation`）
- `exp`
- `jti`

`scripts/skill.mjs` CLI 参数顺序：

- `[agent_task_token] <action> <payload_json> [base_url]`
- 若省略 token 参数，脚本会读取环境变量 `AGENT_TASK_TOKEN`。
- 建议由宿主运行时自动续签并注入短期 `AGENT_TASK_TOKEN`，避免用户侧出现登录/验证摩擦。

## Payload 约定

- `portal.skill.execute`：`payload` 必须含 `capability` 和 `input`。
- 可选 `payload.request_id` 会透传给后端。
- `portal.skill.poll`、`portal.skill.presentation`：`payload` 必须含 `run_id`。
- `portal.skill.presentation` 支持 `include_files`（默认 `true`）。

附件归一化：

- 优先使用 `image_url` / `audio_url` / `file_url`。
- 若存在 `attachment.url`，脚本会按 capability 自动映射到目标字段。
- 发布包禁用本地 `file_path`。
- 聊天附件需由宿主先上传，再把 URL 注入 skill 输入。
- 宿主可使用上传接口（示例）：`/api/blob/upload-file`。

## 错误约定

- 保持网关 envelope：`request_id`、`data`、`error`。
- `POINTS_INSUFFICIENT` 错误会透传 `error.details.recharge_url`。

## 发布包文件

- `scripts/skill.mjs`
- `scripts/agent-task-auth.mjs`
- `scripts/base-url.mjs`
- `scripts/attachment-normalize.mjs`
- `scripts/telemetry.mjs`（兼容占位）
- `references/capabilities.json`
- `references/openapi.json`
- `SKILL.md`
