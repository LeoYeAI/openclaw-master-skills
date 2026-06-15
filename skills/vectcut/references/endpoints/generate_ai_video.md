# Endpoint Params

## generate_ai_video
- Method: `POST`
- Path: `/cut_jianying/generate_ai_video`
- 用途：调用聚合视频模型生成视频，返回异步任务 `task_id`。

### 请求参数
- `prompt` (string, required): 视频生成提示词。
- `model` (string, required): 模型名，常用 `veo3.1`、`veo3.1-pro`、`seedance-1.5-pro`、`grok-video-3`、`sora2`。
- `resolution` (string, required): 输出分辨率，格式 `宽x高`，如 `1280x720`、`1080x1920`。
- `reference_image` (string|array<string>, optional): 参考图 URL，支持首帧扩展或多图参考（按模型能力）。
- `end_image` (string, optional): 尾帧图片 URL，支持首尾帧模型可传。
- `gen_duration` (integer, optional): 生成时长（秒），仅支持该参数的模型可传。
- `draft_id` (string, optional): 草稿 ID，传入后可在成功态回包里关联草稿信息。
- `target_start` (number, optional): 入轨起点（秒）。
- `track_name` (string, optional): 轨道名称，默认 `video_main`。
- `relative_index` (integer, optional): 轨道内相对层级。
- `transform_x`/`transform_y`/`scale_x`/`scale_y`/`speed`/`volume` (number, optional): 位置、缩放、速度、音量。
- `transition`/`transition_duration` (optional): 转场及时长。
- `mask_type` 与 `mask_*` (optional): 蒙版与几何参数。

### 模型能力约束
- `veo3.1`/`veo3.1-pro`：支持首帧扩展、首尾帧、多图参考（最多 3 张）；不支持 `gen_duration`。
- `seedance-1.5-pro`：支持首帧、首尾帧、多图参考；支持 `gen_duration`（4~12）。
- `grok-video-3`：支持首帧扩展；不支持首尾帧与多图参考；支持 `gen_duration`（6/10/15）。
- `sora2`：支持首帧扩展；不支持首尾帧与多图参考；支持 `gen_duration`（10/15），且不建议使用真人照片作为参考图。

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/generate_ai_video' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "model": "veo3.1",
  "prompt": "一张超写实的微距照片，照片中，迷你冲浪者在古朴的石制浴室水槽内乘风破浪。",
  "resolution": "1080x1920",
  "target_start": 1.2,
  "track_name": "video_main"
}'
```

### 关键响应字段
- `status` (string)
- `task_id` (string)

## ai_video_task_status
- Method: `GET`
- Path: `/cut_jianying/aivideo/task_status`
- 用途：查询 AI 视频聚合任务状态，获取进度、草稿与视频结果。

### 请求参数
- Query `task_id` (string, required): `generate_ai_video` 返回的任务 ID。

### 示例请求
```bash
curl --location --request GET 'https://open.vectcut.com/cut_jianying/aivideo/task_status?task_id=AEA270BE7BEE0001160E360AABEFF17D' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json'
```

### 关键响应字段
- `status` (string): `processing` / `completed` / `failed` 等。
- `progress` (number)
- `video_url` (string，完成态可用)
- `draft_id` (string)
- `draft_url` (string)
- `draft_error` (string)

### 错误返回
- HTTP 非 2xx：鉴权或服务异常。
- 响应非 JSON：中止流程并保留原始响应。
- 生成接口缺少 `task_id`：视为任务未创建成功。
- 状态查询接口在完成态缺少 `video_url`：视为结果不可用。
