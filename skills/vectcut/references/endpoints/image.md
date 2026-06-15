# Endpoint Params

## intro_animation 枚举来源

- `references/enums/intro_animation_types.json`

## outro_animation 枚举来源

- `references/enums/outro_animation_types.json`

## combo_animation 枚举来源

- `references/enums/combo_animation_types.json`

## mask_type 枚举来源

- `references/enums/mask_types.json`

- Method: `POST`
- Path: `/cut_jianying/add_image`
- 用途: `向草稿中添加图片`

### 请求参数

- `image_url` (string, required): 图片链接
- `start` (number, optional): 在目标轨道上的开始时间，单位秒，默认0
- `end` (number, required): 在目标轨道上的结束时间，单位秒
- `width` (integer, optional): 草稿画布的宽度，非当前图片的宽度。如果之前已经设置过，则不能重复设置
- `height` (integer, optional): 草稿画布的高度，非当前图片的宽度。如果之前已经设置过，则不能重复设置
- `draft_id` (string, optional): 目标草稿的草稿id，如果不提供，或者云端不存在，则会自动创建一个新的草稿
- `transform_x` (number, optional): 水平移动，相对值。0表示位于中心，水平移动像素 = transform_x \* 草稿宽度
- `transform_x_px` (integer, optional) :水平移动，像素值
- `transform_y` (number, optional): 垂直移动，相对值。0表示位于中心，垂直移动像素 = transform_y \* 视频高度
- `transform_y_px` (string, optional) :垂直移动，像素值
- `scale_x` (number, optional): 水平方向缩放，1.5表示放大到原始图片的1.5倍
- `scale_y` (number, optional): 垂直方向缩放，1.5表示放大到原始图片的1.5倍
- `track_name` (string, optional): 添加的轨道名称，默认image_main。设置为main则位于主轨道
- `relative_index` (integer, optional): 轨道相对位置，越大越靠前
- `intro_animation` (string, optional): 入场动画名
- `intro_animation_duration` (number, optional): 入场动画时间，单位秒
- `outro_animation` (string, optional): 出场动画名，
- `outro_animation_duration` (number, optional): 出场动画时间，单位秒
- `combo_animation` (string, optional): 组合动画名
- `combo_animation_duration` (number, optional): 组合动画时间，单位秒
- `transition` (string, optional): 转场动画，直接查 `references/enums/transition_types.json` 的 `items.name`。
- `transition_duration` (number, optional): 转场动画持续时间，单位秒。
- 转场生效条件：仅当两个相邻图片/视频片段首尾紧邻时生效（后一个 `target_start` - 前一个 `target_end` < `0.01`），且转场参数需要加在前一个元素上。
- `mask_type` (string, optional): 蒙版类型，例如“矩形”
- `mask_center_x` (number, optional): 蒙版中心点坐标，0表示中心，0.5表示向右移动0.5个宽度
- `mask_center_y` (number, optional): 蒙版中心点坐标，0表示中心，0.5表示向下移动0.5个高度
- `mask_size` (number, optional): 蒙版的主要尺寸，以草稿高度的比例表示，默认为0.5
- `mask_rotation` (number, optional): 蒙版旋转角度，默认不旋转
- `mask_feather` (number, optional): 蒙版羽化度，取值范围0~100，默认无羽化
- `mask_invert` (boolean, optional): 蒙版翻转，默认不反转
- `mask_rect_width` (number, optional): 蒙版矩形宽度，仅在蒙版类型为矩形时允许设置，以占素材宽度的比例表示
- `mask_round_corner` (number, optional): 蒙版圆角，仅在蒙版类型为矩形时允许设置，取值范围0~100
- `background_blur` (integer, optional): 背景模糊，1,2,3,4四档可选。track_name设置为main才会生效
- `alpha` (number, optional): 透明度，0-1
- `flip_horizontal` (boolean, optional): 是否镜像反转，默认false
- `rotation` (number, optional)：旋转角度
- `mix_type` (string, optional): 混合模式，目前只支持“正片叠底”

### 示例请求

```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/add_image' \
--header 'Authorization: Bearer  <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "image_url": "https://pic1.imgdb.cn/item/68ba8fc058cb8da5c8801ab0.png",
  "start": 0,
  "end": 5.0,
  "width": 1920,
  "height": 1080,
  "transform_x": 0.2,
  "transform_y": 0.2,
  "scale_x": 1,
  "scale_y": 1,
  "track_name": "video_main",
  "relative_index": 99,
  "intro_animation": "放大",
  "intro_animation_duration": 0.5,
  "outro_animation": "闪现",
  "outro_animation_duration": 0.5,
  "transition": "上移",
  "transition_duration": 0.5,
  "mask_type": "矩形",
  "mask_center_x": 0.5,
  "mask_center_y": 0.5,
  "mask_size": 0.7,
  "mask_rotation": 45.0,
  "mask_feather": 2,
  "mask_invert": true,
  "mask_rect_width": 8,
  "mask_round_corner": 10
}'
```

### 关键响应字段

- `success`
- `error`
- `output`
- `purchase_link`
- `output.draft_id`
- `output.draft_url`
- `output.material_id`（常见于 add/modify）

## modify_image
- Method: `POST`
- Path: `/cut_jianying/modify_image`
- 用途: `根据 material_id 修改图片素材（可更新图片源、时长、位置、动画、透明度、旋转等）`

### 请求参数
- 必填：`draft_id`、`material_id`
- 常用：`image_url`、`start`、`end`、`scale_x`、`scale_y`、`transform_x_px`、`transform_y_px`、`track_name`、`relative_index`
- 动画：`intro_animation`、`intro_animation_duration`、`outro_animation`、`outro_animation_duration`、`transition`
- 其他：`alpha`、`rotation`

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/modify_image' \
--header 'Authorization: Bearer  <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "material_id": "3a6a87bf72cf4014b808edc269865f83",
  "draft_id": "dfd_cat_1774083194_49b60636",
  "image_url": "https://example.com/new.png",
  "start": 15.3,
  "end": 25.2,
  "scale_x": 0.7,
  "scale_y": 0.7,
  "transform_x_px": 470,
  "transform_y_px": 490,
  "track_name": "test_mmain1",
  "relative_index": 63,
  "outro_animation": "缩小",
  "outro_animation_duration": 2,
  "alpha": 0.55,
  "rotation": 44
}'
```

## remove_image
- Method: `POST`
- Path: `/cut_jianying/remove_image`
- 用途: `根据 material_id 删除图片素材`

### 请求参数
- 必填：`draft_id`、`material_id`

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/remove_image' \
--header 'Authorization: Bearer  <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "material_id": "b6746268cdbb46a1859bde7d9abad58a",
  "draft_id": "dfd_cat_1774083194_49b60636"
}'
```
