#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Lightweight runtime helpers for long-running strategy scripts.

This module intentionally focuses on process lifecycle only:
- prevent duplicate startup with a PID file
- install signal handlers
- keep the process alive
- run cleanup callbacks on exit
"""

from __future__ import annotations

import os
import signal
import sys
import time
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Union


PathLike = Union[str, Path]
CleanupCallback = Callable[[], None]


def _normalize_pid_file(pid_file: PathLike) -> Path:
    path = Path(pid_file).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _read_existing_pid(pid_file: Path) -> Optional[int]:
    if not pid_file.exists():
        return None
    try:
        raw = pid_file.read_text(encoding="utf-8").strip()
        return int(raw)
    except Exception:
        return None


def _is_process_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _ensure_single_instance(pid_file: Path) -> None:
    existing_pid = _read_existing_pid(pid_file)
    if existing_pid is None:
        return
    if _is_process_alive(existing_pid):
        raise RuntimeError(f"Strategy already running with PID {existing_pid}: {pid_file}")
    pid_file.unlink(missing_ok=True)


def _run_cleanup(cleanup_callbacks: Iterable[CleanupCallback], pid_file: Path) -> None:
    for callback in cleanup_callbacks:
        try:
            callback()
        except Exception as exc:
            print(f"[strategy_runtime] cleanup callback failed: {exc}", file=sys.stderr, flush=True)
    try:
        pid_file.unlink(missing_ok=True)
    except Exception as exc:
        print(f"[strategy_runtime] failed to remove PID file {pid_file}: {exc}", file=sys.stderr, flush=True)


def run_strategy(
    pid_file: PathLike,
    cleanup_callbacks: Optional[Iterable[CleanupCallback]] = None,
    loop_interval: float = 1.0,
) -> None:
    """
    Start a lightweight strategy runtime loop.

    Expected usage:
    1. The caller sets up subscriptions/callbacks first.
    2. The caller passes cleanup callbacks such as unsubscribe/close functions.
    3. This function manages PID, signal handling, and process lifetime.
    """
    pid_path = _normalize_pid_file(pid_file)
    _ensure_single_instance(pid_path)

    callbacks: List[CleanupCallback] = list(cleanup_callbacks or [])

    def _shutdown(signum=None, frame=None) -> None:
        _run_cleanup(callbacks, pid_path)
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    pid_path.write_text(str(os.getpid()), encoding="utf-8")

    try:
        while True:
            time.sleep(loop_interval)
    finally:
        _run_cleanup(callbacks, pid_path)
