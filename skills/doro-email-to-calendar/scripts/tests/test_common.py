#!/usr/bin/env python3
"""Tests for utils/common.py"""

import unittest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.common import (
    get_day_of_week,
    format_timestamp,
    generate_id,
    generate_indexed_id,
    time_ago
)


class TestGetDayOfWeek(unittest.TestCase):
    """Tests for get_day_of_week function."""

    def test_valid_date_wednesday(self):
        """Test that 2026-02-11 returns Wednesday."""
        self.assertEqual(get_day_of_week("2026-02-11"), "Wednesday")

    def test_valid_date_monday(self):
        """Test that 2026-02-09 returns Monday."""
        self.assertEqual(get_day_of_week("2026-02-09"), "Monday")

    def test_valid_date_sunday(self):
        """Test that 2026-02-15 returns Sunday."""
        self.assertEqual(get_day_of_week("2026-02-15"), "Sunday")

    def test_invalid_format(self):
        """Test that invalid date format returns empty string."""
        self.assertEqual(get_day_of_week("invalid"), "")

    def test_wrong_format(self):
        """Test that wrong date format (MM-DD-YYYY) returns empty string."""
        self.assertEqual(get_day_of_week("02-11-2026"), "")

    def test_empty_string(self):
        """Test that empty string returns empty string."""
        self.assertEqual(get_day_of_week(""), "")

    def test_none_input(self):
        """Test that None input returns empty string."""
        self.assertEqual(get_day_of_week(None), "")


class TestFormatTimestamp(unittest.TestCase):
    """Tests for format_timestamp function."""

    def test_valid_iso_timestamp(self):
        """Test formatting a valid ISO timestamp."""
        result = format_timestamp("2026-02-11T14:30:00")
        self.assertEqual(result, "2026-02-11 14:30")

    def test_custom_format(self):
        """Test formatting with a custom format."""
        result = format_timestamp("2026-02-11T14:30:00", "%Y/%m/%d")
        self.assertEqual(result, "2026/02/11")

    def test_iso_with_microseconds(self):
        """Test formatting ISO timestamp with microseconds."""
        result = format_timestamp("2026-02-11T14:30:00.123456")
        self.assertEqual(result, "2026-02-11 14:30")

    def test_invalid_timestamp(self):
        """Test that invalid timestamp returns original string."""
        self.assertEqual(format_timestamp("invalid"), "invalid")

    def test_empty_string(self):
        """Test that empty string returns empty string."""
        self.assertEqual(format_timestamp(""), "")

    def test_none_input(self):
        """Test that None input returns None (original)."""
        self.assertEqual(format_timestamp(None), None)


class TestGenerateId(unittest.TestCase):
    """Tests for generate_id function."""

    def test_prefix_format(self):
        """Test that generated ID starts with correct prefix."""
        result = generate_id("chg")
        self.assertTrue(result.startswith("chg_"))

    def test_contains_date_parts(self):
        """Test that generated ID contains date parts."""
        result = generate_id("inv")
        # Should have format: inv_YYYYMMDD_HHMMSS
        parts = result.split("_")
        self.assertEqual(len(parts), 3)
        self.assertEqual(parts[0], "inv")
        self.assertEqual(len(parts[1]), 8)  # YYYYMMDD
        self.assertEqual(len(parts[2]), 6)  # HHMMSS

    def test_different_prefixes(self):
        """Test various prefixes work correctly."""
        for prefix in ["chg", "inv", "act", "evt"]:
            result = generate_id(prefix)
            self.assertTrue(result.startswith(f"{prefix}_"))


class TestGenerateIndexedId(unittest.TestCase):
    """Tests for generate_indexed_id function."""

    def test_index_format(self):
        """Test that generated ID includes zero-padded index."""
        result = generate_indexed_id("chg", 1)
        self.assertTrue(result.endswith("_001"))

    def test_larger_index(self):
        """Test larger index values."""
        result = generate_indexed_id("chg", 42)
        self.assertTrue(result.endswith("_042"))

    def test_three_digit_index(self):
        """Test three-digit index."""
        result = generate_indexed_id("chg", 123)
        self.assertTrue(result.endswith("_123"))

    def test_full_format(self):
        """Test full ID format."""
        result = generate_indexed_id("inv", 5)
        # Should have format: inv_YYYYMMDD_HHMMSS_005
        parts = result.split("_")
        self.assertEqual(len(parts), 4)
        self.assertEqual(parts[0], "inv")
        self.assertEqual(parts[3], "005")


class TestTimeAgo(unittest.TestCase):
    """Tests for time_ago function."""

    def test_minutes_ago(self):
        """Test time_ago for recent timestamps (minutes)."""
        now = datetime.now()
        five_min_ago = (now - timedelta(minutes=5)).isoformat()
        result = time_ago(five_min_ago)
        self.assertIn("minutes ago", result)
        self.assertIn("5", result)

    def test_hours_ago(self):
        """Test time_ago for timestamps hours ago."""
        now = datetime.now()
        two_hours_ago = (now - timedelta(hours=2)).isoformat()
        result = time_ago(two_hours_ago)
        self.assertIn("hours ago", result)
        self.assertIn("2", result)

    def test_fractional_hours(self):
        """Test time_ago shows fractional hours."""
        now = datetime.now()
        ninety_min_ago = (now - timedelta(minutes=90)).isoformat()
        result = time_ago(ninety_min_ago)
        self.assertIn("hours ago", result)
        self.assertIn("1.5", result)

    def test_invalid_timestamp(self):
        """Test that invalid timestamp returns empty string."""
        self.assertEqual(time_ago("invalid"), "")

    def test_none_input(self):
        """Test that None input returns empty string."""
        self.assertEqual(time_ago(None), "")


if __name__ == '__main__':
    unittest.main()
