# asr_nlp 回包结构解读

## 样例来源
- 对照样例：`references/asr_nlp.json`

## 顶层结构
- `success` (boolean): 请求是否成功。
- `error` (string): 错误信息，成功时通常为空字符串。
- `mode` (string): 识别模式，样例为 `asr`。
- `content` (string): 合并后的完整文案。
- `segments` (array): 语义分句后的结果列表。

## segments 结构
每个 segment 表示一条适合字幕展示的句段：
- `start` (number): 句段起始时间。
- `end` (number): 句段结束时间。
- `text` (string): 当前句段文本。
- `phrase` (array): 短语级拆分（词组粒度），用于更平滑断句或二次排版。
- `words` (array): 字级时间戳，适合逐字高亮和卡点字幕。

## phrase 结构
- `start_time` / `end_time` (number): 短语级时间范围。
- `text` (string): 短语文本。

## words 结构
- `start_time` / `end_time` (number): 字级时间范围。
- `text` (string): 单字内容。
- `confidence` (number): 置信度（样例中为 0）。

## 时间单位
- 本样例时间单位为毫秒（ms）。
- 字幕写入草稿时，如目标字段使用微秒，需做 `ms -> us` 换算（乘以 1000）。

## 与 asr_basic / asr_llm 的差异
- 相比 `asr_basic`：`asr_nlp` 提供更适合竖屏字幕的语义分句结构（`segments + phrase`）。
- 相比 `asr_llm`：`asr_nlp` 不含 `keywords` 与 `en` 字段，语义增强程度较低但速度更快。

## 解析建议
- 生成竖屏字幕时，优先遍历 `segments` 作为字幕行。
- 逐字动画可直接使用 `words`。
- 若要控制每行长度，可在 `phrase` 粒度二次合并。