#!/usr/bin/env python3
"""
生成交易汇报模板
Usage:
    python3 generate_report.py --type opening --portfolio config/portfolio.json
    python3 generate_report.py --type closing --portfolio config/portfolio.json
    python3 generate_report.py --type daily --portfolio config/portfolio.json
"""

import argparse
import json
import datetime

def load_portfolio(path):
    """加载持仓配置"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_opening_report(portfolio):
    """生成开盘简报"""
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    
    report = f"""## 开盘简报 | {today}

### 隔夜市场
- 美股：纳指 X% / 道指 X% / 标普 X%
- 黄金：$X（X%）
- 原油：$X（X%）

### 当前持仓
| 股票 | 持仓 | 成本 | 现价 | 盈亏 |
|:---|:---:|:---:|:---:|:---:|
"""
    
    for pos in portfolio.get('positions', []):
        report += f"| {pos['name']} | {pos['quantity']}股 | ¥{pos['cost']} | ¥{pos.get('current_price', 'X')} | X% |\n"
    
    report += f"""
### 账户概览
- 总资产：¥{portfolio.get('total_assets', 'X')}
- 可用资金：¥{portfolio.get('cash', 'X')}

### 今日计划
- 关注标的：XXX
- 风控动作：XXX
- 调仓计划：XXX

---
生成时间：{datetime.datetime.now().strftime('%H:%M')}
"""
    return report

def generate_closing_report(portfolio):
    """生成收盘汇报"""
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    
    report = f"""## 收盘汇报 | {today}

### 当日盈亏
- 总盈亏：¥X（X%）
- 持仓市值：¥X
- 可用资金：¥{portfolio.get('cash', 'X')}

### 交易记录
| 时间 | 操作 | 股票 | 数量 | 价格 | 理由 |
|:---|:---:|:---:|:---:|:---:|:---|
| --:-- | -- | -- | -- | -- | -- |

### 持仓明细
| 股票 | 持仓 | 成本 | 现价 | 盈亏 | 占比 |
|:---|:---:|:---:|:---:|:---:|:---:|
"""
    
    for pos in portfolio.get('positions', []):
        report += f"| {pos['name']} | {pos['quantity']}股 | ¥{pos['cost']} | ¥{pos.get('current_price', 'X')} | X% | X% |\n"
    
    report += f"""
### 明日预判
- 大盘走势：XXX
- 关注板块：XXX
- 操作计划：XXX

---
生成时间：{datetime.datetime.now().strftime('%H:%M')}
"""
    return report

def generate_daily_report(portfolio):
    """生成日终总结"""
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    
    report = f"""## 日终总结 | {today}

### 全天回顾
- 开盘情况：XXX
- 盘中操作：XXX
- 收盘状态：XXX

### 盈亏统计
| 项目 | 数值 |
|:---|:---:|
| 当日盈亏 | ¥X（X%）|
| 本周累计 | X% |
| 本月累计 | X% |

### 交易得失
**做得好的**：
- XXX

**需要改进**：
- XXX

### 明日计划
- 候选股票：XXX
- 风控重点：XXX
- 关注消息：XXX

### 风险提示
- XXX

---
汇报人：Alex  
时间：{datetime.datetime.now().strftime('%H:%M')}
"""
    return report

def main():
    parser = argparse.ArgumentParser(description='生成交易汇报')
    parser.add_argument('--type', choices=['opening', 'closing', 'daily'], 
                       required=True, help='报告类型')
    parser.add_argument('--portfolio', default='config/portfolio.json',
                       help='持仓配置文件路径')
    args = parser.parse_args()
    
    try:
        portfolio = load_portfolio(args.portfolio)
    except FileNotFoundError:
        print(f"错误: 找不到持仓配置文件 {args.portfolio}")
        print("请创建配置文件或指定正确的路径")
        return
    
    if args.type == 'opening':
        report = generate_opening_report(portfolio)
        filename = f"reports/opening_{datetime.datetime.now().strftime('%Y%m%d')}.md"
    elif args.type == 'closing':
        report = generate_closing_report(portfolio)
        filename = f"reports/closing_{datetime.datetime.now().strftime('%Y%m%d')}.md"
    else:  # daily
        report = generate_daily_report(portfolio)
        filename = f"reports/daily_{datetime.datetime.now().strftime('%Y%m%d')}.md"
    
    print(report)
    print(f"\n报告已生成，建议保存至: {filename}")

if __name__ == '__main__':
    main()
