from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

import pytest

from shiploop.config import PreflightConfig
from shiploop.preflight import PreflightResult, run_preflight


class TestPreflightResult:
    def test_combined_output_empty_when_no_output(self):
        result = PreflightResult(passed=True)
        assert result.combined_output == ""

    def test_combined_output_includes_all_sections(self):
        result = PreflightResult(
            passed=True,
            build_output="build ok",
            lint_output="lint ok",
            test_output="test ok",
        )
        output = result.combined_output
        assert "=== BUILD ===" in output
        assert "=== LINT ===" in output
        assert "=== TEST ===" in output

    def test_combined_output_partial_sections(self):
        result = PreflightResult(passed=False, build_output="error", failed_step="build")
        output = result.combined_output
        assert "=== BUILD ===" in output
        assert "=== LINT ===" not in output


class TestRunPreflight:
    @pytest.mark.asyncio
    async def test_all_steps_pass(self, tmp_path):
        config = PreflightConfig(build="true", lint="true", test="true")
        result = await run_preflight(config, tmp_path)
        assert result.passed is True
        assert result.failed_step == ""

    @pytest.mark.asyncio
    async def test_build_failure_stops_early(self, tmp_path):
        config = PreflightConfig(build="false", lint="true", test="true")
        result = await run_preflight(config, tmp_path)
        assert result.passed is False
        assert result.failed_step == "build"
        assert result.lint_output == ""

    @pytest.mark.asyncio
    async def test_lint_failure(self, tmp_path):
        config = PreflightConfig(build="true", lint="false", test="true")
        result = await run_preflight(config, tmp_path)
        assert result.passed is False
        assert result.failed_step == "lint"

    @pytest.mark.asyncio
    async def test_test_failure(self, tmp_path):
        config = PreflightConfig(build="true", lint="true", test="false")
        result = await run_preflight(config, tmp_path)
        assert result.passed is False
        assert result.failed_step == "test"

    @pytest.mark.asyncio
    async def test_skips_none_steps(self, tmp_path):
        config = PreflightConfig(build=None, lint=None, test="true")
        result = await run_preflight(config, tmp_path)
        assert result.passed is True
        assert result.build_output == ""

    @pytest.mark.asyncio
    async def test_timeout(self, tmp_path):
        config = PreflightConfig(build="sleep 10")
        result = await run_preflight(config, tmp_path, timeout=1)
        assert result.passed is False
        assert "timed out" in result.errors[0]

    @pytest.mark.asyncio
    async def test_captures_stdout(self, tmp_path):
        config = PreflightConfig(build="echo BUILD_OUTPUT")
        result = await run_preflight(config, tmp_path)
        assert result.passed is True
        assert "BUILD_OUTPUT" in result.build_output
