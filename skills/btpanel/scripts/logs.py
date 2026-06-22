#!/usr/bin/env python3
# /// script
# dependencies = [
#   "requests>=2.28",
#   "pyyaml>=6.0",
#   "rich>=13.0",
# ]
# ///
"""
日志读取脚本
读取服务器上的各种日志文件（Nginx/Apache/Redis/MySQL/PostgreSQL错误日志等）

注意事项：
- 只有已安装的服务才能获取日志
- MySQL 使用特殊接口获取日志，不是文件路径
- PostgreSQL 需要安装 pgsql_manager 插件
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# 兼容开发环境和发布环境的导入
_skill_root = Path(__file__).parent.parent

if (_skill_root / "bt_common").exists():
    sys.path.insert(0, str(_skill_root))
else:
    sys.path.insert(0, str(_skill_root.parent / "src"))

from bt_common import (
    BtClient,
    BtClientManager,
    SERVICE_LOG_PATHS,
    SPECIAL_SERVICE_APIS,
    load_config,
)


# 支持的服务日志（文件路径 + 特殊接口）
SUPPORTED_LOG_SERVICES = list(SERVICE_LOG_PATHS.keys()) + list(SPECIAL_SERVICE_APIS.keys())


def check_service_installed(client: BtClient, service: str) -> tuple[bool, str]:
    """
    检查服务是否已安装

    Args:
        client: 宝塔客户端
        service: 服务名称

    Returns:
        (是否已安装, 状态信息)
    """
    try:
        status = client.get_service_status(service)
        installed = status.get("installed", False)
        running = status.get("status", False)

        if not installed:
            return False, "服务未安装"
        elif not running:
            return True, "服务已安装但未运行"
        else:
            return True, "服务运行中"
    except Exception as e:
        return False, f"检查状态失败: {str(e)}"


def get_service_log(client: BtClient, service: str, log_type: str = "error",
                    lines: int = 100, check_installed: bool = True) -> dict:
    """
    获取服务日志

    Args:
        client: 宝塔客户端
        service: 服务名称
        log_type: 日志类型 (error/slow)
        lines: 返回的最后N行
        check_installed: 是否检查服务安装状态

    Returns:
        日志内容
    """
    result = {
        "server": client.name,
        "service": service,
        "log_type": log_type,
        "timestamp": datetime.now().isoformat(),
        "path": None,
        "content": "",
        "size": 0,
        "installed": True,
        "running": True,
        "error": None,
    }

    try:
        # 检查服务是否支持
        if service not in SUPPORTED_LOG_SERVICES:
            result["error"] = f"不支持的服务: {service}。支持的服务: {', '.join(SUPPORTED_LOG_SERVICES)}"
            result["installed"] = False
            return result

        # 检查服务安装状态
        if check_installed:
            installed, status_msg = check_service_installed(client, service)
            result["installed"] = installed

            if not installed:
                result["error"] = f"无法获取日志: {status_msg}"
                return result

        # 特殊服务处理（pgsql、mysql）
        if service in SPECIAL_SERVICE_APIS:
            api_key = "log" if log_type == "error" else "slow_log"
            endpoint = SPECIAL_SERVICE_APIS[service].get(api_key)
            if not endpoint:
                result["error"] = f"不支持的日志类型: {log_type}"
                return result

            response = client.request(endpoint)
            if response.get("status"):
                # 日志可能是列表格式或字符串
                log_data = response.get("data", [])
                if isinstance(log_data, list):
                    result["content"] = "\n".join(str(line) for line in log_data)
                elif isinstance(log_data, str):
                    # MySQL 日志可能直接是字符串
                    result["content"] = log_data
                else:
                    result["content"] = str(log_data)
            else:
                result["error"] = response.get("msg", "获取日志失败")
            return result

        # 标准服务日志路径（nginx、apache、redis）
        if service not in SERVICE_LOG_PATHS:
            result["error"] = f"不支持的服务: {service}"
            return result

        log_path = SERVICE_LOG_PATHS[service]
        result["path"] = log_path

        # 读取文件内容
        response = client.get_file_body(log_path)
        if response.get("status"):
            content = response.get("data", "")
            result["size"] = response.get("size", 0)

            # 只返回最后N行
            if content:
                content_lines = content.split("\n")
                if len(content_lines) > lines:
                    content_lines = content_lines[-lines:]
                result["content"] = "\n".join(content_lines)
        else:
            result["error"] = response.get("msg", "读取日志文件失败")

    except Exception as e:
        result["error"] = str(e)

    return result


def run_log_check(manager: BtClientManager, server: Optional[str] = None,
                  log_type: str = "error", service: Optional[str] = None,
                  lines: int = 100) -> dict:
    """
    执行日志检查

    Args:
        manager: 客户端管理器
        server: 指定服务器名称
        log_type: 日志类型
        service: 服务名称
        lines: 返回的行数

    Returns:
        检查结果
    """
    # 单个服务器
    if server:
        client = manager.get_client(server)
        return get_service_log(client, service, log_type, lines)

    # 所有服务器
    all_clients = manager.get_all_clients()
    results = {
        "timestamp": datetime.now().isoformat(),
        "servers": [],
    }

    for name, client in all_clients.items():
        try:
            log_result = get_service_log(client, service, log_type, lines)
            results["servers"].append(log_result)
        except Exception as e:
            results["servers"].append({
                "server": name,
                "error": str(e),
            })

    return results


def print_log_output(results: dict, format_type: str = "table"):
    """打印日志输出"""
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.syntax import Syntax

        console = Console()

        if "servers" in results:
            # 多服务器模式
            for server_data in results["servers"]:
                if "error" in server_data and "content" not in server_data:
                    server_name = server_data.get("server", "Unknown")
                    installed = server_data.get("installed", True)
                    if not installed:
                        console.print(f"[yellow]服务器 {server_name}: {server_data['error']}[/yellow]")
                    else:
                        console.print(f"[red]服务器 {server_name} 错误: {server_data['error']}[/red]")
                    continue

                server_name = server_data.get("server", "Unknown")
                service = server_data.get("service", "unknown")
                content = server_data.get("content", "")

                console.print(f"\n[bold cyan]═══ {server_name} - {service} ═══[/bold cyan]")

                if isinstance(content, str):
                    # 日志内容
                    if content.strip():
                        # 尝试语法高亮
                        try:
                            syntax = Syntax(content, "log", theme="monokai", line_numbers=True)
                            console.print(syntax)
                        except Exception:
                            console.print(content)
                    else:
                        console.print("[yellow]日志为空[/yellow]")
                else:
                    console.print(str(content))

                if server_data.get("size"):
                    console.print(f"\n[dim]文件大小: {server_data['size']} 字节[/dim]")

        else:
            # 单服务器模式
            server_name = results.get("server", "Unknown")
            service = results.get("service", "unknown")
            content = results.get("content", "")
            error = results.get("error")
            installed = results.get("installed", True)

            if error:
                if not installed:
                    console.print(f"[yellow]跳过: {error}[/yellow]")
                else:
                    console.print(f"[red]错误: {error}[/red]")
                return

            console.print(Panel(f"[bold]{server_name} - {service}[/bold]", title="日志"))

            if isinstance(content, str):
                if content.strip():
                    try:
                        syntax = Syntax(content, "log", theme="monokai", line_numbers=True)
                        console.print(syntax)
                    except Exception:
                        console.print(content)
                else:
                    console.print("[yellow]日志为空[/yellow]")
            else:
                console.print(str(content))

            if results.get("size"):
                console.print(f"\n[dim]文件大小: {results['size']} 字节[/dim]")

    except ImportError:
        # 无rich库时使用简单输出
        if "servers" in results:
            for server_data in results["servers"]:
                print(f"\n=== {server_data.get('server', 'Unknown')} ===")
                content = server_data.get("content", "")
                print(content)
        else:
            content = results.get("content", "")
            print(content)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="宝塔面板服务日志读取",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 查看Nginx错误日志
  %(prog)s --service nginx

  # 查看Redis日志
  %(prog)s --service redis

  # 查看Apache错误日志
  %(prog)s --service apache

  # 查看MySQL错误日志
  %(prog)s --service mysql

  # 查看MySQL慢查询日志
  %(prog)s --service mysql --log-type slow

  # 查看PostgreSQL日志（需要插件）
  %(prog)s --service pgsql

  # 查看PostgreSQL慢日志
  %(prog)s --service pgsql --log-type slow

  # 指定服务器和行数
  %(prog)s --server prod-01 --service nginx --lines 200

  # JSON格式输出
  %(prog)s --service nginx --format json

支持的服务: nginx, apache, redis, mysql, pgsql

注意事项:
  - 只有已安装的服务才能获取日志
  - MySQL 使用API接口获取日志，非文件路径
  - PostgreSQL 需要安装 pgsql_manager 插件
        """,
    )
    parser.add_argument("--server", "-s", help="指定服务器名称")
    parser.add_argument("--service", required=True,
                        help="服务名称 (nginx/apache/redis/mysql/pgsql)")
    parser.add_argument("--log-type", choices=["error", "slow"], default="error",
                        help="日志类型: error(错误日志), slow(慢日志，mysql/pgsql支持)")
    parser.add_argument("--lines", "-n", type=int, default=100,
                        help="返回最后N行日志 (默认: 100)")
    parser.add_argument("--format", "-f", choices=["json", "table"], default="table",
                        help="输出格式")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--config", "-c", help="配置文件路径")
    parser.add_argument("--no-check", action="store_true",
                        help="跳过服务安装状态检查")

    args = parser.parse_args()

    # 初始化客户端管理器
    manager = BtClientManager()

    try:
        manager.load_config(args.config)
    except FileNotFoundError as e:
        print(f"错误: {e}", file=sys.stderr)
        print("请先配置服务器: bt-config.py add", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"加载配置失败: {e}", file=sys.stderr)
        sys.exit(1)

    if not manager.get_all_clients():
        print("错误: 没有配置任何服务器", file=sys.stderr)
        sys.exit(1)

    # 执行日志读取
    try:
        results = run_log_check(
            manager,
            server=args.server,
            log_type=args.log_type,
            service=args.service,
            lines=args.lines,
        )
    except KeyError as e:
        print(f"错误: 未找到服务器 {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"读取日志失败: {e}", file=sys.stderr)
        sys.exit(1)

    # 输出结果
    if args.format == "json":
        output = json.dumps(results, ensure_ascii=False, indent=2)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"结果已保存到: {args.output}")
        else:
            print(output)
    else:
        print_log_output(results, args.format)


if __name__ == "__main__":
    main()
