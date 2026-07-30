#!/usr/bin/env python3
"""Tests for utils/date_parser.py"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.date_parser import parse_date, parse_time


class TestParseDate(unittest.TestCase):
    """Tests for parse_date function."""

    def test_full_month_name(self):
        """Test parsing 'February 11, 2026' format."""
        self.assertEqual(parse_date("February 11, 2026"), "2026-02-11")

    def test_short_month_name(self):
        """Test parsing 'Feb 11, 2026' format."""
        self.assertEqual(parse_date("Feb 11, 2026"), "2026-02-11")

    def test_us_numeric_format(self):
        """Test parsing '02/11/2026' US format."""
        self.assertEqual(parse_date("02/11/2026"), "2026-02-11")

    def test_iso_format(self):
        """Test parsing '2026-02-11' ISO format."""
        self.assertEqual(parse_date("2026-02-11"), "2026-02-11")

    def test_day_first_format(self):
        """Test parsing '11 February 2026' format."""
        self.assertEqual(parse_date("11 February 2026"), "2026-02-11")

    def test_short_day_first_format(self):
        """Test parsing '11 Feb 2026' format."""
        self.assertEqual(parse_date("11 Feb 2026"), "2026-02-11")

    def test_month_without_comma(self):
        """Test parsing 'February 11 2026' without comma."""
        self.assertEqual(parse_date("February 11 2026"), "2026-02-11")

    def test_single_digit_day(self):
        """Test parsing date with single digit day."""
        self.assertEqual(parse_date("February 1, 2026"), "2026-02-01")

    def test_september_short(self):
        """Test parsing 'Sept' abbreviation."""
        self.assertEqual(parse_date("Sept 15, 2026"), "2026-09-15")

    def test_september_very_short(self):
        """Test parsing 'Sep' abbreviation."""
        self.assertEqual(parse_date("Sep 15, 2026"), "2026-09-15")

    def test_invalid_date_string(self):
        """Test that invalid string returns empty."""
        self.assertEqual(parse_date("invalid"), "")

    def test_empty_string(self):
        """Test that empty string returns empty."""
        self.assertEqual(parse_date(""), "")

    def test_whitespace_handling(self):
        """Test that leading/trailing whitespace is handled."""
        self.assertEqual(parse_date("  February 11, 2026  "), "2026-02-11")


class TestParseTime(unittest.TestCase):
    """Tests for parse_time function."""

    def test_12h_pm(self):
        """Test parsing '2:30 PM' format."""
        self.assertEqual(parse_time("2:30 PM"), "14:30")

    def test_12h_am(self):
        """Test parsing '9:00 AM' format."""
        self.assertEqual(parse_time("9:00 AM"), "09:00")

    def test_24h_format(self):
        """Test parsing '14:30' 24-hour format."""
        self.assertEqual(parse_time("14:30"), "14:30")

    def test_noon(self):
        """Test parsing '12:00 PM' as noon."""
        self.assertEqual(parse_time("12:00 PM"), "12:00")

    def test_midnight_12am(self):
        """Test parsing '12:00 AM' as midnight."""
        self.assertEqual(parse_time("12:00 AM"), "00:00")

    def test_hour_only_pm(self):
        """Test parsing '2 PM' without minutes."""
        self.assertEqual(parse_time("2 PM"), "14:00")

    def test_hour_only_am(self):
        """Test parsing '9 AM' without minutes."""
        self.assertEqual(parse_time("9 AM"), "09:00")

    def test_lowercase_pm(self):
        """Test parsing '2:30 pm' lowercase."""
        self.assertEqual(parse_time("2:30 pm"), "14:30")

    def test_no_space_before_ampm(self):
        """Test parsing '2:30PM' without space."""
        self.assertEqual(parse_time("2:30PM"), "14:30")

    def test_double_digit_hour_12h(self):
        """Test parsing '10:30 AM' double digit hour."""
        self.assertEqual(parse_time("10:30 AM"), "10:30")

    def test_invalid_time_string(self):
        """Test that invalid string returns empty."""
        self.assertEqual(parse_time("invalid"), "")

    def test_empty_string(self):
        """Test that empty string returns empty."""
        self.assertEqual(parse_time(""), "")

    def test_none_input(self):
        """Test that None input returns empty."""
        self.assertEqual(parse_time(None), "")

    def test_whitespace_handling(self):
        """Test that leading/trailing whitespace is handled."""
        self.assertEqual(parse_time("  2:30 PM  "), "14:30")


if __name__ == '__main__':
    unittest.main()
