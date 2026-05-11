#!/usr/bin/env python3
"""
katbot_onboard.py — Interactive onboarding wizard for the Katbot.ai OpenClaw skill.

This script:
  1. Prompts for your MetaMask wallet private key (never stored to disk)
  2. Authenticates with api.katbot.ai via SIWE
  3. Lists existing portfolios or creates a new Hyperliquid one
  4. Saves the agent private key + config to ~/.openclaw/workspace/katbot-identity/
  5. Prints env var export lines to add to your shell profile

Usage:
  python3 {baseDir}/tools/katbot_onboard.py
  python3 {baseDir}/tools/katbot_onboard.py --base-url https://api.katbot.ai
  python3 {baseDir}/tools/katbot_onboard.py --identity-dir /custom/path
"""

import argparse
import getpass
import json
import os
import sys
import requests
from eth_account import Account
from eth_account.messages import encode_defunct

DEFAULT_BASE_URL = "https://api.katbot.ai"
DEFAULT_IDENTITY_DIR = os.getenv("KATBOT_IDENTITY_DIR", os.path.expanduser("~/.openclaw/workspace/katbot-identity"))
DEFAULT_CHAIN_ID = 42161  # Arbitrum


def color(text: str, code: str) -> str:
    """Wrap text in ANSI color codes if stdout is a TTY."""
    if sys.stdout.isatty():
        return f"\033[{code}m{text}\033[0m"
    return text


def green(t): return color(t, "32")
def yellow(t): return color(t, "33")
def red(t): return color(t, "31")
def bold(t): return color(t, "1")
def cyan(t): return color(t, "36")


def banner():
    print()
    print(bold("╔══════════════════════════════════════════╗"))
    print(bold("║   Katbot.ai OpenClaw Skill — Onboarding  ║"))
    print(bold("╚══════════════════════════════════════════╝"))
    print()


def siwe_login(base_url: str, private_key: str, chain_id: int) -> tuple[str, str, str]:
    """Authenticate with SIWE. Returns (access_token, refresh_token, wallet_address)."""
    account = Account.from_key(private_key)
    address = account.address

    print(f"  Wallet address : {cyan(address)}")
    print(f"  Authenticating with {base_url} ...")

    # Step 1: Get nonce
    r = requests.get(f"{base_url}/get-nonce/{address}?chain_id={chain_id}", timeout=15)
    r.raise_for_status()
    message_text = r.json()["message"]

    # Step 2: Sign
    signable = encode_defunct(text=message_text)
    signed = Account.sign_message(signable, private_key)
    signature = signed.signature.hex()

    # Step 3: Login
    r = requests.post(
        f"{base_url}/login",
        json={"address": address, "signature": signature, "chain_id": chain_id},
        timeout=15,
    )
    r.raise_for_status()
    resp = r.json()
    access_token = resp["access_token"]
    refresh_token = resp.get("refresh_token", "")
    print(green("  ✅ Authenticated!"))
    return access_token, refresh_token, address


def list_portfolios(base_url: str, token: str) -> list:
    r = requests.get(f"{base_url}/portfolio", headers={"Authorization": f"Bearer {token}"}, timeout=15)
    r.raise_for_status()
    return r.json()


def create_portfolio(base_url: str, token: str, name: str, initial_balance: float, is_testnet: bool) -> dict:
    payload = {
        "name": name,
        "description": f"OpenClaw agent-managed Hyperliquid portfolio ({name})",
        "initial_balance": initial_balance,
        "portfolio_type": "HYPERLIQUID",
        "is_testnet": is_testnet,
        "tokens_selected": ["BTC", "ETH", "SOL"],
    }
    r = requests.post(
        f"{base_url}/portfolio",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()


def save_identity(identity_dir: str, config: dict, agent_private_key: str, jwt_token: str, refresh_token: str = ""):
    """Write katbot_config.json and katbot_token.json to the identity directory."""
    os.makedirs(identity_dir, exist_ok=True)

    config_path = os.path.join(identity_dir, "katbot_config.json")
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    # Store agent private key in a local secrets file (not committed to git)
    secrets_path = os.path.join(identity_dir, "katbot_secrets.json")
    with open(secrets_path, "w") as f:
        json.dump({"agent_private_key": agent_private_key}, f, indent=2)
    os.chmod(secrets_path, 0o600)

    # Save JWT and refresh tokens for reuse
    token_path = os.path.join(identity_dir, "katbot_token.json")
    with open(token_path, "w") as f:
        json.dump({"access_token": jwt_token, "refresh_token": refresh_token}, f, indent=2)
    os.chmod(token_path, 0o600)

    print(green(f"  ✅ Config saved  → {config_path}"))
    print(green(f"  ✅ Secrets saved → {secrets_path} (mode 600)"))
    print(green(f"  ✅ Token saved   → {token_path} (mode 600)"))


def print_env_instructions(wallet_private_key_placeholder: str, agent_private_key: str):
    print()
    print(bold("══════════════════════════════════════════"))
    print(bold(" Security Best Practices"))
    print(bold("══════════════════════════════════════════"))
    print()
    print(yellow("  1. Wallet Key (MetaMask)"))
    print("     This key is used ONLY for onboarding authentication.")
    print("     It is NOT saved to disk and should NOT be exported to your shell environment.")
    print("     If your session expires, simply run this onboarding script again.")
    print()
    print(yellow("  2. Agent Key (Trading)"))
    print(f"     This key has been securely saved to: {os.path.join(DEFAULT_IDENTITY_DIR, 'katbot_secrets.json')}")
    print("     It allows the agent to place trades on your behalf.")
    print("     Do not share this file or export the key unless necessary for automation.")
    print()
    print(yellow("  3. Session Tokens"))
    print("     Your access token and refresh token have been saved to katbot_token.json.")
    print("     The refresh token is valid for 7 days.")
    print("     If you do not use the agent within 7 days, your session will expire")
    print("     and you will need to run this onboarding script again to re-authenticate.")
    print()


def print_hyperliquid_instructions(agent_address: str):
    print()
    print(bold("══════════════════════════════════════════"))
    print(bold(" Authorize your agent on Hyperliquid:"))
    print(bold("══════════════════════════════════════════"))
    print()
    print(f"  Agent address: {cyan(agent_address)}")
    print()
    print("  1. Go to https://app.hyperliquid.xyz → Settings → API")
    print("  2. Add the agent address above as an API Wallet")
    print("  3. Grant trading permissions, set expiry to 180 days")
    print("  4. Confirm the MetaMask transaction")
    print()
    print("  Once authorized, your OpenClaw agent can execute trades on your behalf.")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Interactive onboarding wizard for the Katbot.ai OpenClaw skill."
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help=f"Katbot API base URL (default: {DEFAULT_BASE_URL})")
    parser.add_argument("--identity-dir", default=DEFAULT_IDENTITY_DIR, help=f"Where to save identity files (default: {DEFAULT_IDENTITY_DIR})")
    parser.add_argument("--chain-id", type=int, default=DEFAULT_CHAIN_ID, help=f"EVM chain ID (default: {DEFAULT_CHAIN_ID} = Arbitrum)")
    args = parser.parse_args()

    banner()

    # ── Step 1: Get wallet private key (hidden input) ──────────────────────────
    print(bold("Step 1: Wallet Authentication"))
    print("  Your MetaMask private key is used to sign a SIWE message.")
    print("  It is NEVER stored to disk — only held in memory during this session.")
    print()
    try:
        private_key = getpass.getpass("  Enter MetaMask private key (hidden): ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n  Aborted.")
        sys.exit(0)

    if not private_key.startswith("0x"):
        private_key = "0x" + private_key

    print()

    # ── Step 2: Authenticate ───────────────────────────────────────────────────
    print(bold("Step 2: Authenticating with Katbot.ai"))
    try:
        jwt_token, refresh_token, wallet_address = siwe_login(args.base_url, private_key, args.chain_id)
    except Exception as e:
        print(red(f"  ❌ Authentication failed: {e}"))
        sys.exit(1)

    print()

    # ── Step 3: List or create portfolio ──────────────────────────────────────
    print(bold("Step 3: Portfolio Setup"))
    try:
        portfolios = list_portfolios(args.base_url, jwt_token)
    except Exception as e:
        print(red(f"  ❌ Failed to list portfolios: {e}"))
        sys.exit(1)

    chosen_portfolio = None
    agent_private_key = None

    if portfolios:
        print(f"  Found {len(portfolios)} existing portfolio(s):\n")
        for i, p in enumerate(portfolios):
            testnet_tag = " [testnet]" if p.get("is_testnet") else " [mainnet]"
            print(f"    [{i+1}] {p['name']} (ID: {p['id']}){testnet_tag}")
        print(f"    [{len(portfolios)+1}] Create a new portfolio")
        print()

        while True:
            try:
                choice = input(f"  Choose [1-{len(portfolios)+1}]: ").strip()
                idx = int(choice) - 1
                if 0 <= idx < len(portfolios):
                    chosen_portfolio = portfolios[idx]
                    # Existing portfolio — agent key must come from env or user
                    print()
                    print(yellow("  ⚠️  For existing portfolios, the agent private key was shown at creation time."))
                    try:
                        agent_private_key = getpass.getpass("  Enter agent private key for this portfolio (hidden): ").strip()
                    except (KeyboardInterrupt, EOFError):
                        print("\n  Aborted.")
                        sys.exit(0)
                    if not agent_private_key.startswith("0x"):
                        agent_private_key = "0x" + agent_private_key
                    break
                elif idx == len(portfolios):
                    chosen_portfolio = None  # will create below
                    break
                else:
                    print(red("  Invalid choice."))
            except (ValueError, KeyboardInterrupt):
                print(red("  Invalid choice."))
    else:
        print("  No portfolios found. Let's create one.")

    if chosen_portfolio is None:
        # Create new portfolio
        print()
        try:
            p_name = input("  Portfolio name (e.g. my-hl-mainnet): ").strip() or "my-hl-mainnet"
            testnet_input = input("  Use testnet? [y/N]: ").strip().lower()
            is_testnet = testnet_input in ("y", "yes")
            balance_input = input("  Initial balance in USD (e.g. 1000): ").strip()
            initial_balance = float(balance_input) if balance_input else 1000.0
        except (KeyboardInterrupt, EOFError):
            print("\n  Aborted.")
            sys.exit(0)

        print()
        print(f"  Creating portfolio '{p_name}' ({'testnet' if is_testnet else 'mainnet'}, ${initial_balance:.2f}) ...")
        try:
            new_p = create_portfolio(args.base_url, jwt_token, p_name, initial_balance, is_testnet)
        except Exception as e:
            print(red(f"  ❌ Portfolio creation failed: {e}"))
            sys.exit(1)

        chosen_portfolio = new_p
        agent_private_key = new_p.get("agent_private_key")

        print(green(f"  ✅ Portfolio created! ID: {new_p['id']}"))
        print(green(f"  Agent address    : {new_p.get('agent_address', 'N/A')}"))
        print()
        print(yellow("  ⚠️  The agent private key is shown only once. It has been saved locally."))

    print()

    # ── Step 4: Save identity files ───────────────────────────────────────────
    print(bold("Step 4: Saving Identity Files"))

    config = {
        "base_url": args.base_url,
        "wallet_address": wallet_address,
        "portfolio_id": chosen_portfolio["id"],
        "portfolio_name": chosen_portfolio.get("name", ""),
        "chain_id": args.chain_id,
    }

    save_identity(args.identity_dir, config, agent_private_key, jwt_token, refresh_token)

    # ── Step 5: Instructions ───────────────────────────────────────────────────
    print()
    print(bold("Step 5: Final Setup"))

    agent_address = chosen_portfolio.get("agent_address")
    if agent_address:
        print_hyperliquid_instructions(agent_address)

    print_env_instructions(wallet_address, agent_private_key)

    # ── Done ───────────────────────────────────────────────────────────────────
    print(bold("══════════════════════════════════════════"))
    print(bold(" ✅ Onboarding complete!"))
    print(bold("══════════════════════════════════════════"))
    print()
    print(f"  Identity dir : {cyan(args.identity_dir)}")
    print(f"  Portfolio ID : {cyan(str(chosen_portfolio['id']))}")
    print(f"  Portfolio    : {cyan(chosen_portfolio.get('name', ''))}")
    print()
    print("  Your OpenClaw agent is ready to trade. Try:")
    print(cyan("    \"How's the market looking?\""))
    print(cyan("    \"Run the trading workflow\""))
    print(cyan("    \"How's my portfolio doing?\""))
    print()


if __name__ == "__main__":
    main()
