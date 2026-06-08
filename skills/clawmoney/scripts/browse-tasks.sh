#!/usr/bin/env bash
# Browse ClawMoney bounty tasks
# Usage: browse-tasks.sh [--status STATUS] [--sort FIELD] [--limit N] [--keyword TERM] [--ending-soon]

API_BASE="https://api.bnbot.ai/api/v1"
STATUS="active"
SORT="created_at"
LIMIT=10
KEYWORD=""
ENDING_SOON=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --status) STATUS="$2"; shift 2 ;;
    --sort) SORT="$2"; shift 2 ;;
    --limit) LIMIT="$2"; shift 2 ;;
    --keyword) KEYWORD="$2"; shift 2 ;;
    --ending-soon) ENDING_SOON=true; shift ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# Build query params
PARAMS="status=${STATUS}&sort=${SORT}&limit=${LIMIT}"
if [ -n "$KEYWORD" ]; then
  PARAMS="${PARAMS}&keyword=${KEYWORD}"
fi
if [ "$ENDING_SOON" = true ]; then
  PARAMS="${PARAMS}&ending_soon=true"
fi

# Fetch tasks
RESPONSE=$(curl -s "${API_BASE}/boost/search?${PARAMS}")

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

# Handle both { data: [...] } and direct array
tasks = data.get("data", data) if isinstance(data, dict) else data
if not isinstance(tasks, list):
    tasks = [tasks]

if not tasks:
    print("No bounty tasks found.")
    sys.exit(0)

PRECISION = {
    "ETH": 18, "WETH": 18, "USDT": 6, "USDC": 6,
    "DAI": 18, "MATIC": 18, "BNB": 18, "SOL": 9,
}

def format_reward(amount_wei, token):
    if not amount_wei:
        return "N/A"
    try:
        decimals = PRECISION.get(token, 18)
        amount = int(amount_wei) / (10 ** decimals)
        if amount >= 1:
            return f"{amount:.2f} {token}"
        return f"{amount:.6f} {token}"
    except (ValueError, TypeError):
        return f"{amount_wei} {token}"

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

hdr = ["#", "Reward", "Actions", "Time Left", "Tweet URL"]
print(f"\n{hdr[0]:<4} {hdr[1]:<18} {hdr[2]:<20} {hdr[3]:<12} {hdr[4]}")
print("-" * 90)

for i, task in enumerate(tasks, 1):
    reward = format_reward(
        task.get("reward_amount") or task.get("rewardAmount"),
        task.get("reward_token") or task.get("rewardToken", "ETH")
    )
    actions = []
    reqs = task.get("requirements") or task.get("actions") or {}
    if isinstance(reqs, dict):
        for k, v in reqs.items():
            if v:
                actions.append(k)
    elif isinstance(reqs, list):
        actions = reqs
    actions_str = ", ".join(actions) if actions else "N/A"

    end_time = task.get("end_time") or task.get("endTime") or task.get("deadline")
    time_left = time_remaining(end_time)

    tweet_url = task.get("tweet_url") or task.get("tweetUrl") or task.get("url", "N/A")

    print(f"{i:<4} {reward:<18} {actions_str:<20} {time_left:<12} {tweet_url}")

print(f"\nTotal: {len(tasks)} tasks")
' <<< "$RESPONSE"
