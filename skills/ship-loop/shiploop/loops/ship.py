from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from pathlib import Path

from ..agent import AgentResult, record_agent_usage, run_agent
from ..budget import BudgetTracker
from ..config import DeployConfig, SegmentConfig, ShipLoopConfig
from ..git_ops import get_changed_files
from ..learnings import LearningsEngine
from ..preflight import PreflightResult, run_preflight
from ..reporting import Reporter, SegmentReport
from ..ship_utils import ship_and_verify

logger = logging.getLogger("shiploop.loop.ship")


@dataclass
class ShipResult:
    success: bool
    commit_sha: str = ""
    tag: str = ""
    deploy_url: str = ""
    report: SegmentReport | None = None
    preflight_result: PreflightResult | None = None
    injected_learning_ids: list[str] | None = None


async def run_ship_loop(
    config: ShipLoopConfig,
    segment: SegmentConfig,
    segment_index: int,
    reporter: Reporter,
    budget: BudgetTracker,
    learnings: LearningsEngine,
) -> ShipResult:
    repo = Path(config.repo)
    report = SegmentReport(name=segment.name, status="running")
    loop_start = time.monotonic()

    relevant_learnings = learnings.search(segment.prompt)
    injected_learning_ids = [l.id for l in relevant_learnings]
    learnings_prefix = learnings.format_for_prompt(relevant_learnings)

    augmented_prompt = segment.prompt
    if learnings_prefix:
        augmented_prompt = learnings_prefix + "\n---\n\n" + segment.prompt
        reporter._print(f"   📚 Loaded {len(relevant_learnings)} relevant learning(s)")
    else:
        reporter._print("   📚 No prior learnings")

    reporter.segment_phase(segment.name, "coding")

    if not budget.check_budget(segment.name):
        reporter.budget_halt(segment.name, budget.get_segment_cost(segment.name), config.budget.max_usd_per_segment)
        report.status = "failed"
        report.errors.append("Budget exceeded before coding")
        report.duration_seconds = time.monotonic() - loop_start
        return ShipResult(success=False, report=report)

    agent_result = await run_agent(
        config.agent_command, augmented_prompt, repo,
        timeout=config.timeouts.agent, segment=segment.name,
    )
    record_agent_usage(budget, segment.name, "ship", agent_result)

    if not agent_result.success:
        report.status = "failed"
        report.errors.append(f"Agent failed: {agent_result.error[:200]}")
        report.duration_seconds = time.monotonic() - loop_start
        return ShipResult(success=False, report=report)

    reporter._print(f"   ✅ Agent completed in {agent_result.duration:.0f}s")

    changed_after_agent = await get_changed_files(repo)
    if not changed_after_agent:
        report.status = "failed"
        report.errors.append(
            "Agent completed but produced no file changes. "
            "The agent may have hallucinated or misunderstood the task."
        )
        report.duration_seconds = time.monotonic() - loop_start
        return ShipResult(success=False, report=report)

    reporter.segment_phase(segment.name, "preflight")
    preflight_result = await run_preflight(
        config.preflight, repo, timeout=config.timeouts.preflight,
    )

    if not preflight_result.passed:
        report.duration_seconds = time.monotonic() - loop_start
        return ShipResult(success=False, report=report, preflight_result=preflight_result)

    reporter._print("   ✅ Preflight passed")

    sv_result = await ship_and_verify(config, segment, repo, reporter)
    if not sv_result.success:
        report.status = "failed"
        report.errors.append(f"Ship failed: {sv_result.error}")
        report.duration_seconds = time.monotonic() - loop_start
        return ShipResult(
            success=False,
            commit_sha=sv_result.commit_sha,
            tag=sv_result.tag,
            report=report,
        )

    report.status = "shipped"
    report.commit = sv_result.commit_sha
    report.tag = sv_result.tag
    report.deploy_url = sv_result.deploy_url
    report.cost_usd = budget.get_segment_cost(segment.name)
    report.duration_seconds = time.monotonic() - loop_start

    # Score learnings: segment shipped first-try → bump scores
    if injected_learning_ids:
        learnings.on_segment_success(injected_learning_ids)

    return ShipResult(
        success=True,
        commit_sha=sv_result.commit_sha,
        tag=sv_result.tag,
        deploy_url=sv_result.deploy_url,
        report=report,
        injected_learning_ids=injected_learning_ids,
    )
