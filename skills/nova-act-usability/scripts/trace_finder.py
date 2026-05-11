#!/usr/bin/env python3
"""
Utility to find Nova Act trace files for a session.
"""

import os
import glob
from typing import List


def find_trace_files(logs_dir: str, session_start_time: float) -> List[str]:
    """
    Find Nova Act HTML trace files generated during a test session.
    
    Args:
        logs_dir: Directory where Nova Act stores logs
        session_start_time: Unix timestamp when session started
    
    Returns:
        List of paths to HTML trace files
    """
    if not os.path.exists(logs_dir):
        return []
    
    # Find all HTML files in the logs directory and subdirectories
    pattern = os.path.join(logs_dir, "**", "*.html")
    html_files = glob.glob(pattern, recursive=True)
    
    # Filter to files created after session start
    trace_files = []
    for filepath in html_files:
        file_mtime = os.path.getmtime(filepath)
        if file_mtime >= session_start_time:
            trace_files.append(filepath)
    
    return sorted(trace_files, key=os.path.getmtime)


def get_latest_session_dir(logs_dir: str) -> str:
    """
    Get the most recently created session directory.
    Nova Act creates directories like: <logs_dir>/<session_id>/
    """
    if not os.path.exists(logs_dir):
        return ""
    
    # Find all subdirectories
    subdirs = [d for d in glob.glob(os.path.join(logs_dir, "*")) if os.path.isdir(d)]
    
    if not subdirs:
        return ""
    
    # Return most recently created
    return max(subdirs, key=os.path.getmtime)


def get_session_traces(logs_dir: str) -> List[str]:
    """
    Get all trace files from the most recent session directory.
    
    Args:
        logs_dir: Base logs directory
    
    Returns:
        List of HTML trace file paths
    """
    session_dir = get_latest_session_dir(logs_dir)
    
    if not session_dir:
        return []
    
    # Find all HTML files in this session directory
    pattern = os.path.join(session_dir, "*.html")
    trace_files = glob.glob(pattern)
    
    return sorted(trace_files, key=os.path.getmtime)
