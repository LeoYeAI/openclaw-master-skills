#!/usr/bin/env python3
"""
CL LP Auto-Rebalancer v1 — Uniswap V3 Concentrated Liquidity on Base
Dynamically adjusts tick range based on volatility and trend:
  - Low volatility  → narrow range (high fee capture)
  - High volatility → wide range (less IL, fewer rebalances)
  - Trend-adaptive asymmetric ranges

Uses OKX DEX API (via onchainos CLI) + OnchainOS Agentic Wallet (TEE signing).
Designed for OpenClaw cron integration.
"""

import fcntl
import json
import math
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ── Load .env if present ────────────────────────────────────────────────────


def _load_env():
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                k = k.strip()
                if k.startswith("export "):
                    k = k[7:].strip()
                os.environ.setdefault(k, v.strip())


_load_env()

# ── Load Config ─────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "config.json"

if CONFIG_FILE.exists():
    CFG = json.loads(CONFIG_FILE.read_text())
else:
    print("ERROR: config.json not found", file=sys.stderr)
    sys.exit(1)

# ── API Keys ────────────────────────────────────────────────────────────────

OKX_API_KEY = os.environ.get("OKX_API_KEY", "")
OKX_SECRET = os.environ.get("OKX_SECRET_KEY", "")
OKX_PASSPHRASE = os.environ.get("OKX_PASSPHRASE", "")

# ── Config values ───────────────────────────────────────────────────────────

INVESTMENT_ID = CFG["investment_id"]
POOL_CHAIN = CFG["pool_chain"]
FEE_TIER = CFG["fee_tier"]
TICK_SPACING = CFG["tick_spacing"]
TOKEN0 = CFG["token0"]
TOKEN1 = CFG["token1"]
ETH_ADDR = TOKEN0["address"]
USDC_ADDR = TOKEN1["address"]
CHAIN_ID = CFG.get("chain_id", "8453")
PLATFORM_ID = CFG.get("platform_id", "68")  # onchainos defi platform ID
NATIVE_TOKEN = CFG.get("native_token", "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
PAIR_NAME = f"{TOKEN0['symbol']}/{TOKEN1['symbol']}"
CHAIN_LABEL = POOL_CHAIN.capitalize()

_rm = CFG["range_mult"]
RANGE_MULT = (
    _rm
    if isinstance(_rm, dict)
    else {"low": _rm * 0.75, "medium": _rm, "high": _rm * 1.25, "extreme": _rm * 1.5}
)
MIN_RANGE_PCT = CFG["min_range_pct"]
MAX_RANGE_PCT = CFG["max_range_pct"]
ASYM_FACTOR = CFG["asym_factor"]

MIN_POSITION_AGE = CFG["min_position_age_seconds"]
MAX_REBALANCES_24H = CFG["max_rebalances_24h"]
GAS_TO_FEE_RATIO = CFG["gas_to_fee_ratio"]
MAX_IL_TOLERANCE_PCT = CFG["max_il_tolerance_pct"]

STOP_LOSS_PCT = CFG["stop_loss_pct"]
TRAILING_STOP_PCT = CFG["trailing_stop_pct"]
SLIPPAGE_PCT = CFG["slippage_pct"]
GAS_RESERVE_ETH = CFG["gas_reserve_eth"]
MIN_TRADE_USD = CFG["min_trade_usd"]

QUIET_INTERVAL = CFG["quiet_interval_seconds"]
MAX_CONSECUTIVE_ERRORS = CFG["max_consecutive_errors"]
COOLDOWN_AFTER_ERRORS = CFG["cooldown_after_errors_seconds"]


# ── Notification credentials ───────────────────────────────────────────────


def _resolve_discord_channel_id() -> str:
    """Resolve Discord channel ID: env override > openclaw.json guilds config."""
    env_id = os.environ.get("DISCORD_CHANNEL_ID", "")
    if env_id:
        return env_id
    try:
        cfg_path = Path.home() / ".openclaw" / "openclaw.json"
        if cfg_path.exists():
            cfg = json.loads(cfg_path.read_text())
            guilds = cfg.get("channels", {}).get("discord", {}).get("guilds", {})
            for _gid, guild_cfg in guilds.items():
                channels = guild_cfg.get("channels", {})
                for ch_id, ch_cfg in channels.items():
                    if ch_cfg.get("allow"):
                        return ch_id
    except Exception:
        pass
    return ""


DISCORD_CHANNEL_ID = _resolve_discord_channel_id()


def _get_discord_token() -> str:
    env_token = os.environ.get("DISCORD_BOT_TOKEN", "")
    if env_token:
        return env_token
    cfg_path = Path.home() / ".openclaw" / "openclaw.json"
    if cfg_path.exists():
        try:
            cfg = json.loads(cfg_path.read_text())
            return cfg.get("channels", {}).get("discord", {}).get("token", "")
        except Exception:
            pass
    return ""


def _get_telegram_config() -> tuple:
    """Return (bot_token, chat_id). Checks env first, then zeroclaw config."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if token and chat_id:
        return token, chat_id
    for cfg_dir in ["zeroclaw-strategy", "zeroclaw", "openclaw"]:
        cfg_path = Path.home() / f".{cfg_dir}" / "config.toml"
        if cfg_path.exists():
            try:
                text = cfg_path.read_text()
                in_tg = False
                for line in text.splitlines():
                    stripped = line.strip()
                    if stripped.startswith("[") and "telegram" in stripped.lower():
                        in_tg = True
                        continue
                    if stripped.startswith("[") and in_tg:
                        break
                    if in_tg and "=" in stripped:
                        k, v = stripped.split("=", 1)
                        k, v = k.strip(), v.strip().strip('"').strip("'")
                        if k == "bot_token" and not token:
                            token = v
                        if k == "chat_id" and not chat_id:
                            chat_id = v
            except Exception:
                pass
    return token, chat_id


TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID = _get_telegram_config()

# ── External portfolio (optional) ─────────────────────────────────────────

HL_WALLET_ADDR = os.environ.get("HL_WALLET_ADDR", "")
BINANCE_API_KEY = os.environ.get("BINANCE_API_KEY", "")
BINANCE_SECRET_KEY = os.environ.get("BINANCE_SECRET_KEY", "")


def _query_hl_balance() -> float:
    """Query Hyperliquid account value via public info API (no auth needed)."""
    if not HL_WALLET_ADDR:
        return 0.0
    try:
        import urllib.request

        payload = json.dumps(
            {"type": "clearinghouseState", "user": HL_WALLET_ADDR}
        ).encode()
        req = urllib.request.Request(
            "https://api.hyperliquid.xyz/info",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        value = float(data.get("marginSummary", {}).get("accountValue", 0))
        # Also check spot balances
        try:
            spot_payload = json.dumps(
                {"type": "spotClearinghouseState", "user": HL_WALLET_ADDR}
            ).encode()
            spot_req = urllib.request.Request(
                "https://api.hyperliquid.xyz/info",
                data=spot_payload,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(spot_req, timeout=10) as resp2:
                spot_data = json.loads(resp2.read())
            for bal in spot_data.get("balances", []):
                if bal.get("coin") == "USDC":
                    value += float(bal.get("total", 0))
        except Exception:
            pass
        return value
    except Exception:
        return 0.0


def _query_binance_balance() -> float:
    """Query Binance Futures USDT balance (signed request)."""
    if not BINANCE_API_KEY or not BINANCE_SECRET_KEY:
        return 0.0
    try:
        import hashlib
        import hmac
        import urllib.request

        ts = int(time.time() * 1000)
        query = f"timestamp={ts}&recvWindow=10000"
        sig = hmac.new(
            BINANCE_SECRET_KEY.encode(), query.encode(), hashlib.sha256
        ).hexdigest()
        url = f"https://fapi.binance.com/fapi/v2/balance?{query}&signature={sig}"
        req = urllib.request.Request(url, headers={"X-MBX-APIKEY": BINANCE_API_KEY})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        for asset in data:
            if asset.get("asset") == "USDT":
                return float(asset.get("balance", 0))
        return 0.0
    except Exception:
        return 0.0


def query_external_portfolio() -> dict:
    """Query all external platform balances. Returns {platform: usd_value}."""
    result = {}
    hl = _query_hl_balance()
    if hl > 0:
        result["HL"] = round(hl, 2)
    bn = _query_binance_balance()
    if bn > 0:
        result["Binance"] = round(bn, 2)
    return result


# ── Multi-Timeframe settings (from grid-trading) ───────────────────────────

MTF_SHORT_PERIOD = 5
MTF_MEDIUM_PERIOD = 12
MTF_LONG_PERIOD = 48
MTF_STRUCTURE_PERIOD = 96
EMA_PERIOD = 20

# ── Paths ───────────────────────────────────────────────────────────────────

STATE_FILE = SCRIPT_DIR / "cl_lp_state.json"
LOG_FILE = SCRIPT_DIR / "cl_lp.log"
MAX_LOG_BYTES = 1_000_000


# ── Logging ─────────────────────────────────────────────────────────────────


def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, file=sys.stderr)
    try:
        if LOG_FILE.exists() and LOG_FILE.stat().st_size > MAX_LOG_BYTES:
            content = LOG_FILE.read_text()
            lines = content.splitlines()
            # Atomic log rotation
            fd, tmp = tempfile.mkstemp(dir=LOG_FILE.parent, suffix=".log.tmp")
            try:
                with os.fdopen(fd, "w") as f:
                    f.write("\n".join(lines[len(lines) // 2 :]) + "\n")
                os.replace(tmp, LOG_FILE)
            except Exception as e:
                print(f"WARNING: log rotation failed: {e}", file=sys.stderr)
                try:
                    os.unlink(tmp)
                except OSError:
                    pass
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except Exception as e:
        print(f"WARNING: log write failed: {e}", file=sys.stderr)


# ── Safe datetime parsing ──────────────────────────────────────────────────


def _safe_isoparse(s: str, default: datetime | None = None) -> datetime | None:
    """Parse ISO datetime string safely. Returns default on failure."""
    if not s:
        return default
    try:
        return datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return default


# ── Process lock ───────────────────────────────────────────────────────────

LOCK_FILE = SCRIPT_DIR / ".cl_lp.lock"
_lock_fd = None


def _acquire_lock() -> bool:
    """Acquire exclusive process lock. Returns False if another instance is running."""
    global _lock_fd
    try:
        _lock_fd = open(LOCK_FILE, "w")
        fcntl.flock(_lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        _lock_fd.write(str(os.getpid()))
        _lock_fd.flush()
        return True
    except (OSError, IOError):
        if _lock_fd:
            _lock_fd.close()
            _lock_fd = None
        return False


def _release_lock():
    """Release process lock."""
    global _lock_fd
    if _lock_fd:
        try:
            fcntl.flock(_lock_fd, fcntl.LOCK_UN)
            _lock_fd.close()
        except (OSError, IOError):
            pass
        _lock_fd = None
    try:
        LOCK_FILE.unlink(missing_ok=True)
    except OSError:
        pass


# ── onchainos CLI wrapper ───────────────────────────────────────────────────


def onchainos_cmd(args: list[str], timeout: int = 30) -> dict | None:
    """Run onchainos CLI command, return parsed JSON."""
    env = os.environ.copy()
    env.setdefault("OKX_API_KEY", OKX_API_KEY)
    env.setdefault("OKX_SECRET_KEY", OKX_SECRET)
    env.setdefault("OKX_PASSPHRASE", OKX_PASSPHRASE)
    try:
        result = subprocess.run(
            ["onchainos"] + args,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        output = result.stdout.strip() if result.stdout else ""
        if output:
            try:
                data = json.loads(output)
                if isinstance(data, dict) and "ok" in data:
                    return data
                return {
                    "ok": True,
                    "data": data if isinstance(data, list) else [data],
                }
            except json.JSONDecodeError:
                log(
                    f"onchainos invalid JSON: {' '.join(args[:3])} output={output[:100]}"
                )
        if result.returncode != 0:
            stderr = result.stderr.strip() if result.stderr else ""
            log(
                f"onchainos rc={result.returncode}: {' '.join(args[:3])} "
                f"{'stderr=' + stderr[:150] if stderr else 'no output'}"
            )
    except subprocess.TimeoutExpired:
        log(f"onchainos timeout: {' '.join(args[:3])}")
    except Exception as e:
        log(f"onchainos error: {e}")
    return None


# ── Wallet Address ──────────────────────────────────────────────────────────

# Auto-switch to the correct account if ACCOUNT_ID is set in config
_cfg_account_id = (
    CFG.get("account_id", "")
    or os.environ.get("ONCHAINOS_ACCOUNT_ID", "")
    or os.environ.get("ACCOUNT_ID", "")
)
if _cfg_account_id:
    try:
        result = subprocess.run(
            ["onchainos", "wallet", "switch", _cfg_account_id],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            print(
                f"WARNING: wallet switch to {_cfg_account_id} failed: "
                f"{result.stderr.strip()[:100] if result.stderr else 'unknown error'}",
                file=sys.stderr,
            )
    except Exception as e:
        print(f"WARNING: wallet switch failed: {e}", file=sys.stderr)


def _resolve_wallet_addr() -> str:
    env_addr = os.environ.get("WALLET_ADDR", "")
    if env_addr:
        return env_addr
    try:
        result = subprocess.run(
            ["onchainos", "wallet", "addresses"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout.strip())
            if data.get("ok") and data.get("data", {}).get("evm"):
                evm_addrs = data["data"]["evm"]
                for entry in evm_addrs:
                    if entry.get("chainIndex") == CHAIN_ID:
                        return entry["address"]
                return evm_addrs[0]["address"]
    except Exception as e:
        print(f"WARNING: wallet address resolution failed: {e}", file=sys.stderr)
    return ""


WALLET_ADDR = _resolve_wallet_addr()
if not WALLET_ADDR:
    print(
        "ERROR: No wallet address found. Login with `onchainos wallet login` or set WALLET_ADDR env.",
        file=sys.stderr,
    )

# ── Price & Balance ─────────────────────────────────────────────────────────


def get_eth_price() -> float | None:
    """Get ETH price from market kline (last close). More reliable than swap quote."""
    data = onchainos_cmd(
        [
            "market",
            "kline",
            "--address",
            ETH_ADDR,
            "--chain",
            POOL_CHAIN,
            "--bar",
            "1m",
            "--limit",
            "1",
        ],
        timeout=10,
    )
    if data and data.get("ok") and data.get("data"):
        candle = data["data"][0]
        try:
            # candle is [ts, open, high, low, close, vol, ...]
            if isinstance(candle, list) and len(candle) >= 5:
                return float(candle[4])  # close price
            elif isinstance(candle, dict):
                return float(candle.get("c", 0) or candle.get("close", 0))
        except (ValueError, TypeError, IndexError):
            pass
    return None


def get_balances(force: bool = False) -> tuple[float, float, bool]:
    """Get ETH and USDC balances via --all to avoid wallet-switch race condition."""
    account_id = _cfg_account_id
    base_args = ["wallet", "balance", "--chain", CHAIN_ID]
    if force:
        base_args.append("--force")
    if account_id:
        data = onchainos_cmd(base_args + ["--all"], timeout=15)
    else:
        data = onchainos_cmd(base_args, timeout=15)
    if not data or not data.get("ok") or not data.get("data"):
        log(f"Balance query failed, raw: {json.dumps(data)[:200] if data else 'None'}")
        return 0.0, 0.0, True
    eth, usdc = 0.0, 0.0
    if account_id:
        # --all returns {details: {accountId: {data: [{tokenAssets: [...]}]}}}
        acct_data = data["data"].get("details", {}).get(account_id)
        if not acct_data or not acct_data.get("data"):
            log(f"Balance: account {account_id} not found in --all response")
            return 0.0, 0.0, True
        for chain_detail in acct_data["data"]:
            for token in chain_detail.get("tokenAssets", []):
                if token.get("tokenAddress") == "" and token.get("symbol") == "ETH":
                    eth = float(token.get("balance", "0"))
                elif token.get("tokenAddress", "").lower() == USDC_ADDR.lower():
                    usdc = float(token.get("balance", "0"))
    else:
        details = data["data"].get("details", [])
        for chain_detail in details:
            for token in chain_detail.get("tokenAssets", []):
                if token.get("tokenAddress") == "" and token.get("symbol") == "ETH":
                    eth = float(token.get("balance", "0"))
                elif token.get("tokenAddress", "").lower() == USDC_ADDR.lower():
                    usdc = float(token.get("balance", "0"))
    return eth, usdc, False


def get_position_detail(token_id: str) -> dict:
    """Get LP position value and unclaimed fees via defi position-detail.

    Returns {"value": float, "unclaimed_fee_usd": float, "assets": list}.
    """
    result = {"value": 0.0, "unclaimed_fee_usd": 0.0, "assets": []}
    if not token_id or not WALLET_ADDR:
        return result
    data = onchainos_cmd(
        [
            "defi",
            "position-detail",
            "--address",
            WALLET_ADDR,
            "--chain",
            POOL_CHAIN,
            "--platform-id",
            PLATFORM_ID,
        ],
        timeout=20,
    )
    if not data or not data.get("ok") or not data.get("data"):
        return result
    try:
        for platform in data["data"]:
            for wallet in platform.get("walletIdPlatformDetailList", []):
                for network in wallet.get("networkHoldVoList", []):
                    for invest in network.get("investTokenBalanceVoList", []):
                        for pos in invest.get("positionList", []):
                            if str(pos.get("tokenId")) == str(token_id):
                                result["value"] = float(pos.get("totalValue", 0))
                                result["assets"] = pos.get("assetsTokenList", [])
                                # Sum unclaimed fees
                                for fee_info in pos.get("unclaimFeesDefiTokenInfo", []):
                                    result["unclaimed_fee_usd"] += float(
                                        fee_info.get("currencyAmount", 0)
                                    )
                                return result
    except (KeyError, ValueError, TypeError):
        pass
    return result


def get_position_value(token_id: str) -> float:
    """Get current LP position value in USD (backward compat wrapper)."""
    return get_position_detail(token_id)["value"]


def _query_all_positions() -> list[dict]:
    """Query all LP positions for this pool. Returns list of {tokenId, assets, value}."""
    if not WALLET_ADDR:
        return []
    data = onchainos_cmd(
        [
            "defi",
            "position-detail",
            "--address",
            WALLET_ADDR,
            "--chain",
            POOL_CHAIN,
            "--platform-id",
            PLATFORM_ID,
        ],
        timeout=20,
    )
    if not data or not data.get("ok") or not data.get("data"):
        return []
    result = []
    try:
        for platform in data["data"]:
            for wallet in platform.get("walletIdPlatformDetailList", []):
                for network in wallet.get("networkHoldVoList", []):
                    for invest in network.get("investTokenBalanceVoList", []):
                        for pos in invest.get("positionList", []):
                            tid = str(pos.get("tokenId", ""))
                            assets = pos.get("assetsTokenList", [])
                            value = sum(
                                float(a.get("currencyAmount", 0)) for a in assets
                            )
                            result.append(
                                {"tokenId": tid, "assets": assets, "value": value}
                            )
    except (KeyError, ValueError, TypeError):
        pass
    return result


def find_latest_token_id(after_token_id: str = "") -> str:
    """Query position-detail to find the latest LP token ID for this pool.

    If after_token_id is provided, only return a token_id numerically greater
    than it (i.e. newly created after the reference point). This prevents
    adopting old positions from previous deploys.
    """
    positions = _query_all_positions()
    if not positions:
        return ""
    if after_token_id:
        try:
            threshold = int(after_token_id)
            candidates = [p for p in positions if int(p["tokenId"]) > threshold]
            if candidates:
                return candidates[-1]["tokenId"]
            return ""
        except (ValueError, TypeError):
            pass
    return positions[-1]["tokenId"]


def cleanup_residual_positions(keep_token_id: str) -> int:
    """Redeem all positions except keep_token_id. Returns count of cleaned positions."""
    positions = _query_all_positions()
    cleaned = 0
    for pos in positions:
        tid = pos["tokenId"]
        if tid == keep_token_id or not tid:
            continue
        val = pos["value"]
        log(f"  Cleaning residual position #{tid} (${val:.2f})")
        ok = defi_redeem(tid)
        if ok:
            cleaned += 1
            log(f"  Redeemed #{tid}")
        else:
            log(f"  WARN: failed to redeem #{tid}")
    if cleaned:
        log(f"  Cleaned {cleaned} residual position(s)")
    return cleaned


# ── K-line / OHLC Data ──────────────────────────────────────────────────────


def get_kline_data(bar: str = "1H", limit: int = 24) -> list[dict] | None:
    data = onchainos_cmd(
        [
            "market",
            "kline",
            "--address",
            ETH_ADDR,
            "--chain",
            POOL_CHAIN,
            "--bar",
            bar,
            "--limit",
            str(limit),
        ],
        timeout=15,
    )
    if data and data.get("ok") and data.get("data"):
        candles = []
        for c in data["data"]:
            try:
                if isinstance(c, list) and len(c) >= 6:
                    candles.append(
                        {
                            "ts": int(c[0]),
                            "open": float(c[1]),
                            "high": float(c[2]),
                            "low": float(c[3]),
                            "close": float(c[4]),
                            "volume": float(c[5]),
                        }
                    )
                elif isinstance(c, dict):
                    candles.append(
                        {
                            "ts": int(c.get("ts", 0)),
                            "open": float(c.get("o", 0) or c.get("open", 0)),
                            "high": float(c.get("h", 0) or c.get("high", 0)),
                            "low": float(c.get("l", 0) or c.get("low", 0)),
                            "close": float(c.get("c", 0) or c.get("close", 0)),
                            "volume": float(c.get("vol", 0) or c.get("volume", 0)),
                        }
                    )
            except (ValueError, TypeError, IndexError):
                continue
        return candles if candles else None
    return None


def calc_kline_volatility(candles: list[dict]) -> float:
    """ATR as percentage of price."""
    if not candles or len(candles) < 2:
        return 0.0
    true_ranges = []
    for i in range(1, len(candles)):
        hi = candles[i]["high"]
        lo = candles[i]["low"]
        pc = candles[i - 1]["close"]
        tr = max(hi - lo, abs(hi - pc), abs(lo - pc))
        true_ranges.append(tr)
    atr = sum(true_ranges) / len(true_ranges)
    avg_price = sum(c["close"] for c in candles) / len(candles)
    return (atr / avg_price) * 100 if avg_price > 0 else 0.0


# ── EMA / Volatility / Multi-Timeframe ──────────────────────────────────────


def calc_ema(prices: list[float], period: int) -> float:
    if not prices:
        return 0.0
    if len(prices) < period:
        return sum(prices) / len(prices)
    k = 2 / (period + 1)
    ema = sum(prices[:period]) / period
    for p in prices[period:]:
        ema = p * k + ema * (1 - k)
    return ema


def calc_volatility(prices: list[float]) -> float:
    if len(prices) < 2:
        return 0.0
    mean = sum(prices) / len(prices)
    variance = sum((p - mean) ** 2 for p in prices) / len(prices)
    return math.sqrt(variance)


def analyze_multi_timeframe(history: list[float], price: float) -> dict:
    result = {
        "trend": "neutral",
        "strength": 0.0,
        "momentum_1h": 0.0,
        "momentum_4h": 0.0,
        "structure": "ranging",
        "ema_short": price,
        "ema_medium": price,
        "ema_long": price,
    }
    if len(history) < MTF_SHORT_PERIOD:
        return result

    ema_short = calc_ema(history, min(MTF_SHORT_PERIOD, len(history)))
    ema_medium = calc_ema(history, min(MTF_MEDIUM_PERIOD, len(history)))
    ema_long = calc_ema(history, min(MTF_LONG_PERIOD, len(history)))
    result["ema_short"] = round(ema_short, 2)
    result["ema_medium"] = round(ema_medium, 2)
    result["ema_long"] = round(ema_long, 2)

    if len(history) >= 12 and history[-12] > 0:
        result["momentum_1h"] = round((price - history[-12]) / history[-12] * 100, 3)
    if len(history) >= 48 and history[-48] > 0:
        result["momentum_4h"] = round((price - history[-48]) / history[-48] * 100, 3)

    if ema_long > 0:
        if ema_short > ema_medium > ema_long:
            result["trend"] = "bullish"
            spread = (ema_short - ema_long) / ema_long * 100
            result["strength"] = round(min(spread / 2.0, 1.0), 3)
        elif ema_short < ema_medium < ema_long:
            result["trend"] = "bearish"
            spread = (ema_long - ema_short) / ema_long * 100
            result["strength"] = round(min(spread / 2.0, 1.0), 3)

    if len(history) >= MTF_STRUCTURE_PERIOD:
        seg_len = MTF_STRUCTURE_PERIOD // 4
        segments = [
            history[-(i + 1) * seg_len : -i * seg_len or None] for i in range(3, -1, -1)
        ]
        seg_highs = [max(s) for s in segments if s]
        seg_lows = [min(s) for s in segments if s]
        hh = all(seg_highs[i] >= seg_highs[i - 1] for i in range(1, len(seg_highs)))
        hl = all(seg_lows[i] >= seg_lows[i - 1] for i in range(1, len(seg_lows)))
        lh = all(seg_highs[i] <= seg_highs[i - 1] for i in range(1, len(seg_highs)))
        ll = all(seg_lows[i] <= seg_lows[i - 1] for i in range(1, len(seg_lows)))
        if hh and hl:
            result["structure"] = "uptrend"
        elif lh and ll:
            result["structure"] = "downtrend"

    return result


# ── Tick Math ───────────────────────────────────────────────────────────────


def _decimal_adjustment() -> float:
    """10^(token1_decimals - token0_decimals) for tick <-> human price conversion."""
    return 10 ** (TOKEN1["decimals"] - TOKEN0["decimals"])


def price_to_tick(price: float, tick_spacing: int = TICK_SPACING) -> int:
    """Convert human-readable price (token1/token0, e.g. USDC/WETH) to nearest valid tick."""
    if price <= 0:
        return 0
    raw_price = price * _decimal_adjustment()  # Adjust for decimal difference
    raw = math.floor(math.log(raw_price) / math.log(1.0001))
    return (raw // tick_spacing) * tick_spacing


def tick_to_price(tick: int) -> float:
    """Convert tick to human-readable price (token1/token0)."""
    return 1.0001**tick / _decimal_adjustment()


# ── Volatility Regime → Range Calculation ───────────────────────────────────


def classify_volatility(atr_pct: float) -> str:
    if atr_pct < 1.5:
        return "low"
    elif atr_pct < 3.0:
        return "medium"
    elif atr_pct < 5.0:
        return "high"
    else:
        return "extreme"


def calc_optimal_range(price: float, atr_pct: float, mtf: dict | None = None) -> dict:
    """Calculate optimal tick range based on volatility and trend.
    Returns {lower_price, upper_price, tick_lower, tick_upper, regime, half_width_pct}."""
    regime = classify_volatility(atr_pct)
    mult = RANGE_MULT.get(regime, 3.0)
    half_width_pct = atr_pct * mult

    # Clamp to min/max
    half_width_pct = max(MIN_RANGE_PCT, min(MAX_RANGE_PCT, half_width_pct))

    # Trend-adaptive asymmetry
    lower_pct = half_width_pct
    upper_pct = half_width_pct

    if mtf:
        trend = mtf.get("trend", "neutral")
        strength = mtf.get("strength", 0)
        if strength > 0.2:
            asym = ASYM_FACTOR * strength
            if trend == "bullish":
                # Widen upside, narrow downside
                upper_pct = half_width_pct * (1 + asym)
                lower_pct = half_width_pct * (1 - asym)
            elif trend == "bearish":
                # Widen downside, narrow upside
                lower_pct = half_width_pct * (1 + asym)
                upper_pct = half_width_pct * (1 - asym)

    lower_price = price * (1 - lower_pct / 100)
    upper_price = price * (1 + upper_pct / 100)

    tick_lower = price_to_tick(lower_price)
    tick_upper = price_to_tick(upper_price)

    # Ensure tick_upper > tick_lower by at least 1 tick_spacing
    if tick_upper <= tick_lower:
        tick_upper = tick_lower + TICK_SPACING

    return {
        "lower_price": round(lower_price, 2),
        "upper_price": round(upper_price, 2),
        "tick_lower": tick_lower,
        "tick_upper": tick_upper,
        "regime": regime,
        "half_width_pct": round(half_width_pct, 2),
        "lower_pct": round(lower_pct, 2),
        "upper_pct": round(upper_pct, 2),
    }


# ── Rebalance Trigger Logic ────────────────────────────────────────────────


def check_rebalance_triggers(
    price: float,
    state: dict,
    atr_pct: float,
    mtf: dict | None = None,
) -> dict | None:
    """Check if rebalancing is needed. Returns trigger info or None."""
    position = state.get("position")
    if not position or not position.get("tick_lower"):
        return None

    tick_lower = position["tick_lower"]
    tick_upper = position["tick_upper"]
    lower_price = tick_to_price(tick_lower)
    upper_price = tick_to_price(tick_upper)

    # [1] Out of range — mandatory
    if price < lower_price or price > upper_price:
        side = "below" if price < lower_price else "above"
        return {"trigger": "out_of_range", "priority": "mandatory", "detail": side}

    # [2] Higher yield pool detected — TODO: requires hourly yield API
    # Trigger when another pool consistently outperforms for 1+ hour.
    # Data source not yet available; placeholder for future implementation.

    return None


# ── Risk Checks (layered) ──────────────────────────────────────────────────


def run_risk_checks(
    state: dict,
    price: float,
    total_usd: float,
    trigger: dict | None,
) -> str | None:
    """Run layered risk checks. Returns skip/reject reason or None (pass)."""
    # [1] Stop triggered
    if state.get("stop_triggered"):
        return f"stop_active: {state['stop_triggered']}"

    # [2] Circuit breaker
    errors = state.get("errors", {})
    if not isinstance(errors, dict):
        errors = {"consecutive": 0, "cooldown_until": None}
        state["errors"] = errors
    if errors.get("consecutive", 0) >= MAX_CONSECUTIVE_ERRORS:
        cooldown_dt = _safe_isoparse(errors.get("cooldown_until", ""))
        if cooldown_dt and cooldown_dt > datetime.now():
            remaining = int((cooldown_dt - datetime.now()).total_seconds()) // 60
            return f"circuit_breaker ({remaining}min remaining)"
        else:
            errors["consecutive"] = 0
            errors["cooldown_until"] = None

    # [3] Data validation
    if not price or price <= 0:
        return "invalid_price"
    if total_usd <= 0:
        return "zero_balance"

    # [4] Stop-loss / trailing-stop / IL
    # Use smoothed portfolio value to avoid API glitch triggers
    value_history = state.get("_value_history", [])
    stats = state.get("stats", {})
    if stats.get("initial_portfolio_usd") and len(value_history) >= 3:
        # Median of recent values for stop decisions
        smooth_usd = sorted(value_history[-5:])[len(value_history[-5:]) // 2]
        pnl = calc_pnl(stats, smooth_usd, price)
        peak = stats.get("portfolio_peak_usd", pnl["cost_basis"])

        # Peak only updates if confirmed by 2 consecutive readings above old peak
        prev_val = value_history[-2] if len(value_history) >= 2 else 0
        if smooth_usd > peak and prev_val > peak:
            peak = smooth_usd
            stats["portfolio_peak_usd"] = round(peak, 2)

        pnl_pct = pnl["pnl_pct"] / 100  # convert to fraction for comparison
        if STOP_LOSS_PCT > 0 and pnl_pct <= -STOP_LOSS_PCT:
            state["stop_triggered"] = (
                f"stop_loss ({pnl_pct * 100:+.1f}% <= -{STOP_LOSS_PCT * 100:.0f}%)"
            )
            return state["stop_triggered"]

        if TRAILING_STOP_PCT > 0 and peak > 0:
            drawdown = (peak - smooth_usd) / peak
            if drawdown >= TRAILING_STOP_PCT:
                state["stop_triggered"] = (
                    f"trailing_stop (drawdown {drawdown * 100:.1f}% from peak ${peak:.0f})"
                )
                return state["stop_triggered"]

    # IL check
    il_pct = stats.get("estimated_il_pct", 0)
    if abs(il_pct) > MAX_IL_TOLERANCE_PCT:
        state["stop_triggered"] = f"il_limit ({il_pct:.1f}% > {MAX_IL_TOLERANCE_PCT}%)"
        return state["stop_triggered"]

    # [5] Rebalance frequency
    rebalance_history = state.get("rebalance_history", [])
    now = datetime.now()
    recent_24h = []
    for r in rebalance_history:
        r_dt = _safe_isoparse(r.get("time", ""))
        if r_dt and (now - r_dt).total_seconds() < 86400:
            recent_24h.append(r)
    if len(recent_24h) >= MAX_REBALANCES_24H:
        return f"max_rebalances ({len(recent_24h)}/{MAX_REBALANCES_24H} in 24h)"

    # [6] Position age
    position = state.get("position")
    if position and position.get("created_at"):
        created_dt = _safe_isoparse(position["created_at"])
        age = (now - created_dt).total_seconds() if created_dt else MIN_POSITION_AGE + 1
        if age < MIN_POSITION_AGE:
            remaining = int(MIN_POSITION_AGE - age)
            return f"position_too_young ({remaining}s remaining)"

    # [7] Gas cost check (skip for mandatory/maintenance triggers)
    if trigger and trigger.get("priority") not in ("mandatory", "maintenance"):
        # Estimate: Base L2 gas ~$0.01-0.05 per tx, rebalance = ~4 txs
        estimated_gas_usd = 0.15
        # Rough fee estimate: position_value * fee_rate * time_in_range
        position_value = total_usd
        daily_fee_estimate = position_value * FEE_TIER * 0.5  # 50% utilization
        hourly_fee = daily_fee_estimate / 24
        expected_fee_until_next = hourly_fee * 4  # assume 4h until next rebalance
        if (
            expected_fee_until_next > 0
            and estimated_gas_usd > expected_fee_until_next * GAS_TO_FEE_RATIO
        ):
            return f"gas_too_high (gas ${estimated_gas_usd:.2f} > {GAS_TO_FEE_RATIO:.0%} of fee ${expected_fee_until_next:.2f})"

    # [8] Minimum range change
    if trigger and trigger.get("trigger") == "volatility_shift":
        # Only rebalance if the new range would differ by >5%
        pass  # Checked after new range calculation in tick()

    return None


# ── DeFi Operations (onchainos defi commands) ──────────────────────────────


def _verify_tx_receipt(order_id: str, retries: int = 3) -> bool:
    """Poll gateway orders to verify TX was mined successfully."""
    for attempt in range(retries):
        time.sleep(4 * (attempt + 1))  # 4s, 8s, 12s
        data = onchainos_cmd(
            [
                "gateway",
                "orders",
                "--address",
                WALLET_ADDR,
                "--chain",
                POOL_CHAIN,
                "--order-id",
                order_id,
            ],
            timeout=15,
        )
        if not data or not data.get("ok"):
            continue
        orders = data.get("data", [])
        if not orders:
            continue
        order = orders[0] if isinstance(orders, list) else orders
        status = str(order.get("txStatus", "") or order.get("status", "")).lower()
        if status in ("success", "1", "confirmed"):
            return True
        if status in ("failed", "0", "reverted"):
            return False
    # Could not confirm — treat as uncertain
    return True  # optimistic fallback to avoid blocking on API lag


def _broadcast_defi_txs(data: dict, label: str) -> bool:
    """Broadcast all transactions from a defi command response.
    Returns True if all transactions were broadcast and confirmed on-chain."""
    result = data.get("data")
    if not result:
        log(f"  {label}: no tx data to broadcast")
        return False
    # Handle both {"dataList": [...]} and direct list formats
    tx_list = []
    if isinstance(result, dict):
        tx_list = result.get("dataList", [])
    elif isinstance(result, list):
        tx_list = result
    if not tx_list:
        log(f"  {label}: empty tx list")
        return False
    for i, tx in enumerate(tx_list):
        tx_type = tx.get("callDataType", f"tx_{i}")
        to_addr = tx.get("to", "")
        calldata = tx.get("serializedData", "") or tx.get("data", "0x")
        value = tx.get("value", "0x0")
        if not to_addr or not calldata:
            log(f"  {label} [{tx_type}]: missing to/data, skip")
            continue
        # Convert hex value to decimal wei
        value_wei = str(int(value, 16) if value.startswith("0x") else int(value))
        broadcast_data = onchainos_cmd(
            [
                "wallet",
                "contract-call",
                "--to",
                to_addr,
                "--chain",
                CHAIN_ID,
                "--input-data",
                calldata,
                "--amt",
                value_wei,
            ],
            timeout=60,
        )
        if broadcast_data and broadcast_data.get("ok") and broadcast_data.get("data"):
            r = broadcast_data["data"]
            if isinstance(r, list):
                r = r[0] if r else {}
            tx_hash = r.get("txHash") or r.get("hash") or r.get("orderId")
            log(f"  {label} [{tx_type}] broadcast OK: {tx_hash}")
            # Verify on-chain execution
            if tx_hash:
                confirmed = _verify_tx_receipt(tx_hash)
                if not confirmed:
                    log(f"  {label} [{tx_type}] TX REVERTED on-chain: {tx_hash}")
                    return False
        else:
            detail = (
                json.dumps(broadcast_data)[:200] if broadcast_data else "no response"
            )
            log(f"  {label} [{tx_type}] broadcast failed: {detail}")
            return False
    return True


def defi_claim_fees(token_id: str) -> bool:
    """Claim accumulated fees from V3 position."""
    if not token_id:
        return False
    data = onchainos_cmd(
        [
            "defi",
            "claim",
            "--address",
            WALLET_ADDR,
            "--chain",
            POOL_CHAIN,
            "--reward-type",
            "V3_FEE",
            "--id",
            INVESTMENT_ID,
            "--token-id",
            token_id,
        ],
        timeout=45,
    )
    if data and data.get("ok"):
        log(f"Fees claim calldata for token_id={token_id}")
        return _broadcast_defi_txs(data, "claim")
    log(f"Claim fees failed: {json.dumps(data)[:200] if data else 'no response'}")
    return False


def defi_redeem(token_id: str) -> bool:
    """Remove all liquidity from V3 position using --ratio 1 (full exit)."""
    if not token_id:
        return False
    data = onchainos_cmd(
        [
            "defi",
            "redeem",
            "--id",
            INVESTMENT_ID,
            "--address",
            WALLET_ADDR,
            "--chain",
            POOL_CHAIN,
            "--token-id",
            token_id,
            "--ratio",
            "1",
        ],
        timeout=60,
    )
    if data and data.get("ok"):
        log(f"Redeem calldata for token_id={token_id}")
        return _broadcast_defi_txs(data, "redeem")
    log(f"Redeem failed: {json.dumps(data)[:200] if data else 'no response'}")
    return False



def defi_calculate_entry(
    input_token: str,
    input_amount: str,
    token_decimal: int,
    tick_lower: int,
    tick_upper: int,
) -> dict | None:
    """Calculate deposit parameters for V3 position."""
    data = onchainos_cmd(
        [
            "defi",
            "calculate-entry",
            "--id",
            INVESTMENT_ID,
            "--address",
            WALLET_ADDR,
            "--chain",
            POOL_CHAIN,
            "--input-token",
            input_token,
            "--input-amount",
            input_amount,
            "--token-decimal",
            str(token_decimal),
            "--tick-lower",
            str(tick_lower),
            "--tick-upper",
            str(tick_upper),
        ],
        timeout=30,
    )
    if data and data.get("ok"):
        result = data.get("data")
        # Extract investWithTokenList for deposit --user-input
        if isinstance(result, dict) and "investWithTokenList" in result:
            return result["investWithTokenList"]
        return result
    log(f"Calculate entry failed: {json.dumps(data)[:200] if data else 'no response'}")
    return None


def defi_deposit(user_input: str, tick_lower: int, tick_upper: int) -> bool:
    """Deposit liquidity into V3 position at specified tick range."""
    # Filter out zero-amount tokens — API rejects coinAmount "0"
    try:
        tokens = json.loads(user_input)
        if isinstance(tokens, list):
            tokens = [t for t in tokens if float(t.get("coinAmount", 0)) > 0]
            if not tokens:
                log("Deposit skipped: all token amounts are zero")
                return False
            user_input = json.dumps(tokens)
    except (json.JSONDecodeError, ValueError):
        pass
    data = onchainos_cmd(
        [
            "defi",
            "deposit",
            "--investment-id",
            INVESTMENT_ID,
            "--address",
            WALLET_ADDR,
            "--chain",
            POOL_CHAIN,
            "--user-input",
            user_input,
            "--tick-lower",
            str(tick_lower),
            "--tick-upper",
            str(tick_upper),
        ],
        timeout=60,
    )
    if data and data.get("ok"):
        log("Deposit calldata received")
        return _broadcast_defi_txs(data, "deposit")
    log(f"Deposit failed: {json.dumps(data)[:200] if data else 'no response'}")
    return False


# ── Swap (reused from grid-trading) ─────────────────────────────────────────


def _wallet_contract_call(tx: dict) -> tuple[str | None, dict | None]:
    value_wei = str(int(tx.get("value", "0")))
    args = [
        "wallet",
        "contract-call",
        "--to",
        tx["to"],
        "--chain",
        CHAIN_ID,
        "--input-data",
        tx.get("data", "0x"),
        "--amt",
        value_wei,
    ]
    try:
        data = onchainos_cmd(args, timeout=45)
        if data and data.get("ok") and data.get("data"):
            result = (
                data["data"]
                if isinstance(data["data"], dict)
                else (
                    data["data"][0] if isinstance(data["data"], list) else data["data"]
                )
            )
            tx_hash = (
                result.get("txHash") or result.get("hash") or result.get("orderId")
            )
            if tx_hash:
                log(f"  Broadcast OK: {tx_hash}")
                return tx_hash, None
            return None, {
                "reason": "no_hash",
                "detail": json.dumps(result)[:200],
                "retriable": True,
            }
        detail = json.dumps(data)[:200] if data else "no response"
        return None, {
            "reason": "contract_call_failed",
            "detail": detail,
            "retriable": True,
        }
    except Exception as e:
        return None, {"reason": "exception", "detail": str(e), "retriable": True}


def simulate_tx(tx: dict) -> dict | None:
    data = onchainos_cmd(
        [
            "gateway",
            "simulate",
            "--from",
            WALLET_ADDR,
            "--to",
            tx["to"],
            "--data",
            tx.get("data", "0x"),
            "--amount",
            tx.get("value", "0"),
            "--chain",
            POOL_CHAIN,
        ],
        timeout=15,
    )
    if data and data.get("ok") and data.get("data"):
        sim = data["data"][0] if isinstance(data["data"], list) else data["data"]
        fail_reason = sim.get("failReason", "")
        gas_used = sim.get("gasUsed", "")
        success = not fail_reason
        log(
            f"  Simulation: {'OK' if success else 'FAIL'} gasUsed={gas_used}"
            + (f" reason={fail_reason}" if fail_reason else "")
        )
        return {"success": success, "failReason": fail_reason, "gasUsed": gas_used}
    return None


def ensure_approval(token_addr: str, spender: str, amount: int) -> bool:
    state = load_state()
    approved_routers = state.get("approved_routers", [])
    key = f"{token_addr}:{spender}".lower()
    if key in [r.lower() for r in approved_routers]:
        return True

    log(f"Approval needed for {token_addr[:10]}... to {spender[:10]}...")
    max_approval = (
        "115792089237316195423570985008687907853269984665640564039457584007913129639935"
    )
    data = onchainos_cmd(
        [
            "swap",
            "approve",
            "--token",
            token_addr,
            "--amount",
            max_approval,
            "--chain",
            POOL_CHAIN,
        ]
    )
    if not data or not data.get("ok") or not data.get("data"):
        log(f"Approve API failed: {json.dumps(data)[:200] if data else 'no response'}")
        return False

    approve_tx = data["data"][0]
    approve_tx["to"] = token_addr
    tx_hash, fail = _wallet_contract_call(approve_tx)
    if not tx_hash:
        log(f"Approval failed: {fail}")
        return False

    log(f"Approval TX: {tx_hash}")
    time.sleep(5)
    approved_routers.append(key)
    state["approved_routers"] = approved_routers
    save_state(state)
    return True


def execute_swap(
    from_token: str,
    to_token: str,
    amount: int,
    price: float,
) -> tuple[str | None, dict | None]:
    """Execute a token swap via onchainos."""
    for attempt in range(2):
        swap_data = onchainos_cmd(
            [
                "swap",
                "swap",
                "--from",
                from_token,
                "--to",
                to_token,
                "--amount",
                str(amount),
                "--chain",
                POOL_CHAIN,
                "--wallet",
                WALLET_ADDR,
                "--slippage",
                str(SLIPPAGE_PCT),
            ]
        )

        if not swap_data or not swap_data.get("ok") or not swap_data.get("data"):
            detail = json.dumps(swap_data)[:200] if swap_data else "no response"
            log(f"Swap quote failed (attempt {attempt + 1}): {detail}")
            if attempt == 0:
                time.sleep(3)
                continue
            return None, {
                "reason": "swap_quote_failed",
                "detail": detail,
                "retriable": True,
            }

        tx = swap_data["data"][0]["tx"]
        log(
            f"  Swap: to={tx['to'][:10]}... value={tx.get('value', '0')} "
            f"gas={tx.get('gas', 'N/A')}"
        )

        simulate_tx(tx)

        # Approve if selling a token (not native ETH)
        if from_token.lower() != ETH_ADDR.lower():
            router_addr = tx["to"]
            if not ensure_approval(from_token, router_addr, amount):
                return None, {
                    "reason": "approval_failed",
                    "detail": f"router {router_addr}",
                    "retriable": True,
                }

        tx_hash, fail = _wallet_contract_call(tx)
        if tx_hash:
            return tx_hash, None

        log(f"Swap failed (attempt {attempt + 1}): {fail}")
        if attempt == 0 and fail and fail.get("retriable"):
            time.sleep(3)
            continue
        return None, fail

    return None, {"reason": "max_retries", "detail": "exhausted", "retriable": True}


def _calc_balanced_deposit(
    available_eth: float,
    usdc_bal: float,
    price: float,
    tick_lower: int,
    tick_upper: int,
) -> str | None:
    """Calculate deposit amounts, pre-swapping ETH↔USDC if ratio is unbalanced.

    Returns JSON string for defi_deposit --user-input, or None on failure.
    """
    deposit_eth_wei = int(available_eth * 0.95 * (10 ** TOKEN0["decimals"]))

    # First call: probe the ratio using ETH as input
    calculated = defi_calculate_entry(
        input_token=NATIVE_TOKEN,
        input_amount=str(deposit_eth_wei),
        token_decimal=TOKEN0["decimals"],
        tick_lower=tick_lower,
        tick_upper=tick_upper,
    )
    if not calculated or not isinstance(calculated, list):
        log("  calculate-entry failed")
        return None

    # Check if USDC needed exceeds wallet balance
    usdc_needed = 0.0
    for item in calculated:
        addr = item.get("tokenAddress", "").lower()
        if addr == USDC_ADDR.lower():
            usdc_needed = float(item.get("coinAmount", 0)) / (10 ** TOKEN1["decimals"])
            break

    if usdc_needed <= usdc_bal * 0.98:
        # Wallet has enough USDC — use as-is
        log(f"  Ratio OK: need {usdc_needed:.2f} USDC, have {usdc_bal:.2f}")
        return json.dumps(calculated)

    # Need to swap some ETH → USDC to balance
    usdc_gap = usdc_needed - usdc_bal
    # Swap enough ETH to cover the gap + 3% buffer for slippage/fees
    swap_eth = usdc_gap / price * 1.03
    if swap_eth > available_eth * 0.9:
        # Safety: don't swap more than 90% of available ETH
        swap_eth = available_eth * 0.45  # swap roughly half
    swap_eth_wei = int(swap_eth * (10 ** TOKEN0["decimals"]))
    log(f"  Pre-swap: {swap_eth:.6f} ETH → USDC (need {usdc_needed:.2f}, have {usdc_bal:.2f})")

    tx_hash, fail = execute_swap(NATIVE_TOKEN, USDC_ADDR, swap_eth_wei, price)
    if not tx_hash:
        log(f"  Pre-swap failed: {fail}")
        return None
    log(f"  Pre-swap OK: {tx_hash}")

    # Wait for swap to settle, then re-check balances with retry
    new_eth, new_usdc, bal_failed = 0.0, usdc_bal, True
    for wait in [12, 10, 10]:
        time.sleep(wait)
        new_eth, new_usdc, bal_failed = get_balances(force=True)
        if not bal_failed and new_usdc > usdc_bal + 1:
            # USDC increased — swap reflected
            break
        log(f"  Waiting for swap to reflect (USDC={new_usdc:.2f}, was {usdc_bal:.2f})")
    if bal_failed:
        log("  Balance check failed after swap")
        return None

    new_available = new_eth - GAS_RESERVE_ETH
    if new_available < 0:
        new_available = 0
    log(f"  Post-swap balances: ETH={new_eth:.6f} USDC={new_usdc:.2f}")

    # Recalculate with updated ETH balance
    new_eth_wei = int(new_available * 0.95 * (10 ** TOKEN0["decimals"]))
    recalculated = defi_calculate_entry(
        input_token=NATIVE_TOKEN,
        input_amount=str(new_eth_wei),
        token_decimal=TOKEN0["decimals"],
        tick_lower=tick_lower,
        tick_upper=tick_upper,
    )
    if recalculated and isinstance(recalculated, list):
        # Verify USDC fits now
        for item in recalculated:
            addr = item.get("tokenAddress", "").lower()
            if addr == USDC_ADDR.lower():
                new_usdc_needed = float(item.get("coinAmount", 0)) / (10 ** TOKEN1["decimals"])
                if new_usdc_needed > new_usdc:
                    log(f"  Still short on USDC after swap ({new_usdc_needed:.2f} > {new_usdc:.2f})")
                    # Last resort: use USDC as input
                    return _calc_entry_usdc_base(new_usdc, tick_lower, tick_upper)
                break
        return json.dumps(recalculated)

    log("  Recalculate-entry failed after swap")
    return _calc_entry_usdc_base(new_usdc, tick_lower, tick_upper)


def _calc_entry_usdc_base(
    usdc_bal: float, tick_lower: int, tick_upper: int,
) -> str | None:
    """Fallback: use USDC as input token for calculate-entry."""
    usdc_amount = int(usdc_bal * 0.90 * (10 ** TOKEN1["decimals"]))
    calculated = defi_calculate_entry(
        input_token=USDC_ADDR,
        input_amount=str(usdc_amount),
        token_decimal=TOKEN1["decimals"],
        tick_lower=tick_lower,
        tick_upper=tick_upper,
    )
    if calculated and isinstance(calculated, list):
        log(f"  Using USDC-base fallback: {usdc_bal * 0.90:.2f} USDC")
        return json.dumps(calculated)
    log("  USDC-base calculate-entry also failed")
    return None


# ── Rebalance Execution ────────────────────────────────────────────────────


def execute_rebalance(
    state: dict,
    price: float,
    new_range: dict,
    trigger: dict,
) -> bool:
    """Execute full rebalance: claim -> redeem -> (swap) -> deposit.
    Returns True on success."""
    position = state.get("position") or {}
    token_id = position.get("token_id", "")
    old_tick_lower = position.get("tick_lower")
    old_tick_upper = position.get("tick_upper")

    new_tick_lower = new_range["tick_lower"]
    new_tick_upper = new_range["tick_upper"]

    log(
        f"REBALANCE: {trigger['trigger']} ({trigger.get('detail', '')}) "
        f"ticks [{old_tick_lower},{old_tick_upper}] -> [{new_tick_lower},{new_tick_upper}]"
    )

    # Step 1: Claim fees (skip if unclaimed < $5 to save gas)
    # Refetch position detail for fresh unclaimed amount before claiming
    unclaimed = 0.0
    if token_id:
        pre_claim_detail = get_position_detail(token_id)
        unclaimed = pre_claim_detail.get("unclaimed_fee_usd", 0)
        state["stats"]["unclaimed_fee_usd"] = round(unclaimed, 4)
    if token_id and unclaimed >= MIN_TRADE_USD:
        claimed = defi_claim_fees(token_id)
        if claimed:
            state["stats"]["total_fees_claimed_usd"] = round(
                state["stats"].get("total_fees_claimed_usd", 0) + unclaimed, 2
            )
            state["stats"]["unclaimed_fee_usd"] = 0.0  # just claimed
            log(
                f"  Fees claimed: ${unclaimed:.2f} (total: ${state['stats']['total_fees_claimed_usd']:.2f})"
            )
    elif token_id:
        log(f"  Skip claim: unclaimed ${unclaimed:.2f} < ${MIN_TRADE_USD:.0f}")
        # Redeem will auto-collect fees, so count them as claimed
        if unclaimed > 0:
            state["stats"]["total_fees_claimed_usd"] = round(
                state["stats"].get("total_fees_claimed_usd", 0) + unclaimed, 2
            )
            state["stats"]["unclaimed_fee_usd"] = 0.0
            log(f"  (will be collected via redeem, recorded: ${unclaimed:.2f})")

    # Step 2: Remove liquidity
    if token_id:
        redeemed = defi_redeem(token_id)
        if not redeemed:
            log("  Redeem failed — will retry next tick")
            return False
        # Mark position as redeemed immediately to prevent stale state
        state["_rebalance_in_progress"] = True
        state["position"] = {
            "token_id": "",
            "tick_lower": None,
            "tick_upper": None,
            "lower_price": None,
            "upper_price": None,
            "created_at": None,
            "created_atr_pct": 0,
            "_redeemed_from": token_id,
        }
        save_state(state)
        time.sleep(3)

    # Step 3: Get current balances after redeem (force refresh to bypass cache)
    eth_bal, usdc_bal, bal_failed = get_balances(force=True)
    if bal_failed:
        log("  Balance query failed after redeem — funds may be idle")
        # Don't crash, but try to continue with what we have
        time.sleep(5)
        eth_bal, usdc_bal, bal_failed = get_balances(force=True)
        if bal_failed:
            log("  Balance still unavailable — aborting, funds sitting idle in wallet")
            return False
    available_eth = eth_bal - GAS_RESERVE_ETH
    if available_eth < 0:
        available_eth = 0

    total_usd = available_eth * price + usdc_bal
    if total_usd < MIN_TRADE_USD:
        log(f"  Balance too low after redeem: ${total_usd:.2f}")
        return False

    # Step 4: Calculate dual-token deposit — swap to balance if needed
    log(f"  Balances: ETH={eth_bal:.6f} USDC={usdc_bal:.2f}")
    user_input_json = _calc_balanced_deposit(
        available_eth, usdc_bal, price,
        new_tick_lower, new_tick_upper,
    )
    if not user_input_json:
        log("  Deposit calculation failed — aborting")
        return False

    # Step 5: Deposit at new range
    # Record current max token_id so we only find positions created AFTER deposit
    pre_deposit_max_tid = ""
    existing = _query_all_positions()
    if existing:
        pre_deposit_max_tid = max(existing, key=lambda p: int(p["tokenId"]))["tokenId"]

    log(f"  Deposit input: {user_input_json[:200]}")
    deposit_result = defi_deposit(user_input_json, new_tick_lower, new_tick_upper)
    if not deposit_result:
        dep_fails = state.get("_consecutive_deposit_failures", 0) + 1
        state["_consecutive_deposit_failures"] = dep_fails
        save_state(state)
        log(f"  Deposit failed (consecutive: {dep_fails}/{MAX_DEPOSIT_FAILURES}) — will retry next tick")
        return False

    # Deposit returns bool; recover token_id and verify on-chain value
    # Only look for token_ids created after pre_deposit_max_tid
    new_token_id = ""
    lp_value = 0.0
    for verify_attempt, delay in enumerate([8, 15, 25], 1):
        time.sleep(delay)
        new_token_id = find_latest_token_id(after_token_id=pre_deposit_max_tid)
        if new_token_id:
            detail = get_position_detail(new_token_id)
            lp_value = detail.get("value", 0)
            if lp_value >= MIN_TRADE_USD:
                log(
                    f"  Deposit verified (attempt {verify_attempt}): "
                    f"token_id={new_token_id} value=${lp_value:.2f}"
                )
                break
            log(
                f"  Verify attempt {verify_attempt}: token_id={new_token_id} "
                f"value=${lp_value:.2f} (too low)"
            )
        else:
            log(f"  Verify attempt {verify_attempt}: no token_id found yet")
    else:
        # All verification attempts exhausted
        if new_token_id:
            # Token exists on-chain but value reads low (indexing lag).
            # Adopt it instead of creating another position that becomes dust.
            log(
                f"  Deposit value unconfirmed but token_id={new_token_id} exists "
                f"on-chain — adopting (value=${lp_value:.2f}, may update next tick)"
            )
        else:
            # No token_id found at all — deposit likely reverted
            dep_fails = state.get("_consecutive_deposit_failures", 0) + 1
            state["_consecutive_deposit_failures"] = dep_fails
            log(
                f"  Deposit verification FAILED: no token_id found after 3 attempts "
                f"(consecutive failures: {dep_fails}/{MAX_DEPOSIT_FAILURES})"
            )
            if dep_fails >= MAX_DEPOSIT_FAILURES:
                state["stop_triggered"] = (
                    f"deposit_failures ({dep_fails} consecutive deposit verifications failed)"
                )
                save_state(state)
                emit(
                    "stop_triggered",
                    {
                        "status": "stop_triggered",
                        "trigger": state["stop_triggered"],
                        "price": round(price, 2),
                    },
                    notify=True,
                    tier="risk_alert",
                )
                log(
                    f"  AUTO-PAUSED: {dep_fails} consecutive deposit failures — "
                    f"manual intervention required (resume-trading to restart)"
                )
            else:
                save_state(state)
            return False

    # Have a valid token_id (verified or adopted) — reset failure counter
    state["_consecutive_deposit_failures"] = 0
    if new_token_id:
        cleanup_residual_positions(new_token_id)

    # Update state
    now_iso = datetime.now().isoformat()
    candles = get_kline_data("1H", 24)
    current_atr = calc_kline_volatility(candles) if candles else 0

    state.pop("_rebalance_in_progress", None)
    # Get current price for IL tracking
    rebal_price = get_eth_price() or 0

    state["position"] = {
        "token_id": new_token_id,
        "tick_lower": new_tick_lower,
        "tick_upper": new_tick_upper,
        "lower_price": new_range["lower_price"],
        "upper_price": new_range["upper_price"],
        "created_at": now_iso,
        "created_atr_pct": round(current_atr, 3),
        "entry_price": round(rebal_price, 2),
    }

    # Record rebalance
    rebalance_record = {
        "time": now_iso,
        "trigger": trigger["trigger"],
        "detail": trigger.get("detail", ""),
        "price": round(rebal_price, 2),
        "old_range": [old_tick_lower, old_tick_upper],
        "new_range": [new_tick_lower, new_tick_upper],
    }
    rebalances = state.get("rebalance_history", [])
    rebalances.append(rebalance_record)
    if len(rebalances) > 50:
        rebalances = rebalances[-50:]
    state["rebalance_history"] = rebalances
    state["stats"]["total_rebalances"] = state["stats"].get("total_rebalances", 0) + 1

    log(
        f"  Rebalance complete: [{new_tick_lower},{new_tick_upper}] "
        f"(${new_range['lower_price']:.2f}-${new_range['upper_price']:.2f}) "
        f"token_id={new_token_id}"
    )
    return True



# ── State Management ────────────────────────────────────────────────────────


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except (json.JSONDecodeError, OSError) as e:
            log(f"State file corrupted: {e}")
            # Try backup
            bak = STATE_FILE.with_suffix(".json.bak")
            if bak.exists():
                try:
                    state = json.loads(bak.read_text())
                    log("Recovered state from backup")
                    return state
                except (json.JSONDecodeError, OSError):
                    log("Backup also corrupted — starting fresh")
    return {
        "version": 1,
        "wallet_address": WALLET_ADDR,
        "pool": {
            "investment_id": INVESTMENT_ID,
            "chain": POOL_CHAIN,
            "token0": TOKEN0,
            "token1": TOKEN1,
            "fee_tier": FEE_TIER,
            "tick_spacing": TICK_SPACING,
        },
        "position": None,
        "price_history": [],
        "vol_history": [],
        "rebalance_history": [],
        "stats": {
            "total_rebalances": 0,
            "total_fees_claimed_usd": 0.0,
            "total_gas_spent_usd": 0.0,
            "time_in_range_pct": 100.0,
            "net_yield_usd": 0.0,
            "initial_portfolio_usd": None,
            "initial_eth_price": None,
            "started_at": datetime.now().isoformat(),
            "last_check": None,
            "total_deposits_usd": 0.0,
            "deposit_history": [],
            "estimated_il_pct": 0.0,
        },
        "errors": {"consecutive": 0, "cooldown_until": None},
        "stop_triggered": None,
        "approved_routers": [],
    }


def save_state(state: dict):
    """Atomic state save: write to temp file, then rename."""
    if STATE_FILE.exists():
        try:
            STATE_FILE.with_suffix(".json.bak").write_text(STATE_FILE.read_text())
        except OSError:
            pass
    content = json.dumps(state, indent=2)
    fd, tmp_path = tempfile.mkstemp(
        dir=STATE_FILE.parent, suffix=".json.tmp", prefix=".cl_lp_"
    )
    try:
        with os.fdopen(fd, "w") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, STATE_FILE)
    except Exception as e:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        log(f"CRITICAL: Failed to save state: {e}")


# ── Structured Event Output ─────────────────────────────────────────────────


def _range_visual(price: float, lower: float, upper: float, width: int = 20) -> str:
    """Build ASCII range position indicator.

    Example: [$1,950 ·····●····· $2,150] ← $2,090
    """
    if not lower or not upper or upper <= lower:
        return ""
    clamped = max(lower, min(upper, price))
    pos = int((clamped - lower) / (upper - lower) * width)
    bar = "·" * pos + "●" + "·" * (width - pos)
    return f"[${lower:,.0f} {bar} ${upper:,.0f}] ← ${price:,.0f}"


def _build_notification(tier: str, data: dict) -> dict:
    """Build dual-format notification block (discord embed + text markdown).

    Returns {"tier": str, "discord": {...}, "text": str} or None if silent.
    """
    price = data.get("price", 0)
    status = data.get("status", "")

    # ── Trade Alert ──────────────────────────────────────────────────────
    if tier == "trade_alert":
        success = status in ("rebalanced", "first_deploy")
        pos = data.get("position", {})
        lower = pos.get("lower_price", 0)
        upper = pos.get("upper_price", 0)
        pnl_usd = data.get("pnl_usd", 0)
        fees = data.get("fees_claimed_usd", 0)
        trigger = data.get("trigger", "")
        tx = data.get("tx_hash", "")

        icon = "🔄" if success else "❌"
        verb = "调仓成功" if success else "调仓失败"
        color = 0x00CC66 if success else 0xFF6600  # green / orange

        fields_discord = [
            {"name": "价格", "value": f"${price:,.2f}", "inline": True},
            {"name": "范围", "value": f"${lower:,.0f} — ${upper:,.0f}", "inline": True},
            {"name": "触发", "value": trigger or "—", "inline": True},
            {"name": "Fee Claimed", "value": f"${fees:,.2f}", "inline": True},
            {"name": "PnL", "value": f"${pnl_usd:+,.2f}", "inline": True},
        ]
        visual = _range_visual(price, lower, upper) if lower and upper else ""
        footer = f"tx: {tx[:10]}...{tx[-6:]}" if tx else ""

        text_lines = [
            f"{icon} **{verb} · {PAIR_NAME} · {CHAIN_LABEL}**",
            f"💰 价格: `${price:,.2f}`",
            f"📐 范围: `${lower:,.0f} — ${upper:,.0f}`",
            f"🎯 触发: `{trigger}`" if trigger else None,
            f"💵 Fee Claimed: `${fees:,.2f}`",
            f"📈 PnL: `${pnl_usd:+,.2f}`",
            f"`{visual}`" if visual else None,
            f"_tx: {tx[:10]}...{tx[-6:]}_" if tx else None,
        ]

        discord_embed = {
            "title": f"{icon} {verb} · {PAIR_NAME} · {CHAIN_LABEL}",
            "color": color,
            "fields": fields_discord,
            "footer": {"text": footer},
        }
        if visual:
            discord_embed["description"] = f"`{visual}`"

        return {
            "tier": "trade_alert",
            "discord": discord_embed,
            "text": "\n".join(ln for ln in text_lines if ln),
        }

    # ── Risk Alert ───────────────────────────────────────────────────────
    if tier == "risk_alert":
        trigger_msg = data.get("trigger", status)
        portfolio = data.get("portfolio_usd", 0)
        auto_resume = data.get("auto_resume", False)

        fields_discord = [
            {"name": "原因", "value": trigger_msg, "inline": False},
            {"name": "价格", "value": f"${price:,.2f}", "inline": True},
            {"name": "组合价值", "value": f"${portfolio:,.2f}", "inline": True},
        ]
        footer = "自动恢复已启用" if auto_resume else "使用 resume-trading 恢复"

        text_lines = [
            f"🛑 **交易停止 · {PAIR_NAME} · {CHAIN_LABEL}**",
            f"⚠️ 原因: `{trigger_msg}`",
            f"💰 价格: `${price:,.2f}` | 组合: `${portfolio:,.2f}`",
            f"_{footer}_",
        ]

        return {
            "tier": "risk_alert",
            "discord": {
                "title": f"🛑 交易停止 · {PAIR_NAME} · {CHAIN_LABEL}",
                "color": 0xFF0000,
                "fields": fields_discord,
                "footer": {"text": footer},
            },
            "text": "\n".join(text_lines),
        }

    # ── Hourly Pulse ─────────────────────────────────────────────────────
    if tier == "hourly_pulse":
        pos = data.get("position", {})
        lower = pos.get("lower_price", 0)
        upper = pos.get("upper_price", 0)
        atr = data.get("atr_pct", 0)
        regime = data.get("regime", "")
        trend = data.get("trend", "neutral")
        strength = data.get("trend_strength", 0)
        tir = data.get("time_in_range_pct", 0)
        rebal = data.get("total_rebalances", 0)
        pnl_usd = data.get("pnl_usd", 0)
        pnl_pct = data.get("pnl_pct", 0)
        pnl_valid = data.get("pnl_valid", False)
        unclaimed = data.get("unclaimed_fee_usd", 0)
        portfolio = data.get("portfolio_usd", 0)
        fee_apy = data.get("fee_apy", 0)
        net_apy = data.get("net_apy", 0)

        visual = _range_visual(price, lower, upper) if lower and upper else ""

        # Token breakdown (wallet + LP)
        bals = data.get("balances", {})
        eth_wallet = bals.get("eth", 0)
        usdc_wallet = bals.get("usdc", 0)
        lp_assets = bals.get("lp_assets", [])

        # Parse LP token amounts
        lp_eth = 0.0
        lp_usdc = 0.0
        for a in lp_assets:
            sym = a.get("symbol", "").upper()
            amt = a.get("amount", 0)
            if sym in ("WETH", "ETH"):
                lp_eth = amt
            elif sym in ("USDC", "USDT"):
                lp_usdc = amt

        total_eth = eth_wallet + lp_eth
        total_usdc = usdc_wallet + lp_usdc

        pnl_str = f"${pnl_usd:+,.2f} ({pnl_pct:+.1f}%)" if pnl_valid else "—"
        apy_str = f"Fee {fee_apy:+.1f}% / Net {net_apy:+.1f}%" if pnl_valid else "—"

        fields_discord = [
            {
                "name": "ETH",
                "value": f"{total_eth:.4f} (${total_eth * price:,.0f})",
                "inline": True,
            },
            {"name": "USDC", "value": f"${total_usdc:,.2f}", "inline": True},
            {"name": "总价值", "value": f"${portfolio:,.0f}", "inline": True},
            {"name": "PnL", "value": pnl_str, "inline": True},
            {"name": "年化 APY", "value": apy_str, "inline": True},
            {"name": "待领费用", "value": f"${unclaimed:,.2f}", "inline": True},
        ]
        footer = f"钱包 {eth_wallet:.4f} ETH + ${usdc_wallet:,.0f} | LP {lp_eth:.4f} ETH + ${lp_usdc:,.0f} · {regime} · {trend}"

        text_lines = [
            f"📊 **{PAIR_NAME} · {CHAIN_LABEL} · 运行中**",
            f"`{visual}`" if visual else None,
            f"💰 `{total_eth:.4f}` ETH (`${total_eth * price:,.0f}`) + `${total_usdc:,.2f}` USDC = **`${portfolio:,.0f}`**",
            f"  钱包: `{eth_wallet:.4f}` ETH + `${usdc_wallet:,.2f}` | LP: `{lp_eth:.4f}` ETH + `${lp_usdc:,.0f}` USDC",
            f"📈 PnL `{pnl_str}` | APY `{apy_str}`" if pnl_valid else None,
            f"💵 待领费用 `${unclaimed:,.2f}`",
            f"_{footer}_",
        ]

        discord_embed = {
            "title": f"📊 {PAIR_NAME} · {CHAIN_LABEL} · 运行中",
            "color": 0x808080,
            "fields": fields_discord,
            "footer": {"text": footer},
        }
        if visual:
            discord_embed["description"] = f"`{visual}`"

        return {
            "tier": "hourly_pulse",
            "discord": discord_embed,
            "text": "\n".join(ln for ln in text_lines if ln),
        }

    # ── Daily Report ─────────────────────────────────────────────────────
    if tier == "daily_report":
        pnl_usd = data.get("pnl_usd", 0)
        pnl_pct = data.get("pnl_pct", 0)
        pnl_valid = data.get("pnl_valid", False)
        tir = data.get("time_in_range_pct", 0)
        rebal = data.get("total_rebalances", 0)
        atr = data.get("atr_pct", 0)
        regime = data.get("regime", "")
        trend = data.get("trend", "neutral")
        strength = data.get("trend_strength", 0)
        fees_claimed = data.get("total_fees_claimed_usd", 0)
        unclaimed = data.get("unclaimed_fee_usd", 0)
        il_pct = data.get("il_pct", 0)
        il_usd = data.get("il_usd", 0)
        fee_apy = data.get("fee_apy", 0)
        net_apy = data.get("net_apy", 0)
        days_running = data.get("days_running", 0)
        cost_basis = data.get("cost_basis", 0)
        today_rebal = data.get("today_rebalances", [])
        portfolio = data.get("portfolio_usd", 0)

        today = datetime.now().date().isoformat()
        pnl_str = f"${pnl_usd:+,.2f} ({pnl_pct:+.1f}%)" if pnl_valid else "数据不足"
        il_str = f"${il_usd:,.2f} ({il_pct:.2f}%)" if il_pct else "—"
        apy_str = f"Fee {fee_apy:+.1f}% / Net {net_apy:+.1f}%" if pnl_valid else "—"

        fields_discord = [
            {"name": "💰 组合价值", "value": f"${portfolio:,.2f}", "inline": True},
            {"name": "📈 PnL", "value": pnl_str, "inline": True},
            {"name": "📊 年化 APY", "value": apy_str, "inline": True},
            {
                "name": "💵 LP 费用",
                "value": f"${fees_claimed + unclaimed:,.2f} (已领 ${fees_claimed:,.2f})",
                "inline": True,
            },
            {"name": "📉 无常损失", "value": il_str, "inline": True},
            {"name": "🔄 今日调仓", "value": f"{len(today_rebal)} 次", "inline": True},
            {"name": "📊 范围内", "value": f"{tir:.0f}%", "inline": True},
            {"name": "📉 波动率", "value": f"{regime} ({atr:.1f}%)", "inline": True},
            {"name": "📈 趋势", "value": f"{trend} ({strength:.2f})", "inline": True},
        ]

        footer = f"运行 {days_running:.1f} 天 · 本金 ${cost_basis:,.0f} · 累计调仓 {rebal} 次"

        text_lines = [
            f"📈 **日报 · {PAIR_NAME} · {today}**",
            "",
            "**收益**",
            f"  PnL: `{pnl_str}` | APY: `{apy_str}`",
            f"  LP 费用: `${fees_claimed + unclaimed:,.2f}` (已领 `${fees_claimed:,.2f}` + 待领 `${unclaimed:,.2f}`)",
            f"  无常损失: `{il_str}`" if il_pct else None,
            "",
            "**运营**",
            f"  今日调仓: `{len(today_rebal)}` 次 | 范围内: `{tir:.0f}%`",
            f"  组合价值: `${portfolio:,.2f}`",
            "",
            "**市场**",
            f"  价格: `${price:,.2f}` | 波动: `{regime}` | 趋势: `{trend}`",
            "",
            f"_{footer}_",
        ]

        # Range visualization for daily report
        pos = data.get("position", {})
        d_lower = pos.get("lower_price", 0)
        d_upper = pos.get("upper_price", 0)
        daily_visual = (
            _range_visual(price, d_lower, d_upper) if d_lower and d_upper else ""
        )

        discord_embed = {
            "title": f"📈 日报 · {PAIR_NAME} · {today}",
            "color": 0x3399FF,
            "fields": fields_discord,
            "footer": {"text": footer},
        }
        if daily_visual:
            discord_embed["description"] = f"`{daily_visual}`"

        return {
            "tier": "daily_report",
            "discord": discord_embed,
            "text": "\n".join(ln for ln in text_lines if ln),
        }

    return None


# ── Notification sending ───────────────────────────────────────────────────


def _send_telegram(text: str) -> bool:
    """Send a message via Telegram Bot API."""
    import urllib.error
    import urllib.request

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        urllib.request.urlopen(req, timeout=10)
        return True
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        log(f"Telegram send error: {exc}")
        return False


def _send_notification(notif: dict):
    """Send notification to Discord (embed) and Telegram (text)."""
    import urllib.error
    import urllib.request

    # Discord embed
    discord_ok = False
    token = _get_discord_token()
    embed = notif.get("discord", {})
    if token and DISCORD_CHANNEL_ID and embed:
        url = f"https://discord.com/api/v10/channels/{DISCORD_CHANNEL_ID}/messages"
        payload = {"embeds": [embed]}
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": f"Bot {token}",
                "Content-Type": "application/json",
                "User-Agent": "DiscordBot (https://openclaw.ai, 1.0)",
            },
        )
        try:
            urllib.request.urlopen(req, timeout=10)
            discord_ok = True
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            log(f"Discord embed error: {exc}")

    # Telegram text
    tg_ok = False
    text = notif.get("text", "")
    if text and (TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID):
        tg_ok = _send_telegram(text)

    if not discord_ok and not tg_ok:
        log("No notification channel available (Discord + Telegram both failed)")


def emit(event_type: str, data: dict, notify: bool = False, tier: str = ""):
    """Emit structured JSON event to stdout (one JSON line per event).

    If tier is provided, builds dual-format notification and sends to
    Discord (embed) + Telegram (markdown text).
    """
    payload = {
        "type": event_type,
        "ts": datetime.now(timezone.utc).isoformat(),
        "notify": notify,
        **data,
    }
    if tier:
        notif = _build_notification(tier, data)
        if notif:
            payload["notification"] = notif
            _send_notification(notif)
    print(json.dumps(payload, ensure_ascii=False), flush=True)


# ── IL Estimation ───────────────────────────────────────────────────────────


def calc_pnl(stats: dict, current_usd: float, current_price: float = 0) -> dict:
    """Calculate PnL in both USD and ETH terms.

    USD: cost_basis = initial_portfolio_usd + deposits; pnl = current - cost_basis
    ETH: cost_basis_eth = initial_portfolio_eth + deposits_eth; pnl = current_eth - cost_basis_eth
    """
    initial = stats.get("initial_portfolio_usd")
    if not initial or initial <= 0:
        return {
            "pnl_usd": 0,
            "pnl_pct": 0,
            "cost_basis": 0,
            "pnl_eth": 0.0,
            "pnl_eth_pct": 0,
            "cost_basis_eth": 0.0,
            "fee_apy": 0,
            "net_apy": 0,
            "days_running": 0,
            "valid": False,
        }
    deposits = stats.get("total_deposits_usd", 0)
    cost_basis = initial + deposits
    pnl_usd = round(current_usd - cost_basis, 2)
    pnl_pct = (pnl_usd / cost_basis * 100) if cost_basis > 0 else 0

    # ETH-denominated PnL
    initial_eth = stats.get("initial_portfolio_eth", 0)
    if not initial_eth and stats.get("initial_eth_price"):
        initial_eth = initial / stats["initial_eth_price"]
    deposits_eth = stats.get("total_deposits_eth", 0)
    cost_basis_eth = initial_eth + deposits_eth
    current_eth = current_usd / current_price if current_price > 0 else 0
    pnl_eth = round(current_eth - cost_basis_eth, 6) if cost_basis_eth > 0 else 0.0
    pnl_eth_pct = (pnl_eth / cost_basis_eth * 100) if cost_basis_eth > 0 else 0

    # Annualized yields
    started = stats.get("started_at", "")
    started_dt = _safe_isoparse(started) if started else None
    days = (datetime.now() - started_dt).total_seconds() / 86400 if started_dt else 0
    days = max(days, 0.01)

    total_fees = stats.get("total_fees_claimed_usd", 0) + stats.get(
        "unclaimed_fee_usd", 0
    )
    fee_apy = (total_fees / cost_basis / days * 365 * 100) if cost_basis > 0 else 0
    net_apy = (pnl_usd / cost_basis / days * 365 * 100) if cost_basis > 0 else 0

    return {
        "pnl_usd": pnl_usd,
        "pnl_pct": round(pnl_pct, 2),
        "cost_basis": cost_basis,
        "pnl_eth": pnl_eth,
        "pnl_eth_pct": round(pnl_eth_pct, 2),
        "cost_basis_eth": round(cost_basis_eth, 6),
        "fee_apy": round(fee_apy, 1),
        "net_apy": round(net_apy, 1),
        "days_running": round(days, 1),
        "valid": True,
    }


def estimate_il(
    entry_price: float,
    current_price: float,
    range_lower: float = 0,
    range_upper: float = 0,
) -> float:
    """Exact V3 impermanent loss for concentrated liquidity position.

    Compares LP position value vs HODL value at current price.
    If range bounds not provided, falls back to V2 full-range formula.
    Handles in-range, below-range, and above-range cases.
    Returns negative percentage (loss) or 0.
    """
    if entry_price <= 0 or current_price <= 0:
        return 0.0

    # V2 fallback if no range provided
    if not (range_lower > 0 and range_upper > range_lower):
        r = current_price / entry_price
        il = 2 * math.sqrt(r) / (1 + r) - 1
        return round(il * 100, 2)

    sp0 = math.sqrt(entry_price)  # sqrt of entry price
    sp1 = math.sqrt(current_price)  # sqrt of current price
    spa = math.sqrt(range_lower)  # sqrt of range lower
    spb = math.sqrt(range_upper)  # sqrt of range upper

    # Clamp entry price to range (should be in-range at deposit time)
    sp0 = max(spa, min(spb, sp0))

    # Token amounts at entry (per unit liquidity L=1)
    x0 = 1 / sp0 - 1 / spb  # token0 (ETH)
    y0 = sp0 - spa  # token1 (USDC)

    # HODL value at current price
    v_hold = x0 * current_price + y0
    if v_hold <= 0:
        return 0.0

    # LP position value at current price (handle out-of-range)
    if current_price <= range_lower:
        # All token0 (ETH), no token1
        x1 = 1 / spa - 1 / spb
        v_lp = x1 * current_price
    elif current_price >= range_upper:
        # All token1 (USDC), no token0
        y1 = spb - spa
        v_lp = y1
    else:
        # In range
        v_lp = 2 * sp1 - current_price / spb - spa

    il = v_lp / v_hold - 1
    return round(il * 100, 2)


# ── Core Logic: tick ────────────────────────────────────────────────────────


STOP_AUTO_RESUME = CFG.get("stop_auto_resume", True)
STOP_RESUME_COOLDOWN = CFG.get("stop_resume_cooldown_seconds", 3600)  # 1h default
STOP_RESUME_REBOUND_PCT = CFG.get("stop_resume_rebound_pct", 0.02)  # 2% default
MAX_AUTO_RESUMES_24H = CFG.get("max_auto_resumes_24h", 2)  # max 2 auto-resumes per 24h
MAX_DEPOSIT_FAILURES = CFG.get("max_deposit_failures", 3)  # pause after N consecutive deposit fails
MAX_BALANCE_FAILURES = CFG.get("max_balance_failures", 5)


def tick():
    """Main loop: check position, decide rebalance, execute."""
    # Process lock — prevent concurrent ticks
    if not _acquire_lock():
        log("Another tick is already running — skipping")
        emit("tick", {"status": "locked", "retriable": False})
        return
    try:
        _tick_inner()
    finally:
        _release_lock()


def _tick_inner():
    """Actual tick logic (called under process lock)."""
    state = load_state()

    # Ensure wallet_address is stored in state
    if WALLET_ADDR and state.get("wallet_address") != WALLET_ADDR:
        state["wallet_address"] = WALLET_ADDR

    # Check for in-progress rebalance from crashed previous tick
    if state.get("_rebalance_in_progress"):
        log(
            "Previous rebalance was interrupted — clearing position, next tick will re-deposit"
        )
        state.pop("_rebalance_in_progress", None)
        state["position"] = None
        save_state(state)

    # Circuit breaker
    errors = state.get("errors", {})
    if not isinstance(errors, dict):
        errors = {"consecutive": 0, "cooldown_until": None}
        state["errors"] = errors
    if errors.get("consecutive", 0) >= MAX_CONSECUTIVE_ERRORS:
        cooldown_dt = _safe_isoparse(errors.get("cooldown_until", ""))
        if cooldown_dt and cooldown_dt > datetime.now():
            remaining = int((cooldown_dt - datetime.now()).total_seconds()) // 60
            log(f"CIRCUIT BREAKER: cooldown {remaining}min remaining")
            emit(
                "tick",
                {
                    "status": "circuit_breaker",
                    "retriable": False,
                    "remaining_min": remaining,
                },
            )
            return
        else:
            errors["consecutive"] = 0
            errors["cooldown_until"] = None

    # Get price
    price = get_eth_price()
    if not price:
        errors["consecutive"] = errors.get("consecutive", 0) + 1
        if errors["consecutive"] >= MAX_CONSECUTIVE_ERRORS:
            errors["cooldown_until"] = (
                datetime.now() + timedelta(seconds=COOLDOWN_AFTER_ERRORS)
            ).isoformat()
            log(f"CIRCUIT BREAKER TRIGGERED after {errors['consecutive']} errors")
        state["errors"] = errors
        save_state(state)
        log("Failed to get price")
        emit(
            "tick",
            {"status": "error", "reason": "price_fetch_failed", "retriable": True},
        )
        return

    errors["consecutive"] = 0
    state["errors"] = errors

    # Update price history (keep 288 = 24h @ 5min)
    history = state.get("price_history", [])
    history.append(price)
    if len(history) > 288:
        history = history[-288:]
    state["price_history"] = history

    # Balances (wallet + LP position)
    eth_bal, usdc_bal, balance_failed = get_balances()
    if balance_failed:
        consec_bal_fail = state.get("_consecutive_balance_failures", 0) + 1
        state["_consecutive_balance_failures"] = consec_bal_fail
        if consec_bal_fail >= MAX_BALANCE_FAILURES:
            log(
                f"Balance query failed {consec_bal_fail} consecutive times — "
                f"pausing trading until balance recovers"
            )
            save_state(state)
            emit(
                "tick",
                {
                    "status": "balance_unavailable",
                    "consecutive_failures": consec_bal_fail,
                    "price": round(price, 2),
                },
                notify=(consec_bal_fail == MAX_BALANCE_FAILURES),
            )
            return
        # Use last known balances for non-critical operations
        last_bal = state.get("last_balances", {})
        if last_bal.get("eth", 0) > 0 or last_bal.get("usdc", 0) > 0:
            eth_bal = last_bal.get("eth", 0)
            usdc_bal = last_bal.get("usdc", 0)
            log(
                f"Balance query failed ({consec_bal_fail}x) — using last known: ETH={eth_bal}, USDC={usdc_bal}"
            )
    else:
        if state.get("_consecutive_balance_failures", 0) > 0:
            log(
                f"Balance query recovered after {state['_consecutive_balance_failures']} failures"
            )
        state["_consecutive_balance_failures"] = 0

    wallet_usd = eth_bal * price + usdc_bal
    position = state.get("position")
    lp_value = 0.0
    unclaimed_fee = 0.0
    lp_assets = []
    # Recover token_id if missing but position exists
    if position and not position.get("token_id") and position.get("tick_lower"):
        recovered_id = find_latest_token_id()
        if recovered_id:
            position["token_id"] = recovered_id
            log(f"Recovered token_id: {recovered_id}")
    # Clean up residual positions (from failed rebalances)
    if position and position.get("token_id"):
        cleanup_residual_positions(position["token_id"])
    if position and position.get("token_id"):
        pos_detail = get_position_detail(position["token_id"])
        lp_value = pos_detail["value"]
        unclaimed_fee = pos_detail["unclaimed_fee_usd"]
        lp_assets = pos_detail.get("assets", [])
        if lp_value == 0.0 and position.get("tick_lower"):
            # Position exists in state but API returned 0 — treat as query failure
            balance_failed = True
            log("LP position query returned 0 value — treating as query failure")
    total_usd = wallet_usd + lp_value
    # Track unclaimed fees in stats
    state.setdefault("stats", {})["unclaimed_fee_usd"] = round(unclaimed_fee, 2)

    # Track portfolio value history for smoothing (only when data is reliable)
    if not balance_failed:
        value_history = state.get("_value_history", [])
        value_history.append(round(total_usd, 2))
        if len(value_history) > 12:  # keep ~1h @ 5min ticks
            value_history = value_history[-12:]
        state["_value_history"] = value_history

    # Initial snapshot — config override > runtime snapshot
    if state["stats"].get("initial_portfolio_usd") is None and not balance_failed:
        cfg_initial = CFG.get("initial_investment_usd")
        if cfg_initial and cfg_initial > 0:
            state["stats"]["initial_portfolio_usd"] = float(cfg_initial)
            state["stats"]["initial_eth_price"] = round(price, 2)
            state["stats"]["initial_portfolio_eth"] = round(float(cfg_initial) / price, 6)
            log(f"Initial portfolio (config): ${cfg_initial} @ ETH ${price:.2f}")
        elif total_usd > 0:
            state["stats"]["initial_portfolio_usd"] = round(total_usd, 2)
            state["stats"]["initial_eth_price"] = round(price, 2)
            state["stats"]["initial_portfolio_eth"] = round(total_usd / price, 6)
            log(f"Initial portfolio (snapshot): ${total_usd:.2f} @ ETH ${price:.2f}")

    # MTF analysis
    mtf = analyze_multi_timeframe(history, price)

    # K-line volatility (refresh hourly)
    kline_vol = None
    kline_cache = state.get("kline_cache")
    kline_stale = True
    if kline_cache and kline_cache.get("fetched_at"):
        fetched_dt = _safe_isoparse(kline_cache["fetched_at"])
        if fetched_dt:
            elapsed = (datetime.now() - fetched_dt).total_seconds()
            kline_stale = elapsed > 3600
    if kline_stale:
        candles = get_kline_data("1H", 24)
        if candles:
            kline_vol = calc_kline_volatility(candles)
            state["kline_cache"] = {
                "atr_pct": round(kline_vol, 3),
                "candles_count": len(candles),
                "fetched_at": datetime.now().isoformat(),
            }
        else:
            kline_vol = kline_cache.get("atr_pct") if kline_cache else None
    else:
        kline_vol = kline_cache.get("atr_pct") if kline_cache else None

    atr_pct = kline_vol if kline_vol else 2.0  # default medium

    # Update vol history
    vol_history = state.get("vol_history", [])
    vol_history.append(
        {"time": datetime.now().isoformat(), "atr_pct": round(atr_pct, 3)}
    )
    if len(vol_history) > 288:
        vol_history = vol_history[-288:]
    state["vol_history"] = vol_history

    # Stop check — with auto-resume and log dedup
    if state.get("stop_triggered"):
        trigger_msg = state["stop_triggered"]

        # Auto-resume logic
        resumed = False
        if STOP_AUTO_RESUME and "trailing_stop" in trigger_msg:
            # Check 24h resume count limit
            resume_log = state.get("_auto_resume_log", [])
            cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
            resume_log = [t for t in resume_log if t > cutoff]
            if len(resume_log) >= MAX_AUTO_RESUMES_24H:
                log(
                    f"AUTO-RESUME BLOCKED: {len(resume_log)} resumes in 24h "
                    f"(limit={MAX_AUTO_RESUMES_24H})"
                )
            else:
                stop_time = _safe_isoparse(state.get("stop_triggered_at", ""))
                cooldown_met = (
                    not stop_time
                    or (datetime.now() - stop_time).total_seconds()
                    > STOP_RESUME_COOLDOWN
                )
                # Check drawdown recovery (use smoothed value)
                stats = state.get("stats", {})
                peak = stats.get("portfolio_peak_usd", 0)
                value_history = state.get("_value_history", [])
                smooth_usd = (
                    sorted(value_history[-5:])[len(value_history[-5:]) // 2]
                    if len(value_history) >= 3
                    else total_usd
                )
                current_drawdown = (
                    (peak - smooth_usd) / peak if peak > 0 else 1.0
                )
                # Resume if drawdown recovered below threshold with margin
                resume_threshold = (
                    TRAILING_STOP_PCT * 0.7
                )  # must recover to 70% of stop level
                if cooldown_met and current_drawdown < resume_threshold:
                    log(
                        f"AUTO-RESUME: drawdown {current_drawdown:.1%} < "
                        f"{resume_threshold:.1%} threshold, cooldown met "
                        f"(resume {len(resume_log)+1}/{MAX_AUTO_RESUMES_24H})"
                    )
                    state.pop("stop_triggered", None)
                    state.pop("stop_notified", None)
                    state.pop("stop_triggered_at", None)
                    # Reset peak to current value to prevent immediate re-trigger
                    stats["portfolio_peak_usd"] = round(smooth_usd, 2)
                    # Record this resume
                    resume_log.append(datetime.now().isoformat())
                    state["_auto_resume_log"] = resume_log
                    save_state(state)
                    resumed_data = {
                        "status": "stop_resumed",
                        "previous_trigger": trigger_msg,
                        "drawdown_pct": round(current_drawdown * 100, 2),
                        "price": round(price, 2),
                        "resume_count_24h": len(resume_log),
                    }
                    emit(
                        "stop_resumed",
                        resumed_data,
                        notify=True,
                        tier="trade_alert",
                    )
                    resumed = True

        if not resumed:
            # Log dedup: only log stop message once per hour
            last_stop_log = _safe_isoparse(state.get("_last_stop_log", ""))
            if (
                not last_stop_log
                or (datetime.now() - last_stop_log).total_seconds() > 3600
            ):
                log(f"STOP ACTIVE: {trigger_msg}")
                state["_last_stop_log"] = datetime.now().isoformat()

            first_notify = not state.get("stop_notified")
            if first_notify:
                state["stop_notified"] = True
                state["stop_triggered_at"] = datetime.now().isoformat()
            save_state(state)
            stop_data = {
                "status": "stop_triggered" if first_notify else "stopped",
                "trigger": trigger_msg,
                "price": round(price, 2),
                "portfolio_usd": round(total_usd, 2),
                "auto_resume": STOP_AUTO_RESUME,
            }
            emit(
                "stop_triggered" if first_notify else "stopped",
                stop_data,
                notify=first_notify,
                tier="risk_alert" if first_notify else "",
            )
            return

    # IL estimation (use position entry_price, fallback to initial)
    position = state.get("position")
    if position and position.get("created_at"):
        entry_price = position.get("entry_price") or state["stats"].get(
            "initial_eth_price", price
        )
        il_pct = estimate_il(
            entry_price,
            price,
            (position.get("lower_price") or 0),
            (position.get("upper_price") or 0),
        )
        state["stats"]["estimated_il_pct"] = il_pct

    # Risk checks (pre-trigger) — skip if balance query failed
    trigger = check_rebalance_triggers(price, state, atr_pct, mtf)
    if balance_failed:
        log("Balance query failed — skipping risk checks this tick")
        risk_reject = None
    else:
        risk_reject = run_risk_checks(state, price, total_usd, trigger)

    tick_status = "no_action"
    rebalanced = False

    if not position or not position.get("tick_lower"):
        # No position — clean up any orphaned positions before creating new one
        residual_cleaned = cleanup_residual_positions("")
        if residual_cleaned:
            log(f"Cleaned {residual_cleaned} orphaned position(s) before initial deposit")
            eth_bal, usdc_bal, balance_failed = get_balances(force=True)
            total_usd = eth_bal * price + usdc_bal
        log("No active position — creating initial LP position")
        new_range = calc_optimal_range(price, atr_pct, mtf)
        log(
            f"Initial range: ${new_range['lower_price']:.2f}-${new_range['upper_price']:.2f} "
            f"({new_range['regime']}, width {new_range['half_width_pct']:.1f}%)"
        )

        # For initial deposit, skip risk checks except data validation
        initial_trigger = {
            "trigger": "initial_deposit",
            "priority": "mandatory",
            "detail": "first position",
        }

        if total_usd < MIN_TRADE_USD:
            log(f"Balance too low for initial deposit: ${total_usd:.2f}")
            tick_status = "insufficient_balance"
        else:
            rebalanced = execute_rebalance(state, price, new_range, initial_trigger)
            tick_status = "initial_deposit" if rebalanced else "initial_deposit_failed"

    elif risk_reject:
        log(f"Risk check: {risk_reject}")
        tick_status = "risk_rejected"

    elif trigger:
        # Check minimum range change for non-mandatory triggers
        if trigger["priority"] != "mandatory":
            new_range = calc_optimal_range(price, atr_pct, mtf)
            old_lower = tick_to_price(position["tick_lower"])
            old_upper = tick_to_price(position["tick_upper"])
            old_width = old_upper - old_lower
            new_width = new_range["upper_price"] - new_range["lower_price"]
            if old_width > 0:
                width_change = abs(new_width - old_width) / old_width
                if width_change < 0.05:
                    # Log at most once per 4h to avoid spam
                    last_skip = _safe_isoparse(state.get("_last_skip_log", ""))
                    now = datetime.now()
                    if not last_skip or (now - last_skip).total_seconds() > 3600:
                        log(
                            f"Range change too small ({width_change:.1%} < 5%)"
                            f" — skipping [{trigger['trigger']}]"
                        )
                        state["_last_skip_log"] = now.isoformat()
                    trigger = None
                    tick_status = "skip_small_change"

        if trigger:
            new_range = calc_optimal_range(price, atr_pct, mtf)
            log(
                f"Rebalance triggered: {trigger['trigger']} ({trigger.get('detail', '')}) "
                f"-> ${new_range['lower_price']:.2f}-${new_range['upper_price']:.2f} "
                f"({new_range['regime']})"
            )
            rebalanced = execute_rebalance(state, price, new_range, trigger)
            if rebalanced:
                tick_status = "rebalanced"
                errors["consecutive"] = 0
            else:
                tick_status = "rebalance_failed"
                errors["consecutive"] = errors.get("consecutive", 0) + 1
                n = errors["consecutive"]
                # Exponential backoff: 10min, 20min, 40min, ... capped at COOLDOWN_AFTER_ERRORS
                backoff = min(600 * (2 ** (n - 1)), COOLDOWN_AFTER_ERRORS)
                errors["cooldown_until"] = (
                    datetime.now() + timedelta(seconds=backoff)
                ).isoformat()
                log(f"Rebalance failed ({n} consecutive) — cooldown {backoff // 60}min")
                state["errors"] = errors

    else:
        tick_status = "in_range"

    # Update time-in-range
    position = state.get("position")
    if position and position.get("tick_lower"):
        lower_p = tick_to_price(position["tick_lower"])
        upper_p = tick_to_price(position["tick_upper"])
        in_range = lower_p <= price <= upper_p

        # Running average
        checks = len(history)
        old_pct = state["stats"].get("time_in_range_pct", 100.0)
        if checks > 1:
            state["stats"]["time_in_range_pct"] = round(
                old_pct * (checks - 1) / checks + (100.0 if in_range else 0.0) / checks,
                1,
            )

    state["stats"]["last_check"] = datetime.now().isoformat()
    # Save balance snapshot for fallback
    if not balance_failed:
        state["last_balances"] = {
            "eth": round(eth_bal, 6),
            "usdc": round(usdc_bal, 2),
            "time": datetime.now().isoformat(),
        }
    save_state(state)

    # Emit tick event
    is_trade = tick_status in (
        "rebalanced",
        "first_deploy",
        "initial_deposit",
    )
    is_quiet = tick_status in (
        "in_range",
        "no_action",
        "risk_rejected",
        "skip_small_change",
    )
    stats = state.get("stats", {})
    pnl = calc_pnl(stats, total_usd, price)
    unclaimed_fee_usd = stats.get("unclaimed_fee_usd", 0)
    claimed_fee_usd = stats.get("total_fees_claimed_usd", 0)

    # IL estimation: exact V3 formula, position entry price > initial price
    pos_entry = (position.get("entry_price") or 0) if position else 0
    entry_price = pos_entry or stats.get("initial_eth_price", 0)
    pos_lower = (position.get("lower_price") or 0) if position else 0
    pos_upper = (position.get("upper_price") or 0) if position else 0
    il_pct = (
        estimate_il(entry_price, price, pos_lower, pos_upper) if entry_price else 0.0
    )
    il_usd = round(il_pct / 100 * total_usd, 2) if il_pct else 0.0

    tick_data = {
        "status": tick_status,
        "price": round(price, 2),
        "atr_pct": round(atr_pct, 2),
        "regime": classify_volatility(atr_pct),
        "trend": mtf.get("trend", "neutral"),
        "trend_strength": round(mtf.get("strength", 0), 2),
        "portfolio_usd": round(total_usd, 2),
        "pnl_usd": pnl["pnl_usd"],
        "pnl_pct": round(pnl["pnl_pct"], 2),
        "pnl_eth": pnl["pnl_eth"],
        "pnl_eth_pct": round(pnl["pnl_eth_pct"], 2),
        "pnl_valid": pnl["valid"],
        "unclaimed_fee_usd": round(unclaimed_fee_usd, 2),
        "total_fees_claimed_usd": round(claimed_fee_usd, 2),
        "il_pct": round(il_pct, 2),
        "il_usd": il_usd,
        "fee_apy": pnl["fee_apy"],
        "net_apy": pnl["net_apy"],
        "days_running": pnl["days_running"],
        "cost_basis": pnl["cost_basis"],
        "balances": {
            "eth": round(eth_bal, 6),
            "usdc": round(usdc_bal, 2),
            "lp_usd": round(lp_value, 2),
            "lp_assets": [
                {
                    "symbol": a.get("tokenSymbol", ""),
                    "amount": float(a.get("coinAmount", 0)),
                }
                for a in lp_assets
                if float(a.get("coinAmount", 0)) > 0
            ],
        },
        "time_in_range_pct": stats.get("time_in_range_pct", 0),
        "total_rebalances": stats.get("total_rebalances", 0),
    }
    if position and position.get("tick_lower"):
        tick_data["position"] = {
            "tick_lower": position["tick_lower"],
            "tick_upper": position["tick_upper"],
            "lower_price": position.get("lower_price"),
            "upper_price": position.get("upper_price"),
        }
    if trigger:
        tick_data["trigger"] = trigger.get("trigger", str(trigger))

    # Determine notification tier
    tier = ""
    if is_trade:
        tier = "trade_alert"
    elif not is_quiet:
        pass  # non-quiet non-trade: emit without notification
    else:
        # Hourly pulse: push if QUIET_INTERVAL elapsed since last notification
        last_notify = _safe_isoparse(state.get("_last_notify_ts", ""))
        if (
            not last_notify
            or (datetime.now() - last_notify).total_seconds() >= QUIET_INTERVAL
        ):
            tier = "hourly_pulse"
            state["_last_notify_ts"] = datetime.now().isoformat()
            save_state(state)

    notify = tier != ""
    emit("tick", tick_data, notify=notify, tier=tier)

    # Cache snapshot for fast status queries (includes external portfolio)
    tick_data["_cached_at"] = datetime.now().isoformat()
    tick_data["external_portfolio"] = query_external_portfolio()
    state["_cached_snapshot"] = tick_data
    save_state(state)


# ── Sub-commands ────────────────────────────────────────────────────────────


def _print_status_from_snapshot(snap: dict, state: dict, cached_age_s: float = 0):
    """Render status text from a tick_data snapshot (cached or live)."""
    position = state.get("position")
    stats = state.get("stats", {})
    price = snap.get("price", 0)
    bals = snap.get("balances", {})
    eth_bal = bals.get("eth", 0)
    usdc_bal = bals.get("usdc", 0)
    lp_value = bals.get("lp_usd", 0)
    lp_assets = bals.get("lp_assets", [])
    total_usd = snap.get("portfolio_usd", 0)
    unclaimed_fee = snap.get("unclaimed_fee_usd", 0)

    # ── Portfolio (cross-platform) ──
    ext = snap.get("external_portfolio", {})
    if ext or total_usd > 0:
        print("**Portfolio**")
        grand_total = 0.0
        for platform, value in ext.items():
            print(f"> {platform}: `${value:,.2f}`")
            grand_total += value
        if total_usd > 0:
            print(f"> Base (CL-LP): `${total_usd:,.2f}`")
            grand_total += total_usd
        print(f"> **Total: `${grand_total:,.2f}`**")
        print()

    header = "**CL LP Auto-Rebalancer v1 -- 状态**"
    if cached_age_s > 0:
        header += f" (缓存 {cached_age_s:.0f}s 前)"
    print(header)
    print(f"> 价格: `${price:.2f}`" if price else "> 价格: 不可用")

    # Wallet + LP breakdown
    wallet_usd = eth_bal * price + usdc_bal
    print(f"> 钱包: `{eth_bal:.6f}` ETH + `${usdc_bal:.2f}` USDC (`${wallet_usd:.0f}`)")

    if lp_value > 0:
        lp_detail_parts = []
        for a in lp_assets:
            sym = a.get("symbol", "")
            amt = a.get("amount", 0)
            if sym and amt > 0:
                usd_val = amt * price if sym.upper() in ("WETH", "ETH") else amt
                lp_detail_parts.append(f"{amt:.4f} {sym} (${usd_val:,.0f})")
        lp_detail = " + ".join(lp_detail_parts) if lp_detail_parts else ""
        lp_line = f"> LP 头寸: `${lp_value:.0f}`"
        if lp_detail:
            lp_line += f" ({lp_detail})"
        if unclaimed_fee > 0.01:
            lp_line += f" | 待领手续费: `${unclaimed_fee:.2f}`"
        print(lp_line)

    print(f"> **总价值: `${total_usd:.0f}`**")

    # Position range
    pos_snap = snap.get("position")
    if pos_snap:
        lower_p = pos_snap.get("lower_price", 0)
        upper_p = pos_snap.get("upper_price", 0)
        if lower_p and upper_p:
            in_range = lower_p <= (price or 0) <= upper_p
            status_emoji = "✅" if in_range else "⚠️"
            status_str = "范围内" if in_range else "范围外"
            edge_str = ""
            if in_range and price:
                edge_dist = min(
                    (price - lower_p) / (upper_p - lower_p),
                    (upper_p - price) / (upper_p - lower_p),
                )
                edge_str = f" | 边缘距离: `{edge_dist:.0%}`"
            print(
                f"> {status_emoji} 范围: `${lower_p:.2f}` - `${upper_p:.2f}` ({status_str}{edge_str})"
            )
            if price:
                bar_w = 30
                pos_ratio = max(0.0, min(1.0, (price - lower_p) / (upper_p - lower_p)))
                cursor = round(pos_ratio * (bar_w - 1))
                bar = list("░" * bar_w)
                if 0 <= cursor < bar_w:
                    bar[cursor] = "█"
                print(f"> `${lower_p:.0f} [{''.join(bar)}] ${upper_p:.0f}`")
                print(f"> `{' ' * (len(f'${lower_p:.0f} [') + cursor)}▲${price:.0f}`")
    elif position and position.get("tick_lower"):
        lower_p = position.get("lower_price", tick_to_price(position["tick_lower"]))
        upper_p = position.get("upper_price", tick_to_price(position["tick_upper"]))
        print(f"> 范围: `${lower_p:.2f}` - `${upper_p:.2f}`")
    else:
        print("> 头寸: 未建立")

    if position and position.get("created_at"):
        created_dt = _safe_isoparse(position["created_at"])
        if created_dt:
            age_h = (datetime.now() - created_dt).total_seconds() / 3600
            rebal_count = stats.get("total_rebalances", 0)
            print(
                f"> 头寸年龄: `{age_h:.1f}h` | 调仓: `{rebal_count}` 次 | token_id: `{position.get('token_id', 'N/A')}`"
            )

    # ATR + Trend
    atr_pct = snap.get("atr_pct", 0)
    regime = snap.get("regime", "")
    if atr_pct:
        print(f"\n> ATR(1H): `{atr_pct:.2f}%` ({regime})")
    trend = snap.get("trend", "")
    trend_str = snap.get("trend_strength", 0)
    if trend:
        print(f"> 趋势: `{trend}` ({trend_str:.0%})")

    # PnL & Yield
    print("\n**收益**")
    if snap.get("pnl_valid") and price:
        print(f"> PnL: **`${snap['pnl_usd']:+.2f}`** (`{snap['pnl_pct']:+.1f}%`)")
        print(
            f"> 年化 APY: Fee `{snap.get('fee_apy', 0):+.1f}%` | Net `{snap.get('net_apy', 0):+.1f}%` (运行 `{snap.get('days_running', 0):.1f}` 天)"
        )
    else:
        print("> PnL: 数据不足")

    claimed_fee = snap.get("total_fees_claimed_usd", 0)
    total_fees = claimed_fee + unclaimed_fee
    if total_fees > 0.01:
        print(
            f"> LP 手续费: `${total_fees:.2f}` (已领 `${claimed_fee:.2f}` + 待领 `${unclaimed_fee:.2f}`)"
        )

    il_pct = snap.get("il_pct", 0)
    il_usd = snap.get("il_usd", 0)
    if il_pct:
        print(f"> 无常损失: `${il_usd:.2f}` (`{il_pct:.2f}%`)")

    print("\n**运行**")
    tir = snap.get("time_in_range_pct", 0)
    rebalances = snap.get("total_rebalances", 0)
    print(f"> 范围内时间: `{tir:.0f}%` | 调仓次数: `{rebalances}`")

    stop = state.get("stop_triggered")
    if stop:
        print(f"\n> 🔴 **交易已停止**: `{stop}`")
        print("> 使用 `resume-trading` 恢复")


# Maximum cache age: 360s (slightly over 5-min tick interval)
_SNAPSHOT_MAX_AGE_S = 360


def status():
    """Print current status — uses cached tick snapshot if fresh, else queries live."""
    state = load_state()

    # Try cached snapshot first
    cached = state.get("_cached_snapshot")
    if cached:
        cached_at = _safe_isoparse(cached.get("_cached_at", ""))
        if cached_at:
            age_s = (datetime.now() - cached_at).total_seconds()
            if age_s < _SNAPSHOT_MAX_AGE_S:
                _print_status_from_snapshot(cached, state, cached_age_s=age_s)
                return

    # Cache stale or missing — live query (force refresh for accurate display)
    price = get_eth_price()
    eth_bal, usdc_bal, bal_failed = get_balances(force=True)
    if bal_failed:
        print("> 余额查询失败，显示的余额可能不准确")
    wallet_usd = eth_bal * (price or 0) + usdc_bal
    position = state.get("position")
    lp_value = 0.0
    unclaimed_fee = 0.0
    lp_assets_raw = []
    if position and position.get("token_id"):
        pos_detail = get_position_detail(position["token_id"])
        lp_value = pos_detail["value"]
        unclaimed_fee = pos_detail["unclaimed_fee_usd"]
        lp_assets_raw = pos_detail.get("assets", [])
    total_usd = wallet_usd + lp_value
    stats = state.get("stats", {})
    history = state.get("price_history", [])

    # Build a live snapshot in tick_data format for the shared renderer
    stats["unclaimed_fee_usd"] = round(unclaimed_fee, 2)
    pnl = calc_pnl(stats, total_usd, price)

    pos_entry = (position.get("entry_price") or 0) if position else 0
    entry_price = pos_entry or stats.get("initial_eth_price", 0)
    pos_lower = (position.get("lower_price") or 0) if position else 0
    pos_upper = (position.get("upper_price") or 0) if position else 0
    il_pct = (
        estimate_il(entry_price, price, pos_lower, pos_upper) if entry_price else 0.0
    )
    il_usd = round(il_pct / 100 * total_usd, 2) if il_pct else 0.0

    # MTF
    mtf = {}
    if price and len(history) >= MTF_SHORT_PERIOD:
        mtf = analyze_multi_timeframe(history, price)

    # ATR
    kline_cache = state.get("kline_cache")
    atr_pct = kline_cache.get("atr_pct", 0) if kline_cache else 0

    live_snap = {
        "price": round(price, 2) if price else 0,
        "atr_pct": round(atr_pct, 2),
        "regime": classify_volatility(atr_pct),
        "trend": mtf.get("trend", ""),
        "trend_strength": round(mtf.get("strength", 0), 2),
        "portfolio_usd": round(total_usd, 2),
        "pnl_usd": pnl["pnl_usd"],
        "pnl_pct": round(pnl["pnl_pct"], 2),
        "pnl_eth": pnl["pnl_eth"],
        "pnl_eth_pct": round(pnl["pnl_eth_pct"], 2),
        "pnl_valid": pnl["valid"],
        "unclaimed_fee_usd": round(unclaimed_fee, 2),
        "total_fees_claimed_usd": round(stats.get("total_fees_claimed_usd", 0), 2),
        "il_pct": round(il_pct, 2),
        "il_usd": il_usd,
        "fee_apy": pnl["fee_apy"],
        "net_apy": pnl["net_apy"],
        "days_running": pnl["days_running"],
        "cost_basis": pnl["cost_basis"],
        "balances": {
            "eth": round(eth_bal, 6),
            "usdc": round(usdc_bal, 2),
            "lp_usd": round(lp_value, 2),
            "lp_assets": [
                {
                    "symbol": a.get("tokenSymbol", ""),
                    "amount": float(a.get("coinAmount", 0)),
                }
                for a in lp_assets_raw
                if float(a.get("coinAmount", 0)) > 0
            ],
        },
        "time_in_range_pct": stats.get("time_in_range_pct", 0),
        "total_rebalances": stats.get("total_rebalances", 0),
    }
    if position and position.get("tick_lower"):
        live_snap["position"] = {
            "tick_lower": position["tick_lower"],
            "tick_upper": position["tick_upper"],
            "lower_price": position.get("lower_price"),
            "upper_price": position.get("upper_price"),
        }

    live_snap["external_portfolio"] = query_external_portfolio()

    _print_status_from_snapshot(live_snap, state)


def report():
    """Daily report."""
    state = load_state()
    price = get_eth_price()
    eth_bal, usdc_bal, _ = get_balances()
    total_usd = eth_bal * (price or 0) + usdc_bal
    stats = state.get("stats", {})
    position = state.get("position")
    history = state.get("price_history", [])
    rebalances = state.get("rebalance_history", [])

    kline_cache = state.get("kline_cache")
    atr = kline_cache.get("atr_pct", 0) if kline_cache else 0
    regime = classify_volatility(atr)

    tir = stats.get("time_in_range_pct", 0)
    total_rebal = stats.get("total_rebalances", 0)

    today = datetime.now().date().isoformat()
    today_rebal = [r for r in rebalances if r["time"].startswith(today)]

    mtf = {}
    if price and len(history) >= MTF_SHORT_PERIOD:
        mtf = analyze_multi_timeframe(history, price)

    # Refetch position for fresh unclaimed fees (report runs independently)
    unclaimed_fee = 0.0
    lp_value = 0.0
    if position and position.get("token_id"):
        pos_detail = get_position_detail(position["token_id"])
        unclaimed_fee = pos_detail.get("unclaimed_fee_usd", 0)
        lp_value = pos_detail.get("value", 0)
        total_usd = eth_bal * (price or 0) + usdc_bal + lp_value
        # Update unclaimed in stats so calc_pnl picks it up for APY
        stats["unclaimed_fee_usd"] = round(unclaimed_fee, 2)
    claimed_fee = stats.get("total_fees_claimed_usd", 0)

    # Recalculate PnL with fresh total_usd (includes LP value)
    pnl = calc_pnl(stats, total_usd, price)

    # IL: exact V3 formula, position entry price > initial price
    pos_entry = (position.get("entry_price") or 0) if position else 0
    entry_price = pos_entry or stats.get("initial_eth_price")
    pos_lower = (position.get("lower_price") or 0) if position else 0
    pos_upper = (position.get("upper_price") or 0) if position else 0
    il_pct = (
        estimate_il(entry_price, price, pos_lower, pos_upper)
        if entry_price and price
        else 0.0
    )
    il_usd = round(il_pct / 100 * total_usd, 2) if il_pct else 0.0

    report_data = {
        "price": round(price, 2) if price else None,
        "atr_pct": round(atr, 2),
        "regime": regime,
        "balances": {"eth": round(eth_bal, 6), "usdc": round(usdc_bal, 2)},
        "portfolio_usd": round(total_usd, 2),
        "pnl_usd": pnl["pnl_usd"],
        "pnl_pct": round(pnl["pnl_pct"], 2),
        "pnl_eth": pnl["pnl_eth"],
        "pnl_eth_pct": round(pnl["pnl_eth_pct"], 2),
        "pnl_valid": pnl["valid"],
        "fee_apy": pnl["fee_apy"],
        "net_apy": pnl["net_apy"],
        "days_running": pnl["days_running"],
        "cost_basis": pnl["cost_basis"],
        "total_fees_claimed_usd": round(claimed_fee, 2),
        "unclaimed_fee_usd": round(unclaimed_fee, 2),
        "il_pct": round(il_pct, 2),
        "il_usd": il_usd,
        "time_in_range_pct": round(tir, 1),
        "total_rebalances": total_rebal,
        "today_rebalances": today_rebal[-5:],
        "trend": mtf.get("trend", "neutral"),
        "trend_strength": round(mtf.get("strength", 0), 2),
        "started_at": stats.get("started_at", ""),
    }
    if position and position.get("lower_price"):
        in_range = position["lower_price"] <= (price or 0) <= position["upper_price"]
        report_data["position"] = {
            "lower_price": position["lower_price"],
            "upper_price": position["upper_price"],
            "in_range": in_range,
        }
    emit("report", report_data, notify=True, tier="daily_report")


def history_cmd():
    """Show rebalance history."""
    state = load_state()
    rebalances = state.get("rebalance_history", [])
    if not rebalances:
        print("暂无调仓记录")
        return

    print(f"**最近 `{len(rebalances)}` 次调仓**")
    for r in rebalances:
        old = r.get("old_range", [None, None])
        new = r.get("new_range", [None, None])
        old_str = f"[{old[0]},{old[1]}]" if old[0] else "N/A"
        new_str = f"[{new[0]},{new[1]}]" if new[0] else "N/A"
        print(
            f"> `{r['time'][:19]}` | {r['trigger']} ({r.get('detail', '')}) "
            f"| {old_str} -> {new_str}"
        )


def reset():
    """Reset state, close position if active."""
    state = load_state()
    position = state.get("position")

    # Try to close existing position — record fees before wiping state
    carried_fees = 0.0
    if position and position.get("token_id"):
        log("Resetting: closing existing position...")
        pre_claim = get_position_detail(position["token_id"])
        unclaimed = pre_claim.get("unclaimed_fee_usd", 0)
        claimed = defi_claim_fees(position["token_id"])
        if claimed and unclaimed > 0:
            carried_fees = round(
                state["stats"].get("total_fees_claimed_usd", 0) + unclaimed, 2
            )
            log(f"  Fees claimed on reset: ${unclaimed:.2f} (carried: ${carried_fees:.2f})")
        else:
            carried_fees = round(state["stats"].get("total_fees_claimed_usd", 0), 2)
        defi_redeem(position["token_id"])

    new_state = (
        load_state.__wrapped__()
        if hasattr(load_state, "__wrapped__")
        else {
            "version": 1,
            "wallet_address": WALLET_ADDR,
            "pool": {
                "investment_id": INVESTMENT_ID,
                "chain": POOL_CHAIN,
                "token0": TOKEN0,
                "token1": TOKEN1,
                "fee_tier": FEE_TIER,
                "tick_spacing": TICK_SPACING,
            },
            "position": None,
            "price_history": [],
            "vol_history": [],
            "rebalance_history": [],
            "stats": {
                "total_rebalances": 0,
                "total_fees_claimed_usd": carried_fees,
                "total_gas_spent_usd": 0.0,
                "time_in_range_pct": 100.0,
                "net_yield_usd": 0.0,
                "initial_portfolio_usd": None,
                "initial_eth_price": None,
                "started_at": datetime.now().isoformat(),
                "last_check": None,
                "total_deposits_usd": 0.0,
                "deposit_history": [],
                "estimated_il_pct": 0.0,
            },
            "errors": {"consecutive": 0, "cooldown_until": None},
            "stop_triggered": None,
            "approved_routers": [],
        }
    )
    save_state(new_state)

    price = get_eth_price()
    eth_bal, usdc_bal, _ = get_balances()
    total = eth_bal * (price or 0) + usdc_bal
    print(f"LP 已重置。价格: `${price:.2f}`, 余额: `${total:.0f}`")
    print("下次 tick 将重新建仓。")


def close():
    """Close position completely and exit."""
    state = load_state()
    position = state.get("position")

    if not position or not position.get("token_id"):
        print("无活跃头寸")
        return

    token_id = position["token_id"]
    log(f"Closing position token_id={token_id}")

    # Record unclaimed fees before claiming
    pre_claim = get_position_detail(token_id)
    unclaimed = pre_claim.get("unclaimed_fee_usd", 0)

    claimed = defi_claim_fees(token_id)
    if claimed and unclaimed > 0:
        state["stats"]["total_fees_claimed_usd"] = round(
            state["stats"].get("total_fees_claimed_usd", 0) + unclaimed, 2
        )
        state["stats"]["unclaimed_fee_usd"] = 0.0
        log(f"  Fees claimed on close: ${unclaimed:.2f} (total: ${state['stats']['total_fees_claimed_usd']:.2f})")

    redeemed = defi_redeem(token_id)

    if redeemed:
        state["position"] = None
        state["stop_triggered"] = "manual_close"
        save_state(state)

        eth_bal, usdc_bal, _ = get_balances()
        price = get_eth_price()
        total = eth_bal * (price or 0) + usdc_bal
        emit(
            "position_closed",
            {
                "token_id": token_id,
                "portfolio_usd": round(total, 2),
                "balances": {
                    "eth": round(eth_bal, 6),
                    "usdc": round(usdc_bal, 2),
                },
            },
            notify=True,
        )
    else:
        print("关闭失败 — 请手动检查")


def analyze():
    """Detailed JSON analysis for AI agent."""
    state = load_state()
    price = get_eth_price()
    eth_bal, usdc_bal, _ = get_balances()
    history = state.get("price_history", [])
    position = state.get("position")
    stats = state.get("stats", {})
    rebalances = state.get("rebalance_history", [])

    if not price:
        print(json.dumps({"error": "price_unavailable"}))
        return

    total_usd = eth_bal * price + usdc_bal
    mtf = analyze_multi_timeframe(history, price)

    candles = get_kline_data("1H", 24)
    kline_vol = calc_kline_volatility(candles) if candles else None
    atr_pct = kline_vol if kline_vol else 2.0

    # Optimal range if we were to rebalance now
    optimal = calc_optimal_range(price, atr_pct, mtf)

    # Current trigger status
    trigger = check_rebalance_triggers(price, state, atr_pct, mtf)

    # IL (exact V3, position entry price > initial price)
    position = state.get("position")
    pos_entry = (position.get("entry_price") or 0) if position else 0
    initial_price = pos_entry or stats.get("initial_eth_price", price)
    pos_lower = (position.get("lower_price") or 0) if position else 0
    pos_upper = (position.get("upper_price") or 0) if position else 0
    il_pct = estimate_il(initial_price, price, pos_lower, pos_upper)

    analysis = {
        "version": "1.0",
        "timestamp": datetime.now().isoformat(),
        "market": {
            "price": round(price, 2),
            "atr_pct": round(atr_pct, 2),
            "regime": classify_volatility(atr_pct),
        },
        "multi_timeframe": mtf,
        "portfolio": {
            "eth": round(eth_bal, 6),
            "usdc": round(usdc_bal, 2),
            "total_usd": round(total_usd, 2),
            "eth_pct": round((eth_bal * price / total_usd) * 100, 1)
            if total_usd > 0
            else 0,
        },
        "position": {
            "tick_lower": position["tick_lower"] if position else None,
            "tick_upper": position["tick_upper"] if position else None,
            "lower_price": position.get("lower_price") if position else None,
            "upper_price": position.get("upper_price") if position else None,
            "token_id": position.get("token_id") if position else None,
            "age_hours": round(
                (
                    datetime.now() - _safe_isoparse(position["created_at"])
                ).total_seconds()
                / 3600,
                1,
            )
            if position
            and position.get("created_at")
            and _safe_isoparse(position["created_at"])
            else None,
        },
        "optimal_range": optimal,
        "trigger": trigger,
        "stats": {
            "total_rebalances": stats.get("total_rebalances", 0),
            "time_in_range_pct": stats.get("time_in_range_pct", 0),
            "estimated_il_pct": il_pct,
            "total_pnl": calc_pnl(stats, total_usd, price)["pnl_usd"],
        },
        "rebalance_history": rebalances[-10:],
    }

    print(json.dumps(analysis, indent=2))


def deposit():
    """Manually record deposit/withdrawal."""
    if len(sys.argv) < 3:
        print("用法: cl_lp.py deposit <金额USD>")
        print("正数=存入, 负数=取出")
        return

    try:
        amount = float(sys.argv[2])
    except ValueError:
        print("无效金额")
        return

    state = load_state()
    event = {
        "time": datetime.now().isoformat(),
        "usd_value": round(amount, 2),
        "type": "manual_deposit" if amount > 0 else "manual_withdrawal",
    }
    dep_history = state["stats"].get("deposit_history", [])
    dep_history.append(event)
    state["stats"]["deposit_history"] = dep_history
    state["stats"]["total_deposits_usd"] = round(
        state["stats"].get("total_deposits_usd", 0) + amount, 2
    )
    save_state(state)

    type_cn = "存入" if amount > 0 else "取出"
    print(f"已记录{type_cn}: ${abs(amount):.2f}")


def resume_trading():
    """Clear stop and resume."""
    state = load_state()
    if not state.get("stop_triggered"):
        print("交易未停止，无需恢复")
        return

    old_trigger = state["stop_triggered"]
    state.pop("stop_triggered", None)
    state.pop("stop_notified", None)
    state.pop("stop_triggered_at", None)
    # Reset failure counters and resume log on manual resume
    state["_consecutive_deposit_failures"] = 0
    state["_auto_resume_log"] = []
    # Reset peak to current portfolio to prevent immediate re-trigger
    eth_bal, usdc_bal, _ = get_balances(force=True)
    price = get_eth_price()
    if price:
        current_usd = eth_bal * price + usdc_bal
        state.setdefault("stats", {})["portfolio_peak_usd"] = round(current_usd, 2)
    save_state(state)
    log(f"Trading resumed (was: {old_trigger})")
    emit(
        "trading_resumed",
        {"previous_trigger": old_trigger},
        notify=True,
    )


# ── Main ────────────────────────────────────────────────────────────────────

COMMANDS = {
    "tick": tick,
    "status": status,
    "report": report,
    "history": history_cmd,
    "reset": reset,
    "close": close,
    "analyze": analyze,
    "deposit": deposit,
    "resume-trading": resume_trading,
}


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "tick"
    handler = COMMANDS.get(cmd)
    if handler:
        handler()
    else:
        print(f"未知命令: {cmd}")
        print(f"可用命令: {', '.join(COMMANDS.keys())}")
        sys.exit(1)
