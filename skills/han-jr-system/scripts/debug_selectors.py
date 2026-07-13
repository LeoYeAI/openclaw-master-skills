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
    
    if not page:
        print('No 1688 page found')
        exit(1)
    
    print(f'Current URL: {page.url}')
    
    # Try different selectors for product titles
    selectors = [
        '.offer-title',
        '.sm-offer-item .title',
        '[data-offer-id] .title',
        '.offer-item-title',
        'a[title]',
        '.item-title',
        '.product-title',
        '.sm-offer-title',
        '.offer-list .title'
    ]
    
    for sel in selectors:
        elems = page.query_selector_all(sel)
        if elems:
            print(f'Selector {sel}: found {len(elems)} elements')
            for i, el in enumerate(elems[:3], 1):
                title = el.get_attribute('title') or el.inner_text()
                if title:
                    print(f'  {i}. {title[:50]}')
    
    browser.close()
