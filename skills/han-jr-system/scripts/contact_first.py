#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright
import time

message = '我要定制一顶棒球帽，两处彩色刺绣，数量1000顶，可以接吗？打样多少钱？多久？'

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://localhost:9222')
    
    # 步骤1: 关闭所有聊天页面，只保留搜索页
    for ctx in browser.contexts:
        for pg in ctx.pages:
            if 'air.1688.com' in pg.url:
                pg.close()
                print('关闭聊天页面')
    
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
    
    print('页面清理完成，只剩搜索页')
    print('='*50)
    
    # 步骤2: 在搜索页点击第一家旺旺
    search_page.bring_to_front()
    time.sleep(1)
    
    buttons = search_page.query_selector_all('.J_WangWang')
    print(f'找到 {len(buttons)} 个旺旺按钮')
    
    if len(buttons) == 0:
        print('没有找到旺旺按钮')
        browser.close()
        exit(1)
    
    print('\n=== 联系第一家 ===')
    search_page.bring_to_front()
    time.sleep(1)
    
    # 点击第一家
    print('点击第一家旺旺按钮...')
    buttons[0].click()
    time.sleep(5)
    
    # 查找聊天页面
    chat_pages = [pg for ctx in browser.contexts for pg in ctx.pages if 'air.1688.com' in pg.url]
    print(f'当前聊天页面数: {len(chat_pages)}')
    
    if len(chat_pages) > 0:
        chat = chat_pages[0]
        print(f'聊天页: {chat.url[:50]}')
        
        # 切换到聊天页
        chat.bring_to_front()
        time.sleep(3)
        
        # 发送消息
        print('发送消息...')
        sent = False
        for frame in chat.frames:
            try:
                inp = frame.locator('pre[contenteditable="true"]').first
                if inp.is_visible():
                    inp.click()
                    time.sleep(0.5)
                    inp.fill(message)
                    time.sleep(0.5)
                    
                    send_btn = frame.locator('button:has-text("发送")').first
                    if send_btn.is_visible():
                        send_btn.click()
                        print('✓ 第一家消息已发送')
                        sent = True
                        time.sleep(2)
                        break
            except Exception as e:
                continue
        
        if not sent:
            print('✗ 发送失败')
    
    print('\n当前所有页面:')
    for ctx_idx, ctx in enumerate(browser.contexts):
        for pg_idx, pg in enumerate(ctx.pages):
            print(f'  [{ctx_idx}.{pg_idx}] {pg.url[:50]}')
    
    browser.close()
