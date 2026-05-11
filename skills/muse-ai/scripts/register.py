#!/usr/bin/env python3
"""Muse 注册/登录流程 — 发验证码 + 手机号登录 → 获取 authToken"""

import argparse
import json
import sys
import os

# 复用 muse_api 的接口
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from muse_api import send_code, login, member_info, MuseAPIError, _save_token

# 合法手机号号段（中国大陆）
_VALID_PHONE_PREFIXES = (
    "13", "14", "15", "16", "17", "18", "19",
)


def _validate_phone(phone):
    """校验手机号格式：11位数字 + 合法号段"""
    if not phone or not phone.isdigit() or len(phone) != 11:
        raise MuseAPIError(-2, "手机号格式不正确，请输入11位手机号")
    if not phone.startswith(_VALID_PHONE_PREFIXES):
        raise MuseAPIError(-2, f"手机号号段不正确（{phone[:3]}...），请输入正确的手机号")


def _print_json(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Muse 注册/登录工具")
    sub = parser.add_subparsers(dest="command", required=True)

    # 发送验证码
    p = sub.add_parser("send-code", help="发送手机验证码")
    p.add_argument("--phone", required=True, help="手机号")

    # 登录
    p = sub.add_parser("login", help="手机号+验证码登录")
    p.add_argument("--phone", required=True, help="手机号")
    p.add_argument("--code", required=True, help="验证码")

    # 验证 token
    p = sub.add_parser("verify", help="验证 token 有效性")
    p.add_argument("--token", required=True, help="authToken")

    args = parser.parse_args()

    try:
        if args.command == "send-code":
            _validate_phone(args.phone)
            send_code(args.phone)
            _print_json({"success": True, "message": f"验证码已发送到 {args.phone}"})

        elif args.command == "login":
            _validate_phone(args.phone)
            data = login(args.phone, args.code)
            auth_token = data.get("authToken", "")
            new_reg = data.get("newReg", False)
            if auth_token:
                _save_token(auth_token)
            _print_json({
                "success": True,
                "authToken": auth_token,
                "newReg": new_reg,
                "message": "注册成功！" if new_reg else "登录成功！",
                "next_step": "Token 已自动保存到 ~/.muse/token",
            })

        elif args.command == "verify":
            info = member_info(args.token)
            _save_token(args.token)
            _print_json({
                "valid": True,
                "credits": info.get("credits", info.get("credit", 0)),
                "memberType": info.get("memberType", 1 if info.get("paidMember") else 0),
            })

    except MuseAPIError as e:
        error_msg = e.msg
        if e.code == 401:
            error_msg = "Token 无效或已过期，请重新登录"
        elif e.code == 429:
            error_msg = "请求过于频繁，请稍后重试"
        _print_json({"success": False, "error": error_msg, "code": e.code})
        sys.exit(1)


if __name__ == "__main__":
    main()
