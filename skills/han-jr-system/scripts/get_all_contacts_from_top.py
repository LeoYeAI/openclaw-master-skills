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
            # 滚动到顶部
            print('Scrolling to top...')
            target_frame.evaluate('''() => {
                const list = document.querySelector('[style*="overflow: auto"]');
                if (list) list.scrollTop = 0;
            }''')
            time.sleep(3)
            
            # 获取所有联系人（从顶部开始）
            print('Getting all contacts from top...')
            
            all_contacts = []
            last_scroll_top = -1
            same_count = 0
            
            for i in range(200):  # 最多200次滚动
                # 获取当前可见的联系人
                contacts = target_frame.evaluate('''() => {
                    const results = [];
                    const items = document.querySelectorAll('.conversation-item');
                    items.forEach(item => {
                        const nameEl = item.querySelector('.name');
                        const timeEl = item.querySelector('.time');
                        const descEl = item.querySelector('.desc');
                        
                        if (nameEl) {
                            const rect = item.getBoundingClientRect();
                            results.push({
                                name: nameEl.innerText.trim(),
                                time: timeEl ? timeEl.innerText.trim() : '',
                                desc: descEl ? descEl.innerText.trim() : '',
                                top: rect.top
                            });
                        }
                    });
                    return results;
                }''')
                
                # 添加到总列表（去重）
                for c in contacts:
                    if not any(existing['name'] == c['name'] for existing in all_contacts):
                        all_contacts.append(c)
                
                # 获取当前scroll位置
                scroll_info = target_frame.evaluate('''() => {
                    const list = document.querySelector('[style*="overflow: auto"]');
                    if (list) {
                        return {
                            scrollTop: list.scrollTop,
                            scrollHeight: list.scrollHeight,
                            clientHeight: list.clientHeight
                        };
                    }
                    return null;
                }''')
                
                if scroll_info:
                    if scroll_info['scrollTop'] == last_scroll_top:
                        same_count += 1
                        if same_count >= 3:
                            print(f'Scroll {i+1}: Reached end (no change)')
                            break
                    else:
                        same_count = 0
                        last_scroll_top = scroll_info['scrollTop']
                        
                        if (i+1) % 10 == 0:
                            print(f'Scroll {i+1}: Total {len(all_contacts)} contacts, ScrollTop: {scroll_info["scrollTop"]} / {scroll_info["scrollHeight"]}')
                
                # 向下滚动
                target_frame.evaluate('''() => {
                    const list = document.querySelector('[style*="overflow: auto"]');
                    if (list) list.scrollTop += 200;
                }''')
                
                time.sleep(0.5)
            
            print(f'\nFinal: Total {len(all_contacts)} unique contacts')
            print('\nFirst 10 contacts:')
            for i, c in enumerate(all_contacts[:10], 1):
                print(f'{i}. {c["name"]} - {c["time"]} - {c["desc"][:30]}')
            
            print('\nLast 10 contacts:')
            for i, c in enumerate(all_contacts[-10:], len(all_contacts)-9):
                print(f'{i}. {c["name"]} - {c["time"]} - {c["desc"][:30]}')
    
    browser.close()
