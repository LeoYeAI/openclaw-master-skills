from __future__ import annotations

import asyncio
import logging
import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from ..agent import record_agent_usage, run_agent
from ..budget import BudgetTracker
from ..config import ShipLoopConfig
from ..git_ops import (
    create_worktree,
    get_diff,
    remove_worktree,
)
from ..learnings import LearningsEngine
from ..preflight import run_preflight
from ..reporting import Reporter

logger = logging.getLogger("shiploop.loop.optimize")

VARIATION_MARKER_PATTERN = re.compile(
    r"---\s*VARIATION\s+(\d+)\s*---\s*\n(.*?)(?=---\s*VARIATION\s+\d+\s*---|$)",
    re.DOTALL | re.IGNORECASE,
)

TYPE_LINE_PATTERN = re.compile(
    r"^<type>\s*:\s*(.+)$", re.MULTILINE,
)


@dataclass
class OptimizationResult:
    ran: bool
    experiments_tried: int = 0
    winner: int | None = None
    prompt_delta: str = ""
    improvement_type: str = ""


@dataclass
class _VariationCandidate:
    variation_num: int
    improvement_type: str
    modified_prompt: str


@dataclass
class _ExperimentOutcome:
    variation_num: int
    passed: bool
    diff_lines: int = 999
    improvement_type: str = ""


def should_optimize(
    config: ShipLoopConfig,
    repair_attempts: int,
    repair_diff_lines: int,
) -> tuple[bool, str]:
    opt_config = config.optimization

    if not opt_config.enabled:
        return False, "optimization disabled"

    is_trivial = repair_attempts <= 1 and repair_diff_lines < opt_config.min_repair_diff_lines
    if is_trivial:
        return False, f"trivial repair ({repair_attempts} attempt, {repair_diff_lines} diff lines)"

    return True, ""


async def run_optimization_loop(
    config: ShipLoopConfig,
    segment_name: str,
    original_prompt: str,
    preflight_error: str,
    repair_diff: str,
    repair_attempts: int,
    repair_diff_lines: int,
    reporter: Reporter,
    budget: BudgetTracker,
    learnings: LearningsEngine,
) -> OptimizationResult:
    repo = Path(config.repo)
    opt_config = config.optimization

    eligible, skip_reason = should_optimize(config, repair_attempts, repair_diff_lines)
    if not eligible:
        reporter.optimization_skipped(segment_name, skip_reason)
        return OptimizationResult(ran=False)

    if not budget.check_optimization_budget(segment_name):
        reporter.optimization_skipped(segment_name, "optimization budget exceeded")
        return OptimizationResult(ran=False)

    existing_optimizations = [
        l for l in learnings.learnings
        if l.segment == segment_name and l.learning_type == "optimization"
    ]
    if existing_optimizations:
        reporter.optimization_skipped(segment_name, "optimization already recorded")
        return OptimizationResult(ran=False)

    reporter.optimization_start(segment_name)

    analysis_prompt = _build_analysis_prompt(
        segment_name, original_prompt, preflight_error, repair_diff, opt_config.max_experiments,
    )

    analysis_result = await run_agent(
        config.agent_command, analysis_prompt, repo,
        timeout=config.timeouts.agent, segment=segment_name,
    )
    record_agent_usage(budget, segment_name, "optimize-analysis", analysis_result)

    if not analysis_result.success:
        reporter.optimization_result(segment_name, {"winner": None})
        return OptimizationResult(ran=True)

    variations = parse_variations(analysis_result.output, opt_config.max_experiments)

    if not variations:
        reporter.optimization_result(segment_name, {"winner": None})
        return OptimizationResult(ran=True)

    outcomes: list[_ExperimentOutcome] = []

    for variation in variations:
        if not budget.check_optimization_budget(segment_name):
            break

        outcome = await _run_experiment(
            config, segment_name, variation, repo, budget,
        )
        outcomes.append(outcome)

    result = _evaluate_outcomes(outcomes, variations)
    result.ran = True
    result.experiments_tried = len(outcomes)

    if result.winner is not None:
        learnings.record(
            segment=segment_name,
            failure=f"Repair required: {preflight_error[:200]}",
            root_cause=f"Original prompt lacked: {result.improvement_type}",
            fix=result.prompt_delta[:500],
            tags=["optimization", "prompt", result.improvement_type],
        )
        last_learning = learnings.learnings[-1]
        last_learning.learning_type = "optimization"
        last_learning.improvement_type = result.improvement_type
        last_learning.prompt_delta = result.prompt_delta[:500]
        learnings._save()

    reporter.optimization_result(segment_name, {
        "winner": result.winner,
        "improvement_type": result.improvement_type,
    })

    return result


async def _run_experiment(
    config: ShipLoopConfig,
    segment_name: str,
    variation: _VariationCandidate,
    repo: Path,
    budget: BudgetTracker,
) -> _ExperimentOutcome:
    worktree_path = Path(tempfile.mkdtemp(
        prefix=f"shiploop-opt-{segment_name}-{variation.variation_num}-",
    ))
    branch_name = f"optimize/{segment_name}-{variation.variation_num}"

    try:
        await create_worktree(repo, branch_name, worktree_path)

        agent_result = await run_agent(
            config.agent_command, variation.modified_prompt, worktree_path,
            timeout=config.timeouts.agent, segment=segment_name,
        )
        record_agent_usage(
            budget, segment_name,
            f"optimize-exp-{variation.variation_num}",
            agent_result,
        )

        if not agent_result.success:
            return _ExperimentOutcome(
                variation_num=variation.variation_num,
                passed=False,
                improvement_type=variation.improvement_type,
            )

        preflight_result = await run_preflight(
            config.preflight, worktree_path,
            timeout=config.timeouts.preflight,
        )

        if preflight_result.passed:
            diff_lines = await _count_diff_lines(worktree_path)
            return _ExperimentOutcome(
                variation_num=variation.variation_num,
                passed=True,
                diff_lines=diff_lines,
                improvement_type=variation.improvement_type,
            )

        return _ExperimentOutcome(
            variation_num=variation.variation_num,
            passed=False,
            improvement_type=variation.improvement_type,
        )

    except Exception as e:
        logger.error("Optimization experiment %d error: %s", variation.variation_num, e)
        return _ExperimentOutcome(
            variation_num=variation.variation_num,
            passed=False,
            improvement_type=variation.improvement_type,
        )
    finally:
        await remove_worktree(repo, worktree_path)
        from ..git_ops import delete_branch
        await delete_branch(repo, branch_name)


def _evaluate_outcomes(
    outcomes: list[_ExperimentOutcome],
    variations: list[_VariationCandidate],
) -> OptimizationResult:
    passing = [o for o in outcomes if o.passed]

    if not passing:
        return OptimizationResult(ran=True, experiments_tried=len(outcomes))

    passing.sort(key=lambda o: o.diff_lines)
    winner = passing[0]

    variation_map = {v.variation_num: v for v in variations}
    winning_variation = variation_map.get(winner.variation_num)

    return OptimizationResult(
        ran=True,
        experiments_tried=len(outcomes),
        winner=winner.variation_num,
        prompt_delta=winning_variation.modified_prompt if winning_variation else "",
        improvement_type=winner.improvement_type,
    )


def parse_variations(
    analysis_output: str,
    expected_count: int,
) -> list[_VariationCandidate]:
    variations: list[_VariationCandidate] = []

    for match in VARIATION_MARKER_PATTERN.finditer(analysis_output):
        variation_num = int(match.group(1))
        body = match.group(2).strip()

        improvement_type = "prompt_structure"
        type_match = TYPE_LINE_PATTERN.search(body)
        if type_match:
            raw_type = type_match.group(1).strip()
            if raw_type in ("prompt_structure", "context_injection", "preflight_hints", "skill_addition"):
                improvement_type = raw_type
            body = TYPE_LINE_PATTERN.sub("", body).strip()

        if body:
            variations.append(_VariationCandidate(
                variation_num=variation_num,
                improvement_type=improvement_type,
                modified_prompt=body,
            ))

    return variations[:expected_count]


def _build_analysis_prompt(
    segment_name: str,
    original_prompt: str,
    preflight_error: str,
    repair_diff: str,
    num_variations: int,
) -> str:
    truncated_error = preflight_error[:500] if len(preflight_error) > 500 else preflight_error
    truncated_diff = repair_diff[:500] if len(repair_diff) > 500 else repair_diff

    return f"""## OPTIMIZATION ANALYSIS for segment: {segment_name}

The segment shipped successfully, but only after repair. Your job is to figure out what
modifications to the ORIGINAL PROMPT would have produced correct code on the first try.

### Original Prompt
{original_prompt}

### Preflight Error (what broke)
```
{truncated_error}
```

### Repair Diff (what the repair changed)
```
{truncated_diff}
```

### Instructions

Generate {num_variations} prompt variations, each taking a different optimization approach.
For each variation, specify the type and provide the modified prompt.

Output format (exactly):

---VARIATION 1---
<type>: prompt_structure | context_injection | preflight_hints | skill_addition
<modified prompt that would have worked on the first try>

---VARIATION 2---
<type>: prompt_structure | context_injection | preflight_hints | skill_addition
<modified prompt that would have worked on the first try>

Focus on concrete, actionable changes — not vague suggestions. The modified prompt should
be the COMPLETE prompt you'd give the agent, not just the delta.
"""


async def _count_diff_lines(cwd: Path) -> int:
    proc = await asyncio.create_subprocess_exec(
        "git", "diff", "--stat", "HEAD~1",
        cwd=cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    lines = stdout.decode().strip().splitlines()
    return len(lines) if lines else 999
