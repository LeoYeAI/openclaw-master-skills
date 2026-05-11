#!/usr/bin/env python3
"""
Clawd Casino - Wallet Generator

Generate a new Ethereum/Polygon wallet for your agent.
This is a one-time setup step.

Recommended usage:
    /wallet-gen --save

The --save flag automatically saves your private key to .env
"""

import argparse
import sys
from pathlib import Path

from eth_account import Account


def find_env_file() -> Path:
    """Find the .env file to save wallet key to."""
    candidates = [
        Path.cwd() / ".env",
        Path.cwd().parent / ".env",
        Path.cwd().parent / "api" / ".env",
    ]
    for path in candidates:
        if path.exists():
            return path
    return Path.cwd() / ".env"


def check_existing_wallet(env_path: Path) -> str | None:
    """Check if CASINO_WALLET_KEY already exists in .env."""
    if not env_path.exists():
        return None

    content = env_path.read_text()
    for line in content.splitlines():
        if line.startswith("CASINO_WALLET_KEY="):
            key = line.split("=", 1)[1].strip()
            if key and key != "0x":
                return key
    return None


def save_wallet_to_env(private_key: str, env_path: Path) -> bool:
    """Save wallet private key to .env file. Returns True on success."""
    try:
        content = ""
        if env_path.exists():
            content = env_path.read_text()

        lines = content.splitlines()
        updated = False
        new_lines = []

        for line in lines:
            if line.startswith("CASINO_WALLET_KEY="):
                new_lines.append(f"CASINO_WALLET_KEY={private_key}")
                updated = True
            else:
                new_lines.append(line)

        if not updated:
            if new_lines and new_lines[-1]:
                new_lines.append("")
            new_lines.append(f"CASINO_WALLET_KEY={private_key}")

        env_path.write_text("\n".join(new_lines) + "\n")
        return True
    except Exception as e:
        print(f"Warning: Could not save to {env_path}: {e}")
        return False


def generate_wallet(save_to_env: bool = False, force: bool = False):
    """
    Generate a new Ethereum/Polygon wallet.

    1. Creates a new random wallet
    2. Displays address and private key
    3. Optionally saves to .env
    """
    env_path = find_env_file()

    # Check for existing wallet
    if save_to_env and not force:
        existing = check_existing_wallet(env_path)
        if existing:
            print("=" * 60)
            print("WARNING: CASINO_WALLET_KEY already exists in .env!")
            print("=" * 60)
            print()
            print(f"Existing key: {existing[:10]}...{existing[-6:]}")
            print()
            print("To overwrite, run with --force:")
            print("  /wallet-gen --save --force")
            print()
            print("This will PERMANENTLY replace your existing wallet.")
            print("Make sure you have backed up the old key!")
            print("=" * 60)
            sys.exit(1)

    # Generate new wallet
    account = Account.create()
    private_key = account.key.hex()
    address = account.address

    print()
    print("New wallet generated!")
    print()
    print(f"  Address:     {address}")
    print(f"  Private Key: {private_key}")
    print()

    if save_to_env:
        if save_wallet_to_env(private_key, env_path):
            print(f"Wallet saved to: {env_path}")
            print()
        else:
            print("Could not save automatically. Add manually:")
            print(f"  export CASINO_WALLET_KEY={private_key}")
            print()
    else:
        print("=" * 60)
        print("TIP: Use --save to automatically save to .env!")
        print("     /wallet-gen --save")
        print("=" * 60)
        print()
        print("Or add manually:")
        print(f"  export CASINO_WALLET_KEY={private_key}")
        print()

    print("=" * 60)
    print("IMPORTANT: Back up your private key!")
    print("If you lose it, you lose access to your wallet forever.")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Fund wallet with USDC on Polygon")
    print("  2. Register: /register --name 'MyAgent' --save")
    print("  3. Approve: /pvp approve")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a new wallet for Clawd Casino",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  /wallet-gen --save              (recommended!)
  /wallet-gen --save --force      (overwrite existing)
  /wallet-gen                     (display only)

The --save flag automatically saves your private key to .env
        """,
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save private key to .env file (recommended!)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing wallet key (use with caution!)",
    )

    args = parser.parse_args()
    generate_wallet(save_to_env=args.save, force=args.force)


if __name__ == "__main__":
    main()
