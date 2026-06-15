# asr_llm 回包结构解读

## 样例来源
- 对照样例：`references/asr_llm.json`

## 顶层结构
- `success` (boolean): 请求是否成功。
- `error` (string): 错误信息，成功时通常为空字符串。
- `mode` (string): 识别模式，样例为 `asr`。
- `content` (string): 合并后的完整文案。
- `segments` (array): 高阶语义分句结果。

## segments 结构
每个 segment 代表一段语义片段：
- `start` / `end` (number): 片段时间范围。
- `text` (string): 中文片段文本。
- `en` (string): 英文语义表达，可用于双语字幕或翻译参考。
- `keywords` (array): 关键词列表，用于摘要、标签或镜头索引。
- `words` (array): 字级时间戳，适配逐字高亮。

## keywords 结构
- `start_time` / `end_time` (number): 关键词在音频中的时间范围。
- `text` (string): 关键词文本。

## words 结构
- `start_time` / `end_time` (number): 字级时间范围。
- `text` (string): 单字内容。
- `confidence` (number): 置信度（样例中为 0）。

## 时间单位
- 本样例时间单位为毫秒（ms）。
- 若后续写入草稿字段使用微秒，统一执行 `ms -> us`（乘以 1000）。

## 与 asr_nlp / asr_basic 的差异
- 相比 `asr_nlp`：新增 `en` 与 `keywords`，更适合短视频摘要、打点和高信息密度字幕。
- 相比 `asr_basic`：语义结构更强，不仅有字级时间，还提供关键词与跨语言表达。

## 解析建议
- 字幕主文本使用 `segments[].text`。
- 关键词提炼使用 `segments[].keywords`，可直接映射为封面文案、标签或章节点。
- 双语场景可用 `segments[].en` 作为初稿，再按风格二次润色。