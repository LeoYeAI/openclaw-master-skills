import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from shiploop.budget import BudgetConfig, BudgetTracker, UsageRecord
from shiploop.config import OptimizationConfig, ShipLoopConfig
from shiploop.learnings import Learning, LearningsEngine
from shiploop.loops.optimize import (
    OptimizationResult,
    _build_analysis_prompt,
    _evaluate_outcomes,
    _ExperimentOutcome,
    _VariationCandidate,
    parse_variations,
    should_optimize,
)


@pytest.fixture
def learnings_path():
    with tempfile.NamedTemporaryFile(suffix=".yml", delete=False) as f:
        path = Path(f.name)
    path.unlink()
    yield path
    path.unlink(missing_ok=True)


@pytest.fixture
def engine(learnings_path):
    return LearningsEngine(learnings_path)


@pytest.fixture
def minimal_config():
    return ShipLoopConfig(
        project="TestProject",
        repo="/tmp/test-repo",
        site="https://example.com",
        agent_command="echo test",
        segments=[{"name": "seg-1", "prompt": "Do something"}],
    )


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
        optimization_budget_usd=5.0,
    )
    return BudgetTracker(config, budget_dir)


class TestShouldOptimize:
    def test_skips_when_disabled(self, minimal_config):
        minimal_config.optimization.enabled = False
        eligible, reason = should_optimize(minimal_config, 2, 10)
        assert eligible is False
        assert "disabled" in reason

    def test_skips_trivial_repair_single_attempt_small_diff(self, minimal_config):
        eligible, reason = should_optimize(minimal_config, 1, 3)
        assert eligible is False
        assert "trivial" in reason

    def test_runs_when_repair_took_multiple_attempts(self, minimal_config):
        eligible, reason = should_optimize(minimal_config, 2, 3)
        assert eligible is True
        assert reason == ""

    def test_runs_when_diff_is_large_enough(self, minimal_config):
        eligible, reason = should_optimize(minimal_config, 1, 10)
        assert eligible is True
        assert reason == ""

    def test_runs_with_both_thresholds_exceeded(self, minimal_config):
        eligible, reason = should_optimize(minimal_config, 3, 20)
        assert eligible is True

    def test_skips_at_exact_threshold_boundary(self, minimal_config):
        eligible, _ = should_optimize(minimal_config, 1, 4)
        assert eligible is False

    def test_runs_at_min_diff_lines_threshold(self, minimal_config):
        eligible, _ = should_optimize(minimal_config, 1, 5)
        assert eligible is True

    def test_custom_thresholds(self):
        config = ShipLoopConfig(
            project="Test",
            repo="/tmp/test",
            site="https://example.com",
            agent_command="echo test",
            optimization=OptimizationConfig(
                min_repair_attempts=2,
                min_repair_diff_lines=20,
            ),
            segments=[{"name": "s1", "prompt": "p1"}],
        )
        eligible, _ = should_optimize(config, 1, 15)
        assert eligible is False

        eligible, _ = should_optimize(config, 2, 15)
        assert eligible is True


class TestParseVariations:
    def test_extracts_from_variation_markers(self):
        output = """Some analysis text.

---VARIATION 1---
<type>: context_injection
Add exports to barrel file when creating new components.

---VARIATION 2---
<type>: preflight_hints
Run build check before committing changes.
"""
        variations = parse_variations(output, 2)
        assert len(variations) == 2
        assert variations[0].variation_num == 1
        assert variations[0].improvement_type == "context_injection"
        assert "barrel file" in variations[0].modified_prompt
        assert variations[1].variation_num == 2
        assert variations[1].improvement_type == "preflight_hints"
        assert "build check" in variations[1].modified_prompt

    def test_handles_case_insensitive_markers(self):
        output = """
---variation 1---
<type>: prompt_structure
Modified prompt here.

---Variation 2---
<type>: skill_addition
Another prompt.
"""
        variations = parse_variations(output, 2)
        assert len(variations) == 2
        assert variations[0].improvement_type == "prompt_structure"
        assert variations[1].improvement_type == "skill_addition"

    def test_defaults_to_prompt_structure_without_type(self):
        output = """
---VARIATION 1---
Just a prompt without a type line.
"""
        variations = parse_variations(output, 1)
        assert len(variations) == 1
        assert variations[0].improvement_type == "prompt_structure"
        assert "Just a prompt" in variations[0].modified_prompt

    def test_ignores_invalid_type_values(self):
        output = """
---VARIATION 1---
<type>: invalid_type_here
The actual prompt content.
"""
        variations = parse_variations(output, 1)
        assert len(variations) == 1
        assert variations[0].improvement_type == "prompt_structure"

    def test_returns_empty_for_no_markers(self):
        output = "No variation markers here at all."
        variations = parse_variations(output, 3)
        assert variations == []

    def test_skips_empty_bodies(self):
        output = """
---VARIATION 1---

---VARIATION 2---
Real content here.
"""
        variations = parse_variations(output, 2)
        assert len(variations) == 1
        assert variations[0].variation_num == 2

    def test_respects_expected_count_limit(self):
        output = """
---VARIATION 1---
<type>: context_injection
First.

---VARIATION 2---
<type>: preflight_hints
Second.

---VARIATION 3---
<type>: skill_addition
Third.
"""
        variations = parse_variations(output, 2)
        assert len(variations) == 2

    def test_type_line_removed_from_prompt(self):
        output = """
---VARIATION 1---
<type>: context_injection
The actual instructions go here.
"""
        variations = parse_variations(output, 1)
        assert "<type>" not in variations[0].modified_prompt
        assert "context_injection" not in variations[0].modified_prompt
        assert "actual instructions" in variations[0].modified_prompt


class TestEvaluateOutcomes:
    def test_no_passing_experiments(self):
        outcomes = [
            _ExperimentOutcome(variation_num=1, passed=False),
            _ExperimentOutcome(variation_num=2, passed=False),
        ]
        variations = [
            _VariationCandidate(1, "context_injection", "prompt 1"),
            _VariationCandidate(2, "preflight_hints", "prompt 2"),
        ]
        result = _evaluate_outcomes(outcomes, variations)
        assert result.winner is None
        assert result.experiments_tried == 2

    def test_single_winner(self):
        outcomes = [
            _ExperimentOutcome(variation_num=1, passed=False),
            _ExperimentOutcome(variation_num=2, passed=True, diff_lines=10, improvement_type="context_injection"),
        ]
        variations = [
            _VariationCandidate(1, "prompt_structure", "prompt 1"),
            _VariationCandidate(2, "context_injection", "prompt 2"),
        ]
        result = _evaluate_outcomes(outcomes, variations)
        assert result.winner == 2
        assert result.prompt_delta == "prompt 2"
        assert result.improvement_type == "context_injection"

    def test_tiebreaker_fewest_diff_lines(self):
        outcomes = [
            _ExperimentOutcome(variation_num=1, passed=True, diff_lines=25, improvement_type="prompt_structure"),
            _ExperimentOutcome(variation_num=2, passed=True, diff_lines=8, improvement_type="context_injection"),
        ]
        variations = [
            _VariationCandidate(1, "prompt_structure", "verbose prompt"),
            _VariationCandidate(2, "context_injection", "concise prompt"),
        ]
        result = _evaluate_outcomes(outcomes, variations)
        assert result.winner == 2
        assert result.prompt_delta == "concise prompt"

    def test_empty_outcomes(self):
        result = _evaluate_outcomes([], [])
        assert result.winner is None
        assert result.experiments_tried == 0


class TestBuildAnalysisPrompt:
    def test_includes_all_components(self):
        prompt = _build_analysis_prompt(
            "dark-mode",
            "Add dark mode toggle",
            "Build failed: missing ThemeToggle export",
            "+export { ThemeToggle } from './ThemeToggle'",
            2,
        )
        assert "dark-mode" in prompt
        assert "Add dark mode toggle" in prompt
        assert "missing ThemeToggle export" in prompt
        assert "ThemeToggle" in prompt
        assert "2" in prompt
        assert "VARIATION 1" in prompt
        assert "VARIATION 2" in prompt

    def test_truncates_long_error(self):
        long_error = "x" * 1000
        prompt = _build_analysis_prompt("seg", "prompt", long_error, "diff", 2)
        assert "x" * 500 in prompt
        assert "x" * 501 not in prompt

    def test_truncates_long_diff(self):
        long_diff = "+" * 1000
        prompt = _build_analysis_prompt("seg", "prompt", "error", long_diff, 2)
        assert "+" * 500 in prompt
        assert "+" * 501 not in prompt


class TestOptimizationBudget:
    def test_check_within_budget(self, tracker):
        assert tracker.check_optimization_budget("seg-1") is True

    def test_check_budget_exceeded(self, tracker):
        for i in range(3):
            tracker.record_usage(UsageRecord(
                segment="seg-1", loop=f"optimize-exp-{i}",
                estimated_cost_usd=2.0,
            ))
        assert tracker.check_optimization_budget("seg-1") is False

    def test_only_counts_optimization_loops(self, tracker):
        tracker.record_usage(UsageRecord(
            segment="seg-1", loop="ship",
            estimated_cost_usd=8.0,
        ))
        tracker.record_usage(UsageRecord(
            segment="seg-1", loop="repair-1",
            estimated_cost_usd=3.0,
        ))
        assert tracker.check_optimization_budget("seg-1") is True

    def test_separate_per_segment(self, tracker):
        tracker.record_usage(UsageRecord(
            segment="seg-1", loop="optimize-exp-1",
            estimated_cost_usd=4.0,
        ))
        assert tracker.check_optimization_budget("seg-2") is True


class TestLearningOptimizationFields:
    def test_learning_has_optimization_fields(self):
        learning = Learning(
            id="L001", date="2026-01-01", segment="seg",
            failure="f", root_cause="r", fix="x",
            learning_type="optimization",
            improvement_type="context_injection",
            prompt_delta="Always add exports to barrel files.",
        )
        assert learning.learning_type == "optimization"
        assert learning.improvement_type == "context_injection"
        assert learning.prompt_delta == "Always add exports to barrel files."

    def test_default_learning_type_is_failure(self):
        learning = Learning(
            id="L001", date="2026-01-01", segment="seg",
            failure="f", root_cause="r", fix="x",
        )
        assert learning.learning_type == "failure"
        assert learning.improvement_type == ""
        assert learning.prompt_delta == ""


class TestFormatForPromptWithOptimizations:
    def test_failure_only(self, engine):
        engine.record(segment="s1", failure="build failed", root_cause="bad import", fix="fixed")
        learnings = engine.search("build")
        output = engine.format_for_prompt(learnings)
        assert "Relevant Lessons from Past Runs" in output
        assert "build failed" in output
        assert "Use these lessons" in output
        assert "Optimized Instructions" not in output

    def test_optimization_only(self, engine):
        engine.record(segment="s1", failure="f", root_cause="r", fix="x")
        last = engine.learnings[-1]
        last.learning_type = "optimization"
        last.improvement_type = "context_injection"
        last.prompt_delta = "Always export components from barrel files."
        engine._save()

        reloaded = LearningsEngine(engine.path)
        output = reloaded.format_for_prompt(reloaded.learnings)
        assert "Optimized Instructions from Past Runs" in output
        assert "context_injection" in output
        assert "Always export components" in output
        assert "Use these lessons" not in output

    def test_mixed_failure_and_optimization(self, engine):
        engine.record(segment="s1", failure="build failed", root_cause="bad import", fix="fixed")
        engine.record(segment="s2", failure="repair needed", root_cause="missing export", fix="added")
        engine.learnings[-1].learning_type = "optimization"
        engine.learnings[-1].improvement_type = "preflight_hints"
        engine.learnings[-1].prompt_delta = "Check exports before building."
        engine._save()

        reloaded = LearningsEngine(engine.path)
        output = reloaded.format_for_prompt(reloaded.learnings)
        assert "Relevant Lessons from Past Runs" in output
        assert "Optimized Instructions from Past Runs" in output
        assert "build failed" in output
        assert "Check exports" in output

    def test_empty_returns_empty(self, engine):
        assert engine.format_for_prompt([]) == ""


class TestOptimizationResultDataclass:
    def test_default_values(self):
        result = OptimizationResult(ran=False)
        assert result.ran is False
        assert result.experiments_tried == 0
        assert result.winner is None
        assert result.prompt_delta == ""
        assert result.improvement_type == ""

    def test_with_winner(self):
        result = OptimizationResult(
            ran=True,
            experiments_tried=2,
            winner=1,
            prompt_delta="Add barrel exports.",
            improvement_type="context_injection",
        )
        assert result.ran is True
        assert result.winner == 1


class TestOptimizationConfig:
    def test_defaults(self):
        config = OptimizationConfig()
        assert config.enabled is True
        assert config.max_experiments == 2
        assert config.min_repair_attempts == 1
        assert config.min_repair_diff_lines == 5
        assert config.budget_usd == 5.0

    def test_custom_values(self):
        config = OptimizationConfig(
            enabled=False,
            max_experiments=4,
            min_repair_attempts=2,
            min_repair_diff_lines=10,
            budget_usd=15.0,
        )
        assert config.enabled is False
        assert config.max_experiments == 4

    def test_config_in_shiploop_config(self):
        config = ShipLoopConfig(
            project="Test",
            repo="/tmp/test",
            site="https://example.com",
            agent_command="echo test",
            optimization={"enabled": False, "max_experiments": 4},
            segments=[{"name": "s1", "prompt": "p1"}],
        )
        assert config.optimization.enabled is False
        assert config.optimization.max_experiments == 4


class TestIdempotency:
    def test_skip_if_optimization_already_exists(self, engine):
        engine.record(segment="seg-1", failure="f", root_cause="r", fix="x")
        engine.learnings[-1].learning_type = "optimization"
        engine.learnings[-1].improvement_type = "context_injection"
        engine.learnings[-1].prompt_delta = "existing optimization"
        engine._save()

        existing = [
            l for l in engine.learnings
            if l.segment == "seg-1" and l.learning_type == "optimization"
        ]
        assert len(existing) == 1
