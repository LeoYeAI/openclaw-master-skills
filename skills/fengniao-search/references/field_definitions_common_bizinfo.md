# 风鸟 API 字段定义 — 通用结构 & 工商维度（searchHint / B1–B5）

> 版本：第一版 | 基于 API 实测验证 | 最后更新：2026-03-25

---

## 通用响应结构

### 响应信封（所有接口共用）

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | number | 状态码。`20000`=成功，`3000000`=无数据，`8888`=业务参数错误，`9999`=系统错误 |
| `msg` | string | 状态消息 |
| `success` | boolean | 是否成功 |
| `data` | object/array/null | 业务数据，结构因接口而异 |

### 三种 data 形态

**① searchHint** — `data` 直接是数组：
```json
{ "code": 20000, "data": [ { "entid": "...", "entName": "..." } ] }
```

**② dataDimension 列表类（B2/B3/B4/B5/C2/C3/C4/D1/D11）** — `data` 是分页对象：
```json
{
  "data": {
    "totalCount": 140,
    "exportCount": 140,
    "filterData": {},
    "aggregation": null,
    "extraInfo": {},
    "apiData": [ ... ]
  }
}
```

**③ dataDimension 单体类（B1）** — `apiData` 是对象而非数组：
```json
{
  "data": {
    "totalCount": 0,
    "apiData": { "entName": "...", "uniscid": "..." }
  }
}
```

### 分页包装字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `totalCount` | number | 符合条件的总记录数。**判断"是否有风险"只看此值**，不看 `apiData` 长度。B1 固定为 `0`（单体查询无分页概念） |
| `exportCount` | number | 可导出数量，通常等于 `totalCount` |
| `filterData` | object/null | 过滤条件。列表类为 `{}`，B1 为 `null` |
| `aggregation` | null | 聚合数据，当前固定为 `null` |
| `extraInfo` | object/null | 额外信息。列表类为 `{}`，B1 为 `null` |
| `apiData` | array/object | 数据本体。列表类为数组（**最多 5 条**，分页参数无效），B1 为单个对象 |

> ⚠️ **D2 严重违法例外**：数据位于 `data.SERILLEGAL` 数组，而非 `data.apiData`。

---

## searchHint — 模糊搜索

`GET /skills/searchHint?key=<搜索词>`（API Key 通过请求头传递）

返回：`data` 为数组，最多 5 条，按相关度排序，不支持分页。

| 字段 | 类型 | 说明 |
|------|------|------|
| `entid` | string | **企业唯一标识**，后续所有维度查询的必传参数 |
| `entName` / `ENTNAME` | string | 企业全称 |
| `entStatus` / `ENTSTATUS` | string | 经营状态（在营 / 注销 / 吊销等） |
| `entStatusColor` | string | 状态颜色标记（`green`=在营，`red`=异常） |
| `entPic` | string | 企业 Logo 图片 URL |
| `ENTNAME_SEARCH` | string | 带高亮 `<span>` 标签的企业名称（仅用于前端展示，**禁止用于逻辑处理**） |
| `highlightNameType` | string | 命中字段类型。`"公司名称"`=精准匹配优先级最高；`"股东"`=匹配的是股东名；`"企业别名"` / `"统一社会信用代码"` 等 |
| `dataType` | string | 固定值 `"company_basic"` |

---

## B1 工商-基本信息

`version=B1` · `apiData` 为**对象**（非数组） · `totalCount` 固定为 `0`

### 核心工商字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `entName` | string | 企业全称 |
| `entid` | string | 企业唯一标识 |
| `uniscid` | string | 统一社会信用代码 |
| `regNo` | string | 工商注册号 |
| `entStatus` | string | 经营状态（在营 / 注销 / 吊销等） |
| `entType` | string | 企业类型（如"有限责任公司"） |
| `regCap` | string | 注册资本金额（万元，不含单位） |
| `regConcat` | string | 注册资本（含货币单位，如"6500 万元人民币"） |
| `esDate` | string | 成立日期（`YYYY-MM-DD`） |
| `opFrom` | string | 经营开始日期 |
| `opTo` | string | 经营截止日期（"长期"表示长期有效） |
| `candate` | string/null | 注销日期（未注销为 `null`） |
| `revdate` | string/null | 吊销日期（未吊销为 `null`） |
| `dom` | string | 注册地址 |
| `regionName` | string | 注册地区（省市区，如"广东省深圳市南山区"） |
| `regOrg` | string | 登记机关 |
| `nicName` | string | 行业分类全称（国标分类，含上级分类） |
| `opScope` | string | 经营范围（含一般经营和许可经营，以"，许可经营项目是："分隔） |

### 法定代表人字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `personId` | string | 法定代表人 ID |
| `personName` | string | 法定代表人姓名 |
| `personTypeCode` | string | 法人类型编码（`"person"` = 自然人） |
| `personEntCount` | number | 法人关联企业数量 |
| `legalPersonType` | string | 法人身份名称（如"法定代表人"） |

### 其他信息字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `entNameEn` | string | 企业英文名称 |
| `historyName` | string | 企业曾用名 |
| `entIntro` | string | 企业简介 |
| `website` | string | 企业官网 |
| `isBranch` | number | 是否分支机构（`0`=主体，`1`=分支） |
| `tags` | array | 企业标签（如 `["大型","500强","国家高新技术企业"]`） |
| `riskTags` | array/null | 风险标签（如 `["被执行人"]`，无风险时为 `null` 或空） |
| `yrEnpNum` | string | 年报员工人数 |
| `tel` | string | 联系电话（第一个） |
| `email` | string | 联系邮箱（第一个） |

> 说明：官网、电话、邮箱属于 **B1 企业基本信息** 中的基础字段，不是单独的独立维度。用户询问这些基础联系方式时，应先按“企业基本信息”维度处理，再从 B1 返回结果中提取对应字段。

---

## B2 工商-股东信息

`version=B2` · `apiData` 为数组，每条为一个股东记录

| 字段 | 类型 | 说明 |
|------|------|------|
| `shaId` | string | 股东 ID |
| `shaName` | string | 股东姓名 / 名称 |
| `shaTypeCode` | string | 股东类型编码（`"person"`=自然人，`"ent"`=法人） |
| `invType` | string | 投资类型（`"自然人股东"` / `"法人股东"`） |
| `fundedRatio` | string | 持股比例（含 `%`，如 `"54.2857%"`） |
| `subConAm` | string | 认缴出资额（含单位，如 `"3,528.5705 万元人民币"`） |
| `conDate` | string | 认缴日期（`YYYY-MM-DD`） |
| `outState` | boolean | 是否退出（`false`=未退出） |
| `riskTags` | array | 股东风险标签 |

---

## B3 工商-高级职员

`version=B3` · `apiData` 为数组，包含董监高及法定代表人

| 字段 | 类型 | 说明 |
|------|------|------|
| `personId` | string | 人员 ID |
| `personName` | string | 姓名 |
| `position` | string | 职务（多个职务以 `";"` 分隔，如 `"董事长;总经理"`） |
| `fundedRatio` | string | 持股比例（无持股则为 `"-"`） |
| `riskTags` | array | 人员风险标签 |

---

## B4 工商-对外投资

`version=B4` · `apiData` 为数组，每条为一个被投企业

| 字段 | 类型 | 说明 |
|------|------|------|
| `entid` | string | 被投企业 ID |
| `entName` | string | 被投企业名称 |
| `entStatus` | string | 被投企业经营状态 |
| `funderRatio` | string | 持股比例（含 `%`） |
| `subConAm` | string | 认缴出资额（含单位） |
| `esDate` | string | 被投企业成立日期（`YYYY-MM-DD`） |
| `personName` | string | 被投企业法定代表人姓名 |

---

## B5 工商-工商变更信息

`version=B5` · `apiData` 为数组，按变更时间倒序

| 字段 | 类型 | 说明 |
|------|------|------|
| `altDate` | string | 变更日期（`YYYY-MM-DD`） |
| `altItemCodeCn` | string | 变更事项名称（中文） |
| `altAf` | string | 变更后内容（纯文本，**用于逻辑处理**） |
| `altBe` | string | 变更前内容（纯文本，**用于逻辑处理**） |
| `altAfClean` | string | 变更后内容（含高亮 HTML 标签，**仅用于前端展示，禁止用于逻辑处理**） |
| `altBeClean` | string | 变更前内容（含高亮 HTML 标签，**仅用于前端展示，禁止用于逻辑处理**） |
