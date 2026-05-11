#!/usr/bin/env python3
"""
Validate .env file security, format, and credential strength.
Checks permissions, entropy, private key exposure, backup security.
"""

import argparse
import math
import os
import re
from pathlib import Path
from typing import Dict, List


def calc_entropy(s: str) -> float:
    """Calculate Shannon entropy of a string in bits per character."""
    if not s:
        return 0.0
    freq = {}
    for c in s:
        freq[c] = freq.get(c, 0) + 1
    length = len(s)
    return -sum((count / length) * math.log2(count / length) for count in freq.values())


def check_permissions(env_file: Path) -> Dict:
    """Check file permissions."""
    if not env_file.exists():
        return {'status': 'missing', 'message': 'File does not exist'}

    mode = oct(env_file.stat().st_mode)[-3:]

    if mode == '600':
        return {'status': 'ok', 'mode': mode}
    else:
        return {
            'status': 'insecure',
            'mode': mode,
            'message': f'Permissions {mode} are too permissive (should be 600)'
        }


def check_gitignore(openclaw_dir: Path) -> Dict:
    """Check if .env is in .gitignore."""
    gitignore = openclaw_dir / '.gitignore'

    if not gitignore.exists():
        return {'status': 'missing', 'message': '.gitignore does not exist'}

    content = gitignore.read_text()
    if '.env' in content or '*.env' in content:
        return {'status': 'ok'}
    else:
        return {'status': 'unprotected', 'message': '.env not in .gitignore'}


def check_format(env_file: Path) -> Dict:
    """Check .env file format."""
    issues = []
    keys = set()
    duplicates = []

    with open(env_file) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue

            # Check format
            if '=' not in line:
                issues.append(f"Line {line_num}: Missing '=' separator")
                continue

            key, value = line.split('=', 1)
            key = key.strip()

            # Check key format
            if not re.match(r'^[A-Z0-9_]+$', key):
                issues.append(f"Line {line_num}: Invalid key format '{key}'")

            # Check for duplicates
            if key in keys:
                duplicates.append(key)
            keys.add(key)

            # Values with spaces that aren't quoted — warn
            if ' ' in value and not (value.startswith('"') or value.startswith("'")):
                # Allow JSON-like values (starts with { or [)
                if not (value.startswith('{') or value.startswith('[')):
                    issues.append(f"Line {line_num}: Value with spaces should be quoted (key: {key})")

    if issues or duplicates:
        return {
            'status': 'issues',
            'issues': issues,
            'duplicates': duplicates,
            'keys_count': len(keys)
        }
    else:
        return {
            'status': 'ok',
            'keys_count': len(keys)
        }


def check_security(env_file: Path) -> Dict:
    """Check for security issues including entropy, private keys, mnemonics."""
    warnings = []

    with open(env_file) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue

            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            # Skip GPG-encrypted placeholders
            if value.startswith('GPG:'):
                continue

            # Check for private key patterns in values (not in ADDRESS/HASH keys)
            key_upper = key.upper()
            if re.match(r'^0x[a-fA-F0-9]{64}$', value):
                if not any(x in key_upper for x in ['ADDRESS', 'HASH', 'TX', 'CONTRACT']):
                    warnings.append(
                        f"Line {line_num}: {key} looks like a private key (0x + 64 hex). "
                        f"Consider GPG encryption: ./scripts/encrypt.py --keys {key}"
                    )

            # Check for mnemonic patterns (12 or 24 words)
            words = value.split()
            if len(words) in (12, 24) and all(w.isalpha() and w.islower() for w in words):
                warnings.append(
                    f"Line {line_num}: {key} looks like a mnemonic seed phrase ({len(words)} words). "
                    f"Consider GPG encryption: ./scripts/encrypt.py --keys {key}"
                )

            # Entropy check for keys that should be secret
            secret_indicators = ['SECRET', 'PRIVATE_KEY', 'MNEMONIC', 'PASSWORD', 'PASSPHRASE']
            if any(ind in key_upper for ind in secret_indicators):
                if value and len(value) > 4:
                    entropy = calc_entropy(value)
                    if entropy < 3.0:
                        warnings.append(
                            f"Line {line_num}: {key} has low entropy ({entropy:.1f} bits/char). "
                            f"May be a weak or placeholder value."
                        )

            # Check for common weak values
            weak_values = ['password', 'password123', 'test', 'changeme', 'admin', 'default',
                           'your_value_here', 'xxx', 'placeholder']
            if value.lower() in weak_values:
                warnings.append(f"Line {line_num}: {key} has a weak/placeholder value")

    return {
        'status': 'ok' if not warnings else 'warnings',
        'warnings': warnings
    }


def check_backups(openclaw_dir: Path) -> Dict:
    """Check backup file and directory permissions."""
    issues = []
    backup_dir = openclaw_dir / 'backups'

    if not backup_dir.exists():
        return {'status': 'ok', 'message': 'No backups directory'}

    # Check backup root dir
    mode = oct(backup_dir.stat().st_mode)[-3:]
    if mode != '700':
        issues.append(f"{backup_dir}: directory mode {mode} (should be 700)")

    # Check each backup subdirectory and files
    for sub in backup_dir.iterdir():
        if sub.is_dir():
            sub_mode = oct(sub.stat().st_mode)[-3:]
            if sub_mode != '700':
                issues.append(f"{sub}: directory mode {sub_mode} (should be 700)")

            for f in sub.iterdir():
                if f.is_file():
                    f_mode = oct(f.stat().st_mode)[-3:]
                    if f_mode != '600':
                        issues.append(f"{f.name}: file mode {f_mode} (should be 600)")

    return {
        'status': 'ok' if not issues else 'issues',
        'issues': issues
    }


def fix_permissions(env_file: Path):
    """Fix .env file permissions."""
    os.chmod(env_file, 0o600)
    print(f"   🔧 Fixed permissions: 600")


def fix_gitignore(openclaw_dir: Path):
    """Add .env to .gitignore."""
    gitignore = openclaw_dir / '.gitignore'
    entries = ['.env', '.env.secrets.gpg', '.env.meta']

    if not gitignore.exists():
        with open(gitignore, 'w') as f:
            f.write("# Credentials\n")
            for e in entries:
                f.write(f"{e}\n")
    else:
        content = gitignore.read_text()
        missing = [e for e in entries if e not in content]
        if missing:
            with open(gitignore, 'a') as f:
                f.write("\n# Credentials\n")
                for e in missing:
                    f.write(f"{e}\n")

    print(f"   🔧 Updated .gitignore")


def fix_backups(openclaw_dir: Path):
    """Fix backup file and directory permissions."""
    backup_dir = openclaw_dir / 'backups'
    if not backup_dir.exists():
        return

    fixed = 0
    os.chmod(backup_dir, 0o700)

    for sub in backup_dir.iterdir():
        if sub.is_dir():
            os.chmod(sub, 0o700)
            fixed += 1
            for f in sub.iterdir():
                if f.is_file():
                    os.chmod(f, 0o600)
                    fixed += 1

    print(f"   🔧 Fixed {fixed} backup file/directory permissions")


def validate(check_type: str = 'all', auto_fix: bool = False) -> bool:
    """Validate .env file."""
    home = Path.home()
    openclaw_dir = home / '.openclaw'
    env_file = openclaw_dir / '.env'

    print("\n🔍 Validating credentials...\n")

    all_ok = True

    # Check permissions
    if check_type in ['all', 'permissions']:
        print("📋 Checking permissions...")
        result = check_permissions(env_file)
        if result['status'] == 'ok':
            print(f"   ✅ Permissions: {result['mode']}")
        elif result['status'] == 'missing':
            print(f"   ❌ {result['message']}")
            return False
        else:
            print(f"   ⚠️  {result['message']}")
            all_ok = False
            if auto_fix:
                fix_permissions(env_file)
                all_ok = True

    # Check gitignore
    if check_type in ['all', 'gitignore']:
        print("\n📋 Checking .gitignore...")
        result = check_gitignore(openclaw_dir)
        if result['status'] == 'ok':
            print(f"   ✅ .env is git-ignored")
        else:
            print(f"   ⚠️  {result.get('message', 'Not protected')}")
            all_ok = False
            if auto_fix:
                fix_gitignore(openclaw_dir)
                all_ok = True

    # Check format
    if check_type in ['all', 'format']:
        print("\n📋 Checking format...")
        result = check_format(env_file)
        if result['status'] == 'ok':
            print(f"   ✅ Format valid ({result['keys_count']} keys)")
        else:
            if result['issues']:
                print(f"   ⚠️  Found {len(result['issues'])} issue(s):")
                for issue in result['issues'][:5]:
                    print(f"      • {issue}")
                if len(result['issues']) > 5:
                    print(f"      ... +{len(result['issues']) - 5} more")
            if result['duplicates']:
                print(f"   ⚠️  Duplicate keys: {', '.join(result['duplicates'])}")
            all_ok = False

    # Check security
    if check_type in ['all', 'security']:
        print("\n📋 Checking security...")
        result = check_security(env_file)
        if result['status'] == 'ok':
            print(f"   ✅ No security warnings")
        else:
            print(f"   ⚠️  Found {len(result['warnings'])} warning(s):")
            for warning in result['warnings'][:10]:
                print(f"      • {warning}")
            if len(result['warnings']) > 10:
                print(f"      ... +{len(result['warnings']) - 10} more")

    # Check backups
    if check_type in ['all', 'backups']:
        print("\n📋 Checking backup security...")
        result = check_backups(openclaw_dir)
        if result['status'] == 'ok':
            print(f"   ✅ Backup permissions OK")
        else:
            print(f"   ⚠️  Found {len(result['issues'])} issue(s):")
            for issue in result['issues'][:10]:
                print(f"      • {issue}")
            if len(result['issues']) > 10:
                print(f"      ... +{len(result['issues']) - 10} more")
            all_ok = False
            if auto_fix:
                fix_backups(openclaw_dir)
                all_ok = True

    # Summary
    print(f"\n{'✅' if all_ok else '⚠️'} Validation {'passed' if all_ok else 'found issues'}")

    if not all_ok and not auto_fix:
        print(f"\n💡 Run with --fix to automatically fix issues")

    return all_ok


def main():
    parser = argparse.ArgumentParser(description='Validate credentials')
    parser.add_argument('--check', choices=['all', 'permissions', 'gitignore', 'format', 'security', 'backups'],
                        default='all', help='What to check')
    parser.add_argument('--fix', action='store_true',
                        help='Automatically fix issues')
    args = parser.parse_args()

    result = validate(args.check, args.fix)
    return 0 if result else 1


if __name__ == '__main__':
    exit(main())
