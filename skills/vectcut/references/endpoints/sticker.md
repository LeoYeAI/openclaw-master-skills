# Endpoint Params

## search_sticker

- Method: `POST`
- Path: `/cut_jianying/search_sticker`
- 用途: `从贴纸库里搜索可用的贴纸，通过搜索贴纸id可以查看可用贴纸id`

### 请求参数
- `keywords` (string, required): 搜索关键词（必填，用于在贴纸库中查找相关贴纸）
- `count` (integer, optional)
- `offset` (integer, optional)

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/search_sticker' \
--header 'Authorization: Bearer  <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
    "keywords": "生日快乐", // 搜索关键词（必填，用于在贴纸库中查找相关贴纸）
    "count": 3,
    "offset": 2
}'
```

### 关键响应字段
- `success`
- `error`
- `output`
- `output.data`

## add_sticker

- Method: `POST`
- Path: `/cut_jianying/add_sticker`
- 用途: `添加贴纸, 通过搜索贴纸id可以查看可用贴纸id`

### 请求参数
- `sticker_id` (string, required): 贴纸资源ID（必填，通过/search_sticker接口获取的贴纸唯一标识）
- `start` (number, optional): 贴纸开始显示时间（秒，选填，默认0）
- `end` (number, optional): 贴纸结束显示时间（秒，选填，默认5.0）
- `draft_id` (string, optional): 草稿ID（选填，指定要添加贴纸的目标草稿）
- `transform_y` (number, optional): 垂直偏移，相对值。0表示位于中心，垂直移动像素 = transform_y * 视频高度
- `transform_y_px` (integer, optional): 垂直位置偏移，像素值
- `transform_x` (number, optional): 水平偏移，相对值。0表示位于中心，水平移动像素 = transform_x * 草稿宽度
- `transform_x_px` (integer, optional): 水平位置偏移，像素值
- `alpha` (number, optional): 贴纸透明度（选填，默认1.0，范围0.0-1.0，1.0为完全不透明）
- `flip_horizontal` (boolean, optional): 是否水平翻转（选填，默认false）
- `flip_vertical` (boolean, optional): 是否垂直翻转（选填，默认false）
- `rotation` (number, optional): 旋转角度（度，选填，默认0.0）
- `scale_x` (number, optional): X轴缩放比例（选填，默认1.0）
- `scale_y` (number, optional): Y轴缩放比例（选填，默认1.0）
- `track_name` (string, optional)
- `relative_index` (integer, optional): 相对索引（选填，默认0，控制轨道内贴纸的层级顺序）
- `width` (integer, optional): 画布宽度（选填，默认1080）
- `height` (integer, optional): 画布高度（选填，默认1920）

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/add_sticker' \
--header 'Authorization: Bearer  <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
    "sticker_id": "7132097333466025252",  // 贴纸资源ID（必填，通过/search_sticker接口获取的贴纸唯一标识）
    "start": 0,  // 贴纸开始显示时间（秒，选填，默认0）
    "end": 5.0,  // 贴纸结束显示时间（秒，选填，默认5.0）
    "draft_id": "draft_67890",  // 草稿ID（选填，指定要添加贴纸的目标草稿）
    "transform_y": 0,  // Y轴位置偏移（选填，默认0）
    "transform_x": 0,  // X轴位置偏移（选填，默认0）
    "alpha": 1.0,  // 贴纸透明度（选填，默认1.0，范围0.0-1.0，1.0为完全不透明）
    "flip_horizontal": false,  // 是否水平翻转（选填，默认false）
    "flip_vertical": false,  // 是否垂直翻转（选填，默认false）
    "rotation": 0.0,  // 旋转角度（度，选填，默认0.0）
    "scale_x": 1.0,  // X轴缩放比例（选填，默认1.0）
    "scale_y": 1.0,  // Y轴缩放比例（选填，默认1.0）
    "track_name": "sticker_main",  // 轨道名称（选填，默认"sticker_main"，用于区分不同贴纸轨道）
    "relative_index": 0,  // 相对索引（选填，默认0，控制轨道内贴纸的层级顺序）
    "width": 1080,  // 画布宽度（选填，默认1080）
    "height": 1920  // 画布高度（选填，默认1920）
}'
```

### 关键响应字段
- `success`
- `error`
- `output`
- `purchase_link`
- `success`
- `output.draft_id`
- `output.draft_url`
