#!/usr/bin/env python3
"""Didit Account Setup - Register, verify, and login programmatically.

Usage:
    python scripts/setup_account.py register <email> <password>
    python scripts/setup_account.py verify <email> <code>
    python scripts/setup_account.py login <email> <password>

Environment:
    No environment variables needed for register/verify/login.

Examples:
    python scripts/setup_account.py register dev@gmail.com 'MyStr0ng!Pass'
    python scripts/setup_account.py verify dev@gmail.com A3K9F2
    python scripts/setup_account.py login dev@gmail.com 'MyStr0ng!Pass'
"""
import argparse
import json
import sys

import requests

AUTH_BASE_URL = "https://apx.didit.me/auth/v2"


def register(email: str, password: str) -> dict:
    response = requests.post(
        f"{AUTH_BASE_URL}/programmatic/register/",
        headers={"Content-Type": "application/json"},
        json={"email": email, "password": password},
        timeout=30,
    )
    if response.status_code == 201:
        return response.json()
    print(f"Error {response.status_code}: {response.text}", file=sys.stderr)
    sys.exit(1)


def verify_email(email: str, code: str) -> dict:
    response = requests.post(
        f"{AUTH_BASE_URL}/programmatic/verify-email/",
        headers={"Content-Type": "application/json"},
        json={"email": email, "code": code},
        timeout=30,
    )
    if response.status_code == 200:
        return response.json()
    print(f"Error {response.status_code}: {response.text}", file=sys.stderr)
    sys.exit(1)


def login(email: str, password: str) -> dict:
    response = requests.post(
        f"{AUTH_BASE_URL}/programmatic/login/",
        headers={"Content-Type": "application/json"},
        json={"email": email, "password": password},
        timeout=30,
    )
    if response.status_code == 200:
        return response.json()
    print(f"Error {response.status_code}: {response.text}", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Didit account setup")
    sub = parser.add_subparsers(dest="command", required=True)

    reg_p = sub.add_parser("register", help="Register a new account")
    reg_p.add_argument("email", help="Email address")
    reg_p.add_argument("password", help="Password (min 8 chars, 1 upper, 1 lower, 1 digit, 1 special)")

    ver_p = sub.add_parser("verify", help="Verify email with OTP code")
    ver_p.add_argument("email", help="Email used during registration")
    ver_p.add_argument("code", help="6-character code from email")

    log_p = sub.add_parser("login", help="Login to existing account")
    log_p.add_argument("email", help="Account email")
    log_p.add_argument("password", help="Account password")

    args = parser.parse_args()

    if args.command == "register":
        result = register(args.email, args.password)
        print(json.dumps(result, indent=2))
        print(f"\n--- Check {args.email} for your 6-character verification code ---")

    elif args.command == "verify":
        result = verify_email(args.email, args.code)
        print(json.dumps(result, indent=2))
        api_key = result.get("application", {}).get("api_key", "")
        org_uuid = result.get("organization", {}).get("uuid", "")
        app_uuid = result.get("application", {}).get("uuid", "")
        print(f"\n--- Account ready! ---")
        print(f"API Key:  {api_key}")
        print(f"Org UUID: {org_uuid}")
        print(f"App UUID: {app_uuid}")
        print(f"\nSet this in your environment:")
        print(f'  export DIDIT_API_KEY="{api_key}"')

    elif args.command == "login":
        result = login(args.email, args.password)
        print(json.dumps(result, indent=2))
        print(f"\n--- Login successful. Access token expires in {result.get('expires_in', '?')}s ---")


if __name__ == "__main__":
    main()
