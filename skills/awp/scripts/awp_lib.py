"""AWP 脚本共享库 — API 调用、钱包命令、ABI 编码、输入验证"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
import urllib.error
from decimal import Decimal
from pathlib import Path

_UINT256_MAX = 2**256 - 1

# ── 配置 ────────────────────────────────────────

API_BASE = os.environ.get("AWP_API_URL", "https://tapi.awp.sh/api")
RPC_URL = os.environ.get("EVM_RPC_URL", "https://mainnet.base.org")


# ── 输出 ────────────────────────────────────────

def info(msg: str) -> None:
    """输出 JSON 信息到 stderr"""
    print(json.dumps({"info": msg}), file=sys.stderr)


def step(name: str, **kwargs: object) -> None:
    """输出执行步骤到 stderr"""
    print(json.dumps({"step": name, **kwargs}), file=sys.stderr)


def die(msg: str) -> None:
    """输出错误到 stderr 并退出"""
    print(json.dumps({"error": msg}), file=sys.stderr)
    sys.exit(1)


# ── HTTP ────────────────────────────────────────

def api_get(path: str) -> dict | list | None:
    """GET {API_BASE}/{path}，返回解析后的 JSON"""
    url = f"{API_BASE}/{path.lstrip('/')}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except (urllib.error.URLError, json.JSONDecodeError, OSError) as e:
        die(f"API request failed: {url} — {e}")
        return None  # unreachable


def api_post(url: str, body: dict) -> tuple[int, dict | str]:
    """POST JSON，返回 (http_code, parsed_body)"""
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body_str = e.read().decode() if e.fp else ""
        try:
            return e.code, json.loads(body_str)
        except json.JSONDecodeError:
            return e.code, body_str
    except (urllib.error.URLError, OSError) as e:
        die(f"POST failed: {url} — {e}")
        return 0, ""  # unreachable


def rpc_call(to: str, data: str) -> str:
    """eth_call via JSON-RPC，返回 hex result"""
    payload = {
        "jsonrpc": "2.0", "method": "eth_call",
        "params": [{"to": to, "data": data}, "latest"], "id": 1,
    }
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        RPC_URL, data=body, method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            # 检查 RPC 级别错误（revert 等）
            if "error" in result:
                err = result["error"]
                msg = err.get("message", err) if isinstance(err, dict) else err
                die(f"RPC error: {msg}")
            return result.get("result", "")
    except (urllib.error.URLError, json.JSONDecodeError, OSError) as e:
        die(f"RPC call failed: {e}")
        return ""  # unreachable


def hex_to_int(val: str) -> int:
    """将 hex 字符串转为 int，失败则 die"""
    if not val or val in ("null", "0x"):
        die("RPC returned empty/null value")
    return int(val, 16)


# ── 钱包命令 ─────────────────────────────────────

def wallet_cmd(args: list[str]) -> str:
    """执行 awp-wallet 命令，返回 stdout"""
    try:
        result = subprocess.run(
            ["awp-wallet"] + args,
            capture_output=True, text=True, timeout=60,
        )
    except subprocess.TimeoutExpired:
        die(f"awp-wallet {args[0]} timed out after 60s")
        return ""  # unreachable
    if result.returncode != 0:
        die(f"awp-wallet {args[0]} failed: {result.stderr.strip() or result.stdout.strip()}")
    return result.stdout.strip()


def get_wallet_address() -> str:
    """获取钱包地址（不需要 token），验证返回的地址格式"""
    out = wallet_cmd(["receive"])
    try:
        addr = json.loads(out).get("eoaAddress")
    except json.JSONDecodeError:
        die(f"Invalid wallet response: {out}")
        return ""  # unreachable
    if not addr or addr == "null":
        die("Wallet address is empty")
    if not ADDR_RE.match(addr):
        die(f"Wallet returned invalid address format: {addr}")
    return addr


def wallet_send(token: str, to: str, data: str, value: str = "0") -> str:
    """发送原始合约调用（calldata），返回结果 JSON。

    awp-wallet send 只支持代币转账，不支持 calldata。
    此函数通过 wallet-raw-call.mjs 桥接脚本调用 awp-wallet 内部签名模块。
    """
    bridge = str(Path(__file__).parent / "wallet-raw-call.mjs")
    args = ["node", bridge, "--token", token, "--to", to, "--data", data, "--value", value]
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        die("wallet-raw-call timed out after 120s")
        return ""  # unreachable
    if result.returncode != 0:
        die(f"wallet-raw-call failed: {result.stderr.strip() or result.stdout.strip()}")
    return result.stdout.strip()


def wallet_approve(token: str, asset: str, spender: str, amount: str) -> str:
    """授权代币，返回结果 JSON"""
    return wallet_cmd(["approve", "--token", token, "--asset", asset,
                        "--spender", spender, "--amount", amount])


def wallet_sign_typed_data(token: str, data: dict) -> str:
    """EIP-712 签名，返回 signature hex"""
    out = wallet_cmd(["sign-typed-data", "--token", token, "--data", json.dumps(data)])
    try:
        sig = json.loads(out).get("signature", "")
    except json.JSONDecodeError:
        die(f"Invalid sign response: {out}")
        return ""  # unreachable
    if not sig:
        die("Empty signature returned")
    return sig


def wallet_balance(token: str, asset: str | None = None) -> str:
    """查询余额"""
    args = ["balance", "--token", token]
    if asset:
        args += ["--asset", asset]
    return wallet_cmd(args)


def wallet_status(token: str) -> str:
    """查询钱包状态（地址、session 有效性）"""
    return wallet_cmd(["status", "--token", token])


# ── 合约注册表 ───────────────────────────────────

def get_registry() -> dict:
    """获取 /registry 并返回完整字典"""
    reg = api_get("registry")
    if not isinstance(reg, dict):
        die("Invalid /registry response")
    return reg


def require_contract(registry: dict, key: str) -> str:
    """从 registry 中获取合约地址，为空则 die"""
    addr = registry.get(key)
    if not addr or addr == "null":
        die(f"Failed to get {key} from /registry")
    return addr


# ── ABI 编码 ─────────────────────────────────────

def pad_address(addr: str) -> str:
    """将 0x 地址补齐为 64 字符（左补零），验证 hex 格式"""
    raw = addr.lower()
    if raw.startswith("0x"):
        raw = raw[2:]
    if not re.match(r"^[0-9a-f]+$", raw):
        die(f"pad_address: invalid hex characters in address: {addr}")
    if len(raw) > 64:
        die(f"pad_address: address too long after stripping 0x prefix: {addr}")
    return raw.zfill(64)


def pad_uint256(val: int) -> str:
    """将整数编码为 64 字符 hex（必须在 uint256 范围内）"""
    if val < 0 or val > _UINT256_MAX:
        die(f"pad_uint256: value out of uint256 range: {val}")
    return format(val, "064x")


def to_wei(human_amount: str) -> int:
    """人类可读 AWP 数量转 wei（使用 Decimal 避免浮点精度丢失）"""
    try:
        result = int(Decimal(human_amount) * Decimal(10**18))
    except (ValueError, TypeError, ArithmeticError) as e:
        die(f"to_wei: invalid amount: {human_amount} ({e})")
        return 0  # unreachable
    if result <= 0:
        die(f"to_wei: converted amount is zero (input: {human_amount})")
    return result


def days_to_seconds(days: str) -> int:
    """天数转秒数（使用 Decimal 避免浮点截断）"""
    try:
        result = int(Decimal(days) * Decimal(86400))
    except (ValueError, TypeError, ArithmeticError) as e:
        die(f"days_to_seconds: invalid input: {days} ({e})")
        return 0  # unreachable
    if result <= 0:
        die(f"days_to_seconds: result is zero (input: {days} days)")
    return result


def encode_calldata(selector: str, *params: str) -> str:
    """拼接 selector + 参数，验证 selector 格式（0x + 8 hex）"""
    if not re.match(r"^0x[0-9a-fA-F]{8}$", selector):
        die(f"encode_calldata: invalid selector format: {selector} (expected 0x + 8 hex chars)")
    return selector + "".join(params)


# ── 输入验证 ─────────────────────────────────────

ADDR_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")


def validate_address(addr: str, name: str = "address") -> str:
    """验证以太坊地址格式"""
    if not ADDR_RE.match(addr):
        die(f"Invalid --{name}: must be 0x + 40 hex chars")
    return addr


def validate_positive_number(val: str, name: str = "amount") -> str:
    """验证正数（允许小数）"""
    if not re.match(r"^[0-9]+\.?[0-9]*$", val):
        die(f"Invalid --{name}: must be a positive number")
    if Decimal(val) <= 0:
        die(f"Invalid --{name}: must be > 0")
    return val


def validate_positive_int(val: str, name: str = "id") -> int:
    """验证正整数（uint256 范围内）"""
    if not re.match(r"^[0-9]+$", val):
        die(f"Invalid --{name}: must be a positive integer > 0")
    n = int(val)
    if n <= 0 or n > _UINT256_MAX:
        die(f"Invalid --{name}: must be > 0 and <= 2^256-1")
    return n


# ── EIP-712 构建 ─────────────────────────────────

def get_eip712_domain(registry: dict) -> dict:
    """从 registry 获取 EIP-712 domain 信息"""
    domain = registry.get("eip712Domain", {})
    name = domain.get("name")
    version = domain.get("version")
    chain_id = domain.get("chainId")
    contract = domain.get("verifyingContract")

    # fallback
    if not name:
        name = "AWPRegistry"
        version = "1"
        info("eip712Domain not in registry, using fallback")
    if not version:
        version = "1"
    if not chain_id:
        chain_id = registry.get("chainId")
    if not contract:
        contract = registry.get("awpRegistry")

    if not chain_id or not contract:
        die("Cannot determine EIP-712 domain from /registry")

    return {
        "name": name,
        "version": str(version),
        "chainId": int(chain_id),
        "verifyingContract": contract,
    }


def build_eip712(domain: dict, primary_type: str, type_fields: list[dict],
                 message: dict) -> dict:
    """构建完整 EIP-712 typed data"""
    return {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            primary_type: type_fields,
        },
        "primaryType": primary_type,
        "domain": domain,
        "message": message,
    }


# ── 通用参数解析 ─────────────────────────────────

def base_parser(description: str) -> argparse.ArgumentParser:
    """创建带 --token 的基础参数解析器"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--token", required=True, help="awp-wallet session token")
    return parser
