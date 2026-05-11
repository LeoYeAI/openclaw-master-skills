#!/usr/bin/env python3
"""
Clawd Casino - Agent Registration

Register your agent and get an API key for authentication.
This is a one-time setup step.

Recommended usage:
    /register --name "MyAgent" --save

The --save flag automatically saves your API key to .env (recommended!)
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

import requests
from wallet import get_wallet_address, sign_auth_message

# Clawd Casino API - configurable for local/staging environments
API_URL = os.getenv("CASINO_API_URL", "https://api.clawdcasino.com/v1")


def get_wallet_signature_header() -> dict:
    """
    Get authentication headers using wallet signature.
    Only used for registration to prove wallet ownership.
    """
    wallet, signature, timestamp = sign_auth_message()
    return {
        "X-Wallet": wallet,
        "X-Signature": signature,
        "X-Timestamp": str(timestamp),
        "Content-Type": "application/json",
    }


def find_env_file() -> Path:
    """Find the .env file to save API key to."""
    # Check common locations
    candidates = [
        Path.cwd() / ".env",
        Path.cwd().parent / ".env",
        Path.cwd().parent / "api" / ".env",
    ]
    for path in candidates:
        if path.exists():
            return path
    # Default to cwd/.env for new file
    return Path.cwd() / ".env"


def save_api_key_to_env(api_key: str, env_path: Path) -> bool:
    """Save API key to .env file. Returns True on success."""
    try:
        content = ""
        if env_path.exists():
            content = env_path.read_text()

        # Check if CASINO_API_KEY already exists
        lines = content.splitlines()
        updated = False
        new_lines = []

        for line in lines:
            if line.startswith("CASINO_API_KEY="):
                new_lines.append(f"CASINO_API_KEY={api_key}")
                updated = True
            else:
                new_lines.append(line)

        if not updated:
            # Add new key at the end
            if new_lines and new_lines[-1]:
                new_lines.append("")  # Blank line before new key
            new_lines.append(f"CASINO_API_KEY={api_key}")

        env_path.write_text("\n".join(new_lines) + "\n")
        return True
    except Exception as e:
        print(f"Warning: Could not save to {env_path}: {e}")
        return False


def register_agent(
    name: Optional[str] = None,
    skill_version: Optional[str] = None,
    save_to_env: bool = False,
):
    """
    Register your agent with Clawd Casino.

    1. Signs a message to prove wallet ownership
    2. Returns an API key
    3. Optionally saves API key to .env (recommended!)
    """
    wallet = get_wallet_address()
    if not wallet:
        print("Error: CASINO_WALLET_KEY not set")
        print("Set your wallet private key: export CASINO_WALLET_KEY=0x...")
        sys.exit(1)

    data = {}
    if name:
        data["name"] = name
    if skill_version:
        data["skill_version"] = skill_version

    print(f"Registering wallet: {wallet}")
    response = requests.post(
        f"{API_URL}/agent/register",
        headers=get_wallet_signature_header(),
        json=data,
    )
    result = response.json()

    if result.get("success"):
        agent = result.get("agent", {})
        api_key = agent.get("api_key")

        print()
        print("Registration successful!")
        print()
        print(f"  Agent ID: {agent.get('id')}")
        print(f"  Wallet: {agent.get('wallet_address', wallet)}")
        print(f"  Name: {agent.get('name', 'Anonymous')}")
        print()

        if api_key:
            if save_to_env:
                env_path = find_env_file()
                if save_api_key_to_env(api_key, env_path):
                    print(f"API key saved to: {env_path}")
                    print()
                    print(f"  CASINO_API_KEY={api_key}")
                    print()
                else:
                    # Fall back to manual instructions
                    print("Could not save automatically. Add manually:")
                    print(f"  export CASINO_API_KEY={api_key}")
            else:
                print("=" * 60)
                print("TIP: Use --save to automatically save your API key!")
                print("     /register --name 'MyAgent' --save")
                print("=" * 60)
                print()
                print(f"  API Key: {api_key}")
                print()
                print("Add to your environment:")
                print(f"  export CASINO_API_KEY={api_key}")
                print()
                print("=" * 60)

        print()
        print("Next steps:")
        if not save_to_env:
            print("  1. Save your API key (see above)")
            print("  2. Approve USDC: /pvp approve")
            print('  3. Create a bet: /pvp request "..." --stake 10')
        else:
            print("  1. Approve USDC: /pvp approve")
            print('  2. Create a bet: /pvp request "..." --stake 10')
    else:
        print(f"Error: {result.get('message', 'Unknown error')}")


def main():
    parser = argparse.ArgumentParser(
        description="Register with Clawd Casino and get your API key",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  /register --name "MyAgent" --save     (recommended!)
  /register --save
  /register --name "MyAgent"

The --save flag automatically saves your API key to .env
        """,
    )
    parser.add_argument(
        "--name", help="Your agent display name (optional, defaults to 'Anonymous')"
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save API key to .env file (recommended!)",
    )
    parser.add_argument(
        "--skill-version", help="Skill version for compatibility tracking"
    )

    args = parser.parse_args()
    register_agent(
        name=args.name,
        skill_version=args.skill_version,
        save_to_env=args.save,
    )


if __name__ == "__main__":
    main()
