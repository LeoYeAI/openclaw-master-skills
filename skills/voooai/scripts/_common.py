"""VoooAI OpenAPI 公共模块：共享函数、鉴权、路径白名单校验（Authorization: Bearer <access_key>）"""

import json
import os
import sys
import urllib.request
import urllib.error

# ── 环境变量配置 ──────────────────────────────────────────────────────────
BASE_URL = os.environ.get("VOOOAI_BASE_URL", "https://voooai.com")
ACCESS_KEY = os.environ.get("VOOOAI_ACCESS_KEY", "")

# 平台画布地址前缀（用于结果展示）
PLATFORM_URL = "https://voooai.com"


def _ensure_access_key() -> str:
    """
    确保 AccessKey 已设置，返回 AccessKey。
    如果未设置则输出错误并退出。
    """
    key = os.environ.get("VOOOAI_ACCESS_KEY", "")
    if not key:
        print("错误：请设置 VOOOAI_ACCESS_KEY 环境变量", file=sys.stderr)
        sys.exit(1)
    return key

# ── API 路径白名单 ──────────────────────────────────────────────────────────
ALLOWED_PATH_PREFIXES = (
    "/api/agent/",
    "/api/node-builder/",
    "/api/upload",
)


def validate_api_path(path: str) -> None:
    """
    校验 API 路径是否在白名单内。
    如果路径不在允许范围内，输出错误并退出。
    
    Args:
        path: API 路径（如 /api/agent/capabilities）
    """
    if not any(path.startswith(prefix) for prefix in ALLOWED_PATH_PREFIXES):
        print(f"错误：不允许的 API 路径: {path}", file=sys.stderr)
        print(f"允许的路径前缀: {', '.join(ALLOWED_PATH_PREFIXES)}", file=sys.stderr)
        sys.exit(1)


def _headers(content_type: str = "application/json") -> dict:
    """
    构建请求头（Bearer Token 认证）
    
    Args:
        content_type: Content-Type 头，默认 application/json
    
    Returns:
        请求头字典
    """
    access_key = _ensure_access_key()
    headers = {
        "Authorization": f"Bearer {access_key}",
    }
    if content_type:
        headers["Content-Type"] = content_type
    return headers


def api_get(path: str, timeout: int = 30) -> dict:
    """
    GET 请求 VoooAI OpenAPI
    
    Args:
        path: API 路径（如 /api/agent/capabilities）
        timeout: 请求超时秒数
    
    Returns:
        JSON 响应字典
    """
    validate_api_path(path)
    url = f"{BASE_URL.rstrip('/')}{path}"
    req = urllib.request.Request(url, method="GET", headers=_headers())
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8") if e.fp else ""
        print(f"API 错误 {e.code}: {err_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"网络错误: {e.reason}", file=sys.stderr)
        sys.exit(1)


def api_post(path: str, body: dict, timeout: int = 60) -> dict:
    """
    POST 请求 VoooAI OpenAPI（JSON body）
    
    Args:
        path: API 路径（如 /api/agent/nl2workflow/analyze）
        body: 请求体字典
        timeout: 请求超时秒数
    
    Returns:
        JSON 响应字典
    """
    validate_api_path(path)
    url = f"{BASE_URL.rstrip('/')}{path}"
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers=_headers(),
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8") if e.fp else ""
        print(f"API 错误 {e.code}: {err_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"网络错误: {e.reason}", file=sys.stderr)
        sys.exit(1)


def json_output(data: dict) -> None:
    """
    统一 JSON 输出格式
    
    Args:
        data: 要输出的字典
    """
    print(json.dumps(data, ensure_ascii=False, indent=2))


def error_exit(message: str, code: int = 1) -> None:
    """
    错误退出（输出到 stderr）
    
    Args:
        message: 错误消息
        code: 退出码
    """
    print(f"错误：{message}", file=sys.stderr)
    sys.exit(code)


def load_json_arg(arg: str) -> dict:
    """
    加载 JSON 参数（支持 JSON 字符串或文件路径）
    
    Args:
        arg: JSON 字符串或文件路径
    
    Returns:
        解析后的字典
    """
    # 尝试作为文件路径加载
    if os.path.isfile(arg):
        try:
            with open(arg, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            error_exit(f"无法读取文件 {arg}: {e}")
    
    # 尝试作为 JSON 字符串解析
    try:
        return json.loads(arg)
    except json.JSONDecodeError as e:
        error_exit(f"无效的 JSON: {e}")
    
    return {}  # 不会执行到这里，但为了类型检查


def parse_set_params(params: list) -> dict:
    """
    解析 --set-param 参数列表（格式：node_id.param_name=value）
    
    Args:
        params: --set-param 参数列表，如 ["node_1.prompt=hello", "node_2.duration=10"]
    
    Returns:
        解析后的参数字典，如 {"node_1": {"prompt": "hello"}, "node_2": {"duration": "10"}}
    """
    result = {}
    for param in params:
        if "=" not in param:
            print(f"警告：忽略无效参数格式 '{param}'（应为 key=value）", file=sys.stderr)
            continue
        key, value = param.split("=", 1)
        
        if "." in key:
            node_id, param_name = key.split(".", 1)
        else:
            # 如果没有 node_id 前缀，使用通用键
            node_id = "_global_"
            param_name = key
        
        if node_id not in result:
            result[node_id] = {}
        
        # 尝试解析为数字或布尔值
        try:
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            elif "." in value:
                value = float(value)
            else:
                value = int(value)
        except ValueError:
            pass  # 保持为字符串
        
        result[node_id][param_name] = value
    
    return result


def apply_params_to_workflow(workflow: dict, params: dict) -> dict:
    """
    将参数应用到工作流的节点中
    
    Args:
        workflow: 工作流数据（包含 nodes 列表）
        params: 参数字典（由 parse_set_params 返回）
    
    Returns:
        更新后的工作流数据
    """
    if not params or "nodes" not in workflow:
        return workflow
    
    for node in workflow.get("nodes", []):
        node_id = node.get("id", "")
        
        # 应用全局参数
        if "_global_" in params:
            if "widget_values" not in node:
                node["widget_values"] = {}
            node["widget_values"].update(params["_global_"])
        
        # 应用节点特定参数
        if node_id in params:
            if "widget_values" not in node:
                node["widget_values"] = {}
            node["widget_values"].update(params[node_id])
    
    return workflow
