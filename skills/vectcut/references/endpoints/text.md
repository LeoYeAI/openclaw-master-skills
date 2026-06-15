# Endpoint Params

## add_text
- Method: `POST`
- Path: `/cut_jianying/add_text`
- 用途：向草稿新增文本素材，支持字体、描边、背景、动画与局部样式。

### 请求参数
#### 必填
- `text` (string): 文本内容。
- `start` (number): 时间线起始时间（秒）。
- `end` (number): 时间线结束时间（秒），必须 `end > start`。

#### 草稿与轨道
- `draft_id` (string, optional): 草稿 ID。
- `track_name` (string, optional, 默认 `text_main`): 目标轨道名。

#### 位置与布局
- `transform_x` (number, optional, 默认 `0`): X 轴位移。
- `transform_y` (number, optional, 默认 `0`): Y 轴位移。
- `vertical` (boolean, optional, 默认 `false`): 是否竖排文本。
- `width` (number, optional, 默认 `1080`): 画布宽度。
- `height` (number, optional, 默认 `1920`): 画布高度。
- `fixed_width` (number, optional, 默认 `-1`): 文本固定宽度，`-1` 表示不固定。
- `fixed_height` (number, optional, 默认 `-1`): 文本固定高度，`-1` 表示不固定。

#### 字体与文字样式
- `font` (string, optional, 默认 `系统`): 字体名称，取值建议来自 `references/enums/font_types.json` 的 `items.name`。
- `font_color` (string, optional, 默认 `#FF0000`): 字体颜色，HEX 格式。
- `font_size` (number, optional, 默认 `8.0`): 字号。
- `font_alpha` (number, optional, 默认 `1.0`, 范围 `0.0~1.0`): 字体透明度。

#### 描边
- `border_alpha` (number, optional, 默认 `1.0`): 描边透明度。
- `border_color` (string, optional, 默认 `#000000`): 描边颜色，HEX 格式。
- `border_width` (number, optional, 默认 `0.0`): 描边宽度。

#### 背景
- `background_color` (string, optional, 默认 `#000000`): 背景颜色，HEX 格式。
- `background_style` (number, optional, 默认 `0`): 背景样式（需匹配服务端支持枚举）。
- `background_alpha` (number, optional, 默认 `0.0`): 背景透明度。

#### 动画
- `intro_animation` (string, optional): 入场动画类型，取值建议来自 `references/enums/text_intro_anims.json` 的 `items.name`。
- `intro_duration` (number, optional, 默认 `0.5`): 入场动画时长（秒）。
- `outro_animation` (string, optional): 出场动画类型，取值建议来自 `references/enums/text_outro_anims.json` 的 `items.name`。
- `outro_duration` (number, optional, 默认 `0.5`): 出场动画时长（秒）。
- `loop_animation` (string, optional): 循环动画类型，取值建议来自 `references/enums/text_loop_anims.json` 的 `items.name`。

#### 局部样式 `text_styles`
- `text_styles` (array, optional): 按字符区间覆盖样式。
- `text_styles[].start` (integer): 起始字符下标（包含）。
- `text_styles[].end` (integer): 结束字符下标（不包含），必须 `end > start`。
- `text_styles[].font` (string, optional): 该区间字体。
- `text_styles[].style.size` (number, optional): 该区间字号。
- `text_styles[].style.bold` (boolean, optional): 是否加粗。
- `text_styles[].style.italic` (boolean, optional): 是否斜体。
- `text_styles[].style.underline` (boolean, optional): 是否下划线。
- `text_styles[].style.color` (string, optional): 该区间字体颜色，HEX。
- `text_styles[].border.alpha` (number, optional): 该区间描边透明度。
- `text_styles[].border.color` (string, optional): 该区间描边颜色，HEX。
- `text_styles[].border.width` (number, optional): 该区间描边宽度。

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/add_text' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "text":"你好!Hello",
  "start":0,
  "end":5,
  "draft_id":"your_draft_id",
  "font":"文轩体",
  "font_color":"#FF0000",
  "font_size":8.0,
  "track_name":"text_main",
  "intro_animation":"向下飞入",
  "intro_duration":0.5,
  "outro_animation":"向下滑动",
  "outro_duration":0.5
}'
```

### 关键响应字段
- `success` (boolean)
- `error` (string)
- `output.material_id` (string)
- `output.draft_id` (string, 可能返回)
- `output.draft_url` (string, 可能返回)

### 错误返回
- HTTP 非 2xx：鉴权或服务异常。
- `success=false` 或 `error` 非空：业务失败。
- 缺少 `output.material_id`：视为添加文本未确认成功。

### 枚举引用
- `references/enums/font_types.json`
- `references/enums/text_intro_anims.json`
- `references/enums/text_outro_anims.json`
- `references/enums/text_loop_anims.json`

## modify_text
- Method: `POST`
- Path: `/cut_jianying/modify_text`
- 用途：根据 `material_id` 修改已存在文本素材。

### 请求参数
- 必填：`draft_id`、`material_id`、`text`、`start`、`end`
- 其余样式参数与 `add_text` 一致（位置、字体、描边、背景、动画、`text_styles`）。
- 时间约束：`end > start`。

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/modify_text' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "draft_id":"dfd_cat_xxx",
  "material_id":"b3679a7e4deb4a90b97e4ebcab36a2f5",
  "text":"你好!Hello",
  "start":0,
  "end":5,
  "font":"文轩体",
  "intro_animation":"向下飞入",
  "outro_animation":"向下滑动"
}'
```

### 关键响应字段
- `success` (boolean)
- `error` (string)
- `output.draft_id` (string)
- `output.draft_url` (string)

### 错误返回
- HTTP 非 2xx：鉴权或服务异常。
- `success=false` 或 `error` 非空：业务失败。

## remove_text
- Method: `POST`
- Path: `/cut_jianying/remove_text`
- 用途：根据 `material_id` 删除文本素材。

### 请求参数
- 必填：`draft_id`、`material_id`

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/remove_text' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "draft_id":"dfd_cat_1774150836_9258c924",
  "material_id":"6cc745f6cfbb4231955be96838c6d727"
}'
```

### 关键响应字段
- `success` (boolean)
- `error` (string)
- `output.draft_id` (string)
- `output.draft_url` (string)

### 错误返回
- HTTP 非 2xx：鉴权或服务异常。
- `success=false` 或 `error` 非空：业务失败。