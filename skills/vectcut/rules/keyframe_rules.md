# keyframe 端点规则（add_video_keyframe）

## 适用范围
- `POST /cut_jianying/add_video_keyframe`

## 请求路由与参数策略
- 必填：`draft_id`。
- 可选：`track_name`，默认建议 `video_main`。
- 支持单关键帧：`property_type`、`time`、`value`。
- 支持批量关键帧：`property_types[]`、`times[]`、`values[]`。
- 批量模式下三组数组必须同时提供且长度一致。
- 当同时出现单关键帧与批量参数时，优先按批量参数执行。
- 支持属性类型：请直接查 `references/enums/keyframe_types.json` 的 `items.name`，字段含义见 `items.description`。
- 关键帧可用于文字、图片、视频素材，按目标素材所在轨道设置 `track_name`。

## 专属异常处理
- 当 HTTP 状态码非 2xx：
  - 含义：鉴权失败、参数非法或服务端异常。
  - 处理：记录状态码与响应体；若为鉴权问题先检查 `VECTCUT_API_KEY`，再重试 1 次。
  - 重试上限：1 次。

- 当响应体不是合法 JSON：
  - 含义：网关异常或服务返回格式不符合约定。
  - 处理：保留原始响应体并中止，不做盲目重试。
  - 重试上限：0 次。

- 当 `success=false` 或 `error` 非空：
  - 含义：业务失败（如草稿不存在、轨道不可用、属性值不合法）。
  - 处理：保留 `error` 与关键入参，修正后重试 1 次。
  - 重试上限：1 次。

- 当关键字段缺失：
  - 缺少 `output.draft_id` 且缺少 `output.draft_url`。
  - 缺少 `output.added_keyframes_count`。
  - 含义：关键帧结果不可确认。
  - 处理：标记为不可继续，要求修正入参或稍后重试。
  - 重试上限：1 次。

## 诊断上下文
失败时至少保留：
- `endpoint`
- `error`
- `status_code`
- `raw_response`
- `draft_id`
- `track_name`
- `property_type` / `property_types`
- `time` / `times`
- `value` / `values`