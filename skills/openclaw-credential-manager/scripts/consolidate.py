#!/usr/bin/env python3
"""
Consolidate credentials into ~/.openclaw/.env
Backs up files with secure permissions (600 files, 700 dirs).
"""

import argparse
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Service-specific key mappings
SERVICE_MAPPINGS = {
    'x': {
        'consumer_key': 'X_CONSUMER_KEY',
        'consumer_secret': 'X_CONSUMER_SECRET',
        'access_token': 'X_ACCESS_TOKEN',
        'access_token_secret': 'X_ACCESS_TOKEN_SECRET',
        'bearer_token': 'X_BEARER_TOKEN',
        'username': 'X_USERNAME',
        'user_id': 'X_USER_ID',
    },
    'farcaster': {
        'custodyPrivateKey': 'FARCASTER_CUSTODY_PRIVATE_KEY',
        'signerPrivateKey': 'FARCASTER_SIGNER_PRIVATE_KEY',
        'signerPublicKey': 'FARCASTER_SIGNER_PUBLIC_KEY',
        'custodyAddress': 'FARCASTER_CUSTODY_ADDRESS',
        'fid': 'FARCASTER_FID',
        'fname': 'FARCASTER_FNAME',
    },
    'molten': {
        'api_key': 'MOLTEN_API_KEY',
        'agent_name': 'MOLTEN_AGENT_NAME',
        'agent_id': 'MOLTEN_AGENT_ID',
    },
    'moltbook': {
        'api_key': 'MOLTBOOK_API_KEY',
        'agent_name': 'MOLTBOOK_AGENT_NAME',
        'profile_url': 'MOLTBOOK_PROFILE_URL',
    },
    'botchan': {
        'api_key': 'BOTCHAN_API_KEY',
        'agent_name': 'BOTCHAN_AGENT_NAME',
    },
    '4claw': {
        'api_key': 'BOTCHAN_API_KEY',
        'name': 'BOTCHAN_AGENT_NAME',
    },
}


def detect_service(path: Path, data: Dict) -> str:
    """Detect service from path or data keys."""
    path_str = str(path).lower()

    # Check path
    for service in SERVICE_MAPPINGS:
        if service in path_str:
            return service

    # Check data keys
    keys = set(k.lower() for k in data.keys())
    if 'consumer_key' in keys or 'consumer_secret' in keys:
        return 'x'
    if 'custodyprivatekey' in keys or 'signerprivatekey' in keys:
        return 'farcaster'
    if 'agent_id' in keys and 'api_key' in keys:
        if 'molten' in str(data.get('api_key', '')):
            return 'molten'
        if 'moltbook' in str(data.get('api_key', '')):
            return 'moltbook'

    return 'generic'


def normalize_key(key: str, service: str) -> str:
    """Normalize a key to ENV format."""
    if service in SERVICE_MAPPINGS:
        mapping = SERVICE_MAPPINGS[service]
        if key in mapping:
            return mapping[key]

    # Generic normalization
    env_key = key.upper()
    env_key = env_key.replace('-', '_')
    env_key = env_key.replace(' ', '_')

    # Add service prefix if not generic
    if service != 'generic' and not env_key.startswith(service.upper()):
        env_key = f"{service.upper()}_{env_key}"

    return env_key


def backup_files(files: List[Path], backup_dir: Path):
    """Backup files before modification with secure permissions."""
    backup_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(backup_dir, 0o700)

    # Also secure parent backup dir
    parent = backup_dir.parent
    if parent.name == 'backups':
        os.chmod(parent, 0o700)

    for file in files:
        if file.exists():
            backup_name = file.name + '.bak'
            if '/' in str(file):
                rel_parts = file.relative_to(Path.home()).parts
                backup_name = '-'.join(rel_parts) + '.bak'

            backup_path = backup_dir / backup_name
            shutil.copy2(file, backup_path)
            os.chmod(backup_path, 0o600)
            print(f"   📦 Backed up: {file} → {backup_path}")


def load_credentials(path: Path) -> Dict:
    """Load credentials from a file."""
    if path.suffix == '.json':
        with open(path) as f:
            data = json.load(f)
        # Flatten nested dicts for .env compatibility
        flat = {}
        for k, v in data.items() if isinstance(data, dict) else []:
            if isinstance(v, (dict, list)):
                flat[k] = json.dumps(v, separators=(',', ':'))
            else:
                flat[k] = str(v)
        return flat if flat else (data if isinstance(data, dict) else {})
    elif '.env' in path.name:
        creds = {}
        with open(path) as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, val = line.split('=', 1)
                    creds[key.strip()] = val.strip()
        return creds
    return {}


def consolidate(service_filter: str = None, backup_only: bool = False,
                auto_yes: bool = False) -> Dict:
    """Consolidate credentials into .env"""
    home = Path.home()
    openclaw_dir = home / '.openclaw'
    env_file = openclaw_dir / '.env'
    env_example = openclaw_dir / '.env.example'
    backup_dir = openclaw_dir / 'backups' / f'credentials-old-{datetime.now().strftime("%Y%m%d")}'

    # Scan for files
    from scan import scan_locations
    results = scan_locations()

    if not results:
        print("✅ No credential files found to migrate")
        return {'status': 'no_files'}

    print(f"\n📋 Found {len(results)} credential file(s) to migrate\n")

    # Backup existing .env
    if env_file.exists():
        backup_files([env_file], backup_dir)

    # Load existing .env if present
    env_data = {}
    if env_file.exists():
        env_data = load_credentials(env_file)
        print(f"   📝 Loading existing .env ({len(env_data)} keys)")

    # Process each file
    files_to_backup = []
    new_keys = {}

    for result in results:
        path = Path(result['path'])
        if not path.exists() or path == env_file:
            continue

        # Skip symlinks that point to main .env
        if path.is_symlink() and path.resolve() == env_file:
            continue

        print(f"\n🔍 Processing: {path}")

        try:
            data = load_credentials(path)
            service = detect_service(path, data)

            if service_filter and service != service_filter:
                print(f"   ⏭️  Skipping (service filter)")
                continue

            print(f"   🏷️  Detected service: {service}")

            for key, value in data.items():
                env_key = normalize_key(key, service)
                if env_key not in env_data:
                    new_keys[env_key] = value
                    print(f"      {key} → {env_key}")

            files_to_backup.append(path)

        except Exception as e:
            print(f"   ❌ Error: {e}")

    if not new_keys and not backup_only:
        print("\n✅ No new credentials to add")
        return {'status': 'no_new_keys'}

    # Confirm
    if not auto_yes and not backup_only:
        print(f"\n📊 Summary:")
        print(f"   New keys to add: {len(new_keys)}")
        print(f"   Files to backup: {len(files_to_backup)}")
        response = input("\n   Proceed? [y/N] ")
        if response.lower() != 'y':
            print("   ❌ Cancelled")
            return {'status': 'cancelled'}

    # Backup files
    if files_to_backup:
        print(f"\n📦 Backing up {len(files_to_backup)} file(s)...")
        backup_files(files_to_backup, backup_dir)

    if backup_only:
        print(f"\n✅ Backup complete: {backup_dir}")
        return {'status': 'backup_only', 'backup_dir': str(backup_dir)}

    # Write .env
    print(f"\n✍️  Writing .env...")
    openclaw_dir.mkdir(parents=True, exist_ok=True)

    # Merge and write
    env_data.update(new_keys)

    with open(env_file, 'w') as f:
        f.write("# OpenClaw Agent Credentials\n")
        f.write("# Generated by credential-manager skill\n\n")

        # Group by service
        services = {}
        for key, value in sorted(env_data.items()):
            service = key.split('_')[0] if '_' in key else 'OTHER'
            if service not in services:
                services[service] = []
            services[service].append((key, value))

        for service, items in sorted(services.items()):
            f.write(f"# {service}\n")
            for key, value in items:
                f.write(f"{key}={value}\n")
            f.write("\n")

    # Set permissions
    os.chmod(env_file, 0o600)
    print(f"   🔒 Set permissions: 600")

    # Create .env.example
    with open(env_example, 'w') as f:
        f.write("# OpenClaw Agent Credentials Template\n")
        f.write("# Copy to .env and fill in your actual values\n\n")
        for key in sorted(env_data.keys()):
            f.write(f"{key}=your_value_here\n")

    print(f"   📄 Created .env.example")

    # Update .gitignore
    gitignore = openclaw_dir / '.gitignore'
    gitignore_entries = ['.env', '.env.secrets.gpg', '.env.meta']
    if gitignore.exists():
        content = gitignore.read_text()
    else:
        content = ''

    missing = [e for e in gitignore_entries if e not in content]
    if missing:
        with open(gitignore, 'a') as f:
            f.write("\n# Credentials\n")
            for entry in missing:
                f.write(f"{entry}\n")
        print(f"   🚫 Updated .gitignore")

    print(f"\n✅ Migration complete!")
    print(f"   📁 Credentials: {env_file}")
    print(f"   📦 Backups: {backup_dir}")
    print(f"\n💡 Next: Run ./scripts/validate.py to verify security")

    return {
        'status': 'success',
        'env_file': str(env_file),
        'backup_dir': str(backup_dir),
        'keys_added': len(new_keys),
    }


def main():
    parser = argparse.ArgumentParser(description='Consolidate credentials')
    parser.add_argument('--service', help='Filter by service')
    parser.add_argument('--backup-only', action='store_true',
                        help='Backup files without consolidating')
    parser.add_argument('--yes', '-y', action='store_true',
                        help='Auto-confirm all prompts')
    args = parser.parse_args()

    result = consolidate(args.service, args.backup_only, args.yes)
    return 0 if result['status'] in ['success', 'no_files', 'backup_only'] else 1


if __name__ == '__main__':
    exit(main())
