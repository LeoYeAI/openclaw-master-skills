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
        
        print('Step 1: Clear search box')
        # 清空搜索框
        for frame in page.frames:
            try:
                inp = frame.locator('input.ant-input').first
                if inp.is_visible():
                    inp.fill('')
                    time.sleep(0.5)
                    inp.press('Enter')
                    print('  Search box cleared and Enter pressed')
                    break
            except:
                pass
        
        time.sleep(3)
        
        print('\nStep 2: Check frames')
        print(f'Total frames: {len(page.frames)}')
        
        for i, frame in enumerate(page.frames):
            try:
                # 尝试多种选择器
                selectors = [
                    '.contact-item',
                    '.conversation-item', 
                    '[class*="contact"]',
                    '[class*="list-item"]',
                    '.ant-list-item'
                ]
                
                for sel in selectors:
                    try:
                        contacts = frame.query_selector_all(sel)
                        if len(contacts) > 0:
                            print(f'Frame {i}: Found {len(contacts)} elements with "{sel}"')
                            # 显示第一个的名称
                            first = contacts[0]
                            name_el = first.query_selector('.name, [class*="name"]')
                            if name_el:
                                name = name_el.inner_text()
                                print(f'  First contact: {name[:30]}')
                            break
                    except:
                        pass
                        
            except Exception as e:
                print(f'Frame {i}: Error')
        
        # 截图
        page.screenshot(path='debug_contacts.png', full_page=False)
        print('\nScreenshot saved: debug_contacts.png')
    
    browser.close()
