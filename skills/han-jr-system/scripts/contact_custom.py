#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
联系新的供应商 - 棒球帽定制
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright
import time

message = '我要定制一顶棒球帽，两处彩色刺绣，数量1000顶，可以接吗？打样多少钱？多久？'

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://localhost:9222')
    
    # 获取搜索页（棒球帽定制）
    search_page = None
    for ctx in browser.contexts:
        for pg in ctx.pages:
            if 'selloffer' in pg.url and '%B6%A8%D6%C6' in pg.url:  # 定制的URL编码
                search_page = pg
                break
        if search_page:
            break
    
    if not search_page:
        print('棒球帽定制搜索页未找到')
        browser.close()
        exit(1)
    
    print('=== 联系棒球帽定制供应商 ===')
    
    # 获取所有旺旺链接
    ww_hrefs = search_page.evaluate('''() => {
        const links = document.querySelectorAll('a[href*="air.1688.com"][href*="im"]');
        return Array.from(links).map(a => a.href);
    }''')
    
    print(f'找到 {len(ww_hrefs)} 个旺旺链接')
    print('='*60)
    
    success_count = 0
    
    for i in range(len(ww_hrefs)):
        print(f'\n[{i+1}/{len(ww_hrefs)}] 联系供应商...')
        
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
                            print(f'  ✓ 消息已发送')
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
        if i < len(ww_hrefs) - 1:
            print('  等待3秒...')
            time.sleep(3)
    
    print('\n' + '='*60)
    print(f'完成: {success_count}/{len(ww_hrefs)} 家定制供应商已联系')
    print('='*60)
    
    browser.close()
