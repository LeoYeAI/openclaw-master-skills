# 滤镜端点规则（add_filter / modify_filter / remove_filter）

## 适用范围
- `POST /cut_jianying/add_filter`
- `POST /cut_jianying/modify_filter`
- `POST /cut_jianying/remove_filter`

## 专属异常处理
- 当 `error` 包含 `Unknown filter type`：
  - 含义：`filter_type` 非法。
  - 处理：读取 `../references/enums/filter_types.json` 校验并替换后重试。
  - 重试上限：1 次。

- 当 `error` 包含 `New segment overlaps with existing segment [start: xxxx, end: yyyy]`：
  - 含义：同轨道已有素材，时间范围冲突。
  - 注意：`[start, end]` 单位是微秒（us）。
  - 处理 A：更换 `track_name` 在新轨道添加。
  - 处理 B：调整 `start/end` 与现有片段错开后重试。
  - 重试上限：1 次。

## 诊断上下文
失败时至少保留：
- `endpoint`
- `draft_id`
- `material_id`
- `track_name`
- `start`
- `end`
- `error`