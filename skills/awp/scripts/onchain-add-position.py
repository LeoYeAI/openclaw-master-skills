#!/usr/bin/env python3
"""链上追加质押 — 向已有 StakeNFT 仓位追加 AWP
addToPosition(uint256 tokenId, uint256 amount, uint64 newLockEndTime)
检查 remainingTime、获取当前 lockEndTime、approve + addToPosition。需要 ETH 作为 gas。
"""
import re
import time as _time

from awp_lib import *


def main() -> None:
    # ── 参数解析 ──
    parser = base_parser("Add AWP to existing StakeNFT position")
    parser.add_argument("--position", required=True, help="StakeNFT token ID")
    parser.add_argument("--amount", required=True, help="AWP amount (human readable)")
    parser.add_argument("--extend-days", default="0", help="额外延长锁定天数（默认 0）")
    args = parser.parse_args()

    position = validate_positive_int(args.position, "position")
    amount = validate_positive_number(args.amount, "amount")

    # 验证 extend-days 非负数
    extend_days_str: str = args.extend_days
    if not re.match(r"^[0-9]+\.?[0-9]*$", extend_days_str):
        die("Invalid --extend-days: must be a non-negative number")
    extend_days = float(extend_days_str)

    # ── 预检查 ──
    wallet_addr = get_wallet_address()
    registry = get_registry()
    awp_token = require_contract(registry, "awpToken")
    stake_nft = require_contract(registry, "stakeNFT")

    token_id_hex = pad_uint256(position)

    # ── Step 1: 检查 remainingTime(tokenId) — selector = 0x0c64a7f2 ──
    remaining_hex = rpc_call(stake_nft, encode_calldata("0x0c64a7f2", token_id_hex))
    if not remaining_hex or remaining_hex in ("0x", "null"):
        die("remainingTime() call failed — position may not exist")

    remaining = hex_to_int(remaining_hex)
    if remaining == 0:
        die(f"PositionExpired: position {position} lock has expired (remainingTime=0). Cannot add to an expired position.")

    # ── Step 2: 获取当前 lockEndTime — positions(uint256) selector = 0x99fbab88 ──
    # 返回 (uint128 amount, uint64 lockEndTime, uint64 createdAt)，各占 32 字节
    positions_hex = rpc_call(stake_nft, encode_calldata("0x99fbab88", token_id_hex))
    if not positions_hex or positions_hex in ("0x", "null"):
        die("positions() call failed")

    # word 1 (offset 64..128) = lockEndTime
    data = positions_hex.replace("0x", "")
    current_lock_end = int(data[64:128], 16)

    # ── Step 3: 计算 newLockEndTime ──
    now = int(_time.time())
    if extend_days > 0:
        candidate = now + int(extend_days * 86400)
        new_lock_end = max(current_lock_end, candidate)
    else:
        new_lock_end = current_lock_end

    # uint64 溢出保护（newLockEndTime 参数类型为 uint64）
    if new_lock_end > 2**64 - 1:
        die(f"new_lock_end too large: {new_lock_end} exceeds uint64 max")

    # ── Step 4: Approve AWP to StakeNFT ──
    amount_wei = to_wei(amount)
    step("approve", spender=stake_nft, amount=f"{amount} AWP")
    wallet_approve(args.token, awp_token, stake_nft, amount)

    # ── Step 5: addToPosition(uint256,uint256,uint64) — selector = 0xd2845e7d ──
    calldata = encode_calldata(
        "0xd2845e7d",
        pad_uint256(position),
        pad_uint256(amount_wei),
        pad_uint256(new_lock_end),
    )

    step("addToPosition", tokenId=position, amount_wei=str(amount_wei),
         newLockEndTime=new_lock_end, remainingTime=remaining)
    result = wallet_send(args.token, stake_nft, calldata)
    print(result)


if __name__ == "__main__":
    main()
