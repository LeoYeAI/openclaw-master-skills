#!/usr/bin/env python3
"""
html_to_png.py - Convert an HTML infographic to a full-page PNG screenshot.

Uses Playwright (headless Chromium) to render the HTML and capture a
full-page screenshot at a configurable viewport width.

Usage:
    python3 html_to_png.py <input.html> [output.png] [--width 1200] [--scale 2]

Arguments:
    input.html   Path to the HTML file to screenshot
    output.png   Output PNG path (default: same name as input with .png)
    --width      Viewport width in pixels (default: 1200)
    --scale       Device scale factor for retina/HiDPI (default: 2)

Requirements:
    pip install playwright
    playwright install chromium
"""

import argparse
import os
import sys
import subprocess


def ensure_playwright():
    """Install playwright + chromium if not available."""
    try:
        import playwright
    except ImportError:
        print("[html_to_png] Installing playwright...", file=sys.stderr)
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "playwright", "-q",
             "--break-system-packages"],
            stdout=subprocess.DEVNULL
        )

    # Check if chromium is installed
    chromium_check = subprocess.run(
        [sys.executable, "-m", "playwright", "install", "--dry-run", "chromium"],
        capture_output=True, text=True
    )
    if chromium_check.returncode != 0 or "chromium" not in chromium_check.stdout.lower():
        print("[html_to_png] Installing chromium browser...", file=sys.stderr)
        subprocess.check_call(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )


def html_to_png(input_path: str, output_path: str, width: int = 1200, scale: int = 2):
    """Render HTML file and save full-page PNG screenshot."""
    from playwright.sync_api import sync_playwright

    abs_input = os.path.abspath(input_path)
    file_url = f"file://{abs_input}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": width, "height": 800},
            device_scale_factor=scale,
        )
        page = context.new_page()

        # Navigate and wait for fonts + animations to settle
        page.goto(file_url, wait_until="networkidle")
        page.wait_for_timeout(1500)  # Let animations complete

        # Force all reveal elements to be visible for the screenshot
        page.evaluate("""
            document.querySelectorAll('.reveal').forEach(el => {
                el.classList.add('visible');
                el.style.opacity = '1';
                el.style.transform = 'none';
            });
            document.querySelectorAll('.ba-fill, .bar-fill').forEach(bar => {
                const w = bar.dataset.width;
                if (w) bar.style.width = w + '%';
            });
            document.querySelectorAll('[data-counter]').forEach(el => {
                const target = el.dataset.counter;
                const suffix = el.dataset.suffix || '';
                el.textContent = parseInt(target).toLocaleString() + suffix;
            });
        """)

        page.wait_for_timeout(500)

        # Full-page screenshot
        page.screenshot(path=output_path, full_page=True)

        browser.close()

    print(f"[html_to_png] Saved: {output_path}")
    print(f"[html_to_png] Width: {width}px, Scale: {scale}x")

    # Report file size
    size_kb = os.path.getsize(output_path) / 1024
    if size_kb > 1024:
        print(f"[html_to_png] Size: {size_kb / 1024:.1f} MB")
    else:
        print(f"[html_to_png] Size: {size_kb:.0f} KB")


def main():
    parser = argparse.ArgumentParser(description="Convert HTML infographic to PNG")
    parser.add_argument("input", help="Input HTML file path")
    parser.add_argument("output", nargs="?", default=None, help="Output PNG path")
    parser.add_argument("--width", type=int, default=1200, help="Viewport width (default: 1200)")
    parser.add_argument("--scale", type=int, default=2, help="Device scale factor (default: 2)")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    output = args.output or os.path.splitext(args.input)[0] + ".png"

    ensure_playwright()
    html_to_png(args.input, output, args.width, args.scale)


if __name__ == "__main__":
    main()
