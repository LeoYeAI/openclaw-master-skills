#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从截图中提取的联系人信息，手动同步到供应商系统
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json
from datetime import datetime
from pathlib import Path

DATABASE_FILE = "suppliers_database.json"

# 从截图中提取的联系人信息
CONTACTS_FROM_SCREENSHOT = [
    {"name": "平阳县云祥文具厂", "last_msg": "[图片]", "time": "20分钟前", "has_unread": True},
    {"name": "michael18069958551", "last_msg": "新消息", "time": "6小时前", "has_unread": True},
    {"name": "headgear24", "last_msg": "", "time": "7小时前", "has_unread": False},
    {"name": "东莞宝瑞森", "last_msg": "价格OK吗？有什么问题直接联系我们", "time": "8小时前", "has_unread": True},
    {"name": "洛阳扬鑫针织", "last_msg": "您好", "time": "6小时前", "has_unread": True},
    {"name": "贝发集团股份有限公司", "last_msg": "", "time": "9小时前", "has_unread": False},
    {"name": "光板帽业", "last_msg": "", "time": "9小时前", "has_unread": False},
    {"name": "义乌嘉闻文具", "last_msg": "", "time": "9小时前", "has_unread": False},
    {"name": "温州市佐澜哲文具有限公司", "last_msg": "亲，还有什么问题可以帮助到您的吗？", "time": "6小时前", "has_unread": True},
    {"name": "温州笔墨方舟", "last_msg": "[图片消息]", "time": "10小时前", "has_unread": True},
]

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

def sync_from_screenshot():
    print("="*60)
    print("从旺旺截图同步联系人到本地供应商系统")
    print("="*60)
    
    db = load_database()
    
    print(f"\n找到 {len(CONTACTS_FROM_SCREENSHOT)} 个联系人")
    print("="*60)
    
    for contact in CONTACTS_FROM_SCREENSHOT:
        name = contact['name']
        last_msg = contact['last_msg']
        msg_time = contact['time']
        has_unread = contact['has_unread']
        
        # 查找或创建供应商
        supplier = find_or_create_supplier(db, name)
        
        # 更新状态
        if has_unread and last_msg:
            supplier['status'] = '已回复'
        elif last_msg:
            supplier['status'] = '已联系'
        
        # 添加沟通记录
        if last_msg:
            supplier['history'].append({
                'time': datetime.now().isoformat(),
                'message': f"[{msg_time}] {last_msg}",
                'direction': 'in' if has_unread else 'out'
            })
        
        print(f"\n✓ 同步: {name}")
        print(f"  状态: {supplier['status']}")
        print(f"  消息: {last_msg[:50] if last_msg else '无'}")
    
    # 保存数据库
    save_database(db)
    
    print("\n" + "="*60)
    print(f"同步完成: {len(CONTACTS_FROM_SCREENSHOT)} 个联系人")
    print(f"数据库现在共有 {len(db['suppliers'])} 家供应商")
    print("="*60)

if __name__ == "__main__":
    sync_from_screenshot()
