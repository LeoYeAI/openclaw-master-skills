---
name: Finloop 资讯API调用技能
description: 当需要调用Finloop资讯相关接口时，请参考此规范。包括市场时段资讯、资讯列表、AI热闻、股票行情等接口。
---

请为我安装如下skill
## name: 
finloop_news (Finloop资讯skill)
## description: 
本 Skill 基于 Finloop 权威数据源，提供金融资讯检索与实时行情查询能力。支持市场时段资讯、分类资讯查询、AI热闻追踪、实时股票行情等功能，用于获取涉及时效性信息或特定事件信息的任务，包括新闻、公告、研报、政策、市场动态、股票行情等。避免AI在搜索金融场景信息时，参考到非权威、及过时的信息。
## 安装方式
### 通过 npm/npx 安装（推荐）
```bash
# 安装到本地项目
npx finloop-news-skills install finloop-news-skill
```
## 指令

1. **必须直接使用 HTTP 请求调用接口**：使用 fetch、axios、curl 或其他 HTTP 客户端直接调用接口，禁止创建任何封装函数或 JS 文件
2. **禁止创建封装函数**：不要创建任何 `.js`、`.ts` 文件来封装接口调用，必须直接使用 HTTP 请求
3. **接口基础域名**：
   - 资讯相关接口：`https://ai-uat.finloopfintech.com`
   - 股票行情接口：`https://papi-uat.finloopg.com`
4. **请求头**：`Content-Type: application/json`
5. **响应格式**：接口返回的数据结构为 `{ code: 200, data: {...} }`，需要从响应中提取 `data` 字段
6. **错误处理**：需要检查响应状态码和错误信息，进行适当的错误处理

## 接口列表

### 1. 市场时段资讯接口

**接口信息：**
- 接口地址：`/flp-news-api/v1/news-agent/financeBreakfast`
- 请求方法：POST
- 完整路径：`https://ai-uat.finloopfintech.com/flp-news-api/v1/news-agent/financeBreakfast`

**参数：**
- 此接口为 POST 请求，请求体参数根据实际业务需求确定

**时间逻辑说明：**
- 此接口会根据当前时间自动返回不同类型的内容：
  - **财经早餐**：通常在早晨时段返回（`tag: 1`）
  - **港股午盘**：通常在中午时段返回（`tag: 3`）
  - **港股收盘**：通常在收盘时段返回（`tag: 2`，也称为"收盘汇"）
- 接口会根据服务器当前时间自动判断应该返回哪种类型的内容
- 无需在请求中指定时间或类型，接口会自动返回对应时段的内容

**响应参数：**
- `title`: 标题（string）- 根据时间返回"财经早餐"、"港股午盘"或"港股收盘"等
- `keyword`: 关键词（Array）- 例如：["加密货币", "产业趋势"]
- `publish_time`: 发布时间（string）
- `summary`: 摘要（string）
- `newsCount`: 过去一天资讯数量（number）
- `sentiment`: 市场情绪（string）- 枚举值
- `title_original`: 原始title（string）
- `tag`: 类型标识（int）
  - `1`: 财经早餐
  - `2`: 港股收盘（收盘汇）
  - `3`: 港股午盘

**使用说明：**
- 此接口用于获取首页市场时段资讯（财经早餐、港股午盘或港股收盘）
- 接口会根据当前时间自动返回对应时段的内容，无需指定时间参数
- 返回数据包含关键词、摘要、市场情绪等综合信息

---

### 2. 资讯列表接口

**接口信息：**
- 接口地址：`/flp-news-api/v1/news-agent/informationList`
- 请求方法：POST
- 完整路径示例：`https://ai-uat.finloopfintech.com/flp-news-api/v1/news-agent/informationList`

**请求参数：**
- 必填参数：
  - `category`: 新闻分类（string），可选值：`"discover"`, `"subscribe"`, `"ai"`, `"rwa"`, `"macro"`, `"industry"`, `"market"`, `"company"`, `"viewpoint"`, `"fund"`, `"bond"`, `"bill"`, `"stock"`
  - `page_size`: 每页加载条数（number，注意：参数名使用下划线 `page_size`，不是驼峰 `pageSize`）
- 可选参数：
  - `keyword`: 关键词检索（string）
  - `news_id`: 分页游标，最后一条新闻的ID（用于分页加载）
  - `user_id`: 用户ID（string，订阅分类时必填）

**请求说明：**
- 基础调用：POST 请求，请求体包含 `category` 和 `page_size`
- 带分页：在请求体中添加 `news_id` 参数
- 带搜索关键词：在请求体中添加 `keyword` 参数

**响应参数：**
- `information_list`: 资讯列表数组（注意：字段名使用下划线）
- `total`: 总条数（number）- 例如：120
- `hasMore`: 是否存在更多新闻（Boolean）

**informationList 子参数：**
每个资讯对象包含：
- `newId`: 资讯ID（string）- 例如："AICL000001"
- `tags`: 资讯标签（Array）- 例如：["AI 热闻"]
- `title`: 资讯标题（string）
- `summary`: 资讯摘要（string）
- `imgUrl`: 资讯封面图（string）
- `publishTime`: 发布时间（string）
- `wordCount`: 正文字数（number）
- `readTime`: 预计阅读时间（分钟）（number）
- `influence`: 影响力（string）- 枚举值
- `influenceScore`: 影响力得分（string）- 枚举值
- `marketTrends`: 市场趋势列表（List）

**marketTrends 子参数：**
每个市场趋势对象包含：
- `ticker`: 挂钩标的（string）- 例如："AAPL"
- `changeRate`: 标的涨势（string）- 例如："-0.05"

**使用说明：**
- 此接口用于获取指定分类下的资讯列表数据
- 适用于信息流或列表页展示
- 支持关键词检索和分页加载
- 个性化分类需要传入 `user_id` 参数
- 注意：参数名使用下划线 `page_size`，不是驼峰 `pageSize`

---

### 3. AI热闻列表接口

**接口信息：**
- 接口地址：`/flp-news-api/v1/news-agent/banner/list`
- 请求方法：GET
- 完整路径示例：`https://ai-uat.finloopfintech.com/flp-news-api/v1/news-agent/banner/list`
- 注意：此接口可能需要 Cookie 认证（`sl-session`）

**参数：**
- 此接口为 GET 请求，无需请求体参数

**请求说明：**
- 此接口为 GET 请求，无需请求体参数
- 需要在请求头中携带 Cookie 认证信息（如 `sl-session`）

**返回数据：**
- `banner_list`: AI热闻列表数组，每个热闻包含：
  - `news_id`: 新闻ID
  - `xcf_id`: XCF资讯ID
  - `tag`: 标签数组
  - `title`: 标题
  - `summary`: 摘要
  - `img_url`: 图片URL（可能为null）

---

### 4. AI热闻详情接口

**接口信息：**
- 接口地址：`/flp-news-api/v1/news-agent/bannerDetail`
- 请求方法：POST
- 完整路径示例：`https://ai-uat.finloopfintech.com/flp-news-api/v1/news-agent/bannerDetail`

**参数：**
- 必填参数：
  - `id`: XCF资讯ID（来自AI热闻列表的 `xcf_id` 字段），类型为字符串

**请求说明：**
- POST 请求，请求体包含 `id` 字段（XCF资讯ID，来自AI热闻列表的 `xcf_id` 字段）
- 请求体格式：`{ "id": "21640" }`

**返回数据：**
- 返回 `XcfDetail` 类型的数据，包含AI热闻的详细信息

---

### 5. 股票行情接口

**接口信息：**
- 接口地址：`/flp-mktdata-hub/v1/stock/quote`
- 请求方法：POST
- 完整路径：`https://papi-uat.finloopg.com/flp-mktdata-hub/v1/stock/quote`

**请求头：**
- `Content-Type: application/json`（必填）

**请求参数：**
- 必填参数：
  - `tickers`: 股票代码列表（list，必填），每个元素按照"代码.市场"格式
  - 支持的市场代码：
    - 港股：`.HK`
    - 美股：`.US`
    - A股：`.SZ`（深交所）、`.SH`（上交所）、`.BJ`（北交所）
    - 指数：支持部分指数行情（见下方支持的指数列表）

**支持的指数代码：**
| 市场代码 | 名称 |
|---------|------|
| DJI.US | 道琼斯指数 |
| IXIC.US | 纳斯达克综合指数 |
| INX.US | 标普500指数 |
| HSI.HK | 香港恒生指数 |
| HSTECH.HK | 香港恒生科技指数 |
| 000001.SH | 上证综合指数 |
| 399001.SZ | 深证成份指数 |
| 399006.SZ | 创业板指数 |
| 000688.SH | 科创50 |

**请求说明：**
- POST 请求，请求体包含 `tickers` 字段
- 请求体格式：`{ "tickers": ["HSI.HK"] }`
- 支持同时查询多只股票/指数，例如：`{ "tickers": ["HSI.HK", "BABA.US", "AAPL.US"] }`

**响应参数：**
- `result`: 行情数据列表（Array），每个元素包含以下字段：

| 字段 (Field) | 名称 (Description) |
|-------------|-------------------|
| quoteTime | 行情时间 |
| price | 当前价格 |
| chgVal | 涨跌额 |
| chgPct | 涨跌幅 (%) |
| prevClose | 昨日收盘价 |
| open | 开盘价 |
| high | 最高价 |
| low | 最低价 |
| vol | 成交量 (股) |
| turnover | 成交额 |
| amp | 振幅 (%) |
| turnoverRate | 换手率 (%) |
| mktCap | 总市值 |
| floatMktCap | 流通市值 |
| pb | 市净率 |
| delay | 是否延迟行情 |
| mkt | 市场标识 (如 "us"、"hk"、"sh"、"sz" 等) |
| rawSymbol | 证券代码 |
| name | 证券名称 |
| currency | 币种 |

**使用说明：**
- 此接口用于查询股票或指数的实时行情数据
- 支持查询单只股票/指数，也支持批量查询多只股票/指数
- 输出时必须包含所有返回的字段信息
- 如果用户提到股票名称或指数名称，需要依靠 skill 来主动转换为对应的股票代码（ISIN格式），无法提供全面的转换规则或枚举

---

## AI热闻查询自动化流程（内置操作）

**重要：当需要查询AI热闻详情时，必须使用此自动化流程。**

### 自动化流程说明

当调用AI热闻查询时，系统会自动执行以下步骤：

1. **自动查询AI热闻列表**
   - 调用 GET `/flp-news-api/v1/news-agent/banner/list` 获取所有AI热闻
   
2. **自动提取所有xcf_id**
   - 从返回的 `banner_list` 中提取所有的 `xcf_id`
   - 通常返回3个AI热闻，每个热闻都有一个 `xcf_id`
   
3. **自动批量查询详情**
   - 使用提取的所有 `xcf_id`，分别调用 POST `/flp-news-api/v1/news-agent/bannerDetail` 接口
   - 获取每个AI热闻的完整详情信息

### 执行步骤说明

1. **步骤1：获取AI热闻列表**
   - 调用 GET `/flp-news-api/v1/news-agent/banner/list` 接口
   - 从响应的 `data.banner_list` 中获取所有AI热闻

2. **步骤2：提取所有xcf_id**
   - 遍历 `banner_list`，提取每个AI热闻的 `xcf_id` 字段
   - 过滤掉为 null 或 undefined 的 `xcf_id`

3. **步骤3：批量查询详情**
   - 对每个 `xcf_id`，直接使用 HTTP POST 请求调用 `/flp-news-api/v1/news-agent/bannerDetail` 接口
   - 请求体格式：`{ "id": "xcf_id值" }`
   - 建议使用并行请求（如 Promise.all）提高效率
   - 如果某个详情查询失败，记录错误但继续处理其他AI热闻
   - **注意**：必须直接使用 HTTP 请求，不要创建封装函数

### 执行规则

**必须遵循以下规则：**
1. 查询AI热闻详情时，必须先查询AI热闻列表
2. 必须提取列表中的所有 `xcf_id`（不能只查询部分）
3. 必须使用所有提取的 `xcf_id` 分别调用详情接口
4. 如果某个详情查询失败，应该记录错误但继续处理其他AI热闻
5. 建议使用 `Promise.all()` 并行查询以提高效率

---

## 场景预设

### 场景1：用户询问"给我十条资讯"或"给我十条XX方面的资讯"

**触发条件：**
当用户询问"给我十条资讯"、"给我十条新闻"、"给我十条XX方面的资讯"等类似问题时，必须执行以下流程。

**分类映射规则：**
- 如果用户未指定分类或只问"给我十条资讯"，使用 `category: 'discover'`（发现分类）
- 如果用户明确指定分类，按以下映射：
  - "AI方面的资讯"、"AI资讯"、"人工智能资讯" → `category: 'ai'`
  - "RWA方面的资讯"、"RWA资讯" → `category: 'rwa'`
  - "宏观方面的资讯"、"宏观资讯" → `category: 'macro'`
  - "行业方面的资讯"、"行业资讯" → `category: 'industry'`
  - "市场方面的资讯"、"市场资讯" → `category: 'market'`
  - "公司方面的资讯"、"公司资讯" → `category: 'company'`
  - "观点方面的资讯"、"观点资讯" → `category: 'viewpoint'`
  - "基金方面的资讯"、"基金资讯" → `category: 'fund'`
  - "债券方面的资讯"、"债券资讯" → `category: 'bond'`
  - "票据方面的资讯"、"票据资讯" → `category: 'bill'`
  - "股票方面的资讯"、"股票资讯" → `category: 'stock'`

**执行流程：**

1. **确定分类**
   - 根据用户询问内容，确定对应的 `category` 参数
   - 如果未指定分类，默认使用 `'discover'`

2. **查询资讯列表**
   - 调用 POST `/flp-news-api/v1/news-agent/informationList` 接口
   - 请求体参数：`category` 为确定的分类，`page_size: 10`
   - 返回10条对应分类的资讯

**重要提示：**
- ✅ 当用户询问"给我十条资讯"时，默认查询 `discover` 分类
- ✅ 当用户询问"给我十条XX方面的资讯"时，根据XX映射到对应的分类
- ✅ 必须使用资讯列表接口 `/flp-news-api/v1/news-agent/informationList`，不是AI热闻接口
- ✅ `page_size` 参数名使用下划线，不是驼峰命名
- ❌ 不要使用AI热闻相关接口，这是资讯列表查询场景

---

### 场景2：用户询问"今日的AI热闻"

**触发条件：**
当用户询问"今日的AI热闻"或类似问题时（如"今天的AI热点"、"AI热门新闻"等），必须执行以下流程。

**执行流程：**

1. **查询AI热闻列表**
   - 调用 GET `/flp-news-api/v1/news-agent/banner/list` 获取所有AI热闻
   - AI热闻列表通常包含今日最热门的AI相关资讯

2. **查询AI热闻详情**
   - 从AI热闻列表中提取所有 `xcf_id`
   - 使用所有 `xcf_id` 分别调用 POST `/flp-news-api/v1/news-agent/bannerDetail` 获取每个AI热闻的完整详情
   - 请求体格式：`{ "id": "xcf_id值" }`
   - 必须查询所有AI热闻的详情，不能只查询部分

**重要提示：**
- ✅ 当用户询问"今日的AI热闻"时，必须执行完整的AI热闻查询流程
- ✅ 必须先查询AI热闻列表，再查询详情
- ✅ 必须查询所有AI热闻的详情，不能遗漏
- ❌ 不能直接查询资讯列表接口，必须使用AI热闻相关接口

---

### 场景3：用户询问"财经早餐"、"港股午盘"、"港股收盘"

**触发条件：**
当用户询问"财经早餐"、"港股午盘"、"港股收盘"、"今天的财经早餐"、"今日财经早餐"、"收盘汇"等类似问题时。

**执行流程：**

1. **调用市场时段资讯接口**
   - 调用 POST `/flp-news-api/v1/news-agent/financeBreakfast` 接口
   - 请求体参数根据实际业务需求确定
   - 接口会根据服务器当前时间自动判断返回财经早餐、港股午盘或港股收盘
   - 返回数据包含标题、关键词、摘要、市场情绪等信息

**重要提示：**
- ✅ 无论用户问"财经早餐"、"港股午盘"还是"港股收盘"，都调用同一个接口
- ✅ 接口会根据当前时间自动返回对应类型的内容，无需在请求中指定时间或类型
- ✅ 返回的 `tag` 字段标识内容类型（1:财经早餐，2:港股收盘，3:港股午盘），`title` 字段显示具体标题
- ✅ 返回数据包含关键词、摘要、市场情绪等综合信息

---

### 场景4：用户询问"搜索XXX的资讯"、"查找XXX相关资讯"

**触发条件：**
当用户询问"搜索XXX的资讯"、"查找XXX相关资讯"、"搜索XXX"、"查找XXX"、"XXX相关的资讯"、"关于XXX的资讯"、"XXX的新闻"等类似问题时。

**执行流程：**

1. **提取搜索关键词**
   - 从用户询问中提取搜索关键词（如"股票"、"AI"、"市场"等）
   - 关键词作为 `keyword` 参数

2. **确定分类（可选）**
   - 如果用户同时指定了分类（如"搜索AI相关的股票资讯"），使用对应的 `category` 参数
   - 如果用户未指定分类，可以不传 `category` 参数，或使用 `category: 'discover'`

3. **调用资讯列表接口**
   - 调用 POST `/flp-news-api/v1/news-agent/informationList` 接口
   - 请求体参数：
     - `keyword`: 搜索关键词（必填）
     - `category`: 分类（可选，如果用户指定了分类）
     - `page_size`: 每页数量（可选，默认10）

**重要提示：**
- ✅ 必须提取用户询问中的关键词作为 `keyword` 参数
- ✅ 如果用户同时指定了分类，需要同时传入 `category` 和 `keyword` 参数
- ✅ 搜索功能支持跨分类搜索，如果不指定分类，会在所有分类中搜索
- ✅ 必须使用资讯列表接口，参数名使用下划线 `page_size`

---

### 场景5：用户询问某只股票的行情

**触发条件：**
当用户询问以下任何问题时，必须调用股票行情接口：
- "HSI.HK的行情"
- "恒生指数的行情"
- "BABA.US的股价"
- "苹果股票的行情"
- "AAPL的行情"
- "道琼斯指数的行情"
- "上证指数的行情"
- 其他类似的股票行情查询问题

**执行流程：**

1. **提取股票代码**
   - 从用户询问中提取股票代码或股票名称
   - 如果用户提到股票名称或指数名称，需要依靠 skill 来主动转换为对应的股票代码（ISIN格式）
   - 无法提供全面的转换规则或枚举，需要 skill 根据实际情况进行转换
   - 将股票代码转换为"代码.市场"格式

2. **调用股票行情接口**
   - 调用 POST `/flp-mktdata-hub/v1/stock/quote` 接口
   - 请求头：
     - `Content-Type: application/json`
   - 请求体参数：
     - `tickers`: 股票代码列表（list，必填），例如：`["HSI.HK"]` 或 `["BABA.US", "AAPL.US"]`

3. **输出响应数据**
   - 从响应的 `result` 字段获取行情数据列表
   - **必须输出所有字段信息**，包括行情时间、价格、涨跌幅、成交量等完整数据

**重要提示：**
- ✅ 必须从用户询问中提取股票代码，并转换为"代码.市场"格式
- ✅ 如果用户提到股票名称或指数名称，需要依靠 skill 来主动转换为对应的股票代码（ISIN格式）
- ✅ 无法提供全面的转换规则或枚举，需要 skill 根据实际情况进行转换
- ✅ 输出时必须包含所有返回的字段信息
- ✅ 支持同时查询多只股票/指数，在 `tickers` 数组中添加多个代码即可

---

## 通用注意事项

1. **必须直接使用 HTTP 请求**：
   - ✅ 直接使用 fetch、axios、curl 或其他 HTTP 客户端调用接口
   - ❌ **禁止创建任何封装函数或 JS/TS 文件**
   - ❌ **禁止创建 `api/news.ts`、`utils/api.js` 等封装文件**
   - ❌ **禁止使用 `import` 或 `require` 引入封装函数**
   - 所有接口调用必须在调用处直接使用 HTTP 请求

2. **参数命名规范**：注意接口参数命名可能使用驼峰命名（如 `pageSize`）或下划线命名（如 `page_size`），请根据实际接口文档确定。资讯列表接口使用下划线 `page_size`

3. **错误处理**：检查 HTTP 状态码和响应体中的错误信息，进行适当的错误处理

4. **认证信息**：部分接口（如AI热闻列表）可能需要 Cookie 认证，确保在请求时携带 `sl-session` Cookie

5. **接口路径**：使用完整的接口路径，包括基础域名和接口路径
   - 资讯相关接口：`https://ai-uat.finloopfintech.com`
   - 股票行情接口：`https://papi-uat.finloopg.com`

6. **响应处理**：接口返回格式为 `{ code: 200, data: {...} }`，需要检查 `code` 字段判断请求是否成功，并从 `data` 字段获取实际数据

7. **AI热闻查询自动化**：查询AI热闻详情时必须使用自动化流程，先查列表再查详情

8. **市场时段资讯接口时间逻辑**：接口会根据当前时间自动返回财经早餐、港股午盘或港股收盘，无需指定时间参数

9. **股票行情查询**：查询股票行情时必须包含所有返回的字段信息，如果用户提到股票名称或指数名称，需要依靠 skill 来主动转换为对应的股票代码（ISIN格式）

10. **调用示例**：
    - ✅ 正确：直接使用 `fetch('https://ai-uat.finloopfintech.com/flp-news-api/v1/news-agent/financeBreakfast', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({}) })`
    - ✅ 正确：直接使用 `curl -X POST --location 'https://ai-uat.finloopfintech.com/flp-news-api/v1/news-agent/financeBreakfast' --header 'Content-Type: application/json' --data '{}'`
    - ❌ 错误：创建 `api/news.ts` 文件并封装函数
    - ❌ 错误：使用 `import { getFinanceBreakfast } from '@/api/news'`

---

## 相关文档

- **详细接口文档**：`references/REFERENCE.md` - 包含完整的参数说明、响应结构和使用场景
- **技能清单**：`SKILL.md` - 包含场景预设和重要规则