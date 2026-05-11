#!/usr/bin/env python3
"""
Remove stock from watchlist
Usage: python3 remove_stock.py <stock_code>
"""
import sys
import os

# Standardized watchlist file path
WATCHLIST_DIR = os.path.expanduser("~/.clawdbot/stock_watcher")
WATCHLIST_FILE = os.path.join(WATCHLIST_DIR, "watchlist.txt")

def remove_stock(stock_code):
    """Remove stock from watchlist."""
    if not os.path.exists(WATCHLIST_FILE):
        print("Watchlist is empty.")
        return False
    
    # Read existing watchlist
    existing_stocks = []
    with open(WATCHLIST_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                existing_stocks.append(line)
    
    # Find and remove the stock
    stock_found = False
    updated_stocks = []
    for stock in existing_stocks:
        if stock.startswith(f"{stock_code}|"):
            stock_found = True
        else:
            updated_stocks.append(stock)
    
    if not stock_found:
        print(f"Stock {stock_code} not found in watchlist")
        return False
    
    # Write back to file
    with open(WATCHLIST_FILE, 'w', encoding='utf-8') as f:
        for stock in updated_stocks:
            f.write(stock + '\n')
    
    print(f"Removed stock {stock_code} from watchlist")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 remove_stock.py <stock_code>")
        sys.exit(1)
    
    stock_code = sys.argv[1]
    remove_stock(stock_code)