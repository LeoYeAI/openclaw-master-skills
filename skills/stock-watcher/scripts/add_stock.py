#!/usr/bin/env python3
"""
Add stock to watchlist
Usage: python3 add_stock.py <stock_code> [stock_name]
"""
import sys
import os
import requests
from bs4 import BeautifulSoup
from config import WATCHLIST_FILE

def get_stock_name_from_code(stock_code):
    """Get stock name from 10jqka.com.cn using stock code"""
    try:
        url = f"https://stockpage.10jqka.com.cn/{stock_code}/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('title')
            if title:
                title_text = title.get_text()
                if '(' in title_text and ')' in title_text:
                    stock_name = title_text.split('(')[0].strip()
                    return stock_name
    except Exception as e:
        pass
    return None

def add_stock(stock_code, stock_name=None):
    """Add stock to watchlist.txt in the correct location"""
    # Ensure the directory exists
    os.makedirs(os.path.dirname(WATCHLIST_FILE), exist_ok=True)
    
    # Get stock name if not provided
    if not stock_name:
        stock_name = get_stock_name_from_code(stock_code)
        if not stock_name:
            stock_name = stock_code  # fallback to code if name cannot be fetched
    
    # Read existing watchlist
    existing_stocks = []
    if os.path.exists(WATCHLIST_FILE):
        with open(WATCHLIST_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    existing_stocks.append(line)
    
    # Check if stock already exists
    stock_entry = f"{stock_code}|{stock_name}"
    stock_exists = False
    for existing in existing_stocks:
        if existing.startswith(f"{stock_code}|"):
            stock_exists = True
            break
    
    if stock_exists:
        print(f"Stock {stock_code} already in watchlist")
        return False
    
    # Add new stock
    existing_stocks.append(stock_entry)
    
    # Write back to file with proper newlines
    with open(WATCHLIST_FILE, 'w', encoding='utf-8') as f:
        for stock in existing_stocks:
            f.write(stock + '\n')
    
    print(f"Added stock {stock_code} ({stock_name}) to watchlist")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 add_stock.py <stock_code> [stock_name]")
        sys.exit(1)
    
    stock_code = sys.argv[1]
    stock_name = sys.argv[2] if len(sys.argv) > 2 else None
    add_stock(stock_code, stock_name)