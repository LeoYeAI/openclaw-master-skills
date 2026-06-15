# 风鸟 API 字段定义 — 经营风险维度（D1 / D2 / D11）& 注意事项

> 版本：第一版 | 基于 API 实测验证 | 最后更新：2026-03-25

---

## D1 经营风险-经营异常

`version=D1` · `apiData` 为数组

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | number | 记录 ID |
| `entname` | string/null | 企业名称（企业返回名称，个体户可能返回注册号，部分返回 `null`） |
| `regno` | string | 注册号 |
| `uniscid` | string | 统一社会信用代码（部分主体为空字符串） |
| `inDate` | string | 列入日期（`YYYY-MM-DD`） |
| `inReason` | string | 列入原因 |
| `inRegOrg` | string | 列入机关 |
| `outDate` | string/null | 移出日期（`YYYY-MM-DD`；`null` 表示尚未移出） |
| `outReason` | string | 移出原因（空字符串表示尚未移出） |
| `outRegOrg` | string | 移出机关（空字符串表示尚未移出） |
| `outState` | boolean | ⚠️ 移出状态（`false`=**仍在名单**，`true`=已移出）。含义与字段名相反，注意区分 |

> ⚠️ `totalCount` 是列入总数（含已移出记录）。若需统计"当前仍在名单"的记录数，需过滤 `outState=false` 的条目。

---

## D2 经营风险-严重违法

`version=D2`

> ⚠️ **结构差异**：数据位于 `data.SERILLEGAL` 数组，**不是** `data.apiData`。字段命名为全小写，与 D1 的 camelCase 不同。

| 字段 | 类型 | 说明 |
|------|------|------|
| `entname` | string | 企业名称 |
| `regno` | string | 注册号 |
| `uniscid` | string | 统一社会信用代码 |
| `inreason` | string | 列入原因 |
| `indate` | string | 列入日期（`YYYY-MM-DD`） |
| `inorg` | string | 列入机关 |
| `outreason` | string | 移出原因（未移出则为空字符串） |
| `outdate` | string/null | 移出日期（未移出则为 `null`） |
| `outorg` | string | 移出机关（未移出则为空字符串） |

**D2 响应结构示例**：
```json
{
  "data": {
    "totalCount": 8,
    "SERILLEGAL": [
      { "entname": "...", "inreason": "...", "indate": "...", "inorg": "..." }
    ]
  }
}
```

---

## D11 经营风险-行政处罚

`version=D11` · `apiData` 为数组

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 记录 ID |
| `entid` | string | 企业 ID |
| `entName` | string | 企业名称 |
| `docNo` | string | 处罚决定书文号 |
| `penaltyDate` | string | 处罚日期（`YYYY-MM-DD`） |
| `publishDate` | string | 公示日期（`YYYY-MM-DD`） |
| `penaltyOrg` | string | 处罚机关名称 |
| `illegalFact` | string | 违法事实描述（详细） |
| `illegalType` | string | 违法类型分类（如 `"文旅广告"`、`"交通运输"`、`"市场监管"`） |
| `penaltyAm` | string/null | 罚款金额（⚠️ 单位：**元**，如 `"10000.00"`；无罚款时为 `null`） |
| `penaltyResult` | string | 处罚结果完整描述 |
| `penaltyBasis` | string | 处罚依据（法律法规条款） |

---

## 关键注意事项速查

| 注意项 | 说明 |
|--------|------|
| `entid` 是核心标识 | 所有维度查询必须用 `entid`，不支持传企业名称或信用代码 |
| `penaltyAm` 单位是**元** | D11 展示时需 ÷ 10000 换算为万元 |
| `execMoney` 单位是**万元** | C2 直接使用，无需换算。与 D11 单位不同，注意区分 |
| `totalCount=0` 含义 | B1 固定返回 `0`（单体数据无分页概念）；其他维度为 `0` 表示无记录 |
| `altAfClean` / `altBeClean` | 含 HTML `<span>` 标签，仅用于前端高亮展示。**逻辑处理必须用 `altAf` / `altBe`** |
| D1 vs D2 字段命名风格 | D1：camelCase（`inDate` / `inReason`）；D2：全小写（`indate` / `inreason`） |
| D2 数据路径不同 | D2 数据在 `data.SERILLEGAL[*]`，其他维度在 `data.apiData[*]` |
| D1 `outState` 语义 | `false`=仍在名单，`true`=已移出；`totalCount` 含已移出记录，需自行过滤 |
| 分页不可用 | `apiData` 始终返回最多前 5 条。`totalCount > 5` 时应告知用户"共 N 条，展示最新 5 条" |
| 英文搜索无效 | searchHint 不支持英文关键词匹配中文企业名称，必须传中文 |

---

## 错误码速查

| code | 含义 | 触发场景 |
|------|------|---------|
| `20000` | 成功 | 正常响应（含空结果） |
| `3000000` | 暂时没有找到相关数据 | searchHint 传空 key |
| `8888` | 业务参数错误 | `entid` 无效、`version` 不存在 |
| `9999` | 系统错误 | 缺少必传参数或鉴权失败 |
