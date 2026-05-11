#!/usr/bin/env python3
"""
Authentication Manager for nblm
Handles Google authentication using agent-browser
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))

from config import (
    DATA_DIR,
    AUTH_DIR,
    GOOGLE_AUTH_FILE,
    ZLIBRARY_AUTH_FILE,
    AGENT_BROWSER_SESSION_FILE,
    DEFAULT_SESSION_ID,
    AGENT_BROWSER_ACTIVITY_FILE,
    AGENT_BROWSER_WATCHDOG_PID_FILE,
    AGENT_BROWSER_IDLE_TIMEOUT_SECONDS
)
from agent_browser_client import AgentBrowserClient, AgentBrowserError
from account_manager import AccountManager, AccountInfo


def _pid_is_alive(pid: int) -> bool:
    """Check whether a PID is alive."""
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def get_watchdog_status() -> dict:
    """Return watchdog and daemon status details."""
    last_activity = None
    owner_pid = None
    if AGENT_BROWSER_ACTIVITY_FILE.exists():
        try:
            payload = json.loads(AGENT_BROWSER_ACTIVITY_FILE.read_text())
            last_activity = payload.get("timestamp")
            owner_pid = payload.get("owner_pid")
        except Exception:
            last_activity = None
            owner_pid = None

    idle_seconds = None
    if last_activity is not None:
        try:
            idle_seconds = max(0, time.time() - float(last_activity))
        except Exception:
            idle_seconds = None

    watchdog_pid = None
    if AGENT_BROWSER_WATCHDOG_PID_FILE.exists():
        try:
            watchdog_pid = int(AGENT_BROWSER_WATCHDOG_PID_FILE.read_text().strip())
        except Exception:
            watchdog_pid = None

    watchdog_alive = bool(watchdog_pid and _pid_is_alive(watchdog_pid))
    owner_alive = bool(owner_pid and _pid_is_alive(int(owner_pid)))
    daemon_running = AgentBrowserClient(session_id=DEFAULT_SESSION_ID)._daemon_is_running()

    return {
        "watchdog_pid": watchdog_pid,
        "watchdog_alive": watchdog_alive,
        "last_activity": last_activity,
        "idle_seconds": idle_seconds,
        "idle_timeout_seconds": AGENT_BROWSER_IDLE_TIMEOUT_SECONDS,
        "owner_pid": owner_pid,
        "owner_alive": owner_alive,
        "daemon_running": daemon_running
    }


NOTEBOOKLM_AUTH_TTL_DAYS = 10


class AuthManager:
    """Unified auth manager for multiple services"""

    SERVICES = {
        "google": {
            "file": GOOGLE_AUTH_FILE,
            "login_url": "https://notebooklm.google.com",
            "success_indicators": ["notebooklm", "notebook"]
        },
        "zlibrary": {
            "file": ZLIBRARY_AUTH_FILE,
            "login_url": "https://zh.zlib.li/",
            "success_indicators": ["logout", "退出"]
        }
    }

    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        AUTH_DIR.mkdir(parents=True, exist_ok=True)
        self.account_manager = AccountManager()
        # Ensure symlink is up-to-date after migration (silent)
        self._ensure_storage_state_symlink(quiet=True)

    def _get_service_config(self, service: str) -> dict:
        service = service or "google"
        if service not in self.SERVICES:
            raise ValueError(f"Unknown service: {service}")
        return self.SERVICES[service]

    def _auth_file(self, service: str) -> Path:
        service = service or "google"
        if service == "google":
            # Use active account from AccountManager
            auth_file = self.account_manager.get_active_auth_file()
            if auth_file:
                return auth_file
            # Fallback to legacy path if no accounts configured
            return GOOGLE_AUTH_FILE
        return self._get_service_config(service)["file"]

    def _auth_timestamp(self, auth_file: Path) -> str:
        try:
            return datetime.fromtimestamp(auth_file.stat().st_mtime).isoformat()
        except Exception:
            return "Unknown"

    def is_authenticated(self, service: str = "google") -> bool:
        """Check if service has valid saved auth"""
        info = self.get_auth_info(service)
        return bool(info.get("authenticated"))

    def get_auth_info(self, service: str = "google") -> dict:
        """Get authentication info for a service"""
        auth_file = self._auth_file(service)
        if not auth_file.exists():
            return {"authenticated": False}

        try:
            payload = json.loads(auth_file.read_text())
        except Exception:
            return {"authenticated": False}

        authenticated = bool(payload.get("cookies") or payload.get("origins"))
        timestamp = self._auth_timestamp(auth_file)
        return {
            "authenticated": authenticated,
            "timestamp": timestamp
        }

    def save_auth(self, service: str = "google", client: AgentBrowserClient = None) -> bool:
        """Save current browser state for service"""
        owns_client = False
        if client is None:
            client = AgentBrowserClient(session_id=self._load_session_id() or DEFAULT_SESSION_ID)
            client.connect()
            owns_client = True

        try:
            payload = client.get_storage_state()
            if not payload:
                return False
            auth_file = self._auth_file(service)
            auth_file.parent.mkdir(parents=True, exist_ok=True)
            auth_file.write_text(json.dumps(payload))
            self._save_session_id(client.session_id)
            return True
        except Exception:
            return False
        finally:
            if owns_client:
                client.disconnect()

    def restore_auth(self, service: str = "google", client: AgentBrowserClient = None) -> bool:
        """Restore saved auth state to browser"""
        auth_file = self._auth_file(service)
        if not auth_file.exists():
            return False

        try:
            payload = json.loads(auth_file.read_text())
        except Exception:
            return False

        owns_client = False
        if client is None:
            client = AgentBrowserClient(session_id=self._load_session_id() or DEFAULT_SESSION_ID)
            client.connect()
            owns_client = True

        try:
            return client.set_storage_state(payload)
        finally:
            if owns_client:
                client.disconnect()

    def _save_session_id(self, session_id: str):
        """Save session ID for future use"""
        AGENT_BROWSER_SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(AGENT_BROWSER_SESSION_FILE, 'w') as f:
            f.write(session_id)

    def _ensure_storage_state_symlink(self, quiet: bool = False):
        """Create symlink from storage_state.json -> active account file for notebooklm-py compatibility.

        The notebooklm-py library's download methods use Playwright internally and look for
        storage at NOTEBOOKLM_HOME/storage_state.json. This symlink ensures the library
        uses the active account's auth data.

        Args:
            quiet: If True, don't print status messages
        """
        storage_state_path = AUTH_DIR / "storage_state.json"

        # Get active account auth file
        active_auth_file = self.account_manager.get_active_auth_file()
        if not active_auth_file or not active_auth_file.exists():
            return

        # Remove existing symlink or file if it exists
        if storage_state_path.exists() or storage_state_path.is_symlink():
            storage_state_path.unlink()

        # Create symlink to active account file (need relative path)
        try:
            # Calculate relative path from AUTH_DIR to the account file
            rel_path = active_auth_file.relative_to(AUTH_DIR)
            storage_state_path.symlink_to(rel_path)
            if not quiet:
                print("   ✓ Updated storage_state.json symlink for notebooklm-py")
        except (OSError, ValueError) as e:
            # On Windows or if relative path fails, fall back to copying
            import shutil
            shutil.copy2(active_auth_file, storage_state_path)
            if not quiet:
                print("   ✓ Updated storage_state.json copy for notebooklm-py")

    def _load_session_id(self) -> str:
        """Load saved session ID"""
        if AGENT_BROWSER_SESSION_FILE.exists():
            with open(AGENT_BROWSER_SESSION_FILE) as f:
                return f.read().strip()
        return None

    def _snapshot_indicates_auth(self, service: str, snapshot: str, client: AgentBrowserClient) -> bool:
        if not snapshot:
            return False
        service_name = service or "google"
        snapshot_lower = snapshot.lower()
        if service_name == "google":
            if client.check_auth(snapshot):
                return False
        if service_name == "zlibrary":
            login_indicators = (
                "login",
                "log in",
                "sign in",
                "sign up",
                "register",
                "登录",
                "注册",
            )
            if any(indicator in snapshot_lower for indicator in login_indicators):
                return False
            indicators = self._get_service_config(service_name)["success_indicators"]
            if any(indicator in snapshot_lower for indicator in indicators):
                return True
            return True
        indicators = self._get_service_config(service_name)["success_indicators"]
        return any(indicator in snapshot_lower for indicator in indicators)

    def setup(self, service: str = "google", use_fresh_profile: bool = False):
        """Interactive authentication setup for specified service

        Args:
            service: Service to authenticate ("google" or "zlibrary")
            use_fresh_profile: If True, use a fresh browser profile to allow adding new accounts
        """
        # Default to google if not specified
        service = service or "google"

        # Use Patchright for Google auth (bypasses "browser not secure" check)
        if service == "google":
            return self._setup_google_with_patchright(use_fresh_profile=use_fresh_profile)

        # For other services, use agent-browser
        return self._setup_with_agent_browser(service)

    def _setup_google_with_patchright(self, use_fresh_profile: bool = False):
        """Setup Google auth using Patchright (anti-detection browser)

        IMPORTANT: Google authentication MUST use Patchright to bypass the
        "This browser or app may not be secure" blocking. Agent-browser uses
        Chrome for Testing which is detected as an automation browser.
        """
        try:
            from patchright_auth import authenticate_with_patchright
        except ImportError as e:
            print(f"❌ Patchright not available: {e}")
            print()
            print("   Google authentication requires Patchright (anti-detection browser).")
            print("   Chrome for Testing is blocked by Google's security checks.")
            print()
            print("   To install Patchright:")
            print("   pip install patchright && patchright install chromium")
            return False
        except Exception as e:
            print(f"❌ Patchright import error: {e}")
            print()
            print("   Please reinstall Patchright:")
            print("   pip install --upgrade patchright && patchright install chromium")
            return False

        try:
            success, email, storage_state = authenticate_with_patchright(
                use_fresh_profile=use_fresh_profile
            )
            if success and storage_state:
                if email:
                    # Check if account already exists
                    if self.account_manager.account_exists(email):
                        # Update existing account
                        existing = self.account_manager.get_account_by_email(email)
                        self.account_manager.update_account_credentials(existing.index, storage_state)
                        # Switch to this account
                        self.account_manager.switch_account(existing.index)
                        print(f"   ✓ Updated existing account: {email}")
                    else:
                        # Add new account
                        account = self.account_manager.add_account(email, storage_state)
                        print(f"   ✓ Added new account [{account.index}]: {email}")
                else:
                    # No email extracted - prompt user
                    email = input("   Enter your Google email: ").strip()
                    if self.account_manager.account_exists(email):
                        existing = self.account_manager.get_account_by_email(email)
                        self.account_manager.update_account_credentials(existing.index, storage_state)
                        self.account_manager.switch_account(existing.index)
                        print(f"   ✓ Updated existing account: {email}")
                    else:
                        account = self.account_manager.add_account(email, storage_state)
                        print(f"   ✓ Added new account [{account.index}]: {email}")

                self._ensure_storage_state_symlink()
            return success
        except Exception as e:
            print(f"❌ Patchright authentication failed: {e}")
            print()
            print("   Please ensure:")
            print("   1. Google Chrome is installed on your system")
            print("   2. Patchright is properly installed: pip install patchright")
            print("   3. Patchright browser is installed: patchright install chromium")
            return False

    def _setup_with_agent_browser(self, service: str):
        """Original setup using agent-browser"""
        service_config = self._get_service_config(service)
        print(f"🔐 Setting up {service} authentication...")
        print("   A browser window will open for you to log in.")
        print()

        client = AgentBrowserClient(session_id=DEFAULT_SESSION_ID, headed=True)

        try:
            client.connect()
            client.navigate(service_config["login_url"])
            time.sleep(2)

            snapshot = client.snapshot()

            if not self._snapshot_indicates_auth(service, snapshot, client):
                print("📄 Current page state:")
                print(snapshot[:1000])
                print()
                print("⏳ Please complete login in the browser window...")
                print("   (This script will wait for you to finish)")

                for _ in range(300):  # 5 minute timeout
                    time.sleep(2)
                    snapshot = client.snapshot()
                    if self._snapshot_indicates_auth(service, snapshot, client):
                        print()
                        print("✅ Authentication successful!")
                        self._save_session_id(client.session_id)
                        self.save_auth(service, client=client)
                        # Extract NotebookLM tokens and create symlink for notebooklm-py
                        if service == "google":
                            self._extract_and_save_tokens(client)
                            self._ensure_storage_state_symlink()
                        return True

                print()
                print("❌ Authentication timeout")
                return False

            print("✅ Already authenticated!")
            self._save_session_id(client.session_id)
            self.save_auth(service, client=client)
            # Extract NotebookLM tokens and create symlink for notebooklm-py
            if service == "google":
                self._extract_and_save_tokens(client)
                self._ensure_storage_state_symlink()
            return True

        except AgentBrowserError as e:
            print(f"❌ [{e.code}]: {e.message}")
            print(f"🔧 Recovery: {e.recovery}")
            return False
        finally:
            client.disconnect()

    def get_notebooklm_credentials(
        self,
        client: AgentBrowserClient = None,
        force_refresh: bool = False,
    ) -> dict:
        """Return NotebookLM auth token and cookie header, persisting if refreshed."""
        auth_file = self._auth_file("google")
        payload = {}
        if auth_file.exists():
            try:
                payload = json.loads(auth_file.read_text())
            except Exception:
                payload = {}

        env_token = os.environ.get("NOTEBOOKLM_AUTH_TOKEN")
        env_cookies = os.environ.get("NOTEBOOKLM_COOKIES")
        if env_token and env_cookies:
            return self._persist_notebooklm_credentials(auth_file, payload, env_token, env_cookies)

        cached_token = payload.get("notebooklm_auth_token")
        cached_cookies = payload.get("notebooklm_cookies")
        if cached_token and cached_cookies and not force_refresh:
            if self._notebooklm_credentials_fresh(payload):
                return {"auth_token": cached_token, "cookies": cached_cookies}

        http_credentials = None
        try:
            http_credentials = self._fetch_notebooklm_token_http(payload)
        except Exception:
            http_credentials = None

        if http_credentials:
            token, cookies = http_credentials
            return self._persist_notebooklm_credentials(auth_file, payload, token, cookies)

        if cached_token and cached_cookies and not force_refresh:
            return {"auth_token": cached_token, "cookies": cached_cookies}

        extracted = None
        owns_client = False
        if client is None:
            client = AgentBrowserClient(session_id=self._load_session_id() or DEFAULT_SESSION_ID)
            client.connect()
            owns_client = True

        try:
            self.restore_auth("google", client=client)
            extracted = self._extract_notebooklm_credentials(client)
        except Exception:
            extracted = None
        finally:
            if owns_client:
                client.disconnect()

        if extracted:
            token, cookies = extracted
            return self._persist_notebooklm_credentials(auth_file, payload, token, cookies)

        if cached_token and cached_cookies:
            return {"auth_token": cached_token, "cookies": cached_cookies}

        if self.setup(service="google"):
            try:
                payload = json.loads(auth_file.read_text())
            except Exception:
                payload = {}
            http_credentials = None
            try:
                http_credentials = self._fetch_notebooklm_token_http(payload)
            except Exception:
                http_credentials = None
            if http_credentials:
                token, cookies = http_credentials
                return self._persist_notebooklm_credentials(auth_file, payload, token, cookies)

            extracted = None
            client = AgentBrowserClient(session_id=self._load_session_id() or DEFAULT_SESSION_ID)
            client.connect()
            try:
                self.restore_auth("google", client=client)
                extracted = self._extract_notebooklm_credentials(client)
            except Exception:
                extracted = None
            finally:
                client.disconnect()
            if extracted:
                token, cookies = extracted
                return self._persist_notebooklm_credentials(auth_file, payload, token, cookies)

            token = payload.get("notebooklm_auth_token")
            cookies = payload.get("notebooklm_cookies")
            if token and cookies:
                return {"auth_token": token, "cookies": cookies}

        raise RuntimeError(
            "NotebookLM auth token or cookies unavailable. "
            "Run: python scripts/run.py auth_manager.py setup"
        )

    @staticmethod
    def _extract_notebooklm_token_from_html(html: str) -> Optional[str]:
        if not html:
            return None
        candidates = [html]
        if '\\"' in html:
            candidates.append(html.replace('\\"', '"'))
        patterns = [
            r'"SNlM0e"\s*:\s*"([^"]+)"',
            r'SNlM0e"\s*,\s*"([^"]+)"',
        ]
        for candidate in candidates:
            for pattern in patterns:
                match = re.search(pattern, candidate)
                if match:
                    token = match.group(1)
                    return token.replace("\\u003d", "=")
        return None

    @staticmethod
    def _notebooklm_credentials_fresh(payload: dict) -> bool:
        updated_at = payload.get("notebooklm_updated_at")
        if not updated_at:
            return False
        try:
            timestamp = datetime.fromisoformat(updated_at)
        except Exception:
            return False
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        age = datetime.now(timezone.utc) - timestamp
        return age <= timedelta(days=NOTEBOOKLM_AUTH_TTL_DAYS)

    @staticmethod
    def _filter_cookies_for_domains(cookies: list, substrings: list) -> list:
        filtered = []
        for cookie in cookies or []:
            domain = (cookie.get("domain") or "").lower()
            if any(sub in domain for sub in substrings):
                filtered.append(cookie)
        return filtered

    def _fetch_notebooklm_token_http(self, payload: dict) -> Optional[tuple]:
        cookies = payload.get("cookies") or []
        filtered = self._filter_cookies_for_domains(cookies, ["google", "notebooklm"])
        cookie_header = self._build_cookie_header(filtered)
        if not cookie_header:
            return None
        request = Request(
            "https://notebooklm.google.com/",
            headers={
                "Cookie": cookie_header,
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
            },
        )
        try:
            with urlopen(request, timeout=15) as response:
                final_url = response.geturl() or ""
                html = response.read().decode("utf-8", errors="replace")
        except (URLError, HTTPError, ValueError, TimeoutError):
            return None
        if "notebooklm.google.com" not in final_url:
            return None
        if "accounts.google.com" in html or "Sign in" in html:
            return None
        token = self._extract_notebooklm_token_from_html(html)
        if not token:
            return None
        return token, cookie_header

    @staticmethod
    def _build_cookie_header(cookies: list) -> str:
        pairs = []
        for cookie in cookies or []:
            name = cookie.get("name")
            value = cookie.get("value")
            if name is None or value is None:
                continue
            pairs.append(f"{name}={value}")
        return "; ".join(pairs)

    @staticmethod
    def _persist_notebooklm_credentials(auth_file: Path, payload: dict, token: str, cookies: str) -> dict:
        payload["notebooklm_auth_token"] = token
        payload["notebooklm_cookies"] = cookies
        payload["notebooklm_updated_at"] = datetime.now(timezone.utc).isoformat()
        auth_file.parent.mkdir(parents=True, exist_ok=True)
        auth_file.write_text(json.dumps(payload))
        return {"auth_token": token, "cookies": cookies}

    def _extract_notebooklm_credentials(self, client: AgentBrowserClient):
        login_url = self._get_service_config("google")["login_url"]
        try:
            client.navigate(login_url)
        except Exception:
            pass

        token = client.evaluate("window.WIZ_global_data?.SNlM0e")
        cookie_list = client.get_cookies(login_url)
        cookie_header = self._build_cookie_header(cookie_list)
        if not token or not cookie_header:
            return None
        return token, cookie_header

    def _extract_notebooklm_tokens_from_page(self, client: AgentBrowserClient) -> dict:
        """Extract csrf_token and session_id from NotebookLM page via JavaScript."""
        js_code = """
            (() => {
                const scripts = document.querySelectorAll('script');
                let csrf = null, session = null;
                for (const s of scripts) {
                    const text = s.textContent || '';
                    const csrfMatch = text.match(/SNlM0e['"\\s:]+['"]([^'"]+)['"]/);
                    const sessionMatch = text.match(/FdrFJe['"\\s:]+['"]([^'"]+)['"]/);
                    if (csrfMatch) csrf = csrfMatch[1];
                    if (sessionMatch) session = sessionMatch[1];
                }
                // Also try WIZ_global_data
                if (!csrf && window.WIZ_global_data?.SNlM0e) {
                    csrf = window.WIZ_global_data.SNlM0e;
                }
                if (!session && window.WIZ_global_data?.FdrFJe) {
                    session = window.WIZ_global_data.FdrFJe;
                }
                return { csrf_token: csrf, session_id: session };
            })()
        """
        result = client.evaluate(js_code)
        if not result:
            return {"csrf_token": None, "session_id": None}
        return result

    def _extract_and_save_tokens(self, client: AgentBrowserClient) -> None:
        """Navigate to NotebookLM if needed and extract/save tokens."""
        try:
            # Check current URL - if not on NotebookLM, navigate there
            current_url = client.get_current_url() if hasattr(client, 'get_current_url') else ""
            if "notebooklm.google.com" not in current_url:
                print("   ⏳ Navigating to NotebookLM to extract API tokens...")
                client.navigate("https://notebooklm.google.com")
                time.sleep(3)  # Wait for page to load

            tokens = self._extract_notebooklm_tokens_from_page(client)
            if tokens.get("csrf_token") and tokens.get("session_id"):
                auth_file = self._auth_file("google")
                payload = json.loads(auth_file.read_text())
                payload["csrf_token"] = tokens["csrf_token"]
                payload["session_id"] = tokens["session_id"]
                payload["extracted_at"] = datetime.now(timezone.utc).isoformat()
                auth_file.write_text(json.dumps(payload))
                print("   ✓ Extracted NotebookLM API tokens")
            else:
                print("   ⚠ Could not extract API tokens (missing csrf_token or session_id)")
        except Exception as e:
            print(f"   ⚠ Could not extract API tokens: {e}")

    def refresh_notebooklm_tokens(self) -> dict:
        """Silently refresh csrf_token and session_id using stored cookies."""
        auth_file = self._auth_file("google")
        if not auth_file.exists():
            raise RuntimeError("No Google auth file found")

        try:
            payload = json.loads(auth_file.read_text())
        except Exception:
            raise RuntimeError("Invalid Google auth file")

        client = AgentBrowserClient(session_id=self._load_session_id() or DEFAULT_SESSION_ID)

        try:
            client.connect()

            # Restore cookies
            if payload.get("cookies"):
                client.set_storage_state({"cookies": payload["cookies"]})

            # Navigate to NotebookLM
            client.navigate("https://notebooklm.google.com")
            time.sleep(3)

            # Check if still authenticated
            snapshot = client.snapshot()
            if client.check_auth(snapshot):
                raise RuntimeError("Session expired, re-authentication required")

            # Extract fresh tokens
            tokens = self._extract_notebooklm_tokens_from_page(client)

            if not tokens.get("csrf_token") or not tokens.get("session_id"):
                raise RuntimeError("Failed to extract NotebookLM tokens from page")

            # Update auth file with new tokens
            payload["csrf_token"] = tokens["csrf_token"]
            payload["session_id"] = tokens["session_id"]
            payload["extracted_at"] = datetime.now(timezone.utc).isoformat()

            auth_file.write_text(json.dumps(payload))

            return tokens

        finally:
            client.disconnect()

    def validate(self, service: str = "google") -> bool:
        """Validate current authentication is still valid"""
        print("🔍 Validating authentication...")

        session_id = self._load_session_id()
        if not session_id:
            print("❌ No saved session")
            return False

        client = AgentBrowserClient(session_id=session_id)

        try:
            client.connect()
            self.restore_auth(service, client=client)
            client.navigate(self._get_service_config(service)["login_url"])
            time.sleep(2)

            snapshot = client.snapshot()

            if self._snapshot_indicates_auth(service, snapshot, client):
                print("✅ Authentication valid")
                self.save_auth(service, client=client)
                return True

            print("❌ Authentication expired")
            return False

        except AgentBrowserError as e:
            print(f"⚠️ Validation error: {e.message}")
            return False
        finally:
            client.disconnect()

    def clear(self, service: str = None):
        """Clear authentication data"""
        print("🧹 Clearing authentication data...")

        if service:
            auth_file = self._auth_file(service)
            if auth_file.exists():
                auth_file.unlink()
                print(f"   ✓ Removed {auth_file.name}")
        else:
            for config in self.SERVICES.values():
                auth_file = config["file"]
                if auth_file.exists():
                    auth_file.unlink()
                    print(f"   ✓ Removed {auth_file.name}")

            if AGENT_BROWSER_SESSION_FILE.exists():
                AGENT_BROWSER_SESSION_FILE.unlink()
                print("   ✓ Removed session_id")

        print("✅ Authentication data cleared")
        print("   Note: Browser profile preserved for future sessions.")

    def status(self, service: str = None):
        """Show current authentication status"""
        print("🔐 Authentication Status")
        print("=" * 40)

        # Show active account for Google
        if service is None or service == "google":
            active = self.account_manager.get_active_account()
            if active:
                print(f"Active Account: [{active.index}] {active.email}")
            else:
                accounts = self.account_manager.list_accounts()
                if accounts:
                    print("Active Account: None selected")
                else:
                    print("Active Account: No accounts configured")
            print()

        services = [service] if service else list(self.SERVICES.keys())
        for service_name in services:
            info = self.get_auth_info(service_name)
            print(f"Service: {service_name}")
            if info.get("authenticated"):
                print("   Status: ✅ Authenticated")
                print(f"   Since: {info.get('timestamp', 'Unknown')}")
            else:
                print("   Status: ❌ Not authenticated")
                print(f"   Run: python scripts/run.py auth_manager.py setup --service {service_name}")

        session_id = self._load_session_id()
        if session_id:
            print(f"   Session: {session_id}")

    def watchdog_status(self):
        """Show watchdog and daemon status"""
        status = get_watchdog_status()
        print("🧭 Watchdog Status")
        print("=" * 40)
        print(f"   Daemon running: {'✅' if status['daemon_running'] else '❌'}")
        print(f"   Watchdog PID: {status['watchdog_pid'] or 'None'}")
        print(f"   Watchdog alive: {'✅' if status['watchdog_alive'] else '❌'}")
        print(f"   Owner PID: {status['owner_pid'] or 'None'}")
        print(f"   Owner alive: {'✅' if status['owner_alive'] else '❌'}")
        if status["idle_seconds"] is not None:
            idle = int(status["idle_seconds"])
            timeout = int(status["idle_timeout_seconds"])
            remaining = max(0, timeout - idle)
            print(f"   Idle seconds: {idle}")
            print(f"   Idle timeout: {timeout}")
            print(f"   Time remaining: {remaining}")
        else:
            print("   Idle seconds: Unknown")

    def stop_daemon(self) -> bool:
        """Stop the agent-browser daemon for the saved session"""
        session_id = self._load_session_id() or DEFAULT_SESSION_ID
        client = AgentBrowserClient(session_id=session_id)
        stopped = client.shutdown()
        if stopped:
            print("✅ Daemon stopped")
        else:
            print("ℹ️ No daemon running")
        return stopped

    def handle_accounts_command(self, action: str, identifier: str = None):
        """Handle accounts subcommand actions."""
        if action == "list":
            self._accounts_list()
        elif action == "add":
            self._accounts_add()
        elif action == "switch":
            if not identifier:
                print("❌ Error: Provide account index or email")
                print("   Usage: auth_manager.py accounts switch <index|email>")
                return False
            self._accounts_switch(identifier)
        elif action == "remove":
            if not identifier:
                print("❌ Error: Provide account index or email")
                print("   Usage: auth_manager.py accounts remove <index|email>")
                return False
            self._accounts_remove(identifier)
        elif action == "reauth":
            if not identifier:
                print("❌ Error: Provide account index or email")
                print("   Usage: auth_manager.py accounts reauth <index|email>")
                return False
            self._accounts_reauth(identifier)
        else:
            print(f"❌ Unknown accounts action: {action}")
            return False
        return True

    def _accounts_list(self):
        """List all accounts."""
        accounts = self.account_manager.list_accounts()
        active = self.account_manager.get_active_account()

        if not accounts:
            print("📧 No Google accounts configured")
            print("   Run: python scripts/run.py auth_manager.py accounts add")
            return

        print("📧 Google Accounts:")
        for acc in accounts:
            is_active = " (active)" if active and acc.index == active.index else ""
            print(f"  [{acc.index}] {acc.email}{is_active}")
            print(f"      Added: {acc.added_at[:10] if acc.added_at else 'Unknown'}")

    def _accounts_add(self):
        """Add a new account via authentication."""
        print("🔐 Adding new Google account...")
        # Use fresh profile to force account selection instead of auto-login
        success = self.setup(service="google", use_fresh_profile=True)
        if success:
            active = self.account_manager.get_active_account()
            if active:
                print(f"✅ Account ready: [{active.index}] {active.email}")

    def _accounts_switch(self, identifier: str):
        """Switch active account and update active notebook."""
        try:
            account = self.account_manager.switch_account(identifier)
            print(f"✅ Switched to: [{account.index}] {account.email}")
            # Update symlink to point to new active account
            self._ensure_storage_state_symlink(quiet=True)

            # Switch active notebook to one belonging to the new account
            self._switch_active_notebook_for_account(account.index)
        except ValueError as e:
            print(f"❌ {e}")
            print("   Run: auth_manager.py accounts list")

    def _switch_active_notebook_for_account(self, account_index: int):
        """Switch active notebook to one belonging to the specified account."""
        from notebook_manager import NotebookLibrary

        library = NotebookLibrary()
        notebooks = library.list_notebooks_for_account(account_index)

        if notebooks:
            # Activate the first notebook for this account
            first_notebook = notebooks[0]
            notebook_id = first_notebook.get('id') or first_notebook.get('notebooklm_id')
            if notebook_id and notebook_id in library.notebooks:
                library.active_notebook_id = notebook_id
                library._save_library()
                print(f"   📓 Active notebook: {first_notebook.get('name', notebook_id)}")
        else:
            # No notebooks for this account - clear active notebook
            if library.active_notebook_id:
                library.active_notebook_id = None
                library._save_library()
                print("   📓 No notebooks for this account")

    def _accounts_remove(self, identifier: str):
        """Remove an account."""
        # Get account info before removal for display
        accounts = self.account_manager.list_accounts()
        target = None
        for acc in accounts:
            if str(acc.index) == str(identifier) or acc.email.lower() == identifier.lower():
                target = acc
                break

        if not target:
            print(f"❌ Account not found: {identifier}")
            return

        print("⚠️ Dangerous operation detected!")
        print("Operation: Remove account credentials")
        print(f"Target account: {target.email}")
        print("Risk: Credentials will be deleted")
        print()
        confirm = input("Are you sure you want to continue? [y/N]: ").strip().lower()

        if confirm not in ("y", "yes"):
            print("❌ Cancelled")
            return

        if self.account_manager.remove_account(identifier):
            print(f"✅ Removed account: {target.email}")
        else:
            print(f"❌ Failed to remove account")

    def _accounts_reauth(self, identifier: str):
        """Re-authenticate an existing account."""
        # Find the account
        accounts = self.account_manager.list_accounts()
        target = None
        for acc in accounts:
            if str(acc.index) == str(identifier) or acc.email.lower() == identifier.lower():
                target = acc
                break

        if not target:
            print(f"❌ Account not found: {identifier}")
            return

        print(f"🔐 Re-authenticating: {target.email}")
        print("   Please log in with this specific account in the browser.")

        # Switch to this account first
        self.account_manager.switch_account(target.index)

        # Run auth
        success = self.setup(service="google")
        if success:
            print(f"✅ Re-authenticated: [{target.index}] {target.email}")


def main():
    parser = argparse.ArgumentParser(description='Manage NotebookLM authentication')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Service choices for reuse
    service_choices = list(AuthManager.SERVICES.keys())

    # Subcommands with --service option
    setup_parser = subparsers.add_parser('setup', help='Setup authentication')
    setup_parser.add_argument('--service', choices=service_choices,
                              help='Auth service (default: google)')
    setup_parser.add_argument('--fresh', action='store_true',
                              help='Use fresh browser profile (forces account selection)')

    status_parser = subparsers.add_parser('status', help='Show authentication status')
    status_parser.add_argument('--service', choices=service_choices,
                               help='Auth service (default: all)')

    validate_parser = subparsers.add_parser('validate', help='Validate authentication')
    validate_parser.add_argument('--service', choices=service_choices,
                                 help='Auth service (default: google)')

    reauth_parser = subparsers.add_parser('reauth', help='Re-authenticate (uses fresh profile)')
    reauth_parser.add_argument('--service', choices=service_choices,
                               help='Auth service (default: google)')

    clear_parser = subparsers.add_parser('clear', help='Clear authentication data')
    clear_parser.add_argument('--service', choices=service_choices,
                              help='Auth service (default: all)')

    subparsers.add_parser('stop-daemon', help='Stop browser daemon')
    subparsers.add_parser('watchdog-status', help='Show watchdog status')

    # New accounts subcommand
    accounts_parser = subparsers.add_parser('accounts', help='Manage multiple Google accounts')
    accounts_parser.add_argument('action', choices=['list', 'add', 'switch', 'remove', 'reauth'],
                                 help='Account action')
    accounts_parser.add_argument('identifier', nargs='?', help='Account index or email')

    args = parser.parse_args()
    auth = AuthManager()

    if args.command == 'accounts':
        success = auth.handle_accounts_command(args.action, args.identifier)
        sys.exit(0 if success else 1)
    elif args.command == 'setup':
        success = auth.setup(service=args.service, use_fresh_profile=args.fresh)
        sys.exit(0 if success else 1)
    elif args.command == 'status':
        auth.status(service=args.service)
    elif args.command == 'validate':
        success = auth.validate(service=args.service or "google")
        sys.exit(0 if success else 1)
    elif args.command == 'reauth':
        service = args.service or "google"
        auth.clear(service=None if args.service is None else service)
        # Always use fresh profile for reauth to force account selection
        success = auth.setup(service=service, use_fresh_profile=True)
        sys.exit(0 if success else 1)
    elif args.command == 'clear':
        auth.clear(service=args.service)
    elif args.command == 'stop-daemon':
        success = auth.stop_daemon()
        sys.exit(0 if success else 1)
    elif args.command == 'watchdog-status':
        auth.watchdog_status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
