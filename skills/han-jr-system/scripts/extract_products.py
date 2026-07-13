#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright
import json

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
    
    # Extract products using JavaScript
    products = page.evaluate('''() => {
        const results = [];
        
        // Find all elements that contain price info (likely product cards)
        const allElements = document.querySelectorAll('*');
        const productCards = [];
        
        for (const el of allElements) {
            // Check if element has price-related class or content
            const text = el.textContent || '';
            const hasPrice = text.includes('¥') || text.includes('元') || /\\d+\\.\\d+/.test(text);
            const className = el.className || '';
            const isPriceElement = typeof className === 'string' && (className.includes('price') || className.includes('Price'));
            
            if (hasPrice && isPriceElement) {
                // Find parent that might be a product card
                let parent = el.parentElement;
                for (let i = 0; i < 5 && parent; i++) {
                    const parentText = parent.textContent || '';
                    if (parentText.length > 50 && parentText.length < 500) {
                        // This might be a product card
                        if (!productCards.includes(parent)) {
                            productCards.push(parent);
                        }
                        break;
                    }
                    parent = parent.parentElement;
                }
            }
        }
        
        // Extract info from each card
        for (const card of productCards.slice(0, 10)) {
            const product = {};
            
            // Get all text
            const fullText = card.textContent || '';
            
            // Find title (usually the longest text that's not price)
            const textNodes = [];
            const walk = (node) => {
                if (node.nodeType === 3) { // Text node
                    const text = node.textContent.trim();
                    if (text.length > 5 && text.length < 100) {
                        textNodes.push(text);
                    }
                }
                for (const child of node.childNodes) {
                    walk(child);
                }
            };
            walk(card);
            
            // Title is usually the longest non-price text
            const nonPriceTexts = textNodes.filter(t => !t.includes('¥') && !/^\\d/.test(t));
            if (nonPriceTexts.length > 0) {
                product.title = nonPriceTexts.sort((a, b) => b.length - a.length)[0];
            }
            
            // Find price
            const priceMatch = fullText.match(/[¥￥]\\s*([\\d,]+(?:\\.\\d+)?)/);
            if (priceMatch) {
                product.price = '¥' + priceMatch[1];
            }
            
            // Find link
            const linkEl = card.querySelector('a[href]');
            if (linkEl) {
                product.link = linkEl.getAttribute('href');
            }
            
            if (product.title) {
                results.push(product);
            }
        }
        
        return results;
    }''')
    
    print(f'Found {len(products)} products:')
    for i, p in enumerate(products, 1):
        print(f'{i}. {p.get("title", "Unknown")[:50]} - {p.get("price", "Unknown")}')
    
    # Save to file
    with open('hat_products.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print('\nSaved to hat_products.json')
    browser.close()
