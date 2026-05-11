#!/usr/bin/env python3
"""链上 deposit AWP 到 StakeNFT（V2）
处理 approve + deposit 两步操作。
"""
from awp_lib import *


def main() -> None:
    parser = base_parser("On-chain deposit AWP to StakeNFT (V2)")
    parser.add_argument("--amount", required=True, help="AWP 数量（人类可读）")
    parser.add_argument("--lock-days", required=True, help="锁定天数（必须 > 0）")
    args = parser.parse_args()

    token: str = args.token
    amount: str = args.amount
    lock_days: str = args.lock_days

    # 验证数值输入
    validate_positive_number(amount, "amount")
    validate_positive_number(lock_days, "lock-days")

    # 预检：获取钱包地址
    wallet_addr = get_wallet_address()

    # 获取合约注册表
    registry = get_registry()
    awp_token = require_contract(registry, "awpToken")
    stake_nft = require_contract(registry, "stakeNFT")

    # 单位转换
    amount_wei = to_wei(amount)
    lock_seconds = days_to_seconds(lock_days)

    # uint64 溢出保护（lockDuration 参数类型为 uint64）
    if lock_seconds > 2**64 - 1:
        die(f"lock-days too large: {lock_days} days ({lock_seconds}s) exceeds uint64 max")

    # 步骤 1：授权 AWP 给 StakeNFT
    step("approve", spender=stake_nft, amount=f"{amount} AWP")
    wallet_approve(token, awp_token, stake_nft, amount)

    # 步骤 2：存款
    # deposit(uint256,uint64) selector = 0x7d552ea6
    calldata = encode_calldata(
        "0x7d552ea6",
        pad_uint256(amount_wei),
        pad_uint256(lock_seconds),
    )

    step("deposit", amount_wei=str(amount_wei), lock_seconds=lock_seconds)
    result = wallet_send(token, stake_nft, calldata)
    print(result)


if __name__ == "__main__":
    main()
