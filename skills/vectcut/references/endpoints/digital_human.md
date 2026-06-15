# Endpoint Params

## create_digital_human
- Method: `POST`
- Path: `/cut_jianying/digital_human/create`
- 用途：基于输入音频与视频创建数字人口播任务，返回异步任务信息。

### 请求参数
- `audio_url` (string, required): 音频链接。
- `video_url` (string, required): 视频链接。
- `license_key` (string, deprecated): 已废弃，不建议传入。

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/digital_human/create' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "audio_url": "https://oss-jianying-resource.oss-cn-hangzhou.aliyuncs.com/test/d0f39150-7b57-4d0d-bfca-730901dca0da-c5ef496b-07b6.mp3",
  "video_url": "https://oss-jianying-resource.oss-cn-hangzhou.aliyuncs.com/test/VID_20260114_231107.mp4"
}'
```

### 关键响应字段
- 回包字段以服务端实际返回为准，建议至少校验以下候选字段之一：
  - `task_id`
  - `id`
  - `output.task_id`
  - `output.id`

## digital_human_task_status
- Method: `GET`
- Path: `/cut_jianying/digital_human/task_status`
- 用途：查询数字人任务状态与结果。

### 请求参数
- Query `task_id` (string, optional): 任务 ID。建议必传。

### 示例请求
```bash
curl --location --request GET 'https://open.vectcut.com/cut_jianying/digital_human/task_status?task_id=TASK_ID' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json'
```

### 关键响应字段
- 回包字段以服务端实际返回为准，建议重点关注：
  - `status`
  - `progress`
  - `video_url` / `result_url`（完成态）
  - `error` / `message`

### 错误返回
- HTTP 非 2xx：鉴权或服务异常。
- 响应非 JSON：中止流程并保留原始响应。
- 创建任务回包缺少任务标识（`task_id/id`）：视为任务未创建成功。
