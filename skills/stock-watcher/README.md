# Stock Watcher Skill

A standardized stock watchlist management skill for Clawdbot that provides clean, consistent functionality for tracking Chinese A-share stocks.

## Features

- ✅ **Add stocks** to watchlist using 6-digit stock codes
- ✅ **View watchlist** with clear formatting
- ✅ **Remove individual stocks** from watchlist
- ✅ **Clear entire watchlist** with one command
- ✅ **Get performance summary** for all watched stocks
- ✅ **Standardized storage path** - no more path confusion!
- ✅ **Easy installation/uninstallation**

## Installation

For new users, the skill will be automatically installed when first used. The installation script creates:

- Standardized watchlist directory: `~/.clawdbot/stock_watcher/`
- Watchlist file: `~/.clawdbot/stock_watcher/watchlist.txt`
- All necessary scripts in the skill directory

## Usage Commands

### Add a stock
```bash
cd ~/.clawdbot/skills/stock-watcher/scripts && python3 add_stock.py 600053
```

### View watchlist
```bash
cd ~/.clawdbot/skills/stock-watcher/scripts && python3 list_stocks.py
```

### Remove a stock
```bash
cd ~/.clawdbot/skills/stock-watcher/scripts && python3 remove_stock.py 600053
```

### Clear watchlist
```bash
cd ~/.clawdbot/skills/stock-watcher/scripts && python3 clear_watchlist.py
```

### Get performance summary
```bash
cd ~/.clawdbot/skills/stock-watcher/scripts && python3 summarize_performance.py
```

## Data Source

- **Primary source**: 同花顺 (10jqka.com.cn)
- **Stock pages**: `https://stockpage.10jqka.com.cn/{stock_code}/`
- **Supported markets**: Shanghai A-shares, Shenzhen A-shares, STAR Market

## File Structure

```
stock-watcher/
├── SKILL.md                 # Skill metadata and instructions
├── scripts/
│   ├── config.py           # Centralized configuration
│   ├── add_stock.py        # Add stock to watchlist
│   ├── list_stocks.py      # List all stocks in watchlist
│   ├── remove_stock.py     # Remove specific stock
│   ├── clear_watchlist.py  # Clear entire watchlist
│   ├── summarize_performance.py # Get stock performance data
│   ├── install.sh          # Installation script
│   └── uninstall.sh        # Uninstallation script
└── references/             # (Reserved for future reference docs)
```

## Storage Location

All user data is stored in a single, standardized location:
- **Directory**: `~/.clawdbot/stock_watcher/`
- **Watchlist file**: `~/.clawdbot/stock_watcher/watchlist.txt`

Format: `stock_code|stock_name` (e.g., `600053|九鼎投资`)

## Troubleshooting

### "Command not found" errors
Ensure you have Python 3 and required packages installed:
```bash
pip3 install requests beautifulsoup4
```

### Network issues
The skill fetches data from 10jqka.com.cn. Ensure you have internet access and the site is accessible.

### Permission errors
Make sure the `~/.clawdbot/` directory is writable by your user.

## Uninstallation

To completely remove the skill and all data:
```bash
cd ~/.clawdbot/skills/stock-watcher/scripts && ./uninstall.sh
```

This will remove both the skill scripts and your watchlist data.