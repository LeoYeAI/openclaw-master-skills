#!/usr/bin/env python3
# /// script
# dependencies = [
#   "requests>=2.28",
#   "pyyaml>=6.0",
#   "rich>=13.0",
# ]
# ///
"""
网站状态检查脚本
检查所有网站和项目的运行状态、SSL证书等
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
    parse_all_sites,
    load_config,
)


def get_server_sites(client: BtClient) -> dict:
    """
    获取单个服务器的网站状态

    Args:
        client: 宝塔客户端

    Returns:
        网站状态信息
    """
    # 获取所有网站和项目
    sites_data = client.get_all_sites()

    # 解析数据
    return parse_all_sites(sites_data, client.name)


def run_sites_check(manager: BtClientManager, server: Optional[str] = None) -> dict:
    """
    执行网站状态检查

    Args:
        manager: 客户端管理器
        server: 指定服务器名称

    Returns:
        检查结果
    """
    # 单个服务器
    if server:
        client = manager.get_client(server)
        return get_server_sites(client)

    # 所有服务器
    all_clients = manager.get_all_clients()
    results = {
        "timestamp": datetime.now().isoformat(),
        "servers": [],
        "summary": {
            "total": 0,
            "running": 0,
            "stopped": 0,
            "ssl_expired": 0,
            "ssl_expiring": 0,
        },
        "alerts": [],
    }

    for name, client in all_clients.items():
        try:
            site_result = get_server_sites(client)
            results["servers"].append(site_result)

            # 汇总统计
            summary = site_result.get("summary", {})
            results["summary"]["total"] += summary.get("total", 0)
            results["summary"]["running"] += summary.get("by_status", {}).get("running", 0)
            results["summary"]["stopped"] += summary.get("by_status", {}).get("stopped", 0)
            results["summary"]["ssl_expired"] += summary.get("ssl_expired", 0)
            results["summary"]["ssl_expiring"] += summary.get("ssl_expiring", 0)

            # 收集告警
            for alert in site_result.get("alerts", []):
                results["alerts"].append(alert)

        except Exception as e:
            results["servers"].append({
                "server": name,
                "error": str(e),
                "sites": [],
                "alerts": [{"level": "critical", "type": "connection", "message": str(e)}],
            })

    return results


def print_sites_table(results: dict):
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

                # 网站列表表格
                sites = server_data.get("sites", [])
                if sites:
                    table = Table(show_header=True, header_style="bold")
                    table.add_column("名称", style="cyan", width=25)
                    table.add_column("类型", width=8)
                    table.add_column("状态", width=8)
                    table.add_column("SSL", width=10)
                    table.add_column("PHP/端口", width=10)
                    table.add_column("备注", width=20)

                    for site in sites:
                        # 状态颜色
                        status = site.get("status", "unknown")
                        if status == "running":
                            status_str = "[green]运行[/green]"
                        elif status == "starting":
                            status_str = "[yellow]启动中[/yellow]"
                        else:
                            status_str = "[red]停止[/red]"

                        # SSL状态
                        ssl = site.get("ssl", {})
                        ssl_status = ssl.get("status", "none")
                        if ssl_status == "valid":
                            ssl_str = f"[green]{ssl.get('days_remaining', 0)}天[/green]"
                        elif ssl_status == "warning":
                            ssl_str = f"[yellow]{ssl.get('days_remaining', 0)}天[/yellow]"
                        elif ssl_status == "critical":
                            ssl_str = f"[red]{ssl.get('days_remaining', 0)}天[/red]"
                        elif ssl_status == "expired":
                            ssl_str = "[red]已过期[/red]"
                        else:
                            ssl_str = "-"

                        # PHP版本或端口
                        php_or_port = site.get("php_version") or str(site.get("port", "")) or "-"

                        table.add_row(
                            site.get("name", "-")[:25],
                            site.get("type", "-"),
                            status_str,
                            ssl_str,
                            php_or_port[:10],
                            (site.get("ps", "") or "")[:20],
                        )

                    console.print(table)
                else:
                    console.print("[yellow]无网站[/yellow]")

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
                         f"网站总数: {summary.get('total', 0)}, "
                         f"[green]运行: {summary.get('running', 0)}[/green], "
                         f"[red]停止: {summary.get('stopped', 0)}[/red], "
                         f"[red]SSL过期: {summary.get('ssl_expired', 0)}[/red], "
                         f"[yellow]SSL即将过期: {summary.get('ssl_expiring', 0)}[/yellow]")

        else:
            # 单服务器模式
            server_name = results.get("server", "Unknown")

            # 基本信息
            console.print(Panel(f"[bold]{server_name}[/bold]", title="服务器"))

            sites = results.get("sites", [])
            if sites:
                table = Table(show_header=True, header_style="bold")
                table.add_column("名称", style="cyan")
                table.add_column("类型")
                table.add_column("状态")
                table.add_column("SSL")
                table.add_column("路径")
                table.add_column("备注")

                for site in sites:
                    status = site.get("status", "unknown")
                    if status == "running":
                        status_str = "[green]运行[/green]"
                    elif status == "starting":
                        status_str = "[yellow]启动中[/yellow]"
                    else:
                        status_str = "[red]停止[/red]"

                    ssl = site.get("ssl", {})
                    ssl_status = ssl.get("status", "none")
                    if ssl_status == "valid":
                        ssl_str = f"[green]有效({ssl.get('days_remaining', 0)}天)[/green]"
                    elif ssl_status == "expired":
                        ssl_str = "[red]已过期[/red]"
                    elif ssl_status in ["warning", "critical"]:
                        ssl_str = f"[yellow]{ssl.get('days_remaining', 0)}天后过期[/yellow]"
                    else:
                        ssl_str = "-"

                    table.add_row(
                        site.get("name", "-"),
                        site.get("type", "-"),
                        status_str,
                        ssl_str,
                        site.get("path", "-")[:40],
                        site.get("ps", "")[:20],
                    )

                console.print(table)
            else:
                console.print("[yellow]无网站[/yellow]")

            # 汇总
            summary = results.get("summary", {})
            console.print(f"\n[bold]汇总:[/bold]")
            console.print(f"  总数: {summary.get('total', 0)}")
            console.print(f"  按类型: {summary.get('by_type', {})}")
            console.print(f"  按状态: {summary.get('by_status', {})}")

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
        description="宝塔面板网站状态检查",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 检查所有服务器的网站状态
  %(prog)s

  # 检查指定服务器
  %(prog)s --server prod-01

  # 只显示停止的网站
  %(prog)s --filter stopped

  # 只显示SSL即将过期的网站
  %(prog)s --filter ssl-warning

  # 输出到文件
  %(prog)s --output sites.json
        """,
    )
    parser.add_argument("--server", "-s", help="指定服务器名称")
    parser.add_argument("--format", "-f", choices=["json", "table"], default="table", help="输出格式")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--filter", choices=["stopped", "ssl-warning", "ssl-expired"],
                        help="过滤条件: stopped(停止的), ssl-warning(SSL即将过期), ssl-expired(SSL已过期)")
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
        results = run_sites_check(manager, args.server)
    except KeyError as e:
        print(f"错误: 未找到服务器 {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"检查失败: {e}", file=sys.stderr)
        sys.exit(1)

    # 应用过滤
    if args.filter:
        results = apply_filter(results, args.filter)

    # 输出结果
    if args.format == "table":
        print_sites_table(results)
    else:
        output = json.dumps(results, ensure_ascii=False, indent=2)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"结果已保存到: {args.output}")
        else:
            print(output)


def apply_filter(results: dict, filter_type: str) -> dict:
    """应用过滤条件"""
    if "servers" in results:
        # 多服务器模式
        for server_data in results.get("servers", []):
            if "sites" in server_data:
                server_data["sites"] = filter_sites(server_data["sites"], filter_type)
    elif "sites" in results:
        # 单服务器模式
        results["sites"] = filter_sites(results["sites"], filter_type)

    return results


def filter_sites(sites: list, filter_type: str) -> list:
    """过滤网站列表"""
    filtered = []
    for site in sites:
        if filter_type == "stopped":
            if site.get("status") == "stopped":
                filtered.append(site)
        elif filter_type == "ssl-warning":
            ssl = site.get("ssl", {})
            if ssl.get("status") == "warning":
                filtered.append(site)
        elif filter_type == "ssl-expired":
            ssl = site.get("ssl", {})
            if ssl.get("status") == "expired":
                filtered.append(site)
    return filtered


if __name__ == "__main__":
    main()
