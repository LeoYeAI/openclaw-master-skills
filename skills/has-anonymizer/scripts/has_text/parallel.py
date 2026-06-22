#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared concurrency settings for model-backed has_text requests."""

from __future__ import annotations

DEFAULT_MAX_PARALLEL_REQUESTS = 4


def resolve_parallel_workers(total_units: int, max_parallel_requests: int) -> int:
    """Clamp worker count to the configured parallel request budget."""
    if max_parallel_requests < 1:
        raise ValueError("max_parallel_requests must be >= 1")
    return min(total_units, max_parallel_requests)
