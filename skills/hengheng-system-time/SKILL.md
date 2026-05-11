---
name: system-time
version: 1.0.0
description: Get accurate system time in various formats and timezones. Use when the user needs to know the current time, date, timestamp, or wants to convert between timezones. Supports ISO 8601, Unix timestamp, human-readable formats, and timezone conversions.
---

# System Time

Get accurate system time information in multiple formats.

## Quick Usage

### Current Time (Local)
```bash
date                                    # Human readable
date -Iseconds                          # ISO 8601 with seconds
date +%s                                # Unix timestamp
```

### Current Time (UTC)
```bash
date -u                                 # UTC human readable
date -u -Iseconds                       # UTC ISO 8601
date -u +%s                             # UTC Unix timestamp (same as local)
```

### Specific Timezone
```bash
TZ=Asia/Shanghai date                   # Shanghai time
TZ=America/New_York date                # New York time
TZ=Europe/London date                   # London time
```

## Common Formats

| Format | Command | Example Output |
|--------|---------|----------------|
| ISO 8601 | `date -Iseconds` | 2024-03-11T16:30:00+08:00 |
| Unix timestamp | `date +%s` | 1710145800 |
| RFC 2822 | `date -R` | Mon, 11 Mar 2024 16:30:00 +0800 |
| Custom | `date "+%Y-%m-%d %H:%M:%S"` | 2024-03-11 16:30:00 |

## Timezone Conversion

Convert from one timezone to another:
```bash
# Convert specific time from Shanghai to New York
TZ=America/New_York date -d "2024-03-11 16:30:00 CST"

# List available timezones
ls /usr/share/zoneinfo/
```

## Python Alternative (for scripting)

```python
from datetime import datetime, timezone

# Current UTC time
utc_now = datetime.now(timezone.utc)
print(utc_now.isoformat())

# Current local time
local_now = datetime.now()
print(local_now.isoformat())

# Unix timestamp
print(int(utc_now.timestamp()))
```

## Notes

- Unix timestamp is always UTC (timezone-independent)
- ISO 8601 format includes timezone offset
- Use `timedatectl` on Linux systems for system clock info
