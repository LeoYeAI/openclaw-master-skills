import json
import tempfile
from pathlib import Path

import pytest

from shiploop.budget import BudgetConfig, BudgetTracker, UsageRecord, estimate_cost, estimate_from_prompt, parse_token_usage


@pytest.fixture
def budget_dir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture
def tracker(budget_dir):
    config = BudgetConfig(
        max_usd_per_segment=10.0,
        max_usd_per_run=50.0,
        halt_on_breach=True,
    )
    return BudgetTracker(config, budget_dir)


class TestBudgetTracker:
    def test_record_and_retrieve(self, tracker):
        record = UsageRecord(
            segment="dark-mode",
            loop="ship",
            tokens_in=1000,
            tokens_out=500,
            estimated_cost_usd=0.05,
            duration_seconds=10.0,
        )
        tracker.record_usage(record)

        assert tracker.get_segment_cost("dark-mode") == 0.05
        assert tracker.get_run_cost() == 0.05

    def test_budget_check_within_limits(self, tracker):
        assert tracker.check_budget("dark-mode") is True

    def test_budget_check_segment_exceeded(self, tracker):
        for i in range(5):
            tracker.record_usage(UsageRecord(
                segment="dark-mode", loop=f"repair-{i}",
                estimated_cost_usd=3.0,
            ))

        assert tracker.check_budget("dark-mode") is False

    def test_budget_check_run_exceeded(self, tracker):
        for i in range(6):
            tracker.record_usage(UsageRecord(
                segment=f"seg-{i}", loop="ship",
                estimated_cost_usd=9.0,
            ))

        assert tracker.check_budget("new-seg") is False

    def test_budget_check_halt_disabled(self, budget_dir):
        config = BudgetConfig(halt_on_breach=False)
        t = BudgetTracker(config, budget_dir)
        for i in range(10):
            t.record_usage(UsageRecord(
                segment="s", loop="ship", estimated_cost_usd=100.0,
            ))
        assert t.check_budget("s") is True

    def test_persistence(self, budget_dir):
        config = BudgetConfig()
        t1 = BudgetTracker(config, budget_dir)
        t1.record_usage(UsageRecord(
            segment="test", loop="ship", estimated_cost_usd=1.23,
        ))

        t2 = BudgetTracker(config, budget_dir)
        assert t2.get_run_cost() == 1.23

    def test_summary(self, tracker):
        tracker.record_usage(UsageRecord(
            segment="seg-1", loop="ship", estimated_cost_usd=2.0,
        ))
        tracker.record_usage(UsageRecord(
            segment="seg-2", loop="ship", estimated_cost_usd=3.0,
        ))
        summary = tracker.get_summary()
        assert summary["total_cost_usd"] == 5.0
        assert summary["by_segment"]["seg-1"] == 2.0
        assert summary["by_segment"]["seg-2"] == 3.0


class TestTokenParsing:
    def test_parse_token_usage(self):
        output = """
        Some output here
        input_tokens: 1,234
        output_tokens: 567
        Done.
        """
        tokens_in, tokens_out = parse_token_usage(output)
        assert tokens_in == 1234
        assert tokens_out == 567

    def test_parse_no_tokens(self):
        tokens_in, tokens_out = parse_token_usage("hello world")
        assert tokens_in == 0
        assert tokens_out == 0

    def test_parse_claude_format(self):
        output = "input tokens: 12345\noutput tokens: 6789"
        tokens_in, tokens_out = parse_token_usage(output)
        assert tokens_in == 12345
        assert tokens_out == 6789

    def test_parse_gpt_format_with_equals(self):
        output = "input_tokens=1000\noutput_tokens=500"
        tokens_in, tokens_out = parse_token_usage(output)
        assert tokens_in == 1000
        assert tokens_out == 500

    def test_parse_large_numbers_with_commas(self):
        output = "input_tokens: 1,234,567\noutput_tokens: 890,123"
        tokens_in, tokens_out = parse_token_usage(output)
        assert tokens_in == 1234567
        assert tokens_out == 890123

    def test_parse_empty_string(self):
        tokens_in, tokens_out = parse_token_usage("")
        assert tokens_in == 0
        assert tokens_out == 0


class TestEstimateFromPrompt:
    def test_basic_estimation(self):
        tokens_in, tokens_out = estimate_from_prompt(4000, 10.0)
        assert tokens_in == 1000
        assert tokens_out == 300

    def test_minimum_floor_input(self):
        tokens_in, tokens_out = estimate_from_prompt(0, 10.0)
        assert tokens_in == 100

    def test_minimum_floor_output(self):
        tokens_in, tokens_out = estimate_from_prompt(4000, 0.0)
        assert tokens_out == 200

    def test_long_duration_scales_output(self):
        tokens_in, tokens_out = estimate_from_prompt(4000, 60.0)
        assert tokens_out == 1800


class TestCostEstimate:
    def test_default_pricing(self):
        cost = estimate_cost(1_000_000, 100_000)
        assert cost > 0

    def test_zero_tokens(self):
        cost = estimate_cost(0, 0)
        assert cost == 0.0

    def test_specific_model(self):
        cost = estimate_cost(1_000_000, 1_000_000, "claude-opus-4-6")
        assert cost > estimate_cost(1_000_000, 1_000_000, "claude-haiku-4-5")
