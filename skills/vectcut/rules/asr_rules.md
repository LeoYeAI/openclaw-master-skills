# ASR 端点规则（asr_basic / asr_nlp / asr_llm）

## 适用范围
- `POST /llm/asr_basic`
- `POST /llm/asr_nlp`
- `POST /llm/asr_llm`

## 选择与降级
- 默认优先级：`asr_llm > asr_nlp > asr_basic`。
- 仅在明确只需基础识别或时延敏感时，才降级到 `asr_nlp` 或 `asr_basic`。
- `asr_basic`：速度最快，适合横屏字幕或素材初步理解。
- `asr_nlp`：速度中等，支持语义分句（每句不超过 12 字），适合竖屏字幕。
- `asr_llm`：速度最慢，支持关键词提取，优先用于竖屏与短视频字幕。

## 入参策略
- 必填：`url`（音频/视频可访问链接）。
- 可选：`content`（正确文案）；当用户可提供原文时必须透传，可显著提升匹配准确率与处理速度。
- 时间单位约定：回包时间戳默认按毫秒解析；写入草稿前按目标字段单位换算。

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
  - 含义：业务失败（媒体不可访问、识别失败、参数不合法）。
  - 处理：优先修正 `url/content` 后重试；若仍失败按优先级降级接口再试一次。
  - 重试上限：1 次。
- 当关键字段缺失：
  - `asr_basic` 缺少 `result.raw.result.utterances`。
  - `asr_nlp` 缺少 `segments`。
  - `asr_llm` 缺少 `segments`。
  - 含义：无法进入后续字幕/语义处理流程。
  - 处理：标记为不可继续，保留原始响应并中止。
  - 重试上限：0 次。

## 诊断上下文
失败时至少保留：
- `endpoint`
- `url`
- `content`
- `error`
- `status_code`
- `raw_response`