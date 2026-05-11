# 工作集示例（Working Set Example）

Last updated: 2026-03-23
Status: active-draft

## 用途（Purpose）

列出需要被例行关注新鲜度的最小文件集合。

List the minimum set of files that should receive routine freshness attention.

---

## 高优先级保鲜文件（Refresh-Critical Files）

### 健康 / 一致性（Health / consistency）
- `memory/health/current-health.json`
- `memory/health/current-health.md`
- `memory/health/memory-consistency.json`
- `memory/health/memory-consistency.md`

### 桥接文件（Bridge files）
- `memory/SYSTEM_OVERVIEW.md`
- `memory/SEARCH_STATE.md`

### 运行态（Runtime）
- `docs/runtime-state-snapshot-2026-03-23.md`
- `docs/runtime-snapshot-refresh-process.md`

### 入口 / 索引层（Entry / index layer）
- `docs/current-state-entrypoints-v1.md`
- `docs/system-state-index-v1.md`

### 与当前态高度重叠的结构化记忆（Structured memory with high current-value overlap）
- `memory/TOPICS_INDEX.md`
- `memory/topics/system-state.md`
- `memory/topics/active-work.md`

---

## 规则（Rule）

如果发生了明显的 system-state 或治理相关变更，先检查这份 working set，再去动低价值的历史/参考文档。

If a meaningful system-state or governance-adjacent change happens, check this working set before touching lower-value historical/reference docs.

Checker:
- `scripts/freshness-check.py`
