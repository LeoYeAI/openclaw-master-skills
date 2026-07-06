---
name: a-stock-orchestrator
description: A股投研指挥官 - 编排调度多个股票分析Skill，串联成完整投研流水线。支持四种模式：板块扫描、板块分析、个股深度分析、持仓体检。最终输出结构化投资简报并自动存档飞书。
---

# A股投研指挥官

编排调度 8 个子 Skill，串联成完整投研流水线。不自己抓数据，只做**调度 + 整合 + 输出**。

## 🎯 四种运行模式

### 模式一：板块扫描（"今天有什么机会？"）

**触发词**：今日机会、扫描市场、找机会、今天买什么、热点

**流程**：
```
Step 1 - 热点扫描
  调用 a-stock-trading-assistant（fetch_stock.py --hot-sectors）
  → 获取当日涨幅前列板块 + 资金流向

Step 2 - 龙头识别
  对 Top 3-5 热点板块，调用 a-stock-leader-identification
  → 每个板块锁定 1-2 只龙头候选

Step 3 - 基本面排雷
  对候选个股，调用 a-stock-fundamental-screening
  → 排除 ST、亏损、减持等风险标的

Step 4 - 量价验证
  对通过排雷的个股，调用 a-stock-volume-price
  → 确认走势真实性，排除诱多

Step 4.5 - 技术面快速扫描（Top 3 候选）
  对 Top 3 候选执行技术面综合分析（同模式三 Step 4.5，简化版）
  → 三方交叉验证技术面强度，排序

Step 5 - 深度分析（Top 2-3）
  默认：stock-research-engine
  辅助（如有 Token）：tradingagents-analysis
  → 输出完整研报

Step 6 - 汇总输出投资简报
```

### 模式二：板块分析（"帮我分析 XX 板块"）

**触发词**：分析XX板块、XX行业怎么样、板块摸底

**流程**：
```
Step 1 - 板块概况
  调用 akshare-stock 获取板块行情数据
    → stock_board_industry_name_em() 或 stock_board_concept_name_em()
  调用 a-stock-trading-assistant 获取板块实时数据

Step 2 - 热点新闻与资金流向
  调用 akshare-stock 获取板块资金流向数据
  用 web_search 搜索板块近期热点新闻（最近3天）
  → 整理板块驱动因素

Step 3 - 龙头识别
  调用 a-stock-leader-identification
  → 板块内找真龙 + 跟风股对比

Step 4 - 成分股扫描与排雷
  调用 akshare-stock 获取板块成分股列表
    → stock_board_industry_cons_em(symbol="板块名")
  调用 a-stock-fundamental-screening 对主要成分股排雷
  → 输出风险标的清单

Step 5 - 量价验证（Top 3）
  调用 a-stock-volume-price
  → 确认龙头走势

Step 6 - 深度分析（龙头股）
  默认：stock-research-engine
  辅助（如有 Token）：tradingagents-analysis

Step 7 - 输出板块分析报告
```

### 模式三：个股深度分析（"帮我看看 600519"）

**触发词**：分析XX、看看XX、XX怎么样、帮我看看这个票、股票代码

**流程**：
```
Step 1 - 实时行情
  调用 a-stock-trading-assistant（fetch_stock.py --code XXX）
  → 当前价、涨跌幅、成交量、技术指标

Step 2 - 历史数据
  调用 akshare-stock 获取 K 线 + 财务数据
  → 近30日K线、PE/PB/ROE等

Step 3 - 基本面排雷
  调用 a-stock-fundamental-screening
  → 排雷检查

Step 4 - 量价验证
  调用 a-stock-volume-price
  → 量价关系判断

Step 4.5 - 技术面综合分析（三方交叉验证）
  同时执行三个技术面分析方案，交叉验证：
  
  4.5a - 方案A: a-stock-kline-analyzer
    exec: python3 skills/a-stock-kline-analyzer/scripts/kline_analyzer.py --code XXX --days 60 --report
    → K线形态识别 + 量能分析 + 技术评分(0-100)
    → 提取：趋势判断、MACD信号、RSI信号、支撑位/压力位、综合建议
  
  4.5b - 方案B: stock-kline-analysis
    exec: python3 -c "
      from scripts.fetch_kline import fetch_all_timeframes
      from scripts.indicators import add_indicators
      d, w, m = fetch_all_timeframes('XXX')
      d = add_indicators(d)
      # 输出最后3日指标 + 多时间框架判断
    " (在 skills/stock-kline-analysis/ 目录下执行)
    → 多时间框架分析（日线+周线+月线）
    → 提取：均线排列、MACD/RSI/ATR 数值、布林带位置
    → 图表生成：
      exec: plot_kline(d, code='XXX', name='名称', out_path='/tmp/kline-XXX.png')
      上传飞书：feishu_doc_media insert（需先 wiki_space_node get 获取 obj_token）
      wiki node token → obj_token 转换示例：
        feishu_wiki_space_node(action="get", token="wiki_node_token")
        → obj_token, obj_type
        然后 feishu_doc_media(action="insert", doc_id=obj_token, file_path="/tmp/kline-XXX.png", type="image")
  
  4.5c - 方案C: stock-daily-analysis（AI增强）
    exec (在 skills/stock-daily-analysis/ 目录下执行):
      python3 -c "
      from scripts.data_fetcher import get_daily_data
      from scripts.trend_analyzer import analyze_stock
      from scripts.ai_analyzer import AIAnalyzer
      import json
      df = get_daily_data('XXX', 60)
      # 列名转换（tushare 中文列名 → trend_analyzer 英文列名）
      df = df.rename(columns={'日期':'date','开盘':'open','最高':'high','最低':'low','收盘':'close','成交量':'volume','成交额':'amount'})
      df = df[['date','open','high','low','close','volume']]
      tech = analyze_stock(df, 'XXX')
      tech_data = {
        'current_price': tech.current_price,
        'ma5': tech.ma5, 'ma10': tech.ma10, 'ma20': tech.ma20,
        'bias_ma5': tech.bias_ma5, 'bias_ma10': tech.bias_ma10,
        'trend_status': tech.trend_status.value,
        'macd_status': tech.macd_status.value,
        'macd_signal': str(tech.macd_signal),
        'rsi_status': tech.rsi_status.value,
        'rsi_signal': str(tech.rsi_signal),
        'volume_status': tech.volume_status.value,
        'volume_trend': str(tech.volume_trend),
        'signal_score': tech.signal_score,
        'buy_signal': tech.buy_signal.value,
        'signal_reasons': tech.signal_reasons,
        'risk_factors': tech.risk_factors,
      }
      config = json.load(open('config.json'))
      ai = AIAnalyzer(config['ai'])
      result = ai.analyze('XXX', '名称', tech_data)
      print(json.dumps(result, ensure_ascii=False, indent=2))
      "
    → LLM 趋势判断 + 买入信号评分
    → 提取：sentiment_score、trend_prediction、operation_advice、confidence_level
  
  4.5d - 三方交叉验证汇总
    对比三个方案的核心指标，判断一致性：
    - 趋势方向：三方是否一致（看多/看空/分歧）
    - MACD：金叉/死叉一致性
    - RSI：超买/超卖/中性
    - 综合评分：取均值或加权
    - 输出"技术面综合分析"章节（见输出模板）

Step 5 - 深度研报
  主力：stock-research-engine（按其分析框架执行完整6步）
  辅助（如有 Token）：tradingagents-analysis → 多智能体交叉验证

Step 5.5 - 多空辩论
  调用 stock-debate V2.1
  → 读取 skills/stock-debate/SKILL.md，按其7步流程执行
  → 数据采集：腾讯财经（直连）+ 东方财富（代理）+ AkShare
  → 代理：仅数据采集时按需启停（stock_start_proxy / stock_stop_proxy），采集完必须关闭
  → 输出多空辩论报告，写入飞书（节点：EhQ6w2F5yiC0DKkxlzlcEMvIn2f）

Step 6 - 输出个股投资简报
```

### 模式四：持仓体检（"看看我的持仓"）

**触发词**：持仓、我的股票、体检、盈亏

**流程**：
```
Step 1 - 持仓汇总
  调用 a-stock-portfolio-monitor（portfolio.py analyze）
  → 总盈亏、各股盈亏

Step 2 - 逐股体检
  对每只持仓股执行模式三的 Step 1-5
  → 止损止盈建议

Step 3 - 调仓建议
  综合所有持仓分析，输出：
  - 建议卖出（触及止损/基本面恶化）
  - 建议减仓（涨幅达标）
  - 建议持有（趋势完好）
  - 建议加仓（回调到位/基本面改善）

Step 4 - 输出持仓体检报告
```

---

## 📋 子 Skill 调度清单

| 子 Skill | 用途 | 调用方式 |
|----------|------|----------|
| akshare-stock | 历史数据/财务/板块/资金流向 | 读取 SKILL.md 获取 API 调用方法，用 exec 执行 Python |
| a-stock-trading-assistant | 实时行情/热点板块 | exec 执行 scripts/fetch_stock.py |
| stock-research-engine | 深度研报（主力） | 读取 SKILL.md + references/analysis-framework.md，按框架执行 |
| stock-debate | 多空辩论（V2.1） | 读取 SKILL.md，按7步流程执行，采集时按需启停代理 |
| tradingagents-analysis | 多智能体分析（辅助） | 需 TRADINGAGENTS_TOKEN，exec 调用 API |
| a-stock-fundamental-screening | 基本面排雷 | 读取 SKILL.md 获取筛选规则 |
| a-stock-leader-identification | 龙头股识别 | 读取 SKILL.md 获取识别规则 |
| a-stock-volume-price | 量价关系验证 | 读取 SKILL.md 获取验证规则 |
| **a-stock-kline-analyzer** | **技术面A：K线形态+评分** | exec scripts/kline_analyzer.py --code XXX --days 60 --report |
| **stock-kline-analysis** | **技术面B：多时间框架+图表** | exec Python import fetch_kline + indicators + chart |
| **stock-daily-analysis** | **技术面C：LLM趋势判断** | exec Python import data_fetcher + trend_analyzer + ai_analyzer |
| a-stock-portfolio-monitor | 持仓管理 | exec 执行 scripts/portfolio.py |

### 数据源分工

| 场景 | 主数据源 | 说明 |
|------|----------|------|
| 实时行情 | a-stock-trading-assistant | 东方财富/同花顺实时数据 |
| 历史 K 线 | akshare-stock | stock_zh_a_hist() |
| 财务指标 | akshare-stock | stock_financial_analysis_indicator() |
| 板块成分股 | akshare-stock | stock_board_industry_cons_em() |
| 资金流向 | akshare-stock | stock_individual_fund_flow() |

---

## 📤 输出规范

### 投资简报模板（每次分析必输出）

**文档结构**（2026-03-23 起）：
- 创建**三个独立文档**互相链接：
  1. 综合简报（主文档，含评级表格 + 核心结论 + 跟踪清单）
  2. 深度研报（stock-research-engine 输出，完整基本面分析）
  3. 多空辩论（stock-debate 输出，7 步辩论流程）
- 简报中放两个详细报告链接，实现快速导航

**写作原则**：
1. 专业术语必须配"人话解释"（如 MACD→"短期与中期趋势的差距"）
2. 先给结论，再给原因，最后给操作建议
3. 用类比和场景帮助理解（如"布林带=价格通道"）
4. 避免堆砌数字，突出重点
5. 风险用 emoji 标等级（🔴高 🟡中 🟢低）

```markdown
# 📋 [股票名称](代码) 综合简报

> 生成时间：YYYY-MM-DD HH:MM | 数据截至：YYYY-MM-DD

## 🎯 一句话结论
[看多/看空/中性 + 理由，不超过30字]

## 💰 当前行情
| 项目 | 数值 | 什么意思 |
|------|------|----------|
| 最新价 | XX.XX | - |
| 今日涨幅 | +X.XX% | 涨了多少 |
| 成交额 | XX亿 | 交投是否活跃 |

## 📈 技术面分析（三家一起看，更靠谱）

### 三家观点对比
| 问题 | A方案(看K线) | B方案(多周期) | C方案(AI) | 一致吗？ |
|------|-------|-------|-------|------|
| 什么趋势？ | ... | ... | ... | ✅/⚠️/❌ |
| 动能如何？ | ... | ... | ... | ✅/⚠️/❌ |
| 买还是卖？ | ... | ... | ... | ✅/⚠️/❌ |

### 用人话解释
[每个方案用1-2段大白话总结核心观点]
[附带详细报告链接]

### 综合判断
[三方一致性分析 + 核心结论]

## 🛡️ 风险提示
| 风险等级 | 风险 | 说明 |
|----------|------|------|
| 🔴/🟡/🟢 | ... | ... |

## 💡 操作建议
| 项目 | 建议 | 说明 |
|------|------|------|
| 怎么做 | 买入/观望/卖出 | ... |
| 入场价 | XX元 | ... |
| 止损位 | XX元 | ... |
| 目标位 | XX元 | ... |
| 仓位 | XX% | ... |

**一句话操作指南**：[不超过40字的可执行建议]

## 📎 详细报告链接
- [方案A - K线形态分析](飞书链接)
- [方案B - 多时间框架分析](飞书链接)
- [方案C - AI趋势分析](飞书链接)

### 基本面
- ROE: XX%
- 营收增速: XX%
- ...

### 技术面综合分析（三方交叉验证）

#### 指标汇总
| 指标 | A方案(K线形态) | B方案(多时间框架) | C方案(AI趋势) | 共识 |
|------|-------|-------|-------|------|
| 趋势 | 多头/空头/震荡 | 日线/周线方向 | AI预测 | ✅/⚠️/❌ |
| MACD | 金叉/死叉 | 数值+方向 | - | ✅/⚠️ |
| RSI | 数值+区域 | 数值+区域 | - | ✅/⚠️ |
| 技术评分 | X分 | - | 情绪分X | 综合 |
| 买入信号 | 有/无 | - | 买入/观望/卖出 | ✅/⚠️ |

#### A方案要点（a-stock-kline-analyzer）
- 均线排列：MA5/MA10/MA20 排列状态
- MACD：DIF/DEA 数值及信号
- RSI：数值及区域判断
- 布林带：当前价格在布林带中的位置
- K线形态：锤子线/十字星/吞没等
- 量能分析：量比、换手率、量价关系
- 支撑位/压力位

#### B方案要点（stock-kline-analysis）
- 日线/周线/月线多时间框架共振
- ATR 波动率
- 布林带宽度

#### C方案要点（stock-daily-analysis AI分析）
- 趋势预测：上涨/下跌/震荡
- 操作建议：买入/持有/观望/卖出
- 置信度：高/中/低
- AI 核心判断

#### 综合判断
[三方一致性分析 + 核心结论]

## ⚠️ 免责声明
```markdown
## 🏭 板块概况
- 板块名称 / 概念
- 板块涨跌幅 / 资金净流入
- 近期热点新闻（3条以内）

## 🏆 龙头股
| 排名 | 股票 | 代码 | 涨幅 | 理由 |
|------|------|------|------|------|

## ⛔ 风险标的（排雷结果）
| 股票 | 代码 | 风险类型 | 原因 |
|------|------|----------|------|
```

### 持仓体检报告额外包含
```markdown
## 💼 持仓汇总
| 股票 | 成本 | 现价 | 盈亏 | 盈亏% |
|------|------|------|------|-------|
| **总计** | | | **+XX元** | **+X.X%** |

## 🔄 调仓建议
| 操作 | 股票 | 理由 |
|------|------|------|
```

---

## 📁 飞书存档

每次分析完成后，自动创建飞书文档存档。

- **父节点**: `EhQ6w2F5yiC0DKkxlzlcEMvIn2f`（投研分析笔记）
- **文档命名规则**:
  - 个股分析: `[日期] 个股分析 - 股票名称(代码)`
  - 板块扫描: `[日期] 每日板块扫描`
  - 板块分析: `[日期] 板块分析 - 板块名称`
  - 持仓体检: `[日期] 持仓体检`
- **工具**: 使用 feishu_create_doc 创建，将投资简报 Markdown 作为内容
- **Wiki 空间**: https://vicyrpffceo.feishu.cn/wiki/EhQ6w2F5yiC0DKkxlzlcEMvIn2f

---

## ⚙️ 依赖与配置

### 必需
- Python 3.10+
- tushare (`pip install tushare`)

### 数据源配置
Tushare Pro 作为主数据源（支持海外访问），Token 轮换配置在 `config/tushare-tokens.json`。

```python
import tushare as ts
ts.set_token("从 config/tushare-tokens.json 读取")
pro = ts.pro_api()

# 日K线
pro.daily(ts_code='002460.SZ', start_date='20260101', end_date='20260322')
# 财务指标（需2000积分）
pro.fina_indicator(ts_code='002460.SZ')
# 资金流向（需5000积分）
pro.moneyflow(ts_code='002460.SZ')
# 板块成分股
pro.ths_member(ts_code='885756.TI')
# 每日行情
pro.daily(trade_date='20260322')
```

备用数据源：a-stock-trading-assistant（腾讯财经，用于实时行情补充）

### 可选
- TRADINGAGENTS_TOKEN: 多智能体分析功能
  - 格式: `ta-sk-*`
  - 获取: https://app.510168.xyz → Settings → API Tokens
  - 未配置时自动跳过，不影响主流程

### 环境变量
```bash
# 可选，多智能体分析
export TRADINGAGENTS_TOKEN="ta-sk-xxx"

# 可选，自托管后端
# export TRADINGAGENTS_API_URL="https://your-server:8000"
```

---

## 🔧 技术面分析集成（V1.0）

### 版本信息
- **版本**: V1.0
- **发布日期**: 2026-03-22
- **端到端测试**: 赣锋锂业(002460) ✅

### 技术面三方交叉验证

| 方案 | Skill | 核心能力 | 数据源 | 执行耗时 |
|------|-------|----------|--------|----------|
| A | a-stock-kline-analyzer | K线形态+量能+技术评分(-5~+5) | baostock | ~10s |
| B | stock-kline-analysis | 多时间框架+可视化图表 | tushare | ~8s |
| C | stock-daily-analysis | LLM趋势判断+情绪评分(0~100) | tushare+GLM | ~15s |

### 依赖配置
- **baostock**: `pip install baostock`（方案A）
- **tushare**: `pip install tushare`（方案B/C），token 在 `config/tushare-tokens.json`
- **GLM API**: `config/stock-daily-analysis/config.json`（方案C）
- **中文字体**: `apt install fonts-wqy-zenhei`（方案B图表）
- **matplotlib**: `pip install matplotlib`（方案B图表）

### 飞书图表上传流程
```
1. 生成图表 → /tmp/kline-{code}.png
2. feishu_create_doc 创建文档 → 获取 doc_id
3. 如果文档在 Wiki 中：
   feishu_wiki_space_node(action="get", token="wiki_node_token") → obj_token
4. feishu_doc_media(action="insert", doc_id=obj_token, file_path="/tmp/...", type="image")
```

### 已知限制
1. 方案A实时行情（新浪API）海外不可用，使用 baostock K线数据替代
2. 方案C仅支持A股（港股/美股需额外适配）
3. 方案C筹码分布功能暂不可用（tushare 无此接口）
4. 三方案并行执行总耗时 ~20-30 秒

---

## ⚠️ 免责声明

- 所有分析仅供个人研究参考，不构成投资建议
- 数据来源于公开市场信息，可能存在延迟
- 投资有风险，入市需谨慎
- 最终决策权在用户手中
