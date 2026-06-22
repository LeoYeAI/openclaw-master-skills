# /// script
# dependencies = []
# ///
"""
工具函数模块
提供格式化输出、阈值检查、告警生成等功能
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class Alert:
    """告警信息"""

    level: str  # warning, critical
    type: str  # cpu, memory, disk, service, ssl, security
    message: str
    value: Optional[float] = None
    extra: dict = field(default_factory=dict)


def format_bytes(bytes_value: int, decimals: int = 2) -> str:
    """
    格式化字节大小为人类可读格式

    Args:
        bytes_value: 字节数
        decimals: 小数位数

    Returns:
        格式化后的字符串
    """
    if bytes_value == 0:
        return "0 B"

    k = 1024
    sizes = ["B", "KB", "MB", "GB", "TB", "PB"]
    i = 0
    value = float(bytes_value)

    while value >= k and i < len(sizes) - 1:
        value /= k
        i += 1

    return f"{value:.{decimals}f} {sizes[i]}"


def format_uptime(seconds: int) -> str:
    """
    格式化运行时间

    Args:
        seconds: 秒数

    Returns:
        格式化后的字符串
    """
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60

    if days > 0:
        return f"{days}天{hours}小时"
    if hours > 0:
        return f"{hours}小时{minutes}分钟"
    return f"{minutes}分钟"


def format_timestamp(ts: Optional[str] = None) -> str:
    """
    格式化时间戳

    Args:
        ts: ISO格式时间戳，为None时使用当前时间

    Returns:
        格式化后的时间字符串
    """
    if ts:
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, AttributeError):
            return ts
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def parse_system_monitor_data(data: dict, server_name: str) -> dict:
    """
    解析系统监控数据（GetNetWork接口返回）

    Args:
        data: 原始API响应
        server_name: 服务器名称

    Returns:
        格式化后的系统监控数据
    """
    result = {
        "server": server_name,
        "timestamp": datetime.now().isoformat(),
        "version": data.get("version", "unknown"),
        "hostname": data.get("title", "unknown"),
        "system": data.get("simple_system", data.get("system", "unknown")),
        "uptime": data.get("time", "unknown"),
        "docker_running": data.get("docker_run", False),
    }

    # 解析CPU数据
    # cpu格式: [使用率%, 核心数, [用户态%, 系统态%], CPU型号, ?, ?]
    cpu_data = data.get("cpu", [])
    if isinstance(cpu_data, list) and len(cpu_data) >= 4:
        result["cpu"] = {
            "usage": round(cpu_data[0], 2) if isinstance(cpu_data[0], (int, float)) else 0,
            "cores": cpu_data[1] if isinstance(cpu_data[1], int) else 1,
            "user_usage": round(cpu_data[2][0], 2) if isinstance(cpu_data[2], list) and len(cpu_data[2]) > 0 else 0,
            "system_usage": round(cpu_data[2][1], 2) if isinstance(cpu_data[2], list) and len(cpu_data[2]) > 1 else 0,
            "model": cpu_data[3] if isinstance(cpu_data[3], str) else "Unknown",
        }
    else:
        result["cpu"] = {"usage": 0, "cores": 1, "model": "Unknown"}

    # 解析CPU时间分布
    cpu_times = data.get("cpu_times", {})
    if cpu_times:
        result["cpu"]["times"] = {
            "user": round(cpu_times.get("user", 0), 2),
            "system": round(cpu_times.get("system", 0), 2),
            "idle": round(cpu_times.get("idle", 0), 2),
            "iowait": round(cpu_times.get("iowait", 0), 2),
        }
        # 进程数
        result["processes"] = {
            "total": cpu_times.get("总进程数", 0),
            "active": cpu_times.get("活动进程数", 0),
        }

    # 解析负载
    load_data = data.get("load", {})
    if load_data:
        result["load"] = {
            "one_minute": round(load_data.get("one", 0), 2),
            "five_minute": round(load_data.get("five", 0), 2),
            "fifteen_minute": round(load_data.get("fifteen", 0), 2),
            "cpu_count": load_data.get("max", 1),
            "safe_limit": load_data.get("safe", 1),
        }

    # 解析内存数据 (单位: MB)
    mem_data = data.get("mem", {})
    if mem_data:
        mem_total = mem_data.get("memTotal", 0)
        mem_free = mem_data.get("memFree", 0)
        mem_cached = mem_data.get("memCached", 0)
        mem_buffers = mem_data.get("memBuffers", 0)
        mem_available = mem_data.get("memAvailable", 0)
        mem_used = mem_data.get("memRealUsed", mem_total - mem_free)

        result["memory"] = {
            "total_mb": mem_total,
            "total_gb": round(mem_total / 1024, 2),
            "used_mb": mem_used,
            "used_gb": round(mem_used / 1024, 2),
            "free_mb": mem_free,
            "available_mb": mem_available,
            "cached_mb": mem_cached,
            "buffers_mb": mem_buffers,
            "percent": round((mem_used / mem_total * 100), 2) if mem_total > 0 else 0,
            "available_percent": round((mem_available / mem_total * 100), 2) if mem_total > 0 else 0,
        }

    # 解析磁盘数据
    disk_list = data.get("disk", [])
    disks = []
    total_size = 0
    total_used = 0

    for disk in disk_list:
        if isinstance(disk, dict):
            byte_size = disk.get("byte_size", [0, 0, 0])
            size_info = disk.get("size", ["0", "0", "0", "0%"])

            disk_total = byte_size[0] if isinstance(byte_size, list) and len(byte_size) > 0 else 0
            disk_used = byte_size[1] if isinstance(byte_size, list) and len(byte_size) > 1 else 0
            disk_free = byte_size[2] if isinstance(byte_size, list) and len(byte_size) > 2 else 0

            # 跳过挂载的远程存储（如ossfs）
            filesystem = disk.get("filesystem", "")
            if "fuse" in filesystem.lower() or "ossfs" in filesystem.lower():
                continue

            disk_entry = {
                "path": disk.get("path", "/"),
                "filesystem": filesystem,
                "type": disk.get("type", "unknown"),
                "total_bytes": disk_total,
                "used_bytes": disk_used,
                "free_bytes": disk_free,
                "total_human": size_info[0] if len(size_info) > 0 else "0",
                "used_human": size_info[1] if len(size_info) > 1 else "0",
                "free_human": size_info[2] if len(size_info) > 2 else "0",
                "percent": float(size_info[3].replace("%", "").strip()) if len(size_info) > 3 and isinstance(size_info[3], str) else 0,
                "name": disk.get("rname", disk.get("path", "/")),
            }
            disks.append(disk_entry)
            total_size += disk_total
            total_used += disk_used

    result["disk"] = {
        "disks": disks,
        "total_bytes": total_size,
        "used_bytes": total_used,
        "free_bytes": total_size - total_used,
        "total_human": format_bytes(total_size),
        "used_human": format_bytes(total_used),
        "free_human": format_bytes(total_size - total_used),
        "percent": round((total_used / total_size * 100), 2) if total_size > 0 else 0,
    }

    # 解析网络数据
    result["network"] = {
        "total_up": format_bytes(data.get("upTotal", 0)),
        "total_down": format_bytes(data.get("downTotal", 0)),
        "current_up": round(data.get("up", 0), 2),  # KB/s
        "current_down": round(data.get("down", 0), 2),  # KB/s
        "up_packets": data.get("upPackets", 0),
        "down_packets": data.get("downPackets", 0),
        "interfaces": {},
    }

    # 各网卡数据
    network_ifaces = data.get("network", {})
    for iface, stats in network_ifaces.items():
        if isinstance(stats, dict):
            result["network"]["interfaces"][iface] = {
                "up_total": format_bytes(stats.get("upTotal", 0)),
                "down_total": format_bytes(stats.get("downTotal", 0)),
                "current_up": round(stats.get("up", 0), 2),
                "current_down": round(stats.get("down", 0), 2),
            }

    # 资源统计
    result["resources"] = {
        "sites": data.get("site_total", 0),
        "databases": data.get("database_total", 0),
        "ftp_accounts": data.get("ftp_total", 0),
    }

    # IO统计
    iostat = data.get("iostat", {})
    if iostat and "ALL" in iostat:
        all_io = iostat["ALL"]
        result["io"] = {
            "read_count": all_io.get("read_count", 0),
            "write_count": all_io.get("write_count", 0),
            "read_bytes": format_bytes(all_io.get("read_bytes", 0)),
            "write_bytes": format_bytes(all_io.get("write_bytes", 0)),
        }

    return result


def parse_system_status_legacy(data: dict, server_name: str) -> dict:
    """
    解析旧版系统状态响应（GetSystemTotal接口）

    Args:
        data: 原始API响应
        server_name: 服务器名称

    Returns:
        格式化后的系统状态
    """
    mem_total = data.get("mem_total", 0)
    mem_used = data.get("mem_used", 0)
    disk_total = data.get("disk_total", 0)
    disk_used = data.get("disk_used", 0)

    # 转换为GB
    mem_total_gb = mem_total / 1024 / 1024 / 1024 if mem_total else 0
    mem_used_gb = mem_used / 1024 / 1024 / 1024 if mem_used else 0
    disk_total_gb = disk_total / 1024 / 1024 / 1024 if disk_total else 0
    disk_used_gb = disk_used / 1024 / 1024 / 1024 if disk_used else 0

    # 计算百分比
    mem_percent = (mem_used / mem_total * 100) if mem_total > 0 else 0
    disk_percent = (disk_used / disk_total * 100) if disk_total > 0 else 0

    return {
        "server": server_name,
        "timestamp": datetime.now().isoformat(),
        "metrics": {
            "cpu": {
                "usage": float(data.get("cpu_usage", 0) or 0),
                "cores": int(data.get("cpu_core", 1) or 1),
                "model": data.get("cpu_model", "Unknown") or "Unknown",
            },
            "memory": {
                "used": round(mem_used_gb, 2),
                "total": round(mem_total_gb, 2),
                "percent": round(mem_percent, 2),
            },
            "disk": {
                "used": round(disk_used_gb, 2),
                "total": round(disk_total_gb, 2),
                "percent": round(disk_percent, 2),
            },
            "system": {
                "hostname": data.get("host_name", "Unknown") or "Unknown",
                "os": data.get("system", "Unknown") or "Unknown",
                "uptime": format_uptime(int(data.get("up_time", 0) or 0)),
            },
        },
    }


def check_thresholds(metrics: dict, thresholds: dict) -> list[Alert]:
    """
    检查阈值告警

    Args:
        metrics: 格式化后的指标数据（来自parse_system_monitor_data）
        thresholds: 阈值配置

    Returns:
        告警列表
    """
    alerts = []

    cpu_threshold = thresholds.get("cpu", 80)
    memory_threshold = thresholds.get("memory", 85)
    disk_threshold = thresholds.get("disk", 90)

    # CPU告警
    cpu_data = metrics.get("cpu", {})
    cpu_usage = cpu_data.get("usage", 0)
    if cpu_usage >= cpu_threshold:
        alerts.append(
            Alert(
                level="warning",
                type="cpu",
                message=f"CPU使用率过高: {cpu_usage}% (阈值: {cpu_threshold}%)",
                value=cpu_usage,
            )
        )

    # 内存告警
    mem_data = metrics.get("memory", {})
    mem_percent = mem_data.get("percent", 0)
    if mem_percent >= memory_threshold:
        alerts.append(
            Alert(
                level="warning",
                type="memory",
                message=f"内存使用率过高: {mem_percent}% (阈值: {memory_threshold}%)",
                value=mem_percent,
                extra={
                    "used_mb": mem_data.get("used_mb"),
                    "total_mb": mem_data.get("total_mb"),
                },
            )
        )

    # 磁盘告警
    disk_data = metrics.get("disk", {})
    disk_percent = disk_data.get("percent", 0)
    if disk_percent >= disk_threshold:
        alerts.append(
            Alert(
                level="critical",
                type="disk",
                message=f"磁盘使用率过高: {disk_percent}% (阈值: {disk_threshold}%)",
                value=disk_percent,
                extra={
                    "used_human": disk_data.get("used_human"),
                    "total_human": disk_data.get("total_human"),
                },
            )
        )

    # 检查各磁盘分区
    for disk in disk_data.get("disks", []):
        disk_p = disk.get("percent", 0)
        if disk_p >= disk_threshold:
            alerts.append(
                Alert(
                    level="critical" if disk_p >= 95 else "warning",
                    type="disk",
                    message=f"磁盘分区 {disk.get('path', '/')} 使用率过高: {disk_p}%",
                    value=disk_p,
                    extra={"path": disk.get("path")},
                )
            )

    # 负载告警
    load_data = metrics.get("load", {})
    if load_data:
        one_min_load = load_data.get("one_minute", 0)
        cpu_count = load_data.get("cpu_count", 1)
        # 负载超过CPU核心数时告警
        if one_min_load >= cpu_count:
            alerts.append(
                Alert(
                    level="warning",
                    type="load",
                    message=f"系统负载过高: {one_min_load} (CPU核心数: {cpu_count})",
                    value=one_min_load,
                )
            )

    return alerts


def format_security_report(data: dict, server_name: str) -> dict:
    """
    格式化安全报告

    Args:
        data: 原始安全数据
        server_name: 服务器名称

    Returns:
        格式化后的安全报告
    """
    return {
        "server": server_name,
        "timestamp": datetime.now().isoformat(),
        "security": {
            "firewall": {
                "status": data.get("firewall_status", "unknown"),
                "rules": data.get("firewall_rules", 0),
            },
            "ssh": {
                "failedAttempts": data.get("ssh_failed", 0),
                "lastLogin": data.get("last_login"),
                "lastLoginIp": data.get("last_login_ip"),
            },
            "suspiciousIps": data.get("suspicious_ips", []),
            "recentAlerts": data.get("security_alerts", []),
        },
    }


def format_service_status(services: list, server_name: str) -> dict:
    """
    格式化服务状态

    Args:
        services: 服务列表
        server_name: 服务器名称

    Returns:
        格式化后的服务状态
    """
    formatted_services = []
    running_count = 0
    stopped_count = 0

    for svc in services:
        status = svc.get("status", "unknown")
        if status == "running":
            running_count += 1
        else:
            stopped_count += 1

        formatted_services.append(
            {
                "name": svc.get("name"),
                "status": status,
                "enabled": svc.get("enabled", True),
                "uptime": format_uptime(svc["uptime"]) if svc.get("uptime") else None,
            }
        )

    return {
        "server": server_name,
        "timestamp": datetime.now().isoformat(),
        "services": formatted_services,
        "summary": {
            "total": len(services),
            "running": running_count,
            "stopped": stopped_count,
        },
    }


def check_ssl_status(ssl_data) -> dict:
    """
    检查SSL证书状态

    Args:
        ssl_data: SSL数据（可能是dict或-1或None）

    Returns:
        SSL状态信息
    """
    if ssl_data == -1 or ssl_data is None:
        return {"status": "none", "enabled": False, "message": "未配置SSL", "days_remaining": None}

    if not isinstance(ssl_data, dict):
        return {"status": "unknown", "enabled": False, "message": "SSL状态未知", "days_remaining": None}

    endtime = ssl_data.get("endtime", 0)
    if endtime is None:
        endtime = 0

    if endtime < 0:
        return {
            "status": "expired",
            "enabled": True,
            "message": f"已过期{-endtime}天",
            "days_remaining": endtime,
            "issuer": ssl_data.get("issuer_O", "Unknown"),
            "not_after": ssl_data.get("notAfter", ""),
        }
    elif endtime <= 7:
        return {
            "status": "critical",
            "enabled": True,
            "message": f"将在{endtime}天内过期",
            "days_remaining": endtime,
            "issuer": ssl_data.get("issuer_O", "Unknown"),
            "not_after": ssl_data.get("notAfter", ""),
        }
    elif endtime <= 30:
        return {
            "status": "warning",
            "enabled": True,
            "message": f"将在{endtime}天内过期",
            "days_remaining": endtime,
            "issuer": ssl_data.get("issuer_O", "Unknown"),
            "not_after": ssl_data.get("notAfter", ""),
        }
    else:
        return {
            "status": "valid",
            "enabled": True,
            "message": f"剩余{endtime}天",
            "days_remaining": endtime,
            "issuer": ssl_data.get("issuer_O", "Unknown"),
            "not_after": ssl_data.get("notAfter", ""),
        }


def parse_php_site(site: dict, server_name: str) -> dict:
    """
    解析PHP网站数据

    Args:
        site: 网站数据
        server_name: 服务器名称

    Returns:
        格式化后的网站信息
    """
    # 判断运行状态
    status = "running" if site.get("status") == "1" and not site.get("stop") else "stopped"

    # 解析SSL
    ssl_info = check_ssl_status(site.get("ssl"))

    # 解析PHP版本
    php_version = site.get("php_version", "")
    if php_version in ["静态", "其它", "其他"]:
        php_version = "static"

    return {
        "name": site.get("name", ""),
        "server": server_name,
        "type": "PHP",
        "status": status,
        "path": site.get("path", ""),
        "domains": site.get("domain", 0),
        "php_version": php_version,
        "proxy": site.get("proxy", False),
        "redirect": site.get("redirect", False),
        "waf_enabled": site.get("waf", {}).get("status", False),
        "backup_count": site.get("backup_count", 0),
        "ssl": ssl_info,
        "process": None,  # PHP项目无进程信息
        "addtime": site.get("addtime", ""),
        "ps": site.get("ps", ""),
    }


def parse_project_site(project: dict, server_name: str) -> dict:
    """
    解析项目类型网站数据（Java/Node/Go/Python/.NET/Other）

    Args:
        project: 项目数据
        server_name: 服务器名称

    Returns:
        格式化后的项目信息
    """
    project_type = project.get("project_type", "Unknown")

    # 判断运行状态
    # Java: pid_info存在且pid > 0, starting=True表示启动中
    # Node/Go/NET: load_info存在且有pid, run=True
    # Python: run=True, pids非空
    # Other: run=True, load_info非空
    status = "stopped"
    process_info = None

    # 检查进程信息
    load_info = project.get("load_info", {})
    pid_info = project.get("pid_info", {})
    pids = project.get("pids", [])

    if project_type == "Java":
        if pid_info and pid_info.get("pid"):
            status = "running"
            process_info = {
                "pid": pid_info.get("pid"),
                "status": pid_info.get("status", "unknown"),
                "memory_used": format_bytes(pid_info.get("memory_used", 0)),
                "cpu_percent": pid_info.get("cpu_percent", 0),
                "threads": pid_info.get("threads", 0),
                "running_time": pid_info.get("running_time", 0),
            }
        elif project.get("starting"):
            status = "starting"
    elif project_type == "Python":
        if project.get("run") or pids:
            status = "running"
            if pids:
                process_info = {"pids": pids}
    else:  # Node, Go, net, Other
        if project.get("run") or load_info:
            status = "running"
            if load_info:
                # load_info可能有多个进程
                first_pid = list(load_info.values())[0] if load_info else {}
                process_info = {
                    "pid": first_pid.get("pid"),
                    "status": first_pid.get("status", "unknown"),
                    "memory_used": format_bytes(first_pid.get("memory_used", 0)),
                    "cpu_percent": first_pid.get("cpu_percent", 0),
                    "threads": first_pid.get("threads", 0),
                    "connects": first_pid.get("connects", 0),
                }

    # 解析SSL
    ssl_info = check_ssl_status(project.get("ssl"))

    # 获取域名
    project_config = project.get("project_config", {})
    domains = project_config.get("domains", [])

    # 获取端口
    port = project_config.get("port", "")

    return {
        "name": project.get("name", ""),
        "server": server_name,
        "type": project_type,
        "status": status,
        "path": project.get("path", ""),
        "domains": len(domains) if domains else 0,
        "domain_list": domains,
        "port": port,
        "ssl": ssl_info,
        "process": process_info,
        "addtime": project.get("addtime", ""),
        "ps": project.get("ps", ""),
    }


def parse_proxy_site(proxy: dict, server_name: str) -> dict:
    """
    解析反代项目数据

    Args:
        proxy: 反代项目数据
        server_name: 服务器名称

    Returns:
        格式化后的反代项目信息
    """
    # 反代项目通过status字段和healthy字段判断状态
    # status: "1" = 运行, "0" = 停止
    # healthy: 1 = 健康, 0 = 不健康
    status = "running" if proxy.get("status") == "1" else "stopped"
    healthy = proxy.get("healthy", 1) == 1

    # 解析SSL
    ssl_info = check_ssl_status(proxy.get("ssl"))

    return {
        "name": proxy.get("name", ""),
        "server": server_name,
        "type": "Proxy",
        "status": status,
        "path": proxy.get("path", ""),
        "proxy_pass": proxy.get("proxy_pass", ""),
        "healthy": healthy,
        "waf_enabled": proxy.get("waf", {}).get("status", False),
        "ssl": ssl_info,
        "conf_path": proxy.get("conf_path", ""),
        "process": None,  # 反代项目无进程信息
        "addtime": proxy.get("addtime", ""),
        "ps": proxy.get("ps", ""),
    }


def parse_html_site(html: dict, server_name: str) -> dict:
    """
    解析HTML静态项目数据

    Args:
        html: HTML项目数据
        server_name: 服务器名称

    Returns:
        格式化后的HTML项目信息
    """
    # HTML静态项目通过status字段判断状态
    # status: "1" = 运行, "0" = 停止
    status = "running" if html.get("status") == "1" else "stopped"

    # 解析SSL
    ssl_info = check_ssl_status(html.get("ssl"))

    return {
        "name": html.get("name", ""),
        "server": server_name,
        "type": "HTML",
        "status": status,
        "path": html.get("path", ""),
        "ssl": ssl_info,
        "process": None,  # HTML静态项目无进程信息
        "addtime": html.get("addtime", ""),
        "ps": html.get("ps", ""),
    }


def parse_all_sites(sites_data: list, server_name: str) -> dict:
    """
    解析所有网站/项目数据

    Args:
        sites_data: 网站数据列表（来自get_all_sites）
        server_name: 服务器名称

    Returns:
        格式化后的网站汇总信息
    """
    sites = []
    alerts = []
    ssl_expiring = []
    ssl_expired = []

    for site in sites_data:
        source = site.get("_source", "PHP")

        if source == "PHP":
            parsed = parse_php_site(site, server_name)
        elif source == "Proxy":
            parsed = parse_proxy_site(site, server_name)
        elif source == "HTML":
            parsed = parse_html_site(site, server_name)
        else:
            parsed = parse_project_site(site, server_name)

        sites.append(parsed)

        # 检查SSL告警
        ssl_info = parsed.get("ssl", {})
        if ssl_info.get("status") == "expired":
            ssl_expired.append(parsed["name"])
            alerts.append({
                "level": "critical",
                "type": "ssl",
                "message": f"网站 {parsed['name']} SSL证书已过期",
                "site": parsed["name"],
            })
        elif ssl_info.get("status") == "critical":
            ssl_expiring.append(parsed["name"])
            alerts.append({
                "level": "critical",
                "type": "ssl",
                "message": f"网站 {parsed['name']} SSL证书将在{ssl_info.get('days_remaining', 0)}天内过期",
                "site": parsed["name"],
            })
        elif ssl_info.get("status") == "warning":
            ssl_expiring.append(parsed["name"])
            alerts.append({
                "level": "warning",
                "type": "ssl",
                "message": f"网站 {parsed['name']} SSL证书将在{ssl_info.get('days_remaining', 0)}天内过期",
                "site": parsed["name"],
            })

        # 检查运行状态告警
        if parsed["status"] == "stopped":
            alerts.append({
                "level": "warning",
                "type": "site",
                "message": f"网站 {parsed['name']} 已停止",
                "site": parsed["name"],
            })

        # 检查反代项目健康状态
        if source == "Proxy" and not parsed.get("healthy", True):
            alerts.append({
                "level": "warning",
                "type": "proxy",
                "message": f"反代项目 {parsed['name']} 后端不健康",
                "site": parsed["name"],
            })

    # 统计
    by_type = {}
    by_status = {"running": 0, "stopped": 0, "starting": 0}
    for site in sites:
        site_type = site.get("type", "Unknown")
        by_type[site_type] = by_type.get(site_type, 0) + 1
        by_status[site.get("status", "stopped")] = by_status.get(site.get("status", "stopped"), 0) + 1

    return {
        "server": server_name,
        "timestamp": datetime.now().isoformat(),
        "sites": sites,
        "summary": {
            "total": len(sites),
            "by_type": by_type,
            "by_status": by_status,
            "ssl_expired": len(ssl_expired),
            "ssl_expiring": len(ssl_expiring),
        },
        "alerts": alerts,
    }


def print_table(data: list[dict], headers: Optional[list[str]] = None) -> str:
    """
    生成表格格式的输出

    Args:
        data: 数据列表
        headers: 表头，为None时从数据中提取

    Returns:
        格式化的表格字符串
    """
    if not data:
        return "无数据"

    if headers is None:
        headers = list(data[0].keys())

    # 计算列宽
    widths = [len(str(h)) for h in headers]
    for row in data:
        for i, h in enumerate(headers):
            value = row.get(h, "")
            widths[i] = max(widths[i], len(str(value)))

    # 构建表格
    lines = []

    # 表头
    header_line = " | ".join(str(h).ljust(widths[i]) for i, h in enumerate(headers))
    lines.append(header_line)
    lines.append("-+-".join("-" * w for w in widths))

    # 数据行
    for row in data:
        line = " | ".join(str(row.get(h, "")).ljust(widths[i]) for i, h in enumerate(headers))
        lines.append(line)

    return "\n".join(lines)


def output_result(data: Any, output_format: str = "json", output_file: Optional[str] = None) -> str:
    """
    输出结果

    Args:
        data: 要输出的数据
        output_format: 输出格式 (json/table)
        output_file: 输出文件路径

    Returns:
        格式化后的输出字符串
    """
    import json

    if output_format == "json":
        # 处理dataclass对象
        if hasattr(data, "__dataclass_fields__"):
            from dataclasses import asdict

            output = json.dumps(asdict(data), ensure_ascii=False, indent=2)
        elif isinstance(data, dict):
            output = json.dumps(data, ensure_ascii=False, indent=2)
        elif isinstance(data, list):
            output = json.dumps(data, ensure_ascii=False, indent=2)
        else:
            output = str(data)
    else:
        output = str(data)

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output)

    return output


def generate_summary_report(results: dict, report_type: str) -> str:
    """
    生成摘要报告

    Args:
        results: 巡检结果
        report_type: 报告类型 (system/security/health)

    Returns:
        格式化的报告字符串
    """
    lines = []
    timestamp = format_timestamp()

    if report_type == "system":
        lines.append("=" * 50)
        lines.append(f"系统资源监控报告 - {timestamp}")
        lines.append("=" * 50)

        for server in results.get("servers", []):
            name = server.get("server", "Unknown")
            if "error" in server:
                lines.append(f"\n[{name}] 连接失败: {server['error']}")
                continue

            # 新格式数据
            cpu = server.get("cpu", {})
            memory = server.get("memory", {})
            disk = server.get("disk", {})

            lines.append(f"\n[{name}]")
            lines.append(f"  系统: {server.get('system', 'Unknown')} ({server.get('hostname', 'Unknown')})")
            lines.append(f"  运行时间: {server.get('uptime', 'Unknown')}")
            lines.append(f"  CPU: {cpu.get('usage', 0):.1f}% ({cpu.get('cores', 1)}核 - {cpu.get('model', 'Unknown')})")
            lines.append(f"  内存: {memory.get('percent', 0):.1f}% ({memory.get('used_mb', 0)}/{memory.get('total_mb', 0)} MB)")
            lines.append(f"  磁盘: {disk.get('percent', 0):.1f}% ({disk.get('used_human', '0')}/{disk.get('total_human', '0')})")

            # 资源统计
            resources = server.get("resources", {})
            if resources:
                lines.append(f"  资源: 网站{resources.get('sites', 0)}个, 数据库{resources.get('databases', 0)}个")

            alerts = server.get("alerts", [])
            if alerts:
                lines.append(f"  告警: {len(alerts)}条")
                for alert in alerts[:3]:
                    lines.append(f"    - [{alert['level']}] {alert['message']}")

        summary = results.get("summary", {})
        lines.append(f"\n汇总: 正常{summary.get('healthy', 0)}, 警告{summary.get('warning', 0)}, 异常{summary.get('critical', 0)}")

    elif report_type == "security":
        lines.append("=" * 50)
        lines.append(f"安全巡检报告 - {timestamp}")
        lines.append("=" * 50)

        for server in results.get("servers", []):
            name = server.get("server", "Unknown")
            risk = server.get("riskLevel", "unknown")

            risk_emoji = {"low": "✅", "medium": "🟡", "high": "🟠", "critical": "🔴"}.get(risk, "❓")
            lines.append(f"\n[{name}] 风险等级: {risk_emoji} {risk.upper()}")

            if "error" in server:
                lines.append(f"  检查失败: {server['error']}")
                continue

            ssh = server.get("ssh", {})
            if ssh:
                lines.append(f"  SSH端口: {ssh.get('port', 'N/A')}")

            firewall = server.get("firewall", {})
            if firewall:
                fw_status = "运行中" if firewall.get("status") == "running" else "已停止"
                lines.append(f"  防火墙: {fw_status}")

            alerts = server.get("alerts", [])
            if alerts:
                lines.append(f"  告警: {len(alerts)}条")

        summary = results.get("summary", {})
        lines.append(
            f"\n汇总: 低风险{summary.get('low', 0)}, 中风险{summary.get('medium', 0)}, "
            f"高风险{summary.get('high', 0)}, 严重{summary.get('critical', 0)}"
        )

    elif report_type == "health":
        lines.append("=" * 50)
        lines.append(f"健康检查报告 - {timestamp}")
        lines.append("=" * 50)

        for server in results.get("servers", []):
            name = server.get("server", "Unknown")
            status = server.get("overallStatus", "unknown")

            status_emoji = {"healthy": "✅", "warning": "🟡", "critical": "🔴"}.get(status, "❓")
            lines.append(f"\n[{name}] 状态: {status_emoji} {status.upper()}")

            if "error" in server:
                lines.append(f"  检查失败: {server['error']}")
                continue

            services = server.get("services", {})
            if services:
                lines.append(f"  服务: {services.get('running', 0)}/{services.get('total', 0)} 运行中")

            sites = server.get("sites", {})
            if sites:
                lines.append(f"  网站: {sites.get('running', 0)}/{sites.get('total', 0)} 运行中")

            databases = server.get("databases", {})
            if databases:
                lines.append(f"  数据库: {databases.get('total', 0)}个")

            alerts = server.get("alerts", [])
            if alerts:
                lines.append(f"  告警: {len(alerts)}条")

        summary = results.get("summary", {})
        lines.append(
            f"\n汇总: 健康{summary.get('healthy', 0)}, 警告{summary.get('warning', 0)}, "
            f"异常{summary.get('critical', 0)}"
        )

    lines.append("\n" + "=" * 50)
    return "\n".join(lines)
