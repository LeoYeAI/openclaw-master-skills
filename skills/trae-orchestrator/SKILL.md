---
name: "trae-orchestrator"
description: "Orchestrates TRAE IDE for automated software development with multi-agent collaboration. Invoke when user wants to develop software using TRAE or needs automated project management."
---

# TRAE Orchestrator

Automated software development controller that orchestrates TRAE IDE for fully autonomous project delivery.

## When to Invoke

- User wants to develop software using TRAE
- User needs automated project management
- User provides software requirements and project directory
- User asks for multi-agent development workflow
- User wants to automate TRAE with Python scripts

## Quick Start (Recommended)

### One-Line Project Launch

```python
from automation_helper import quick_start

# 一键启动项目
quick_start(
    project_dir='D:\\MyProject',
    requirements={
        'name': '我的项目',
        'description': '项目描述...',
        'features': ['功能1', '功能2'],
        'tech_stack': 'Node.js + React'
    }
)
```

This will:
1. ✅ Create project structure
2. ✅ Create requirements.md
3. ✅ Create prompt for TRAE
4. ✅ Launch TRAE IDE
5. ✅ Send development task to TRAE

## Automation Helper Module

A practical Python module (`automation_helper.py`) is provided for easy automation:

### TRAEController - IDE Controller

```python
from automation_helper import TRAEController

# Initialize (auto-detects TRAE path)
controller = TRAEController()
# Or specify path
controller = TRAEController('E:\\software\\Trae CN\\Trae CN.exe')

# First-time setup
controller.setup('E:\\software\\Trae CN\\Trae CN.exe')

# Launch TRAE with project
controller.launch('D:\\MyProject')

# Send prompt (requires pyautogui)
controller.send_prompt("Create a web app...", delay=5)
```

### ProjectManager - Project Setup

```python
from automation_helper import ProjectManager

# Create project structure
ProjectManager.create_project(
    project_dir='D:\\MyProject',
    requirements={
        'name': '星空篝火游戏',
        'description': '多人联机游戏',
        'features': ['3D场景', '多人联机', '聊天系统'],
        'tech_stack': 'Three.js + Node.js'
    }
)

# Create prompt for TRAE
ProjectManager.create_prompt('D:\\MyProject')
```

### ProgressMonitor - Monitor Progress

```python
from automation_helper import ProgressMonitor

# Monitor project progress
monitor = ProgressMonitor('D:\\MyProject')

# Check signals
if monitor.check_signal('project_done'):
    print("Project complete!")

# Get status summary
status = monitor.get_status()
print(status)

# Wait for completion
monitor.wait_for_completion(timeout=3600)  # 1 hour timeout
```

### User Control Functions

```python
from automation_helper import pause_project, resume_project, stop_project

pause_project('D:\\MyProject')   # Pause
resume_project('D:\\MyProject')  # Resume
stop_project('D:\\MyProject')    # Stop
```

## Token Optimization Strategy

### CRITICAL: Minimize openclaw Token Usage

| openclaw Does | TRAE Does (Free) |
|---------------|------------------|
| Orchestrate workflow | All code generation |
| Read only: task_plan.md, progress.md | Read/write all source files |
| Send prompts | Execute prompts |
| Detect completion | Self-check quality |
| Intervene on loops | Auto-fix bugs (3 attempts) |

### Event-Driven Completion Detection (No Polling!)

**DO NOT poll every 30 seconds.** Use these efficient methods:

#### Method 1: Signal File (Most Efficient)

TRAE creates a signal file when done - openclaw only checks if file exists:

```
# In prompt, instruct TRAE:
"When phase complete, create file: .trae-docs/.signal_{PHASE}_DONE"

# openclaw checks:
if os.path.exists('.trae-docs/.signal_planning_done'):
    # Phase complete, read progress.md once
    # Delete signal file after reading
```

**Token cost: 0** (file existence check is free)

#### Method 2: File Modification Time

Only read when timestamp changes:

```python
last_mtime = 0

def check_progress():
    global last_mtime
    current_mtime = os.path.getmtime('.trae-docs/progress.md')
    if current_mtime > last_mtime:
        last_mtime = current_mtime
        return read_file('.trae-docs/progress.md')
    return None  # No change, don't read
```

**Token cost: 0** until file actually changes

#### Method 3: Watchdog File Monitor (Background)

Use filesystem events instead of polling:

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ProgressHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if 'progress.md' in event.src_path:
            # File changed, now read it
            content = read_file(event.src_path)
            process_status(content)

observer = Observer()
observer.schedule(ProgressHandler(), path='.trae-docs/')
observer.start()
```

**Token cost: 0** until file changes, then only 1 read

### Recommended: Signal File + Timestamp Combo

```
┌─────────────────────────────────────────────────────────┐
│  TRAE completes task                                    │
│       ↓                                                 │
│  TRAE creates .signal_done (empty file)                 │
│       ↓                                                 │
│  openclaw detects signal file exists (0 tokens)         │
│       ↓                                                 │
│  openclaw reads progress.md once                        │
│       ↓                                                 │
│  openclaw deletes signal file                           │
│       ↓                                                 │
│  openclaw sends next prompt                             │
└─────────────────────────────────────────────────────────┘
```

## First-Time Setup

### Step 1: Get TRAE Installation Path

```
Ask user: "Please provide the TRAE installation directory path"
Example: "C:\Users\XXX\AppData\Local\Programs\Trae CN"
```

### Step 2: Verify and Save

1. Check if directory contains `Trae CN.exe`
2. Launch TRAE to verify it works
3. Save to `config.json`:
```json
{
  "trae_install_path": "USER_PROVIDED_PATH",
  "trae_executable": "Trae CN.exe",
  "window_identifier": "Trae CN",
  "max_instances": 3,
  "version": "1.0.0"
}
```

## Project Structure

```
{project_dir}/
├── .trae-docs/
│   ├── requirements.md    # User requirements
│   ├── architecture.md    # System design
│   ├── task_plan.md       # Development plan
│   ├── progress.md        # Current status (openclaw reads this)
│   └── review_log.md      # Review history
└── src/                   # Generated code (TRAE manages)
```

## Super-Efficient Workflow

### Phase 1: Planning (One Prompt)

**Send single comprehensive prompt:**

```
Develop [SOFTWARE_TYPE] with these requirements:

[REQUIREMENTS]

Tech stack: [TECHNOLOGIES]

INSTRUCTIONS:
1. Create .trae-docs/architecture.md with system design
2. Create .trae-docs/task_plan.md with task breakdown
3. Create .trae-docs/progress.md with initial status
4. Each task must be completable within 200k tokens
5. Include acceptance criteria for each task
6. Mark task dependencies clearly

COMPLETION SIGNAL:
When done, create empty file: .trae-docs/.signal_planning_done
Also update progress.md with:
STATUS: PLANNING_COMPLETE
TASKS_TOTAL: N
ESTIMATED_TOKENS: N

Use SOLO mode. Work autonomously.
```

**Detection:** Check if `.signal_planning_done` exists (0 tokens), then read `progress.md` once.

### Phase 2: Batch Implementation

**Send tasks in batches (not one by one):**

```
BATCH IMPLEMENTATION - Tasks [START_ID] to [END_ID]

Read .trae-docs/task_plan.md for task details.

For each task:
1. Implement following architecture.md
2. Write unit tests
3. Update progress.md with completion status
4. Mark task as [x] in task_plan.md

COMPLETION SIGNAL:
After ALL tasks in batch:
1. Create empty file: .trae-docs/.signal_batch_[N]_done
2. Update progress.md with:
   STATUS: BATCH_[N]_COMPLETE
   COMPLETED_TASKS: [IDs]
   REMAINING_TASKS: [IDs]

Work autonomously in SOLO mode.
```

**Detection:** Check if `.signal_batch_N_done` exists (0 tokens), then read `progress.md` once.

### Phase 3: Self-Review

**Let TRAE review itself:**

```
SELF-REVIEW PHASE

Review all implemented code:
1. Check against requirements.md
2. Run all tests
3. Check code quality
4. Document issues in review_log.md

If issues found:
- Fix them automatically
- Re-run tests
- Update review_log.md

COMPLETION SIGNAL:
When done, create empty file: .trae-docs/.signal_review_done
Also update progress.md with:
STATUS: REVIEW_COMPLETE
ISSUES_FOUND: N
ISSUES_FIXED: N

If blocked, create: .trae-docs/.signal_blocked
And update progress.md with:
STATUS: BLOCKED
BLOCKER: [description]
```

**Detection:** Check if `.signal_review_done` or `.signal_blocked` exists (0 tokens), then read `progress.md` once.

## Minimal Intervention Protocol

### Intervention Triggers (Signal-Based)

| Signal File | Action |
|-------------|--------|
| `.signal_blocked` | Read blocker description, provide guidance |
| `.signal_need_clarification` | Ask user for input |
| `.signal_error_loop` | Read error log, send new approach |
| `.signal_context_full` | Start new conversation with checkpoint |

### No Intervention Needed When

- No signal files present (TRAE is working)
- `.signal_batch_N_done` exists (normal progress)
- Files are being modified (active development)

### Timeout Fallback

Only if no signal file and no file changes for 10+ minutes:

```python
# Last resort check
if no_signal_files() and file_age('progress.md') > 600:
    # Check TRAE window state
    screenshot = capture_trae_window()
    if "产物汇总" in screenshot:
        # TRAE finished but forgot signal
        create_signal_file('.signal_done')
    elif is_idle(screenshot):
        # TRAE is stuck
        create_signal_file('.signal_blocked')
```

## Error Handling

### Bug-Fix Loop (3+ attempts detected via .signal_error_loop)

```
ALTERNATIVE APPROACH for [BUG_ID]

Previous attempts failed. Try:
1. [DIFFERENT_APPROACH]
2. Consider: [ALTERNATIVE_SOLUTION]
3. If still fails after 3 more attempts:
   - Create .signal_blocked
   - Update progress.md with BLOCKER description

Start fresh. Do not reference previous attempts.

COMPLETION SIGNAL:
- Success: Create .signal_fixed_[BUG_ID]
- Failed: Create .signal_blocked
```

### Context Overflow (TRAE handles automatically)

Include in initial prompt:
```
CONTEXT MANAGEMENT:
- Monitor token usage
- When approaching 200k tokens:
  1. Create checkpoint summary in progress.md
  2. Create .signal_context_full
  3. List remaining tasks
  4. Note partial implementations
```

When openclaw detects `.signal_context_full`:
```
Start new TRAE conversation with:
"Continue from checkpoint. Read progress.md for context.
Remaining tasks: [LIST]
Resume from: [LAST_COMPLETED_TASK]"
```

## Multi-Agent Strategy

### When to Use Multiple TRAE Windows

| Project Size | Strategy |
|--------------|----------|
| Small (<10 tasks) | Single TRAE instance |
| Medium (10-30 tasks) | 2 instances: Planner+Coder, Reviewer |
| Large (>30 tasks) | 3 instances: Planner, Coder, Reviewer |

### Parallel Execution

For large projects, run Coder and Reviewer in parallel:
```
Window 1 (Coder): Implement tasks 1-5
Window 2 (Reviewer): Review completed tasks
```

## Progress File Format

TRAE updates `progress.md` - openclaw only reads this file:

```markdown
# Project Progress

## Status: [PLANNING|IMPLEMENTING|REVIEWING|COMPLETE|BLOCKED]

## Current Phase: [Phase Name]

## Completed Tasks: [ID1, ID2, ...]

## Remaining Tasks: [ID1, ID2, ...]

## Issues:
- [Issue 1]
- [Issue 2]

## Blockers:
- [Blocker description] (if STATUS: BLOCKED)

## Last Updated: [TIMESTAMP]
```

## Quality Gates (TRAE Self-Check)

Include in implementation prompts:
```
SELF-CHECK before marking task complete:
- [ ] Code compiles without errors
- [ ] All tests pass
- [ ] No linting errors
- [ ] Documentation updated
- [ ] progress.md updated
```

## Prompt Templates (Token-Efficient)

### Planning
```
PLAN: [REQUIREMENTS]
STACK: [TECH]
OUTPUT: .trae-docs/{architecture.md, task_plan.md, progress.md}
SIGNAL: Create .trae-docs/.signal_planning_done when done
```

### Implementation
```
IMPLEMENT: Tasks [IDS]
PLAN: .trae-docs/task_plan.md
ARCH: .trae-docs/architecture.md
UPDATE: .trae-docs/progress.md
SIGNAL: Create .trae-docs/.signal_batch_[N]_done when done
```

### Review
```
REVIEW: All code
CHECK: .trae-docs/requirements.md
LOG: .trae-docs/review_log.md
STATUS: .trae-docs/progress.md
SIGNAL: Create .trae-docs/.signal_review_done when done
```

### Bug Fix
```
FIX: [BUG_ID]
LOG: .trae-docs/review_log.md
ATTEMPTS: [N]
NEW_APPROACH: [APPROACH]
SIGNAL: Create .trae-docs/.signal_fixed_[BUG_ID] when done
OR: Create .trae-docs/.signal_blocked if still failing
```

## Desktop Automation (Minimal)

Only needed for:
1. Launching TRAE
2. Sending initial prompt
3. Emergency intervention (timeout fallback)

```python
import os
import subprocess
import pyperclip
import pyautogui

# Launch TRAE
def launch_trae(config):
    subprocess.Popen(f"{config['trae_install_path']}\\Trae CN.exe")

# Send prompt
def send_prompt(prompt_text):
    pyperclip.copy(prompt_text)
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('enter')

# Signal file detection (0 tokens!)
def check_signal(signal_type):
    signal_path = f".trae-docs/.signal_{signal_type}"
    return os.path.exists(signal_path)

# Clean up signal after handling
def clear_signal(signal_type):
    signal_path = f".trae-docs/.signal_{signal_type}"
    if os.path.exists(signal_path):
        os.remove(signal_path)

# Main orchestration loop
def orchestrate():
    while True:
        if check_signal('planning_done'):
            progress = read_file('.trae-docs/progress.md')
            # Process and send next prompt
            clear_signal('planning_done')
            send_prompt(implementation_prompt)
            
        elif check_signal('blocked'):
            blocker = read_file('.trae-docs/progress.md')
            # Analyze and provide guidance
            clear_signal('blocked')
            send_prompt(guidance_prompt)
            
        elif check_signal('project_done'):
            # Project complete!
            break
            
        # Sleep to avoid CPU usage (no token cost)
        time.sleep(1)
```

## Self-Update

Log in `execution_log.json`:
```json
{
  "executions": [{
    "timestamp": "ISO_DATE",
    "project": "NAME",
    "tasks": N,
    "interventions": N,
    "token_saved_estimate": N
  }]
}
```

## Quick Reference

| openclaw Action | Trigger |
|-----------------|---------|
| Check signal file | Continuous (0 tokens) |
| Read progress.md | Only when signal file exists |
| Read task_plan.md | Once per phase |
| Send prompt | Once per phase/batch |
| Intervene | Only on BLOCKED/loop |

| TRAE Action | Trigger |
|-------------|---------|
| Generate code | Continuous |
| Create signal file | When phase done |
| Update progress.md | After each task |
| Self-check quality | After each task |
| Handle errors | Automatic (3 attempts) |

## Signal File Naming Convention

| Phase | Signal File |
|-------|-------------|
| Planning | `.signal_planning_done` |
| Batch N | `.signal_batch_N_done` |
| Review | `.signal_review_done` |
| Complete | `.signal_project_done` |
| Blocked | `.signal_blocked` |

## User Control Mechanism

### Control Signals (User-Initiated)

| User Action | Signal File | Effect |
|-------------|-------------|--------|
| **Pause** | `.signal_pause` | Stop orchestration, keep TRAE running |
| **Resume** | `.signal_resume` | Continue from where paused |
| **Stop** | `.signal_stop` | Terminate project, archive progress |
| **Skip Task** | `.signal_skip_[TASK_ID]` | Skip specific task, continue next |
| **Force Complete** | `.signal_force_done` | Mark current phase as done |

### How to Use Control Signals

**Method 1: Command Line (Windows PowerShell)**

```powershell
# 暂停项目
New-Item -Path ".trae-docs\.signal_pause" -ItemType file

# 恢复项目
New-Item -Path ".trae-docs\.signal_resume" -ItemType file

# 停止项目
New-Item -Path ".trae-docs\.signal_stop" -ItemType file

# 跳过任务
New-Item -Path ".trae-docs\.signal_skip_task_3" -ItemType file

# 强制完成
New-Item -Path ".trae-docs\.signal_force_done" -ItemType file
```

**Method 2: Control Script (Recommended)**

Run the control script for easy interaction:

```powershell
# In project directory
python .trae/skills/trae-orchestrator/control.py
```

This launches an interactive menu:
```
TRAE Orchestrator Control Panel
================================
Current Status: RUNNING
Phase: Implementation
Progress: 5/15 tasks

[1] Pause Project
[2] Resume Project  
[3] Stop Project
[4] Skip Task
[5] Force Complete
[6] View Status
[7] Exit

Enter choice:
```

**Method 3: Direct Python Call**

```python
from automation_helper import pause_project, resume_project, stop_project

pause_project("./my-project")   # 暂停
resume_project("./my-project")  # 恢复
stop_project("./my-project")    # 停止
```

**Method 4: File Manager**

1. Open project folder in file explorer
2. Navigate to `.trae-docs/` folder
3. Create new text file, rename to `.signal_pause` (remove .txt extension)
4. Confirm extension change

### Orchestration Loop with Control

```python
def orchestrate(project_dir=".", handlers=None):
    while True:
        # 1. Check control signals FIRST
        if check_signal('stop', project_dir):
            archive_progress(project_dir)
            return False, "Project stopped by user"
        
        if check_signal('pause', project_dir):
            # Wait for resume signal
            while not check_signal('resume', project_dir):
                if check_signal('stop', project_dir):
                    return False, "Project stopped during pause"
                time.sleep(5)
            clear_signal('resume', project_dir)
            clear_signal('pause', project_dir)
        
        # 2. Check skip signals
        for skip_signal in get_skip_signals(project_dir):
            task_id = skip_signal.replace('skip_', '')
            mark_task_skipped(task_id, project_dir)
            clear_signal(skip_signal, project_dir)
        
        # 3. Check force complete
        if check_signal('force_done', project_dir):
            clear_signal('force_done', project_dir)
            # Move to next phase
            send_next_prompt()
        
        # 4. Normal signal processing
        signals = get_all_signals(project_dir)
        # ... rest of orchestration
```

### Pause Behavior

When `.signal_pause` is detected:

```
┌─────────────────────────────────────────────────────────┐
│  openclaw detects .signal_pause                         │
│       ↓                                                 │
│  Stop sending new prompts                               │
│       ↓                                                 │
│  Keep TRAE running (finish current task)                │
│       ↓                                                 │
│  Wait for .signal_resume or .signal_stop                │
│       ↓                                                 │
│  Resume: Continue from last checkpoint                  │
│  Stop: Archive and terminate                            │
└─────────────────────────────────────────────────────────┘
```

### Stop Behavior

When `.signal_stop` is detected:

```
┌─────────────────────────────────────────────────────────┐
│  openclaw detects .signal_stop                          │
│       ↓                                                 │
│  Create final progress snapshot                         │
│       ↓                                                 │
│  Archive .trae-docs/ to .trae-archive/[timestamp]/      │
│       ↓                                                 │
│  Clear all signal files                                 │
│       ↓                                                 │
│  Return control to user                                 │
└─────────────────────────────────────────────────────────┘
```

### Status File for User Visibility

openclaw maintains `.trae-docs/orchestrator_status.md`:

```markdown
# Orchestrator Status

## State: [RUNNING|PAUSED|STOPPED|WAITING]

## Last Action: [timestamp] - [action description]

## Next Action: [what will happen next]

## User Controls Available:
- Pause: Create .signal_pause
- Resume: Create .signal_resume (when paused)
- Stop: Create .signal_stop

## Current Progress:
- Phase: [phase name]
- Completed: N tasks
- Remaining: M tasks
```

### Quick Commands for Users

```powershell
# Check status
cat .trae-docs\orchestrator_status.md

# Or use control panel (recommended)
python .trae\skills\trae-orchestrator\control.py

# Quick commands
New-Item -Path ".trae-docs\.signal_pause" -ItemType file      # Pause
New-Item -Path ".trae-docs\.signal_resume" -ItemType file     # Resume
New-Item -Path ".trae-docs\.signal_stop" -ItemType file       # Stop
New-Item -Path ".trae-docs\.signal_skip_task_3" -ItemType file # Skip task 3
New-Item -Path ".trae-docs\.signal_force_done" -ItemType file # Force complete
```

## Complete Workflow Example

Here's a complete example of using the automation helper:

```python
#!/usr/bin/env python3
"""
完整示例：使用 TRAE 自动化开发一个项目
"""
from automation_helper import (
    TRAEController, 
    ProjectManager, 
    ProgressMonitor,
    quick_start,
    pause_project,
    stop_project
)

# ========== 方法 1: 一键快速启动 ==========
def method1_quick_start():
    """最简单的方式"""
    quick_start(
        project_dir='D:\\MyGame',
        requirements={
            'name': '星空篝火游戏',
            'description': '一个多人联机的3D篝火游戏',
            'features': [
                '3D星空场景',
                '多人联机',
                '聊天系统',
                '篝火效果'
            ],
            'tech_stack': 'Three.js + Node.js + Socket.io'
        },
        trae_path='E:\\software\\Trae CN\\Trae CN.exe'  # 可选，自动查找
    )

# ========== 方法 2: 分步控制 ==========
def method2_step_by_step():
    """更精细的控制"""
    
    # 1. 创建项目
    ProjectManager.create_project(
        project_dir='D:\\MyGame',
        requirements="""
# 星空篝火游戏

## 描述
创建一个多人联机的3D篝火游戏

## 功能
- 3D星空场景
- 多人联机
- 聊天系统
"""
    )
    
    # 2. 创建自定义提示
    custom_prompt = """
请开发一个星空篝火游戏。

要求：
1. 使用 Three.js 创建3D场景
2. 使用 Socket.io 实现多人联机
3. 包含星空、篝火、玩家角色
4. 实现移动、聊天、互动功能

完成后创建 .trae-docs/.signal_project_done
"""
    ProjectManager.create_prompt('D:\\MyGame', custom_prompt)
    
    # 3. 启动 TRAE
    controller = TRAEController('E:\\software\\Trae CN\\Trae CN.exe')
    controller.launch('D:\\MyGame')
    
    # 4. 发送提示
    controller.send_prompt(custom_prompt, delay=5)

# ========== 方法 3: 监控进度 ==========
def method3_monitor():
    """监控开发进度"""
    monitor = ProgressMonitor('D:\\MyGame')
    
    # 检查当前状态
    status = monitor.get_status()
    print(f"当前状态: {status}")
    
    # 等待完成（带超时）
    completed = monitor.wait_for_completion(timeout=3600)
    
    if completed:
        print("✅ 项目开发完成！")
    else:
        print("⚠️ 项目未完成或被阻塞")

# ========== 运行 ==========
if __name__ == '__main__':
    # 选择方法
    method1_quick_start()  # 最简单
    # method2_step_by_step()  # 更灵活
    # method3_monitor()  # 仅监控
```

## File Creation Strategy

### How to Teach TRAE to Create Files

**Method 1: Pre-create Requirements (Recommended)**

Create `requirements.md` BEFORE starting TRAE:

```python
from automation_helper import ProjectManager

ProjectManager.create_project(
    project_dir='D:\\MyProject',
    requirements={
        'name': 'My App',
        'description': 'An awesome application',
        'features': ['Feature 1', 'Feature 2'],
        'tech_stack': 'React + Node.js'
    }
)
```

This creates:
- `.trae-docs/requirements.md` - TRAE reads this
- `.trae-docs/prompt_to_trape.md` - Instructions for TRAE

Then TRAE will:
1. Read `requirements.md`
2. Create `architecture.md`
3. Create `task_plan.md`
4. Create actual code files

**Method 2: Include File List in Prompt**

```
Create the following files:
1. src/index.js - Entry point
2. src/components/App.js - Main component
3. src/styles.css - Styles
4. package.json - Dependencies

Use this structure:
```
my-app/
├── src/
│   ├── index.js
│   ├── components/
│   │   └── App.js
│   └── styles.css
└── package.json
```
```

**Method 3: Phase-Based Creation**

```
PHASE 1 - Setup:
- Create package.json
- Create folder structure

PHASE 2 - Core:
- Create src/index.js
- Create src/app.js

PHASE 3 - UI:
- Create src/components/
- Create src/styles/
```

## Dependencies

### Required
- Python 3.7+
- TRAE IDE installed

### Optional (for auto-send)
```bash
pip install pyautogui pyperclip
```

Without these, you need to manually paste the prompt into TRAE.

## Troubleshooting

### TRAE Not Found
```python
from automation_helper import TRAEController

controller = TRAEController()
controller.setup('E:\\software\\Trae CN\\Trae CN.exe')  # 手动设置路径
```

### Permission Denied
Run Python as Administrator or check TRAE path permissions.

### Prompt Not Sent
Install pyautogui:
```bash
pip install pyautogui pyperclip
```

Or manually copy from `.trae-docs/prompt_to_trape.md` and paste into TRAE.

---

**Core Principle**: Event-driven orchestration. TRAE signals completion, openclaw responds. User controls via signal files. Zero polling, zero wasted tokens.

**New in this version**: Practical Python automation module (`automation_helper.py`) for one-line project launch and easy control.
