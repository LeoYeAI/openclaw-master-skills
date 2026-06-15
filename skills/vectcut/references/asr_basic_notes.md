# asr_basic 回包结构解读

## 样例来源
- 对照样例：`references/asr_basic.json`

## 顶层结构
- `success` (boolean): 请求是否成功。
- `error` (string): 错误信息，成功时通常为空字符串。
- `mode` (string): 识别模式，样例为 `asr`。
- `content` (string): 识别出的整段文本（顶层聚合结果）。
- `result` (object): 基础识别主结果容器。

## result 结构
- `result.content` (string): 识别内容（与顶层 `content` 含义接近）。
- `result.raw.audio_info.duration` (number): 音频总时长。
- `result.raw.result.text` (string): 原始识别全文。
- `result.raw.result.utterances` (array): 句级分段结果（带字级时间戳）。

## utterances 结构
- `start_time` / `end_time` (number): 当前句子时间范围。
- `text` (string): 当前句子文本。
- `additions.speaker` (string): 说话人编号（如有）。
- `words` (array): 字级识别结果。

## words 结构
- `start_time` / `end_time` (number): 单字时间范围。
- `text` (string): 单字内容。
- `confidence` (number): 置信度。

## 时间单位
- 本样例时间单位为毫秒（ms）。
- 若写入草稿字段需微秒，统一执行 `ms -> us`（乘以 1000）。

## 与 asr_nlp / asr_llm 的差异
- `asr_basic` 结果嵌套更深（`result.raw.result.utterances`）。
- 不提供 `segments[].phrase`（nlp）与 `segments[].keywords/en`（llm）。
- 适合基础字幕识别、字级打点和素材初步理解。