#!/usr/bin/env python3
"""
Shared date and time parsing utilities for email-to-calendar skill.

Usage:
    python3 date_parser.py date "February 11, 2026"
    python3 date_parser.py time "2:30 PM"

Returns ISO format or empty string if parsing fails.
"""

import sys
import re
from datetime import datetime

MONTH_MAP = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4,
    'may': 5, 'june': 6, 'july': 7, 'august': 8,
    'september': 9, 'october': 10, 'november': 11, 'december': 12,
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'sept': 9, 'oct': 10,
    'nov': 11, 'dec': 12
}

DATE_FORMATS = [
    '%B %d, %Y', '%b %d, %Y',
    '%d %B %Y', '%d %b %Y',
    '%m/%d/%Y', '%d/%m/%Y',
    '%Y-%m-%d', '%Y/%m/%d'
]


def parse_date(date_str: str) -> str:
    """Parse various date formats to ISO format (YYYY-MM-DD)."""
    date_str = date_str.strip()

    # Try standard formats
    for fmt in DATE_FORMATS:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            pass

    # Try regex pattern for "Month DD, YYYY" variations
    pattern = r'(\w+)\s+(\d{1,2}),?\s+(\d{4})'
    match = re.search(pattern, date_str, re.I)
    if match:
        month_name, day, year = match.groups()
        month_num = MONTH_MAP.get(month_name.lower())
        if month_num:
            return f'{year}-{month_num:02d}-{int(day):02d}'

    return ''


def parse_time(time_str: str) -> str:
    """Parse various time formats to HH:MM format."""
    if not time_str:
        return ''

    time_str = time_str.strip()

    # Pattern: HH:MM AM/PM or HH:MM
    pattern1 = r'(\d{1,2}):(\d{2})\s*(am|pm)?'
    match = re.search(pattern1, time_str, re.I)
    if match:
        hour, minute, ampm = int(match.group(1)), int(match.group(2)), match.group(3)
        if ampm:
            ampm = ampm.lower()
            if ampm == 'pm' and hour != 12:
                hour += 12
            elif ampm == 'am' and hour == 12:
                hour = 0
        return f'{hour:02d}:{minute:02d}'

    # Pattern: H AM/PM (no minutes)
    pattern2 = r'(\d{1,2})\s*(am|pm)'
    match = re.search(pattern2, time_str, re.I)
    if match:
        hour, ampm = int(match.group(1)), match.group(2).lower()
        if ampm == 'pm' and hour != 12:
            hour += 12
        elif ampm == 'am' and hour == 12:
            hour = 0
        return f'{hour:02d}:00'

    return ''


def main():
    if len(sys.argv) < 3:
        print("Usage: date_parser.py <date|time> <value>", file=sys.stderr)
        sys.exit(1)

    mode = sys.argv[1]
    value = sys.argv[2]

    if mode == 'date':
        print(parse_date(value))
    elif mode == 'time':
        print(parse_time(value))
    else:
        print(f"Unknown mode: {mode}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
