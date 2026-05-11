#!/usr/bin/env python3
"""
Ezviz Device Configuration Script
萤石设备配置脚本 - 支持 9 个配置 API

根据文档 ID: 701,702,703,706,707,712,713,714,715
"""

import os
import sys
import json
from datetime import datetime
import time

import requests

# Add lib directory to path for token_manager import
script_dir = os.path.dirname(os.path.abspath(__file__))
lib_dir = os.path.join(script_dir, "..", "lib")
sys.path.insert(0, lib_dir)

from token_manager import get_cached_token

# ============================================================================
# Configuration
# ============================================================================

# API endpoints (using openai.ys7.com - Ezviz Open API domain)
CONFIG_APIS = {
    # 701: 设置布撤防
    "defence_set": {
        "url": "/api/lapp/device/defence/set",
        "method": "POST",
        "params": ["accessToken", "deviceSerial", "isDefence"]
    },
    # 702: 获取布撤防时间计划
    "defence_plan_get": {
        "url": "/api/lapp/device/defence/plan/get",
        "method": "POST",
        "params": ["accessToken", "deviceSerial", "channelNo"]
    },
    # 703: 设置布撤防计划
    "defence_plan_set": {
        "url": "/api/lapp/device/defence/plan/set",
        "method": "POST",
        "params": ["accessToken", "deviceSerial", "startTime", "stopTime", "period", "enable"]
    },
    # 706: 获取镜头遮蔽开关状态 (使用 scene/switch API)
    "shelter_get": {
        "url": "/api/lapp/device/scene/switch/status",
        "method": "POST",
        "params": ["accessToken", "deviceSerial"]
    },
    # 707: 设置镜头遮蔽开关 (使用 scene/switch API)
    "shelter_set": {
        "url": "/api/lapp/device/scene/switch/set",
        "method": "POST",
        "params": ["accessToken", "deviceSerial", "channelNo", "enable"]
    },
    # 712: 获取全天录像开关状态
    "fullday_record_get": {
        "url": "/api/lapp/device/fullday/record/switch/status",
        "method": "POST",
        "params": ["accessToken", "deviceSerial"]
    },
    # 713: 设置全天录像开关状态
    "fullday_record_set": {
        "url": "/api/lapp/device/fullday/record/switch/set",
        "method": "POST",
        "params": ["accessToken", "deviceSerial", "enable"]
    },
    # 714: 获取移动侦测灵敏度配置 (使用 algorithm/config API)
    "motion_detect_sensitivity_get": {
        "url": "/api/lapp/device/algorithm/config/get",
        "method": "POST",
        "params": ["accessToken", "deviceSerial"]
    },
    # 715: 设置移动侦测灵敏度 (使用 algorithm/config API)
    "motion_detect_sensitivity_set": {
        "url": "/api/lapp/device/algorithm/config/set",
        "method": "POST",
        "params": ["accessToken", "deviceSerial", "channelNo", "type", "value"]
    },
}

# API domain (openai.ys7.com = Ezviz Open API, not AI)
API_DOMAIN = "https://openai.ys7.com"

# Environment variables
APP_KEY = os.getenv("EZVIZ_APP_KEY", "")
APP_SECRET = os.getenv("EZVIZ_APP_SECRET", "")
DEVICE_SERIAL = os.getenv("EZVIZ_DEVICE_SERIAL", "")
CHANNEL_NO = os.getenv("EZVIZ_CHANNEL_NO", "1")

# ============================================================================
# Config File Reader (Fallback)
# ============================================================================

def load_ezviz_config_from_files():
    """
    Load Ezviz credentials from OpenClaw config files.
    
    Search order:
    1. ~/.openclaw/config.json
    2. ~/.openclaw/gateway/config.json
    3. ~/.openclaw/channels.json
    
    Returns:
        dict: {app_key, app_secret, domain} or None if not found
    """
    import os.path
    
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
            
            # Check channels.ezviz
            channels = config.get("channels", {})
            ezviz = channels.get("ezviz", {})
            
            if ezviz.get("enabled", False):
                app_key = ezviz.get("appId") or ezviz.get("appKey")
                app_secret = ezviz.get("appSecret")
                domain = ezviz.get("domain", API_DOMAIN)
                
                if app_key and app_secret:
                    print(f"[INFO] Loaded Ezviz config from: {config_path}")
                    return {
                        "app_key": app_key,
                        "app_secret": app_secret,
                        "domain": domain
                    }
        except Exception as e:
            print(f"[WARNING] Failed to load config from {config_path}: {e}")
            continue
    
    return None

# ============================================================================
# Helper Functions
# ============================================================================

def execute_config(access_token, device_serial, config_type, value=None, extra_params=None):
    """
    Execute device configuration.
    
    Args:
        access_token: Ezviz access token
        device_serial: Device serial number
        config_type: Configuration type (defence_set, shelter_get, etc.)
        value: Configuration value (for set actions: isDefence, enable, sensitivity)
        extra_params: Additional parameters (for defence_plan_set: startTime, stopTime, period)
    
    Returns:
        dict: Configuration result
    """
    if config_type not in CONFIG_APIS:
        return {
            "success": False,
            "error": f"Unknown config type: {config_type}",
            "available_types": list(CONFIG_APIS.keys())
        }
    
    api_info = CONFIG_APIS[config_type]
    api_url = f"{API_DOMAIN}{api_info['url']}"
    
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "accessToken": access_token,
        "deviceSerial": device_serial.upper()
    }
    
    # Add channelNo for APIs that support it
    if "channelNo" in api_info["params"]:
        data["channelNo"] = CHANNEL_NO  # Use env var or default
    
    # Add action-specific parameters based on API docs
    if value is not None:
        if config_type == "defence_set":
            # 701: isDefence - 0:睡眠，8:在家，16:外出 (普通 IPC: 0-撤防，1-布防)
            data["isDefence"] = str(value)
        elif config_type == "shelter_set":
            # 707: enable - 0:关闭，1:开启 (镜头遮蔽)
            data["enable"] = str(value)
            data["channelNo"] = CHANNEL_NO
        elif config_type == "fullday_record_set":
            # 713: enable - 0:关闭，1:开启
            data["enable"] = str(value)
        elif config_type == "motion_detect_sensitivity_set":
            # 715: type=0 (移动侦测), value=0-6 (0 最低灵敏度)
            data["type"] = "0"
            data["value"] = str(value)
            data["channelNo"] = CHANNEL_NO
        elif config_type == "defence_plan_set":
            # 703: Multiple parameters needed
            if extra_params:
                data["startTime"] = extra_params.get("startTime", "00:00")
                data["stopTime"] = extra_params.get("stopTime", "00:00")
                data["period"] = extra_params.get("period", "0,1,2,3,4,5,6")
                data["enable"] = str(extra_params.get("enable", 1))
            else:
                # Default values
                data["startTime"] = "00:00"
                data["stopTime"] = "00:00"
                data["period"] = "0,1,2,3,4,5,6"
                data["enable"] = "1"
    
    print(f"[INFO] Calling API: {api_url}")
    print(f"[INFO] Device: {device_serial}, Type: {config_type}")
    if value:
        print(f"[INFO] Value: {value}")
    
    try:
        response = requests.post(api_url, headers=headers, data=data, timeout=30)
        result = response.json()
        
        if result.get("code") == "200":
            print(f"[SUCCESS] Config executed successfully!")
            return {
                "success": True,
                "data": result.get("data", {}),
                "message": result.get("msg", "Success")
            }
        else:
            error_msg = result.get("msg", "Config failed")
            print(f"[ERROR] Config failed: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "code": result.get("code")
            }
    
    except Exception as e:
        print(f"[ERROR] Config failed: {type(e).__name__}")
        return {
            "success": False,
            "error": str(e)
        }

# ============================================================================
# Main
# ============================================================================

def main():
    """Main entry point."""
    print("=" * 70)
    print("Ezviz Device Config (萤石设备配置)")
    print("=" * 70)
    print(f"[Time] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Configuration (Priority: env vars > config files > command line)
    app_key = APP_KEY
    app_secret = APP_SECRET
    device_serial = DEVICE_SERIAL
    
    # Fallback to config files
    if not app_key or not app_secret:
        file_config = load_ezviz_config_from_files()
        if file_config:
            app_key = app_key or file_config.get("app_key", "")
            app_secret = app_secret or file_config.get("app_secret", "")
    
    # Fallback to command line arguments
    app_key = app_key or sys.argv[1] if len(sys.argv) > 1 else app_key
    app_secret = app_secret or sys.argv[2] if len(sys.argv) > 2 else app_secret
    device_serial = device_serial or sys.argv[3] if len(sys.argv) > 3 else device_serial
    
    config_type = sys.argv[4] if len(sys.argv) > 4 else "defence_set"
    value = sys.argv[5] if len(sys.argv) > 5 else None
    
    # Validate
    if not app_key or not app_secret:
        print("[ERROR] APP_KEY and APP_SECRET required.")
        print("[INFO] Set EZVIZ_APP_KEY and EZVIZ_APP_SECRET env vars,")
        print("[INFO] or add to ~/.openclaw/channels.json,")
        print("[INFO] or pass as command line arguments.")
        sys.exit(1)
    
    if not device_serial:
        print("[ERROR] DEVICE_SERIAL required.")
        print("[INFO] Set EZVIZ_DEVICE_SERIAL env var.")
        sys.exit(1)
    
    print(f"[INFO] Device: {device_serial}")
    print(f"[INFO] Config Type: {config_type}")
    if value:
        print(f"[INFO] Value: {value}")
    
    # Parse extra_params for defence_plan_set
    extra_params = None
    if config_type == "defence_plan_set" and value:
        try:
            # Try to parse as JSON
            extra_params = json.loads(value)
            print(f"[INFO] Parsed extra_params: {extra_params}")
        except json.JSONDecodeError:
            print("[WARN] Failed to parse value as JSON, using as-is")
    
    # Step 1: Get access token (with global cache)
    print("\n" + "=" * 70)
    print("[Step 1] Getting access token...")
    print("=" * 70)
    
    token_result = get_cached_token(app_key, app_secret)
    
    if not token_result["success"]:
        print(f"[ERROR] Failed to get token: {token_result.get('error')}")
        sys.exit(1)
    
    access_token = token_result["access_token"]
    expire_time = token_result["expire_time"]
    from_cache = token_result.get("from_cache", False)
    
    expire_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expire_time / 1000))
    if from_cache:
        print(f"[SUCCESS] Using cached token, expires: {expire_str}")
    else:
        print(f"[SUCCESS] Token obtained, expires: {expire_str}")
    
    # Step 2: Execute config
    print("\n" + "=" * 70)
    print("[Step 2] Executing config...")
    print("=" * 70)
    
    config_result = execute_config(
        access_token, device_serial, config_type, value, extra_params
    )
    
    # Output result
    print("\n" + "=" * 70)
    print("CONFIG RESULT")
    print("=" * 70)
    
    if config_result["success"]:
        print(f"  Device:     {device_serial}")
        print(f"  Type:       {config_type}")
        print(f"  Value:      {value}")
        print(f"  Status:     success")
        if config_result.get("data"):
            print(f"  Data:       {json.dumps(config_result['data'], ensure_ascii=False)}")
    else:
        print(f"  Device:     {device_serial}")
        print(f"  Type:       {config_type}")
        print(f"  Status:     failed")
        print(f"  Error:      {config_result.get('error')}")
        if config_result.get("code"):
            print(f"  Code:       {config_result['code']}")
    
    print("=" * 70)
    
    # Exit with appropriate code
    sys.exit(0 if config_result["success"] else 1)

if __name__ == "__main__":
    main()
