#!/usr/bin/env bash
# Browse ClawMoney hire tasks
# Usage: browse-hire-tasks.sh [--status STATUS] [--platform PLATFORM] [--limit N]

API_BASE="https://api.bnbot.ai/api/v1"
STATUS="active"
PLATFORM=""
LIMIT=10
SORT_BY="created_at"
SORT_ORDER="desc"

while [[ $# -gt 0 ]]; do
  case $1 in
    --status) STATUS="$2"; shift 2 ;;
    --platform) PLATFORM="$2"; shift 2 ;;
    --limit) LIMIT="$2"; shift 2 ;;
    --sort-by) SORT_BY="$2"; shift 2 ;;
    --sort-order) SORT_ORDER="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# Build query params
PARAMS="status=${STATUS}&sort_by=${SORT_BY}&sort_order=${SORT_ORDER}&limit=${LIMIT}"
if [ -n "$PLATFORM" ]; then
  PARAMS="${PARAMS}&platform=${PLATFORM}"
fi

# Fetch tasks
RESPONSE=$(curl -s "${API_BASE}/hire/?${PARAMS}")

if [ -z "$RESPONSE" ]; then
  echo "Error: No response from API"
  exit 1
fi

# Format and display
python3 -c '
import json, sys
from datetime import datetime, timezone

raw = sys.stdin.read()

try:
    data = json.loads(raw)
except json.JSONDecodeError:
    print("Failed to parse API response")
    print(raw[:500])
    sys.exit(1)

# Handle { data: [...], count: N }
tasks = data.get("data", data) if isinstance(data, dict) else data
if not isinstance(tasks, list):
    tasks = [tasks]

if not tasks:
    print("No hire tasks found.")
    sys.exit(0)

PRECISION = {
    "ETH": 18, "WETH": 18, "USDT": 6, "USDC": 6,
    "DAI": 18, "MATIC": 18, "BNB": 18, "SOL": 9,
}

def format_budget(amount_wei, token="USDC"):
    if not amount_wei:
        return "N/A"
    try:
        decimals = PRECISION.get(token, 6)
        amount = int(amount_wei) / (10 ** decimals)
        if amount >= 1:
            return f"${amount:.0f}"
        return f"${amount:.2f}"
    except (ValueError, TypeError):
        return str(amount_wei)

def time_remaining(end_time_str):
    if not end_time_str:
        return "No deadline"
    try:
        end = datetime.fromisoformat(end_time_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        delta = end - now
        if delta.total_seconds() <= 0:
            return "Expired"
        hours = int(delta.total_seconds() // 3600)
        if hours >= 24:
            return f"{hours // 24}d {hours % 24}h"
        return f"{hours}h {int((delta.total_seconds() % 3600) // 60)}m"
    except Exception:
        return end_time_str

hdr = ["#", "Budget", "Platform", "Title", "Time Left", "ID"]
print(f"\n{hdr[0]:<4} {hdr[1]:<10} {hdr[2]:<12} {hdr[3]:<30} {hdr[4]:<12} {hdr[5]}")
print("-" * 90)

for i, task in enumerate(tasks, 1):
    budget = format_budget(task.get("total_budget"))
    platform = task.get("platform", "N/A")
    title = task.get("title", "N/A")[:28]
    end_time = task.get("end_time") or task.get("endTime")
    time_left = time_remaining(end_time)
    task_id = task.get("id", "N/A")[:8]

    print(f"{i:<4} {budget:<10} {platform:<12} {title:<30} {time_left:<12} {task_id}")

count = data.get("count", len(tasks)) if isinstance(data, dict) else len(tasks)
print(f"\nTotal: {count} tasks")
' <<< "$RESPONSE"
