#!/usr/bin/env python3
"""
Scan for credential files in common locations.
Supports deep scanning for hardcoded secrets in source files.
"""

import argparse
import json
import math
import os
import re
from pathlib import Path
from typing import Dict, List

# Common credential file patterns
CREDENTIAL_PATTERNS = [
    "~/.config/*/credentials.json",
    "~/.config/*/*.credentials.json",
    "~/.openclaw/*.json",
    "~/.openclaw/*-credentials*",
    "~/.openclaw/workspace/memory/*-creds.json",
    "~/.openclaw/workspace/memory/*credentials*.json",
    "~/.openclaw/workspace/.env",
    "~/.openclaw/workspace/.env.*",
    "~/.openclaw/workspace/*/.env",
    "~/.openclaw/workspace/skills/*/.env",
    "~/.openclaw/workspace/skills/*/repo/.env",
    "~/.openclaw/workspace/scripts/.env",
    "~/.local/share/*/credentials.json",
]

# Sensitive key patterns
SENSITIVE_KEYS = [
    r"api[_-]?key",
    r"access[_-]?token",
    r"secret",
    r"password",
    r"passphrase",
    r"credentials",
    r"auth",
    r"bearer",
    r"oauth",
    r"consumer[_-]?key",
    r"private[_-]?key",
    r"mnemonic",
    r"seed[_-]?phrase",
    r"signing[_-]?key",
    r"wallet[_-]?key",
]

# Deep scan patterns for hardcoded secrets
DEEP_SCAN_PATTERNS = [
    (r'(?:sk_|pk_|Bearer\s+)[A-Za-z0-9_\-]{20,}', 'API key prefix (sk_/pk_/Bearer)'),
    (r'0x[a-fA-F0-9]{64}', 'Possible private key (0x + 64 hex)'),
    (r'(?:api[_-]?key|secret|token|password)\s*[=:]\s*["\']?[A-Za-z0-9_\-]{16,}', 'Hardcoded credential assignment'),
    (r'(?:mnemonic|seed)\s*[=:]\s*["\'](?:\w+\s+){11,23}\w+', 'Possible mnemonic/seed phrase'),
]

DEEP_SCAN_EXTENSIONS = {'.sh', '.js', '.py', '.mjs', '.ts', '.jsx', '.tsx'}
DEEP_SCAN_EXCLUDE = {'node_modules', '.git', '__pycache__', '.venv', 'venv'}


def calc_entropy(s: str) -> float:
    """Calculate Shannon entropy of a string in bits per character."""
    if not s:
        return 0.0
    freq = {}
    for c in s:
        freq[c] = freq.get(c, 0) + 1
    length = len(s)
    return -sum((count / length) * math.log2(count / length) for count in freq.values())


def scan_json_file(path: Path) -> Dict:
    """Scan a JSON file for credentials."""
    try:
        with open(path) as f:
            data = json.load(f)

        keys = []
        if isinstance(data, dict):
            keys = [k.lower() for k in data.keys()]

        has_sensitive = any(
            any(re.search(pattern, key, re.IGNORECASE) for pattern in SENSITIVE_KEYS)
            for key in keys
        )

        result = {
            "path": str(path),
            "type": "json",
            "keys": list(data.keys()) if isinstance(data, dict) else [],
            "likely_credentials": has_sensitive,
            "size": path.stat().st_size,
            "mode": oct(path.stat().st_mode)[-3:],
        }

        # Check if symlink
        if path.is_symlink():
            result["symlink_target"] = str(path.resolve())

        return result
    except Exception as e:
        return {
            "path": str(path),
            "type": "json",
            "error": str(e),
            "likely_credentials": True,
        }


def scan_env_file(path: Path) -> Dict:
    """Scan a .env file for credentials."""
    try:
        keys = []
        with open(path) as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key = line.split('=', 1)[0].strip()
                    keys.append(key)

        result = {
            "path": str(path),
            "type": "env",
            "keys": keys,
            "likely_credentials": len(keys) > 0,
            "size": path.stat().st_size,
            "mode": oct(path.stat().st_mode)[-3:],
        }

        # Check if symlink
        if path.is_symlink():
            target = path.resolve()
            result["symlink_target"] = str(target)
            main_env = Path.home() / '.openclaw' / '.env'
            result["symlink_ok"] = target == main_env

        return result
    except Exception as e:
        return {
            "path": str(path),
            "type": "env",
            "error": str(e),
            "likely_credentials": True,
        }


def deep_scan(scan_dir: Path = None) -> List[Dict]:
    """Scan source files for hardcoded credentials."""
    if scan_dir is None:
        scan_dir = Path.home() / '.openclaw' / 'workspace'

    findings = []

    for root, dirs, files in os.walk(scan_dir):
        # Prune excluded directories
        dirs[:] = [d for d in dirs if d not in DEEP_SCAN_EXCLUDE]

        for fname in files:
            fpath = Path(root) / fname
            if fpath.suffix not in DEEP_SCAN_EXTENSIONS:
                continue

            try:
                with open(fpath, 'r', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        for pattern, desc in DEEP_SCAN_PATTERNS:
                            matches = re.findall(pattern, line)
                            for match in matches:
                                # Skip common false positives
                                if match in ('0x' + '0' * 64, '0x' + 'f' * 64):
                                    continue
                                # Skip if it's a variable reference
                                if match.startswith('$') or match.startswith('process.env'):
                                    continue
                                findings.append({
                                    "file": str(fpath),
                                    "line": line_num,
                                    "pattern": desc,
                                    "preview": match[:20] + '...' if len(match) > 20 else match,
                                })
            except (PermissionError, UnicodeDecodeError):
                continue

    return findings


def scan_locations(custom_paths: List[str] = None) -> List[Dict]:
    """Scan all common credential locations."""
    results = []
    home = Path.home()

    patterns = CREDENTIAL_PATTERNS.copy()
    if custom_paths:
        patterns.extend(custom_paths)

    # Expand patterns and check files
    checked = set()
    for pattern in patterns:
        expanded = home.glob(pattern.replace('~/', ''))
        for path in expanded:
            # Follow symlinks for existence check but report them
            if not (path.is_file() or path.is_symlink()) or str(path) in checked:
                continue
            checked.add(str(path))

            if path.suffix == '.json':
                result = scan_json_file(path)
            elif '.env' in path.name:
                result = scan_env_file(path)
            else:
                continue

            if result.get('likely_credentials'):
                results.append(result)

    # Check for existing .env
    env_path = home / '.openclaw' / '.env'
    if env_path.exists() and str(env_path) not in checked:
        results.append(scan_env_file(env_path))

    return results


def main():
    parser = argparse.ArgumentParser(description='Scan for credential files')
    parser.add_argument('--paths', nargs='+', help='Additional paths to scan')
    parser.add_argument('--deep', action='store_true',
                        help='Deep scan source files for hardcoded secrets')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                        help='Output format')
    args = parser.parse_args()

    results = scan_locations(args.paths)

    if args.format == 'json':
        output = {"files": results}
        if args.deep:
            output["deep_scan"] = deep_scan()
        print(json.dumps(output, indent=2))
    else:
        print(f"\n🔍 Found {len(results)} credential file(s):\n")
        for r in results:
            status = "✅" if r.get('mode') == '600' else "⚠️"
            print(f"{status} {r['path']}")
            print(f"   Type: {r['type']}")
            if r.get('symlink_target'):
                ok = "✅" if r.get('symlink_ok', True) else "⚠️"
                print(f"   {ok} Symlink → {r['symlink_target']}")
            if 'keys' in r:
                print(f"   Keys: {', '.join(r['keys'][:5])}")
                if len(r['keys']) > 5:
                    print(f"        (+{len(r['keys']) - 5} more)")
            print(f"   Mode: {r.get('mode', 'unknown')}")
            if r.get('mode') != '600':
                print(f"   ⚠️  Should be 600 for security")
            print()

        if args.deep:
            findings = deep_scan()
            if findings:
                print(f"\n🔎 Deep scan: {len(findings)} potential hardcoded secret(s):\n")
                for f in findings[:20]:
                    print(f"   ⚠️  {f['file']}:{f['line']}")
                    print(f"      Pattern: {f['pattern']}")
                    print(f"      Preview: {f['preview']}")
                    print()
                if len(findings) > 20:
                    print(f"   ... +{len(findings) - 20} more findings")
            else:
                print(f"\n🔎 Deep scan: No hardcoded secrets found ✅")

        print(f"\n📊 Summary:")
        print(f"   Total files: {len(results)}")
        print(f"   Insecure permissions: {sum(1 for r in results if r.get('mode') != '600')}")
        symlinks = [r for r in results if r.get('symlink_target')]
        if symlinks:
            print(f"   Symlinks: {len(symlinks)}")
        print(f"\n💡 Next: Run ./scripts/consolidate.py to merge into .env\n")


if __name__ == '__main__':
    main()
