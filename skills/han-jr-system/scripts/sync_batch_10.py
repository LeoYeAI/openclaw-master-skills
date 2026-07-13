#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分批同步旺旺联系人 - 每批10家

用法:
    python sync_batch_10.py --batch 0  # 同步第1-10家
    python sync_batch_10.py --batch 1  # 同步第11-20家
    ...
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import argparse
import json
import time
from datetime import datetime
from pathlib import Path

DATABASE_FILE = "suppliers_database.json"

def safe_print(text):
    try:
        print(text)
    except:
        print(str(text).encode('utf-8', errors='replace').decode('utf-8', errors='replace'))

def load_database():
    db_path = Path(DATABASE_FILE)
    if db_path.exists():
        with open(db_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'suppliers': [], 'last_updated': datetime.now().isoformat()}

def save_database(data):
    data['last_updated'] = datetime.now().isoformat()
    with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def find_or_create_supplier(db, name):
    for s in db['suppliers']:
        if s['name'] == name:
            return s
    
    supplier = {
        'id': len(db['suppliers']) + 1,
        'name': name,
        'product': '帽子',
        'link': '',
        'price': 'Unknown',
        'contact': '',
        'notes': '从旺旺同步',
        'status': '待联系',
        'created_at': datetime.now().isoformat(),
        'history': []
    }
    db['suppliers'].append(supplier)
    return supplier

def sync_batch_10(batch_num=0):
    """同步指定批次的10个联系人"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        safe_print("Error: pip install playwright")
        return 0
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception as e:
            safe_print(f"Error: Cannot connect to Chrome: {e}")
            return 0
        
        try:
            # 查找旺旺聊天页面
            wangwang_page = None
            for ctx in browser.contexts:
                for pg in ctx.pages:
                    if "air.1688.com" in pg.url and "def_cbu_web_im" in pg.url:
                        wangwang_page = pg
                        break
                if wangwang_page:
                    break
            
            if not wangwang_page:
                safe_print("旺旺聊天页面未找到")
                browser.close()
                return 0
            
            safe_print("="*60)
            safe_print(f"同步第 {batch_num + 1} 批联系人（每批10家）")
            safe_print("="*60)
            
            wangwang_page.bring_to_front()
            time.sleep(2)
            
            # 找到包含联系人的frame
            target_frame = None
            for frame in wangwang_page.frames:
                try:
                    contacts_test = frame.query_selector_all('.conversation-item')
                    if len(contacts_test) > 0:
                        target_frame = frame
                        break
                except:
                    pass
            
            if not target_frame:
                safe_print("未找到包含联系人的frame")
                browser.close()
                return 0
            
            db = load_database()
            
            # 获取所有联系人
            safe_print("\n获取所有联系人...")
            
            all_contacts = []
            last_scroll_top = -1
            same_count = 0
            
            for i in range(100):
                contacts = target_frame.evaluate('''() => {
                    const results = [];
                    const items = document.querySelectorAll('.conversation-item');
                    items.forEach(item => {
                        const nameEl = item.querySelector('.name');
                        if (nameEl) {
                            const rect = item.getBoundingClientRect();
                            results.push({
                                name: nameEl.innerText.trim(),
                                top: rect.top,
                                itemTop: item.offsetTop
                            });
                        }
                    });
                    return results;
                }''')
                
                for c in contacts:
                    if not any(existing['name'] == c['name'] for existing in all_contacts):
                        all_contacts.append(c)
                
                scroll_info = target_frame.evaluate('''() => {
                    const list = document.querySelector('[style*="overflow: auto"]');
                    if (list) return { scrollTop: list.scrollTop, scrollHeight: list.scrollHeight };
                    return null;
                }''')
                
                if scroll_info:
                    if scroll_info['scrollTop'] == last_scroll_top:
                        same_count += 1
                        if same_count >= 3:
                            break
                    else:
                        same_count = 0
                        last_scroll_top = scroll_info['scrollTop']
                
                target_frame.evaluate('''() => {
                    const list = document.querySelector('[style*="overflow: auto"]');
                    if (list) list.scrollTop += 300;
                }''')
                
                time.sleep(0.5)
            
            safe_print(f"总共找到 {len(all_contacts)} 个联系人")
            
            # 计算本批次的起始和结束索引
            start_idx = batch_num * 10
            end_idx = min(start_idx + 10, len(all_contacts))
            
            if start_idx >= len(all_contacts):
                safe_print(f"批次 {batch_num} 超出范围，总共只有 {len(all_contacts)} 个联系人")
                browser.close()
                return 0
            
            batch_contacts = all_contacts[start_idx:end_idx]
            
            safe_print(f"\n本批次: 第 {start_idx + 1} - {end_idx} 家")
            safe_print("="*60)
            
            synced_count = 0
            
            for i, contact in enumerate(batch_contacts, 1):
                name = contact['name']
                item_top = contact.get('itemTop', 0)
                
                safe_print(f"\n[{i}/{len(batch_contacts)}] {name[:40]}")
                
                try:
                    # 先滚动到联系人位置
                    target_frame.evaluate(f'''
                        () => {{
                            const list = document.querySelector('[style*="overflow: auto"]');
                            if (list) list.scrollTop = {item_top} - 100;
                        }}
                    ''')
                    time.sleep(1)
                    
                    # 点击联系人
                    clicked = target_frame.evaluate(f'''
                        (contactName) => {{
                            const items = document.querySelectorAll('.conversation-item');
                            for (const item of items) {{
                                const nameEl = item.querySelector('.name');
                                if (nameEl && nameEl.innerText.trim() === contactName) {{
                                    item.click();
                                    return true;
                                }}
                            }}
                            return false;
                        }}
                    ''', name)
                    
                    if clicked:
                        time.sleep(3)
                        
                        # 获取对话
                        messages = wangwang_page.evaluate('''() => {
                            const results = [];
                            const msgElements = document.querySelectorAll('.message-item, .msg-item, .bubble');
                            msgElements.forEach(msg => {
                                const text = msg.innerText || '';
                                if (text.trim() && text.length > 5) {
                                    const className = msg.className || '';
                                    const isMine = className.includes('mine') || className.includes('self');
                                    
                                    const exists = results.find(r => r.text === text.substring(0, 200));
                                    if (!exists) {
                                        results.push({
                                            text: text.substring(0, 200),
                                            direction: isMine ? 'out' : 'in'
                                        });
                                    }
                                }
                            });
                            return results.slice(-3);
                        }''')
                        
                        # 同步到数据库
                        supplier = find_or_create_supplier(db, name)
                        
                        has_reply = any(m['direction'] == 'in' for m in messages)
                        if has_reply:
                            supplier['status'] = '已回复'
                        elif messages:
                            supplier['status'] = '已联系'
                        
                        for msg in messages:
                            exists = False
                            for h in supplier['history']:
                                if h['message'] == msg['text']:
                                    exists = True
                                    break
                            
                            if not exists:
                                supplier['history'].append({
                                    'time': datetime.now().isoformat(),
                                    'message': msg['text'],
                                    'direction': msg['direction']
                                })
                        
                        synced_count += 1
                        safe_print(f"  ✓ 同步完成 ({len(messages)} 条)")
                    else:
                        safe_print("  ✗ 点击失败")
                    
                except Exception as e:
                    safe_print(f"  ✗ 错误: {e}")
                
                if i < len(batch_contacts):
                    time.sleep(2)
            
            # 保存数据库
            save_database(db)
            
            safe_print("\n" + "="*60)
            safe_print(f"批次 {batch_num} 完成: 同步 {synced_count}/{len(batch_contacts)} 家")
            safe_print(f"数据库现在共有 {len(db['suppliers'])} 家供应商")
            safe_print("="*60)
            
            browser.close()
            return synced_count
            
        except Exception as e:
            safe_print(f"错误: {e}")
            browser.close()
            return 0

def main():
    parser = argparse.ArgumentParser(description='分批同步旺旺联系人（每批10家）')
    parser.add_argument('--batch', '-b', type=int, default=0, help='批次号（从0开始）')
    args = parser.parse_args()
    
    sync_batch_10(args.batch)

if __name__ == "__main__":
    main()
