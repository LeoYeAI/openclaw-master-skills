#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动联系两家供应商 - 使用直接打开链接方式

方法：直接获取旺旺链接的href，在新标签页打开聊天页面
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright
import time

message = '我要定制一顶棒球帽，两处彩色刺绣，数量1000顶，可以接吗？打样多少钱？多久？'

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://localhost:9222')
    
    # 关闭所有聊天页面
    for ctx in browser.contexts:
        for pg in ctx.pages:
            if 'air.1688.com' in pg.url:
                pg.close()
    
    # 获取搜索页
    search_page = None
    for ctx in browser.contexts:
        for pg in ctx.pages:
            if 'selloffer' in pg.url:
                search_page = pg
                break
    
    if not search_page:
        print('搜索页未找到')
        browser.close()
        exit(1)
    
    print('=== 使用直接链接方式联系供应商 ===')
    search_page.bring_to_front()
    time.sleep(2)
    
    # 获取所有旺旺链接的href
    ww_hrefs = search_page.evaluate('''() => {
        const links = document.querySelectorAll('a[href*="air.1688.com"][href*="im"]');
        return Array.from(links).map(a => a.href);
    }''')
    
    print(f'找到 {len(ww_hrefs)} 个旺旺链接')
    
    if len(ww_hrefs) >= 2:
        # === 联系第一家 ===
        print('\n--- 联系第一家 ---')
        print(f'链接: {ww_hrefs[0][:60]}')
        
        # 直接打开聊天链接
        chat1 = browser.contexts[0].new_page()
        chat1.goto(ww_hrefs[0], wait_until="domcontentloaded")
        time.sleep(5)
        
        print(f'聊天页已打开: {chat1.url[:40]}')
        
        # 发送消息
        print('发送消息...')
        for frame in chat1.frames:
            try:
                inp = frame.locator('pre[contenteditable="true"]').first
                if inp.is_visible():
                    inp.click()
                    time.sleep(0.5)
                    inp.fill(message)
                    time.sleep(0.5)
                    
                    btn = frame.locator('button:has-text("发送")').first
                    if btn.is_visible():
                        btn.click()
                        print('✓ 第一家消息已发送')
                        time.sleep(2)
                        break
            except:
                pass
        
        # 关闭第一家聊天页
        chat1.close()
        print('关闭第一家聊天页')
        time.sleep(2)
        
        # === 联系第二家 ===
        print('\n--- 联系第二家 ---')
        print(f'链接: {ww_hrefs[1][:60]}')
        
        # 直接打开聊天链接
        chat2 = browser.contexts[0].new_page()
        chat2.goto(ww_hrefs[1], wait_until="domcontentloaded")
        time.sleep(5)
        
        print(f'聊天页已打开: {chat2.url[:40]}')
        
        # 发送消息
        print('发送消息...')
        for frame in chat2.frames:
            try:
                inp = frame.locator('pre[contenteditable="true"]').first
                if inp.is_visible():
                    inp.click()
                    time.sleep(0.5)
                    inp.fill(message)
                    time.sleep(0.5)
                    
                    btn = frame.locator('button:has-text("发送")').first
                    if btn.is_visible():
                        btn.click()
                        print('✓ 第二家消息已发送')
                        time.sleep(2)
                        break
            except:
                pass
        
        # 关闭第二家聊天页
        chat2.close()
        print('关闭第二家聊天页')
        
        print('\n=== 完成 ===')
        print('当前页面数:', len([p for ctx in browser.contexts for p in ctx.pages]))
    else:
        print('旺旺链接不足2个')
    
    browser.close()
