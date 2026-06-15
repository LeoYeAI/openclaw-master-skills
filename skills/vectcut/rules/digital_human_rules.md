# digital_human 端点规则（create_digital_human/digital_human_task_status）

## 适用范围
- `POST /cut_jianying/digital_human/create`
- `GET /cut_jianying/digital_human/task_status`

## 请求路由与参数策略
- 创建任务必填：`audio_url`、`video_url`。
- 查询任务建议必填：`task_id`。
- `license_key` 已废弃，默认不传。

## 专属异常处理
- 当 HTTP 状态码非 2xx：
  - 含义：鉴权失败、参数非法或服务端异常。
  - 处理：记录状态码与响应体；若为鉴权问题先检查 `VECTCUT_API_KEY`，再重试 1 次。
  - 重试上限：1 次。

- 当响应体不是合法 JSON：
  - 含义：网关异常或服务返回格式不符合约定。
  - 处理：保留原始响应体并中止，不做盲目重试。
  - 重试上限：0 次。

- 当创建任务响应缺少任务标识：
  - 判定：`task_id` / `id` / `output.task_id` / `output.id` 均缺失。
  - 含义：任务未创建成功。
  - 处理：标记失败并保留原始响应。
  - 重试上限：1 次。

- 当状态查询进入失败态：
  - 判定：`status` 为 `failed` / `failure` / `error`。
  - 处理：输出失败状态并停止轮询。
  - 重试上限：0 次。

## 诊断上下文
失败时至少保留：
- `endpoint`
- `error`
- `status_code`
- `raw_response`
- `task_id`
- `audio_url`
- `video_url`
