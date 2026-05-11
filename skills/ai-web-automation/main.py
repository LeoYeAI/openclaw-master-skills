#!/usr/bin/env python3
# Web Automation Service - Main Script

import os
import sys
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent.resolve()
OUTPUT_DIR = SCRIPT_DIR / "output"

def scrape_web(url):
    """抓取网页"""
    try:
        import requests
        response = requests.get(url, timeout=10)

        report = f"# Web Scraping Report: {url}\n\n"
        report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report += f"## Scraping Results\n\n"
        report += f"- URL: {url}\n"
        report += f"- Status Code: {response.status_code}\n"
        report += f"- Content Length: {len(response.text)} bytes\n\n"

        # Extract title
        import re
        title_match = re.search(r'<title>(.*?)</title>', response.text)
        if title_match:
            report += f"**Page Title:** {title_match.group(1)}\n\n"

        # Extract links
        links = re.findall(r'href="([^"]+)"', response.text)
        report += f"**Found {len(links)} links**\n\n"

        output_file = OUTPUT_DIR / f"scrape_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_file.write_text(report, encoding='utf-8')

        return str(output_file)
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 main.py <action> <url> [options]")
        print("\nActions:")
        print("  scrape  <url> - Scrape web page")
        print("\nExamples:")
        print("  python3 main.py scrape https://example.com")
        sys.exit(1)

    action = sys.argv[1]
    url = sys.argv[2]

    if action == "scrape":
        result = scrape_web(url)
        print(f"Scraping saved to: {result}")
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main()
