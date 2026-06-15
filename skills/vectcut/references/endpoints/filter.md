# Endpoint Params

## add_filter

- Method: `POST`
- Path: `/cut_jianying/add_filter`
- 用途：在指定时间范围内向草稿添加滤镜。

### 请求参数
- `filter_type` (string, required): 滤镜类型名称
- `start` (number, required): 开始时间（秒）, 默认0秒
- `end` (number, required): 结束时间（秒），默认5秒
- `draft_id` (string, optional): 草稿 ID，不填则创建新草稿
- `track_name` (string, optional): 轨道名, 默认filter_main，设置不同轨道名等于新建了一个轨道
- `relative_index` (integer, optional): 相对轨道位置，越大越靠上
- `intensity` (number, optional): 滤镜强度，[0-100], 默认 `100`

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/add_filter' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "filter_type": "黑胶唱片",
  "start": 0,
  "end": 3,
  "track_name": "filter_1",
  "relative_index": 1,
  "intensity": 86
}'
```

### 关键响应字段
- `success` (boolean)
- `error` (string)
- `output.draft_id` (string, 草稿id， 后续如果继续编辑这个草稿可以用上)
- `output.draft_url` (string, 草稿url， 可以在浏览器中打开查看)
- `output.material_id` (string, 滤镜id， 后续如果需要删除、修改这个滤镜可以用上)

### 错误返回
- `error` 添加滤镜时出错:xxx。
- `error` 包含 `Unknown filter type`：`filter_type` 非法，先查 `../enums/filter_types.json` 后重试。
- `error` 包含 `New segment overlaps with existing segment [start: xxxx, end: yyyy]`：当前轨道已有素材与待添加片段时间范围冲突。
  - 其中 `start/end` 为微秒（us）。
  - 处理方式 A：更换 `track_name`，在新轨道添加。
  - 处理方式 B：调整 `start/end`，与现有片段错开后再添加。

## modify_filter

- Method: `POST`
- Path: `/cut_jianying/modify_filter`
- 用途：修改已添加滤镜（可改类型、时间区间、轨道与强度）。

### 请求参数
- `material_id` (string, required): 需要修改的滤镜素材 id
- `draft_id` (string, required): 草稿 id
- `filter_type` (string, optional): 新滤镜类型名称
- `start` (number, optional): 新开始时间（秒）
- `end` (number, optional): 新结束时间（秒）
- `track_name` (string, optional): 轨道名
- `relative_index` (integer, optional): 相对轨道位置，越大越靠上
- `intensity` (number, optional): 滤镜强度

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/modify_filter' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "material_id": "1f0c5b83ba724e09a641b1eee3de353c",
  "draft_id": "dfd_cat_1773672212_43b28cc5",
  "filter_type": "黑胶唱片",
  "start": 3,
  "end": 30,
  "track_name": "filter_1",
  "relative_index": 1,
  "intensity": 45
}'
```

### 关键响应字段
- `success` (boolean)
- `error` (string)
- `output.draft_id` (string, 草稿id， 后续如果继续编辑这个草稿可以用上)
- `output.draft_url` (string, 草稿url， 可以在浏览器中打开查看)
- `output.material_id` (string, 滤镜id， 后续如果需要删除、修改这个滤镜可以用上)

### 错误返回
- `error` 添加滤镜时出错:xxx。
- `error` 包含 `Unknown filter type`：`filter_type` 非法，先查 `../enums/filter_types.json` 后重试。
- `error` 包含 `New segment overlaps with existing segment [start: xxxx, end: yyyy]`：当前轨道已有素材与待添加片段时间范围冲突。
  - 其中 `start/end` 为微秒（us）。
  - 处理方式 A：更换 `track_name`，在新轨道添加。
  - 处理方式 B：调整 `start/end`，与现有片段错开后再添加。

## remove_filter

- Method: `POST`
- Path: `/cut_jianying/remove_filter`
- 用途：删除草稿中指定滤镜。

### 请求参数
- `material_id` (string, required): 滤镜素材 id
- `draft_id` (string, required): 草稿 id

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/remove_filter' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "material_id": "c54a84b97b904f818b12b1782fbdc076",
  "draft_id": "dfd_cat_1773672328_d3a400c5"
}'
```

### 关键响应字段
- `success` (boolean)
- `error` (string)
- `output.draft_id` (string, 草稿id， 后续如果继续编辑这个草稿可以用上)
- `output.draft_url` (string, 草稿url， 可以在浏览器中打开查看)

### 错误返回
- `error` 删除滤镜时出错啦：未找到滤镜素材 xxx。仅提示即可，不需要寻找解决方法，继续执行其他任务