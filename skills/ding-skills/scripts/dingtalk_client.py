"""钉钉 API 客户端 - 封装认证和 HTTP 请求，支持 OpenAPI 和 TOP API"""

import os
import sys
import json
import requests

API_BASE = "https://api.dingtalk.com"
OPEN_API_BASE = f"{API_BASE}/v1.0"
TOP_API_BASE = "https://oapi.dingtalk.com"


def get_credentials():
    app_key = os.environ.get("DINGTALK_APP_KEY")
    app_secret = os.environ.get("DINGTALK_APP_SECRET")
    if not app_key or not app_secret:
        print(json.dumps({
            "success": False,
            "error": {
                "code": "MISSING_CREDENTIALS",
                "message": "缺少钉钉应用凭证，请设置环境变量 DINGTALK_APP_KEY 和 DINGTALK_APP_SECRET",
            }
        }, ensure_ascii=False, indent=2))
        sys.exit(1)
    return app_key, app_secret


def get_access_token():
    app_key, app_secret = get_credentials()
    print("正在获取 access_token...", file=sys.stderr)
    resp = requests.post(f"{OPEN_API_BASE}/oauth2/accessToken", json={
        "appKey": app_key,
        "appSecret": app_secret,
    })
    data = resp.json()
    token = data.get("accessToken")
    if not token:
        print(json.dumps({
            "success": False,
            "error": {
                "code": data.get("code", "UNKNOWN"),
                "message": data.get("message", "获取 access_token 失败"),
            }
        }, ensure_ascii=False, indent=2))
        sys.exit(1)
    print("access_token 获取成功", file=sys.stderr)
    return token


def api_request(method, path, token, json_body=None, params=None, api_version="v1.0"):
    """OpenAPI 请求 (api.dingtalk.com)，通过 header 传递 token"""
    headers = {"x-acs-dingtalk-access-token": token}
    url = f"{API_BASE}/{api_version}{path}"
    resp = requests.request(method, url, headers=headers, json=json_body, params=params)
    if resp.status_code >= 400:
        data = resp.json() if resp.text else {}
        raise ApiError(
            code=data.get("code", f"HTTP_{resp.status_code}"),
            message=data.get("message", resp.text),
            request_id=data.get("requestid"),
        )
    if resp.status_code == 204 or not resp.text:
        return {}
    return resp.json()


def top_api_request(method, path, token, json_body=None):
    """TOP API 请求 (oapi.dingtalk.com)，通过 query 参数传递 token，响应格式带 errcode/result"""
    url = f"{TOP_API_BASE}{path}"
    params = {"access_token": token}
    resp = requests.request(method, url, params=params, json=json_body)
    if resp.status_code >= 400:
        data = resp.json() if resp.text else {}
        raise ApiError(
            code=data.get("code", f"HTTP_{resp.status_code}"),
            message=data.get("message", resp.text),
        )
    data = resp.json()
    if data.get("errcode", 0) != 0:
        raise ApiError(
            code=str(data.get("errcode")),
            message=data.get("errmsg", "未知错误"),
        )
    return data


class ApiError(Exception):
    def __init__(self, code, message, request_id=None):
        self.code = code
        self.api_message = message
        self.request_id = request_id
        super().__init__(f"{code}: {message}")


def handle_error(e):
    if isinstance(e, ApiError):
        print(json.dumps({
            "success": False,
            "error": {
                "code": e.code,
                "message": e.api_message,
                "requestId": e.request_id,
            }
        }, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({
            "success": False,
            "error": {
                "code": "UNKNOWN_ERROR",
                "message": str(e),
            }
        }, ensure_ascii=False, indent=2))


def get_robot_code(arg_value=None):
    """获取 robotCode：优先使用传入参数，其次读取环境变量 DINGTALK_ROBOT_CODE"""
    code = arg_value or os.environ.get("DINGTALK_ROBOT_CODE")
    if not code:
        print(json.dumps({
            "success": False,
            "error": {
                "code": "MISSING_ROBOT_CODE",
                "message": "缺少 robotCode，请通过命令行参数传入或设置环境变量 DINGTALK_ROBOT_CODE",
            }
        }, ensure_ascii=False, indent=2))
        sys.exit(1)
    return code


def output(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))
