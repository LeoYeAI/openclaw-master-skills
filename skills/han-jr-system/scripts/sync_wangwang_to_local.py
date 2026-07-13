#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同步旺旺联系人和对话记录到本地供应商系统

功能:
    1. 从旺旺聊天页面获取所有联系人列表
    2. 获取每个联系人的对话记录
    3. 同步到本地供应商数据库
    4. 更新供应商状态和沟通历史

使用方法:
    python sync_wangwang_to_local.py
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json
import time
import re
from datetime import datetime
from pathlib import Path

DATABASE_FILE = "suppliers_database.json"

def safe_print(text):
    try:
        print(text)
    except:
        print(str(text).encode('utf-8', errors='replace').decode('utf-8', errors='replace'))

def load_database():
    """加载供应商数据库"""
    db_path = Path(DATABASE_FILE)
    if db_path.exists():
        with open(db_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'suppliers': [], 'last_updated': datetime.now().isoformat()}

def save_database(data):
    """保存供应商数据库"""
    data['last_updated'] = datetime.now().isoformat()
    with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def find_or_create_supplier(db, name, link=None):
    """查找或创建供应商"""
    # 先尝试查找
    for s in db['suppliers']:
        if s['name'] == name or (link and s['link'] == link):
            return s
    
    # 创建新供应商
    supplier = {
        'id': len(db['suppliers']) + 1,
        'name': name,
        'product': '帽子',
        'link': link or '',
        'price': 'Unknown',
        'contact': '',
        'notes': '从旺旺同步',
        'status': '待联系',
        'created_at': datetime.now().isoformat(),
        'history': []
    }
    db['suppliers'].append(supplier)
    return supplier

def sync_wangwang_contacts():
    """同步旺旺联系人和对话记录"""
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
                safe_print("请先打开1688消息中心")
                browser.close()
                return 0
            
            safe_print("="*60)
            safe_print("同步旺旺联系人到本地供应商系统")
            safe_print("="*60)
            
            wangwang_page.bring_to_front()
            time.sleep(2)
            
            # 加载数据库
            db = load_database()
            
            # 获取联系人列表
            safe_print("\n获取联系人列表...")
            
            contacts = []
            
            # 尝试多种方式获取联系人
            for frame_idx, frame in enumerate(wangwang_page.frames):
                try:
                    # 查找联系人元素
                    contact_elements = frame.query_selector_all(
                        '.contact-item, .conversation-item, [class*="contact"], [class*="conversation"]'
                    )
                    
                    for elem in contact_elements:
                        try:
                            # 获取联系人名称
                            name_elem = elem.query_selector('.name, [class*="name"], .title, [class*="title"]')
                            name = name_elem.inner_text() if name_elem else 'Unknown'
                            
                            # 获取最后消息
                            msg_elem = elem.query_selector('.message, [class*="message"], .last-msg, [class*="last"]')
                            last_msg = msg_elem.inner_text() if msg_elem else ''
                            
                            # 获取时间
                            time_elem = elem.query_selector('.time, [class*="time"]')
                            msg_time = time_elem.inner_text() if time_elem else ''
                            
                            # 检查是否有未读消息
                            unread_elem = elem.query_selector('.unread, [class*="unread"], .badge, [class*="badge"]')
                            has_unread = unread_elem is not None
                            
                            contacts.append({
                                'name': name.strip(),
                                'last_message': last_msg.strip(),
                                'time': msg_time.strip(),
                                'has_unread': has_unread,
                                'element': elem
                            })
                        except:
                            pass
                except:
                    pass
            
            safe_print(f"找到 {len(contacts)} 个联系人")
            
            if not contacts:
                safe_print("未找到联系人，尝试JavaScript方式获取...")
                
                # 使用JavaScript获取联系人
                contacts_data = wangwang_page.evaluate('''() => {
                    const results = [];
                    const items = document.querySelectorAll('.contact-item, .conversation-item, [class*="contact"], [class*="list-item"]');
                    items.forEach(item => {
                        const nameEl = item.querySelector('.name, [class*="name"]');
                        const msgEl = item.querySelector('.message, [class*="message"]');
                        const timeEl = item.querySelector('.time, [class*="time"]');
                        const unreadEl = item.querySelector('.unread, [class*="unread"]');
                        
                        if (nameEl) {
                            results.push({
                                name: nameEl.innerText.trim(),
                                last_message: msgEl ? msgEl.innerText.trim() : '',
                                time: timeEl ? timeEl.innerText.trim() : '',
                                has_unread: !!unreadEl
                            });
                        }
                    });
                    return results;
                }''')
                
                contacts = contacts_data
                safe_print(f"JavaScript方式找到 {len(contacts)} 个联系人")
            
            # 同步到本地数据库
            synced_count = 0
            
            for contact in contacts:
                name = contact['name']
                last_msg = contact['last_message']
                msg_time = contact['time']
                has_unread = contact['has_unread']
                
                # 查找或创建供应商
                supplier = find_or_create_supplier(db, name)
                
                # 更新状态
                if has_unread:
                    supplier['status'] = '已回复'
                elif last_msg:
                    supplier['status'] = '已联系'
                
                # 添加沟通记录
                if last_msg:
                    # 检查是否已存在相同记录
                    exists = False
                    for h in supplier['history']:
                        if h['message'] == last_msg:
                            exists = True
                            break
                    
                    if not exists:
                        direction = 'in' if has_unread else 'out'
                        supplier['history'].append({
                            'time': datetime.now().isoformat(),
                            'message': last_msg,
                            'direction': direction
                        })
                
                synced_count += 1
                safe_print(f"  ✓ 同步: {name[:30]} - {last_msg[:30] if last_msg else '无消息'}")
            
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
    sync_wangwang_contacts()
