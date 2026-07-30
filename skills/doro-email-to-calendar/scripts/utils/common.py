#!/usr/bin/env python3
"""
Shared utility functions for email-to-calendar skill.

Provides common operations used across multiple scripts.
"""

from datetime import datetime
from typing import Optional


def get_day_of_week(date_str: str) -> str:
    """
    Get day of week name from a date string.

    Args:
        date_str: Date in YYYY-MM-DD format

    Returns:
        Day name (e.g., 'Monday') or empty string if parsing fails
    """
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime('%A')
    except (ValueError, TypeError):
        return ""


def format_timestamp(iso_str: str, fmt: str = '%Y-%m-%d %H:%M') -> str:
    """
    Format an ISO timestamp string to a human-readable format.

    Args:
        iso_str: ISO format timestamp
        fmt: Output format (default: 'YYYY-MM-DD HH:MM')

    Returns:
        Formatted timestamp or original string if parsing fails
    """
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime(fmt)
    except (ValueError, TypeError):
        return iso_str


def generate_id(prefix: str) -> str:
    """
    Generate a unique ID with timestamp and counter placeholder.

    Args:
        prefix: ID prefix (e.g., 'chg', 'inv', 'act')

    Returns:
        Generated ID like 'chg_20260202_143000'
    """
    now = datetime.now()
    return f"{prefix}_{now.strftime('%Y%m%d_%H%M%S')}"


def generate_indexed_id(prefix: str, index: int) -> str:
    """
    Generate a unique ID with timestamp and index.

    Args:
        prefix: ID prefix (e.g., 'chg', 'inv')
        index: Sequential index number

    Returns:
        Generated ID like 'chg_20260202_143000_001'
    """
    now = datetime.now()
    return f"{prefix}_{now.strftime('%Y%m%d_%H%M%S')}_{index:03d}"


def time_ago(iso_timestamp: str) -> str:
    """
    Get a human-readable 'time ago' string.

    Args:
        iso_timestamp: ISO format timestamp

    Returns:
        String like '5 minutes ago' or '2.5 hours ago'
    """
    try:
        dt = datetime.fromisoformat(iso_timestamp)
        delta = datetime.now() - dt
        hours = delta.total_seconds() / 3600

        if hours < 1:
            minutes = int(delta.total_seconds() / 60)
            return f"{minutes} minutes ago"
        else:
            return f"{hours:.1f} hours ago"
    except (ValueError, TypeError):
        return ""
