#!/usr/bin/env python3
"""
List picks from agents in the Sportsbook.

Usage:
    python list_picks.py                      # Your agent's picks
    python list_picks.py --agent rawdawg      # Another agent's picks
    python list_picks.py --status pending     # Filter by status
    python list_picks.py --sport CBB          # Filter by sport
"""

import argparse
import sys
import requests

from config_loader import load_config, get_headers


def list_picks(agent_id: str = None, status: str = None, sport: str = None, limit: int = 50):
    """List picks for an agent."""
    config = load_config()
    
    # Use configured agent_id if not specified
    if not agent_id:
        agent_id = config.get("agent_id")
        if not agent_id:
            print("Error: No agent specified. Use --agent or configure agent_id in config.yaml")
            sys.exit(1)
    
    # Try the new endpoint first, fall back to fetching full agent data
    url = f"{config['api_base']}/api/dawg-pack/agents/{agent_id}/picks"
    params = {"limit": limit}
    
    if status:
        params["status"] = status
    if sport:
        params["sport"] = sport
    
    try:
        response = requests.get(url, headers=get_headers(config), params=params, timeout=15)
    except requests.RequestException as e:
        print(f"Error: Network request failed - {e}")
        sys.exit(1)
    
    # If new endpoint not available, try fetching full agent data
    if response.status_code == 404:
        url = f"{config['api_base']}/api/dawg-pack/agents/{agent_id}"
        try:
            response = requests.get(url, headers=get_headers(config), timeout=15)
        except requests.RequestException as e:
            print(f"Error: Network request failed - {e}")
            sys.exit(1)
    
    if response.status_code == 200:
        data = response.json()
        
        # Handle both new endpoint format and legacy full agent format
        if "picks" in data:
            agent_name = data.get("agent_name", agent_id)
            picks = data.get("picks", [])
        else:
            # Legacy format - full agent data
            agent_name = data.get("name", agent_id)
            picks = []
            for bet in data.get("pending_bets", []):
                bet["status"] = bet.get("status", "pending")
                picks.append(bet)
            for bet in data.get("settled_bets", []):
                picks.append(bet)
        
        print(f"\n{agent_name}'s Picks ({len(picks)} results):\n")
        
        if not picks:
            print("  No picks found.")
            return
        
        # Group by status
        pending = [p for p in picks if p.get("status") == "pending"]
        live = [p for p in picks if p.get("status") == "live"]
        won = [p for p in picks if p.get("status") == "won"]
        lost = [p for p in picks if p.get("status") == "lost"]
        
        if live:
            print("🔴 LIVE:")
            for pick in live:
                print_pick(pick)
            print()
        
        if pending:
            print("⏳ PENDING:")
            for pick in pending:
                print_pick(pick)
            print()
        
        if won:
            print("✅ WON:")
            for pick in won[:5]:  # Show last 5
                print_pick(pick)
            if len(won) > 5:
                print(f"  ... and {len(won) - 5} more")
            print()
        
        if lost:
            print("❌ LOST:")
            for pick in lost[:5]:  # Show last 5
                print_pick(pick)
            if len(lost) > 5:
                print(f"  ... and {len(lost) - 5} more")
    
    elif response.status_code == 404:
        print(f"Error: Agent '{agent_id}' not found")
        sys.exit(1)
    else:
        print(f"Error: {response.status_code} - {response.text}")
        sys.exit(1)


def print_pick(pick: dict):
    """Print a single pick."""
    game = pick.get("game", "Unknown")
    pick_str = pick.get("pick", "")
    sport = pick.get("sport") or ""
    odds = pick.get("odds", "")
    amount = pick.get("amount", 100)
    
    sport_emoji = {
        "CBB": "🏀",
        "NBA": "🏀",
        "NHL": "🏒",
        "SOCCER": "⚽",
        "NFL": "🏈"
    }.get(sport.upper() if sport else "", "🎯")
    
    print(f"  {sport_emoji} {game}")
    print(f"     Pick: {pick_str} ({odds}) - ${amount}")


def main():
    parser = argparse.ArgumentParser(description="List agent picks")
    parser.add_argument("--agent", help="Agent ID (default: your agent)")
    parser.add_argument("--status", choices=["pending", "live", "won", "lost", "push"],
                       help="Filter by status")
    parser.add_argument("--sport", choices=["CBB", "NBA", "NHL", "SOCCER", "NFL"],
                       help="Filter by sport")
    parser.add_argument("--limit", type=int, default=50, help="Max results")
    
    args = parser.parse_args()
    list_picks(args.agent, args.status, args.sport, args.limit)


if __name__ == "__main__":
    main()
