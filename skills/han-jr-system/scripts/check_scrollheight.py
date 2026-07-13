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
        
        # 找到包含联系人的frame
        target_frame = None
        for frame in page.frames:
            try:
                contacts_test = frame.query_selector_all('.conversation-item')
                if len(contacts_test) > 0:
                    target_frame = frame
                    break
            except:
                pass
        
        if target_frame:
            # 滚动到底部
            print('Scrolling to bottom...')
            for i in range(30):
                target_frame.evaluate('''() => {
                    const list = document.querySelector('.conversation-list, .contact-list, [class*="list"]');
                    if (list) list.scrollTop = list.scrollHeight;
                }''')
                time.sleep(0.5)
            
            time.sleep(2)
            
            # 获取ScrollHeight
            scroll_info = target_frame.evaluate('''() => {
                const list = document.querySelector('.conversation-list, .contact-list, [class*="list"]');
                if (list) {
                    return {
                        scrollTop: list.scrollTop,
                        scrollHeight: list.scrollHeight,
                        clientHeight: list.clientHeight
                    };
                }
                return null;
            }''')
            
            if scroll_info:
                print(f'ScrollTop: {scroll_info["scrollTop"]}')
                print(f'ScrollHeight: {scroll_info["scrollHeight"]}')
                print(f'ClientHeight: {scroll_info["clientHeight"]}')
            
            # 获取联系人数量
            contacts = target_frame.query_selector_all('.conversation-item')
            print(f'Total contacts: {len(contacts)}')
    
    browser.close()
