"""Kelly Criterion position sizing for prediction market trades.

Implements fractional Kelly to determine optimal position size given:
- Edge (estimated_prob - market_price)
- Confidence from estimator
- Current bankroll (cash available)
- Portfolio exposure limits

Binary outcome assumption: Kalshi markets resolve YES (1) or NO (0).
Uses fractional Kelly (α = 0.25 default) for noise robustness.

Usage:
    python kelly_size.py [options]
"""

import json
import math
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# ── Configuration ──────────────────────────────────────────────────────────

DEFAULT_ALPHA = 0.25
MIN_EDGE_FOR_SIZING = 0.03
MAX_CONTRACTS_PER_TRADE = 100
MAX_COST_PER_TRADE_USD = 25.00
MIN_CONTRACTS = 1
CONFIDENCE_EXPONENT = 2.0


def _load_kelly_config():
    """Load Kelly parameters — premium from config file, else use built-in defaults."""
    global DEFAULT_ALPHA, CONFIDENCE_EXPONENT, MIN_EDGE_FOR_SIZING
    global MAX_CONTRACTS_PER_TRADE, MAX_COST_PER_TRADE_USD

    for candidate in [
        Path.home() / "kelly_config.json",
        Path.home() / "prompt-lab" / "kelly_config.json",
    ]:
        if candidate.exists():
            try:
                with open(candidate) as f:
                    cfg = json.load(f)
                DEFAULT_ALPHA = cfg.get("alpha", cfg.get("kelly_fraction", DEFAULT_ALPHA))
                CONFIDENCE_EXPONENT = cfg.get("confidence_exponent", cfg.get("conf_exp", CONFIDENCE_EXPONENT))
                MIN_EDGE_FOR_SIZING = cfg.get("min_edge_for_sizing", cfg.get("min_edge", MIN_EDGE_FOR_SIZING))
                MAX_CONTRACTS_PER_TRADE = cfg.get("max_contracts_per_trade", MAX_CONTRACTS_PER_TRADE)
                MAX_COST_PER_TRADE_USD = cfg.get("max_cost_per_trade_usd", MAX_COST_PER_TRADE_USD)
                logger.info("Loaded Kelly config from %s: alpha=%.2f, conf_exp=%.1f, min_edge=%.3f",
                           candidate, DEFAULT_ALPHA, CONFIDENCE_EXPONENT, MIN_EDGE_FOR_SIZING)
                return
            except Exception as e:
                logger.warning("Failed to load Kelly config from %s: %s", candidate, e)


_load_kelly_config()


@dataclass
class KellyResult:
    """Output of Kelly position sizing."""
    contracts: int
    cost_usd: float
    kelly_fraction: float
    fractional_kelly: float
    edge_pct: float
    reason: str
    capped: bool
    bankroll_fraction: float


def kelly_size(
    estimated_prob: float,
    market_price_cents: int,
    confidence: float,
    bankroll_usd: float,
    side: str = "yes",
    alpha: float = DEFAULT_ALPHA,
    max_cost_usd: float = MAX_COST_PER_TRADE_USD,
    max_contracts: int = MAX_CONTRACTS_PER_TRADE,
    current_exposure_usd: float = 0.0,
    max_portfolio_exposure_usd: float = 100.0,
) -> KellyResult:
    """Calculate optimal position size using fractional Kelly Criterion.

    For binary prediction markets:
        Kelly fraction f* = (p * b - q) / b
        where:
            p = estimated true probability of winning
            q = 1 - p (probability of losing)
            b = decimal odds - 1 = (payout / cost) - 1

    For a YES contract at price c (cents):
        If YES wins: receive 100¢, profit = (100 - c)¢
        If YES loses: lose c¢
        b = (100 - c) / c

    Args:
        estimated_prob: Model's estimated probability of YES (0.01-0.99)
        market_price_cents: Current market price in cents (1-99)
        confidence: Estimator confidence (0.0-1.0)
        bankroll_usd: Available cash for trading
        side: "yes" or "no"
        alpha: Fractional Kelly multiplier (default 0.25)
        max_cost_usd: Hard cap on trade cost
        max_contracts: Hard cap on contract count
        current_exposure_usd: Current portfolio exposure
        max_portfolio_exposure_usd: Maximum total portfolio exposure

    Returns:
        KellyResult with recommended contracts and metadata
    """
    side = side.lower().strip()

    # Determine effective probability and cost based on side
    if side == "yes":
        p = estimated_prob
        cost_cents = market_price_cents
        profit_cents = 100 - market_price_cents
    else:
        p = 1 - estimated_prob
        cost_cents = 100 - market_price_cents
        profit_cents = market_price_cents

    q = 1 - p
    edge_pct = abs(estimated_prob - market_price_cents / 100.0) * 100

    # Sanity checks
    if cost_cents <= 0 or cost_cents >= 100:
        return KellyResult(0, 0, 0, 0, edge_pct, "Invalid price", False, 0)

    if bankroll_usd <= 0:
        return KellyResult(0, 0, 0, 0, edge_pct, "No bankroll", False, 0)

    if edge_pct < MIN_EDGE_FOR_SIZING * 100:
        return KellyResult(
            0, 0, 0, 0, edge_pct,
            f"Edge {edge_pct:.1f}% below {MIN_EDGE_FOR_SIZING*100:.0f}% minimum",
            False, 0,
        )

    if confidence < 0.2:
        return KellyResult(0, 0, 0, 0, edge_pct, "Confidence too low", False, 0)

    # Decimal odds for the bet
    b = profit_cents / cost_cents

    # Raw Kelly fraction
    kelly_f = (p * b - q) / b

    # Kelly says don't bet
    if kelly_f <= 0:
        return KellyResult(
            0, 0, round(kelly_f, 4), 0, edge_pct,
            f"Negative Kelly ({kelly_f:.3f}) — odds don't justify bet",
            False, 0,
        )

    # Apply fractional Kelly with confidence discount
    confidence_discount = confidence ** CONFIDENCE_EXPONENT
    fractional_f = kelly_f * alpha * confidence_discount

    # Convert to dollar amount
    bet_usd = fractional_f * bankroll_usd
    cost_per_contract = cost_cents / 100.0
    raw_contracts = bet_usd / cost_per_contract

    # Apply caps
    capped = False
    contracts = int(math.floor(raw_contracts))
    cap_reason = ""

    # Cap 1: Max contracts per trade
    if contracts > max_contracts:
        contracts = max_contracts
        capped = True
        cap_reason = f"capped at {max_contracts} max contracts"

    # Cap 2: Max cost per trade
    trade_cost = contracts * cost_per_contract
    if trade_cost > max_cost_usd:
        contracts = int(math.floor(max_cost_usd / cost_per_contract))
        capped = True
        cap_reason = f"capped at ${max_cost_usd:.0f} max cost"

    # Cap 3: Portfolio exposure limit
    remaining_exposure = max_portfolio_exposure_usd - current_exposure_usd
    if remaining_exposure <= 0:
        return KellyResult(
            0, 0, round(kelly_f, 4), round(fractional_f, 4), edge_pct,
            f"Portfolio at limit (${current_exposure_usd:.0f}/${max_portfolio_exposure_usd:.0f})",
            True, 0,
        )

    trade_cost = contracts * cost_per_contract
    if trade_cost > remaining_exposure:
        contracts = int(math.floor(remaining_exposure / cost_per_contract))
        capped = True
        cap_reason = f"capped by exposure (${remaining_exposure:.0f} remaining)"

    # Floor
    if contracts < MIN_CONTRACTS:
        if edge_pct >= MIN_EDGE_FOR_SIZING * 100 and kelly_f > 0:
            contracts = MIN_CONTRACTS
        else:
            return KellyResult(0, 0, round(kelly_f, 4), round(fractional_f, 4), edge_pct,
                               "Kelly too small for 1 contract", False, 0)

    final_cost = contracts * cost_per_contract
    bankroll_pct = (final_cost / bankroll_usd) * 100 if bankroll_usd > 0 else 0

    reason_parts = [
        f"Kelly={kelly_f:.3f}",
        f"frac={fractional_f:.3f} (α={alpha}, conf={confidence:.2f})",
        f"{contracts}x @ {cost_cents}¢ = ${final_cost:.2f}",
        f"({bankroll_pct:.1f}% of bankroll)",
    ]
    if capped:
        reason_parts.append(cap_reason)

    return KellyResult(
        contracts=contracts,
        cost_usd=round(final_cost, 2),
        kelly_fraction=round(kelly_f, 4),
        fractional_kelly=round(fractional_f, 4),
        edge_pct=round(edge_pct, 1),
        reason=" | ".join(reason_parts),
        capped=capped,
        bankroll_fraction=round(bankroll_pct, 1),
    )


def kelly_from_edge_result(edge: dict, bankroll_usd: float, **kwargs) -> KellyResult:
    """Convenience wrapper: size a position from an edge scanner result dict."""
    estimated_prob = edge.get("estimated_probability", 0.5)
    market_cents = int(edge.get("yes_price", 50))
    confidence = edge.get("confidence", 0.3)
    direction = edge.get("direction", "fair")

    side = "yes" if direction == "underpriced" else "no"

    return kelly_size(
        estimated_prob=estimated_prob,
        market_price_cents=market_cents,
        confidence=confidence,
        bankroll_usd=bankroll_usd,
        side=side,
        **kwargs,
    )


if __name__ == "__main__":
    import sys

    # Example: size a position
    result = kelly_size(
        estimated_prob=0.62,
        market_price_cents=48,
        confidence=0.68,
        bankroll_usd=200.0,
        side="yes",
    )

    print(f"Contracts: {result.contracts}")
    print(f"Cost: ${result.cost_usd:.2f}")
    print(f"Edge: {result.edge_pct:.1f}%")
    print(f"Kelly: {result.kelly_fraction:.3f}")
    print(f"Fractional: {result.fractional_kelly:.3f}")
    print(f"Bankroll %: {result.bankroll_fraction:.1f}%")
    print(f"Reason: {result.reason}")
