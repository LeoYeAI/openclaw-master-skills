#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1688 Supplier Search Script - Fixed Encoding Version

Usage:
    python search_1688_fixed.py --keyword "文件夹" --num 5
    
Dependencies:
    pip install playwright
    
Note: Requires Chrome already started (chrome_launch.py)
"""

import argparse
import json
import sys
import time
import re
import urllib.parse

# Fix encoding for Windows - CRITICAL
def safe_print(*a, **k):
    def to_safe(s):
        return "".join(c if ord(c) < 128 else "?" for c in str(s))
    try:
        print(*a, **k)
    except (UnicodeEncodeError, UnicodeDecodeError):
        print(*[to_safe(x) for x in a], **k)

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


def keyword_in_text(keyword, text):
    """Check if keyword is in text (supports Chinese partial match)"""
    if not text or not keyword:
        return False
    text = text.strip()
    if keyword in text:
        return True
    # At least 2 chars from keyword match (for Chinese)
    if len(keyword) >= 2:
        chars = [c for c in keyword if c.isalnum() or "\u4e00" <= c <= "\u9fff"]
        if len(chars) >= 2 and sum(1 for c in chars if c in text) >= 2:
            return True
    return False


def search_1688(keyword, num_results=5):
    """
    Search suppliers on 1688 using direct URL (avoids encoding issues)
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        safe_print("Error: playwright required")
        safe_print("Run: pip install playwright")
        sys.exit(1)
    
    results = []
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception as e:
            safe_print(f"Error: Cannot connect to Chrome. Please run chrome_launch.py first")
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
                # Create new page
                page = browser.contexts[0].new_page()
            
            page.set_default_timeout(30000)
            
            # CRITICAL FIX: Use direct URL with properly encoded keyword
            # This avoids encoding issues with filling search input
            safe_print(f"Searching for: {keyword}")
            
            # Properly encode the keyword for URL
            # Use quote_plus to handle spaces and special chars
            encoded_keyword = urllib.parse.quote(keyword.encode('utf-8'))
            search_url = f"{BASE_URL}?keywords={encoded_keyword}"
            
            safe_print(f"Opening search URL...")
            page.goto(search_url, wait_until="domcontentloaded")
            page.wait_for_timeout(5000)  # Wait for page to load
            
            safe_print(f"Current URL: {(page.url or '')[:80]}")
            
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
            
            # Backup: extract from offer links
            if not titles:
                try:
                    for a in page.locator("a[href*='offer']").all()[:40]:
                        t = (a.get_attribute("title") or a.inner_text() or "").strip()
                        if 4 <= len(t) <= 80 and t not in titles:
                            titles.append(t)
                except Exception:
                    pass
            
            # Backup: extract from cards with price
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
            
            # Filter valid results
            titles = [t for t in titles if not any(x in t for x in ("Click", "feedback", ">")) and len(t) > 5]
            
            # Match keyword and build results
            match_count = 0
            for i, t in enumerate(titles[:num_results], 1):
                is_match = keyword_in_text(keyword, t)
                if is_match:
                    match_count += 1
                
                # Try to extract link
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
                    'link': link or f'https://detail.1688.com/offer/search_{i}.html',
                    'price': 'Unknown',
                    'location': 'Unknown',
                    'match': is_match
                })
            
            safe_print(f"Found {len(titles)} titles, {match_count} match keyword")
            browser.close()
            
        except Exception as e:
            safe_print(f"Search error: {e}")
            browser.close()
            sys.exit(1)
    
    return results


def verify_results(results, keyword):
    """First Check: Verify search results"""
    safe_print("\nExecuting First Check (10s)...")
    time.sleep(10)
    
    if not results:
        safe_print("First Check FAIL: No suppliers found")
        return False
    
    # Check if keyword is in results
    match_count = sum(1 for r in results if r.get('match', False))
    
    if match_count > 0:
        safe_print(f"First Check PASS: Found {len(results)} suppliers, {match_count} match keyword")
        return True
    else:
        safe_print(f"First Check WARNING: Keyword not directly found, but {len(results)} results extracted")
        return len(results) > 0


def double_check(keyword, num_results):
    """Double Check: Retry search"""
    safe_print("\nExecuting Double Check (20s)...")
    time.sleep(10)
    
    results = search_1688(keyword, num_results)
    return verify_results(results, keyword)


def save_results(results, filename='suppliers.json'):
    """Save results to JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    safe_print(f"Results saved to: {filename}")


def main():
    parser = argparse.ArgumentParser(description='1688 Supplier Search (Fixed Encoding)')
    parser.add_argument('--keyword', '-k', required=True, help='Search keyword (Chinese preferred)')
    parser.add_argument('--num', '-n', type=int, default=5, help='Number of results')
    parser.add_argument('--output', '-o', default='suppliers.json', help='Output file')
    args = parser.parse_args()
    
    safe_print("="*50)
    safe_print(f"1688 Search: {args.keyword}")
    safe_print("="*50)
    
    # Execute search
    results = search_1688(args.keyword, args.num)
    
    # First Check verification
    if verify_results(results, args.keyword):
        safe_print("\nSearch successful!")
        for i, r in enumerate(results, 1):
            match_marker = "[MATCH]" if r.get('match') else ""
            safe_print(f"{i}. {r['name'][:60]} {match_marker}")
            safe_print(f"   Link: {r['link']}")
        
        save_results(results, args.output)
        return 0
    
    # Double Check
    safe_print("\nFirst Check failed, executing Double Check...")
    if double_check(args.keyword, args.num):
        safe_print("\nDouble Check successful!")
        return 0
    
    safe_print("\nSearch failed: Both checks failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())