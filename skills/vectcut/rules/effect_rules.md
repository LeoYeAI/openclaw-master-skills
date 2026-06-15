# 特效端点规则（add_effect / modify_effect / remove_effect）

## 适用范围
- `POST /cut_jianying/add_effect`
- `POST /cut_jianying/modify_effect`
- `POST /cut_jianying/remove_effect`

## 专属异常处理
- 当 `error` 包含 `Unknown effect type`：
  - 含义：`effect_type` 非法。
  - 处理：先调用 `get_video_scene_effect_types` 或 `get_video_character_effect_types` 获取可用特效后替换重试。
  - 重试上限：1 次。

- 当 `error` 包含 `New segment overlaps with existing segment [start: xxxx, end: yyyy]`：
  - 含义：同轨道时间范围冲突。
  - 注意：`[start, end]` 单位是微秒（us）。
  - 处理 A：更换 `track_name` 后重试。
  - 处理 B：调整 `start/end` 与现有片段错开后重试。
  - 重试上限：1 次。

- remove_effect 返回“未找到特效素材”时，仅提示并继续后续任务。

## 诊断上下文
失败时至少保留：
- `endpoint`
- `draft_id`
- `material_id`
- `track_name`
- `start`
- `end`
- `effect_type`
- `error`