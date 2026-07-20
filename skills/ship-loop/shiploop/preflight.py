from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from pathlib import Path

from .config import PreflightConfig

logger = logging.getLogger("shiploop.preflight")


@dataclass
class PreflightResult:
    passed: bool
    build_output: str = ""
    lint_output: str = ""
    test_output: str = ""
    failed_step: str = ""
    errors: list[str] = field(default_factory=list)

    @property
    def combined_output(self) -> str:
        parts = []
        if self.build_output:
            parts.append(f"=== BUILD ===\n{self.build_output}")
        if self.lint_output:
            parts.append(f"=== LINT ===\n{self.lint_output}")
        if self.test_output:
            parts.append(f"=== TEST ===\n{self.test_output}")
        return "\n\n".join(parts)


async def run_preflight(config: PreflightConfig, cwd: Path, timeout: int = 300) -> PreflightResult:
    result = PreflightResult(passed=True)

    steps = [
        ("build", config.build),
        ("lint", config.lint),
        ("test", config.test),
    ]

    for step_name, command in steps:
        if not command:
            continue

        logger.info("Running %s: %s", step_name, command)
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            output = stdout.decode(errors="replace")

            setattr(result, f"{step_name}_output", output)

            if proc.returncode != 0:
                result.passed = False
                result.failed_step = step_name
                result.errors.append(f"{step_name} failed (exit {proc.returncode})")
                logger.warning("%s failed (exit %d)", step_name, proc.returncode)
                return result

            logger.info("%s passed", step_name)

        except asyncio.TimeoutError:
            result.passed = False
            result.failed_step = step_name
            result.errors.append(f"{step_name} timed out after {timeout}s")
            return result

    return result
