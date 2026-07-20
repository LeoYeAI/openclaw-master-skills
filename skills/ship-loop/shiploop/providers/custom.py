from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import TYPE_CHECKING

from .base import DeployVerifier, VerificationResult

if TYPE_CHECKING:
    from shiploop.config import DeployConfig

logger = logging.getLogger("shiploop.deploy.custom")

ALLOWED_ENV_KEYS = {"PATH", "HOME", "USER", "SHELL", "TERM"}


def _build_curated_env(commit_hash: str, site_url: str, extra_env: dict[str, str] | None = None) -> dict[str, str]:
    env: dict[str, str] = {}
    for key in ALLOWED_ENV_KEYS:
        if key in os.environ:
            env[key] = os.environ[key]
    env["SHIPLOOP_COMMIT"] = commit_hash
    env["SHIPLOOP_SITE"] = site_url
    if extra_env:
        env.update(extra_env)
    return env


class Verifier(DeployVerifier):
    async def verify(
        self,
        commit_hash: str,
        config: DeployConfig,
        site_url: str,
    ) -> VerificationResult:
        if not config.script:
            return VerificationResult(
                success=False,
                details="Custom provider requires 'script' field in deploy config",
            )

        start = time.monotonic()

        try:
            proc = await asyncio.create_subprocess_shell(
                config.script,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                env=_build_curated_env(commit_hash, site_url),
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=config.timeout)
            output = stdout.decode(errors="replace").strip()
            elapsed = time.monotonic() - start

            if proc.returncode == 0:
                return VerificationResult(
                    success=True,
                    deploy_url=site_url,
                    details=output[:500],
                    duration_seconds=elapsed,
                )
            return VerificationResult(
                success=False,
                details=f"Script exited {proc.returncode}: {output[:500]}",
                duration_seconds=elapsed,
            )

        except asyncio.TimeoutError:
            return VerificationResult(
                success=False,
                details=f"Custom verify script timed out after {config.timeout}s",
                duration_seconds=time.monotonic() - start,
            )
