#!/usr/bin/env python3
"""
Environment check for MiniMaxStudio (TTS, Music, Video).

Usage:
    python scripts/check_environment.py
    python scripts/check_environment.py --test-api
"""

import argparse
import sys
import os
import subprocess


def check_python():
    v = sys.version_info
    if v.major >= 3 and v.minor >= 8:
        print(f"[OK] Python {v.major}.{v.minor}.{v.micro}")
        return True
    print(f"[FAIL] Python {v.major}.{v.minor} (need 3.8+)")
    return False


def check_package(name):
    try:
        __import__(name)
        print(f"[OK] {name}")
        return True
    except ImportError:
        print(f"[FAIL] {name} not installed (pip install {name})")
        return False


def check_ffmpeg():
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            print("[OK] FFmpeg installed")
            return True
    except Exception:
        pass
    print("[FAIL] FFmpeg not installed")
    return False


def check_api_key():
    api_key = os.getenv("MINIMAX_API_KEY")
    if not api_key:
        print("[FAIL] MINIMAX_API_KEY not set")
        print("  export MINIMAX_API_KEY='your-key'")
        return False
    if not api_key.startswith("sk-api"):
        print("[FAIL] Invalid API key format")
        print(f"  Expected: sk-api-xxxxxxxxxxxxxxxxxxxxxxxx")
        print(f"  Got: {api_key[:20]}..." if len(api_key) > 20 else f"  Got: {api_key}")
        return False
    print(f"[OK] MINIMAX_API_KEY set ({len(api_key)} chars)")
    return True


def check_api_connectivity():
    import requests

    api_key = os.getenv("MINIMAX_API_KEY")
    if not api_key:
        print("[FAIL] API connectivity skipped (MINIMAX_API_KEY not set)")
        return False
    try:
        resp = requests.get(
            "https://api.minimaxi.com",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10,
        )
        if resp.status_code < 500:
            print(f"[OK] API host reachable (HTTP {resp.status_code})")
            return True
    except Exception as e:
        print(f"[FAIL] API connectivity: {e}")
        return False
    print("[FAIL] API host unreachable")
    return False


def main():
    parser = argparse.ArgumentParser(description="MiniMaxStudio environment checker")
    parser.add_argument("--test-api", action="store_true", help="Test API reachability")
    args = parser.parse_args()

    print("MiniMaxStudio Environment Check\n" + "=" * 40)

    checks = [
        ("Python", check_python()),
        ("requests", check_package("requests")),
        ("websockets", check_package("websockets")),
        ("FFmpeg", check_ffmpeg()),
        ("API Key", check_api_key()),
    ]
    if args.test_api:
        checks.append(("API Connectivity", check_api_connectivity()))

    print("\n" + "=" * 40)
    passed = sum(1 for _, r in checks if r)
    total = len(checks)
    if passed == total:
        print(f"All {total} checks passed!")
        return 0
    else:
        print(f"{total - passed} check(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
