#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同步所有旺旺联系人 - 从第一个点击到最后一个

功能:
    1. 获取旺旺所有联系人列表
    2. 从第一个开始，逐个点击
    3. 获取每个联系人的对话记录
    4. 同步到本地数据库
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

def sync_all_contacts():
    """同步所有联系人"""
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
            safe_print("同步所有旺旺联系人")
            safe_print("="*60)
            
            wangwang_page.bring_to_front()
            time.sleep(2)
            
            db = load_database()
            
            # 获取所有联系人
            safe_print("\n获取联系人列表...")
            
            contacts = wangwang_page.evaluate('''() => {
                const results = [];
                const items = document.querySelectorAll('.contact-item, .conversation-item, [class*="contact"], [class*="list-item"]');
                items.forEach((item, index) => {
                    const nameEl = item.querySelector('.name, [class*="name"]');
                    if (nameEl) {
                        const name = nameEl.innerText.trim();
                        // 去重
                        if (!results.find(r => r.name === name)) {
                            results.push({
                                index: index,
                                name: name
                            });
                        }
                    }
                });
                return results;
            }''')
            
            safe_print(f"找到 {len(contacts)} 个联系人")
            safe_print("="*60)
            
            synced_count = 0
            
            # 从第一个到最后一个逐个点击
            for i, contact_info in enumerate(contacts, 1):
                name = contact_info['name']
                
                safe_print(f"\n[{i}/{len(contacts)}] 处理: {name[:40]}")
                
                try:
                    # 点击联系人
                    clicked = wangwang_page.evaluate(f'''
                        (contactName) => {{
                            const items = document.querySelectorAll('.contact-item, .conversation-item, [class*="contact"], [class*="list-item"]');
                            for (const item of items) {{
                                const nameEl = item.querySelector('.name, [class*="name"]');
                                if (nameEl && nameEl.innerText.trim() === contactName) {{
                                    item.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                                    setTimeout(() => item.click(), 500);
                                    return true;
                                }}
                            }}
                            return false;
                        }}
                    ''', name)
                    
                    if clicked:
                        safe_print("  已点击，等待加载...")
                        time.sleep(4)  # 等待聊天加载
                        
                        # 获取对话记录
                        messages = wangwang_page.evaluate('''() => {
                            const results = [];
                            const msgElements = document.querySelectorAll('.message-item, .msg-item, .bubble, [class*="message"], [class*="bubble"]');
                            msgElements.forEach(msg => {
                                const text = msg.innerText || '';
                                if (text.trim() && text.length > 5) {
                                    const className = msg.className || '';
                                    const isMine = className.includes('mine') || className.includes('self') || 
                                                  msg.getAttribute('data-direction') === 'out';
                                    
                                    // 去重检查
                                    const exists = results.find(r => r.text === text.substring(0, 200));
                                    if (!exists) {
                                        results.push({
                                            text: text.substring(0, 200),
                                            direction: isMine ? 'out' : 'in'
                                        });
                                    }
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
                        
                        # 添加新消息
                        new_count = 0
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
                                new_count += 1
                        
                        if new_count > 0:
                            safe_print(f"  新增 {new_count} 条消息")
                        
                        synced_count += 1
                        
                        # 显示最新消息
                        if messages:
                            last_msg = messages[-1]
                            direction = "发出" if last_msg['direction'] == 'out' else "收到"
                            text = last_msg['text'][:50]
                            safe_print(f"  最新: [{direction}] {text}")
                    else:
                        safe_print("  点击失败")
                    
                except Exception as e:
                    safe_print(f"  错误: {e}")
                
                # 间隔
                if i < len(contacts):
                    time.sleep(2)
            
            # 保存数据库
            save_database(db)
            
            safe_print("\n" + "="*60)
            safe_print(f"完成: 同步 {synced_count}/{len(contacts)} 个联系人")
            safe_print(f"数据库现在共有 {len(db['suppliers'])} 家供应商")
            safe_print("="*60)
            
            browser.close()
            return synced_count
            
        except Exception as e:
            safe_print(f"错误: {e}")
            browser.close()
            return 0

if __name__ == "__main__":
    sync_all_contacts()
