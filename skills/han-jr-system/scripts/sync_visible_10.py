#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动同步可见的10家联系人

根据截图，左侧可见的联系人：
1. 询报价助理小慧
2. 平阳县云祥文具厂
3. michael18069958551
4. headgear24
5. 东莞宝瑞森
6. 洛阳扬鑫针织
7. 贝发集团股份有限公司
8. 光板帽业
9. 义乌嘉闻文具
10. 温州市佐澜哲文具有限公司
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json
import time
from datetime import datetime
from pathlib import Path

DATABASE_FILE = "suppliers_database.json"

# 截图中可见的10家联系人
VISIBLE_CONTACTS = [
    "询报价助理小慧",
    "平阳县云祥文具厂",
    "michael18069958551",
    "headgear24",
    "东莞宝瑞森",
    "洛阳扬鑫针织",
    "贝发集团股份有限公司",
    "光板帽业",
    "义乌嘉闻文具",
    "温州市佐澜哲文具有限公司"
]

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

def sync_visible_contacts():
    """同步截图中可见的10家联系人"""
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
            safe_print("同步截图中可见的10家联系人")
            safe_print("="*60)
            
            wangwang_page.bring_to_front()
            time.sleep(2)
            
            db = load_database()
            
            synced_count = 0
            
            for i, name in enumerate(VISIBLE_CONTACTS, 1):
                safe_print(f"\n[{i}/10] {name}")
                
                try:
                    # 使用JavaScript点击联系人
                    clicked = wangwang_page.evaluate(f'''
                        (contactName) => {{
                            // 查找所有可能包含联系人的元素
                            const allElements = document.querySelectorAll('*');
                            for (const el of allElements) {{
                                if (el.textContent && el.textContent.includes(contactName)) {{
                                    // 找到包含该文本的元素，向上查找可点击的父元素
                                    let clickable = el;
                                    while (clickable && !clickable.classList.contains('conversation-item')) {{
                                        clickable = clickable.parentElement;
                                        if (!clickable) break;
                                    }}
                                    if (clickable) {{
                                        clickable.click();
                                        return true;
                                    }}
                                }}
                            }}
                            return false;
                        }}
                    ''', name)
                    
                    if clicked:
                        safe_print("  已点击，等待加载...")
                        time.sleep(3)
                        
                        # 截图验证
                        screenshot_file = f'visible_{i:02d}_{name[:15].replace(" ", "_")}.png'
                        wangwang_page.screenshot(path=screenshot_file, full_page=False)
                        safe_print(f"  截图: {screenshot_file}")
                        
                        # 获取对话
                        messages = wangwang_page.evaluate('''() => {
                            const results = [];
                            const msgElements = document.querySelectorAll('.message-item, .msg-item, .bubble, [class*="message"]');
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
                            return results.slice(-5);
                        }''')
                        
                        safe_print(f"  获取到 {len(messages)} 条消息")
                        
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
                        safe_print(f"  ✓ 同步完成")
                    else:
                        safe_print("  ✗ 点击失败")
                    
                except Exception as e:
                    safe_print(f"  ✗ 错误: {e}")
                
                if i < 10:
                    time.sleep(2)
            
            # 保存数据库
            save_database(db)
            
            safe_print("\n" + "="*60)
            safe_print(f"完成: 同步 {synced_count}/10 家")
            safe_print(f"数据库现在共有 {len(db['suppliers'])} 家供应商")
            safe_print("="*60)
            
            browser.close()
            return synced_count
            
        except Exception as e:
            safe_print(f"错误: {e}")
            browser.close()
            return 0

if __name__ == "__main__":
    sync_visible_contacts()
