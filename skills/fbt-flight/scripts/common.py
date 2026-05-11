#!/usr/bin/env python3
"""
分贝通机票助手公共模块
提供共享的工具函数和API调用封装
"""
import json
import os
import ssl
import tempfile
import urllib.request
import urllib.error
from datetime import datetime, timedelta


def get_api_url():
    """获取API服务地址"""
    return os.environ.get("FBT_API_URL", "https://app-gate.fenbeitong.com/air_biz/skill/execute")


def get_temp_file_path(filename):
    """获取跨平台的临时文件路径"""
    return os.path.join(tempfile.gettempdir(), filename)


def get_auth_file_path():
    # 使用临时目录下的文件（避免权限问题）
    return get_temp_file_path(".fbt_auth.json")


def save_api_key(api_key, phone):
    """
    保存 apiKey 到持久化文件

    Args:
        api_key: API密钥
        phone: 手机号

    Returns:
        成功返回True，失败返回False
    """
    auth_file = get_auth_file_path()

    auth_data = {
        "apiKey": api_key,
        "phone": phone,
        "auth_time": datetime.now().isoformat(),
        "expire_days": 90
    }

    try:
        with open(auth_file, 'w', encoding='utf-8') as f:
            json.dump(auth_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存 apiKey 失败: {str(e)}")
        return False


def load_api_key():
    """
    从持久化文件加载 apiKey

    Returns:
        有效的 apiKey，如果不存在或已过期返回None
    """
    auth_file = get_auth_file_path()

    if not os.path.exists(auth_file):
        return None

    try:
        with open(auth_file, 'r', encoding='utf-8') as f:
            auth_data = json.load(f)

        api_key = auth_data.get("apiKey")
        auth_time_str = auth_data.get("auth_time")
        expire_days = auth_data.get("expire_days", 90)

        if not api_key or not auth_time_str:
            return None

        # 检查是否过期
        auth_time = datetime.fromisoformat(auth_time_str)
        expire_time = auth_time + timedelta(days=expire_days)

        if datetime.now() > expire_time:
            print("apiKey 已过期，请重新鉴权")
            return None

        return api_key
    except Exception as e:
        print(f"加载 apiKey 失败: {str(e)}")
        return None


def get_api_key_info():
    """
    获取 apiKey 信息（用于状态查询）

    Returns:
        包含鉴权信息的字典，如果不存在或已过期返回None
    """
    auth_file = get_auth_file_path()

    if not os.path.exists(auth_file):
        return None

    try:
        with open(auth_file, 'r', encoding='utf-8') as f:
            auth_data = json.load(f)

        auth_time_str = auth_data.get("auth_time")
        expire_days = auth_data.get("expire_days", 90)
        phone = auth_data.get("phone")

        if not auth_time_str:
            return None

        auth_time = datetime.fromisoformat(auth_time_str)
        expire_time = auth_time + timedelta(days=expire_days)
        days_remaining = (expire_time - datetime.now()).days

        if days_remaining < 0:
            return None

        return {
            "phone": phone,
            "auth_time": auth_time.strftime("%Y-%m-%d %H:%M:%S"),
            "days_remaining": days_remaining
        }
    except Exception as e:
        return None


def call_api_without_auth(method_name, business_params, **extra_params):
    """
    调用分贝通机票API（不带 apiKey，仅用于鉴权接口）

    Args:
        method_name: API方法名
        business_params: 业务参数字典
        **extra_params: 额外的顶层参数

    Returns:
        API响应的JSON对象，失败时返回None
    """
    api_url = get_api_url()

    payload = {
        "methodName": method_name,
        "businessParams": json.dumps(business_params),
        **extra_params
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(api_url, data=data, headers=headers, method='POST')

        # 注意：生产环境应移除此行，使用默认证书验证
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(req, context=context) as response:
            response_data = response.read().decode('utf-8')
            return json.loads(response_data)
    except urllib.error.HTTPError as e:
        print(f"HTTP错误: {e.code} - {e.reason}")
        return None
    except urllib.error.URLError as e:
        print(f"URL错误: {e.reason}")
        return None
    except Exception as e:
        print(f"请求失败: {str(e)}")
        return None


def call_api(method_name, business_params, **extra_params):
    """
    调用分贝通机票API的统一封装（自动注入 apiKey）

    Args:
        method_name: API方法名（searchFlight, searchPrice, createOrder）
        business_params: 业务参数字典
        **extra_params: 额外的顶层参数（如 name, phone, idCard）

    Returns:
        API响应的JSON对象，失败时返回None
    """
    # 加载 apiKey
    api_key = load_api_key()
    if not api_key:
        print("错误: 未找到有效的 apiKey，请先执行鉴权流程")
        print("运行: python3 auth.py send <手机号>")
        return None

    api_url = get_api_url()

    payload = {
        "methodName": method_name,
        "apiKey": api_key,  # 自动注入 apiKey
        "businessParams": json.dumps(business_params),
        **extra_params
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(api_url, data=data, headers=headers, method='POST')

        # 注意：生产环境应移除此行，使用默认证书验证
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(req, context=context) as response:
            response_data = response.read().decode('utf-8')
            return json.loads(response_data)
    except urllib.error.HTTPError as e:
        print(f"HTTP错误: {e.code} - {e.reason}")
        return None
    except urllib.error.URLError as e:
        print(f"URL错误: {e.reason}")
        return None
    except Exception as e:
        print(f"请求失败: {str(e)}")
        return None


def format_timestamp(timestamp, format_str="%H:%M"):
    """
    格式化时间戳为可读时间

    Args:
        timestamp: 毫秒级时间戳
        format_str: 时间格式字符串，默认为 "%H:%M"

    Returns:
        格式化后的时间字符串
    """
    if not timestamp:
        return "--:--"
    dt = datetime.fromtimestamp(timestamp / 1000)
    return dt.strftime(format_str)


def check_api_response(response, error_prefix="操作失败"):
    """
    检查API响应是否成功

    Args:
        response: API响应对象
        error_prefix: 错误提示前缀

    Returns:
        成功返回True，失败返回False并打印错误信息
    """
    if not response:
        print(f"{error_prefix}: 无响应数据")
        return False

    if response.get("code") != 0:
        print(f"{error_prefix}")
        print(f"错误信息: {response.get('msg', '未知错误')}")
        return False

    return True