# Endpoint Params

## create_draft

- Method: `POST`
- Path: `/cut_jianying/create_draft`
- 用途：创建草稿，作为后续添加图片/音频/视频等素材的承载对象。

### 请求参数
- `width` (number, optional): 视频宽度，默认 `1080`
- `height` (number, optional): 视频高度，默认 `1920`
- `cover` (string, optional): 草稿封面图 URL
- `name` (string, optional): 草稿名称
- `type` (string, optional): 草稿类型，默认 `claw`

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/create_draft' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "width": 1080,
  "height": 1920,
  "name": "draft_demo"
}'
```

### 关键响应字段
- `success` (boolean)
- `error` (string)
- `output.draft_id` (string, required): 草稿 ID，后续操作需引用。
- `output.draft_url` (string, required): 草稿 URL，用于预览与分享。
- `purchase_link` (string)

### 错误返回
- `success=false` 或 `error` 非空：创建失败，修正参数后重试。
- HTTP 非 2xx：鉴权或服务异常，先检查 `VECTCUT_API_KEY` 与请求体。
- 响应非 JSON 或缺少 `output.draft_id`：视为不可用结果并中止后续流程。

## modify_draft

- Method: `POST`
- Path: `/cut_jianying/modify_draft`
- 用途：修改草稿基础信息（名称、封面）。

### 请求参数
- `draft_id` (string, required): 草稿 ID
- `name` (string, optional): 新草稿名称
- `cover` (string, optional): 新封面图 URL

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/modify_draft' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "draft_id": "dfd_xxx",
  "name": "new_draft_name"
}'
```

### 关键响应字段
- `success` (boolean)
- `error` (string)
- `output.draft_id` (string, required): 草稿 ID，确认修改生效。
- `output.draft_url` (string, required): 草稿 URL，用于预览与分享。
- `purchase_link` (string)

### 错误返回
- `success=false` 或 `error` 非空：修改失败，检查 `draft_id` 与可选字段后重试。
- HTTP 非 2xx：鉴权或服务异常，先检查 `VECTCUT_API_KEY` 与请求体。
- 响应非 JSON 或缺少 `output.draft_id`：视为不可用结果并中止后续流程。

## remove_draft

- Method: `POST`
- Path: `/cut_jianying/remove_draft`
- 用途：删除指定草稿。

### 请求参数
- `draft_id` (string, required): 草稿 ID

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/remove_draft' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "draft_id": "dfd_xxx"
}'
```

### 关键响应字段
- `success` (boolean)
- `error` (string)
- `output` (string|object)
- `purchase_link` (string)

### 错误返回
- `success=false` 或 `error` 非空：删除失败，检查 `draft_id` 后重试。
- HTTP 非 2xx：鉴权或服务异常，先检查 `VECTCUT_API_KEY` 与请求体。
- 响应非 JSON：删除失败不影响后续操作。

## query_script

- Method: `POST`
- Path: `/cut_jianying/query_script`
- 用途：查询当前草稿结构，用于反思自查与编排校验。

### 请求参数
- `draft_id` (string, required): 草稿 ID

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/cut_jianying/query_script' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "draft_id": "dfd_xxx"
}'
```

### 关键响应字段
- `success` (boolean)
- `error` (string)
- `output` (string, draft JSON 文本)
- `purchase_link` (string)

### 错误返回
- `success=false` 或 `error` 非空：查询失败，检查 `draft_id` 后重试。
- HTTP 非 2xx：鉴权或服务异常，先检查 `VECTCUT_API_KEY` 与请求体。
- 响应非 JSON 或缺少 `output`：保留原始响应并中止后续校验流程。