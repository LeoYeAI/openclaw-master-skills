#!/usr/bin/env python3
"""
命令解析脚本
用于解析用户的自然语言命令并调用股票订单管理功能
"""

import os
import sys
import json
from datetime import datetime
from stock_order import StockOrderManager
from stock_info import StockInfoFetcher

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def parse_command(command):
    """解析用户命令
    
    Args:
        command: 用户输入的命令字符串
    
    Returns:
        tuple: (action, params) - 动作名称和参数
    """
    command = command.strip()
    
    # 处理添加订单命令
    if command.startswith('保存股票订单'):
        parts = command.split()
        if len(parts) >= 5:
            stock_code = parts[1]
            stock_name = parts[2]
            buy_price = float(parts[3])
            stock_type = parts[4]
            buy_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            return 'add_stock_order', {
                'stock_code': stock_code,
                'stock_name': stock_name,
                'buy_time': buy_time,
                'buy_price': buy_price,
                'stock_type': stock_type
            }
    
    # 处理查看订单命令
    elif command.startswith('查看股票订单'):
        parts = command.split()
        params = {}
        if len(parts) == 4:
            # 查看股票订单 持有
            # 查看股票订单 A股
            if parts[3] in ['持有', '已卖出', '已止损']:
                params['status'] = parts[3]
            else:
                params['stock_type'] = parts[3]
        elif len(parts) == 5:
            # 查看股票订单 持有 A股
            params['status'] = parts[3]
            params['stock_type'] = parts[4]
        return 'list_stock_orders', params
    
    # 处理查看订单详情命令
    elif command.startswith('查看订单详情'):
        parts = command.split()
        if len(parts) == 4:
            order_id = parts[3]
            return 'get_stock_order', {'order_id': order_id}
    
    # 处理更新订单状态命令
    elif command.startswith('更新订单状态'):
        parts = command.split()
        if len(parts) == 5:
            order_id = parts[3]
            status = parts[4]
            return 'update_stock_order_status', {
                'order_id': order_id,
                'status': status
            }
    
    # 处理删除订单命令
    elif command.startswith('删除订单'):
        parts = command.split()
        if len(parts) == 3:
            order_id = parts[2]
            return 'delete_stock_order', {'order_id': order_id}
    
    # 处理获取股票信息命令
    elif command.startswith('获取股票信息'):
        parts = command.split()
        if len(parts) == 3:
            stock_code = parts[2]
            return 'get_stock_info', {'stock_code': stock_code}
    
    return None, None

def execute_action(action, params):
    """执行动作
    
    Args:
        action: 动作名称
        params: 动作参数
    
    Returns:
        dict: 执行结果
    """
    try:
        order_manager = StockOrderManager()
        
        if action == 'add_stock_order':
            order_id = order_manager.add_order(
                stock_code=params['stock_code'],
                stock_name=params['stock_name'],
                buy_time=params['buy_time'],
                buy_price=params['buy_price'],
                stock_type=params['stock_type']
            )
            return {
                "success": True,
                "message": f"成功添加订单，订单ID: {order_id}",
                "order_id": order_id
            }
        
        elif action == 'list_stock_orders':
            orders = order_manager.get_all_orders()
            
            # 按状态筛选
            if 'status' in params:
                orders = [order for order in orders if order['status'] == params['status']]
            
            # 按股票类型筛选
            if 'stock_type' in params:
                orders = [order for order in orders if order['stock_type'] == params['stock_type']]
            
            return {
                "success": True,
                "message": f"成功获取 {len(orders)} 个订单",
                "orders": orders
            }
        
        elif action == 'get_stock_order':
            order = order_manager.get_order_by_id(params['order_id'])
            if order:
                return {
                    "success": True,
                    "message": "成功获取订单详情",
                    "order": order
                }
            else:
                return {
                    "success": False,
                    "message": f"未找到订单: {params['order_id']}"
                }
        
        elif action == 'update_stock_order_status':
            success = order_manager.update_order_status(params['order_id'], params['status'])
            if success:
                return {
                    "success": True,
                    "message": f"成功更新订单状态: {params['order_id']} -> {params['status']}"
                }
            else:
                return {
                    "success": False,
                    "message": f"更新订单状态失败: {params['order_id']}"
                }
        
        elif action == 'delete_stock_order':
            success = order_manager.delete_order(params['order_id'])
            if success:
                return {
                    "success": True,
                    "message": f"成功删除订单: {params['order_id']}"
                }
            else:
                return {
                    "success": False,
                    "message": f"删除订单失败: {params['order_id']}"
                }
        
        elif action == 'get_stock_info':
            fetcher = StockInfoFetcher()
            stock_info = fetcher.fetch_and_save_stock_info(params['stock_code'])
            if stock_info:
                return {
                    "success": True,
                    "message": f"成功获取股票 {stock_info['code']} ({stock_info['name']}) 信息",
                    "stock_info": stock_info
                }
            else:
                return {
                    "success": False,
                    "message": f"获取股票 {params['stock_code']} 信息失败"
                }
        
        else:
            return {
                "success": False,
                "message": f"未知动作: {action}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"执行动作失败: {str(e)}"
        }

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage: python command_parser.py <command>")
        sys.exit(1)
    
    command = ' '.join(sys.argv[1:])
    action, params = parse_command(command)
    
    if action:
        result = execute_action(action, params)
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(json.dumps({
            "success": False,
            "message": f"无法解析命令: {command}"
        }, ensure_ascii=False))

if __name__ == "__main__":
    main()