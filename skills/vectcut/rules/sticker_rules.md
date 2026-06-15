# sticker 端点规则（search_sticker / add_sticker）

## 适用范围
- `POST /cut_jianying/search_sticker`
- `POST /cut_jianying/add_sticker`

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
  - 含义：业务失败（如鉴权失败、资源不可访问、参数不合法）。
  - 处理：保留 `error` 与关键入参，修正后重试 1 次。
  - 重试上限：1 次。

- 当关键字段缺失：
  - `search_sticker` 缺少 `output.data`。
  - `add_sticker` 缺少 `output.draft_id` 或 `output.draft_url`。
  - 含义：关键字段缺失，无法进入后续编排。
  - 处理：标记为不可继续，要求修正入参或稍后重试。
  - 重试上限：1 次。

## 诊断上下文
失败时至少保留：
- `endpoint`
- `error`
- `status_code`
- `raw_response`
- `draft_id`
