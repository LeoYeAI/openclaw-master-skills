#!/usr/bin/env python3
"""链上提取 — 从过期的 StakeNFT 仓位提取 AWP (V2)
withdraw(uint256 tokenId) — 销毁仓位 NFT，归还 AWP
仅当锁定已到期（remainingTime == 0）时可调用。需要 ETH 作为 gas。
"""
from awp_lib import *


def main() -> None:
    # ── 参数解析 ──
    parser = base_parser("Withdraw from expired StakeNFT position")
    parser.add_argument("--position", required=True, help="StakeNFT token ID")
    args = parser.parse_args()

    position = validate_positive_int(args.position, "position")

    # ── 预检查 ──
    wallet_addr = get_wallet_address()
    registry = get_registry()
    stake_nft = require_contract(registry, "stakeNFT")

    # ── 检查 remainingTime(tokenId) — selector = 0x0c64a7f2 ──
    position_padded = pad_uint256(position)
    remaining_hex = rpc_call(stake_nft, encode_calldata("0x0c64a7f2", position_padded))

    if not remaining_hex or remaining_hex in ("0x", "null"):
        die("Could not fetch remainingTime — is the position ID valid?")

    remaining = hex_to_int(remaining_hex)

    if remaining != 0:
        days_left = round(remaining / 86400, 1)
        die(f"Position #{position} still locked — {days_left} days remaining. Cannot withdraw yet.")

    # ── 发送 withdraw(uint256) — selector = 0x2e1a7d4d ──
    calldata = encode_calldata("0x2e1a7d4d", position_padded)
    step("withdraw", position=position, target=stake_nft)
    result = wallet_send(args.token, stake_nft, calldata)
    print(result)


if __name__ == "__main__":
    main()
