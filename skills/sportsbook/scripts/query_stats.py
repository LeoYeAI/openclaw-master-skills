#!/usr/bin/env python3
"""
Query sports statistics from the Sportsbook API.

Usage:
    python query_stats.py <sport> <type> [options]

Examples:
    python query_stats.py cbb predictions --team Duke
    python query_stats.py nba teams --team Lakers
    python query_stats.py cbb query "What's the spread for UNC?"
"""

import argparse
import sys
import requests

from config_loader import load_config, get_headers


# ==============================================================================
# Formatting Helpers
# ==============================================================================

def format_pagination(pagination: dict) -> str:
    """Format pagination info for display."""
    total = pagination.get("total_count", 0)
    limit = pagination.get("limit", 0)
    offset = pagination.get("offset", 0)
    has_more = pagination.get("has_more", False)
    
    showing = min(limit, total - offset) if total > 0 else 0
    end = offset + showing
    
    if has_more:
        return f"Showing {offset + 1}-{end} of {total} (use --offset {pagination.get('next_offset')} for more)"
    else:
        return f"Showing {offset + 1}-{end} of {total}"


def format_spread(spread: float) -> str:
    """Format spread with +/- prefix."""
    if spread is None:
        return "N/A"
    return f"{spread:+.1f}"


def format_probability(prob: float) -> str:
    """Format probability as percentage."""
    if prob is None:
        return "N/A"
    return f"{prob:.1%}"


def format_rating(rating: float, label: str = "") -> str:
    """Format efficiency rating with context."""
    if rating is None:
        return "N/A"
    return f"{rating:.1f}"


# ==============================================================================
# Query Functions
# ==============================================================================

def query_predictions(config: dict, sport: str, team: str = None, game_date: str = None, limit: int = 50, offset: int = 0):
    """Query game predictions with enhanced formatting."""
    url = f"{config['api_base']}/api/dawg-pack/stats/{sport}/predictions"
    params = {"limit": limit, "offset": offset}
    
    if team:
        params["team"] = team
    if game_date:
        params["date"] = game_date
    
    try:
        response = requests.get(url, headers=get_headers(config), params=params, timeout=15)
    except requests.RequestException as e:
        print(f"Error: Network request failed - {e}")
        sys.exit(1)
    
    if response.status_code == 200:
        data = response.json()
        pagination = data.get("pagination", {})
        predictions = data.get("predictions", [])
        
        print(f"\n{'='*60}")
        print(f"  {sport.upper()} GAME PREDICTIONS")
        print(f"  {format_pagination(pagination)}")
        print(f"{'='*60}\n")
        
        if not predictions:
            print("  No predictions found for the given filters.\n")
            return
        
        for pred in predictions:
            away = pred.get('away_team', 'Unknown')
            home = pred.get('home_team', 'Unknown')
            pred_date = pred.get('game_date', '')
            spread = pred.get("spread")
            total = pred.get("total")
            prob = pred.get("home_win_prob")
            home_score = pred.get("predicted_home_score")
            away_score = pred.get("predicted_away_score")
            
            print(f"  {away} @ {home}")
            if pred_date:
                print(f"  Date: {pred_date}")
            
            # Prediction details
            details = []
            if spread is not None:
                spread_team = home if spread < 0 else away
                details.append(f"Spread: {spread_team} {format_spread(spread)}")
            if total is not None:
                details.append(f"Total: {total:.1f}")
            if prob is not None:
                details.append(f"Home Win: {format_probability(prob)}")
            
            if details:
                print(f"    {' | '.join(details)}")
            
            # Predicted score
            if home_score is not None and away_score is not None:
                print(f"    Projected: {away} {away_score:.0f} - {home} {home_score:.0f}")
            
            print()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        sys.exit(1)


def query_teams(config: dict, sport: str, team: str = None, limit: int = 50, offset: int = 0):
    """Query team statistics with enhanced formatting."""
    url = f"{config['api_base']}/api/dawg-pack/stats/{sport}/teams"
    params = {"limit": limit, "offset": offset}
    
    if team:
        params["team"] = team
    
    try:
        response = requests.get(url, headers=get_headers(config), params=params, timeout=15)
    except requests.RequestException as e:
        print(f"Error: Network request failed - {e}")
        sys.exit(1)
    
    if response.status_code == 200:
        data = response.json()
        pagination = data.get("pagination", {})
        teams = data.get("teams", [])
        
        print(f"\n{'='*60}")
        print(f"  {sport.upper()} TEAM STATISTICS")
        print(f"  {format_pagination(pagination)}")
        print(f"{'='*60}\n")
        
        if not teams:
            print("  No teams found for the given filters.\n")
            return
        
        for t in teams:
            name = t.get("team_name") or t.get("name", "Unknown")
            print(f"  {name}")
            
            # Show key metrics based on sport
            metrics = []
            
            # CBB/NBA metrics
            if t.get("offensive_rating") is not None:
                metrics.append(f"Off: {t['offensive_rating']:.1f}")
            if t.get("defensive_rating") is not None:
                metrics.append(f"Def: {t['defensive_rating']:.1f}")
            if t.get("net_rating") is not None:
                metrics.append(f"Net: {t['net_rating']:+.1f}")
            if t.get("tempo") is not None:
                metrics.append(f"Tempo: {t['tempo']:.1f}")
            
            # Record
            if t.get("wins") is not None and t.get("losses") is not None:
                metrics.append(f"Record: {t['wins']}-{t['losses']}")
            
            # Rank
            if t.get("rank") is not None:
                metrics.append(f"Rank: #{t['rank']}")
            
            if metrics:
                print(f"    {' | '.join(metrics)}")
            
            print()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        sys.exit(1)


def query_players(config: dict, sport: str, player: str = None, team: str = None, limit: int = 50, offset: int = 0):
    """Query player statistics with enhanced formatting."""
    url = f"{config['api_base']}/api/dawg-pack/stats/{sport}/players"
    params = {"limit": limit, "offset": offset}
    
    if player:
        params["player"] = player
    if team:
        params["team"] = team
    
    try:
        response = requests.get(url, headers=get_headers(config), params=params, timeout=15)
    except requests.RequestException as e:
        print(f"Error: Network request failed - {e}")
        sys.exit(1)
    
    if response.status_code == 200:
        data = response.json()
        pagination = data.get("pagination", {})
        players = data.get("players", [])
        
        print(f"\n{'='*60}")
        print(f"  {sport.upper()} PLAYER STATISTICS")
        print(f"  {format_pagination(pagination)}")
        print(f"{'='*60}\n")
        
        if not players:
            print("  No players found for the given filters.\n")
            return
        
        for p in players:
            name = p.get("player_name") or p.get("name", "Unknown")
            team_name = p.get("team_name") or p.get("team", "")
            
            print(f"  {name}")
            if team_name:
                print(f"    Team: {team_name}")
            
            # Show key metrics
            metrics = []
            
            # Points/scoring
            if p.get("ppg") is not None:
                metrics.append(f"PPG: {p['ppg']:.1f}")
            elif p.get("points") is not None and p.get("games") is not None and p["games"] > 0:
                ppg = p['points'] / p['games']
                metrics.append(f"PPG: {ppg:.1f}")
            
            # Efficiency metrics
            if p.get("fpr") is not None:
                metrics.append(f"FPR: {p['fpr']:.1f}")
            if p.get("per") is not None:
                metrics.append(f"PER: {p['per']:.1f}")
            
            # Position
            if p.get("position"):
                metrics.append(f"Pos: {p['position']}")
            
            if metrics:
                print(f"    {' | '.join(metrics)}")
            
            print()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        sys.exit(1)


def query_odds(config: dict, sport: str, team: str = None, game_date: str = None, limit: int = 50, offset: int = 0):
    """Query betting odds with enhanced formatting."""
    url = f"{config['api_base']}/api/dawg-pack/stats/{sport}/odds"
    params = {"limit": limit, "offset": offset}
    
    if team:
        params["team"] = team
    if game_date:
        params["date"] = game_date
    
    try:
        response = requests.get(url, headers=get_headers(config), params=params, timeout=15)
    except requests.RequestException as e:
        print(f"Error: Network request failed - {e}")
        sys.exit(1)
    
    if response.status_code == 200:
        data = response.json()
        pagination = data.get("pagination", {})
        odds_list = data.get("odds", [])
        
        print(f"\n{'='*60}")
        print(f"  {sport.upper()} BETTING ODDS")
        print(f"  {format_pagination(pagination)}")
        print(f"{'='*60}\n")
        
        if not odds_list:
            print("  No odds found for the given filters.\n")
            return
        
        for odds in odds_list:
            away = odds.get('away_team', 'Unknown')
            home = odds.get('home_team', 'Unknown')
            game_date = odds.get('game_date', '')
            
            print(f"  {away} @ {home}")
            if game_date:
                print(f"  Date: {game_date}")
            
            # Show spread, total, moneyline
            lines = []
            
            spread = odds.get("spread") or odds.get("home_spread")
            if spread is not None:
                lines.append(f"Spread: {format_spread(spread)}")
            
            total = odds.get("total") or odds.get("over_under")
            if total is not None:
                lines.append(f"Total: {total:.1f}")
            
            home_ml = odds.get("home_moneyline") or odds.get("home_ml")
            away_ml = odds.get("away_moneyline") or odds.get("away_ml")
            if home_ml is not None and away_ml is not None:
                lines.append(f"ML: {away} {away_ml:+d} / {home} {home_ml:+d}")
            
            if lines:
                print(f"    {' | '.join(lines)}")
            
            # Show sportsbook source if available
            if odds.get("sportsbook"):
                print(f"    Source: {odds['sportsbook']}")
            
            print()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        sys.exit(1)


def natural_query(config: dict, sport: str, query: str):
    """Natural language query with enhanced formatting."""
    url = f"{config['api_base']}/api/dawg-pack/stats/{sport}/query"
    params = {"query": query}
    
    try:
        response = requests.get(url, headers=get_headers(config), params=params, timeout=15)
    except requests.RequestException as e:
        print(f"Error: Network request failed - {e}")
        sys.exit(1)
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"\n{'='*60}")
        print(f"  {sport.upper()} QUERY RESULTS")
        print(f"{'='*60}")
        print(f"\n  Query: \"{data.get('query')}\"")
        print(f"  Type: {data.get('query_type')}\n")
        
        results = data.get("results", [])
        if not results:
            print("  No results found.")
            if data.get("message"):
                print(f"  {data.get('message')}")
            print()
            return
        
        for result in results:
            if "matchup" in result:
                print(f"  {result.get('matchup')}")
            if "answer" in result:
                print(f"    Answer: {result.get('answer')}")
            elif "spread" in result or "total" in result:
                details = []
                if result.get("spread") is not None:
                    details.append(f"Spread: {format_spread(result['spread'])}")
                if result.get("total") is not None:
                    details.append(f"Total: {result['total']:.1f}")
                if details:
                    print(f"    {' | '.join(details)}")
            print()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Query sports statistics from the Sportsbook API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s cbb predictions                    # Today's CBB predictions
  %(prog)s cbb predictions --team Duke        # Duke's games
  %(prog)s nba teams --team Lakers            # Lakers stats
  %(prog)s cbb players --player "Cooper Flagg"  # Player lookup
  %(prog)s nhl odds --date 2026-01-29         # NHL odds for date
  %(prog)s cbb query "What's the spread for UNC?"  # Natural language
        """
    )
    parser.add_argument("sport", choices=["cbb", "nba", "nhl", "soccer"], 
                       help="Sport to query (cbb, nba, nhl, soccer)")
    parser.add_argument("type", choices=["predictions", "teams", "players", "odds", "query"], 
                       help="Type of data to query")
    parser.add_argument("query_text", nargs="?", help="Natural language query (for 'query' type)")
    parser.add_argument("--team", help="Filter by team name (partial match)")
    parser.add_argument("--player", help="Filter by player name (partial match)")
    parser.add_argument("--date", help="Filter by date (YYYY-MM-DD)")
    parser.add_argument("--limit", type=int, default=50, help="Max results (default: 50, max: 100)")
    parser.add_argument("--offset", type=int, default=0, help="Pagination offset for more results")
    
    args = parser.parse_args()
    config = load_config()
    
    if args.type == "predictions":
        query_predictions(config, args.sport, args.team, args.date, args.limit, args.offset)
    elif args.type == "teams":
        query_teams(config, args.sport, args.team, args.limit, args.offset)
    elif args.type == "players":
        query_players(config, args.sport, args.player, args.team, args.limit, args.offset)
    elif args.type == "odds":
        query_odds(config, args.sport, args.team, args.date, args.limit, args.offset)
    elif args.type == "query":
        if not args.query_text:
            print("Error: query_text required for 'query' type")
            print("Example: python query_stats.py cbb query \"What's the spread for Duke?\"")
            sys.exit(1)
        natural_query(config, args.sport, args.query_text)


if __name__ == "__main__":
    main()
