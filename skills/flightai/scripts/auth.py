#!/usr/bin/env python3
"""
AI机票助手 - 鉴权模块
处理用户手机号验证和 apiKey 获取
"""
import sys
import json
from common import call_api_without_auth, check_api_response, save_api_key, get_api_key_info


def send_verification_code(phone):
    """发送验证码到用户手机"""
    business_params = {
        "phone": phone,
        "action": "send_code"
    }

    print(f"\n正在向 {phone} 发送验证码...")
    response = call_api_without_auth("auth", business_params, phone=phone)

    if not check_api_response(response, "发送验证码失败"):
        return False

    print("✅ 验证码已发送，请查收短信")
    return True


def verify_and_get_api_key(phone, code):
    """验证验证码并获取 apiKey"""
    business_params = {
        "phone": phone,
        "code": code,
        "action": "verify_code"
    }

    print(f"\n正在验证...")
    response = call_api_without_auth("auth", business_params, phone=phone, verifyCode=code)

    if not check_api_response(response, "验证失败"):
        return None

    data = response.get("data", {})
    api_key = data.get("apiKey")

    if not api_key:
        print("错误: 未获取到 apiKey")
        return None

    # 保存 apiKey
    if save_api_key(api_key, phone):
        print("✅ 鉴权成功！")
        print(f"apiKey 已保存！")
        return api_key
    else:
        print("错误: apiKey 保存失败")
        return None


def check_auth_status():
    """检查当前鉴权状态"""
    info = get_api_key_info()

    if not info:
        print("❌ 未鉴权")
        print("请先完成鉴权流程")
        return False

    print("✅ 已鉴权")
    print(f"手机号: {info['phone']}")
    print(f"鉴权时间: {info['auth_time']}")
    return True


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  1. 发送验证码: python3 auth.py send <phone>")
        print("  2. 验证并获取 apiKey: python3 auth.py verify <phone> <code>")
        print("  3. 查看鉴权状态: python3 auth.py status")
        print("\n示例:")
        print("  python3 auth.py send 13800138000")
        print("  python3 auth.py verify 13800138000 123456")
        print("  python3 auth.py status")
        sys.exit(1)

    action = sys.argv[1]

    if action == "send":
        if len(sys.argv) != 3:
            print("用法: python3 auth.py send <phone>")
            sys.exit(1)
        phone = sys.argv[2]
        send_verification_code(phone)

    elif action == "verify":
        if len(sys.argv) != 4:
            print("用法: python3 auth.py verify <phone> <code>")
            sys.exit(1)
        phone = sys.argv[2]
        code = sys.argv[3]
        verify_and_get_api_key(phone, code)

    elif action == "status":
        check_auth_status()

    else:
        print(f"未知操作: {action}")
        print("支持的操作: send, verify, status")
        sys.exit(1)


if __name__ == "__main__":
    main()
