# 工具调用参数参考

> 详细参数 schema——SKILL.md 中仅保留调用示例，完整参数在此文件备用。

## mcporter 调用规范

**参数格式**：`key=value`，**不是** `--key value`
- ✅ `mcporter call asmcp.file_search keyword="文档" type="doc" start=0 rows=25`
- ❌ `mcporter call asmcp.file_search --keyword 文档`

**超时配置**：`chat_send` 需要 10 分钟超时，在 `~/.openclaw/openclaw.json` 的 `skills.entries["anyshare-mcp-skills"].env` 中设置 `MCPORTER_CALL_TIMEOUT=600000`（毫秒）。兜底：单次 `mcporter call` 末尾加 `--timeout 600000`。

## file_search

```json
{
  "name": "file_search",
  "arguments": {
    "keyword": "<用户关键词>",
    "type": "doc",
    "start": 0,
    "rows": 25,
    "range": [],
    "dimension": ["basename"],
    "model": "phrase"
  }
}
```

**固定字段**（不许改）：`type="doc"`, `dimension=["basename"]`, `model="phrase"`
**动态字段**：仅 `keyword`、`start`、`rows`、`range`（4个）
**不传字段**：`condition`、`custom`、`delimiter` 等可能导致服务端报错，一律不传

**返回结构**：响应内容在 `result.files` 数组（不是 `data`），每项含 `basename`、`size`、`extension`、`doc_id`、`parent_path`、`highlight` 等。

**分页**：`rows` 上限 25；下一页将 `start` 设为上次响应的 `next` 值。

## folder_sub_objects

```json
{
  "name": "folder_sub_objects",
  "arguments": {
    "id": "<docid（完整路径）>",
    "limit": 1000
  }
}
```

**传完整 docid**，不传 id（最后一段）。

## file_osdownload

```json
{
  "name": "file_osdownload",
  "arguments": {
    "docid": "<docid（完整路径）>"
  }
}
```

## file_upload

```json
{
  "name": "file_upload",
  "arguments": {
    "docid": "<目标目录 docid（完整路径）>",
    "file_path": "<MCP 服务端可读的本地路径>"
  }
}
```

`file_path` 直接用本地真实路径即可，不需要复制到临时目录。

## file_convert_path

```json
{
  "name": "file_convert_path",
  "arguments": {
    "docid": "<docid（完整 gns 路径）>"
  }
}
```

**仅用于展示 namepath**，不替代其它工具的 docid 传参。详见 `concepts.md`。

## chat_send — 全文写作（生成大纲）

```json
{
  "name": "chat_send",
  "arguments": {
    "query": "<用户写作任务描述>",
    "selection": "",
    "times": 1,
    "skill_name": "__全文写作__2",
    "web_search_mode": "off",
    "datasource": [],
    "source_ranges": [{ "id": "<文档的 id>", "type": "doc" }],
    "template_id": 1,
    "interrupted_parent_qa_id": ""
  }
}
```

**`source_ranges[].id` 传 id（docid 最后一段），不传完整 docid。**
`type` 固定为 `"doc"`。
`version`、`temporary_area_id` **不要传**（无法从响应可靠获取）。

## chat_send — 全文写作（基于大纲生成正文）

```json
{
  "name": "chat_send",
  "arguments": {
    "query": "基于大纲生成文档",
    "selection": "<已确认的大纲全文>",
    "conversation_id": "<步骤2返回的 conversation_id>",
    "times": 1,
    "skill_name": "__大纲写作__1",
    "web_search_mode": "off",
    "datasource": [],
    "source_ranges": [{ "id": "<文档的 id>", "type": "doc" }],
    "interrupted_parent_qa_id": ""
  }
}
```

## chat_send — Bot 问答（简化模式）

```json
{
  "name": "chat_send",
  "arguments": {
    "query": "<用户的写作或问答任务>",
    "skill_name": "__全文写作__2",
    "source_ranges": [{ "id": "<文档的 id>", "type": "doc" }],
    "web_search_mode": "off"
  }
}
```

适用于：用户已确认**不做全文写作**（不做大纲确认流程）的简化问答。

## auth_login

```json
{
  "name": "auth_login",
  "arguments": {
    "token": "<AnyShare Bearer token（不含 Bearer 前缀，仅 ory_at_xxx 部分）>"
  }
}
```

## auth_status

无参数，查询当前登录状态。

## 工具列表查询（诊断用）

```bash
mcporter list asmcp
# 或
mcporter call asmcp.tools/list
```

## HTTP 备选（工具调用全失败时）

```bash
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}' \
  "https://anyshare.aishu.cn/mcp"
```
