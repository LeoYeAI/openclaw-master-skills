#!/bin/bash
# Scrapling - Quick scrape script

# Usage:
#   python3 scrapling.py fetch <url> [selector]
#   python3 scrapling.py scrape <url> <selector>
#   python3 scrapling.py spider <spider_file>

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Ensure scrapling is installed (use python3 -m pip)
python3 -m pip show scrapling >/dev/null 2>&1 || python3 -m pip install scrapling

# Default to fetch mode
MODE="${1:-fetch}"
URL="${2:-https://example.com}"
SELECTOR="${3:-body}"

case "$MODE" in
    fetch)
        echo "Fetching $URL with selector: $SELECTOR"
        python3 -c "
from scrapling.fetchers import Fetcher
page = Fetcher.fetch('$URL')
elements = page.css('$SELECTOR')
for i, el in enumerate(elements.all()[:10], 1):
    print(f'{i}. {el.strip()[:200]}')
"
        ;;
    stealth)
        echo "Stealth fetching $URL..."
        python3 -c "
from scrapling.fetchers import StealthyFetcher
StealthyFetcher.adaptive = True
page = StealthyFetcher.fetch('$URL', headless=True, network_idle=True)
print(page.content[:2000])
"
        ;;
    spider)
        echo "Running spider: $URL"
        python3 "$URL"
        ;;
    install)
        echo "Installing Scrapling with all extras..."
        python3 -m pip install "scrapling[all]"
        scrapling install
        ;;
    *)
        echo "Usage: $0 {fetch|stealth|spider|install} [url] [selector]"
        echo ""
        echo "Commands:"
        echo "  fetch <url> [selector]  - Basic HTTP fetch"
        echo "  stealth <url>           - Stealthy fetch (anti-bot)"
        echo "  spider <file>          - Run spider script"
        echo "  install                - Install scrapling with all extras"
        ;;
esac
