#!/usr/bin/env python3
"""
Enforce .env requirement for OpenClaw skills.
Supports GPG-encrypted credentials transparently.

Usage: Import this in your skill's scripts to validate credentials are properly secured.

Example:
    from enforce import require_secure_env, get_credential

    require_secure_env()

    # Works for both plaintext and GPG-encrypted keys
    api_key = get_credential('SERVICE_API_KEY')
    wallet_key = get_credential('MAIN_WALLET_PRIVATE_KEY')  # Auto-decrypts from GPG
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def check_env_exists() -> bool:
    """Check if .env file exists."""
    env_file = Path.home() / '.openclaw' / '.env'
    return env_file.exists()


def check_env_permissions() -> bool:
    """Check if .env has correct permissions (600)."""
    env_file = Path.home() / '.openclaw' / '.env'
    if not env_file.exists():
        return False
    mode = oct(env_file.stat().st_mode)[-3:]
    return mode == '600'


def check_gitignore() -> bool:
    """Check if .env is git-ignored."""
    gitignore = Path.home() / '.openclaw' / '.gitignore'
    if not gitignore.exists():
        return False
    return '.env' in gitignore.read_text()


def is_gpg_available() -> bool:
    """Check if GPG is available on the system."""
    try:
        subprocess.run(['gpg', '--version'], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def _load_env_file() -> dict:
    """Load all key-value pairs from .env file."""
    env_file = Path.home() / '.openclaw' / '.env'
    data = {}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                data[k.strip()] = v.strip()
    return data


def _decrypt_gpg_key(key_name: str) -> str:
    """Decrypt a specific key from the GPG-encrypted secrets file."""
    secrets_file = Path.home() / '.openclaw' / '.env.secrets.gpg'

    if not secrets_file.exists():
        print(f"\n❌ GPG secrets file not found: {secrets_file}", file=sys.stderr)
        print("Run: ./scripts/encrypt.py --keys ... to set up GPG encryption\n", file=sys.stderr)
        return None

    if not is_gpg_available():
        print("\n❌ GPG is not installed. Cannot decrypt secrets.", file=sys.stderr)
        print("Install: sudo apt install gnupg\n", file=sys.stderr)
        return None

    try:
        result = subprocess.run(
            ['gpg', '-d', '--batch', '--quiet', str(secrets_file)],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            print(f"\n❌ GPG decryption failed: {result.stderr.strip()}", file=sys.stderr)
            return None

        secrets = json.loads(result.stdout)
        return secrets.get(key_name)

    except subprocess.TimeoutExpired:
        print("\n❌ GPG decryption timed out (passphrase may be needed)", file=sys.stderr)
        return None
    except json.JSONDecodeError:
        print("\n❌ GPG secrets file is corrupted", file=sys.stderr)
        return None


def require_secure_env(exit_on_fail: bool = True) -> bool:
    """
    Enforce secure .env setup.

    Args:
        exit_on_fail: If True, exit with error. If False, return bool.

    Returns:
        True if all checks pass, False otherwise.
    """
    checks = [
        (check_env_exists, "❌ ~/.openclaw/.env does not exist"),
        (check_env_permissions, "❌ ~/.openclaw/.env has insecure permissions (should be 600)"),
        (check_gitignore, "❌ .env is not git-ignored"),
    ]

    failed = []
    for check_fn, error_msg in checks:
        if not check_fn():
            failed.append(error_msg)

    if failed:
        print("\n🔒 SECURITY REQUIREMENT NOT MET\n", file=sys.stderr)
        print("OpenClaw requires centralized credential management.", file=sys.stderr)
        print("\nIssues found:", file=sys.stderr)
        for msg in failed:
            print(f"  {msg}", file=sys.stderr)

        print("\n💡 Fix this by running:", file=sys.stderr)
        print("   cd ~/.openclaw/skills/credential-manager", file=sys.stderr)
        print("   ./scripts/consolidate.py", file=sys.stderr)
        print("   ./scripts/validate.py --fix", file=sys.stderr)
        print("\nSee CORE-PRINCIPLE.md for why this is mandatory.\n", file=sys.stderr)

        if exit_on_fail:
            sys.exit(1)
        return False

    return True


def get_credential(key: str, required: bool = True) -> str:
    """
    Safely get a credential from .env, with GPG decryption support.

    If the value starts with 'GPG:', the actual value is decrypted from
    ~/.openclaw/.env.secrets.gpg transparently.

    Args:
        key: Credential key (e.g., 'X_ACCESS_TOKEN')
        required: If True, exit on missing key. If False, return None.

    Returns:
        Credential value (or None if not required and missing)

    Raises:
        SystemExit: If .env not secure or key not found (when required=True)
    """
    require_secure_env()

    env_data = _load_env_file()
    value = env_data.get(key)

    if value is None:
        if not required:
            return None
        print(f"\n❌ Credential '{key}' not found in .env\n", file=sys.stderr)
        print("Add it to ~/.openclaw/.env:", file=sys.stderr)
        print(f"   {key}=your_value_here\n", file=sys.stderr)
        sys.exit(1)

    # Handle GPG-encrypted values
    if value.startswith('GPG:'):
        gpg_key = value[4:]  # Strip 'GPG:' prefix
        decrypted = _decrypt_gpg_key(gpg_key)
        if decrypted is None:
            if not required:
                return None
            print(f"\n❌ Failed to decrypt '{key}' from GPG secrets\n", file=sys.stderr)
            sys.exit(1)
        return decrypted

    return value


if __name__ == '__main__':
    # When run directly, validate and report
    print("🔍 Checking OpenClaw credential security...\n")

    if require_secure_env(exit_on_fail=False):
        print("✅ All security checks passed")
        print("\nYour credentials are properly secured:")
        print("  • ~/.openclaw/.env exists")
        print("  • Permissions are 600 (owner only)")
        print("  • Git-ignored")

        # Check GPG status
        if is_gpg_available():
            secrets_file = Path.home() / '.openclaw' / '.env.secrets.gpg'
            if secrets_file.exists():
                print("  • GPG encryption active ✅")
            else:
                print("  • GPG available but no encrypted secrets")
        else:
            print("  • GPG not installed (optional)")

        print("\n🔒 Good job! Your OpenClaw deployment follows security best practices.")
        sys.exit(0)
    else:
        sys.exit(1)
