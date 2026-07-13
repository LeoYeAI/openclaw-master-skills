#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chrome启动脚本 - 按SOUL.md规则启动Chrome并验证

用法:
    python chrome_launch.py
    
返回:
    0 - 启动成功且验证通过
    1 - 启动失败
"""

import subprocess
import time
import sys
import os

def launch_chrome():
    """Launch Chrome with remote debugging"""
    chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
    user_data = r'C:\Users\Moha\AppData\Local\Google\Chrome\User Data'
    
    # Use direct subprocess instead of powershell to avoid quote issues
    cmd = [
        chrome_path,
        '--remote-debugging-port=9222',
        f'--user-data-dir={user_data}'
    ]
    
    try:
        # Start Chrome without waiting (detached)
        subprocess.Popen(cmd, shell=False)
        safe_print("Chrome launch command executed")
        return True
    except Exception as e:
        safe_print(f"Launch error: {e}")
        return False

def verify_login():
    """Verify Chrome started - 10s First Check"""
    safe_print("Waiting for Chrome to start...")
    time.sleep(10)  # First Check: 10 seconds
    
    # Try to connect to Chrome
    try:
        import requests
        response = requests.get('http://localhost:9222/json', timeout=5)
        if response.status_code == 200:
            safe_print("First Check PASS: Chrome started and CDP available")
            return True
        else:
            safe_print(f"First Check FAIL: CDP returned status {response.status_code}")
            return False
    except Exception as e:
        safe_print(f"First Check FAIL: Cannot connect to Chrome CDP - {e}")
        return False

def double_check():
    """Double Check - retry within 20 seconds"""
    safe_print("Executing Double Check (20s)...")
    time.sleep(10)  # Additional 10 seconds, total 20
    
    try:
        import requests
        response = requests.get('http://localhost:9222/json', timeout=5)
        if response.status_code == 200:
            safe_print("Double Check PASS: Chrome ready")
            return True
    except Exception as e:
        safe_print(f"Double Check FAIL: {e}")
    
    return False

def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('utf-8', errors='replace').decode('utf-8'))

def main():
    safe_print("="*50)
    safe_print("Chrome Launch and Verify")
    safe_print("="*50)
    
    # Step 1: 启动
    if not launch_chrome():
        safe_print("Launch failed, exit")
        sys.exit(1)
    
    # Step 2: First Check (10秒)
    if verify_login():
        safe_print("Verification passed, Chrome ready")
        sys.exit(0)
    
    # Step 3: Double Check (20秒)
    if double_check():
        safe_print("Verification passed (Double Check), Chrome ready")
        sys.exit(0)
    
    # 失败
    safe_print("Verification failed: Chrome not ready within 20 seconds")
    safe_print("Please check: 1. Chrome installed 2. Port 9222 not occupied")
    sys.exit(1)

if __name__ == "__main__":
    main()