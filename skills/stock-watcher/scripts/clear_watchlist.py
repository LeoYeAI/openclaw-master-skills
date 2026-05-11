#!/usr/bin/env python3
"""
Clear the entire watchlist.
This script removes all stocks from the watchlist file.
"""
import os
import sys

# Define the watchlist file path directly
WATCHLIST_FILE = os.path.expanduser("~/.clawdbot/stock_watcher/watchlist.txt")

def clear_watchlist():
    """Clear the entire watchlist."""
    # Ensure the directory exists
    os.makedirs(os.path.dirname(WATCHLIST_FILE), exist_ok=True)
    
    # Clear the file by opening in write mode and closing immediately
    with open(WATCHLIST_FILE, 'w', encoding='utf-8') as f:
        pass
    
    print("Watchlist cleared successfully.")

if __name__ == "__main__":
    clear_watchlist()