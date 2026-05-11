#!/usr/bin/env python3
"""链上 allocate stake 到 agent+subnet（V2）
V2 签名: allocate(address staker, address agent, uint256 subnetId, uint256 amount)
staker 参数现在是显式的（第一个参数）。调用者必须是 staker 或 delegate。
"""
from awp_lib import *


def main() -> None:
    parser = base_parser("On-chain allocate stake to agent+subnet (V2)")
    parser.add_argument("--agent", required=True, help="代理地址")
    parser.add_argument("--subnet", required=True, help="子网 ID")
    parser.add_argument("--amount", required=True, help="AWP 数量（人类可读）")
    args = parser.parse_args()

    token: str = args.token
    agent: str = args.agent
    subnet: str = args.subnet
    amount: str = args.amount

    # 验证输入
    validate_address(agent, "agent")
    validate_positive_number(amount, "amount")
    subnet_id: int = validate_positive_int(subnet, "subnet")

    # 预检：获取钱包地址
    wallet_addr = get_wallet_address()

    # 获取合约注册表
    registry = get_registry()
    awp_registry = require_contract(registry, "awpRegistry")

    # 检查未分配余额
    balance = api_get(f"staking/user/{wallet_addr}/balance")
    if not isinstance(balance, dict):
        die("Could not fetch balance — check address")
    unallocated = balance.get("unallocated")
    if unallocated is None or unallocated == "null":
        die("Could not fetch balance — check address")

    amount_wei = to_wei(amount)
    unallocated_int = int(unallocated)
    # 注意：API 数据可能有延迟（约几秒），链上状态可能已变更。
    # 此检查用于提前捕获明显错误，最终以链上校验为准。
    if amount_wei > unallocated_int:
        die(f"Insufficient unallocated balance: have {unallocated_int / 10**18} AWP, need {amount} AWP")

    # allocate(address,address,uint256,uint256) selector = 0xd035a9a7
    # 参数: staker (self), agent, subnetId, amount
    calldata = encode_calldata(
        "0xd035a9a7",
        pad_address(wallet_addr),
        pad_address(agent),
        pad_uint256(subnet_id),
        pad_uint256(amount_wei),
    )

    step("allocate", staker=wallet_addr, agent=agent, subnet=subnet_id, amount=f"{amount} AWP")
    result = wallet_send(token, awp_registry, calldata)
    print(result)


if __name__ == "__main__":
    main()
