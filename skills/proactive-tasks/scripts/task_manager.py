#!/usr/bin/env python3
"""
Proactive Task Manager v1.2.0
Enables AI agents to manage goals and work autonomously on tasks.
Includes Phase 2: WAL, SESSION-STATE, working buffer, self-healing.
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any
import uuid

# Data file location
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
DATA_FILE = DATA_DIR / "tasks.json"
PROJECT_ROOT = SCRIPT_DIR.parent
WORKSPACE_ROOT = PROJECT_ROOT.parent.parent
MEMORY_DIR = WORKSPACE_ROOT / "memory"
SESSION_STATE_FILE = WORKSPACE_ROOT / "SESSION-STATE.md"
WORKING_BUFFER_FILE = MEMORY_DIR / "working-buffer.md"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
MEMORY_DIR.mkdir(exist_ok=True)

def load_data() -> Dict[str, Any]:
    """Load tasks data from JSON file."""
    if not DATA_FILE.exists():
        return {"goals": [], "tasks": []}
    
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data: Dict[str, Any]) -> None:
    """Save tasks data to JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def generate_id(prefix: str) -> str:
    """Generate a unique ID."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def find_goal_by_title(data: Dict[str, Any], title: str) -> Optional[Dict]:
    """Find a goal by title (case-insensitive partial match)."""
    title_lower = title.lower()
    for goal in data["goals"]:
        if title_lower in goal["title"].lower():
            return goal
    return None

def find_task_by_id(data: Dict[str, Any], task_id: str) -> Optional[Dict]:
    """Find a task by ID."""
    for task in data["tasks"]:
        if task["id"] == task_id:
            return task
    return None

def get_task_dependencies_met(data: Dict[str, Any], task: Dict) -> bool:
    """Check if all task dependencies are completed."""
    if "depends_on" not in task or not task["depends_on"]:
        return True
    
    for dep_id in task["depends_on"]:
        dep_task = find_task_by_id(data, dep_id)
        if not dep_task or dep_task["status"] != "completed":
            return False
    
    return True

def add_goal(args) -> None:
    """Add a new goal."""
    data = load_data()
    
    goal = {
        "id": generate_id("goal"),
        "title": args.title,
        "priority": args.priority,
        "context": args.context or "",
        "created_at": datetime.now(timezone.utc).isoformat() + "Z",
        "status": args.status
    }
    
    data["goals"].append(goal)
    save_data(data)
    
    print(json.dumps({"success": True, "goal": goal}, indent=2))

def add_task(args) -> None:
    """Add a task to a goal."""
    data = load_data()
    
    # Find the goal
    goal = find_goal_by_title(data, args.goal_title)
    if not goal:
        print(json.dumps({"success": False, "error": f"Goal not found: {args.goal_title}"}), file=sys.stderr)
        sys.exit(1)
    
    task = {
        "id": generate_id("task"),
        "goal_id": goal["id"],
        "title": args.task_title,
        "priority": args.priority or goal["priority"],
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat() + "Z",
        "notes": ""
    }
    
    if args.depends_on:
        task["depends_on"] = args.depends_on.split(",")
    
    if args.estimate:
        task["estimate_minutes"] = args.estimate
    
    data["tasks"].append(task)
    save_data(data)
    
    print(json.dumps({"success": True, "task": task}, indent=2))

def next_task(args) -> None:
    """Get the next task to work on."""
    data = load_data()
    
    # Filter pending tasks
    candidates = [
        task for task in data["tasks"]
        if task["status"] == "pending" and get_task_dependencies_met(data, task)
    ]
    
    # Apply goal filter if specified
    if args.goal:
        candidates = [t for t in candidates if t["goal_id"] == args.goal]
    
    # Apply time estimate filter if specified
    if args.max_estimate:
        candidates = [
            t for t in candidates
            if "estimate_minutes" in t and t["estimate_minutes"] <= args.max_estimate
        ]
    
    if not candidates:
        print(json.dumps({"success": True, "task": None, "message": "No tasks available"}))
        return
    
    # Sort by priority (high > medium > low)
    priority_order = {"high": 3, "medium": 2, "low": 1}
    candidates.sort(key=lambda t: priority_order.get(t["priority"], 0), reverse=True)
    
    next_task = candidates[0]
    
    # Get goal info
    goal = next((g for g in data["goals"] if g["id"] == next_task["goal_id"]), None)
    
    result = {
        "success": True,
        "task": next_task,
        "goal": goal
    }
    
    print(json.dumps(result, indent=2))

def complete_task(args) -> None:
    """Mark a task as completed."""
    data = load_data()
    
    task = find_task_by_id(data, args.task_id)
    if not task:
        print(json.dumps({"success": False, "error": f"Task not found: {args.task_id}"}), file=sys.stderr)
        sys.exit(1)
    
    task["status"] = "completed"
    task["completed_at"] = datetime.now(timezone.utc).isoformat() + "Z"
    
    if args.notes:
        task["notes"] = args.notes
    
    save_data(data)
    
    print(json.dumps({"success": True, "task": task}, indent=2))

def update_task(args) -> None:
    """Update a task."""
    data = load_data()
    
    task = find_task_by_id(data, args.task_id)
    if not task:
        print(json.dumps({"success": False, "error": f"Task not found: {args.task_id}"}), file=sys.stderr)
        sys.exit(1)
    
    if args.status:
        task["status"] = args.status
    
    if args.priority:
        task["priority"] = args.priority
    
    if args.notes:
        if task.get("notes"):
            task["notes"] += "\n" + args.notes
        else:
            task["notes"] = args.notes
    
    task["updated_at"] = datetime.now(timezone.utc).isoformat() + "Z"
    
    save_data(data)
    
    print(json.dumps({"success": True, "task": task}, indent=2))

def list_goals(args) -> None:
    """List all goals."""
    data = load_data()
    
    goals = data["goals"]
    
    if args.status:
        goals = [g for g in goals if g["status"] == args.status]
    
    if args.priority:
        goals = [g for g in goals if g["priority"] == args.priority]
    
    print(json.dumps({"success": True, "goals": goals}, indent=2))

def list_tasks(args) -> None:
    """List tasks for a goal."""
    data = load_data()
    
    goal = find_goal_by_title(data, args.goal_title)
    if not goal:
        print(json.dumps({"success": False, "error": f"Goal not found: {args.goal_title}"}), file=sys.stderr)
        sys.exit(1)
    
    tasks = [t for t in data["tasks"] if t["goal_id"] == goal["id"]]
    
    if args.status:
        tasks = [t for t in tasks if t["status"] == args.status]
    
    if args.priority:
        tasks = [t for t in tasks if t["priority"] == args.priority]
    
    print(json.dumps({"success": True, "goal": goal, "tasks": tasks}, indent=2))

def status(args) -> None:
    """Show overall status."""
    data = load_data()
    
    active_goals = [g for g in data["goals"] if g["status"] == "active"]
    
    tasks_by_status = {}
    for status_name in ["pending", "in_progress", "blocked", "needs_input", "completed"]:
        tasks_by_status[status_name] = len([t for t in data["tasks"] if t["status"] == status_name])
    
    # Recent completions (last 5)
    completed_tasks = [t for t in data["tasks"] if t["status"] == "completed"]
    completed_tasks.sort(key=lambda t: t.get("completed_at", ""), reverse=True)
    recent_completions = completed_tasks[:5]
    
    result = {
        "success": True,
        "active_goals_count": len(active_goals),
        "tasks_by_status": tasks_by_status,
        "recent_completions": recent_completions
    }
    
    print(json.dumps(result, indent=2))

# ==================== PHASE 2: WAL, SESSION-STATE, HEALTH-CHECK ====================

def log_to_wal(event_type: str, content: Dict[str, Any]) -> None:
    """Write-Ahead Logging: Log critical changes BEFORE persisting data."""
    timestamp = datetime.now(timezone.utc).isoformat()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    wal_file = MEMORY_DIR / f"WAL-{today}.log"
    
    wal_entry = {
        "timestamp": timestamp,
        "event_type": event_type,
        "content": content
    }
    
    with open(wal_file, 'a') as f:
        f.write(json.dumps(wal_entry) + "\n")


def append_to_buffer(event_type: str, details: str) -> None:
    """Append to working buffer - captures all changes during danger zone."""
    timestamp = datetime.now(timezone.utc).isoformat()
    entry = f"- {event_type} ({timestamp}): {details}\n"
    
    with open(WORKING_BUFFER_FILE, 'a') as f:
        f.write(entry)


def update_session_state(task: Dict, goal: Dict, action: str = "") -> None:
    """Update SESSION-STATE.md with current task context."""
    progress = task.get("progress", 0)
    estimate = task.get("estimate_minutes", 0)
    actual = task.get("actual_minutes", 0)
    status = task.get("status", "pending")
    
    velocity = ""
    if estimate > 0:
        ratio = actual / estimate
        if ratio < 1:
            velocity = f"{int((1 - ratio) * 100)}% faster than estimate"
        elif ratio > 1:
            velocity = f"{int((ratio - 1) * 100)}% slower than estimate"
        else:
            velocity = "on pace with estimate"
    
    content = f"""# SESSION-STATE.md - Active Working Memory
Last updated: {datetime.now(timezone.utc).isoformat()}

## Current Task
- ID: {task.get("id", "unknown")}
- Title: {task.get("title", "N/A")}
- Status: {status}
- Progress: {progress}%
- Estimated: {estimate} min
- Actual logged: {actual} min {f"({velocity})" if velocity else ""}

## Goal Context
- ID: {goal.get("id", "unknown")}
- Title: {goal.get("title", "N/A")}
- Priority: {goal.get("priority", "medium")}

## Task Details
- Created: {task.get("created_at", "N/A")}
- Updated: {task.get("updated_at", "N/A")}
- Notes: {task.get("notes", "None")}

## Blockers
- {task.get("blocked_reason", "None")}

## Next Action
{action or "Continue with current task or mark as complete"}
"""
    
    with open(SESSION_STATE_FILE, 'w') as f:
        f.write(content)


def mark_progress(args) -> None:
    """Mark task progress (0-100%) - Phase 2 enhanced."""
    data = load_data()
    task = find_task_by_id(data, args.task_id)
    
    if not task:
        print(json.dumps({"success": False, "error": f"Task not found: {args.task_id}"}), file=sys.stderr)
        sys.exit(1)
    
    old_progress = task.get("progress", 0)
    
    # WAL FIRST
    log_to_wal("PROGRESS_CHANGE", {
        "task_id": args.task_id,
        "old_progress": old_progress,
        "new_progress": args.progress,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    task["progress"] = args.progress
    task["updated_at"] = datetime.now(timezone.utc).isoformat() + "Z"
    
    if args.notes:
        if task.get("notes"):
            task["notes"] += "\n" + args.notes
        else:
            task["notes"] = args.notes
    
    if args.progress >= 100 and task.get("status") != "completed":
        task["status"] = "in_progress"
    elif args.progress > 0 and task.get("status") == "pending":
        task["status"] = "in_progress"
    
    save_data(data)
    
    goal = next((g for g in data["goals"] if g["id"] == task.get("goal_id")), None)
    if goal:
        update_session_state(task, goal, f"Progress marked: {old_progress}% → {args.progress}%")
    
    append_to_buffer("PROGRESS", f"{args.task_id}: {old_progress}% → {args.progress}%")
    
    result = {
        "success": True,
        "task": task,
        "progress_change": f"{old_progress}% → {args.progress}%"
    }
    print(json.dumps(result, indent=2))


def log_time(args) -> None:
    """Log time spent on a task - Phase 2 enhanced."""
    data = load_data()
    task = find_task_by_id(data, args.task_id)
    
    if not task:
        print(json.dumps({"success": False, "error": f"Task not found: {args.task_id}"}), file=sys.stderr)
        sys.exit(1)
    
    old_actual = task.get("actual_minutes", 0)
    new_actual = old_actual + args.minutes
    
    # WAL FIRST
    log_to_wal("TIME_LOG", {
        "task_id": args.task_id,
        "minutes_logged": args.minutes,
        "old_total": old_actual,
        "new_total": new_actual,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    task["actual_minutes"] = new_actual
    task["updated_at"] = datetime.now(timezone.utc).isoformat() + "Z"
    
    if args.notes:
        if task.get("notes"):
            task["notes"] += "\n" + args.notes
        else:
            task["notes"] = args.notes
    
    if task.get("status") == "pending" and new_actual > 0:
        task["status"] = "in_progress"
    
    save_data(data)
    
    goal = next((g for g in data["goals"] if g["id"] == task.get("goal_id")), None)
    if goal:
        update_session_state(task, goal, f"Logged {args.minutes} min (total: {new_actual} min)")
    
    append_to_buffer("TIME_LOG", f"{args.task_id}: +{args.minutes} min (total: {new_actual} min)")
    
    estimate = task.get("estimate_minutes", 0)
    velocity = ""
    if estimate > 0:
        ratio = new_actual / estimate
        if ratio < 1:
            velocity = f"{int((1 - ratio) * 100)}% faster than estimate"
        elif ratio > 1:
            velocity = f"{int((ratio - 1) * 100)}% slower than estimate"
    
    result = {
        "success": True,
        "task": task,
        "time_logged": args.minutes,
        "total_actual": new_actual,
        "estimate": estimate,
        "velocity": velocity
    }
    print(json.dumps(result, indent=2))


def mark_blocked(args) -> None:
    """Mark task as blocked - Phase 2 enhanced."""
    data = load_data()
    task = find_task_by_id(data, args.task_id)
    
    if not task:
        print(json.dumps({"success": False, "error": f"Task not found: {args.task_id}"}), file=sys.stderr)
        sys.exit(1)
    
    old_status = task.get("status", "pending")
    
    # WAL FIRST
    log_to_wal("STATUS_CHANGE", {
        "task_id": args.task_id,
        "old_status": old_status,
        "new_status": "blocked",
        "reason": args.reason,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    task["status"] = "blocked"
    task["blocked_reason"] = args.reason
    task["updated_at"] = datetime.now(timezone.utc).isoformat() + "Z"
    
    save_data(data)
    
    goal = next((g for g in data["goals"] if g["id"] == task.get("goal_id")), None)
    if goal:
        update_session_state(task, goal, f"BLOCKED: {args.reason}")
    
    append_to_buffer("BLOCKED", f"{args.task_id}: {args.reason}")
    
    result = {
        "success": True,
        "task": task,
        "status_change": f"{old_status} → blocked",
        "reason": args.reason
    }
    print(json.dumps(result, indent=2))


def health_check(args) -> None:
    """Health check: detect and report broken task states."""
    data = load_data()
    issues = []
    fixes = []
    
    for task in data["tasks"]:
        task_id = task.get("id", "unknown")
        
        if task.get("recurring") and not task.get("goal_id"):
            issues.append(f"Orphaned recurring task: {task_id}")
            task["recurring"] = None
            fixes.append(f"Removed recurring flag from {task_id}")
        
        if task.get("status") == "completed" and task.get("progress", 100) < 100:
            issues.append(f"Impossible state: {task_id} completed but progress={task.get('progress')}%")
            task["progress"] = 100
            fixes.append(f"Set progress=100% for completed task {task_id}")
        
        if task.get("status") == "completed" and not task.get("completed_at"):
            issues.append(f"Inconsistent completion: {task_id} status=completed but no completed_at")
            task["completed_at"] = datetime.now(timezone.utc).isoformat() + "Z"
            fixes.append(f"Added completed_at timestamp to {task_id}")
        
        if task.get("actual_minutes", 0) > task.get("estimate_minutes", 1) * 10:
            ratio = task.get("actual_minutes", 0) / task.get("estimate_minutes", 1)
            issues.append(f"Time anomaly: {task_id} actual={task.get('actual_minutes')}m vs estimate={task.get('estimate_minutes')}m ({ratio:.1f}x)")
        
        if task.get("status") == "completed":
            completed_at = task.get("completed_at", "")
            if completed_at > datetime.now(timezone.utc).isoformat():
                issues.append(f"Bad date: {task_id} completed_at={completed_at} is in future")
                task["completed_at"] = datetime.now(timezone.utc).isoformat() + "Z"
                fixes.append(f"Reset completed_at for {task_id}")
    
    if fixes:
        save_data(data)
    
    log_to_wal("HEALTH_CHECK", {
        "issues_found": len(issues),
        "auto_fixes_applied": len(fixes),
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    result = {
        "success": True,
        "health_status": "healthy" if not issues else "issues_found",
        "issues": issues,
        "auto_fixes": fixes,
        "summary": f"Found {len(issues)} issues, auto-fixed {len(fixes)}"
    }
    print(json.dumps(result, indent=2))


def flush_buffer(args) -> None:
    """Flush working buffer to daily memory file."""
    if not WORKING_BUFFER_FILE.exists():
        result = {
            "success": True,
            "message": "Buffer is empty, nothing to flush"
        }
        print(json.dumps(result, indent=2))
        return
    
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    daily_file = MEMORY_DIR / f"{today}.md"
    
    with open(WORKING_BUFFER_FILE, 'r') as f:
        buffer_content = f.read()
    
    section = f"\n## Task Updates\n{buffer_content}\n"
    with open(daily_file, 'a') as f:
        f.write(section)
    
    WORKING_BUFFER_FILE.write_text("")
    
    result = {
        "success": True,
        "message": f"Buffer flushed to {daily_file}",
        "lines_flushed": len(buffer_content.split('\n'))
    }
    print(json.dumps(result, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Proactive Task Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # add-goal
    parser_add_goal = subparsers.add_parser("add-goal", help="Add a new goal")
    parser_add_goal.add_argument("title", help="Goal title")
    parser_add_goal.add_argument("--priority", choices=["low", "medium", "high"], default="medium")
    parser_add_goal.add_argument("--context", help="Goal context/background")
    parser_add_goal.add_argument("--status", choices=["active", "paused", "completed"], default="active")
    
    # add-task
    parser_add_task = subparsers.add_parser("add-task", help="Add a task to a goal")
    parser_add_task.add_argument("goal_title", help="Goal title (partial match)")
    parser_add_task.add_argument("task_title", help="Task title")
    parser_add_task.add_argument("--priority", choices=["low", "medium", "high"])
    parser_add_task.add_argument("--depends-on", help="Comma-separated task IDs this depends on")
    parser_add_task.add_argument("--estimate", type=int, help="Estimated minutes to complete")
    
    # next-task
    parser_next_task = subparsers.add_parser("next-task", help="Get next task to work on")
    parser_next_task.add_argument("--goal", help="Goal ID filter")
    parser_next_task.add_argument("--max-estimate", type=int, help="Max time estimate filter")
    
    # complete-task
    parser_complete_task = subparsers.add_parser("complete-task", help="Mark task as completed")
    parser_complete_task.add_argument("task_id", help="Task ID")
    parser_complete_task.add_argument("--notes", help="Completion notes")
    
    # update-task
    parser_update_task = subparsers.add_parser("update-task", help="Update a task")
    parser_update_task.add_argument("task_id", help="Task ID")
    parser_update_task.add_argument("--status", choices=["pending", "in_progress", "blocked", "needs_input", "completed", "cancelled"])
    parser_update_task.add_argument("--priority", choices=["low", "medium", "high"])
    parser_update_task.add_argument("--notes", help="Add notes")
    
    # list-goals
    parser_list_goals = subparsers.add_parser("list-goals", help="List goals")
    parser_list_goals.add_argument("--status", choices=["active", "paused", "completed"])
    parser_list_goals.add_argument("--priority", choices=["low", "medium", "high"])
    
    # list-tasks
    parser_list_tasks = subparsers.add_parser("list-tasks", help="List tasks for a goal")
    parser_list_tasks.add_argument("goal_title", help="Goal title (partial match)")
    parser_list_tasks.add_argument("--status", choices=["pending", "in_progress", "blocked", "needs_input", "completed", "cancelled"])
    parser_list_tasks.add_argument("--priority", choices=["low", "medium", "high"])
    
    # status
    parser_status = subparsers.add_parser("status", help="Show overall status")
    
    # Phase 2 commands
    
    # mark-progress
    parser_mark_progress = subparsers.add_parser("mark-progress", help="Mark task progress (0-100%)")
    parser_mark_progress.add_argument("task_id", help="Task ID")
    parser_mark_progress.add_argument("progress", type=int, help="Progress percentage (0-100)")
    parser_mark_progress.add_argument("--notes", help="Optional notes")
    
    # log-time
    parser_log_time = subparsers.add_parser("log-time", help="Log time spent on task")
    parser_log_time.add_argument("task_id", help="Task ID")
    parser_log_time.add_argument("minutes", type=int, help="Minutes spent")
    parser_log_time.add_argument("--notes", help="Optional notes")
    
    # mark-blocked
    parser_mark_blocked = subparsers.add_parser("mark-blocked", help="Mark task as blocked")
    parser_mark_blocked.add_argument("task_id", help="Task ID")
    parser_mark_blocked.add_argument("reason", help="Reason for blocking")
    
    # health-check
    parser_health_check = subparsers.add_parser("health-check", help="Check and fix broken task states")
    
    # flush-buffer
    parser_flush_buffer = subparsers.add_parser("flush-buffer", help="Flush working buffer to daily memory")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Route to command handlers
    commands = {
        "add-goal": add_goal,
        "add-task": add_task,
        "next-task": next_task,
        "complete-task": complete_task,
        "update-task": update_task,
        "list-goals": list_goals,
        "list-tasks": list_tasks,
        "status": status,
        "mark-progress": mark_progress,
        "log-time": log_time,
        "mark-blocked": mark_blocked,
        "health-check": health_check,
        "flush-buffer": flush_buffer
    }
    
    commands[args.command](args)

if __name__ == "__main__":
    main()
