# CL LP Auto-Rebalancer

Uniswap V3 集中流动性自动调仓策略，运行在 EVM L2 链上，通过 OKX OnchainOS 执行 DeFi 操作。

**核心思路：用波动率决定范围宽度。** 低波动率收紧范围提高资本效率，高波动率放宽范围减少调仓和无常损失。结合趋势分析进行不对称调整——看涨时向上延伸范围，看跌时向下延伸。

## 特性

- **波动率自适应范围** — 基于 1H K 线 ATR 动态计算范围宽度
- **趋势不对称调整** — MTF 多时间框架分析，沿趋势方向偏移范围
- **完整调仓流水线** — claim fees → remove liquidity → swap ratio → add liquidity
- **防过度调仓** — 最小持仓时间、日频率限制、Gas 成本检查
- **风控体系** — 止损 / 追踪止损 / IL 容忍度 / 熔断 / 紧急回退部署
- **Gas 感知触发** — 仅在预期手续费收益超过 Gas 成本时调仓

## 架构

```
┌─────────────────────────────────────────────────────┐
│               AI Agent (Claude)                      │
│  策略设计 → 回测验证 → 参数调优 → 复盘迭代          │
└──────────────────────┬──────────────────────────────┘
                       │ 生成 / 优化
┌──────────────────────▼──────────────────────────────┐
│               策略脚本 (Python)                      │
│  价格采集 → 波动率分析 → 范围计算 → 调仓决策 → 执行 │
└──────────────────────┬──────────────────────────────┘
                       │ 调用
┌──────────────────────▼──────────────────────────────┐
│                 onchainos Skills                      │
│  行情 · K线 · 钱包 · LP头寸 · DeFi操作 · TEE签名   │
└──────────────────────┬──────────────────────────────┘
                       │ 上链
┌──────────────────────▼──────────────────────────────┐
│                  EVM L2 链上执行                      │
│       Uniswap V3 池 → LP NFT 头寸 → 手续费收入      │
└─────────────────────────────────────────────────────┘
```

## 范围算法

```
当前价格 → 1H K线 (24根) → ATR% → 波动率分类 → 范围宽度
                                        ↓
                                  趋势不对称调整 (MTF)
                                        ↓
                                  Tick 对齐 → 最终范围
```

| 波动率 | ATR | 范围示例 (ETH@$2000) | 资本效率 |
|--------|-----|---------------------|----------|
| Low (<1.5%) | $25 | $1950–$2050 | ~20× |
| Medium (1.5–3%) | $45 | $1865–$2135 | ~7× |
| High (3–5%) | $70 | $1650–$2350 | ~3× |
| Extreme (>5%) | $120 | $1040–$2960 | ~1× |

详细算法说明见 [references/range-algorithm.md](references/range-algorithm.md)。

## 快速开始

```bash
# 1. 安装
openclaw skill install cl-lp-rebalancer

# 2. 配置
cd ~/.openclaw/skills/cl-lp-rebalancer/references
cp ../.env.example .env    # 填入 API keys + 钱包地址
vi config.json             # 调整池参数

# 3. 测试（只读，安全）
python3 cl_lp.py status

# 4. 注册 cron
zeroclaw cron add '*/5 * * * *' \
  'cd ~/.openclaw/skills/cl-lp-rebalancer/references && set -a && . ../.env && set +a && python3 cl_lp.py tick'
```

## 命令

| 命令 | 用途 | 触发 |
|------|------|------|
| `tick` | 主循环：采集→分析→决策→执行 | Cron 每 5 分钟 |
| `status` | 头寸、范围可视化、收益、趋势 | 手动 |
| `report` | 每日报告 (JSON) | Cron 每天 |
| `history` | 调仓历史 | 手动 |
| `analyze` | 市场分析 + 调仓建议 | AI Agent |
| `reset` | 清除状态，从链上重新检测 | 手动 |
| `close` | 完全退出头寸 | 手动 |
| `deposit <amt>` | 记录外部存取款 | 手动 |
| `resume-trading` | 清除止损恢复交易 | 手动 |

## 目录结构

```
cl-lp-rebalancer/
├── SKILL.md              # AI Agent 核心知识（流水线、状态机、参数）
├── README.md             # 本文件
├── .env.example          # 环境变量模板
└── references/
    ├── cl_lp.py       # 策略代码（零第三方依赖）
    ├── config.json       # 参考配置（所有可调参数）
    └── range-algorithm.md # 范围算法详解
```

## 前置条件

- **onchainos** — OKX OnchainOS CLI，内置钱包管理、DEX 交易、DeFi 操作、TEE 签名等 Skills
- **OKX API Key** — DEX 交易 + DeFi 操作权限
- **Python 3.10+** — 零第三方依赖

## License

Apache-2.0
