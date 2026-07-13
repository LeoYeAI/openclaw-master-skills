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
            print('Checking scroll position from top to bottom...\n')
            
            # 先滚动到顶部
            target_frame.evaluate('''() => {
                const list = document.querySelector('.conversation-list, .contact-list, [class*="list"]');
                if (list) list.scrollTop = 0;
            }''')
            time.sleep(2)
            
            # 逐步滚动到底部，记录每一步的ScrollHeight
            all_contacts = set()
            scroll_positions = []
            
            for i in range(50):
                # 获取当前信息
                info = target_frame.evaluate('''() => {
                    const list = document.querySelector('.conversation-list, .contact-list, [class*="list"]');
                    const items = document.querySelectorAll('.conversation-item');
                    const names = [];
                    items.forEach(item => {
                        const nameEl = item.querySelector('.name');
                        if (nameEl) names.push(nameEl.innerText.trim());
                    });
                    
                    if (list) {
                        return {
                            scrollTop: list.scrollTop,
                            scrollHeight: list.scrollHeight,
                            clientHeight: list.clientHeight,
                            names: names
                        };
                    }
                    return null;
                }''')
                
                if info:
                    scroll_positions.append({
                        'step': i+1,
                        'scrollTop': info['scrollTop'],
                        'scrollHeight': info['scrollHeight'],
                        'contact_count': len(info['names'])
                    })
                    
                    for name in info['names']:
                        all_contacts.add(name)
                    
                    # 滚动一点
                    target_frame.evaluate('''() => {
                        const list = document.querySelector('.conversation-list, .contact-list, [class*="list"]');
                        if (list) list.scrollTop += 100;
                    }''')
                    
                    time.sleep(0.3)
            
            # 显示结果
            print('Scroll positions:')
            for pos in scroll_positions[::5]:  # 每5步显示一次
                print(f"  Step {pos['step']}: ScrollTop={pos['scrollTop']}, ScrollHeight={pos['scrollHeight']}, Contacts={pos['contact_count']}")
            
            print(f'\nFinal:')
            print(f'  Total unique contacts: {len(all_contacts)}')
            print(f'  Max ScrollHeight: {max(p["scrollHeight"] for p in scroll_positions)}')
            print(f'  Max ScrollTop: {max(p["scrollTop"] for p in scroll_positions)}')
    
    browser.close()
