#!/usr/bin/env python3
"""
Folder sync manager for NotebookLM.
Scans local folders, tracks file changes, and syncs to NotebookLM notebooks.
"""

import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

from config import DATA_DIR

SUPPORTED_EXTENSIONS = {'.pdf', '.txt', '.md', '.docx', '.html', '.epub'}

# Ensure sync directory exists
SYNC_DIR = DATA_DIR / "sync"
SYNC_DIR.mkdir(parents=True, exist_ok=True)


class SyncAction(Enum):
    """Sync action types."""
    ADD = "add"
    UPDATE = "update"
    SKIP = "skip"
    DELETE = "delete"


@dataclass
class TrackedFile:
    """Represents a tracked file in the sync state."""
    filename: str
    hash: str
    modified_at: str
    source_id: Optional[str] = None
    uploaded_at: Optional[str] = None


@dataclass
class SyncState:
    """Represents the sync tracking state."""
    version: int = 1
    folder_path: str = ""
    notebook_id: Optional[str] = None
    notebook_url: Optional[str] = None
    account_index: Optional[int] = None
    account_email: Optional[str] = None
    last_sync_at: Optional[str] = None
    files: dict[str, TrackedFile] = field(default_factory=dict)


class SyncManager:
    """Manages folder-to-notebook synchronization."""

    def __init__(self, folder_path: str):
        self.folder_path = Path(folder_path).resolve()
        # Store tracking file in data/sync/ (not in the synced folder!)
        folder_hash = hashlib.md5(str(self.folder_path).encode()).hexdigest()[:12]
        self.tracking_file = SYNC_DIR / f"{folder_hash}.sync.json"
        self.state = SyncState(folder_path=str(self.folder_path))

    def load_state(self) -> bool:
        """Load sync state from tracking file.

        Returns:
            True if state loaded successfully (creates fresh state if file doesn't exist or is corrupted)
        """
        if not self.tracking_file.exists():
            # Create fresh state for new sync folder
            self.state = SyncState(folder_path=str(self.folder_path))
            return True

        try:
            data = json.loads(self.tracking_file.read_text())

            # Validate version
            if data.get("version") != 1:
                raise ValueError(f"Unsupported tracking file version: {data.get('version')}")

            # Reconstruct state
            self.state = SyncState(
                version=data.get("version", 1),
                folder_path=data.get("folder_path", str(self.folder_path)),
                notebook_id=data.get("notebook_id"),
                notebook_url=data.get("notebook_url"),
                account_index=data.get("account_index"),
                account_email=data.get("account_email"),
                last_sync_at=data.get("last_sync_at"),
            )

            # Reconstruct file entries
            for path, file_data in data.get("files", {}).items():
                self.state.files[path] = TrackedFile(
                    filename=file_data.get("filename", ""),
                    hash=file_data.get("hash", ""),
                    modified_at=file_data.get("modified_at", ""),
                    source_id=file_data.get("source_id"),
                    uploaded_at=file_data.get("uploaded_at"),
                )

            return True

        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️ Error loading tracking file: {e}")
            # Backup corrupted file
            broken = self.tracking_file.with_suffix(".json.broken")
            if not broken.exists():
                self.tracking_file.replace(broken)
                print(f"   Backed up corrupted file to: {broken}")
            # Create fresh state
            self.state = SyncState(folder_path=str(self.folder_path))
            return True

    def save_state(self) -> bool:
        """Save sync state to tracking file.

        Returns:
            True if saved successfully, False on error
        """
        try:
            data = {
                "version": self.state.version,
                "folder_path": self.state.folder_path,
                "notebook_id": self.state.notebook_id,
                "notebook_url": self.state.notebook_url,
                "account_index": self.state.account_index,
                "account_email": self.state.account_email,
                "last_sync_at": self.state.last_sync_at,
                "files": {}
            }

            for path, file_info in self.state.files.items():
                data["files"][path] = {
                    "filename": file_info.filename,
                    "hash": file_info.hash,
                    "modified_at": file_info.modified_at,
                    "source_id": file_info.source_id,
                    "uploaded_at": file_info.uploaded_at,
                }

            # Atomic write via temp file
            temp_file = self.tracking_file.with_suffix(".json.tmp")
            temp_file.write_text(json.dumps(data, indent=2))
            temp_file.replace(self.tracking_file)
            return True

        except Exception as e:
            print(f"❌ Error saving tracking file: {e}")
            return False

    def scan_folder(self) -> dict[str, dict]:
        """Scan folder for supported files.

        Returns:
            Dict mapping relative path -> file info dict with:
            - path: relative path from folder
            - absolute_path: full path
            - filename: file stem (without extension)
            - extension: file extension
            - modified_at: ISO timestamp
            - size: file size in bytes
        """
        files = {}

        if not self.folder_path.exists():
            print(f"⚠️ Folder does not exist: {self.folder_path}")
            return files

        for root, dirs, filenames in os.walk(self.folder_path):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for filename in filenames:
                # Skip hidden files
                if filename.startswith('.'):
                    continue

                path = Path(root) / filename
                relative_path = path.relative_to(self.folder_path)

                # Check extension
                ext = path.suffix.lower()
                if ext not in SUPPORTED_EXTENSIONS:
                    continue

                try:
                    stat = path.stat()
                    # Normalize paths to POSIX format for cross-platform portability
                    posix_path = relative_path.as_posix()
                    files[posix_path] = {
                        "path": posix_path,
                        "absolute_path": str(path),
                        "filename": path.stem,
                        "extension": ext,
                        "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "size": stat.st_size,
                    }
                except OSError as e:
                    print(f"⚠️ Could not access {path}: {e}")

        print(f"📁 Found {len(files)} supported files in {self.folder_path}")
        return files

    def compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA-256 hash of a file.

        Returns:
            Hash string prefixed with algorithm name, e.g., "sha256:abc123..."
        """
        sha256 = hashlib.sha256()

        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)

        return f"sha256:{sha256.hexdigest()}"

    def get_sync_plan(self, local_files: dict[str, dict]) -> list[dict]:
        """Generate sync plan comparing local files with tracking state.

        Args:
            local_files: Dict from scan_folder() with file info

        Returns:
            List of sync actions with:
            - action: SyncAction value
            - path: relative file path
            - local_info: file info from local_files
            - tracked_info: previous tracking info (if exists)
            - source_id: existing source ID for update/delete (if exists)
        """
        plan = []

        # Check each local file
        for path, local_info in local_files.items():
            # Compute hash for comparison
            abs_path = Path(local_info["absolute_path"])
            current_hash = self.compute_file_hash(abs_path)
            local_info["hash"] = current_hash

            if path not in self.state.files:
                # New file - needs addition
                plan.append({
                    "action": SyncAction.ADD.value,
                    "path": path,
                    "local_info": local_info,
                    "tracked_info": None,
                    "source_id": None,
                })
            else:
                tracked = self.state.files[path]

                if tracked.hash != current_hash:
                    # Content changed - needs update
                    if tracked.source_id:
                        plan.append({
                            "action": SyncAction.UPDATE.value,
                            "path": path,
                            "local_info": local_info,
                            "tracked_info": tracked,
                            "source_id": tracked.source_id,
                        })
                    else:
                        # No existing source, treat as add
                        plan.append({
                            "action": SyncAction.ADD.value,
                            "path": path,
                            "local_info": local_info,
                            "tracked_info": tracked,
                            "source_id": None,
                        })
                else:
                    # Unchanged - skip
                    plan.append({
                        "action": SyncAction.SKIP.value,
                        "path": path,
                        "local_info": local_info,
                        "tracked_info": tracked,
                        "source_id": tracked.source_id,
                    })

        # Check for deleted files (in tracking but not in local)
        for path in self.state.files:
            if path not in local_files:
                plan.append({
                    "action": SyncAction.DELETE.value,
                    "path": path,
                    "local_info": None,
                    "tracked_info": self.state.files[path],
                    "source_id": self.state.files[path].source_id,
                })

        return plan

    async def execute_sync(
        self,
        notebook_id: str,
        account_index: int,
        account_email: str,
        dry_run: bool = False,
    ) -> dict:
        """Execute full sync workflow.

        Args:
            notebook_id: Target NotebookLM notebook ID
            account_index: Active Google account index
            account_email: Active Google account email
            dry_run: If True, only show plan without executing

        Returns:
            Dict with sync results: add, update, skip, delete, errors
        """
        from notebooklm_wrapper import NotebookLMWrapper

        self.load_state()
        self._warn_if_account_mismatch(account_index, account_email)

        local_files = self.scan_folder()
        plan = self.get_sync_plan(local_files)

        self._print_sync_plan(plan, dry_run)
        if dry_run:
            return self._summarize_plan(plan)

        async with NotebookLMWrapper() as wrapper:
            result = await self._execute_plan(wrapper, plan, notebook_id)

        self._update_state_after_sync(notebook_id, account_index, account_email)
        return result

    def _warn_if_account_mismatch(self, account_index: int, account_email: str):
        """Warn if current account differs from tracking file account."""
        if self.state.account_index is not None and self.state.account_index != account_index:
            print(f"⚠️ Tracking file was created with account [{self.state.account_index}] {self.state.account_email}")
            print(f"   Current active account: [{account_index}] {account_email}")
            print("   Continuing with new account (tracking file will be updated)")

    def _update_state_after_sync(self, notebook_id: str, account_index: int, account_email: str):
        """Update tracking state after successful sync."""
        self.state.notebook_id = notebook_id
        self.state.account_index = account_index
        self.state.account_email = account_email
        self.state.last_sync_at = datetime.now(timezone.utc).isoformat()
        self.save_state()

    async def _execute_plan(
        self,
        wrapper,
        plan: list[dict],
        notebook_id: str,
        dry_run: bool = False,
    ) -> dict:
        """Execute sync plan using NotebookLMWrapper.

        Args:
            wrapper: NotebookLMWrapper instance
            plan: List of sync actions
            notebook_id: Target notebook ID
            dry_run: If True, don't actually modify anything

        Returns:
            Dict with sync results
        """
        result = {"add": 0, "update": 0, "skip": 0, "delete": 0, "errors": []}

        for item in plan:
            action = item["action"]
            path = item["path"]
            local_info = item["local_info"]

            if action == SyncAction.SKIP.value:
                result["skip"] += 1
                continue

            if dry_run:
                print(f"   [DRY-RUN] {action.upper()} {path}")
                continue

            try:
                if action == SyncAction.ADD.value:
                    print(f"   ➕ Adding: {path}")
                    source_id = await self._upload_file(wrapper, notebook_id, local_info)
                    self._update_tracked_file(path, local_info, source_id)
                    result["add"] += 1

                elif action == SyncAction.UPDATE.value:
                    print(f"   🔄 Updating: {path}")
                    old_source_id = item["source_id"]
                    if old_source_id:
                        await wrapper.delete_source(notebook_id, old_source_id)
                    source_id = await self._upload_file(wrapper, notebook_id, local_info)
                    self._update_tracked_file(path, local_info, source_id)
                    result["update"] += 1

                elif action == SyncAction.DELETE.value:
                    print(f"   🗑️ Deleting remote: {path}")
                    source_id = item["source_id"]
                    if source_id:
                        await wrapper.delete_source(notebook_id, source_id)
                    del self.state.files[path]
                    result["delete"] += 1

            except Exception as e:
                print(f"   ❌ Error {action} {path}: {e}")
                result["errors"].append({"path": path, "action": action, "error": str(e)})

        return result

    async def _upload_file(self, wrapper, notebook_id: str, local_info: dict) -> Optional[str]:
        """Upload a single file to NotebookLM.

        Args:
            wrapper: NotebookLMWrapper instance
            notebook_id: Target notebook ID
            local_info: File info dict with absolute_path

        Returns:
            Source ID from upload response
        """
        file_path = Path(local_info["absolute_path"])
        upload_result = await wrapper.add_file(notebook_id, file_path)
        return upload_result.get("source_id")

    def _update_tracked_file(self, path: str, local_info: dict, source_id: Optional[str]):
        """Update or create a tracked file entry in state.

        Args:
            path: Relative file path
            local_info: File info dict with filename, hash, modified_at
            source_id: Source ID from NotebookLM
        """
        self.state.files[path] = TrackedFile(
            filename=local_info["filename"],
            hash=local_info["hash"],
            modified_at=local_info["modified_at"],
            source_id=source_id,
            uploaded_at=datetime.now(timezone.utc).isoformat(),
        )

    def _print_sync_plan(self, plan: list[dict], dry_run: bool = False):
        """Print formatted sync plan.

        Args:
            plan: List of sync actions
            dry_run: If True, show dry-run indicator
        """
        prefix = "🔍 [DRY-RUN] " if dry_run else "📋 Sync Plan:"
        print(f"\n{prefix}")

        counts = {"add": 0, "update": 0, "skip": 0, "delete": 0}
        for item in plan:
            action = item["action"]
            path = item["path"]
            counts[action] += 1
            symbol = {"add": "➕", "update": "🔄", "skip": "✓", "delete": "🗑️"}[action]
            print(f"   {symbol} {path:<30} [{action.upper()}]")

        print(f"\n   Total: {counts['add']} add, {counts['update']} update, {counts['skip']} skip, {counts['delete']} delete")

    def _summarize_plan(self, plan: list[dict]) -> dict:
        """Summarize plan without executing.

        Args:
            plan: List of sync actions

        Returns:
            Dict with counts by action type
        """
        result = {"add": 0, "update": 0, "skip": 0, "delete": 0, "errors": []}
        for item in plan:
            result[item["action"]] += 1
        return result