# Endpoint Params

## extract_audio
- Method: `POST`
- Path: `/process/extract_audio`
- 用途：从视频中提取音频，输出可直接下载/复用的音频链接。

### 请求参数
- `video_url` (string, required): 待提取音频的视频 URL（需公网可访问）。

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/process/extract_audio' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{"video_url":"https://example.com/demo.mp4"}'
```

### 关键响应字段
- `code` (number)
- `message` (string)
- `data.public_url` (string, 音频结果 URL)

## split_video
- Method: `POST`
- Path: `/process/split_video`
- 用途：按时间区间切分视频或音频，输出切片结果链接。

### 请求参数
- `video_url` (string, required): 待切分媒体 URL。
- `start` (number, required): 起始时间（秒）。
- `end` (number, required): 结束时间（秒），必须大于 `start`。

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/process/split_video' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{"video_url":"https://example.com/demo.mp4","start":3.3,"end":5.1}'
```

### 关键响应字段
- `code` (number)
- `message` (string)
- `data.public_url` (string, 切分后媒体 URL)

### 错误返回
- HTTP 非 2xx：鉴权或服务异常。
- `code != 200`：业务失败，优先检查 URL 可访问性与 `start/end` 合法性。
- 缺少 `data.public_url`：视为不可用结果，停止后续编排。