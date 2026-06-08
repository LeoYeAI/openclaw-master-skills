#!/usr/bin/env python3
"""
获取股票市场数据和技术指标
Usage: python3 get_market_data.py <stock_code> [days]
Example: python3 get_market_data.py 300750.SZ 365
"""

import sys
import os
import json
import tushare as ts
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 设置 Tushare Token (必须通过环境变量设置)
TUSHARE_TOKEN = os.environ.get('TUSHARE_TOKEN')
if not TUSHARE_TOKEN:
    print("错误: 请设置环境变量 TUSHARE_TOKEN", file=sys.stderr)
    sys.exit(1)
ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api()


def get_daily_data(ts_code, days=365):
    """获取日线数据"""
    try:
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
        
        df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        if df.empty:
            return None
        # 按日期正序排列
        df = df.sort_values('trade_date').reset_index(drop=True)
        return df
    except Exception as e:
        print(f"获取日线数据失败: {e}", file=sys.stderr)
        return None


def calculate_ma(df, periods=[5, 10, 20, 60]):
    """计算均线"""
    result = {}
    for period in periods:
        if len(df) >= period:
            result[f'MA{period}'] = round(df['close'].tail(period).mean(), 2)
        else:
            result[f'MA{period}'] = None
    return result


def calculate_macd(df, fast=12, slow=26, signal=9):
    """计算MACD指标"""
    if len(df) < slow + signal:
        return None
    
    closes = df['close'].values
    ema_fast = pd.Series(closes).ewm(span=fast, adjust=False).mean()
    ema_slow = pd.Series(closes).ewm(span=slow, adjust=False).mean()
    dif = ema_fast - ema_slow
    dea = dif.ewm(span=signal, adjust=False).mean()
    macd = (dif - dea) * 2
    
    return {
        'DIF': round(dif.iloc[-1], 4),
        'DEA': round(dea.iloc[-1], 4),
        'MACD': round(macd.iloc[-1], 4),
        'signal': '金叉' if dif.iloc[-1] > dea.iloc[-1] and dif.iloc[-2] <= dea.iloc[-2] else
                  '死叉' if dif.iloc[-1] < dea.iloc[-1] and dif.iloc[-2] >= dea.iloc[-2] else
                  '多头' if dif.iloc[-1] > dea.iloc[-1] else '空头'
    }


def calculate_rsi(df, period=14):
    """计算RSI指标"""
    if len(df) < period + 1:
        return None
    
    closes = df['close'].values
    deltas = np.diff(closes)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])
    
    if avg_loss == 0:
        rsi = 100
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
    
    return {
        'RSI': round(rsi, 2),
        'status': '超买' if rsi > 70 else ('超卖' if rsi < 30 else '正常')
    }


def calculate_kdj(df, n=9, m1=3, m2=3):
    """计算KDJ指标"""
    if len(df) < n:
        return None
    
    low_min = df['low'].tail(n).min()
    high_max = df['high'].tail(n).max()
    close = df['close'].iloc[-1]
    
    if high_max == low_min:
        rsv = 50
    else:
        rsv = (close - low_min) / (high_max - low_min) * 100
    
    # 简化计算，只返回当前值
    k = rsv  # 简化
    d = k    # 简化
    j = 3 * k - 2 * d
    
    return {
        'K': round(k, 2),
        'D': round(d, 2),
        'J': round(j, 2),
        'status': '超买' if k > 80 else ('超卖' if k < 20 else '正常')
    }


def calculate_boll(df, period=20, std_dev=2):
    """计算布林带"""
    if len(df) < period:
        return None
    
    closes = df['close'].tail(period)
    mid = closes.mean()
    std = closes.std()
    upper = mid + std_dev * std
    lower = mid - std_dev * std
    current = df['close'].iloc[-1]
    
    return {
        'upper': round(upper, 2),
        'mid': round(mid, 2),
        'lower': round(lower, 2),
        'current': round(current, 2),
        'position': '上轨上方' if current > upper else 
                    ('下轨下方' if current < lower else '布林带内')
    }


def get_moneyflow(ts_code, days=10):
    """获取资金流向"""
    try:
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
        
        df = pro.moneyflow(ts_code=ts_code, start_date=start_date, end_date=end_date)
        if df.empty:
            return None
        
        # 按日期正序排列
        df = df.sort_values('trade_date').reset_index(drop=True)
        return df.to_dict('records')
    except Exception as e:
        print(f"获取资金流向失败: {e}", file=sys.stderr)
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 get_market_data.py <stock_code> [days]", file=sys.stderr)
        sys.exit(1)
    
    ts_code = sys.argv[1]
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 365
    
    print(f"正在获取 {ts_code} 的市场数据 (近{days}天)...", file=sys.stderr)
    
    # 获取日线数据
    daily_df = get_daily_data(ts_code, days)
    if daily_df is None or daily_df.empty:
        print(json.dumps({'error': '无法获取日线数据'}, ensure_ascii=False))
        sys.exit(1)
    
    # 计算技术指标
    result = {
        'stock_code': ts_code,
        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'latest_price': {
            'close': float(daily_df['close'].iloc[-1]),
            'high': float(daily_df['high'].iloc[-1]),
            'low': float(daily_df['low'].iloc[-1]),
            'volume': float(daily_df['vol'].iloc[-1]),
            'amount': float(daily_df['amount'].iloc[-1]),
            'trade_date': daily_df['trade_date'].iloc[-1]
        },
        'ma': calculate_ma(daily_df),
        'macd': calculate_macd(daily_df),
        'rsi': calculate_rsi(daily_df),
        'kdj': calculate_kdj(daily_df),
        'boll': calculate_boll(daily_df),
        'moneyflow': get_moneyflow(ts_code, 10),
        'price_change': {
            '1d': round((daily_df['close'].iloc[-1] / daily_df['close'].iloc[-2] - 1) * 100, 2) if len(daily_df) > 1 else None,
            '5d': round((daily_df['close'].iloc[-1] / daily_df['close'].iloc[-6] - 1) * 100, 2) if len(daily_df) > 5 else None,
            '20d': round((daily_df['close'].iloc[-1] / daily_df['close'].iloc[-21] - 1) * 100, 2) if len(daily_df) > 20 else None,
            '60d': round((daily_df['close'].iloc[-1] / daily_df['close'].iloc[-61] - 1) * 100, 2) if len(daily_df) > 60 else None,
            '1y': round((daily_df['close'].iloc[-1] / daily_df['close'].iloc[0] - 1) * 100, 2) if len(daily_df) > 0 else None
        }
    }
    
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == '__main__':
    main()