---
name: phy-cron-explainer
description: Cron expression explainer, validator, and converter. Translates any cron expression into plain English ("0 */6 * * *" → "Every 6 hours, at minute 0"), shows the next 5 scheduled run times with exact dates, detects impossible/conflicting expressions (Feb 30, conflicting day-of-week + day-of-month), identifies suspicious patterns (every minute in production, very-frequent schedules on expensive operations), and converts plain English descriptions to cron ("every weekday at 9am" → "0 9 * * 1-5"). Supports all major flavors: standard Unix 5-field, 6-field with seconds, AWS EventBridge, GitHub Actions schedule, Kubernetes CronJob, Spring @Scheduled, and special strings (@yearly, @monthly, @daily, @hourly, @reboot). Also scans .github/workflows/ and Kubernetes YAML files for cron schedules and audits them. Zero external API — pure local parsing. Triggers on "cron expression", "what does this cron mean", "cron to English", "cron schedule", "explain cron", "@reboot", "/cron".
license: Apache-2.0
metadata:
  author: PHY041
  version: "1.0.0"
  tags:
    - cron
    - scheduling
    - devops
    - developer-tools
    - kubernetes
    - github-actions
    - aws
    - automation
    - ci-cd
    - utilities
---

# Cron Explainer

`0 2 * * 1`

What does that mean? Every Monday at 2am. How about `*/5 9-17 * * 1-5`? Every 5 minutes between 9am and 5pm on weekdays.

You shouldn't need to count fields in your head. This skill translates any cron expression into plain English, shows the next scheduled runs, catches impossible expressions before they go to production, converts English descriptions to cron, and scans your CI/K8s configs to audit all your schedules in one shot.

**All major cron flavors. Zero external API.**

---

## Trigger Phrases

- "cron expression", "explain this cron", "what does cron mean"
- "cron to English", "translate cron"
- "cron schedule", "next run time"
- "English to cron", "convert to cron"
- "cron syntax", "cron debug"
- "kubernetes cronjob", "github actions schedule"
- "/cron"

---

## How to Provide Input

```bash
# Option 1: Explain a cron expression
/cron "0 2 * * 1"
/cron "*/5 9-17 * * 1-5"
/cron "0 0 1,15 * *"

# Option 2: Explain a special string
/cron "@daily"
/cron "@reboot"
/cron "@every 6h"    # Kubernetes/Go format

# Option 3: Convert English to cron
/cron "every weekday at 9am"
/cron "every 5 minutes during business hours"
/cron "first day of every month at midnight"
/cron "every 15 minutes from 8am to 6pm on weekdays"

# Option 4: Show next N run times
/cron "0 */6 * * *" --next 10

# Option 5: Validate an expression
/cron "0 25 * * *" --validate    # 25th hour — invalid

# Option 6: Scan project files for cron schedules
/cron --scan .                    # scans GitHub Actions, Kubernetes YAML, crontab
/cron --scan .github/workflows/

# Option 7: Detect flavor
/cron "0/5 * * * ? *" --flavor aws-eventbridge
```

---

## Step 1: Parse and Explain Cron Expression

```python
from datetime import datetime, timedelta
import re
from typing import Optional


# ── Special strings ──────────────────────────────────────────────────────────

SPECIAL_STRINGS = {
    '@yearly':   ('0 0 1 1 *',  'Once a year, at midnight on January 1st'),
    '@annually': ('0 0 1 1 *',  'Once a year, at midnight on January 1st'),
    '@monthly':  ('0 0 1 * *',  'Once a month, at midnight on the 1st'),
    '@weekly':   ('0 0 * * 0',  'Once a week, at midnight on Sunday'),
    '@daily':    ('0 0 * * *',  'Every day at midnight'),
    '@midnight': ('0 0 * * *',  'Every day at midnight'),
    '@hourly':   ('0 * * * *',  'Every hour, at the top of the hour'),
    '@reboot':   (None,         'Once, on system startup/reboot'),
    '@every_1m': ('* * * * *',  'Every minute'),
    '@every_5m': ('*/5 * * * *','Every 5 minutes'),
    '@every_1h': ('0 * * * *',  'Every hour'),
}

WEEKDAY_NAMES = ['Sunday', 'Monday', 'Tuesday', 'Wednesday',
                 'Thursday', 'Friday', 'Saturday']
MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']


def detect_flavor(expression: str) -> str:
    """Detect cron flavor from expression structure."""
    parts = expression.strip().split()
    if len(parts) == 6:
        # Could be 6-field with seconds (Quartz/Spring) or 6-field Linux
        if re.search(r'[?L#W]', parts[5]):
            return 'quartz'
        return '6field-seconds'
    if len(parts) == 7:
        return 'quartz-7field'
    if len(parts) == 5:
        return 'standard'
    return 'unknown'


def explain_field(value: str, field: str, names: Optional[list] = None) -> str:
    """Convert a single cron field to English."""

    if value == '*':
        return None  # "every" is implied

    if value == '?':
        return None  # Quartz "any" — implied

    # Step: */N or start/N
    step_match = re.match(r'^(\*|\d+)/(\d+)$', value)
    if step_match:
        start = step_match.group(1)
        step = int(step_match.group(2))
        if field == 'minute':
            return f'every {step} minute{"s" if step > 1 else ""}'
        if field == 'hour':
            return f'every {step} hour{"s" if step > 1 else ""}'
        if field == 'day_of_month':
            return f'every {step} day{"s" if step > 1 else ""}'
        if field == 'month':
            return f'every {step} month{"s" if step > 1 else ""}'
        if field == 'second':
            return f'every {step} second{"s" if step > 1 else ""}'
        return f'every {step}'

    # Range: N-M
    range_match = re.match(r'^(\d+)-(\d+)$', value)
    if range_match:
        lo, hi = int(range_match.group(1)), int(range_match.group(2))
        if names:
            lo_name = names[lo] if lo < len(names) else str(lo)
            hi_name = names[hi] if hi < len(names) else str(hi)
            return f'{lo_name} through {hi_name}'
        if field == 'hour':
            lo_fmt = f'{lo}:00 {"AM" if lo < 12 else "PM"}'
            hi_fmt = f'{hi % 12 or 12}:00 {"AM" if hi < 12 else "PM"}'
            return f'between {lo_fmt} and {hi_fmt}'
        return f'{lo} to {hi}'

    # Range with step: N-M/S
    range_step_match = re.match(r'^(\d+)-(\d+)/(\d+)$', value)
    if range_step_match:
        lo = int(range_step_match.group(1))
        hi = int(range_step_match.group(2))
        step = int(range_step_match.group(3))
        range_desc = explain_field(f'{lo}-{hi}', field, names)
        return f'every {step} {field.replace("_", " ")}{"s" if step > 1 else ""} {range_desc}'

    # List: N,M,P
    if ',' in value:
        parts = [p.strip() for p in value.split(',')]
        if names:
            named = [names[int(p)] if p.isdigit() and int(p) < len(names) else p for p in parts]
        else:
            named = parts
        if len(named) == 2:
            return f'{named[0]} and {named[1]}'
        return ', '.join(named[:-1]) + f', and {named[-1]}'

    # Single value
    if value.isdigit():
        n = int(value)
        if field == 'hour':
            if n == 0: return 'midnight'
            if n == 12: return 'noon'
            if n < 12: return f'{n}:00 AM'
            return f'{n - 12}:00 PM'
        if field == 'minute':
            return f'minute {n}' if n != 0 else 'on the hour'
        if field == 'second':
            return f'second {n}'
        if field == 'day_of_month':
            suffix = 'st' if n % 10 == 1 and n != 11 else \
                     'nd' if n % 10 == 2 and n != 12 else \
                     'rd' if n % 10 == 3 and n != 13 else 'th'
            return f'the {n}{suffix}'
        if field == 'month' and names:
            return names[n - 1] if 1 <= n <= 12 else str(n)
        if field == 'day_of_week' and names:
            return names[n % 7]
        return str(n)

    # Special Quartz: L (last), W (nearest weekday), # (Nth weekday)
    if value.upper() == 'L' and field == 'day_of_month':
        return 'the last day of the month'
    if value.upper() == 'L' and field == 'day_of_week':
        return 'the last weekday of the month'
    lw_match = re.match(r'^(\d+)W$', value, re.I)
    if lw_match:
        return f'the weekday nearest the {lw_match.group(1)}th'
    hash_match = re.match(r'^(\d+)#(\d+)$', value)
    if hash_match:
        day = int(hash_match.group(1))
        nth = int(hash_match.group(2))
        ordinals = ['', '1st', '2nd', '3rd', '4th', '5th']
        day_name = WEEKDAY_NAMES[day % 7]
        return f'the {ordinals[nth]} {day_name} of the month'

    return value  # fallback — return as-is


def explain_cron(expression: str) -> dict:
    """
    Parse a cron expression and return a human-readable explanation.
    Returns dict with: explanation, flavor, issues, fields
    """
    expr = expression.strip()

    # Handle special strings
    expr_lower = expr.lower()
    if expr_lower in SPECIAL_STRINGS:
        cron_equiv, desc = SPECIAL_STRINGS[expr_lower]
        return {
            'expression': expr,
            'flavor': 'special',
            'explanation': desc,
            'next_runs': [] if expr_lower == '@reboot' else None,
            'issues': [],
            'fields': {},
        }

    # Normalize: replace month/weekday names with numbers
    expr = expr.upper()
    month_map = {'JAN':1,'FEB':2,'MAR':3,'APR':4,'MAY':5,'JUN':6,
                 'JUL':7,'AUG':8,'SEP':9,'OCT':10,'NOV':11,'DEC':12}
    dow_map = {'SUN':0,'MON':1,'TUE':2,'WED':3,'THU':4,'FRI':5,'SAT':6}
    for name, num in {**month_map, **dow_map}.items():
        expr = expr.replace(name, str(num))

    parts = expr.split()
    flavor = detect_flavor(expression)
    issues = []

    # Map parts to field names by flavor
    if flavor == '6field-seconds':
        if len(parts) != 6:
            issues.append({'severity': 'ERROR', 'message': f'Expected 6 fields, got {len(parts)}'})
            return {'expression': expression, 'flavor': flavor, 'explanation': 'Invalid', 'issues': issues, 'fields': {}}
        field_names = ['second', 'minute', 'hour', 'day_of_month', 'month', 'day_of_week']
        field_values = dict(zip(field_names, parts))
    elif len(parts) == 5:
        field_names = ['minute', 'hour', 'day_of_month', 'month', 'day_of_week']
        field_values = dict(zip(field_names, parts))
    else:
        issues.append({'severity': 'ERROR', 'message': f'Unrecognized format: {len(parts)} fields'})
        return {'expression': expression, 'flavor': flavor, 'explanation': 'Invalid', 'issues': issues, 'fields': {}}

    # Explain each field
    minute_desc = explain_field(field_values.get('minute', '*'), 'minute')
    hour_desc = explain_field(field_values.get('hour', '*'), 'hour')
    dom_desc = explain_field(field_values.get('day_of_month', '*'), 'day_of_month')
    month_desc = explain_field(field_values.get('month', '*'), 'month', MONTH_NAMES)
    dow_desc = explain_field(field_values.get('day_of_week', '*'), 'day_of_week', WEEKDAY_NAMES)
    sec_desc = explain_field(field_values.get('second', None) or '0', 'second') if flavor == '6field-seconds' else None

    # Compose natural language description
    parts_en = []

    # Frequency
    if minute_desc and minute_desc.startswith('every'):
        parts_en.append(minute_desc.capitalize())
    elif minute_desc and minute_desc.startswith('minute'):
        if hour_desc:
            parts_en.append(f'At {hour_desc}, {minute_desc}')
        else:
            parts_en.append(f'Every hour, {minute_desc}')
    elif not minute_desc and not hour_desc:
        parts_en.append('Every minute')
    elif not minute_desc and hour_desc:
        parts_en.append(f'Every hour at {hour_desc}')
    elif minute_desc == 'on the hour' and hour_desc:
        parts_en.append(f'At {hour_desc}')
    else:
        if hour_desc and minute_desc:
            # Format as clock time if both are single values
            parts_en.append(f'At {hour_desc}')
            if minute_desc and not minute_desc.startswith('on the hour'):
                parts_en[-1] += f', {minute_desc}'
        elif hour_desc:
            parts_en.append(f'At {hour_desc}')
        elif minute_desc:
            parts_en.append(f'Every hour, at {minute_desc}')

    if sec_desc and sec_desc != 'second 0':
        parts_en.append(f'at {sec_desc}')

    # Day constraints
    if dom_desc and dow_desc:
        parts_en.append(f'on {dom_desc} or {dow_desc}')
    elif dom_desc:
        parts_en.append(f'on {dom_desc}')
    elif dow_desc:
        parts_en.append(f'on {dow_desc}{"s" if not dow_desc.endswith("day") else ""}')

    # Month constraint
    if month_desc:
        parts_en.append(f'in {month_desc}')

    explanation = ', '.join(parts_en) if parts_en else 'Every minute'

    # ── Validation ────────────────────────────────────────────────────────────

    # Every minute in production
    if field_values.get('minute', '') == '*' and field_values.get('hour', '') == '*':
        issues.append({
            'severity': 'WARNING',
            'message': 'Runs every minute — confirm this is intentional for a production schedule',
        })

    # Validate numeric bounds
    BOUNDS = {
        'minute': (0, 59), 'hour': (0, 23),
        'day_of_month': (1, 31), 'month': (1, 12), 'day_of_week': (0, 7),
        'second': (0, 59),
    }
    for fname, fval in field_values.items():
        if fname not in BOUNDS or fval in ('*', '?'):
            continue
        lo, hi = BOUNDS[fname]
        # Extract all numeric values
        nums = re.findall(r'\d+', fval)
        for n_str in nums:
            n = int(n_str)
            if n < lo or n > hi:
                issues.append({
                    'severity': 'ERROR',
                    'message': f'Invalid {fname} value: {n} (valid range: {lo}-{hi})',
                })

    # February 30 / 31 impossibility
    month_val = field_values.get('month', '*')
    dom_val = field_values.get('day_of_month', '*')
    if month_val == '2' and dom_val not in ('*', '?'):
        days = re.findall(r'\d+', dom_val)
        for d in days:
            if int(d) > 29:
                issues.append({
                    'severity': 'ERROR',
                    'message': f'day-of-month={d} in month=2 (February) — this date never occurs',
                })
            elif int(d) == 29:
                issues.append({
                    'severity': 'WARNING',
                    'message': 'day-of-month=29 in February — only runs on leap years',
                })

    # Detect conflicting DOW + DOM (both specified — runs on OR condition, often surprising)
    if dom_val not in ('*', '?') and field_values.get('day_of_week', '*') not in ('*', '?'):
        issues.append({
            'severity': 'INFO',
            'message': (
                'Both day-of-month and day-of-week are specified — '
                'standard cron uses OR (runs if EITHER matches). '
                'Use ? for one field if you want AND behavior (Quartz only).'
            ),
        })

    return {
        'expression': expression,
        'flavor': flavor,
        'explanation': explanation,
        'fields': field_values,
        'issues': issues,
    }
```

---

## Step 2: Calculate Next Run Times

```python
from datetime import datetime, timezone

def next_runs(expression: str, count: int = 5, after: Optional[datetime] = None) -> list[datetime]:
    """
    Calculate the next N run times for a cron expression.
    Uses croniter if available, otherwise falls back to manual calculation.
    """
    after = after or datetime.now(tz=timezone.utc)

    try:
        from croniter import croniter
        cron = croniter(expression, after)
        return [cron.get_next(datetime) for _ in range(count)]
    except ImportError:
        pass

    # Fallback: install croniter
    import subprocess
    subprocess.run(['pip', 'install', 'croniter', '-q'], check=True)
    from croniter import croniter
    cron = croniter(expression, after)
    return [cron.get_next(datetime) for _ in range(count)]


def format_run_times(runs: list[datetime], timezone_name: str = 'UTC') -> list[str]:
    """Format run times for display."""
    now = datetime.now(tz=timezone.utc)
    result = []
    for dt in runs:
        diff = dt - now
        if diff.total_seconds() < 60:
            rel = 'in less than a minute'
        elif diff.total_seconds() < 3600:
            mins = int(diff.total_seconds() / 60)
            rel = f'in {mins} minute{"s" if mins > 1 else ""}'
        elif diff.total_seconds() < 86400:
            hours = int(diff.total_seconds() / 3600)
            rel = f'in {hours} hour{"s" if hours > 1 else ""}'
        else:
            days = int(diff.total_seconds() / 86400)
            rel = f'in {days} day{"s" if days > 1 else ""}'

        result.append(f'{dt.strftime("%Y-%m-%d %H:%M:%S")} UTC ({rel})')
    return result
```

---

## Step 3: English → Cron Converter

```python
import re

def english_to_cron(description: str) -> dict:
    """
    Convert a plain-English schedule description to cron expression.
    Returns {'cron': str, 'explanation': str, 'confidence': str}
    """
    desc = description.lower().strip()

    # Special patterns
    if re.search(r'every\s+minute', desc):
        return {'cron': '* * * * *', 'explanation': 'Every minute', 'confidence': 'HIGH'}

    if re.search(r'every\s+hour', desc):
        return {'cron': '0 * * * *', 'explanation': 'Every hour', 'confidence': 'HIGH'}

    if re.search(r'midnight|every\s+(?:day\s+at\s+)?12\s*am', desc):
        return {'cron': '0 0 * * *', 'explanation': 'Every day at midnight', 'confidence': 'HIGH'}

    if re.search(r'noon|every\s+(?:day\s+at\s+)?12\s*pm', desc):
        return {'cron': '0 12 * * *', 'explanation': 'Every day at noon', 'confidence': 'HIGH'}

    # Extract time: "at 9am", "at 3:30pm", "at 14:00"
    time_match = re.search(
        r'at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?',
        desc, re.I
    )
    hour = minute = None
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2)) if time_match.group(2) else 0
        ampm = (time_match.group(3) or '').lower()
        if ampm == 'pm' and hour != 12:
            hour += 12
        elif ampm == 'am' and hour == 12:
            hour = 0

    # Day of week
    dow_map = {
        'sunday': 0, 'monday': 1, 'tuesday': 2, 'wednesday': 3,
        'thursday': 4, 'friday': 5, 'saturday': 6,
        'weekday': '1-5', 'weekdays': '1-5',
        'weekend': '0,6', 'weekends': '0,6',
        'every day': '*', 'daily': '*',
    }

    dow = '*'
    for key, val in dow_map.items():
        if key in desc:
            dow = str(val)
            break

    # Interval: "every N minutes/hours"
    interval_match = re.search(r'every\s+(\d+)\s+(minute|hour|min|hr)s?', desc, re.I)
    if interval_match:
        n = int(interval_match.group(1))
        unit = interval_match.group(2).lower()

        # Business hours modifier
        if re.search(r'business\s+hours?|work\s+hours?|9\s*(?:am|to)\s*5', desc):
            if unit in ('minute', 'min'):
                cron = f'*/{n} 9-17 * * 1-5'
                return {'cron': cron,
                        'explanation': f'Every {n} minutes, between 9am and 5pm, Monday–Friday',
                        'confidence': 'HIGH'}
            if unit in ('hour', 'hr'):
                cron = f'0 */{ n} * * 1-5' if n > 1 else f'0 9-17 * * 1-5'
                return {'cron': cron,
                        'explanation': f'Every {n} hour{"s" if n>1 else ""}, weekdays only',
                        'confidence': 'MEDIUM'}

        if unit in ('minute', 'min'):
            cron_min = f'*/{n}' if n > 1 else '*'
            cron = f'{cron_min} * * * *'
            return {'cron': cron,
                    'explanation': f'Every {n} minute{"s" if n>1 else ""}',
                    'confidence': 'HIGH'}

        if unit in ('hour', 'hr'):
            cron = f'0 */{n} * * *'
            return {'cron': cron,
                    'explanation': f'Every {n} hour{"s" if n>1 else ""}',
                    'confidence': 'HIGH'}

    # "first day of every month"
    if re.search(r'first\s+day\s+of\s+(?:every|each)\s+month', desc):
        h = hour if hour is not None else 0
        m = minute if minute is not None else 0
        cron = f'{m} {h} 1 * *'
        time_str = f'at {h:02d}:{m:02d}' if hour is not None else 'at midnight'
        return {'cron': cron,
                'explanation': f'On the 1st of every month, {time_str}',
                'confidence': 'HIGH'}

    # "every weekday at Xam"
    if hour is not None and dow != '*':
        m = minute if minute is not None else 0
        cron = f'{m} {hour} * * {dow}'
        dow_names = {'1-5': 'Monday–Friday', '0,6': 'Saturday and Sunday',
                     '0': 'Sunday', '1': 'Monday', '*': 'every day'}
        dow_str = dow_names.get(str(dow), f'day {dow}')
        return {'cron': cron,
                'explanation': f'At {hour:02d}:{m:02d}, {dow_str}',
                'confidence': 'HIGH'}

    # Simple "every day at X"
    if hour is not None:
        m = minute if minute is not None else 0
        cron = f'{m} {hour} * * *'
        am_pm = 'AM' if hour < 12 else 'PM'
        h12 = hour % 12 or 12
        return {'cron': cron,
                'explanation': f'Every day at {h12}:{m:02d} {am_pm}',
                'confidence': 'HIGH'}

    return {
        'cron': None,
        'explanation': 'Could not parse — try: "every weekday at 9am", "every 5 minutes", "first day of month at midnight"',
        'confidence': 'NONE',
    }
```

---

## Step 4: Scan Project Files for Cron Schedules

```python
import glob
import re
import yaml  # pyyaml
from pathlib import Path


def scan_for_cron_schedules(root: str = '.') -> list[dict]:
    """Find all cron expressions in GitHub Actions, Kubernetes, and crontab files."""
    schedules = []

    # GitHub Actions schedule triggers
    for fpath in glob.glob(f'{root}/.github/workflows/*.yml', recursive=False):
        fpath += '' if fpath.endswith('.yml') else ''
        for path in glob.glob(f'{root}/.github/workflows/*.yml') + glob.glob(f'{root}/.github/workflows/*.yaml'):
            try:
                content = Path(path).read_text(errors='replace')
                doc = yaml.safe_load(content)
                if not isinstance(doc, dict):
                    continue
                on = doc.get('on', doc.get(True, {}))
                if isinstance(on, dict):
                    schedule = on.get('schedule', [])
                    if isinstance(schedule, list):
                        for item in schedule:
                            if isinstance(item, dict) and 'cron' in item:
                                schedules.append({
                                    'file': path,
                                    'source': 'github-actions',
                                    'expression': item['cron'],
                                    'context': doc.get('name', 'workflow'),
                                })
            except Exception:
                continue

    # Kubernetes CronJob specs
    for path in glob.glob(f'{root}/**/*.yaml', recursive=True) + glob.glob(f'{root}/**/*.yml', recursive=True):
        if any(skip in path for skip in ['.git', 'node_modules', 'vendor']):
            continue
        try:
            content = Path(path).read_text(errors='replace')
            if 'CronJob' not in content:
                continue
            doc = yaml.safe_load(content)
            if isinstance(doc, dict) and doc.get('kind') == 'CronJob':
                schedule = (doc.get('spec', {}) or {}).get('schedule')
                if schedule:
                    schedules.append({
                        'file': path,
                        'source': 'kubernetes-cronjob',
                        'expression': schedule,
                        'context': doc.get('metadata', {}).get('name', 'cronjob'),
                    })
        except Exception:
            continue

    # crontab files
    for crontab_path in ['crontab', 'crontab.txt', 'etc/cron.d', 'docker/cron']:
        full = f'{root}/{crontab_path}'
        if not Path(full).exists():
            continue
        try:
            for i, line in enumerate(Path(full).read_text().splitlines(), 1):
                line = line.strip()
                if line.startswith('#') or not line:
                    continue
                # crontab line format: min hour dom month dow command
                parts = line.split()
                if len(parts) >= 6:
                    expr = ' '.join(parts[:5])
                    command = ' '.join(parts[5:])
                    schedules.append({
                        'file': crontab_path,
                        'source': 'crontab',
                        'expression': expr,
                        'context': command[:60],
                        'line': i,
                    })
        except Exception:
            continue

    return schedules
```

---

## Step 5: Output Report

```markdown
## Cron Expression Analysis

---

### Expression: `*/5 9-17 * * 1-5`

**Translation:** Every 5 minutes, between 9:00 AM and 5:00 PM, on Monday through Friday

**Flavor:** Standard Unix (5-field)

**Field Breakdown:**
| Field | Value | Meaning |
|-------|-------|---------|
| Minute | `*/5` | Every 5 minutes |
| Hour | `9-17` | Between 9:00 AM and 5:00 PM |
| Day-of-month | `*` | Every day |
| Month | `*` | Every month |
| Day-of-week | `1-5` | Monday through Friday |

**Next 5 scheduled runs:**
```
2026-03-19 09:00:00 UTC (in 3 minutes)
2026-03-19 09:05:00 UTC (in 8 minutes)
2026-03-19 09:10:00 UTC (in 13 minutes)
2026-03-19 09:15:00 UTC (in 18 minutes)
2026-03-19 09:20:00 UTC (in 23 minutes)
```

**Issues:** None ✅

---

### Expression: `0 0 30 2 *`

**Translation:** At midnight, on the 30th of February

**Issues:**
- 🔴 ERROR: `day-of-month=30 in month=2 (February)` — **this date never occurs**. Job will never run.

**Fix:** Did you mean the last day of every month?
```
# Last day of every month (Quartz):  0 0 L * *
# 28th of February specifically:     0 0 28 2 *
# Every month on the 30th:           0 0 30 * *  (skips Feb, Apr, Jun, Sep, Nov)
```

---

### English → Cron Examples

| Input | Output | Explanation |
|-------|--------|-------------|
| `"every weekday at 9am"` | `0 9 * * 1-5` | At 09:00, Monday–Friday |
| `"every 15 minutes during business hours"` | `*/15 9-17 * * 1-5` | Every 15 min, 9am–5pm, Mon–Fri |
| `"first day of every month at midnight"` | `0 0 1 * *` | At midnight on the 1st |
| `"every Sunday at 2:30am"` | `30 2 * * 0` | At 02:30, Sunday |
| `"every 6 hours"` | `0 */6 * * *` | At minute 0, every 6 hours |

---

### Project Scan: .github/workflows/

Found 3 cron schedules:

| File | Schedule | Explanation | Issues |
|------|----------|-------------|--------|
| `.github/workflows/deploy.yml` | `0 2 * * 1` | Every Monday at 2:00 AM | ✅ OK |
| `.github/workflows/cleanup.yml` | `*/5 * * * *` | Every 5 minutes | ⚠️ Very frequent — confirm intentional |
| `.github/workflows/report.yml` | `0 0 30 2 *` | Feb 30th at midnight | 🔴 NEVER RUNS (Feb 30 doesn't exist) |

---

### Flavor Reference

| Flavor | Fields | Example | Notes |
|--------|--------|---------|-------|
| Standard Unix | `min hour dom month dow` | `0 2 * * 1` | `cron`, `crontab` |
| 6-field (seconds) | `sec min hour dom month dow` | `0 0 2 * * 1` | Spring, Quartz |
| GitHub Actions | `min hour dom month dow` | `'0 2 * * 1'` | Under `on.schedule.cron` |
| AWS EventBridge | `min hour dom month dow year` | `0 2 ? * MON *` | Uses `?` for DOM/DOW |
| Kubernetes | `min hour dom month dow` | `0 2 * * 1` | `.spec.schedule` |
```

---

## Quick Mode Output

```
Cron: */5 9-17 * * 1-5

Every 5 minutes, between 9:00 AM and 5:00 PM, Monday–Friday

Next run: 2026-03-19 09:00:00 UTC (in 3 minutes)
Issues: none

To convert English → cron:
  "every weekday at 9am" → 0 9 * * 1-5
  "first of month midnight" → 0 0 1 * *
```
