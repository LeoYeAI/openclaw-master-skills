# Endpoint Params

## effect_type 枚举来源
- `references/enums/character_effect_types.json`
- `references/enums/scene_effect_types.json`

## add_effect

- Method: `POST`
- Path: `/cut_jianying/add_effect`
- 用途：在指定时间范围向草稿添加特效。

### 请求参数
- `effect_type` (string, required): 特效类型名称
- `effect_category` (string, required): 特效分类，`character` 或 `scene`
- `start` (number, optional): 开始时间（秒），默认 `0`
- `end` (number, optional): 结束时间（秒），默认 `3.0`
- `draft_id` (string, optional): 草稿 ID
- `track_name` (string, optional): 特效轨道名，默认 `effect_01`
- `params` (array[number], optional): 特效参数列表，可以填3个[0-100]的参数，越大特效越明显

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/add_effect' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "effect_type": "MV封面",
  "start": 0,
  "end": 3.0,
  "draft_id": "draft_789",
  "track_name": "effect_01",
  "params": [45, 35,45],
  "width": 1080,
  "height": 1920
}'
```

### 关键响应字段
- `success` (boolean)
- `error` (string)
- `output.draft_id` (string, 草稿id， 后续如果继续编辑这个草稿可以用上)
- `output.draft_url` (string, 草稿url， 可以在浏览器中打开查看)
- `output.material_id` (string, 特效id， 后续如果需要删除、修改这个特效可以用上)

### 错误返回
- `error` 包含 `Unknown scene effect type`：`effect_type` 非法，查 `../enums/scene_effect_types.json` 后重试。
- `error` 包含 `Unknown character effect type`：`effect_type` 非法，查 `../enums/character_effect_types.json` 后重试。
- `error` 包含 `New segment overlaps with existing segment [start: xxxx, end: yyyy]`：当前轨道已有素材与待添加片段时间范围冲突。
  - 其中 `start/end` 为微秒（us）。
  - 处理方式 A：更换 `track_name`，在新轨道添加。
  - 处理方式 B：调整 `start/end`，与现有片段错开后再添加。

## modify_effect

- Method: `POST`
- Path: `/cut_jianying/modify_effect`
- 用途：修改已添加特效（可改类型、时间区间、轨道与参数）。

### 请求参数
- `material_id` (string, required): 需要修改的特效素材 id
- `draft_id` (string, required): 草稿 id
- `effect_category` (string, optional): 特效分类，`character` 或 `scene`
- `effect_type` (string, optional): 新特效类型名称
- `start` (number, optional): 新开始时间（秒）
- `end` (number, optional): 新结束时间（秒）
- `track_name` (string, optional): 轨道名
- `params` (array[number], optional): 特效参数

### 关键响应字段
- `success` (boolean)
- `error` (string)
- `output.draft_id` (string, 草稿id， 后续如果继续编辑这个草稿可以用上)
- `output.draft_url` (string, 草稿url， 可以在浏览器中打开查看)
- `output.material_id` (string, 特效id， 后续如果需要删除、修改这个特效可以用上)

### 错误返回
- `error` 包含 `Unknown scene effect type`：`effect_type` 非法，查 `../enums/scene_effect_types.json` 后重试。
- `error` 包含 `Unknown character effect type`：`effect_type` 非法，查 `../enums/character_effect_types.json` 后重试。
- `error` 包含 `New segment overlaps with existing segment [start: xxxx, end: yyyy]`：当前轨道已有素材与待添加片段时间范围冲突。
  - 其中 `start/end` 为微秒（us）。
  - 处理方式 A：更换 `track_name`，在新轨道添加。
  - 处理方式 B：调整 `start/end`，与现有片段错开后再添加。

## remove_effect

- Method: `POST`
- Path: `/cut_jianying/remove_effect`
- 用途：删除草稿中指定特效。

### 请求参数
- `material_id` (string, required): 特效素材 id
- `draft_id` (string, required): 草稿 id

### 关键响应字段
- `success` (boolean)
- `error` (string)
- `output.draft_id` (string, 草稿id， 后续如果继续编辑这个草稿可以用上)
- `output.draft_url` (string, 草稿url， 可以在浏览器中打开查看)

### 错误返回
- `error` 删除特效失败：仅提示并继续后续任务。