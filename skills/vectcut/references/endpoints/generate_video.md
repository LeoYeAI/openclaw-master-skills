# Endpoint Params

## generate_video
- Method: `POST`
- Path: `/cut_jianying/generate_video`
- 用途：对指定草稿发起云渲染，生成异步任务 `task_id`。

### 请求参数
- `draft_id` (string, required): 目标草稿 ID。
- `resolution` (string, optional): 分辨率，默认 `720P`，常用值 `480P/720P/1080P/2K/4K`。
- `framerate` (string, optional): 帧率，默认 `24`，常用值 `24/25/30/50/60`。

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/generate_video' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{"draft_id":"dfd_xxx","resolution":"1080P","framerate":"30"}'
```

### 关键响应字段
- `success` (boolean)
- `error` (string)
- `output.success` (boolean)
- `output.task_id` (string)

### 错误返回
- HTTP 非 2xx：鉴权或服务异常，检查 `VECTCUT_API_KEY` 与 `draft_id`。
- 响应非 JSON 或缺少 `output.task_id`：中止轮询，保留原始响应。

## task_status
- Method: `POST`
- Path: `/cut_jianying/task_status`
- 用途：按 `task_id` 轮询云渲染状态，获取中间进度或最终播放链接。

### 请求参数
- `task_id` (string, required): `generate_video` 返回的任务 ID。

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/task_status' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{"task_id":"6c653617-8133-4c51-8bd0-8635e9e25879"}'
```

### 关键响应字段
- `success` (boolean，网络请求成功，这里仅表示服务握手成功，并不代表业务处理成功)
- `error` (string，网络错误，这里展示的是请求task_status接口的网络错误，不代表业务错误)
- `output.status` (状态枚举，PENDING:排队中。PROCESSING:处理素材。UPLOADING：上传中。SUCCESS:成功。DOWNLOADING：下载素材。EXPORTING：导出中。FAILURE：失败)
- `output.error` (string，业务错误，如果导出失败，这里将会返回具体的错误信息，例如素材丢失，超时等)
- `output.message` (string, 消息，例如“排队，导出，上传，成功，错误“等等)
- `output.result` (string, 正确结果，只有当导出成功，这里才会展示导出的视频链接。)
- `output.success` (boolean, 是否成功，只有当任务成功才会置为true。任务失败，正在处理中都会置为false)
- `output.task_id` (string, 当前任务的唯一ID)
- `output.progress` (number|string|null)

### 错误返回
- HTTP 非 2xx：鉴权或服务异常。
- `output.status=FAILURE`：渲染失败，停止轮询并输出失败原因。
- 超过轮询上限仍未成功：返回超时错误，保留最后一次状态。