import pytest

from shiploop.loops.meta import _build_failure_context, _build_meta_prompt, _parse_experiments


class TestParseExperiments:
    def test_extracts_from_approach_markers(self):
        meta_output = """Some analysis text here.

---APPROACH 1---
Rewrite the component using a different library.
Use react-aria instead of radix.

---APPROACH 2---
Simplify the implementation by removing unnecessary abstraction.
Use plain CSS instead of CSS-in-JS.

---APPROACH 3---
Split the feature into two smaller segments.
"""
        experiments = _parse_experiments(meta_output, 3, "original", "context")
        assert len(experiments) == 3
        assert "react-aria" in experiments[1]
        assert "plain CSS" in experiments[2]
        assert "Split the feature" in experiments[3]

    def test_handles_case_insensitive_markers(self):
        meta_output = """
---approach 1---
First approach text.

---Approach 2---
Second approach text.
"""
        experiments = _parse_experiments(meta_output, 2, "orig", "ctx")
        assert "First approach" in experiments[1]
        assert "Second approach" in experiments[2]

    def test_strips_code_fences(self):
        meta_output = """
---APPROACH 1---
```
Do this thing with code fences wrapping it.
```

---APPROACH 2---
No fences here.
"""
        experiments = _parse_experiments(meta_output, 2, "orig", "ctx")
        assert "```" not in experiments[1]
        assert "Do this thing" in experiments[1]

    def test_fallback_when_parsing_fails(self):
        meta_output = "This output has no approach markers at all."
        experiments = _parse_experiments(meta_output, 3, "Build a widget", "error context")
        assert len(experiments) == 3
        for exp_num in [1, 2, 3]:
            assert "Alternative approach" in experiments[exp_num]
            assert "Build a widget" in experiments[exp_num]

    def test_partial_markers(self):
        meta_output = """
---APPROACH 1---
First approach only.
"""
        experiments = _parse_experiments(meta_output, 3, "original", "context")
        assert "First approach" in experiments[1]
        assert "Alternative approach 2" in experiments[2]
        assert "Alternative approach 3" in experiments[3]

    def test_empty_approach_body_uses_fallback(self):
        meta_output = """
---APPROACH 1---

---APPROACH 2---
Real content here.
"""
        experiments = _parse_experiments(meta_output, 2, "original", "context")
        assert "Alternative approach 1" in experiments[1]
        assert "Real content" in experiments[2]


class TestBuildFailureContext:
    def test_includes_segment_name(self):
        ctx = _build_failure_context("dark-mode", "Add dark mode", ["error 1"])
        assert "dark-mode" in ctx
        assert "Add dark mode" in ctx

    def test_includes_all_errors(self):
        errors = ["build error", "lint error", "test error"]
        ctx = _build_failure_context("seg", "prompt", errors)
        assert "Attempt 1" in ctx
        assert "Attempt 2" in ctx
        assert "Attempt 3" in ctx
        assert "build error" in ctx
        assert "test error" in ctx

    def test_truncates_long_errors(self):
        long_error = "x" * 1000
        ctx = _build_failure_context("seg", "prompt", [long_error])
        assert len(long_error) > 500
        assert "x" * 500 in ctx
        assert "x" * 501 not in ctx


class TestBuildMetaPrompt:
    def test_includes_experiment_count(self):
        prompt = _build_meta_prompt("seg", 4, "failure context")
        assert "4" in prompt
        assert "APPROACH 1" in prompt
        assert f"APPROACH 4" in prompt

    def test_includes_failure_context(self):
        prompt = _build_meta_prompt("seg", 3, "Module not found error details")
        assert "Module not found" in prompt
