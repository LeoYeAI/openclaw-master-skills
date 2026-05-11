#!/usr/bin/env python3
"""
Shared Blackboard - Agent Coordination State Manager (Atomic Commit Edition)

A markdown-based shared state system for multi-agent coordination.
Stores key-value pairs with optional TTL (time-to-live) expiration.

FEATURES:
  - File Locking: Prevents race conditions in multi-agent environments
  - Staging Area: propose → validate → commit workflow
  - Atomic Commits: Changes are all-or-nothing

Usage:
    python blackboard.py write KEY VALUE [--ttl SECONDS]
    python blackboard.py read KEY
    python blackboard.py delete KEY
    python blackboard.py list
    python blackboard.py snapshot
    
    # Atomic commit workflow:
    python blackboard.py propose CHANGE_ID KEY VALUE [--ttl SECONDS]
    python blackboard.py validate CHANGE_ID
    python blackboard.py commit CHANGE_ID
    python blackboard.py abort CHANGE_ID
    python blackboard.py list-pending

Examples:
    python blackboard.py write "task:analysis" '{"status": "running"}'
    python blackboard.py write "cache:data" '{"value": 123}' --ttl 3600
    python blackboard.py read "task:analysis"
    python blackboard.py list
    
    # Safe multi-agent update:
    python blackboard.py propose "chg_001" "order:123" '{"status": "approved"}'
    python blackboard.py validate "chg_001"  # Orchestrator checks for conflicts
    python blackboard.py commit "chg_001"    # Apply atomically
"""

import argparse
import json
import os
import re
import sys
import time
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from contextlib import contextmanager

# Try to import fcntl (Unix only), fall back to file-based locking on Windows
_fcntl: Any = None
try:
    import fcntl as _fcntl_import
    _fcntl = _fcntl_import
except ImportError:
    pass  # fcntl unavailable on Windows; file-based lock fallback is used instead

# Default blackboard location
BLACKBOARD_PATH = Path(__file__).parent.parent / "swarm-blackboard.md"
LOCK_PATH = Path(__file__).parent.parent / "data" / ".blackboard.lock"
PENDING_DIR = Path(__file__).parent.parent / "data" / "pending_changes"

# Lock timeout settings
LOCK_TIMEOUT_SECONDS = 10
LOCK_RETRY_INTERVAL = 0.1


class FileLock:
    """
    Cross-platform file lock for preventing race conditions.
    Uses fcntl on Unix, fallback to lock file on Windows.
    """
    
    def __init__(self, lock_path: Path, timeout: float = LOCK_TIMEOUT_SECONDS):
        self.lock_path = lock_path
        self.timeout = timeout
        self.lock_file: Optional[Any] = None
        self.lock_marker: Optional[Path] = None
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
    
    def acquire(self) -> bool:
        """Acquire the lock with timeout."""
        start_time = time.time()
        
        while True:
            try:
                self.lock_file = open(self.lock_path, 'w')
                
                if _fcntl is not None:
                    # Unix/Linux/Mac - use fcntl
                    _fcntl.flock(self.lock_file.fileno(), _fcntl.LOCK_EX | _fcntl.LOCK_NB)
                else:
                    # Windows fallback: use lock marker file
                    self.lock_marker = self.lock_path.with_suffix('.locked')
                    if self.lock_marker.exists():
                        # Check if stale (older than timeout)
                        age = time.time() - self.lock_marker.stat().st_mtime
                        if age < self.timeout:
                            self.lock_file.close()
                            raise BlockingIOError("Lock held by another process")
                        # Stale lock, remove it
                        self.lock_marker.unlink()
                    self.lock_marker.write_text(str(time.time()))
                
                # Write lock holder info
                self.lock_file.write(json.dumps({
                    "pid": os.getpid(),
                    "acquired_at": datetime.now(timezone.utc).isoformat()
                }))
                self.lock_file.flush()
                return True
                
            except (BlockingIOError, OSError):
                if self.lock_file:
                    self.lock_file.close()
                    self.lock_file = None
                if time.time() - start_time > self.timeout:
                    return False
                time.sleep(LOCK_RETRY_INTERVAL)
    
    def release(self) -> None:
        """Release the lock."""
        if self.lock_file:
            try:
                if _fcntl is not None:
                    _fcntl.flock(self.lock_file.fileno(), _fcntl.LOCK_UN)
                elif self.lock_marker and self.lock_marker.exists():
                    self.lock_marker.unlink()
                
                self.lock_file.close()
            except Exception:
                pass  # best-effort unlock; fd and marker cleaned up in finally
            finally:
                self.lock_file = None
                self.lock_marker = None


@contextmanager
def blackboard_lock(lock_path: Path = LOCK_PATH):
    """Context manager for atomic blackboard access."""
    lock = FileLock(lock_path)
    if not lock.acquire():
        raise TimeoutError(
            f"Could not acquire blackboard lock within {LOCK_TIMEOUT_SECONDS}s. "
            "Another agent may be holding it. Retry later."
        )
    try:
        yield
    finally:
        lock.release()


class SharedBlackboard:
    """Markdown-based shared state for agent coordination with atomic commits."""
    
    def __init__(self, path: Path = BLACKBOARD_PATH):
        self.path = path
        self.cache: dict[str, dict[str, Any]] = {}
        self.pending_dir = PENDING_DIR
        self.pending_dir.mkdir(parents=True, exist_ok=True)
        self._initialize()
        self._load_from_disk()
    
    def _initialize(self):
        """Create blackboard file if it doesn't exist."""
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            initial_content = f"""# Swarm Blackboard
Last Updated: {datetime.now(timezone.utc).isoformat()}

## Active Tasks
| TaskID | Agent | Status | Started | Description |
|--------|-------|--------|---------|-------------|

## Knowledge Cache
<!-- Cached results from agent operations -->

## Coordination Signals
<!-- Agent availability status -->

## Execution History
<!-- Chronological log of completed tasks -->
"""
            self.path.write_text(initial_content, encoding="utf-8")
    
    def _load_from_disk(self):
        """Load entries from the markdown blackboard."""
        try:
            content = self.path.read_text(encoding="utf-8")
            
            # Parse Knowledge Cache section
            cache_match = re.search(
                r'## Knowledge Cache\n([\s\S]*?)(?=\n## |$)', 
                content
            )
            
            if cache_match:
                cache_section = cache_match.group(1)
                # Find all entries: ### key\n{json}
                entries = re.findall(
                    r'### (\S+)\n([\s\S]*?)(?=\n### |$)',
                    cache_section
                )
                
                for key, value_str in entries:
                    try:
                        entry = json.loads(value_str.strip())
                        self.cache[key] = entry
                    except json.JSONDecodeError:
                        # Skip malformed entries
                        pass
        except Exception as e:
            print(f"Warning: Failed to load blackboard: {e}", file=sys.stderr)
    
    def _persist_to_disk(self):
        """Save entries to the markdown blackboard."""
        sections = [
            "# Swarm Blackboard",
            f"Last Updated: {datetime.now(timezone.utc).isoformat()}",
            "",
            "## Active Tasks",
            "| TaskID | Agent | Status | Started | Description |",
            "|--------|-------|--------|---------|-------------|",
            "",
            "## Knowledge Cache",
        ]
        
        # Clean expired entries and write valid ones
        for key, entry in list(self.cache.items()):
            if self._is_expired(entry):
                del self.cache[key]
                continue
            
            sections.append(f"### {key}")
            sections.append(json.dumps(entry, indent=2))
            sections.append("")
        
        sections.extend([
            "## Coordination Signals",
            "",
            "## Execution History",
        ])
        
        self.path.write_text("\n".join(sections), encoding="utf-8")
    
    def _is_expired(self, entry: dict[str, Any]) -> bool:
        """Check if an entry has expired based on TTL."""
        ttl = entry.get("ttl")
        if ttl is None:
            return False
        
        timestamp = entry.get("timestamp")
        if not timestamp:
            return False
        
        try:
            created = datetime.fromisoformat(str(timestamp).replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            elapsed = (now - created).total_seconds()
            return elapsed > ttl
        except Exception:
            return False
    
    def read(self, key: str) -> Optional[dict[str, Any]]:
        """Read an entry from the blackboard."""
        entry = self.cache.get(key)
        if entry is None:
            return None
        
        if self._is_expired(entry):
            del self.cache[key]
            self._persist_to_disk()
            return None
        
        return entry
    
    def write(self, key: str, value: Any, source_agent: str = "unknown", 
              ttl: Optional[int] = None) -> dict[str, Any]:
        """Write an entry to the blackboard (with file locking)."""
        entry: dict[str, Any] = {
            "key": key,
            "value": value,
            "source_agent": source_agent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ttl": ttl,
        }
        
        with blackboard_lock():
            # Reload to get latest state
            self._load_from_disk()
            self.cache[key] = entry
            self._persist_to_disk()
        
        return entry
    
    def delete(self, key: str) -> bool:
        """Delete an entry from the blackboard (with file locking)."""
        with blackboard_lock():
            self._load_from_disk()
            if key in self.cache:
                del self.cache[key]
                self._persist_to_disk()
                return True
        return False
    
    # ========================================================================
    # ATOMIC COMMIT WORKFLOW: propose → validate → commit
    # ========================================================================

    @staticmethod
    def _sanitize_change_id(change_id: str) -> str:
        """
        Sanitize change_id to prevent path traversal attacks.
        Only allows alphanumeric characters, hyphens, underscores, and dots.
        Rejects any path separators or parent directory references.
        """
        if not change_id:
            raise ValueError("change_id must be a non-empty string")
        # Strip whitespace
        sanitized = change_id.strip()
        # Reject path separators and parent directory traversal
        if any(c in sanitized for c in ('/', '\\', '..')):
            raise ValueError(
                f"Invalid change_id '{change_id}': must not contain path separators or '..'"
            )
        # Only allow safe characters: alphanumeric, hyphen, underscore, dot
        if not re.match(r'^[a-zA-Z0-9_\-\.]+$', sanitized):
            raise ValueError(
                f"Invalid change_id '{change_id}': only alphanumeric, hyphen, underscore, and dot allowed"
            )
        return sanitized

    def _safe_pending_path(self, change_id: str, suffix: str = ".pending.json") -> Path:
        """Build a pending-file path and verify it stays inside pending_dir."""
        safe_id = self._sanitize_change_id(change_id)
        target = (self.pending_dir / f"{safe_id}{suffix}").resolve()
        if not str(target).startswith(str(self.pending_dir.resolve())):
            raise ValueError(f"Path traversal blocked for change_id '{change_id}'")
        return target

    def propose_change(self, change_id: str, key: str, value: Any, 
                       source_agent: str = "unknown", ttl: Optional[int] = None,
                       operation: str = "write") -> dict[str, Any]:
        """
        Stage a change without applying it (Step 1 of atomic commit).
        
        The change is written to a .pending file and must be validated
        and committed by the orchestrator before it takes effect.
        """
        pending_file = self._safe_pending_path(change_id)
        
        # Check for duplicate change_id
        if pending_file.exists():
            return {
                "success": False,
                "error": f"Change ID '{change_id}' already exists. Use a unique ID."
            }
        
        # Get current value for conflict detection
        current_entry = self.cache.get(key)
        current_hash = None
        if current_entry:
            current_hash = hashlib.sha256(
                json.dumps(current_entry, sort_keys=True).encode()
            ).hexdigest()[:16]
        
        change_set: dict[str, Any] = {
            "change_id": change_id,
            "operation": operation,  # "write" or "delete"
            "key": key,
            "value": value,
            "source_agent": source_agent,
            "ttl": ttl,
            "proposed_at": datetime.now(timezone.utc).isoformat(),
            "status": "pending",
            "base_hash": current_hash,  # For conflict detection
        }
        
        pending_file.write_text(json.dumps(change_set, indent=2))
        
        return {
            "success": True,
            "change_id": change_id,
            "status": "proposed",
            "pending_file": str(pending_file),
            "message": "Change staged. Run 'validate' then 'commit' to apply."
        }
    
    def validate_change(self, change_id: str) -> dict[str, Any]:
        """
        Validate a pending change for conflicts (Step 2 of atomic commit).
        
        Checks:
        - Change exists
        - No conflicting changes to the same key
        - Base hash matches (data hasn't changed since proposal)
        """
        pending_file = self._safe_pending_path(change_id)
        
        if not pending_file.exists():
            return {
                "valid": False,
                "error": f"Change '{change_id}' not found. Was it proposed?"
            }
        
        change_set = json.loads(pending_file.read_text())
        
        if change_set["status"] != "pending":
            return {
                "valid": False,
                "error": f"Change is in '{change_set['status']}' state, not 'pending'"
            }
        
        key = change_set["key"]
        base_hash = change_set["base_hash"]
        
        # Check for conflicts: has the key changed since we proposed?
        with blackboard_lock():
            self._load_from_disk()
            current_entry = self.cache.get(key)
        
        current_hash = None
        if current_entry:
            current_hash = hashlib.sha256(
                json.dumps(current_entry, sort_keys=True).encode()
            ).hexdigest()[:16]
        
        if base_hash != current_hash:
            return {
                "valid": False,
                "conflict": True,
                "error": f"CONFLICT: Key '{key}' was modified since proposal. "
                         f"Expected hash {base_hash}, got {current_hash}. "
                         "Abort and re-propose with fresh data.",
                "current_value": current_entry
            }
        
        # Check for other pending changes to the same key
        conflicts: list[str] = []
        for other_file in self.pending_dir.glob("*.pending.json"):
            if other_file.name == pending_file.name:
                continue
            other_change = json.loads(other_file.read_text())
            if other_change["key"] == key and other_change["status"] == "pending":
                conflicts.append(other_change["change_id"])
        
        if conflicts:
            return {
                "valid": False,
                "conflict": True,
                "error": f"CONFLICT: Other pending changes affect key '{key}': {conflicts}. "
                         "Resolve conflicts before committing."
            }
        
        # Mark as validated
        change_set["status"] = "validated"
        change_set["validated_at"] = datetime.now(timezone.utc).isoformat()
        pending_file.write_text(json.dumps(change_set, indent=2))
        
        return {
            "valid": True,
            "change_id": change_id,
            "key": key,
            "status": "validated",
            "message": "No conflicts detected. Ready to commit."
        }
    
    def commit_change(self, change_id: str) -> dict[str, Any]:
        """
        Apply a validated change atomically (Step 3 of atomic commit).
        """
        pending_file = self._safe_pending_path(change_id)
        
        if not pending_file.exists():
            return {
                "committed": False,
                "error": f"Change '{change_id}' not found."
            }
        
        change_set = json.loads(pending_file.read_text())
        
        if change_set["status"] != "validated":
            return {
                "committed": False,
                "error": f"Change must be validated first. Current status: {change_set['status']}"
            }
        
        # Apply the change atomically
        with blackboard_lock():
            self._load_from_disk()
            
            if change_set["operation"] == "delete":
                if change_set["key"] in self.cache:
                    del self.cache[change_set["key"]]
            else:
                entry: dict[str, Any] = {
                    "key": change_set["key"],
                    "value": change_set["value"],
                    "source_agent": change_set["source_agent"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "ttl": change_set["ttl"],
                    "committed_from": change_id
                }
                self.cache[change_set["key"]] = entry
            
            self._persist_to_disk()
        
        # Archive the committed change
        change_set["status"] = "committed"
        change_set["committed_at"] = datetime.now(timezone.utc).isoformat()
        
        safe_id = self._sanitize_change_id(change_id)
        archive_dir = self.pending_dir / "archive"
        archive_dir.mkdir(exist_ok=True)
        archive_file = archive_dir / f"{safe_id}.committed.json"
        archive_file.write_text(json.dumps(change_set, indent=2))
        
        # Remove pending file
        pending_file.unlink()
        
        return {
            "committed": True,
            "change_id": change_id,
            "key": change_set["key"],
            "operation": change_set["operation"],
            "message": "Change committed atomically."
        }
    
    def abort_change(self, change_id: str) -> dict[str, Any]:
        """Abort a pending change without applying it."""
        pending_file = self._safe_pending_path(change_id)
        
        if not pending_file.exists():
            return {
                "aborted": False,
                "error": f"Change '{change_id}' not found."
            }
        
        change_set = json.loads(pending_file.read_text())
        change_set["status"] = "aborted"
        change_set["aborted_at"] = datetime.now(timezone.utc).isoformat()
        
        # Archive the aborted change
        safe_id = self._sanitize_change_id(change_id)
        archive_dir = self.pending_dir / "archive"
        archive_dir.mkdir(exist_ok=True)
        archive_file = archive_dir / f"{safe_id}.aborted.json"
        archive_file.write_text(json.dumps(change_set, indent=2))
        
        pending_file.unlink()
        
        return {
            "aborted": True,
            "change_id": change_id,
            "key": change_set["key"]
        }
    
    def list_pending_changes(self) -> list[dict[str, Any]]:
        """List all pending changes awaiting commit."""
        pending: list[dict[str, Any]] = []
        for pending_file in self.pending_dir.glob("*.pending.json"):
            change_set = json.loads(pending_file.read_text())
            pending.append({
                "change_id": change_set["change_id"],
                "key": change_set["key"],
                "operation": change_set["operation"],
                "source_agent": change_set["source_agent"],
                "status": change_set["status"],
                "proposed_at": change_set["proposed_at"]
            })
        return pending
    
    def exists(self, key: str) -> bool:
        """Check if a key exists (and is not expired)."""
        return self.read(key) is not None
    
    def list_keys(self) -> list[str]:
        """List all valid (non-expired) keys."""
        valid_keys: list[str] = []
        for key in list(self.cache.keys()):
            if self.read(key) is not None:
                valid_keys.append(key)
        return valid_keys
    
    def get_snapshot(self) -> dict[str, dict[str, Any]]:
        """Get a snapshot of all valid entries."""
        snapshot: dict[str, dict[str, Any]] = {}
        for key in list(self.cache.keys()):
            entry = self.read(key)
            if entry is not None:
                snapshot[key] = entry
        return snapshot


def main():
    parser = argparse.ArgumentParser(
        description="Shared Blackboard - Agent Coordination State Manager (Atomic Commit Edition)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  write KEY VALUE [--ttl SECONDS]     Write a value (with file locking)
  read KEY                            Read a value
  delete KEY                          Delete a key
  list                                List all keys
  snapshot                            Get full snapshot as JSON

Atomic Commit Workflow (for multi-agent safety):
  propose CHANGE_ID KEY VALUE         Stage a change (Step 1)
  validate CHANGE_ID                  Check for conflicts (Step 2)
  commit CHANGE_ID                    Apply atomically (Step 3)
  abort CHANGE_ID                     Cancel a pending change
  list-pending                        Show all pending changes

Examples:
  %(prog)s write "task:analysis" '{"status": "running"}'
  %(prog)s write "cache:temp" '{"data": [1,2,3]}' --ttl 3600
  
  # Safe multi-agent update:
  %(prog)s propose "chg_001" "order:123" '{"status": "approved"}'
  %(prog)s validate "chg_001"
  %(prog)s commit "chg_001"
"""
    )
    
    parser.add_argument(
        "command",
        choices=["write", "read", "delete", "list", "snapshot", 
                 "propose", "validate", "commit", "abort", "list-pending"],
        help="Command to execute"
    )
    parser.add_argument(
        "key",
        nargs="?",
        help="Key name or Change ID (depending on command)"
    )
    parser.add_argument(
        "value",
        nargs="?",
        help="JSON value (required for write/propose)"
    )
    parser.add_argument(
        "--ttl",
        type=int,
        help="Time-to-live in seconds (for write/propose)"
    )
    parser.add_argument(
        "--agent",
        default="cli",
        help="Source agent ID (for write/propose)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=BLACKBOARD_PATH,
        help="Path to blackboard file"
    )
    
    args = parser.parse_args()
    bb = SharedBlackboard(args.path)
    
    try:
        if args.command == "write":
            if not args.key or not args.value:
                print("Error: write requires KEY and VALUE", file=sys.stderr)
                sys.exit(1)
            
            try:
                value = json.loads(args.value)
            except json.JSONDecodeError:
                value = args.value
            
            entry = bb.write(args.key, value, args.agent, args.ttl)
            
            if args.json:
                print(json.dumps(entry, indent=2))
            else:
                print(f"✅ Written: {args.key} (with lock)")
                if args.ttl:
                    print(f"   TTL: {args.ttl} seconds")
        
        elif args.command == "read":
            if not args.key:
                print("Error: read requires KEY", file=sys.stderr)
                sys.exit(1)
            
            entry = bb.read(args.key)
            
            if entry is None:
                if args.json:
                    print("null")
                else:
                    print(f"❌ Key not found or expired: {args.key}")
                sys.exit(1)
            
            if args.json:
                print(json.dumps(entry, indent=2))
            else:
                print(f"📖 {args.key}:")
                print(f"   Value: {json.dumps(entry.get('value'))}")
                print(f"   Source: {entry.get('source_agent')}")
                print(f"   Timestamp: {entry.get('timestamp')}")
                if entry.get('ttl'):
                    print(f"   TTL: {entry['ttl']} seconds")
        
        elif args.command == "delete":
            if not args.key:
                print("Error: delete requires KEY", file=sys.stderr)
                sys.exit(1)
            
            if bb.delete(args.key):
                print(f"✅ Deleted: {args.key}")
            else:
                print(f"❌ Key not found: {args.key}")
                sys.exit(1)
        
        elif args.command == "list":
            keys = bb.list_keys()
            
            if args.json:
                print(json.dumps(keys, indent=2))
            else:
                if keys:
                    print(f"📋 Blackboard keys ({len(keys)}):")
                    for key in sorted(keys):
                        entry = bb.read(key)
                        ttl_info = f" [TTL: {entry['ttl']}s]" if entry and entry.get('ttl') else ""
                        print(f"   • {key}{ttl_info}")
                else:
                    print("📋 Blackboard is empty")
        
        elif args.command == "snapshot":
            snapshot = bb.get_snapshot()
            print(json.dumps(snapshot, indent=2))
        
        # === ATOMIC COMMIT COMMANDS ===
        
        elif args.command == "propose":
            if not args.key or not args.value:
                print("Error: propose requires CHANGE_ID and KEY VALUE", file=sys.stderr)
                print("Usage: propose CHANGE_ID KEY VALUE", file=sys.stderr)
                sys.exit(1)
            
            # Parse: propose CHANGE_ID KEY VALUE (key is actually change_id, value is "KEY VALUE")
            parts = args.value.split(" ", 1)
            if len(parts) < 2:
                print("Error: propose requires CHANGE_ID KEY VALUE", file=sys.stderr)
                sys.exit(1)
            
            change_id = args.key
            actual_key = parts[0]
            actual_value_str = parts[1] if len(parts) > 1 else "{}"
            
            try:
                actual_value = json.loads(actual_value_str)
            except json.JSONDecodeError:
                actual_value = actual_value_str
            
            result = bb.propose_change(change_id, actual_key, actual_value, args.agent, args.ttl)
            
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                if result["success"]:
                    print(f"📝 Change PROPOSED: {change_id}")
                    print(f"   Key: {actual_key}")
                    print(f"   Status: pending validation")
                    print(f"   Next: run 'validate {change_id}'")
                else:
                    print(f"❌ Proposal FAILED: {result['error']}")
                    sys.exit(1)
        
        elif args.command == "validate":
            if not args.key:
                print("Error: validate requires CHANGE_ID", file=sys.stderr)
                sys.exit(1)
            
            result = bb.validate_change(args.key)
            
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                if result["valid"]:
                    print(f"✅ Change VALIDATED: {args.key}")
                    print(f"   Key: {result['key']}")
                    print(f"   No conflicts detected")
                    print(f"   Next: run 'commit {args.key}'")
                else:
                    print(f"❌ Validation FAILED: {result['error']}")
                    sys.exit(1)
        
        elif args.command == "commit":
            if not args.key:
                print("Error: commit requires CHANGE_ID", file=sys.stderr)
                sys.exit(1)
            
            result = bb.commit_change(args.key)
            
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                if result["committed"]:
                    print(f"🎉 Change COMMITTED: {args.key}")
                    print(f"   Key: {result['key']}")
                    print(f"   Operation: {result['operation']}")
                else:
                    print(f"❌ Commit FAILED: {result['error']}")
                    sys.exit(1)
        
        elif args.command == "abort":
            if not args.key:
                print("Error: abort requires CHANGE_ID", file=sys.stderr)
                sys.exit(1)
            
            result = bb.abort_change(args.key)
            
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                if result["aborted"]:
                    print(f"🚫 Change ABORTED: {args.key}")
                else:
                    print(f"❌ Abort FAILED: {result['error']}")
                    sys.exit(1)
        
        elif args.command == "list-pending":
            pending = bb.list_pending_changes()
            
            if args.json:
                print(json.dumps(pending, indent=2))
            else:
                if pending:
                    print(f"📋 Pending changes ({len(pending)}):")
                    for p in pending:
                        status_icon = "🟡" if p["status"] == "pending" else "🟢"
                        print(f"   {status_icon} {p['change_id']}: {p['operation']} '{p['key']}'")
                        print(f"      Agent: {p['source_agent']} | Status: {p['status']}")
                else:
                    print("📋 No pending changes")
    
    except TimeoutError as e:
        print(f"🔒 LOCK TIMEOUT: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
