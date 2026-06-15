# Endpoint Params

## add_video / modify_video / remove_video

- Method: `POST`
- Path: `/cut_jianying/add_video`
- 用途: `添加视频`

### 请求参数
- `video_url` (string, required): 视频资源URL（必填，用于获取视频素材）
- `start` (number, optional): 视频素材的起始截取时间（秒，选填，默认0）
- `end` (number, optional): 视频素材的结束截取时间（秒，选填，默认表示截取至视频末尾）
- `width` (integer, optional): 草稿画布的宽度，非当前视频的宽度。如果之前已经设置过，则不能重复设置
- `height` (integer, optional): 草稿画布的高度，非当前视频的高度。如果之前已经设置过，则不能重复设置
- `draft_id` (string, optional): 草稿ID（选填，用于关联目标草稿）
- `transform_y` (number, optional): 垂直偏移，相对值。0表示位于中心，垂直移动像素 = transform_y * 视频高度
- `transform_y_px` (integer, optional)
- `scale_x` (number, optional): 水平方向缩放，1.5表示放大到原始视频的1.5倍
- `scale_y` (number, optional): 垂直方向缩放，1.5表示放大到原始视频的1.5倍
- `transform_x` (number, optional): 水平偏移，相对值。0表示位于中心，水平移动像素 = transform_x * 草稿宽度
- `transform_x_px` (integer, optional)
- `speed` (number, optional): 视频播放速度（选填，默认1.0，大于1为加速，小于1为减速）
- `target_start` (number, optional): 视频在时间线上的起始位置（秒，选填，默认0）
- `track_name` (string, optional): 添加的轨道名称，默认video_main。设置为main则位于主轨道
- `relative_index` (integer, optional): 轨道相对位置，越大越靠前
- `intro_animation` (string, optional): 入场动画名，用get_intro_animation_types查看支持的入场动画名
- `intro_animation_duration` (number, optional): 入场动画时间，单位秒
- `outro_animation` (string, optional): 出场动画名，用get_outro_animation_types查看支持的出场动画
- `outro_animation_duration` (number, optional): 出场动画时间，单位秒
- `duration` (number, optional): 原始素材的时长，单位秒，精确到小数点后6位。正确设置可以提升运行速度，但是设置错误可能带来不可预知的错误。
- `transition` (string, optional): 转场动画，直接查 `references/enums/transition_types.json` 的 `items.name`。
- `transition_duration` (number, optional): 转场持续时间（秒，选填，默认0.5）。
- 转场生效条件：仅当两个相邻图片/视频片段首尾紧邻时生效（后一个 `target_start` - 前一个 `target_end` < `0.01`），且转场参数需要加在前一个元素上。
- `volume` (number, optional): 音量（选填，单位db，默认0.0，-100表示静音）
- `mask_type` (string, optional): 蒙版类型（选填，如圆形、矩形等）
- `mask_center_x` (number, optional): 蒙版中心点坐标，0表示中心，0.5表示向右移动0.5个宽度
- `mask_center_y` (number, optional): 蒙版中心点坐标，0表示中心，0.5表示向下移动0.5个高度
- `mask_size` (number, optional): 蒙版的主要尺寸，以草稿高度的比例表示，默认为0.5
- `mask_rotation` (number, optional): 蒙版旋转角度（选填，默认0.0度）
- `mask_feather` (number, optional): 蒙版羽化程度（选填，默认0.0，值越大边缘越柔和）
- `mask_invert` (boolean, optional): 是否反转蒙版（选填，默认false）
- `mask_rect_width` (number, optional): 蒙版矩形宽度，仅在蒙版类型为矩形时允许设置，以占素材宽度的比例表示
- `mask_round_corner` (number, optional): 蒙版圆角，仅在蒙版类型为矩形时允许设置，取值范围0~100
- `background_blur` (number, optional): 背景模糊，1,2,3,4四档可选
- `alpha` (number, optional)
- `flip_horizontal` (boolean, optional): 镜像反转，默认false
- `mix_type` (string, optional): 混合模式，目前只支持“正片叠底”

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/add_video' \
--header 'Authorization: Bearer  <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
    "video_url": "https://cdn.wanx.aliyuncs.com/wanx/1719234057367822001/text_to_video/092faf3c94244973ab752ee1280ba76f.mp4?spm=5176.29623064.0.0.41ed26d6cBOhV3&file=092faf3c94244973ab752ee1280ba76f.mp4",  // 视频资源URL（必填，用于获取视频素材）
    "start": 0,  // 视频素材的起始截取时间（秒，选填，默认0）
    "end": 0,  // 视频素材的结束截取时间（秒，选填，默认0，0通常表示截取至视频末尾）
    "width": 1080,  // 画布宽度（选填，默认1080）
    "height": 1920,  // 画布高度（选填，默认1920）
    "draft_id": "draft_123456",  // 草稿ID（选填，用于关联目标草稿）
    "transform_y": 0,  // Y轴位置偏移（选填，默认0）
    "scale_x": 1,  // X轴缩放比例（选填，默认1）
    "scale_y": 1,  // Y轴缩放比例（选填，默认1）
    "transform_x": 0,  // X轴位置偏移（选填，默认0）
    "speed": 1.0,  // 视频播放速度（选填，默认1.0，大于1为加速，小于1为减速）
    "target_start": 0,  // 视频在时间线上的起始位置（秒，选填，默认0）
    "track_name": "video_main",  // 轨道名称（选填，默认"video_main"）
    "relative_index": 0,  // 相对索引（选填，默认0，用于控制轨道内素材的排列顺序）
    "duration": null,  // 视频素材的总时长（秒，选填，主动设置可以提升当前节点运行速度）
    "transition": "云朵",  // 转场类型（选填，如"云朵"等，需与支持的类型匹配）
    "transition_duration": 0.5,  // 转场持续时间（秒，选填，默认0.5）
    "volume": 1.0,  // 视频音量（选填，默认1.0，范围通常为0.0-1.0）
    // 蒙版相关参数
    "mask_type": "圆形",  // 蒙版类型（选填，如圆形、矩形等）
    "mask_center_x": 0.5,  // 蒙版中心X坐标（选填，默认0.5，相对屏幕宽度比例）
    "mask_center_y": 0.5,  // 蒙版中心Y坐标（选填，默认0.5，相对屏幕高度比例）
    "mask_size": 1.0,  // 蒙版大小（选填，默认1.0，相对屏幕高度比例）
    "mask_rotation": 0.0,  // 蒙版旋转角度（选填，默认0.0度）
    "mask_feather": 0.0,  // 蒙版羽化程度（选填，默认0.0，值越大边缘越柔和）
    "mask_invert": false,  // 是否反转蒙版（选填，默认false）
    "mask_rect_width": null,  // 矩形蒙版宽度（选填，仅mask_type为矩形时有效）
    "mask_round_corner": null  // 矩形蒙版圆角（选填，仅mask_type为矩形时有效）
}'
```

### 关键响应字段
- `success`
- `error`
- `output`
- `purchase_link`
- `output.draft_id`
- `output.draft_url`
- `output.material_id`（add/modify 常见返回）

## modify_video
- Method: `POST`
- Path: `/cut_jianying/modify_video`
- 用途: `根据 material_id 修改视频素材`

### 请求参数
- 必填：`draft_id`、`material_id`
- 常用：`video_url`、`start`、`end`、`transform_x`、`transform_y`、`scale_x`、`scale_y`、`speed`、`target_start`、`relative_index`、`volume`
- 可选：`flip_horizontal`、`track_name`、`intro_animation`、`outro_animation`、`transition` 等

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/modify_video' \
--header 'Authorization: Bearer  <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "draft_id": "dfd_cat_1774145590_a398e5b3",
  "material_id": "293a3b6e56414e96b51351d588b2e9f3",
  "video_url": "https://player.install-ai-guider.top/example/VID_20260120_211842.mp4",
  "start": 0,
  "end": 10,
  "transform_x": 0.6,
  "transform_y": 0.6,
  "scale_x": 1.1,
  "scale_y": 1.1,
  "speed": 1.0,
  "target_start": 12,
  "relative_index": 0,
  "volume": 15.0
}'
```

## remove_video
- Method: `POST`
- Path: `/cut_jianying/remove_video`
- 用途: `根据 material_id 删除视频素材`

### 请求参数
- 必填：`material_id`、`draft_id`

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/remove_video' \
--header 'Authorization: Bearer  <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "material_id": "8822537f77424064bce925a830a602da",
  "draft_id": "dfd_cat_1774145590_a398e5b3"
}'
```
