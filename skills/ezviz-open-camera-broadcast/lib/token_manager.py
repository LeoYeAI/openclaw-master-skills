#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ezviz Global Token Manager (萤石全局 Token 管理器)

提供全局 Token 缓存管理，支持多个技能共享同一个 Token。

功能:
- 全局 Token 缓存（系统临时目录）
- 自动检测 Token 是否过期
- 到期前 5 分钟自动刷新
- 支持多账号（基于 appKey:appSecret 哈希）
- 原子写入，确保数据安全

Usage:
    from token_manager import get_cached_token, refresh_token
    
    # 获取 Token（优先缓存，过期自动刷新）
    token_result = get_cached_token(app_key, app_secret)
    if token_result["success"]:
        access_token = token_result["access_token"]
    
    # 强制刷新 Token
    token_result = refresh_token(app_key, app_secret)
"""

import os
import sys
import time
import json
import hashlib
import tempfile
import requests
from datetime import datetime

# Configuration
TOKEN_GET_API_URL = "https://openai.ys7.com/api/lapp/token/get"

# Cache configuration
CACHE_DIR_NAME = "ezviz_global_token_cache"
CACHE_FILE_NAME = "global_token_cache.json"
TOKEN_BUFFER_TIME = 5 * 60 * 1000  # 5 minutes buffer before expiry


def get_cache_dir():
    """Get global cache directory path."""
    base_temp = tempfile.gettempdir()
    cache_dir = os.path.join(base_temp, CACHE_DIR_NAME)
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def get_cache_file_path():
    """Get global cache file path."""
    return os.path.join(get_cache_dir(), CACHE_FILE_NAME)


def generate_cache_key(app_key, app_secret):
    """Generate unique cache key based on appKey and appSecret."""
    return hashlib.md5(f"{app_key}:{app_secret}".encode()).hexdigest()


def get_current_timestamp():
    """Get current Unix timestamp in milliseconds."""
    return int(time.time() * 1000)


def load_token_cache():
    """
    Load all cached tokens from global cache file.
    
    Returns:
        dict: All cached token data or empty dict if not exists
    """
    cache_file = get_cache_file_path()
    
    if not os.path.exists(cache_file):
        return {}
    
    try:
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)
        return cache_data
    
    except Exception as e:
        print(f"[WARNING] Failed to load token cache: {e}", file=sys.stderr)
        return {}


def save_token_cache(cache_data):
    """
    Save all tokens to global cache file (atomic write).
    
    Args:
        cache_data: Dict of all cached tokens
    """
    cache_file = get_cache_file_path()
    cache_dir = get_cache_dir()
    
    try:
        # Write to temp file first, then rename (atomic operation)
        temp_file = cache_file + ".tmp"
        with open(temp_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
        
        os.replace(temp_file, cache_file)
        
        # Set file permissions (readable only by owner)
        os.chmod(cache_file, 0o600)
        
        return True
    
    except Exception as e:
        print(f"[WARNING] Failed to save token cache: {e}", file=sys.stderr)
        return False


def get_cached_token(app_key, app_secret, use_cache=True):
    """
    Get access token, using cached version if available and valid.
    
    Args:
        app_key: Ezviz app key
        app_secret: Ezviz app secret
        use_cache: Whether to use cached token (default True)
    
    Returns:
        dict: {
            success: bool,
            access_token: str,
            expire_time: int,
            from_cache: bool,
            error: str (optional)
        }
    """
    cache_key = generate_cache_key(app_key, app_secret)
    
    # Try to load from cache first
    if use_cache:
        all_cache = load_token_cache()
        
        if cache_key in all_cache:
            cached = all_cache[cache_key]
            expire_time = cached.get("expire_time", 0)
            current_time = get_current_timestamp()
            
            # Check if cache is still valid (with buffer time)
            if current_time + TOKEN_BUFFER_TIME < expire_time:
                expire_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expire_time / 1000))
                print(f"[INFO] Using cached global token, expires: {expire_str}")
                return {
                    "success": True,
                    "access_token": cached["access_token"],
                    "expire_time": expire_time,
                    "from_cache": True
                }
            else:
                print(f"[INFO] Cached token expired or about to expire, will get new one")
    
    # Cache miss or expired, get new token
    return refresh_token(app_key, app_secret, cache_key)


def refresh_token(app_key, app_secret, cache_key=None):
    """
    Get new access token from Ezviz API and save to cache.
    
    Args:
        app_key: Ezviz app key
        app_secret: Ezviz app secret
        cache_key: Pre-computed cache key (optional)
    
    Returns:
        dict: {
            success: bool,
            access_token: str,
            expire_time: int,
            from_cache: bool,
            error: str (optional)
        }
    """
    print(f"[INFO] Getting access token from Ezviz API...")
    
    if cache_key is None:
        cache_key = generate_cache_key(app_key, app_secret)
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "appKey": app_key,
        "appSecret": app_secret
    }
    
    try:
        response = requests.post(
            TOKEN_GET_API_URL,
            headers=headers,
            data=data,
            timeout=30
        )
        
        result = response.json()
        
        if result.get("code") == "200":
            data = result.get("data", {})
            access_token = data.get("accessToken", "")
            expire_time = data.get("expireTime", 0)
            expire_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expire_time / 1000))
            print(f"[SUCCESS] Token obtained, expires: {expire_str}")
            
            # Save to global cache
            all_cache = load_token_cache()
            all_cache[cache_key] = {
                "cache_key": cache_key,
                "access_token": access_token,
                "expire_time": expire_time,
                "created_at": get_current_timestamp(),
                "app_key_prefix": app_key[:8] + "..." if len(app_key) > 8 else app_key
            }
            
            if save_token_cache(all_cache):
                print(f"[INFO] Token saved to global cache")
            
            return {
                "success": True,
                "access_token": access_token,
                "expire_time": expire_time,
                "from_cache": False
            }
        else:
            error_msg = result.get("msg", "Unknown error")
            print(f"[ERROR] Get token failed: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "code": result.get("code")
            }
    
    except Exception as e:
        print(f"[ERROR] Get token failed: {type(e).__name__}: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def clear_token_cache(app_key=None, app_secret=None):
    """
    Clear token cache.
    
    Args:
        app_key: Specific app key to clear (optional, clears all if None)
        app_secret: Specific app secret to clear (optional, requires app_key)
    
    Returns:
        bool: True if successful
    """
    try:
        if app_key and app_secret:
            # Clear specific token
            cache_key = generate_cache_key(app_key, app_secret)
            all_cache = load_token_cache()
            
            if cache_key in all_cache:
                del all_cache[cache_key]
                save_token_cache(all_cache)
                print(f"[INFO] Cleared cached token for app: {app_key[:8]}...")
            else:
                print(f"[INFO] No cached token found for app: {app_key[:8]}...")
        else:
            # Clear all tokens
            cache_file = get_cache_file_path()
            if os.path.exists(cache_file):
                os.remove(cache_file)
                print(f"[INFO] Cleared all cached tokens")
            else:
                print(f"[INFO] No cached tokens to clear")
        
        return True
    
    except Exception as e:
        print(f"[ERROR] Failed to clear cache: {e}")
        return False


def list_cached_tokens():
    """
    List all cached tokens (without showing actual tokens).
    
    Returns:
        list: List of cached token info dicts
    """
    all_cache = load_token_cache()
    result = []
    
    for cache_key, data in all_cache.items():
        expire_time = data.get("expire_time", 0)
        current_time = get_current_timestamp()
        is_valid = current_time + TOKEN_BUFFER_TIME < expire_time
        
        result.append({
            "cache_key": cache_key[:16] + "...",
            "app_key_prefix": data.get("app_key_prefix", "unknown"),
            "expire_time": expire_time,
            "expire_str": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expire_time / 1000)),
            "is_valid": is_valid,
            "created_at": data.get("created_at", 0)
        })
    
    return result


# CLI interface for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Ezviz Global Token Manager")
    parser.add_argument("action", choices=["get", "refresh", "clear", "list"],
                       help="Action to perform")
    parser.add_argument("--app-key", help="Ezviz app key")
    parser.add_argument("--app-secret", help="Ezviz app secret")
    
    args = parser.parse_args()
    
    if args.action == "list":
        tokens = list_cached_tokens()
        if tokens:
            print(f"\n{'='*60}")
            print("CACHED TOKENS")
            print(f"{'='*60}")
            for token in tokens:
                status = "✅ Valid" if token["is_valid"] else "❌ Expired"
                print(f"\nApp: {token['app_key_prefix']}")
                print(f"  Cache Key: {token['cache_key']}")
                print(f"  Expires: {token['expire_str']}")
                print(f"  Status: {status}")
        else:
            print("No cached tokens found.")
    
    elif args.action == "clear":
        clear_token_cache(args.app_key, args.app_secret)
    
    elif args.action in ["get", "refresh"]:
        if not args.app_key or not args.app_secret:
            print("Error: --app-key and --app-secret required for get/refresh actions")
            sys.exit(1)
        
        use_cache = (args.action == "get")
        result = get_cached_token(args.app_key, args.app_secret, use_cache=use_cache)
        
        if result["success"]:
            print(f"\nAccess Token: {result['access_token'][:30]}...")
            print(f"Expires: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result['expire_time'] / 1000))}")
            print(f"From Cache: {result['from_cache']}")
        else:
            print(f"\nFailed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
