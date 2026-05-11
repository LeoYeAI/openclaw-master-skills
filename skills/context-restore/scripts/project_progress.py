#!/usr/bin/env python3
"""
Project Progress Module
=======================

Provides functions for dynamically reading project progress from
project directories. Reads status.json or .progress files to get
real-time project status, milestones, and completion percentage.

Features:
- Reads project status from status.json or .progress files
- Supports both JSON and simple key=value formats
- Extracts milestones and completion percentage
- Integrates with context restoration system

Usage:
    from project_progress import get_project_progress, get_all_project_progress
    
    # Get progress for a single project
    progress = get_project_progress("hermes-plan")
    
    # Get progress for all projects
    all_progress = get_all_project_progress()
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


# =============================================================================
# CONSTANTS
# =============================================================================

# Default project directories
PROJECTS_BASE_PATH = "/home/athur/.openclaw/workspace/projects"

# Status file names (in order of preference)
STATUS_FILES = ["status.json", ".progress", "progress.json"]

# Valid project statuses
VALID_STATUSES = ["active", "completed", "paused", "archived", "planning"]


# =============================================================================
# PROJECT PROGRESS FUNCTIONS
# =============================================================================

def read_status_file(project_path: str) -> Optional[dict]:
    """
    Read project status from status.json or .progress file.
    
    Attempts to read status files in order of preference:
    1. status.json (JSON format)
    2. .progress (JSON or key=value format)
    3. progress.json (JSON format)
    
    Args:
        project_path: Path to the project directory.
        
    Returns:
        Parsed status dictionary, or None if no valid file found.
        
    Example:
        >>> status = read_status_file("/home/athur/.openclaw/workspace/projects/hermes-plan")
        >>> print(status['status'])
        'active'
    """
    for filename in STATUS_FILES:
        filepath = os.path.join(project_path, filename)
        
        if not os.path.exists(filepath):
            continue
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if not content or not content.strip():
                continue
                
            # Try JSON format first
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                pass
            
            # Try key=value format (.progress file)
            if filename == ".progress":
                result = parse_key_value_format(content)
                if result:
                    return result
                    
        except (OSError, PermissionError):
            continue
    
    return None


def parse_key_value_format(content: str) -> Optional[dict]:
    """
    Parse key=value format .progress file.
    
    Supports formats like:
        status=active
        progress=75
        milestones=Planning,Development,Testing,Deployment
        
    Args:
        content: Raw content string from .progress file.
        
    Returns:
        Parsed dictionary, or None if parsing fails.
        
    Example:
        >>> content = "status=active\\nprogress=50\\nmilestones=A,B,C"
        >>> result = parse_key_value_format(content)
        >>> print(result['status'])
        'active'
    """
    result = {}
    milestones = []
    
    for line in content.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip().lower()
            value = value.strip()
            
            if key == "status":
                result['status'] = value.lower()
            elif key == "progress":
                try:
                    result['progress'] = int(value)
                except ValueError:
                    try:
                        result['progress'] = float(value)
                    except ValueError:
                        pass
            elif key == "milestones":
                milestones = [m.strip() for m in value.split(',') if m.strip()]
            elif key == "name":
                result['name'] = value
            elif key == "description":
                result['description'] = value
            elif key == "last_updated":
                result['last_updated'] = value
            elif key == "version":
                result['version'] = value
    
    if milestones:
        result['milestones'] = milestones
    
    return result if result else None


def get_project_progress(project_name: str) -> dict:
    """
    Get progress information for a specific project.
    
    Dynamically reads project directory to get real-time progress,
    status, milestones, and other metadata.
    
    Args:
        project_name: Name of the project (directory name).
        
    Returns:
        Dictionary containing:
        - 'project': Project name
        - 'status': Project status (active|completed|paused|archived|planning)
        - 'progress': Completion percentage (0-100)
        - 'milestones': List of milestones
        - 'last_updated': Timestamp of last update
        - 'exists': Whether project directory exists
        - 'error': Error message if any
        
    Example:
        >>> progress = get_project_progress("hermes-plan")
        >>> print(progress['status'])
        'active'
        >>> print(progress['progress'])
        75
    """
    project_path = os.path.join(PROJECTS_BASE_PATH, project_name)
    
    # Check if project directory exists
    if not os.path.exists(project_path):
        return {
            "project": project_name,
            "status": "unknown",
            "progress": 0,
            "milestones": [],
            "last_updated": None,
            "exists": False,
            "error": f"Project directory not found: {project_path}"
        }
    
    # Try to read status file
    status_data = read_status_file(project_path)
    
    if status_data is None:
        return {
            "project": project_name,
            "status": "unknown",
            "progress": 0,
            "milestones": [],
            "last_updated": None,
            "exists": True,
            "error": "No status file found"
        }
    
    # Validate and normalize status
    status = status_data.get('status', 'unknown').lower()
    if status not in VALID_STATUSES:
        status = 'unknown'
    
    # Get progress percentage
    progress = status_data.get('progress', 0)
    if isinstance(progress, (int, float)):
        progress = max(0, min(100, int(progress)))
    else:
        progress = 0
    
    # Get milestones
    milestones = status_data.get('milestones', [])
    if isinstance(milestones, str):
        milestones = [m.strip() for m in milestones.split(',') if m.strip()]
    
    # Get last updated timestamp
    last_updated = status_data.get('last_updated')
    if last_updated:
        # Validate timestamp format
        try:
            datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            last_updated = None
    
    # If no timestamp, use file modification time
    if not last_updated:
        for filename in STATUS_FILES:
            filepath = os.path.join(project_path, filename)
            if os.path.exists(filepath):
                try:
                    mtime = os.path.getmtime(filepath)
                    last_updated = datetime.fromtimestamp(mtime).isoformat()
                    break
                except OSError:
                    pass
    
    return {
        "project": project_name,
        "status": status,
        "progress": progress,
        "milestones": milestones,
        "last_updated": last_updated,
        "exists": True,
        "error": None,
        "name": status_data.get('name', project_name),
        "description": status_data.get('description', ''),
        "version": status_data.get('version', None)
    }


def get_all_project_progress() -> list[dict]:
    """
    Get progress for all projects in the projects directory.
    
    Scans the projects directory and retrieves progress information
    for each project found.
    
    Returns:
        List of project progress dictionaries, sorted by project name.
        
    Example:
        >>> all_progress = get_all_project_progress()
        >>> for p in all_progress:
        ...     print(f"{p['project']}: {p['progress']}% - {p['status']}")
    """
    if not os.path.exists(PROJECTS_BASE_PATH):
        return []
    
    projects = []
    
    try:
        entries = os.listdir(PROJECTS_BASE_PATH)
    except OSError:
        return []
    
    for entry in entries:
        project_path = os.path.join(PROJECTS_BASE_PATH, entry)
        
        # Only process directories
        if not os.path.isdir(project_path):
            continue
            
        # Skip hidden directories
        if entry.startswith('.'):
            continue
        
        progress = get_project_progress(entry)
        projects.append(progress)
    
    # Sort by project name
    projects.sort(key=lambda x: x['project'])
    
    return projects


def calculate_overall_progress(projects: list[dict]) -> dict:
    """
    Calculate overall progress across multiple projects.
    
    Args:
        projects: List of project progress dictionaries.
        
    Returns:
        Dictionary containing aggregate statistics.
        
    Example:
        >>> all_p = get_all_project_progress()
        >>> stats = calculate_overall_progress(all_p)
        >>> print(f"Average progress: {stats['average_progress']}%")
    """
    if not projects:
        return {
            "total_projects": 0,
            "active_projects": 0,
            "completed_projects": 0,
            "average_progress": 0,
            "total_progress": 0
        }
    
    total = len(projects)
    active = sum(1 for p in projects if p['status'] == 'active')
    completed = sum(1 for p in projects if p['status'] == 'completed')
    
    # Calculate average progress (only counting non-zero projects)
    progress_values = [p['progress'] for p in projects if p['progress'] > 0]
    if progress_values:
        avg_progress = sum(progress_values) / len(progress_values)
    else:
        avg_progress = 0
    
    return {
        "total_projects": total,
        "active_projects": active,
        "completed_projects": completed,
        "average_progress": round(avg_progress, 1),
        "total_progress": sum(p['progress'] for p in projects)
    }


# =============================================================================
# INTEGRATION WITH CONTEXT RESTORATION
# =============================================================================

def get_project_summary_for_context() -> dict:
    """
    Get project progress summary for context restoration integration.
    
    Returns a structured dictionary ready for integration into
    the get_context_summary() output.
    
    Returns:
        Dictionary with 'projects' (list) and 'project_summary' (dict).
    """
    projects = get_all_project_progress()
    overview = calculate_overall_progress(projects)
    
    return {
        "projects": projects,
        "project_summary": {
            "total": overview['total_projects'],
            "active": overview['active_projects'],
            "completed": overview['completed_projects'],
            "average_progress": overview['average_progress']
        },
        "last_refreshed": datetime.now().isoformat()
    }


# =============================================================================
# STANDALONE EXECUTION
# =============================================================================

if __name__ == '__main__':
    import sys
    
    print("=" * 60)
    print("PROJECT PROGRESS REPORT")
    print("=" * 60)
    
    # Get all project progress
    all_progress = get_all_project_progress()
    
    if not all_progress:
        print("\nNo projects found in:", PROJECTS_BASE_PATH)
        print("\nTo add a project:")
        print("  1. Create directory: mkdir -p projects/<project-name>")
        print("  2. Add status.json or .progress file")
        sys.exit(0)
    
    # Calculate overall stats
    stats = calculate_overall_progress(all_progress)
    
    print(f"\n📊 Overall Statistics:")
    print(f"   Total Projects: {stats['total_projects']}")
    print(f"   Active: {stats['active_projects']}")
    print(f"   Completed: {stats['completed_projects']}")
    print(f"   Average Progress: {stats['average_progress']}%")
    
    print(f"\n📁 Project Details:")
    print("-" * 60)
    
    for project in all_progress:
        name = project.get('name', project['project'])
        status_emoji = {
            'active': '🟢',
            'completed': '✅',
            'paused': '⏸️',
            'archived': '📦',
            'unknown': '❓',
            'planning': '📋'
        }.get(project['status'], '❓')
        
        print(f"\n{status_emoji} {name}")
        print(f"   Status: {project['status']}")
        print(f"   Progress: {project['progress']}%")
        print(f"   Milestones: {len(project['milestones'])} items")
        
        if project.get('last_updated'):
            print(f"   Last Updated: {project['last_updated']}")
        
        if project.get('error'):
            print(f"   ⚠️  {project['error']}")
    
    print("\n" + "=" * 60)
