import hashlib

from shiploop.loops.repair import _build_repair_prompt, _compute_error_signature
from shiploop.preflight import PreflightResult


class TestConvergenceDetection:
    def test_same_error_produces_same_signature(self):
        error = "error: Cannot find module './Foo'\nerror: Build failed\nexit 1"
        sig1 = _compute_error_signature(error)
        sig2 = _compute_error_signature(error)
        assert sig1 == sig2

    def test_same_first_five_lines_converges(self):
        error_a = "line1\nline2\nline3\nline4\nline5\nextraA\nmore_a"
        error_b = "line1\nline2\nline3\nline4\nline5\nextraB\nmore_b"
        assert _compute_error_signature(error_a) == _compute_error_signature(error_b)

    def test_different_errors_do_not_converge(self):
        error_a = "TypeError: undefined is not a function"
        error_b = "SyntaxError: unexpected token"
        assert _compute_error_signature(error_a) != _compute_error_signature(error_b)

    def test_empty_error_text(self):
        sig = _compute_error_signature("")
        assert isinstance(sig, str)
        assert len(sig) == 16

    def test_signature_is_hex_substring(self):
        sig = _compute_error_signature("some error text")
        assert len(sig) == 16
        int(sig, 16)


class TestRepairPrompt:
    def test_includes_error_output(self):
        preflight = PreflightResult(
            passed=False,
            build_output="ERROR: module not found\nstack trace line 1\nstack trace line 2",
            failed_step="build",
            errors=["build failed (exit 1)"],
        )
        prompt = _build_repair_prompt("dark-mode", 1, preflight, None)
        assert "module not found" in prompt
        assert "stack trace" in prompt

    def test_includes_failed_step(self):
        preflight = PreflightResult(
            passed=False,
            test_output="FAIL src/test.ts",
            failed_step="test",
            errors=["test failed (exit 1)"],
        )
        prompt = _build_repair_prompt("auth", 2, preflight, None)
        assert "test" in prompt
        assert "REPAIR ATTEMPT 2" in prompt
        assert "auth" in prompt

    def test_includes_segment_name_and_attempt(self):
        preflight = PreflightResult(
            passed=False, lint_output="lint error", failed_step="lint",
            errors=["lint failed"],
        )
        prompt = _build_repair_prompt("contact-form", 3, preflight, None)
        assert "contact-form" in prompt
        assert "REPAIR ATTEMPT 3" in prompt

    def test_truncates_long_output(self):
        long_output = "error line\n" * 200
        preflight = PreflightResult(
            passed=False, build_output=long_output, failed_step="build",
            errors=["build failed"],
        )
        prompt = _build_repair_prompt("seg", 1, preflight, None)
        prompt_lines = prompt.splitlines()
        assert len(prompt_lines) < 200
