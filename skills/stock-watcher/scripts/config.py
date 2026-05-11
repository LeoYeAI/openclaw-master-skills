#!/usr/bin/env python3
"""
Configuration for stock-watcher skill.
Centralized configuration to avoid path confusion.
"""
import os

# Standardized watchlist file path
WATCHLIST_DIR = os.path.expanduser("~/.clawdbot/stock_watcher")
WATCHLIST_FILE = os.path.join(WATCHLIST_DIR, "watchlist.txt")

# Ensure directory exists
os.makedirs(WATCHLIST_DIR, exist_ok=True)