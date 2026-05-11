#!/usr/bin/env python3
"""
Ezviz Multimodal Analysis Skill (萤石多模态理解技能)

通过萤石设备抓图 + 智能体分析接口，实现对摄像头画面的多模态理解分析。

工作流程:
1. 获取 AccessToken (appKey + appSecret) - 使用全局 Token 缓存
2. 对每个设备：抓取当前画面
3. 调用智能体分析接口进行理解分析
4. 输出分析结果
"""

import sys
import os
import time
import json
import re
import requests
from datetime import datetime

# Add lib directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
lib_dir = os.path.join(os.path.dirname(script_dir), "lib")
sys.path.insert(0, lib_dir)

from token_manager import get_cached_token

# Configuration
DEVICE_CAPTURE_API_URL = "https://openai.ys7.com/api/lapp/device/capture"
AGENT_ANALYSIS_API_URL = "https://aidialoggw.ys7.com/api/service/open/intelligent/agent/engine/agent/anaylsis"

# Environment variables
APP_KEY = os.environ.get("EZVIZ_APP_KEY", "")
APP_SECRET = os.environ.get("EZVIZ_APP_SECRET", "")
DEVICE_SERIAL = os.environ.get("EZVIZ_DEVICE_SERIAL", "")
CHANNEL_NO = os.environ.get("EZVIZ_CHANNEL_NO", "1")
AGENT_ID = os.environ.get("EZVIZ_AGENT_ID", "")
ANALYSIS_TEXT = os.environ.get("EZVIZ_ANALYSIS_TEXT", "请分析这张图片的内容")


def validate_device_serial(device_str):
    """
    Validate device serial format.
    
    Args:
        device_str: Device serial string (comma-separated)
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not device_str:
        return False, "Device serial is empty"
    
    # Allow letters, numbers, colons, and commas
    if not re.match(r'^[A-Za-z0-9_:,]+$', device_str):
        return False, "Device serial contains invalid characters (only A-Z, a-z, 0-9, :, comma allowed)"
    
    return True, None


def get_credentials_from_env_or_config():
    """
    Get credentials from environment variables or config files.
    
    Priority:
    1. Environment variables (highest)
    2. OpenClaw config files (~/.openclaw/*.json)
    3. Command line arguments (lowest)
    
    Returns:
        tuple: (app_key, app_secret, agent_id, source)
    """
    app_key = APP_KEY
    app_secret = APP_SECRET
    agent_id = AGENT_ID
    source = "environment"
    
    # If env vars are set, use them
    if app_key and app_secret:
        return app_key, app_secret, agent_id, source
    
    # Try to load from config files
    config_paths = [
        os.path.expanduser("~/.openclaw/config.json"),
        os.path.expanduser("~/.openclaw/gateway/config.json"),
        os.path.expanduser("~/.openclaw/channels.json"),
    ]
    
    for config_path in config_paths:
        if not os.path.exists(config_path):
            continue
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            ezviz_config = config.get("channels", {}).get("ezviz", {})
            if ezviz_config.get("enabled", True):
                config_app_key = ezviz_config.get("appId", "")
                config_app_secret = ezviz_config.get("appSecret", "")
                
                if config_app_key and config_app_secret:
                    print(f"[WARNING] Reading credentials from config file: {config_path}")
                    print(f"[WARNING] Environment variables have higher priority")
                    app_key = config_app_key
                    app_secret = config_app_secret
                    source = f"config:{config_path}"
                    break
        except Exception as e:
            continue
    
    return app_key, app_secret, agent_id, source


def parse_device_list(device_str, channel_str="1"):
    """Parse device list from string."""
    devices = []
    if not device_str:
        return devices
    
    for item in device_str.split(","):
        item = item.strip()
        if not item:
            continue
        
        if ":" in item:
            parts = item.split(":")
            serial = parts[0].strip().upper()
            channel = int(parts[1].strip()) if len(parts) > 1 else int(channel_str)
        else:
            serial = item.upper()
            channel = int(channel_str)
        
        devices.append((serial, channel))
    
    return devices


def capture_device_image(access_token, device_serial, channel_no=1):
    """Capture image from device."""
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "accessToken": access_token,
        "deviceSerial": device_serial.upper(),
        "channelNo": str(channel_no)
    }
    
    try:
        response = requests.post(DEVICE_CAPTURE_API_URL, headers=headers, data=data, timeout=30)
        result = response.json()
        
        if result.get("code") == "200":
            data = result.get("data", {})
            return {"success": True, "pic_url": data.get("picUrl", "")}
        else:
            return {"success": False, "error": result.get("msg", "Capture failed")}
    except Exception as e:
        return {"success": False, "error": str(e)}


def agent_analysis(access_token, agent_id, image_url, analysis_text="请分析这张图片的内容"):
    """
    Call intelligent agent analysis API.
    
    API: POST /api/service/open/intelligent/agent/engine/agent/anaylsis
    
    Args:
        access_token: Ezviz access token
        agent_id: AI agent ID (from console)
        image_url: Image URL to analyze
        analysis_text: Analysis prompt/instruction
    
    Returns:
        dict: Analysis result
    """
    print(f"[INFO] Calling agent analysis: agentId={agent_id[:8]}...")
    
    headers = {
        "accessToken": access_token,
        "Content-Type": "application/json"
    }
    
    payload = {
        "appId": agent_id,
        "mediaType": "image",
        "text": analysis_text,
        "dataType": "url",
        "data": image_url
    }
    
    try:
        response = requests.post(AGENT_ANALYSIS_API_URL, headers=headers, json=payload, timeout=60)
        result = response.json()
        
        # Don't log full response to avoid leaking data
        
        if result.get("meta", {}).get("code") == 200:
            # Parse the data field (it's a JSON string inside JSON)
            data_str = result.get("data", "")
            try:
                data_parsed = json.loads(data_str) if data_str else {}
            except:
                data_parsed = {"raw": data_str}
            
            print(f"[SUCCESS] Analysis completed!")
            return {
                "success": True,
                "analysis": data_parsed,
                "raw_data": data_str
            }
        else:
            meta = result.get("meta", {})
            error_msg = meta.get("message", "Analysis failed")
            print(f"[ERROR] Analysis failed: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "code": meta.get("code")
            }
    except Exception as e:
        print(f"[ERROR] Analysis failed: {type(e).__name__}")
        return {"success": False, "error": str(e)}


def main():
    """Main workflow."""
    print("=" * 70)
    print("Ezviz Multimodal Analysis Skill (萤石多模态理解技能)")
    print("=" * 70)
    print(f"[Time] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Configuration
    app_key = APP_KEY or sys.argv[1] if len(sys.argv) > 1 else ""
    app_secret = APP_SECRET or sys.argv[2] if len(sys.argv) > 2 else ""
    device_str = DEVICE_SERIAL or sys.argv[3] if len(sys.argv) > 3 else ""
    channel_str = CHANNEL_NO or (sys.argv[4] if len(sys.argv) > 4 else "1")
    agent_id = AGENT_ID or sys.argv[5] if len(sys.argv) > 5 else ""
    analysis_text = ANALYSIS_TEXT or (sys.argv[6] if len(sys.argv) > 6 else "请分析这张图片的内容")
    
    # If env vars not set, try to load from config
    if not app_key or not app_secret:
        app_key, app_secret, config_agent_id, source = get_credentials_from_env_or_config()
        if config_agent_id and not agent_id:
            agent_id = config_agent_id
    
    # Validate device serial
    is_valid, error_msg = validate_device_serial(device_str)
    if not is_valid:
        print(f"[ERROR] Invalid device serial: {error_msg}")
        sys.exit(1)
    
    # Validate credentials source
    if "config:" in (app_key + app_secret):
        print(f"[WARNING] Credentials loaded from config file")
    else:
        print(f"[OK] Using credentials from environment variables")
    
    print(f"[OK] Device serial format validated")
    
    devices = parse_device_list(device_str, channel_str)
    if not devices:
        print("[ERROR] At least one device serial required.")
        sys.exit(1)
    
    if not agent_id:
        print("[ERROR] agentId required. Get from https://openai.ys7.com/console/aiAgent/aiAgent.html")
        sys.exit(1)
    
    print(f"[INFO] Target devices: {len(devices)}")
    for serial, channel in devices:
        print(f"       - {serial} (Channel: {channel})")
    print(f"[INFO] Agent ID: {agent_id[:8]}...")
    print(f"[INFO] Analysis: {analysis_text}")
    
    # Step 1: Get access token (using global cache)
    print(f"\n{'='*70}")
    print("[Step 1] Getting access token...")
    print(f"{'='*70}")
    
    token_result = get_cached_token(app_key, app_secret)
    
    if not token_result["success"]:
        print(f"[ERROR] Failed to get token: {token_result.get('error')}")
        sys.exit(1)
    
    access_token = token_result["access_token"]
    expire_time = token_result.get("expire_time", 0)
    expire_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expire_time / 1000))
    
    # Step 2: Process each device
    print(f"\n{'='*70}")
    print("[Step 2] Capturing and analyzing images...")
    print(f"{'='*70}")
    
    results = {
        "total": len(devices),
        "success": 0,
        "failed": 0,
        "analyses": []
    }
    
    for device_serial, channel_no in devices:
        print(f"\n{'='*70}")
        print(f"[Device] {device_serial} (Channel: {channel_no})")
        print(f"{'='*70}")
        
        # Capture image
        capture_result = capture_device_image(access_token, device_serial, channel_no)
        
        if not capture_result["success"]:
            print(f"[ERROR] Capture failed: {capture_result.get('error')}")
            results["failed"] += 1
            results["analyses"].append({
                "device": device_serial,
                "channel": channel_no,
                "error": capture_result.get("error")
            })
            continue
        
        image_url = capture_result["pic_url"]
        print(f"[SUCCESS] Image captured: {image_url[:60]}...")
        
        # Agent analysis
        analysis_result = agent_analysis(access_token, agent_id, image_url, analysis_text)
        
        if analysis_result["success"]:
            print(f"[SUCCESS] Analysis completed!")
            print(f"\n[Analysis Result]")
            print(json.dumps(analysis_result["analysis"], indent=2, ensure_ascii=False))
            
            results["success"] += 1
            results["analyses"].append({
                "device": device_serial,
                "channel": channel_no,
                "image_url": image_url,
                "analysis": analysis_result["analysis"],
                "success": True
            })
        else:
            print(f"[ERROR] Analysis failed: {analysis_result.get('error')}")
            results["failed"] += 1
            results["analyses"].append({
                "device": device_serial,
                "channel": channel_no,
                "image_url": image_url,
                "error": analysis_result.get("error"),
                "success": False
            })
        
        # Wait 4s between devices to avoid rate limiting (Ezviz recommends >=4s interval)
        time.sleep(4)
    
    # Summary
    print(f"\n{'='*70}")
    print("ANALYSIS SUMMARY")
    print(f"{'='*70}")
    print(f"  Total devices:  {results['total']}")
    print(f"  Success:        {results['success']}")
    print(f"  Failed:         {results['failed']}")
    print(f"{'='*70}")
    
    print(f"\n[JSON Result]")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    print(f"\n{'='*70}")
    print("Workflow completed")
    print(f"{'='*70}")
    
    sys.exit(0 if results["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
