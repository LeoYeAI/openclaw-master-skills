#!/usr/bin/env python3
"""Team Dispatch Watcher (low-frequency reconciliation)

Purpose
- Provide a *low-frequency* safety net when completion events are missed.
- Detect and surface "stuck" tasks (in-progress longer than timeoutSeconds + grace).
- Send detailed alerts to main agent with full context from task files.

What it does
- Scans ~/.openclaw/workspace/tasks/active/*.json
- For each task in-progress:
    - If overdue -> mark as failed with error=timeout and increment retries
    - If retries remain -> reset to pending (so the main agent can re-dispatch)
    - Else -> keep failed and mark project blocked
- Sends detailed alert to main agent with task context

Usage
  python3 scripts/watch.py --interval 60 --grace 15

Recommended
- interval: 30-120s (adaptive is implemented; this is the max sleep)
- grace: 10-30s
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import random
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

TZ_SH = timezone(timedelta(hours=8))


def now_iso() -> str:
    return datetime.now(TZ_SH).isoformat(timespec="seconds")


def parse_iso(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


@dataclass
class TaskDetail:
    """单个任务的详细信息"""
    project: str
    task_id: str
    agent_id: str
    description: str
    status: str
    error: str
    retries: int
    retry_limit: int
    timeout_seconds: int
    started_at: str | None
    depends_on: List[str]
    result: str


@dataclass
class ScanResult:
    changed_files: int = 0
    overdue_tasks: int = 0
    reset_to_pending: int = 0
    blocked_projects: int = 0
    task_details: List[TaskDetail] = field(default_factory=list)
    blocked_projects_info: List[Dict[str, Any]] = field(default_factory=list)


def scan_file(path: str, grace: int) -> tuple[bool, dict, ScanResult]:
    """扫描单个项目文件，返回是否变更、更新后的数据、扫描结果"""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    project_name = data.get("project", os.path.basename(path).replace(".json", ""))
    retry_limit = int(data.get("retryLimit", 1))
    project_status = data.get("status", "active")

    changed = False
    sr = ScanResult()

    if project_status not in ("active", "blocked"):
        return False, data, sr

    tasks = data.get("tasks", [])
    project_blocked = False
    blocked_tasks = []

    for t in tasks:
        if t.get("status") != "in-progress":
            continue
        
        started = parse_iso(t.get("startedAt"))
        timeout_s = int(t.get("timeoutSeconds", 60))
        
        if not started:
            continue

        deadline = started.timestamp() + timeout_s + grace
        if time.time() <= deadline:
            continue

        # overdue detected
        task_detail = TaskDetail(
            project=project_name,
            task_id=t.get("id", "unknown"),
            agent_id=t.get("agentId", "unknown"),
            description=t.get("description", "")[:200],  # 截断避免太长
            status="failed",
            error=f"timeout: exceeded {timeout_s}s (+{grace}s grace)",
            retries=int(t.get("retries", 0)) + 1,
            retry_limit=retry_limit,
            timeout_seconds=timeout_s,
            started_at=t.get("startedAt"),
            depends_on=t.get("dependsOn", []),
            result=t.get("result", "")[:500]  # 截断
        )
        
        sr.overdue_tasks += 1
        t["error"] = task_detail.error
        t["status"] = "failed"
        t["completedAt"] = now_iso()
        t["retries"] = task_detail.retries
        changed = True

        if t["retries"] <= retry_limit:
            # auto retry: reset to pending
            t["status"] = "pending"
            t["startedAt"] = None
            t["sessionKey"] = None
            sr.reset_to_pending += 1
            task_detail.status = "reset_to_pending"
        else:
            # retries exhausted -> block project
            project_blocked = True
            blocked_tasks.append(task_detail)
            
        sr.task_details.append(task_detail)

    if project_blocked:
        data["status"] = "blocked"
        sr.blocked_projects += 1
        sr.blocked_projects_info.append({
            "project": project_name,
            "blocked_tasks": [{"id": t.task_id, "agent": t.agent_id, "description": t.description} for t in blocked_tasks],
            "total_tasks": len(tasks),
            "failed_tasks": len(blocked_tasks)
        })

    if changed:
        sr.changed_files += 1
        data["updated"] = now_iso()
        
    return changed, data, sr


def scan_once(tasks_dir: str, grace: int) -> ScanResult:
    """扫描所有活跃项目"""
    out = ScanResult()
    active_dir = os.path.join(tasks_dir, "active")
    
    if not os.path.exists(active_dir):
        return out
        
    for path in glob.glob(os.path.join(active_dir, "*.json")):
        try:
            changed, data, sr = scan_file(path, grace=grace)
            out.changed_files += sr.changed_files
            out.overdue_tasks += sr.overdue_tasks
            out.reset_to_pending += sr.reset_to_pending
            out.blocked_projects += sr.blocked_projects
            out.task_details.extend(sr.task_details)
            out.blocked_projects_info.extend(sr.blocked_projects_info)
            
            if changed:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[{now_iso()}] Error processing {path}: {e}", file=sys.stderr, flush=True)
            
    return out


def build_alert_message(sr: ScanResult) -> str:
    """构建发送给主 Agent 的告警消息"""
    lines = [
        "🚨 Team Dispatch Watcher 告警",
        "",
        f"扫描时间: {now_iso()}",
        f"超时任务: {sr.overdue_tasks} 个",
        f"已重置: {sr.reset_to_pending} 个（将重新派发）",
        f"阻塞项目: {sr.blocked_projects} 个（重试耗尽）",
        ""
    ]
    
    if sr.task_details:
        lines.append("📋 任务详情:")
        lines.append("")
        
        for task in sr.task_details:
            status_emoji = "🔄" if task.status == "reset_to_pending" else "❌"
            lines.append(f"{status_emoji} [{task.project}] {task.task_id}")
            lines.append(f"   Agent: {task.agent_id}")
            lines.append(f"   描述: {task.description}")
            lines.append(f"   状态: {task.status} (重试: {task.retries}/{task.retry_limit})")
            if task.error:
                lines.append(f"   错误: {task.error}")
            if task.depends_on:
                lines.append(f"   依赖: {', '.join(task.depends_on)}")
            lines.append("")
    
    if sr.blocked_projects_info:
        lines.append("🚫 阻塞项目详情:")
        lines.append("")
        for info in sr.blocked_projects_info:
            lines.append(f"项目: {info['project']}")
            lines.append(f"失败任务: {info['failed_tasks']}/{info['total_tasks']}")
            for bt in info['blocked_tasks']:
                lines.append(f"  - {bt['id']} ({bt['agent']}): {bt['description'][:100]}")
            lines.append("")
    
    lines.append("💡 建议操作:")
    if sr.reset_to_pending > 0:
        lines.append("- 已重置的任务将在下次调度时自动重新派发")
    if sr.blocked_projects > 0:
        lines.append("- 阻塞项目需要人工干预：检查失败原因或调整 retryLimit")
        lines.append("- 使用 `openclaw sessions list` 查看子 Agent 状态")
    
    return "\n".join(lines)


def send_event_to_main_agent(message: str) -> bool:
    """发送事件给主 Agent
    
    尝试多种方式（按优先级）：
    1. openclaw sessions send --agent main（如果 main agent 存在）
    2. 写入 .team-dispatch-alert 文件（fallback）
    """
    # 方式1: 尝试直接发送给 main agent
    try:
        result = subprocess.run(
            ["openclaw", "agents", "list", "--json"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            agents = json.loads(result.stdout)
            has_main = any(a.get("id") == "main" for a in agents)
            
            if has_main:
                # 发送给 main agent
                send_result = subprocess.run(
                    ["openclaw", "sessions", "send", "--agent", "main", "--message", message],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if send_result.returncode == 0:
                    print(f"[{now_iso()}] ✅ 已发送事件给 main agent")
                    return True
    except Exception as e:
        print(f"[{now_iso()}] 直接发送失败: {e}", file=sys.stderr, flush=True)
    
    # 方式2: fallback 到文件
    try:
        alert_file = os.path.expanduser("~/.openclaw/workspace/.team-dispatch-alert")
        alert_data = {
            "timestamp": now_iso(),
            "source": "watcher",
            "type": "anomaly_detected",
            "message": message,
            "requires_action": True
        }
        with open(alert_file, "w", encoding="utf-8") as f:
            json.dump(alert_data, f, ensure_ascii=False, indent=2)
        print(f"[{now_iso()}] 📝 已写入告警文件: {alert_file}")
        return True
    except Exception as e:
        print(f"[{now_iso()}] 写入文件失败: {e}", file=sys.stderr, flush=True)
        return False


def notify_main_agent(sr: ScanResult) -> None:
    """通知主 Agent（带详细上下文）"""
    if sr.overdue_tasks == 0 and sr.blocked_projects == 0:
        return
        
    message = build_alert_message(sr)
    send_event_to_main_agent(message)


def main() -> None:
    ap = argparse.ArgumentParser(description="Team Dispatch Watcher")
    ap.add_argument("--tasks-dir", default=os.path.expanduser("~/.openclaw/workspace/tasks"),
                    help="任务目录路径")
    ap.add_argument("--interval", type=int, default=60, 
                    help="扫描间隔（秒）")
    ap.add_argument("--grace", type=int, default=15,
                    help="超时宽限期（秒）")
    ap.add_argument("--once", action="store_true",
                    help="只运行一次然后退出")
    ap.add_argument("--notify", action="store_true", default=True,
                    help="检测到异常时通知主 Agent")
    ap.add_argument("--no-notify", dest="notify", action="store_false",
                    help="禁用通知")
    args = ap.parse_args()

    interval = max(10, args.interval)

    def sleep_s() -> int:
        # 自适应间隔：有变化时快一点，无变化时慢一点
        return max(10, int(interval * (0.6 + random.random() * 0.6)))

    print(f"[{now_iso()}] Watcher 启动 | interval={interval}s grace={args.grace}s notify={args.notify}")

    while True:
        sr = scan_once(args.tasks_dir, grace=args.grace)
        
        # 静默模式：只有异常时才输出和通知
        if sr.overdue_tasks > 0 or sr.blocked_projects > 0 or sr.reset_to_pending > 0:
            print(
                f"[{now_iso()}] 检测到异常: changed={sr.changed_files} "
                f"overdue={sr.overdue_tasks} reset={sr.reset_to_pending} "
                f"blocked={sr.blocked_projects}",
                flush=True
            )
            
            if args.notify:
                notify_main_agent(sr)
        
        if args.once:
            break
            
        time.sleep(sleep_s())


if __name__ == "__main__":
    main()
