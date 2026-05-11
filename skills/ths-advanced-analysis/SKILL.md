---
name: ths-advanced-analysis
description: 基于 thsdk 进行高级股票分析：分钟K线（1m/5m/15m/30m/60m/120m）、板块/指数行情（主要指数/申万行业/概念板块成分股）、多股票批量对比（表格+归一化走势图+相关性热力图）、盘口深度、大单流向、集合竞价异动、日内分时、历史分时。当用户提到"分钟K线"、"日内走势"、"盘口"、"大单"、"竞价异动"、"板块行情"、"行业排名"、"概念板块"、"成分股"、"对比多只股票"、"批量分析"、"涨幅对比"、"相关性"，或者需要同时查看2只以上股票、关注短线交易、量化研究时，必须使用此skill。
---

# THS Advanced Analysis Skill

## 对话引导规范

### 澄清意图（意图模糊时必问）

用户输入往往不精确，调用前先判断意图，**不要猜测直接跑**。

| 用户说 | 可能的意图 | 必问 |
|--------|-----------|------|
| "帮我看看XX股票" | 实时行情？K线走势？大单？ | ✅ |
| "分析一下XX" | 技术面？资金面？和谁对比？ | ✅ |
| "XX板块怎么样" | 板块整体涨跌？成分股？领涨股？ | ✅ |
| "选一些好股票" | 短线？价值？哪个行业？条件？ | ✅ |
| "XX的5分钟K线" | 意图明确 | ❌ 直接执行 |
| "今日涨停股" | 意图明确 | ❌ 直接执行 |

**澄清话术示例：**

```
用户："帮我分析一下宁德时代"
Claude："好的，请问你主要想看哪个方向？
  1. 今日实时行情 + 资金流向
  2. 分钟K线（盘中走势）
  3. 近期日K线趋势
  4. 和比亚迪、亿纬锂能等对比
  5. 用问财筛选相关概念股"
```

### 调用后的后续提示（有延伸价值时才提）

不要每次都机械列出"还可以做XYZ"。只在以下情况自然地带出：

| 场景 | 合适的后续提示 |
|------|-------------|
| 展示了行业排名 | "需要查某个行业的成分股行情吗？" |
| 展示了分钟K线 | "需要同时看大单流向或盘口深度吗？" |
| 展示了多股对比表格 | "需要展示归一化走势图或相关性吗？" |
| 问财选出了候选股 | "需要对这些股票做K线技术验证吗？" |
| 展示了竞价异动 | "需要对某只异动股拉盘前分时看细节吗？" |

---

## 完整调用案例（直接可运行）

详见 `examples/` 目录，4个端到端场景：

| 文件 | 场景 |
|------|------|
| `examples/01_minute_kline.py` | 分钟K线 + 均线 + 成交量异动标注 |
| `examples/02_sector_industry.py` | 行业排名 + 概念板块成分股 + 指数行情 |
| `examples/03_multi_stock_compare.py` | 多股批量对比：表格 + 归一化走势 + 相关性 |
| `examples/04_bigorder_auction.py` | 大单流向 + 竞价异动扫描 + 分时/盘口 |
| `examples/05_wencai_nlp.py` | 问财NLP：选股/行情/财务/技术/复杂组合 + 与klines联用 |

---

## 场景速查

| 用户需求 | 使用方法 |
|---------|---------|
| 今日涨停/连板/竞价强势股 | `wencai_nlp("今日涨停，非ST")` |
| 财务指标选股（ROE/PE/PB）| `wencai_nlp("连续3年ROE大于15%，非ST")` |
| 技术形态选股（MACD金叉）| `wencai_nlp("均线多头排列，MACD金叉")` |
| 复杂组合条件选股 | `wencai_nlp("...多条件...")` 见案例5 |
| 宁德时代5分钟K线 | `klines(code, interval="5m", count=78)` |
| 茅台今日分时图 | `intraday_data(code)` |
| 历史某日分时 | `min_snapshot(code, date="20250101")` |
| 盘口买卖五档 | `depth(code)` 或 `tick_level1(code)` |
| 大单流向 | `big_order_flow(code)` |
| 今日竞价异动 | `call_auction_anomaly(market)` |
| 申万行业列表 | `ths_industry()` |
| 概念板块列表 | `ths_concept()` |
| 板块成分股 | `block_constituents(link_code)` |
| 指数行情 | `market_data_index(ths_code)` |
| 多股票对比 | 批量 `market_data_cn` + `klines` |
| 权息资料/除权 | `corporate_action(code)` |
| 今日IPO | `ipo_today()` |

---

## 第零步：安装

```bash
pip install --upgrade thsdk
```

> 包来源：[PyPI](https://pypi.org/project/thsdk/)

---

## 连接

所有调用统一使用游客模式，无需账户配置：

```python
from thsdk import THS

with THS() as ths:
    ...
```

---

## 第一步：股票代码解析

**所有中文名/缩写/短代码** 先用 `search_symbols` 获得完整 ths_code：

```python
with THS() as ths:
    resp = ths.search_symbols("宁德时代")
    # resp.data → [{'THSCODE': 'USZA300750', 'Name': '宁德时代', 'Code': '300750', 'MarketDisplay': '深A'}, ...]
```

**代码选择规则：**

| 情况 | 处理 |
|------|-----|
| 0条结果 | 告知用户未找到 |
| 1条结果 | 直接使用 |
| 多条结果，只有1只A股 | 自动选A股 |
| 多条结果，多只A股 | 展示列表，等用户选择 |

**指数用专用市场前缀（不需要 search_symbols）：**

| 指数 | THSCODE |
|------|---------|
| 上证指数 | `USHI000001` |
| 深证成指 | `USZI399001` |
| 创业板指 | `USZI399006` |
| 科创50 | `USHI000688` |
| 沪深300 | `USHI000300` |
| 中证500 | `USHI000905` |
| 上证50 | `USHI000016` |

> ⚠️ 指数前缀是 `USHI`/`USZI`（非 `USHA`/`USZA`），需调用 `market_data_index` 而非 `market_data_cn`

---

## 市场代码说明

| 前缀 | 含义 |
|------|------|
| `USHA` | 上海A股 |
| `USZA` | 深圳A股 |
| `USHI` | 上海指数 |
| `USZI` | 深圳指数 |
| `USTM` | 北交所 |
| `UHKG` | 港股 |

---

## K线数据

### interval 完整参数

`"1m"` / `"5m"` / `"15m"` / `"30m"` / `"60m"` / `"120m"` / `"day"` / `"week"` / `"month"` / `"quarter"` / `"year"`

> ⚠️ 正确写法是 `"5m"` 而非 `"5min"`

### 用法（count 与 start/end 二选一，不可混用）

```python
from datetime import datetime
from zoneinfo import ZoneInfo

tz = ZoneInfo('Asia/Shanghai')

with THS() as ths:
    # 方式1：按条数（最常用）
    resp = ths.klines("USZA300750", interval="5m", count=78)

    # 方式2：按时间范围
    resp = ths.klines(
        "USZA300750",
        interval="day",
        start_time=datetime(2025, 1, 1, tzinfo=tz),
        end_time=datetime(2025, 3, 1, tzinfo=tz)
    )

    # 复权：前复权 forward / 后复权 backward / 不复权 ""（默认）
    resp = ths.klines("USHA600519", interval="day", count=250, adjust="forward")

    df = resp.df  # 列: 时间, 开盘价, 最高价, 最低价, 收盘价, 成交量 等
    # 分钟K线的"时间"已自动转为 datetime；日K的"时间"为 datetime(YYYYMMDD)
```

### 分钟K线分析示例

```python
with THS() as ths:
    resp = ths.klines("USZA300750", interval="5m", count=78)
    df = resp.df
    df['ma5'] = df['收盘价'].rolling(5).mean()
    df['ma20'] = df['收盘价'].rolling(20).mean()
    # 成交量异动（超均量2倍）
    df['vol_avg'] = df['成交量'].rolling(20).mean()
    df['vol_spike'] = df['成交量'] > df['vol_avg'] * 2
    # 支撑/压力位
    support = df['最低价'].tail(20).min()
    resistance = df['最高价'].tail(20).max()
```

---

## 盘口与实时数据

### 日内分时（当日）

```python
with THS() as ths:
    resp = ths.intraday_data("USZA300750")
    df = resp.df  # 列: 时间(datetime), 价格, 成交量, 均价 等
```

### 历史分时（近一年内任意日期）

```python
with THS() as ths:
    resp = ths.min_snapshot("USZA300750", date="20250301")
    df = resp.df
```

### 买卖五档盘口

```python
with THS() as ths:
    resp = ths.depth("USZA300750")              # 单只
    resp = ths.depth(["USZA300750", "USHA600519"])  # 多只
    df = resp.df  # 含 买1~5价/量, 卖1~5价/量
```

### 3秒 Tick 数据

```python
with THS() as ths:
    resp = ths.tick_level1("USZA300750")
    df = resp.df
```

### 超级盘口（含十档委托）

```python
with THS() as ths:
    resp = ths.tick_super_level1("USZA300750")                      # 实时
    resp = ths.tick_super_level1("USZA300750", date="20250301")     # 历史（近一年）
    df = resp.df
```

---

## 大单与竞价

### 大单流向

```python
with THS() as ths:
    resp = ths.big_order_flow("USZA300750")
    df = resp.df
    # 含字段：主动买入特大单量/金额/笔数、主动卖出特大单量/金额/笔数、
    #         主动买入大单量/金额/笔数、资金流入/流出 等
```

### 集合竞价异动（盘前9:15~9:25监控）

```python
with THS() as ths:
    resp = ths.call_auction_anomaly("USHA")   # 沪市
    resp = ths.call_auction_anomaly("USZA")   # 深市
    df = resp.df
    # 异动类型1 已自动映射中文：
    # 涨停试盘 / 跌停试盘 / 涨停撤单 / 竞价抢筹 / 竞价砸盘
    # 大幅高开 / 大幅低开 / 急速上涨 / 急速下跌
    # 买一剩余大 / 卖一剩余大 / 大买单试盘 / 大卖单试盘
```

### 早盘集合竞价快照

```python
with THS() as ths:
    resp = ths.call_auction("USZA300750")
    df = resp.df
```

---

## 板块与指数

### 行业板块列表

```python
with THS() as ths:
    resp = ths.ths_industry()   # 同花顺行业（含 URFI 前缀的 link_code）
    df = resp.df  # 含板块名称、代码(link_code)、涨幅、成交量、上涨/下跌家数 等
```

### 概念板块列表

```python
with THS() as ths:
    resp = ths.ths_concept()
    df = resp.df  # 含概念名称、link_code、涨幅、领涨股 等
```

### 板块成分股

```python
with THS() as ths:
    # 先获取行业/概念列表，找到 link_code（格式 URFIXXXXXX）
    industry_resp = ths.ths_industry()
    target_row = [r for r in industry_resp.data if '新能源' in str(r.get('名称', ''))][0]
    link_code = target_row.get('代码') or target_row.get('link_code')

    resp = ths.block_constituents(link_code)
    df = resp.df  # 含成分股代码、名称等
```

### 板块实时行情

```python
with THS() as ths:
    # query_key: "基础数据"（涨幅/成交/市值）或 "扩展"（涨速/主力净流入）
    resp = ths.market_data_block("URFI881273", "基础数据")
    df = resp.df
    # 含: 价格, 涨幅, 成交量, 板块总市值, 板块流通市值, 上涨家数, 下跌家数, 领涨股
```

### 指数实时行情

```python
with THS() as ths:
    # 单只
    resp = ths.market_data_index("USHI000001", "基础数据")
    # 多只（必须同市场：同为 USHI 或同为 USZI）
    resp = ths.market_data_index(["USHI000001", "USHI000300", "USHI000905"])
    df = resp.df  # 含: 价格, 涨幅, 涨跌, 成交量, 总金额, 最高价, 最低价

    # 扩展（含量比、振幅等）
    resp = ths.market_data_index("USHI000001", "扩展")
```

### market_data_cn 可用 query_key

| query_key | 含义 |
|-----------|------|
| `"基础数据"` | 价格、涨跌幅、成交量、金额、开高低、涨速、当前量 |
| `"基础数据2"` | 精简版 |
| `"基础数据3"` | 极简（价格、昨收、成交量） |
| `"扩展1"` | 涨幅、涨跌、换手率、量比、主力净流入、委比 |
| `"扩展2"` | 涨幅、换手率、总市值、流通市值、委比、流通市值 |
| `"汇总"` | 全量字段（基础+扩展合并，多股对比首选） |

> ⚠️ `market_data_cn` 要求同市场：沪A（USHA）和深A（USZA）不能在同一次调用里混合

---

## 多股票批量对比

### 完整流程

```python
import pandas as pd
from collections import defaultdict
from thsdk import THS

stock_names = ["贵州茅台", "五粮液", "泸州老窖"]

with THS() as ths:
    # Step 1: 批量解析代码
    stock_codes = []
    for name in stock_names:
        resp = ths.search_symbols(name)
        a_shares = [s for s in resp.data
                    if any(m in s.get('MarketDisplay', '') for m in ['沪A', '深A'])]
        if a_shares:
            stock_codes.append({'name': name, 'code': a_shares[0]['THSCODE']})

    # Step 2: 按市场分组（market_data_cn 要求同市场）
    by_market = defaultdict(list)
    for s in stock_codes:
        by_market[s['code'][:4]].append(s)

    # Step 3: 批量获取行情
    rows = []
    for market, stocks in by_market.items():
        codes = [s['code'] for s in stocks]
        resp = ths.market_data_cn(codes, "汇总")
        for i, row in enumerate(resp.data):
            row['股票名称'] = stocks[i]['name']
            rows.append(row)
    quote_df = pd.DataFrame(rows)

    # Step 4: 批量K线
    klines_data = {}
    for s in stock_codes:
        resp = ths.klines(s['code'], interval="day", count=30, adjust="forward")
        klines_data[s['name']] = resp.df

# Step 5: 归一化
for name, df in klines_data.items():
    df['归一化'] = df['收盘价'] / df['收盘价'].iloc[0] * 100

# Step 6: 相关性（量化场景）
returns = pd.DataFrame({
    name: df['收盘价'].pct_change()
    for name, df in klines_data.items()
})
corr_matrix = returns.corr()
```

### 输出规范（两步走）

**第一步：表格**（show_widget 渲染）

| 股票 | 最新价 | 涨幅% | 成交额 | 换手率 | 量比 | 主力净流入 | 总市值 |

**第二步：图表**（show_widget 渲染）
1. 归一化走势折线图（多线，颜色区分，起点=100）
2. 量化场景额外输出：相关性热力图

---

## 问财自然语言查询（wencai_nlp）

问财是同花顺旗下 AI 选股平台（iwencai.com），支持用自然语言做全市场扫描。
`wencai_nlp` 直接对接同一接口，多条件用**逗号/分号/空格**分隔。

```python
with THS() as ths:
    resp = ths.wencai_nlp("连续3日主力净流入，换手率大于5%，非ST")
    df = resp.df  # 每行一只股票，列为查询涉及的字段
```

> ⚠️ buffer_size 已设为 8MB，返回数据量大时无需手动调整

### 六大查询类型速查

**① 行情 & 盘面**
```python
"今日涨停，非ST"
"连续2日涨停，非一字板，非ST"
"今日涨停原因类别，涨停封单额，封单量"
"竞价涨幅大于3%，竞价量大于昨日成交量5%，非ST"
"主力净流入由大到小排名前20，非ST"
"近10日区间主力资金流向大于5000万，市值大于100亿，日成交额大于30亿"
```

**② 板块 & 行业**
```python
"今日申万行业涨跌幅排名"
"今日概念板块涨幅排名前20"
"人工智能概念股，今日涨跌幅，成交额，主力净流入"
"半导体行业股票，涨幅，换手率，市值"
"今日涨幅最大的5个概念板块，涨幅，成分股数量"
```

**③ 财务指标**
```python
"连续3年ROE大于15%，非ST，上市大于3年"
"净利润增长率大于30%，营业收入增长率大于20%，非ST"
"市盈率小于15，股息率大于3%，市净率小于2，非ST"
"市净率小于1，非ST，流通市值大于20亿"          # 破净股
"连续5年分红，股息率大于4%，资产负债率小于60%"
```

**④ 技术形态**
```python
"均线多头排列，MACD金叉，换手率大于3%，非ST"
"5日均线上穿20日均线，成交量放大，涨幅大于1%"
"均线粘合，平台突破，成交量大于5日均量1.5倍"
"仙人指路，非ST，非停牌"
"250日新高，非ST，沪深A，上市超过250天"
```

**⑤ 复杂组合（短线/量化）**
```python
# 短线强势选股
"均线多头排列，MACD金叉，DIFF上穿中轴，换手率大于1%且小于10%，30日内有2个交易日涨幅大于4%，非ST"

# 竞价选股（隔日打板）
"昨日非一字板涨停，今日竞价涨幅大于等于0%且小于等于9.9%，今日隔夜买单额小于10亿，非ST，非科创板"

# 连板选股
"最近5日有过涨停，最近5日没有跌停，今日成交量大于5日平均成交量，今日竞价涨幅在2%到3%之间，非北交所非科创板非ST"
```

**⑥ 信息查询（非选股）**
```python
"涨停原因归类前20"                       # 今日涨停题材分布
"今日龙虎榜"                             # 龙虎榜数据
"今日大宗交易"                           # 大宗交易
"今日融资融券余额最大的前20只股票"
"近一周北向资金净买入前20"
```

### wencai_nlp 返回数据处理

```python
with THS() as ths:
    resp = ths.wencai_nlp("连续3日主力净流入，换手率大于5%，非ST，市值大于30亿")
    if not resp:
        print(f"查询失败: {resp.error}")
    else:
        df = resp.df
        # 字段名来自查询语句，常见列：股票代码、股票简称、涨幅、成交额、主力净流入 等

        # 补全 ths_code（供后续调用 klines/market_data_cn）
        def to_ths_code(code_str):
            code_str = str(code_str).zfill(6)
            if code_str.startswith('6'):   return f"USHA{code_str}"
            if code_str.startswith(('0','3')): return f"USZA{code_str}"
            if code_str.startswith('8'):   return f"USTM{code_str}"
            return None

        df['ths_code'] = df.get('股票代码', df.get('代码', pd.Series())).apply(to_ths_code)
```

### wencai_nlp vs wencai_base

| 方法 | 用途 |
|------|------|
| `wencai_nlp(condition)` | **主要用法**。完整自然语言，返回股票列表+字段数据 |
| `wencai_base(condition)` | 简单条件查询，如 `"所属行业"` 查单只股票的归属 |

完整示例见 `examples/05_wencai_nlp.py`

---

## 其他实用 API

### 权息资料（除权除息历史）

```python
with THS() as ths:
    resp = ths.corporate_action("USHA600519")
    df = resp.df
```

### 今日IPO / 待申购

```python
with THS() as ths:
    resp = ths.ipo_today()   # 今日上市新股
    resp = ths.ipo_wait()    # 待申购打新
```

### 问财自然语言查询

```python
with THS() as ths:
    resp = ths.wencai_nlp("今日申万行业涨跌幅排名")
    resp = ths.wencai_nlp("今日概念板块涨跌幅排名前20")
    resp = ths.wencai_nlp("换手率大于10%且涨幅大于5%的股票")
    df_list = resp.data
```

---

## 错误处理

```python
with THS() as ths:
    resp = ths.klines("USZA300750", interval="5m", count=60)
    if not resp:                  # resp.success == False
        print(f"调用失败: {resp.error}")
    elif resp.df.empty:
        print("数据为空，可能是非交易时间")
    else:
        df = resp.df
```

**常见报错速查：**

| 错误信息 | 原因 | 解决 |
|---------|------|------|
| `"未登录"` | 未 connect | 确保使用 `with THS() as ths` |
| `"证券代码必须为10个字符"` | 代码格式错误 | 先过 `search_symbols` |
| `"一次性查询多支股票必须市场代码相同"` | 沪深混合 | 按市场分组分别查询 |
| `"无效的周期类型: 5min"` | interval 写法错 | 改为 `"5m"` |
| `"'count' 参数不能与 'start_time' 同时使用"` | 参数冲突 | 二选一 |

---

## 与 ths-financial-data 的分工

| 场景 | skill |
|------|-------|
| 单只A股行情/资金流向/日K | `ths-financial-data` |
| 分钟K线 / 盘中监控 | **本 skill** |
| 盘口深度 / 大单 / 竞价异动 | **本 skill** |
| 板块/指数行情及成分股 | **本 skill** |
| 多股票批量对比 | **本 skill** |
| 问财自然语言查询 | 两者均可 |
