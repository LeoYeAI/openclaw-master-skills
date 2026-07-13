#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright
import urllib.parse

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
    
    # Get the search input value
    search_input = page.query_selector('input[type=text]')
    if search_input:
        value = search_input.input_value()
        print(f'Search input value: {value}')
    
    # Check URL parameters
    print(f'Current URL: {page.url}')
    
    # Try to get product titles from the recommendation section
    titles = page.evaluate('''() => {
        const results = [];
        // Look for product cards
        const cards = document.querySelectorAll('.offer-item, .sm-offer-item, .product-item, .goods-item, [data-offer-id]');
        for (const card of cards) {
            const titleEl = card.querySelector('.title, .offer-title, .product-title, h3, h4, a');
            if (titleEl) {
                const text = titleEl.textContent || titleEl.getAttribute('title');
                if (text && text.length > 5) {
                    results.push(text.trim());
                }
            }
        }
        return results.slice(0, 10);
    }''')
    
    print(f'Found {len(titles)} product titles:')
    for i, t in enumerate(titles, 1):
        print(f'{i}. {t}')
    
    browser.close()
