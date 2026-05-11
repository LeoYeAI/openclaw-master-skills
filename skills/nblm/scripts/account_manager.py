#!/usr/bin/env python3
"""
Multi-Account Manager for nblm
Handles multiple Google account credentials with index-based switching.
"""

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any

from config import (
    GOOGLE_AUTH_DIR,
    GOOGLE_AUTH_INDEX,
    GOOGLE_AUTH_FILE,
    AUTH_DIR,
    LIBRARY_FILE,
)


@dataclass
class AccountInfo:
    """Information about a stored Google account."""
    index: int
    email: str
    file_path: Path
    added_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "email": self.email,
            "file": self.file_path.name,
            "added_at": self.added_at,
        }


class AccountManager:
    """Manages multiple Google account credentials."""

    def __init__(self):
        """Initialize AccountManager and run migration if needed."""
        self._ensure_directories()
        self._migrate_if_needed()

    def _ensure_directories(self) -> None:
        """Create necessary directories."""
        GOOGLE_AUTH_DIR.mkdir(parents=True, exist_ok=True)

    def _load_index(self) -> Dict[str, Any]:
        """Load the account index file."""
        if not GOOGLE_AUTH_INDEX.exists():
            return {"version": 2, "active_account": None, "accounts": []}
        try:
            return json.loads(GOOGLE_AUTH_INDEX.read_text())
        except (json.JSONDecodeError, IOError):
            return {"version": 2, "active_account": None, "accounts": []}

    def _save_index(self, data: Dict[str, Any]) -> None:
        """Save the account index file."""
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        GOOGLE_AUTH_INDEX.write_text(json.dumps(data, indent=2))

    @staticmethod
    def _sanitize_email_for_filename(email: str) -> str:
        """Convert email to filesystem-safe filename component.

        Example: user@gmail.com -> user-gmail-com
        """
        # Remove @ and replace . with -
        sanitized = email.replace("@", "-").replace(".", "-")
        # Remove any other unsafe characters
        sanitized = re.sub(r"[^a-zA-Z0-9-]", "", sanitized)
        return sanitized.lower()

    def _get_account_file_path(self, index: int, email: str) -> Path:
        """Generate the credential file path for an account."""
        sanitized = self._sanitize_email_for_filename(email)
        return GOOGLE_AUTH_DIR / f"{index}-{sanitized}.json"

    def _get_next_index(self) -> int:
        """Get the next available account index."""
        data = self._load_index()
        if not data["accounts"]:
            return 1
        return max(acc["index"] for acc in data["accounts"]) + 1

    def list_accounts(self) -> List[AccountInfo]:
        """List all registered accounts."""
        data = self._load_index()
        accounts = []
        for acc in data["accounts"]:
            file_path = GOOGLE_AUTH_DIR / acc["file"]
            accounts.append(AccountInfo(
                index=acc["index"],
                email=acc["email"],
                file_path=file_path,
                added_at=acc.get("added_at", ""),
            ))
        return sorted(accounts, key=lambda a: a.index)

    def get_active_account(self) -> Optional[AccountInfo]:
        """Get the currently active account."""
        data = self._load_index()
        active_index = data.get("active_account")
        if active_index is None:
            return None
        for acc in data["accounts"]:
            if acc["index"] == active_index:
                file_path = GOOGLE_AUTH_DIR / acc["file"]
                return AccountInfo(
                    index=acc["index"],
                    email=acc["email"],
                    file_path=file_path,
                    added_at=acc.get("added_at", ""),
                )
        return None

    def get_active_auth_file(self) -> Optional[Path]:
        """Get the auth file path for the active account."""
        account = self.get_active_account()
        if account:
            return account.file_path
        return None

    def switch_account(self, identifier: str | int) -> AccountInfo:
        """Switch to a different account by index or email.

        Args:
            identifier: Account index (int) or email (str)

        Returns:
            The newly active AccountInfo

        Raises:
            ValueError: If account not found
        """
        data = self._load_index()
        target_account = None

        # Try to match by index or email
        for acc in data["accounts"]:
            if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
                if acc["index"] == int(identifier):
                    target_account = acc
                    break
            else:
                if acc["email"].lower() == identifier.lower():
                    target_account = acc
                    break

        if not target_account:
            raise ValueError(f"Account not found: {identifier}")

        # Update active account
        data["active_account"] = target_account["index"]
        self._save_index(data)

        file_path = GOOGLE_AUTH_DIR / target_account["file"]
        return AccountInfo(
            index=target_account["index"],
            email=target_account["email"],
            file_path=file_path,
            added_at=target_account.get("added_at", ""),
        )

    def get_account_by_index(self, index: int) -> Optional[AccountInfo]:
        """Get account by index."""
        data = self._load_index()
        for acc in data["accounts"]:
            if acc["index"] == index:
                file_path = GOOGLE_AUTH_DIR / acc["file"]
                return AccountInfo(
                    index=acc["index"],
                    email=acc["email"],
                    file_path=file_path,
                    added_at=acc.get("added_at", ""),
                )
        return None

    def get_account_by_email(self, email: str) -> Optional[AccountInfo]:
        """Get account by email."""
        data = self._load_index()
        for acc in data["accounts"]:
            if acc["email"].lower() == email.lower():
                file_path = GOOGLE_AUTH_DIR / acc["file"]
                return AccountInfo(
                    index=acc["index"],
                    email=acc["email"],
                    file_path=file_path,
                    added_at=acc.get("added_at", ""),
                )
        return None

    def account_exists(self, email: str) -> bool:
        """Check if an account with this email already exists."""
        return self.get_account_by_email(email) is not None

    def add_account(self, email: str, credentials: Dict[str, Any]) -> AccountInfo:
        """Add a new account with credentials.

        Args:
            email: The Google account email
            credentials: The auth credentials dict (cookies, tokens, etc.)

        Returns:
            The newly created AccountInfo

        Raises:
            ValueError: If account already exists
        """
        if self.account_exists(email):
            raise ValueError(f"Account already exists: {email}")

        # Get next index
        index = self._get_next_index()
        file_path = self._get_account_file_path(index, email)

        # Save credentials
        file_path.write_text(json.dumps(credentials, indent=2))

        # Update index
        data = self._load_index()
        data["accounts"].append({
            "index": index,
            "email": email,
            "file": file_path.name,
            "added_at": datetime.now(timezone.utc).isoformat(),
        })

        # Set as active if first account
        if data["active_account"] is None:
            data["active_account"] = index

        self._save_index(data)

        return AccountInfo(
            index=index,
            email=email,
            file_path=file_path,
            added_at=datetime.now(timezone.utc).isoformat(),
        )

    def remove_account(self, identifier: str | int) -> bool:
        """Remove an account by index or email.

        Args:
            identifier: Account index (int) or email (str)

        Returns:
            True if removed, False if not found
        """
        data = self._load_index()
        target_idx = None
        target_file = None
        target_index = None

        for i, acc in enumerate(data["accounts"]):
            if isinstance(identifier, int) or (isinstance(identifier, str) and str(identifier).isdigit()):
                if acc["index"] == int(identifier):
                    target_idx = i
                    target_file = acc["file"]
                    target_index = acc["index"]
                    break
            else:
                if acc["email"].lower() == str(identifier).lower():
                    target_idx = i
                    target_file = acc["file"]
                    target_index = acc["index"]
                    break

        if target_idx is None:
            return False

        # Remove from index
        data["accounts"].pop(target_idx)

        # Handle active account removal
        if data["active_account"] == target_index:
            if data["accounts"]:
                # Switch to first remaining account
                data["active_account"] = data["accounts"][0]["index"]
            else:
                data["active_account"] = None

        self._save_index(data)

        # Delete credential file
        file_path = GOOGLE_AUTH_DIR / target_file
        if file_path.exists():
            file_path.unlink()

        return True

    def update_account_credentials(self, index: int, credentials: Dict[str, Any]) -> bool:
        """Update credentials for an existing account.

        Used for re-authentication.
        """
        account = self.get_account_by_index(index)
        if not account:
            return False

        account.file_path.write_text(json.dumps(credentials, indent=2))
        return True

    def get_account_credentials(self, index: int) -> Optional[Dict[str, Any]]:
        """Load credentials for an account."""
        account = self.get_account_by_index(index)
        if not account or not account.file_path.exists():
            return None
        try:
            return json.loads(account.file_path.read_text())
        except (json.JSONDecodeError, IOError):
            return None

    def _migrate_if_needed(self) -> bool:
        """Migrate from single-account to multi-account structure if needed.

        Returns True if migration was performed.
        """
        # Check if old structure exists and new structure doesn't
        old_auth_file = AUTH_DIR / "google.json"

        if not old_auth_file.exists():
            return False

        # Check if already migrated (index file exists with accounts)
        data = self._load_index()
        if data["accounts"]:
            return False

        print("🔄 Migrating to multi-account structure...")

        # Load old credentials
        try:
            old_creds = json.loads(old_auth_file.read_text())
        except (json.JSONDecodeError, IOError) as e:
            print(f"   ⚠️ Could not read old auth file: {e}")
            return False

        # Extract email from credentials
        email = self._extract_email_from_credentials(old_creds)
        if not email:
            # Don't create placeholder accounts - keep legacy file until proper auth
            print("   ⚠️ Could not extract email from existing credentials")
            print("   ℹ️ Legacy google.json will remain active")
            print("   ℹ️ Run 'auth_manager.py accounts add' to migrate with proper email")
            return False
        else:
            print(f"   ✓ Detected existing account: {email}")

        # Create new account entry
        index = 1
        file_path = self._get_account_file_path(index, email)

        # Move credentials to new location
        file_path.write_text(json.dumps(old_creds, indent=2))
        print(f"   ✓ Migrated credentials to {file_path.name}")

        # Update index
        data["accounts"].append({
            "index": index,
            "email": email,
            "file": file_path.name,
            "added_at": datetime.now(timezone.utc).isoformat(),
        })
        data["active_account"] = index
        self._save_index(data)

        # Remove old file
        old_auth_file.unlink()
        print("   ✓ Removed legacy google.json")

        # Migrate library.json notebooks to include account association
        self._migrate_library_notebooks(index, email)

        print("   ✓ Migration complete!")
        return True

    def _migrate_library_notebooks(self, account_index: int, account_email: str) -> None:
        """Add account association to existing notebooks in library.json."""
        if not LIBRARY_FILE.exists():
            return

        try:
            data = json.loads(LIBRARY_FILE.read_text())
        except (json.JSONDecodeError, IOError):
            return

        notebooks = data.get("notebooks", {})
        updated_count = 0

        for notebook_id, notebook in notebooks.items():
            if notebook.get("account_index") is None:
                notebook["account_index"] = account_index
                notebook["account_email"] = account_email
                updated_count += 1

        if updated_count > 0:
            data["notebooks"] = notebooks
            data["updated_at"] = datetime.now(timezone.utc).isoformat()
            LIBRARY_FILE.write_text(json.dumps(data, indent=2))
            print(f"   ✓ Updated {updated_count} notebooks with account association")

    def _extract_email_from_credentials(self, creds: Dict[str, Any]) -> Optional[str]:
        """Extract email address from stored credentials.

        Looks in cookies for Google account identifiers.
        """
        cookies = creds.get("cookies", [])

        # Look for SAPISID or similar cookies that might contain email hints
        for cookie in cookies:
            name = cookie.get("name", "").upper()
            value = cookie.get("value", "")

            # Some Google cookies encode the email
            if name in ("GMAIL_AT", "GMAIL_RTT"):
                # These cookies sometimes contain email-like patterns
                email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', value)
                if email_match:
                    return email_match.group(0)

        # Check localStorage origins for email
        origins = creds.get("origins", [])
        for origin in origins:
            local_storage = origin.get("localStorage", [])
            for item in local_storage:
                value = item.get("value", "")
                if "@" in value and "google" in value.lower():
                    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', value)
                    if email_match:
                        return email_match.group(0)

        return None
