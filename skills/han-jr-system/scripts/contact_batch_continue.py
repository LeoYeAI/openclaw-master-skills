#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
继续联系更多供应商 - 使用正确的iframe方法

流程：
1. 获取所有旺旺链接
2. 逐一打开聊天页面
3. 在Frame 1中找到输入框
4. 发送消息
5. 关闭聊天页
6. 继续下一家
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
    
    print('=== 批量联系供应商 ===')
    
    # 获取所有旺旺链接
    ww_hrefs = search_page.evaluate('''() => {
        const links = document.querySelectorAll('a[href*="air.1688.com"][href*="im"]');
        return Array.from(links).map(a => a.href);
    }''')
    
    print(f'找到 {len(ww_hrefs)} 个旺旺链接')
    print(f'计划联系: {min(len(ww_hrefs), 10)} 家供应商')
    print('='*60)
    
    success_count = 0
    
    for i in range(min(len(ww_hrefs), 10)):
        print(f'\n[{i+1}/{min(len(ww_hrefs), 10)}] 联系供应商...')
        print(f'链接: {ww_hrefs[i][:60]}')
        
        try:
            # 打开聊天页面
            chat_page = browser.contexts[0].new_page()
            chat_page.goto(ww_hrefs[i], wait_until="domcontentloaded")
            time.sleep(4)
            
            chat_page.bring_to_front()
            time.sleep(1)
            
            # 在Frame 1中发送消息
            sent = False
            for frame_idx, frame in enumerate(chat_page.frames):
                try:
                    inp = frame.locator("pre[contenteditable='true']").first
                    if inp.is_visible():
                        inp.click()
                        time.sleep(0.3)
                        inp.fill(message)
                        time.sleep(0.3)
                        
                        btn = frame.locator("button:has-text('发送')").first
                        if btn.is_visible():
                            btn.click()
                            print(f'  ✓ 消息已发送 (Frame {frame_idx})')
                            sent = True
                            success_count += 1
                            time.sleep(1)
                            break
                except:
                    continue
            
            if not sent:
                print(f'  ✗ 发送失败')
            
            # 关闭聊天页
            chat_page.close()
            time.sleep(2)
            
        except Exception as e:
            print(f'  ✗ 错误: {e}')
            continue
        
        # 间隔
        if i < min(len(ww_hrefs), 10) - 1:
            print('  等待3秒...')
            time.sleep(3)
    
    print('\n' + '='*60)
    print(f'完成: {success_count}/{min(len(ww_hrefs), 10)} 家供应商已联系')
    print('='*60)
    
    browser.close()
