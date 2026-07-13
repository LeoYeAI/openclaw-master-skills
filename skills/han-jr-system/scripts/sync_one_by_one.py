#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
逐个检查更新旺旺联系人 - 从最后一个到第一个

流程:
    1. 滚动到底部
    2. 从最后一个联系人开始
    3. 逐个点击，获取对话
    4. 同步到数据库
    5. 截图验证
    6. 移动到上一个联系人
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

def sync_contacts_one_by_one():
    """逐个同步联系人"""
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
            safe_print("逐个同步旺旺联系人（从最后一个到第一个）")
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
            
            # 滚动到底部获取所有联系人
            safe_print("\n滚动到底部获取所有联系人...")
            for i in range(20):
                target_frame.evaluate('''() => {
                    const list = document.querySelector('.conversation-list, .contact-list, [class*="list"]');
                    if (list) list.scrollTop = list.scrollHeight;
                }''')
                time.sleep(1)
            
            # 获取所有联系人（从底部到顶部）
            contacts = target_frame.evaluate('''() => {
                const results = [];
                const items = document.querySelectorAll('.conversation-item');
                items.forEach((item, index) => {
                    const nameEl = item.querySelector('.name');
                    const msgEl = item.querySelector('.message, [class*="message"]');
                    const timeEl = item.querySelector('.time, [class*="time"]');
                    
                    if (nameEl) {
                        const name = nameEl.innerText.trim();
                        const lastMsg = msgEl ? msgEl.innerText.trim() : '';
                        const timeText = timeEl ? timeEl.innerText.trim() : '';
                        
                        if (name && name !== 'Unknown' && name.length > 0) {
                            results.push({
                                index: index,
                                name: name,
                                lastMsg: lastMsg,
                                time: timeText
                            });
                        }
                    }
                });
                return results;
            }''')
            
            # 反转列表，从最后一个开始
            contacts.reverse()
            
            safe_print(f"找到 {len(contacts)} 个联系人")
            safe_print("="*60)
            
            synced_count = 0
            
            # 从最后一个（现在在列表开头）到第一个逐个处理
            for i, contact in enumerate(contacts, 1):
                name = contact['name']
                last_msg = contact['lastMsg']
                time_text = contact['time']
                
                safe_print(f"\n[{i}/{len(contacts)}] 处理: {name[:40]}")
                safe_print(f"  时间: {time_text}")
                safe_print(f"  预览: {last_msg[:50] if last_msg else '无'}")
                
                try:
                    # 点击联系人
                    clicked = target_frame.evaluate(f'''
                        (contactName) => {{
                            const items = document.querySelectorAll('.conversation-item');
                            for (const item of items) {{
                                const nameEl = item.querySelector('.name');
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
                        time.sleep(4)
                        
                        # 截图验证
                        screenshot_file = f'contact_{i:03d}_{name[:20].replace(" ", "_")}.png'
                        wangwang_page.screenshot(path=screenshot_file, full_page=False)
                        safe_print(f"  截图: {screenshot_file}")
                        
                        # 获取对话记录
                        messages = wangwang_page.evaluate('''() => {
                            const results = [];
                            const msgElements = document.querySelectorAll('.message-item, .msg-item, .bubble, [class*="message"]');
                            msgElements.forEach(msg => {
                                const text = msg.innerText || '';
                                if (text.trim() && text.length > 5) {
                                    const className = msg.className || '';
                                    const isMine = className.includes('mine') || className.includes('self') || 
                                                  msg.getAttribute('data-direction') === 'out';
                                    
                                    const exists = results.find(r => r.text === text.substring(0, 200));
                                    if (!exists) {
                                        results.push({
                                            text: text.substring(0, 200),
                                            direction: isMine ? 'out' : 'in'
                                        });
                                    }
                                }
                            });
                            return results.slice(-5);  // 最近5条
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
                            last = messages[-1]
                            direction = "发出" if last['direction'] == 'out' else "收到"
                            text = last['text'][:40]
                            safe_print(f"  最新: [{direction}] {text}")
                    else:
                        safe_print("  点击失败")
                    
                except Exception as e:
                    safe_print(f"  错误: {e}")
                
                # 间隔
                if i < len(contacts):
                    safe_print("  等待3秒...")
                    time.sleep(3)
            
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
            import traceback
            safe_print(traceback.format_exc())
            browser.close()
            return 0

if __name__ == "__main__":
    sync_contacts_one_by_one()
