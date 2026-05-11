#!/usr/bin/env python3
"""完全 gasless 的子网注册 — 通过双重 EIP-712 签名（V2）"""

from __future__ import annotations

import json
import re
import time

from awp_lib import (
    API_BASE,
    api_get,
    api_post,
    base_parser,
    build_eip712,
    die,
    get_eip712_domain,
    get_registry,
    get_wallet_address,
    hex_to_int,
    info,
    pad_address,
    require_contract,
    rpc_call,
    step,
    wallet_sign_typed_data,
)


def parse_args() -> tuple[str, str, str, str, int, str, str]:
    """解析命令行参数，返回 (token, name, symbol, salt, min_stake, subnet_manager, skills_uri)"""
    parser = base_parser("AWP gasless subnet registration via dual EIP-712 signatures")
    parser.add_argument("--name", required=True, help="子网名称")
    parser.add_argument("--symbol", required=True, help="子网代币符号")
    parser.add_argument(
        "--salt",
        default="0x0000000000000000000000000000000000000000000000000000000000000000",
        help="bytes32 salt（默认全零）",
    )
    parser.add_argument("--min-stake", default="0", help="最低质押量（wei）")
    parser.add_argument(
        "--subnet-manager",
        default="0x0000000000000000000000000000000000000000",
        help="子网管理者地址",
    )
    parser.add_argument("--skills-uri", default="", help="技能 URI")
    args = parser.parse_args()

    # 验证 min-stake 是非负整数
    if not re.match(r"^[0-9]+$", args.min_stake):
        die("Invalid --min-stake: must be a non-negative integer (wei)")
    min_stake = int(args.min_stake)

    # 验证 subnet-manager 地址格式
    if not re.match(r"^0x[0-9a-fA-F]{40}$", args.subnet_manager):
        die("Invalid --subnet-manager: must be 0x + 40 hex chars")

    # 验证 salt 格式（bytes32）
    if not re.match(r"^0x[0-9a-fA-F]{64}$", args.salt):
        die("Invalid --salt: must be 0x + 64 hex chars (bytes32)")

    return args.token, args.name, args.symbol, args.salt, min_stake, args.subnet_manager, args.skills_uri


def main() -> None:
    """主流程"""
    token, name, symbol, salt, min_stake, subnet_manager, skills_uri = parse_args()

    # Step 1: 获取 registry
    step("fetch_registry")
    registry = get_registry()
    awp_registry = require_contract(registry, "awpRegistry")
    awp_token = require_contract(registry, "awpToken")
    domain = get_eip712_domain(registry)
    chain_id = domain["chainId"]

    # Step 2: 获取钱包地址
    step("get_wallet_address")
    wallet_addr = get_wallet_address()

    # Step 3: 获取 initialAlphaPrice — selector = 0x6d345eea
    step("get_initial_alpha_price")
    price_hex = rpc_call(awp_registry, "0x6d345eea")
    if not price_hex or price_hex in ("0x", "null"):
        die("initialAlphaPrice() returned empty — is AWP_REGISTRY correct?")
    initial_alpha_price = hex_to_int(price_hex)

    # LP_COST = 100M * 10^18 * initialAlphaPrice / 10^18
    lp_cost = 100_000_000 * 10**18 * initial_alpha_price // 10**18

    # Step 4: 获取 nonces
    step("get_nonces")

    # Registry nonce — 先尝试 API，回退到 RPC
    nonce_resp = api_get(f"nonce/{wallet_addr}")
    registry_nonce: int | None = None
    if isinstance(nonce_resp, dict):
        raw = nonce_resp.get("nonce")
        if raw is not None and raw != "null":
            registry_nonce = int(raw)

    if registry_nonce is None:
        # 回退: 从合约读取 nonce
        addr_padded = pad_address(wallet_addr)
        registry_nonce_hex = rpc_call(awp_registry, f"0x7ecebe00{addr_padded}")
        registry_nonce = hex_to_int(registry_nonce_hex)

    # AWPToken permit nonce（始终从 RPC 读取 — 没有 REST 端点）
    addr_padded = pad_address(wallet_addr)
    permit_nonce_hex = rpc_call(awp_token, f"0x7ecebe00{addr_padded}")
    permit_nonce = hex_to_int(permit_nonce_hex)

    # Step 5: 截止时间（1 小时后）
    deadline = int(time.time()) + 3600

    # Step 6: 签署 ERC-2612 Permit
    step("sign_permit")
    permit_domain = {
        "name": "AWP Token",
        "version": "1",
        "chainId": chain_id,
        "verifyingContract": awp_token,
    }
    permit_data = build_eip712(
        permit_domain,
        "Permit",
        [
            {"name": "owner", "type": "address"},
            {"name": "spender", "type": "address"},
            {"name": "value", "type": "uint256"},
            {"name": "nonce", "type": "uint256"},
            {"name": "deadline", "type": "uint256"},
        ],
        {
            "owner": wallet_addr,
            "spender": awp_registry,
            "value": lp_cost,
            "nonce": permit_nonce,
            "deadline": deadline,
        },
    )
    permit_signature = wallet_sign_typed_data(token, permit_data)

    # Step 7: 签署 EIP-712 RegisterSubnet（V2 包含 skillsURI 字段）
    step("sign_register_subnet")
    register_data = build_eip712(
        domain,
        "RegisterSubnet",
        [
            {"name": "user", "type": "address"},
            {"name": "name", "type": "string"},
            {"name": "symbol", "type": "string"},
            {"name": "subnetManager", "type": "address"},
            {"name": "salt", "type": "bytes32"},
            {"name": "minStake", "type": "uint128"},
            {"name": "skillsURI", "type": "string"},
            {"name": "nonce", "type": "uint256"},
            {"name": "deadline", "type": "uint256"},
        ],
        {
            "user": wallet_addr,
            "name": name,
            "symbol": symbol,
            "subnetManager": subnet_manager,
            "salt": salt,
            "minStake": min_stake,
            "skillsURI": skills_uri,
            "nonce": registry_nonce,
            "deadline": deadline,
        },
    )
    register_signature = wallet_sign_typed_data(token, register_data)

    # Step 8: 提交到 relay
    step("submit_relay")
    relay_body = {
        "user": wallet_addr,
        "name": name,
        "symbol": symbol,
        "subnetManager": subnet_manager,
        "salt": salt,
        "minStake": str(min_stake),
        "skillsURI": skills_uri,
        "deadline": deadline,
        "permitSignature": permit_signature,
        "registerSignature": register_signature,
    }

    relay_url = f"{API_BASE}/relay/register-subnet"
    info(f"Submitting to {relay_url}")
    http_code, body = api_post(relay_url, relay_body)

    if 200 <= http_code < 300:
        print(json.dumps(body) if isinstance(body, dict) else body)
    else:
        die(f"Relay returned HTTP {http_code}: {body}")


if __name__ == "__main__":
    main()
