#!/usr/bin/env python3
"""
获取股票基本面数据
Usage: python3 get_fundamentals.py <stock_code>
Example: python3 get_fundamentals.py 300750.SZ
"""

import sys
import os
import json
import tushare as ts
from datetime import datetime, timedelta

# 设置 Tushare Token (必须通过环境变量设置)
TUSHARE_TOKEN = os.environ.get('TUSHARE_TOKEN')
if not TUSHARE_TOKEN:
    print("错误: 请设置环境变量 TUSHARE_TOKEN", file=sys.stderr)
    sys.exit(1)
ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api()


def get_stock_info(ts_code):
    """获取股票基本信息"""
    try:
        df = pro.stock_basic(ts_code=ts_code, fields='ts_code,name,industry,market,list_date')
        if df.empty:
            return None
        return df.iloc[0].to_dict()
    except Exception as e:
        print(f"获取股票信息失败: {e}", file=sys.stderr)
        return None


def get_daily_basic(ts_code):
    """获取每日基本面指标"""
    try:
        # 获取最近30天的数据
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
        
        df = pro.daily_basic(ts_code=ts_code, start_date=start_date, end_date=end_date,
                             fields='ts_code,trade_date,pe,pb,ps,total_mv,circ_mv,turnover_rate')
        if df.empty:
            return None
        return df.iloc[0].to_dict()
    except Exception as e:
        print(f"获取每日基本面失败: {e}", file=sys.stderr)
        return None


def get_financial_indicator(ts_code):
    """获取财务指标"""
    try:
        df = pro.fina_indicator(ts_code=ts_code, fields='ts_code,end_date,roe,roa,debt_ratio,current_ratio,grossprofit_margin,netprofit_margin')
        if df.empty:
            return None
        # 取最近4个季度
        return df.head(4).to_dict('records')
    except Exception as e:
        print(f"获取财务指标失败: {e}", file=sys.stderr)
        return None


def get_income(ts_code):
    """获取利润表"""
    try:
        df = pro.income(ts_code=ts_code, fields='ts_code,end_date,revenue,n_income,gross_profit,total_cogs')
        if df.empty:
            return None
        return df.head(4).to_dict('records')
    except Exception as e:
        print(f"获取利润表失败: {e}", file=sys.stderr)
        return None


def get_balancesheet(ts_code):
    """获取资产负债表"""
    try:
        df = pro.balancesheet(ts_code=ts_code, fields='ts_code,end_date,total_assets,total_liab,total_hldr_eqy_exc_min_int,money_cap,fix_assets')
        if df.empty:
            return None
        return df.head(4).to_dict('records')
    except Exception as e:
        print(f"获取资产负债表失败: {e}", file=sys.stderr)
        return None


def get_cashflow(ts_code):
    """获取现金流量表"""
    try:
        df = pro.cashflow(ts_code=ts_code, fields='ts_code,end_date,n_cashflow_act,n_cashflow_inv_act,n_cash_flows_fnc_act')
        if df.empty:
            return None
        return df.head(4).to_dict('records')
    except Exception as e:
        print(f"获取现金流量表失败: {e}", file=sys.stderr)
        return None


def get_top10_holders(ts_code):
    """获取前10大股东"""
    try:
        df = pro.top10_holders(ts_code=ts_code)
        if df.empty:
            return None
        return df.head(10).to_dict('records')
    except Exception as e:
        print(f"获取股东信息失败: {e}", file=sys.stderr)
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 get_fundamentals.py <stock_code>", file=sys.stderr)
        sys.exit(1)
    
    ts_code = sys.argv[1]
    print(f"正在获取 {ts_code} 的基本面数据...", file=sys.stderr)
    
    result = {
        'stock_code': ts_code,
        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'stock_info': get_stock_info(ts_code),
        'daily_basic': get_daily_basic(ts_code),
        'financial_indicator': get_financial_indicator(ts_code),
        'income': get_income(ts_code),
        'balancesheet': get_balancesheet(ts_code),
        'cashflow': get_cashflow(ts_code),
        'top10_holders': get_top10_holders(ts_code)
    }
    
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == '__main__':
    main()