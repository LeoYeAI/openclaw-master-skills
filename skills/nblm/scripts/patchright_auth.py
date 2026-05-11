#!/usr/bin/env python3
"""
Patchright-based Google Authentication for nblm

Uses Patchright (anti-detection Playwright fork) to bypass Google's
"This browser or app may not be secure" blocking for personal Gmail accounts.

Key techniques:
- Uses real Chrome executable (not Chrome for Testing)
- Persistent context maintains session
- No custom headers that trigger detection
- Patchright's anti-detection patches
"""

import json
import os
import shutil
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

from config import (
    GOOGLE_AUTH_FILE,
    SKILL_DIR,
)

# NotebookLM URL
NOTEBOOKLM_URL = "https://notebooklm.google.com"


# Patchright browser profile directory
PATCHRIGHT_PROFILE_DIR = SKILL_DIR / "data" / "patchright-profile"


def _find_chrome_executable() -> Optional[str]:
    """Find the real Chrome executable path on the current platform."""
    import platform
    system = platform.system()

    if system == "Darwin":  # macOS
        paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            os.path.expanduser("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        ]
    elif system == "Windows":
        paths = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
        ]
    else:  # Linux
        paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/opt/google/chrome/chrome",
        ]

    for path in paths:
        if os.path.isfile(path):
            return path
    return None


def _extract_storage_state(context) -> Dict[str, Any]:
    """Extract cookies and localStorage from browser context."""
    # Get cookies
    cookies = context.cookies()

    # Get localStorage from NotebookLM origin
    origins = []
    try:
        page = context.pages[0] if context.pages else None
        if page and "notebooklm.google.com" in page.url:
            local_storage = page.evaluate("() => Object.entries(localStorage)")
            origins.append({
                "origin": "https://notebooklm.google.com",
                "localStorage": [{"name": k, "value": v} for k, v in local_storage]
            })
    except Exception:
        pass  # localStorage extraction is optional

    return {
        "cookies": cookies,
        "origins": origins,
    }


def _save_auth_state(storage_state: Dict[str, Any]) -> None:
    """Save authentication state to google.json."""
    GOOGLE_AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Add timestamp
    storage_state["notebooklm_updated_at"] = datetime.now(timezone.utc).isoformat()

    with open(GOOGLE_AUTH_FILE, "w") as f:
        json.dump(storage_state, f, indent=2)


def _extract_email_from_page(page) -> Optional[str]:
    """Extract the logged-in user's email from the page."""
    try:
        email = page.evaluate("""
            () => {
                // Try aria-label on account button
                const accountBtn = document.querySelector('[aria-label*="@"]');
                if (accountBtn) {
                    const match = accountBtn.getAttribute('aria-label').match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}/);
                    if (match) return match[0];
                }

                // Try data attributes
                const elements = document.querySelectorAll('[data-email], [data-user-email]');
                for (const el of elements) {
                    const email = el.getAttribute('data-email') || el.getAttribute('data-user-email');
                    if (email && email.includes('@')) return email;
                }

                // Try text content in account-related elements
                const accountElements = document.querySelectorAll('[class*="account"], [class*="user"], [class*="profile"]');
                for (const el of accountElements) {
                    const match = el.textContent.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}/);
                    if (match) return match[0];
                }

                return null;
            }
        """)
        return email
    except Exception:
        return None


def authenticate_with_patchright(
    timeout_seconds: int = 600,
    use_fresh_profile: bool = False
) -> tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    Perform Google authentication using Patchright.

    Opens a real Chrome browser for user to log in manually.
    Waits for successful authentication, then extracts session data.

    Args:
        timeout_seconds: Maximum time to wait for user to complete login
        use_fresh_profile: If True, use a temporary profile to force account selection

    Returns:
        Tuple of (success, email, storage_state):
        - success: True if authentication succeeded
        - email: The authenticated user's email address (if extractable)
        - storage_state: Browser storage state dict for saving credentials
    """
    try:
        from patchright.sync_api import sync_playwright
    except ImportError:
        print("❌ Patchright not installed. Run: pip install patchright && patchright install chromium")
        return False, None, None

    # Find real Chrome executable - always use real Chrome
    chrome_path = _find_chrome_executable()
    if not chrome_path:
        print("❌ Google Chrome not found. Please install Chrome.")
        return False, None, None

    print("🔐 Opening Chrome for Google authentication...", flush=True)
    print(f"   Using: {chrome_path}", flush=True)
    print("   (Patchright anti-detection enabled)", flush=True)
    if use_fresh_profile:
        print("   (Fresh session for new account login)", flush=True)
    print(flush=True)

    # Determine profile directory
    temp_profile_dir = None
    if use_fresh_profile:
        # Use a temporary profile for adding new accounts
        # This avoids Chrome's profile switching when signing into a different account
        temp_profile_dir = tempfile.mkdtemp(prefix="nblm-auth-")
        profile_dir = temp_profile_dir
        print(f"🧹 Using temporary profile for clean login...", flush=True)
    else:
        # Use persistent profile for normal auth/re-auth
        PATCHRIGHT_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
        profile_dir = str(PATCHRIGHT_PROFILE_DIR)

    try:
        with sync_playwright() as p:
            # Launch with anti-detection settings
            # Key: ignore_default_args removes --enable-automation flag
            # args disable additional automation indicators
            launch_args = [
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--disable-dev-shm-usage",
                "--no-first-run",
                "--no-default-browser-check",
                # Enable remote debugging so we can detect pages in other windows
                "--remote-debugging-port=0",
            ]

            # For fresh profile: disable Chrome sign-in and sync to prevent profile switching
            if use_fresh_profile:
                launch_args.extend([
                    "--disable-sync",
                    "--disable-features=ChromeWhatsNewUI",
                    "--no-service-autorun",
                    "--password-store=basic",
                ])

            # Build launch options
            launch_options = {
                "user_data_dir": profile_dir,
                "headless": False,               # Must be visible for auth
                "no_viewport": True,             # Don't override viewport
                "ignore_default_args": [
                    "--enable-automation",    # Removes automation banner
                    "--enable-blink-features=AutomationControlled",
                ],
                "args": launch_args,
            }

            # Only set executable_path if using real Chrome
            if chrome_path:
                launch_options["executable_path"] = chrome_path

            context = p.chromium.launch_persistent_context(**launch_options)

            page = context.pages[0] if context.pages else context.new_page()

            # Get CDP session for detecting pages across all windows
            cdp_session = None
            try:
                cdp_session = context.new_cdp_session(page)
            except Exception:
                pass  # CDP not available, will use context.pages only

            # Navigate to NotebookLM - it will redirect to Google login if needed
            print(f"🌐 Navigating to {NOTEBOOKLM_URL}...", flush=True)
            page.goto(NOTEBOOKLM_URL, wait_until="domcontentloaded")

            # Wait for user to complete authentication
            print(flush=True)
            print("⏳ Please complete login in the browser window...", flush=True)
            print("   (DO NOT close the browser - it will close automatically)", flush=True)
            print(flush=True)

            def check_cdp_for_notebooklm() -> bool:
                """Use CDP to check if any Chrome page has NotebookLM."""
                if not cdp_session:
                    return False
                try:
                    result = cdp_session.send("Target.getTargets")
                    for target in result.get("targetInfos", []):
                        url = target.get("url", "")
                        if "notebooklm.google.com" in url and "accounts.google.com" not in url:
                            return True
                except Exception:
                    pass
                return False

            start_time = time.time()
            authenticated = False
            auth_page = None
            last_url = ""
            check_count = 0

            while time.time() - start_time < timeout_seconds:
                try:
                    # Check if browser/page is still open
                    if not context.pages or len(context.pages) == 0:
                        # Browser was closed by user
                        print("⚠️ Browser was closed manually", flush=True)
                        # If we were on NotebookLM, try to save what we have
                        if "notebooklm.google.com" in last_url:
                            print("   Attempting to save session from last URL...", flush=True)
                            authenticated = True
                        break

                    # Check ALL pages in context (Google may open new tabs)
                    for p in context.pages:
                        try:
                            current_url = p.url
                            # Check if any page reached NotebookLM
                            if "notebooklm.google.com" in current_url:
                                if "accounts.google.com" not in current_url and "/signin" not in current_url:
                                    print("   ✓ Detected NotebookLM homepage!", flush=True)
                                    auth_page = p
                                    time.sleep(2)
                                    authenticated = True
                                    break
                        except Exception:
                            continue  # Page might be closing

                    if authenticated:
                        break

                    # Also check via CDP for pages in other Chrome windows
                    if not authenticated and check_cdp_for_notebooklm():
                        print("   ✓ Detected NotebookLM in another window via CDP!", flush=True)
                        time.sleep(2)
                        authenticated = True
                        break

                    # Use first page for status display
                    current_url = context.pages[0].url if context.pages else ""
                    check_count += 1

                    # Debug: show URL periodically
                    if check_count % 5 == 1:  # Every 5 seconds
                        num_pages = len(context.pages)
                        page_info = f" ({num_pages} tabs)" if num_pages > 1 else ""
                        print(f"   Checking: {current_url[:60]}{page_info}", flush=True)

                    last_url = current_url
                    time.sleep(1)
                except Exception as e:
                    # Browser might have been closed
                    error_msg = str(e)
                    if "closed" in error_msg.lower():
                        print("⚠️ Browser was closed", flush=True)
                        if "notebooklm.google.com" in last_url:
                            authenticated = True
                    else:
                        print(f"❌ Browser error: {e}", flush=True)
                    break

            # Use the page where auth completed, or first page
            page = auth_page if auth_page else (context.pages[0] if context.pages else None)

            if authenticated:
                print("✅ Authentication successful!", flush=True)

                # If auth was detected via CDP (another window), navigate our page to NotebookLM
                # to get the cookies (session is shared across windows)
                if page and "notebooklm.google.com" not in page.url:
                    print("   Navigating to NotebookLM to capture session...", flush=True)
                    try:
                        page.goto(NOTEBOOKLM_URL, wait_until="domcontentloaded")
                        time.sleep(2)  # Wait for page to load
                    except Exception:
                        pass

                # Extract email and storage state before browser closes
                try:
                    email = _extract_email_from_page(page)
                    if email:
                        print(f"   ✓ Logged in as: {email}", flush=True)
                    storage_state = _extract_storage_state(context)
                except Exception:
                    # Browser already closed, can't extract
                    print("   ⚠️ Could not extract session (browser closed)", flush=True)
                    email = None
                    storage_state = None
            else:
                print("❌ Authentication timed out", flush=True)
                email = None
                storage_state = None

            context.close()

            # Clean up temporary profile if used
            if temp_profile_dir and os.path.exists(temp_profile_dir):
                try:
                    shutil.rmtree(temp_profile_dir)
                except Exception:
                    pass  # Best effort cleanup

            return authenticated, email, storage_state
    except Exception as e:
        print(f"❌ Authentication error: {e}", flush=True)
        # Clean up temporary profile on error
        if temp_profile_dir and os.path.exists(temp_profile_dir):
            try:
                shutil.rmtree(temp_profile_dir)
            except Exception:
                pass
        return False, None, None


def clear_patchright_profile() -> bool:
    """Clear the Patchright browser profile for fresh auth."""
    import shutil

    if PATCHRIGHT_PROFILE_DIR.exists():
        shutil.rmtree(PATCHRIGHT_PROFILE_DIR)
        print(f"   ✓ Cleared Patchright profile")
        return True
    return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "clear":
        clear_patchright_profile()
    else:
        success, email, storage_state = authenticate_with_patchright()
        if success:
            print(f"Email: {email}")
            # Save for backward compatibility when run standalone
            if storage_state:
                _save_auth_state(storage_state)
        sys.exit(0 if success else 1)
