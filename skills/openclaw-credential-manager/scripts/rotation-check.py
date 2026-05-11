#!/usr/bin/env python3
"""
Credential rotation tracking.
Tracks creation dates, rotation schedules, and warns when keys need rotation.
"""

import argparse
import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict


# Risk classification patterns
RISK_PATTERNS = {
    'critical': [
        r'PRIVATE_KEY', r'MNEMONIC', r'SEED', r'WALLET_KEY',
        r'CUSTODY', r'SIGNER', r'PASSPHRASE',
    ],
    'standard': [
        r'API_KEY', r'SECRET', r'TOKEN', r'BEARER',
        r'CONSUMER', r'ACCESS', r'AUTH',
    ],
    'low': [
        r'.*',  # Everything else
    ],
}

ROTATION_DAYS = {
    'critical': 90,
    'standard': 180,
    'low': 365,
}


def classify_risk(key_name: str) -> str:
    """Classify a key's risk level based on its name."""
    key_upper = key_name.upper()
    for level in ['critical', 'standard']:
        for pattern in RISK_PATTERNS[level]:
            if re.search(pattern, key_upper):
                return level
    return 'low'


def load_env_keys(env_file: Path) -> list:
    """Load key names from .env file."""
    keys = []
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key = line.split('=', 1)[0].strip()
                keys.append(key)
    return keys


def load_meta(meta_file: Path) -> dict:
    """Load rotation metadata."""
    if not meta_file.exists():
        return {}
    with open(meta_file) as f:
        return json.load(f)


def save_meta(meta_file: Path, meta: dict):
    """Save rotation metadata with secure permissions."""
    with open(meta_file, 'w') as f:
        json.dump(meta, f, indent=2, default=str)
    os.chmod(meta_file, 0o600)


def init_meta(env_file: Path, meta_file: Path):
    """Initialize rotation metadata for all keys in .env."""
    keys = load_env_keys(env_file)
    existing = load_meta(meta_file)
    today = datetime.now().strftime('%Y-%m-%d')

    meta = {}
    new_count = 0

    for key in keys:
        if key in existing:
            meta[key] = existing[key]
        else:
            risk = classify_risk(key)
            meta[key] = {
                'created': today,
                'lastRotated': None,
                'rotationDays': ROTATION_DAYS[risk],
                'risk': risk,
            }
            new_count += 1

    save_meta(meta_file, meta)

    print(f"\n📋 Initialized rotation tracking")
    print(f"   Total keys: {len(meta)}")
    print(f"   New entries: {new_count}")
    print(f"   Critical: {sum(1 for v in meta.values() if v['risk'] == 'critical')}")
    print(f"   Standard: {sum(1 for v in meta.values() if v['risk'] == 'standard')}")
    print(f"   Low: {sum(1 for v in meta.values() if v['risk'] == 'low')}")
    print(f"\n   📁 Metadata: {meta_file}")


def record_rotation(meta_file: Path, key_name: str):
    """Record that a key was rotated today."""
    meta = load_meta(meta_file)

    if key_name not in meta:
        print(f"⚠️  Key '{key_name}' not found in rotation metadata")
        print(f"   Run: ./scripts/rotation-check.py --init")
        return

    meta[key_name]['lastRotated'] = datetime.now().strftime('%Y-%m-%d')
    save_meta(meta_file, meta)
    print(f"✅ Recorded rotation for {key_name} ({datetime.now().strftime('%Y-%m-%d')})")


def check_rotation(meta_file: Path) -> bool:
    """Check rotation status of all keys."""
    meta = load_meta(meta_file)

    if not meta:
        print("\n⚠️  No rotation metadata found")
        print("   Run: ./scripts/rotation-check.py --init")
        return False

    today = datetime.now()
    overdue = []
    upcoming = []
    ok = []

    print(f"\n🔄 Credential Rotation Status ({today.strftime('%Y-%m-%d')})\n")

    for key, info in sorted(meta.items(), key=lambda x: x[1]['risk']):
        risk = info['risk']
        rotation_days = info['rotationDays']
        last_date_str = info.get('lastRotated') or info.get('created', today.strftime('%Y-%m-%d'))

        try:
            last_date = datetime.strptime(last_date_str, '%Y-%m-%d')
        except (ValueError, TypeError):
            last_date = today

        age_days = (today - last_date).days
        next_rotation = last_date + timedelta(days=rotation_days)
        days_until = (next_rotation - today).days

        if days_until < 0:
            overdue.append((key, risk, age_days, rotation_days, abs(days_until)))
        elif days_until < 14:
            upcoming.append((key, risk, age_days, rotation_days, days_until))
        else:
            ok.append((key, risk, age_days, rotation_days, days_until))

    # Print overdue
    if overdue:
        print("🔴 OVERDUE:")
        for key, risk, age, rot, overdue_days in overdue:
            print(f"   ❌ {key}")
            print(f"      Risk: {risk} | Age: {age}d | Rotate every: {rot}d | Overdue: {overdue_days}d")
        print()

    # Print upcoming
    if upcoming:
        print("🟡 UPCOMING (within 14 days):")
        for key, risk, age, rot, days_left in upcoming:
            print(f"   ⚠️  {key}")
            print(f"      Risk: {risk} | Age: {age}d | Rotate every: {rot}d | Due in: {days_left}d")
        print()

    # Print OK summary
    if ok:
        print(f"✅ OK: {len(ok)} key(s) within rotation schedule")
        # Show critical/standard detail even if OK
        for key, risk, age, rot, days_left in ok:
            if risk in ('critical', 'standard'):
                print(f"   ✅ {key} ({risk}, {age}d old, due in {days_left}d)")
        print()

    # Summary
    total = len(overdue) + len(upcoming) + len(ok)
    print(f"📊 Summary: {total} keys tracked")
    print(f"   🔴 Overdue: {len(overdue)}")
    print(f"   🟡 Upcoming: {len(upcoming)}")
    print(f"   ✅ OK: {len(ok)}")

    if overdue:
        print(f"\n💡 Rotate overdue keys and record:")
        print(f"   ./scripts/rotation-check.py --rotated KEY_NAME")

    return len(overdue) == 0


def main():
    parser = argparse.ArgumentParser(description='Credential rotation tracking')
    parser.add_argument('--init', action='store_true',
                        help='Initialize rotation metadata for all keys')
    parser.add_argument('--rotated', metavar='KEY',
                        help='Record that a key was rotated today')
    parser.add_argument('--meta-file', default=None,
                        help='Path to metadata file (default: ~/.openclaw/.env.meta)')
    args = parser.parse_args()

    home = Path.home()
    env_file = home / '.openclaw' / '.env'
    meta_file = Path(args.meta_file) if args.meta_file else home / '.openclaw' / '.env.meta'

    if not env_file.exists():
        print("❌ ~/.openclaw/.env does not exist")
        return 1

    if args.init:
        init_meta(env_file, meta_file)
        return 0

    if args.rotated:
        record_rotation(meta_file, args.rotated)
        return 0

    # Default: check rotation status
    all_ok = check_rotation(meta_file)
    return 0 if all_ok else 1


if __name__ == '__main__':
    exit(main())
