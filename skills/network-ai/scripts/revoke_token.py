#!/usr/bin/env python3
"""
Revoke Grant Token & TTL Enforcement

Revoke permission tokens and automatically cleanup expired grants.

Usage:
    python revoke_token.py TOKEN           # Revoke specific token
    python revoke_token.py --cleanup       # Remove all expired tokens
    python revoke_token.py --list-expired  # List expired tokens without removing

Example:
    python revoke_token.py grant_a1b2c3d4e5f6
    python revoke_token.py --cleanup --json
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

GRANTS_FILE = Path(__file__).parent.parent / "data" / "active_grants.json"
AUDIT_LOG = Path(__file__).parent.parent / "data" / "audit_log.jsonl"


def log_audit(action: str, details: dict[str, Any]) -> None:
    """Append entry to audit log."""
    AUDIT_LOG.parent.mkdir(exist_ok=True)
    entry: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "details": details
    }
    with open(AUDIT_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


def revoke_token(token: str) -> dict[str, Any]:
    """Revoke a grant token."""
    if not GRANTS_FILE.exists():
        return {
            "revoked": False,
            "reason": "No grants file found"
        }
    
    try:
        grants = json.loads(GRANTS_FILE.read_text())
    except json.JSONDecodeError:
        return {
            "revoked": False,
            "reason": "Invalid grants file"
        }
    
    if token not in grants:
        return {
            "revoked": False,
            "reason": "Token not found"
        }
    
    grant = grants.pop(token)
    GRANTS_FILE.write_text(json.dumps(grants, indent=2))
    
    log_audit("permission_revoked", {
        "token": token,
        "original_grant": grant
    })
    
    return {
        "revoked": True,
        "grant": grant
    }


def is_token_expired(grant: dict[str, Any]) -> bool:
    """Check if a grant token has expired."""
    expires_at = grant.get("expires_at")
    if not expires_at:
        return False
    try:
        expiry_time = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        return datetime.now(timezone.utc) > expiry_time
    except (ValueError, AttributeError):
        return False


def list_expired_tokens() -> dict[str, Any]:
    """List all expired tokens without removing them."""
    if not GRANTS_FILE.exists():
        return {"expired_tokens": [], "total_grants": 0}
    
    try:
        grants = json.loads(GRANTS_FILE.read_text())
    except json.JSONDecodeError:
        return {"error": "Invalid grants file"}
    
    expired: list[dict[str, Any]] = []
    now = datetime.now(timezone.utc)
    
    for token, grant in grants.items():
        if is_token_expired(grant):
            expired.append({
                "token": token,
                "agent": grant.get("agent_id"),
                "resource": grant.get("resource_type"),
                "expired_at": grant.get("expires_at")
            })
    
    return {
        "expired_tokens": expired,
        "expired_count": len(expired),
        "total_grants": len(grants),
        "checked_at": now.isoformat()
    }


def cleanup_expired_tokens() -> dict[str, Any]:
    """Remove all expired tokens from active grants (TTL enforcement)."""
    if not GRANTS_FILE.exists():
        return {
            "cleaned": 0,
            "remaining": 0,
            "message": "No grants file found"
        }
    
    try:
        grants = json.loads(GRANTS_FILE.read_text())
    except json.JSONDecodeError:
        return {
            "cleaned": 0,
            "error": "Invalid grants file"
        }
    
    original_count = len(grants)
    expired_tokens: list[dict[str, Any]] = []
    
    # Find and remove expired tokens
    tokens_to_remove: list[str] = []
    for token, grant in grants.items():
        if is_token_expired(grant):
            tokens_to_remove.append(token)
            expired_tokens.append({
                "token": token,
                "agent": grant.get("agent_id"),
                "resource": grant.get("resource_type"),
                "expired_at": grant.get("expires_at")
            })
    
    for token in tokens_to_remove:
        grants.pop(token)
    
    # Write back cleaned grants
    GRANTS_FILE.write_text(json.dumps(grants, indent=2))
    
    # Log the cleanup
    if expired_tokens:
        log_audit("ttl_cleanup", {
            "expired_count": len(expired_tokens),
            "expired_tokens": expired_tokens,
            "remaining_grants": len(grants)
        })
    
    return {
        "cleaned": len(expired_tokens),
        "expired_tokens": expired_tokens,
        "remaining": len(grants),
        "original_count": original_count,
        "cleaned_at": datetime.now(timezone.utc).isoformat()
    }


def main():
    parser = argparse.ArgumentParser(
        description="Revoke permission grant tokens and enforce TTL cleanup"
    )
    parser.add_argument("token", nargs="?", help="Grant token to revoke")
    parser.add_argument("--cleanup", action="store_true", 
                        help="Remove all expired tokens (TTL enforcement)")
    parser.add_argument("--list-expired", action="store_true",
                        help="List expired tokens without removing")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    # Handle --list-expired
    if args.list_expired:
        result = list_expired_tokens()
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            expired = result.get("expired_tokens", [])
            if expired:
                print(f"⏰ Found {len(expired)} expired token(s):")
                for t in expired:
                    print(f"   • {t['token'][:20]}... ({t['agent']} → {t['resource']})")
                    print(f"     Expired: {t['expired_at']}")
            else:
                print("✅ No expired tokens found")
            print(f"\n   Total grants: {result.get('total_grants', 0)}")
        sys.exit(0)
    
    # Handle --cleanup
    if args.cleanup:
        result = cleanup_expired_tokens()
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            cleaned = result.get("cleaned", 0)
            if cleaned > 0:
                print(f"🧹 TTL Cleanup Complete")
                print(f"   Removed: {cleaned} expired token(s)")
                for t in result.get("expired_tokens", []):
                    print(f"   • {t['token'][:20]}... ({t['agent']})")
            else:
                print("✅ No expired tokens to clean")
            print(f"   Remaining active grants: {result.get('remaining', 0)}")
        sys.exit(0)
    
    # Handle single token revocation
    if not args.token:
        parser.print_help()
        sys.exit(1)
    
    result = revoke_token(args.token)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["revoked"]:
            grant = result["grant"]
            print("✅ Token REVOKED")
            print(f"   Agent: {grant.get('agent_id')}")
            print(f"   Resource: {grant.get('resource_type')}")
        else:
            print("❌ Revocation FAILED")
            print(f"   Reason: {result.get('reason')}")
    
    sys.exit(0 if result.get("revoked") or result.get("cleaned", 0) >= 0 else 1)


if __name__ == "__main__":
    main()
