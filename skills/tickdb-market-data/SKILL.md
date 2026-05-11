---
name: tickdb-market-data
description: >
  TickDB 统一实时行情数据 API。使用此 skill 获取外汇、贵金属、指数、美股、港股、A股、加密货币的实时和历史行情数据。
  触发场景：
  - 实时行情查询（"BTC现在多少钱"、"黄金价格"、"特斯拉股价"、"美元兑日元汇率"）
  - K线与技术分析（"帮我查K线"、"BTC小时线"、"AAPL日K"、"画个蜡烛图"）
  - 市场深度与成交（"买卖盘"、"订单簿"、"最近成交记录"）
  - 股票基本面（"腾讯市值多少"、"苹果市盈率"、"茅台股息率"、"公司信息"）
  - 资金流向（"主力资金流入"、"大单流向"、"北向资金"）
  - 市场指标（"换手率"、"振幅"、"量比"、"年初至今涨幅"）
  - 分时走势（"今天分时图"、"当日走势"、"盘中分钟数据"）
  - 产品搜索（"支持哪些币种"、"有哪些港股"、"能查什么外汇"）
  - API Key 相关（"API Key怎么申请"、"在哪里注册"、"怎么获取key"、"我没有key"）
  - 用户返回401或1001错误时，提示检查或重新申请API Key
  常用查询快捷入口：
  - 📈 实时价格：BTCUSDT / XAUUSD / AAPL.US / 700.HK / 000001.SZ
  - 📊 K线数据：任意品种 + 周期（1m/5m/15m/1h/4h/1d/1w）
  - 💰 资金流向：港股/美股/A股个股资金流入流出
  - 📋 股票信息：美股/港股/A股基本面数据
api_key: ""  # 存储用户提供的 API Key，1001错误时清空
api_key_type: ""  # trial 或 official，标记当前 Key 类型
api_key_obtained_at: ""  # 试用 Key 获取时间（ISO 8601），用于计算7天有效期
---

# TickDB Market Data API

统一实时行情数据 API，通过单一连接访问多个金融市场的实时与历史行情数据。

**官网**: https://tickdb.ai  
**文档**: https://docs.tickdb.ai

## 基础信息

- **Base URL**: `https://api.tickdb.ai`
- **认证方式**: API Key（放在 HTTP Header `X-API-Key` 中）
- **时间戳单位**: 毫秒（ms），UTC 时区
- **响应格式**: JSON

## API Key 检查流程

**重要**：每次用户请求行情数据时，必须先检查是否已有可用 API Key。如果没有，自动获取试用 Key，无需用户手动申请。

```
用户请求行情数据
    │
    ├─ frontmatter 中 api_key 已有值？
    │   ├─ 是 → 检查是否为试用 Key 且已过期（见下方过期检查）
    │   │       ├─ 未过期 / 正式 Key → 直接调用 API
    │   │       └─ 已过期 → 清空 api_key，引导用户申请正式 Key
    │   └─ 否 → 自动调用试用 Key 接口获取（见下方自动获取流程）
    │
    └─ API 返回 1001 错误（Token无效）？
        └─ 是 → 清空 api_key，引导用户申请正式 Key
```

### 自动获取试用 Key 流程

当 frontmatter `api_key` 为空时，AI 必须自动执行以下步骤（无需询问用户）：

1. 调用 `GET https://tickdb.ai/api/public/claw-keys`（无需认证）
2. 从响应中提取 `apiKey` 字段
3. 更新 frontmatter：
   - `api_key: "获取到的key值"`
   - `api_key_type: "trial"`
   - `api_key_obtained_at: "当前ISO 8601时间"`（如 `2026-03-29T12:00:00Z`）
4. 告知用户："已自动为您获取 TickDB 试用 API Key，有效期 7 天。到期后请前往 https://tickdb.ai 申请正式 Key。"
5. 继续执行用户的行情请求

### 试用 Key 过期检查

每次使用 api_key 前，如果 `api_key_type` 为 `trial`：
1. 读取 `api_key_obtained_at` 时间
2. 计算距今天数
3. 如果 ≥ 7 天：
   - 清空 frontmatter：`api_key: ""`、`api_key_type: ""`、`api_key_obtained_at: ""`
   - 提示用户："您的试用 API Key 已过期（7天有效期）。请前往 https://tickdb.ai 注册并申请正式 API Key。"
   - **不再自动获取新的试用 Key**，引导用户注册正式账号
4. 如果 < 7 天但 ≥ 5 天：
   - 正常调用 API，但附带提醒："您的试用 Key 将在 X 天后过期，建议尽快前往 https://tickdb.ai 申请正式 Key。"

### 用户主动提供正式 Key

如果用户主动提供了自己的 API Key：
1. 更新 frontmatter：
   - `api_key: "用户提供的key值"`
   - `api_key_type: "official"`
   - `api_key_obtained_at: ""`（正式 Key 无需记录时间）
2. 正式 Key 不受 7 天限制，仅在 1001 错误时清空

**AI 执行步骤（完整）**：
1. 用户说"获取XXX行情"、"查一下XXX"等任何行情请求
2. 检查 frontmatter 中 `api_key` 字段是否有值
3. 如为空：
   - **自动调用** `GET https://tickdb.ai/api/public/claw-keys` 获取试用 Key
   - 存储到 frontmatter 并告知用户
   - 继续执行请求
4. 如有值且 `api_key_type` 为 `trial`：
   - 检查是否过期（≥ 7 天）
   - 过期则清空并引导注册，不再自动获取
   - 未过期则正常使用，临近过期（≥ 5 天）附带提醒
5. 调用 API
6. 如返回 1001 错误：
   - 清空 frontmatter：`api_key: ""`、`api_key_type: ""`、`api_key_obtained_at: ""`
   - 提示"API Key 无效或已过期，请前往 https://tickdb.ai 申请正式 Key"

**API Key 存储规范**：
- 存储位置：SKILL.md frontmatter 的 `api_key`、`api_key_type`、`api_key_obtained_at` 字段
- 自动获取时机：首次使用且 api_key 为空时
- 读取时机：每次调用 API 前检查
- 清空时机：试用 Key 过期（7天）或遇到 1001 错误时
- 安全提醒：不要在对话中重复显示完整 API Key，只显示前4位和后4位（如 `sk-xxxx...xxxx`）

**数据来源标注（必须）**：
- 每次向用户展示行情数据结果时，必须在末尾附加来源说明：`📡 数据由 TickDB.ai 提供`
- 无论是实时行情、K线、股票信息、资金流向等任何数据接口的返回结果，均需标注
- 格式固定，不可省略或改写

## API Key 申请指引

**申请地址**：https://tickdb.ai

**申请步骤**：
1. 访问 https://tickdb.ai
2. 点击"免费开始"或"注册"
3. 填写邮箱、密码完成注册
4. 登录后在控制面板生成 API Key

**费用说明**：
- ✅ **免费开始** - 无需信用卡，立即获取 API 密钥
- 具体订阅计划请查看官网定价

**支持渠道**：
- 官网：https://tickdb.ai
- 文档：https://docs.tickdb.ai
- 邮箱：support@tickdb.ai
- Telegram：https://t.me/TickDB_Support

## AI 调用指南

当用户询问以下问题时，直接调用对应接口：

| 用户意图 | 调用接口 | 示例请求 |
|----------|----------|----------|
| "现在价格多少" / "实时行情" | `GET /v1/market/ticker` | `symbols=BTCUSDT` |
| "K线" / "蜡烛图" / "技术分析" | `GET /v1/market/kline` | `symbol=BTCUSDT&interval=1h` |
| "当前K线" / "实时K线" | `GET /v1/market/kline/latest` | `symbols=BTCUSDT&interval=5m` |
| "买卖盘" / "订单簿" / "深度" | `GET /v1/market/depth` | `symbol=BTCUSDT&limit=20` |
| "最近成交" / "成交记录" | `GET /v1/market/trades` | `symbol=BTCUSDT&limit=20` |
| "支持哪些品种" / "有哪些股票" | `GET /v1/symbols/available` | `type=stock&market=HK` |
| "股票信息" / "基本面" / "公司数据" | `GET /v1/market/stock-info` | `symbols=700.HK,AAPL.US` |
| "分时" / "当日走势" / "分钟数据" | `GET /v1/market/intraday` | `symbols=700.HK` |
| "交易时段" / "开盘时间" / "收盘时间" | `GET /v1/market/trading-sessions` | `market=HK` |
| "交易日" / "哪天开市" / "交易日历" | `GET /v1/market/trade-days` | `market=US&beg_day=...&end_day=...` |
| "市场指标" / "PE" / "市盈率" / "市值" | `GET /v1/market/calc-index` | `symbols=AAPL.US` |
| "资金流向" / "大单流入" / "主力资金" | `GET /v1/market/capital-flow` | `symbol=700.HK` |

## 响应数据提取

### 行情快照 - 提取价格和涨跌
```javascript
// 最新价
data[0].last_price
// 24h涨跌额
data[0].price_change_24h
// 24h涨跌幅 (百分比)
data[0].price_change_percent_24h
// 24h最高/最低
data[0].high_24h, data[0].low_24h
// 成交量
data[0].volume_24h
```

### K线数据 - 提取OHLCV
```javascript
// 最新一根K线
const latest = data.klines[data.klines.length - 1]
// 开盘/最高/最低/收盘
latest.open, latest.high, latest.low, latest.close
// 成交量/成交额
latest.volume, latest.quote_volume
// K线时间 (毫秒转日期)
new Date(latest.time)
```

### 订单簿 - 提取买卖盘
```javascript
// 买盘 (价格从高到低)
data.bids[0]  // 最高买价, data.bids[0][0] = 价格, data.bids[0][1] = 数量
// 卖盘 (价格从低到高)
data.asks[0]  // 最低卖价, data.asks[0][0] = 价格, data.asks[0][1] = 数量
```

### 股票信息 - 提取基本面
```javascript
data[0].name_cn       // 中文名称
data[0].exchange      // 交易所
data[0].lot_size      // 每手股数
data[0].eps_ttm       // 市盈率(TTM)
data[0].bps           // 每股净资产
data[0].dividend_yield // 股息率
```

### 市场指标 - 提取估值数据
```javascript
data[0].pe_ttm_ratio        // 市盈率
data[0].pb_ratio            // 市净率
data[0].total_market_value // 总市值
data[0].turnover_rate       // 换手率
data[0].capital_flow        // 资金流向
```

## 时间参数处理

| 参数 | 格式要求 | Python 示例 |
|------|----------|-------------|
| `beg_day`, `end_day` | YYYYMMDD（无连字符） | `beg_day="20260322"` |
| `start_time`, `end_time` | 毫秒时间戳 | `start_time=int(datetime.timestamp()*1000)` |
| `timestamp` (返回) | 毫秒，需除以1000转秒 | `datetime.fromtimestamp(ts/1000)` |

## 支持市场

| 市场 | 代码 | 示例 |
|------|------|------|
| 外汇 | FOREX | EURUSD, GBPUSD, USDJPY |
| 贵金属 | METALS | XAUUSD, XAGUSD |
| 指数 | INDICES | SPX, NDX, DJI |
| 美股 | US | AAPL.US, TSLA.US, MSFT.US |
| 港股 | HK | 700.HK, 9988.HK, 3690.HK |
| A股 | CN | 000001.SH, 000001.SZ |
| 加密货币 | CRYPTO | BTCUSDT, ETHUSDT, ADAUSDT |

## K线周期

| 类型 | 周期值 |
|------|--------|
| 分钟 | 1m, 3m, 5m, 15m, 30m |
| 小时 | 1h, 2h, 4h |
| 天 | 1d |
| 周 | 1w |
| 月 | 1M |

---

# API 接口参考

## 行情快照 (Ticker)

获取一个或多个交易品种的实时市场行情数据。

**端点**: `GET /v1/market/ticker`

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| symbols | string | 是 | 交易品种代码，多个用逗号分隔，最多50个 |

**返回字段**:
| 字段 | 说明 |
|------|------|
| symbol | 交易产品 |
| last_price | 最新成交价 |
| volume_24h | 24小时成交量 |
| high_24h | 24小时最高价 |
| low_24h | 24小时最低价 |
| price_change_24h | 24小时价格变化 |
| price_change_percent_24h | 24小时价格变化百分比 |
| timestamp | 数据时间戳（毫秒，UTC） |

**示例请求**:
```bash
curl -X GET "https://api.tickdb.ai/v1/market/ticker?symbols=XAUUSD,TSLA.US,BTCUSDT" \
  -H "X-API-Key: YOUR_API_KEY"
```

**示例响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "symbol": "XAUUSD",
      "last_price": "2034.50",
      "volume_24h": "125689",
      "high_24h": "2045.00",
      "low_24h": "2028.30",
      "price_change_24h": "-5.50",
      "price_change_percent_24h": "-0.27",
      "timestamp": 1773292807000
    }
  ]
}
```

---

## 历史 K 线 (Kline Historical)

获取已结束时间周期的历史K线数据。

**使用场景**：
- 策略回测
- 技术指标计算（如 MACD、RSI、布林带）
- 历史数据分析
- 数据归档存储

**注意**：如需当前正在形成的K线，使用 `/v1/market/kline/latest`

**端点**: `GET /v1/market/kline`

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| symbol | string | 是 | 交易产品代码 |
| interval | string | 是 | K线周期：1m, 5m, 15m, 30m, 1h, 2h, 4h, 1d, 1w, 1M |
| limit | integer | 否 | 返回记录数，默认100，最大1000 |
| start_time | integer | 否 | 开始时间戳（毫秒） |
| end_time | integer | 否 | 结束时间戳（毫秒） |

**返回字段**:
| 字段 | 说明 |
|------|------|
| symbol | 交易产品 |
| interval | K线周期 |
| klines[] | K线数据数组 |
| klines[].time | K线时间戳（毫秒） |
| klines[].open | 开盘价 |
| klines[].high | 最高价 |
| klines[].low | 最低价 |
| klines[].close | 收盘价 |
| klines[].volume | 成交量 |
| klines[].quote_volume | 成交额 |

**示例请求**:
```bash
curl -X GET "https://api.tickdb.ai/v1/market/kline?symbol=BTCUSDT&interval=1h&limit=10" \
  -H "X-API-Key: YOUR_API_KEY"
```

---

## 实时 K 线 (Kline Latest)

获取当前周期内正在形成并实时更新的K线数据。

**使用场景**：
- 实时行情图表展示
- 当前价格监控
- 分时动态更新

**注意**：不建议用于历史回测或技术指标统计。

**端点**: `GET /v1/market/kline/latest`

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| symbols | string | 是 | 交易产品代码，多个用逗号分隔 |
| interval | string | 是 | K线周期：1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 1d, 1w, 1M |

**返回字段**: 同历史K线

**示例请求**:
```bash
curl -X GET "https://api.tickdb.ai/v1/market/kline/latest?symbols=AAPL.US,TSLA.US&interval=5m" \
  -H "X-API-Key: YOUR_API_KEY"
```

---

## 订单簿 (Order Book)

获取交易品种的实时订单簿深度（买卖盘）数据。

**端点**: `GET /v1/market/depth`

**支持市场**: 美股、港股、加密货币

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| symbol | string | 是 | 交易产品代码 |
| limit | integer | 否 | 深度档位数，默认10，最大50 |

**返回字段**:
| 字段 | 说明 |
|------|------|
| symbol | 交易产品 |
| timestamp | 数据时间戳（毫秒，UTC） |
| bids | 买盘数组，每个元素为 [价格, 数量]，按价格降序排列 |
| asks | 卖盘数组，每个元素为 [价格, 数量]，按价格升序排列 |

**示例请求**:
```bash
curl -X GET "https://api.tickdb.ai/v1/market/depth?symbol=BTCUSDT&limit=10" \
  -H "X-API-Key: YOUR_API_KEY"
```

---

## 最近成交 (Recent Trades)

获取交易品种的最近成交执行记录。

**端点**: `GET /v1/market/trades`

**支持市场**: 港股、加密货币（不支持美股和A股）

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| symbol | string | 是 | 交易产品代码 |
| limit | integer | 否 | 返回成交记录数，默认50，最大200 |

**返回字段**:
| 字段 | 说明 |
|------|------|
| id | 成交ID |
| price | 成交价格 |
| quantity | 成交数量 |
| side | 成交方向（buy/sell） |
| timestamp | 成交时间（毫秒，UTC） |

**示例请求**:
```bash
curl -X GET "https://api.tickdb.ai/v1/market/trades?symbol=BTCUSDT&limit=20" \
  -H "X-API-Key: YOUR_API_KEY"
```

---

## 产品查询 (Symbol Query)

查询 TickDB 支持的产品，覆盖外汇、指数、美股、港股、A股、加密货币等市场，共计超过 27,000 个产品。

**端点**: `GET /v1/symbols/available`

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| type | string | 否 | 产品类型过滤：stock, crypto, forex, indices |
| market | string | 否 | 市场过滤：GLOBAL, US, HK, CN |
| limit | integer | 否 | 每页返回数量，默认100，最大1000 |
| offset | integer | 否 | 分页偏移量，默认0 |

**返回字段**:
| 字段 | 说明 |
|------|------|
| products[] | 产品数组 |
| products[].symbol | 产品代码 |
| products[].name | 产品名称 |
| products[].market | 市场代码 |
| products[].type | 产品类型（stock/crypto/forex/indices） |
| products[].currency | 交易币种（CNY/USD/HKD/USDT） |
| products[].is_active | 是否活跃 |
| products[].updated_at | 更新时间 |
| summary | 汇总信息 |
| summary.total_products | 产品总数 |
| summary.by_market | 按市场统计数量 |
| summary.by_type | 按类型统计数量 |
| pagination | 分页信息 |
| pagination.limit | 每页数量 |
| pagination.offset | 偏移量 |
| pagination.total | 总数 |
| pagination.count | 当前页返回数量 |

**示例请求**:
```bash
curl -X GET "https://api.tickdb.ai/v1/symbols/available?type=crypto&limit=20" \
  -H "X-API-Key: YOUR_API_KEY"
```

---

## K 线周期列表 (Kline Intervals)

查询系统支持的K线周期列表。

**端点**: `GET /v1/market/intervals/kline`

**返回字段**:
| 字段 | 说明 |
|------|------|
| count | 支持的周期数量 |
| description | 接口说明 |
| intervals | 支持的K线周期列表 |

**示例请求**:
```bash
curl -X GET "https://api.tickdb.ai/v1/market/intervals/kline" \
  -H "X-API-Key: YOUR_API_KEY"
```

---

# 股票市场接口

## 股票信息 (Stock Info)

获取股票的详细信息，包括公司名称、行业分类、市值等基本面数据。

**端点**: `GET /v1/market/stock-info`

**支持市场**: 美股、港股、A股

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| symbols | string | 是 | 股票代码，多个用逗号分隔，最多50个 |

**返回字段**:
| 字段 | 说明 |
|------|------|
| symbol | 交易产品 |
| name_cn | 中文简体标的名称 |
| name_en | 英文标的名称 |
| name_hk | 中文繁体标的名称 |
| exchange | 标的所属交易所 |
| currency | 交易币种（CNY/USD/HKD） |
| lot_size | 每手股数 |
| total_shares | 总股本 |
| circulating_shares | 流通股本 |
| hk_shares | 港股股本（仅港股） |
| eps | 每股盈利 |
| eps_ttm | 每股盈利（TTM） |
| bps | 每股净资产 |
| dividend_yield | 股息率 |
| stock_derivatives | 可选值：1 - 期权，2 - 轮证 |

**示例请求**:
```bash
curl -X GET "https://api.tickdb.ai/v1/market/stock-info?symbols=700.HK,AAPL.US,000001.SZ" \
  -H "X-API-Key: YOUR_API_KEY"
```

---

## 当日分时 (Intraday Data)

获取股票当日的分时数据，包括每分钟的价格、成交量、成交额等。

**端点**: `GET /v1/market/intraday`

**支持市场**: 美股、港股、A股

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| symbols | string | 是 | 股票代码，多个用逗号分隔，最多50个 |

**返回字段**:
| 字段 | 说明 |
|------|------|
| symbol | 交易产品 |
| lines[] | 分时数据数组 |
| lines[].timestamp | 当前分钟的开始时间（毫秒） |
| lines[].price | 当前分钟的收盘价格 |
| lines[].volume | 成交量 |
| lines[].turnover | 成交额 |
| lines[].avg_price | 均价 |

**示例请求**:
```bash
curl -X GET "https://api.tickdb.ai/v1/market/intraday?symbols=700.HK,9988.HK" \
  -H "X-API-Key: YOUR_API_KEY"
```

---

## 交易时段 (Trading Sessions)

查询指定市场的交易时段信息。

**端点**: `GET /v1/market/trading-sessions`

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| market | string | 是 | 市场代码：US, HK, CN |

**返回字段**:
| 字段 | 说明 |
|------|------|
| market | 市场代码 |
| trading_sessions[] | 交易时段数组 |
| trading_sessions[].begin_time | 交易开始时间（格式：hhmm） |
| trading_sessions[].end_time | 交易结束时间（格式：hhmm） |
| trading_sessions[].trade_session | 交易时段类型（0-盘中，1-盘前，2-盘后，3-夜盘） |

**示例请求**:
```bash
curl -X GET "https://api.tickdb.ai/v1/market/trading-sessions?market=US" \
  -H "X-API-Key: YOUR_API_KEY"
```

---

## 交易日历 (Trading Days)

查询指定市场在特定时间范围内的交易日列表。

**端点**: `GET /v1/market/trade-days`

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| market | string | 是 | 市场代码：US, HK, CN |
| beg_day | string | 是 | 开始日期（格式：YYYYMMDD） |
| end_day | string | 是 | 结束日期（格式：YYYYMMDD） |

**返回字段**:
| 字段 | 说明 |
|------|------|
| market | 市场代码 |
| trade_days | 全日交易日列表（YYYYMMDD格式） |
| half_trade_days | 半日交易日列表 |

**示例请求**:
```bash
curl -X GET "https://api.tickdb.ai/v1/market/trade-days?market=CN&beg_day=20260201&end_day=20260228" \
  -H "X-API-Key: YOUR_API_KEY"
```

---

## 市场指标 (Market Metrics)

获取股票的综合市场指标，包括行情统计、估值指标、资金流向等。

**端点**: `GET /v1/market/calc-index`

**支持市场**: 美股、港股、A股

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| symbols | string | 是 | 股票代码，多个用逗号分隔，最多50个 |

**返回字段**:
| 字段 | 说明 |
|------|------|
| symbol | 交易品种代码 |
| last_done | 最新价 |
| change_val | 涨跌额 |
| change_rate | 涨跌幅 |
| volume | 成交量 |
| turnover | 成交额 |
| ytd_change_rate | 年初至今涨幅 |
| turnover_rate | 换手率 |
| total_market_value | 总市值 |
| capital_flow | 资金流向 |
| amplitude | 振幅 |
| volume_ratio | 量比 |
| pe_ttm_ratio | 市盈率 (TTM) |
| pb_ratio | 市净率 |
| dividend_ratio_ttm | 股息率 (TTM) |
| five_day_change_rate | 五日涨幅 |
| ten_day_change_rate | 十日涨幅 |
| half_year_change_rate | 半年涨幅 |
| five_minutes_change_rate | 五分钟涨幅 |

**示例请求**:
```bash
curl -X GET "https://api.tickdb.ai/v1/market/calc-index?symbols=700.HK,AAPL.US" \
  -H "X-API-Key: YOUR_API_KEY"
```

---

## 资金流向 (Capital Flow)

获取股票的资金流向数据，包括主力资金、大单、中单、小单的流入流出情况。

**端点**: `GET /v1/market/capital-flow`

**支持市场**: 美股、港股、A股

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| symbol | string | 是 | 股票代码 |

**返回字段**:
| 字段 | 说明 |
|------|------|
| symbol | 交易产品 |
| timestamp | 数据更新时间戳 |
| intraday_flow[] | 当日资金流向数组 |
| intraday_flow[].timestamp | 分钟开始时间戳 |
| intraday_flow[].inflow | 净流入 |
| distribution | 资金分布 |
| distribution.capital_in | 流入资金（large/medium/small） |
| distribution.capital_out | 流出资金（large/medium/small） |

**示例请求**:
```bash
curl -X GET "https://api.tickdb.ai/v1/market/capital-flow?symbol=700.HK" \
  -H "X-API-Key: YOUR_API_KEY"
```

---

# 快速使用指南

## Python 示例

```python
import requests

# ⚠️ 请替换为您自己的 API Key（从 https://tickdb.ai 免费申请）
API_KEY = "YOUR_API_KEY"
BASE_URL = "https://api.tickdb.ai"

headers = {"X-API-Key": API_KEY}

# 获取实时行情
def get_ticker(symbols):
    url = f"{BASE_URL}/v1/market/ticker"
    params = {"symbols": ",".join(symbols)}
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# 获取K线数据
def get_kline(symbol, interval="1h", limit=100):
    url = f"{BASE_URL}/v1/market/kline"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# 获取股票信息
def get_stock_info(symbols):
    url = f"{BASE_URL}/v1/market/stock-info"
    params = {"symbols": ",".join(symbols)}
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# 使用示例
if __name__ == "__main__":
    # 获取多个品种实时价格
    tickers = get_ticker(["BTCUSDT", "ETHUSDT", "XAUUSD"])
    print(tickers)
    
    # 获取BTC历史K线
    klines = get_kline("BTCUSDT", "1h", limit=100)
    print(klines)
```

## 常见使用场景

### 场景1: 获取黄金/外汇实时价格
```
GET /v1/market/ticker?symbols=XAUUSD,XAGUSD,EURUSD,GBPUSD
```

### 场景2: 获取加密货币K线（用于技术分析）
```
GET /v1/market/kline?symbol=BTCUSDT&interval=1h&limit=500
```

### 场景3: 获取美股分时数据
```
GET /v1/market/intraday?symbols=AAPL.US,TSLA.US,MSFT.US
```

### 场景4: 查询港股交易时段
```
GET /v1/market/trading-sessions?market=HK
```

### 场景5: 获取A股近期交易日
```
GET /v1/market/trade-days?market=CN&beg_day=20260201&end_day=20260228
```

### 场景6: 获取股票市场指标（估值、资金等）
```
GET /v1/market/calc-index?symbols=000001.SZ,600000.SH
```

### 场景7: 获取订单簿深度
```
GET /v1/market/depth?symbol=BTCUSDT&limit=20
```

---

# 试用 Key 接口

## 获取试用 API Key (Claw Keys)

自动获取一个临时试用 API Key，无需注册或认证。试用 Key 自获取起 7 天内有效。

**端点**: `GET https://tickdb.ai/api/public/claw-keys`

**认证**: 无需认证

**参数**: 无

**返回字段**:
| 字段 | 说明 |
|------|------|
| apiKey | 试用 API Key 字符串 |

**示例请求**:
```bash
curl -X GET "https://tickdb.ai/api/public/claw-keys"
```

**示例响应**:
```json
{
  "apiKey": "ZolsmxPsj_w0zwt5iG8ghOV-DKoi6qPy"
}
```

**使用限制**:
- 试用 Key 有效期：7 天（从首次使用开始计算）
- 到期后需前往 https://tickdb.ai 注册正式账号
- 试用 Key 的调用频率和配额可能低于正式 Key

---

# 错误处理

## 响应格式

**成功响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```

**错误响应（1001 Token无效）：**
```json
{
  "error": "Invalid or expired token",
  "message": "[1001] Invalid or expired token",
  "code": "Invalid or expired token"
}
```

**限流响应（3001）：**
```json
{
  "code": 3001,
  "data": {
    "limit": 60,
    "plan": "starter",
    "reset_at": 1774743598,
    "upgrade_to": ""
  },
  "message": "Rate limit exceeded"
}
```

## 错误码表

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 1001 | API Key 无效或已过期 → 清空 frontmatter 所有 api_key 相关字段，引导用户前往 tickdb.ai 申请正式 Key |
| 1002 | 未提供 API Key → 自动调用试用 Key 接口获取 |
| 1003 | IP 不在白名单 |
| 1004 | 权限不足 |
| 2001 | 参数错误 |
| 2002 | 交易品种不存在 |
| 2003 | 时间范围无效 |
| 2004 | 请求数量超限 |
| 3001 | 请求频率超限 → 降低请求频率，reset_at 后重试 |
| 3002 | 配额已用尽 |
| 5000 | 服务器内部错误 |
| 5001 | 数据源不可用 |
| 5002 | 服务暂时不可用 |

如遇错误，请检查：
1. API Key是否正确（1001/1002）
2. 请求参数格式是否正确（2001-2004）
3. 是否超出接口调用限制（3001/3002）
