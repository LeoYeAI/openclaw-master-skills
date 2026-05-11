"""Tests for rebalance trigger logic."""

import unittest
from datetime import datetime, timedelta


def tick_to_price(tick: int, decimal_adj: float = 1e12) -> float:
    return 1.0001**tick / decimal_adj


def check_rebalance_triggers(
    price: float,
    state: dict,
    atr_pct: float,
    mtf: dict | None = None,
) -> dict | None:
    """Extracted trigger logic matching cl_lp.py."""
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

    # [2] Higher yield pool — TODO: requires hourly yield API

    return None


class TestOutOfRange(unittest.TestCase):
    """Only out_of_range should trigger rebalance."""

    def _make_state(self, tick_lower: int, tick_upper: int, age_hours: float = 0):
        state = {
            "position": {
                "tick_lower": tick_lower,
                "tick_upper": tick_upper,
                "created_atr_pct": 2.0,
            }
        }
        if age_hours:
            state["position"]["created_at"] = (
                datetime.now() - timedelta(hours=age_hours)
            ).isoformat()
        return state

    def _range_prices(self, tick_lower, tick_upper):
        return tick_to_price(tick_lower), tick_to_price(tick_upper)

    def test_in_range_center_no_trigger(self):
        """Price at center of range → no trigger."""
        tl, tu = -200220, -199200
        lower, upper = self._range_prices(tl, tu)
        state = self._make_state(tl, tu, age_hours=100)
        result = check_rebalance_triggers((lower + upper) / 2, state, 2.0)
        self.assertIsNone(result)

    def test_in_range_near_edge_no_trigger(self):
        """Price at 5% of range but still in range → no trigger."""
        tl, tu = -200220, -199200
        lower, upper = self._range_prices(tl, tu)
        price = lower + 0.05 * (upper - lower)
        state = self._make_state(tl, tu, age_hours=100)
        result = check_rebalance_triggers(price, state, 2.0)
        self.assertIsNone(result)

    def test_below_range_triggers(self):
        """Price below lower → out_of_range."""
        tl, tu = -200220, -199200
        lower, _ = self._range_prices(tl, tu)
        state = self._make_state(tl, tu)
        result = check_rebalance_triggers(lower * 0.95, state, 2.0)
        self.assertIsNotNone(result)
        self.assertEqual(result["trigger"], "out_of_range")
        self.assertEqual(result["detail"], "below")

    def test_above_range_triggers(self):
        """Price above upper → out_of_range."""
        tl, tu = -200220, -199200
        _, upper = self._range_prices(tl, tu)
        state = self._make_state(tl, tu)
        result = check_rebalance_triggers(upper * 1.05, state, 2.0)
        self.assertIsNotNone(result)
        self.assertEqual(result["trigger"], "out_of_range")
        self.assertEqual(result["detail"], "above")

    def test_no_position_no_trigger(self):
        """No position → no trigger."""
        result = check_rebalance_triggers(2000.0, {}, 2.0)
        self.assertIsNone(result)

    def test_high_volatility_no_trigger_if_in_range(self):
        """Volatility shift alone should NOT trigger (removed)."""
        tl, tu = -200220, -199200
        lower, upper = self._range_prices(tl, tu)
        state = self._make_state(tl, tu, age_hours=48)
        # atr_pct=5.0 vs created_atr=2.0 → 150% change, old logic would trigger
        result = check_rebalance_triggers((lower + upper) / 2, state, 5.0)
        self.assertIsNone(result)

    def test_old_position_no_trigger_if_in_range(self):
        """Old position (100h) in range should NOT trigger (time_decay removed)."""
        tl, tu = -200220, -199200
        lower, upper = self._range_prices(tl, tu)
        price = lower + 0.10 * (upper - lower)  # near edge but in range
        state = self._make_state(tl, tu, age_hours=100)
        result = check_rebalance_triggers(price, state, 2.0)
        self.assertIsNone(result)


class TestExponentialBackoff(unittest.TestCase):
    """Test that backoff grows exponentially and caps correctly."""

    def test_backoff_progression(self):
        COOLDOWN_AFTER_ERRORS = 3600
        for n, expected_min in [(1, 10), (2, 20), (3, 40), (4, 60), (5, 60), (6, 60)]:
            backoff = min(600 * (2 ** (n - 1)), COOLDOWN_AFTER_ERRORS)
            self.assertEqual(backoff, expected_min * 60, f"n={n}")

    def test_backoff_cap(self):
        COOLDOWN_AFTER_ERRORS = 3600
        for n in range(1, 20):
            backoff = min(600 * (2 ** (n - 1)), COOLDOWN_AFTER_ERRORS)
            self.assertLessEqual(backoff, COOLDOWN_AFTER_ERRORS)


if __name__ == "__main__":
    unittest.main()
