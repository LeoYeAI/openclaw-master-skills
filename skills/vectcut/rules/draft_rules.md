# 草稿管理端点规则（create_draft / modify_draft / remove_draft / query_script）

## 适用范围
- `POST /cut_jianying/create_draft`
- `POST /cut_jianying/modify_draft`
- `POST /cut_jianying/remove_draft`
- `POST /cut_jianying/query_script`

## 专属异常处理
- 当 HTTP 状态码非 2xx：
  - 含义：鉴权失败、参数非法或服务端异常。
  - 处理：记录状态码与响应体；若为鉴权问题先检查 `VECTCUT_API_KEY`，再重试 1 次。
  - 重试上限：1 次。

- 当响应体不是合法 JSON：
  - 含义：网关异常或返回格式不符合约定。
  - 处理：保留原始响应体并中止，不做盲目重试。
  - 重试上限：0 次。

- 当 `success=false` 或 `error` 非空：
  - 含义：草稿创建/修改/删除/查询业务失败。
  - 处理：保留 `error` 与请求参数上下文，修正参数后重试 1 次。
  - 重试上限：1 次。

- 当关键字段缺失：
  - `create_draft` / `modify_draft` 缺少 `output.draft_id`。
  - `query_script` 缺少 `output`。
  - 含义：无法进入后续草稿编排流程。
  - 处理：标记为不可继续，保留原始响应并中止。
  - 重试上限：1 次。

## 诊断上下文
失败时至少保留：
- `endpoint`
- `draft_id`
- `name`
- `cover`
- `error`
- `status_code`
- `raw_response`