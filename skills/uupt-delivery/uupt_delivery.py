#!/usr/bin/env python3
"""
UU跑腿同城配送服务 Agent Skill (Python 版本)
提供订单询价、发单、订单查询、取消订单、跑男追踪等功能。

用法：
    python uupt_delivery.py register --mobile="手机号" [--sms-code="验证码"]
    python uupt_delivery.py price --from-address="起始地址" --to-address="目的地址" [--city="城市名"]
    python uupt_delivery.py create --price-token="询价token" --receiver-phone="收件人电话"
    python uupt_delivery.py detail --order-code="订单编号"
    python uupt_delivery.py cancel --order-code="订单编号" [--reason="取消原因"]
    python uupt_delivery.py track --order-code="订单编号"

配置方式：
    1. 预制配置：defaults.json（appId、appSecret，随 Skill 分发）
    2. 用户配置：config.json（openId，注册后自动保存）
    3. 环境变量：UUPT_OPEN_ID（可选覆盖）
"""

import sys
import os
import json
import hashlib
import time
import argparse
import tempfile
from pathlib import Path
from urllib.parse import quote

try:
    import requests
except ImportError:
    print("[错误] 缺少 requests 库，请运行: pip install requests")
    sys.exit(1)

# 配置文件路径
CONFIG_FILE = Path(__file__).parent / "config.json"
DEFAULTS_FILE = Path(__file__).parent / "defaults.json"

# 默认 API 地址
DEFAULT_API_URL = "https://api-open.uupt.com/openapi/v3/"


def read_config() -> dict:
    """读取配置文件"""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"[警告] 读取配置文件失败: {e}")
    return {}


def read_defaults() -> dict:
    """读取预制默认配置"""
    try:
        if DEFAULTS_FILE.exists():
            with open(DEFAULTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"[警告] 读取默认配置失败: {e}")
    return {}


def save_config(config: dict) -> bool:
    """保存配置文件（合并写入）"""
    try:
        existing = read_config()
        merged = {**existing, **config}
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(merged, f, indent=2, ensure_ascii=False)
        print(f"[成功] 配置已保存到: {CONFIG_FILE}")
        return True
    except Exception as e:
        print(f"[错误] 保存配置文件失败: {e}")
        return False


def get_config() -> dict:
    """获取配置（优先级：环境变量 > config.json > defaults.json）"""
    defaults = read_defaults()
    config = read_config()
    return {
        "app_id": os.environ.get("UUPT_APP_ID") or config.get("appId") or defaults.get("appId"),
        "app_secret": os.environ.get("UUPT_APP_SECRET") or config.get("appSecret") or defaults.get("appSecret"),
        "open_id": os.environ.get("UUPT_OPEN_ID") or config.get("openId") or defaults.get("openId"),
        "api_url": os.environ.get("UUPT_API_URL") or config.get("apiUrl") or defaults.get("apiUrl") or DEFAULT_API_URL,
    }


def ensure_config() -> dict:
    """检查并确保配置完整"""
    config = get_config()
    
    if not config["app_id"] or not config["app_secret"]:
        print("\n[FATAL] 缺少应用凭证，请确认 defaults.json 文件完整")
        raise ValueError("[FATAL] 缺少应用凭证 (appId/appSecret)，请确认 defaults.json 文件存在且内容完整")
    
    if not config["open_id"]:
        print("\n[REGISTRATION_REQUIRED]")
        print("尚未注册，请先完成手机号验证获取授权。")
        print('请运行注册脚本: python uupt_delivery.py register --mobile="您的手机号"')
        raise ValueError("[REGISTRATION_REQUIRED] 尚未注册，请先完成手机号验证获取授权")
    
    return config


def generate_md5(text: str) -> str:
    """生成 MD5 签名"""
    return hashlib.md5(text.encode("utf-8")).hexdigest().upper()


def post_request(biz_params: dict, api_path: str) -> dict:
    """发送 API 请求（需要 openId 的业务接口）"""
    config = ensure_config()
    timestamp = int(time.time())
    biz_json = json.dumps(biz_params, ensure_ascii=False, separators=(",", ":"))
    
    sign_str = biz_json + config["app_secret"] + str(timestamp)
    sign = generate_md5(sign_str)
    
    payload = {
        "openId": config["open_id"],
        "timestamp": timestamp,
        "biz": biz_json,
        "sign": sign,
    }
    
    url = config["api_url"] + api_path
    headers = {
        "X-App-Id": config["app_id"],
        "Content-Type": "application/json",
    }
    
    print(f"[请求] 正在请求: {api_path}...")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            print("[成功] 请求成功\n")
            return response.json()
        else:
            print(f"[错误] 请求失败: HTTP {response.status_code}")
            return {"error": f"HTTP {response.status_code}"}
    except requests.RequestException as e:
        print(f"[错误] 请求异常: {e}")
        return {"error": str(e)}


def post_unauthorized_request(biz_params: dict, api_path: str) -> dict:
    """发送无需 openId 的 API 请求（用于注册/授权接口）"""
    config = get_config()
    
    if not config["app_id"] or not config["app_secret"]:
        raise ValueError("[FATAL] 缺少应用凭证 (appId/appSecret)，请确认 defaults.json 文件存在且内容完整")
    
    timestamp = int(time.time())
    biz_json = json.dumps(biz_params, ensure_ascii=False, separators=(",", ":"))
    
    sign_str = biz_json + config["app_secret"] + str(timestamp)
    sign = generate_md5(sign_str)
    
    payload = {
        "timestamp": timestamp,
        "biz": biz_json,
        "sign": sign,
    }
    
    url = config["api_url"] + api_path
    headers = {
        "X-App-Id": config["app_id"],
        "Content-Type": "application/json",
    }
    
    print(f"[请求] 正在请求: {api_path}...")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            print("[成功] 请求成功\n")
            return response.json()
        else:
            print(f"[错误] 请求失败: HTTP {response.status_code}")
            return {"error": f"HTTP {response.status_code}"}
    except requests.RequestException as e:
        print(f"[错误] 请求异常: {e}")
        return {"error": str(e)}


def get_public_ip() -> str:
    """获取用户公网 IP
    使用多个备用服务，提高成功率
    """
    ip_services = [
        {"url": "https://httpbin.org/ip", "extract": lambda d: d.get("origin")},
        {"url": "https://ipinfo.io/json", "extract": lambda d: d.get("ip")},
        {"url": "https://api64.ipify.org?format=json", "extract": lambda d: d.get("ip")},
        {"url": "https://api.ipify.org?format=json", "extract": lambda d: d.get("ip")},
    ]

    for service in ip_services:
        try:
            response = requests.get(service["url"], timeout=5)
            ip = service["extract"](response.json())
            if ip:
                # 处理可能的逗号分隔的多个IP
                clean_ip = ip.split(",")[0].strip()
                return clean_ip
        except Exception as e:
            print(f"[IP查询] {service['url']} 失败: {e}")
            continue

    print("[错误] 所有IP查询服务均不可用")
    return ""


def send_sms_code(user_mobile: str, user_ip: str, image_code: str = "") -> dict:
    """发送短信验证码"""
    if not user_mobile:
        raise ValueError("手机号为必填项")
    if not user_ip:
        raise ValueError("用户公网 IP 为必填项")
    
    biz = {
        "userMobile": user_mobile,
        "userIp": user_ip,
        "imageCode": image_code or "",
    }
    
    print("[注册] 正在发送短信验证码...")
    return post_unauthorized_request(biz, "user/unauthorized/sendSmsCode")


def user_auth(user_mobile: str, user_ip: str, sms_code: str) -> dict:
    """商户授权（获取 openId）"""
    if not user_mobile:
        raise ValueError("手机号为必填项")
    if not user_ip:
        raise ValueError("用户公网 IP 为必填项")
    if not sms_code:
        raise ValueError("短信验证码为必填项")
    
    biz = {
        "userMobile": user_mobile,
        "userIp": user_ip,
        "smsCode": sms_code,
        "cityName": "郑州市",
        "countyName": "",
    }
    
    print("[注册] 正在进行商户授权...")
    result = post_unauthorized_request(biz, "user/unauthorized/auth")
    
    if result and result.get("body") and result["body"].get("openId"):
        save_config({"openId": result["body"]["openId"]})
        print("[成功] 授权成功，openId 已保存")
    
    return result


def format_price(price_in_fen: int) -> str:
    """格式化价格（分转元）"""
    return f"{price_in_fen / 100:.2f}"


# ============ 业务功能 ============

def order_price(from_address: str, to_address: str, city_name: str = "郑州市") -> dict:
    """订单询价"""
    if not from_address or not to_address:
        raise ValueError("起始地址和目的地址为必填项")
    
    # 确保城市名带"市"
    if city_name and not city_name.endswith("市"):
        city_name = city_name + "市"
    
    biz = {
        "fromAddress": from_address,
        "toAddress": to_address,
        "sendType": "SEND",
        "cityName": city_name,
        "specialChannel": 2,
    }
    
    print("[询价] 正在查询配送价格...")
    return post_request(biz, "order/orderPrice")


def create_order(price_token: str, receiver_phone: str) -> dict:
    """创建订单"""
    if not price_token:
        raise ValueError("priceToken 为必填项，请先调用订单询价接口")
    if not receiver_phone:
        raise ValueError("收件人电话为必填项")
    
    biz = {
        "priceToken": price_token,
        "receiver_phone": receiver_phone,
        "pushType": "OPEN_ORDER",
        "payType": "BALANCE_PAY",
        "specialChannel": 2,
        "specialType": "NOT_NEED_WARM",
    }
    
    print("[下单] 正在创建订单...")
    return post_request(biz, "order/addOrder")


def order_detail(order_code: str) -> dict:
    """查询订单详情"""
    if not order_code:
        raise ValueError("订单编号为必填项")
    
    biz = {"order_code": order_code}
    
    print("[查询] 正在查询订单详情...")
    return post_request(biz, "order/orderDetail")


def cancel_order(order_code: str, reason: str = "") -> dict:
    """取消订单"""
    if not order_code:
        raise ValueError("订单编号为必填项")
    
    biz = {
        "order_code": order_code,
        "reason": reason or "",
    }
    
    print("[取消] 正在取消订单...")
    return post_request(biz, "order/cancelOrder")


def driver_track(order_code: str) -> dict:
    """跑男实时追踪"""
    if not order_code:
        raise ValueError("订单编号为必填项")
    
    biz = {"order_code": order_code}
    
    print("[追踪] 正在查询跑男信息...")
    return post_request(biz, "order/driverTrack")


# ============ 结果格式化 ============

def format_price_result(result: dict) -> None:
    """格式化询价结果"""
    print("[结果] 询价结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if result.get("data") and result["data"].get("priceInfo"):
        data = result["data"]
        print("\n[价格] 价格摘要:")
        price_info = data["priceInfo"]
        if "totalPrice" in price_info:
            print(f"   预估费用: {format_price(price_info['totalPrice'])} 元")
        if data.get("priceToken"):
            print(f"   priceToken: {data['priceToken']}")
            print("\n[提示] 使用此 priceToken 创建订单")


def format_create_result(result: dict) -> None:
    """格式化创建订单结果"""
    print("[结果] 创建结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if result.get("data") and result["data"].get("order_code"):
        data = result["data"]
        # 检查是否需要支付（余额不足）
        if data.get("orderUrl"):
            payment_url = data["orderUrl"]
            order_code = data["order_code"]
            
            # 检测是否为微信支付 URL
            is_wechat_pay = payment_url.startswith("weixin://")
            
            print("\n[警告] 账户余额不足，需要完成支付")
            print(f"   订单编号: {order_code}")
            
            if is_wechat_pay:
                # 微信支付：下载二维码图片到本地
                qrcode_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={quote(payment_url, safe='')}"
                
                print("\n[支付] 微信支付")
                print("   正在生成支付二维码...")
                
                try:
                    # 下载二维码图片到本地临时目录
                    temp_dir = tempfile.gettempdir()
                    qr_file_name = f"wechat_pay_{order_code}.png"
                    qr_file_path = os.path.join(temp_dir, qr_file_name)
                    
                    response = requests.get(qrcode_url, timeout=10)
                    response.raise_for_status()
                    
                    with open(qr_file_path, 'wb') as f:
                        f.write(response.content)
                    
                    print("   二维码已生成！")
                    print("   请使用微信扫码支付")
                    
                    # 输出特殊标记，供 Agent 识别
                    print("\n[PAYMENT_REQUIRED]")
                    print("[WECHAT_PAY_QRCODE]")
                    print(f"ORDER_CODE={order_code}")
                    print(f"PAYMENT_URL={payment_url}")
                    print(f"QRCODE_FILE={qr_file_path}")
                    print(f"QRCODE_URL={qrcode_url}")
                except Exception as e:
                    print(f"   下载二维码失败: {e}")
                    print(f"   请手动访问二维码链接: {qrcode_url}")
                    
                    print("\n[PAYMENT_REQUIRED]")
                    print("[WECHAT_PAY_QRCODE]")
                    print(f"ORDER_CODE={order_code}")
                    print(f"PAYMENT_URL={payment_url}")
                    print(f"QRCODE_URL={qrcode_url}")
            else:
                # 非微信支付（如支付宝）：直接输出链接
                print("\n[支付] 请点击以下链接完成支付：")
                print(f"   支付链接: {payment_url}")
                
                # 输出特殊标记，供 Agent 识别
                print("\n[PAYMENT_REQUIRED]")
                print(f"ORDER_CODE={order_code}")
                print(f"PAYMENT_URL={payment_url}")
            
            print("\n   支付完成后，订单将自动生效")
        else:
            print("\n[成功] 订单创建成功!")
            print(f"   订单编号: {data['order_code']}")
            print("\n[提示] 使用订单编号可查询订单详情或跟踪跑男位置")


def format_detail_result(result: dict, order_code: str) -> None:
    """格式化订单详情结果"""
    print("[结果] 订单详情:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if result.get("data"):
        data = result["data"]
        print("\n[详情] 订单摘要:")
        print(f"   订单编号: {data.get('order_code', order_code)}")
        print(f"   订单状态: {data.get('order_status', '-')}")
        if data.get("price"):
            print(f"   配送费用: {format_price(data['price'])} 元")
        if data.get("driver_name"):
            print(f"   骑手姓名: {data['driver_name']}")
            print(f"   骑手电话: {data.get('driver_phone', '-')}")


def format_cancel_result(result: dict, order_code: str, reason: str) -> None:
    """格式化取消订单结果"""
    print("[结果] 取消结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if result.get("code") in [0, "0"]:
        print("\n[成功] 订单已取消")
        print(f"   订单编号: {order_code}")
        if reason:
            print(f"   取消原因: {reason}")


def format_track_result(result: dict) -> None:
    """格式化跑男追踪结果"""
    print("[结果] 跑男信息:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if result.get("data"):
        data = result["data"]
        print("\n[骑手] 跑男摘要:")
        if data.get("driver_name"):
            print(f"   骑手姓名: {data['driver_name']}")
            print(f"   联系电话: {data.get('driver_phone', '-')}")
        if data.get("longitude") and data.get("latitude"):
            print(f"   当前位置: {data['longitude']}, {data['latitude']}")
        if data.get("distance"):
            print(f"   距离目的地: {data['distance']} 米")


# ============ 命令行入口 ============

def print_usage():
    """打印使用说明"""
    usage = """
UU跑腿同城配送服务 (Python 版本)

用法:
  python uupt_delivery.py <命令> [参数]

命令:
  register  手机号注册/获取授权
  price     订单询价
  create    创建订单
  detail    查询订单详情
  cancel    取消订单
  track     跑男实时追踪

示例:
  python uupt_delivery.py register --mobile="13800138000"
  python uupt_delivery.py register --mobile="13800138000" --sms-code="123456"
  python uupt_delivery.py price --from-address="郑州市金水区农业路" --to-address="郑州市二七区德化街"
  python uupt_delivery.py create --price-token="xxx" --receiver-phone="13800138000"
  python uupt_delivery.py detail --order-code="UU123456789"
  python uupt_delivery.py cancel --order-code="UU123456789" --reason="用户改变主意"
  python uupt_delivery.py track --order-code="UU123456789"

首次使用:
  运行任何命令时会自动检测是否需要注册。
  如需手动注册: python uupt_delivery.py register --mobile="您的手机号"
    """.strip()
    print(usage)


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ["-h", "--help"]:
        print_usage()
        sys.exit(0)
    
    command = sys.argv[1].lower()
    
    parser = argparse.ArgumentParser(add_help=False)
    
    try:
        if command == "register":
            parser.add_argument("--mobile", required=True, help="用户手机号")
            parser.add_argument("--sms-code", default="", help="短信验证码")
            parser.add_argument("--image-code", default="", help="图片验证码")
            parser.add_argument("--ip", default="", help="手动指定公网IP")
            args = parser.parse_args(sys.argv[2:])
            
            # 获取公网 IP
            user_ip = args.ip
            if not user_ip:
                print("[注册] 正在获取公网 IP...")
                user_ip = get_public_ip()
                if not user_ip:
                    print("[错误] 无法自动获取公网 IP，请使用 --ip 参数手动指定")
                    sys.exit(1)
                print(f"   公网 IP: {user_ip}")
            
            if args.sms_code:
                # 第二步：完成授权
                print("\n[注册] 正在完成商户授权...")
                auth_result = user_auth(args.mobile, user_ip, args.sms_code)
                
                if auth_result and auth_result.get("body") and auth_result["body"].get("openId"):
                    print("\n[REGISTRATION_SUCCESS]")
                    print(f"[成功] 注册成功！openId 已保存到配置文件。")
                    print(f"   openId: {auth_result['body']['openId']}")
                else:
                    print("\n[REGISTRATION_FAILED]")
                    print("[错误] 授权失败")
                    if auth_result:
                        print(f"   错误码: {auth_result.get('code', '-')}")
                        print(f"   错误信息: {auth_result.get('msg', '-')}")
                    print("\n[提示] 请重新发送验证码后重试")
                    sys.exit(1)
            else:
                # 第一步：发送短信验证码
                print("\n[注册] 正在发送短信验证码...")
                sms_result = send_sms_code(args.mobile, user_ip, args.image_code)
                
                if not sms_result:
                    print("[错误] 发送验证码失败，请稍后重试")
                    sys.exit(1)
                
                # 检查是否需要图片验证码
                if str(sms_result.get("code", "")) == "88100106":
                    print("\n[IMAGE_CAPTCHA_REQUIRED]")
                    if sms_result.get("msg"):
                        print(f"IMAGE_DATA=data:image/png;base64,{sms_result['msg']}")
                    print("\n[警告] 需要图片验证码，请识别图片中的数字后重新运行:")
                    print(f'   python uupt_delivery.py register --mobile="{args.mobile}" --image-code="图片中的数字"')
                    sys.exit(2)
                
                if str(sms_result.get("code", "")) == "1":
                    print("\n[SMS_SENT]")
                    print("[成功] 验证码已发送，请查看手机短信。")
                    print("\n[提示] 收到验证码后，请运行:")
                    print(f'   python uupt_delivery.py register --mobile="{args.mobile}" --sms-code="收到的验证码"')
                else:
                    print(f"\n[错误] 发送验证码失败: {sms_result.get('msg', '未知错误')}")
                    sys.exit(1)
        
        elif command == "price":
            parser.add_argument("--from-address", required=True, help="起始地址")
            parser.add_argument("--to-address", required=True, help="目的地址")
            parser.add_argument("--city", default="郑州市", help="城市名称")
            args = parser.parse_args(sys.argv[2:])
            
            result = order_price(args.from_address, args.to_address, args.city)
            format_price_result(result)
            
        elif command == "create":
            parser.add_argument("--price-token", required=True, help="询价返回的token")
            parser.add_argument("--receiver-phone", required=True, help="收件人电话")
            args = parser.parse_args(sys.argv[2:])
            
            result = create_order(args.price_token, args.receiver_phone)
            format_create_result(result)
            
        elif command == "detail":
            parser.add_argument("--order-code", required=True, help="订单编号")
            args = parser.parse_args(sys.argv[2:])
            
            result = order_detail(args.order_code)
            format_detail_result(result, args.order_code)
            
        elif command == "cancel":
            parser.add_argument("--order-code", required=True, help="订单编号")
            parser.add_argument("--reason", default="", help="取消原因")
            args = parser.parse_args(sys.argv[2:])
            
            result = cancel_order(args.order_code, args.reason)
            format_cancel_result(result, args.order_code, args.reason)
            
        elif command == "track":
            parser.add_argument("--order-code", required=True, help="订单编号")
            args = parser.parse_args(sys.argv[2:])
            
            result = driver_track(args.order_code)
            format_track_result(result)
            
        else:
            print(f"[错误] 未知命令: {command}")
            print("   支持的命令: register, price, create, detail, cancel, track")
            print("   使用 -h 查看帮助")
            sys.exit(1)
            
    except ValueError as e:
        print(f"[错误] 参数错误: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n已取消。")
        sys.exit(0)


if __name__ == "__main__":
    main()
