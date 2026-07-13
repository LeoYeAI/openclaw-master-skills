#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://localhost:9222')
    
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
        
        # 检查页面状态
        for frame in page.frames:
            try:
                contacts = frame.query_selector_all('.conversation-item')
                if len(contacts) > 0:
                    print(f'Found {len(contacts)} contacts in frame')
                    
                    # 检查前5个联系人的位置
                    for i, contact in enumerate(contacts[:5]):
                        try:
                            rect = contact.evaluate('el => el.getBoundingClientRect()')
                            name = contact.query_selector('.name')
                            name_text = name.inner_text() if name else 'Unknown'
                            is_visible = 0 <= rect['y'] <= 600
                            print(f'  {i+1}. {name_text[:30]} - y: {int(rect["y"])}, visible: {is_visible}')
                        except:
                            pass
                    break
            except:
                pass
    
    browser.close()
