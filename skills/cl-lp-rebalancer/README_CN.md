# CL LP 自动调仓器

[English](./README.md)

基于 OKX DEX API 的 EVM L2 链上 Uniswap V3 集中流动性 LP 自动调仓策略。

## 特性

- **波动率自适应范围** — 低波动率收紧范围（提高资本效率），高波动率放宽范围（减少调仓和无常损失）
- **趋势不对称调整** — 沿趋势方向偏移范围，降低无常损失
- **多时间框架分析** — 5 分钟价格历史 + 1 小时 K 线 ATR
- **完整调仓流水线** — 领取手续费 → 移除流动性 → 比例兑换 → 添加流动性
- **Gas 感知触发** — 仅在预期手续费收益超过 gas 成本时调仓
- **Discord 通知** — 调仓提醒、持仓状态

## 架构

```
Cron (5分钟) → Python 脚本 → onchainos CLI → OKX Web3 API → 链上
                   ↓                ↓
             state_v1.json    钱包 (TEE 签名)
                   ↓
             价格+波动率分析 → 范围计算 → 调仓执行 → Discord
```

## 与网格交易的区别

| 维度 | 网格交易 | CL LP 调仓器 |
|------|---------|-------------|
| 收益来源 | 网格价差（低买高卖） | LP 手续费（做市） |
| 链上操作 | swap 买卖 | add/remove liquidity + claim fees |
| 核心参数 | 网格间距、层数 | 范围宽度、tick 间距 |
| 持仓形式 | 两种代币余额 | NFT position（LP token） |
| 风险特征 | 单边行情踏空 | 无常损失（IL） |

## 安装

**ClawHub**（推荐）:
```bash
npx clawhub install cl-lp-rebalancer
```

**手动安装**:
```bash
cp -r cl-lp-rebalancer ~/.openclaw/skills/
```

## 目录结构

```
cl-lp-rebalancer/
├── SKILL.md      # 核心知识：算法、流水线、配置
├── install.sh    # 多平台安装器
└── references/   # 详细文档
```

## 前置条件

- onchainos CLI — `npx skills add okx/onchainos-skills`
- OKX API Key，需有 DEX 交易权限
- OnchainOS Agentic Wallet，需启用 TEE 签名
- Python 3.10+
- VPS（推荐，用于 7×24 运行）

## 许可证

Apache-2.0
