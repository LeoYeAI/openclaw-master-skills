#!/usr/bin/env python3
"""
Neodomain AI - Get Available Image Models
"""

import argparse
import json
import sys
import urllib.request
import urllib.error

BASE_URL = "https://story.neodomain.cn/agent/ai-image-generation"


def get_models(scenario_type: int = 1, user_id: str = None, token: str = None):
    """Get available image models by scenario type."""
    url = f"{BASE_URL}/models/by-scenario?scenarioType={scenario_type}"
    if user_id:
        url += f"&userId={user_id}"
    
    headers = {"Content-Type": "application/json"}
    if token:
        headers["accessToken"] = token
    
    req = urllib.request.Request(url, headers=headers, method="GET")
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}", file=sys.stderr)
        print(e.read().decode("utf-8"), file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Get available image generation models")
    parser.add_argument("--scenario-type", type=int, default=1, 
                        help="Scenario type: 1-图片工具, 2-画布, 3-重绘, 4-设计, 5-分镜")
    parser.add_argument("--user-id", help="User ID for membership priority")
    parser.add_argument("--token", "--access-token", dest="token", help="Access token")
    
    args = parser.parse_args()
    
    # Try to get token from environment if not provided
    if not args.token:
        import os
        args.token = os.environ.get("NEODOMAIN_ACCESS_TOKEN")
    
    if not args.token:
        print("❌ Error: Access token required. Use --token or set NEODOMAIN_ACCESS_TOKEN", file=sys.stderr)
        sys.exit(1)
    
    result = get_models(args.scenario_type, args.user_id, args.token)
    
    if result.get("success"):
        models = result.get("data", [])
        print(f"\n📸 Available Image Models ({len(models)}):\n")
        
        for m in models:
            print(f"  {m.get('model_name')}")
            print(f"    Display: {m.get('model_display_name')}")
            print(f"    Provider: {m.get('provider')}")
            print(f"    Type: {m.get('model_type')}")
            print(f"    Cost: {m.get('points_cost_per_image')} points/image")
            print(f"    Sizes: {', '.join(m.get('supported_sizes', []))}")
            print(f"    Ratios: {', '.join(m.get('supported_aspect_ratios', []))}")
            print(f"    Requires membership: {m.get('require_membership')}")
            print()
    else:
        print(f"❌ Error: {result.get('errMessage')}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
