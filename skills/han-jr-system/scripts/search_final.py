#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1688 Supplier Search - Final Fixed Version
Handles encoding issues properly
"""

import sys
import io

# Force UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import argparse
import json
import time
import urllib.parse

def safe_print(text):
    try:
        print(text)
    except:
        print(str(text).encode('utf-8', errors='replace').decode('utf-8', errors='replace'))

def search_1688(keyword, num_results=5):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        safe_print("Error: pip install playwright")
        sys.exit(1)
    
    results = []
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception as e:
            safe_print(f"Error: {e}")
            sys.exit(1)
        
        try:
            # Get page
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
            
            # Search using URL
            safe_print(f"Search: {keyword}")
            encoded = urllib.parse.quote(keyword.encode('utf-8'))
            url = f"https://s.1688.com/selloffer/offer_search.htm?keywords={encoded}"
            
            safe_print(f"URL: {url}")
            page.goto(url, wait_until="domcontentloaded")
            time.sleep(6)
            
            safe_print(f"Loaded: {(page.url or '')[:60]}")
            
            # Extract titles using JavaScript (more reliable)
            titles = page.evaluate("""() => {
                const titles = [];
                // Try multiple selectors
                const selectors = [
                    '.sm-offer-item .offer-title',
                    '.offer-item .title',
                    '[data-offer-id] .title',
                    'a[title]'
                ];
                for (const sel of selectors) {
                    const elems = document.querySelectorAll(sel);
                    for (const el of elems) {
                        const text = el.getAttribute('title') || el.innerText;
                        if (text && text.length > 3 && text.length < 100) {
                            titles.push(text.trim());
                        }
                    }
                    if (titles.length > 0) break;
                }
                return titles.slice(0, 10);
            }""")
            
            safe_print(f"Found {len(titles)} titles")
            
            for i, t in enumerate(titles[:num_results], 1):
                results.append({
                    'name': t,
                    'link': f'https://detail.1688.com/offer/{i}.html',
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
    parser = argparse.ArgumentParser()
    parser.add_argument('--keyword', '-k', required=True)
    parser.add_argument('--num', '-n', type=int, default=5)
    parser.add_argument('--output', '-o', default='suppliers.json')
    args = parser.parse_args()
    
    safe_print("="*50)
    safe_print(f"1688 Search: {args.keyword}")
    safe_print("="*50)
    
    results = search_1688(args.keyword, args.num)
    
    if results:
        safe_print(f"\nResults: {len(results)}")
        for i, r in enumerate(results, 1):
            safe_print(f"{i}. {r['name'][:50]}")
        
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        safe_print(f"\nSaved: {args.output}")
        return 0
    else:
        safe_print("\nNo results")
        return 1

if __name__ == "__main__":
    sys.exit(main())