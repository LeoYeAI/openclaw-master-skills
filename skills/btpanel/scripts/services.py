#!/usr/bin/env python3
# /// script
# dependencies = [
#   "requests>=2.28",
#   "pyyaml>=6.0",
#   "rich>=13.0",
# ]
# ///
"""
服务状态检查脚本
检查服务器上运行的服务状态（Nginx/Apache/PHP/Redis/Memcached等）
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
    SOFTWARE_SERVICES,
    load_config,
)


def get_server_services(client: BtClient, services: Optional[list] = None) -> dict:
    """
    获取单个服务器的服务状态

    Args:
        client: 宝塔客户端
        services: 要查询的服务列表

    Returns:
        服务状态信息
    """
    # 获取所有服务状态
    service_list = client.get_all_services_status(services)

    # 统计
    total = len(service_list)
    running = sum(1 for s in service_list if s.get("status"))
    stopped = sum(1 for s in service_list if s.get("installed") and not s.get("status"))
    not_installed = sum(1 for s in service_list if not s.get("installed"))

    # 生成告警
    alerts = []
    for svc in service_list:
        if svc.get("installed") and not svc.get("status"):
            alerts.append({
                "level": "warning",
                "type": "service",
                "message": f"服务 {svc.get('title', svc.get('name'))} 已停止",
                "service": svc.get("name"),
            })
        elif svc.get("error"):
            alerts.append({
                "level": "warning",
                "type": "service",
                "message": f"服务 {svc.get('name')} 状态查询失败: {svc.get('error')}",
                "service": svc.get("name"),
            })

    return {
        "server": client.name,
        "timestamp": datetime.now().isoformat(),
        "services": service_list,
        "summary": {
            "total": total,
            "running": running,
            "stopped": stopped,
            "not_installed": not_installed,
        },
        "alerts": alerts,
    }


def run_services_check(manager: BtClientManager, server: Optional[str] = None,
                       services: Optional[list] = None) -> dict:
    """
    执行服务状态检查

    Args:
        manager: 客户端管理器
        server: 指定服务器名称
        services: 要查询的服务列表

    Returns:
        检查结果
    """
    # 单个服务器
    if server:
        client = manager.get_client(server)
        return get_server_services(client, services)

    # 所有服务器
    all_clients = manager.get_all_clients()
    results = {
        "timestamp": datetime.now().isoformat(),
        "servers": [],
        "summary": {
            "total_servers": 0,
            "total_services": 0,
            "total_running": 0,
            "total_stopped": 0,
        },
        "alerts": [],
    }

    for name, client in all_clients.items():
        try:
            service_result = get_server_services(client, services)
            results["servers"].append(service_result)

            # 汇总统计
            summary = service_result.get("summary", {})
            results["summary"]["total_servers"] += 1
            results["summary"]["total_services"] += summary.get("total", 0)
            results["summary"]["total_running"] += summary.get("running", 0)
            results["summary"]["total_stopped"] += summary.get("stopped", 0)

            # 收集告警
            for alert in service_result.get("alerts", []):
                results["alerts"].append(alert)

        except Exception as e:
            results["servers"].append({
                "server": name,
                "error": str(e),
                "services": [],
                "alerts": [{"level": "critical", "type": "connection", "message": str(e)}],
            })

    return results


def print_services_table(results: dict):
    """打印表格格式输出"""
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel

        console = Console()

        if "servers" in results and len(results["servers"]) > 1:
            # 多服务器模式 - 显示汇总
            for server_data in results["servers"]:
                if "error" in server_data:
                    console.print(f"[red]服务器 {server_data['server']} 连接失败: {server_data['error']}[/red]")
                    continue

                server_name = server_data.get("server", "Unknown")
                summary = server_data.get("summary", {})

                # 服务器标题
                console.print(f"\n[bold cyan]═══ {server_name} ═══[/bold cyan]")

                # 服务列表表格
                services = server_data.get("services", [])
                if services:
                    table = Table(show_header=True, header_style="bold")
                    table.add_column("服务", style="cyan", width=20)
                    table.add_column("版本", width=12)
                    table.add_column("状态", width=10)
                    table.add_column("安装", width=8)
                    table.add_column("PID", width=8)

                    for svc in services:
                        # 状态颜色
                        if not svc.get("installed", False):
                            status_str = "[dim]未安装[/dim]"
                        elif svc.get("status"):
                            status_str = "[green]运行中[/green]"
                        else:
                            status_str = "[red]已停止[/red]"

                        # 安装状态
                        installed_str = "✓" if svc.get("installed") else "-"

                        # PID
                        pid = svc.get("pid", 0) or 0
                        pid_str = str(pid) if pid > 0 else "-"

                        table.add_row(
                            svc.get("title", svc.get("name", "-"))[:20],
                            svc.get("version", "-")[:12],
                            status_str,
                            installed_str,
                            pid_str,
                        )

                    console.print(table)
                else:
                    console.print("[yellow]无服务信息[/yellow]")

                # 汇总
                console.print(f"\n[dim]汇总: "
                             f"总数 {summary.get('total', 0)}, "
                             f"[green]运行 {summary.get('running', 0)}[/green], "
                             f"[red]停止 {summary.get('stopped', 0)}[/red], "
                             f"[dim]未安装 {summary.get('not_installed', 0)}[/dim][/dim]")

                # 告警
                alerts = server_data.get("alerts", [])
                if alerts:
                    console.print("\n[yellow]告警:[/yellow]")
                    for alert in alerts[:5]:
                        level = alert.get("level", "warning")
                        color = "red" if level == "critical" else "yellow"
                        console.print(f"  [{color}]• {alert.get('message', '')}[/{color}]")

            # 总汇总
            summary = results.get("summary", {})
            console.print(f"\n[bold]总汇总:[/bold] "
                         f"服务器: {summary.get('total_servers', 0)}, "
                         f"服务总数: {summary.get('total_services', 0)}, "
                         f"[green]运行: {summary.get('total_running', 0)}[/green], "
                         f"[red]停止: {summary.get('total_stopped', 0)}[/red]")

        else:
            # 单服务器模式
            server_name = results.get("server", "Unknown")

            # 基本信息
            console.print(Panel(f"[bold]{server_name}[/bold]", title="服务器"))

            services = results.get("services", [])
            if services:
                table = Table(show_header=True, header_style="bold")
                table.add_column("服务", style="cyan")
                table.add_column("版本")
                table.add_column("状态")
                table.add_column("安装")
                table.add_column("PID")

                for svc in services:
                    # 状态颜色
                    if not svc.get("installed", False):
                        status_str = "[dim]未安装[/dim]"
                    elif svc.get("status"):
                        status_str = "[green]运行中[/green]"
                    else:
                        status_str = "[red]已停止[/red]"

                    # 安装状态
                    installed_str = "✓" if svc.get("installed") else "-"

                    # PID
                    pid = svc.get("pid", 0) or 0
                    pid_str = str(pid) if pid > 0 else "-"

                    table.add_row(
                        svc.get("title", svc.get("name", "-")),
                        svc.get("version", "-"),
                        status_str,
                        installed_str,
                        pid_str,
                    )

                console.print(table)
            else:
                console.print("[yellow]无服务信息[/yellow]")

            # 汇总
            summary = results.get("summary", {})
            console.print(f"\n[bold]汇总:[/bold]")
            console.print(f"  总数: {summary.get('total', 0)}")
            console.print(f"  [green]运行: {summary.get('running', 0)}[/green]")
            console.print(f"  [red]停止: {summary.get('stopped', 0)}[/red]")
            console.print(f"  [dim]未安装: {summary.get('not_installed', 0)}[/dim]")

            # 告警
            alerts = results.get("alerts", [])
            if alerts:
                console.print(f"\n[bold yellow]告警 ({len(alerts)}条):[/bold yellow]")
                for alert in alerts:
                    level = alert.get("level", "warning")
                    color = "red" if level == "critical" else "yellow"
                    console.print(f"  [{color}]• {alert.get('message', '')}[/{color}]")

    except ImportError:
        print("请安装rich库以使用表格输出: pip install rich")
        print(json.dumps(results, ensure_ascii=False, indent=2))


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="宝塔面板服务状态检查",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 检查所有服务器的服务状态
  %(prog)s

  # 检查指定服务器
  %(prog)s --server prod-01

  # 只检查特定服务
  %(prog)s --service nginx --service redis

  # JSON格式输出
  %(prog)s --format json

  # 输出到文件
  %(prog)s --output services.json

支持的服务: nginx, apache, mysql, redis, memcached, pure-ftpd
PHP服务: 自动检测已安装的PHP版本（php-8.2, php-7.4等）
PostgreSQL: 需要安装pgsql_manager插件

字段说明:
  installed (setup): 服务是否已安装
  status: 服务是否正在运行（仅installed=true时有意义）
  version: 已安装的版本号
  pid: 主进程ID（运行中时）
        """,
    )
    parser.add_argument("--server", "-s", help="指定服务器名称")
    parser.add_argument("--format", "-f", choices=["json", "table"], default="table", help="输出格式")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--service", action="append", dest="services",
                        help="指定要检查的服务（可多次指定）")
    parser.add_argument("--config", "-c", help="配置文件路径")

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

    # 执行检查
    try:
        results = run_services_check(manager, args.server, args.services)
    except KeyError as e:
        print(f"错误: 未找到服务器 {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"检查失败: {e}", file=sys.stderr)
        sys.exit(1)

    # 输出结果
    if args.format == "table":
        print_services_table(results)
    else:
        output = json.dumps(results, ensure_ascii=False, indent=2)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"结果已保存到: {args.output}")
        else:
            print(output)


if __name__ == "__main__":
    main()
