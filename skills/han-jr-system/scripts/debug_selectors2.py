#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://localhost:9222')
    page = None
    for ctx in browser.contexts:
        for pg in ctx.pages:
            if '1688.com' in (pg.url or ''):
                page = pg
                break
        if page:
            break
    
    # Debug selectors
    selectors = [
        '.offer-list .offer-item',
        '.sm-offer-list .sm-offer-item', 
        '.offer-item',
        '[data-offer-id]',
        '.product-item',
        '.goods-item',
        '.main-container .offer-item',
        '.search-result .offer-item'
    ]
    
    for sel in selectors:
        try:
            elems = page.query_selector_all(sel)
            if elems:
                print(f'{sel}: {len(elems)} elements')
        except Exception as e:
            print(f'{sel}: error - {e}')
    
    # Try to find any clickable product links
    all_links = page.query_selector_all('a')
    print(f'\nTotal links: {len(all_links)}')
    
    # Check for product cards by looking for price elements
    price_elems = page.query_selector_all('[class*="price"], [class*="Price"]')
    print(f'Price elements: {len(price_elems)}')
    
    browser.close()
