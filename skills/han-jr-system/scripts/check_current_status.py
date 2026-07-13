#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://localhost:9222')
    
    # 找到旺旺页面
    page = None
    for ctx in browser.contexts:
        for pg in ctx.pages:
            if 'air.1688.com' in pg.url:
                page = pg
                break
        if page:
            break
    
    if page:
        page.bring_to_front()
        time.sleep(2)
        
        # 截图查看当前状态
        page.screenshot(path='current_wangwang_status.png', full_page=False)
        print('Screenshot saved: current_wangwang_status.png')
        
        # 获取页面信息
        info = page.evaluate('''() => {
            const list = document.querySelector('[style*="overflow: auto"]');
            const items = document.querySelectorAll('.conversation-item');
            
            const visibleItems = [];
            items.forEach((item, i) => {
                const rect = item.getBoundingClientRect();
                const nameEl = item.querySelector('.name');
                if (nameEl && rect.top >= 0 && rect.bottom <= window.innerHeight) {
                    visibleItems.push({
                        index: i,
                        name: nameEl.innerText.trim(),
                        top: rect.top,
                        bottom: rect.bottom
                    });
                }
            });
            
            return {
                scrollTop: list ? list.scrollTop : 0,
                scrollHeight: list ? list.scrollHeight : 0,
                totalItems: items.length,
                visibleItems: visibleItems
            };
        }''')
        
        print(f'ScrollTop: {info["scrollTop"]}')
        print(f'ScrollHeight: {info["scrollHeight"]}')
        print(f'Total items: {info["totalItems"]}')
        print(f'Visible items: {len(info["visibleItems"])}')
        print('\nVisible contacts:')
        for item in info['visibleItems']:
            print(f'  [{item["index"]}] {item["name"]} (top: {item["top"]:.0f})')
    
    browser.close()
