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
        
        # 查找搜索框
        search_box = page.query_selector('input.ant-input')
        if search_box:
            print('Found search box (ant-input)')
            
            # 获取placeholder
            placeholder = search_box.get_attribute('placeholder')
            print(f'Placeholder: {placeholder}')
            
            # 输入供应商名称
            search_box.fill('东莞宝瑞森')
            print('Input: 东莞宝瑞森')
            
            time.sleep(2)
            
            # 截图查看搜索结果
            page.screenshot(path='search_result.png', full_page=False)
            print('Screenshot saved: search_result.png')
        else:
            print('Search box not found')
            # 尝试其他选择器
            inputs = page.query_selector_all('input[type="text"]')
            print(f'Found {len(inputs)} text inputs')
            for i, inp in enumerate(inputs):
                ph = inp.get_attribute('placeholder') or ''
                print(f'  Input {i}: placeholder="{ph}"')
    
    browser.close()
