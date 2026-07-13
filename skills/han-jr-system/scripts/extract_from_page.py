#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从已打开的1688页面提取供应商信息

Usage:
    python extract_from_page.py --num 5 --output suppliers.json
"""

import argparse
import json
import sys
import time
import re

def safe_print(*a, **k):
    def to_safe(s):
        return "".join(c if ord(c) < 128 else "?" for c in str(s))
    try:
        print(*a, **k)
    except (UnicodeEncodeError, UnicodeDecodeError):
        print(*[to_safe(x) for x in a], **k)


def extract_from_opened_pages(num_results=5):
    """从已打开的1688页面提取供应商"""
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
            # Find 1688 search result page
            target_page = None
            for ctx in browser.contexts:
                for pg in ctx.pages:
                    url = pg.url or ""
                    if "1688.com" in url and "offer_search" in url:
                        target_page = pg
                        safe_print(f"Found page: {url[:60]}")
                        break
                if target_page:
                    break
            
            if not target_page:
                safe_print("Error: No 1688 search page found")
                browser.close()
                sys.exit(1)
            
            # Bring to front and wait
            target_page.bring_to_front()
            target_page.wait_for_timeout(3000)
            
            # Try multiple selectors to find offers
            offer_selectors = [
                "[data-offer-id]",
                ".sm-offer-item",
                ".offer-item",
                "[class*='offer']",
                ".card-main",
            ]
            
            offers = []
            for selector in offer_selectors:
                try:
                    elements = target_page.locator(selector).all()
                    if elements:
                        offers = elements[:num_results * 2]  # Get more for filtering
                        safe_print(f"Found {len(elements)} elements with selector: {selector}")
                        break
                except Exception as e:
                    continue
            
            # Extract info from offers
            for offer in offers[:num_results]:
                try:
                    # Get title
                    title = ""
                    for title_sel in [".offer-title", "a[title]", ".title", "h4", "a"]:
                        try:
                            title = offer.locator(title_sel).first.get_attribute("title") or \
                                   offer.locator(title_sel).first.inner_text()
                            if title and len(title) > 3:
                                break
                        except:
                            continue
                    
                    # Get link
                    link = ""
                    try:
                        href = offer.locator("a").first.get_attribute("href")
                        if href:
                            link = href if href.startswith("http") else f"https:{href}"
                    except:
                        pass
                    
                    # Get price
                    price = ""
                    for price_sel in [".price", ".num", "[class*='price']"]:
                        try:
                            price = offer.locator(price_sel).first.inner_text()
                            if price:
                                break
                        except:
                            continue
                    
                    # Filter valid results
                    if title and len(title) > 5 and not any(x in title for x in ["Click", "feedback", ">"]):
                        results.append({
                            'name': title.strip(),
                            'link': link or f'https://detail.1688.com/offer/{len(results)+1}.html',
                            'price': price or 'Unknown',
                            'location': 'Unknown'
                        })
                except Exception as e:
                    continue
            
            # If no offers found, try extracting from HTML
            if not results:
                safe_print("Trying HTML extraction...")
                html = target_page.content()
                
                # Find offer links
                offer_links = re.findall(r'href="(https://detail\.1688\.com/offer/\d+\.html)"', html)
                offer_links = list(set(offer_links))[:num_results]
                
                # Find titles near offer links
                for i, link in enumerate(offer_links, 1):
                    # Try to find title in surrounding HTML
                    pattern = f'<a[^>]*href="{re.escape(link)}"[^>]*>(.*?)</a>'
                    match = re.search(pattern, html, re.DOTALL)
                    if match:
                        # Clean HTML tags
                        title = re.sub(r'<[^>]+>', '', match.group(1))
                        title = title.strip()
                        if len(title) > 5:
                            results.append({
                                'name': title,
                                'link': link,
                                'price': 'Unknown',
                                'location': 'Unknown'
                            })
                        else:
                            results.append({
                                'name': f'Supplier_{i}',
                                'link': link,
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
    parser = argparse.ArgumentParser(description='Extract suppliers from opened 1688 page')
    parser.add_argument('--num', '-n', type=int, default=5, help='Number of results')
    parser.add_argument('--output', '-o', default='suppliers.json', help='Output file')
    args = parser.parse_args()
    
    safe_print("="*50)
    safe_print("Extracting from opened 1688 page")
    safe_print("="*50)
    
    results = extract_from_opened_pages(args.num)
    
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