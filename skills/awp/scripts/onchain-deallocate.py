#!/usr/bin/env python3
"""链上 deallocate stake 从 agent+subnet（V2）
deallocate(address staker, address agent, uint256 subnetId, uint256 amount)
立即生效，无冷却期。
"""
from awp_lib import *


def main() -> None:
    parser = base_parser("On-chain deallocate stake from agent+subnet (V2)")
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

    amount_wei = to_wei(amount)

    # deallocate(address,address,uint256,uint256) selector = 0x716fb83d
    calldata = encode_calldata(
        "0x716fb83d",
        pad_address(wallet_addr),
        pad_address(agent),
        pad_uint256(subnet_id),
        pad_uint256(amount_wei),
    )

    step("deallocate", staker=wallet_addr, agent=agent, subnet=subnet_id, amount=f"{amount} AWP")
    result = wallet_send(token, awp_registry, calldata)
    print(result)


if __name__ == "__main__":
    main()
