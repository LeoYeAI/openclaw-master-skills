#!/usr/bin/env bash
# Briefing Room — Helper script for setup and utilities
# The actual briefing is composed by the agent (SKILL.md), not this script.
# This script handles: setup checks, folder creation, audio post-processing.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_PY="$SCRIPT_DIR/config.py"

# Read config values via Python
cfg() {
    python3 "$CONFIG_PY" get "$1" 2>/dev/null || echo ""
}

BRIEFINGS_DIR="$(cfg output.folder)"
[ -z "$BRIEFINGS_DIR" ] && BRIEFINGS_DIR="$HOME/Documents/Briefing Room"
DATE=$(date +%Y-%m-%d)
OUTPUT_DIR="$BRIEFINGS_DIR/$DATE"

# User-Agent for sites behind Cloudflare
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

usage() {
    echo "Briefing Room — Helper Script"
    echo ""
    echo "Usage: briefing.sh <command>"
    echo ""
    echo "Commands:"
    echo "  setup       Check dependencies and show status"
    echo "  init        Create today's output folder"
    echo "  weather     Fetch weather data (JSON)"
    echo "  trends      Fetch X/Twitter trends (US + UK + Worldwide)"
    echo "  webtrends   Fetch Google Trends (US + UK + Worldwide)"
    echo "  crypto      Fetch crypto prices (JSON)"
    echo "  open        Open today's briefing folder"
    echo "  list        List all briefings"
    echo "  clean       Remove briefings older than 30 days"
    echo "  config      Show current configuration"
    echo ""
}

cmd_setup() {
    python3 "$CONFIG_PY" status
}

cmd_init() {
    mkdir -p "$OUTPUT_DIR"
    echo "$OUTPUT_DIR"
}

cmd_weather() {
    local lat lon tz city
    lat="$(cfg location.latitude)"
    lon="$(cfg location.longitude)"
    tz="$(cfg location.timezone)"
    city="$(cfg location.city)"
    # Fallbacks match config.py DEFAULT_CONFIG
    [ -z "$lat" ] && lat="48.15"
    [ -z "$lon" ] && lon="17.11"
    [ -z "$tz" ] && tz="Europe/Bratislava"
    [ -z "$city" ] && city="Bratislava"

    local tz_encoded="${tz/\//%2F}"

    echo "=== Current Weather ($city) ==="
    curl -s --max-time 10 "https://api.open-meteo.com/v1/forecast?latitude=$lat&longitude=$lon&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m&timezone=$tz_encoded"
    echo ""
    echo ""
    echo "=== 7-Day Forecast ==="
    curl -s --max-time 10 "https://api.open-meteo.com/v1/forecast?latitude=$lat&longitude=$lon&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code&timezone=$tz_encoded"
    echo ""
}

cmd_trends() {
    echo "=== X/Twitter Trends ==="
    # Configurable regions: comma-separated slugs in config, or default US+UK+Worldwide
    local regions_cfg
    regions_cfg="$(cfg trends.regions)"
    if [ -z "$regions_cfg" ] || [ "$regions_cfg" = "None" ]; then
        regions_cfg="united-states,united-kingdom,"
    fi

    IFS=',' read -ra slugs <<< "$regions_cfg"
    for slug in "${slugs[@]}"; do
        slug="$(echo "$slug" | xargs)"  # trim whitespace
        local label url
        if [ -z "$slug" ]; then
            label="Worldwide"
            url="https://getdaytrends.com/"
        else
            label="${slug//-/ }"
            # Capitalize words
            label="$(echo "$label" | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)}1')"
            url="https://getdaytrends.com/$slug/"
        fi
        echo ""
        echo "--- $label ---"
        local html
        html="$(curl -s --max-time 15 -A "$UA" "$url" 2>/dev/null)" || true
        if [ -z "$html" ]; then
            echo "(failed to fetch)"
            continue
        fi
        echo "$html" | python3 -c "
import sys, urllib.parse, re
html = sys.stdin.read()
trends = re.findall(r'/trend/([^/]+)/', html)
seen = set()
for t in trends:
    name = urllib.parse.unquote(t)
    if name not in seen:
        seen.add(name)
        print(name)
" | head -25
    done
}

cmd_webtrends() {
    echo "=== Google Trends (Web) ==="
    # Configurable regions for Google Trends
    local regions_cfg
    regions_cfg="$(cfg webtrends.regions)"
    if [ -z "$regions_cfg" ] || [ "$regions_cfg" = "None" ]; then
        regions_cfg="US,GB,"
    fi

    IFS=',' read -ra geos <<< "$regions_cfg"
    for geo in "${geos[@]}"; do
        geo="$(echo "$geo" | xargs)"  # trim whitespace
        local label url
        if [ -z "$geo" ]; then
            label="Worldwide"
            url="https://trends.google.com/trending/rss?geo="
        else
            label="$geo"
            url="https://trends.google.com/trending/rss?geo=$geo"
        fi
        echo ""
        echo "--- $label ---"
        local xml
        xml="$(curl -s --max-time 15 "$url" 2>/dev/null)" || true
        if [ -z "$xml" ]; then
            echo "(failed to fetch)"
            continue
        fi
        echo "$xml" | python3 -c "
import sys, re, html as html_mod

xml = sys.stdin.read()
items = re.findall(r'<item>(.*?)</item>', xml, re.DOTALL)
for item in items[:20]:
    title = re.search(r'<title>(.*?)</title>', item)
    traffic = re.search(r'<ht:approx_traffic>(.*?)</ht:approx_traffic>', item)
    headlines = re.findall(r'<ht:news_item_title>(.*?)</ht:news_item_title>', item)

    t = html_mod.unescape(title.group(1)) if title else '?'
    tr = traffic.group(1) if traffic else '?'
    h = html_mod.unescape(headlines[0]) if headlines else ''

    print(f'{t} ({tr})')
    if h:
        print(f'  → {h}')
"
    done
}

cmd_crypto() {
    echo "=== Crypto Prices ==="
    for coin in BTC ETH SOL XRP; do
        echo -n "$coin/USD: "
        curl -s --max-time 10 "https://api.coinbase.com/v2/prices/$coin-USD/spot" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['data']['amount'])" 2>/dev/null || echo "N/A"
    done
}

cmd_open() {
    if [ -d "$OUTPUT_DIR" ]; then
        open "$OUTPUT_DIR"
    else
        echo "No briefing for today ($DATE). Run the briefing first!"
        exit 1
    fi
}

cmd_list() {
    if [ -d "$BRIEFINGS_DIR" ]; then
        echo "📻 Available Briefings:"
        echo ""
        local found=false
        for dir in "$BRIEFINGS_DIR"/20*/; do
            [ -e "$dir" ] || continue
            found=true
            local date
            date=$(basename "$dir")
            local files
            files=$(ls "$dir" 2>/dev/null | tr '\n' ', ' | sed 's/,$//')
            echo "  $date — $files"
        done
        if ! $found; then
            echo "  No briefings yet."
        fi
    else
        echo "No briefings yet."
    fi
}

cmd_clean() {
    local cutoff
    cutoff=$(date -v-30d +%Y-%m-%d 2>/dev/null || date -d "30 days ago" +%Y-%m-%d)
    local count=0
    for dir in "$BRIEFINGS_DIR"/20*/; do
        [ -e "$dir" ] || continue
        local date
        date=$(basename "$dir")
        if [[ "$date" < "$cutoff" ]]; then
            echo "Removing $date..."
            rm -rf "$dir"
            count=$((count + 1))
        fi
    done
    echo "Cleaned up $count old briefing(s)."
}

cmd_config() {
    python3 "$CONFIG_PY" show
}

# Main
case "${1:-}" in
    setup)  cmd_setup ;;
    init)   cmd_init ;;
    weather) cmd_weather ;;
    trends) cmd_trends ;;
    webtrends) cmd_webtrends ;;
    crypto) cmd_crypto ;;
    open)   cmd_open ;;
    list)   cmd_list ;;
    clean)  cmd_clean ;;
    config) cmd_config ;;
    *)      usage ;;
esac
