#!/usr/bin/env python3
"""
Analyze and visualize a task hierarchy graph.

Usage:
    python analyze-task-graph.py <task-stack.json>
    python analyze-task-graph.py <task-stack.json> --format dot > graph.dot
    python analyze-task-graph.py <task-stack.json> --format ascii
"""

import json
import sys
from typing import Any


STATUS_SYMBOLS = {
    'pending': '○',
    'in_progress': '◐',
    'complete': '✓',
    'failed': '✗',
    'skipped': '⊘',
    'blocked': '⊙',
}

STATUS_COLORS = {
    'pending': 'gray',
    'in_progress': 'yellow',
    'complete': 'green',
    'failed': 'red',
    'skipped': 'lightgray',
    'blocked': 'orange',
}


def flatten_tasks(task_stack: dict) -> list[dict]:
    """Flatten the task tree into a list."""
    tasks = []
    
    def collect(task_list: list, parent_id: str | None = None):
        for task in task_list:
            task['_parent_id'] = parent_id
            tasks.append(task)
            if 'subtasks' in task:
                collect(task['subtasks'], task.get('id'))
    
    collect(task_stack.get('tasks', []))
    return tasks


def analyze_stats(tasks: list[dict]) -> dict:
    """Calculate statistics about the task graph."""
    stats = {
        'total': len(tasks),
        'by_status': {},
        'max_depth': 0,
        'avg_subtasks': 0,
        'blocked_count': 0,
    }
    
    # Count by status
    for task in tasks:
        status = task.get('status', 'pending')
        stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
    
    # Calculate depth
    def depth(task_id: str, all_tasks: dict[str, dict]) -> int:
        task = all_tasks.get(task_id)
        if not task or not task.get('_parent_id'):
            return 0
        return 1 + depth(task['_parent_id'], all_tasks)
    
    task_map = {t.get('id'): t for t in tasks if t.get('id')}
    for task in tasks:
        d = depth(task.get('id'), task_map)
        stats['max_depth'] = max(stats['max_depth'], d)
    
    # Average subtasks
    parent_tasks = [t for t in tasks if 'subtasks' in t and t['subtasks']]
    if parent_tasks:
        stats['avg_subtasks'] = sum(len(t['subtasks']) for t in parent_tasks) / len(parent_tasks)
    
    return stats


def render_ascii(task_stack: dict) -> str:
    """Render task graph as ASCII tree."""
    lines = []
    
    def render_task(task: dict, indent: int = 0, last: bool = True):
        prefix = '    ' * indent
        branch = '└── ' if last else '├── '
        if indent > 0:
            prefix = '│   ' * (indent - 1) + branch
        
        status = task.get('status', 'pending')
        symbol = STATUS_SYMBOLS.get(status, '?')
        title = task.get('title', 'Untitled')
        
        lines.append(f"{prefix}{symbol} {title}")
        
        subtasks = task.get('subtasks', [])
        for i, subtask in enumerate(subtasks):
            render_task(subtask, indent + 1, i == len(subtasks) - 1)
    
    for i, task in enumerate(task_stack.get('tasks', [])):
        render_task(task, 0, i == len(task_stack.get('tasks', [])) - 1)
    
    return '\n'.join(lines)


def render_dot(task_stack: dict) -> str:
    """Render task graph as DOT format for Graphviz."""
    lines = [
        'digraph TaskGraph {',
        '    rankdir=TB;',
        '    node [shape=box, style=filled];',
        '',
    ]
    
    def add_node(task: dict):
        task_id = task.get('id', 'unknown')
        title = task.get('title', 'Untitled').replace('"', '\\"')
        status = task.get('status', 'pending')
        color = STATUS_COLORS.get(status, 'white')
        
        lines.append(f'    "{task_id}" [label="{title}", fillcolor={color}];')
        
        for subtask in task.get('subtasks', []):
            subtask_id = subtask.get('id', 'unknown')
            lines.append(f'    "{task_id}" -> "{subtask_id}";')
            add_node(subtask)
    
    for task in task_stack.get('tasks', []):
        add_node(task)
    
    lines.append('}')
    return '\n'.join(lines)


def render_json_summary(task_stack: dict, stats: dict) -> str:
    """Render summary as JSON."""
    return json.dumps({
        'stats': stats,
        'activeTaskId': task_stack.get('activeTaskId'),
    }, indent=2)


def main():
    if len(sys.argv) < 2:
        print("Usage: analyze-task-graph.py <task-stack.json> [--format ascii|dot|json]", file=sys.stderr)
        sys.exit(1)
    
    with open(sys.argv[1]) as f:
        task_stack = json.load(f)
    
    # Parse format
    fmt = 'ascii'
    if '--format' in sys.argv:
        idx = sys.argv.index('--format')
        if idx + 1 < len(sys.argv):
            fmt = sys.argv[idx + 1]
    
    tasks = flatten_tasks(task_stack)
    stats = analyze_stats(tasks)
    
    if fmt == 'dot':
        print(render_dot(task_stack))
    elif fmt == 'json':
        print(render_json_summary(task_stack, stats))
    else:
        # ASCII output with stats
        print("Task Graph")
        print("=" * 40)
        print(render_ascii(task_stack))
        print()
        print("Statistics")
        print("-" * 40)
        print(f"Total tasks: {stats['total']}")
        print(f"Max depth: {stats['max_depth']}")
        print(f"Avg subtasks: {stats['avg_subtasks']:.1f}")
        print()
        print("By status:")
        for status, count in sorted(stats['by_status'].items()):
            symbol = STATUS_SYMBOLS.get(status, '?')
            print(f"  {symbol} {status}: {count}")
        
        if task_stack.get('activeTaskId'):
            print()
            print(f"Active: {task_stack['activeTaskId']}")


if __name__ == '__main__':
    main()
