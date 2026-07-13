#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同步旺旺联系人和完整对话记录到本地供应商系统 - 改进版

功能:
    1. 点击每个联系人获取完整对话记录
    2. 同步到本地供应商数据库
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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

def sync_with_chat_history():
    """同步旺旺联系人和完整对话记录"""
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
            safe_print("同步旺旺联系人和对话记录")
            safe_print("="*60)
            
            wangwang_page.bring_to_front()
            time.sleep(2)
            
            db = load_database()
            
            # 获取联系人列表（使用JavaScript）
            safe_print("\n获取联系人列表...")
            
            contacts_js = wangwang_page.evaluate('''() => {
                const results = [];
                const items = document.querySelectorAll('.contact-item, .conversation-item, [class*="contact"], [class*="list-item"]');
                items.forEach((item, index) => {
                    const nameEl = item.querySelector('.name, [class*="name"]');
                    if (nameEl) {
                        results.push({
                            index: index,
                            name: nameEl.innerText.trim()
                        });
                    }
                });
                return results;
            }''')
            
            unique_contacts = []
            seen_names = set()
            for c in contacts_js:
                if c['name'] not in seen_names and c['name'] != 'Unknown':
                    seen_names.add(c['name'])
                    unique_contacts.append(c)
            
            safe_print(f"找到 {len(unique_contacts)} 个唯一联系人")
            safe_print("="*60)
            
            synced_count = 0
            
            # 只处理前10个联系人
            for contact_info in unique_contacts[:10]:
                name = contact_info['name']
                
                safe_print(f"\n[{synced_count+1}/10] 处理: {name}")
                
                try:
                    # 点击联系人
                    clicked = wangwang_page.evaluate(f'''(contactName) => {{
                        const items = document.querySelectorAll('.contact-item, .conversation-item, [class*="contact"], [class*="list-item"]');
                        for (const item of items) {{
                            const nameEl = item.querySelector('.name, [class*="name"]');
                            if (nameEl && nameEl.innerText.trim() === contactName) {{
                                item.click();
                                return true;
                            }}
                        }}
                        return false;
                    }}''', name)
                    
                    if clicked:
                        safe_print("  已点击联系人，等待加载...")
                        time.sleep(3)
                        
                        # 获取对话记录
                        messages = wangwang_page.evaluate('''() => {
                            const results = [];
                            const msgElements = document.querySelectorAll('.message-item, .msg-item, [class*="message"], [class*="bubble"]');
                            msgElements.forEach(msg => {
                                const textEl = msg.querySelector('.text, [class*="text"], .content, [class*="content"]');
                                const text = textEl ? textEl.innerText.trim() : msg.innerText.trim();
                                
                                // 判断是发出还是收到
                                const isMine = msg.classList.contains('mine') || msg.classList.contains('self') || 
                                              msg.getAttribute('data-direction') === 'out';
                                
                                if (text && text.length > 0) {
                                    results.push({
                                        text: text.substring(0, 200),
                                        direction: isMine ? 'out' : 'in'
                                    });
                                }
                            });
                            return results.slice(-10);  // 最近10条
                        }''')
                        
                        safe_print(f"  获取到 {len(messages)} 条消息")
                        
                        # 查找或创建供应商
                        supplier = find_or_create_supplier(db, name)
                        
                        # 更新状态
                        has_reply = any(m['direction'] == 'in' for m in messages)
                        if has_reply:
                            supplier['status'] = '已回复'
                        elif messages:
                            supplier['status'] = '已联系'
                        
                        # 添加对话记录
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
                        
                        if messages:
                            safe_print("  最新消息:")
                            for msg in messages[-3:]:
                                direction = "→" if msg['direction'] == 'out' else "←"
                                safe_print(f"    {direction} {msg['text'][:50]}")
                    else:
                        safe_print("  点击失败")
                
                except Exception as e:
                    safe_print(f"  Error: {e}")
                
                time.sleep(2)
            
            # 保存数据库
            save_database(db)
            
            safe_print("\n" + "="*60)
            safe_print(f"同步完成: {synced_count} 个联系人")
            safe_print(f"数据库现在共有 {len(db['suppliers'])} 家供应商")
            safe_print("="*60)
            
            browser.close()
            return synced_count
            
        except Exception as e:
            safe_print(f"Error: {e}")
            import traceback
            safe_print(traceback.format_exc())
            browser.close()
            return 0

if __name__ == "__main__":
    sync_with_chat_history()
