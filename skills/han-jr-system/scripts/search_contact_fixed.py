#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜索旺旺联系人并查看最新信息 - 修复版

流程:
    1. 在搜索框输入供应商名称
    2. 按 Enter 触发搜索
    3. 等待搜索结果
    4. 点击第一个联系人（确保点击正确元素）
    5. 等待聊天内容加载（增加等待时间）
    6. 获取最新对话记录

重要修复:
    - 点击联系人后增加等待时间（5秒）
    - 使用 bring_to_front() 确保页面激活
    - 添加重试机制
    - 截图验证每一步
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

def search_contact_and_get_chat(supplier_name):
    """搜索联系人并获取对话"""
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
                safe_print("Wangwang chat page not found")
                browser.close()
                return None
            
            safe_print("="*60)
            safe_print(f"Search supplier: {supplier_name}")
            safe_print("="*60)
            
            # 确保页面在最前面
            wangwang_page.bring_to_front()
            time.sleep(2)
            
            # 截图初始状态
            wangwang_page.screenshot(path='step0_initial.png', full_page=False)
            
            # 步骤1: 在搜索框输入供应商名称
            safe_print("\nStep 1: Enter supplier name in search box...")
            
            search_input = None
            for frame in wangwang_page.frames:
                try:
                    inp = frame.locator('input.ant-input').first
                    if inp.is_visible():
                        placeholder = inp.get_attribute('placeholder') or ''
                        if '搜索' in placeholder:
                            search_input = inp
                            safe_print(f"  Found search box (placeholder: {placeholder})")
                            break
                except:
                    pass
            
            if not search_input:
                safe_print("  Search box not found")
                browser.close()
                return None
            
            # 清空并输入
            search_input.fill("")
            time.sleep(0.5)
            search_input.fill(supplier_name)
            safe_print(f"  Input: {supplier_name}")
            
            # 截图输入后
            wangwang_page.screenshot(path='step1_input.png', full_page=False)
            
            # 步骤2: 按 Enter 触发搜索
            safe_print("\nStep 2: Press Enter to search...")
            search_input.press("Enter")
            safe_print("  Enter pressed")
            
            # 等待搜索结果加载（增加等待时间）
            safe_print("  Waiting for search results...")
            time.sleep(4)
            
            # 截图搜索结果
            wangwang_page.screenshot(path='step2_search_results.png', full_page=False)
            safe_print("  Screenshot: step2_search_results.png")
            
            # 步骤3: 点击第一个联系人
            safe_print("\nStep 3: Click first contact...")
            
            clicked = False
            clicked_name = ""
            
            # 尝试多种方式查找和点击联系人
            for attempt in range(3):  # 重试3次
                if clicked:
                    break
                
                for frame in wangwang_page.frames:
                    try:
                        # 方式1: 查找匹配的联系人
                        contacts = frame.query_selector_all('.contact-item, .conversation-item, [class*="contact"]')
                        
                        for contact in contacts:
                            try:
                                name_el = contact.query_selector('.name, [class*="name"]')
                                if name_el:
                                    name_text = name_el.inner_text() or ''
                                    if supplier_name in name_text:
                                        # 滚动到可见
                                        contact.scroll_into_view_if_needed()
                                        time.sleep(0.5)
                                        # 点击
                                        contact.click()
                                        clicked_name = name_text
                                        clicked = True
                                        break
                            except:
                                pass
                        
                        if clicked:
                            break
                        
                        # 方式2: 如果没找到匹配的，点击第一个可见的
                        if not clicked and len(contacts) > 0:
                            for contact in contacts:
                                try:
                                    if contact.is_visible():
                                        contact.scroll_into_view_if_needed()
                                        time.sleep(0.5)
                                        contact.click()
                                        name_el = contact.query_selector('.name')
                                        clicked_name = name_el.inner_text() if name_el else "First contact"
                                        clicked = True
                                        break
                                except:
                                    pass
                        
                        if clicked:
                            break
                            
                    except Exception as e:
                        pass
                
                if not clicked:
                    safe_print(f"  Retry {attempt + 1}/3...")
                    time.sleep(2)
            
            if not clicked:
                safe_print("  Failed to click contact after 3 attempts")
                browser.close()
                return None
            
            safe_print(f"  Clicked: {clicked_name}")
            
            # 截图点击后
            wangwang_page.screenshot(path='step3_clicked.png', full_page=False)
            
            # 等待聊天内容加载（增加等待时间到5秒）
            safe_print("  Waiting for chat to load...")
            time.sleep(5)
            
            # 确保页面激活
            wangwang_page.bring_to_front()
            time.sleep(1)
            
            # 截图聊天加载后
            wangwang_page.screenshot(path='step4_chat_loaded.png', full_page=False)
            safe_print("  Screenshot: step4_chat_loaded.png")
            
            # 步骤4: 获取对话记录
            safe_print("\nStep 4: Get chat history...")
            
            messages = []
            
            # 在多个frames中查找消息
            for frame_idx, frame in enumerate(wangwang_page.frames):
                try:
                    # 查找消息气泡（多种选择器）
                    msg_selectors = [
                        '.message-item',
                        '.msg-item',
                        '.bubble',
                        '[class*="message"]',
                        '[class*="bubble"]'
                    ]
                    
                    for selector in msg_selectors:
                        msg_elements = frame.query_selector_all(selector)
                        
                        for msg in msg_elements:
                            try:
                                text = msg.inner_text() or ""
                                if text.strip() and len(text) > 5:
                                    # 判断方向
                                    class_name = msg.get_attribute('class') or ''
                                    is_mine = 'mine' in class_name or 'self' in class_name or 'out' in class_name
                                    
                                    # 避免重复
                                    exists = False
                                    for m in messages:
                                        if m['text'] == text[:200]:
                                            exists = True
                                            break
                                    
                                    if not exists:
                                        messages.append({
                                            'text': text[:200],
                                            'direction': 'out' if is_mine else 'in'
                                        })
                            except:
                                pass
                except:
                    pass
            
            # 去重并排序
            safe_print(f"  Found {len(messages)} unique messages")
            
            if messages:
                safe_print("\n  Latest messages:")
                for msg in messages[-5:]:
                    direction = "→ SENT" if msg['direction'] == 'out' else "← RECEIVED"
                    text = msg['text'][:60] if len(msg['text']) > 60 else msg['text']
                    # 只显示第一行
                    text_first_line = text.split('\n')[0]
                    safe_print(f"    {direction}: {text_first_line}")
            
            # 步骤5: 同步到数据库
            safe_print("\nStep 5: Sync to local database...")
            
            db = load_database()
            supplier = find_supplier(db, supplier_name)
            
            if supplier:
                # 更新状态
                has_reply = any(m['direction'] == 'in' for m in messages)
                if has_reply:
                    supplier['status'] = '已回复'
                    safe_print(f"  Status updated: 已回复")
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
                    safe_print(f"  Added {new_count} new messages")
                else:
                    safe_print(f"  No new messages")
                
                save_database(db)
                safe_print(f"  ✓ Synced to supplier: {supplier_name}")
            else:
                safe_print(f"  ⚠ Supplier not found in database: {supplier_name}")
                safe_print(f"  Consider adding supplier first")
            
            # 最终截图
            wangwang_page.screenshot(path='step5_final.png', full_page=False)
            
            safe_print("\n" + "="*60)
            safe_print("Completed successfully!")
            safe_print("="*60)
            
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
    
    parser = argparse.ArgumentParser(description='Search Wangwang contact and get latest chat - Fixed version')
    parser.add_argument('--name', '-n', required=True, help='Supplier name')
    args = parser.parse_args()
    
    search_contact_and_get_chat(args.name)
