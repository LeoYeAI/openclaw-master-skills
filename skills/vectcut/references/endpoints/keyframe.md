# Endpoint Params

## add_video_keyframe
- Method: `POST`
- Path: `/cut_jianying/add_video_keyframe`
- 用途：给文字、图片、视频素材添加关键帧，可控制位置、缩放、透明度、旋转等属性。

### 请求参数
- `draft_id` (string, required): 草稿 ID。
- `track_name` (string, optional): 轨道名称，默认 `video_main`。

单关键帧（向后兼容）：
- `property_type` (string, optional): 属性类型，默认 `alpha`。
- `time` (number, optional): 关键帧时间点（秒），默认 `0.0`。
- `value` (string|number, optional): 属性值，默认 `1.0`。

批量关键帧（推荐）：
- `property_types` (array<string>, optional): 属性类型数组。
- `times` (array<number>, optional): 时间数组（秒）。
- `values` (array<string|number>, optional): 属性值数组。

### 参数约束
- 批量模式下，`property_types`、`times`、`values` 必须同时出现。
- 批量模式下，三组数组长度必须一致。
- 当单关键帧与批量参数同时出现时，优先按批量参数处理。
- 常见 `property_type`：`alpha`、`scale_x`、`scale_y`、`transform_x`、`transform_y`、`rotation`。

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/add_video_keyframe' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "draft_id": "dfd_cat_1753709045_3a033ea7",
  "track_name": "video_main",
  "property_types": ["alpha", "scale_x", "scale_y"],
  "times": [0.0, 1.2, 2.4],
  "values": ["1.0", "1.2", "0.9"]
}'
```

### 关键响应字段
- `success` (boolean)
- `error` (string)
- `output.added_keyframes_count` (integer)
- `output.draft_id` (string)
- `output.draft_url` (string)

### 错误返回
- HTTP 非 2xx：鉴权或服务异常，先检查 `VECTCUT_API_KEY`。
- `success=false` 或 `error` 非空：业务失败，修正参数后重试。
- 响应非 JSON：中止流程并保留原始响应。
- 缺少 `output.draft_id`/`output.draft_url`：视为结果不可继续追踪。
- 缺少 `output.added_keyframes_count`：视为关键帧写入结果不可确认。