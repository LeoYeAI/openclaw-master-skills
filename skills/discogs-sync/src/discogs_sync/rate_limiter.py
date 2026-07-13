"""Proactive rate limiting via Discogs response headers."""

from __future__ import annotations

import time
import threading


class RateLimiter:
    """Track Discogs rate limit headers and throttle requests proactively."""

    MIN_INTERVAL = 1.1  # seconds between requests (stays under 60/min)
    SLOW_INTERVAL = 2.0  # when remaining <= 5
    PAUSE_DURATION = 10.0  # when remaining <= 2
    LOW_THRESHOLD = 5
    CRITICAL_THRESHOLD = 2

    def __init__(self) -> None:
        self._remaining: int | None = None
        self._last_request_time: float = 0.0
        self._lock = threading.Lock()

    def update_from_headers(self, headers: dict) -> None:
        """Update rate limit state from response headers."""
        remaining = headers.get("X-Discogs-Ratelimit-Remaining")
        if remaining is not None:
            try:
                self._remaining = int(remaining)
            except (ValueError, TypeError):
                pass

    def wait_if_needed(self, verbose: bool = False, description: str = "") -> float:
        """Block until it's safe to make the next request.

        Returns the actual wait time in seconds.
        """
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_request_time

            # Determine required interval
            if self._remaining is not None and self._remaining <= self.CRITICAL_THRESHOLD:
                required = self.PAUSE_DURATION
                reason = f"critical (remaining={self._remaining})"
            elif self._remaining is not None and self._remaining <= self.LOW_THRESHOLD:
                required = self.SLOW_INTERVAL
                reason = f"low (remaining={self._remaining})"
            else:
                required = self.MIN_INTERVAL
                reason = "normal"

            wait_time = required - elapsed
            if wait_time > 0:
                if verbose and wait_time > self.MIN_INTERVAL:
                    from .output import print_verbose
                    desc = f" for {description}" if description else ""
                    print_verbose(f"Rate limiter: waiting {wait_time:.1f}s{desc} [{reason}]")
                time.sleep(wait_time)

            self._last_request_time = time.monotonic()
            return max(wait_time, 0.0)

    @property
    def remaining(self) -> int | None:
        return self._remaining


# Global rate limiter instance
_global_limiter = RateLimiter()


def get_rate_limiter() -> RateLimiter:
    return _global_limiter
