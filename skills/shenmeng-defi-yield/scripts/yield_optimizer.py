#!/usr/bin/env python3
"""
DeFi 收益优化建议器
根据用户资产和风险偏好，推荐最佳收益策略

用法:
  python3 scripts/yield_optimizer.py --asset USDC --risk low --top 5
"""
from dataclasses import dataclass
from typing import List

@dataclass
class Strategy:
    protocol: str
    vault_name: str
    asset: str
    chain: str
    apy: float
    min_deposit: float
    risk_level: str
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
    Strategy("Convex", "3pool", "USDC", "Ethereum", 4.8, 10, "low", False, False, "Curve + CVX 叠加"),
    # ETH
    Strategy("Lido", "stETH", "ETH", "Ethereum", 4.3, 0, "low", False, False, "最安全的 ETH 质押"),
    Strategy("Yearn", "yETH", "ETH", "Ethereum", 5.1, 0, "medium", True, False, "自动策略，有 IL"),
    Strategy("Rocket Pool", "rETH", "ETH", "Ethereum", 4.6, 0.1, "low", False, False, "去中心化"),
    Strategy("Gearbox", "dGEAR", "ETH", "Ethereum", 15.0, 0.5, "high", True, True, "杠杆策略，高风险"),
    # BTC
    Strategy("Curve", "renBTC/wBTC", "WBTC", "Ethereum", 2.1, 0.01, "medium", True, False, "BTC 稳定对"),
    Strategy("Yearn", "yWBTC", "WBTC", "Arbitrum", 4.8, 0, "medium", True, False, "Yearn 托管"),
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
    parser.add_argument("--asset", "-a", default="USDC", help="资产类型: USDC/ETH/WBTC")
    parser.add_argument("--risk", "-r", default="low", choices=["low", "medium", "high"], help="风险等级")
    parser.add_argument("--top", "-n", type=int, default=5, help="显示前 N 名")
    args = parser.parse_args()

    print("=" * 60)
    print(f"  收益优化建议 | 资产: {args.asset} | 风险: {args.risk}")
    print("=" * 60)

    results = optimize(args.asset, args.risk, 0)
    if not results:
        print("\n未找到符合条件的策略")
    for i, s in enumerate(results[:args.top], 1):
        print(f"\n🏦 #{i} {s.protocol} - {s.vault_name}")
        print(f"   资产: {s.asset} | 链: {s.chain}")
        print(f"   APY: {s.apy:.2f}% | 风险: {s.risk_level.upper()}")
        print(f"   IL: {'⚠️ 有' if s.il_risk else '✅ 无'} | 锁仓: {'⏱️ 有' if s.lockup else '✅ 无'}")
        print(f"   备注: {s.notes}")
