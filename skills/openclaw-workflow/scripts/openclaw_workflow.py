#!/usr/bin/env python3
"""
OpenClaw Workflow CLI — 工作流命令行入口

用法:
    python3 openclaw_workflow.py execute <workflow.yaml>   运行工作流
    python3 openclaw_workflow.py validate <workflow.yaml>  验证工作流语法
    python3 openclaw_workflow.py list [directory]          列出可用工作流
    python3 openclaw_workflow.py runs                      列出历史运行记录
    python3 openclaw_workflow.py resume <run_id>           从断点恢复
    python3 openclaw_workflow.py dashboard                 启动 Streamlit 面板
"""

import argparse
import json
import os
import sys

# ── 强制 stdout/stderr 行缓冲 ─────────────────────────────
# OpenClaw exec 工具以非 TTY 方式运行子进程，Python 默认全缓冲会导致
# agent 看不到任何输出，误以为进程挂起而 kill 掉。
# 必须在所有 import 之前（尤其是 engine）生效。
os.environ["PYTHONUNBUFFERED"] = "1"
try:
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
except AttributeError:
    pass  # Python < 3.7

# 确保 engine 包可导入
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.engine import WorkflowEngine


def cmd_execute(args):
    """执行工作流"""
    engine = WorkflowEngine(workflow_file=args.workflow)
    record = engine.run()

    print("\n" + "=" * 60)
    print(f"工作流: {record.flow_id}")
    print(f"运行ID: {record.run_id}")
    print(f"状态:   {record.status}")
    print(f"开始:   {record.started_at}")
    print(f"结束:   {record.finished_at}")
    print(f"步骤:   {len(record.steps)} 步")

    for s in record.steps:
        icon = {"success": "✅", "failed": "❌", "skipped": "⏭️", "pending": "⏳"}.get(s.status, "❓")
        retry_info = f" (重试 {s.retries} 次)" if s.retries > 0 else ""
        print(f"  {icon} {s.step_name} [{s.step_type}] {s.status}{retry_info}")
    print("=" * 60)

    return 0 if record.status == "success" else 1


def cmd_validate(args):
    """验证工作流"""
    engine = WorkflowEngine(workflow_file=args.workflow)
    is_valid, errors = engine.validate()

    if is_valid:
        print("✅ 工作流验证通过!")
        # 显示警告
        warnings = [e for e in errors if e.severity == "warning"]
        for w in warnings:
            print(f"  {w}")
    else:
        print("❌ 工作流验证失败:")
        for e in errors:
            print(f"  {e}")

    return 0 if is_valid else 1


def cmd_list(args):
    """列出工作流"""
    directory = getattr(args, 'directory', None)
    workflows = WorkflowEngine.list_workflows(directory)

    if not workflows:
        print("未找到工作流文件")
        return 0

    print(f"找到 {len(workflows)} 个工作流:\n")
    for wf in workflows:
        print(f"  📋 {wf['name']}")
        print(f"     文件: {wf['file']}")
        print(f"     步骤: {wf['steps']} 步")
        if wf['description']:
            print(f"     描述: {wf['description']}")
        print()

    return 0


def cmd_runs(args):
    """列出运行记录"""
    runs = WorkflowEngine.list_runs()

    if not runs:
        print("暂无运行记录")
        return 0

    print(f"最近 {len(runs)} 条运行记录:\n")
    for run in runs:
        icon = {"success": "✅", "failed": "❌", "aborted": "⛔"}.get(run["status"], "❓")
        print(f"  {icon} {run['flow_id']}")
        print(f"     ID: {run['run_id']}")
        print(f"     状态: {run['status']}")
        print(f"     时间: {run.get('started_at', 'N/A')}")
        steps_count = len(run.get("steps", []))
        print(f"     步骤: {steps_count} 步")
        print()

    return 0


def cmd_resume(args):
    """从断点恢复"""
    try:
        engine = WorkflowEngine.resume(args.run_id)
        print(f"✅ 已加载快照: {args.run_id}")
        print("⚠️  断点恢复功能尚在开发中")
        return 0
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return 1


def cmd_dashboard(args):
    """启动 Streamlit 面板"""
    dashboard_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard.py")

    if not os.path.exists(dashboard_path):
        print("❌ 面板文件不存在")
        return 1

    port = getattr(args, 'port', 8501)
    os.execvp("streamlit", ["streamlit", "run", dashboard_path, "--server.port", str(port)])


def main():
    parser = argparse.ArgumentParser(
        prog="openclaw-workflow",
        description="OpenClaw Workflow: 确定性工作流编排引擎",
    )
    sub = parser.add_subparsers(dest="command", help="子命令")

    # execute
    p_exec = sub.add_parser("execute", aliases=["run", "exec"], help="执行工作流")
    p_exec.add_argument("workflow", help="工作流 YAML 文件路径")

    # validate
    p_val = sub.add_parser("validate", aliases=["check"], help="验证工作流语法")
    p_val.add_argument("workflow", help="工作流 YAML 文件路径")

    # list
    p_list = sub.add_parser("list", aliases=["ls"], help="列出可用工作流")
    p_list.add_argument("directory", nargs="?", help="搜索目录")

    # runs
    p_runs = sub.add_parser("runs", aliases=["history"], help="列出运行记录")

    # resume
    p_resume = sub.add_parser("resume", help="从断点恢复")
    p_resume.add_argument("run_id", help="运行 ID")

    # dashboard
    p_dash = sub.add_parser("dashboard", aliases=["ui", "web"], help="启动可视化面板")
    p_dash.add_argument("--port", type=int, default=8501, help="端口号")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    cmd_map = {
        "execute": cmd_execute, "run": cmd_execute, "exec": cmd_execute,
        "validate": cmd_validate, "check": cmd_validate,
        "list": cmd_list, "ls": cmd_list,
        "runs": cmd_runs, "history": cmd_runs,
        "resume": cmd_resume,
        "dashboard": cmd_dashboard, "ui": cmd_dashboard, "web": cmd_dashboard,
    }

    handler = cmd_map.get(args.command)
    if handler:
        sys.exit(handler(args))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
