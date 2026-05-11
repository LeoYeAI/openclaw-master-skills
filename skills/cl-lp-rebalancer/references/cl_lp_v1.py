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
                os.environ.setdefault(k.strip(), v.strip())


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
EMERGENCY_RANGE_MULT = CFG["emergency_range_mult"]

STOP_LOSS_PCT = CFG["stop_loss_pct"]
TRAILING_STOP_PCT = CFG["trailing_stop_pct"]
SLIPPAGE_PCT = CFG["slippage_pct"]
GAS_RESERVE_ETH = CFG["gas_reserve_eth"]
MIN_TRADE_USD = CFG["min_trade_usd"]

QUIET_INTERVAL = CFG["quiet_interval_seconds"]
MAX_CONSECUTIVE_ERRORS = CFG["max_consecutive_errors"]
COOLDOWN_AFTER_ERRORS = CFG["cooldown_after_errors_seconds"]

# ── Multi-Timeframe settings (from grid-trading) ───────────────────────────

MTF_SHORT_PERIOD = 5
MTF_MEDIUM_PERIOD = 12
MTF_LONG_PERIOD = 48
MTF_STRUCTURE_PERIOD = 96
EMA_PERIOD = 20

# ── Paths ───────────────────────────────────────────────────────────────────

STATE_FILE = SCRIPT_DIR / "cl_lp_state.json"
LOG_FILE = SCRIPT_DIR / "cl_lp_v1.log"
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

LOCK_FILE = SCRIPT_DIR / ".cl_lp_v1.lock"
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


def get_balances() -> tuple[float, float, bool]:
    """Get ETH and USDC balances. Returns (eth, usdc, failed)."""
    data = onchainos_cmd(["wallet", "balance", "--chain", CHAIN_ID], timeout=15)
    if not data or not data.get("ok") or not data.get("data"):
        log(f"Balance query failed, raw: {json.dumps(data)[:200] if data else 'None'}")
        return 0.0, 0.0, True
    # Verify returned address matches configured wallet
    # Address is inside details[].tokenAssets[].address, not at top level
    details = data["data"].get("details", [])
    if details and WALLET_ADDR:
        first_addr = ""
        for chain_detail in details:
            for token in chain_detail.get("tokenAssets", []):
                first_addr = token.get("address", "")
                if first_addr:
                    break
            if first_addr:
                break
        if first_addr and first_addr.lower() != WALLET_ADDR.lower():
            log(
                f"Balance address mismatch: got {first_addr}, "
                f"expected {WALLET_ADDR} — wrong account active"
            )
            return 0.0, 0.0, True
    eth, usdc = 0.0, 0.0
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


def find_latest_token_id() -> str:
    """Query position-detail to find the latest LP token ID for this pool."""
    if not WALLET_ADDR:
        return ""
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
        return ""
    try:
        for platform in data["data"]:
            for wallet in platform.get("walletIdPlatformDetailList", []):
                for network in wallet.get("networkHoldVoList", []):
                    for invest in network.get("investTokenBalanceVoList", []):
                        positions = invest.get("positionList", [])
                        if positions:
                            # Return the last (newest) position's tokenId
                            return str(positions[-1].get("tokenId", ""))
    except (KeyError, ValueError, TypeError):
        pass
    return ""


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

    # [2] Volatility regime change — adaptive
    created_atr = position.get("created_atr_pct", 0)
    if created_atr > 0:
        vol_change = abs(atr_pct - created_atr) / created_atr
        if vol_change > 0.3:
            old_regime = classify_volatility(created_atr)
            new_regime = classify_volatility(atr_pct)
            return {
                "trigger": "volatility_shift",
                "priority": "adaptive",
                "detail": f"{old_regime}->{new_regime} (delta {vol_change:.0%})",
            }

    # [4] Time decay — maintenance (>24h)
    created_at = position.get("created_at")
    if created_at:
        created_dt = _safe_isoparse(created_at)
        age_seconds = (datetime.now() - created_dt).total_seconds() if created_dt else 0
        if age_seconds > 86400:  # 24h
            return {
                "trigger": "time_decay",
                "priority": "maintenance",
                "detail": f"{age_seconds / 3600:.1f}h old",
            }

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
    initial = stats.get("initial_portfolio_usd")
    if initial and initial > 0 and len(value_history) >= 3:
        # Median of recent values for stop decisions
        smooth_usd = sorted(value_history[-5:])[len(value_history[-5:]) // 2]
        cost_basis = initial + stats.get("total_deposits_usd", 0)
        peak = stats.get("portfolio_peak_usd", cost_basis)

        # Peak only updates if confirmed by 2 consecutive readings above old peak
        prev_val = value_history[-2] if len(value_history) >= 2 else 0
        if smooth_usd > peak and prev_val > peak:
            peak = smooth_usd
            stats["portfolio_peak_usd"] = round(peak, 2)

        pnl_pct = (smooth_usd - cost_basis) / cost_basis if cost_basis > 0 else 0
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


def _broadcast_defi_txs(data: dict, label: str) -> bool:
    """Broadcast all transactions from a defi command response.
    Returns True if all transactions were broadcast successfully."""
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
        # Convert hex value to decimal ETH
        value_wei = int(value, 16) if value.startswith("0x") else int(value)
        value_eth = str(value_wei / 1e18) if value_wei > 0 else "0"
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
                "--value",
                value_eth,
            ],
            timeout=60,
        )
        if broadcast_data and broadcast_data.get("ok") and broadcast_data.get("data"):
            r = broadcast_data["data"]
            if isinstance(r, list):
                r = r[0] if r else {}
            tx_hash = r.get("txHash") or r.get("hash") or r.get("orderId")
            log(f"  {label} [{tx_type}] broadcast OK: {tx_hash}")
        else:
            detail = (
                json.dumps(broadcast_data)[:200] if broadcast_data else "no response"
            )
            log(f"  {label} [{tx_type}] broadcast failed: {detail}")
            return False
        time.sleep(2)  # wait between txs
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
    """Remove all liquidity from V3 position."""
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
            "--percent",
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
            f"--tick-lower={tick_lower}",
            f"--tick-upper={tick_upper}",
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
            f"--tick-lower={tick_lower}",
            f"--tick-upper={tick_upper}",
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
    value_wei = int(tx.get("value", "0"))
    value_eth = str(value_wei / 1e18) if value_wei > 0 else "0"
    args = [
        "wallet",
        "contract-call",
        "--to",
        tx["to"],
        "--chain",
        CHAIN_ID,
        "--input-data",
        tx.get("data", "0x"),
        "--value",
        value_eth,
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
    unclaimed = state.get("stats", {}).get("unclaimed_fee_usd", 0)
    if token_id and unclaimed >= MIN_TRADE_USD:
        claimed = defi_claim_fees(token_id)
        if claimed:
            log(f"  Fees claimed: {json.dumps(claimed)[:200]}")
    elif token_id:
        log(f"  Skip claim: unclaimed ${unclaimed:.2f} < ${MIN_TRADE_USD:.0f}")

    # Step 2: Remove liquidity
    if token_id:
        redeemed = defi_redeem(token_id)
        if not redeemed:
            log("  Redeem failed — attempting emergency wide deposit")
            return _emergency_deposit(state, price, trigger)
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

    # Step 3: Get current balances after redeem
    eth_bal, usdc_bal, bal_failed = get_balances()
    if bal_failed:
        log("  Balance query failed after redeem — funds may be idle")
        # Don't crash, but try to continue with what we have
        time.sleep(5)
        eth_bal, usdc_bal, bal_failed = get_balances()
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

    # Step 4: Deposit with USDC only — OKX adapter handles internal swap
    usdc_deposit = int(usdc_bal * 0.95)  # 95% to leave buffer
    log(f"  Balances: ETH={eth_bal:.6f} USDC={usdc_bal:.2f} deposit={usdc_deposit}")
    user_input_json = json.dumps(
        [
            {
                "chainIndex": CHAIN_ID,
                "coinAmount": str(usdc_deposit),
                "tokenAddress": USDC_ADDR,
            }
        ]
    )

    # Step 5: Deposit at new range
    log(f"  Deposit input: {user_input_json[:200]}")
    deposit_result = defi_deposit(user_input_json, new_tick_lower, new_tick_upper)
    if not deposit_result:
        log("  Deposit failed — attempting emergency wide deposit")
        return _emergency_deposit(state, price, trigger)

    # Deposit returns bool; recover token_id from on-chain position-detail
    time.sleep(5)  # wait for chain confirmation
    new_token_id = find_latest_token_id()
    if new_token_id:
        log(f"  Found token_id from position-detail: {new_token_id}")
    else:
        log("  Warning: deposit broadcast OK but token_id not found")

    # Update state
    now_iso = datetime.now().isoformat()
    candles = get_kline_data("1H", 24)
    current_atr = calc_kline_volatility(candles) if candles else 0

    state.pop("_rebalance_in_progress", None)
    state["position"] = {
        "token_id": new_token_id,
        "tick_lower": new_tick_lower,
        "tick_upper": new_tick_upper,
        "lower_price": new_range["lower_price"],
        "upper_price": new_range["upper_price"],
        "created_at": now_iso,
        "created_atr_pct": round(current_atr, 3),
    }

    # Record rebalance
    rebalance_record = {
        "time": now_iso,
        "trigger": trigger["trigger"],
        "detail": trigger.get("detail", ""),
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


def _emergency_deposit(state: dict, price: float, trigger: dict) -> bool:
    """Emergency fallback: deposit with extra-wide range."""
    log("EMERGENCY: deploying with wide range")
    # MAX_RANGE_PCT is in percentage points (10 = 10%), same as calc_optimal_range
    half_width = MAX_RANGE_PCT * EMERGENCY_RANGE_MULT  # e.g. 10 * 2.0 = 20%

    lower_price = price * (1 - half_width / 100)
    upper_price = price * (1 + half_width / 100)
    tick_lower = price_to_tick(lower_price)
    tick_upper = price_to_tick(upper_price)

    eth_bal, usdc_bal, bal_failed = get_balances()
    if bal_failed:
        log("  Emergency: balance query failed — cannot proceed")
        return False
    usdc_deposit = int(usdc_bal * 0.9)
    if usdc_deposit < MIN_TRADE_USD:
        log(f"  Emergency: USDC balance too low ({usdc_bal:.2f})")
        return False
    user_input = json.dumps(
        [
            {
                "chainIndex": CHAIN_ID,
                "coinAmount": str(usdc_deposit),
                "tokenAddress": USDC_ADDR,
            }
        ]
    )

    deposit_result = defi_deposit(user_input, tick_lower, tick_upper)
    if deposit_result:
        time.sleep(5)
        new_token_id = find_latest_token_id()
        if new_token_id:
            log(f"  Found token_id from position-detail: {new_token_id}")
        else:
            new_token_id = ""
            log("  Warning: emergency deposit OK but token_id not found")

        state["position"] = {
            "token_id": new_token_id,
            "tick_lower": tick_lower,
            "tick_upper": tick_upper,
            "lower_price": round(lower_price, 2),
            "upper_price": round(upper_price, 2),
            "created_at": datetime.now().isoformat(),
            "created_atr_pct": round(half_width, 2),  # already in percentage
        }
        log(
            f"  Emergency deposit OK: [{tick_lower},{tick_upper}] "
            f"(${lower_price:.2f}-${upper_price:.2f})"
        )
        return True

    log("  Emergency deposit also failed — funds sitting idle")
    return False


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


def emit(event_type: str, data: dict, notify: bool = False):
    """Emit structured JSON event to stdout (one JSON line per event).

    Strategy script is a headless engine. The hosting agent platform
    (ZeroClaw, OpenClaw, etc.) reads stdout and routes notifications.
    """
    payload = {
        "type": event_type,
        "ts": datetime.now(timezone.utc).isoformat(),
        "notify": notify,
        **data,
    }
    print(json.dumps(payload, ensure_ascii=False), flush=True)


# ── IL Estimation ───────────────────────────────────────────────────────────


def estimate_il(entry_price: float, current_price: float) -> float:
    """Estimate impermanent loss percentage for a CL position.
    Simplified: IL = 2*sqrt(r)/(1+r) - 1, where r = current/entry."""
    if entry_price <= 0 or current_price <= 0:
        return 0.0
    r = current_price / entry_price
    il = 2 * math.sqrt(r) / (1 + r) - 1
    return round(il * 100, 2)


# ── Core Logic: tick ────────────────────────────────────────────────────────


STOP_AUTO_RESUME = CFG.get("stop_auto_resume", True)
STOP_RESUME_COOLDOWN = CFG.get("stop_resume_cooldown_seconds", 3600)  # 1h default
STOP_RESUME_REBOUND_PCT = CFG.get("stop_resume_rebound_pct", 0.02)  # 2% default
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
    # Recover token_id if missing but position exists
    if position and not position.get("token_id") and position.get("tick_lower"):
        recovered_id = find_latest_token_id()
        if recovered_id:
            position["token_id"] = recovered_id
            log(f"Recovered token_id: {recovered_id}")
    if position and position.get("token_id"):
        pos_detail = get_position_detail(position["token_id"])
        lp_value = pos_detail["value"]
        unclaimed_fee = pos_detail["unclaimed_fee_usd"]
        if lp_value == 0.0 and position.get("tick_lower"):
            # Position exists in state but API returned 0 — treat as query failure
            balance_failed = True
            log("LP position query returned 0 value — treating as query failure")
    total_usd = wallet_usd + lp_value
    state["stats"]["unclaimed_fee_usd"] = round(unclaimed_fee, 4)

    # Track portfolio value history for smoothing (only when data is reliable)
    if not balance_failed:
        value_history = state.get("_value_history", [])
        value_history.append(round(total_usd, 2))
        if len(value_history) > 12:  # keep ~1h @ 5min ticks
            value_history = value_history[-12:]
        state["_value_history"] = value_history

    # Initial snapshot — only when both wallet and LP data are reliable
    if (
        state["stats"].get("initial_portfolio_usd") is None
        and total_usd > 0
        and not balance_failed
    ):
        state["stats"]["initial_portfolio_usd"] = round(total_usd, 2)
        state["stats"]["initial_eth_price"] = round(price, 2)
        log(f"Initial portfolio: ${total_usd:.2f} @ ETH ${price:.2f}")

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
            stop_time = _safe_isoparse(state.get("stop_triggered_at", ""))
            cooldown_met = (
                not stop_time
                or (datetime.now() - stop_time).total_seconds() > STOP_RESUME_COOLDOWN
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
            current_drawdown = (peak - smooth_usd) / peak if peak > 0 else 1.0
            # Resume if drawdown recovered below threshold with margin
            resume_threshold = (
                TRAILING_STOP_PCT * 0.7
            )  # must recover to 70% of stop level
            if cooldown_met and current_drawdown < resume_threshold:
                log(
                    f"AUTO-RESUME: drawdown {current_drawdown:.1%} < {resume_threshold:.1%} "
                    f"threshold, cooldown met"
                )
                state.pop("stop_triggered", None)
                state.pop("stop_notified", None)
                state.pop("stop_triggered_at", None)
                save_state(state)
                emit(
                    "stop_resumed",
                    {
                        "previous_trigger": trigger_msg,
                        "drawdown_pct": round(current_drawdown * 100, 2),
                        "price": round(price, 2),
                    },
                    notify=True,
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
            emit(
                "stop_triggered" if first_notify else "stopped",
                {
                    "trigger": trigger_msg,
                    "price": round(price, 2),
                    "portfolio_usd": round(total_usd, 2),
                    "auto_resume": STOP_AUTO_RESUME,
                },
                notify=first_notify,
            )
            return

    # IL estimation
    position = state.get("position")
    if position and position.get("created_at"):
        entry_price = state["stats"].get("initial_eth_price", price)
        il_pct = estimate_il(entry_price, price)
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
        # No position — initial deposit
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
            else:
                tick_status = "rebalance_failed"
                errors["consecutive"] = errors.get("consecutive", 0) + 1
                if errors["consecutive"] >= MAX_CONSECUTIVE_ERRORS:
                    errors["cooldown_until"] = (
                        datetime.now() + timedelta(seconds=COOLDOWN_AFTER_ERRORS)
                    ).isoformat()
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
    has_event = tick_status not in (
        "in_range",
        "no_action",
        "risk_rejected",
        "skip_small_change",
    )
    stats = state.get("stats", {})
    initial = stats.get("initial_portfolio_usd")
    deposits = stats.get("total_deposits_usd", 0)
    cost_basis = (initial or 0) + deposits
    tick_data = {
        "status": tick_status,
        "price": round(price, 2),
        "atr_pct": round(atr_pct, 2),
        "regime": classify_volatility(atr_pct),
        "trend": mtf.get("trend", "neutral"),
        "trend_strength": round(mtf.get("strength", 0), 2),
        "portfolio_usd": round(total_usd, 2),
        "pnl_usd": round(total_usd - cost_basis, 2) if initial else 0,
        "balances": {
            "eth": round(eth_bal, 6),
            "usdc": round(usdc_bal, 2),
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
        tick_data["trigger"] = trigger
    emit("tick", tick_data, notify=has_event)


# ── Sub-commands ────────────────────────────────────────────────────────────


def status():
    """Print current status."""
    state = load_state()
    price = get_eth_price()
    eth_bal, usdc_bal, bal_failed = get_balances()
    if bal_failed:
        print("> 余额查询失败，显示的余额可能不准确")
    wallet_usd = eth_bal * (price or 0) + usdc_bal
    position = state.get("position")
    lp_value = 0.0
    if position and position.get("token_id"):
        lp_value = get_position_value(position["token_id"])
    total_usd = wallet_usd + lp_value
    stats = state.get("stats", {})
    history = state.get("price_history", [])

    print("**CL LP Auto-Rebalancer v1 -- 状态**")
    print(f"> 价格: `${price:.2f}`" if price else "> 价格: 不可用")
    lp_str = f" + LP `${lp_value:.0f}`" if lp_value > 0 else ""
    print(
        f"> 余额: `{eth_bal:.6f}` ETH + `${usdc_bal:.2f}` USDC{lp_str} = **`${total_usd:.0f}`**"
    )

    if position and position.get("tick_lower"):
        lower_p = position.get("lower_price", tick_to_price(position["tick_lower"]))
        upper_p = position.get("upper_price", tick_to_price(position["tick_upper"]))
        in_range = lower_p <= (price or 0) <= upper_p
        status_str = "范围内" if in_range else "范围外"
        print(f"> 范围: `${lower_p:.2f}` - `${upper_p:.2f}` ({status_str})")
        print(
            f"> Tick: `{position['tick_lower']}` - `{position['tick_upper']}` "
            f"| token_id: `{position.get('token_id', 'N/A')}`"
        )
        if position.get("created_at"):
            created_dt = _safe_isoparse(position["created_at"])
            if created_dt:
                age_h = (datetime.now() - created_dt).total_seconds() / 3600
                print(f"> 头寸年龄: `{age_h:.1f}h`")
    else:
        print("> 头寸: 未建立")

    # K-line ATR
    kline_cache = state.get("kline_cache")
    if kline_cache:
        atr = kline_cache.get("atr_pct", 0)
        regime = classify_volatility(atr)
        print(f"\n> ATR(1H): `{atr:.2f}%` ({regime})")

    # MTF
    if price and len(history) >= MTF_SHORT_PERIOD:
        mtf = analyze_multi_timeframe(history, price)
        print(
            f"> 趋势: `{mtf['trend']}` ({mtf['strength']:.0%}) | 结构: `{mtf['structure']}`"
        )
        print(
            f"> 动量: 1h `{mtf['momentum_1h']:+.2f}%` | 4h `{mtf['momentum_4h']:+.2f}%`"
        )

    # PnL
    initial = stats.get("initial_portfolio_usd")
    deposits = stats.get("total_deposits_usd", 0)
    print("\n**统计**")
    if initial and price:
        cost_basis = initial + deposits
        total_pnl = round(total_usd - cost_basis, 2)
        pct = (total_pnl / cost_basis) * 100 if cost_basis else 0
        print(f"> 总收益: **`${total_pnl:+.2f}`** (`{pct:+.1f}%`)")

    tir = stats.get("time_in_range_pct", 0)
    rebalances = stats.get("total_rebalances", 0)
    il = stats.get("estimated_il_pct", 0)
    print(f"> 范围内时间: `{tir:.0f}%` | 调仓次数: `{rebalances}`")
    print(f"> 估计 IL: `{il:.2f}%`")

    stop = state.get("stop_triggered")
    if stop:
        print(f"\n> **交易已停止**: `{stop}`")
        print("> 使用 `resume-trading` 恢复")


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

    initial = stats.get("initial_portfolio_usd")
    deposits = stats.get("total_deposits_usd", 0)
    cost_basis = (initial or 0) + deposits
    total_pnl = round(total_usd - cost_basis, 2) if initial else 0
    pnl_pct = (total_pnl / cost_basis * 100) if cost_basis else 0
    tir = stats.get("time_in_range_pct", 0)
    total_rebal = stats.get("total_rebalances", 0)
    il = stats.get("estimated_il_pct", 0)

    today = datetime.now().date().isoformat()
    today_rebal = [r for r in rebalances if r["time"].startswith(today)]

    mtf = {}
    if price and len(history) >= MTF_SHORT_PERIOD:
        mtf = analyze_multi_timeframe(history, price)

    report_data = {
        "price": round(price, 2) if price else None,
        "atr_pct": round(atr, 2),
        "regime": regime,
        "balances": {"eth": round(eth_bal, 6), "usdc": round(usdc_bal, 2)},
        "portfolio_usd": round(total_usd, 2),
        "pnl_usd": total_pnl,
        "pnl_pct": round(pnl_pct, 2),
        "time_in_range_pct": round(tir, 1),
        "total_rebalances": total_rebal,
        "estimated_il_pct": round(il, 2),
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
    emit("report", report_data, notify=True)


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

    # Try to close existing position
    if position and position.get("token_id"):
        log("Resetting: closing existing position...")
        defi_claim_fees(position["token_id"])
        defi_redeem(position["token_id"])

    new_state = (
        load_state.__wrapped__()
        if hasattr(load_state, "__wrapped__")
        else {
            "version": 1,
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

    defi_claim_fees(token_id)
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

    # IL
    initial_price = stats.get("initial_eth_price", price)
    il_pct = estimate_il(initial_price, price)

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
            "total_pnl": round(
                total_usd
                - (
                    (stats.get("initial_portfolio_usd") or 0)
                    + stats.get("total_deposits_usd", 0)
                ),
                2,
            ),
        },
        "rebalance_history": rebalances[-10:],
    }

    print(json.dumps(analysis, indent=2))


def deposit():
    """Manually record deposit/withdrawal."""
    if len(sys.argv) < 3:
        print("用法: cl_lp_v1.py deposit <金额USD>")
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
