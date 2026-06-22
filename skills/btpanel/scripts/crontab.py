#!/usr/bin/env python3
# /// script
# dependencies = [
#   "requests>=2.28",
#   "pyyaml>=6.0",
#   "rich>=13.0",
# ]
# ///
"""
计划任务检查脚本
检查宝塔面板的计划任务，重点关注备份任务
"""

import argparse
import json
import re
import sys
import time
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


# 任务类型映射
TASK_TYPE_MAP = {
    "toShell": "Shell脚本",
    "site": "备份网站",
    "database": "备份数据库",
    "path": "备份目录",
    "sync_time": "同步时间",
    "log": "切割日志",
    "rememory": "释放内存",
    "access": "访问URL",
    "backup": "备份",
}

# 任务类型分类
BACKUP_TYPES = ["site", "database", "path"]


def parse_crontab_task(task: dict) -> dict:
    """
    解析计划任务数据

    Args:
        task: 原始任务数据

    Returns:
        解析后的任务信息
    """
    s_type = task.get("sType", "")
    task_type = TASK_TYPE_MAP.get(s_type, s_type or "其他")

    # 判断是否为备份任务
    is_backup = s_type in BACKUP_TYPES or "备份" in task.get("name", "")

    # 解析执行周期
    cycle = task.get("cycle", "") or task.get("type_zh", "")

    # 解析执行时间
    exec_time = ""
    if task.get("type") == "day":
        hour = task.get("where_hour", 0)
        minute = task.get("where_minute", 0)
        exec_time = f"每天 {hour:02d}:{minute:02d}"
    elif task.get("type") == "hour":
        minute = task.get("where_minute", 0)
        exec_time = f"每小时 {minute:02d}分"
    elif task.get("type") == "minute-n":
        interval = task.get("where1", "5")
        exec_time = f"每 {interval} 分钟"
    elif task.get("type") == "week":
        days = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"]
        day_idx = int(task.get("where1", 0))
        hour = task.get("where_hour", 0)
        minute = task.get("where_minute", 0)
        exec_time = f"每{days[day_idx]} {hour:02d}:{minute:02d}"
    elif task.get("type") == "month":
        day = task.get("where1", 1)
        hour = task.get("where_hour", 0)
        minute = task.get("where_minute", 0)
        exec_time = f"每月{day}日 {hour:02d}:{minute:02d}"

    return {
        "id": task.get("id"),
        "name": task.get("name", "") or task.get("rname", ""),
        "type": task_type,
        "s_type": s_type,
        "is_backup": is_backup,
        "status": task.get("status", 0) == 1,
        "enabled": task.get("status", 0) == 1,
        "cycle": cycle,
        "exec_time": exec_time,
        "backup_target": task.get("sName", "") if is_backup else "",
        "backup_path": task.get("db_backup_path", "/www/backup"),
        "save_count": task.get("save", 0) if is_backup else None,
        "command": task.get("sBody", ""),
        "user": task.get("user", "root"),
        "addtime": task.get("addtime", ""),
        "type_name": task.get("type_name", ""),
        "result": task.get("result", 0),  # 0=未执行/失败, 1=成功
    }


def get_crontab_status(client: BtClient, page: int = 1, limit: int = 100) -> dict:
    """
    获取计划任务状态

    Args:
        client: 宝塔客户端
        page: 页码
        limit: 每页数量

    Returns:
        计划任务状态信息
    """
    result = {
        "server": client.name,
        "timestamp": datetime.now().isoformat(),
        "tasks": [],
        "summary": {
            "total": 0,
            "enabled": 0,
            "disabled": 0,
            "backup_tasks": 0,
            "shell_tasks": 0,
            "other_tasks": 0,
        },
        "backup_tasks": [],
        "alerts": [],
    }

    try:
        response = client.get_crontab_list(page=page, limit=limit)
        tasks = response.get("data", [])

        for task in tasks:
            parsed = parse_crontab_task(task)
            result["tasks"].append(parsed)

            # 统计
            result["summary"]["total"] += 1
            if parsed["enabled"]:
                result["summary"]["enabled"] += 1
            else:
                result["summary"]["disabled"] += 1
                result["alerts"].append({
                    "level": "warning",
                    "type": "crontab",
                    "message": f"任务 [{parsed['name']}] 已禁用",
                    "task_id": parsed["id"],
                })

            if parsed["is_backup"]:
                result["summary"]["backup_tasks"] += 1
                result["backup_tasks"].append(parsed)
            elif parsed["s_type"] == "toShell":
                result["summary"]["shell_tasks"] += 1
            else:
                result["summary"]["other_tasks"] += 1

    except Exception as e:
        result["error"] = str(e)
        result["alerts"].append({
            "level": "critical",
            "type": "connection",
            "message": f"获取计划任务失败: {e}",
        })

    return result


def get_backup_task_logs(client: BtClient, task_id: int, days: int = 7) -> dict:
    """
    获取备份任务日志

    Args:
        client: 宝塔客户端
        task_id: 任务ID
        days: 查询天数

    Returns:
        任务日志信息
    """
    result = {
        "server": client.name,
        "task_id": task_id,
        "timestamp": datetime.now().isoformat(),
        "logs": [],
        "last_status": None,
        "alerts": [],
    }

    try:
        # 计算时间范围
        end_timestamp = int(time.time())
        start_timestamp = end_timestamp - (days * 24 * 60 * 60)

        response = client.get_crontab_logs(
            task_id=task_id,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
        )

        if response.get("status"):
            log_content = response.get("msg", "")
            result["logs"] = parse_backup_log(log_content)

            # 分析最后的执行状态
            if result["logs"]:
                last_log = result["logs"][-1]
                result["last_status"] = last_log.get("status")
                if last_log.get("status") == "failed":
                    result["alerts"].append({
                        "level": "warning",
                        "type": "backup",
                        "message": f"备份任务最后一次执行失败: {last_log.get('message', '')}",
                    })
        else:
            result["error"] = response.get("msg", "获取日志失败")

    except Exception as e:
        result["error"] = str(e)

    return result


def parse_backup_log(log_content: str) -> list:
    """
    解析备份日志

    Args:
        log_content: 日志内容

    Returns:
        解析后的日志列表
    """
    logs = []

    # 按执行块分割
    blocks = re.split(r"={10,}", log_content)

    for block in blocks:
        if not block.strip():
            continue

        log_entry = {
            "time": "",
            "status": "unknown",
            "message": "",
            "details": [],
        }

        # 提取时间
        time_match = re.search(r"开始备份\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]", block)
        if time_match:
            log_entry["time"] = time_match.group(1)

        # 提取状态
        if "Successful" in block:
            log_entry["status"] = "success"
        elif "Failed" in block or "失败" in block:
            log_entry["status"] = "failed"

        # 提取详细信息
        lines = block.strip().split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("|-"):
                log_entry["details"].append(line[2:])

        # 提取备份文件路径
        file_match = re.search(r"网站已备份到：(.+\.tar\.gz)", block)
        if file_match:
            log_entry["backup_file"] = file_match.group(1)

        if log_entry["time"] or log_entry["status"] != "unknown":
            logs.append(log_entry)

    return logs


def run_crontab_check(manager: BtClientManager, server: Optional[str] = None,
                      backup_only: bool = False) -> dict:
    """
    执行计划任务检查

    Args:
        manager: 客户端管理器
        server: 指定服务器名称
        backup_only: 只返回备份任务

    Returns:
        检查结果
    """
    # 单个服务器
    if server:
        client = manager.get_client(server)
        result = get_crontab_status(client)
        if backup_only:
            result["tasks"] = [t for t in result["tasks"] if t["is_backup"]]
        return result

    # 所有服务器
    all_clients = manager.get_all_clients()
    results = {
        "timestamp": datetime.now().isoformat(),
        "servers": [],
        "summary": {
            "total_servers": 0,
            "total_tasks": 0,
            "total_backup_tasks": 0,
            "total_enabled": 0,
            "total_disabled": 0,
        },
        "alerts": [],
    }

    for name, client in all_clients.items():
        try:
            server_result = get_crontab_status(client)
            if backup_only:
                server_result["tasks"] = [t for t in server_result["tasks"] if t["is_backup"]]

            results["servers"].append(server_result)

            # 汇总
            summary = server_result.get("summary", {})
            results["summary"]["total_servers"] += 1
            results["summary"]["total_tasks"] += summary.get("total", 0)
            results["summary"]["total_backup_tasks"] += summary.get("backup_tasks", 0)
            results["summary"]["total_enabled"] += summary.get("enabled", 0)
            results["summary"]["total_disabled"] += summary.get("disabled", 0)

            # 收集告警
            for alert in server_result.get("alerts", []):
                alert["server"] = name
                results["alerts"].append(alert)

        except Exception as e:
            results["servers"].append({
                "server": name,
                "error": str(e),
                "alerts": [{"level": "critical", "type": "connection", "message": str(e)}],
            })

    return results


def print_crontab_table(results: dict, backup_only: bool = False):
    """打印表格格式输出"""
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel

        console = Console()

        if "servers" in results and len(results["servers"]) > 1:
            # 多服务器模式
            for server_data in results["servers"]:
                if "error" in server_data:
                    console.print(f"[red]服务器 {server_data.get('server', 'Unknown')} 错误: {server_data['error']}[/red]")
                    continue

                server_name = server_data.get("server", "Unknown")
                summary = server_data.get("summary", {})

                console.print(f"\n[bold cyan]═══ {server_name} ═══[/bold cyan]")

                # 任务列表
                tasks = server_data.get("tasks", [])
                if tasks:
                    table = Table(show_header=True, header_style="bold")
                    table.add_column("名称", style="cyan", width=30)
                    table.add_column("类型", width=12)
                    table.add_column("状态", width=8)
                    table.add_column("执行时间", width=20)
                    table.add_column("备份目标", width=15)

                    for task in tasks:
                        # 状态
                        if task["enabled"]:
                            status_str = "[green]启用[/green]"
                        else:
                            status_str = "[red]禁用[/red]"

                        # 备份目标
                        backup_target = task.get("backup_target", "") or ""

                        table.add_row(
                            task.get("name", "-")[:30],
                            task.get("type", "-"),
                            status_str,
                            task.get("exec_time", "-")[:20],
                            backup_target[:15],
                        )

                    console.print(table)
                else:
                    console.print("[yellow]无计划任务[/yellow]")

                # 汇总
                console.print(f"\n[dim]汇总: "
                             f"总数 {summary.get('total', 0)}, "
                             f"[green]启用 {summary.get('enabled', 0)}[/green], "
                             f"[red]禁用 {summary.get('disabled', 0)}[/red], "
                             f"备份任务 {summary.get('backup_tasks', 0)}[/dim]")

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
                         f"任务总数: {summary.get('total_tasks', 0)}, "
                         f"[green]启用: {summary.get('total_enabled', 0)}[/green], "
                         f"[red]禁用: {summary.get('total_disabled', 0)}[/red], "
                         f"备份任务: {summary.get('total_backup_tasks', 0)}")

        else:
            # 单服务器模式
            server_name = results.get("server", "Unknown")
            summary = results.get("summary", {})

            console.print(Panel(f"[bold]{server_name} - 计划任务[/bold]", title="服务器"))

            tasks = results.get("tasks", [])
            if tasks:
                table = Table(show_header=True, header_style="bold")
                table.add_column("ID", width=6)
                table.add_column("名称", style="cyan")
                table.add_column("类型")
                table.add_column("状态")
                table.add_column("执行时间")
                table.add_column("备份目标")
                table.add_column("保留数")

                for task in tasks:
                    # 状态
                    if task["enabled"]:
                        status_str = "[green]启用[/green]"
                    else:
                        status_str = "[red]禁用[/red]"

                    # 保留数
                    save_count = task.get("save_count")
                    save_str = str(save_count) if save_count is not None else "-"

                    table.add_row(
                        str(task.get("id", "-")),
                        task.get("name", "-")[:25],
                        task.get("type", "-"),
                        status_str,
                        task.get("exec_time", "-"),
                        task.get("backup_target", "")[:15] or "-",
                        save_str,
                    )

                console.print(table)
            else:
                console.print("[yellow]无计划任务[/yellow]")

            # 汇总
            console.print(f"\n[bold]汇总:[/bold]")
            console.print(f"  总数: {summary.get('total', 0)}")
            console.print(f"  [green]启用: {summary.get('enabled', 0)}[/green]")
            console.print(f"  [red]禁用: {summary.get('disabled', 0)}[/red]")
            console.print(f"  备份任务: {summary.get('backup_tasks', 0)}")
            console.print(f"  Shell任务: {summary.get('shell_tasks', 0)}")
            console.print(f"  其他任务: {summary.get('other_tasks', 0)}")

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
        description="宝塔面板计划任务检查",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 查看所有计划任务
  %(prog)s

  # 只查看备份任务
  %(prog)s --backup-only

  # 查看指定服务器
  %(prog)s --server prod-01

  # 查看备份任务日志
  %(prog)s --logs --task-id 11

  # JSON格式输出
  %(prog)s --format json
        """,
    )
    parser.add_argument("--server", "-s", help="指定服务器名称")
    parser.add_argument("--backup-only", action="store_true", help="只显示备份任务")
    parser.add_argument("--logs", action="store_true", help="查看任务日志")
    parser.add_argument("--task-id", type=int, help="任务ID（配合--logs使用）")
    parser.add_argument("--days", type=int, default=7, help="日志查询天数（默认7天）")
    parser.add_argument("--format", "-f", choices=["json", "table"], default="table", help="输出格式")
    parser.add_argument("--output", "-o", help="输出文件路径")
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

    try:
        if args.logs and args.task_id:
            # 查看任务日志
            if args.server:
                client = manager.get_client(args.server)
            else:
                # 获取第一个服务器
                client = list(manager.get_all_clients().values())[0]

            results = get_backup_task_logs(client, args.task_id, args.days)
        else:
            # 查看任务列表
            results = run_crontab_check(manager, args.server, args.backup_only)

    except KeyError as e:
        print(f"错误: 未找到服务器 {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"检查失败: {e}", file=sys.stderr)
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
        if args.logs:
            # 日志输出
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            print_crontab_table(results, args.backup_only)


if __name__ == "__main__":
    main()
