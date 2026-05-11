"""
Shared Playwright browser for Content Claw.

Used by extract.py to render web pages for source extraction.

Usage:
    from browser import create_browser
    with create_browser() as page:
        page.goto("https://example.com")
"""

import sys
from contextlib import contextmanager
from pathlib import Path

STEALTH_INIT = "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
DEFAULT_VIEWPORT = {"width": 1280, "height": 800}
BROWSER_ARGS = ["--disable-blink-features=AutomationControlled", "--no-sandbox"]


@contextmanager
def create_browser():
    """Context manager that yields a Page with stealth settings."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=BROWSER_ARGS)
        context = browser.new_context(
            user_agent=USER_AGENT,
            viewport=DEFAULT_VIEWPORT,
            locale="en-US",
        )
        page = context.new_page()
        page.add_init_script(STEALTH_INIT)
        try:
            yield page
        finally:
            context.close()
            browser.close()
