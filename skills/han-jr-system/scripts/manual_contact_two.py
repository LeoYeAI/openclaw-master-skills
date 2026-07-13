#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动连续联系两家供应商
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
    
    # 获取搜索结果页
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
    
    print('=== 手动联系供应商 ===')
    print('当前页面数:', len([p for ctx in browser.contexts for p in ctx.pages]))
    
    # 确保在搜索结果页
    search_page.bring_to_front()
    print('在搜索结果页')
    time.sleep(1)
    
    # 找到所有旺旺按钮
    buttons = search_page.query_selector_all('.J_WangWang')
    print(f'找到 {len(buttons)} 个旺旺按钮')
    
    if len(buttons) >= 2:
        # === 联系第一家 ===
        print('\n--- 联系第一家 ---')
        search_page.bring_to_front()
        buttons[0].click()
        print('点击第一家旺旺')
        time.sleep(4)
        
        # 获取聊天页
        chat = None
        for ctx in browser.contexts:
            for pg in ctx.pages:
                if 'air.1688.com' in pg.url:
                    chat = pg
                    break
            if chat:
                break
        
        if chat:
            print(f'聊天页URL: {chat.url[:50]}')
            chat.bring_to_front()
            time.sleep(2)
            
            # 发送消息
            for frame in chat.frames:
                try:
                    inp = frame.locator('pre[contenteditable="true"]').first
                    if inp.is_visible():
                        inp.click()
                        inp.fill(message)
                        time.sleep(0.5)
                        btn = frame.locator('button:has-text("发送")').first
                        btn.click()
                        print('✓ 第一家消息已发送')
                        break
                except Exception as e:
                    print(f'发送失败: {e}')
            
            time.sleep(2)
        
        # === 联系第二家 ===
        print('\n--- 联系第二家 ---')
        
        # 先关闭第一家聊天页
        if chat:
            chat.close()
            print('关闭第一家聊天页')
            time.sleep(2)
        
        # 回到搜索页
        search_page.bring_to_front()
        print('回到搜索页')
        time.sleep(1)
        
        # 重新获取按钮（页面可能刷新）
        buttons = search_page.query_selector_all('.J_WangWang')
        
        # 点击第二家
        if len(buttons) >= 2:
            buttons[1].click()
            print('点击第二家旺旺')
            time.sleep(4)
            
            # 获取新的聊天页
            chat2 = None
            for ctx in browser.contexts:
                for pg in ctx.pages:
                    if 'air.1688.com' in pg.url:
                        chat2 = pg
                        break
                if chat2:
                    break
            
            if chat2:
                print(f'聊天页URL: {chat2.url[:50]}')
                chat2.bring_to_front()
                time.sleep(2)
                
                # 发送消息
                for frame in chat2.frames:
                    try:
                        inp = frame.locator('pre[contenteditable="true"]').first
                        if inp.is_visible():
                            inp.click()
                            inp.fill(message)
                            time.sleep(0.5)
                            btn = frame.locator('button:has-text("发送")').first
                            btn.click()
                            print('✓ 第二家消息已发送')
                            break
                    except Exception as e:
                        print(f'发送失败: {e}')
                
                time.sleep(2)
                chat2.close()
        
        print('\n当前页面数:', len([p for ctx in browser.contexts for p in ctx.pages]))
    
    browser.close()
    print('\n=== 完成 ===')
