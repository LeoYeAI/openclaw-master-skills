#!/usr/bin/env python3
"""
GPG encryption for high-value secrets.
Encrypts specified keys from .env into .env.secrets.gpg
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def is_gpg_available() -> bool:
    """Check if GPG is available."""
    try:
        subprocess.run(['gpg', '--version'], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def load_env(env_file: Path) -> dict:
    """Load .env file as dict preserving order."""
    data = {}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                data[k.strip()] = v.strip()
    return data


def read_env_lines(env_file: Path) -> list:
    """Read .env file preserving all lines (comments, blanks)."""
    with open(env_file) as f:
        return f.readlines()


def write_env_lines(env_file: Path, lines: list):
    """Write lines back to .env with secure permissions."""
    with open(env_file, 'w') as f:
        f.writelines(lines)
    os.chmod(env_file, 0o600)


def load_secrets(secrets_file: Path, passphrase: str = None) -> dict:
    """Decrypt and load existing secrets from GPG file."""
    if not secrets_file.exists():
        return {}

    if passphrase is None:
        passphrase = _get_passphrase()

    try:
        result = subprocess.run(
            ['gpg', '-d', '--batch', '--quiet',
             '--passphrase-fd', '0',
             str(secrets_file)],
            input=passphrase,
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"❌ GPG decryption failed: {result.stderr.strip()}", file=sys.stderr)
    except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
        print(f"❌ Failed to load secrets: {e}", file=sys.stderr)

    return {}


def _get_passphrase() -> str:
    """Get passphrase from environment or prompt."""
    # Check environment variable first (for automation)
    passphrase = os.environ.get('OPENCLAW_GPG_PASSPHRASE')
    if passphrase:
        return passphrase

    # Interactive prompt
    import getpass
    passphrase = getpass.getpass("🔑 Enter GPG passphrase for OpenClaw secrets: ")
    if not passphrase:
        print("❌ Passphrase cannot be empty", file=sys.stderr)
        sys.exit(1)
    return passphrase


def save_secrets(secrets_file: Path, secrets: dict, passphrase: str = None):
    """Encrypt and save secrets to GPG file."""
    json_data = json.dumps(secrets, indent=2)

    if passphrase is None:
        passphrase = _get_passphrase()

    # Write to temp file first, then encrypt
    tmp_file = secrets_file.parent / '.env.secrets.tmp'
    try:
        with open(tmp_file, 'w') as f:
            f.write(json_data)
        os.chmod(tmp_file, 0o600)

        # Encrypt with symmetric cipher using passphrase via fd
        result = subprocess.run(
            ['gpg', '-c', '--batch', '--yes',
             '--cipher-algo', 'AES256',
             '--passphrase-fd', '0',
             '-o', str(secrets_file),
             str(tmp_file)],
            input=passphrase,
            capture_output=True, text=True, timeout=30
        )

        if result.returncode != 0:
            print(f"❌ GPG encryption failed: {result.stderr.strip()}", file=sys.stderr)
            return False

        os.chmod(secrets_file, 0o600)
        return True

    finally:
        # Always clean up temp file
        if tmp_file.exists():
            tmp_file.unlink()


def encrypt_keys(key_names: list):
    """Encrypt specified keys from .env into GPG secrets file."""
    home = Path.home()
    env_file = home / '.openclaw' / '.env'
    secrets_file = home / '.openclaw' / '.env.secrets.gpg'

    if not env_file.exists():
        print("❌ ~/.openclaw/.env does not exist")
        return False

    if not is_gpg_available():
        print("❌ GPG is not installed")
        print("   Install: sudo apt install gnupg")
        print("   Then run: ./scripts/setup-gpg.sh")
        return False

    # Get passphrase once for the whole operation
    passphrase = _get_passphrase()

    # Load current .env
    env_data = load_env(env_file)
    env_lines = read_env_lines(env_file)

    # Load existing secrets
    secrets = load_secrets(secrets_file, passphrase)

    encrypted = []
    not_found = []

    for key in key_names:
        key = key.strip()
        if key not in env_data:
            not_found.append(key)
            continue

        value = env_data[key]

        # Skip if already encrypted
        if value.startswith('GPG:'):
            print(f"   ⏭️  {key}: already encrypted")
            continue

        # Move value to secrets
        secrets[key] = value
        encrypted.append(key)

        # Replace in .env lines with GPG placeholder
        for i, line in enumerate(env_lines):
            stripped = line.strip()
            if stripped.startswith(f'{key}=') and not stripped.startswith('#'):
                env_lines[i] = f"{key}=GPG:{key}\n"
                break

    if not_found:
        print(f"\n⚠️  Keys not found in .env: {', '.join(not_found)}")

    if not encrypted:
        print("\n✅ No new keys to encrypt")
        return True

    # Save encrypted secrets
    print(f"\n🔐 Encrypting {len(encrypted)} key(s)...")
    if not save_secrets(secrets_file, secrets, passphrase):
        return False

    # Update .env with GPG placeholders
    write_env_lines(env_file, env_lines)

    print(f"   ✅ Encrypted: {', '.join(encrypted)}")
    print(f"   📁 Secrets: {secrets_file}")
    print(f"   📝 .env updated with GPG: placeholders")

    return True


def decrypt_keys(key_names: list):
    """Decrypt specified keys back from GPG to plaintext .env."""
    home = Path.home()
    env_file = home / '.openclaw' / '.env'
    secrets_file = home / '.openclaw' / '.env.secrets.gpg'

    if not secrets_file.exists():
        print("❌ No GPG secrets file found")
        return False

    # Get passphrase once
    passphrase = _get_passphrase()

    env_data = load_env(env_file)
    env_lines = read_env_lines(env_file)
    secrets = load_secrets(secrets_file, passphrase)

    decrypted = []

    for key in key_names:
        key = key.strip()
        value = env_data.get(key, '')

        if not value.startswith('GPG:'):
            print(f"   ⏭️  {key}: not GPG-encrypted")
            continue

        if key not in secrets:
            print(f"   ⚠️  {key}: not found in GPG secrets")
            continue

        # Restore value in .env
        for i, line in enumerate(env_lines):
            stripped = line.strip()
            if stripped.startswith(f'{key}=') and not stripped.startswith('#'):
                env_lines[i] = f"{key}={secrets[key]}\n"
                break

        # Remove from secrets
        del secrets[key]
        decrypted.append(key)

    if not decrypted:
        print("\n✅ No keys to decrypt")
        return True

    # Update secrets file (or remove if empty)
    if secrets:
        save_secrets(secrets_file, secrets, passphrase)
    else:
        secrets_file.unlink()
        print("   🗑️  Removed empty secrets file")

    # Update .env
    write_env_lines(env_file, env_lines)

    print(f"\n🔓 Decrypted {len(decrypted)} key(s): {', '.join(decrypted)}")

    return True


def list_encrypted():
    """List currently encrypted keys."""
    home = Path.home()
    env_file = home / '.openclaw' / '.env'

    if not env_file.exists():
        print("❌ ~/.openclaw/.env does not exist")
        return

    env_data = load_env(env_file)
    gpg_keys = [k for k, v in env_data.items() if v.startswith('GPG:')]

    if gpg_keys:
        print(f"\n🔐 GPG-encrypted keys ({len(gpg_keys)}):\n")
        for key in sorted(gpg_keys):
            print(f"   • {key}")

        secrets_file = home / '.openclaw' / '.env.secrets.gpg'
        if secrets_file.exists():
            print(f"\n   📁 Secrets file: {secrets_file}")
            mode = oct(secrets_file.stat().st_mode)[-3:]
            status = "✅" if mode == '600' else f"⚠️  mode {mode}"
            print(f"   🔒 Permissions: {status}")
        else:
            print(f"\n   ⚠️  Secrets file missing!")
    else:
        print("\n📋 No GPG-encrypted keys found in .env")


def main():
    parser = argparse.ArgumentParser(description='GPG encryption for high-value secrets')
    parser.add_argument('--keys', help='Comma-separated list of keys to encrypt/decrypt')
    parser.add_argument('--list', action='store_true', help='List encrypted keys')
    parser.add_argument('--decrypt', action='store_true', help='Decrypt keys back to plaintext')
    args = parser.parse_args()

    if args.list:
        list_encrypted()
        return 0

    if not args.keys:
        parser.print_help()
        print("\n💡 Examples:")
        print("   ./scripts/encrypt.py --keys MAIN_WALLET_PRIVATE_KEY,FARCASTER_CUSTODY_PRIVATE_KEY")
        print("   ./scripts/encrypt.py --list")
        print("   ./scripts/encrypt.py --decrypt --keys MAIN_WALLET_PRIVATE_KEY")
        return 1

    key_list = [k.strip() for k in args.keys.split(',')]

    if args.decrypt:
        success = decrypt_keys(key_list)
    else:
        success = encrypt_keys(key_list)

    return 0 if success else 1


if __name__ == '__main__':
    exit(main())
