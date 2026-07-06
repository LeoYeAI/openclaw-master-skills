#!/usr/bin/env python3
"""
DeFi APY 批量查询器
查询 Yearn、Beefy、Pendle 等主流协议的 APY 数据

用法:
  python3 scripts/apy_checker.py --asset USDC --top 10
"""
import requests
import json
from dataclasses import dataclass
from typing import List

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
        for vault in data.get("data", [])[:30]:
            try:
                apy_data = vault.get("apy", {})
                net_apy = 0.0
                if isinstance(apy_data, dict):
                    net_apy = float(apy_data.get("net_apy", 0) or 0)
                elif isinstance(apy_data, (int, float)):
                    net_apy = float(apy_data)
                tvl_data = vault.get("tvl", {})
                tvl = 0.0
                if isinstance(tvl_data, dict):
                    tvl = float(tvl_data.get("tvl", 0) or 0)
                results.append(VaultInfo(
                    protocol="Yearn",
                    chain=vault.get("chain", "ethereum"),
                    asset=vault.get("symbol", "").replace("yv", "").upper(),
                    vault_address=vault.get("address", ""),
                    apy=net_apy * 100,
                    tvl_usd=tvl,
                ))
            except Exception:
                continue
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
            try:
                if asset and asset.upper() not in vault.get("token", "").upper():
                    continue
                vault_apy = vault.get("apy", 0) or 0
                if isinstance(vault_apy, dict):
                    vault_apy = vault_apy.get("total", 0) or 0
                results.append(VaultInfo(
                    protocol="Beefy",
                    chain=vault.get("chain", ""),
                    asset=vault.get("token", ""),
                    vault_address=vault.get("earnContractAddress", ""),
                    apy=float(vault_apy) * 100,
                    tvl_usd=float(vault.get("tvl", 0) or 0),
                ))
            except Exception:
                continue
    except Exception as e:
        print(f"Beefy API 失败: {e}")
    return results

def query_defillama(asset: str = "") -> List[VaultInfo]:
    """通过 DeFi Llama API 查询"""
    url = "https://yields.llama.fi/vaults"
    results = []
    try:
        resp = requests.get(url, timeout=15)
        data = resp.json().get("data", [])
        for vault in data:
            try:
                symbol = vault.get("symbol", "")
                if asset and asset.upper() not in symbol.upper():
                    continue
                apy = vault.get("apy", 0) or 0
                results.append(VaultInfo(
                    protocol=vault.get("project", ""),
                    chain=vault.get("chain", ""),
                    asset=symbol,
                    vault_address=vault.get("symbol", ""),
                    apy=float(apy) * 100,
                    tvl_usd=float(vault.get("tvlUsd", 0) or 0),
                ))
            except Exception:
                continue
    except Exception as e:
        print(f"DeFi Llama API 失败: {e}")
    return results

def format_results(vaults: List[VaultInfo], top_n: int = 10):
    """格式化输出"""
    sorted_vaults = sorted(vaults, key=lambda x: x.apy, reverse=True)
    print(f"\n{'协议':<14} {'链':<10} {'资产':<12} {'APY':>9} {'TVL($)':>14}")
    print("-" * 65)
    shown = 0
    for v in sorted_vaults:
        if shown >= top_n:
            break
        if v.apy <= 0:
            continue
        apy_str = f"{v.apy:.2f}%"
        tvl_str = f"${v.tvl_usd:,.0f}" if v.tvl_usd > 0 else "N/A"
        print(f"{v.protocol:<14} {v.chain:<10} {v.asset:<12} {apy_str:>9} {tvl_str:>14}")
        shown += 1

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="DeFi APY 查询器")
    parser.add_argument("--asset", "-a", default="", help="过滤资产，如 USDC、ETH、WBTC")
    parser.add_argument("--top", "-n", type=int, default=15, help="显示前 N 名")
    args = parser.parse_args()

    print("=" * 65)
    print("  DeFi APY 查询器")
    print("=" * 65)

    all_vaults = []
    all_vaults += query_yearn_vaults()
    all_vaults += query_beefy_vaults(args.asset)

    if not all_vaults:
        print("\n⚠️ 官方 API 未返回数据，尝试 DeFi Llama...")
        all_vaults = query_defillama(args.asset)

    if all_vaults:
        format_results(all_vaults, args.top)
    else:
        print("未获取到数据，请稍后重试")
