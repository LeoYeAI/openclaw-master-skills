#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from pathlib import Path

# 重置供应商数据库
db_file = Path('suppliers_database.json')
if db_file.exists():
    with open(db_file, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    # 清除所有沟通记录，重置状态为待联系
    for s in db['suppliers']:
        s['history'] = []
        s['status'] = '待联系'
    
    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    
    print('Database reset complete')
else:
    print('数据库文件不存在')
