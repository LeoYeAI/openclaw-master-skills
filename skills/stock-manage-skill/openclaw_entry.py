#!/usr/bin/env python3
"""
OpenClaw 入口脚本
用于处理 OpenClaw 的请求并调用股票订单管理功能
"""

import os
import sys
import json
from stock_order import StockOrderManager
from stock_info import StockInfoFetcher

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime

def handle_add_stock_order(params):
    """处理添加股票订单请求"""
    try:
        order_manager = StockOrderManager()
        # 自动生成当前时间作为买入时间（如果未提供）
        buy_time = params.get('buy_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        order_id = order_manager.add_order(
            stock_code=params['stock_code'],
            stock_name=params['stock_name'],
            buy_time=buy_time,
            buy_price=params['buy_price'],
            stock_type=params.get('stock_type', 'A股')
        )
        return {
            "success": True,
            "message": f"成功添加订单，订单ID: {order_id}",
            "order_id": order_id
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"添加订单失败: {str(e)}"
        }

def handle_list_stock_orders(params):
    """处理列出股票订单请求"""
    try:
        order_manager = StockOrderManager()
        orders = order_manager.get_all_orders()
        
        # 按状态筛选
        if 'status' in params and params['status']:
            orders = [order for order in orders if order['status'] == params['status']]
        
        # 按股票类型筛选
        if 'stock_type' in params and params['stock_type']:
            orders = [order for order in orders if order['stock_type'] == params['stock_type']]
        
        return {
            "success": True,
            "message": f"成功获取 {len(orders)} 个订单",
            "orders": orders
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"获取订单失败: {str(e)}"
        }

def handle_get_stock_order(params):
    """处理获取股票订单详情请求"""
    try:
        order_manager = StockOrderManager()
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
    except Exception as e:
        return {
            "success": False,
            "message": f"获取订单详情失败: {str(e)}"
        }

def handle_update_stock_order_status(params):
    """处理更新股票订单状态请求"""
    try:
        order_manager = StockOrderManager()
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
    except Exception as e:
        return {
            "success": False,
            "message": f"更新订单状态失败: {str(e)}"
        }

def handle_delete_stock_order(params):
    """处理删除股票订单请求"""
    try:
        order_manager = StockOrderManager()
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
    except Exception as e:
        return {
            "success": False,
            "message": f"删除订单失败: {str(e)}"
        }

def handle_get_stock_info(params):
    """处理获取股票信息请求"""
    try:
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
    except Exception as e:
        return {
            "success": False,
            "message": f"获取股票信息失败: {str(e)}"
        }

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage: python openclaw_entry.py <action> <params>")
        sys.exit(1)
    
    action = sys.argv[1]
    params = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    
    handlers = {
        'add_stock_order': handle_add_stock_order,
        'list_stock_orders': handle_list_stock_orders,
        'get_stock_order': handle_get_stock_order,
        'update_stock_order_status': handle_update_stock_order_status,
        'delete_stock_order': handle_delete_stock_order,
        'get_stock_info': handle_get_stock_info
    }
    
    if action in handlers:
        result = handlers[action](params)
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(json.dumps({
            "success": False,
            "message": f"未知操作: {action}"
        }, ensure_ascii=False))

if __name__ == "__main__":
    main()