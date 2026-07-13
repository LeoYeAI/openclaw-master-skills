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
        
        print(f'Total frames: {len(page.frames)}')
        
        # 在所有frames中查找搜索框
        for i, frame in enumerate(page.frames):
            try:
                # 尝试多种选择器
                selectors = [
                    'input.ant-input',
                    'input[type="text"]',
                    'input[placeholder*="搜索"]',
                    '.search-input input',
                ]
                
                for sel in selectors:
                    inp = frame.query_selector(sel)
                    if inp:
                        ph = inp.get_attribute('placeholder') or ''
                        print(f'Frame {i}: Found input with selector "{sel}"')
                        print(f'  Placeholder: {ph}')
                        
                        # 输入供应商名称
                        inp.fill('东莞宝瑞森')
                        print(f'  Input: 东莞宝瑞森')
                        
                        time.sleep(2)
                        
                        # 截图
                        page.screenshot(path=f'search_frame_{i}.png', full_page=False)
                        print(f'  Screenshot: search_frame_{i}.png')
                        break
            except Exception as e:
                print(f'Frame {i}: Error - {e}')
    
    browser.close()
