#!/usr/bin/env python3
"""
Validate Grant Token

Check if a permission grant token is valid and not expired.

Usage:
    python validate_token.py TOKEN

Example:
    python validate_token.py grant_a1b2c3d4e5f6
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

GRANTS_FILE = Path(__file__).parent.parent / "data" / "active_grants.json"


def validate_token(token: str) -> dict[str, Any]:
    """Validate a grant token and return its details."""
    if not GRANTS_FILE.exists():
        return {
            "valid": False,
            "reason": "No grants file found"
        }
    
    try:
        grants = json.loads(GRANTS_FILE.read_text())
    except json.JSONDecodeError:
        return {
            "valid": False,
            "reason": "Invalid grants file"
        }
    
    if token not in grants:
        return {
            "valid": False,
            "reason": "Token not found"
        }
    
    grant = grants[token]
    
    # Check expiration
    expires_at = grant.get("expires_at")
    if expires_at:
        try:
            expiry = datetime.fromisoformat(str(expires_at).replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            
            if now > expiry:
                return {
                    "valid": False,
                    "reason": "Token has expired",
                    "expired_at": expires_at
                }
        except Exception:
            pass  # unparseable expiry field — treat token as non-expired
    
    return {
        "valid": True,
        "grant": grant
    }


def main():
    parser = argparse.ArgumentParser(description="Validate a permission grant token")
    parser.add_argument("token", help="Grant token to validate")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    result = validate_token(args.token)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["valid"]:
            grant = result["grant"]
            print("✅ Token is VALID")
            print(f"   Agent: {grant.get('agent_id')}")
            print(f"   Resource: {grant.get('resource_type')}")
            print(f"   Scope: {grant.get('scope', 'N/A')}")
            print(f"   Expires: {grant.get('expires_at')}")
            print(f"   Restrictions: {', '.join(grant.get('restrictions', []))}")
        else:
            print("❌ Token is INVALID")
            print(f"   Reason: {result.get('reason')}")
    
    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
