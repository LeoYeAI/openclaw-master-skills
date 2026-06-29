#!/usr/bin/env python3
"""
Neodomain AI - Get Available Video Models
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
import os

BASE_URL = "https://story.neodomain.cn/agent/user/video"


def get_universal_models(request_type: int = 1, token: str = None):
    """Get available video models with universal configuration."""
    url = f"{BASE_URL}/models/universal/byLogin?requestType={request_type}"
    
    headers = {"Content-Type": "application/json"}
    if token:
        headers["accessToken"] = token
    
    req = urllib.request.Request(url, headers=headers, method="GET")
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error (universal): {e.code}", file=sys.stderr)
        print(e.read().decode("utf-8"), file=sys.stderr)
        return {"success": False, "data": []}


def get_video_models(request_type: int = 1, token: str = None):
    """Get available video models with cascading configuration."""
    url = f"{BASE_URL}/models/cascading/v2/byLogin?requestType={request_type}"
    
    headers = {"Content-Type": "application/json"}
    if token:
        headers["accessToken"] = token
    
    req = urllib.request.Request(url, headers=headers, method="GET")
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}", file=sys.stderr)
        print(e.read().decode("utf-8"), file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Get available video generation models")
    parser.add_argument("--request-type", type=int, default=2, 
                        help="Request type: 1-视频工具, 2-画布")
    parser.add_argument("--token", "--access-token", dest="token", help="Access token")
    
    args = parser.parse_args()
    
    if not args.token:
        args.token = os.environ.get("NEODOMAIN_ACCESS_TOKEN")
    
    if not args.token:
        print("❌ Error: Access token required. Use --token or set NEODOMAIN_ACCESS_TOKEN", file=sys.stderr)
        sys.exit(1)
    
    result = get_video_models(args.request_type, args.token)
    universal_result = get_universal_models(args.request_type, args.token)
    
    cascading_models = result.get("data", []) if result.get("success") else []
    universal_models = universal_result.get("data", []) if universal_result.get("success") else []
    
    cascading_values = {m.get("value") for m in cascading_models}
    extra_universal = [m for m in universal_models if m.get("value") not in cascading_values]
    models = cascading_models + extra_universal
    
    if not result.get("success") and not universal_result.get("success"):
        print(f"❌ Error: {result.get('errMessage')}", file=sys.stderr)
        sys.exit(1)
    
    print(f"\n🎬 Available Video Models ({len(models)}):\n")

    for model in models:
        print(f"  {model.get('name')} ({model.get('value')})")
        print(f"    Provider: {model.get('provider')}")
        print(f"    Description: {model.get('description')}")
        print(f"    Tags: {', '.join(model.get('tags', []))}")
        print(f"    Features:")
        print(f"      - Audio: {'✅' if model.get('supportAudio') else '❌'}")
        print(f"      - Prompt Enhance: {'✅' if model.get('supportEnhance') else '❌'}")
        print(f"      - First/Last Frame: {'✅' if model.get('supportFirstLastFrame') else '❌'}")
        print(f"      - Multi-Image Ref: {'✅' if model.get('supportReferenceToVideo') else '❌'}")
        
        # Show generation types
        for gt in model.get("generationTypes", []):
            print(f"    {gt.get('name')}:")
            for res in gt.get("resolutions", []):
                print(f"      {res.get('name')}:")
                for dur in res.get("durations", []):
                    print(f"        {dur.get('name')}:")
                    for ar in dur.get("aspectRatios", []):
                        cost = ar.get("basePoints", 0)
                        audio_cost = ar.get("audioPoints", 0)
                        enhance_cost = ar.get("enhancePoints", 0)
                        print(f"          {ar.get('value')}: {cost} pts" +
                              (f" (+{audio_cost} audio)" if audio_cost else "") +
                              (f" (+{enhance_cost} enhance)" if enhance_cost else ""))
        print()


if __name__ == "__main__":
    main()
