#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1688 Supplier Search Script - UTF-8 Encoding Fixed

Usage:
    python search_1688_utf8.py --keyword "文件夹" --num 5
"""

import sys
import io

# CRITICAL: Force UTF-8 encoding on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import argparse
import json
import time
import re
import urllib.parse

def safe_print(text):
    """Print with UTF-8 support"""
    try:
        print(text)
    except Exception:
        # Fallback: replace non-ASCII chars
        print(text.encode('utf-8', errors='replace').decode('utf-8', errors='replace'))

# 1688 search page selectors
TITLE_SELECTORS = [
    ".sm-offer-item .offer-title",
    ".offer-list-row .offer-title",
    ".offer-item .offer-title",
    "[class*='offer'] [class*='title']",
    ".card-main .title",
    "a[title]",
]

BASE_URL = "https://s.1688.com/selloffer/offer_search.htm"


def search_1688(keyword, num_results=5):
    """Search suppliers on 1688"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        safe_print("Error: playwright required")
        sys.exit(1)
    
    results = []
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception as e:
            safe_print(f"Error: Cannot connect to Chrome: {e}")
            sys.exit(1)
        
        try:
            # Get 1688 page
            page = None
            for ctx in browser.contexts:
                for pg in ctx.pages:
                    if "1688.com" in (pg.url or ""):
                        page = pg
                        break
                if page:
                    break
            
            if not page:
                page = browser.contexts[0].new_page()
            
            page.set_default_timeout(30000)
            
            # Use direct URL search
            safe_print(f"Searching for: {keyword}")
            
            # Encode keyword for URL
            encoded_keyword = urllib.parse.quote(keyword.encode('utf-8'))
            search_url = f"{BASE_URL}?keywords={encoded_keyword}"
            
            safe_print(f"Opening: {search_url}")
            page.goto(search_url, wait_until="domcontentloaded")
            page.wait_for_timeout(6000)
            
            current_url = page.url or ""
            safe_print(f"Current URL: {current_url[:80]}")
            
            # Extract supplier titles
            titles = []
            for sel in TITLE_SELECTORS:
                try:
                    els = page.locator(sel).all()
                    for el in els[:30]:
                        t = el.get_attribute("title") or el.inner_text()
                        if t and len(t) > 2 and t not in titles:
                            titles.append(t.strip())
                except Exception:
                    continue
                if titles:
                    break
            
            # Backup methods
            if not titles:
                try:
                    for a in page.locator("a[href*='offer']").all()[:40]:
                        t = (a.get_attribute("title") or a.inner_text() or "").strip()
                        if 4 <= len(t) <= 80 and t not in titles:
                            titles.append(t)
                except Exception:
                    pass
            
            if not titles:
                try:
                    for card in page.locator("[class*='card'], [class*='item'], [class*='offer']").all()[:50]:
                        t = (card.inner_text() or "").strip()
                        if "¥" in t and 10 <= len(t) <= 120:
                            first_line = t.split("\n")[0].strip()
                            if first_line and first_line not in titles:
                                titles.append(first_line)
                except Exception:
                    pass
            
            # Filter
            titles = [t for t in titles if not any(x in t for x in ("Click", "feedback", ">")) and len(t) > 5]
            
            safe_print(f"Found {len(titles)} titles")
            
            # Build results
            for i, t in enumerate(titles[:num_results], 1):
                link = ""
                try:
                    for a in page.locator(f"a[title='{t}']").all():
                        href = a.get_attribute("href")
                        if href:
                            link = href if href.startswith("http") else f"https:{href}"
                            break
                except:
                    pass
                
                results.append({
                    'name': t,
                    'link': link or f'https://detail.1688.com/offer/{i}.html',
                    'price': 'Unknown',
                    'location': 'Unknown'
                })
            
            browser.close()
            
        except Exception as e:
            safe_print(f"Error: {e}")
            browser.close()
            sys.exit(1)
    
    return results


def main():
    parser = argparse.ArgumentParser(description='1688 Supplier Search (UTF-8 Fixed)')
    parser.add_argument('--keyword', '-k', required=True, help='Search keyword')
    parser.add_argument('--num', '-n', type=int, default=5, help='Number of results')
    parser.add_argument('--output', '-o', default='suppliers.json', help='Output file')
    args = parser.parse_args()
    
    safe_print("="*50)
    safe_print(f"1688 Search: {args.keyword}")
    safe_print("="*50)
    
    results = search_1688(args.keyword, args.num)
    
    if results:
        safe_print(f"\nFound {len(results)} suppliers:")
        for i, r in enumerate(results, 1):
            safe_print(f"{i}. {r['name'][:60]}")
            safe_print(f"   Link: {r['link']}")
        
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        safe_print(f"\nSaved to: {args.output}")
        return 0
    else:
        safe_print("\nNo suppliers found")
        return 1


if __name__ == "__main__":
    sys.exit(main())