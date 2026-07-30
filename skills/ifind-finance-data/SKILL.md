---
name: "iFinD-Finance-Data"
description: "iFinD (同花顺) financial data query - query stocks, funds, macroeconomics, industry economics, news and announcements. Supports smart stock/fund screening, financial data queries, announcement search, and macro/industry indicator search. Trigger: ifind, 同花顺, 股票查询, 基金查询, 宏观数据, 行业数据, 金融数据, 行情数据, 财务数据, 选股, 选基, 财经新闻, 上市公司公告, 热点事件, 股票基本面, 基金业绩, 经济指标, 金融资讯, financial data, stock query, fund query, macro data, market data"
homepage: https://www.51ifind.com
version: 1.0.0
author: iFind
tags:
  - latest
---

# iFinD Financial Data Query (同花顺金融数据查询)

本技能用于查询股票、基金、宏观经济、行业经济及新闻公告数据。
This skill queries stock, fund, macroeconomic, industry economic data and news/announcements.

- **核心能力 / Core Capabilities**：智能选股选基，金融数据查询，公告资讯搜索，宏观行业指标搜索
  - Smart stock/fund screening, financial data queries, announcement search, macro/industry indicator search
- **数据范围 / Data Coverage**：股票、基金、宏观经济、行业经济及新闻公告数据
  - Stocks, funds, macroeconomics, industry economics, news and announcements

## 使用方法 / Usage

本 skill 封装了同花顺金融数据MCP服务的调用接口，支持 Python 和 Node.js 两种调用方式：
This skill encapsulates the iFinD Financial Data MCP service, supporting both Python and Node.js:

- **Node.js方案 / Node.js Solution**：使用 `call-node.js` 脚本（无需额外依赖，使用内置模块）
  - Use `call-node.js` (no extra dependencies, uses built-in modules)
- **Python方案 / Python Solution**：使用 `call.py` 脚本（需安装 `requests` 库）
  - Use `call.py` (requires `requests` library)
- **推荐方案 / Preferred**：当用户未指定python，或不确定python环境时，优先使用Node.js方案
  - When user doesn't specify Python or environment is unclear, prefer Node.js solution
- **query参数说明 / Query Note**：股票基金数据查询工具的 query 参数一般支持多主体、多指标，但不宜超过 10 个
  - Query supports multiple subjects and indicators, but keep under 10 for best results

## 首次使用 / First-Time Setup

- **配置密钥 / Configure Token**：`mcp_config.json` 用于存储用户密钥，如不存在有效密钥，需提示用户到"iFinD终端-工具-常用工具-数据MCP"获取密钥，帮助其完成密钥写入，或手动写入
  - `mcp_config.json` stores the user auth token. If no valid token exists, guide user to obtain one from "iFinD Terminal - Tools - Common Tools - Data MCP"

## 数据范围 / Data Coverage

- **股票数据 / Stock Data**：股票搜索、基本信息、财务数据、行情、股东、风险指标、ESG评级、重大事件等
  - Stock search, basic info, financial data, quotes, shareholders, risk indicators, ESG ratings, major events
- **基金数据 / Fund Data**：基金搜索、基金资料、基金行情、持仓明细、持有人结构、基金公司信息等
  - Fund search, fund profile, fund quotes, holdings, holder structure, fund company info
- **宏观经济数据 / Macro Data**：GDP、CPI、PPI、行业经济指标、大宗商品数据等
  - GDP, CPI, PPI, industry economic indicators, commodity data
- **新闻公告 / News & Announcements**：财经新闻、上市公司公告、热点事件等
  - Financial news, listed company announcements, trending events

## 使用技巧 / Tips

1. **先搜再查 / Search First**：针对宏观行业经济指标，当你无法确定用户具体想要的指标，可以先采用 `search_edb` 进行搜索，然后根据搜索结果指标结合上下文再发起数据查询 `get_edb_data`
   - For macro/industry indicators, when unsure of specific indicator, search first with `search_edb` then query with `get_edb_data`
2. **查询合并 / Combine Queries**：股票基金数据查询支持多主体、多指标查询，主体数、指标数控制在 5 个以内效果最佳
   - Stock/fund queries support multiple subjects and indicators; keep to 5 or fewer for best results
3. **板块类股票主体 / Sector Stocks**：股票数据查询支持直接以行业板块类股票作为主体，但需注意行业范围或时间范围不宜过大，以免触发超长截断
   - Stock queries support sector/stock category as subject; avoid overly broad industry or time ranges

## 核心函数 / Core Functions

### call(server_type, tool_name, params)

发起金融数据请求 / Make financial data request.

**参数 / Parameters：**
- `server_type` (str): 服务类型 / Service type:
  - `"stock"` - 股票服务 / Stock service
  - `"fund"` - 基金服务 / Fund service
  - `"edb"` - 宏观经济/行业经济指标服务 / Macro/industry economic indicator service
  - `"news"` - 新闻公告服务 / News/announcement service
- `tool_name` (str): 工具名称 / Tool name (see tool lists below)
- `params` (dict): 请求参数 / Request parameters

**返回值 / Returns：**
```python
{
    "ok": True/False,
    "status_code": HTTP状态码/HTTP status code,
    "data": ...,      # ok=True时返回/when ok=True
    "error": ...,     # ok=False时返回/when ok=False
    "raw": ...        # 原始响应/raw response
}
```

### list_tools(server_type)

列出指定服务类型的所有可用工具 / List all available tools for a service type.

---

## 股票服务工具 / Stock Service Tools (server_type="stock")

| 工具名称 / Tool | 功能说明 / Description | 典型参数 / Example Params |
|:---------|---------|---------|
| `search_stocks` | 智能选股 / Smart stock screening | `{"query": "自然语言选股条件/NL screening condition"}` 如/e.g. `"电子行业市值大于100亿"` |
| `get_stock_summary` | 股票信息摘要 / Stock summary | `{"query": "股票简称+查询内容/ticker+query"}` 如/e.g. `"茅台财务状况"` |
| `get_stock_info` | 股票基本资料、日频行情与技术指标 / Stock info, daily quotes & technical indicators | `{"query": "股票简称+指标名称+时间/ticker+indicator+time"}` 如/e.g. `"格力电器上市时间"` |
| `get_stock_shareholders` | 股本结构与股东数据 / Share structure & shareholder data | `{"query": "股票简称+指标/ticker+indicator"}` 如/e.g. `"光明乳业流通股占比"` |
| `get_stock_financials` | 财务数据与指标 / Financial data & indicators | `{"query": "股票简称+财务指标+财报日期/ticker+financial indicator+report date"}` 如/e.g. `"科大讯飞2025年三季度的ROE"` |
| `get_risk_indicators` | 风险定量指标 / Risk quantitative indicators | `{"query": "股票+时间+指标/ticker+time+indicator"}` 如/e.g. `"航天电子在2026-03-19的夏普比率"` |
| `get_stock_events` | 上市公司重大事件类指标 / Major corporate event indicators | `{"query": "股票+事件相关指标/ticker+event indicator"}` 如/e.g. `"摩尔线程IPO首发股本数量"` |
| `get_esg_data` | ESG评级数据 / ESG rating data | `{"query": "股票+ESG评级指标/ticker+ESG indicator"}` 如/e.g. `"诚意药业中诚信ESG评级"` |

### 选股查询示例 / Stock Screening Example

```python
# 智能选股 / Smart stock screening
call("stock", "search_stocks", {"query": "汽车零部件行业市值大于1000亿的股票"})
```

---

## 基金服务工具 / Fund Service Tools (server_type="fund")

| 工具名称 / Tool | 功能说明 / Description | 典型参数 / Example Params |
|:---------|---------|---------|
| `search_funds` | 基金搜索 / Fund search | `{"query": "模糊基金名称或选基需求/fund name or screening需求"}` 如/e.g. `"南方基金新能源ETF"` |
| `get_fund_profile` | 基金基本资料 / Fund profile | `{"query": "基金名称+指标/fund name+indicator"}` 如/e.g. `"工银双盈债券A(010068)的发行日期与发行费率"` |
| `get_fund_market_performance` | 基金行情与业绩 / Fund quotes & performance | `{"query": "基金名称+时间范围+指标/fund name+time range+indicator"}` 如/e.g. `"方正富邦策略精选A(010072)在近一月收益率"` |
| `get_fund_ownership` | 基金份额与持有人 / Fund shares & holders | `{"query": "基金名称+日期+指标/fund name+date+indicator"}` 如/e.g. `"湘财长弘灵活配置混合A(010076)在2025-06-30的申购总份额和赎回总份额"` |
| `get_fund_portfolio` | 基金持仓明细 / Fund holdings detail | `{"query": "基金名称+日期+指标/fund name+date+indicator"}` 如/e.g. `"工银优质成长混合A(010088)在2025-06-30披露报告中的股票投资占比"` |
| `get_fund_financials` | 基金财务指标 / Fund financial indicators | `{"query": "基金名称+日期+指标/fund name+date+indicator"}` 如/e.g. `"泰康浩泽混合A(010081)在2025-06-30的利润"` |
| `get_fund_company_info` | 基金公司信息 / Fund company info | `{"query": "基金名称+所属基金公司维度指标/fund name+fund company dimension indicator"}` 如/e.g. `"蜂巢丰瑞的所属基金公司基金经理数量"` |

---

## 宏观经济/行业经济指标服务 / Macro/Industry Economic Indicator Service (server_type="edb")

- 宏观行业经济指标支持"先搜索再取数"，当你不明确具体指标时，可以先发起搜索请求，再结合用户需求选择具体指标查询
- Macro/industry indicators support "search first, then query". When unsure of specific indicator, search first then select based on user needs

| 工具名称 / Tool | 功能说明 / Description | 典型参数 / Example Params |
|:---------|---------|---------|
| `search_edb` | 指标搜索 / Indicator search | `{"query": "行业/产品/指标描述/industry/product/indicator description"}` 如/e.g. `"光模块产业链相关指标"` |
| `get_edb_data` | 指标数据查询 / Indicator data query | `{"query": "指标名称+时间范围/indicator name+time range"}` 如/e.g. `"光伏电池产量202301-202506"` |

### EDB查询示例 / EDB Query Example

```python
# 搜索可能的指标 / Search possible indicators
call("edb", "search_edb", {"query": "新能源汽车产量相关指标"})

# 获取具体数据 / Get specific data
call("edb", "get_edb_data", {"query": "新能源汽车产量当月值（202301-202506）"})
```

---

## 新闻公告服务 / News & Announcement Service (server_type="news")

- 新闻公告服务内置语义检索能力，支持输入需要查询的内容，返回相关段落，而非公告全文
- News/announcement service has built-in semantic search, returning relevant paragraphs not full texts
- 热点事件查询工具注重时效性，参数限制不宜过多，否则容易无结果
- Trending events query focuses on timeliness; too many parameter restrictions may result in no results
- query 字段支持同时输入报告元数据要求及查询内容
- Query field supports both report metadata and search content

| 工具名称 / Tool | 功能说明 / Description | 典型参数 / Example Params |
|:---------|---------|---------|
| `search_news` | 新闻资讯语义检索 / News semantic search | `{"query": "内容/content", "time_start": "开始日期/start date", "time_end": "结束日期/end date", "size": 数量/count}` |
| `search_notice` | 公告语义检索 / Announcement semantic search | `{"query": "内容/content", "time_start": "开始日期/start date", "time_end": "结束日期/end date", "size": 数量/count}` |
| `search_trending_news` | 热点事件资讯查询 / Trending event query | `{"keyword": "关键词/keyword", "industry_name": "行业/industry", "time_scope": "时效范围/time scope", "size": 数量/count}` |

### 新闻查询示例 / News Query Examples

```python
# 财经新闻 / Financial news
call("news", "search_news", {
    "query": "脑机接口技术最新进展",
    "time_start": "2025-01-01",
    "time_end": "2026-01-01",
    "size": 5
})

# 上市公司公告 / Listed company announcements
call("news", "search_notice", {
    "query": "光迅科技2024年度报告 光模块技术",
    "time_start": "2025-01-01",
    "time_end": "2026-01-01",
    "size": 5
})

# 热点事件 / Trending events
call("news", "search_trending_news", {
    "keyword": "智能体",
    "industry_name": "计算机",
    "time_scope": "24小时",
    "size": 5
})
```

---

## 使用示例 / Usage Examples

本skill提供两种调用方案，请根据您的环境选择（用户未指定且不明确python环境时，优先选择 Node.js 方案）：
This skill provides two invocation methods. Choose based on your environment (prefer Node.js when user doesn't specify and Python environment is unclear):

### 方案1：Node.js脚本调用方式 / Method 1: Node.js Script

```javascript
const { call, listTools } = require('./call-node.js');

async function main() {
    // 查询股票数据 / Query stock data
    const result1 = await call("stock", "search_stocks", { query: "电子行业市值排名前20的股票" });
    console.log(JSON.stringify(result1, null, 2));

    // 查询基金数据 / Query fund data
    const result2 = await call("fund", "search_funds", { query: "南方基金的新能源ETF" });
    console.log(JSON.stringify(result2, null, 2));

    // 查询宏观经济数据 / Query macroeconomic data
    const result3 = await call("edb", "get_edb_data", { query: "光伏电池产量当月值（202301-202506）" });
    console.log(JSON.stringify(result3, null, 2));

    // 查询新闻 / Query news
    const result4 = await call("news", "search_news", {
        query: "人工智能行业动态",
        time_start: "2025-01-01",
        time_end: "2026-01-01",
        size: 5
    });
    console.log(JSON.stringify(result4, null, 2));
}

main().catch(console.error);
```

### 方案2：Python脚本调用方式 / Method 2: Python Script

```python
from call import call, list_tools

# 查询股票数据 / Query stock data
result = call("stock", "search_stocks", {"query": "电子行业市值排名前20的股票"})
print(result)

# 查询基金数据 / Query fund data
result = call("fund", "search_funds", {"query": "南方基金的新能源ETF"})
print(result)

# 查询宏观经济数据 / Query macroeconomic data
result = call("edb", "get_edb_data", {"query": "光伏电池产量当月值（202301-202506）"})
print(result)

# 查询新闻 / Query news
result = call("news", "search_news", {
    "query": "人工智能行业动态",
    "time_start": "2025-01-01",
    "time_end": "2026-01-01",
    "size": 5
})
print(result)
```

**Node.js方案特点 / Node.js Solution Features：**
- 无需安装额外依赖库，使用Node.js内置的 `http`/`https` 模块
  - No extra dependencies, uses Node.js built-in `http`/`https` modules
- 异步函数设计，支持 `async/await` 语法
  - Async function design with `async/await` syntax
- 与Python方案使用相同的配置文件 `mcp_config.json`
  - Uses same `mcp_config.json` as Python solution

---

## 注意事项 / Notes

1. 配置文件 `mcp_config.json` 需要包含有效的 `auth_token`（两个方案共用）
   - `mcp_config.json` requires a valid `auth_token` (shared by both solutions)
2. 请求地址已经内置在请求脚本 `call.py` 和 `call-node.js` 内部，无需重新配置
   - Request URLs are built into scripts, no need to reconfigure
3. 所有函数返回结果需检查 `ok` 字段确认请求是否成功
   - Always check `ok` field in response to confirm request success
4. 时间参数格式 / Time parameter format：`YYYY-MM-DD`
5. `search_edb` 可用于不确定具体指标名称时的模糊搜索
   - `search_edb` can be used for fuzzy search when exact indicator name is unknown
6. 如无Python环境，可使用Node.js方案（`call-node.js`），无需安装任何依赖
   - If no Python environment, use Node.js solution (`call-node.js`), no dependencies needed
7. 单次请求完成后，请帮助用户清除你临时生成的取数脚本
   - After request completion, help user clean up temporary data-fetching scripts
