# AlphaPai Open API 完整参考文档

本文档包含所有接口的详细字段定义和请求/响应示例。

## 目录

- [AlphaPai Open API 完整参考文档](#alphapai-open-api-完整参考文档)
  - [目录](#目录)
  - [1. 投研知识问答](#1-投研知识问答)
    - [请求参数](#请求参数)
    - [响应参数](#响应参数)
    - [回答类型码(type)](#回答类型码type)
    - [引用数据结构 (references)](#引用数据结构-references)
    - [引用类型枚举](#引用类型枚举)
    - [请求示例 - 非stream模式](#请求示例---非stream模式)
    - [请求示例 - stream模式](#请求示例---stream模式)
  - [2. 投研知识检索（基于RAG技术）](#2-投研知识检索基于rag技术)
    - [请求参数](#请求参数-1)
    - [recallType 可选值](#recalltype-可选值)
    - [响应参数](#响应参数-1)
    - [请求示例](#请求示例)
    - [响应示例](#响应示例)
  - [3. 股票 Agent 接口](#3-股票-agent-接口)
    - [agentMode=1 — 个股业绩点评](#agentmode1--个股业绩点评)
    - [agentMode=2 — 公司一页纸](#agentmode2--公司一页纸)
    - [agentMode=3 — 个股调研大纲](#agentmode3--个股调研大纲)
    - [agentMode=5 — 主题选股](#agentmode5--主题选股)
    - [agentMode=7 — 投资逻辑](#agentmode7--投资逻辑)
    - [agentMode=8 — 可比公司](#agentmode8--可比公司)
    - [agentMode=9 — 观点 Challenge](#agentmode9--观点-challenge)
    - [agentMode=11 — 行业一页纸](#agentmode11--行业一页纸)
    - [agentMode=12 — 个股选基](#agentmode12--个股选基)
    - [agentMode=13 — 主题选基](#agentmode13--主题选基)
    - [agentMode=15 — 画图](#agentmode15--画图)
  - [4. 获取股票公告列表](#4-获取股票公告列表)
    - [请求参数](#请求参数-2)
    - [响应参数 (data 列表每条)](#响应参数-data-列表每条)
  - [5. 搜图表](#5-搜图表)
    - [请求参数](#请求参数-3)
    - [响应参数 (data 列表每条)](#响应参数-data-列表每条-1)

---

## 1. 投研知识问答

**URL**: `POST /alpha/open-api/v1/paipai/qa-text`

> 根据用户输入问题，采用RAG（Retrivel-Augment-Generation，检索增强生成)技术从Alpha派（一个覆盖A股、港股、美股的专业的投资研究SaaS产品）平台获取高质量的投研参考资料，然后进行总结推理回答。

### 请求参数

| 字段                   | 必填 | 类型         | 说明                                  | 示例                                                                                                                  |
| ---------------------- | ---- | ------------ | ------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| question               | 是   | String       | 问题内容                              | "为什么美光比海力士在hbm的市占率低？"                                                                                 |
| mode                   | 是   | String       | 模式                                  | 字符串枚举，Alpha派问答思考模式，`Flash`——简单搜索问答，一问一搜一答，`Think`——Wide Search，一问多搜一答，默认为Flash |
| context                | 否   | List[String] | 多轮对话上下文                        | ["云南缺电对哪些公司会造成影响？","对行业的影响呢？"]                                                                 |
| questionId             | 否   | String       | 唯一标识，并发时区分问题              | "OZqY\_-E55-M1OwxZTL4U81713770934462"                                                                                 |
| isAutoRoute            | 否   | Boolean      | 自动路由(默认true)，false强制文本回答 | true                                                                                                                  |
| isStream               | 否   | Boolean      | 流式返回(默认false)                   | false                                                                                                                 |
| isWebSearch            | 否   | Boolean      | 联网搜索(默认false)                   | false                                                                                                                 |
| isDeepReasoning        | 否   | Boolean      | 深度推理(默认false)                   | false                                                                                                                 |
| requestSelectStartTime | 否   | String       | 筛选开始时间                          | "2025-01-01"                                                                                                          |
| requestSelectEndTime   | 否   | String       | 筛选结束时间                          | "2025-03-01"                                                                                                          |

### 响应参数

| 字段        | 类型       | 说明                           |
| ----------- | ---------- | ------------------------------ |
| answer      | String     | 回答内容，stream模式逐字返回   |
| answerOrder | Integer    | stream回答序号                 |
| references  | List[Dict] | 引用数据列表（见下方引用结构） |
| type        | Integer    | 回答类型(见下方类型码)         |
| isEnd       | Boolean    | 本次回答是否完结               |
| routeName   | String     | 处理逻辑路由名称               |
| questionId  | String     | 问题唯一标识                   |

### 回答类型码(type)

| 值  | 含义             |
| --- | ---------------- |
| 101 | 问题分析阶段     |
| 102 | 获取资料阶段     |
| 103 | 获取资料完成     |
| 104 | 正在生成回答     |
| 108 | 思维链           |
| 200 | 成功             |
| 201 | 结果为空         |
| 202 | GPT              |
| 203 | 用户当日超过限制 |
| 204 | 系统当前超过限制 |
| 206 | 敏感词限制       |
| 207 | PRE_QA           |
| 500 | 失败             |

### 引用数据结构 (references)

每条引用包含以下字段：

| 字段          | 说明         |
| ------------- | ------------ |
| sentence      | 引用句子     |
| rank          | 排序号       |
| chunk         | 上下文文本   |
| id            | 引用资源id   |
| type          | 引用资源类型 |
| title         | 标题         |
| publishDate   | 发布日期     |
| isSelfPrivate | 是否私有纪要 |
| url           | 引用资源链接 |
| teamName      | 团队名称     |
| instShortName | 机构名称     |
| filePath      | 引用文件路径 |

### 引用类型枚举

| type值                | 含义                 |
| --------------------- | -------------------- |
| comment               | 机构点评             |
| vps                   | 基金定期报告         |
| report                | 内资研报             |
| foreign_report        | 外资研报             |
| wechat_public_article | 公众号               |
| ann                   | 公司公告             |
| roadShow              | 路演纪要             |
| roadShow_ir           | 上市公司披露投关纪要 |
| roadShow_us           | 美股纪要             |
| table                 | 公告/研报表格        |
| image                 | 研报图片             |
| edb                   | EDB数据库            |

### 请求示例 - 非stream模式

```json
{
    "question": "请梳理下国内各车厂智能驾驶的研发进度",
    "questionId": "OZqY_-E55-M1OwxZTL4U81713770934462",
    "isStream": false,
    "isAutoRoute": false
}
```

### 请求示例 - stream模式

```json
{
    "question": "讯兔科技首席科学家是谁？",
    "questionId": "OZqY_-E55-M1OwxZTL4U81713770934462",
    "isStream": true,
    "isAutoRoute": false
}
```

---

## 2. 投研知识检索（基于RAG技术）

> 根据用户输入问题，采用RAG（Retrivel-Augment-Generation，检索增强生成)技术从Alpha派（一个覆盖A股、港股、美股的专业的投资研究SaaS产品）平台检索召回高质量的投研参考资料

**URL**: `POST /alpha/open-api/v1/paipai/recall-data`

### 请求参数

| 字段       | 必填 | 类型         | 说明                                                                            | 示例                        |
| ---------- | ---- | ------------ | ------------------------------------------------------------------------------- | --------------------------- |
| query      | 是   | String       | 查询问题                                                                        | "贵州茅台2024年市值多少?"   |
| recallType | 是   | List[String] | 召回数据类型筛选                                                                | ["comment", "qa", "report"] |
| isCutOff   | 否   | Boolean      | 是否截断数据(默认true)。true=与送入大模型一致；false=返回排序后截断前的完整内容 | false                       |
| startTime  | 否   | String       | 开始日期，格式yyyy-MM-dd                                                        | "2025-02-18"                |
| endTime    | 否   | String       | 结束日期，格式yyyy-MM-dd                                                        | "2025-03-20"                |

### recallType 可选值

List[str]，文档类型列表，JSON列表字符串，示例：`[]`表示不限制类型，`["report"]`表示限定`report`类型。支持的报告类型及含义如下：

- "comment"——点评，覆盖了国内券商分析师，每日给专业机构投资者发送的点评信息（时效性高，但可能存在部分吹水、夸大、信息质量不扎实的问题）
- "vps"——基金定期报告
- "report"——国内券商研报，覆盖了国内券商分析师撰写的研究报告
- "foreign_report"——海外券商研报 ，覆盖了国外头部券商分析师（比如摩根、花旗等机构分析师）撰写的研究报告
- "wechat_public_article"——微信公众号，覆盖了国内微信生态下的一些对投研有帮助的公众号内容，包括各个行业主题相关的公众号资讯，以及上市公司官方微信公众号
- "ann"——上市公司官方公告，覆盖了上市公司在交易所发布的最权威最官方口径的公告内容
- "roadShow"——路演会议纪要，包括上市公司的业绩交流会、券商路演、专家交流等各种国内主流路演平台的会议纪要
- "roadShow_ir"——上市公司官方披露的公开路演纪要，量少，且优于披露要求稀缺性弱于`roadShow`类型
- "roadShow_us"——美股上市公司earnings_scripts纪要，
- "roadShow_od"——私域会议纪要，"table"——公告/研报中的数据表格，
- "image"——研报中的图片，通常包括一些产业链图示、指标分析对比的图表等，
- "qa"——基于调研纪要、上市公司公告，提取的调研与路演中的Q&A
- "edb"——宏观经济、行业、个股主题的时间序列数据库

### 响应参数

返回 `data` 为 List，每条数据结构：

| 字段        | 类型         | 说明                             |
| ----------- | ------------ | -------------------------------- |
| id          | String       | 数据ID                           |
| type        | String       | 数据类型（comment/qa/report等）  |
| contextInfo | String       | 上下文信息（含发布时间、标题等） |
| chunks      | List[String] | 文本块内容                       |
| sentenceIds | List[String] | 句子ID列表                       |
| contextText | String       | 问题文本（仅qa类型有值）         |
| answer      | String       | 回答文本（仅qa类型有值）         |

### 请求示例

```json
{
    "query": "贵州茅台2024年市值多少?",
    "isCutOff": false,
    "recallType": ["comment", "qa", "report"],
    "startTime": "2025-02-18",
    "endTime": "2025-03-20"
}
```

### 响应示例

```json
{
    "code": 200000,
    "message": "success",
    "data": [
        {
            "id": "HCMT00000000839881",
            "type": "comment",
            "contextInfo": "(发布时间为:2025-03-18 08:53:40)标题：河南&江苏白酒综合大商交流250317，点评内容：",
            "chunks": ["波汾价格从470-480升至500..."],
            "sentenceIds": ["HCMT00000000839881_11"],
            "contextText": "",
            "answer": ""
        },
        {
            "id": "TRANSQA000011039428",
            "type": "qa",
            "contextInfo": "(发布时间为:2025-02-18)股票：中国神华...",
            "chunks": [],
            "sentenceIds": [],
            "contextText": "2024年年度的分红展望是什么?",
            "answer": "2023年按A股口径分红比例为75.2%..."
        }
    ]
}
```

---

## 3. 股票 Agent 接口

**URL**: `POST /alpha/open-api/v1/paipai/stock/agent`

专业 Agentic-Workflow，支持多种投研场景。SSE 流式返回，响应结构与文本问答接口一致（type 状态码、references 结构相同）。

所有模式均需传 `question`（String，必填），⚠️不同Mode下，question的含义不同，详情参考下文

---

### agentMode=1 — 个股业绩点评

| 字段              | 必填 | 类型    | 说明                                                                                      |
| ----------------- | :--: | ------- | ----------------------------------------------------------------------------------------- |
| question          |  是  | String  | 模板字符串，`{stock.name}{stockReportPeriod}业绩点评`，比如：`易德龙2025年一季报业绩点评` |
| stock             |  是  | Dict    | `{"code": "603380.SH", "name": "易德龙"}`                                                 |
| reportType        |  是  | String  | 报告类型，如 `季报` `年报`                                                                |
| stockReportId     |  是  | String  | 公告ID（先从[4. 获取股票公告列表](#4-获取股票公告列表)查询获取）                          |
| stockReportTitle  |  是  | String  | 公告标题，参考从[4. 获取股票公告列表](#4-获取股票公告列表)查询获取的结果                  |
| stockReportPeriod |  是  | String  | 报告期，如 `2025年一季报`                                                                 |
| template          |  是  | Integer | `0`（固定传alpha派模板）`1` 时需要填写`templateText`字段                                  |
| templateText      |  否  | String  | 用户自己的业绩点评模板                                                                    |
| templateConcern   |  否  | String  | 用户点评中，希望关注的话题、要点                                                          |

如果用户需要根据自己的点评模板填写，需要修改`templateText`，如果额外一些关注话题，修改`templateConcern`

示例参数：

```json
{
    "agentMode": 1,
    "question": "易德龙2025年一季报业绩点评",
    "stock": {
        "code": "603380.SH",
        "name": "易德龙"
    },
    "template": 0,
    "templateText": "",
    "reportType": "季报",
    "stockReportId": "HANNC002658114224",
    "stockReportTitle": "易德龙(603380.SH):苏州易德龙科技股份有限公司2025年第一季度报告",
    "stockReportPeriod": "2025年一季报",
    "templateConcern": ""
}
```

---

### agentMode=2 — 公司一页纸

| 字段         | 必填 | 类型    | 说明                                                                                              |
| ------------ | :--: | ------- | ------------------------------------------------------------------------------------------------- |
| question     |  是  | String  | 模板字符串，`{stock.name}（{stock.code}）的公司一页纸`，比如：`亿纬锂能（300014.SZ）的公司一页纸` |
| stock        |  是  | Dict    | `{"code": "300014.SZ", "name": "亿纬锂能"}`                                                       |
| template     |  是  | Integer | `0`（固定传alpha派模板）`1` 时需要填写`templateText`字段                                          |
| templateText |  否  | String  | 用户自己的公司一页纸分析模板                                                                      |
| language     |  否  | String  | 语言，美股可选 `中文` / `英文`                                                                    |

示例参数：

```json
{
    "agentMode": 2,
    "question": "亿纬锂能（300014.SZ）的公司一页纸",
    "stock": {
        "code": "300014.SZ",
        "name": "亿纬锂能"
    },
    "template": 0,
    "templateText": ""
}
```

---

### agentMode=3 — 个股调研大纲

| 字段         | 必填 | 类型    | 说明                                                                                                  |
| ------------ | :--: | ------- | ----------------------------------------------------------------------------------------------------- |
| question     |  是  | String  | 模板字符串，`{stock.name}（{stock.code}）的调研问题大纲`，比如：`巨星科技（002444.SZ）的调研问题大纲` |
| stock        |  是  | Dict    | 股票信息，`{"code": "002444.SZ", "name": "巨星科技"}`                                                 |
| template     |  是  | Integer | `0`（固定参数）                                                                                       |
| templateText |  否  | String  | 用户在调研大纲总结中关注的内容，默认传空字符串                                                        |

示例参数：

```json
{
    "agentMode": 3,
    "question": "巨星科技（002444.SZ）的调研问题大纲",
    "stock": {
        "code": "002444.SZ",
        "name": "巨星科技"
    },
    "template": 0,
    "templateText": ""
}
```

---

### agentMode=5 — 主题选股

| 字段         | 必填 | 类型    | 说明                                                             |
| ------------ | :--: | ------- | ---------------------------------------------------------------- |
| question     |  是  | String  | 选股主题描述，与`templateText`保持一致，比如：`和白酒相关的公司` |
| template     |  是  | Integer | `1`（固定参数）                                                  |
| templateText |  是  | String  | 选股主题描述，与`question`保持一致                               |

示例参数：

```json
{
    "agentMode": 5,
    "question": "和白酒相关的公司",
    "template": 1,
    "templateText": "和白酒相关的公司"
}
```

---

### agentMode=7 — 投资逻辑

| 字段         | 必填 | 类型    | 说明                                                                                                  |
| ------------ | :--: | ------- | ----------------------------------------------------------------------------------------------------- |
| question     |  是  | String  | 模板字符串，`{stock.name}（{stock.code}）的公司投资逻辑`，比如：`亿纬锂能（300014.SZ）的公司投资逻辑` |
| stock        |  是  | Dict    | 股票信息，`{"code": "300014.SZ", "name": "亿纬锂能"}`                                                 |
| template     |  是  | Integer | `0`（固定参数）                                                                                       |
| templateText |  否  | String  | 用户在投资逻辑中关注的分析要点、维度、指标等，默认传空字符串                                          |
| onlyAnswer   |  否  | Boolean | 是否只返回最终答案，不返回中间过程（默认 `false`）                                                    |

示例参数：

```json
{
    "agentMode": 7,
    "question": "亿纬锂能（300014.SZ）的公司投资逻辑",
    "onlyAnswer": false,
    "stock": {
        "code": "300014.SZ",
        "name": "亿纬锂能"
    },
    "template": 0,
    "templateText": ""
}
```

---

### agentMode=8 — 可比公司

| 字段            | 必填 | 类型    | 说明                                                                                        |
| --------------- | :--: | ------- | ------------------------------------------------------------------------------------------- |
| question        |  是  | String  | 模板字符串，`{stock.name}（{stock.code}）的可比公司`，比如：`比亚迪（002594.SZ）的可比公司` |
| stock           |  是  | Dict    | 股票信息，`{"code": "002594.SZ", "name": "比亚迪"}`                                         |
| template        |  是  | Integer | `1`（固定参数）                                                                             |
| templateText    |  否  | String  | 暂未启用，默认传空字符串                                                                    |
| templateConcern |  否  | String  | 对比过程中，用户关心的话题，比如产品参数、技术路线，估值、盈利等                            |

示例参数：

```json
{
    "agentMode": 8,
    "question": "比亚迪（002594.SZ）的可比公司",
    "stock": {
        "code": "002594.SZ",
        "name": "比亚迪"
    },
    "template": 1,
    "templateText": "",
    "templateConcern": "关注技术路线，盈利和出海能力"
}
```

---

### agentMode=9 — 观点 Challenge

| 字段                   | 必填 | 类型    | 说明                                                                                       |
| ---------------------- | :--: | ------- | ------------------------------------------------------------------------------------------ |
| question               |  是  | String  | 模板字符串，`Challenge该观点：{templateText}`，比如：`Challenge该观点：小米汽车未来的增长` |
| template               |  是  | Integer | `1`（固定参数）                                                                            |
| templateText           |  是  | String  | 待 Challenge 的观点内容，与`question`中观点描述保持一致                                    |
| templateConcern        |  否  | String  | 关注焦点，可进一步限定 Challenge 范围，如 `YU7`                                            |
| requestSelectStartTime |  否  | String  | 检索信息起始时间，格式 `yyyy-MM-dd`                                                        |
| requestSelectEndTime   |  否  | String  | 检索信息截止时间，格式 `yyyy-MM-dd`                                                        |

示例参数：

```json
{
    "agentMode": 9,
    "question": "Challenge该观点：小米汽车未来的增长",
    "template": 1,
    "templateText": "小米汽车未来的增长",
    "templateConcern": "YU7",
    "requestSelectStartTime": "2024-10-25",
    "requestSelectEndTime": "2025-10-24"
}
```

---

### agentMode=11 — 行业一页纸

| 字段          | 必填 | 类型    | 说明                                                                |
| ------------- | :--: | ------- | ------------------------------------------------------------------- |
| question      |  是  | String  | 模板字符串，`{inputIndustry}的行业一页纸`，比如：`白酒的行业一页纸` |
| inputIndustry |  是  | String  | 行业名称，如 `白酒`、`光伏`                                         |
| template      |  是  | Integer | `0`（固定传alpha派模板）；`1` 时需要填写`templateText`字段          |
| templateText  |  否  | String  | 用户自己的行业一页纸模板，`template=1` 时填写，默认传空字符串       |

示例参数：

```json
{
    "agentMode": 11,
    "question": "白酒的行业一页纸",
    "inputIndustry": "白酒",
    "template": 0,
    "templateText": ""
}
```

---

### agentMode=12 — 个股选基

| 字段         | 必填 | 类型       | 说明                                                                                                                                                                                                                |
| ------------ | :--: | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| question     |  是  | String     | 自然语言描述查询条件，格式参考：`{报告期}持有{股票名列表}的基金有哪些？`，比如：`2025三季报持有环旭电子、中际旭创、卓胜微的基金有哪些？`                                                                            |
| stockList    |  是  | List[Dict] | 股票列表，每项 `{"code": "...", "name": "..."}`                                                                                                                                                                     |
| reportDate   |  是  | String     | 报告期对应日期，格式 `yyyy-MM-dd`；需要参考`ifAnnual`参数，每年四档：`03-31`一季报、`06-30` 二级报（ifAnnual=0）/中报（ifAnnual=1）、`09-30`三季报、`12-31`四季报（ifAnnual=0）/年报（ifAnnual=1），如 `2025-09-30` |
| fundType     |  是  | String     | 基金类型筛选：`全部` / `主动` / `指数` / `ETF`                                                                                                                                                                      |
| template     |  是  | Integer    | `0`（固定参数）                                                                                                                                                                                                     |
| templateText |  否  | String     | 暂未启用，默认传空字符串                                                                                                                                                                                            |
| ifAnnual     |  否  | Integer    | 是否年报：`0`=否（默认），`1`=是                                                                                                                                                                                    |

示例参数：

```json
{
    "agentMode": 12,
    "question": "2025三季报持有环旭电子、中际旭创、卓胜微的基金有哪些？",
    "fundType": "全部",
    "reportDate": "2025-09-30",
    "ifAnnual": 0,
    "template": 0,
    "templateText": "",
    "stockList": [
        {
            "code": "601231.SH",
            "name": "环旭电子"
        },
        {
            "code": "300308.SZ",
            "name": "中际旭创"
        },
        {
            "code": "300782.SZ",
            "name": "卓胜微"
        }
    ]
}
```

---

### agentMode=13 — 主题选基

| 字段         | 必填 | 类型    | 说明                                                                                                                                                                                                                                  |
| ------------ | :--: | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| question     |  是  | String  | 自然语言描述查询条件，格式参考：`{报告期}持有{主题}的{基金类型}基金有哪些？`，比如：`2025三季报持有房地产的主动基金有哪些？`                                                                                                          |
| reportDate   |  是  | String  | 报告期对应日期，格式 `yyyy-MM-dd`；需要参考`ifAnnual`参数，每年四档：`03-31`一季报、`06-30` 二级报（ifAnnual=0）/中报（ifAnnual=1）、`09-30`三季报、`12-31`四季报（ifAnnual=0）/年报（ifAnnual=1），如 `2025-09-30`，表示`2025三季报` |
| fundType     |  是  | String  | 基金类型筛选：`全部` / `主动` / `指数` / `ETF`                                                                                                                                                                                        |
| template     |  是  | Integer | `0`（固定参数）                                                                                                                                                                                                                       |
| templateText |  否  | String  | 暂未启用，默认传空字符串                                                                                                                                                                                                              |
| ifAnnual     |  否  | Integer | 是否年报：`0`=否（默认），`1`=是                                                                                                                                                                                                      |

示例参数：

```json
{
    "agentMode": 13,
    "question": "2025三季报持有房地产的主动基金有哪些？",
    "fundType": "主动",
    "reportDate": "2025-09-30",
    "ifAnnual": 0,
    "template": 0,
    "templateText": ""
}
```

---

### agentMode=15 — 画图

| 字段         | 必填 | 类型         | 说明                                                                            |
| ------------ | :--: | ------------ | ------------------------------------------------------------------------------- |
| question     |  是  | String       | 画图主题，即用户实际输入的内容，比如：`黄金`、`新能源汽车`                      |
| pictureColor |  是  | List[String] | 颜色HEX值，二元组，分别表示主色和辅色，不含 `#` 前缀，如 `["2A66F6", "A5A8AF"]` |
| pictureStyle |  是  | String       | 画图风格：`PPT风格` / `科普风格`                                                |
| source       |  否  | Integer      | 产出形式：`0`=仅图片（默认），`1`=图文                                          |

示例参数：

```json
{
    "agentMode": 15,
    "question": "黄金",
    "pictureColor": ["2A66F6", "A5A8AF"],
    "pictureStyle": "科普风格",
    "source": 0
}
```

---

## 4. 获取股票公告列表

**URL**: `POST /alpha/open-api/v1/paipai/stock/report`

根据股票代码获取上市公司在交易所公开的公告列表，常用于查询业绩点评所需的 `stockReportId`。

### 请求参数

| 字段 | 必填 | 类型   | 说明     | 示例值        |
| ---- | ---- | ------ | -------- | ------------- |
| code | 是   | String | 股票编码 | `"603380.SH"` |

### 响应参数 (data 列表每条)

| 字段             | 类型   | 说明     |
| ---------------- | ------ | -------- |
| stockCode        | String | 股票编码 |
| stockName        | String | 股票名称 |
| reportType       | String | 报告类型 |
| reportPeriod     | String | 报告期   |
| stockReportId    | String | 公告ID   |
| stockReportTitle | String | 报告标题 |

---

## 5. 搜图表

**URL**: `POST /alpha/open-api/v1/paipai/search-image`

根据语义从研报和公告中搜索相关图片和表格。

### 请求参数

| 字段       | 必填 | 类型         | 说明                                                                 | 示例值         |
| ---------- | ---- | ------------ | -------------------------------------------------------------------- | -------------- |
| queryText  | 是   | String       | 检索查询的文本内容                                                   | "黄金价格趋势" |
| filesRange | 否   | List[String] | 来源类型代码列表，可选值：3-内资研报，8-外资研报，6-公告，9-三方研报 | `["3","8"]`    |
| topk       | 否   | Integer      | 返回结果数量，范围1-100，默认50                                      | `80`           |
| recallMode | 否   | String       | 召回模式: both(默认)/vector_only/es_only                             | `"both"`       |
| useLlmRank | 否   | Boolean      | 是否使用LLM重排序，默认false                                         | `false`        |
| startDate  | 否   | String       | 开始日期，格式 yyyy-MM-dd                                            | `"2025-01-01"` |
| endDate    | 否   | String       | 结束日期，格式 yyyy-MM-dd                                            | `"2025-10-01"` |

### 响应参数 (data 列表每条)

| 字段            | 类型         | 说明                                    |
| --------------- | ------------ | --------------------------------------- |
| articleId       | String       | 文章ID                                  |
| articleTitle    | String       | 文章标题                                |
| articleType     | String       | 文章类型                                |
| publishDate     | String       | 发布日期 yyyy-MM-dd HH:mm:ss            |
| pageIndex       | Integer      | 页码索引                                |
| bbox            | String       | 图片在页面上的位置坐标 [x1, y1, x2, y2] |
| captionList     | List[String] | 图片标题列表                            |
| footnoteList    | List[String] | 脚注列表                                |
| imageUrl        | String       | 图片URL                                 |
| source          | String       | 图片来源                                |
| llmScore        | Float        | LLM评分                                 |
| llmReason       | String       | LLM评分理由                             |
| institutionList | List[Dict]   | 机构信息列表 (code, name, logo)         |
| authorList      | List[String] | 作者列表                                |

---
