#!/usr/bin/env python3
"""
Neodomain AI - Authentication Script
Send verification code and login to get access token.
"""

import argparse
import json
import sys
import urllib.request
import urllib.error

BASE_URL = "https://story.neodomain.cn"
USER_SOURCE = "NEO"


def send_code(contact: str) -> dict:
    """Send verification code to phone or email."""
    url = f"{BASE_URL}/user/login/send-unified-code"
    data = json.dumps({"contact": contact, "userSource": USER_SOURCE}).encode("utf-8")
    
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}", file=sys.stderr)
        print(e.read().decode("utf-8"), file=sys.stderr)
        sys.exit(1)


def login(contact: str, code: str, invitation_code: str = None) -> dict:
    """Login with verification code. Returns data dict which may contain
    authorization token directly, or needSelectIdentity=True with identities list."""
    url = f"{BASE_URL}/user/login/unified-login/identity"
    payload = {
        "contact": contact,
        "code": code,
        "invitationCode": invitation_code or "",
        "userSource": USER_SOURCE,
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            if result.get("success"):
                return result.get("data", {})
            else:
                print(f"Login failed: {result.get('errMessage')}", file=sys.stderr)
                sys.exit(1)
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}", file=sys.stderr)
        print(e.read().decode("utf-8"), file=sys.stderr)
        sys.exit(1)


def select_identity(user_id: str, contact: str) -> dict:
    """Select identity after multi-identity login to obtain access token."""
    url = f"{BASE_URL}/user/login/select-identity"
    payload = {"userId": user_id, "contact": contact}
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            if result.get("success"):
                return result.get("data", {})
            else:
                print(f"Select identity failed: {result.get('errMessage')}", file=sys.stderr)
                sys.exit(1)
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}", file=sys.stderr)
        print(e.read().decode("utf-8"), file=sys.stderr)
        sys.exit(1)


def print_token_info(result: dict):
    """Print access token and user info from a login/select-identity result."""
    print("\n✅ Login successful!")
    print(f"\nAccess Token:")
    print(result.get("authorization"))
    print(f"\nUser Info:")
    print(f"  User ID: {result.get('userId')}")
    print(f"  Nickname: {result.get('nickname')}")
    print(f"  User Type: {result.get('userType')}")
    print(f"  Email: {result.get('email')}")
    print(f"  Mobile: {result.get('mobile')}")
    if result.get("enterpriseName"):
        print(f"  Enterprise: {result.get('enterpriseName')}")
    print("\n📝 Add to your environment:")
    print(f'export NEODOMAIN_ACCESS_TOKEN="{result.get("authorization")}"')


def main():
    parser = argparse.ArgumentParser(description="Neodomain AI Authentication")
    parser.add_argument("--send-code", action="store_true", help="Send verification code")
    parser.add_argument("--login", action="store_true", help="Login with code")
    parser.add_argument("--select-identity", action="store_true", help="Select identity after multi-identity login")
    parser.add_argument("--contact", required=True, help="Phone number or email")
    parser.add_argument("--code", help="Verification code (for --login)")
    parser.add_argument("--invitation-code", help="Invitation code (optional)")
    parser.add_argument("--user-id", help="User ID to select (for --select-identity)")
    
    args = parser.parse_args()
    
    if args.send_code:
        result = send_code(args.contact)
        if result.get("success"):
            print("✅ Verification code sent successfully!")
        else:
            print(f"❌ Failed: {result.get('errMessage')}")
            sys.exit(1)
    
    elif args.login:
        if not args.code:
            print("❌ Error: --code is required for login")
            sys.exit(1)
        
        data = login(args.contact, args.code, args.invitation_code)
        
        if data.get("needSelectIdentity"):
            identities = data.get("identities", [])
            print("\n⚠️  Multiple identities found. Please select one:\n")
            for i, identity in enumerate(identities, 1):
                user_type = identity.get("userType", "")
                nickname = identity.get("nickname", "")
                enterprise = identity.get("enterpriseName", "")
                user_id = identity.get("userId", "")
                label = f"{nickname}"
                if enterprise:
                    label += f" ({enterprise})"
                print(f"  {i}. [{user_type}] {label}")
                print(f"     userId: {user_id}")
            print(f"\n📝 Run the following to complete login (replace <userId> with your choice):")
            print(f'python3 {sys.argv[0]} --select-identity --contact "{args.contact}" --user-id "<userId>"')
        else:
            print_token_info(data)
    
    elif args.select_identity:
        if not args.user_id:
            print("❌ Error: --user-id is required for --select-identity")
            sys.exit(1)
        
        data = select_identity(args.user_id, args.contact)
        print_token_info(data)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
