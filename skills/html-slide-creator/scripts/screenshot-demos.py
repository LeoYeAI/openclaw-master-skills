#!/usr/bin/env python3
"""
screenshot-demos.py — capture first-slide screenshots of all demo HTMLs
Usage: python3 screenshot-demos.py [demos-dir] [output-dir]
Requires: pip install playwright; playwright install --with-deps chromium (or use system Chrome)
"""
import sys
import os
import pathlib
import time

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("ERROR: playwright not installed. Run: pip install playwright")
    sys.exit(1)

DEMOS_DIR = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).parent.parent / "demos"
OUT_DIR   = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else DEMOS_DIR / "screenshots"
WIDTH, HEIGHT = 1280, 720

OUT_DIR.mkdir(parents=True, exist_ok=True)

# Map demo filename → screenshot filename
DEMOS = [
    ("intro-en.html",        "blue-sky.png"),          # Blue Sky style
    ("bold-signal.html",     "bold-signal.png"),
    ("electric-studio.html", "electric-studio.png"),
    ("creative-voltage.html","creative-voltage.png"),
    ("dark-botanical.html",  "dark-botanical.png"),
    ("notebook-tabs.html",   "notebook-tabs.png"),
    ("pastel-geometry.html", "pastel-geometry.png"),
    ("split-pastel.html",    "split-pastel.png"),
    ("vintage-editorial.html","vintage-editorial.png"),
    ("neon-cyber.html",      "neon-cyber.png"),
    ("terminal-green.html",  "terminal-green.png"),
    ("swiss-modern.html",    "swiss-modern.png"),
    ("paper-ink.html",       "paper-ink.png"),
    ("aurora-mesh.html",     "aurora-mesh.png"),
    ("enterprise-dark.html", "enterprise-dark.png"),
    ("glassmorphism.html",   "glassmorphism.png"),
    ("neo-brutalism.html",   "neo-brutalism.png"),
    ("chinese-chan.html",          "chinese-chan.png"),
    ("data-story.html",            "data-story.png"),
    ("intro-modern-newspaper.html","modern-newspaper.png"),
    ("intro-neo-retro-dev.html",   "neo-retro-dev.png"),
]

def screenshot_demo(page, html_path, out_path, width=WIDTH, height=HEIGHT):
    url = html_path.as_uri()
    page.set_viewport_size({"width": width, "height": height})
    page.goto(url, wait_until="networkidle", timeout=15000)
    # Wait for fonts and animations to load
    page.wait_for_timeout(1200)
    page.screenshot(path=str(out_path), clip={"x": 0, "y": 0, "width": width, "height": height})
    return True

def main():
    missing = [name for name, _ in DEMOS if not (DEMOS_DIR / name).exists()]
    if missing:
        print(f"WARNING: Missing demo files: {missing}")

    with sync_playwright() as pw:
        # Try system Chrome first, fall back to Chromium
        try:
            browser = pw.chromium.launch(channel="chrome", headless=True)
            print("Using system Chrome")
        except Exception:
            try:
                browser = pw.chromium.launch(headless=True)
                print("Using Playwright Chromium")
            except Exception as e:
                print(f"ERROR: Cannot launch browser: {e}")
                print("Install Chrome or run: playwright install chromium")
                sys.exit(1)

        page = browser.new_page()

        ok, failed = [], []
        for html_name, png_name in DEMOS:
            html_path = DEMOS_DIR / html_name
            out_path  = OUT_DIR / png_name
            if not html_path.exists():
                print(f"  SKIP  {html_name} (not found)")
                continue
            try:
                screenshot_demo(page, html_path, out_path)
                size_kb = out_path.stat().st_size // 1024
                print(f"  OK    {png_name} ({size_kb} KB)")
                ok.append(png_name)
            except Exception as e:
                print(f"  FAIL  {html_name}: {e}")
                failed.append(html_name)

        browser.close()

    print(f"\nDone: {len(ok)} screenshots saved to {OUT_DIR}")
    if failed:
        print(f"Failed: {failed}")

if __name__ == "__main__":
    main()
