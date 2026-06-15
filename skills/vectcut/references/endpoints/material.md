# Endpoint Params

## get_duration

- Method: `POST`
- Path: `/cut_jianying/get_duration`
- 用途：获取音频/视频素材的原始时长，供分镜规划与音画对齐使用。

### 请求参数
- `url` (string, required): 待解析的音频或视频 URL，需可公网访问。

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/llm/video_detail' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "video_url":"https://example.com/demo.mp4"
}'
```

### 关键响应字段
- `success` (boolean)
- `error` (string)
- `output.duration` (number, 素材时长，单位秒)
- `output.video_url` (string, 服务侧识别后的素材 URL)
- `purchase_link` (string)

### 错误返回
- `success=false` 或 `error` 非空：素材解析失败或 URL 不可访问，可再重试一次。
- HTTP 非 2xx：鉴权或服务异常，先检查 `VECTCUT_API_KEY` 与请求体，再重试 1 次。
- 响应非 JSON 或 `output.duration`为0：视为不可用结果，可再重试1次。

## get_resolution

- Method: `POST`
- Path: `/cut_jianying/get_resolution`
- 用途：获取视频/图片素材的原始分辨率，供画幅校验与排版策略使用。

### 请求参数
- `url` (string, required): 待解析的视频或图片 URL，需可公网访问。

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/get_resolution' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "url":"https://example.com/demo.mp4"
}'
```

### 关键响应字段
- `success` (boolean)
- `error` (string)
- `output.width` (number, 素材宽度，单位像素)
- `output.height` (number，素材高度，单位像素)
- `output.video_url` (string, 服务侧识别后的素材 URL)
- `purchase_link` (string)

### 错误返回
- `success=false` 或 `error` 非空：素材解析失败或 URL 不可访问，再重试 1 次。
- HTTP 非 2xx：鉴权或服务异常，先检查 `VECTCUT_API_KEY` 与请求体，再重试 1 次。
- 响应非 JSON 或 `output.width/output.height` 为0：视为不可用结果，再重试 1 次。

## video_detail

- Method: `POST`
- Path: `/llm/video_detail`
- 用途：利用大模型对视频内容做细粒度文字描述，产出可用于脚本规划与镜头理解的语义结果。

### 请求参数
- `video_url` (string, required): 待分析的视频 URL，需可公网访问。

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/video_detail' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "url":"https://example.com/demo.mp4"
}'
```

### 关键响应字段
- `success` (boolean)
- `error` (string)
- `result` (object)
- `output.video_detail` (string, 大模型视觉理解结果)
- `purchase_link` (string)

### 错误返回
- `success=false` 或 `error` 非空：视频理解失败或 URL 不可访问，更换可访问 URL 后重试 1 次。
- HTTP 非 2xx：鉴权或服务异常，先检查 `VECTCUT_API_KEY` 与请求体，再重试 1 次。
- 响应非 JSON 或缺少 `output`：视为不可用结果，保留原始响应并中止后续理解流程。