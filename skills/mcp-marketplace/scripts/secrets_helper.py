#!/usr/bin/env python3
"""Detect available secrets managers and generate store/retrieve commands."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys


def detect_managers() -> list[dict]:
    """Detect available secrets managers on the system."""
    managers = []

    # Check 1Password CLI
    if shutil.which("op"):
        available = False
        try:
            result = subprocess.run(
                ["op", "account", "list", "--format=json"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                accounts = json.loads(result.stdout)
                if accounts:
                    available = True
        except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
            pass

        managers.append({
            "name": "1password",
            "displayName": "1Password CLI",
            "command": "op",
            "available": available,
            "note": "Signed in" if available else "CLI found but not signed in — run 'op signin' first",
        })

    # Check macOS Keychain
    if shutil.which("security"):
        managers.append({
            "name": "keychain",
            "displayName": "macOS Keychain",
            "command": "security",
            "available": True,
            "note": "Always available on macOS",
        })

    return managers


def generate_store_command(manager: str, service_name: str, env_var: str) -> dict:
    """Generate the command to store a secret."""
    if manager == "1password":
        return {
            "manager": "1password",
            "storeCommand": f'op item create --category=api-credential --title "MCP: {service_name}" --vault=Private "credential=<your-token>"',
            "retrieveCommand": f'op read "op://Private/MCP: {service_name}/credential"',
            "shellIntegration": f'export {env_var}=$(op read "op://Private/MCP: {service_name}/credential")',
            "note": "Add the export line to ~/.zshrc for automatic retrieval on shell start",
        }
    elif manager == "keychain":
        return {
            "manager": "keychain",
            "storeCommand": f'security add-generic-password -a mcp -s "{service_name}" -w "<your-token>"',
            "retrieveCommand": f'security find-generic-password -a mcp -s "{service_name}" -w',
            "shellIntegration": f'export {env_var}=$(security find-generic-password -a mcp -s "{service_name}" -w)',
            "note": "Add the export line to ~/.zshrc for automatic retrieval on shell start",
        }
    else:
        return {"error": f"Unknown manager: {manager}"}


def main():
    parser = argparse.ArgumentParser(description="Detect and use secrets managers for MCP tokens")
    parser.add_argument("--action", required=True, choices=["detect", "store-command"], help="Action to perform")
    parser.add_argument("--manager", default=None, choices=["1password", "keychain"], help="Secrets manager to use")
    parser.add_argument("--service", default=None, help="Service name (e.g., 'github', 'slack')")
    parser.add_argument("--env-var", default=None, help="Environment variable name")
    args = parser.parse_args()

    if args.action == "detect":
        managers = detect_managers()
        output = {
            "action": "detect-managers",
            "managersFound": len(managers),
            "managers": managers,
        }
        json.dump(output, sys.stdout, indent=2)
        print()

    elif args.action == "store-command":
        if not all([args.manager, args.service, args.env_var]):
            json.dump(
                {"error": "store-command requires --manager, --service, and --env-var"},
                sys.stdout, indent=2,
            )
            print()
            sys.exit(1)
        result = generate_store_command(args.manager, args.service, args.env_var)
        json.dump(result, sys.stdout, indent=2)
        print()


if __name__ == "__main__":
    main()
