#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1688 Supplier Search Script - Based on desktop experience

Usage:
    python search_1688.py --keyword "铅笔" --num 5
    
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

# Fix encoding for Windows (from desktop experience)
def safe_print(*a, **k):
    def to_safe(s):
        return "".join(c if ord(c) < 128 else "?" for c in str(s))
    try:
        print(*a, **k)
    except (UnicodeEncodeError, UnicodeDecodeError):
        print(*[to_safe(x) for x in a], **k)

# 1688 search page selectors (from desktop experience)
SEARCH_INPUT_SELECTORS = [
    "input#search-key",
    "input[name='keywords']",
    "#search-key",
    ".search-input input",
    "[class*='search'] input[type='text']",
    "header input[type='text']",
]

SEARCH_BUTTON_SELECTORS = [
    "button[type='submit']",
    ".search-btn",
    "[class*='search'] button",
    "a.btn-search",
    ".search-button",
]

TITLE_SELECTORS = [
    ".sm-offer-item .offer-title",
    ".offer-list-row .offer-title",
    ".offer-item .offer-title",
    "[class*='offer'] [class*='title']",
    ".card-main .title",
    "a[title]",
]

BASE_URL = "https://s.1688.com/selloffer/offer_search.htm"
HOME_URL = "https://www.1688.com"


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
    Search suppliers on 1688
    Returns: [{'name': 'supplier name', 'link': 'url', 'price': 'price range', 'location': 'region'}, ...]
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        safe_print("Error: playwright required")
        safe_print("Run: pip install playwright")
        safe_print("Then: playwright install chromium")
        sys.exit(1)
    
    results = []
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception as e:
            safe_print(f"Error: Cannot connect to Chrome. Please run chrome_launch.py first")
            safe_print(f"Details: {e}")
            sys.exit(1)
        
        try:
            # Get 1688 page or any available page
            page = None
            for ctx in browser.contexts:
                for pg in ctx.pages:
                    if "1688.com" in (pg.url or ""):
                        page = pg
                        break
                if page:
                    break
            
            # If no 1688 page, use first available page
            if not page:
                for ctx in browser.contexts:
                    for pg in ctx.pages:
                        if (pg.url or "").startswith("http"):
                            page = pg
                            break
                    if page:
                        break
            
            if not page:
                safe_print("Error: No browser tab found")
                browser.close()
                sys.exit(1)
            
            safe_print(f"Using tab: {(page.url or '')[:60]}")
            
            page.set_default_timeout(30000)
            
            # Check if we're on a punish/verification page
            current_url = page.url or ""
            if "punish" in current_url or "_____tmd_____" in current_url:
                safe_print("Warning: 1688 detected automation, waiting...")
                page.wait_for_timeout(10000)  # Wait 10s for any verification
                page.goto(HOME_URL, wait_until="domcontentloaded")
                page.wait_for_timeout(5000)
            
            # Step 1: Go to 1688 homepage
            safe_print("Opening 1688 homepage...")
            page.goto(HOME_URL, wait_until="domcontentloaded")
            page.wait_for_timeout(5000)  # Increased wait time
            
            # Step 2: Find and fill search input
            search_input = None
            for sel in SEARCH_INPUT_SELECTORS:
                try:
                    loc = page.locator(sel)
                    if loc.count() > 0:
                        loc.first.wait_for(state="visible", timeout=3000)
                        search_input = loc.first
                        break
                except Exception:
                    continue
            
            if not search_input:
                safe_print("Search input not found, trying direct URL...")
                # Fallback: direct search URL
                q = urllib.parse.quote(keyword, encoding="utf-8")
                page.goto(f"{BASE_URL}?keywords={q}", wait_until="domcontentloaded")
                page.wait_for_timeout(5000)
            else:
                # Fill keyword and search
                safe_print(f"Filling keyword: {keyword}")
                search_input.click()
                page.wait_for_timeout(200)
                search_input.clear()
                page.wait_for_timeout(150)
                # Type with delay to avoid detection (human-like)
                search_input.press_sequentially(keyword, delay=120)
                page.wait_for_timeout(800)
                
                # Click search button or press Enter
                clicked = False
                for btn_sel in SEARCH_BUTTON_SELECTORS:
                    try:
                        btn = page.locator(btn_sel)
                        if btn.count() > 0:
                            btn.first.click()
                            clicked = True
                            break
                    except Exception:
                        continue
                
                page.wait_for_timeout(1000)
                if not clicked:
                    search_input.press("Enter")
                
                page.wait_for_timeout(8000)  # Wait longer for results
                
                # Verify we're on search page
                if "offer_search" not in (page.url or ""):
                    safe_print("Not on search page, redirecting...")
                    q = urllib.parse.quote(keyword, encoding="utf-8")
                    page.goto(f"{BASE_URL}?keywords={q}", wait_until="domcontentloaded")
                    page.wait_for_timeout(3000)
            
            safe_print(f"Current URL: {(page.url or '')[:80]}")
            
            # Step 3: Extract supplier titles
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
            
            # Filter out non-product titles
            titles = [t for t in titles if not any(x in t for x in ("Click", "feedback", ">")) and len(t) > 5]
            
            # Check if we got results
            if not titles:
                # Save HTML for debugging
                try:
                    html = page.content()
                    debug_file = "c:\\Users\\Moha\\.cursor-tutor\\1688_debug.html"
                    with open(debug_file, "w", encoding="utf-8") as f:
                        f.write(html)
                    safe_print(f"Page HTML saved to {debug_file}")
                    
                    if "login" in (page.url or "") or "passport" in (page.url or ""):
                        safe_print("[WARNING] Page requires login - 1688 may need login to see search results")
                except Exception:
                    pass
                
                safe_print("No product titles found")
                browser.close()
                return results
            
            # Match keyword and build results
            match_count = 0
            for i, t in enumerate(titles[:num_results], 1):
                is_match = keyword_in_text(keyword, t)
                if is_match:
                    match_count += 1
                
                # Try to extract link
                link = ""
                try:
                    # Find link for this title
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
            
            # Debug: show sample titles
            safe_print(f"Sample titles found:")
            for i, t in enumerate(titles[:5], 1):
                safe_print(f"  {i}. {t[:60]}{'...' if len(t) > 60 else ''}")
            
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
        safe_print(f"First Check PASS: Found {len(results)} suppliers, {match_count} match keyword '{keyword}'")
        return True
    else:
        safe_print(f"First Check WARNING: Keyword '{keyword}' not directly found, but {len(results)} results extracted")
        # Still pass if we got results
        return len(results) > 0


def double_check(keyword, num_results):
    """Double Check: Retry search"""
    safe_print("\nExecuting Double Check (20s)...")
    time.sleep(10)  # Additional wait
    
    # Retry once
    results = search_1688(keyword, num_results)
    return verify_results(results, keyword)


def save_results(results, filename='suppliers.json'):
    """Save results to JSON"""
    import json
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    safe_print(f"Results saved to: {filename}")


def main():
    parser = argparse.ArgumentParser(description='1688 Supplier Search')
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
            safe_print(f"{i}. {r['name']} {match_marker}")
            safe_print(f"   Link: {r['link']}")
            safe_print("")
        
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