#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜索旺旺联系人并查看最新信息

流程:
    1. 在搜索框输入供应商名称
    2. 点击第一个联系人
    3. 获取最新对话记录
    4. 同步到本地数据库

重要:
    - 搜索框选择器: input[placeholder="搜索联系人"]
    - 输入后等待搜索结果
    - 点击第一个联系人
    - 在Frame 1中获取对话记录
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

def find_supplier(db, name):
    for s in db['suppliers']:
        if s['name'] == name:
            return s
    return None

def search_and_get_chat(supplier_name):
    """搜索供应商并获取最新对话"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        safe_print("Error: pip install playwright")
        return None
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception as e:
            safe_print(f"Error: Cannot connect to Chrome: {e}")
            return None
        
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
                return None
            
            safe_print("="*60)
            safe_print(f"搜索供应商: {supplier_name}")
            safe_print("="*60)
            
            wangwang_page.bring_to_front()
            time.sleep(2)
            
            # 步骤1: 找到搜索框并输入供应商名称
            safe_print("\n步骤1: 在搜索框输入供应商名称...")
            
            search_input = None
            for frame in wangwang_page.frames:
                try:
                    inp = frame.locator('input[placeholder="搜索联系人"]').first
                    if inp.is_visible():
                        search_input = inp
                        safe_print("  找到搜索框")
                        break
                except:
                    pass
            
            if not search_input:
                safe_print("  未找到搜索框，尝试JavaScript...")
                # 使用JavaScript查找
                wangwang_page.evaluate(f'''
                    () => {{
                        const input = document.querySelector('input[placeholder="搜索联系人"]');
                        if (input) {{
                            input.value = "{supplier_name}";
                            input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            return true;
                        }}
                        return false;
                    }}
                ''')
            else:
                # 使用Playwright输入
                search_input.fill("")
                search_input.fill(supplier_name)
                safe_print(f"  已输入: {supplier_name}")
            
            time.sleep(2)  # 等待搜索结果
            
            # 步骤2: 点击第一个联系人
            safe_print("\n步骤2: 点击第一个联系人...")
            
            clicked = wangwang_page.evaluate(f'''
                () => {{
                    // 查找包含供应商名称的第一个联系人
                    const contacts = document.querySelectorAll('.contact-item, .conversation-item, [class*="contact"], [class*="list-item"]');
                    for (const contact of contacts) {{
                        const nameEl = contact.querySelector('.name, [class*="name"]');
                        if (nameEl && nameEl.innerText.includes("{supplier_name}")) {{
                            contact.click();
                            return nameEl.innerText.trim();
                        }}
                    }}
                    // 如果没找到匹配的，点击第一个
                    if (contacts.length > 0) {{
                        contacts[0].click();
                        const firstName = contacts[0].querySelector('.name, [class*="name"]');
                        return firstName ? firstName.innerText.trim() : 'Unknown';
                    }}
                    return null;
                }}
            ''')
            
            if clicked:
                safe_print(f"  已点击联系人: {clicked}")
            else:
                safe_print("  未找到联系人")
                browser.close()
                return None
            
            time.sleep(3)  # 等待聊天内容加载
            
            # 步骤3: 获取对话记录
            safe_print("\n步骤3: 获取对话记录...")
            
            messages = []
            for frame_idx, frame in enumerate(wangwang_page.frames):
                try:
                    msg_elements = frame.query_selector_all('.message-item, .msg-item, [class*="message"], [class*="bubble"]')
                    
                    for msg in msg_elements[-10:]:  # 最近10条
                        try:
                            text = msg.inner_text() or ""
                            if text.strip():
                                # 判断方向
                                is_mine = msg.evaluate('el => el.classList.contains("mine") || el.classList.contains("self")')
                                messages.append({
                                    'text': text[:200],
                                    'direction': 'out' if is_mine else 'in'
                                })
                        except:
                            pass
                except:
                    pass
            
            safe_print(f"  获取到 {len(messages)} 条消息")
            
            if messages:
                safe_print("\n  最新消息:")
                for msg in messages[-5:]:
                    direction = "→" if msg['direction'] == 'out' else "←"
                    safe_print(f"    {direction} {msg['text'][:60]}")
            
            # 步骤4: 同步到数据库
            safe_print("\n步骤4: 同步到本地数据库...")
            
            db = load_database()
            supplier = find_supplier(db, supplier_name)
            
            if supplier:
                # 更新状态
                has_reply = any(m['direction'] == 'in' for m in messages)
                if has_reply:
                    supplier['status'] = '已回复'
                elif messages:
                    supplier['status'] = '已联系'
                
                # 添加新消息
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
                
                save_database(db)
                safe_print(f"  ✓ 已同步到供应商: {supplier_name}")
            else:
                safe_print(f"  ⚠ 本地数据库中未找到供应商: {supplier_name}")
            
            browser.close()
            return messages
            
        except Exception as e:
            safe_print(f"Error: {e}")
            import traceback
            safe_print(traceback.format_exc())
            browser.close()
            return None

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='搜索旺旺联系人并查看最新信息')
    parser.add_argument('--name', '-n', required=True, help='供应商名称')
    args = parser.parse_args()
    
    search_and_get_chat(args.name)
