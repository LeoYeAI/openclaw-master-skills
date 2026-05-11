#!/usr/bin/env python3
"""链上子网生命周期管理 — activate/pause/resume (V2)
在调用前检查当前子网状态，防止无效的状态转换。
仅 SubnetNFT 所有者可操作。需要 ETH 作为 gas。
"""
from awp_lib import *

# 动作 → (所需前置状态, 合约 selector)
ACTION_CONFIG: dict[str, tuple[str, str]] = {
    "activate": ("Pending", "0xcead1c96"),   # activateSubnet(uint256)
    "pause":    ("Active",  "0x44e047ca"),   # pauseSubnet(uint256)
    "resume":   ("Paused",  "0x5364944c"),   # resumeSubnet(uint256)
}


def main() -> None:
    # ── 参数解析 ──
    parser = base_parser("Subnet lifecycle: activate / pause / resume")
    parser.add_argument("--subnet", required=True, help="Subnet ID")
    parser.add_argument("--action", required=True, choices=["activate", "pause", "resume"],
                        help="操作类型")
    args = parser.parse_args()

    subnet_id = validate_positive_int(args.subnet, "subnet")
    action: str = args.action

    # ── 预检查 ──
    wallet_addr = get_wallet_address()
    registry = get_registry()
    awp_registry = require_contract(registry, "awpRegistry")

    # ── 检查当前子网状态 ──
    subnet_info = api_get(f"subnets/{subnet_id}")
    if not isinstance(subnet_info, dict):
        die(f"Subnet #{subnet_id} not found")

    status = subnet_info.get("status")
    if not status or status == "null":
        die(f"Subnet #{subnet_id} not found")

    # 验证状态转换
    required_status, selector = ACTION_CONFIG[action]
    if status != required_status:
        die(f"Cannot {action}: subnet is {status} (must be {required_status})")

    # ── 发送交易 ──
    subnet_padded = pad_uint256(subnet_id)
    calldata = encode_calldata(selector, subnet_padded)

    step(f"{action}Subnet", subnet=subnet_id, currentStatus=status)
    result = wallet_send(args.token, awp_registry, calldata)
    print(result)


if __name__ == "__main__":
    main()
