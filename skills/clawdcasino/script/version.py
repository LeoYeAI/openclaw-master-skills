#!/usr/bin/env python3
"""
Clawd Casino - Skill Version Check

Check if your skill is up to date before starting a session.
If outdated, you should update to get the latest features and fixes.
"""

import argparse
import os
import sys

import requests

# Clawd Casino API - configurable for local/staging environments
API_URL = os.getenv("CASINO_API_URL", "https://api.clawdcasino.com/v1")

# Local skill version - should match SKILL.md
LOCAL_VERSION = "1.4.0"


def check_version(quiet: bool = False):
    """
    Check if the local skill version matches the server version.
    Returns True if up to date, False if update needed.
    """
    try:
        response = requests.get(f"{API_URL}/skill/version", timeout=10)
        result = response.json()

        server_version = result.get("version", "unknown")
        skill_name = result.get("name", "clawdcasino")
        changelog = result.get("changelog")

        if quiet:
            # Machine-readable output for scripts
            if server_version == LOCAL_VERSION:
                print("up_to_date")
                return True
            else:
                print(f"update_available:{server_version}")
                return False

        # Human-readable output
        print(f"Skill: {skill_name}")
        print(f"Local version:  {LOCAL_VERSION}")
        print(f"Server version: {server_version}")
        print()

        if server_version == LOCAL_VERSION:
            print("✓ Your skill is up to date!")
            return True
        else:
            print("⚠ Update available!")
            print()
            print(f"Your version ({LOCAL_VERSION}) differs from server ({server_version}).")
            print("Please update your skill to get the latest features and fixes.")
            if changelog:
                print()
                print(f"What's new: {changelog}")
            return False

    except requests.exceptions.RequestException as e:
        if quiet:
            print(f"error:{e}")
        else:
            print(f"Error checking version: {e}")
            print("Could not reach the Clawd Casino API.")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Check if your Clawd Casino skill is up to date",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  /version              Check skill version (human-readable)
  /version --quiet      Check skill version (machine-readable)

Always run this before starting a betting session to ensure
you have the latest features and bug fixes.
        """,
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Machine-readable output (up_to_date, update_available:<version>, or error:<msg>)"
    )

    args = parser.parse_args()
    is_current = check_version(quiet=args.quiet)

    # Exit with code 0 if up to date, 1 if update needed
    sys.exit(0 if is_current else 1)


if __name__ == "__main__":
    main()
