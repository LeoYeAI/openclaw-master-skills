# Endpoint Params

## asr_basic
- Method: `POST`
- Path: `/llm/asr_basic`
- 用途：基础语音识别，速度最快；返回完整文案、句级时间、字级时间。

### 请求参数
- `url` (string, required): 待识别音频/视频 URL，需可公网访问。
- `content` (string, optional): 已知正确文案，传入后可提升匹配准确率与速度。

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/llm/asr_basic' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{"url":"https://example.com/demo.mp4","content":"可选：已知原文"}'
```

### 关键响应字段
- `success` (boolean)
- `error` (string)
- `content` (string)
- `result.raw.result.utterances` (array, 句级+字级时间戳)

### 结构解读
- `references/asr_basic_notes.md`

### 错误返回
- `success=false` 或 `error` 非空：识别失败，修正 `url/content` 后重试 1 次。
- HTTP 非 2xx：鉴权或服务异常，先检查 `VECTCUT_API_KEY` 与请求体。
- 响应非 JSON 或缺少 `result.raw.result.utterances`：中止后续流程并保留原始响应。

## asr_nlp
- Method: `POST`
- Path: `/llm/asr_nlp`
- 用途：中速识别，在 basic 基础上增加语义分句（适合竖屏字幕）。

### 请求参数
- `url` (string, required)
- `content` (string, optional)

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/llm/asr_nlp' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{"url":"https://example.com/demo.mp4","content":"可选：已知原文"}'
```

### 关键响应字段
- `success` (boolean)
- `error` (string)
- `content` (string)
- `segments` (array, 语义分句结果，含 `phrase/words`)

### 结构解读
- `references/asr_nlp_notes.md`

### 错误返回
- 响应非 JSON 或缺少 `segments`：中止后续流程并保留原始响应。
- 其他同 `asr_basic`。

## asr_llm
- Method: `POST`
- Path: `/llm/asr_llm`
- 用途：最强识别，在 nlp 基础上增加关键词提取，优先用于竖屏/短视频字幕。

### 请求参数
- `url` (string, required)
- `content` (string, optional)

### 示例请求
```bash
curl --location --request POST 'https://open.vectcut.com/llm/asr_llm' \
--header 'Authorization: Bearer <token>' \
--header 'Content-Type: application/json' \
--data-raw '{"url":"https://example.com/demo.mp4","content":"可选：已知原文"}'
```

### 关键响应字段
- `success` (boolean)
- `error` (string)
- `content` (string)
- `segments` (array, 含 `keywords/en/words`)

### 结构解读
- `references/asr_llm_notes.md

### 错误返回
- 响应非 JSON 或缺少 `segments`：中止后续流程并保留原始响应。
- 其他同 `asr_basic`。