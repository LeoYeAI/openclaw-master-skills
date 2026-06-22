# /// script
# dependencies = []
# ///
"""
宝塔面板 API 端点定义
定义所有宝塔面板 API 接口路径
"""

# 宝塔面板版本要求
MIN_PANEL_VERSION = "9.0.0"

# API 端点定义
# 格式: 端点路径?动作参数
API_ENDPOINTS = {
    # 系统状态（综合接口，包含CPU、内存、磁盘、网络、负载等）
    "SYSTEM_STATUS": "/system?action=GetNetWork",  # 综合监控数据接口

    # 日志相关
    "PANEL_LOGS": "/logs?action=GetLogs",
    "ERROR_LOGS": "/site?action=GetErrorLog",
    "SITE_LOGS": "/site?action=GetSiteLogs",
    "FILE_BODY": "/files?action=GetFileBody",  # 读取文件内容

    # 安全相关
    "FIREWALL_STATUS": "/safe?action=GetFirewallStatus",
    "SECURITY_LOGS": "/safe?action=GetLogs",
    "SSH_INFO": "/safe?action=GetSshInfo",
    "SSH_LOGS": "/mod/ssh/com/get_ssh_list",  # SSH登录日志

    # 服务管理
    "SERVICE_LIST": "/system?action=GetServiceList",
    "SERVICE_STATUS": "/system?action=GetServiceStatus",
    "SOFTWARE_INFO": "/plugin?action=get_soft_find",  # 获取软件信息，参数 sName=服务名
    "SOFTWARE_LIST": "/plugin?action=get_soft_list",  # 获取软件列表

    # 网站管理 - PHP项目（传统网站）
    "SITE_LIST": "/datalist/data/get_data_list",  # 需要参数 table=sites

    # 项目管理 - 不同类型的项目有不同端点
    "PROJECT_JAVA_LIST": "/mod/java/project/project_list",
    "PROJECT_NODE_LIST": "/project/nodejs/get_project_list",
    "PROJECT_GO_LIST": "/project/go/get_project_list",
    "PROJECT_PYTHON_LIST": "/project/python/GetProjectList",
    "PROJECT_NET_LIST": "/project/net/get_project_list",
    "PROJECT_PROXY_LIST": "/mod/proxy/com/get_list",  # 反代项目
    "PROJECT_HTML_LIST": "/project/html/get_project_list",  # HTML静态项目
    "PROJECT_OTHER_LIST": "/project/other/get_project_list",  # 其他项目

    # 数据库
    "DATABASE_LIST": "/database?action=GetDatabases",

    # 任务管理
    "TASK_LIST": "/task?action=GetTaskList",
    "CRONTAB_LIST": "/crontab?action=GetCrontab",  # 计划任务列表
    "CRONTAB_LOGS": "/crontab?action=GetLogs",  # 计划任务日志
}

# API 端点分组
API_GROUPS = {
    "system": ["SYSTEM_STATUS"],
    "logs": ["PANEL_LOGS", "ERROR_LOGS", "SITE_LOGS", "FILE_BODY"],
    "security": ["FIREWALL_STATUS", "SECURITY_LOGS", "SSH_INFO", "SSH_LOGS"],
    "service": ["SERVICE_LIST", "SERVICE_STATUS", "SOFTWARE_INFO", "SOFTWARE_LIST"],
    "site": ["SITE_LIST", "PROJECT_JAVA_LIST", "PROJECT_NODE_LIST", "PROJECT_GO_LIST", "PROJECT_PYTHON_LIST", "PROJECT_NET_LIST", "PROJECT_PROXY_LIST", "PROJECT_HTML_LIST", "PROJECT_OTHER_LIST"],
    "database": ["DATABASE_LIST"],
    "task": ["TASK_LIST", "CRONTAB_LIST", "CRONTAB_LOGS"],
}

# 端点说明
API_DESCRIPTIONS = {
    "SYSTEM_STATUS": "获取系统综合监控数据（CPU、内存、磁盘、网络、负载等）",
    "PANEL_LOGS": "获取面板操作日志",
    "ERROR_LOGS": "获取错误日志",
    "SITE_LOGS": "获取网站日志",
    "FILE_BODY": "读取文件内容（用于读取日志文件）",
    "FIREWALL_STATUS": "获取防火墙状态",
    "SECURITY_LOGS": "获取安全日志",
    "SSH_INFO": "获取SSH配置信息",
    "SSH_LOGS": "获取SSH登录日志",
    "SERVICE_LIST": "获取服务列表",
    "SERVICE_STATUS": "获取服务状态",
    "SOFTWARE_INFO": "获取软件信息（nginx/apache/redis/memcached等）",
    "SOFTWARE_LIST": "获取软件列表（PHP多版本查询）",
    "SITE_LIST": "获取PHP网站列表（传统网站）",
    "PROJECT_JAVA_LIST": "获取Java项目列表",
    "PROJECT_NODE_LIST": "获取Node.js项目列表",
    "PROJECT_GO_LIST": "获取Go项目列表",
    "PROJECT_PYTHON_LIST": "获取Python项目列表",
    "PROJECT_NET_LIST": "获取.NET项目列表",
    "PROJECT_PROXY_LIST": "获取反代项目列表",
    "PROJECT_HTML_LIST": "获取HTML静态项目列表",
    "PROJECT_OTHER_LIST": "获取其他项目列表",
    "DATABASE_LIST": "获取数据库列表",
    "TASK_LIST": "获取任务列表",
    "CRONTAB_LIST": "获取计划任务列表",
    "CRONTAB_LOGS": "获取计划任务日志",
}

# 项目类型映射
PROJECT_TYPES = {
    "PHP": "SITE_LIST",
    "Java": "PROJECT_JAVA_LIST",
    "Node": "PROJECT_NODE_LIST",
    "Go": "PROJECT_GO_LIST",
    "Python": "PROJECT_PYTHON_LIST",
    "net": "PROJECT_NET_LIST",
    "Proxy": "PROJECT_PROXY_LIST",
    "HTML": "PROJECT_HTML_LIST",
    "Other": "PROJECT_OTHER_LIST",
}

# 支持查询状态的服务列表（通过 SOFTWARE_INFO 接口查询）
SOFTWARE_SERVICES = ["nginx", "apache", "mysql", "pure-ftpd", "redis", "memcached"]

# PHP版本列表（服务名称格式：php-X.X，如 php-8.2、php-7.4）
# 注意：PHP 是多版本共存的服务，一台服务器可能同时安装多个版本
# 查询时使用 get_soft_list 接口，返回的 name 字段与服务名称完全匹配
PHP_VERSIONS = ["8.5", "8.4", "8.3", "8.2", "8.1", "8.0", "7.4", "7.3", "7.2", "7.1", "7.0", "5.6", "5.5", "5.4", "5.3", "5.2"]

# 服务日志路径（通过 FILE_BODY 接口读取）
# 注意：只有已安装且运行的服务才有日志可读取
SERVICE_LOG_PATHS = {
    "nginx": "/www/server/nginx/logs/error.log",
    "apache": "/www/wwwlogs/error_log",
    "redis": "/www/server/redis/redis.log",
    # mysql 使用特殊接口，不使用文件路径
    # memcached 无标准日志文件
}

# MySQL 日志接口
MYSQL_LOG_APIS = {
    "error": "/database?action=GetErrorLog",      # MySQL 错误日志
    "slow": "/database?action=GetSlowLogs",       # MySQL 慢查询日志
}

# 特殊服务API（需要插件支持的数据库服务）
SPECIAL_SERVICE_APIS = {
    "pgsql": {
        "status": "/plugin?action=a&name=pgsql_manager&s=get_service",
        "log": "/plugin?action=a&name=pgsql_manager&s=get_pgsql_log",
        "slow_log": "/plugin?action=a&name=pgsql_manager&s=get_slow_pgsql_log",
    },
    "mysql": {
        "log": "/database?action=GetErrorLog",
        "slow_log": "/database?action=GetSlowLogs",
    }
}


def get_endpoint(name: str) -> str:
    """
    获取 API 端点路径

    Args:
        name: 端点名称

    Returns:
        端点路径

    Raises:
        KeyError: 端点不存在
    """
    if name not in API_ENDPOINTS:
        raise KeyError(f"未找到 API 端点: {name}")
    return API_ENDPOINTS[name]


def get_endpoints_by_group(group: str) -> dict:
    """
    获取分组下的所有端点

    Args:
        group: 分组名称

    Returns:
        端点字典
    """
    if group not in API_GROUPS:
        return {}
    return {name: API_ENDPOINTS[name] for name in API_GROUPS[group]}


def list_endpoints() -> dict:
    """
    列出所有端点

    Returns:
        端点字典
    """
    return API_ENDPOINTS.copy()


def get_endpoint_description(name: str) -> str:
    """
    获取端点说明

    Args:
        name: 端点名称

    Returns:
        端点说明
    """
    return API_DESCRIPTIONS.get(name, "未知端点")
