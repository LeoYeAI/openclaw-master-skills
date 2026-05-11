#!/usr/bin/env python3
"""链上子网设置更新 — setSkillsURI 或 setMinStake (V2)
重要：这些调用发送到 SubnetNFT 合约，而非 AWPRegistry！
仅 NFT 所有者可操作。需要 ETH 作为 gas。
"""
import re

from awp_lib import *


def encode_set_skills_uri(subnet_id: int, uri: str) -> str:
    """编码 setSkillsURI(uint256, string) — selector = 0x7c2f4cd6"""
    uri_bytes = uri.encode("utf-8")
    uri_len = len(uri_bytes)
    padded_len = ((uri_len + 31) // 32) * 32
    uri_hex = uri_bytes.hex().ljust(padded_len * 2, "0")

    selector = "0x7c2f4cd6"
    # tokenId
    p1 = pad_uint256(subnet_id)
    # offset 指向 string 数据（2 * 32 = 64 字节）
    p2 = pad_uint256(64)
    # string: length + padded data
    str_len = pad_uint256(uri_len)

    return selector + p1 + p2 + str_len + uri_hex


def encode_set_min_stake(subnet_id: int, min_stake: int) -> str:
    """编码 setMinStake(uint256, uint128) — selector = 0x63a9bbe5"""
    return encode_calldata("0x63a9bbe5", pad_uint256(subnet_id), pad_uint256(min_stake))


def main() -> None:
    # ── 参数解析 ──
    parser = base_parser("Update subnet settings: setSkillsURI or setMinStake")
    parser.add_argument("--subnet", required=True, help="Subnet ID")
    parser.add_argument("--skills-uri", default="", help="新的 skills URI")
    parser.add_argument("--min-stake", default="", help="新的最小质押量（wei）")
    args = parser.parse_args()

    subnet_id = validate_positive_int(args.subnet, "subnet")
    skills_uri: str = args.skills_uri
    min_stake_str: str = args.min_stake

    # 互斥验证
    if not skills_uri and not min_stake_str:
        die("Provide --skills-uri or --min-stake")
    if skills_uri and min_stake_str:
        die("Provide only one of --skills-uri or --min-stake per call")

    # 验证 min-stake
    min_stake: int = 0
    if min_stake_str:
        if not re.match(r"^[0-9]+$", min_stake_str):
            die("Invalid --min-stake: must be a non-negative integer (wei)")
        min_stake = int(min_stake_str)

    # ── 预检查 ──
    wallet_addr = get_wallet_address()
    registry = get_registry()
    subnet_nft = require_contract(registry, "subnetNFT")

    # ── 构建 calldata 并发送 ──
    if skills_uri:
        calldata = encode_set_skills_uri(subnet_id, skills_uri)
        step("setSkillsURI", subnet=subnet_id, skillsURI=skills_uri,
             target=f"SubnetNFT ({subnet_nft})")
    else:
        calldata = encode_set_min_stake(subnet_id, min_stake)
        step("setMinStake", subnet=subnet_id, minStake=min_stake_str,
             target=f"SubnetNFT ({subnet_nft})")

    result = wallet_send(args.token, subnet_nft, calldata)
    print(result)


if __name__ == "__main__":
    main()
