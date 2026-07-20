from __future__ import annotations

import asyncio
import logging
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path

from ..agent import record_agent_usage, run_agent
from ..budget import BudgetTracker
from ..config import ShipLoopConfig
from ..learnings import LearningsEngine
from ..preflight import run_preflight
from ..reporting import Reporter
from ..git_ops import (
    checkout,
    create_worktree,
    delete_branch,
    discard_changes,
    get_current_branch,
    merge_branch,
    remove_worktree,
)

logger = logging.getLogger("shiploop.loop.meta")


@dataclass
class MetaResult:
    success: bool
    winner_experiment: int | None = None
    winner_branch: str = ""
    experiments_tried: int = 0


async def run_meta_loop(
    config: ShipLoopConfig,
    segment_name: str,
    segment_prompt: str,
    all_errors: list[str],
    reporter: Reporter,
    budget: BudgetTracker,
    learnings: LearningsEngine,
) -> MetaResult:
    repo = Path(config.repo)
    meta_config = config.meta
    num_experiments = meta_config.experiments

    if not meta_config.enabled:
        reporter._print("   Meta loop disabled — segment failed")
        return MetaResult(success=False)

    reporter.meta_start()

    await discard_changes(repo)

    original_branch = await get_current_branch(repo)

    reporter.meta_analysis()
    failure_context = _build_failure_context(segment_name, segment_prompt, all_errors)
    meta_prompt = _build_meta_prompt(segment_name, num_experiments, failure_context)

    meta_agent = await run_agent(
        config.agent_command, meta_prompt, repo,
        timeout=config.timeouts.agent, segment=segment_name,
    )
    record_agent_usage(budget, segment_name, "meta-analysis", meta_agent)

    if not meta_agent.success:
        reporter._print("   ❌ Meta-analysis agent failed")
        return MetaResult(success=False)

    reporter._print("   ✅ Meta-analysis complete")

    experiment_prompts = _parse_experiments(meta_agent.output, num_experiments, segment_prompt, failure_context)

    candidates: list[tuple[int, int]] = []

    for exp_num in range(1, num_experiments + 1):
        reporter.experiment_start(exp_num, num_experiments)

        if not budget.check_budget(segment_name):
            reporter.budget_halt(
                segment_name,
                budget.get_segment_cost(segment_name),
                config.budget.max_usd_per_segment,
            )
            break

        exp_prompt = experiment_prompts.get(exp_num, "")
        if not exp_prompt:
            reporter._print(f"   ⚠️  No prompt for experiment {exp_num}, skipping")
            continue

        branch_name = f"experiment/{segment_name}-{exp_num}"
        worktree_path = Path(tempfile.mkdtemp(prefix=f"shiploop-exp-{segment_name}-{exp_num}-"))

        try:
            await create_worktree(repo, branch_name, worktree_path)

            agent_result = await run_agent(
                config.agent_command, exp_prompt, worktree_path,
                timeout=config.timeouts.agent, segment=segment_name,
            )
            record_agent_usage(budget, segment_name, f"experiment-{exp_num}", agent_result)

            if not agent_result.success:
                reporter.experiment_result(exp_num, False)
                continue

            preflight_result = await run_preflight(
                config.preflight, worktree_path,
                timeout=config.timeouts.preflight,
            )

            if preflight_result.passed:
                diff_lines = await _count_diff_lines(worktree_path)
                candidates.append((exp_num, diff_lines))
                reporter.experiment_result(exp_num, True, diff_lines)
            else:
                reporter.experiment_result(exp_num, False)

        except Exception as e:
            logger.error("Experiment %d error: %s", exp_num, e)
            reporter.experiment_result(exp_num, False)
        finally:
            await remove_worktree(repo, worktree_path)

    await checkout(repo, original_branch)

    if not candidates:
        reporter._print(f"\n   ❌ ALL {num_experiments} experiments failed — segment failed")

        error_summary = "; ".join(
            err[:100] for err in all_errors[:3]
        ) if all_errors else "no error details captured"

        learnings.record(
            segment=segment_name,
            failure=f"All {num_experiments} repair and meta-experiment attempts failed. Errors: {error_summary}"[:500],
            root_cause=f"Failure context: {failure_context[:300]}",
            fix="No automated fix found — task may need decomposition or human intervention",
            tags=["meta-failure", "needs-human"],
        )

        for exp_num in range(1, num_experiments + 1):
            await delete_branch(repo, f"experiment/{segment_name}-{exp_num}")

        return MetaResult(success=False, experiments_tried=num_experiments)

    candidates.sort(key=lambda x: x[1])
    winner_num, winner_diff = candidates[0]
    winner_branch = f"experiment/{segment_name}-{winner_num}"

    reporter.experiment_winner(winner_num, winner_branch)

    merged = await merge_branch(
        repo, winner_branch,
        f"feat(shiploop): {segment_name} via meta-experiment {winner_num}",
    )

    if not merged:
        reporter._print(f"   ❌ Merge conflict — winner branch preserved: {winner_branch}")
        return MetaResult(success=False, winner_experiment=winner_num, experiments_tried=num_experiments)

    learnings.record(
        segment=segment_name,
        failure=f"Repair loop exhausted",
        root_cause="Required meta-analysis and experiment branching",
        fix=f"Experiment {winner_num} succeeded with alternative approach",
        tags=["meta-success", f"experiment-{winner_num}"],
    )

    for exp_num in range(1, num_experiments + 1):
        await delete_branch(repo, f"experiment/{segment_name}-{exp_num}")

    reporter._print("   ✅ Winner merged, experiment branches cleaned")

    return MetaResult(
        success=True,
        winner_experiment=winner_num,
        winner_branch=winner_branch,
        experiments_tried=num_experiments,
    )


# Emitted events for meta loop visibility (used by orchestrator event queue):
# - "meta_analysis_complete": after meta-analysis agent finishes
# - "experiment_passed": when an experiment passes preflight
# - "meta_done": when winner is merged (emitted by orchestrator)



def _build_failure_context(segment_name: str, prompt: str, all_errors: list[str]) -> str:
    lines = [
        f"# Failure History for: {segment_name}",
        "",
        "## Original Prompt",
        prompt,
        "",
        "## Error History from All Attempts",
    ]
    for i, error in enumerate(all_errors, 1):
        truncated = error[:500] if len(error) > 500 else error
        lines.append(f"\n### Attempt {i}")
        lines.append(f"```\n{truncated}\n```")
    return "\n".join(lines)


def _build_meta_prompt(segment_name: str, num_experiments: int, failure_context: str) -> str:
    return f"""## META-ANALYSIS: Why does segment "{segment_name}" keep failing?

All repair attempts failed. Analyze the failure history below and:

1. Identify the ROOT CAUSE — not the symptom, the underlying issue
2. Propose {num_experiments} different approaches to solve this, each fundamentally different
3. For each approach, write a COMPLETE implementation prompt

Output format (exactly):
---APPROACH 1---
<complete prompt for approach 1>
---APPROACH 2---
<complete prompt for approach 2>
---APPROACH {num_experiments}---
<complete prompt for approach {num_experiments}>

{failure_context}
"""


def _parse_experiments(
    meta_output: str,
    num_experiments: int,
    original_prompt: str,
    failure_context: str,
) -> dict[int, str]:
    experiments: dict[int, str] = {}

    for exp_num in range(1, num_experiments + 1):
        pattern = rf"---\s*APPROACH\s+{exp_num}\s*---\s*\n(.*?)(?=---\s*APPROACH\s+\d+\s*---|$)"
        match = re.search(pattern, meta_output, re.DOTALL | re.IGNORECASE)

        if match:
            prompt_text = match.group(1).strip()
            prompt_text = re.sub(r"^```\s*\n?|```\s*$", "", prompt_text).strip()
            if prompt_text:
                experiments[exp_num] = prompt_text
                continue

        experiments[exp_num] = f"""## Alternative approach {exp_num}

The standard approach failed multiple times. Try a fundamentally different strategy.

Original task:
{original_prompt}

Previous failures (summary):
{failure_context[-500:]}

Use approach {exp_num}: try a fundamentally different implementation strategy.
"""

    return experiments


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
