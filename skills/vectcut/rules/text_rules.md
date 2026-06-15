# 文本端点规则（add_text）

## 适用范围
- `POST /cut_jianying/add_text`
- `POST /cut_jianying/modify_text`
- `POST /cut_jianying/remove_text`

## 调用策略
- 面向标题、注释、标识文案等场景，先确定时间段，再确定样式。
- 标准流程（add）：准备 `text/start/end` -> 按需补充样式参数 -> 调用 `add_text` -> 校验 `output.material_id`。
- 标准流程（modify）：准备 `draft_id/material_id/text/start/end` -> 调用 `modify_text` -> 校验 `output.draft_id/draft_url`。
- 标准流程（remove）：准备 `draft_id/material_id` -> 调用 `remove_text` -> 校验 `output.draft_id/draft_url`。
- 时长约束：add/modify 必须满足 `end > start`。

## 入参约束
- add 必填：`text`、`start`、`end`。
- modify 必填：`draft_id`、`material_id`、`text`、`start`、`end`。
- remove 必填：`draft_id`、`material_id`。
- `text` 必须为非空字符串。
- add/modify 的 `start/end` 必须为数字且满足 `end > start`。
- `text_styles` 仅在 add/modify 需要局部样式时传入；每段必须提供 `start/end` 且 `end > start`。
- 枚举约束：
  - `font` 必须优先从 `references/enums/font_types.json` 的 `items.name` 选取。
  - `intro_animation` 必须优先从 `references/enums/text_intro_anims.json` 的 `items.name` 选取。
  - `outro_animation` 必须优先从 `references/enums/text_outro_anims.json` 的 `items.name` 选取。
  - `loop_animation` 必须优先从 `references/enums/text_loop_anims.json` 的 `items.name` 选取。
- 样式参数默认透传，避免强制裁剪合法业务字段。

## 专属异常处理
- 当 HTTP 非 2xx：检查 `VECTCUT_API_KEY` 与请求体后重试 1 次。
- 当响应非 JSON：中止并保留原始响应。
- 当 `success=false` 或 `error` 非空：修正参数后重试 1 次。
- add 缺少 `output.material_id`：中止并保留原始响应。
- modify/remove 缺少 `output.draft_id` 且缺少 `output.draft_url`：中止并保留原始响应。

## 诊断上下文
失败时至少保留：
- `endpoint`
- `draft_id`
- `text`
- `start`
- `end`
- `track_name`
- `error`
- `raw_response`