from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from pathlib import Path

from ..agent import record_agent_usage, run_agent
from ..budget import BudgetTracker
from ..config import ShipLoopConfig
from ..learnings import LearningsEngine
from ..preflight import PreflightResult, run_preflight
from ..reporting import Reporter

logger = logging.getLogger("shiploop.loop.repair")


@dataclass
class RepairResult:
    success: bool
    attempts_used: int = 0
    converged: bool = False


async def run_repair_loop(
    config: ShipLoopConfig,
    segment_name: str,
    initial_preflight: PreflightResult,
    reporter: Reporter,
    budget: BudgetTracker,
    learnings: LearningsEngine,
    run_id: str | None = None,
) -> RepairResult:
    repo = Path(config.repo)
    max_attempts = config.repair.max_attempts
    error_signatures: list[str] = []
    last_preflight = initial_preflight

    for attempt in range(1, max_attempts + 1):
        reporter.repair_attempt(segment_name, attempt, max_attempts)

        error_sig = _compute_error_signature(last_preflight.combined_output)
        error_signatures.append(error_sig)

        if len(error_signatures) >= 2 and error_signatures[-1] == error_signatures[-2]:
            reporter._print("   ⚠️  Convergence detected: same error twice in a row")
            return RepairResult(success=False, attempts_used=attempt, converged=True)

        if not budget.check_budget(segment_name):
            reporter.budget_halt(
                segment_name,
                budget.get_segment_cost(segment_name),
                config.budget.max_usd_per_segment,
            )
            return RepairResult(success=False, attempts_used=attempt)

        repair_prompt = _build_repair_prompt(
            segment_name, attempt, last_preflight, repo,
        )

        agent_result = await run_agent(
            config.agent_command, repair_prompt, repo,
            timeout=config.timeouts.agent, segment=segment_name,
        )
        record_agent_usage(budget, segment_name, f"repair-{attempt}", agent_result)

        if not agent_result.success:
            reporter.repair_failure(segment_name, attempt, f"Agent failed: {agent_result.error[:100]}")
            # Check if this is a case the system didn't know how to handle
            if "unhandled" in agent_result.error.lower() or attempt == max_attempts:
                learnings.record_decision_gap(
                    segment=segment_name,
                    context=f"Repair agent failed on attempt {attempt}: {agent_result.error[:300]}",
                    verdict="repair_agent_failed",
                    run_id=run_id,
                )
            continue

        preflight_result = await run_preflight(
            config.preflight, repo, timeout=config.timeouts.preflight,
        )

        if preflight_result.passed:
            reporter.repair_success(segment_name, attempt)

            _record_repair_learning(
                learnings, segment_name, last_preflight, attempt,
            )
            return RepairResult(success=True, attempts_used=attempt)

        error_matches_known = _check_matches_known_learning(learnings, preflight_result.combined_output)
        if not error_matches_known and attempt == max_attempts:
            # Emit MISSING_DECISION_BRANCH: repair failed with an unknown error
            learnings.record_decision_gap(
                segment=segment_name,
                context=f"Repair exhausted with unmatched error: {preflight_result.combined_output[:500]}",
                verdict="repair_exhausted_unknown_error",
                run_id=run_id,
            )

        reporter.repair_failure(segment_name, attempt, preflight_result.errors[0] if preflight_result.errors else "unknown")
        last_preflight = preflight_result

    return RepairResult(success=False, attempts_used=max_attempts)


def _compute_error_signature(error_text: str) -> str:
    lines = error_text.strip().splitlines()[:5]
    content = "\n".join(lines)
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def _build_repair_prompt(
    segment_name: str,
    attempt: int,
    preflight: PreflightResult,
    repo: Path,
) -> str:
    error_output = preflight.combined_output
    last_lines = "\n".join(error_output.splitlines()[-100:]) if error_output else "(no output)"

    return f"""## REPAIR ATTEMPT {attempt} for segment: {segment_name}

The previous attempt to implement this segment failed. Your job is to FIX the issues
so the code builds, lints, and tests cleanly.

### Failed Step
{preflight.failed_step}

### Error Output
```
{last_lines}
```

### Instructions
1. Read the error output carefully
2. Identify the root cause
3. Fix the code — do NOT start over from scratch unless the approach is fundamentally broken
4. Ensure the project builds, lints, and tests pass
5. Do NOT remove or disable tests to make them pass
"""


def _check_matches_known_learning(learnings: LearningsEngine, error_text: str) -> bool:
    """Return True if this error matches any known learning (so we know how to handle it)."""
    if not error_text:
        return False
    results = learnings.search(error_text[:300], max_results=1)
    return len(results) > 0


def _record_repair_learning(
    learnings: LearningsEngine,
    segment_name: str,
    failed_preflight: PreflightResult,
    attempt: int,
) -> None:
    error_summary = failed_preflight.errors[0] if failed_preflight.errors else "unknown error"
    learnings.record(
        segment=segment_name,
        failure=error_summary,
        root_cause=f"Fixed by repair loop attempt {attempt}",
        fix=f"Repair agent auto-fixed on attempt {attempt}",
        tags=["repair", f"attempt-{attempt}"],
    )
