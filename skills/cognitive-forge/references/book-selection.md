# Book Selection Logic

## Multi-Source Selection (优先级从高到低)

### Source 1: User-Specified (用户直接指定)
用户在对话中明确说 "分析《XXX》by YYY" → 直接使用，跳过选书流程。
- `source` 标记为 `user_specified`

### Source 2: Queue (预排队列)
从 `memory/reading-history.json` 的 `queue` 数组取第一项：
```json
{
  "queue": [
    {"title": "《穷查理宝典》", "author": "彼得·考夫曼", "topic": "决策科学"}
  ]
}
```
- FIFO 顺序，取出后从 queue 中移除
- `source` 标记为 `queue`

### Source 3: book-scout Web Search (网络搜索)
当 queue 为空且用户未指定时，调用 `book-scout` skill。
- `source` 标记为 `web_search`

---

## Configurable Topic Mapping (可配置主题映射)

### 配置优先级
1. **HEARTBEAT-reading.md 自定义** → 优先使用
2. **默认映射** → 兜底

### 默认星期-主题映射

| Weekday | Default Category |
|---------|-----------------|
| Monday | Business Strategy |
| Tuesday | Psychology |
| Wednesday | Technology |
| Thursday | Economics |
| Friday | Innovation |
| Saturday | Philosophy |
| Sunday | Biography |

### 自定义覆盖

用户可在 `HEARTBEAT-reading.md` 中添加以下 section 覆盖默认值：

```markdown
## 主题映射（可选覆盖）
Monday: Product Design
Tuesday: Product Design
Wednesday: AI Technology
Thursday: Decision Science
Friday: Innovation
Saturday: Philosophy
Sunday: Self-Growth
```

也支持按时段细分（参考 HEARTBEAT-reading.md 中的 21 主题轮转配置）。

---

## Deduplication (去重)

### 双层去重

| 层级 | 检查内容 | 来源字段 |
|------|---------|---------|
| **书名去重** | 新书标题 vs 已读列表 | `used_models[].book` |
| **模型去重** | 新模型名称 vs 已提取列表 | `used_models[].model` |

### 去重流程

1. 从 `memory/reading-history.json` 加载 `used_models` 数组
2. 提取所有 `book` 字段 → 已读书名列表
3. 提取所有 `model` 字段 → 已提取模型名列表
4. 两个列表都传给 `book-scout` 用于排除
5. `mental-model-forge` 返回后，再与已提取模型名做语义相似度检查
   - 如果新模型与已有模型本质相同（如 "第一性原理" vs "First Principles Thinking"）→ 跳过，重新提取

### Category Exhausted

如果某主题的书已全部处理完：
- `book-scout` 自动从其他主题中选择
- 优先选择覆盖最薄弱的主题

---

## reading-history.json Schema

```json
{
  "schema_version": 1,
  "last_attempted": null,
  "queue": [],
  "used_models": [
    {
      "date": "2026-03-24",
      "book": "《上瘾》",
      "author": "尼尔·埃亚尔",
      "model": "上瘾模型（Hook Model）",
      "category": "用户增长",
      "source": "web_search",
      "applied_count": 0,
      "tags": ["thinking-pattern"]
    }
  ]
}
```

## Adding Books to Queue

用户可以手动向 queue 中添加待读书目：
```
"帮我把《穷查理宝典》加入阅读队列"
```

AI 会向 `reading-history.json` 的 `queue` 数组追加：
```json
{"title": "《穷查理宝典》", "author": "彼得·考夫曼", "topic": "决策科学"}
```
