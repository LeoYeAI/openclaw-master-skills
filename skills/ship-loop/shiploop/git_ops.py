from __future__ import annotations

import asyncio
import fnmatch
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger("shiploop.git")

ALWAYS_BLOCKED = [
    ".env", ".env.*",
    "*.key", "*.pem", "*.p12", "*.pfx", "*.secret",
    "id_rsa", "id_ed25519", "*.keystore",
    "credentials.json", "service-account*.json", "token.json",
    ".npmrc",
    "node_modules/*", "__pycache__/*", ".pytest_cache/*",
    "*.sqlite", "*.sqlite3",
    ".DS_Store",
    "learnings.yml",
]


DEFAULT_GIT_TIMEOUT = 60


async def run_git(args: list[str], cwd: Path, check: bool = True, timeout: int = DEFAULT_GIT_TIMEOUT) -> tuple[int, str, str]:
    proc = await asyncio.create_subprocess_exec(
        "git", *args,
        cwd=cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        try:
            proc.kill()
        except ProcessLookupError:
            pass
        raise GitError(f"git {' '.join(args)} timed out after {timeout}s")
    out = stdout.decode().strip()
    err = stderr.decode().strip()
    if check and proc.returncode != 0:
        raise GitError(f"git {' '.join(args)} failed (exit {proc.returncode}): {err}")
    return proc.returncode, out, err


class GitError(Exception):
    pass


async def get_changed_files(cwd: Path) -> list[str]:
    _, diff_out, _ = await run_git(["diff", "--name-only", "HEAD"], cwd, check=False)
    _, untracked_out, _ = await run_git(["ls-files", "--others", "--exclude-standard"], cwd, check=False)

    files: list[str] = []
    for line in diff_out.splitlines():
        stripped = line.strip()
        if stripped:
            files.append(stripped)
    for line in untracked_out.splitlines():
        stripped = line.strip()
        if stripped:
            files.append(stripped)
    return sorted(set(files))


def security_scan(files: list[str], extra_patterns: list[str] | None = None) -> tuple[list[str], list[str]]:
    all_patterns = ALWAYS_BLOCKED + (extra_patterns or [])

    safe: list[str] = []
    blocked: list[str] = []

    for filepath in files:
        basename = Path(filepath).name
        is_blocked = False
        for pattern in all_patterns:
            if fnmatch.fnmatch(filepath, pattern) or fnmatch.fnmatch(basename, pattern):
                is_blocked = True
                blocked.append(f"{filepath} (matched: {pattern})")
                break
            if pattern.endswith("/*"):
                dir_prefix = pattern[:-2]
                if filepath.startswith(dir_prefix + "/"):
                    is_blocked = True
                    blocked.append(f"{filepath} (matched: {pattern})")
                    break
        if not is_blocked:
            safe.append(filepath)

    return safe, blocked


async def stage_files(files: list[str], cwd: Path) -> None:
    for filepath in files:
        full_path = cwd / filepath
        if full_path.exists():
            await run_git(["add", filepath], cwd)
        else:
            await run_git(["rm", "--cached", filepath], cwd, check=False)


async def commit(message: str, cwd: Path) -> str:
    await run_git(["commit", "-m", message], cwd)
    _, sha, _ = await run_git(["rev-parse", "HEAD"], cwd)
    return sha


async def get_short_sha(cwd: Path) -> str:
    _, sha, _ = await run_git(["rev-parse", "--short", "HEAD"], cwd)
    return sha


async def create_tag(segment_name: str, cwd: Path) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    tag_name = f"shiploop/{segment_name}/{timestamp}"
    await run_git(["tag", tag_name, "HEAD"], cwd)
    return tag_name


async def push(cwd: Path, include_tags: bool = True) -> None:
    _, branch, _ = await run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd)
    args = ["push", "origin", branch]
    if include_tags:
        args.append("--tags")
    await run_git(args, cwd)


async def get_current_branch(cwd: Path) -> str:
    _, branch, _ = await run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd)
    return branch


async def create_worktree(cwd: Path, branch_name: str, worktree_path: Path) -> None:
    await run_git(["worktree", "add", "-b", branch_name, str(worktree_path)], cwd)


async def remove_worktree(cwd: Path, worktree_path: Path) -> None:
    await run_git(["worktree", "remove", str(worktree_path), "--force"], cwd, check=False)


async def delete_branch(cwd: Path, branch_name: str) -> None:
    await run_git(["branch", "-D", branch_name], cwd, check=False)


async def merge_branch(cwd: Path, branch_name: str, message: str) -> bool:
    returncode, _, err = await run_git(["merge", branch_name, "-m", message], cwd, check=False)
    if returncode != 0:
        await run_git(["merge", "--abort"], cwd, check=False)
        logger.error("Merge conflict merging %s: %s", branch_name, err)
        return False
    return True


async def checkout(cwd: Path, target: str) -> None:
    await run_git(["checkout", target], cwd)


async def discard_changes(cwd: Path) -> None:
    await run_git(["checkout", "--", "."], cwd, check=False)
    await run_git(["clean", "-fd"], cwd, check=False)


async def get_diff(cwd: Path, max_lines: int = 500) -> str:
    _, diff_out, _ = await run_git(["diff", "HEAD"], cwd, check=False)
    lines = diff_out.splitlines()
    if len(lines) > max_lines:
        return "\n".join(lines[:max_lines]) + f"\n... ({len(lines) - max_lines} lines truncated)"
    return diff_out


async def get_diff_stat(cwd: Path) -> str:
    _, stat, _ = await run_git(["diff", "--stat", "HEAD"], cwd, check=False)
    return stat


async def get_touched_paths(cwd: Path) -> list[str]:
    """Return list of files changed in the latest commit."""
    _, out, _ = await run_git(
        ["diff-tree", "--no-commit-id", "-r", "--name-only", "HEAD"],
        cwd, check=False,
    )
    if not out:
        # Fallback: diff against parent
        _, out, _ = await run_git(
            ["show", "--stat", "--format=", "HEAD"],
            cwd, check=False,
        )
    paths: list[str] = []
    for line in out.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("..."):
            paths.append(stripped)
    return paths
