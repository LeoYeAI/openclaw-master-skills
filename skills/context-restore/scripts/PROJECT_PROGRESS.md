# Project Progress Module

## Overview

The `project_progress` module provides dynamic reading of project progress from project directories. It reads `status.json` or `.progress` files to get real-time project status, milestones, and completion percentage.

## Features

- **Dynamic Progress Reading**: Reads project status files automatically
- **Multiple Format Support**: Supports both JSON and key=value formats
- **Milestone Tracking**: Extracts and tracks project milestones
- **Context Integration**: Seamlessly integrates with `restore_context.py`

## Usage

### Basic Usage

```python
from project_progress import get_project_progress, get_all_project_progress

# Get progress for a single project
progress = get_project_progress("hermes-plan")
print(f"{progress['name']}: {progress['progress']}% - {progress['status']}")

# Get progress for all projects
all_progress = get_all_project_progress()
for p in all_progress:
    print(f"{p['name']}: {p['progress']}%")
```

### Integration with Context Summary

```python
from restore_context import get_context_summary

summary = get_context_summary('./compressed_context/latest_compressed.json')
project_progress = summary['project_progress']

# Access project summary
print(f"Total Projects: {project_progress['project_summary']['total']}")
print(f"Average Progress: {project_progress['project_summary']['average_progress']}%")

# Access individual projects
for project in project_progress['projects']:
    print(f"- {project['name']}: {project['progress']}%")
```

## Status File Formats

### JSON Format (status.json)

```json
{
  "name": "Project Name",
  "description": "Project description",
  "status": "active",
  "progress": 75,
  "version": "1.0.0",
  "milestones": ["Phase 1", "Phase 2", "Phase 3"],
  "last_updated": "2026-02-07T12:00:00",
  "current_phase": "Phase 2"
}
```

### Key=Value Format (.progress)

```
name=Project Name
description=Project description
status=active
progress=75
version=1.0.0
milestones=Phase 1,Phase 2,Phase 3
last_updated=2026-02-07T12:00:00
```

## Project Directory Structure

```
projects/
├── hermes-plan/
│   └── status.json
├── akasha-plan/
│   └── status.json
└── morning-brief/
    └── .progress
```

## API Reference

### `get_project_progress(project_name: str) -> dict`

Get progress information for a specific project.

**Returns:**
```python
{
    "project": "hermes-plan",
    "status": "active",
    "progress": 65,
    "milestones": [...],
    "last_updated": "2026-02-07T18:30:00",
    "exists": True,
    "error": None,
    "name": "Hermes Plan",
    "description": "Data analysis assistant...",
    "version": "2.1.0"
}
```

### `get_all_project_progress() -> list[dict]`

Get progress for all projects in the projects directory.

### `get_project_summary_for_context() -> dict`

Get project progress summary for context restoration integration.

### `calculate_overall_progress(projects: list[dict]) -> dict`

Calculate aggregate statistics across projects.

## Running Standalone

```bash
python3 project_progress.py
```

Output:
```
============================================================
PROJECT PROGRESS REPORT
============================================================

📊 Overall Statistics:
   Total Projects: 3
   Active: 3
   Completed: 0
   Average Progress: 81.7%

📁 Project Details:
------------------------------------------------------------

🟢 Akasha Plan
   Status: active
   Progress: 80%
   Milestones: 5 items
   Last Updated: 2026-02-07T20:00:00

...
```

## Valid Status Values

- `active`: Project is actively being developed
- `completed`: Project is finished
- `paused`: Project is temporarily paused
- `archived`: Project is archived
- `planning`: Project is in planning phase
- `unknown`: Status cannot be determined
