#!/usr/bin/env python3
"""链上 register() — 显式注册（V2）
V2 中 register() 等同于 setRecipient(msg.sender)。
每个地址隐式为 root；调用 register() 只是显式将 recipient 设为自己。
"""
from awp_lib import *


def main() -> None:
    parser = base_parser("On-chain register (V2)")
    args = parser.parse_args()
    token: str = args.token

    # 预检：获取钱包地址
    wallet_addr = get_wallet_address()

    # 获取合约注册表
    registry = get_registry()
    awp_registry = require_contract(registry, "awpRegistry")

    # 检查是否已注册
    check = api_get(f"address/{wallet_addr}/check")
    if isinstance(check, dict):
        # V2: .isRegistered; V1: .isRegisteredUser
        is_registered = check.get("isRegistered")
        if is_registered is None:
            is_registered = check.get("isRegisteredUser", False)
        recipient = check.get("recipient", "")

        if str(is_registered).lower() == "true":
            print(json.dumps({
                "status": "already_registered",
                "address": wallet_addr,
                "recipient": recipient,
            }))
            return

    # register() selector = 0x1aa3a008
    step("register", address=wallet_addr)
    result = wallet_send(token, awp_registry, "0x1aa3a008")
    print(result)


if __name__ == "__main__":
    main()
