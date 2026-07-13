#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量同步所有待联系供应商的旺旺回复

功能:
    1. 获取所有待联系供应商列表
    2. 逐一搜索旺旺联系人
    3. 获取最新对话记录
    4. 同步到本地数据库
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json
import time
import subprocess
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

def get_pending_suppliers():
    """获取所有待联系的供应商"""
    db = load_database()
    pending = [s for s in db['suppliers'] if s['status'] == '待联系']
    return pending

def sync_all_pending():
    """同步所有待联系供应商"""
    pending = get_pending_suppliers()
    
    safe_print("="*60)
    safe_print(f"批量同步 {len(pending)} 家待联系供应商")
    safe_print("="*60)
    
    if not pending:
        safe_print("没有待联系的供应商")
        return
    
    success_count = 0
    
    for i, supplier in enumerate(pending[:10], 1):  # 只处理前10家
        name = supplier['name']
        
        safe_print(f"\n[{i}/10] 同步: {name[:40]}")
        safe_print("-"*60)
        
        try:
            # 调用 search_contact_fixed.py
            result = subprocess.run(
                ['python', 'search_contact_fixed.py', '--name', name],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=90
            )
            
            if result.returncode == 0:
                safe_print(f"  ✓ 同步成功")
                success_count += 1
            else:
                safe_print(f"  ✗ 同步失败")
                if result.stderr:
                    safe_print(f"  Error: {result.stderr[:100]}")
            
        except subprocess.TimeoutExpired:
            safe_print(f"  ✗ 超时")
        except Exception as e:
            safe_print(f"  ✗ 错误: {e}")
        
        # 间隔
        if i < 10:
            safe_print("  等待5秒...")
            time.sleep(5)
    
    safe_print("\n" + "="*60)
    safe_print(f"完成: {success_count}/10 家供应商已同步")
    safe_print("="*60)
    
    # 显示统计
    db = load_database()
    status_count = {}
    for s in db['suppliers']:
        status = s['status']
        status_count[status] = status_count.get(status, 0) + 1
    
    safe_print("\n当前状态分布:")
    for status, count in status_count.items():
        safe_print(f"  {status}: {count} 家")

if __name__ == "__main__":
    sync_all_pending()
