# ArbiScan — 跨交易所加密货币扫描 & 监控

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**12 种扫描，覆盖 Binance、OKX、Bybit、Bitget。套利、监控、信号 — 全部公开 API，无需 key。**

ArbiScan 是一个 [OpenClaw Skill](https://clawhub.ai) 和独立 CLI 工具，扫描主流交易所的套利机会、市场异常和交易信号。覆盖 100 个交易对，4 个交易所。是否行动由你决定 — ArbiScan 只负责发现。

## 扫描类型

### 套利类（发现价格/费率差异）

| 类型 | 功能 | 数据源 |
|------|------|--------|
| **资金费率套利** | 比较各交易所永续合约资金费率差异 | 资金费率端点 |
| **期现基差套利** | 发现同交易所现货与合约价差 | 现货 + 合约价格 |
| **跨所现货价差** | 寻找不同交易所之间的 bid/ask 价差 | 订单簿最优报价 |
| **跨所合约价差** | 寻找不同交易所之间的合约价差 | 合约行情 |

### 监控类（跟踪市场状态）

| 类型 | 功能 | 数据源 |
|------|------|--------|
| **稳定币脱锚** | 监测 USDC/DAI/FDUSD/TUSD 偏离 $1 | 稳定币价格 |
| **持仓量监控** | 跟踪 OI 分布，标记某交易所集中度过高 | 持仓量端点 |
| **费率异常警报** | 费率超过 ±0.1%（正常值 10 倍）时告警 | 资金费率端点 |
| **24h 涨跌幅排行** | 最近 24 小时涨跌最大的币种 | 24h 行情 |
| **成交量异常** | 检测某交易所成交量异常集中或飙升 | 24h 成交量 |

### 信号类（识别交易信号）

| 类型 | 功能 | 数据源 |
|------|------|--------|
| **费率趋势** | 连续 ≥5 期同方向费率 = 稳定套利机会 | 历史费率 |
| **多空比** | 标记极端仓位（一方 >65%）| Binance + Bybit 多空比 |
| **新币上线检测** | A 所有 B 所没有的币 = 溢价窗口 | 各所交易对列表 |

## 快速开始

### 作为 OpenClaw Skill

从 ClawHub 安装，让 AI Agent 帮你扫描：

```
"扫描资金费率套利机会，APY 大于 10%"
"哪些币的费率现在很极端？"
"看看过去 24 小时涨跌最大的币"
"有没有稳定币在脱锚？"
"找出只在 Binance 上线但 OKX 没有的币"
```

### 独立运行（Python）

```bash
cd scripts/
pip install -r requirements.txt

# 运行所有扫描
python scanner.py --all

# 按分类运行
python scanner.py --type arbitrage      # 4 种套利扫描
python scanner.py --type monitor        # 5 种监控扫描
python scanner.py --type signals        # 3 种信号扫描

# 单独运行
python scanner.py --type funding --min-apy 10
python scanner.py --type price_movers
python scanner.py --type long_short
python scanner.py --type new_listing

# 输出格式
python scanner.py --type funding --format markdown
python scanner.py --type price_movers --format json
```

## 示例输出

```
  Funding Rate Arbitrage
================================================================================
Symbol     Long (低费率)         Short (高费率)        Rate Diff   Est. APY%   Risk    Window
---------  -------------------  --------------------  ----------  ----------  ------  --------
FILUSDT    Binance -0.0799%     Bitget -0.0104%       0.0695%     76.1%       HIGH    ~8h
SEIUSDT    Binance -0.0317%     OKX -0.0026%          0.0291%     31.9%       MEDIUM  ~8h
BTCUSDT    Binance -0.0027%     OKX 0.0064%           0.0091%     10.0%       LOW     ~8h
```

```
  24h Price Movers (Gainers & Losers)
================================================================================
Symbol     Exchange    Price        24h Change%    24h Volume (USDT)    Direction
---------  ----------  -----------  -------------  -------------------  ---------
ARBUSDT    Binance     $0.1017      -2.59%         $41,804,011          DUMP
SOLUSDT    OKX         $87.9300     -1.15%         $11,760,759          DUMP
SEIUSDT    Bybit       $0.0664      +0.54%         $15,798,499          PUMP
```

## 可组合使用

ArbiScan 设计为与交易所交易 Skill 配合使用：

1. **ArbiScan** 扫描发现机会和信号（本 Skill）
2. **Binance/Bybit/Bitget Skill** 执行交易（如果你决定行动）
3. **TradeOS** 可管理完整工作流

```
"用 ArbiScan 找机会，然后用 Binance skill 执行最优的那个"
```

## 设计理念："看和用分开"

ArbiScan **只扫描、不交易**：
- 零风险：不接触你的资金，不需要 API key
- 纯信息：发现机会后，执行交给你或交易所 Skill
- 可组合：和 Binance/Bybit/Bitget 的交易 Skill 配合使用

## 工作原理

- 仅使用**公开 API 端点** — 无需 API key，无需认证
- 内置限频（请求间隔 200ms），遵守交易所速率限制
- 覆盖市值 **Top 30 交易对**（可按需扩展）
- **12 种扫描**，分 3 大类（套利、监控、信号）
- 基于年化收益和币种类别的风险评分

## 支持的交易所

| 交易所 | 现货 | 合约 | 资金费率 | 持仓量 | 多空比 |
|--------|------|------|----------|--------|--------|
| Binance | ✅  | ✅   | ✅       | ✅     | ✅     |
| Bybit   | ✅  | ✅   | ✅       | ✅     | ✅     |
| OKX     | ✅  | ✅   | ✅       | ✅     | —      |
| Bitget  | ✅  | ✅   | ✅       | ✅     | —      |

## 免责声明

ArbiScan 仅供信息参考，不构成投资建议。显示的机会是理论值，实际执行需考虑：

- Gas/提币手续费
- 交易所之间的转账时间
- 滑点和流动性
- 交易所对手风险
- 合规要求

请自行研究后再做决策。

## 开源协议

MIT
