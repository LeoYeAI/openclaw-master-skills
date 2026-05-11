#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mx_stock_simulator - 妙想模拟组合管理 skill
支持持仓查询、买卖操作、撤单、委托查询、历史成交查询和资金查询
"""

import os
import sys
import json
import requests
from datetime import datetime

# 环境变量配置
MX_APIKEY = os.environ.get('MX_APIKEY')
MX_API_URL = os.environ.get('MX_API_URL', 'https://mkapi2.dfcfs.com/finskillshub')

# 输出目录配置
OUTPUT_DIR = '/root/.openclaw/workspace/mx_data/output'
PREFIX = 'mx_stock_simulator_'

def check_apikey():
    """检查API Key是否配置"""
    if not MX_APIKEY:
        print("❌ 未找到MX_APIKEY，请设置环境变量：")
        print("   export MX_APIKEY=your_apikey")
        return False
    return True

def ensure_output_dir():
    """确保输出目录存在"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR, exist_ok=True)

def save_result(query, text, data):
    """保存结果到文件"""
    ensure_output_dir()
    safe_query = query.replace(' ', '_')[:50]
    
    # 保存文本结果
    txt_file = os.path.join(OUTPUT_DIR, f"{PREFIX}{safe_query}.txt")
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(text)
    
    # 保存原始JSON
    json_file = os.path.join(OUTPUT_DIR, f"{PREFIX}{safe_query}.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return txt_file, json_file

def make_request(endpoint, payload):
    """发送POST请求到API"""
    url = f"{MX_API_URL}{endpoint}"
    headers = {
        'apikey': MX_APIKEY,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {str(e)}")
        return None

def format_balance(data):
    """格式化资金查询结果"""
    code = data.get('code')
    # 兼容多种成功码: 0, "0", 200, "200"
    if str(code) not in ['0', '200']:
        return f"❌ 查询失败: {data.get('message', '未知错误')}", data
    
    d = data.get('data', data)
    currency_unit = d.get('currencyUnit', 1000)
    
    def to_yuan(val):
        if val is None:
            return '-'
        return f"{val / currency_unit:.2f}"
    
    result = "📊 账户资金信息\n"
    result += "================================================================================\n"
    result += f"总资产:     {to_yuan(d.get('totalAssets'))} 元\n"
    result += f"可用资金:   {to_yuan(d.get('availBalance'))} 元\n"
    result += f"冻结资金:   {to_yuan(d.get('frozenMoney'))} 元\n"
    result += f"持仓市值:   {to_yuan(d.get('totalPosValue'))} 元\n"
    result += f"仓位比例:   {d.get('totalPosPct', '-')}%\n"
    if 'initMoney' in d:
        result += f"初始资金:   {to_yuan(d.get('initMoney'))} 元\n"
    if 'oprDays' in d:
        result += f"运作天数:   {d.get('oprDays')} 天\n"
    if 'nav' in d:
        result += f"单位净值:   {d.get('nav'):.4f}\n"
    result += "================================================================================\n"
    
    return result, data

def format_positions(data):
    """格式化持仓查询结果"""
    code = data.get('code')
    if str(code) not in ['0', '200']:
        return f"❌ 查询失败: {data.get('message', '未知错误')}", data
    
    d = data.get('data', data)
    pos_list = d.get('posList', [])
    currency_unit = d.get('currencyUnit', 1000)
    
    result = "📊 当前持仓\n"
    result += "====================================================================================================\n"
    result += f"{'股票代码':<10} {'股票名称':<10} {'持仓(股)':<10} {'可用(股)':<10} {'现价(元)':<10} {'成本(元)':<10} {'市值(元)':<12} {'当日盈亏':<12} {'持仓盈亏'}\n"
    result += "----------------------------------------------------------------------------------------------------\n"
    
    total_profit = 0
    for pos in pos_list:
        sec_code = pos.get('secCode', '')
        sec_name = pos.get('secName', '')
        count = pos.get('count', 0)
        avail_count = pos.get('availCount', 0)
        price_dec = pos.get('priceDec', 2)
        price = pos.get('price', 0) / (10 ** price_dec)
        cost_dec = pos.get('costPriceDec', 2)
        cost = pos.get('costPrice', 0) / (10 ** cost_dec)
        value = pos.get('value', 0) / currency_unit
        day_profit = pos.get('dayProfit', 0) / currency_unit
        profit = pos.get('profit', 0) / currency_unit
        total_profit += profit
        
        day_profit_str = f"{day_profit:+.2f}"
        profit_str = f"{profit:+.2f}"
        
        result += f"{sec_code:<10} {sec_name:<10} {count:<10} {avail_count:<10} {price:<10.2f} {cost:<10.2f} {value:<12.2f} {day_profit_str:<12} {profit_str}\n"
    
    if not pos_list:
        result += "暂无持仓\n"
    
    result += "----------------------------------------------------------------------------------------------------\n"
    result += f"总持仓盈亏: {total_profit:+.2f} 元\n"
    if d.get('totalAssets'):
        result += f"总资产: {d.get('totalAssets') / currency_unit:.2f} 元\n"
    result += "====================================================================================================\n"
    result += f"共 {len(pos_list)} 只持仓股票\n"
    
    return result, data

def format_orders(data):
    """格式化委托查询结果"""
    code = data.get('code')
    if str(code) not in ['0', '200']:
        return f"❌ 查询失败: {data.get('message', '未知错误')}", data
    
    d = data.get('data', data)
    orders = d.get('orders', [])
    currency_unit = d.get('currencyUnit', 1000)
    
    status_map = {
        1: "未报",
        2: "已报",
        3: "部成",
        4: "已成",
        5: "部成待撤",
        6: "已报待撤",
        7: "部撤",
        8: "已撤",
        9: "废单",
        10: "撤单失败"
    }
    
    drt_map = {
        1: "买入",
        2: "卖出"
    }
    
    result = "📋 委托记录\n"
    result += "====================================================================================================\n"
    result += f"{'订单ID':<14} {'方向':<4} {'股票':<6} {'名称':<8} {'价格':<8} {'数量':<8} {'状态':<6} {'委托时间'}\n"
    result += "----------------------------------------------------------------------------------------------------\n"
    
    if not orders:
        result += "暂无委托记录\n"
    
    for order in orders:
        order_id = order.get('id', '')
        drt = drt_map.get(order.get('drt', 0), '-')
        sec_code = order.get('secCode', '')
        sec_name = order.get('secName', '')
        price_dec = order.get('priceDec', 2)
        price = order.get('price', 0) / (10 ** price_dec)
        count = order.get('count', 0)
        status = status_map.get(order.get('status', 0), '-')
        time_ts = order.get('time', 0)
        time_str = datetime.fromtimestamp(time_ts).strftime('%Y-%m-%d %H:%M:%S') if time_ts else '-'
        
        result += f"{order_id:<14} {drt:<4} {sec_code:<6} {sec_name:<8} {price:<8.2f} {count:<8} {status:<6} {time_str}\n"
    
    result += "====================================================================================================\n"
    result += f"共 {len(orders)} 条委托记录\n"
    
    return result, data

def format_cancel(data):
    """格式化撤单结果"""
    code = data.get('code')
    if str(code) not in ['0', '200']:
        return f"❌ 撤单失败: {data.get('message', '未知错误')}", data
    
    d = data.get('data', data)
    rc = d.get('rc', -1)
    rmsg = d.get('rmsg', '')
    cancel_count = d.get('cancelCount', 0)
    fail_count = d.get('failCount', 0)
    fail_list = d.get('failList', [])
    
    result = "✅ 撤单完成\n"
    result += "================================================================================\n"
    result += f"{rmsg}\n"
    result += f"成功撤单: {cancel_count} 笔\n"
    result += f"撤单失败: {fail_count} 笔\n"
    
    if fail_list:
        result += "失败详情:\n"
        for fail in fail_list:
            result += f"  订单 {fail.get('orderID', '')}: {fail.get('rmsg', '')}\n"
    
    result += "================================================================================\n"
    
    return result, data

def format_trade_result(data):
    """格式化交易结果"""
    code = data.get('code')
    if str(code) not in ['0', '200']:
        return f"❌ 委托失败: {data.get('message', '未知错误')}", data
    
    data = data.get('data', data)
    order_id = data.get('orderId', '')
    status = data.get('status', '')
    
    result = "✅ 委托成功\n"
    result += "================================================================================\n"
    result += f"订单编号: {order_id}\n"
    result += f"状态: {status}\n"
    result += "================================================================================\n"
    
    return result, data

def parse_query(query):
    """解析自然语言查询，识别意图"""
    query = query.lower()
    
    # 意图识别
    if any(word in query for word in ['持仓', '我的持仓', '持仓情况', '查持仓']):
        return 'positions', None
    
    if any(word in query for word in ['资金', '我的资金', '账户余额', '资金情况']):
        return 'balance', None
    
    if any(word in query for word in ['委托', '订单', '成交记录', '历史成交', '交易历史']):
        return 'orders', None
    
    if any(word in query for word in ['撤单', '撤销', '取消', 'cancel']):
        return 'cancel', None
    
    if any(word in query for word in ['买入', 'buy', '买进']):
        return 'buy', parse_trade_params(query, 'buy')
    
    if any(word in query for word in ['卖出', 'sell', '卖掉']):
        return 'sell', parse_trade_params(query, 'sell')
    
    # 默认查询持仓
    return 'positions', None

def parse_trade_params(query, trade_type):
    """解析交易参数"""
    import re
    
    # 提取6位数字股票代码
    codes = re.findall(r'\b(\d{6})\b', query)
    # 提取数字数量
    quantities = re.findall(r'(\d+)\s*(股|手)', query)
    
    stock_code = codes[0] if codes else None
    quantity = int(quantities[0][0]) * (100 if quantities and quantities[0][1] == '手' else 1) if quantities else None
    
    # 提取价格
    prices = re.findall(r'(?:价格|成交价|按|@)\s*(\d+\.?\d*)', query)
    price = float(prices[0]) if prices else None
    
    # 判断是否市价委托
    use_market = any(word in query for word in ['现价', '市价', '最新价', '市场价格'])
    
    return {
        'stock_code': stock_code,
        'quantity': quantity,
        'price': price,
        'use_market_price': use_market
    }

def main():
    """主函数"""
    if not check_apikey():
        sys.exit(1)
    
    # 获取查询文本
    query = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else '查询持仓'
    
    # 解析意图
    intent, params = parse_query(query)
    
    if intent == 'positions':
        # 查询持仓
        data = make_request('/api/claw/mockTrading/positions', {})
        if data is None:
            sys.exit(1)
        result_text, _ = format_positions(data)
        print(result_text)
        save_result(query, result_text, data)
    
    elif intent == 'balance':
        # 查询资金
        data = make_request('/api/claw/mockTrading/balance', {})
        if data is None:
            sys.exit(1)
        result_text, _ = format_balance(data)
        print(result_text)
        save_result(query, result_text, data)
    
    elif intent == 'orders':
        # 查询委托
        data = make_request('/api/claw/mockTrading/orders', {})
        if data is None:
            sys.exit(1)
        result_text, _ = format_orders(data)
        print(result_text)
        save_result(query, result_text, data)
    
    elif intent == 'cancel':
        # 撤单 - 默认一键撤单
        payload = {'type': 'all'}
        data = make_request('/api/claw/mockTrading/cancel', payload)
        if data is None:
            sys.exit(1)
        result_text, _ = format_cancel(data)
        print(result_text)
        save_result(query, result_text, data)
    
    elif intent in ['buy', 'sell']:
        # 买入/卖出 - 使用 /trade 端点
        if not params or not params.get('stock_code'):
            print("❌ 请提供股票代码（6位数字）")
            sys.exit(1)
        if not params.get('quantity'):
            print("❌ 请提供委托数量")
            sys.exit(1)
        
        payload = {
            'type': intent,
            'stockCode': params['stock_code'],
            'quantity': params['quantity'],
            'useMarketPrice': params.get('use_market_price', False)
        }
        
        if not payload['useMarketPrice'] and params.get('price'):
            payload['price'] = params['price']
        
        # 如果是市价，不需要价格
        if payload['useMarketPrice']:
            payload['useMarketPrice'] = True
        
        data = make_request('/api/claw/mockTrading/trade', payload)
        if data is None:
            sys.exit(1)
        result_text, _ = format_trade_result(data)
        print(result_text)
        save_result(query, result_text, data)
    
    else:
        print(f"❌ 无法识别的操作: {query}")
        sys.exit(1)

if __name__ == '__main__':
    main()
