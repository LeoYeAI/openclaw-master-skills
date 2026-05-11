---
name: ifind-data
description: |
  同花顺 iFinD (51ifind.com) 金融数据查询。支持 A 股/基金/债券/期货/指数的实时行情、历史行情、财务指标、宏观经济数据等 18 个 API 接口。
  Chinese financial data query skill powered by THS iFinD (51ifind.com) API. Covers real-time quotes, historical data, financial indicators, macro economics, fund valuation, and more across 18 API endpoints for A-shares, funds, bonds, futures, and indices.
metadata:
  author: sinabs
  version: "1.0.0"
  openclaw:
    requires:
      env:
        - IFIND_REFRESH_TOKEN
---

# iFinD 金融数据查询 Skill

## Overview

| # | API | URL 路径 | 用途 |
|---|-----|----------|------|
| 1 | 基础数据 | `basic_data_service` | 财务指标、基本面数据 |
| 2 | 日期序列 | `date_sequence` | 按时间序列获取指标数据 |
| 3 | 历史行情 | `cmd_history_quotation` | 日K/周K等历史行情 |
| 4 | 高频序列 | `high_frequency` | 分钟级高频数据+技术指标 |
| 5 | 实时行情 | `real_time_quotation` | 最新价、涨跌幅、成交量 |
| 6 | 日内快照 | `snap_shot` | 逐笔/分钟级日内盘口快照 |
| 7 | 经济数据库 | `edb_service` | 宏观经济指标(GDP、CPI等) |
| 8 | 专题报表 | `data_pool` | REITs、龙虎榜等专题数据 |
| 9 | 组合管理 | `portfolio_manage` | 组合新建/导入/交易/监控 |
| 10 | 智能选股 | `smart_stock_picking` | 按条件筛选股票 |
| 11 | 基金估值(分钟) | `fund_valuation` | 基金实时分钟级估值 |
| 12 | 基金估值(日) | `final_fund_valuation` | 基金日终估值 |
| 13 | 日期查询 | `get_trade_dates` | 查询交易日历 |
| 14 | 日期偏移 | `get_trade_dates` | 基于基准日前推后推 |
| 15 | 数据量查询 | `get_data_volume` | 查询账号已用数据量 |
| 16 | 错误信息查询 | `get_error_message` | 查询错误码含义 |
| 17 | 代码转换 | `get_thscode` | 证券代码转同花顺代码 |
| 18 | 公告查询 | `report_query` | 上市公司公告检索下载 |

## 首次使用检查（AI Agent 必读）

**每次调用 API 前，必须先检查 `IFIND_REFRESH_TOKEN` 是否已配置：**

```bash
grep -q 'IFIND_REFRESH_TOKEN=.' ~/.openclaw/skills/ifind-data/.env 2>/dev/null && echo "ok" || echo "missing"
```

如果返回 `missing`，**停止执行**，向用户提示：

> 使用 iFinD 金融数据查询需要你的 refresh_token。获取方式：
> - **还没有账号**：访问 https://ft.10jqka.com.cn 申请 iFinD 量化数据终端
> - **已有账号**：打开 iFinD 超级命令客户端 → 工具 → refresh_token 查询；或登录 https://quantapi.51ifind.com 在账号信息中查看
>
> 请把你的 refresh_token 发给我，我帮你配置好。

用户回复 token 后，**静默写入配置，不要展示命令**：
```bash
sed -i 's/^IFIND_REFRESH_TOKEN=.*/IFIND_REFRESH_TOKEN=用户提供的token/' ~/.openclaw/skills/ifind-data/.env
```
写入后告诉用户「已配置好，正在为你查询...」，然后继续执行 API 调用。

## SkillPay 计费规则（AI Agent 必读）

1. **永远不要让用户去 skillpay.me 注册** — 用户不需要注册
2. **余额不足时，直接把 payment_url 发给用户** — 告诉他们点击链接用 USDT 充值
3. **user_id 由脚本自动生成** — 不要问用户要
4. **查余额是免费的** — 只有实际执行 API 查询时才扣费（0.0001 USDT/次）
5. 用户充值后余额自动到账，可继续使用

## 试用期提示（AI Agent 必读）

脚本 stderr 中如果出现 `[TRIAL]` 开头的行，说明用户处于免费试用期。**每次**看到此标记时，在回复数据结果之后，必须附加如下提示：

> ---
> 🎁 您正在免费试用中，剩余 {trial_remaining_days} 天。试用期结束后按 0.0001 USDT/次计费（约 ¥0.0007/次），充值 1 USDT 可使用约 10000 次查询。

从 `[TRIAL]` 后的 JSON 中提取 `trial_remaining_days` 填入。**不要省略这个提示，每次试用期调用都要显示。**

## 调用方式

所有 API 通过 `scripts/ifind-api` 二进制调用：

```bash
./scripts/ifind-api "<api_endpoint>" '<json_body>'
```

- `api_endpoint`: 下方各 API 的路径名（如 `real_time_quotation`）
- `json_body`: JSON 格式的请求参数

二进制自动处理：user_id 生成 → 计费验证 → iFinD Token 获取 → API 请求 → 返回结果。

**日志排查**：出问题时查看 `.data/ifind.log`，每次请求记录 endpoint、状态、耗时等信息，日志超过 1MB 自动轮转。

---

## API 1: 基础数据

**Endpoint**: `basic_data_service`

**参数**:

| key | 必须 | 说明 | 示例 |
|-----|------|------|------|
| codes | 是 | 逗号分隔的证券代码 | `"300033.SZ,600030.SH"` |
| indipara | 是 | 指标及参数数组 | 见下方 |

**indipara 格式**:
```json
[{
  "indicator": "ths_roe_stock",
  "indiparams": ["20241231"]
}]
```

**示例**:
```json
{
  "codes": "300033.SZ,600030.SH",
  "indipara": [{
    "indicator": "ths_roe_stock",
    "indiparams": ["20241231"]
  }, {
    "indicator": "ths_roe_avg_by_ths_stock",
    "indiparams": ["20241231"]
  }]
}
```

> 指标名过多，推荐使用超级命令生成。常用：`ths_roe_stock`(ROE)、`ths_eps_stock`(EPS)、`ths_pe_stock`(PE)等。

---

## API 2: 日期序列

**Endpoint**: `date_sequence`

**参数**:

| key | 必须 | 说明 | 示例 |
|-----|------|------|------|
| codes | 是 | 逗号分隔的证券代码 | `"300033.SZ,600030.SH"` |
| startdate | 是 | 开始日期 | `"2023-01-01"` |
| enddate | 是 | 结束日期 | `"2024-12-31"` |
| indipara | 是 | 指标及参数数组 | 同基础数据格式 |
| functionpara | 否 | 附加参数 | 见下方 |

**functionpara 选项**:

| 名称 | key | 可选值 | 默认 |
|------|-----|--------|------|
| 时间周期 | Interval | D/W/M/Q/S/Y | D |
| 日期类型 | Days | Tradedays/Alldays | Tradedays |
| 非交易间隔 | Fill | Previous/Blank | Previous |

**示例**:
```json
{
  "codes": "300033.SZ,600030.SH",
  "startdate": "20230101",
  "enddate": "20241231",
  "functionpara": {"Days": "Alldays", "Fill": "Blank", "Interval": "Y"},
  "indipara": [{
    "indicator": "ths_total_equity_atoopc_stock",
    "indiparams": ["", "100"]
  }]
}
```

---

## API 3: 历史行情

**Endpoint**: `cmd_history_quotation`

**参数**:

| key | 必须 | 说明 | 示例 |
|-----|------|------|------|
| codes | 是 | 逗号分隔的证券代码 | `"300033.SZ,600030.SH"` |
| indicators | 是 | 逗号分隔的指标 | `"open,close,volume"` |
| startdate | 是 | 开始日期 | `"2024-01-01"` |
| enddate | 是 | 结束日期 | `"2025-01-01"` |
| functionpara | 否 | 附加参数 | 见下方 |

**常用 indicators**: `preClose`(前收盘价), `open`(开盘价), `high`(最高价), `low`(最低价), `close`(收盘价), `avgPrice`(均价), `change`(涨跌), `changeRatio`(涨跌幅), `volume`(成交量), `amount`(成交额), `turnoverRatio`(换手率), `pe_ttm`(市盈率TTM), `pe`(PE), `pb`(PB), `ps`(PS), `pcf`(PCF)

基金专用: `netAssetValue`(单位净值), `adjustedNAV`(复权单位净值), `accumulatedNAV`(累计单位净值)

**functionpara 选项**:

| 名称 | key | 可选值 | 默认 |
|------|-----|--------|------|
| 时间周期 | Interval | D/W/M/Q/S/Y | D |
| 复权方式 | CPS | 1-不复权 2-前复权 3-后复权 | 1 |
| 非交易间隔 | Fill | Previous/Blank/数值/Omit | Previous |
| 货币 | Currency | MHB(美元)/GHB(港元)/RMB/YSHB(原始) | YSHB |

**示例**:
```json
{
  "codes": "300033.SZ,600030.SH",
  "indicators": "open,close,volume",
  "startdate": "2024-08-25",
  "enddate": "2025-08-25",
  "functionpara": {"Interval": "W", "CPS": "3", "Currency": "RMB", "Fill": "Blank"}
}
```

---

## API 4: 高频序列

**Endpoint**: `high_frequency`

**参数**:

| key | 必须 | 说明 | 示例 |
|-----|------|------|------|
| codes | 是 | 逗号分隔的证券代码 | `"300033.SZ"` |
| indicators | 是 | 逗号分隔的指标 | `"open,high,low,close"` |
| starttime | 是 | 开始时间 | `"2024-01-01 09:15:00"` |
| endtime | 是 | 结束时间 | `"2024-01-01 15:15:00"` |
| functionpara | 否 | 附加参数 | 见下方 |

**常用 indicators**: `open`, `high`, `low`, `close`, `avgPrice`, `volume`, `amount`, `change`, `changeRatio`, `turnoverRatio`, `sellVolume`(内盘), `buyVolume`(外盘)

技术指标: `MA`, `MACD`, `KDJ`, `RSI`, `BOLL`, `CCI`, `OBV`, `ATR` 等（需在 functionpara.calculate 中配置参数）

资金流向: `large_amt_timeline`(主力净流入), `active_buy_large_volume`(主动买入特大单量) 等

**functionpara 选项**:

| 名称 | key | 可选值 | 默认 |
|------|-----|--------|------|
| 时间周期 | Interval | 1/3/5/10/15/30/60(分钟) | 1 |
| 非交易间隔 | Fill | Previous/Blank/数值/Original | Original |
| 复权方式 | CPS | no/forward3/backward1 等 | no |
| 技术指标参数 | calculate | 各指标对应参数 | - |

**技术指标 calculate 示例**:
```json
{
  "Interval": "1",
  "calculate": {
    "MACD": "12,26,9,MACD",
    "KDJ": "9,3,3,K"
  }
}
```

---

## API 5: 实时行情

**Endpoint**: `real_time_quotation`

**参数**:

| key | 必须 | 说明 | 示例 |
|-----|------|------|------|
| codes | 是 | 逗号分隔的证券代码 | `"300033.SZ,600000.SH"` |
| indicators | 是 | 逗号分隔的指标 | `"open,high,low,latest"` |

**常用 indicators**:

通用: `tradeDate`, `tradeTime`, `preClose`, `open`, `high`, `low`, `latest`(最新价), `change`, `changeRatio`, `amount`, `volume`, `turnoverRatio`

股票: `totalCapital`(总市值), `mv`(流通市值), `pe_ttm`, `pb`, `vol_ratio`(量比), `committee`(委比), `swing`(振幅), `bid1`~`bid10`(买价), `ask1`~`ask10`(卖价), `bidSize1`~`bidSize10`, `askSize1`~`askSize10`

资金流向: `mainNetInflow`(主力净流入), `largeNetInflow`(超大单净流入), `bigNetInflow`(大单净流入)

**示例**:
```json
{
  "codes": "300033.SZ,600000.SH",
  "indicators": "open,high,low,latest,changeRatio,volume,amount"
}
```

---

## API 6: 日内快照

**Endpoint**: `snap_shot`

**参数**:

| key | 必须 | 说明 | 示例 |
|-----|------|------|------|
| codes | 是 | 逗号分隔的证券代码 | `"300033.SZ"` |
| indicators | 是 | 逗号分隔的指标 | `"open,high,low,latest"` |
| starttime | 是 | 开始时间(同一天) | `"2025-01-06 09:30:00"` |
| endtime | 是 | 结束时间(同一天) | `"2025-01-06 15:00:00"` |

> 注意：起始和结束日期必须是同一天。

**常用 indicators**: `tradeDate`, `tradeTime`, `preClose`, `open`, `high`, `low`, `latest`, `amt`(成交额), `vol`(成交量), `amount`(累计成交额), `volume`(累计成交量), `bid1`~`bid10`, `ask1`~`ask10`, `bidSize1`~`bidSize10`, `askSize1`~`askSize10`

---

## API 7: 经济数据库 (EDB)

**Endpoint**: `edb_service`

**参数**:

| key | 必须 | 说明 | 示例 |
|-----|------|------|------|
| indicators | 是 | 逗号分隔的EDB指标代码 | `"M001620326,M002822183"` |
| startdate | 是 | 开始日期 | `"2018-01-01"` |
| enddate | 是 | 结束日期 | `"2024-12-31"` |
| functionpara | 否 | 更新时间筛选 | 见下方 |

> EDB 指标代码需通过超级命令查询，如 GDP、CPI、PMI 等宏观指标。

**示例**:
```json
{
  "indicators": "M001620326,M002822183",
  "startdate": "2018-01-01",
  "enddate": "2024-12-31"
}
```

---

## API 8: 专题报表

**Endpoint**: `data_pool`

**参数**:

| key | 必须 | 说明 | 示例 |
|-----|------|------|------|
| reportname | 是 | 报表编码 | `"p03341"` |
| functionpara | 是 | 报表参数 | 见示例 |
| outputpara | 是 | 输出字段控制 | `"p03341_f001:Y,p03341_f002:Y"` |

> 报表编码需通过超级命令查看。

**示例**:
```json
{
  "reportname": "p03341",
  "functionpara": {
    "sdate": "20210421",
    "edate": "20241231",
    "xmzt": "全部",
    "jcsslx": "全部",
    "jys": "全部"
  },
  "outputpara": "p03341_f001:Y,p03341_f002:Y"
}
```

---

## API 9: 组合管理

**Endpoint**: `portfolio_manage`

支持多个子功能，通过 `func` 字段区分：

### 9.1 组合新建 (`func: "newportf"`)

```json
{
  "func": "newportf",
  "name": "策略组合",
  "group": 11580,
  "performbm": {"code": "000300.SH", "name": "沪深300"},
  "tday": "国内交易所",
  "currency": "CNY"
}
```

### 9.2 模板导入 (`func: "importf"`)

```json
{
  "func": "importf",
  "portfid": 161390,
  "content": [
    ["交易日期","证券代码","业务类型","数量","价格","成交金额","费用","证券类型"],
    ["2020-03-30","CNY","现金存入","","",10000000,"",""],
    ["2020-04-01","600000.SH","买入",100,10.09,1009,5.225,"A股"]
  ]
}
```

### 9.3 现金存取 (`func: "cashacs"`)

```json
{
  "func": "cashacs",
  "portfid": 161390,
  "functionpara": {"acesscls": "101", "amount": "10000"}
}
```

> acesscls: 101=存入不计收益, 102=取出不计收益

### 9.4 普通交易 (`func: "deal"`)

```json
{
  "func": "deal",
  "portfid": 161390,
  "functionpara": {
    "thscode": "300033", "direct": "buy", "codeName": "同花顺",
    "marketCode": "212100", "securityType": "001001",
    "price": 78.7, "volume": 100, "currency": "CNY",
    "fee": "0", "feep": 0, "rate": "1.00"
  }
}
```

### 9.5 交易流水 (`func: "query_exchange_records"`)

```json
{
  "func": "query_exchange_records",
  "portfid": 161390,
  "indicators": "date,code,name,dealPrice,dealNumber,realPrice,businessName",
  "startdate": "2024-10-01",
  "enddate": "2024-10-07"
}
```

> 最大时间区间为 7 天。

### 9.6 组合监控 (`func: "query_overview"`)

```json
{
  "func": "query_overview",
  "portfid": 161390,
  "indicators": "category,thscode,stockName,newPrice,increase,increaseRate,number,marketValue,weight,floatProfit,floatProfitRate"
}
```

### 9.7 持仓分析 (`func: "query_positions"`)

```json
{
  "func": "query_positions",
  "portfid": 161390,
  "indicators": "categoryName,securityName,thsCode,weight,marketPrice,cost,wavepl,cumpl,price,increaseRate,amount,costPrice",
  "date": "2024-10-19",
  "functionpara": {"penetrate": "false"}
}
```

### 9.8 绩效指标 (`func: "query_perform"`)

```json
{
  "func": "query_perform",
  "portfid": 161390,
  "performbm": "000300",
  "startdate": "2020-06-02",
  "enddate": "2024-10-20",
  "functionpara": {"pfclass": "utnv", "cycle": "day"}
}
```

> pfclass: perform=业绩表现, nasset=净资产, utnv=组合净值

### 9.9 风险指标 (`func: "query_risk_profits"`)

```json
{
  "func": "query_risk_profits",
  "portfid": 161390,
  "indicators": ["alpha,yield,annual_yield,sharpe_ratio,max_drawdown,beta,annual_volatility"],
  "startdate": "2023-10-19",
  "enddate": "2024-10-19",
  "functionpara": {"cycle": "day", "benchmark": "000300"}
}
```

---

## API 10: 智能选股

**Endpoint**: `smart_stock_picking`

**参数**:

| key | 必须 | 说明 | 示例 |
|-----|------|------|------|
| searchstring | 是 | 搜索关键词 | `"个股热度"` |
| searchtype | 是 | 搜索类别 | `"stock"` |

**示例**:
```json
{
  "searchstring": "个股热度",
  "searchtype": "stock"
}
```

---

## API 11: 基金实时估值(分钟)

**Endpoint**: `fund_valuation`

**参数**:

| key | 必须 | 说明 | 示例 |
|-----|------|------|------|
| codes | 是 | 逗号分隔的基金代码 | `"000001.OF,000003.OF"` |
| functionpara | 是 | 参数 | 见下方 |
| outputpara | 是 | 输出字段 | `"changeRatioValuation:Y,realTimeValuation:Y"` |

**functionpara**:

| key | 说明 |
|-----|------|
| onlyLastest | 1=仅最新估值, 0=时间区间估值 |
| beginTime | 开始时间（onlyLastest=0 时需要） |
| endTime | 结束时间（onlyLastest=0 时需要） |

**示例**:
```json
{
  "codes": "000001.OF,000003.OF",
  "functionpara": {"onlyLastest": "1"},
  "outputpara": "changeRatioValuation:Y,realTimeValuation:Y,Deviation30TDays:Y"
}
```

---

## API 12: 基金实时估值(日)

**Endpoint**: `final_fund_valuation`

**参数**:

| key | 必须 | 说明 | 示例 |
|-----|------|------|------|
| codes | 是 | 分号分隔的基金代码 | `"000001.OF;000003.OF"` |
| functionpara | 是 | beginDate + endDate | 见下方 |
| outputpara | 是 | 输出字段 | `"finalValuation:Y,netAssetValue:Y,deviation:Y"` |

**示例**:
```json
{
  "codes": "000001.OF;000003.OF",
  "functionpara": {"beginDate": "2024-06-01", "endDate": "2024-12-31"},
  "outputpara": "finalValuation:Y,netAssetValue:Y,deviation:Y"
}
```

---

## API 13: 日期查询

**Endpoint**: `get_trade_dates`

**参数**:

| key | 必须 | 说明 | 示例 |
|-----|------|------|------|
| marketcode | 是 | 交易所代码 | `"212001"` |
| startdate | 是 | 开始日期 | `"2025-01-01"` |
| enddate | 是 | 结束日期 | `"2025-12-31"` |
| functionpara | 是 | 查询参数 | 见下方 |

**常用 marketcode**: `212001`(上交所), `212100`(深交所), `212200`(港交所)

**functionpara**:

| key | 说明 | 值 |
|-----|------|----|
| mode | 模式 | "1"=查询区间日期, "2"=查询日期数目 |
| dateType | 类型 | "0"=交易日, "1"=日历日 |
| period | 周期 | D/W/M/Q/S/Y |
| dateFormat | 格式 | "0"=YYYY-MM-DD, "1"=YYYY/MM/DD, "2"=YYYYMMDD |

**示例**:
```json
{
  "marketcode": "212001",
  "functionpara": {"mode": "1", "dateType": "0", "period": "D", "dateFormat": "0"},
  "startdate": "2025-01-01",
  "enddate": "2025-12-31"
}
```

---

## API 14: 日期偏移

**Endpoint**: `get_trade_dates`

**参数**:

| key | 必须 | 说明 | 示例 |
|-----|------|------|------|
| marketcode | 是 | 交易所代码 | `"212001"` |
| startdate | 是 | 基准日期 | `"2025-03-06"` |
| functionpara | 是 | 偏移参数 | 见下方 |

**functionpara**:

| key | 说明 | 值 |
|-----|------|----|
| dateType | 类型 | "0"=交易日, "1"=日历日 |
| period | 周期 | D/W/M/Q/S/Y |
| offset | 偏移 | "-5"=前推5, "5"=后推5 |
| dateFormat | 格式 | "0"/"1"/"2" |
| output | 输出 | "sequencedate"=所有日期, "singledate"=单个 |

**示例**:
```json
{
  "marketcode": "212001",
  "functionpara": {"dateType": "0", "period": "D", "offset": "-5", "dateFormat": "0", "output": "sequencedate"},
  "startdate": "2025-03-06"
}
```

---

## API 15: 数据量查询

**Endpoint**: `get_data_volume`

无需 JSON body，仅需 token 访问即可。

```bash
./scripts/ifind-api "get_data_volume" '{}'
```

---

## API 16: 错误信息查询

**Endpoint**: `get_error_message`

```json
{"errorcode": -1}
```

---

## API 17: 代码转换

**Endpoint**: `get_thscode`

**参数**:

| key | 必须 | 说明 | 示例 |
|-----|------|------|------|
| seccode | 是 | 行情代码 | `"300033"` |
| functionpara | 是 | 转换参数 | 见下方 |

**functionpara**:

| key | 说明 |
|-----|------|
| mode | seccode=按代码查, secname=按名称查 |
| sectype | 证券类型（空字符串=全部） |
| market | 市场代码（空字符串=全部） |
| tradestatus | 0=全部, 1=交易中, 2=已退市 |
| isexact | 0=模糊, 1=精确 |

**示例**:
```json
{
  "seccode": "300033",
  "functionpara": {"mode": "seccode", "sectype": "", "market": "", "tradestatus": "0", "isexact": "0"}
}
```

---

## API 18: 公告查询

**Endpoint**: `report_query`

**参数**:

| key | 必须 | 说明 | 示例 |
|-----|------|------|------|
| codes | 是 | 逗号分隔的证券代码 | `"300033.SZ,600000.SH"` |
| functionpara | 否 | 筛选参数 | 见下方 |
| outputpara | 是 | 输出字段 | 见下方 |

**functionpara 可选项**:

| key | 说明 |
|-----|------|
| reportType | 公告类型: 903=全部, 901=年报 等 |
| beginrDate | 公告开始日期 |
| endrDate | 公告截止日期 |
| keyWord | 标题关键词 |

**outputpara**: `"reportDate:Y,thscode:Y,secName:Y,ctime:Y,reportTitle:Y,pdfURL:Y,seq:Y"`

**示例**:
```json
{
  "codes": "300033.SZ,600000.SH",
  "functionpara": {"reportType": "901", "beginrDate": "2024-01-01", "endrDate": "2025-03-06"},
  "outputpara": "reportDate:Y,thscode:Y,secName:Y,ctime:Y,reportTitle:Y,pdfURL:Y,seq:Y"
}
```

> 返回的 pdfURL 可用于下载公告原文。

---

## 通用响应格式

所有 API 返回 JSON，通用字段：

| 字段 | 说明 |
|------|------|
| errorcode | 错误码，0=正常 |
| errmsg | 错误信息 |
| tables | 数据主体 |
| perf | 耗时(ms) |
| dataVol | 数据量消耗 |

---

## 常见错误码

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| -1010 | token 已失效 | 重新获取 access_token |
| -1302 | access_token 过期 | 脚本自动重试 |
| -1303 | 绑定IP超过20个 | 减少使用设备 |
| -4001 | 数据为空 | 检查代码/日期范围 |
| -4206 | 错误的同花顺代码 | 用代码转换API查正确代码 |
| -4304~4306 | 单次数据量超限 | 缩小时间范围或代码数量 |
| -4400 | 每分钟超过600次 | 降低请求频率 |

完整错误码请参考 `references/iFinD HTTP API 用户手册.txt`。

---

## SkillPay 计费说明

### 3 天免费试用
- 新用户首次调用自动开始 **3 天免费试用期**
- 试用期内无限制使用，不扣费
- 返回结果中包含 `trial: true` 和 `trial_remaining_days` 字段
- AI Agent 可提示用户："您正在试用期内，剩余 X 天免费使用"

### 试用期结束后
- 每次 API 调用扣费 **0.0001 USDT**
- 余额不足时脚本返回 JSON 包含 `payment_url` 字段
- **AI Agent 应将充值链接直接发送给用户**，告知"试用期已结束，点击链接用 USDT 充值即可继续使用"
- 用户无需注册任何账号，点击链接 → 连钱包 → 支付 USDT（BNB Chain）→ 余额自动到账
- 充值后可立即继续使用，无需等待
