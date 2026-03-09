#!/usr/bin/env python3
"""
持仓风险监控脚本
Usage:
    python3 risk_monitor.py --portfolio config/portfolio.json --threshold 8
"""

import argparse
import json
import requests
import sys

def get_realtime_price(code):
    """通过腾讯API获取实时价格"""
    # 添加市场前缀
    if code.startswith('6'):
        code = f'sh{code}'
    elif code.startswith('0') or code.startswith('3'):
        code = f'sz{code}'
    
    url = f'http://qt.gtimg.cn/q={code}'
    try:
        r = requests.get(url, timeout=5)
        data = r.text.split('~')
        if len(data) > 45:
            return {
                'price': float(data[3]),
                'change_pct': float(data[32]),
                'name': data[1]
            }
    except Exception as e:
        print(f"获取 {code} 价格失败: {e}")
    return None

def check_risk(position, threshold):
    """检查风险"""
    code = position['code']
    cost = position['cost']
    
    realtime = get_realtime_price(code)
    if not realtime:
        return None
    
    current_price = realtime['price']
    change_pct = (current_price - cost) / cost * 100
    
    risk_status = {
        'code': code,
        'name': position['name'],
        'cost': cost,
        'current': current_price,
        'change_pct': change_pct,
        'alerts': []
    }
    
    # 检查止损
    if change_pct <= -threshold:
        risk_status['alerts'].append(f'🔴 止损提醒: 跌幅达 {change_pct:.2f}%')
    
    # 检查止盈
    if change_pct >= position.get('take_profit', 5):
        risk_status['alerts'].append(f'🟢 止盈提醒: 涨幅达 {change_pct:.2f}%')
    
    # 检查日内暴跌
    if realtime['change_pct'] <= -5:
        risk_status['alerts'].append(f'⚠️ 日内暴跌: {realtime["change_pct"]:.2f}%')
    
    # 检查日内暴涨
    if realtime['change_pct'] >= 5:
        risk_status['alerts'].append(f'⚠️ 日内暴涨: +{realtime["change_pct"]:.2f}%')
    
    return risk_status

def main():
    parser = argparse.ArgumentParser(description='持仓风险监控')
    parser.add_argument('--portfolio', default='config/portfolio.json',
                       help='持仓配置文件路径')
    parser.add_argument('--threshold', type=float, default=8,
                       help='止损阈值（百分比，默认8%）')
    args = parser.parse_args()
    
    try:
        with open(args.portfolio, 'r', encoding='utf-8') as f:
            portfolio = json.load(f)
    except FileNotFoundError:
        print(f"错误: 找不到持仓配置文件 {args.portfolio}")
        sys.exit(1)
    
    print(f"🔍 持仓风险监控 | 止损阈值: -{args.threshold}%")
    print("=" * 60)
    
    has_alert = False
    for position in portfolio.get('positions', []):
        status = check_risk(position, args.threshold)
        if status:
            print(f"\n{status['name']} ({status['code']})")
            print(f"  成本: ¥{status['cost']:.2f} | 现价: ¥{status['current']:.2f}")
            print(f"  盈亏: {status['change_pct']:+.2f}%")
            
            if status['alerts']:
                has_alert = True
                for alert in status['alerts']:
                    print(f"  {alert}")
            else:
                print(f"  ✅ 风险正常")
    
    print("\n" + "=" * 60)
    if has_alert:
        print("⚠️ 发现风险预警，请及时处理！")
    else:
        print("✅ 所有持仓风险正常")

if __name__ == '__main__':
    main()
