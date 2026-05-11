#!/usr/bin/env python3
"""Test risk validation for edge cases."""

import sys
sys.path.insert(0, '.')

from leg_optimizer import TradeLeg, MultiLegStrategy, validate_strategy_risk
import numpy as np

def make_strategy(legs, max_profit, max_loss, breakevens, stype='put_credit_spread'):
    s = MultiLegStrategy(
        ticker='TEST', strategy_type=stype, underlying_price=100.0, legs=legs,
        max_profit=max_profit, max_loss=max_loss, breakevens=breakevens,
        pop=0.65, expected_value=10.0, risk_adjusted_return=0.5
    )
    return s

def leg(strike, opt_type, action, qty=1):
    return TradeLeg(strike=strike, expiration='2026-03-20', dte=30,
                    premium=1.0, option_type=opt_type, action=action, quantity=qty)

tests = []

# 1. Normal spread (valid)
s = make_strategy([leg(95, 'put', 'sell'), leg(90, 'put', 'buy')], 100, 400, [94.0])
tests.append(("Normal spread", s, True))

# 2. Zero profit (invalid)
s = make_strategy([leg(95, 'put', 'sell'), leg(90, 'put', 'buy')], 0, 400, [95.0])
tests.append(("Zero max_profit", s, False))

# 3. Zero loss (invalid - arb)
s = make_strategy([leg(95, 'put', 'sell'), leg(90, 'put', 'buy')], 100, 0, [94.0])
tests.append(("Zero max_loss", s, False))

# 4. Negative max_profit
s = make_strategy([leg(95, 'put', 'sell'), leg(90, 'put', 'buy')], -50, 400, [95.0])
tests.append(("Negative max_profit", s, False))

# 5. Negative max_loss
s = make_strategy([leg(95, 'put', 'sell'), leg(90, 'put', 'buy')], 100, -50, [94.0])
tests.append(("Negative max_loss", s, False))

# 6. Naked short call (infinite risk)
s = make_strategy([leg(105, 'call', 'sell')], 100, 400, [106.0], 'call_credit_spread')
tests.append(("Naked short call", s, False))

# 7. Naked short put
s = make_strategy([leg(95, 'put', 'sell')], 100, 400, [94.0], 'put_credit_spread')
tests.append(("Naked short put", s, False))

# 8. Ratio spread (2:1 short:long calls)
s = make_strategy(
    [leg(105, 'call', 'sell', 2), leg(110, 'call', 'buy', 1)],
    200, 300, [107.0], 'call_credit_spread'
)
tests.append(("Ratio call spread 2:1", s, False))

# 9. Non-finite breakeven
s = make_strategy([leg(95, 'put', 'sell'), leg(90, 'put', 'buy')], 100, 400, [float('inf')])
tests.append(("Infinite breakeven", s, False))

# 10. NaN pop
s = make_strategy([leg(95, 'put', 'sell'), leg(90, 'put', 'buy')], 100, 400, [94.0])
s.pop = float('nan')
tests.append(("NaN POP", s, False))

# 11. Iron condor (valid)
s = make_strategy(
    [leg(90, 'put', 'buy'), leg(95, 'put', 'sell'), leg(105, 'call', 'sell'), leg(110, 'call', 'buy')],
    200, 300, [93.0, 107.0], 'iron_condor'
)
tests.append(("Valid iron condor", s, True))

# 12. No legs
s = make_strategy([], 100, 400, [94.0])
tests.append(("No legs", s, False))

passed = 0
failed = 0
for name, strat, expected_valid in tests:
    is_valid, reason = validate_strategy_risk(strat)
    status = "PASS" if is_valid == expected_valid else "FAIL"
    if status == "FAIL":
        failed += 1
        print(f"  FAIL: {name} — expected valid={expected_valid}, got valid={is_valid} ({reason})")
    else:
        passed += 1
        print(f"  PASS: {name} — valid={is_valid} ({reason})")

print(f"\n{passed}/{passed+failed} tests passed")
sys.exit(1 if failed > 0 else 0)
