"""File-based locking for concurrent access (ADR-007).

Cross-platform: uses fcntl on Unix, msvcrt on Windows.
Falls back to a simple mkdir-based lock if neither is available.
"""

from __future__ import annotations

import json
import os
import sys
import time
import warnings
from pathlib import Path

STALE_LOCK_SECONDS = 60

# Platform-specific locking primitives
_lock_impl = None  # "fcntl" | "msvcrt" | "mkdir"

if sys.platform != "win32":
    try:
        import fcntl as _fcntl

        _lock_impl = "fcntl"
    except ImportError:
        _lock_impl = "mkdir"
else:
    try:
        import msvcrt as _msvcrt

        _lock_impl = "msvcrt"
    except ImportError:
        _lock_impl = "mkdir"


class LockError(Exception):
    pass


def _flock_exclusive_nb(fd):
    """Acquire exclusive non-blocking flock (Unix)."""
    _fcntl.flock(fd, _fcntl.LOCK_EX | _fcntl.LOCK_NB)


def _flock_unlock(fd):
    """Release flock (Unix)."""
    _fcntl.flock(fd, _fcntl.LOCK_UN)


def _msvcrt_lock_nb(fd):
    """Acquire exclusive non-blocking lock (Windows)."""
    _msvcrt.locking(fd, _msvcrt.LK_NBLCK, 1)


def _msvcrt_unlock(fd):
    """Release lock (Windows)."""
    try:
        _msvcrt.locking(fd, _msvcrt.LK_UNLCK, 1)
    except OSError:
        pass


class PalaiaLock:
    """Advisory file lock with stale detection.

    Uses fcntl on Unix, msvcrt on Windows, mkdir-based fallback otherwise.
    """

    def __init__(self, palaia_root: Path, timeout: float = 5.0):
        self.lock_path = palaia_root / ".lock"
        self.timeout = timeout
        self._fd = None
        self._mkdir_lock = None  # Path for mkdir fallback

    def _check_stale(self) -> bool:
        """Check if existing lock is stale (>60s old). If stale, remove it and warn."""
        if not self.lock_path.exists():
            return False
        try:
            with open(self.lock_path, "r") as f:
                data = json.load(f)
            lock_ts = data.get("ts", 0)
            lock_pid = data.get("pid", 0)
            age = time.time() - lock_ts
            if age > STALE_LOCK_SECONDS:
                warnings.warn(
                    f"Stale lock detected (age: {age:.0f}s, pid: {lock_pid}). Overriding stale lock.",
                    stacklevel=3,
                )
                try:
                    self.lock_path.unlink(missing_ok=True)
                except OSError:
                    pass
                return True
        except (json.JSONDecodeError, OSError, ValueError):
            # Corrupt lock file — treat as stale
            try:
                self.lock_path.unlink(missing_ok=True)
            except OSError:
                pass
            return True
        return False

    def _write_lock_info(self, fd):
        """Write PID and timestamp to the lock file descriptor."""
        fd.write(json.dumps({"pid": os.getpid(), "ts": time.time()}))
        fd.flush()

    def _acquire_fcntl(self) -> None:
        """Acquire lock using fcntl (Unix)."""
        deadline = time.monotonic() + self.timeout
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        self._check_stale()

        self._fd = open(self.lock_path, "w")
        while True:
            try:
                _flock_exclusive_nb(self._fd)
                self._write_lock_info(self._fd)
                return
            except (IOError, OSError):
                if time.monotonic() >= deadline:
                    if self._check_stale():
                        try:
                            self._fd.close()
                            self._fd = open(self.lock_path, "w")
                            _flock_exclusive_nb(self._fd)
                            self._write_lock_info(self._fd)
                            return
                        except (IOError, OSError):
                            pass
                    self._fd.close()
                    self._fd = None
                    raise LockError(f"Could not acquire lock within {self.timeout}s")
                time.sleep(0.05)

    def _release_fcntl(self) -> None:
        """Release fcntl lock."""
        if self._fd:
            try:
                _flock_unlock(self._fd)
                self._fd.close()
            except (IOError, OSError):
                pass
            self._fd = None
            try:
                self.lock_path.unlink(missing_ok=True)
            except OSError:
                pass

    def _acquire_msvcrt(self) -> None:
        """Acquire lock using msvcrt (Windows)."""
        deadline = time.monotonic() + self.timeout
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        self._check_stale()

        self._fd = open(self.lock_path, "w")
        while True:
            try:
                _msvcrt_lock_nb(self._fd.fileno())
                self._write_lock_info(self._fd)
                return
            except (IOError, OSError):
                if time.monotonic() >= deadline:
                    if self._check_stale():
                        try:
                            self._fd.close()
                            self._fd = open(self.lock_path, "w")
                            _msvcrt_lock_nb(self._fd.fileno())
                            self._write_lock_info(self._fd)
                            return
                        except (IOError, OSError):
                            pass
                    self._fd.close()
                    self._fd = None
                    raise LockError(f"Could not acquire lock within {self.timeout}s")
                time.sleep(0.05)

    def _release_msvcrt(self) -> None:
        """Release msvcrt lock."""
        if self._fd:
            try:
                _msvcrt_unlock(self._fd.fileno())
                self._fd.close()
            except (IOError, OSError):
                pass
            self._fd = None
            try:
                self.lock_path.unlink(missing_ok=True)
            except OSError:
                pass

    def _acquire_mkdir(self) -> None:
        """Acquire lock using mkdir atomicity (fallback)."""
        deadline = time.monotonic() + self.timeout
        self._mkdir_lock = self.lock_path.with_suffix(".lk")
        self._check_stale()

        while True:
            try:
                self._mkdir_lock.mkdir(parents=True, exist_ok=False)
                # Write lock info to the regular lock file for stale detection
                self.lock_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.lock_path, "w") as f:
                    f.write(json.dumps({"pid": os.getpid(), "ts": time.time()}))
                return
            except FileExistsError:
                if time.monotonic() >= deadline:
                    if self._check_stale():
                        try:
                            self._mkdir_lock.rmdir()
                        except OSError:
                            pass
                        try:
                            self._mkdir_lock.mkdir(exist_ok=False)
                            with open(self.lock_path, "w") as f:
                                f.write(json.dumps({"pid": os.getpid(), "ts": time.time()}))
                            return
                        except (FileExistsError, OSError):
                            pass
                    raise LockError(f"Could not acquire lock within {self.timeout}s")
                time.sleep(0.05)

    def _release_mkdir(self) -> None:
        """Release mkdir lock."""
        if self._mkdir_lock:
            try:
                self._mkdir_lock.rmdir()
            except OSError:
                pass
            self._mkdir_lock = None
        try:
            self.lock_path.unlink(missing_ok=True)
        except OSError:
            pass

    def acquire(self) -> None:
        if _lock_impl == "fcntl":
            self._acquire_fcntl()
        elif _lock_impl == "msvcrt":
            self._acquire_msvcrt()
        else:
            self._acquire_mkdir()

    def release(self) -> None:
        if _lock_impl == "fcntl":
            self._release_fcntl()
        elif _lock_impl == "msvcrt":
            self._release_msvcrt()
        else:
            self._release_mkdir()

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, *args):
        self.release()
