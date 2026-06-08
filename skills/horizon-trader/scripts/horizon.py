#!/usr/bin/env python3
"""OpenClaw CLI entry point for Horizon SDK.

Usage: python3 horizon.py <command> [args...]

All output is JSON printed to stdout.
"""

from __future__ import annotations

import json
import os
import re
import sys

# Remove this script's directory from sys.path to prevent self-shadowing
# (this file is named horizon.py, which would shadow the horizon package).
_script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path = [p for p in sys.path if os.path.abspath(p) != _script_dir]


# ---------------------------------------------------------------------------
# Input validation helpers
# ---------------------------------------------------------------------------

# Identifiers: market IDs, order IDs, feed names, slugs, tickers.
# Allow alphanumeric, hyphens, underscores, dots, colons. Max 256 chars.
_ID_RE = re.compile(r"^[A-Za-z0-9._:/-]{1,256}$")

# Hex addresses (Ethereum-style): 0x followed by hex digits. Max 66 chars
# (covers condition IDs which can be longer than 42).
_HEX_RE = re.compile(r"^0x[0-9a-fA-F]{1,64}$")

# Allowed exchanges (whitelist).
_VALID_EXCHANGES = {"polymarket", "kalshi", "paper"}

# Allowed side values (whitelist).
_VALID_SIDES = {"yes", "no"}

# Allowed order side values (whitelist).
_VALID_ORDER_SIDES = {"buy", "sell"}

# Allowed sort-by values for wallet-positions.
_VALID_SORT_BY = {"TOKENS", "CURRENT", "INITIAL", "CASHPNL", "PERCENTPNL", "PRICE", "AVGPRICE"}

# Feed types that accept URLs in config_json (require SSRF validation).
_URL_FEED_TYPES = {"chainlink": "rpc_url", "rest_json_path": "url", "rest": "url"}

# All allowed feed types.
_VALID_FEED_TYPES = {
    "binance_ws", "polymarket_book", "kalshi_book", "predictit",
    "manifold", "espn", "nws", "chainlink", "rest_json_path", "rest",
}

# Blocked hostnames / IP patterns for SSRF prevention.
_BLOCKED_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0", "[::1]", "metadata.google.internal"}


def _is_private_ip(hostname: str) -> bool:
    """Check if hostname looks like a private/internal IP address."""
    parts = hostname.split(".")
    if len(parts) != 4:
        return False
    try:
        octets = [int(p) for p in parts]
    except ValueError:
        return False
    if octets[0] == 10:
        return True
    if octets[0] == 172 and 16 <= octets[1] <= 31:
        return True
    if octets[0] == 192 and octets[1] == 168:
        return True
    if octets[0] == 169 and octets[1] == 254:
        return True
    return False


def _validate_public_url(url_str: str, label: str) -> str:
    """Validate that a URL is HTTPS and targets a public host (not internal/private)."""
    from urllib.parse import urlparse
    parsed = urlparse(url_str)
    if parsed.scheme not in ("https",):
        _print({"error": f"{label} must use HTTPS"})
        sys.exit(1)
    hostname = (parsed.hostname or "").lower()
    if not hostname:
        _print({"error": f"{label} has no hostname"})
        sys.exit(1)
    if hostname in _BLOCKED_HOSTS or _is_private_ip(hostname):
        _print({"error": f"{label} cannot target private/internal addresses"})
        sys.exit(1)
    return url_str


def _validate_id(value: str, label: str) -> str:
    """Validate an identifier string (market ID, order ID, feed name, etc.)."""
    if not _ID_RE.match(value):
        _print({"error": f"invalid {label}: must be 1-256 alphanumeric/dash/underscore/dot/colon characters"})
        sys.exit(1)
    return value


def _validate_hex_or_id(value: str, label: str) -> str:
    """Validate a value that can be either a hex address or an identifier."""
    if value.startswith("0x") or value.startswith("0X"):
        if not _HEX_RE.match(value):
            _print({"error": f"invalid {label}: malformed hex address"})
            sys.exit(1)
    elif not _ID_RE.match(value):
        _print({"error": f"invalid {label}: must be alphanumeric or hex address"})
        sys.exit(1)
    return value


def _validate_exchange(value: str) -> str:
    """Validate exchange name against whitelist."""
    if value.lower() not in _VALID_EXCHANGES:
        _print({"error": f"invalid exchange: {value!r}. Must be one of: {', '.join(sorted(_VALID_EXCHANGES))}"})
        sys.exit(1)
    return value.lower()


def _validate_side(value: str) -> str:
    """Validate side (yes/no) against whitelist."""
    if value.lower() not in _VALID_SIDES:
        _print({"error": f"invalid side: {value!r}. Must be 'yes' or 'no'"})
        sys.exit(1)
    return value.lower()


def _validate_order_side(value: str) -> str:
    """Validate order side (buy/sell) against whitelist."""
    if value.lower() not in _VALID_ORDER_SIDES:
        _print({"error": f"invalid order_side: {value!r}. Must be 'buy' or 'sell'"})
        sys.exit(1)
    return value.lower()


def _validate_sort_by(value: str) -> str:
    """Validate sort_by against allowed values."""
    if value.upper() not in _VALID_SORT_BY:
        _print({"error": f"invalid sort_by: {value!r}. Must be one of: {', '.join(sorted(_VALID_SORT_BY))}"})
        sys.exit(1)
    return value.upper()


def _safe_int(value: str, label: str) -> int:
    """Parse a string to int with error handling."""
    try:
        return int(value)
    except ValueError:
        _print({"error": f"invalid {label}: {value!r} is not an integer"})
        sys.exit(1)


def _safe_float(value: str, label: str) -> float:
    """Parse a string to float with error handling."""
    try:
        result = float(value)
    except ValueError:
        _print({"error": f"invalid {label}: {value!r} is not a number"})
        sys.exit(1)
    if result != result:  # NaN check
        _print({"error": f"invalid {label}: NaN is not allowed"})
        sys.exit(1)
    return result


def _safe_float_list(value: str, label: str) -> list[float]:
    """Parse a comma-separated string to list of floats."""
    try:
        return [float(x) for x in value.split(",")]
    except ValueError:
        _print({"error": f"invalid {label}: must be comma-separated numbers"})
        sys.exit(1)


def _validate_text(value: str, label: str, max_len: int = 500) -> str:
    """Validate free-text input: length-cap only (no shell metacharacters needed
    since this never touches a shell)."""
    if len(value) > max_len:
        _print({"error": f"{label} too long (max {max_len} chars)"})
        sys.exit(1)
    return value


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def _print(data: object) -> None:
    print(json.dumps(data, indent=2))


# ---------------------------------------------------------------------------
# Main dispatch
# ---------------------------------------------------------------------------

def main() -> None:
    args = sys.argv[1:]
    if not args:
        _print({"error": "no command. try: status, positions, orders, fills, quote, cancel, cancel-all, cancel-market, discover, market-detail, discover-events, top-markets, kelly, kill-switch, stop-loss, take-profit, feed, feeds, feed-health, feed-metrics, parity, contingent, wallet-trades, market-trades, wallet-positions, wallet-value, wallet-profile, top-holders, market-flow, simulate, arb, entropy, kl-divergence, hurst, variance-ratio, cf-var, greeks, deflated-sharpe, signal-diagnostics, market-efficiency, stress-test, start-feed, tearsheet, bayesian-opt, portfolio, portfolio-weights, update-params, get-params, hawkes, correlation"})
        sys.exit(1)

    cmd = args[0]

    from horizon import tools

    if cmd == "status":
        _print(tools.engine_status())

    elif cmd == "positions":
        _print(tools.list_positions())

    elif cmd == "orders":
        market_id = _validate_id(args[1], "market_id") if len(args) > 1 else None
        _print(tools.list_open_orders(market_id))

    elif cmd == "fills":
        limit = _safe_int(args[1], "limit") if len(args) > 1 else 20
        _print(tools.list_recent_fills(limit))

    elif cmd == "quote":
        if len(args) < 5:
            _print({"error": "usage: quote <market_id> <side> <price> <size> [market_side]"})
            sys.exit(1)
        market_id = _validate_id(args[1], "market_id")
        side = _validate_order_side(args[2])
        price = _safe_float(args[3], "price")
        size = _safe_float(args[4], "size")
        market_side = _validate_side(args[5]) if len(args) > 5 else "yes"
        _print(tools.submit_order(market_id, side, price, size, market_side))

    elif cmd == "cancel":
        if len(args) < 2:
            _print({"error": "usage: cancel <order_id>"})
            sys.exit(1)
        _print(tools.cancel_order(_validate_id(args[1], "order_id")))

    elif cmd == "cancel-all":
        _print(tools.cancel_all_orders())

    elif cmd == "cancel-market":
        if len(args) < 2:
            _print({"error": "usage: cancel-market <market_id>"})
            sys.exit(1)
        _print(tools.cancel_market_orders(_validate_id(args[1], "market_id")))

    elif cmd == "discover":
        exchange = _validate_exchange(args[1]) if len(args) > 1 else "polymarket"
        query = _validate_text(args[2], "query") if len(args) > 2 else ""
        limit = _safe_int(args[3], "limit") if len(args) > 3 else 10
        market_type = "all"
        if len(args) > 4:
            mt = args[4].lower()
            if mt not in ("all", "binary", "multi"):
                _print({"error": f"invalid market_type: {mt!r}. Must be 'all', 'binary', or 'multi'"})
                sys.exit(1)
            market_type = mt
        category = _validate_text(args[5], "category", 100) if len(args) > 5 else ""
        _print(tools.discover(exchange, query, limit, market_type, category))

    elif cmd == "market-detail":
        if len(args) < 2:
            _print({"error": "usage: market-detail <slug_or_id> [exchange]"})
            sys.exit(1)
        slug_or_id = _validate_id(args[1], "slug_or_id")
        exchange = _validate_exchange(args[2]) if len(args) > 2 else "polymarket"
        _print(tools.market_detail(slug_or_id, exchange))

    elif cmd == "kelly":
        if len(args) < 4:
            _print({"error": "usage: kelly <prob> <price> <bankroll> [fraction] [max_size]"})
            sys.exit(1)
        prob = _safe_float(args[1], "prob")
        price = _safe_float(args[2], "price")
        bankroll = _safe_float(args[3], "bankroll")
        fraction = _safe_float(args[4], "fraction") if len(args) > 4 else 0.25
        max_size = _safe_float(args[5], "max_size") if len(args) > 5 else 100.0
        _print(tools.kelly_sizing(prob, price, bankroll, fraction, max_size))

    elif cmd == "kill-switch":
        if len(args) < 2:
            _print({"error": "usage: kill-switch <on|off> [reason]"})
            sys.exit(1)
        if args[1] == "on":
            reason = _validate_text(args[2], "reason", 200) if len(args) > 2 else "manual"
            _print(tools.activate_kill_switch(reason))
        elif args[1] == "off":
            _print(tools.deactivate_kill_switch())
        else:
            _print({"error": "usage: kill-switch <on|off> [reason]"})
            sys.exit(1)

    elif cmd == "stop-loss":
        if len(args) < 6:
            _print({"error": "usage: stop-loss <market_id> <side> <order_side> <size> <trigger_price>"})
            sys.exit(1)
        _print(tools.add_stop_loss(
            _validate_id(args[1], "market_id"),
            _validate_side(args[2]),
            _validate_order_side(args[3]),
            _safe_float(args[4], "size"),
            _safe_float(args[5], "trigger_price"),
        ))

    elif cmd == "take-profit":
        if len(args) < 6:
            _print({"error": "usage: take-profit <market_id> <side> <order_side> <size> <trigger_price>"})
            sys.exit(1)
        _print(tools.add_take_profit(
            _validate_id(args[1], "market_id"),
            _validate_side(args[2]),
            _validate_order_side(args[3]),
            _safe_float(args[4], "size"),
            _safe_float(args[5], "trigger_price"),
        ))

    elif cmd == "feed":
        if len(args) < 2:
            _print({"error": "usage: feed <name>"})
            sys.exit(1)
        _print(tools.get_feed_snapshot(_validate_id(args[1], "feed_name")))

    elif cmd == "feeds":
        _print(tools.list_all_feeds())

    elif cmd == "parity":
        if len(args) < 2:
            _print({"error": "usage: parity <market_id> [feed_name]"})
            sys.exit(1)
        market_id = _validate_id(args[1], "market_id")
        feed_name = _validate_id(args[2], "feed_name") if len(args) > 2 else None
        _print(tools.check_parity(market_id, feed_name))

    elif cmd == "contingent":
        _print(tools.list_contingent_orders())

    # --- Feed health ---

    elif cmd == "feed-metrics":
        if len(args) < 2:
            _print(tools.all_feed_metrics())
        else:
            _print(tools.feed_metrics(_validate_id(args[1], "feed_name")))

    elif cmd == "feed-health":
        threshold = _safe_float(args[1], "threshold") if len(args) > 1 else 30.0
        _print(tools.check_feed_health(threshold))

    # --- Discovery ---

    elif cmd == "discover-events":
        query = _validate_text(args[1], "query") if len(args) > 1 else ""
        limit = _safe_int(args[2], "limit") if len(args) > 2 else 10
        _print(tools.discover_event(query, limit))

    elif cmd == "top-markets":
        exchange = _validate_exchange(args[1]) if len(args) > 1 else "polymarket"
        limit = _safe_int(args[2], "limit") if len(args) > 2 else 10
        category = _validate_text(args[3], "category", 100) if len(args) > 3 else ""
        _print(tools.get_top_markets(exchange, limit, category))

    # --- Wallet analytics (Polymarket, no auth) ---

    elif cmd == "wallet-trades":
        if len(args) < 2:
            _print({"error": "usage: wallet-trades <address> [limit] [condition_id]"})
            sys.exit(1)
        address = _validate_hex_or_id(args[1], "address")
        limit = _safe_int(args[2], "limit") if len(args) > 2 else 50
        cid = _validate_hex_or_id(args[3], "condition_id") if len(args) > 3 else None
        _print(tools.wallet_trades(address, limit, cid))

    elif cmd == "market-trades":
        if len(args) < 2:
            _print({"error": "usage: market-trades <condition_id> [limit] [side] [min_size]"})
            sys.exit(1)
        cid = _validate_hex_or_id(args[1], "condition_id")
        limit = _safe_int(args[2], "limit") if len(args) > 2 else 50
        side = _validate_order_side(args[3]) if len(args) > 3 else None
        min_size = _safe_float(args[4], "min_size") if len(args) > 4 else 0.0
        _print(tools.market_trades(cid, limit, side, min_size))

    elif cmd == "wallet-positions":
        if len(args) < 2:
            _print({"error": "usage: wallet-positions <address> [limit] [sort_by]"})
            sys.exit(1)
        address = _validate_hex_or_id(args[1], "address")
        limit = _safe_int(args[2], "limit") if len(args) > 2 else 50
        sort_by = _validate_sort_by(args[3]) if len(args) > 3 else "CURRENT"
        _print(tools.wallet_positions(address, limit, sort_by))

    elif cmd == "wallet-value":
        if len(args) < 2:
            _print({"error": "usage: wallet-value <address>"})
            sys.exit(1)
        _print(tools.wallet_value(_validate_hex_or_id(args[1], "address")))

    elif cmd == "wallet-profile":
        if len(args) < 2:
            _print({"error": "usage: wallet-profile <address>"})
            sys.exit(1)
        _print(tools.wallet_profile(_validate_hex_or_id(args[1], "address")))

    elif cmd == "top-holders":
        if len(args) < 2:
            _print({"error": "usage: top-holders <condition_id> [limit]"})
            sys.exit(1)
        cid = _validate_hex_or_id(args[1], "condition_id")
        limit = _safe_int(args[2], "limit") if len(args) > 2 else 20
        _print(tools.market_top_holders(cid, limit))

    elif cmd == "market-flow":
        if len(args) < 2:
            _print({"error": "usage: market-flow <condition_id> [trade_limit] [top_n]"})
            sys.exit(1)
        cid = _validate_hex_or_id(args[1], "condition_id")
        trade_limit = _safe_int(args[2], "trade_limit") if len(args) > 2 else 500
        top_n = _safe_int(args[3], "top_n") if len(args) > 3 else 10
        _print(tools.market_flow(cid, trade_limit, top_n))

    # --- Start feed ---

    elif cmd == "start-feed":
        if len(args) < 3:
            _print({"error": "usage: start-feed <name> <feed_type> [config_json]"})
            sys.exit(1)
        name = _validate_id(args[1], "feed_name")
        feed_type = _validate_id(args[2], "feed_type")
        if feed_type not in _VALID_FEED_TYPES:
            _print({"error": f"unknown feed type {feed_type!r}. Allowed: {', '.join(sorted(_VALID_FEED_TYPES))}"})
            sys.exit(1)
        config_json = args[3] if len(args) > 3 else None
        # Validate config_json is valid JSON if provided
        if config_json is not None:
            try:
                cfg = json.loads(config_json)
            except json.JSONDecodeError:
                _print({"error": "config_json must be valid JSON"})
                sys.exit(1)
            # SSRF prevention: validate URLs in feed types that accept them
            if feed_type in _URL_FEED_TYPES:
                url_key = _URL_FEED_TYPES[feed_type]
                if url_key in cfg:
                    _validate_public_url(cfg[url_key], url_key)
        _print(tools.start_feed(name, feed_type, config_json=config_json))

    # --- Simulation ---

    elif cmd == "simulate":
        scenarios = _safe_int(args[1], "scenarios") if len(args) > 1 else 10000
        seed = _safe_int(args[2], "seed") if len(args) > 2 else None
        _print(tools.simulate_portfolio(scenarios, seed))

    # --- Arbitrage ---

    elif cmd == "arb":
        if len(args) < 7:
            _print({"error": "usage: arb <market_id> <buy_exchange> <sell_exchange> <buy_price> <sell_price> <size>"})
            sys.exit(1)
        _print(tools.execute_arb(
            _validate_id(args[1], "market_id"),
            _validate_exchange(args[2]),
            _validate_exchange(args[3]),
            _safe_float(args[4], "buy_price"),
            _safe_float(args[5], "sell_price"),
            _safe_float(args[6], "size"),
        ))

    # --- Quantitative Analytics ---

    elif cmd == "entropy":
        if len(args) < 2:
            _print({"error": "usage: entropy <probability>"})
            sys.exit(1)
        _print(tools.compute_shannon_entropy(_safe_float(args[1], "probability")))

    elif cmd == "kl-divergence":
        if len(args) < 3:
            _print({"error": "usage: kl-divergence <p_values> <q_values> (comma-separated)"})
            sys.exit(1)
        p = _safe_float_list(args[1], "p_values")
        q = _safe_float_list(args[2], "q_values")
        _print(tools.compute_kl_divergence(p, q))

    elif cmd == "hurst":
        if len(args) < 2:
            _print({"error": "usage: hurst <prices> (comma-separated)"})
            sys.exit(1)
        _print(tools.compute_hurst_exponent(_safe_float_list(args[1], "prices")))

    elif cmd == "variance-ratio":
        if len(args) < 2:
            _print({"error": "usage: variance-ratio <returns> (comma-separated) [period]"})
            sys.exit(1)
        returns = _safe_float_list(args[1], "returns")
        period = _safe_int(args[2], "period") if len(args) > 2 else 2
        _print(tools.compute_variance_ratio(returns, period))

    elif cmd == "cf-var":
        if len(args) < 2:
            _print({"error": "usage: cf-var <returns> (comma-separated) [confidence]"})
            sys.exit(1)
        returns = _safe_float_list(args[1], "returns")
        confidence = _safe_float(args[2], "confidence") if len(args) > 2 else 0.95
        _print(tools.compute_cornish_fisher_var(returns, confidence))

    elif cmd == "greeks":
        if len(args) < 3:
            _print({"error": "usage: greeks <price> <size> [is_yes] [t_hours] [vol]"})
            sys.exit(1)
        price = _safe_float(args[1], "price")
        size = _safe_float(args[2], "size")
        is_yes = args[3].lower() in ("true", "yes", "1") if len(args) > 3 else True
        t_hours = _safe_float(args[4], "t_hours") if len(args) > 4 else 24.0
        vol = _safe_float(args[5], "vol") if len(args) > 5 else 0.2
        _print(tools.compute_prediction_greeks(price, size, is_yes, t_hours, vol))

    elif cmd == "deflated-sharpe":
        if len(args) < 4:
            _print({"error": "usage: deflated-sharpe <sharpe> <n_obs> <n_trials> [skew] [kurt]"})
            sys.exit(1)
        sharpe = _safe_float(args[1], "sharpe")
        n_obs = _safe_int(args[2], "n_obs")
        n_trials = _safe_int(args[3], "n_trials")
        skew = _safe_float(args[4], "skew") if len(args) > 4 else 0.0
        kurt = _safe_float(args[5], "kurt") if len(args) > 5 else 3.0
        _print(tools.compute_deflated_sharpe(sharpe, n_obs, n_trials, skew, kurt))

    elif cmd == "signal-diagnostics":
        if len(args) < 3:
            _print({"error": "usage: signal-diagnostics <predictions> <outcomes> (comma-separated)"})
            sys.exit(1)
        predictions = _safe_float_list(args[1], "predictions")
        outcomes = _safe_float_list(args[2], "outcomes")
        _print(tools.run_signal_diagnostics(predictions, outcomes))

    elif cmd == "market-efficiency":
        if len(args) < 2:
            _print({"error": "usage: market-efficiency <prices> (comma-separated)"})
            sys.exit(1)
        _print(tools.run_market_efficiency(_safe_float_list(args[1], "prices")))

    elif cmd == "stress-test":
        scenarios = _safe_int(args[1], "scenarios") if len(args) > 1 else 10000
        seed = _safe_int(args[2], "seed") if len(args) > 2 else None
        _print(tools.run_stress_test(scenarios, seed))

    # --- Tearsheet ---

    # tearsheet <equity_csv> - Generate tearsheet from equity curve CSV (one value per line)
    elif cmd == "tearsheet":
        path = args[1] if len(args) > 1 else None
        if not path:
            _print({"error": "usage: tearsheet <equity_csv_path>"})
        else:
            import csv
            with open(path) as f:
                reader = csv.reader(f)
                equity = [float(row[0]) for row in reader if row]
            from horizon.analytics import generate_tearsheet
            ts = generate_tearsheet(equity_curve=equity)
            result = {
                "sharpe_ratio": ts.sharpe_ratio,
                "sortino_ratio": ts.sortino_ratio,
                "max_drawdown": ts.max_drawdown,
                "calmar_ratio": ts.calmar_ratio,
                "win_rate": ts.win_rate,
                "profit_factor": ts.profit_factor,
                "total_trades": ts.total_trades,
                "tail_ratio": ts.tail_ratio,
                "monthly_returns": ts.monthly_returns,
                "top_drawdowns_count": len(ts.top_drawdowns) if ts.top_drawdowns else 0,
            }
            _print(result)

    # --- Bayesian Optimization ---

    # bayesian-opt <param_space_json> [n_iterations] [n_initial] - Run Bayesian optimization
    # param_space_json: '{"spread": [0.01, 0.10], "gamma": [0.1, 1.0]}'
    elif cmd == "bayesian-opt":
        import json as j2
        space_json = args[1] if len(args) > 1 else None
        if not space_json:
            _print({"error": "usage: bayesian-opt '<param_space_json>' [n_iterations] [n_initial]"})
        else:
            param_space = j2.loads(space_json)
            n_iter = int(args[2]) if len(args) > 2 else 20
            n_init = int(args[3]) if len(args) > 3 else 5
            from horizon.bayesian_opt import bayesian_optimize
            def objective(**params):
                total = 0.0
                for name, val in params.items():
                    bounds = param_space.get(name, [0, 1])
                    mid = (bounds[0] + bounds[1]) / 2
                    total -= (val - mid) ** 2
                return total
            result = bayesian_optimize(objective=objective, param_space=param_space, n_iterations=n_iter, n_initial=n_init)
            _print({
                "best_params": {k: round(v, 6) for k, v in result.best_params.items()},
                "best_value": round(result.best_value, 6),
                "n_iterations": result.n_iterations,
            })

    # --- Portfolio ---

    # portfolio - Get portfolio metrics from current engine positions
    elif cmd == "portfolio":
        engine = tools.get_engine()
        from horizon.portfolio import Portfolio
        portfolio = Portfolio.from_engine(engine)
        m = portfolio.metrics()
        _print({
            "total_value": round(m.total_value, 2),
            "total_pnl": round(m.total_pnl, 2),
            "total_pnl_pct": round(m.total_pnl_pct, 4),
            "num_positions": m.num_positions,
            "long_exposure": round(m.long_exposure, 2),
            "short_exposure": round(m.short_exposure, 2),
            "net_exposure": round(m.net_exposure, 2),
            "gross_exposure": round(m.gross_exposure, 2),
            "herfindahl_index": round(m.herfindahl_index, 4),
            "max_concentration": round(m.max_concentration, 4),
        })

    # portfolio-weights [method] - Compute optimal weights (equal|kelly|risk_parity|min_variance)
    elif cmd == "portfolio-weights":
        method = args[1] if len(args) > 1 else "equal"
        engine = tools.get_engine()
        from horizon.portfolio import Portfolio
        portfolio = Portfolio.from_engine(engine)
        if method == "kelly":
            weights = portfolio.optimize_kelly()
        elif method == "risk_parity":
            weights = portfolio.optimize_risk_parity()
        elif method == "min_variance":
            weights = portfolio.optimize_min_variance()
        else:
            weights = portfolio.optimize_equal_weight()
        _print({"method": method, "weights": {k: round(v, 6) for k, v in weights.items()}})

    # --- Runtime Parameters ---

    # update-params <json> - Hot-reload runtime parameters
    elif cmd == "update-params":
        import json as j2
        params_json = args[1] if len(args) > 1 else None
        if not params_json:
            _print({"error": "usage: update-params '<json>'"})
        else:
            engine = tools.get_engine()
            params = j2.loads(params_json)
            engine.update_params_batch(params)
            _print({"updated": list(params.keys()), "count": len(params)})

    # get-params - Get all runtime parameters
    elif cmd == "get-params":
        engine = tools.get_engine()
        params = engine.get_all_params()
        _print({"params": {k: round(v, 6) for k, v in params.items()}, "count": len(params)})

    # --- Hawkes Process ---

    # hawkes <event_times_csv> [mu] [alpha] [beta] - Compute Hawkes process intensity
    elif cmd == "hawkes":
        times_str = args[1] if len(args) > 1 else None
        if not times_str:
            _print({"error": "usage: hawkes <event_times_csv> [mu] [alpha] [beta]"})
        else:
            event_times = [float(x) for x in times_str.split(",")]
            mu = float(args[2]) if len(args) > 2 else 0.1
            alpha = float(args[3]) if len(args) > 3 else 0.5
            beta = float(args[4]) if len(args) > 4 else 1.0
            from horizon._horizon import HawkesProcess
            hp = HawkesProcess(mu=mu, alpha=alpha, beta=beta)
            for t in event_times:
                hp.add_event(t)
            now = event_times[-1] + 1e-6 if event_times else 0.0
            _print({
                "intensity": round(hp.intensity(now), 6),
                "branching_ratio": round(hp.branching_ratio(), 6),
                "expected_events_1m": round(hp.expected_events(now, 60.0), 4),
                "event_count": hp.event_count(),
            })

    # --- Correlation / Covariance ---

    # correlation <returns_json> - Compute Ledoit-Wolf shrinkage covariance matrix
    # returns_json: '[[0.01, 0.02], [-0.01, 0.03], ...]' (rows=observations, cols=assets)
    elif cmd == "correlation":
        import json as j2
        returns_json = args[1] if len(args) > 1 else None
        if not returns_json:
            _print({"error": "usage: correlation '<returns_json>'"})
        else:
            returns = j2.loads(returns_json)
            from horizon._horizon import ledoit_wolf_shrinkage
            matrix, shrinkage = ledoit_wolf_shrinkage(returns)
            _print({
                "matrix": [[round(v, 8) for v in row] for row in matrix],
                "shrinkage_intensity": round(shrinkage, 6),
                "n_assets": len(matrix),
                "n_observations": len(returns),
            })

    else:
        _print({"error": f"unknown command: {args[0][:64]}"})
        sys.exit(1)


if __name__ == "__main__":
    main()
