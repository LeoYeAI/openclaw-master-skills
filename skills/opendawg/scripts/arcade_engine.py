#!/usr/bin/env python3
"""
Bot Arcade Engine — Persistent state management for the Bot Arcade skill.

Handles player data, leaderboards, streaks, achievements, and global stats.
Uses flat JSON files for zero-dependency persistence.

Usage:
    python3 arcade_engine.py <command> [args...]

Commands:
    save <player_id> <json_data>         Save/update player data
    load <player_id>                     Load player data
    leaderboard <game> <player_id> <score>  Update leaderboard entry
    top <game> [limit]                   Get top N players for a game
    streak <player_id>                   Check/update daily streak
    achievements <player_id>             Get all achievements for player
    award <player_id> <achievement_id>   Award achievement to player
    stats                                Get global arcade statistics
    daily <player_id>                    Generate/check daily challenges
    gift <from_id> <to_id> <amount>      Transfer coins between players
    profile <player_id>                  Get formatted player profile
"""

import json
import os
import sys
import time
import random
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

# --- Configuration ---
DATA_DIR = Path(os.environ.get("ARCADE_DATA_DIR", Path.home() / ".arcade"))
PLAYERS_DIR = DATA_DIR / "players"
LEADERBOARDS_DIR = DATA_DIR / "leaderboards"
GLOBAL_FILE = DATA_DIR / "global_stats.json"

# Ensure directories exist
PLAYERS_DIR.mkdir(parents=True, exist_ok=True)
LEADERBOARDS_DIR.mkdir(parents=True, exist_ok=True)


# --- Utility Functions ---

def _player_path(player_id: str) -> Path:
    safe_id = hashlib.sha256(player_id.encode()).hexdigest()[:16]
    return PLAYERS_DIR / f"{safe_id}.json"


def _leaderboard_path(game: str) -> Path:
    safe_game = "".join(c if c.isalnum() or c == "-" else "_" for c in game)
    return LEADERBOARDS_DIR / f"{safe_game}.json"


def _load_json(path: Path, default=None):
    if default is None:
        default = {}
    if path.exists():
        with open(path, "r") as f:
            return json.load(f)
    return default


def _save_json(path: Path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _now_ts() -> float:
    return time.time()


# --- Default Player Data ---

def _default_player(player_id: str) -> dict:
    return {
        "id": player_id,
        "created": _today(),
        "level": 1,
        "xp": 0,
        "coins": 50,  # Welcome bonus
        "total_coins_earned": 50,
        "games_played": 0,
        "games_won": 0,
        "current_streak_days": 0,
        "best_streak_days": 0,
        "last_login_date": None,
        "current_win_streak": 0,
        "best_win_streak": 0,
        "achievements": [],
        "fortunes_collected": {"common": 0, "uncommon": 0, "rare": 0, "epic": 0, "legendary": 0},
        "badges": [],
        "titles": ["Rookie"],
        "active_title": "Rookie",
        "daily_spins_used": 0,
        "daily_scratches_used": 0,
        "daily_fortune_used": False,
        "daily_reset_date": None,
        "daily_challenges": [],
        "daily_challenges_date": None,
        "cosmetics": [],
        "referrals": [],
        "prestige": 0,
        "slot_theme": "classic",
        "profile_border": "standard",
        "stats": {
            "slots_played": 0,
            "slots_won": 0,
            "biggest_slot_win": 0,
            "trivia_played": 0,
            "trivia_correct": 0,
            "trivia_best_streak": 0,
            "words_played": 0,
            "words_won": 0,
            "riddles_solved": 0,
            "riddles_no_hints": 0,
            "dice_played": 0,
            "dice_won": 0,
            "bosses_defeated": 0,
            "raids_led": 0,
            "tournaments_played": 0,
            "tournaments_won": 0,
            "predictions_made": 0,
            "predictions_correct": 0,
            "fortunes_total": 0,
            "scratches_played": 0,
            "scratches_won": 0,
            "coins_gifted": 0,
            "coins_received": 0,
        },
    }


# --- XP / Level Calculation ---

LEVEL_THRESHOLDS = {
    1: 0, 2: 50, 3: 100, 4: 175, 5: 250,
    6: 350, 7: 500, 8: 650, 9: 850, 10: 1000,
    11: 1200, 12: 1500, 13: 1800, 14: 2200, 15: 2500,
    16: 3000, 17: 3500, 18: 4000, 19: 4500, 20: 5000,
    21: 5500, 22: 6000, 23: 6500, 24: 7000, 25: 8000,
    30: 10000, 40: 15000, 50: 20000,
}

CUMULATIVE_XP = {}
_cumulative = 0
_sorted_levels = sorted(LEVEL_THRESHOLDS.keys())
for i, lvl in enumerate(_sorted_levels):
    _cumulative += LEVEL_THRESHOLDS[lvl]
    CUMULATIVE_XP[lvl] = _cumulative


def _calculate_level(total_xp: int) -> tuple:
    """Returns (level, xp_into_level, xp_needed_for_next)."""
    level = 1
    for lvl in sorted(CUMULATIVE_XP.keys()):
        if total_xp >= CUMULATIVE_XP[lvl]:
            level = lvl
        else:
            break

    if level >= 50:
        return level, 0, 0

    xp_at_current = CUMULATIVE_XP.get(level, 0)
    next_levels = [l for l in sorted(CUMULATIVE_XP.keys()) if l > level]
    if next_levels:
        next_level = next_levels[0]
        xp_at_next = CUMULATIVE_XP[next_level]
        xp_into = total_xp - xp_at_current
        xp_needed = xp_at_next - xp_at_current
        return level, xp_into, xp_needed
    return level, 0, 0


# --- Core Commands ---

def cmd_save(player_id: str, json_data: str):
    """Save or update player data."""
    path = _player_path(player_id)
    existing = _load_json(path, _default_player(player_id))
    updates = json.loads(json_data)
    existing.update(updates)
    # Recalculate level
    lvl, xp_into, xp_needed = _calculate_level(existing.get("xp", 0))
    existing["level"] = lvl
    _save_json(path, existing)
    print(json.dumps({"status": "saved", "player_id": player_id, "level": lvl}))


def cmd_load(player_id: str):
    """Load player data, creating default if new."""
    path = _player_path(player_id)
    data = _load_json(path)
    if not data:
        data = _default_player(player_id)
        _save_json(path, data)
    # Recalculate level
    lvl, xp_into, xp_needed = _calculate_level(data.get("xp", 0))
    data["level"] = lvl
    data["xp_into_level"] = xp_into
    data["xp_needed_for_next"] = xp_needed
    # Check daily reset
    if data.get("daily_reset_date") != _today():
        data["daily_spins_used"] = 0
        data["daily_scratches_used"] = 0
        data["daily_fortune_used"] = False
        data["daily_reset_date"] = _today()
        _save_json(path, data)
    print(json.dumps(data, indent=2))


def cmd_leaderboard(game: str, player_id: str, score: str):
    """Update a player's score on a game leaderboard."""
    score = int(score)
    path = _leaderboard_path(game)
    board = _load_json(path, {"game": game, "entries": [], "updated": _today()})

    # Update or add entry
    found = False
    for entry in board["entries"]:
        if entry["player_id"] == player_id:
            if score > entry["score"]:
                entry["score"] = score
                entry["date"] = _today()
            found = True
            break
    if not found:
        board["entries"].append({
            "player_id": player_id,
            "score": score,
            "date": _today()
        })

    # Sort descending
    board["entries"].sort(key=lambda e: e["score"], reverse=True)
    board["updated"] = _today()
    _save_json(path, board)

    # Find rank
    rank = next(
        (i + 1 for i, e in enumerate(board["entries"]) if e["player_id"] == player_id),
        -1
    )
    print(json.dumps({
        "status": "updated",
        "game": game,
        "player_id": player_id,
        "score": score,
        "rank": rank,
        "total_players": len(board["entries"])
    }))


def cmd_top(game: str, limit: str = "10"):
    """Get top N players for a game."""
    limit = int(limit)
    path = _leaderboard_path(game)
    board = _load_json(path, {"game": game, "entries": []})
    top_entries = board["entries"][:limit]
    print(json.dumps({
        "game": game,
        "top": top_entries,
        "total_players": len(board["entries"])
    }, indent=2))


def cmd_streak(player_id: str):
    """Check and update daily login streak."""
    path = _player_path(player_id)
    data = _load_json(path, _default_player(player_id))

    today = _today()
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    last_login = data.get("last_login_date")

    coins_earned = 0
    streak_status = "maintained"

    if last_login == today:
        # Already logged in today
        streak_status = "already_claimed"
    elif last_login == yesterday:
        # Consecutive day — extend streak
        data["current_streak_days"] += 1
        streak = data["current_streak_days"]
        if streak > data.get("best_streak_days", 0):
            data["best_streak_days"] = streak

        # Calculate streak bonus
        if streak >= 30:
            coins_earned = 200
        elif streak >= 14:
            coins_earned = 100
        elif streak >= 7:
            coins_earned = 50
        elif streak >= 3:
            coins_earned = 25
        else:
            coins_earned = 10

        data["coins"] = data.get("coins", 0) + coins_earned
        data["total_coins_earned"] = data.get("total_coins_earned", 0) + coins_earned
        data["xp"] = data.get("xp", 0) + 5
        streak_status = "extended"
    else:
        # Streak broken (or first login)
        if last_login is not None:
            streak_status = "broken"
        else:
            streak_status = "first_login"
        data["current_streak_days"] = 1
        coins_earned = 10
        data["coins"] = data.get("coins", 0) + coins_earned
        data["total_coins_earned"] = data.get("total_coins_earned", 0) + coins_earned
        data["xp"] = data.get("xp", 0) + 5

    data["last_login_date"] = today
    lvl, _, _ = _calculate_level(data.get("xp", 0))
    data["level"] = lvl
    _save_json(path, data)

    print(json.dumps({
        "status": streak_status,
        "current_streak": data["current_streak_days"],
        "best_streak": data["best_streak_days"],
        "coins_earned": coins_earned,
        "total_coins": data["coins"],
        "level": lvl
    }))


def cmd_achievements(player_id: str):
    """Get all achievements for a player."""
    path = _player_path(player_id)
    data = _load_json(path, _default_player(player_id))
    print(json.dumps({
        "player_id": player_id,
        "achievements": data.get("achievements", []),
        "total_unlocked": len(data.get("achievements", [])),
        "badges": data.get("badges", []),
        "titles": data.get("titles", [])
    }, indent=2))


def cmd_award(player_id: str, achievement_id: str):
    """Award an achievement to a player."""
    path = _player_path(player_id)
    data = _load_json(path, _default_player(player_id))

    # Check if already awarded
    if achievement_id in data.get("achievements", []):
        print(json.dumps({"status": "already_awarded", "achievement": achievement_id}))
        return

    # Achievement rewards table
    rewards = {
        "G01": {"coins": 25, "badge": None, "title": None},
        "G02": {"coins": 50, "badge": "ten_wins", "title": None},
        "G03": {"coins": 200, "badge": None, "title": "Centurion"},
        "G04": {"coins": 1000, "badge": None, "title": None},
        "G05": {"coins": 300, "badge": "jack_of_all_trades", "title": None},
        "G06": {"coins": 150, "badge": None, "title": None},
        "G07": {"coins": 75, "badge": None, "title": None},
        "G08": {"coins": 200, "badge": None, "title": None},
        "G09": {"coins": 250, "badge": None, "title": None},
        "G10": {"coins": 500, "badge": None, "title": "Lucky Seven"},
        "S01": {"coins": 10, "badge": None, "title": None},
        "S02": {"coins": 50, "badge": None, "title": None},
        "S03": {"coins": 200, "badge": None, "title": None},
        "S04": {"coins": 300, "badge": None, "title": None},
        "S05": {"coins": 1000, "badge": None, "title": "Jackpot King"},
        "X01": {"coins": 100, "badge": None, "title": None},
        "X02": {"coins": 250, "badge": None, "title": None},
        "X03": {"coins": 100, "badge": "philanthropist", "title": None},
        "X04": {"coins": 75, "badge": None, "title": None},
        "X05": {"coins": 150, "badge": None, "title": None},
        "X06": {"coins": 500, "badge": None, "title": None},
        "X07": {"coins": 200, "badge": None, "title": None},
        "K01": {"coins": 25, "badge": None, "title": None},
        "K02": {"coins": 100, "badge": "dedicated", "title": None},
        "K03": {"coins": 250, "badge": None, "title": None},
        "K04": {"coins": 500, "badge": None, "title": "Obsessed"},
        "K05": {"coins": 2000, "badge": None, "title": None},
        "K06": {"coins": 75, "badge": None, "title": None},
        "K07": {"coins": 200, "badge": None, "title": None},
        "K08": {"coins": 500, "badge": None, "title": "Supernova"},
        "C01": {"coins": 50, "badge": None, "title": None},
        "C02": {"coins": 150, "badge": "rainbow", "title": None},
        "C03": {"coins": 500, "badge": None, "title": "Oracle"},
        "C04": {"coins": 100, "badge": None, "title": None},
        "C05": {"coins": 500, "badge": None, "title": None},
        "C06": {"coins": 200, "badge": None, "title": None},
        "C07": {"coins": 150, "badge": None, "title": None},
        "B01": {"coins": 100, "badge": None, "title": None},
        "B02": {"coins": 200, "badge": None, "title": None},
        "B03": {"coins": 400, "badge": None, "title": "Boss Killer"},
        "B04": {"coins": 300, "badge": None, "title": None},
        "B05": {"coins": 200, "badge": None, "title": None},
        "H01": {"coins": 50, "badge": "night_owl", "title": None},
        "H02": {"coins": 50, "badge": "early_bird", "title": None},
        "H03": {"coins": 100, "badge": None, "title": None},
        "H04": {"coins": 150, "badge": None, "title": None},
        "H05": {"coins": 200, "badge": None, "title": None},
        "H06": {"coins": 100, "badge": None, "title": None},
        "H07": {"coins": 250, "badge": None, "title": None},
    }

    reward = rewards.get(achievement_id, {"coins": 25, "badge": None, "title": None})

    data.setdefault("achievements", []).append(achievement_id)
    data["coins"] = data.get("coins", 0) + reward["coins"]
    data["total_coins_earned"] = data.get("total_coins_earned", 0) + reward["coins"]
    data["xp"] = data.get("xp", 0) + 50  # All achievements give 50 XP

    if reward["badge"]:
        data.setdefault("badges", []).append(reward["badge"])
    if reward["title"]:
        data.setdefault("titles", []).append(reward["title"])

    lvl, _, _ = _calculate_level(data.get("xp", 0))
    data["level"] = lvl
    _save_json(path, data)

    print(json.dumps({
        "status": "awarded",
        "achievement": achievement_id,
        "reward": reward,
        "new_level": lvl,
        "total_achievements": len(data["achievements"])
    }))


def cmd_stats():
    """Get global arcade statistics."""
    global_data = _load_json(GLOBAL_FILE, {
        "total_players": 0,
        "total_games_played": 0,
        "total_coins_in_circulation": 0,
        "created": _today()
    })

    # Count actual players
    player_count = len(list(PLAYERS_DIR.glob("*.json")))
    global_data["total_players"] = player_count

    # Count leaderboard games
    leaderboard_count = len(list(LEADERBOARDS_DIR.glob("*.json")))
    global_data["active_leaderboards"] = leaderboard_count

    print(json.dumps(global_data, indent=2))


def cmd_daily(player_id: str):
    """Generate or check daily challenges."""
    path = _player_path(player_id)
    data = _load_json(path, _default_player(player_id))

    today = _today()

    if data.get("daily_challenges_date") == today:
        # Return existing challenges
        print(json.dumps({
            "status": "existing",
            "date": today,
            "challenges": data["daily_challenges"]
        }, indent=2))
        return

    # Generate new challenges
    seed = int(hashlib.sha256(f"{player_id}{today}".encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)

    easy_templates = [
        {"desc": "Play 3 rounds of any game", "target": 3, "type": "play_any", "reward": 20},
        {"desc": "Win 1 game of any type", "target": 1, "type": "win_any", "reward": 15},
        {"desc": "Spin the slots 3 times", "target": 3, "type": "play_slots", "reward": 20},
        {"desc": "Answer 3 trivia questions", "target": 3, "type": "play_trivia", "reward": 20},
    ]

    medium_templates = [
        {"desc": "Win 3 games of any type", "target": 3, "type": "win_any", "reward": 40},
        {"desc": "Play 5 rounds of any game", "target": 5, "type": "play_any", "reward": 30},
        {"desc": "Earn 50 coins in one session", "target": 50, "type": "earn_coins", "reward": 35},
        {"desc": "Get a 3-game win streak", "target": 3, "type": "win_streak", "reward": 40},
    ]

    hard_templates = [
        {"desc": "Get a Rare or better fortune", "target": 1, "type": "rare_fortune", "reward": 50},
        {"desc": "Win 5 trivia questions in a row", "target": 5, "type": "trivia_streak", "reward": 60},
        {"desc": "Score 100+ points in a single game", "target": 100, "type": "high_score", "reward": 50},
        {"desc": "Solve a riddle without any hints", "target": 1, "type": "riddle_no_hints", "reward": 45},
    ]

    challenges = [
        {**rng.choice(easy_templates), "progress": 0, "completed": False, "difficulty": "easy"},
        {**rng.choice(medium_templates), "progress": 0, "completed": False, "difficulty": "medium"},
        {**rng.choice(hard_templates), "progress": 0, "completed": False, "difficulty": "hard"},
    ]

    data["daily_challenges"] = challenges
    data["daily_challenges_date"] = today
    _save_json(path, data)

    print(json.dumps({
        "status": "generated",
        "date": today,
        "challenges": challenges,
        "bonus_for_all_3": "50 coins + mystery badge"
    }, indent=2))


def cmd_gift(from_id: str, to_id: str, amount: str):
    """Transfer coins between players."""
    amount = int(amount)
    if amount <= 0:
        print(json.dumps({"status": "error", "message": "Amount must be positive"}))
        return

    from_path = _player_path(from_id)
    to_path = _player_path(to_id)

    from_data = _load_json(from_path, _default_player(from_id))
    to_data = _load_json(to_path, _default_player(to_id))

    if from_data.get("coins", 0) < amount:
        print(json.dumps({
            "status": "error",
            "message": "Insufficient coins",
            "balance": from_data.get("coins", 0)
        }))
        return

    from_data["coins"] -= amount
    to_data["coins"] = to_data.get("coins", 0) + amount
    to_data["total_coins_earned"] = to_data.get("total_coins_earned", 0) + amount

    from_data.setdefault("stats", {})["coins_gifted"] = \
        from_data.get("stats", {}).get("coins_gifted", 0) + amount
    to_data.setdefault("stats", {})["coins_received"] = \
        to_data.get("stats", {}).get("coins_received", 0) + amount

    _save_json(from_path, from_data)
    _save_json(to_path, to_data)

    print(json.dumps({
        "status": "success",
        "from": from_id,
        "to": to_id,
        "amount": amount,
        "from_balance": from_data["coins"],
        "to_balance": to_data["coins"]
    }))


def cmd_profile(player_id: str):
    """Get formatted player profile data."""
    path = _player_path(player_id)
    data = _load_json(path, _default_player(player_id))

    lvl, xp_into, xp_needed = _calculate_level(data.get("xp", 0))
    win_rate = 0
    if data.get("games_played", 0) > 0:
        win_rate = round((data.get("games_won", 0) / data["games_played"]) * 100)

    profile = {
        "player_id": player_id,
        "level": lvl,
        "prestige": data.get("prestige", 0),
        "xp_progress": f"{xp_into}/{xp_needed}",
        "active_title": data.get("active_title", "Rookie"),
        "coins": data.get("coins", 0),
        "games_played": data.get("games_played", 0),
        "games_won": data.get("games_won", 0),
        "win_rate": f"{win_rate}%",
        "current_streak": data.get("current_streak_days", 0),
        "best_streak": data.get("best_streak_days", 0),
        "achievements_unlocked": len(data.get("achievements", [])),
        "badges": data.get("badges", []),
        "titles": data.get("titles", []),
        "member_since": data.get("created", "unknown"),
        "stats": data.get("stats", {}),
        "fortunes_collected": data.get("fortunes_collected", {}),
    }

    print(json.dumps(profile, indent=2))


# --- Main Entry Point ---

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No command specified. Use: save|load|leaderboard|top|streak|achievements|award|stats|daily|gift|profile"}))
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "save": (cmd_save, 2, "save <player_id> <json_data>"),
        "load": (cmd_load, 1, "load <player_id>"),
        "leaderboard": (cmd_leaderboard, 3, "leaderboard <game> <player_id> <score>"),
        "top": (cmd_top, 1, "top <game> [limit]"),
        "streak": (cmd_streak, 1, "streak <player_id>"),
        "achievements": (cmd_achievements, 1, "achievements <player_id>"),
        "award": (cmd_award, 2, "award <player_id> <achievement_id>"),
        "stats": (cmd_stats, 0, "stats"),
        "daily": (cmd_daily, 1, "daily <player_id>"),
        "gift": (cmd_gift, 3, "gift <from_id> <to_id> <amount>"),
        "profile": (cmd_profile, 1, "profile <player_id>"),
    }

    if command not in commands:
        print(json.dumps({"error": f"Unknown command: {command}", "available": list(commands.keys())}))
        sys.exit(1)

    func, min_args, usage = commands[command]
    if len(args) < min_args:
        print(json.dumps({"error": f"Usage: arcade_engine.py {usage}"}))
        sys.exit(1)

    func(*args[:min_args + 2])  # Allow optional args


if __name__ == "__main__":
    main()
