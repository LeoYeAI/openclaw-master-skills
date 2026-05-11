#!/bin/bash
# Uninstall stock-watcher skill

set -e

# Remove watchlist directory and files
WATCHLIST_DIR="$HOME/.clawdbot/stock_watcher"
if [ -d "$WATCHLIST_DIR" ]; then
    rm -rf "$WATCHLIST_DIR"
    echo "Removed watchlist directory: $WATCHLIST_DIR"
fi

echo "Stock watcher skill uninstalled successfully."