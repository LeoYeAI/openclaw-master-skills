#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HealthFit Data Backup Script
Function: Backup data/ directory to data/db/backup/

Privacy Design:
  private_sexual_health.json is excluded from all backups by default.
  To include, run with --include-private parameter and confirm in interactive prompt.
  This is the actual implementation of the "secondary confirmation" promise in SKILL.md.
"""

import sys
import shutil
import json
import argparse
import logging
import time
import random
import string
from datetime import datetime
from pathlib import Path

# Configure logging
def setup_logging():
    """Setup logging"""
    log_path = Path(__file__).parent.parent / "data" / "backup.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        encoding='utf-8'
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# ─── Sensitive File List ─────────────────────────────────────────────────────────────
# Files in this list are excluded from backup by default.
# Users must meet both following conditions to include them in backup:
#   1. Add --include-private parameter when running
#   2. Manually input "yes" in interactive prompt to confirm
PRIVATE_FILES = {
    "private_sexual_health.json",
}
# ─────────────────────────────────────────────────────────────────────────────────────


def get_skill_dir() -> Path:
    """Get HealthFit skill root directory (two levels up from this script)"""
    return Path(__file__).parent.parent


def get_data_dir() -> Path:
    return get_skill_dir() / "data"


def get_backup_dir() -> Path:
    return get_skill_dir() / "data" / "db" / "backup"


def check_disk_space(required_mb: int = 100) -> bool:
    """Check if disk space is sufficient"""
    try:
        total, used, free = shutil.disk_usage(Path(__file__).parent)
        free_mb = free // (1024 * 1024)
        if free_mb < required_mb:
            logger.error(f"Insufficient disk space: need {required_mb}MB, have {free_mb}MB")
            print(f"❌ Insufficient disk space: need {required_mb}MB, have {free_mb}MB")
            return False
        return True
    except Exception as e:
        logger.error(f"Disk space check failed: {e}")
        return True  # Don't block backup if check fails


def safe_copy(src: Path, dest: Path) -> bool:
    """Safely copy file with error handling"""
    try:
        if not src.exists():
            logger.warning(f"Source file doesn't exist: {src}")
            return False
        
        if not dest.parent.exists():
            dest.parent.mkdir(parents=True)
        
        shutil.copy2(src, dest)
        logger.info(f"Successfully copied: {src} -> {dest}")
        return True
    
    except PermissionError:
        logger.error(f"Permission denied, cannot copy: {src}")
        print(f"❌ Permission error: cannot access {src}")
        return False
    
    except OSError as e:
        logger.error(f"System error: {e}")
        print(f"❌ System error: {e}")
        return False


def backup_with_retry(src: Path, dest: Path, max_retries: int = 3) -> bool:
    """Backup with retry mechanism"""
    for attempt in range(max_retries):
        if safe_copy(src, dest):
            return True
        logger.warning(f"Attempt {attempt + 1} failed, retrying...")
        time.sleep(1)
    return False


def _confirm_private_inclusion() -> bool:
    """
    Interactive secondary confirmation before backing up sensitive files.
    Only returns True when user explicitly inputs "yes".
    """
    print()
    print("=" * 60)
    print("⚠️  WARNING: Highly Sensitive Data Backup Confirmation  ⚠️")
    print("=" * 60)
    print("""
You have requested to include sensitive private files in this backup.

Files involved:
  - private_sexual_health.json (sexual health records)
  - Other personal health privacy information

This operation risks:
  ❌ Backup files may be accessed by others
  ❌ Cloud sync may automatically upload
  ❌ Data breach may cause privacy damage

Please confirm you understand these risks.
""")
    print("=" * 60)
    
    # Random verification code confirmation
    verify_code = ''.join(random.choices(string.ascii_uppercase, k=6))
    print(f"\nPlease enter the following verification code to confirm: {verify_code}")
    
    user_input = input("Verification code: ").strip().upper()
    if user_input != verify_code:
        print("❌ Verification code incorrect, operation cancelled")
        logger.warning("Private file backup verification failed")
        return False
    
    # Record operation log
    log_path = Path(__file__).parent.parent / "data" / "security_log.txt"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] Private file backup operation confirmed\n")
    
    logger.info("Private file backup verification passed")
    print("✅ Verification passed, continuing backup...\n")
    return True


def _copy_json_dir(json_dir: Path, dest: Path, include_private: bool) -> dict:
    """
    Copy json/ directory to target path, filtering sensitive files.
    
    Returns summary dict: {copied: [...], skipped: [...]}
    """
    dest.mkdir(parents=True, exist_ok=True)
    summary = {"copied": [], "skipped": []}
    
    # Copy top-level JSON files (filtered by list)
    for src_file in json_dir.glob("*.json"):
        if src_file.name in PRIVATE_FILES:
            if include_private:
                if backup_with_retry(src_file, dest / src_file.name):
                    summary["copied"].append(src_file.name)
                else:
                    summary["skipped"].append(src_file.name + " (copy failed)")
            else:
                summary["skipped"].append(src_file.name)
        else:
            if backup_with_retry(src_file, dest / src_file.name):
                summary["copied"].append(src_file.name)
            else:
                summary["skipped"].append(src_file.name + " (copy failed)")
    
    # Fully copy daily/ subdirectory (no sensitive files in this directory)
    daily_src = json_dir / "daily"
    if daily_src.exists():
        shutil.copytree(daily_src, dest / "daily")
        daily_count = len(list((dest / "daily").glob("*.json")))
        summary["copied"].append(f"daily/ ({daily_count} files)")
    
    return summary


def create_backup(include_private: bool = False) -> Path:
    """
    Create timestamped backup under data/db/backup/.
    
    Args:
        include_private: If True (and user confirmed), also backup sensitive files.
                        If False (default), sensitive files are silently excluded.
    """
    
    # Check disk space
    if not check_disk_space():
        logger.error("Backup cancelled due to insufficient disk space")
        return None
    
    backup_dir = get_backup_dir()
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate backup directory name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"backup_{timestamp}"
    backup_path.mkdir()
    
    print(f"📦 Starting backup to: {backup_path}")
    logger.info(f"Backup started: {backup_path}")
    
    # Copy json/ directory
    json_dir = get_data_dir() / "json"
    if json_dir.exists():
        print("📄 Backing up JSON files...")
        summary = _copy_json_dir(json_dir, backup_path / "json", include_private)
        print(f"   Copied: {len(summary['copied'])} files")
        print(f"   Skipped: {len(summary['skipped'])} sensitive files")
        logger.info(f"JSON backup complete: {len(summary['copied'])} copied, {len(summary['skipped'])} skipped")
    
    # Copy txt/ directory
    txt_dir = get_data_dir() / "txt"
    if txt_dir.exists():
        print("📄 Backing up TXT files...")
        shutil.copytree(txt_dir, backup_path / "txt")
        logger.info("TXT backup complete")
    
    # Copy database
    db_file = get_data_dir() / "db" / "healthfit.db"
    if db_file.exists():
        print("📊 Backing up database...")
        backup_with_retry(db_file, backup_path / "db" / "healthfit.db")
        logger.info("Database backup complete")
    
    # Clean old backups (keep max 4)
    cleanup_old_backups(backup_dir, max_backups=4)
    
    print(f"\n✅ Backup complete: {backup_path}")
    logger.info(f"Backup complete: {backup_path}")
    
    return backup_path


def cleanup_old_backups(backup_dir: Path, max_backups: int = 4):
    """Clean old backups, keep only max_backups most recent"""
    backups = sorted(backup_dir.glob("backup_*"), reverse=True)
    
    if len(backups) > max_backups:
        for old_backup in backups[max_backups:]:
            shutil.rmtree(old_backup)
            logger.info(f"Cleaned old backup: {old_backup}")
        print(f"🧹 Cleaned {len(backups) - max_backups} old backups (kept {max_backups})")


def main():
    parser = argparse.ArgumentParser(description="HealthFit Data Backup")
    parser.add_argument("--include-private", action="store_true", 
                       help="Include sensitive private files (requires secondary confirmation)")
    
    args = parser.parse_args()
    
    # Secondary confirmation for sensitive files
    include_private = False
    if args.include_private:
        include_private = _confirm_private_inclusion()
    
    # Create backup
    backup_path = create_backup(include_private)
    
    if backup_path:
        print(f"\n💡 Tip: Backup stored at {backup_path}")
        print(f"   Old backups are automatically cleaned (keeps 4 most recent)")
    else:
        print("\n❌ Backup failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
