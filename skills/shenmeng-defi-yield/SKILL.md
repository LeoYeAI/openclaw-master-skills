---
name: defi-yield
description: |
  DeFi 收益聚合器（Yield Aggregator）助手。帮助用户找到最佳收益策略、
  分析各协议 APY、执行自动复投、追踪仓位收益。

  当用户提到以下内容时激活：
  - "收益聚合"、"DeFi 收益"、"撸收益"
  - "Yearn Finance"、"Beefy Finance"、"Pendle"、"Gamma"
  - "APY 查询"、"哪个池子收益最高"、"收益策略"
  - "自动复投"、"流动性挖矿"、"收益农场"
  - "质押收益"、"LP 收益"、"稳定币收益"
  - 查询 APY、对比收益、分析风险、执行操作
---

# DeFi Yield Aggregator Skill

## 概述

收益聚合器（Yield Aggregator）是 DeFi 中的**自动理财协议**，核心逻辑：

```
用户入金 → 协议自动分配到最高收益池子 → 收益自动复投 → 用户受益
```

**相比手动收益耕种的优势：**
- 自动复利（收益再投资，省 Gas）
- 策略由专业团队维护（Yearn 等）
- 智能路由（自动切换到收益最高的池子）

---

## 核心概念

| 术语 | 含义 |
|------|------|
| **APY** | 年化收益率（含复利效应） |
| **APR** | 年化收益率（不含复利） |
| **TVL** | Total Value Locked，锁仓量 |
| **Vault** | 收益池，用户存入资产、协议自动操作 |
| **Auto-compounding** | 自动复利，收益自动再质押 |
| **Delta Neutral** | 三角中性，对冲风险策略 |
| **Leverage / 杠杆** | 借款放大收益（同时放大风险） |
| **IL** | Impermanent Loss，无常损失 |

---

## 主流收益聚合协议

### 🥇 Yearn Finance（以太坊）
| 项目 | 信息 |
|------|------|
| 官网 | yearn.finance |
| 链 | Ethereum、Arbitrum、Polygon、Fantom |
| 特点 | 主动策略 Vault（yVaults），顶级安全性 |
| 代币 | YFI（治理代币） |
| APY 来源 | yearn.finance/vaults |

### 🥈 Beefy Finance（多链）
| 项目 | 信息 |
|------|------|
| 官网 | beefy.finance |
| 链 | 50+ 条链（BSC/ETH/Polygon/Arbitrum等） |
| 特点 | 多链覆盖，收益 Vault 数量最多 |
| 代币 | BIFI |
| APY 来源 | beefy.finance/vaults |

### 🥉 Pendle Finance（创新）
| 项目 | 信息 |
|------|------|
| 官网 | pendle.finance |
| 链 | Ethereum、Arbitrum、BSC |
| 特点 | 收益代币化（PT / YT），可锁定未来收益 |
| 适合 | 预期利率下降，想提前锁定高收益 |

### 🏅 Gamma Strategies（Gamma）
| 项目 | 信息 |
|------|------|
| 官网 | gamma.xyz |
| 链 | Ethereum、Polygon |
| 特点 | Uniswap V3 流动性管理，专攻 LP 收益 |
| 适合 | 想做市但不想主动管理 LP 仓位 |

### 🏅 Stargate（跨链）
| 项目 | 信息 |
|------|------|
| 官网 | stargate.finance |
| 链 | 多链 |
| 特点 | 跨链稳定币桥 + 收益池 |
| 适合 | 稳定币跨链 + 收益双赢 |

### 其他常见协议
| 协议 | 特点 |
|------|------|
| **Convex Finance** | CVX 生态，专注 Curve 收益 |
| **Aura Finance** | Balancer 收益聚合 |
| **Gearbox** | 杠杆收益协议 |
| **Roken** | Lido rETH 质押收益增强 |
| **Eigenlayer** | 再质押（Restaking）收益 |

---

## 工具

**API / Web 抓取**
- `extract_content_from_websites` — 抓取 Yearn / Beefy / Pendle 等官方 APY 数据
- `batch_web_search` — 搜索最新收益策略、协议动态

**Python 脚本**
- `scripts/apy_checker.py` — 批量查询多协议 APY
- `scripts/position_tracker.py` — 追踪钱包在各协议中的仓位和收益
- `scripts/yield_optimizer.py` — 收益对比分析，优化建议

---

## 工作流程

### 场景一：查询最佳 APY

1. 确认用户资产类型：稳定币 / ETH / BTC / 山寨币
2. 确认链偏好和风险承受能力
3. 查询各协议对应 Vault APY
4. 输出对比表 + 建议

**操作步骤：**
```
1. 使用 apy_checker.py 拉取 Yearn / Beefy / Gamma 等协议 APY
2. 对比稳定币收益（USDC/USDT/DAI）
3. 考虑 Gas 成本（以太坊主网 vs L2）
4. 提示无常损失风险和流动性限制
5. 给出最优策略建议
```

### 场景二：收益策略分析

根据用户持仓类型推荐策略：

**稳定币（USDC/USDT/DAI）：**
```
最优：Yearn yUSDC Vault / Beefy USDC Vault
APY 范围：3%~15%（根据市场情况）
风险：低（单币池，无 IL）
注意：Gas 成本要低于收益
推荐链：Arbitrum / Polygon（低 Gas）
```

**ETH 生态：**
```
方案A：直接质押 Lido → 4~5% APY（安全稳定）
方案B：stETH 在 Curve/Yearn 循环LP → 5~10% APY
方案C：Yearn ETH Vault → 自动策略
风险：ETH 波动 + IL
```

**BTC 生态：**
```
方案A：WBTC 存入 BitBTC -> 4~6% APY
方案B：Curve wBTC/renBTC 池
风险：BTC 波动
```

### 场景三：仓位追踪

1. 用户提供钱包地址
2. 调用 position_tracker.py 扫描
3. 输出各协议的资产分布 + 估算收益
4. 提示未领取奖励情况

---

## 常用脚本

### 脚本 1：APY 批量查询

文件：`scripts/apy_checker.py`

```python
#!/usr/bin/env python3
"""
DeFi APY 批量查询器
查询 Yearn、Beefy、Pendle 等主流协议的 APY 数据
"""
import requests
import json
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class VaultInfo:
    protocol: str
    chain: str
    asset: str
    vault_address: str
    apy: float  # percentage
    tvl_usd: float
    has_reward_token: bool = False
    reward_apy: float = 0.0

def query_yearn_vaults() -> List[VaultInfo]:
    """查询 Yearn Finance Vaults"""
    url = "https://yearn.vision/vaults"
    results = []
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        for vault in data.get("data", [])[:20]:
            results.append(VaultInfo(
                protocol="Yearn",
                chain=vault.get("chain", "ethereum"),
                asset=vault.get("symbol", "").replace("yv", "").upper(),
                vault_address=vault.get("address", ""),
                apy=float(vault.get("apy", {}).get("net_apy", 0) or 0) * 100,
                tvl_usd=float(vault.get("tvl", {}).get("tvl", 0) or 0),
            ))
    except Exception as e:
        print(f"Yearn API 失败: {e}")
    return results

def query_beefy_vaults(asset: str = "") -> List[VaultInfo]:
    """查询 Beefy Finance Vaults"""
    url = "https://api.beefy.finance/vaults"
    results = []
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        for vault in data:
            if asset and asset.upper() not in vault.get("token", "").upper():
                continue
            results.append(VaultInfo(
                protocol="Beefy",
                chain=vault.get("chain", ""),
                asset=vault.get("token", ""),
                vault_address=vault.get("earnContractAddress", ""),
                apy=float(vault.get("apy", 0) or 0) * 100,
                tvl_usd=float(vault.get("tvl", 0) or 0),
            ))
    except Exception as e:
        print(f"Beefy API 失败: {e}")
    return results

def query_pendle_markets() -> List[VaultInfo]:
    """查询 Pendle Finance 市场"""
    url = "https://api.pendle.finance/vip/data/api/v1/markets"
    results = []
    headers = {"Accept": "application/json"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json().get("data", []) if isinstance(resp.json(), dict) else resp.json()
        for m in data[:10]:
            results.append(VaultInfo(
                protocol="Pendle",
                chain="ethereum",
                asset=m.get("underlyingAsset", ""),
                vault_address=m.get("address", ""),
                apy=float(m.get("apy", 0) or 0),
                tvl_usd=float(m.get("tvlUsd", 0) or 0),
            ))
    except Exception as e:
        print(f"Pendle API 失败: {e}")
    return results

def format_results(vaults: List[VaultInfo], top_n: int = 10):
    """格式化输出"""
    # 排序
    sorted_vaults = sorted(vaults, key=lambda x: x.apy, reverse=True)
    print(f"\n{'协议':<10} {'链':<10} {'资产':<12} {'APY':>8} {'TVL($)':>14}")
    print("-" * 60)
    for v in sorted_vaults[:top_n]:
        apy_str = f"{v.apy:.2f}%" if v.apy > 0 else "N/A"
        tvl_str = f"${v.tvl_usd:,.0f}" if v.tvl_usd > 0 else "N/A"
        print(f"{v.protocol:<10} {v.chain:<10} {v.asset:<12} {apy_str:>8} {tvl_str:>14}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="DeFi APY 查询器")
    parser.add_argument("--asset", "-a", default="", help="过滤资产，如 USDC、ETH")
    parser.add_argument("--top", "-n", type=int, default=10, help="显示前 N 名")
    args = parser.parse_args()

    print("=" * 60)
    print("  DeFi APY 查询器")
    print("=" * 60)

    all_vaults = []
    all_vaults += query_yearn_vaults()
    all_vaults += query_beefy_vaults(args.asset)

    if all_vaults:
        format_results(all_vaults, args.top)
    else:
        print("未获取到数据，请检查网络")
```

### 脚本 2：仓位追踪器

文件：`scripts/position_tracker.py`

```python
#!/usr/bin/env python3
"""
DeFi 仓位追踪器
查询钱包在各收益协议中的持仓和累计收益

用法:
  export WALLET=0xYourAddress
  python3 scripts/position_tracker.py
"""
import os
import requests
from web3 import Web3
from dataclasses import dataclass
from typing import Dict, List

WALLET = os.getenv("WALLET", "0x0000000000000000000000000000000000000000")

# 常用协议 Vault 地址（部分）
KNOWN_VAULTS = {
    "yearn": {
        "name": "Yearn Finance",
        "vaults": {
            "0x5f18C75AbDAe578b477E319BcA4F55eFEF2eF892": "yUSDC",
            "0xa354F3587Ae0fB13C52e4873BCCC4767C8eFc2D9": "yUSDT",
            "0x8d0C6B68D3E1D2d8f2d0D3F9d5E3f2E8D2E1E0E1": "yDAI",
        }
    },
    "beefy": {
        "name": "Beefy Finance",
        "vaults": {
            "0x0000000000000000000000000000000000000000": "beUSDC",
        }
    }
}

@dataclass
class Position:
    protocol: str
    vault: str
    asset: str
    balance: float
    value_usd: float
    apy: float
    pending_rewards: float = 0.0

def get_token_balance(w3: Web3, token_addr: str, wallet: str) -> float:
    """查询 Token 余额"""
    erc20_abi = [
        {
            "inputs": [{"name": "account", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "decimals",
            "outputs": [{"name": "", "type": "uint8"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "symbol",
            "outputs": [{"name": "", "type": "string"}],
            "stateMutability": "view",
            "type": "function"
        }
    ]
    try:
        contract = w3.eth.contract(address=Web3.to_checksum_address(token_addr), abi=erc20_abi)
        bal = contract.functions.balanceOf(Web3.to_checksum_address(wallet)).call()
        decimals = contract.functions.decimals().call()
        return bal / (10 ** decimals)
    except Exception:
        return 0.0

def estimate_yearn_position(vault_addr: str, wallet: str, rpc_url: str) -> Optional[Position]:
    """估算 Yearn Vault 仓位"""
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        return None
    balance = get_token_balance(w3, vault_addr, wallet)
    if balance <= 0:
        return None
    return Position(
        protocol="Yearn",
        vault=vault_addr[:10] + "...",
        asset="Vault Share",
        balance=balance,
        value_usd=balance * 1.0,  # 简化估算
        apy=0.0,
    )

def main():
    if WALLET.startswith("0x000"):
        print("⚠️ 请设置钱包地址:")
        print("   export WALLET=0xYourAddress")
        print("   python3 scripts/position_tracker.py")
        return

    print(f"🔍 扫描地址: {WALLET}")
    print("-" * 50)

    rpc = "https://eth.llamarpc.com"
    positions: List[Position] = []

    # 扫描 Yearn
    print("\n📊 Yearn Vaults...")
    for addr, name in KNOWN_VAULTS["yearn"]["vaults"].items():
        pos = estimate_yearn_position(addr, WALLET, rpc)
        if pos:
            positions.append(pos)
            print(f"   ✅ {name}: {pos.balance:.4f} shares (≈${pos.value_usd:.2f})")

    if not positions:
        print("   📭 未发现已知的 Yearn 仓位")

    print("\n📊 Beefy Finance...")
    print("   (需要 Beefy API，建议直接在 beefy.finance 钱包连接查看)")

    print("\n" + "=" * 50)
    total_value = sum(p.value_usd for p in positions)
    total_apy = sum(p.apy * p.value_usd for p in positions) / max(total_value, 1)
    print(f"\n💰 累计 TVL: ${total_value:,.2f}")
    print(f"📈 加权 APY: {total_apy:.2f}%")

if __name__ == "__main__":
    main()
```

### 脚本 3：收益优化建议器

文件：`scripts/yield_optimizer.py`

```python
#!/usr/bin/env python3
"""
DeFi 收益优化建议器
根据用户资产和风险偏好，推荐最佳收益策略
"""
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Strategy:
    protocol: str
    vault_name: str
    asset: str
    chain: str
    apy: float
    min_deposit: float
    risk_level: str  # low / medium / high
    il_risk: bool
    lockup: bool
    notes: str

STRATEGIES = [
    # 稳定币
    Strategy("Yearn", "yUSDC", "USDC", "Ethereum", 4.5, 0, "low", False, False, "安全首选，TVL 高"),
    Strategy("Yearn", "yUSDC", "USDC", "Arbitrum", 6.2, 0, "low", False, False, "L2 低 Gas，APY 更高"),
    Strategy("Beefy", "USDC", "USDC", "Polygon", 5.8, 0, "low", False, False, "Polygon 低费用"),
    Strategy("Beefy", "USDT", "USDT", "Arbitrum", 7.1, 0, "medium", False, False, "APY 较高"),
    Strategy("Curve", "3pool", "USDT/USDC/DAI", "Ethereum", 3.2, 1000, "low", False, False, "主流稳定币池"),
    Strategy("Convex", "3pool", "USDC", "Ethereum", 4.8, 10, "low", False, False, "Curve + CVX 叠加收益"),
    # ETH
    Strategy("Lido", "stETH", "ETH", "Ethereum", 4.3, 0, "low", False, False, "最安全的 ETH 质押"),
    Strategy("Yearn", "yETH", "ETH", "Ethereum", 5.1, 0, "medium", True, False, "自动策略，有 IL"),
    Strategy("Rocket Pool", "rETH", "ETH", "Ethereum", 4.6, 0.1, "low", False, False, "去中心化，比 Lido 收益略高"),
    Strategy("Gearbox", "dGEAR", "ETH", "Ethereum", 15.0, 0.5, "high", True, True, "杠杆策略，风险高"),
    # BTC
    Strategy("Curve", "renBTC/wBTC", "WBTC", "Ethereum", 2.1, 0.01, "medium", True, False, "BTC 稳定对，有 IL"),
    Strategy("Yearn", "yWBTC", "WBTC", "Arbitrum", 4.8, 0, "medium", True, False, "Yearn 托管，省 Gas"),
]

def optimize(asset: str, risk: str = "low", min_apy: float = 0) -> List[Strategy]:
    """根据条件过滤策略"""
    results = []
    for s in STRATEGIES:
        if asset.lower() not in s.asset.lower():
            continue
        if risk == "low" and s.risk_level not in ("low",):
            continue
        if risk == "medium" and s.risk_level == "high":
            continue
        if s.apy < min_apy:
            continue
        results.append(s)
    return sorted(results, key=lambda x: x.apy, reverse=True)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="DeFi 收益优化建议")
    parser.add_argument("--asset", "-a", default="USDC", help="资产类型")
    parser.add_argument("--risk", "-r", default="low", choices=["low", "medium", "high"], help="风险等级")
    parser.add_argument("--min-apy", "-m", type=float, default=0, help="最低 APY 要求")
    args = parser.parse_args()

    print("=" * 60)
    print(f"  收益优化建议 | 资产: {args.asset} | 风险: {args.risk}")
    print("=" * 60)

    results = optimize(args.asset, args.risk, args.min_apy)
    if not results:
        print("\n未找到符合条件的策略")
    for s in results[:5]:
        print(f"\n🏦 {s.protocol} - {s.vault_name}")
        print(f"   资产: {s.asset} | 链: {s.chain}")
        print(f"   APY: {s.apy:.2f}% | 风险: {s.risk_level.upper()}")
        print(f"   IL 风险: {'⚠️ 有' if s.il_risk else '✅ 无'} | 锁仓: {'⏱️ 有' if s.lockup else '✅ 无'}")
        print(f"   备注: {s.notes}")
```

---

## 风险提示 ⚠️

| 风险类型 | 说明 | 防范 |
|---------|------|------|
| **无常损失 (IL)** | 流动性池中资产价格波动导致损失 | 优先选单币池（无 IL） |
| **智能合约漏洞** | 协议被攻击导致资金损失 | 选择经过审计的知名协议 |
| ** Rug Pull** | 流动性突撤导致亏损 | 检查 TVL 和团队背景 |
| **Gas 成本** | L2 收益高但波动大 | 计算净收益（扣 Gas 后） |
| **预言机操纵** | 价格数据被操纵 | 选择有 TWAP 保护的协议 |
| **流动性不足** | 提取时池子没足够流动性 | 选择高 TVL 协议 |

---

## 参考链接

- Yearn Vaults：https://yearn.finance/vaults
- Beefy Vaults：https://beefy.finance/vaults
- Pendle：https://pendle.finance
- Gamma Strategies：https://gamma.xyz
- DeFi Llama（收益对比）：https://defillama.com/yields
- Dune Analytics（收益看板）：https://dune.com
