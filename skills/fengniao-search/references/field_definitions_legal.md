# 风鸟 API 字段定义 — 法律诉讼维度（C2 / C3 / C4）

> 版本：第一版 | 基于 API 实测验证 | 最后更新：2026-03-25

---

## C2 法律诉讼-被执行人

`version=C2` · `apiData` 为数组

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 记录 ID |
| `entityName` | string | 被执行人名称 |
| `entid` | string | 企业 ID |
| `courtName` | string | 执行法院名称 |
| `caseCode` | string | 案号 |
| `caseState` | string | 案件状态（如 `"执行中"`） |
| `execMoney` | string/null | 执行标的金额（⚠️ 单位：**万元**，可为 `null`） |
| `execMoneyFormat` | string/null | 格式化金额（千位分隔，可为 `null`） |
| `regDate` | string | 立案日期（`YYYY-MM-DD`） |
| `gistId` | string/null | 执行依据文号（可为 `null`） |
| `caseUniqueId` | string | 案件唯一标识（系统内部去重用） |

---

## C3 法律诉讼-失信被执行人

`version=C3` · `apiData` 为数组

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 记录 ID |
| `entid` | string | 企业 ID |
| `entityName` | string | 失信被执行人名称 |
| `caseCode` | string | 案号 |
| `courtName` | string | 执行法院名称 |
| `gistId` | string | 执行依据文号（生效法律文书号） |
| `gistUnit` | string | 作出执行依据的单位（法院名称） |
| `regDate` | string | 立案日期（`YYYY-MM-DD`） |
| `publishDate` | string | 数据发布日期（`YYYY-MM-DD`） |
| `duty` | string | 被执行人义务（判决内容摘要，部分为 `"."` 或 `"="` 占位） |
| `performance` | string | 履行情况（如 `"全部未履行"`） |
| `performedPart` | string | 已履行部分说明 |
| `unperformedPart` | string | 未履行部分说明 |
| `disruptTypeName` | string | 失信行为类型（如 `"被执行人无正当理由拒不履行执行和解协议"`） |
| `partyTypeName` | string | 当事人类型（`"法人"` / `"自然人"`） |
| `status` | string | 记录状态（`"未下架"` 表示仍在失信名单上） |
| `caseUniqueId` | string | 案件唯一标识 |

---

## C4 法律诉讼-限制高消费

`version=C4` · `apiData` 为数组

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 记录 ID |
| `entid` | string | 企业 ID |
| `entName` | string | 被限制企业名称 |
| `caseCode` | string | 案号 |
| `court` | string | 作出限制的法院名称 |
| `regDate` | string | 立案日期（`YYYY-MM-DD`） |
| `publishDate` | string | 数据发布日期（`YYYY-MM-DD`） |
| `pdfUrl` | string | 限高令原文 PDF 链接 |
| `applicationList` | array | 申请人列表，每项含 `entityId`、`entityName`、`entityType`、`entityTypeCode` |
| `relatedList` | array | 关联人列表（通常为法定代表人），字段同 `applicationList` |
| `caseUniqueId` | string | 案件唯一标识 |
