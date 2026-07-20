from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shiploop.agent import AgentResult, _persist_agent_output, record_agent_usage, run_agent
from shiploop.budget import BudgetConfig, BudgetTracker


@pytest.fixture
def budget_dir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture
def tracker(budget_dir):
    config = BudgetConfig()
    return BudgetTracker(config, budget_dir)


class TestRunAgent:
    @pytest.mark.asyncio
    async def test_successful_agent_run(self, tmp_path):
        result = await run_agent("echo hello", "test prompt", tmp_path)
        assert result.success is True
        assert "hello" in result.output
        assert result.duration > 0

    @pytest.mark.asyncio
    async def test_agent_failure_nonzero_exit(self, tmp_path):
        result = await run_agent("false", "test prompt", tmp_path)
        assert result.success is False
        assert "exited with code" in result.error

    @pytest.mark.asyncio
    async def test_agent_timeout(self, tmp_path):
        result = await run_agent("sleep 10", "test", tmp_path, timeout=1)
        assert result.success is False
        assert "timed out" in result.error

    @pytest.mark.asyncio
    async def test_agent_receives_prompt_via_stdin(self, tmp_path):
        result = await run_agent("cat", "HELLO_FROM_STDIN", tmp_path)
        assert result.success is True
        assert "HELLO_FROM_STDIN" in result.output

    @pytest.mark.asyncio
    async def test_agent_persists_output_when_segment_given(self, tmp_path):
        result = await run_agent("echo logged", "prompt", tmp_path, segment="test-seg")
        assert result.success is True
        log_dir = tmp_path / ".shiploop" / "logs"
        assert log_dir.exists()
        logs = list(log_dir.glob("test-seg-*.log"))
        assert len(logs) == 1
        assert "logged" in logs[0].read_text()


class TestPersistAgentOutput:
    def test_creates_log_file(self, tmp_path):
        _persist_agent_output(tmp_path, "my-seg", "some output")
        log_dir = tmp_path / ".shiploop" / "logs"
        assert log_dir.exists()
        logs = list(log_dir.glob("my-seg-*.log"))
        assert len(logs) == 1
        assert logs[0].read_text() == "some output"

    def test_handles_missing_dir_gracefully(self):
        _persist_agent_output(Path("/nonexistent/path"), "seg", "output")


class TestRecordAgentUsage:
    def test_records_usage_with_parsed_tokens(self, tracker):
        result = AgentResult(
            success=True,
            output="input_tokens: 100\noutput_tokens: 50",
            duration=5.0,
        )
        record_agent_usage(tracker, "seg-1", "ship", result)
        assert tracker.get_segment_cost("seg-1") > 0

    def test_records_usage_with_estimated_tokens(self, tracker):
        result = AgentResult(success=True, output="no token info", duration=10.0)
        record_agent_usage(tracker, "seg-1", "ship", result)
        assert len(tracker.records) == 1
        assert tracker.records[0].tokens_in > 0
