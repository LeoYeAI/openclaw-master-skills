#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MiniVCS Skill - lightweight file version management system
- Modify: save an incremental diff plus a full pre-edit snapshot (supports rollback)
- Delete: save the full file to trash (supports restore)

Retention policy:
- Normal files: 7 days
- Important files: 14 days (system paths, config files, entry files, etc.)

After each record operation, the full record table is scanned automatically
(from earliest to latest), and a list of expired records that can be cleaned
up is returned for the Agent to confirm with the user.
"""

import os
import sys
import json
import time
import shutil
import difflib
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional

# -------------------------------------------------------------------
# Important file detection rules
# -------------------------------------------------------------------

# Absolute system paths that always qualify as important
IMPORTANT_PATH_PREFIXES_ABSOLUTE = [
    "/etc/",
    "/root/",
    "/usr/local/etc/",
    "/opt/",
]

# User-home-relative directories that qualify as important (expanded at runtime).
# Only specific config/credential dirs -- NOT the entire home directory.
IMPORTANT_HOME_SUBDIRS = [
    ".ssh",
    ".gnupg",
    ".gpg",
    ".config",
    ".local/share",
    ".openclaw",
    ".kube",
    ".docker",
    ".aws",
    ".azure",
]

# Windows system directories (matched case-insensitively)
IMPORTANT_WINDOWS_PREFIXES = [
    "c:\\windows\\",
    "c:\\programdata\\",
    "c:\\program files\\",
    "c:\\program files (x86)\\",
]

IMPORTANT_FILENAME_PATTERNS = [
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".conf",
    ".env",
    "main.py",
    "app.py",
    "server.py",
    "wsgi.py",
    "asgi.py",
    "index.ts",
    "index.js",
    "main.ts",
    "main.go",
    "main.rs",
    "manage.py",
    "settings.py",
    "config.py",
    "dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "makefile",
    "cmakelists.txt",
]

# Paths containing any of these segments are auto-skipped (generated / vendored content)
SKIP_PATH_SEGMENTS = [
    "node_modules",
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    ".tox",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "dist",
    "build",
    ".next",
    ".nuxt",
    ".turbo",
]

RETENTION_NORMAL_DAYS = 7
RETENTION_IMPORTANT_DAYS = 14

BINARY_SIZE_WARN_THRESHOLD = 50 * 1024 * 1024  # 50 MB


def _build_important_home_prefixes() -> list[str]:
    """Expand IMPORTANT_HOME_SUBDIRS into absolute prefixes for the current user."""
    home = os.path.expanduser("~")
    return [os.path.join(home, d) + os.sep for d in IMPORTANT_HOME_SUBDIRS]


def is_important_file(file_path: str) -> bool:
    """Determine whether a file is important and needs a longer retention period."""
    abs_path = os.path.abspath(file_path)

    # System path prefixes (Unix)
    for prefix in IMPORTANT_PATH_PREFIXES_ABSOLUTE:
        if abs_path.startswith(prefix):
            return True

    # Specific user config/credential directories under home
    for prefix in _build_important_home_prefixes():
        if abs_path.startswith(prefix):
            return True

    # Windows system directories (case-insensitive)
    if sys.platform == "win32":
        lower = abs_path.lower().replace("/", "\\")
        for prefix in IMPORTANT_WINDOWS_PREFIXES:
            if lower.startswith(prefix):
                return True

    # Filename patterns (lowercase match)
    filename = os.path.basename(abs_path).lower()
    for pattern in IMPORTANT_FILENAME_PATTERNS:
        if filename == pattern or filename.endswith(pattern):
            return True

    return False


def should_skip_path(file_path: str) -> Optional[str]:
    """Return the matched skip segment if the path should be auto-skipped, else None."""
    normalized = os.path.abspath(file_path).replace("\\", "/")
    parts = normalized.split("/")
    for segment in SKIP_PATH_SEGMENTS:
        if segment in parts:
            return segment
    return None


def get_retention_days(file_path: str) -> int:
    """Return retention days based on file importance."""
    return RETENTION_IMPORTANT_DAYS if is_important_file(file_path) else RETENTION_NORMAL_DAYS


def _make_safe_path(relative_path: str) -> str:
    """
    Convert a relative path into a safe string that can be used as a filename.
    Use the full relative path rather than just the filename to avoid conflicts
    between files with the same name.
    """
    return relative_path.replace(os.sep, "__").replace("/", "__")


# -------------------------------------------------------------------
# LogManager
# -------------------------------------------------------------------


class LogManager:
    """Log manager responsible for reading and writing JSON change records."""

    def __init__(self, vcs_root: str):
        self.vcs_root = vcs_root
        self.log_file = os.path.join(vcs_root, "logs.json")
        self._ensure_log_file()

    def _ensure_log_file(self):
        if not os.path.exists(self.log_file):
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump({"version": "1.0", "records": []}, f, ensure_ascii=False, indent=2)

    def _read_log(self) -> Dict[str, Any]:
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"version": "1.0", "records": []}

    def _write_log(self, data: Dict[str, Any]):
        # Atomic write: write a temp file first, then rename it to avoid corrupting logs.json on crash
        tmp_file = self.log_file + ".tmp"
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_file, self.log_file)

    def append_record(self, record: Dict[str, Any]) -> str:
        data = self._read_log()
        record_id = record.get("recordId", f"{int(time.time() * 1000)}")
        record["recordId"] = record_id

        now_ms = int(time.time() * 1000)
        if "timestamp" not in record:
            record["timestamp"] = now_ms
        if "datetime" not in record:
            record["datetime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # If expireAt is not set, calculate it automatically from retentionDays
        if "expireAt" not in record:
            retention_days = record.get("retentionDays", RETENTION_NORMAL_DAYS)
            record["expireAt"] = record["timestamp"] + retention_days * 24 * 60 * 60 * 1000
        if "expireAtDatetime" not in record:
            record["expireAtDatetime"] = datetime.fromtimestamp(record["expireAt"] / 1000).strftime("%Y-%m-%d %H:%M:%S")

        data["records"].append(record)
        self._write_log(data)
        return record_id

    def update_record(self, record_id: str, updates: Dict[str, Any]) -> bool:
        """Update fields on the specified record."""
        data = self._read_log()
        for record in data["records"]:
            if record.get("recordId") == record_id:
                record.update(updates)
                self._write_log(data)
                return True
        return False

    def get_history_by_file(self, file_path: str, descending: bool = True) -> List[Dict[str, Any]]:
        data = self._read_log()
        records = [r for r in data["records"] if r.get("filePath") == file_path]
        records.sort(key=lambda x: x.get("timestamp", 0), reverse=descending)
        return records

    def get_all_history(self, descending: bool = True) -> List[Dict[str, Any]]:
        data = self._read_log()
        records = list(data["records"])
        records.sort(key=lambda x: x.get("timestamp", 0), reverse=descending)
        return records

    def get_due_for_cleanup(self) -> List[Dict[str, Any]]:
        """
        Return expired records (expireAt <= current time), sorted by expireAt
        from earliest to latest. Skip records that were already restored or rolled back.
        """
        data = self._read_log()
        current_time = int(time.time() * 1000)
        skip_actions = {"RESTORED", "ROLLED_BACK"}
        due = [
            r
            for r in data["records"]
            if r.get("expireAt") is not None and r["expireAt"] <= current_time and r.get("action") not in skip_actions
        ]
        due.sort(key=lambda x: x.get("expireAt", 0))
        return due

    def extend_record_expiry(self, record_id: str, additional_ms: int) -> bool:
        """Extend expireAt on the specified record by additional_ms milliseconds."""
        data = self._read_log()
        for record in data["records"]:
            if record.get("recordId") == record_id:
                record["expireAt"] = record.get("expireAt", int(time.time() * 1000)) + additional_ms
                record["expireAtDatetime"] = datetime.fromtimestamp(record["expireAt"] / 1000).strftime("%Y-%m-%d %H:%M:%S")
                self._write_log(data)
                return True
        return False

    def get_expired_records(self, days: int) -> List[Dict[str, Any]]:
        """Compatibility for the old interface: query expired records by fixed days."""
        data = self._read_log()
        current_time = int(time.time() * 1000)
        expire_ms = days * 24 * 60 * 60 * 1000
        return [r for r in data["records"] if current_time - r.get("timestamp", 0) > expire_ms]

    def delete_record(self, record_id: str) -> bool:
        data = self._read_log()
        original_count = len(data["records"])
        data["records"] = [r for r in data["records"] if r.get("recordId") != record_id]
        if len(data["records"]) < original_count:
            self._write_log(data)
            return True
        return False

    def clean_expired_records(self, days: int) -> Dict[str, Any]:
        expired = self.get_expired_records(days)
        deleted_count = sum(1 for r in expired if self.delete_record(r.get("recordId", "")))
        return {"deleted_count": deleted_count, "deleted_records": expired}

    def get_record_by_id(self, record_id: str) -> Optional[Dict[str, Any]]:
        data = self._read_log()
        for record in data["records"]:
            if record.get("recordId") == record_id:
                return record
        return None


# -------------------------------------------------------------------
# DiffEngine
# -------------------------------------------------------------------


class DiffEngine:
    """Diff engine that generates file change differences."""

    @staticmethod
    def generate_diff(old_content: str, new_content: str, context: int = 3) -> str:
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile="original",
            tofile="modified",
            lineterm="\n",
            n=context,
        )
        return "".join(diff)

    @staticmethod
    def parse_diff_summary(diff_text: str) -> Dict[str, int | str]:
        added = removed = 0
        for line in diff_text.splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                added += 1
            elif line.startswith("-") and not line.startswith("---"):
                removed += 1
        return {
            "added": added,
            "removed": removed,
            "summary": f"+{added} lines, -{removed} lines" if added or removed else "No changes",
        }


# -------------------------------------------------------------------
# FileManager
# -------------------------------------------------------------------


class FileManager:
    """File manager responsible for physical file operations."""

    def __init__(self, vcs_root: str, project_root: str):
        self.vcs_root = vcs_root
        self.project_root = project_root
        self.trash_dir = os.path.join(vcs_root, "trash")
        self.diffs_dir = os.path.join(vcs_root, "diffs")
        self.bases_dir = os.path.join(vcs_root, "bases")
        self.snapshots_dir = os.path.join(vcs_root, "snapshots")  # Full pre-edit snapshots for text files, used for rollback
        self.backups_dir = os.path.join(vcs_root, "backups")  # Full-copy backups for binary files
        os.makedirs(self.trash_dir, exist_ok=True)
        os.makedirs(self.diffs_dir, exist_ok=True)
        os.makedirs(self.bases_dir, exist_ok=True)
        os.makedirs(self.snapshots_dir, exist_ok=True)
        os.makedirs(self.backups_dir, exist_ok=True)

    def get_file_content(self, file_path: str) -> Optional[str]:
        if not os.path.exists(file_path):
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            try:
                with open(file_path, "rb") as f:
                    return f.read().decode("utf-8", errors="ignore")
            except Exception:
                return None

    def is_binary_file(self, file_path: str) -> bool:
        """Detect whether a file is binary using a simple heuristic: read the first 1KB and check for NUL bytes."""
        try:
            with open(file_path, "rb") as f:
                chunk = f.read(1024)
            return b"\x00" in chunk
        except Exception:
            return False

    def save_to_trash(self, file_path: str) -> str:
        """Move a deleted file into the trash directory while preserving its full content."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        timestamp = int(time.time() * 1000)
        filename = os.path.basename(file_path)
        trash_filename = f"{timestamp}_{filename}.bak"
        trash_path = os.path.join(self.trash_dir, trash_filename)
        shutil.move(file_path, trash_path)
        return trash_path

    def restore_from_trash(self, trash_path: str, target_path: str) -> bool:
        """Restore a file from the trash directory (move; the original backup disappears)."""
        try:
            if not os.path.exists(trash_path):
                return False
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            shutil.move(trash_path, target_path)
            return True
        except Exception:
            return False

    def save_binary_backup(self, file_path: str) -> str:
        """Copy a binary file in full to the backups directory, saved with a .bak extension, without deleting the original file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        timestamp = int(time.time() * 1000)
        filename = os.path.basename(file_path)
        backup_filename = f"{timestamp}_{filename}.bak"
        backup_path = os.path.join(self.backups_dir, backup_filename)
        shutil.copy2(file_path, backup_path)
        return backup_path

    def restore_binary_backup(self, backup_path: str, target_path: str) -> bool:
        """Copy a .bak file from the backups directory back to the original path, overwriting the current file while keeping the backup."""
        try:
            if not os.path.exists(backup_path):
                return False
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            shutil.copy2(backup_path, target_path)
            return True
        except Exception:
            return False

    def save_diff(self, relative_path: str, diff_content: str) -> str:
        """Save a diff patch into the diffs directory, named by full relative path to avoid same-name conflicts."""
        timestamp = int(time.time() * 1000)
        safe_path = _make_safe_path(relative_path)
        diff_path = os.path.join(self.diffs_dir, f"{timestamp}_{safe_path}.patch")
        with open(diff_path, "w", encoding="utf-8") as f:
            f.write(diff_content)
        return diff_path

    def save_snapshot(self, relative_path: str, content: str) -> str:
        """Save a full snapshot from before file modification for rollback."""
        timestamp = int(time.time() * 1000)
        safe_path = _make_safe_path(relative_path)
        snap_path = os.path.join(self.snapshots_dir, f"{timestamp}_{safe_path}.snap")
        with open(snap_path, "w", encoding="utf-8") as f:
            f.write(content)
        return snap_path

    def save_base(self, relative_path: str, content: str) -> str:
        """Save current content as the baseline for the next comparison, named by full relative path."""
        safe_path = _make_safe_path(relative_path)
        base_path = os.path.join(self.bases_dir, f"{safe_path}.base")
        with open(base_path, "w", encoding="utf-8") as f:
            f.write(content)
        return base_path

    def get_base(self, relative_path: str) -> Optional[str]:
        """Get the baseline content from the previous record."""
        safe_path = _make_safe_path(relative_path)
        base_path = os.path.join(self.bases_dir, f"{safe_path}.base")
        return self.get_file_content(base_path)

    def delete_base(self, relative_path: str) -> bool:
        """Delete the baseline file."""
        safe_path = _make_safe_path(relative_path)
        base_path = os.path.join(self.bases_dir, f"{safe_path}.base")
        if os.path.exists(base_path):
            os.remove(base_path)
            return True
        return False


# -------------------------------------------------------------------
# MiniVCS
# -------------------------------------------------------------------


class MiniVCS:
    """MiniVCS core controller."""

    def __init__(self, project_root: str, vcs_root: Optional[str] = None):
        self.project_root = os.path.abspath(project_root)
        # By default, store data in ~/.openclaw/minivcs/ so it is decoupled from the project directory
        if vcs_root is not None:
            self.vcs_root = os.path.abspath(vcs_root)
        else:
            self.vcs_root = os.path.join(os.path.expanduser("~"), ".openclaw", "minivcs")
        self.log_manager = LogManager(self.vcs_root)
        self.diff_engine = DiffEngine()
        self.file_manager = FileManager(self.vcs_root, self.project_root)

    def _get_relative_path(self, absolute_path: str) -> str:
        if absolute_path.startswith(self.project_root + os.sep):
            return absolute_path[len(self.project_root) + 1 :]
        return absolute_path

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    def record_modify(self, file_path: str) -> Dict[str, Any]:
        """
        Record a file modification (incremental diff + pre-edit snapshot).
        Call it once after each edit; there is no need to call it both before and after:
        - First call (no base): save current content as the baseline; this record has no snapshot
        - Later calls (with base): diff = base -> current, snapshot = base (that is, the pre-edit content), then update base
        After the call, a list of expired records pending cleanup is returned automatically.

        Snapshot chain example (call once after each edit):
          Initial C0 -> record() -> base=C0
          Edit C1    -> record() -> snapshot=C0, base=C1  (R1, can roll back to C0)
          Edit C2    -> record() -> snapshot=C1, base=C2  (R2, can roll back to C1 = state at t1)
          Edit C3    -> record() -> snapshot=C2, base=C3  (R3, can roll back to C2 = state at t2)
        """
        abs_path = os.path.abspath(file_path)
        if not os.path.exists(abs_path):
            return {"success": False, "error": f"File not found: {file_path}"}

        skip_segment = should_skip_path(abs_path)
        if skip_segment:
            return {
                "success": False,
                "skipped": True,
                "reason": f"Path contains '{skip_segment}' which is in the auto-skip list",
            }

        # Binary files: cannot generate diffs, so use a full-copy backup instead (.bak copy, original file kept)
        if self.file_manager.is_binary_file(abs_path):
            return self._record_binary_backup(abs_path)

        try:
            new_content = self.file_manager.get_file_content(abs_path)
            if new_content is None:
                return {"success": False, "error": "Cannot read file content"}

            relative_path = self._get_relative_path(abs_path)
            prev_base = self.file_manager.get_base(relative_path)
            old_content = prev_base if prev_base is not None else ""

            diff_text = self.diff_engine.generate_diff(old_content, new_content)
            diff_summary = self.diff_engine.parse_diff_summary(diff_text)

            if old_content != "" and diff_summary["added"] == 0 and diff_summary["removed"] == 0:
                due = self.query_due_for_cleanup()
                return {"success": True, "message": "No changes detected", "skipped": True, "due_for_cleanup": due}

            diff_path = self.file_manager.save_diff(relative_path, diff_text)

            # When a baseline exists, old_content is the pre-edit content; save it as a snapshot for rollback
            snap_path = None
            if old_content:
                snap_path = self.file_manager.save_snapshot(relative_path, old_content)

            # Update the baseline to the current content
            self.file_manager.save_base(relative_path, new_content)

            retention_days = get_retention_days(abs_path)
            important = is_important_file(abs_path)

            record: Dict[str, Any] = {
                "filePath": relative_path,
                "action": "MODIFY",
                "diffFile": diff_path,
                "summary": diff_summary["summary"],
                "linesAdded": diff_summary["added"],
                "linesRemoved": diff_summary["removed"],
                "isImportant": important,
                "retentionDays": retention_days,
            }
            if snap_path:
                record["snapshotFile"] = snap_path

            record_id = self.log_manager.append_record(record)
            due = self.query_due_for_cleanup()

            return {
                "success": True,
                "recordId": record_id,
                "summary": diff_summary["summary"],
                "diffFile": diff_path,
                "snapshotFile": snap_path,
                "canRollback": snap_path is not None,
                "isImportant": important,
                "retentionDays": retention_days,
                "due_for_cleanup": due,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _record_binary_backup(self, abs_path: str) -> Dict[str, Any]:
        """Binary file backup: copy the current file in full as a .bak, keep the original file, and support later restoration."""
        try:
            relative_path = self._get_relative_path(abs_path)
            important = is_important_file(abs_path)
            retention_days = get_retention_days(abs_path)

            file_size = os.path.getsize(abs_path)
            size_warning = file_size > BINARY_SIZE_WARN_THRESHOLD

            backup_path = self.file_manager.save_binary_backup(abs_path)

            record = {
                "filePath": relative_path,
                "action": "BINARY_BACKUP",
                "backupFile": backup_path,
                "summary": f"Binary file backup ({file_size} bytes)",
                "isImportant": important,
                "retentionDays": retention_days,
            }

            record_id = self.log_manager.append_record(record)
            due = self.query_due_for_cleanup()

            result: Dict[str, Any] = {
                "success": True,
                "recordId": record_id,
                "backupFile": backup_path,
                "summary": record["summary"],
                "canRollback": True,
                "isImportant": important,
                "retentionDays": retention_days,
                "fileSize": file_size,
                "due_for_cleanup": due,
            }
            if size_warning:
                result["sizeWarning"] = True
                result["sizeWarningMessage"] = (
                    f"Binary file is {file_size / 1024 / 1024:.1f} MB, "
                    f"exceeding the {BINARY_SIZE_WARN_THRESHOLD / 1024 / 1024:.0f} MB warning threshold"
                )
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def record_delete(self, file_path: str) -> Dict[str, Any]:
        """
        Record a file deletion by moving the file into trash as a full local copy.
        After the call, a list of expired records pending cleanup is returned automatically.
        """
        abs_path = os.path.abspath(file_path)
        if not os.path.exists(abs_path):
            return {"success": False, "error": f"File not found: {file_path}"}

        skip_segment = should_skip_path(abs_path)
        if skip_segment:
            return {
                "success": False,
                "skipped": True,
                "reason": f"Path contains '{skip_segment}' which is in the auto-skip list",
            }

        try:
            relative_path = self._get_relative_path(abs_path)
            important = is_important_file(abs_path)
            retention_days = get_retention_days(abs_path)

            trash_path = self.file_manager.save_to_trash(abs_path)

            record = {
                "filePath": relative_path,
                "action": "DELETE",
                "trashFile": trash_path,
                "summary": "File moved to trash as a local restore copy",
                "isImportant": important,
                "retentionDays": retention_days,
            }

            record_id = self.log_manager.append_record(record)
            due = self.query_due_for_cleanup()

            return {
                "success": True,
                "recordId": record_id,
                "trashFile": trash_path,
                "message": "File deleted and stored in trash as a local restore copy",
                "isImportant": important,
                "retentionDays": retention_days,
                "due_for_cleanup": due,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ------------------------------------------------------------------
    # Restore / rollback
    # ------------------------------------------------------------------

    def restore_file(self, record_id: str) -> Dict[str, Any]:
        """
        Restore a file:
        - DELETE record: restore the full file from trash
        - MODIFY record: roll back to the pre-edit state using the pre-edit snapshot
        After success, mark the record as RESTORED / ROLLED_BACK.
        """
        record = self.log_manager.get_record_by_id(record_id)
        if not record:
            return {"success": False, "error": "Record not found"}

        action = record.get("action")

        if action == "DELETE":
            trash_file = record.get("trashFile")
            if not trash_file or not os.path.exists(trash_file):
                return {"success": False, "error": "Backup file not found (may have been cleaned up)"}
            # filePath may be relative or absolute
            file_path = record.get("filePath", "")
            target_path = file_path if os.path.isabs(file_path) else os.path.join(self.project_root, file_path)
            success = self.file_manager.restore_from_trash(trash_file, target_path)
            if success:
                # Mark the record as restored to prevent duplicate restore or appearance in the trash list
                self.log_manager.update_record(
                    record_id,
                    {
                        "action": "RESTORED",
                        "restoredAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "trashFile": None,
                    },
                )
                return {"success": True, "message": f"File restored to: {target_path}"}
            return {"success": False, "error": "Failed to restore file from trash"}

        elif action == "MODIFY":
            snap_file = record.get("snapshotFile")
            if not snap_file or not os.path.exists(snap_file):
                return {
                    "success": False,
                    "error": (
                        "No pre-edit snapshot available for this record. "
                        "Rollback is only possible when record_modify was called "
                        "both before AND after the edit."
                    ),
                }
            content = self.file_manager.get_file_content(snap_file)
            if content is None:
                return {"success": False, "error": "Cannot read snapshot file"}
            file_path = record.get("filePath", "")
            target_path = file_path if os.path.isabs(file_path) else os.path.join(self.project_root, file_path)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)
            self.log_manager.update_record(
                record_id,
                {
                    "action": "ROLLED_BACK",
                    "rolledBackAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
            )
            return {"success": True, "message": f"File rolled back to pre-edit state: {target_path}"}

        elif action == "BINARY_BACKUP":
            backup_file = record.get("backupFile")
            if not backup_file or not os.path.exists(backup_file):
                return {"success": False, "error": "Backup file not found (may have been cleaned up)"}
            file_path = record.get("filePath", "")
            target_path = file_path if os.path.isabs(file_path) else os.path.join(self.project_root, file_path)
            success = self.file_manager.restore_binary_backup(backup_file, target_path)
            if success:
                self.log_manager.update_record(
                    record_id,
                    {
                        "action": "ROLLED_BACK",
                        "rolledBackAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    },
                )
                return {"success": True, "message": f"Binary file restored to: {target_path}"}
            return {"success": False, "error": "Failed to restore binary backup"}

        elif action in ("RESTORED", "ROLLED_BACK"):
            return {"success": False, "error": f"This record has already been {action.lower()}"}

        return {"success": False, "error": f"Unknown action: {action}"}

    # ------------------------------------------------------------------
    # Expired cleanup management
    # ------------------------------------------------------------------

    def query_due_for_cleanup(self) -> List[Dict[str, Any]]:
        """
        Scan the full record table and return records whose expireAt <= current time,
        ordered from earliest to latest. Restored/rolled-back records are excluded.
        """
        return self.log_manager.get_due_for_cleanup()

    def extend_record_expiry(self, record_id: str) -> Dict[str, Any]:
        """Extend a record's expiration time by one retention cycle (retentionDays days)."""
        record = self.log_manager.get_record_by_id(record_id)
        if not record:
            return {"success": False, "error": "Record not found"}

        retention_days = record.get("retentionDays", RETENTION_NORMAL_DAYS)
        additional_ms = retention_days * 24 * 60 * 60 * 1000
        ok = self.log_manager.extend_record_expiry(record_id, additional_ms)
        if ok:
            updated = self.log_manager.get_record_by_id(record_id)
            if updated is None:
                return {"success": False, "error": "Failed to reload updated record"}
            return {
                "success": True,
                "recordId": record_id,
                "newExpireAt": updated.get("expireAt"),
                "newExpireAtDatetime": updated.get("expireAtDatetime"),
                "message": f"Expiry extended by {retention_days} days",
            }
        return {"success": False, "error": "Failed to extend expiry"}

    def delete_due_records(self, record_ids: List[str]) -> Dict[str, Any]:
        """Batch-delete expired records that the user has confirmed can be cleaned up (log + physical files)."""
        deleted_records = []
        failed_records = []
        deleted_files: List[str] = []

        for record_id in record_ids:
            result = self.delete_record_by_id(record_id, delete_files=True)
            if result.get("success"):
                deleted_records.append(record_id)
                deleted_files.extend(result.get("deleted_files", []))
            else:
                failed_records.append({"recordId": record_id, "error": result.get("error")})

        return {
            "success": True,
            "deleted_count": len(deleted_records),
            "deleted_records": deleted_records,
            "failed_records": failed_records,
            "deleted_files": deleted_files,
        }

    # ------------------------------------------------------------------
    # Query / history
    # ------------------------------------------------------------------

    def get_history(self, file_path: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        if file_path:
            abs_path = os.path.abspath(file_path)
            relative_path = self._get_relative_path(abs_path)
            history = self.log_manager.get_history_by_file(relative_path)
        else:
            history = self.log_manager.get_all_history()
        return history[:limit]

    def get_file_diff(self, record_id: str) -> Optional[str]:
        record = self.log_manager.get_record_by_id(record_id)
        if not record or record.get("action") != "MODIFY":
            return None
        diff_file = record.get("diffFile")
        if not diff_file or not os.path.exists(diff_file):
            return None
        return self.file_manager.get_file_content(diff_file)

    def query_expired(self, days: int) -> List[Dict[str, Any]]:
        """Compatibility for the old interface: query expired records by fixed days."""
        return self.log_manager.get_expired_records(days)

    def clean_expired(self, days: int, delete_files: bool = False) -> Dict[str, Any]:
        """Compatibility for the old interface: clean expired records."""
        expired = self.log_manager.get_expired_records(days)
        deleted_files = []
        if delete_files:
            for record in expired:
                diff_file = record.get("diffFile")
                if diff_file and os.path.exists(diff_file):
                    os.remove(diff_file)
                    deleted_files.append(diff_file)
        result = self.log_manager.clean_expired_records(days)
        result["deleted_files"] = deleted_files
        return result

    def list_trash(self) -> List[Dict[str, Any]]:
        """List deleted files in trash that have not yet been restored."""
        records = self.log_manager.get_all_history()
        return [
            {
                "recordId": r.get("recordId"),
                "filePath": r.get("filePath"),
                "datetime": r.get("datetime"),
                "trashFile": r.get("trashFile"),
                "isImportant": r.get("isImportant", False),
                "retentionDays": r.get("retentionDays", RETENTION_NORMAL_DAYS),
                "expireAtDatetime": r.get("expireAtDatetime"),
            }
            for r in records
            if r.get("action") == "DELETE"
        ]

    def delete_record_by_id(self, record_id: str, delete_files: bool = True) -> Dict[str, Any]:
        """Delete the specified record (log + physical files)."""
        record = self.log_manager.get_record_by_id(record_id)
        if not record:
            return {"success": False, "error": "Record not found"}

        deleted_files = []

        if delete_files:
            # Delete diff file
            diff_file = record.get("diffFile")
            if diff_file and os.path.exists(diff_file):
                os.remove(diff_file)
                deleted_files.append(diff_file)

            # Delete trash backup
            trash_file = record.get("trashFile")
            if trash_file and os.path.exists(trash_file):
                os.remove(trash_file)
                deleted_files.append(trash_file)

            # Delete snapshot file
            snap_file = record.get("snapshotFile")
            if snap_file and os.path.exists(snap_file):
                os.remove(snap_file)
                deleted_files.append(snap_file)

            # Delete binary backup file
            backup_file = record.get("backupFile")
            if backup_file and os.path.exists(backup_file):
                os.remove(backup_file)
                deleted_files.append(backup_file)

            # Delete the base file only when no other MODIFY records exist for this file
            file_path = record.get("filePath")
            if file_path and record.get("action") == "MODIFY":
                remaining = [
                    r
                    for r in self.log_manager.get_history_by_file(file_path)
                    if r.get("action") == "MODIFY" and r.get("recordId") != record_id
                ]
                if not remaining:
                    self.file_manager.delete_base(file_path)

        self.log_manager.delete_record(record_id)
        return {
            "success": True,
            "deleted_record": record_id,
            "deleted_files": deleted_files,
            "message": f"Record {record_id} deleted",
        }

    def merge_modify(self, file_path: str, keep_record_id: Optional[str] = None) -> Dict[str, Any]:
        """Merge multiple modification records for the same file, keeping the latest one by default."""
        abs_path = os.path.abspath(file_path)
        relative_path = self._get_relative_path(abs_path)

        records = self.log_manager.get_history_by_file(relative_path, descending=True)
        modify_records = [r for r in records if r.get("action") == "MODIFY"]

        if len(modify_records) <= 1:
            return {"success": False, "error": "No need to merge (only one or zero record)"}

        if keep_record_id:
            keep_record = next((r for r in modify_records if r.get("recordId") == keep_record_id), None)
            if not keep_record:
                return {"success": False, "error": "Record not found"}
        else:
            keep_record = modify_records[0]

        deleted_count = 0
        deleted_files = []
        for r in modify_records:
            if r.get("recordId") == keep_record.get("recordId"):
                continue
            rid = r.get("recordId")
            if isinstance(rid, str) and self.log_manager.delete_record(rid):
                deleted_count += 1
            for fkey in ("diffFile", "snapshotFile"):
                f = r.get(fkey)
                if f and os.path.exists(f):
                    os.remove(f)
                    deleted_files.append(f)

        return {
            "success": True,
            "kept_record": keep_record.get("recordId"),
            "deleted_count": deleted_count,
            "deleted_files": deleted_files,
            "message": f"Merged {deleted_count} records, kept latest: {keep_record.get('recordId')}",
        }


# -------------------------------------------------------------------
# CLI output helpers
# -------------------------------------------------------------------


def print_records(records: list, show_diff: bool = False, vcs: Optional[MiniVCS] = None):
    if not records:
        print("No records found.")
        return
    for i, record in enumerate(records):
        important_tag = " [IMPORTANT]" if record.get("isImportant") else ""
        action = record.get("action", "")
        rollback_tag = " [rollback available]" if action == "MODIFY" and record.get("snapshotFile") else ""
        print(f"\n[{i + 1}] Record ID: {record.get('recordId')}")
        print(f"    File    : {record.get('filePath')}{important_tag}")
        print(f"    Action  : {action}{rollback_tag}")
        print(f"    Time    : {record.get('datetime')}")
        print(f"    Summary : {record.get('summary')}")
        print(f"    Expires : {record.get('expireAtDatetime', 'N/A')}  (retention {record.get('retentionDays', '?')}d)")
        if show_diff and vcs and action == "MODIFY":
            diff_content = vcs.get_file_diff(record.get("recordId"))
            if diff_content:
                print("\n    Diff Content:")
                print("    " + "-" * 40)
                for line in diff_content.splitlines()[:30]:
                    print(f"    {line}")


def print_due_for_cleanup(due: list):
    if not due:
        return
    print(f"\n{'=' * 50}")
    print(f"  [CLEANUP NOTICE] {len(due)} record(s) have expired and are pending cleanup:")
    for i, r in enumerate(due):
        important_tag = " [IMPORTANT]" if r.get("isImportant") else ""
        print(f"  [{i + 1}] ID={r.get('recordId')}  File={r.get('filePath')}{important_tag}")
        print(f"       Action={r.get('action')}  Created={r.get('datetime')}  Expired={r.get('expireAtDatetime')}")
    print("  Use 'cleanup --confirm' to delete, or 'extend <record_id>' to postpone.")
    print(f"{'=' * 50}")


# -------------------------------------------------------------------
# CLI entry
# -------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="MiniVCS - lightweight file version management system")
    parser.add_argument(
        "command",
        choices=["record", "delete", "history", "restore", "expired", "trash", "remove", "cleanup", "extend"],
        help="Command",
    )
    parser.add_argument("file", nargs="?", help="File path or Record ID")
    parser.add_argument("-n", "--limit", type=int, default=10, help="Record count limit")
    parser.add_argument("-d", "--show-diff", action="store_true", help="Show diff content")
    parser.add_argument("-c", "--clean", action="store_true", help="Clean expired records (used with the expired command)")
    parser.add_argument("--delete-files", action="store_true", help="Delete physical files as well")
    parser.add_argument("--confirm", action="store_true", help="Confirm cleanup execution (used with the cleanup command)")
    parser.add_argument("--project-root", default=os.getcwd(), help="Project root directory (used to compute relative paths)")
    parser.add_argument("--vcs-root", default=None, help="VCS data storage directory (default: ~/.openclaw/minivcs)")

    args = parser.parse_args()

    try:
        vcs = MiniVCS(args.project_root, vcs_root=args.vcs_root)
    except Exception as e:
        print(f"Error: Failed to initialize MiniVCS: {e}")
        return 1

    if args.command == "record":
        if not args.file:
            print("Error: Please specify a file to record")
            return 1
        if not os.path.exists(args.file):
            print(f"Error: File not found: {args.file}")
            return 1
        result = vcs.record_modify(args.file)
        if result.get("skipped") and not result.get("success"):
            print(f"~ Skipped: {result.get('reason')}")
        elif result.get("success"):
            if result.get("skipped"):
                print("~ No changes detected, skipped.")
            elif result.get("action") == "BINARY_BACKUP" or result.get("backupFile"):
                print("✓ Binary file backed up! (.bak copy saved)")
                print(f"  Record ID  : {result.get('recordId')}")
                print(f"  Backup     : {result.get('backupFile')}")
                print(f"  Summary    : {result.get('summary')}")
                important_tag = " [IMPORTANT]" if result.get("isImportant") else ""
                print(f"  Retention  : {result.get('retentionDays')} days{important_tag}")
                print(f"  Rollback   : available (use restore {result.get('recordId')})")
                if result.get("sizeWarning"):
                    print(f"  ⚠ WARNING  : {result.get('sizeWarningMessage')}")
            else:
                print("✓ File change recorded!")
                print(f"  Record ID  : {result.get('recordId')}")
                print(f"  Summary    : {result.get('summary')}")
                important_tag = " [IMPORTANT]" if result.get("isImportant") else ""
                print(f"  Retention  : {result.get('retentionDays')} days{important_tag}")
                if result.get("canRollback"):
                    print(f"  Rollback   : available (use restore {result.get('recordId')})")
            print_due_for_cleanup(result.get("due_for_cleanup", []))
        else:
            print(f"✗ Failed: {result.get('error')}")
            return 1

    elif args.command == "delete":
        if not args.file:
            print("Error: Please specify a file to delete")
            return 1
        if not os.path.exists(args.file):
            print(f"Error: File not found: {args.file}")
            return 1
        result = vcs.record_delete(args.file)
        if result.get("skipped") and not result.get("success"):
            print(f"~ Skipped: {result.get('reason')}")
        elif result.get("success"):
            print("✓ File deleted and backed up!")
            print(f"  Record ID  : {result.get('recordId')}")
            print(f"  Backup     : {result.get('trashFile')}")
            important_tag = " [IMPORTANT]" if result.get("isImportant") else ""
            print(f"  Retention  : {result.get('retentionDays')} days{important_tag}")
            print_due_for_cleanup(result.get("due_for_cleanup", []))
        else:
            print(f"✗ Failed: {result.get('error')}")
            return 1

    elif args.command == "history":
        records = vcs.get_history(args.file, args.limit)
        if args.file:
            print(f"\n=== History for: {args.file} ===")
        else:
            print(f"\n=== All History (latest {args.limit} records) ===")
        print_records(records, args.show_diff, vcs)

    elif args.command == "restore":
        if not args.file:
            print("Error: Please specify a record ID to restore/rollback")
            return 1
        result = vcs.restore_file(args.file)
        if result.get("success"):
            print(f"✓ {result.get('message')}")
        else:
            print(f"✗ Failed: {result.get('error')}")
            return 1

    elif args.command == "expired":
        if not args.file:
            print("Error: Please specify number of days")
            return 1
        try:
            days = int(args.file)
        except ValueError:
            print("Error: Days must be a number")
            return 1
        if args.clean:
            result = vcs.clean_expired(days, args.delete_files)
            print(f"\n=== Cleaned Expired Records (>{days} days) ===")
            print(f"Records deleted: {result.get('deleted_count')}")
            if args.delete_files and result.get("deleted_files"):
                print(f"Diff files deleted: {len(result.get('deleted_files', []))}")
        else:
            records = vcs.query_expired(days)
            print(f"\n=== Expired Records (>{days} days) ===")
            print(f"Total: {len(records)} records")
            print_records(records)

    elif args.command == "trash":
        files = vcs.list_trash()
        print("\n=== Trash Bin ===")
        if not files:
            print("Trash is empty.")
            return 0
        for i, f in enumerate(files):
            important_tag = " [IMPORTANT]" if f.get("isImportant") else ""
            print(f"\n[{i + 1}] {f.get('filePath')}{important_tag}")
            print(f"    Deleted at : {f.get('datetime')}")
            print(f"    Expires at : {f.get('expireAtDatetime', 'N/A')}")
            print(f"    Record ID  : {f.get('recordId')}")

    elif args.command == "remove":
        if not args.file:
            print("Error: Please specify a record ID to remove")
            print("  Use 'history' command to see record IDs")
            return 1
        result = vcs.delete_record_by_id(args.file)
        if result.get("success"):
            print("✓ Record removed successfully!")
            print(f"  {result.get('message')}")
        else:
            print(f"✗ Failed: {result.get('error')}")
            return 1

    elif args.command == "cleanup":
        due = vcs.query_due_for_cleanup()
        if not due:
            print("✓ No records due for cleanup.")
            return 0
        print(f"\n=== Records Due for Cleanup ({len(due)} total, oldest first) ===")
        print_records(due, vcs=vcs)
        if args.confirm:
            record_ids = [rid for r in due if isinstance((rid := r.get("recordId")), str)]
            result = vcs.delete_due_records(record_ids)
            print(f"\n✓ Cleanup complete: {result.get('deleted_count')} records deleted.")
            if result.get("failed_records"):
                print(f"  Failed: {result.get('failed_records')}")
        else:
            print("\n  To delete these records, run with --confirm")
            print("  To postpone a record, run: extend <record_id>")

    elif args.command == "extend":
        if not args.file:
            print("Error: Please specify a record ID to extend")
            return 1
        result = vcs.extend_record_expiry(args.file)
        if result.get("success"):
            print("✓ Expiry extended!")
            print(f"  Record ID     : {result.get('recordId')}")
            print(f"  New expire at : {result.get('newExpireAtDatetime')}")
            print(f"  {result.get('message')}")
        else:
            print(f"✗ Failed: {result.get('error')}")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
