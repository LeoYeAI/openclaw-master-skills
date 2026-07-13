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
        
        # 清空搜索框
        for frame in page.frames:
            try:
                inp = frame.locator('input.ant-input').first
                if inp.is_visible():
                    inp.fill('')
                    inp.press('Enter')
                    print('Search box cleared')
                    break
            except:
                pass
        
        time.sleep(3)
        
        # 找到包含联系人的frame
        target_frame = None
        for frame in page.frames:
            try:
                contacts_test = frame.query_selector_all('.conversation-item')
                if len(contacts_test) > 0:
                    target_frame = frame
                    break
            except:
                pass
        
        if target_frame:
            # 持续滚动，获取更多联系人
            all_names = set()
            last_count = 0
            no_change = 0
            
            print('Scrolling to get all contacts...')
            
            for i in range(50):  # 最多滚动50次
                # 获取当前联系人
                contacts = target_frame.evaluate('''() => {
                    const results = [];
                    const items = document.querySelectorAll('.conversation-item');
                    items.forEach(item => {
                        const nameEl = item.querySelector('.name');
                        if (nameEl) {
                            results.push(nameEl.innerText.trim());
                        }
                    });
                    return results;
                }''')
                
                for name in contacts:
                    if name:
                        all_names.add(name)
                
                current_count = len(all_names)
                
                if current_count > last_count:
                    print(f'Scroll {i+1}: Total {current_count} contacts (+{current_count - last_count})')
                    last_count = current_count
                    no_change = 0
                else:
                    no_change += 1
                    if no_change >= 5:
                        print(f'Scroll {i+1}: No new contacts, stopping')
                        break
                
                # 滚动
                target_frame.evaluate('''() => {
                    const list = document.querySelector('.conversation-list, .contact-list, [class*="list"]');
                    if (list) list.scrollTop = list.scrollHeight;
                }''')
                
                time.sleep(1.5)
            
            print(f'\nFinal: Total {len(all_names)} contacts')
            print('\nAll contacts:')
            for i, name in enumerate(sorted(all_names), 1):
                print(f'{i}. {name}')
    
    browser.close()
