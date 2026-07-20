from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from .config import SegmentConfig, ShipLoopConfig
from .deploy import verify_deployment
from .git_ops import (
    commit,
    create_tag,
    get_changed_files,
    get_short_sha,
    push,
    security_scan,
    stage_files,
)
from .reporting import Reporter, SegmentReport

logger = logging.getLogger("shiploop.ship_utils")


@dataclass
class ShipChangesResult:
    success: bool
    commit_sha: str = ""
    tag: str = ""
    deploy_url: str = ""
    error: str = ""


async def ship_and_verify(
    config: ShipLoopConfig,
    segment: SegmentConfig,
    repo: Path,
    reporter: Reporter,
) -> ShipChangesResult:
    reporter.segment_phase(segment.name, "shipping")

    changed_files = await get_changed_files(repo)
    if not changed_files:
        return ShipChangesResult(success=False, error="No changed files to commit")

    safe_files, blocked_files = security_scan(changed_files, config.blocked_patterns)

    if blocked_files:
        blocked_list = "; ".join(blocked_files[:5])
        return ShipChangesResult(success=False, error=f"Blocked files detected: {blocked_list}")

    if not safe_files:
        return ShipChangesResult(success=False, error="No safe files to commit after security scan")

    await stage_files(safe_files, repo)

    commit_msg = f"feat(shiploop): {segment.name}"
    sha = await commit(commit_msg, repo)
    tag = await create_tag(segment.name, repo)

    await push(repo, include_tags=True)

    short_sha = await get_short_sha(repo)
    reporter._print(f"   📦 Committed: {short_sha}")
    reporter._print(f"   🏷  Tagged: {tag}")

    reporter.segment_phase(segment.name, "verifying")
    verify_result = await verify_deployment(config.deploy, sha, config.site)

    if verify_result.success:
        reporter._print("   ✅ Deploy verified")
        return ShipChangesResult(
            success=True, commit_sha=sha, tag=tag,
            deploy_url=verify_result.deploy_url or "",
        )

    return ShipChangesResult(
        success=False, commit_sha=sha, tag=tag,
        error=f"Deploy verification failed: {verify_result.details}",
    )
