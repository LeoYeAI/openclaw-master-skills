# generate_ai_image 端点规则（generate_image）

## 适用范围
- `POST /cut_jianying/generate_image`

## 请求路由与参数策略
- 必填：`prompt`、`model`。
- `model` 建议值：`nano_banana_2`、`nano_banana_pro`、`jimeng-4.5`（兼容 `nano_banana`）。
- `size` 建议传入 `宽x高` 格式并与模型支持分辨率匹配。
- 图生图场景传 `reference_image`；文生图场景可不传。
- 入草稿场景建议传 `draft_id`、`start`、`end`、`track_name`。

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
  - 含义：业务失败（如模型不支持、分辨率不支持、资源不可访问）。
  - 处理：保留 `error` 与关键入参，修正后重试 1 次。
  - 重试上限：1 次。

- 当关键字段缺失：
  - 缺少 `output.image_url`。
  - 含义：生成图片结果不可用。
  - 处理：标记为不可继续，要求修正入参或稍后重试。
  - 重试上限：1 次。

## 诊断上下文
失败时至少保留：
- `endpoint`
- `error`
- `status_code`
- `raw_response`
- `prompt`
- `model`
- `size`
- `draft_id`