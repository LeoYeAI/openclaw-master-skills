#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ezviz Open PTZ Controller - Main Script
萤石开放平台云台设备控制主脚本

支持设备列表查询、设备状态查询、云台控制 (PTZ)、预置点管理等功能
使用环境变量认证，Token 自动获取（带缓存）
"""

import os
import sys
import json
import requests
from datetime import datetime

# Add lib directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
lib_dir = os.path.join(os.path.dirname(script_dir), "lib")
sys.path.insert(0, lib_dir)

from token_manager import get_cached_token

# ============================================================================
# Configuration
# ============================================================================

API_BASE_URL = "https://openai.ys7.com"

APP_KEY = os.getenv("EZVIZ_APP_KEY", "")
APP_SECRET = os.getenv("EZVIZ_APP_SECRET", "")

# ============================================================================
# API Functions
# ============================================================================

def list_devices(access_token):
    """Get device list"""
    url = f"{API_BASE_URL}/api/lapp/device/list"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"accessToken": access_token, "pageStart": 0, "pageSize": 100}
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=30)
        result = response.json()
        
        if result.get("code") == "200":
            return {"success": True, "data": result.get("data", {})}
        else:
            return {"success": False, "error": result.get("msg", "Failed"), "code": result.get("code")}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_device_status(access_token, device_serial):
    """Get device status"""
    url = f"{API_BASE_URL}/api/lapp/device/info"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"accessToken": access_token, "deviceSerial": device_serial.upper()}
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=30)
        result = response.json()
        
        if result.get("code") == "200":
            return {"success": True, "data": result.get("data", {})}
        else:
            return {"success": False, "error": result.get("msg", "Failed"), "code": result.get("code")}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_device_capacity(access_token, device_serial):
    """Get device capacity"""
    url = f"{API_BASE_URL}/api/lapp/device/capacity"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"accessToken": access_token, "deviceSerial": device_serial.upper()}
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=30)
        result = response.json()
        
        if result.get("code") == "200":
            return {"success": True, "data": result.get("data", {})}
        else:
            return {"success": False, "error": result.get("msg", "Failed"), "code": result.get("code")}
    except Exception as e:
        return {"success": False, "error": str(e)}

def ptz_start(access_token, device_serial, channel_no, direction, speed):
    """Start PTZ control"""
    url = f"{API_BASE_URL}/api/lapp/device/ptz/start"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "accessToken": access_token,
        "deviceSerial": device_serial.upper(),
        "channelNo": str(channel_no),
        "direction": str(direction),
        "speed": str(speed)
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=30)
        result = response.json()
        
        if result.get("code") == "200":
            return {"success": True, "message": "PTZ control started"}
        else:
            return {"success": False, "error": result.get("msg", "Failed"), "code": result.get("code")}
    except Exception as e:
        return {"success": False, "error": str(e)}

def ptz_stop(access_token, device_serial, channel_no):
    """Stop PTZ control"""
    url = f"{API_BASE_URL}/api/lapp/device/ptz/stop"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "accessToken": access_token,
        "deviceSerial": device_serial.upper(),
        "channelNo": str(channel_no)
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=30)
        result = response.json()
        
        if result.get("code") == "200":
            return {"success": True, "message": "PTZ control stopped"}
        else:
            return {"success": False, "error": result.get("msg", "Failed"), "code": result.get("code")}
    except Exception as e:
        return {"success": False, "error": str(e)}

def preset_add(access_token, device_serial, channel_no):
    """Add preset"""
    url = f"{API_BASE_URL}/api/lapp/device/preset/add"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "accessToken": access_token,
        "deviceSerial": device_serial.upper(),
        "channelNo": str(channel_no)
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=30)
        result = response.json()
        
        if result.get("code") == "200":
            return {"success": True, "data": result.get("data", {}), "message": "Preset added"}
        else:
            return {"success": False, "error": result.get("msg", "Failed"), "code": result.get("code")}
    except Exception as e:
        return {"success": False, "error": str(e)}

def preset_move(access_token, device_serial, channel_no, index):
    """Move to preset"""
    url = f"{API_BASE_URL}/api/lapp/device/preset/move"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "accessToken": access_token,
        "deviceSerial": device_serial.upper(),
        "channelNo": str(channel_no),
        "index": str(index)
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=30)
        result = response.json()
        
        if result.get("code") == "200":
            return {"success": True, "message": f"Moving to preset {index}"}
        else:
            return {"success": False, "error": result.get("msg", "Failed"), "code": result.get("code")}
    except Exception as e:
        return {"success": False, "error": str(e)}

def preset_clear(access_token, device_serial, channel_no, index):
    """Clear preset"""
    url = f"{API_BASE_URL}/api/lapp/device/preset/clear"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "accessToken": access_token,
        "deviceSerial": device_serial.upper(),
        "channelNo": str(channel_no),
        "index": str(index)
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=30)
        result = response.json()
        
        if result.get("code") == "200":
            return {"success": True, "message": f"Preset {index} cleared"}
        else:
            return {"success": False, "error": result.get("msg", "Failed"), "code": result.get("code")}
    except Exception as e:
        return {"success": False, "error": str(e)}

def mirror_flip(access_token, device_serial, channel_no, command):
    """Mirror flip"""
    url = f"{API_BASE_URL}/api/lapp/device/ptz/mirror"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "accessToken": access_token,
        "deviceSerial": device_serial.upper(),
        "channelNo": str(channel_no),
        "command": str(command)
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=30)
        result = response.json()
        
        if result.get("code") == "200":
            return {"success": True, "message": "Mirror flip executed"}
        else:
            return {"success": False, "error": result.get("msg", "Failed"), "code": result.get("code")}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================================================
# Main
# ============================================================================

def print_header():
    print("=" * 70)
    print("Ezviz Open PTZ Control (萤石开放平台云台设备控制)")
    print("=" * 70)
    print(f"[Time] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 main.py appKey appSecret <command> [params...]")
        print("\nCommands:")
        print("  list                                    - List all devices")
        print("  status <dev>                            - Get device status")
        print("  capacity <dev>                          - Get device capacity")
        print("  ptz_start <dev> <ch> <dir> <spd>        - Start PTZ control")
        print("  ptz_stop <dev> <ch>                     - Stop PTZ control")
        print("  preset_add <dev> <ch>                   - Add preset")
        print("  preset_move <dev> <ch> <idx>            - Move to preset")
        print("  preset_clear <dev> <ch> <idx>           - Clear preset")
        print("  mirror <dev> <ch> <cmd>                 - Mirror flip")
        sys.exit(1)
    
    # Parse arguments
    app_key = sys.argv[1]
    app_secret = sys.argv[2]
    command = sys.argv[3]
    args = sys.argv[4:]
    
    print_header()
    
    # Validate credentials
    if not app_key or not app_secret:
        print("[ERROR] APP_KEY and APP_SECRET required")
        sys.exit(1)
    
    # Step 1: Get token (with cache support)
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
    expire_str = datetime.fromtimestamp(expire_time / 1000).strftime('%Y-%m-%d %H:%M:%S')
    
    if from_cache:
        print(f"[SUCCESS] Using cached token, expires: {expire_str}")
    else:
        print(f"[SUCCESS] Token obtained, expires: {expire_str}")
    
    # Step 2: Execute command
    print("\n" + "=" * 70)
    print("[Step 2] Executing command...")
    print("=" * 70)
    
    result = None
    
    if command == "list":
        print(f"[INFO] Calling API: {API_BASE_URL}/api/lapp/device/list")
        result = list_devices(access_token)
        
        if result["success"]:
            print("[SUCCESS] Device list retrieved")
            data = result.get("data", [])
            # Data can be list or dict with 'list' key
            if isinstance(data, dict):
                devices = data.get("list", [])
            else:
                devices = data
            print(f"\n[INFO] Total devices: {len(devices)}")
            for dev in devices:
                serial = dev.get("deviceSerial", "unknown")
                status = "online" if dev.get("isOnline") == 1 else "offline"
                print(f"  - {serial} (Status: {status})")
    
    elif command == "status" and len(args) >= 1:
        device_serial = args[0]
        print(f"[INFO] Device: {device_serial}")
        print(f"[INFO] Calling API: {API_BASE_URL}/api/lapp/device/info")
        result = get_device_status(access_token, device_serial)
        
        if result["success"]:
            print("[SUCCESS] Device status retrieved")
            data = result.get("data", {})
            print(f"  Status: {'online' if data.get('isOnline') == 1 else 'offline'}")
    
    elif command == "capacity" and len(args) >= 1:
        device_serial = args[0]
        print(f"[INFO] Device: {device_serial}")
        print(f"[INFO] Calling API: {API_BASE_URL}/api/lapp/device/capacity")
        result = get_device_capacity(access_token, device_serial)
        
        if result["success"]:
            print("[SUCCESS] Device capacity retrieved")
            print(f"  Data: {json.dumps(result.get('data', {}), indent=2, ensure_ascii=False)}")
    
    elif command == "ptz_start" and len(args) >= 4:
        device_serial, channel_no, direction, speed = args[0], int(args[1]), int(args[2]), int(args[3])
        print(f"[INFO] Device: {device_serial}, Channel: {channel_no}")
        print(f"[INFO] Direction: {direction}, Speed: {speed}")
        print(f"[INFO] Calling API: {API_BASE_URL}/api/lapp/device/ptz/start")
        result = ptz_start(access_token, device_serial, channel_no, direction, speed)
        
        if result["success"]:
            print("[SUCCESS] PTZ control started")
    
    elif command == "ptz_stop" and len(args) >= 2:
        device_serial, channel_no = args[0], int(args[1])
        print(f"[INFO] Device: {device_serial}, Channel: {channel_no}")
        print(f"[INFO] Calling API: {API_BASE_URL}/api/lapp/device/ptz/stop")
        result = ptz_stop(access_token, device_serial, channel_no)
        
        if result["success"]:
            print("[SUCCESS] PTZ control stopped")
    
    elif command == "preset_add" and len(args) >= 2:
        device_serial, channel_no = args[0], int(args[1])
        print(f"[INFO] Device: {device_serial}, Channel: {channel_no}")
        print(f"[INFO] Calling API: {API_BASE_URL}/api/lapp/device/preset/add")
        result = preset_add(access_token, device_serial, channel_no)
        
        if result["success"]:
            preset_index = result.get("data", {}).get("index", "unknown")
            print(f"[SUCCESS] Preset added, index: {preset_index}")
    
    elif command == "preset_move" and len(args) >= 3:
        device_serial, channel_no, index = args[0], int(args[1]), int(args[2])
        print(f"[INFO] Device: {device_serial}, Channel: {channel_no}, Preset: {index}")
        print(f"[INFO] Calling API: {API_BASE_URL}/api/lapp/device/preset/move")
        result = preset_move(access_token, device_serial, channel_no, index)
        
        if result["success"]:
            print("[SUCCESS] Moving to preset")
    
    elif command == "preset_clear" and len(args) >= 3:
        device_serial, channel_no, index = args[0], int(args[1]), int(args[2])
        print(f"[INFO] Device: {device_serial}, Channel: {channel_no}, Preset: {index}")
        print(f"[INFO] Calling API: {API_BASE_URL}/api/lapp/device/preset/clear")
        result = preset_clear(access_token, device_serial, channel_no, index)
        
        if result["success"]:
            print("[SUCCESS] Preset cleared")
    
    elif command == "mirror" and len(args) >= 3:
        device_serial, channel_no, cmd = args[0], int(args[1]), int(args[2])
        print(f"[INFO] Device: {device_serial}, Channel: {channel_no}, Command: {cmd}")
        print(f"[INFO] Calling API: {API_BASE_URL}/api/lapp/device/ptz/mirror")
        result = mirror_flip(access_token, device_serial, channel_no, cmd)
        
        if result["success"]:
            print("[SUCCESS] Mirror flip executed")
    
    else:
        print(f"[ERROR] Unknown command: {command}")
        print("[INFO] Use 'python3 main.py appKey appSecret' to see usage")
        sys.exit(1)
    
    # Output result
    print("\n" + "=" * 70)
    print("RESULT")
    print("=" * 70)
    
    if result:
        if result.get("success"):
            print(f"  Status:     success")
            if result.get("message"):
                print(f"  Message:    {result['message']}")
        else:
            print(f"  Status:     failed")
            print(f"  Error:      {result.get('error', 'Unknown error')}")
            if result.get("code"):
                print(f"  Code:       {result['code']}")
    
    print("=" * 70)
    
    sys.exit(0 if (result and result.get("success")) else 1)

if __name__ == "__main__":
    main()
