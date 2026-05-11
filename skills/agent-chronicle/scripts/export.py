#!/usr/bin/env python3
"""
AI Diary Export

Export diary entries to PDF or HTML using pandoc.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
CONFIG_FILE = SKILL_DIR / "config.json"
DEFAULT_DIARY_PATH = "memory/diary/"

def load_config():
    """Load configuration from config.json"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {
        "diary_path": DEFAULT_DIARY_PATH,
        "export": {
            "default_format": "pdf",
            "style": "minimal"
        }
    }

def get_workspace_root():
    """Find the workspace root"""
    import os
    
    # Check environment variable first
    env_workspace = os.getenv("OPENCLAW_WORKSPACE") or os.getenv("AGENT_WORKSPACE")
    if env_workspace:
        env_path = Path(env_workspace)
        if (env_path / "memory").exists():
            return env_path
    
    # Try common locations
    candidates = [
        Path.cwd(),
        Path.home() / "clawd",
        Path.home() / ".openclaw" / "workspace",
    ]
    for path in candidates:
        if (path / "memory").exists():
            return path
    return Path.cwd()

def get_diary_path(config):
    """Get full path to diary directory"""
    workspace = get_workspace_root()
    return workspace / config.get("diary_path", DEFAULT_DIARY_PATH)

def check_pandoc():
    """Check if pandoc is installed"""
    try:
        subprocess.run(["pandoc", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def collect_entries(diary_path, days=None, month=None, all_entries=False):
    """Collect diary entries to export"""
    entries = []
    
    if not diary_path.exists():
        print(f"Diary path not found: {diary_path}")
        return entries
    
    # Get all markdown files
    md_files = sorted(diary_path.glob("*.md"))
    
    if all_entries:
        entries = md_files
    elif month:
        # Filter by month (format: YYYY-MM)
        entries = [f for f in md_files if f.stem.startswith(month)]
    elif days:
        # Get last N days
        cutoff = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff.strftime("%Y-%m-%d")
        entries = [f for f in md_files if f.stem >= cutoff_str]
    else:
        entries = md_files
    
    return entries

def combine_entries(entries):
    """Combine multiple entries into one document"""
    combined = []
    
    for entry_path in entries:
        with open(entry_path) as f:
            content = f.read()
        combined.append(content)
        combined.append("\n\n---\n\n")  # Page break hint
    
    return "\n".join(combined)

def export_pdf(content, output_path):
    """Export content to PDF using pandoc"""
    # Create temp markdown file
    temp_md = output_path.parent / ".temp_diary.md"
    
    # Add title page
    title_content = f"""---
title: AI Diary
date: {datetime.now().strftime("%Y-%m-%d")}
geometry: margin=1in
---

{content}
"""
    
    with open(temp_md, 'w') as f:
        f.write(title_content)
    
    try:
        result = subprocess.run([
            "pandoc",
            str(temp_md),
            "-o", str(output_path),
            "--sandbox",
            "--pdf-engine=xelatex",
            "-V", "mainfont=DejaVu Sans",
            "-V", "geometry:margin=1in"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            # Try without xelatex
            result = subprocess.run([
                "pandoc",
                str(temp_md),
                "-o", str(output_path),
                "--sandbox",
            ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ Exported to {output_path}")
            return True
        else:
            print(f"Error: {result.stderr}")
            return False
    finally:
        if temp_md.exists():
            temp_md.unlink()

def export_html(content, output_path):
    """Export content to HTML using pandoc"""
    temp_md = output_path.parent / ".temp_diary.md"
    
    with open(temp_md, 'w') as f:
        f.write(content)
    
    try:
        result = subprocess.run([
            "pandoc",
            str(temp_md),
            "-o", str(output_path),
            "--sandbox",
            "--standalone",
            "--metadata", "title=AI Diary",
            "--css=https://cdn.simplecss.org/simple.min.css"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ Exported to {output_path}")
            return True
        else:
            print(f"Error: {result.stderr}")
            return False
    finally:
        if temp_md.exists():
            temp_md.unlink()

def main():
    parser = argparse.ArgumentParser(description="Export AI Diary entries")
    parser.add_argument("--format", "-f", choices=["pdf", "html"], default="pdf",
                        help="Export format (default: pdf)")
    parser.add_argument("--days", "-d", type=int, help="Export last N days")
    parser.add_argument("--month", "-m", help="Export specific month (YYYY-MM)")
    parser.add_argument("--all", action="store_true", help="Export all entries")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--list", action="store_true", help="List available entries")
    
    args = parser.parse_args()
    
    config = load_config()
    diary_path = get_diary_path(config)
    
    if args.list:
        entries = collect_entries(diary_path, all_entries=True)
        print(f"Found {len(entries)} diary entries in {diary_path}:\n")
        for entry in entries:
            print(f"  {entry.stem}")
        return
    
    # Check pandoc
    if not check_pandoc():
        print("Error: pandoc is not installed.")
        print("Install with: apt install pandoc")
        print("For PDF: apt install pandoc texlive-xetex")
        sys.exit(1)
    
    # Collect entries
    entries = collect_entries(
        diary_path,
        days=args.days,
        month=args.month,
        all_entries=args.all
    )
    
    if not entries:
        print("No diary entries found to export.")
        sys.exit(1)
    
    print(f"Exporting {len(entries)} entries...")
    
    # Combine content
    content = combine_entries(entries)
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        workspace = get_workspace_root()
        ext = "pdf" if args.format == "pdf" else "html"
        timestamp = datetime.now().strftime("%Y%m%d")
        output_path = workspace / f"diary-export-{timestamp}.{ext}"
    
    # Export
    if args.format == "pdf":
        export_pdf(content, output_path)
    else:
        export_html(content, output_path)

if __name__ == "__main__":
    main()
