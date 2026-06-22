# /// script
# dependencies = [
#   "requests>=2.28",
#   "pyyaml>=6.0",
# ]
# ///
"""
宝塔面板API客户端
支持多服务器管理和API请求封装
"""

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Optional
from urllib.parse import urlencode

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .api_endpoints import API_ENDPOINTS, MIN_PANEL_VERSION, get_endpoint


def sign_request(token: str, params: Optional[dict] = None) -> dict:
    """
    生成API请求签名
    宝塔API使用 MD5(time + MD5(token)) 的签名机制

    Args:
        token: 宝塔面板API Token
        params: 请求参数

    Returns:
        包含签名的完整参数
    """
    if params is None:
        params = {}

    request_time = int(time.time())
    # 签名算法: request_token = md5(request_time + md5(token))
    token_md5 = hashlib.md5(token.encode()).hexdigest()
    request_token = hashlib.md5(f"{request_time}{token_md5}".encode()).hexdigest()

    return {
        **params,
        "request_time": request_time,
        "request_token": request_token,
    }


@dataclass
class ServerConfig:
    """服务器配置"""

    name: str
    host: str
    token: str
    timeout: int = 10000
    enabled: bool = True


@dataclass
class BtClient:
    """
    宝塔面板客户端类

    Attributes:
        name: 服务器名称
        host: 面板地址
        token: API Token
        timeout: 请求超时时间（毫秒）
    """

    name: str
    host: str
    token: str
    timeout: int = 10000
    enabled: bool = True
    _session: requests.Session = field(default=None, repr=False, compare=False)  # type: ignore

    def __post_init__(self):
        # 移除末尾斜杠
        self.host = self.host.rstrip("/")
        # 创建session
        self._session = requests.Session()
        # 配置重试策略
        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry)
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)
        # 设置默认headers
        self._session.headers.update(
            {"Content-Type": "application/x-www-form-urlencoded"}
        )
        # 禁用SSL警告（宝塔面板默认使用自签名证书）
        self._session.verify = False

    def request(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """
        发送API请求

        Args:
            endpoint: API端点
            params: 请求参数

        Returns:
            API响应数据

        Raises:
            ConnectionError: 无法连接到服务器
            TimeoutError: 请求超时
            RuntimeError: API请求失败
        """
        signed_params = sign_request(self.token, params)
        url = f"{self.host}{endpoint}"

        try:
            response = self._session.post(
                url,
                data=urlencode(signed_params),
                timeout=self.timeout / 1000,
            )
            response.raise_for_status()
            data = response.json()

            # 检查宝塔API响应状态
            if data.get("status") is False:
                raise RuntimeError(data.get("msg", "API请求失败"))

            return data

        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"无法连接到服务器: {self.host}")
        except requests.exceptions.Timeout:
            raise TimeoutError(f"请求超时: {self.host}")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"请求失败: {e}")

    def get_system_status(self) -> dict:
        """
        获取系统综合监控数据
        包含CPU、内存、磁盘、网络、负载、系统信息等

        Returns:
            原始监控数据
        """
        return self.request(API_ENDPOINTS["SYSTEM_STATUS"])

    def get_service_list(self) -> list:
        """获取服务列表"""
        result = self.request(API_ENDPOINTS["SERVICE_LIST"])
        return result if isinstance(result, list) else result.get("data", [])

    def get_site_list(self, page: int = 1, limit: int = 100) -> list:
        """
        获取PHP网站列表（传统网站）

        Args:
            page: 页码
            limit: 每页数量
        """
        params = {"type": "-1", "search": "", "p": page, "limit": limit, "table": "sites", "order": ""}
        result = self.request(API_ENDPOINTS["SITE_LIST"], params)
        return result.get("data", []) if isinstance(result, dict) else []

    def get_project_list(self, project_type: str, page: int = 1, limit: int = 100) -> list:
        """
        获取项目列表（Java/Node/Go/Python/.NET/Proxy/HTML/Other）

        Args:
            project_type: 项目类型 (Java/Node/Go/Python/net/Proxy/HTML/Other)
            page: 页码
            limit: 每页数量
        """
        from .api_endpoints import PROJECT_TYPES

        endpoint_key = PROJECT_TYPES.get(project_type)
        if not endpoint_key:
            raise ValueError(f"不支持的项目类型: {project_type}，支持的类型: {list(PROJECT_TYPES.keys())}")

        endpoint = API_ENDPOINTS[endpoint_key]
        params = {"search": "", "p": page, "limit": limit, "type_id": ""}
        result = self.request(endpoint, params)
        return result.get("data", []) if isinstance(result, dict) else []

    def get_all_sites(self) -> list:
        """
        获取所有网站和项目列表

        Returns:
            所有网站的列表，包含不同类型的项目
        """
        all_sites = []

        # 获取PHP网站
        php_sites = self.get_site_list()
        for site in php_sites:
            site["_source"] = "PHP"
            all_sites.append(site)

        # 获取各类型项目（Java/Node/Go/Python/net/Proxy/HTML/Other）
        for project_type in ["Java", "Node", "Go", "Python", "net", "Proxy", "HTML", "Other"]:
            try:
                projects = self.get_project_list(project_type)
                for proj in projects:
                    proj["_source"] = project_type
                    all_sites.append(proj)
            except Exception:
                # 忽略单个类型的获取错误
                pass

        return all_sites

    def get_database_list(self) -> list:
        """获取数据库列表"""
        result = self.request(API_ENDPOINTS["DATABASE_LIST"])
        return result if isinstance(result, list) else result.get("data", [])

    def get_firewall_status(self) -> dict:
        """获取防火墙状态"""
        return self.request(API_ENDPOINTS["FIREWALL_STATUS"])

    def get_security_logs(self, page: int = 1, limit: int = 20) -> dict:
        """
        获取安全日志

        Args:
            page: 页码
            limit: 每页数量
        """
        return self.request(API_ENDPOINTS["SECURITY_LOGS"], {"page": page, "limit": limit})

    def get_ssh_info(self) -> dict:
        """获取SSH信息"""
        return self.request(API_ENDPOINTS["SSH_INFO"])

    def get_ssh_logs(self, page: int = 1, limit: int = 20, search: str = "",
                     login_type: str = "ALL") -> dict:
        """
        获取SSH登录日志

        Args:
            page: 页码
            limit: 每页数量
            search: 搜索关键字（IP地址或用户名）
            login_type: 登录类型过滤 (ALL/password/key)

        Returns:
            SSH登录日志列表
        """
        params = {
            "search": search,
            "p": page,
            "limit": limit,
            "select": "ALL",
            "historyType": "ALL",
        }
        result = self.request(API_ENDPOINTS["SSH_LOGS"], params)
        return result if isinstance(result, dict) else {"data": result}

    def get_panel_logs(self, page: int = 1, limit: int = 20) -> dict:
        """
        获取面板操作日志

        Args:
            page: 页码
            limit: 每页数量
        """
        return self.request(API_ENDPOINTS["PANEL_LOGS"], {"page": page, "limit": limit})

    def get_error_logs(self, site_name: str) -> dict:
        """
        获取错误日志

        Args:
            site_name: 网站名称
        """
        return self.request(API_ENDPOINTS["ERROR_LOGS"], {"siteName": site_name})

    def get_task_list(self) -> dict:
        """获取任务列表"""
        return self.request(API_ENDPOINTS["TASK_LIST"])

    def get_software_info(self, name: str) -> dict:
        """
        获取软件/服务信息

        Args:
            name: 服务名称 (nginx/apache/redis/memcached/pure-ftpd等)

        Returns:
            软件信息，包含版本、状态、是否安装等
        """
        params = {"sName": name}
        return self.request(API_ENDPOINTS["SOFTWARE_INFO"], params)

    def get_php_versions(self) -> list:
        """
        获取已安装的PHP版本列表

        Returns:
            已安装的PHP版本信息列表
        """
        params = {"type": -1, "query": "php", "p": 1, "row": 30, "force": 0}
        result = self.request(API_ENDPOINTS["SOFTWARE_LIST"], params)
        return result.get("list", []) if isinstance(result, dict) else []

    def get_file_body(self, path: str) -> dict:
        """
        读取文件内容（用于读取日志文件）

        Args:
            path: 文件路径

        Returns:
            文件内容信息
        """
        params = {"path": path}
        return self.request(API_ENDPOINTS["FILE_BODY"], params)

    def get_service_log(self, service: str, log_type: str = "error") -> dict:
        """
        获取服务日志

        注意：只有已安装且运行的服务才有日志可读取。
        调用前应先检查服务的 installed 状态。

        Args:
            service: 服务名称 (nginx/apache/redis/mysql/pgsql)
            log_type: 日志类型 (error/slow)

        Returns:
            日志内容
        """
        from .api_endpoints import SERVICE_LOG_PATHS, SPECIAL_SERVICE_APIS

        # 特殊服务处理（pgsql、mysql）
        if service in SPECIAL_SERVICE_APIS:
            api_key = "log" if log_type == "error" else "slow_log"
            endpoint = SPECIAL_SERVICE_APIS[service].get(api_key)
            if endpoint:
                return self.request(endpoint)
            return {"status": False, "msg": f"不支持的日志类型: {log_type}"}

        # 标准服务日志路径（nginx、apache、redis）
        if service in SERVICE_LOG_PATHS:
            log_path = SERVICE_LOG_PATHS[service]
            return self.get_file_body(log_path)

        return {"status": False, "msg": f"不支持的服务: {service}"}

    def get_service_status(self, service: str) -> dict:
        """
        获取单个服务状态

        Args:
            service: 服务名称 (nginx/apache/redis/memcached/pure-ftpd/pgsql/php-x.x)

        Returns:
            服务状态信息
        """
        from .api_endpoints import SPECIAL_SERVICE_APIS

        # 特殊服务处理（pgsql）
        if service == "pgsql":
            endpoint = SPECIAL_SERVICE_APIS["pgsql"]["status"]
            result = self.request(endpoint)
            if result.get("status") and "data" in result:
                # 解析pgsql状态格式: {"data": ["开启", 1], "status": true}
                data = result.get("data", [])
                return {
                    "name": service,
                    "title": "PostgreSQL",
                    "status": data[1] == 1 if len(data) > 1 else False,
                    "status_text": data[0] if len(data) > 0 else "未知",
                    "installed": True,
                }
            return {"name": service, "status": False, "installed": False}

        # 标准服务通过软件接口查询
        info = self.get_software_info(service)
        if isinstance(info, dict):
            return {
                "name": service,
                "title": info.get("title", service),
                "version": info.get("version", ""),
                "status": info.get("status", False),
                "installed": info.get("setup", False),
                "pid": info.get("pid", 0),
            }
        return {"name": service, "status": False, "installed": False}

    def get_all_services_status(self, services: Optional[list] = None) -> list:
        """
        获取所有服务状态

        Args:
            services: 要查询的服务列表，为None时查询默认服务

        Returns:
            服务状态列表
        """
        from .api_endpoints import SOFTWARE_SERVICES

        if services is None:
            services = SOFTWARE_SERVICES.copy()

        results = []

        # 查询标准服务
        for service in services:
            try:
                status = self.get_service_status(service)
                results.append(status)
            except Exception as e:
                results.append({
                    "name": service,
                    "status": False,
                    "installed": False,
                    "error": str(e),
                })

        # 查询已安装的PHP版本
        try:
            php_list = self.get_php_versions()
            for php_info in php_list:
                name = php_info.get("name", "")
                if name.startswith("php-"):
                    results.append({
                        "name": name,
                        "title": php_info.get("title", name),
                        "version": php_info.get("version", ""),
                        "status": php_info.get("status", False),
                        "installed": php_info.get("setup", False),
                        "pid": php_info.get("pid", 0),
                    })
        except Exception:
            pass

        # 查询pgsql（如果安装）
        try:
            pgsql_status = self.get_service_status("pgsql")
            if pgsql_status.get("installed"):
                results.append(pgsql_status)
        except Exception:
            pass

        return results

    def get_crontab_list(self, page: int = 1, limit: int = 100, search: str = "") -> dict:
        """
        获取计划任务列表

        Args:
            page: 页码
            limit: 每页数量
            search: 搜索关键字

        Returns:
            计划任务列表
        """
        params = {"p": page, "count": limit, "search": search, "type_id": "", "order_param": ""}
        result = self.request(API_ENDPOINTS["CRONTAB_LIST"], params)
        return result if isinstance(result, dict) else {"data": result}

    def get_crontab_logs(self, task_id: int, start_timestamp: Optional[int] = None,
                         end_timestamp: Optional[int] = None) -> dict:
        """
        获取计划任务日志

        Args:
            task_id: 任务ID
            start_timestamp: 开始时间戳
            end_timestamp: 结束时间戳

        Returns:
            任务日志
        """
        params = {"id": task_id}
        if start_timestamp:
            params["start_timestamp"] = start_timestamp
        if end_timestamp:
            params["end_timestamp"] = end_timestamp
        return self.request(API_ENDPOINTS["CRONTAB_LOGS"], params)

    def health_check(self) -> bool:
        """
        健康检查

        Returns:
            是否连接成功
        """
        try:
            self.get_system_status()
            return True
        except Exception:
            return False

    def close(self):
        """关闭连接"""
        self._session.close()


class BtClientManager:
    """多服务器管理器"""

    def __init__(self):
        self.clients: dict[str, BtClient] = {}
        self.config: Optional[dict] = None
        self.global_config: dict = {
            "retryCount": 3,
            "retryDelay": 1000,
            "concurrency": 3,
            "thresholds": {"cpu": 80, "memory": 85, "disk": 90},
        }

    def load_config(self, config_path: Optional[str] = None) -> "BtClientManager":
        """
        从配置文件加载服务器

        Args:
            config_path: 配置文件路径

        Returns:
            self，支持链式调用
        """
        from .config import load_config

        self.config = load_config(config_path)

        # 加载全局配置
        if "global" in self.config:
            self.global_config.update(self.config["global"])

        # 初始化所有服务器客户端
        for server in self.config.get("servers", []):
            if server.get("enabled", True):
                client = BtClient(
                    name=server["name"],
                    host=server["host"],
                    token=server["token"],
                    timeout=server.get("timeout", 10000),
                )
                self.clients[server["name"]] = client

        return self

    def get_global_config(self) -> dict:
        """获取全局配置"""
        return self.global_config

    def get_client(self, name: str) -> BtClient:
        """
        获取客户端

        Args:
            name: 服务器名称

        Returns:
            宝塔客户端实例

        Raises:
            KeyError: 未找到服务器
        """
        if name not in self.clients:
            raise KeyError(f"未找到服务器: {name}")
        return self.clients[name]

    def get_all_clients(self) -> dict[str, BtClient]:
        """获取所有客户端"""
        return self.clients

    def add_server(self, config: dict) -> BtClient:
        """
        添加服务器

        Args:
            config: 服务器配置
        """
        client = BtClient(
            name=config["name"],
            host=config["host"],
            token=config["token"],
            timeout=config.get("timeout", 10000),
        )
        self.clients[config["name"]] = client
        return client

    def remove_server(self, name: str):
        """
        移除服务器

        Args:
            name: 服务器名称
        """
        if name in self.clients:
            self.clients[name].close()
            del self.clients[name]

    def get_server_list(self) -> list[str]:
        """获取服务器列表"""
        return list(self.clients.keys())

    def execute_all(self, action) -> dict[str, Any]:
        """
        并行执行所有服务器的操作

        Args:
            action: 异步操作函数，接收BtClient参数

        Returns:
            各服务器的执行结果
        """
        results = {}
        for name, client in self.clients.items():
            try:
                result = action(client)
                results[name] = {"success": True, "data": result}
            except Exception as e:
                results[name] = {"success": False, "error": str(e)}
        return results

    def check_all_connections(self) -> dict[str, bool]:
        """检查所有服务器连接状态"""
        return {name: client.health_check() for name, client in self.clients.items()}

    def close_all(self):
        """关闭所有连接"""
        for client in self.clients.values():
            client.close()
