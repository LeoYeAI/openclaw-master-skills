---
name: quant-trader-daily
description: |
  [中文] 量化交易员日常任务管理系统 - 专为股票交易员设计的每日工作流程管理工具。
  包含：开盘/收盘/日终汇报模板、实时持仓监控、风控提醒、交易日志记录。
  使用场景：(1) 管理每日交易任务时间表 (2) 生成汇报给上级的简报 (3) 监控持仓风险 (4) 记录交易日志 (5) 复盘分析
  
  [English] Quantitative Trader Daily Task Management System - A comprehensive daily workflow management tool designed for stock traders.
  Features: Opening/Closing/End-of-day report templates, real-time portfolio monitoring, risk control alerts, trading log recording.
  Use cases: (1) Manage daily trading schedules (2) Generate briefings for supervisors (3) Monitor portfolio risks (4) Record trading logs (5) Performance review
version: 1.0.0
author: Kimi Claw
tags:
  - quant-trading
  - daily-tasks
  - portfolio-management
  - risk-control
  - trading-report
---

# Quant Trader Daily | 量化交易员日常任务管理

> 📈 [EN] A comprehensive daily workflow management tool for stock traders
> 📈 [中文] 专为股票交易员设计的每日工作流程管理工具

---

## 🚀 Quick Start | 快速开始

### [EN] View Today's Task Schedule | [中文] 查看今日任务表
```bash
# Read daily task list
cat references/daily-schedule.md
```

### [EN] Generate Opening Report | [中文] 生成开盘简报
```bash
# Generate opening report template
python3 scripts/generate_report.py --type opening --portfolio config/portfolio.json
```

### [EN] Generate Closing Report | [中文] 生成收盘汇报
```bash
# Generate closing report template
python3 scripts/generate_report.py --type closing --portfolio config/portfolio.json
```

### [EN] Monitor Portfolio Risk | [中文] 监控持仓风险
```bash
# Check if positions trigger risk control lines
python3 scripts/risk_monitor.py --portfolio config/portfolio.json --threshold 8
```

---

## 📅 Daily Schedule | 每日任务时间表

### [EN] Pre-Market Preparation (07:00 - 09:30) | [中文] 盘前准备（07:00 - 09:30）

| Time | Task (EN) | Task (中文) | Description |
|:---:|:---|:---|:---|
| **07:00** | US Stocks + Commodities Morning Report | 美股板块+大宗商品早报 | Review overnight US stocks, gold, crude oil trends |
| **08:00** | Global Financial News | 全球财经资讯早报 | Caixin/ East Money/ Xueqiu hot stocks |
| **09:15** | Market + Portfolio Technical Analysis | 大盘+持仓形态分析 | Technical patterns of holdings |
| **09:25** | Today's Trading Strategy | 今日操盘策略 | Plan today's trades |
| **09:30** | A-Share Market Open | A股开盘 | Start real-time monitoring |

### [EN] Intraday Trading (09:30 - 15:00) | [中文] 盘中交易（09:30 - 15:00）

| Time | Task (EN) | Task (中文) | Description |
|:---:|:---|:---|:---|
| **09:35** | 📢 Opening Brief | 📢 开盘简报 | Report P&L and plans to supervisor |
| **10:00** | 1st Risk Control Check | 第一轮风控检查 | Check stop-loss/take-profit levels |
| **10:30** | Portfolio Review | 持仓复盘 | Morning position review |
| **Every 15min** | Real-time Portfolio Monitoring | A股持仓实时监控 | Continuous position tracking |
| **12:00** | Morning Review + PM Strategy | 早盘复盘+下午操盘策略 | Summarize morning, plan afternoon |
| **14:00** | 2nd Risk Control Check | 第二轮风控检查 | Check risk levels again |
| **14:30** | Closing Trading Strategy | 尾盘买卖策略 | Plan closing trades |
| **15:00** | Market Close | 收盘 | Confirm all trades |

### [EN] Post-Market Summary (15:00 - 18:00) | [中文] 盘后总结（15:00 - 18:00）

| Time | Task (EN) | Task (中文) | Description |
|:---:|:---|:---|:---|
| **15:05** | 📢 Closing Report | 📢 收盘汇报 | Report P&L to supervisor |
| **15:30** | Full-Day Trading Review | 全天操盘复盘 | Review day's operations |
| **17:30** | Screen Stocks for Tomorrow | 筛股选出明日候选股票 | Prepare tomorrow's watchlist |
| **18:00** | 📢 End-of-Day Summary | 📢 日终总结 | Send complete daily report |

### [EN] Evening Session (20:00 - 23:00) | [中文] 晚间时段（20:00 - 23:00）

| Time | Task (EN) | Task (中文) | Description |
|:---:|:---|:---|:---|
| **20:00** | Global Financial News Summary | 全球财经资讯总结 | Summarize daily global finance news |
| **23:00** | Full-Day Work Review | 全日工作复盘 | Review and prepare to rest |

---

## 🛠️ Command Quick Reference | 命令速查

| Command | Function (EN) | Function (中文) |
|:---|:---|:---|
| `generate_report --type opening` | Generate Opening Report | 生成开盘简报 |
| `generate_report --type closing` | Generate Closing Report | 生成收盘汇报 |
| `generate_report --type daily` | Generate Daily Summary | 生成日终总结 |
| `risk_monitor --threshold 8` | Monitor Risk Control Lines (default -8%) | 监控风控线（默认-8%）|
| `portfolio_status` | View Portfolio Overview | 查看持仓总览 |
| `trading_log --add` | Add Trading Record | 添加交易记录 |

---

## 📊 Report Templates | 汇报模板

### [EN] Opening Brief (09:35) | [中文] 开盘简报（09:35）

```markdown
## Opening Brief | 开盘简报 | YYYY-MM-DD

### Overnight Markets | 隔夜市场
- US Stocks: Nasdaq X% / Dow X% / S&P X%
- Gold: $X (X%)
- Crude Oil: $X (X%)

### Current Holdings | 当前持仓
| Stock | Position | Cost | Current | P&L |
|:---|:---:|:---:|:---:|:---:|
| Stock A | X shares | ¥X | ¥X | +X% |

### Today's Plan | 今日计划
- Watchlist: XXX
- Risk Actions: XXX
- Adjustment Plan: XXX
```

### [EN] Closing Report (15:05) | [中文] 收盘汇报（15:05）

```markdown
## Closing Report | 收盘汇报 | YYYY-MM-DD

### Daily P&L | 当日盈亏
- Total P&L: ¥X (X%)
- Portfolio Value: ¥X
- Available Cash: ¥X

### Trading Records | 交易记录
| Time | Action | Stock | Quantity | Price |
|:---|:---:|:---:|:---:|:---:|
| 09:35 | Buy | XXX | X shares | ¥X |

### Holdings Detail | 持仓明细
| Stock | Position | Cost | Current | P&L |
|:---|:---:|:---:|:---:|:---:|
| Stock A | X shares | ¥X | ¥X | +X% |
```

---

## ⚙️ Configuration Files | 配置文件

### [EN] Portfolio Config | [中文] 持仓配置 `config/portfolio.json`

```json
{
  "positions": [
    {
      "code": "002353",
      "name": "杰瑞股份",
      "quantity": 7400,
      "cost": 117.30,
      "stop_loss": -8,
      "take_profit": 5
    }
  ],
  "cash": 2307880.54,
  "total_assets": 5310139.54
}
```

### [EN] Risk Config | [中文] 风控配置 `config/risk.json`

```json
{
  "stop_loss_pct": -8,
  "take_profit_pct": 5,
  "max_single_position": 30,
  "alert_interval": 15
}
```

---

## 🔗 Detailed References | 详细参考

- **Daily Schedule**: [references/daily-schedule.md](references/daily-schedule.md)
- **Report Templates**: [references/report-templates.md](references/report-templates.md)
- **Risk Management**: [references/risk-management.md](references/risk-management.md)

---

*Version: 1.0.0*  
*Target Users: Stock Traders / Quant Trading Departments | 股票交易员 / 量化交易部*  
*Trading Days: Monday-Friday | 周一到周五*
