#!/usr/bin/env python3
"""
信用卡福利自动报告生成器
生成月度/季度福利使用情况汇总
"""

import json
from datetime import datetime, timezone
from pathlib import Path

# 配置
CARDS_FILE = Path("/home/node/.openclaw/workspace/skills/card-benefits-tracker/cards.json")
TZ_OFFSET = -8  # PST

def get_local_date():
    """获取本地日期（America/Los_Angeles）"""
    return datetime.now(timezone.utc).astimezone()

def load_cards():
    """加载信用卡数据"""
    with open(CARDS_FILE, 'r') as f:
        data = json.load(f)
    return data['cards']

def analyze_monthly_benefits(cards, current_month, current_day):
    """分析月度福利"""
    report_lines = []
    total_monthly_value = 0
    
    for card in cards:
        card_name = card['name']
        monthly_benefits = []
        
        for benefit in card.get('benefits', []):
            if benefit['frequency'] == 'monthly':
                amount = benefit['amount']
                name = benefit['name']
                notes = benefit.get('notes', '')
                total_monthly_value += amount
                monthly_benefits.append({
                    'name': name,
                    'amount': amount,
                    'notes': notes,
                    'card': card_name
                })
        
        if monthly_benefits:
            report_lines.append(f"\n• {card_name}:")
            for b in monthly_benefits:
                report_lines.append(f"  - {b['name']}: ${b['amount']}")
    
    return report_lines, total_monthly_value

def analyze_quarterly_benefits(cards):
    """分析季度福利"""
    report_lines = []
    total_quarterly_value = 0
    
    # 简单判断季度（1-3月: Q1, 4-6月: Q2, etc.）
    now = get_local_date()
    month = now.month
    quarter = (month - 1) // 3 + 1
    quarter_months = {1: (1,3), 2: (4,6), 3: (7,9), 4: (10,12)}[quarter]
    quarter_name = f"Q{quarter}"
    
    for card in cards:
        card_name = card['name']
        quarterly_benefits = []
        
        for benefit in card.get('benefits', []):
            if benefit['frequency'] == 'quarterly':
                amount = benefit['amount']
                name = benefit['name']
                total_quarterly_value += amount
                quarterly_benefits.append({
                    'name': name,
                    'amount': amount,
                    'card': card_name
                })
        
        if quarterly_benefits:
            report_lines.append(f"\n• {card_name}:")
            for b in quarterly_benefits:
                report_lines.append(f"  - {b['name']}: ${b['amount']} (本季度有效)")
    
    return report_lines, total_quarterly_value, quarter_name

def generate_report():
    """生成完整报告"""
    now = get_local_date()
    date_str = now.strftime("%Y年%m月%d日")
    
    cards = load_cards()
    
    # 分析
    monthly_lines, monthly_total = analyze_monthly_benefits(cards, now.month, now.day)
    quarterly_lines, quarterly_total, quarter_name = analyze_quarterly_benefits(cards)
    
    # 构建报告
    report = f"📊 信用卡福利报告\n"
    report += f"📅 生成时间: {date_str} (America/Los_Angeles)\n"
    report += "="*50 + "\n\n"
    
    if monthly_lines:
        report += "🗓️ 本月可使用的月度福利（月底截止）:\n"
        report += "".join(monthly_lines)
        report += f"\n\n💰 月度福利总价值: ${monthly_total:,.2f}/月\n"
    else:
        report += "🗓️ 本月无月度福利\n"
    
    if quarterly_lines:
        report += f"\n🏆 本季度({quarter_name})可使用的季度福利:\n"
        report += "".join(quarterly_lines)
        report += f"\n\n💰 季度福利总价值: ${quarterly_total:,.2f}/季度\n"
    else:
        report += "\n🏆 本季度无季度福利\n"
    
    report += "\n" + "="*50 + "\n"
    report += "💡 建议: 尽快使用这些福利，过期作废！\n"
    
    return report

if __name__ == "__main__":
    print(generate_report())
