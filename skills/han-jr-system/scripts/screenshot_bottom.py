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
        
        # 找到包含联系人的frame并滚动到底
        for frame in page.frames:
            try:
                contacts_test = frame.query_selector_all('.conversation-item')
                if len(contacts_test) > 0:
                    # 滚动到底
                    for i in range(10):
                        frame.evaluate('''() => {
                            const list = document.querySelector('.conversation-list, .contact-list, [class*="list"]');
                            if (list) list.scrollTop = list.scrollHeight;
                        }''')
                        time.sleep(1)
                    
                    # 截图
                    page.screenshot(path='contacts_at_bottom.png', full_page=False)
                    print('Screenshot saved: contacts_at_bottom.png')
                    break
            except:
                pass
    
    browser.close()
