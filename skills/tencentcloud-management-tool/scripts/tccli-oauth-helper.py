#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tccli OAuth 登录辅助工具

解决 tccli auth login --browser no 在非交互式环境下无法输入验证码的问题。

用法:
  # 第一步: 生成授权链接
  python3 tccli-oauth-helper.py --get-url
  
  # 第二步: 用户访问链接登录后，获取 base64 验证码，然后:
  python3 tccli-oauth-helper.py --code "验证码字符串"
  
  # 或者一步完成（如果已有验证码）:
  python3 tccli-oauth-helper.py --code "eyJhY2Nlc3NUb2tlbi..."
  
  # 检查凭证状态:
  python3 tccli-oauth-helper.py --status
"""

import argparse
import base64
import json
import os
import random
import string
import sys
import time
from urllib.parse import urlencode

# 尝试从 tccli 动态导入常量
try:
    from tccli.oauth import _APP_ID, _AUTH_URL, _REDIRECT_URL, _SITE, _DEFAULT_LANG, _API_ENDPOINT
except (ImportError, AttributeError):
    # tccli 未安装或版本不兼容时，使用回退默认值
    _APP_ID = 100038427476
    _AUTH_URL = "https://cloud.tencent.com/open/authorize"
    _REDIRECT_URL = "https://cli.cloud.tencent.com/oauth"
    _SITE = "cn"
    _DEFAULT_LANG = "zh-CN"
    _API_ENDPOINT = "https://cli.cloud.tencent.com"

# 状态文件路径
_STATE_FILE = os.path.expanduser("~/.tccli/.oauth_state")


def get_temp_cred(access_token, site):
    """获取临时凭证（从 tccli/oauth.py 复制）"""
    import uuid
    import requests
    
    api_endpoint = _API_ENDPOINT + "/get_temp_cred"
    body = {
        "TraceId": str(uuid.uuid4()),
        "AccessToken": access_token,
        "Site": site,
    }
    http_response = requests.post(api_endpoint, json=body, verify=True)
    resp = http_response.json()

    if "Error" in resp:
        raise ValueError("get_temp_key: %s" % json.dumps(resp))

    return {
        "secretId": resp["SecretId"],
        "secretKey": resp["SecretKey"],
        "token": resp["Token"],
        "expiresAt": resp["ExpiresAt"],
    }


def cred_path_of_profile(profile):
    """凭证文件路径"""
    return os.path.join(os.path.expanduser("~"), ".tccli", profile + ".credential")


def save_credential(token, new_cred, profile):
    """保存凭证（从 tccli/oauth.py 复制）"""
    cred_path = cred_path_of_profile(profile)

    # 确保目录存在
    os.makedirs(os.path.dirname(cred_path), exist_ok=True)

    cred = {
        "type": "oauth",
        "secretId": new_cred["secretId"],
        "secretKey": new_cred["secretKey"],
        "token": new_cred["token"],
        "expiresAt": new_cred["expiresAt"],
        "oauth": {
            "openId": token["openId"],
            "accessToken": token["accessToken"],
            "expiresAt": token["expiresAt"],
            "refreshToken": token["refreshToken"],
            "site": token["site"],
        },
    }
    with open(cred_path, "w") as cred_file:
        json.dump(cred, cred_file, indent=4)


def generate_state():
    """生成随机 state"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(10))


def save_state(state):
    """保存 state 到文件"""
    os.makedirs(os.path.dirname(_STATE_FILE), exist_ok=True)
    with open(_STATE_FILE, 'w') as f:
        json.dump({'state': state, 'timestamp': time.time()}, f)


def load_state():
    """从文件加载 state"""
    try:
        with open(_STATE_FILE, 'r') as f:
            data = json.load(f)
            # 检查是否过期（10分钟）
            if time.time() - data.get('timestamp', 0) > 600:
                return None
            return data.get('state')
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def clear_state():
    """清除 state 文件"""
    try:
        os.remove(_STATE_FILE)
    except FileNotFoundError:
        pass


def get_auth_url(state, language=_DEFAULT_LANG):
    """生成授权 URL"""
    redirect_params = {
        "browser": "no",
        "lang": language,
        "site": _SITE,
    }
    redirect_query = urlencode(redirect_params)
    redirect_url = _REDIRECT_URL + "?" + redirect_query
    
    url_params = {
        "scope": "login",
        "app_id": _APP_ID,
        "redirect_url": redirect_url,
        "state": state,
    }
    url_query = urlencode(url_params)
    auth_url = _AUTH_URL + "?" + url_query
    
    return auth_url


def do_get_url(args):
    """生成授权链接"""
    state = generate_state()
    save_state(state)
    
    auth_url = get_auth_url(state)
    
    print("━" * 60)
    print("🔐 腾讯云 OAuth 授权登录")
    print("━" * 60)
    print()
    print("请在浏览器中打开以下链接完成登录：")
    print()
    print(auth_url)
    print()
    print("━" * 60)
    print("登录后，页面会显示一串 base64 编码的验证码。")
    print("请复制该验证码，然后运行以下命令完成登录：")
    print()
    print("  python3 tccli-oauth-helper.py --code \"验证码\"")
    print()
    print("或发送给 AI 助手，让它帮你完成登录。")
    print("━" * 60)
    print()
    print(f"📌 State: {state} (10分钟内有效)")
    
    return 0


def do_login_with_code(args):
    """使用验证码完成登录"""
    code = args.code.strip()
    profile = args.profile or "default"
    
    # 尝试加载保存的 state
    saved_state = load_state()
    
    try:
        # 解码验证码
        token_json = base64.b64decode(code)
        token = json.loads(token_json)
    except Exception as e:
        print(f"❌ 验证码解析失败: {e}")
        print()
        print("请确保复制了完整的 base64 验证码字符串。")
        return 1
    
    # 验证 state（如果有保存的话）
    token_state = token.get("state")
    if saved_state and token_state != saved_state:
        print(f"⚠️  警告: state 不匹配")
        print(f"   期望: {saved_state}")
        print(f"   实际: {token_state}")
        print()
        print("可能是使用了旧的授权链接。继续尝试...")
    
    try:
        # 获取临时凭证
        print("🔄 正在获取临时凭证...")
        cred = get_temp_cred(token["accessToken"], token.get("site", _SITE))
        
        # 保存凭证
        save_credential(token, cred, profile)
        clear_state()
        
        cred_path = cred_path_of_profile(profile)
        
        print()
        print("━" * 60)
        print("✅ OAuth 登录成功!")
        print("━" * 60)
        print(f"📌 配置文件: {profile}")
        print(f"📌 凭证路径: {cred_path}")
        print(f"📌 过期时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cred['expiresAt']))}")
        print("━" * 60)
        print()
        print("现在可以使用 tccli 了，例如：")
        print("  tccli cvm DescribeInstances --region ap-guangzhou")
        print()
        
        return 0
        
    except Exception as e:
        print(f"❌ 登录失败: {e}")
        return 1


def do_status(args):
    """检查凭证状态"""
    profile = args.profile or "default"
    cred_path = cred_path_of_profile(profile)
    
    print("━" * 60)
    print("🔍 tccli 凭证状态检查")
    print("━" * 60)
    print(f"📌 配置文件: {profile}")
    print(f"📌 凭证路径: {cred_path}")
    print()
    
    if not os.path.exists(cred_path):
        print("❌ 凭证文件不存在")
        print()
        print("请先运行 OAuth 登录:")
        print("  python3 tccli-oauth-helper.py --get-url")
        return 1
    
    try:
        with open(cred_path, 'r') as f:
            cred = json.load(f)
        
        cred_type = cred.get("type", "unknown")
        print(f"📌 凭证类型: {cred_type}")
        
        if cred_type == "oauth":
            expires_at = cred.get("expiresAt", 0)
            now = time.time()
            
            if expires_at > now:
                remaining = expires_at - now
                hours = int(remaining // 3600)
                minutes = int((remaining % 3600) // 60)
                print(f"📌 过期时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expires_at))}")
                print(f"📌 剩余有效期: {hours}小时{minutes}分钟")
                print()
                print("✅ 凭证有效")
            else:
                print(f"📌 过期时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expires_at))}")
                print()
                print("❌ 凭证已过期，需要重新登录")
                print()
                print("请运行: python3 tccli-oauth-helper.py --get-url")
                return 1
        else:
            # API 密钥方式
            secret_id = cred.get("secretId", "")
            if secret_id:
                print(f"📌 SecretId: {secret_id[:8]}...{secret_id[-4:]}")
                print()
                print("✅ 使用 API 密钥凭证")
            else:
                print("❌ 凭证文件格式异常")
                return 1
                
    except Exception as e:
        print(f"❌ 读取凭证失败: {e}")
        return 1
    
    print("━" * 60)
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="tccli OAuth 登录辅助工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成授权链接
  python3 tccli-oauth-helper.py --get-url
  
  # 使用验证码完成登录
  python3 tccli-oauth-helper.py --code "eyJhY2Nlc3NUb2tlbi..."
  
  # 检查凭证状态
  python3 tccli-oauth-helper.py --status
  
  # 指定配置文件
  python3 tccli-oauth-helper.py --code "验证码" --profile myprofile
"""
    )
    
    parser.add_argument("--get-url", action="store_true",
                        help="生成 OAuth 授权链接")
    parser.add_argument("--code", type=str,
                        help="base64 编码的验证码，用于完成登录")
    parser.add_argument("--status", action="store_true",
                        help="检查当前凭证状态")
    parser.add_argument("--profile", type=str, default="default",
                        help="配置文件名称 (默认: default)")
    
    args = parser.parse_args()
    
    if args.get_url:
        return do_get_url(args)
    elif args.code:
        return do_login_with_code(args)
    elif args.status:
        return do_status(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
