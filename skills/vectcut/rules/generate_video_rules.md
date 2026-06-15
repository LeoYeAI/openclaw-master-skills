# 云渲染规则（generate_video / task_status）

## 适用范围
- `POST /cut_jianying/generate_video`
- `POST /cut_jianying/task_status`

## 调用策略
- 云渲染有两类用途：
  - 创作过程核验：在关键里程碑发起渲染，验证当前画面与预期一致。
  - 最终交付导出：任务结束时可选渲染成片并返回可播放链接。
- 标准流程：`generate_video -> task_status(轮询)`。
- 轮询终止条件：
  - 成功：`output.result` 非空。
  - 失败：`output.status=FAILURE`。
  - 超时：达到最大轮询次数仍非成功。

## 专属异常处理
- 当 HTTP 非 2xx：
  - 含义：鉴权或服务异常。
  - 处理：检查 `VECTCUT_API_KEY`、`draft_id/task_id` 后重试。
  - 重试上限：1 次。

- 当 `generate_video` 响应缺少 `output.task_id`：
  - 含义：无法进入轮询阶段。
  - 处理：中止并保留原始响应。
  - 重试上限：0 次。

- 当 `task_status` 缺少 `output.status`：
  - 含义：任务状态不可判定。
  - 处理：忽略并继续处理。

- 当 `output.status=FAILURE`：
  - 含义：渲染任务失败。
  - 处理：返回失败信息，不再继续轮询。
  - 重试上限：0 次。

## 诊断上下文
失败时至少保留：
- `endpoint`
- `draft_id`
- `task_id`
- `status`
- `progress`
- `error`