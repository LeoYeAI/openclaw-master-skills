#!/usr/bin/env python3
"""链上 bind(address target) — 绑定到账户树中的目标（V2）
基于树的绑定，带反循环检查。
"""
from awp_lib import *


def main() -> None:
    parser = base_parser("On-chain bind to target address (V2)")
    parser.add_argument("--target", required=True, help="绑定目标地址")
    # 兼容旧参数名
    parser.add_argument("--principal", dest="target_alt", help=argparse.SUPPRESS)
    args = parser.parse_args()

    token: str = args.token
    target: str = args.target_alt if args.target_alt else args.target
    validate_address(target, "target")

    # 预检：获取钱包地址
    wallet_addr = get_wallet_address()

    # 获取合约注册表
    registry = get_registry()
    awp_registry = require_contract(registry, "awpRegistry")

    # 检查是否已绑定
    check = api_get(f"address/{wallet_addr}/check")
    if isinstance(check, dict):
        # V2: .boundTo; V1: .isRegisteredAgent + .ownerAddress
        bound_to = check.get("boundTo", "")
        is_agent = str(check.get("isRegisteredAgent", False)).lower()
        if is_agent == "true":
            bound_to = check.get("ownerAddress", "")

        zero_addr = "0x0000000000000000000000000000000000000000"
        if bound_to and bound_to != "null" and bound_to != zero_addr:
            print(json.dumps({
                "status": "already_bound",
                "address": wallet_addr,
                "boundTo": bound_to,
            }))
            return

    # bind(address) selector = 0x81bac14f + ABI 编码地址
    calldata = encode_calldata("0x81bac14f", pad_address(target))

    step("bind", address=wallet_addr, target=target)
    result = wallet_send(token, awp_registry, calldata)
    print(result)


if __name__ == "__main__":
    main()
