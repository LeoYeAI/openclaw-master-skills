# SignalRadar Notion Sync Reference

## 1) 页面结构（当前实现）

配置 `--notion-page-id` 后，`watchlist-refresh` 会在该父页面下维护一个目录页：

- `SignalRadar`（可通过参数改名）

目录页下维护这些子页面/对象：

- `SignalRadar_Watchlist_DB`：**Notion Database 表格**，展示所有监测条目（可排序/筛选）。
- `SignalRadar_Manual_Entries`：用户手动新增条目入口。
- `polymarket_watchlist_2026`：监测条目主清单 markdown（AI任务读取源，仍同步到 Notion 作为 Database 过渡方案）。
- `polymarket_rollover_2026`：watchlist 自动维护日志（默认不同步到 Notion）。
**只读页面同步默认关闭**。设置 `notion.sync_readonly_pages = true` 可开启 rollover 页面的 Notion 同步。

## 2) Notion Database（Watchlist 表格）

watchlist-refresh 运行时会自动创建或更新 `SignalRadar_Watchlist_DB` Database。

列定义：

| 列名 | 类型 | 说明 |
|------|------|------|
| 问题 | title | 市场问题文本 |
| 分类 | select | AI Releases / Crypto 等 |
| Yes概率 | number (percent) | 当前概率 |
| 24h成交额 | number (dollar) | 24小时成交额 |
| 截止日 | date | 市场截止日期 |
| WatchLevel | select | normal / important |
| ThresholdPP | number | 自定义触发阈值 |
| Source | select | auto（关键词扫描）/ manual（用户添加） |

## 3) 可编辑规则

- `SignalRadar_Watchlist_DB`：可编辑（用户可直接在 Notion 表格中修改）。
- `SignalRadar_Manual_Entries`：可编辑（推荐在这里加条目）。
- `polymarket_watchlist_2026`：部分可编辑（不建议改表头）。
- `polymarket_rollover_2026`：只读。
- ~~`signalradar_monitor_jobs`~~：已弃用（cron 解耦后不再导出）。

## 4) 手动条目格式

支持以下输入（每行一条）：

- `Category | Question | EndDate`
- `Category | Question | EndDate | WatchLevel | ThresholdPP`
- `Category | Question`
- `Polymarket URL`

示例：

- `AI Releases | Will GPT-6 be released by June 30, 2026? | 2026-06-30`
- `AI Releases | Will GPT-6 be released by June 30, 2026? | 2026-06-30 | important | 4.0`
- `https://polymarket.com/event/will-openai-release-gpt-6-before-july-2026`

容错规则：

- 允许项目符号、中文竖线 `｜`。
- 错误格式行会跳过。
- 已存在条目不会重复写入（输出 `SKIPPED=... EXISTING=...`）。

## 5) 关键参数（watchlist-refresh）

- `--notion-page-id`：Notion 父页面 ID（必填才启用同步）。
- `--notion-root-page-title`：目录页标题，默认 `SignalRadar`。
- `--notion-manual-page-title`：手动条目页标题，默认 `SignalRadar_Manual_Entries`。

依赖脚本（已随 skill 分发）：

- `scripts/polymarket_watchlist_refresh.py`
- `scripts/sync_md_to_notion_v4.sh`
- `scripts/notion_watchlist_db.py`
- `scripts/write_notion_entry.py`

运行时会优先使用 skill 目录内脚本；若缺失会返回结构化错误，不再静默忽略。

## 6) Bot 写入条目

Bot/Agent 可通过 `write_notion_entry.py` 向 Notion 写入监测条目：

```bash
python3 scripts/write_notion_entry.py \
    --parent-page-id <NOTION_PAGE_ID> \
    --entry "AI Releases | Will GPT-6 be released? | 2026-06-30 | important | 4.0"
```

功能：
- 写入 Notion Database（SignalRadar_Watchlist_DB）
- 同时追加到 Manual_Entries 页面（向后兼容）
- 自动去重（按 question 文本匹配）

## 7) 运行输出判读

- `notion_pull=DIRECTORY_PAGE=... SOURCE_PAGE_CREATED:...`
  - 首次创建目录页/手动页成功。
- `notion_pull=... MERGED=N TOTAL=M`
  - 本次新增了 `N` 条。
- `SKIPPED=K EXISTING=...`
  - 这些问题已存在，未重复新增。
- `notion_sync=ok`
  - Markdown 到 Notion 同步成功。
- `notion_db=ok created=N updated=M skipped=K db_id=...`
  - Notion Database 同步成功。
- `{"error_code":"...","message":"...","details":{...}}`
  - 结构化失败输出，可被 AI Agent 稳定解析。

## 8) 关键词配置

watchlist 扫描的关键词存储在 `config/watchlist_keywords.json`：

```json
{
  "keywords": {
    "AI Releases": ["claude 5", "gpt-6", "deepseek", ...],
    "SpaceX IPO": ["spacex ipo", ...]
  },
  "manual_markets": []
}
```

用户可直接编辑此文件来添加/删除分类和关键词。如果文件不存在，使用代码内置的默认值。
