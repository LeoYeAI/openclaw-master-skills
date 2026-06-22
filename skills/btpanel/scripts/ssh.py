#!/usr/bin/env python3
# /// script
# dependencies = [
#   "requests>=2.28",
#   "pyyaml>=6.0",
#   "rich>=13.0",
# ]
# ///
"""
SSH状态检查脚本
检查SSH服务状态和登录日志
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
    load_config,
)


def get_ssh_status(client: BtClient) -> dict:
    """
    获取SSH服务状态

    Args:
        client: 宝塔客户端

    Returns:
        SSH状态信息
    """
    result = {
        "server": client.name,
        "timestamp": datetime.now().isoformat(),
        "ssh": {},
        "alerts": [],
    }

    try:
        info = client.get_ssh_info()

        ssh_info = {
            "port": info.get("port", 22),
            "status": info.get("status", False),
            "status_text": info.get("status_text", "未知"),
            "ping_enabled": info.get("ping", False),
            "firewall_status": info.get("firewall_status", False),
            "fail2ban": {
                "status": info.get("fail2ban", {}).get("status", 0) == 1,
                "installed": info.get("fail2ban", {}).get("installed", 0) == 1,
            },
            "ban_cron_job": info.get("ban_cron_job", False),
        }

        result["ssh"] = ssh_info

        # 生成告警
        if not ssh_info["status"]:
            result["alerts"].append({
                "level": "critical",
                "type": "ssh",
                "message": "SSH服务已停止",
            })

        # 检查非标准端口
        if ssh_info["port"] != 22:
            result["alerts"].append({
                "level": "info",
                "type": "ssh",
                "message": f"SSH使用非标准端口: {ssh_info['port']}",
            })

    except Exception as e:
        result["error"] = str(e)
        result["alerts"].append({
            "level": "critical",
            "type": "connection",
            "message": f"获取SSH状态失败: {e}",
        })

    return result


def get_ssh_logs(client: BtClient, page: int = 1, limit: int = 50,
                 login_filter: str = "ALL", search: str = "") -> dict:
    """
    获取SSH登录日志

    Args:
        client: 宝塔客户端
        page: 页码
        limit: 每页数量
        login_filter: 过滤类型 (ALL/success/failed)
        search: 搜索关键字

    Returns:
        SSH登录日志
    """
    result = {
        "server": client.name,
        "timestamp": datetime.now().isoformat(),
        "logs": [],
        "summary": {
            "total": 0,
            "success": 0,
            "failed": 0,
            "unique_ips": set(),
        },
        "alerts": [],
    }

    try:
        response = client.get_ssh_logs(page=page, limit=limit, search=search)
        logs = response.get("data", [])

        # 解析日志
        parsed_logs = []
        for log in logs:
            parsed_log = {
                "time": log.get("time", ""),
                "timestamp": log.get("timestamp", 0),
                "type": log.get("type", "unknown"),  # success/failed
                "status": log.get("status", 0),
                "user": log.get("user", ""),
                "address": log.get("address", ""),
                "port": log.get("port", ""),
                "login_type": log.get("login_type", "password"),
                "area": log.get("area", {}).get("info", "未知"),
                "deny_status": log.get("deny_status", 0),
            }

            # 应用过滤
            if login_filter != "ALL":
                if login_filter == "success" and parsed_log["type"] != "success":
                    continue
                elif login_filter == "failed" and parsed_log["type"] != "failed":
                    continue

            parsed_logs.append(parsed_log)

            # 统计
            result["summary"]["total"] += 1
            if parsed_log["type"] == "success":
                result["summary"]["success"] += 1
            else:
                result["summary"]["failed"] += 1
            result["summary"]["unique_ips"].add(parsed_log["address"])

        result["logs"] = parsed_logs
        result["summary"]["unique_ips"] = len(result["summary"]["unique_ips"])

        # 生成告警 - 检测异常登录
        recent_failed = sum(1 for log in parsed_logs[:10] if log["type"] == "failed")
        if recent_failed >= 5:
            result["alerts"].append({
                "level": "warning",
                "type": "ssh",
                "message": f"最近10条日志中有{recent_failed}次登录失败",
            })

    except Exception as e:
        result["error"] = str(e)
        result["alerts"].append({
            "level": "critical",
            "type": "connection",
            "message": f"获取SSH日志失败: {e}",
        })

    return result


def run_ssh_check(manager: BtClientManager, server: Optional[str] = None,
                  check_type: str = "status") -> dict:
    """
    执行SSH检查

    Args:
        manager: 客户端管理器
        server: 指定服务器名称
        check_type: 检查类型 (status/logs)

    Returns:
        检查结果
    """
    # 单个服务器
    if server:
        client = manager.get_client(server)
        if check_type == "status":
            return get_ssh_status(client)
        else:
            return get_ssh_logs(client)

    # 所有服务器
    all_clients = manager.get_all_clients()
    results = {
        "timestamp": datetime.now().isoformat(),
        "servers": [],
    }

    for name, client in all_clients.items():
        try:
            if check_type == "status":
                result = get_ssh_status(client)
            else:
                result = get_ssh_logs(client)
            results["servers"].append(result)
        except Exception as e:
            results["servers"].append({
                "server": name,
                "error": str(e),
                "alerts": [{"level": "critical", "type": "connection", "message": str(e)}],
            })

    return results


def print_ssh_status(results: dict):
    """打印SSH状态输出"""
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel

        console = Console()

        if "servers" in results:
            # 多服务器模式
            for server_data in results["servers"]:
                if "error" in server_data:
                    console.print(f"[red]服务器 {server_data.get('server', 'Unknown')} 错误: {server_data['error']}[/red]")
                    continue

                server_name = server_data.get("server", "Unknown")
                ssh_info = server_data.get("ssh", {})

                console.print(f"\n[bold cyan]═══ {server_name} ═══[/bold cyan]")

                # SSH状态表格
                table = Table(show_header=True, header_style="bold")
                table.add_column("项目", style="cyan", width=20)
                table.add_column("值", width=30)

                status_str = "[green]运行中[/green]" if ssh_info.get("status") else "[red]已停止[/red]"
                table.add_row("SSH服务", status_str)
                table.add_row("端口", str(ssh_info.get("port", 22)))
                table.add_row("Ping", "允许" if ssh_info.get("ping_enabled") else "禁止")
                table.add_row("防火墙", "开启" if ssh_info.get("firewall_status") else "关闭")

                fail2ban = ssh_info.get("fail2ban", {})
                fb_status = "已安装" if fail2ban.get("installed") else "未安装"
                if fail2ban.get("status"):
                    fb_status += " [green](运行中)[/green]"
                table.add_row("Fail2ban", fb_status)

                console.print(table)

                # 告警
                alerts = server_data.get("alerts", [])
                if alerts:
                    console.print("\n[yellow]提示:[/yellow]")
                    for alert in alerts:
                        level = alert.get("level", "info")
                        if level == "critical":
                            color = "red"
                        elif level == "warning":
                            color = "yellow"
                        else:
                            color = "blue"
                        console.print(f"  [{color}]• {alert.get('message', '')}[/{color}]")

        else:
            # 单服务器模式
            server_name = results.get("server", "Unknown")
            ssh_info = results.get("ssh", {})

            console.print(Panel(f"[bold]{server_name} - SSH状态[/bold]", title="服务器"))

            table = Table(show_header=True, header_style="bold")
            table.add_column("项目", style="cyan")
            table.add_column("值")

            status_str = "[green]运行中[/green]" if ssh_info.get("status") else "[red]已停止[/red]"
            table.add_row("SSH服务", status_str)
            table.add_row("端口", str(ssh_info.get("port", 22)))
            table.add_row("状态描述", ssh_info.get("status_text", "未知"))
            table.add_row("Ping", "允许" if ssh_info.get("ping_enabled") else "禁止")
            table.add_row("防火墙", "开启" if ssh_info.get("firewall_status") else "关闭")

            fail2ban = ssh_info.get("fail2ban", {})
            fb_status = "已安装" if fail2ban.get("installed") else "未安装"
            if fail2ban.get("status"):
                fb_status += " (运行中)"
            table.add_row("Fail2ban", fb_status)

            console.print(table)

            # 告警
            alerts = results.get("alerts", [])
            if alerts:
                console.print(f"\n[bold yellow]告警 ({len(alerts)}条):[/bold yellow]")
                for alert in alerts:
                    level = alert.get("level", "info")
                    if level == "critical":
                        color = "red"
                    elif level == "warning":
                        color = "yellow"
                    else:
                        color = "blue"
                    console.print(f"  [{color}]• {alert.get('message', '')}[/{color}]")

    except ImportError:
        print("请安装rich库以使用表格输出: pip install rich")
        print(json.dumps(results, ensure_ascii=False, indent=2, default=str))


def print_ssh_logs(results: dict):
    """打印SSH日志输出"""
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel

        console = Console()

        if "servers" in results:
            # 多服务器模式
            for server_data in results["servers"]:
                if "error" in server_data:
                    console.print(f"[red]服务器 {server_data.get('server', 'Unknown')} 错误: {server_data['error']}[/red]")
                    continue

                server_name = server_data.get("server", "Unknown")
                logs = server_data.get("logs", [])
                summary = server_data.get("summary", {})

                console.print(f"\n[bold cyan]═══ {server_name} ═══[/bold cyan]")

                # 汇总
                console.print(f"[dim]总计: {summary.get('total', 0)} 条, "
                             f"[green]成功: {summary.get('success', 0)}[/green], "
                             f"[red]失败: {summary.get('failed', 0)}[/red], "
                             f"独立IP: {summary.get('unique_ips', 0)}[/dim]")

                if logs:
                    table = Table(show_header=True, header_style="bold")
                    table.add_column("时间", width=20)
                    table.add_column("类型", width=8)
                    table.add_column("用户", width=10)
                    table.add_column("IP地址", width=18)
                    table.add_column("地区", width=15)

                    for log in logs[:30]:
                        type_str = "[green]成功[/green]" if log["type"] == "success" else "[red]失败[/red]"
                        table.add_row(
                            log.get("time", "")[:19],
                            type_str,
                            log.get("user", "-"),
                            log.get("address", "-"),
                            log.get("area", "未知")[:15],
                        )

                    console.print(table)
                else:
                    console.print("[yellow]无登录日志[/yellow]")

                # 告警
                alerts = server_data.get("alerts", [])
                if alerts:
                    console.print("\n[yellow]告警:[/yellow]")
                    for alert in alerts:
                        level = alert.get("level", "warning")
                        color = "red" if level == "critical" else "yellow"
                        console.print(f"  [{color}]• {alert.get('message', '')}[/{color}]")

        else:
            # 单服务器模式
            server_name = results.get("server", "Unknown")
            logs = results.get("logs", [])
            summary = results.get("summary", {})

            console.print(Panel(f"[bold]{server_name} - SSH登录日志[/bold]", title="服务器"))

            # 汇总
            console.print(f"[dim]总计: {summary.get('total', 0)} 条, "
                         f"[green]成功: {summary.get('success', 0)}[/green], "
                         f"[red]失败: {summary.get('failed', 0)}[/red], "
                         f"独立IP: {summary.get('unique_ips', 0)}[/dim]")

            if logs:
                table = Table(show_header=True, header_style="bold")
                table.add_column("时间")
                table.add_column("类型")
                table.add_column("用户")
                table.add_column("IP地址")
                table.add_column("端口")
                table.add_column("地区")

                for log in logs[:50]:
                    type_str = "[green]成功[/green]" if log["type"] == "success" else "[red]失败[/red]"
                    table.add_row(
                        log.get("time", "")[:19],
                        type_str,
                        log.get("user", "-"),
                        log.get("address", "-"),
                        log.get("port", "-"),
                        log.get("area", "未知"),
                    )

                console.print(table)
            else:
                console.print("[yellow]无登录日志[/yellow]")

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
        print(json.dumps(results, ensure_ascii=False, indent=2, default=str))


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="宝塔面板SSH状态和日志检查",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 查看SSH服务状态
  %(prog)s --status

  # 查看SSH登录日志
  %(prog)s --logs

  # 只查看失败的登录日志
  %(prog)s --logs --filter failed

  # 只查看成功的登录日志
  %(prog)s --logs --filter success

  # 搜索特定IP的登录记录
  %(prog)s --logs --search 192.168.1.1

  # 指定服务器
  %(prog)s --status --server prod-01

  # JSON格式输出
  %(prog)s --logs --format json
        """,
    )
    parser.add_argument("--server", "-s", help="指定服务器名称")
    parser.add_argument("--status", action="store_true", help="查看SSH服务状态")
    parser.add_argument("--logs", action="store_true", help="查看SSH登录日志")
    parser.add_argument("--filter", choices=["ALL", "success", "failed"], default="ALL",
                        help="日志过滤: ALL(全部), success(成功), failed(失败)")
    parser.add_argument("--search", help="搜索关键字（IP地址或用户名）")
    parser.add_argument("--limit", "-n", type=int, default=50,
                        help="返回日志条数 (默认: 50)")
    parser.add_argument("--format", "-f", choices=["json", "table"], default="table",
                        help="输出格式")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--config", "-c", help="配置文件路径")

    args = parser.parse_args()

    # 默认显示状态
    if not args.status and not args.logs:
        args.status = True

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
        if args.status:
            results = run_ssh_check(manager, args.server, "status")
            if args.format == "json":
                output = json.dumps(results, ensure_ascii=False, indent=2, default=str)
                if args.output:
                    with open(args.output, "w", encoding="utf-8") as f:
                        f.write(output)
                    print(f"结果已保存到: {args.output}")
                else:
                    print(output)
            else:
                print_ssh_status(results)

        if args.logs:
            results = run_ssh_check(manager, args.server, "logs")
            # 应用过滤
            if args.filter != "ALL" or args.search:
                if "servers" in results:
                    for server_data in results["servers"]:
                        if "logs" in server_data:
                            filtered_logs = []
                            for log in server_data["logs"]:
                                if args.filter != "ALL":
                                    if args.filter == "success" and log["type"] != "success":
                                        continue
                                    elif args.filter == "failed" and log["type"] != "failed":
                                        continue
                                if args.search:
                                    if args.search not in log.get("address", "") and args.search not in log.get("user", ""):
                                        continue
                                filtered_logs.append(log)
                            server_data["logs"] = filtered_logs
                            # 更新统计
                            server_data["summary"]["total"] = len(filtered_logs)
                            server_data["summary"]["success"] = sum(1 for l in filtered_logs if l["type"] == "success")
                            server_data["summary"]["failed"] = sum(1 for l in filtered_logs if l["type"] == "failed")
                            server_data["summary"]["unique_ips"] = len(set(l["address"] for l in filtered_logs))
                elif "logs" in results:
                    filtered_logs = []
                    for log in results["logs"]:
                        if args.filter != "ALL":
                            if args.filter == "success" and log["type"] != "success":
                                continue
                            elif args.filter == "failed" and log["type"] != "failed":
                                continue
                        if args.search:
                            if args.search not in log.get("address", "") and args.search not in log.get("user", ""):
                                continue
                        filtered_logs.append(log)
                    results["logs"] = filtered_logs
                    results["summary"]["total"] = len(filtered_logs)
                    results["summary"]["success"] = sum(1 for l in filtered_logs if l["type"] == "success")
                    results["summary"]["failed"] = sum(1 for l in filtered_logs if l["type"] == "failed")
                    results["summary"]["unique_ips"] = len(set(l["address"] for l in filtered_logs))

            if args.format == "json":
                output = json.dumps(results, ensure_ascii=False, indent=2, default=str)
                if args.output:
                    with open(args.output, "w", encoding="utf-8") as f:
                        f.write(output)
                    print(f"结果已保存到: {args.output}")
                else:
                    print(output)
            else:
                print_ssh_logs(results)

    except KeyError as e:
        print(f"错误: 未找到服务器 {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"检查失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
