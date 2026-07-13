#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地供应商管理系统

功能:
    1. 记录供应商信息（名称、链接、价格、联系方式等）
    2. 记录沟通历史
    3. 标记供应商状态（待联系、已联系、已回复、已成交等）
    4. 搜索和筛选供应商
    5. 导出供应商列表

数据文件: suppliers_database.json
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
    """加载供应商数据库"""
    db_path = Path(DATABASE_FILE)
    if db_path.exists():
        with open(db_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'suppliers': [],
        'last_updated': datetime.now().isoformat()
    }

def save_database(data):
    """保存供应商数据库"""
    data['last_updated'] = datetime.now().isoformat()
    with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    safe_print(f"✓ 数据库已保存: {DATABASE_FILE}")

def add_supplier(name, product, link, price=None, contact=None, notes=None):
    """添加新供应商"""
    db = load_database()
    
    # 检查是否已存在
    for s in db['suppliers']:
        if s['link'] == link:
            safe_print(f"⚠ 供应商已存在: {name}")
            return False
    
    supplier = {
        'id': len(db['suppliers']) + 1,
        'name': name,
        'product': product,
        'link': link,
        'price': price or 'Unknown',
        'contact': contact or '',
        'notes': notes or '',
        'status': '待联系',
        'created_at': datetime.now().isoformat(),
        'history': []
    }
    
    db['suppliers'].append(supplier)
    save_database(db)
    safe_print(f"✓ 已添加供应商: {name}")
    return True

def update_supplier(supplier_id, **kwargs):
    """更新供应商信息"""
    db = load_database()
    
    for s in db['suppliers']:
        if s['id'] == supplier_id:
            for key, value in kwargs.items():
                if key in s:
                    s[key] = value
            save_database(db)
            safe_print(f"✓ 已更新供应商 ID {supplier_id}")
            return True
    
    safe_print(f"✗ 未找到供应商 ID {supplier_id}")
    return False

def add_communication(supplier_id, message, direction='out'):
    """添加沟通记录"""
    db = load_database()
    
    for s in db['suppliers']:
        if s['id'] == supplier_id:
            record = {
                'time': datetime.now().isoformat(),
                'message': message,
                'direction': direction  # 'out' 发出, 'in' 收到
            }
            s['history'].append(record)
            
            # 更新状态
            if direction == 'out':
                s['status'] = '已联系'
            else:
                s['status'] = '已回复'
            
            save_database(db)
            safe_print(f"✓ 已添加沟通记录到供应商 ID {supplier_id}")
            return True
    
    safe_print(f"✗ 未找到供应商 ID {supplier_id}")
    return False

def list_suppliers(status=None, product=None):
    """列出供应商"""
    db = load_database()
    suppliers = db['suppliers']
    
    # 筛选
    if status:
        suppliers = [s for s in suppliers if s['status'] == status]
    if product:
        suppliers = [s for s in suppliers if product.lower() in s['product'].lower()]
    
    safe_print("="*80)
    safe_print(f"供应商列表 (共 {len(suppliers)} 家)")
    safe_print("="*80)
    
    for s in suppliers:
        safe_print(f"\n[{s['id']}] {s['name']}")
        safe_print(f"    产品: {s['product']}")
        safe_print(f"    价格: {s['price']}")
        safe_print(f"    状态: {s['status']}")
        safe_print(f"    链接: {s['link'][:50]}...")
        if s['history']:
            safe_print(f"    沟通记录: {len(s['history'])} 条")
    
    safe_print("\n" + "="*80)
    return suppliers

def get_supplier(supplier_id):
    """获取单个供应商详情"""
    db = load_database()
    
    for s in db['suppliers']:
        if s['id'] == supplier_id:
            safe_print("="*80)
            safe_print(f"供应商详情 [{s['id']}]")
            safe_print("="*80)
            safe_print(f"名称: {s['name']}")
            safe_print(f"产品: {s['product']}")
            safe_print(f"价格: {s['price']}")
            safe_print(f"联系方式: {s['contact']}")
            safe_print(f"状态: {s['status']}")
            safe_print(f"链接: {s['link']}")
            safe_print(f"备注: {s['notes']}")
            safe_print(f"创建时间: {s['created_at']}")
            
            if s['history']:
                safe_print("\n沟通历史:")
                for h in s['history']:
                    direction = "→ 发出" if h['direction'] == 'out' else "← 收到"
                    safe_print(f"  [{h['time'][:16]}] {direction}: {h['message'][:50]}")
            
            safe_print("="*80)
            return s
    
    safe_print(f"✗ 未找到供应商 ID {supplier_id}")
    return None

def delete_supplier(supplier_id):
    """删除供应商"""
    db = load_database()
    
    for i, s in enumerate(db['suppliers']):
        if s['id'] == supplier_id:
            del db['suppliers'][i]
            save_database(db)
            safe_print(f"✓ 已删除供应商 ID {supplier_id}")
            return True
    
    safe_print(f"✗ 未找到供应商 ID {supplier_id}")
    return False

def export_suppliers(filename='suppliers_export.json'):
    """导出供应商列表"""
    db = load_database()
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    safe_print(f"✓ 已导出到: {filename}")

def import_from_search_results():
    """从搜索结果导入供应商"""
    result_files = [
        'results/棒球帽.json',
        'results/棒球帽定制.json',
        'results/鸭舌帽刺绣.json'
    ]
    
    imported = 0
    for file in result_files:
        path = Path(file)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for item in data:
                name = item.get('name', 'Unknown')
                link = item.get('link', '')
                price = item.get('price', 'Unknown')
                
                # 从产品名称推断产品类型
                product = '帽子'
                if '棒球' in name:
                    product = '棒球帽'
                elif '鸭舌' in name:
                    product = '鸭舌帽'
                
                if add_supplier(name, product, link, price):
                    imported += 1
    
    safe_print(f"\n✓ 共导入 {imported} 家供应商")

def show_statistics():
    """显示统计信息"""
    db = load_database()
    suppliers = db['suppliers']
    
    safe_print("="*60)
    safe_print("供应商统计")
    safe_print("="*60)
    safe_print(f"总供应商数: {len(suppliers)}")
    
    # 按状态统计
    status_count = {}
    for s in suppliers:
        status = s['status']
        status_count[status] = status_count.get(status, 0) + 1
    
    safe_print("\n按状态分布:")
    for status, count in status_count.items():
        safe_print(f"  {status}: {count} 家")
    
    # 按产品统计
    product_count = {}
    for s in suppliers:
        product = s['product']
        product_count[product] = product_count.get(product, 0) + 1
    
    safe_print("\n按产品分布:")
    for product, count in product_count.items():
        safe_print(f"  {product}: {count} 家")
    
    safe_print("="*60)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='本地供应商管理系统',
        epilog='''
示例:
  # 添加供应商
  python supplier_manager.py add --name "XXX公司" --product "棒球帽" --link "http://..."
  
  # 列出所有供应商
  python supplier_manager.py list
  
  # 列出已回复的供应商
  python supplier_manager.py list --status 已回复
  
  # 查看供应商详情
  python supplier_manager.py get --id 1
  
  # 添加沟通记录
  python supplier_manager.py communicate --id 1 --message "已回复，价格OK"
  
  # 从搜索结果导入
  python supplier_manager.py import
  
  # 显示统计
  python supplier_manager.py stats
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # add 命令
    add_parser = subparsers.add_parser('add', help='添加供应商')
    add_parser.add_argument('--name', required=True, help='供应商名称')
    add_parser.add_argument('--product', required=True, help='产品类型')
    add_parser.add_argument('--link', required=True, help='店铺链接')
    add_parser.add_argument('--price', help='价格')
    add_parser.add_argument('--contact', help='联系方式')
    add_parser.add_argument('--notes', help='备注')
    
    # list 命令
    list_parser = subparsers.add_parser('list', help='列出供应商')
    list_parser.add_argument('--status', help='按状态筛选')
    list_parser.add_argument('--product', help='按产品筛选')
    
    # get 命令
    get_parser = subparsers.add_parser('get', help='查看供应商详情')
    get_parser.add_argument('--id', type=int, required=True, help='供应商ID')
    
    # communicate 命令
    comm_parser = subparsers.add_parser('communicate', help='添加沟通记录')
    comm_parser.add_argument('--id', type=int, required=True, help='供应商ID')
    comm_parser.add_argument('--message', required=True, help='消息内容')
    comm_parser.add_argument('--direction', choices=['out', 'in'], default='out', help='方向')
    
    # update 命令
    update_parser = subparsers.add_parser('update', help='更新供应商')
    update_parser.add_argument('--id', type=int, required=True, help='供应商ID')
    update_parser.add_argument('--status', help='状态')
    update_parser.add_argument('--price', help='价格')
    update_parser.add_argument('--contact', help='联系方式')
    update_parser.add_argument('--notes', help='备注')
    
    # delete 命令
    delete_parser = subparsers.add_parser('delete', help='删除供应商')
    delete_parser.add_argument('--id', type=int, required=True, help='供应商ID')
    
    # import 命令
    subparsers.add_parser('import', help='从搜索结果导入')
    
    # stats 命令
    subparsers.add_parser('stats', help='显示统计')
    
    # export 命令
    export_parser = subparsers.add_parser('export', help='导出供应商')
    export_parser.add_argument('--file', default='suppliers_export.json', help='文件名')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'add':
        add_supplier(args.name, args.product, args.link, args.price, args.contact, args.notes)
    elif args.command == 'list':
        list_suppliers(args.status, args.product)
    elif args.command == 'get':
        get_supplier(args.id)
    elif args.command == 'communicate':
        add_communication(args.id, args.message, args.direction)
    elif args.command == 'update':
        kwargs = {}
        if args.status:
            kwargs['status'] = args.status
        if args.price:
            kwargs['price'] = args.price
        if args.contact:
            kwargs['contact'] = args.contact
        if args.notes:
            kwargs['notes'] = args.notes
        update_supplier(args.id, **kwargs)
    elif args.command == 'delete':
        delete_supplier(args.id)
    elif args.command == 'import':
        import_from_search_results()
    elif args.command == 'stats':
        show_statistics()
    elif args.command == 'export':
        export_suppliers(args.file)

if __name__ == "__main__":
    main()
