#!/usr/bin/env python3
# /// script
# dependencies = [
#   "yfinance",
#   "rich",
#   "pandas",
#   "plotille",
#   "matplotlib",
#   "mplfinance"
# ]
# ///

import sys
import yfinance as yf
import pandas as pd
import plotille
import matplotlib.pyplot as plt
import mplfinance as mpf
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
import os
import subprocess

console = Console()

def _has_data(s: pd.Series) -> bool:
    """Return True if a Series-like has at least one non-NaN value."""
    try:
        return s is not None and hasattr(s, "dropna") and not s.dropna().empty
    except Exception:
        return False

# --- Technical Indicators ---

def calc_rsi(close: pd.Series, window: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/window, adjust=False, min_periods=window).mean()
    avg_loss = loss.ewm(alpha=1/window, adjust=False, min_periods=window).mean()
    rs = avg_gain / avg_loss.replace(0, pd.NA)
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calc_macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    ema_fast = close.ewm(span=fast, adjust=False, min_periods=fast).mean()
    ema_slow = close.ewm(span=slow, adjust=False, min_periods=slow).mean()
    macd = ema_fast - ema_slow
    sig = macd.ewm(span=signal, adjust=False, min_periods=signal).mean()
    hist = macd - sig
    return macd, sig, hist


def calc_bbands(close: pd.Series, window: int = 20, n_std: float = 2.0):
    ma = close.rolling(window=window, min_periods=window).mean()
    std = close.rolling(window=window, min_periods=window).std(ddof=0)
    upper = ma + n_std * std
    lower = ma - n_std * std
    return upper, ma, lower


def calc_vwap(df: pd.DataFrame) -> pd.Series:
    # VWAP over the provided window (cumulative over the selected period)
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3
    vol = df['Volume'].fillna(0)
    tpv = (typical_price * vol).cumsum()
    vwap = tpv / vol.cumsum().replace(0, pd.NA)
    return vwap


def calc_atr(df: pd.DataFrame, window: int = 14) -> pd.Series:
    high = df['High']
    low = df['Low']
    close = df['Close']
    prev_close = close.shift(1)
    tr = pd.concat([
        (high - low),
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1/window, adjust=False, min_periods=window).mean()
    return atr

def get_ticker_info(symbol):
    ticker = yf.Ticker(symbol)
    try:
        info = ticker.info
        if not info or ('regularMarketPrice' not in info and 'currentPrice' not in info):
            if not info.get('symbol'): return None, None
        return ticker, info
    except:
        return None, None

def show_price(symbol, ticker, info):
    current = info.get('regularMarketPrice') or info.get('currentPrice')
    prev_close = info.get('regularMarketPreviousClose') or info.get('previousClose')
    if current is None: return
    change = current - prev_close
    pct_change = (change / prev_close) * 100
    color = "green" if change >= 0 else "red"
    sign = "+" if change >= 0 else ""
    table = Table(title=f"Price: {info.get('longName', symbol)}")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="magenta")
    table.add_row("Symbol", symbol)
    table.add_row("Current Price", f"{current:,.2f} {info.get('currency', '')}")
    table.add_row("Change", f"[{color}]{sign}{change:,.2f} ({sign}{pct_change:.2f}%)[/{color}]")
    console.print(table)

def show_fundamentals(symbol, ticker, info):
    table = Table(title=f"Fundamentals: {info.get('longName', symbol)}")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    metrics = [
        ("Market Cap", info.get('marketCap')),
        ("PE Ratio", info.get('forwardPE')),
        ("EPS", info.get('trailingEps')),
        ("ROE", info.get('returnOnEquity')),
    ]
    for name, val in metrics:
        table.add_row(name, str(val))
    console.print(table)

def show_history(symbol, ticker, period="1mo"):
    hist = ticker.history(period=period)
    chart = plotille.plot(hist.index, hist['Close'], height=15, width=60)
    console.print(Panel(chart, title=f"Chart: {symbol}", border_style="green"))

def save_pro_chart(symbol, ticker, period="3mo", chart_type='candle', indicators=None):
    indicators = indicators or {}
    hist = ticker.history(period=period)
    if hist.empty:
        return None

    # Normalize index/name for mplfinance
    hist = hist.copy()
    if not isinstance(hist.index, pd.DatetimeIndex):
        hist.index = pd.to_datetime(hist.index)

    path = f"/tmp/{symbol}_pro.png"
    mc = mpf.make_marketcolors(up='red', down='blue', inherit=True)
    s  = mpf.make_mpf_style(marketcolors=mc, gridstyle='--', y_on_right=True)

    addplots = []
    panel_ratios = [6, 2]  # main + volume
    next_panel = 2  # reserve panel 1 for volume

    close = hist['Close']

    # Overlays on main panel (0)
    if indicators.get('bb'):
        upper, mid, lower = calc_bbands(close)
        if _has_data(upper):
            addplots.append(mpf.make_addplot(upper, color='gray', width=0.8, panel=0))
            addplots.append(mpf.make_addplot(mid,   color='dimgray', width=0.8, panel=0))
            addplots.append(mpf.make_addplot(lower, color='gray', width=0.8, panel=0))

    if indicators.get('vwap'):
        vwap = calc_vwap(hist)
        if _has_data(vwap):
            addplots.append(mpf.make_addplot(vwap, color='purple', width=1.0, panel=0))

    # RSI panel
    if indicators.get('rsi'):
        rsi = calc_rsi(close)
        if _has_data(rsi):
            rsi_panel = next_panel
            next_panel += 1
            panel_ratios.append(2)
            addplots.append(mpf.make_addplot(rsi, panel=rsi_panel, color='orange', width=1.0, ylabel='RSI'))
            addplots.append(mpf.make_addplot(pd.Series(70, index=hist.index), panel=rsi_panel, color='gray', linestyle='--', width=0.7))
            addplots.append(mpf.make_addplot(pd.Series(30, index=hist.index), panel=rsi_panel, color='gray', linestyle='--', width=0.7))

    # MACD panel
    if indicators.get('macd'):
        macd, sig, histo = calc_macd(close)
        if _has_data(macd):
            macd_panel = next_panel
            next_panel += 1
            panel_ratios.append(2)
            addplots.append(mpf.make_addplot(macd, panel=macd_panel, color='blue', width=1.0, ylabel='MACD'))
            addplots.append(mpf.make_addplot(sig, panel=macd_panel, color='red', width=1.0))
            bar_colors = histo.apply(lambda x: 'green' if x >= 0 else 'red').tolist()
            addplots.append(mpf.make_addplot(histo, panel=macd_panel, type='bar', color=bar_colors, alpha=0.35))

    # ATR panel
    if indicators.get('atr'):
        atr = calc_atr(hist)
        if _has_data(atr):
            atr_panel = next_panel
            next_panel += 1
            panel_ratios.append(2)
            addplots.append(mpf.make_addplot(atr, panel=atr_panel, color='teal', width=1.0, ylabel='ATR'))

    # Assemble plot
    plot_kwargs = dict(
        type=chart_type,
        volume=True,
        volume_panel=1,
        title=f"\n{symbol} Analysis ({period})",
        style=s,
        mav=(5, 20, 60),
        savefig=path,
    )

    if addplots:
        plot_kwargs['addplot'] = addplots
        plot_kwargs['panel_ratios'] = tuple(panel_ratios)

    mpf.plot(hist, **plot_kwargs)
    return path

def show_report(symbol, ticker, info, period="6mo"):
    # 1. Price & Change Summary
    current = info.get('regularMarketPrice') or info.get('currentPrice')
    prev_close = info.get('regularMarketPreviousClose') or info.get('previousClose')
    change = current - prev_close if current and prev_close else 0
    pct_change = (change / prev_close) * 100 if prev_close else 0
    
    # 2. Fundamentals Summary
    mcap = info.get('marketCap', 0)
    pe = info.get('forwardPE', 'N/A')
    
    # 3. Technical Indicators (latest)
    hist = ticker.history(period=period)
    if hist.empty:
        rprint("[red]No history data for report[/red]")
        return
    
    close = hist['Close']
    
    rsi_series = calc_rsi(close)
    rsi_val = rsi_series.iloc[-1] if _has_data(rsi_series) else "N/A"
    rsi_label = ""
    if isinstance(rsi_val, (int, float)):
        rsi_label = f" ({'Overbought' if rsi_val > 70 else 'Oversold' if rsi_val < 30 else 'Neutral'})"
    
    upper, mid, lower = calc_bbands(close)
    bb_display = "N/A"
    if _has_data(upper) and _has_data(lower) and (upper.iloc[-1] != lower.iloc[-1]):
        bb_pos = (close.iloc[-1] - lower.iloc[-1]) / (upper.iloc[-1] - lower.iloc[-1]) * 100
        bb_label = f" ({'Upper' if bb_pos > 80 else 'Lower' if bb_pos < 20 else 'Middle'})"
        bb_display = f"{bb_pos:.1f}%{bb_label}"
        
    macd, sig, histo = calc_macd(close)
    macd_val = macd.iloc[-1] if _has_data(macd) else "N/A"
    macd_sig = sig.iloc[-1] if _has_data(sig) else "N/A"
    macd_label = ""
    if isinstance(macd_val, (int, float)) and isinstance(macd_sig, (int, float)):
        macd_label = f" ({'Bullish' if macd_val > macd_sig else 'Bearish'})"
    
    # 4. Generate Chart (with main indicators)
    indicators = {'rsi': True, 'macd': True, 'bb': True}
    chart_path = save_pro_chart(symbol, ticker, period=period, indicators=indicators)
    
    # 5. Build Rich Report
    color = "green" if change >= 0 else "red"
    sign = "+" if change >= 0 else ""
    
    rsi_val_str = f"{rsi_val:.1f}" if isinstance(rsi_val, (int, float)) else "N/A"
    macd_val_str = f"{macd_val:.2f}" if isinstance(macd_val, (int, float)) else "N/A"
    macd_sig_str = f"{macd_sig:.2f}" if isinstance(macd_sig, (int, float)) else "N/A"
    
    report_title = f"🚀 [bold]{info.get('longName', symbol)}[/bold] Analysis Report"
    content = f"""
[bold cyan]● Market Quote[/bold cyan]
  Price: [bold]{current:,.2f} {info.get('currency', '')}[/bold]
  Change: [{color}]{sign}{change:,.2f} ({sign}{pct_change:.2f}%)[/{color}]

[bold cyan]● Fundamentals[/bold cyan]
  Market Cap: {mcap/1e9:,.1f}B | Forward PE: {pe}

[bold cyan]● Technical Signals (Latest)[/bold cyan]
  RSI(14): {rsi_val_str}{rsi_label}
  BB Position: {bb_display}
  MACD: {macd_val_str} | Signal: {macd_sig_str}{macd_label}
"""
    rprint(Panel(content.strip(), title=report_title, border_style="bright_blue"))
    if chart_path:
        print(f"CHART_PATH:{chart_path}")

def main():
    if len(sys.argv) < 2: sys.exit(1)
    
    import argparse
    parser = argparse.ArgumentParser(description="Stock Info Explorer")
    parser.add_argument("cmd", choices=["price", "fundamentals", "history", "pro", "chart", "report", "option"], nargs='?', default="price")
    parser.add_argument("symbol", help="Stock ticker symbol")
    parser.add_argument("period", nargs='?', default="3mo")
    parser.add_argument("chart_type", nargs='?', default="candle")
    parser.add_argument("--rsi", action="store_true")
    parser.add_argument("--macd", action="store_true")
    parser.add_argument("--bb", action="store_true")
    parser.add_argument("--vwap", action="store_true")
    parser.add_argument("--atr", action="store_true")
    
    # Backward compatibility for positional args or simple 'yf.py TSLA'
    args_list = sys.argv[1:]
    if len(args_list) > 0 and args_list[0] not in ["price", "fundamentals", "history", "pro", "chart", "report", "option"]:
        args_list.insert(0, "price")
    
    args = parser.parse_args(args_list)
    
    cmd = args.cmd
    symbol = args.symbol
    period = args.period
    chart_type = args.chart_type
    
    indicators = {
        'rsi': args.rsi,
        'macd': args.macd,
        'bb': args.bb,
        'vwap': args.vwap,
        'atr': args.atr
    }

    # option command does not require yfinance lookup
    if cmd == "option":
        uw_path = f"{os.path.dirname(__file__)}/uw.py"
        try:
            cp = subprocess.run(
                ["python3", uw_path, symbol],
                capture_output=True,
                text=True,
                timeout=25,
            )
            out = (cp.stdout or "").strip()
            err = (cp.stderr or "").strip()
            if out:
                print(out)
            if cp.returncode != 0:
                print(f"[option] exit_code={cp.returncode}")
                if err:
                    print(err)
        except subprocess.TimeoutExpired:
            print("[option] TIMEOUT: option scrape exceeded 25s and was safely aborted.")
            print("[option] tip: free tier detailed flow is limited (JPM/INTC/IWM/XSP).")
        return

    ticker, info = get_ticker_info(symbol)
    if not ticker: sys.exit(1)

    if cmd == "price": show_price(symbol, ticker, info)
    elif cmd == "fundamentals": show_fundamentals(symbol, ticker, info)
    elif cmd == "history": show_history(symbol, ticker, period=period)
    elif cmd == "report": show_report(symbol, ticker, info, period=period)
    elif cmd == "option":
        uw_path = f"{os.path.dirname(__file__)}/uw.py"
        try:
            cp = subprocess.run(
                ["python3", uw_path, symbol],
                capture_output=True,
                text=True,
                timeout=25,
            )
            out = (cp.stdout or "").strip()
            err = (cp.stderr or "").strip()
            if out:
                print(out)
            if cp.returncode != 0:
                print(f"[option] exit_code={cp.returncode}")
                if err:
                    print(err)
        except subprocess.TimeoutExpired:
            print("[option] TIMEOUT: option scrape exceeded 25s and was safely aborted.")
            print("[option] tip: free tier detailed flow is limited (JPM/INTC/IWM/XSP).")
    elif cmd == "pro":
        path = save_pro_chart(symbol, ticker, period=period, chart_type=chart_type, indicators=indicators)
        if path: print(f"CHART_PATH:{path}")
        
        # Summary for indicators
        hist = ticker.history(period=period)
        if not hist.empty:
            close = hist['Close']
            summary_parts = []
            if args.rsi:
                rsi_val = calc_rsi(close).iloc[-1]
                summary_parts.append(f"RSI: {rsi_val:.1f}")
            if args.bb:
                upper, mid, lower = calc_bbands(close)
                bb_pos = (close.iloc[-1] - lower.iloc[-1]) / (upper.iloc[-1] - lower.iloc[-1]) * 100
                summary_parts.append(f"BB Pos: {bb_pos:.1f}%")
            if summary_parts:
                rprint(f"[cyan]Indicator Summary:[/cyan] {' | '.join(summary_parts)}")

    elif cmd == "chart":
        hist = ticker.history(period=period)
        plt.figure(figsize=(10,6))
        plt.plot(hist.index, hist['Close'])
        path = f"/tmp/{symbol}_simple.png"
        plt.savefig(path)
        plt.close()
        print(f"CHART_PATH:{path}")
    else:
        show_price(symbol, ticker, info)

if __name__ == "__main__":
    main()
