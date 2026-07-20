from __future__ import annotations

import asyncio
import logging
import shlex
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .budget import BudgetTracker, UsageRecord, estimate_cost, estimate_from_prompt, parse_token_usage

logger = logging.getLogger("shiploop.agent")


@dataclass
class AgentResult:
    success: bool
    output: str = ""
    error: str = ""
    duration: float = 0.0


def _ensure_log_dir(cwd: Path) -> Path:
    log_dir = cwd / ".shiploop" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def _persist_agent_output(cwd: Path, segment: str, output: str) -> None:
    try:
        log_dir = _ensure_log_dir(cwd)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        log_file = log_dir / f"{segment}-{timestamp}.log"
        log_file.write_text(output)
        logger.info("Agent output saved to %s", log_file)
    except OSError as e:
        logger.warning("Failed to persist agent output: %s", e)


async def run_agent(
    agent_command: str, prompt: str, cwd: Path, timeout: int = 900,
    segment: str = "",
) -> AgentResult:
    parts = shlex.split(agent_command)
    start = time.monotonic()

    try:
        proc = await asyncio.create_subprocess_exec(
            *parts,
            cwd=cwd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        stdout, _ = await asyncio.wait_for(
            proc.communicate(input=prompt.encode()), timeout=timeout,
        )
        duration = time.monotonic() - start
        output = stdout.decode(errors="replace")

        if segment:
            _persist_agent_output(cwd, segment, output)

        if proc.returncode != 0:
            return AgentResult(
                success=False,
                output=output,
                error=f"Agent exited with code {proc.returncode}",
                duration=duration,
            )
        return AgentResult(success=True, output=output, duration=duration)
    except asyncio.TimeoutError:
        duration = time.monotonic() - start
        try:
            proc.kill()
        except ProcessLookupError:
            pass
        return AgentResult(
            success=False,
            output="",
            error=f"Agent timed out after {timeout}s",
            duration=duration,
        )


def record_agent_usage(
    budget: BudgetTracker,
    segment: str,
    loop: str,
    agent_result: AgentResult,
) -> None:
    tokens_in, tokens_out = parse_token_usage(agent_result.output)
    if tokens_in == 0 and tokens_out == 0:
        tokens_in, tokens_out = estimate_from_prompt(
            len(agent_result.output), agent_result.duration,
        )
    cost = estimate_cost(tokens_in, tokens_out)
    budget.record_usage(UsageRecord(
        segment=segment,
        loop=loop,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        estimated_cost_usd=cost,
        duration_seconds=agent_result.duration,
    ))
