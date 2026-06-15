# Endpoint Params

## generate_ai_image
- Method: `POST`
- Path: `/cut_jianying/generate_image`
- 用途：调用聚合图像模型生成图片，并可直接写入草稿时间线。

### 请求参数
- `prompt` (string, required): 图像生成提示词。
- `model` (string, required): 建议值 `nano_banana_2`、`nano_banana_pro`、`jimeng-4.5`（兼容值 `nano_banana`）。
- `reference_image` (string, optional): 参考图 URL，支持图生图。
- `size` (string, optional): 输出尺寸，格式 `宽x高`，如 `1024x1024`、`1376x768`、`768x1376`。
- `draft_id` (string, optional): 草稿 ID，传入后将图片写入该草稿。
- `start`/`end` (number, optional): 入轨时间段（秒）。
- `width`/`height` (integer, optional): 画布尺寸。
- `transform_x`/`transform_y`/`scale_x`/`scale_y` (number, optional): 位置与缩放。
- `track_name` (string, optional): 轨道名，默认 `video_main`。
- `relative_index` (integer, optional): 图层相对顺序。
- `intro_animation`/`intro_animation_duration` (optional): 入场动画及持续时长。
- `outro_animation`/`outro_animation_duration` (optional): 出场动画及持续时长。
- `transition`/`transition_duration` (optional): 转场及时长。
- `mask_type` 与一组 `mask_*` 字段 (optional): 蒙版与蒙版几何参数。

### 模型与分辨率约束
- `nano_banana_2`、`nano_banana_pro`：支持 1K/2K/4K 多比例分辨率。
- `jimeng-4.5`：支持 1K/2K/4K，常用 `1:1`、`16:9`、`9:16`、`4:3`、`3:2`、`21:9`。
- 具体可选分辨率组合以官方文档为准。

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/generate_image' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "prompt": "给这个人带上红色的帽子",
  "model": "nano_banana_2",
  "reference_image": "https://oss-jianying-resource.oss-cn-hangzhou.aliyuncs.com/test/shuziren.jpg",
  "size": "1024x1024",
  "draft_id": "dfd_cat_xxx",
  "start": 1.0,
  "end": 5.0,
  "track_name": "video_main"
}'
```

### 关键响应字段
- `success` (boolean)
- `error` (string)
- `output.image_url` (string)
- `output.draft_id` (string)
- `output.draft_url` (string)

### 错误返回
- HTTP 非 2xx：鉴权或服务异常。
- `success=false` 或 `error` 非空：业务失败，修正参数后重试。
- 响应非 JSON：中止流程并保留原始响应。
- 缺少 `output.image_url`：视为生成结果不可用。