from __future__ import annotations

import asyncio
import tempfile
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import yaml

from shiploop.agent import AgentResult
from shiploop.config import SegmentStatus, load_config, save_config
from shiploop.loops.ship import ShipResult
from shiploop.orchestrator import Orchestrator
from shiploop.preflight import PreflightResult
from shiploop.providers.base import VerificationResult
from shiploop.reporting import SegmentReport


def _make_config(segments, repo_path="/tmp/test-repo"):
    return {
        "project": "IntegrationTest",
        "repo": repo_path,
        "site": "https://example.com",
        "agent_command": "echo test",
        "preflight": {"build": "echo build", "lint": "echo lint", "test": "echo test"},
        "deploy": {"provider": "custom", "script": "echo ok"},
        "repair": {"max_attempts": 2},
        "meta": {"enabled": True, "experiments": 2},
        "budget": {"max_usd_per_segment": 100.0, "max_usd_per_run": 500.0},
        "segments": segments,
    }


@pytest.fixture
def config_with_deps():
    data = _make_config([
        {"name": "seg-a", "prompt": "Build feature A", "depends_on": []},
        {"name": "seg-b", "prompt": "Build feature B", "depends_on": ["seg-a"]},
    ])
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        yaml.dump(data, f)
        path = Path(f.name)
    yield path
    path.unlink(missing_ok=True)


@pytest.fixture
def config_single():
    data = _make_config([
        {"name": "seg-1", "prompt": "Build something", "depends_on": []},
    ])
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        yaml.dump(data, f)
        path = Path(f.name)
    yield path
    path.unlink(missing_ok=True)


def _agent_success(output="done"):
    return AgentResult(success=True, output=output, duration=5.0)


def _agent_failure(error="Agent failed"):
    return AgentResult(success=False, output="", error=error, duration=2.0)


def _preflight_pass():
    return PreflightResult(passed=True, build_output="ok", lint_output="ok", test_output="ok")


def _preflight_fail(step="build", error="build error"):
    return PreflightResult(
        passed=False, build_output=error, failed_step=step,
        errors=[f"{step} failed (exit 1)"],
    )


def _verify_success():
    return VerificationResult(success=True, deploy_url="https://example.com", details="OK")


def _verify_failure():
    return VerificationResult(success=False, details="Deploy failed")


def _orch_lock_patches():
    return [
        patch("shiploop.orchestrator.Orchestrator._acquire_lock"),
        patch("shiploop.orchestrator.Orchestrator._release_lock"),
        patch("shiploop.orchestrator.Orchestrator._install_signal_handlers"),
        patch("shiploop.orchestrator.Orchestrator._cleanup_orphaned_worktrees"),
    ]


def _ship_git_patches():
    return [
        patch("shiploop.ship_utils.get_changed_files", new_callable=AsyncMock, return_value=["src/main.py"]),
        patch("shiploop.ship_utils.security_scan", return_value=(["src/main.py"], [])),
        patch("shiploop.ship_utils.stage_files", new_callable=AsyncMock),
        patch("shiploop.ship_utils.commit", new_callable=AsyncMock, return_value="abc123"),
        patch("shiploop.ship_utils.create_tag", new_callable=AsyncMock, return_value="shiploop/seg/tag"),
        patch("shiploop.ship_utils.push", new_callable=AsyncMock),
        patch("shiploop.ship_utils.get_short_sha", new_callable=AsyncMock, return_value="abc123"),
        patch("shiploop.ship_utils.verify_deployment", new_callable=AsyncMock, return_value=_verify_success()),
    ]


def _apply_patches(stack, patch_list):
    for p in patch_list:
        stack.enter_context(p)


class TestHappyPath:
    @pytest.mark.asyncio
    async def test_two_segments_with_dependency_both_ship(self, config_with_deps):
        with ExitStack() as stack:
            _apply_patches(stack, _orch_lock_patches())
            _apply_patches(stack, _ship_git_patches())
            stack.enter_context(patch("shiploop.loops.ship.run_agent", new_callable=AsyncMock, return_value=_agent_success()))
            stack.enter_context(patch("shiploop.loops.ship.run_preflight", new_callable=AsyncMock, return_value=_preflight_pass()))
            stack.enter_context(patch("shiploop.loops.ship.get_changed_files", new_callable=AsyncMock, return_value=["src/main.py"]))
            stack.enter_context(patch("shiploop.loops.ship.record_agent_usage"))

            orch = Orchestrator(config_with_deps)
            result = await orch._run_pipeline()

        assert result is True
        reloaded = load_config(config_with_deps)
        assert reloaded.segments[0].status == SegmentStatus.SHIPPED
        assert reloaded.segments[1].status == SegmentStatus.SHIPPED


class TestRepairPath:
    @pytest.mark.asyncio
    async def test_preflight_fails_repair_fixes_then_ships(self, config_single):
        call_count = {"preflight": 0}

        async def mock_preflight(*args, **kwargs):
            call_count["preflight"] += 1
            if call_count["preflight"] == 1:
                return _preflight_fail()
            return _preflight_pass()

        with ExitStack() as stack:
            _apply_patches(stack, _orch_lock_patches())
            _apply_patches(stack, _ship_git_patches())
            stack.enter_context(patch("shiploop.loops.ship.run_agent", new_callable=AsyncMock, return_value=_agent_success()))
            stack.enter_context(patch("shiploop.loops.ship.run_preflight", new_callable=AsyncMock, side_effect=mock_preflight))
            stack.enter_context(patch("shiploop.loops.ship.get_changed_files", new_callable=AsyncMock, return_value=["src/main.py"]))
            stack.enter_context(patch("shiploop.loops.ship.record_agent_usage"))
            stack.enter_context(patch("shiploop.loops.repair.run_agent", new_callable=AsyncMock, return_value=_agent_success()))
            stack.enter_context(patch("shiploop.loops.repair.run_preflight", new_callable=AsyncMock, return_value=_preflight_pass()))
            stack.enter_context(patch("shiploop.loops.repair.record_agent_usage"))
            stack.enter_context(patch("shiploop.orchestrator.get_diff", new_callable=AsyncMock, return_value="+fix"))
            stack.enter_context(patch("shiploop.orchestrator.get_diff_stat", new_callable=AsyncMock, return_value="1 file"))
            stack.enter_context(patch("shiploop.loops.optimize.run_agent", new_callable=AsyncMock, return_value=_agent_failure()))
            stack.enter_context(patch("shiploop.loops.optimize.record_agent_usage"))

            orch = Orchestrator(config_single)
            result = await orch._run_pipeline()

        assert result is True


class TestMetaPath:
    @pytest.mark.asyncio
    async def test_repair_exhausted_meta_experiment_succeeds(self, config_single):
        meta_output = "---APPROACH 1---\nTry A\n---APPROACH 2---\nTry B"

        with ExitStack() as stack:
            _apply_patches(stack, _orch_lock_patches())
            _apply_patches(stack, _ship_git_patches())
            stack.enter_context(patch("shiploop.loops.ship.run_agent", new_callable=AsyncMock, return_value=_agent_success()))
            stack.enter_context(patch("shiploop.loops.ship.run_preflight", new_callable=AsyncMock, return_value=_preflight_fail()))
            stack.enter_context(patch("shiploop.loops.ship.get_changed_files", new_callable=AsyncMock, return_value=["src/main.py"]))
            stack.enter_context(patch("shiploop.loops.ship.record_agent_usage"))
            stack.enter_context(patch("shiploop.loops.repair.run_agent", new_callable=AsyncMock, return_value=_agent_success()))
            stack.enter_context(patch("shiploop.loops.repair.run_preflight", new_callable=AsyncMock, return_value=_preflight_fail()))
            stack.enter_context(patch("shiploop.loops.repair.record_agent_usage"))
            stack.enter_context(patch("shiploop.loops.meta.run_agent", new_callable=AsyncMock, return_value=_agent_success(meta_output)))
            stack.enter_context(patch("shiploop.loops.meta.run_preflight", new_callable=AsyncMock, return_value=_preflight_pass()))
            stack.enter_context(patch("shiploop.loops.meta.record_agent_usage"))
            stack.enter_context(patch("shiploop.loops.meta.discard_changes", new_callable=AsyncMock))
            stack.enter_context(patch("shiploop.loops.meta.get_current_branch", new_callable=AsyncMock, return_value="main"))
            stack.enter_context(patch("shiploop.loops.meta.create_worktree", new_callable=AsyncMock))
            stack.enter_context(patch("shiploop.loops.meta.remove_worktree", new_callable=AsyncMock))
            stack.enter_context(patch("shiploop.loops.meta.checkout", new_callable=AsyncMock))
            stack.enter_context(patch("shiploop.loops.meta.merge_branch", new_callable=AsyncMock, return_value=True))
            stack.enter_context(patch("shiploop.loops.meta.delete_branch", new_callable=AsyncMock))
            stack.enter_context(patch("shiploop.loops.meta._count_diff_lines", new_callable=AsyncMock, return_value=5))

            orch = Orchestrator(config_single)
            result = await orch._run_pipeline()

        assert result is True


class TestFailedPath:
    @pytest.mark.asyncio
    async def test_everything_fails_segment_marked_failed(self, config_single):
        meta_output = "---APPROACH 1---\nA\n---APPROACH 2---\nB"

        with ExitStack() as stack:
            _apply_patches(stack, _orch_lock_patches())
            stack.enter_context(patch("shiploop.loops.ship.run_agent", new_callable=AsyncMock, return_value=_agent_success()))
            stack.enter_context(patch("shiploop.loops.ship.run_preflight", new_callable=AsyncMock, return_value=_preflight_fail()))
            stack.enter_context(patch("shiploop.loops.ship.get_changed_files", new_callable=AsyncMock, return_value=["src/main.py"]))
            stack.enter_context(patch("shiploop.loops.ship.record_agent_usage"))
            stack.enter_context(patch("shiploop.loops.repair.run_agent", new_callable=AsyncMock, return_value=_agent_success()))
            stack.enter_context(patch("shiploop.loops.repair.run_preflight", new_callable=AsyncMock, return_value=_preflight_fail()))
            stack.enter_context(patch("shiploop.loops.repair.record_agent_usage"))
            stack.enter_context(patch("shiploop.loops.meta.run_agent", new_callable=AsyncMock, return_value=_agent_success(meta_output)))
            stack.enter_context(patch("shiploop.loops.meta.run_preflight", new_callable=AsyncMock, return_value=_preflight_fail()))
            stack.enter_context(patch("shiploop.loops.meta.record_agent_usage"))
            stack.enter_context(patch("shiploop.loops.meta.discard_changes", new_callable=AsyncMock))
            stack.enter_context(patch("shiploop.loops.meta.get_current_branch", new_callable=AsyncMock, return_value="main"))
            stack.enter_context(patch("shiploop.loops.meta.create_worktree", new_callable=AsyncMock))
            stack.enter_context(patch("shiploop.loops.meta.remove_worktree", new_callable=AsyncMock))
            stack.enter_context(patch("shiploop.loops.meta.checkout", new_callable=AsyncMock))
            stack.enter_context(patch("shiploop.loops.meta.delete_branch", new_callable=AsyncMock))

            orch = Orchestrator(config_single)
            result = await orch._run_pipeline()

        assert result is False
        reloaded = load_config(config_single)
        assert reloaded.segments[0].status == SegmentStatus.FAILED


class TestCrashRecovery:
    def test_active_segment_marked_failed_on_restart(self, config_single):
        orch = Orchestrator(config_single)
        orch.config.segments[0].status = SegmentStatus.CODING
        save_config(orch.config, config_single)

        orch2 = Orchestrator(config_single)
        recovered = orch2._recover_crashed_segments()
        assert "seg-1" in recovered
        assert orch2.config.segments[0].status == SegmentStatus.FAILED

    @pytest.mark.asyncio
    async def test_verifying_segment_gets_re_verification_attempt(self, config_single):
        orch = Orchestrator(config_single)
        orch.config.segments[0].status = SegmentStatus.FAILED
        orch.config.segments[0].commit = "abc123"
        save_config(orch.config, config_single)

        with patch("shiploop.orchestrator.verify_deployment", new_callable=AsyncMock, return_value=_verify_success()):
            orch2 = Orchestrator(config_single)
            re_verified = await orch2._recover_verifying_segments()

        assert "seg-1" in re_verified
        assert orch2.config.segments[0].status == SegmentStatus.SHIPPED
