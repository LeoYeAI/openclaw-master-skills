#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动操作：正确点击iframe中的联系人并发送消息

学习点：
1. 使用 page.frames 遍历所有frames
2. 在正确的frame中找到输入框
3. 点击联系人列表
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
    
    print('=== 手动操作：正确点击iframe联系人 ===')
    
    # 获取旺旺链接
    ww_hrefs = search_page.evaluate('''() => {
        const links = document.querySelectorAll('a[href*="air.1688.com"][href*="im"]');
        return Array.from(links).map(a => a.href);
    }''')
    
    print(f'找到 {len(ww_hrefs)} 个旺旺链接')
    
    if len(ww_hrefs) >= 1:
        # === 联系第一家 ===
        print('\n--- 联系第一家 ---')
        
        # 打开聊天链接
        chat_page = browser.contexts[0].new_page()
        chat_page.goto(ww_hrefs[0], wait_until="domcontentloaded")
        print('聊天页打开，等待加载...')
        time.sleep(5)
        
        chat_page.bring_to_front()
        time.sleep(2)
        
        # 截图查看当前状态
        chat_page.screenshot(path='chat_step1_opened.png', full_page=False)
        print('截图: chat_step1_opened.png')
        
        # 查看所有frames
        print(f'\n页面frames数量: {len(chat_page.frames)}')
        for i, frame in enumerate(chat_page.frames):
            print(f'  Frame {i}: {frame.url[:50]}')
        
        # 尝试点击联系人列表第一位
        print('\n尝试点击联系人...')
        
        # 方法1：在主页面找联系人
        contact_clicked = False
        try:
            # 常见联系人选择器
            contact_selectors = [
                '.contact-list .contact-item:first-child',
                '.contact-item:first-child',
                '.list-wrap .list-item:first-child',
                '[class*="contact"]:first-child',
                '.conversation-item:first-child',
            ]
            
            for sel in contact_selectors:
                try:
                    contact = chat_page.locator(sel).first
                    if contact.is_visible():
                        contact.click()
                        print(f'点击联系人成功: {sel}')
                        contact_clicked = True
                        time.sleep(2)
                        break
                except:
                    continue
        except Exception as e:
            print(f'主页面点击联系人失败: {e}')
        
        # 方法2：在每个frame中找联系人
        if not contact_clicked:
            print('在主页面未找到联系人，尝试在frames中查找...')
            for i, frame in enumerate(chat_page.frames):
                try:
                    print(f'  检查 Frame {i}...')
                    # 尝试找联系人
                    contacts = frame.query_selector_all('.contact-item, .list-item')
                    if len(contacts) > 0:
                        print(f'    找到 {len(contacts)} 个联系人')
                        contacts[0].click()
                        print(f'    点击了第一个联系人')
                        contact_clicked = True
                        time.sleep(2)
                        break
                except Exception as e:
                    print(f'    Frame {i} 失败: {e}')
        
        # 截图点击联系人后的状态
        chat_page.screenshot(path='chat_step2_contact_clicked.png', full_page=False)
        print('截图: chat_step2_contact_clicked.png')
        
        # 发送消息
        print('\n发送消息...')
        sent = False
        
        # 方法1：在主页面找输入框
        for sel in ["pre[contenteditable='true']", "[contenteditable='true']"]:
            try:
                inp = chat_page.locator(sel).first
                if inp.is_visible():
                    inp.click()
                    time.sleep(0.5)
                    inp.fill(message)
                    time.sleep(0.5)
                    
                    btn = chat_page.locator("button:has-text('发送')").first
                    if btn.is_visible():
                        btn.click()
                        print('✓ 消息已发送（主页面）')
                        sent = True
                        time.sleep(2)
                        break
            except:
                pass
        
        # 方法2：在frames中找输入框
        if not sent:
            print('在主页面未找到输入框，尝试在frames中查找...')
            for i, frame in enumerate(chat_page.frames):
                try:
                    print(f'  检查 Frame {i}...')
                    inp = frame.locator("pre[contenteditable='true']").first
                    if inp.is_visible():
                        inp.click()
                        time.sleep(0.5)
                        inp.fill(message)
                        time.sleep(0.5)
                        
                        btn = frame.locator("button:has-text('发送')").first
                        if btn.is_visible():
                            btn.click()
                            print(f'✓ 消息已发送（Frame {i}）')
                            sent = True
                            time.sleep(2)
                            break
                except Exception as e:
                    print(f'    Frame {i} 失败: {e}')
        
        # 截图发送后的状态
        chat_page.screenshot(path='chat_step3_message_sent.png', full_page=False)
        print('截图: chat_step3_message_sent.png')
        
        if not sent:
            print('✗ 消息发送失败')
        
        # 关闭聊天页
        chat_page.close()
        print('\n关闭聊天页')
        
        print('\n=== 完成 ===')
    else:
        print('旺旺链接不足')
    
    browser.close()
