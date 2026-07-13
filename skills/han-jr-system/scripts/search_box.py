#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1688 Supplier Search - Search Box Input Version
Uses search box input instead of URL parameters
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
            
            # Step 1: Go to 1688 search page
            safe_print(f"Search: {keyword}")
            page.goto("https://s.1688.com/selloffer/offer_search.htm", wait_until="domcontentloaded")
            time.sleep(3)
            
            safe_print(f"Loaded: {(page.url or '')[:60]}")
            
            # Step 2: Find and clear search box
            search_selectors = [
                'input[placeholder*="搜索"]',
                'input[type="text"]',
                '.search-input input',
                '#search-input',
                'input[name="keywords"]'
            ]
            
            search_box = None
            for selector in search_selectors:
                try:
                    search_box = page.query_selector(selector)
                    if search_box:
                        safe_print(f"Found search box: {selector}")
                        break
                except:
                    continue
            
            if not search_box:
                safe_print("Error: Could not find search box")
                browser.close()
                sys.exit(1)
            
            # Step 3: Clear and input keyword
            search_box.click()
            search_box.fill("")  # Clear first
            time.sleep(0.5)
            search_box.fill(keyword)
            safe_print(f"Input keyword: {keyword}")
            time.sleep(1)
            
            # Step 4: Submit search (press Enter)
            search_box.press("Enter")
            safe_print("Submitted search")
            
            # Step 5: Wait for results to load
            time.sleep(5)
            
            safe_print(f"Result URL: {(page.url or '')[:80]}")
            
            # Step 6: Extract product information
            products = page.evaluate("""() => {
                const products = [];
                
                // Try multiple selectors for product cards
                const card_selectors = [
                    '.sm-offer-item',
                    '.offer-item',
                    '[data-offer-id]',
                    '.product-item',
                    '.goods-item'
                ];
                
                for (const card_sel of card_selectors) {
                    const cards = document.querySelectorAll(card_sel);
                    if (cards.length > 0) {
                        for (const card of cards.slice(0, 10)) {
                            const product = {};
                            
                            // Get title
                            const title_el = card.querySelector('.title, .offer-title, h3, h4, a[title]');
                            if (title_el) {
                                product.title = title_el.getAttribute('title') || title_el.textContent;
                            }
                            
                            // Get price
                            const price_el = card.querySelector('.price, .offer-price, .price-num');
                            if (price_el) {
                                product.price = price_el.textContent.trim();
                            }
                            
                            // Get location
                            const loc_el = card.querySelector('.location, .province, .city');
                            if (loc_el) {
                                product.location = loc_el.textContent.trim();
                            }
                            
                            // Get link
                            const link_el = card.querySelector('a[href]');
                            if (link_el) {
                                product.link = link_el.getAttribute('href');
                            }
                            
                            if (product.title && product.title.length > 3) {
                                products.push(product);
                            }
                        }
                        if (products.length > 0) break;
                    }
                }
                
                return products.slice(0, 10);
            }""")
            
            safe_print(f"Found {len(products)} products")
            
            for i, p in enumerate(products[:num_results], 1):
                title = p.get('title', 'Unknown')
                price = p.get('price', 'Unknown')
                location = p.get('location', 'Unknown')
                link = p.get('link', '')
                
                results.append({
                    'name': title.strip() if title else 'Unknown',
                    'price': price.strip() if price else 'Unknown',
                    'location': location.strip() if location else 'Unknown',
                    'link': link if link else f'https://detail.1688.com/offer/{i}.html'
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
    safe_print(f"1688 Search (Search Box): {args.keyword}")
    safe_print("="*50)
    
    results = search_1688(args.keyword, args.num)
    
    if results:
        safe_print(f"\nResults: {len(results)}")
        for i, r in enumerate(results, 1):
            title = r['name'][:50] if r['name'] else 'Unknown'
            safe_print(f"{i}. {title}")
        
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        safe_print(f"\nSaved: {args.output}")
        return 0
    else:
        safe_print("\nNo results")
        return 1

if __name__ == "__main__":
    sys.exit(main())
