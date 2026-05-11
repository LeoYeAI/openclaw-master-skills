"""
Position Sizer — Kelly Criterion Adapted for Small Options Accounts

Calculates optimal position size for vertical spread trades using the
Kelly criterion, with aggressive guardrails for capital preservation
on small accounts (default: $390).

Designed to integrate with:
    - Conviction Engine (80+ score = EXECUTE signal)
    - Options Profit Calculator (POP, max loss, max profit)

Kelly Formula Used:
    Kelly % = (POP * Win - (1 - POP) * Loss) / Win

    Where:
        POP  = Probability of Profit (0.0 to 1.0)
        Win  = Max profit per spread (dollars)
        Loss = Max loss per spread (dollars, positive number)

    We apply a fractional Kelly (default quarter-Kelly = 0.25) to
    reduce volatility of returns and account drawdown risk.

Example Usage:
    >>> from position_sizer import calculate_position, format_recommendation

    # Spread with $200 max loss, $100 max profit, 65% POP
    >>> result = calculate_position(
    ...     account_value=390,
    ...     max_loss_per_spread=200,
    ...     win_amount=100,
    ...     pop=0.65,
    ... )
    >>> result['recommendation']
    'SKIP'
    >>> result['contracts']
    0

    # Tighter spread: $80 max loss, $40 max profit, 55% POP
    >>> result = calculate_position(
    ...     account_value=390,
    ...     max_loss_per_spread=80,
    ...     win_amount=40,
    ...     pop=0.55,
    ... )
    >>> result['recommendation']
    'EXECUTE'
    >>> result['contracts']
    1
"""

from __future__ import annotations

import math
from typing import Optional, Dict, Any

# Import enhanced Kelly for unified implementation
from enhanced_kelly import EnhancedKellySizer, KellyFraction, PositionResult


# ---------------------------------------------------------------------------
# Constants — Account Guardrails
# ---------------------------------------------------------------------------

DEFAULT_ACCOUNT_VALUE: float = 390.0
DEFAULT_KELLY_FRACTION: float = 0.25       # Quarter-Kelly
DEFAULT_MAX_POSITION_PCT: float = 0.25     # 25% of account per trade
MAX_SINGLE_TRADE_RISK: float = 100.0       # Hard dollar cap
CASH_BUFFER: float = 150.0                 # Always keep this much cash
MAX_DEPLOYABLE_CAPITAL: float = DEFAULT_ACCOUNT_VALUE - CASH_BUFFER  # $240
WIDE_SPREAD_THRESHOLD: float = 150.0       # Flag spreads wider than this


# ---------------------------------------------------------------------------
# Core: Kelly Criterion (delegated to enhanced_kelly module)
# ---------------------------------------------------------------------------

def kelly_criterion(pop: float, win_amount: float, loss_amount: float) -> float:
    """
    Compute the full Kelly criterion percentage.
    
    This is a convenience wrapper around EnhancedKellySizer.kelly_criterion()
    for backwards compatibility.
    
    Args:
        pop: Probability of profit, between 0.0 and 1.0.
        win_amount: Dollar profit if the trade wins (positive).
        loss_amount: Dollar loss if the trade loses (positive).

    Returns:
        Kelly percentage as a decimal (e.g. 0.10 = 10% of bankroll).
        Returns 0.0 if the edge is zero or negative.
    """
    if not 0.0 <= pop <= 1.0:
        raise ValueError(f"POP must be between 0 and 1, got {pop}")
    if win_amount <= 0:
        raise ValueError(f"win_amount must be positive, got {win_amount}")
    if loss_amount <= 0:
        raise ValueError(f"loss_amount must be positive, got {loss_amount}")
    
    sizer = EnhancedKellySizer()
    kelly, _ = sizer.kelly_criterion(pop, win_amount, loss_amount)
    return kelly


# ---------------------------------------------------------------------------
# Core: Position Sizing
# ---------------------------------------------------------------------------

def calculate_position(
    account_value: float = DEFAULT_ACCOUNT_VALUE,
    max_loss_per_spread: float = 0.0,
    win_amount: float = 0.0,
    pop: float = 0.0,
    kelly_fraction: float = DEFAULT_KELLY_FRACTION,
    max_position_pct: float = DEFAULT_MAX_POSITION_PCT,
) -> dict:
    """Calculate position size with Kelly criterion and account guardrails.

    This is the main entry point. Feed it the outputs from the options
    profit calculator (POP, max loss, max profit) and it returns a
    sized recommendation.

    Args:
        account_value: Total account value in dollars.
        max_loss_per_spread: Maximum loss per single spread contract
            (positive number, in dollars).
        win_amount: Maximum profit per single spread contract
            (positive number, in dollars).
        pop: Probability of profit from the calculator (0.0 to 1.0).
        kelly_fraction: Fraction of Kelly to use (0.25 = quarter-Kelly).
        max_position_pct: Maximum percentage of account to risk on
            any single trade (0.0 to 1.0).

    Returns:
        Dictionary with keys:
            contracts (int): Number of spread contracts to trade.
            total_risk (float): Total dollar risk (contracts * max_loss).
            risk_pct (float): Risk as percentage of account (0.0 to 1.0).
            kelly_full_pct (float): What full Kelly recommends.
            kelly_adj_pct (float): Fractional Kelly (after applying fraction).
            recommendation (str): 'EXECUTE', 'REDUCE', or 'SKIP'.
            reason (str): Human-readable explanation of the decision.

    Examples:
        >>> # Wide spread on a $390 account — too risky
        >>> r = calculate_position(390, 200, 100, 0.65)
        >>> r['recommendation']
        'SKIP'
        >>> r['contracts']
        0

        >>> # Tight spread, modest edge
        >>> r = calculate_position(390, 80, 40, 0.55)
        >>> r['recommendation']
        'EXECUTE'
        >>> r['contracts']
        1

        >>> # Strong edge, high POP
        >>> r = calculate_position(390, 50, 150, 0.70)
        >>> r['recommendation']
        'EXECUTE'
        >>> r['contracts']
        1
    """
    # Input validation
    if account_value <= 0:
        raise ValueError(f"account_value must be positive, got {account_value}")
    if max_loss_per_spread <= 0:
        raise ValueError(f"max_loss_per_spread must be positive, got {max_loss_per_spread}")
    if win_amount <= 0:
        raise ValueError(f"win_amount must be positive, got {win_amount}")
    if not 0.0 <= pop <= 1.0:
        raise ValueError(f"pop must be between 0 and 1, got {pop}")

    # Compute Kelly
    full_kelly = kelly_criterion(pop, win_amount, max_loss_per_spread)
    adj_kelly = full_kelly * kelly_fraction

    # Base result template
    result = {
        "contracts": 0,
        "total_risk": 0.0,
        "risk_pct": 0.0,
        "kelly_full_pct": round(full_kelly, 4),
        "kelly_adj_pct": round(adj_kelly, 4),
        "recommendation": "SKIP",
        "reason": "",
    }

    # --- Decision Gate 1: Kelly says no edge ---
    if full_kelly <= 0:
        result["reason"] = (
            f"Negative edge. Kelly = {full_kelly:.2%}. "
            f"POP of {pop:.0%} does not compensate for "
            f"{max_loss_per_spread / win_amount:.1f}:1 risk/reward ratio."
        )
        return result

    # --- Decision Gate 2: Single spread exceeds wide-spread threshold ---
    if max_loss_per_spread > WIDE_SPREAD_THRESHOLD:
        result["reason"] = (
            f"Max loss per spread (${max_loss_per_spread:.0f}) exceeds "
            f"${WIDE_SPREAD_THRESHOLD:.0f} threshold. "
            f"Find tighter strikes to reduce per-contract risk."
        )
        return result

    # --- Compute deployable capital ---
    deployable = min(
        account_value - CASH_BUFFER,  # respect cash buffer
        MAX_DEPLOYABLE_CAPITAL,       # hard cap
    )
    deployable = max(deployable, 0.0)  # can't deploy negative

    if deployable <= 0:
        result["reason"] = (
            f"Insufficient deployable capital. Account ${account_value:.0f} "
            f"minus ${CASH_BUFFER:.0f} buffer = ${deployable:.0f} available."
        )
        return result

    # --- Compute Kelly-optimal dollar risk ---
    max_risk_by_pct = account_value * max_position_pct
    hard_dollar_cap = min(MAX_SINGLE_TRADE_RISK, max_risk_by_pct, deployable)
    kelly_dollar_risk = adj_kelly * account_value

    # --- Determine contracts ---
    effective_risk = min(kelly_dollar_risk, hard_dollar_cap)
    contracts = max(int(math.floor(effective_risk / max_loss_per_spread)), 0)

    # At least 1 contract if Kelly is positive and we can afford it
    if contracts == 0 and full_kelly > 0 and max_loss_per_spread <= hard_dollar_cap:
        contracts = 1

    # Final affordability check
    if contracts * max_loss_per_spread > hard_dollar_cap:
        contracts = max(int(math.floor(hard_dollar_cap / max_loss_per_spread)), 0)

    if contracts == 0:
        result["reason"] = (
            f"Kelly is positive ({full_kelly:.2%}) but min spread cost "
            f"(${max_loss_per_spread:.0f}) exceeds risk cap "
            f"(${hard_dollar_cap:.0f})."
        )
        return result

    total_risk = contracts * max_loss_per_spread
    risk_pct = total_risk / account_value

    # --- Determine recommendation ---
    was_capped = kelly_dollar_risk > hard_dollar_cap
    recommendation = "REDUCE" if was_capped else "EXECUTE"

    if was_capped:
        reason = (
            f"Kelly suggests risking ${kelly_dollar_risk:.0f} "
            f"({adj_kelly:.2%} of account) but guardrails cap at "
            f"${hard_dollar_cap:.0f}. Sized down to {contracts} contract(s)."
        )
    else:
        reason = (
            f"Edge confirmed. {contracts} contract(s) at "
            f"${max_loss_per_spread:.0f} risk each = ${total_risk:.0f} total "
            f"({risk_pct:.1%} of account)."
        )

    result.update({
        "contracts": contracts,
        "total_risk": round(total_risk, 2),
        "risk_pct": round(risk_pct, 4),
        "recommendation": recommendation,
        "reason": reason,
    })

    return result


# ---------------------------------------------------------------------------
# Helper: Pretty-Print Recommendation
# ---------------------------------------------------------------------------

def format_recommendation(result: dict) -> str:
    """Format a position sizing result for CLI display.

    Args:
        result: Dictionary returned by calculate_position().

    Returns:
        Multi-line formatted string.

    Example:
        >>> r = calculate_position(390, 80, 40, 0.55)
        >>> print(format_recommendation(r))  # doctest: +SKIP
        ╔══════════════════════════════════════╗
        ║  POSITION SIZER — EXECUTE            ║
        ...
    """
    rec = result["recommendation"]

    # Status bar icons
    status_icons = {
        "EXECUTE": "[GO]",
        "REDUCE": "[!!]",
        "SKIP": "[XX]",
    }
    icon = status_icons.get(rec, "")

    border = "=" * 50
    lines = [
        f"\n{'=' * 50}",
        f"  POSITION SIZER  {icon}  {rec}",
        f"{'=' * 50}",
        "",
        f"  Kelly (full):       {result['kelly_full_pct']:>8.2%}",
        f"  Kelly (adjusted):   {result['kelly_adj_pct']:>8.2%}",
        "",
        f"  Contracts:          {result['contracts']:>8d}",
        f"  Total Risk:         ${result['total_risk']:>7.2f}",
        f"  Risk % of Account:  {result['risk_pct']:>8.2%}",
        "",
        f"  {result['reason']}",
        "",
        f"{'=' * 50}",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Helper: Strike Adjustment Suggestions
# ---------------------------------------------------------------------------

def suggest_strike_adjustment(
    max_loss: float,
    account_value: float = DEFAULT_ACCOUNT_VALUE,
) -> str:
    """Provide guidance on tightening strikes to fit account size.

    When a spread's max loss is too large for the account, this function
    suggests target strike widths and max-loss ranges that would be
    tradeable.

    Args:
        max_loss: Current max loss per spread (dollars).
        account_value: Account value (dollars).

    Returns:
        Human-readable suggestion string.

    Examples:
        >>> print(suggest_strike_adjustment(200, 390))  # doctest: +SKIP
        STRIKE ADJUSTMENT NEEDED
        ...
    """
    deployable = max(account_value - CASH_BUFFER, 0)
    hard_cap = min(MAX_SINGLE_TRADE_RISK, deployable)

    lines = []

    if max_loss <= hard_cap:
        lines.append("Current spread width is within account limits.")
        lines.append(f"Max loss ${max_loss:.0f} fits under ${hard_cap:.0f} cap.")
        return "\n".join(lines)

    lines.append("STRIKE ADJUSTMENT NEEDED")
    lines.append(f"  Current max loss:     ${max_loss:.0f}")
    lines.append(f"  Account risk cap:     ${hard_cap:.0f}")
    lines.append(f"  Overshoot:            ${max_loss - hard_cap:.0f}")
    lines.append("")
    lines.append("Suggestions:")

    # For vertical spreads, max loss = (strike width - net credit) * 100
    # or (strike width * 100) - net credit for credit spreads.
    # We work backward from the hard cap.
    lines.append(f"  1. Target max loss under ${hard_cap:.0f} per spread.")
    lines.append(f"  2. For a $1-wide spread: max loss ~ $50-$80 (good fit).")
    lines.append(f"  3. For a $2-wide spread: max loss ~ $100-$150 (borderline).")
    lines.append(f"  4. For a $5-wide spread: max loss ~ $300-$400 (too wide).")
    lines.append("")
    lines.append("Rules of thumb for a ${:.0f} account:".format(account_value))
    lines.append(f"  - Prefer $1-$2 wide strikes")
    lines.append(f"  - Collect at least 30% of spread width as credit")
    lines.append(f"  - Keep max loss under ${hard_cap:.0f} per contract")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Batch Analysis Helper
# ---------------------------------------------------------------------------

def screen_trades(
    trades: list[dict],
    account_value: float = DEFAULT_ACCOUNT_VALUE,
    kelly_fraction: float = DEFAULT_KELLY_FRACTION,
) -> list[dict]:
    """Screen multiple trade candidates and rank by Kelly edge.

    Args:
        trades: List of dicts, each with keys:
            'ticker' (str), 'max_loss' (float), 'win_amount' (float),
            'pop' (float), and optionally 'conviction' (int).
        account_value: Account value in dollars.
        kelly_fraction: Fractional Kelly to apply.

    Returns:
        List of dicts sorted by Kelly edge (best first), each augmented
        with position sizing results.

    Example:
        >>> candidates = [
        ...     {'ticker': 'AAPL', 'max_loss': 80, 'win_amount': 40, 'pop': 0.60},
        ...     {'ticker': 'SPY',  'max_loss': 50, 'win_amount': 150, 'pop': 0.70},
        ... ]
        >>> ranked = screen_trades(candidates, account_value=390)
        >>> ranked[0]['ticker']  # Best edge first
        'SPY'
    """
    results = []
    for trade in trades:
        sizing = calculate_position(
            account_value=account_value,
            max_loss_per_spread=trade["max_loss"],
            win_amount=trade["win_amount"],
            pop=trade["pop"],
            kelly_fraction=kelly_fraction,
        )
        entry = {**trade, **sizing}
        results.append(entry)

    # Sort: EXECUTE/REDUCE first, then by Kelly edge descending
    priority = {"EXECUTE": 0, "REDUCE": 1, "SKIP": 2}
    results.sort(key=lambda x: (priority.get(x["recommendation"], 3), -x["kelly_full_pct"]))

    return results


# ---------------------------------------------------------------------------
# Enhanced Kelly Integration
# ---------------------------------------------------------------------------

def calculate_position_enhanced(
    spread_cost: float,
    max_loss: float,
    win_amount: float,
    conviction: float,
    pop: float,
    account_value: float = DEFAULT_ACCOUNT_VALUE,
    max_drawdown: float = 0.20,
    existing_correlation: float = 0.0,
) -> Dict[str, Any]:
    """
    Calculate position size using enhanced Kelly criterion.
    
    This function uses the EnhancedKellySizer for
    drawdown-constrained, conviction-based position sizing.
    
    Args:
        spread_cost: Cost to enter one spread.
        max_loss: Maximum loss per contract.
        win_amount: Maximum win per contract.
        conviction: Conviction score from engine (0-100).
        pop: Probability of profit.
        account_value: Account value in dollars.
        max_drawdown: Maximum acceptable drawdown.
        existing_correlation: Correlation with existing positions.
        
    Returns:
        Position sizing dictionary with enhanced metrics.
        
    Example:
        >>> result = calculate_position_enhanced(
        ...     spread_cost=80, max_loss=80, win_amount=40,
        ...     conviction=85, pop=0.65
        ... )
        >>> print(f"Contracts: {result['contracts']}")
    """
    sizer = EnhancedKellySizer(account_value, max_drawdown)
    return sizer.calculate_position(
        spread_cost=spread_cost,
        max_loss=max_loss,
        win_amount=win_amount,
        conviction=conviction,
        pop=pop,
        existing_correlation=existing_correlation,
    )


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

def _cli() -> None:
    """Simple CLI for quick position sizing checks."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Position Sizer — Kelly Criterion for Small Options Accounts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python position_sizer.py --loss 80 --win 40 --pop 0.55
  python position_sizer.py --loss 200 --win 100 --pop 0.65 --account 390
  python position_sizer.py --loss 50 --win 150 --pop 0.70 --kelly-frac 0.25
        """,
    )
    parser.add_argument("--account", type=float, default=DEFAULT_ACCOUNT_VALUE,
                        help=f"Account value (default: ${DEFAULT_ACCOUNT_VALUE:.0f})")
    parser.add_argument("--loss", type=float, required=True,
                        help="Max loss per spread (dollars)")
    parser.add_argument("--win", type=float, required=True,
                        help="Max profit per spread (dollars)")
    parser.add_argument("--pop", type=float, required=True,
                        help="Probability of profit (0.0 to 1.0)")
    parser.add_argument("--kelly-frac", type=float, default=DEFAULT_KELLY_FRACTION,
                        help=f"Kelly fraction (default: {DEFAULT_KELLY_FRACTION})")
    parser.add_argument("--max-pct", type=float, default=DEFAULT_MAX_POSITION_PCT,
                        help=f"Max position %% (default: {DEFAULT_MAX_POSITION_PCT})")

    args = parser.parse_args()

    result = calculate_position(
        account_value=args.account,
        max_loss_per_spread=args.loss,
        win_amount=args.win,
        pop=args.pop,
        kelly_fraction=args.kelly_frac,
        max_position_pct=args.max_pct,
    )

    print(format_recommendation(result))

    # If SKIP due to wide strikes, show adjustment guidance
    if result["recommendation"] == "SKIP" and args.loss > WIDE_SPREAD_THRESHOLD:
        print()
        print(suggest_strike_adjustment(args.loss, args.account))


if __name__ == "__main__":
    _cli()
