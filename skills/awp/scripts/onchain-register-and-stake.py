#!/usr/bin/env python3
"""一键 registerAndStake: 在单笔交易中完成 register + deposit + allocate
处理 approve（到 AWP_REGISTRY）+ registerAndStake 两步操作。
"""
from awp_lib import *


def main() -> None:
    parser = base_parser("One-click registerAndStake: register + deposit + allocate")
    parser.add_argument("--amount", required=True, help="存款 AWP 数量（人类可读）")
    parser.add_argument("--lock-days", required=True, help="锁定天数")
    parser.add_argument("--agent", required=True, help="代理地址")
    parser.add_argument("--subnet", required=True, help="子网 ID")
    parser.add_argument("--allocate-amount", required=True, help="分配 AWP 数量（人类可读）")
    args = parser.parse_args()

    token: str = args.token
    amount: str = args.amount
    lock_days: str = args.lock_days
    agent: str = args.agent
    subnet: str = args.subnet
    allocate_amount: str = args.allocate_amount

    # 验证数值输入
    validate_positive_number(amount, "amount")
    validate_positive_number(lock_days, "lock-days")
    validate_positive_number(allocate_amount, "allocate-amount")
    validate_address(agent, "agent")
    subnet_id: int = validate_positive_int(subnet, "subnet")

    # 预检：获取钱包地址
    wallet_addr = get_wallet_address()

    # 获取合约注册表
    registry = get_registry()
    awp_token = require_contract(registry, "awpToken")
    awp_registry = require_contract(registry, "awpRegistry")

    # 单位转换
    amount_wei = to_wei(amount)
    lock_seconds = days_to_seconds(lock_days)
    allocate_wei = to_wei(allocate_amount)

    # 分配金额不能超过存款金额
    if allocate_wei > amount_wei:
        die(f"allocate-amount ({allocate_amount} AWP) exceeds deposit amount ({amount} AWP)")

    # 步骤 1：授权 AWP 给 AWP_REGISTRY（注意：目标是 AWP_REGISTRY，不是 StakeNFT）
    step("approve", spender=awp_registry,
         note="Approve target is AWP_REGISTRY, NOT StakeNFT",
         amount=f"{amount} AWP")
    wallet_approve(token, awp_token, awp_registry, amount)

    # 步骤 2：registerAndStake(uint256 depositAmount, uint64 lockDuration,
    #          address agent, uint256 subnetId, uint256 allocateAmount)
    # selector = 0x34426564
    calldata = encode_calldata(
        "0x34426564",
        pad_uint256(amount_wei),
        pad_uint256(lock_seconds),
        pad_address(agent),
        pad_uint256(subnet_id),
        pad_uint256(allocate_wei),
    )

    step("registerAndStake", to=awp_registry,
         deposit_amount_wei=str(amount_wei), lock_seconds=lock_seconds,
         agent=agent, subnet=subnet_id, allocate_amount_wei=str(allocate_wei))
    result = wallet_send(token, awp_registry, calldata)
    print(result)


if __name__ == "__main__":
    main()
