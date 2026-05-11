#!/usr/bin/env python3
"""
Agent Browser Client for nblm
Python client that communicates with agent-browser daemon via Unix socket
"""

import json
import os
import re
import socket
import subprocess
import time
import sys
import tempfile
from urllib.parse import urlparse
from pathlib import Path
from typing import Optional, Dict, Any

from config import (
    AGENT_BROWSER_ACTIVITY_FILE,
    AGENT_BROWSER_STATE_FILE,
    AGENT_BROWSER_WATCHDOG_PID_FILE,
    AGENT_BROWSER_SOCKET_DIR,
    DEFAULT_SESSION_ID,
    SKILL_DIR
)


class AgentBrowserError(Exception):
    """Structured error for agent-browser operations"""

    def __init__(self, code: str, message: str, recovery: str, snapshot: str = None):
        self.code = code
        self.message = message
        self.recovery = recovery
        self.snapshot = snapshot
        super().__init__(f"[{code}] {message}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "recovery": self.recovery,
            "snapshot": self.snapshot
        }


class AgentBrowserClient:
    """Python client for agent-browser daemon"""

    def __init__(self, session_id: str = None, headed: bool = False):
        self.session_id = session_id or DEFAULT_SESSION_ID
        self.socket_path = AGENT_BROWSER_SOCKET_DIR / f"agent-browser-{self.session_id}.sock"
        self.socket: Optional[socket.socket] = None
        self._buffer = b""
        self._command_id = 0
        self.headed = headed
        self._started_daemon = False

    def connect(self) -> bool:
        """Connect to daemon, starting it if necessary"""
        daemon_running = self._daemon_is_running()

        if self.headed and daemon_running:
            self._stop_daemon()
            daemon_running = False

        if not daemon_running:
            self._start_daemon()
            self._started_daemon = True

        try:
            self.socket = self._connect_socket()
            self.launch(headless=not self.headed)
            self.restore_storage_state()
            return True
        except ConnectionRefusedError:
            raise AgentBrowserError(
                code="DAEMON_UNAVAILABLE",
                message="Cannot connect to browser daemon",
                recovery="Check Node.js installation, ensure agent-browser is installed"
            )

    def disconnect(self):
        """Close connection to daemon without stopping it"""
        if self.socket:
            try:
                self.socket.close()
            except Exception:
                pass
            self.socket = None

    def shutdown(self, timeout: int = 5) -> bool:
        """Request daemon shutdown for this session"""
        is_running = bool(self.socket) or self._daemon_is_running()
        if not is_running:
            return False

        if self.socket:
            try:
                self._send_command("close")
            except AgentBrowserError:
                pass
            self.disconnect()
        else:
            sock = None
            try:
                sock = self._connect_socket(timeout=timeout)
                response = self._send_command_on_socket(sock, "close")
                if not response.get("success", False):
                    raise AgentBrowserError(
                        code="CLI_ERROR",
                        message=str(response.get("error", "Unknown error")),
                        recovery="Retry the shutdown command"
                    )
            finally:
                if sock:
                    try:
                        sock.close()
                    except Exception:
                        pass

        self._await_socket_gone(timeout)
        return True

    def launch(self, headless: bool = True) -> Dict[str, Any]:
        """Launch browser in daemon

        Args:
            headless: Run in headless mode
        """
        params = {"headless": headless}
        return self._send_command("launch", params)

    def _daemon_is_running(self) -> bool:
        """Check if daemon socket exists and is responsive"""
        if not self.socket_path.exists():
            return False
        try:
            test_socket = self._connect_socket(timeout=1)
            test_socket.close()
            return True
        except Exception:
            return False

    def _connect_socket(self, timeout: int = 120) -> socket.socket:
        """Create a configured socket connection to the daemon"""
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect(str(self.socket_path))
        return sock

    def _start_daemon(self):
        """Start the agent-browser daemon"""
        print("🚀 Starting browser daemon...")

        env = os.environ.copy()
        env["AGENT_BROWSER_SESSION"] = self.session_id

        daemon_script = SKILL_DIR / "node_modules" / "agent-browser" / "dist" / "daemon.js"

        if not daemon_script.exists():
            raise AgentBrowserError(
                code="DAEMON_UNAVAILABLE",
                message="agent-browser daemon script not found",
                recovery="Run 'npm install' in the skill directory"
            )

        subprocess.Popen(
            ["node", str(daemon_script)],
            cwd=str(SKILL_DIR),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Wait for daemon to be ready
        for _ in range(30):  # 30 second timeout
            time.sleep(1)
            if self._daemon_is_running():
                print("✅ Daemon started")
                return

        raise AgentBrowserError(
            code="DAEMON_UNAVAILABLE",
            message="Daemon failed to start within timeout",
            recovery="Check Node.js installation and agent-browser dependency"
        )

    def _stop_daemon(self):
        """Stop the daemon for this session"""
        self.shutdown(timeout=5)

    def _send_command(self, action: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send command to daemon and receive response"""
        if not self.socket:
            raise AgentBrowserError(
                code="NOT_CONNECTED",
                message="Not connected to daemon",
                recovery="Call connect() first"
            )

        self._record_activity()
        self._command_id += 1
        command = {"id": str(self._command_id), "action": action}
        if params:
            command.update(params)

        # Send JSON terminated by newline
        message = json.dumps(command) + "\n"
        self.socket.sendall(message.encode())

        # Read response
        response = self._read_response()
        if not response.get("success", False):
            raise AgentBrowserError(
                code="CLI_ERROR",
                message=str(response.get("error", "Unknown error")),
                recovery="Retry the command or restart the daemon"
            )

        return response.get("data", {})

    def _send_command_on_socket(self, sock: socket.socket, action: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send command over a provided socket and return raw response"""
        self._command_id += 1
        command = {"id": str(self._command_id), "action": action}
        if params:
            command.update(params)

        message = json.dumps(command) + "\n"
        sock.sendall(message.encode())

        buffer = b""
        while True:
            if b"\n" in buffer:
                line, _ = buffer.split(b"\n", 1)
                return json.loads(line.decode())

            chunk = sock.recv(65536)
            if not chunk:
                raise AgentBrowserError(
                    code="CONNECTION_CLOSED",
                    message="Daemon closed connection",
                    recovery="Retry the command or restart the daemon"
                )
            buffer += chunk

    def _read_response(self) -> Dict[str, Any]:
        """Read JSON response from daemon"""
        while True:
            # Check buffer for complete message
            if b"\n" in self._buffer:
                line, self._buffer = self._buffer.split(b"\n", 1)
                return json.loads(line.decode())

            # Read more data
            try:
                chunk = self.socket.recv(65536)
                if not chunk:
                    raise AgentBrowserError(
                        code="CONNECTION_CLOSED",
                        message="Daemon closed connection",
                        recovery="Reconnect to daemon"
                    )
                self._buffer += chunk
            except socket.timeout:
                raise AgentBrowserError(
                    code="TIMEOUT",
                    message="Daemon response timeout",
                    recovery="Operation took too long, try again"
                )

    def _await_socket_gone(self, timeout: int = 5) -> bool:
        """Wait for the daemon socket to be removed"""
        deadline = time.time() + timeout
        while time.time() < deadline:
            if not self.socket_path.exists():
                return True
            time.sleep(0.1)
        return False

    def get_storage_state(self, state_path: Optional[Path] = None) -> dict:
        """Get complete Playwright storage state (cookies + origins)"""
        temp_path = None
        target_path = state_path
        if target_path is None:
            fd, temp_name = tempfile.mkstemp(prefix="agent-browser-state-", suffix=".json")
            os.close(fd)
            temp_path = Path(temp_name)
            target_path = temp_path

        try:
            self._send_command("state_save", {"path": str(target_path)})
            return json.loads(target_path.read_text())
        except Exception:
            return {}
        finally:
            if temp_path:
                try:
                    temp_path.unlink()
                except Exception:
                    pass

    def set_storage_state(self, state: dict) -> bool:
        """Restore storage state from saved Playwright state"""
        if not state:
            return False

        cookies = state.get("cookies") or []
        if cookies:
            self._set_cookies(cookies)

        for origin_data in state.get("origins", []) or []:
            origin = origin_data.get("origin")
            if not origin:
                continue

            local_storage = origin_data.get("localStorage") or []
            session_storage = origin_data.get("sessionStorage") or []

            if not local_storage and not session_storage:
                continue

            # Navigate and wait for load state, then additional delay for stability
            self.navigate(origin, wait_until="load")
            # Additional wait to ensure execution context is fully stable after any JS execution
            self._send_command("wait", {"timeout": 3000})
            for item in local_storage:
                key = item.get("name")
                value = item.get("value")
                if key is None or value is None:
                    continue
                self._send_command(
                    "storage_set",
                    {"type": "local", "key": key, "value": value}
                )
            for item in session_storage:
                key = item.get("name")
                value = item.get("value")
                if key is None or value is None:
                    continue
                self._send_command(
                    "storage_set",
                    {"type": "session", "key": key, "value": value}
                )

        return True

    def save_storage_state(self, state_path: Path = AGENT_BROWSER_STATE_FILE) -> bool:
        """Persist Playwright storage state to disk"""
        try:
            payload = self.get_storage_state()
            if not payload:
                return False
            state_path.parent.mkdir(parents=True, exist_ok=True)
            with open(state_path, "w") as handle:
                json.dump(payload, handle)
            return True
        except Exception:
            return False

    def restore_storage_state(self, state_path: Path = AGENT_BROWSER_STATE_FILE) -> bool:
        """Restore Playwright storage state from disk"""
        if not state_path.exists():
            return False
        try:
            payload = json.loads(state_path.read_text())
        except Exception:
            return False
        return self.set_storage_state(payload)

    def _record_activity(self):
        """Record activity and ensure the watchdog is running"""
        try:
            AGENT_BROWSER_ACTIVITY_FILE.parent.mkdir(parents=True, exist_ok=True)
            payload = {"timestamp": time.time()}
            owner_pid = None
            env_owner_pid = os.environ.get("AGENT_BROWSER_OWNER_PID")
            if env_owner_pid and env_owner_pid.isdigit():
                owner_pid = int(env_owner_pid)
            else:
                existing_owner_pid = self._read_existing_owner_pid()
                if existing_owner_pid is not None and self._pid_is_alive(existing_owner_pid):
                    owner_pid = existing_owner_pid
            if owner_pid is not None:
                payload["owner_pid"] = owner_pid
            with open(AGENT_BROWSER_ACTIVITY_FILE, "w") as handle:
                json.dump(payload, handle)
        except Exception:
            return

        try:
            self._ensure_watchdog()
        except Exception:
            pass

    def _read_existing_owner_pid(self) -> Optional[int]:
        """Read the previously recorded owner PID if available."""
        try:
            if not AGENT_BROWSER_ACTIVITY_FILE.exists():
                return None
            payload = json.loads(AGENT_BROWSER_ACTIVITY_FILE.read_text())
        except Exception:
            return None

        owner_pid = payload.get("owner_pid")
        if isinstance(owner_pid, int):
            return owner_pid
        if isinstance(owner_pid, str) and owner_pid.isdigit():
            return int(owner_pid)
        return None

    def _ensure_watchdog(self):
        """Start the idle watchdog if needed"""
        existing_pid = self._read_watchdog_pid()
        if existing_pid and self._pid_is_alive(existing_pid):
            return

        env = os.environ.copy()
        env["AGENT_BROWSER_SESSION"] = self.session_id

        watchdog_script = SKILL_DIR / "scripts" / "daemon_watchdog.py"
        if not watchdog_script.exists():
            return

        process = subprocess.Popen(
            [sys.executable, str(watchdog_script)],
            cwd=str(SKILL_DIR),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        self._write_watchdog_pid(process.pid)

    def _read_watchdog_pid(self) -> Optional[int]:
        """Read watchdog PID from disk if present"""
        try:
            if AGENT_BROWSER_WATCHDOG_PID_FILE.exists():
                return int(AGENT_BROWSER_WATCHDOG_PID_FILE.read_text().strip())
        except Exception:
            return None
        return None

    def _write_watchdog_pid(self, pid: int):
        """Write watchdog PID to disk"""
        try:
            AGENT_BROWSER_WATCHDOG_PID_FILE.parent.mkdir(parents=True, exist_ok=True)
            AGENT_BROWSER_WATCHDOG_PID_FILE.write_text(str(pid))
        except Exception:
            pass

    def _pid_is_alive(self, pid: int) -> bool:
        """Check whether a PID is alive"""
        if pid <= 0:
            return False
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
        return True

    def _get_cookies(self) -> list:
        """Return all cookies from the current context"""
        return self.get_cookies()

    def get_cookies(self, urls: Optional[object] = None) -> list:
        """Return cookies for the provided URL(s) or all cookies when omitted"""
        params = {}
        if urls:
            if isinstance(urls, (list, tuple)):
                params["urls"] = list(urls)
            else:
                params["urls"] = [str(urls)]
        response = self._send_command("cookies_get", params or None)
        return response.get("cookies", [])

    def evaluate(self, script: str):
        """Evaluate a script in the page context and return the result"""
        response = self._send_command("evaluate", {"script": script})
        return response.get("result")

    def _set_cookies(self, cookies: list):
        """Set cookies on the current context"""
        if not cookies:
            return
        self._send_command("cookies_set", {"cookies": cookies})

    def _get_local_storage(self) -> dict:
        """Return localStorage for the current origin"""
        response = self._send_command("storage_get", {"type": "local"})
        return response.get("data", {}) or {}

    def _set_local_storage(self, local_storage: dict):
        """Set localStorage entries on the current origin"""
        if not local_storage:
            return
        for key, value in local_storage.items():
            self._send_command(
                "storage_set",
                {"type": "local", "key": key, "value": value}
            )

    def _get_origin(self) -> Optional[str]:
        """Return origin for the current page"""
        response = self._send_command("url")
        url = response.get("url")
        if not url:
            return None
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return None
        return f"{parsed.scheme}://{parsed.netloc}"

    # === Browser Actions ===

    def navigate(self, url: str, wait_until: Optional[str] = None) -> Dict[str, Any]:
        """Navigate to URL"""
        print(f"🌐 Navigating to {url[:50]}...")
        params = {"url": url}
        if wait_until:
            params["waitUntil"] = wait_until
        elif self._started_daemon:
            params["waitUntil"] = "domcontentloaded"
        response = self._send_command("navigate", params)
        return response

    def snapshot(self, prune: bool = True, interactive: bool = False) -> str:
        """Get accessibility tree snapshot of current page"""
        params = {"compact": prune}
        if interactive:
            params["interactive"] = True
        response = self._send_command("snapshot", params)

        return response.get("snapshot", "")

    def click(self, ref: str) -> Dict[str, Any]:
        """Click element by ref"""
        print(f"🖱️ Clicking ref={ref}")
        response = self._send_command("click", {"selector": f"@{ref}"})
        return response

    def fill(self, ref: str, text: str) -> Dict[str, Any]:
        """Fill input field by ref (clears first)"""
        print(f"⌨️ Filling ref={ref}")
        response = self._send_command("fill", {"selector": f"@{ref}", "value": text})
        return response

    def upload(self, selector: str, files) -> Dict[str, Any]:
        """Upload file(s) using an input selector"""
        file_list = files if isinstance(files, list) else [files]
        print(f"📤 Uploading {len(file_list)} file(s)")
        response = self._send_command("upload", {"selector": selector, "files": file_list})
        return response

    def type_text(self, ref: str, text: str, submit: bool = False) -> Dict[str, Any]:
        """Type text into element (appends to existing)"""
        print(f"⌨️ Typing into ref={ref}")
        response = self._send_command("type", {"selector": f"@{ref}", "text": text})
        if submit:
            self.press_key("Enter")
        return response

    def press_key(self, key: str) -> Dict[str, Any]:
        """Press keyboard key"""
        response = self._send_command("press", {"key": key})
        return response

    def wait_for(self, timeout: int = 30) -> Dict[str, Any]:
        """Wait for time in seconds"""
        response = self._send_command("wait", {"timeout": timeout * 1000})
        return response

    def wait_for_load(self, state: str = "networkidle") -> Dict[str, Any]:
        """Wait for page load state (load, domcontentloaded, networkidle)."""
        return self._send_command("wait", {"load": state})

    def wait_for_selector(self, selector: str, timeout_ms: int = 10000, state: str = "attached") -> Dict[str, Any]:
        """Wait for a selector to appear in the DOM."""
        params = {"selector": selector, "timeout": timeout_ms, "state": state}
        return self._send_command("wait", params)

    # === Utility Methods ===

    def check_auth(self, snapshot: str = None) -> bool:
        """Check if current page indicates authentication is needed"""
        if snapshot is None:
            snapshot = self.snapshot()

        auth_field_indicators = (
            "email or phone",
            "password",
            "username",
        )
        auth_action_indicators = (
            "sign in",
            "log in",
            "login",
            "choose an account",
            "select an account",
            "use another account",
            "signed out",
        )

        for line in snapshot.splitlines():
            line_lower = line.strip().lower()
            if not line_lower:
                continue

            if "textbox" in line_lower:
                if any(indicator in line_lower for indicator in auth_field_indicators):
                    return True

            is_action_line = (
                line_lower.startswith("heading")
                or "button" in line_lower
                or "link" in line_lower
            )
            if is_action_line and any(indicator in line_lower for indicator in auth_action_indicators):
                return True

        return False

    def find_ref_by_role(self, snapshot: str, role: str, hint: str = None) -> Optional[str]:
        """Parse snapshot to find element ref by role and optional text hint"""
        for line in snapshot.split('\n'):
            line_lower = line.lower()
            if role.lower() in line_lower:
                if hint is None or hint.lower() in line_lower:
                    match = re.search(r'\[ref=(\w+)\]', line)
                    if match:
                        return match.group(1)
        return None

    def find_refs_by_role(self, snapshot: str, role: str) -> list:
        """Find all refs matching a role"""
        refs = []
        for line in snapshot.split('\n'):
            if role.lower() in line.lower():
                match = re.search(r'\[ref=(\w+)\]', line)
                if match:
                    refs.append(match.group(1))
        return refs


if __name__ == "__main__":
    print("Agent Browser Client - Use with ask_question.py")
