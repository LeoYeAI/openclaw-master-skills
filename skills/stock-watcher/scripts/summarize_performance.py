#!/usr/bin/env python3
"""
Summarize the performance of all stocks in the watchlist.
This script fetches current stock data from 10jqka.com.cn for each stock
in the watchlist and provides a summary of their recent performance.
"""
import os
import sys
import requests
from bs4 import BeautifulSoup
import time

# Standardized watchlist file path
WATCHLIST_FILE = os.path.expanduser("~/.clawdbot/stock_watcher/watchlist.txt")

def fetch_stock_data(stock_code):
    """Fetch stock data from 10jqka.com.cn."""
    url = f"https://stockpage.10jqka.com.cn/{stock_code}/"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract basic info
        title = soup.find('title')
        stock_name = ""
        if title:
            title_text = title.get_text()
            if '(' in title_text and ')' in title_text:
                stock_name = title_text.split('(')[0].strip()
        
        # Look for performance data
        performance_data = {}
        
        # Try to find recent performance indicators
        # This is a simplified version - in practice, you'd need more robust parsing
        text_content = soup.get_text()
        
        # Look for key phrases
        if '涨跌幅' in text_content:
            # Extract percentage changes
            import re
            percentages = re.findall(r'[-+]?\d+\.?\d*%', text_content)
            if percentages:
                performance_data['recent_changes'] = percentages[:3]  # Get first 3 percentages
        
        return {
            'code': stock_code,
            'name': stock_name,
            'url': url,
            'performance': performance_data
        }
        
    except Exception as e:
        print(f"Error fetching data for {stock_code}: {e}", file=sys.stderr)
        return None

def summarize_performance():
    """Summarize performance of all stocks in watchlist."""
    if not os.path.exists(WATCHLIST_FILE):
        return
    
    with open(WATCHLIST_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    if not lines or all(not line.strip() for line in lines):
        return
    
    # Directly output performance summary without any command prompts
    for line in lines:
        line = line.strip()
        if line:
            parts = line.split('|')
            if len(parts) == 2:
                code, name = parts
                
                # Fetch data
                stock_data = fetch_stock_data(code)
                if stock_data:
                    if stock_data['performance']:
                        for i, change in enumerate(stock_data['performance'].get('recent_changes', []), 1):
                            print(f"{code} - {name} - 指标{i}: {change}")
                    else:
                        print(f"{code} - {name} - 行情数据暂不可用")
                else:
                    print(f"{code} - {name} - 获取数据失败")
                
                # Be respectful to the server
                time.sleep(1)

if __name__ == "__main__":
    summarize_performance()