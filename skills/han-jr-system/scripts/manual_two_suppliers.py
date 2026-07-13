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
    
    print('=== 在搜索结果页联系供应商 ===')
    print('当前页面:', search_page.url[:50])
    
    # 确保在搜索页
    search_page.bring_to_front()
    time.sleep(2)
    
    # 找到所有旺旺链接（在搜索结果页）
    # 旺旺链接特征：href包含 air.1688.com 和 im
    ww_links = search_page.query_selector_all('a[href*="air.1688.com"][href*="im"]')
    print(f'找到 {len(ww_links)} 个旺旺链接')
    
    if len(ww_links) == 0:
        print('尝试其他选择器...')
        ww_links = search_page.query_selector_all('.ww-link, .J_WangWang')
        print(f'找到 {len(ww_links)} 个旺旺按钮')
    
    if len(ww_links) >= 2:
        # === 联系第一家 ===
        print('\n--- 联系第一家 ---')
        search_page.bring_to_front()
        time.sleep(1)
        
        print('点击第一家旺旺...')
        ww_links[0].click()
        time.sleep(5)
        
        # 查找新打开的聊天页
        chat = None
        for ctx in browser.contexts:
            for pg in ctx.pages:
                if 'air.1688.com' in pg.url:
                    chat = pg
                    break
            if chat:
                break
        
        if chat:
            print(f'聊天页已打开: {chat.url[:40]}')
            chat.bring_to_front()
            time.sleep(3)
            
            # 发送消息
            print('发送消息...')
            for frame in chat.frames:
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
            
            # 关闭聊天页
            chat.close()
            print('关闭第一家聊天页')
            time.sleep(2)
        
        # === 联系第二家 ===
        print('\n--- 联系第二家 ---')
        search_page.bring_to_front()
        time.sleep(1)
        
        # 重新获取链接
        ww_links = search_page.query_selector_all('a[href*="air.1688.com"][href*="im"]')
        
        if len(ww_links) >= 2:
            print('点击第二家旺旺...')
            ww_links[1].click()
            time.sleep(5)
            
            # 查找新聊天页
            chat2 = None
            for ctx in browser.contexts:
                for pg in ctx.pages:
                    if 'air.1688.com' in pg.url:
                        chat2 = pg
                        break
                if chat2:
                    break
            
            if chat2:
                print(f'聊天页已打开: {chat2.url[:40]}')
                chat2.bring_to_front()
                time.sleep(3)
                
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
                
                chat2.close()
                print('关闭第二家聊天页')
        
        print('\n=== 完成 ===')
        print('当前页面数:', len([p for ctx in browser.contexts for p in ctx.pages]))
    else:
        print('旺旺链接不足2个')
    
    browser.close()
