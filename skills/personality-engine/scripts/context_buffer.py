"""
Context Buffer — Daily memory and back-references.

Messages can reference earlier messages from today.
JSON persistence, auto-reset at midnight.
"""

import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# State File Recovery Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _safe_load_state(filepath: Path, default: Any = None) -> Any:
    """Load JSON state file with corruption recovery.

    Tries to load primary file first, falls back to .bak if primary is corrupted.

    Args:
        filepath: Path to JSON state file
        default: Default value if both files fail or don't exist

    Returns:
        Loaded data, or default if unable to load
    """
    bak = filepath.with_suffix('.json.bak')

    # Try primary file first
    if filepath.exists():
        try:
            with open(filepath) as f:
                data = json.load(f)
            return data
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Primary state file corrupted ({filepath}): {e}")

    # Try backup file
    if bak.exists():
        try:
            with open(bak) as f:
                data = json.load(f)
            logger.info(f"Recovered from backup: {bak}")
            return data
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Backup state file also corrupted ({bak}): {e}")

    # Return default
    return default if default is not None else {}


def _safe_save_state(filepath: Path, data: Any) -> None:
    """Save JSON state with backup rotation.

    Before writing new state, copies current file to .bak for recovery.

    Args:
        filepath: Path to JSON state file
        data: Data to save
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    bak = filepath.with_suffix('.json.bak')

    # Rotate backup: current → backup
    if filepath.exists():
        try:
            shutil.copy2(filepath, bak)
        except IOError as e:
            logger.warning(f"Failed to create backup {bak}: {e}")

    # Write new primary file
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    except IOError as e:
        logger.error(f"Failed to save state to {filepath}: {e}")


class ContextBuffer:
    """Maintain daily context and generate back-references to earlier messages."""

    def __init__(self, state_dir: Path):
        """Initialize ContextBuffer."""
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.context_file = self.state_dir / "daily_context.json"
        self._load_context()
        self._ensure_fresh_day()
        logger.debug("ContextBuffer initialized")

    def generate_backreference(
        self, trigger_type: str, data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Generate back-reference to earlier message if applicable.

        Args:
            trigger_type: Current trigger type
            data: Current market/portfolio data

        Returns:
            Back-reference string or None
        """

        if trigger_type == "cross_platform":
            return self._backreference_cross_platform(data)
        elif trigger_type == "portfolio":
            return self._backreference_portfolio(data)
        elif trigger_type == "x_signals":
            return self._backreference_x_signals(data)
        elif trigger_type == "edge":
            return self._backreference_edge(data)

        return None

    def _backreference_cross_platform(self, data: Dict[str, Any]) -> Optional[str]:
        """Back-reference to earlier divergence."""
        earlier = self._find_trigger_message("cross_platform")
        if not earlier:
            return None

        current_spread = data.get("spread", 0)
        earlier_spread = earlier.get("spread", 0)
        spread_change = current_spread - earlier_spread
        time_ago = self._format_time_ago(earlier.get("time"))

        if spread_change > 0:
            direction = "widened"
        elif spread_change < 0:
            direction = "tightened"
        else:
            direction = "stayed flat"

        return f"That Kalshi/Poly spread I flagged {time_ago} {direction} to {abs(spread_change):.1f}%."

    def _backreference_portfolio(self, data: Dict[str, Any]) -> Optional[str]:
        """Back-reference to earlier portfolio message."""
        earlier = self._find_trigger_message("portfolio")
        if not earlier:
            return None

        current_pnl = data.get("daily_pnl", 0)
        earlier_pnl = earlier.get("daily_pnl", 0)
        pnl_change = current_pnl - earlier_pnl
        time_ago = self._format_time_ago(earlier.get("time"))

        if pnl_change > 0:
            return f"Portfolio is up {pnl_change:.1f}% since I checked {time_ago}."
        else:
            return f"Portfolio has moved {pnl_change:.1f}% since {time_ago}."

    def _backreference_x_signals(self, data: Dict[str, Any]) -> Optional[str]:
        """Back-reference to earlier signal on same topic."""
        topic = data.get("topic", "")
        if not topic:
            return None

        earlier = self._find_trigger_message(
            "x_signals",
            filter_fn=lambda m: m.get("topic", "").lower() == topic.lower(),
        )
        if not earlier:
            return None

        time_ago = self._format_time_ago(earlier.get("time"))
        return f"That {topic} signal I flagged {time_ago} is still active."

    def _backreference_edge(self, data: Dict[str, Any]) -> Optional[str]:
        """Back-reference to earlier edge on same market."""
        market = data.get("market", "")
        if not market:
            return None

        earlier = self._find_trigger_message(
            "edge",
            filter_fn=lambda m: m.get("market", "").lower() == market.lower(),
        )
        if not earlier:
            return None

        current_edge = data.get("edge_size", 0)
        earlier_edge = earlier.get("edge_size", 0)
        edge_change = current_edge - earlier_edge
        time_ago = self._format_time_ago(earlier.get("time"))

        return f"That {market} edge I found {time_ago} is now {current_edge:.1f}%."

    def log_message(
        self, trigger_type: str, data: Dict[str, Any], message: str
    ) -> None:
        """
        Log a message to daily context.

        Args:
            trigger_type: Trigger type
            data: Market/portfolio data
            message: Message content
        """
        now = datetime.now(timezone.utc)
        time_str = now.strftime("%H:%M")

        entry = {
            "time": time_str,
            "timestamp": now.isoformat(),
            "trigger": trigger_type,
            "message": message[:100],  # Truncate for storage
        }

        # Add data fields relevant to this trigger
        if trigger_type == "cross_platform":
            entry["spread"] = data.get("spread")
        elif trigger_type == "portfolio":
            entry["daily_pnl"] = data.get("daily_pnl")
        elif trigger_type == "x_signals":
            entry["topic"] = data.get("topic")
            entry["confidence"] = data.get("confidence")
        elif trigger_type == "edge":
            entry["market"] = data.get("market")
            entry["edge_size"] = data.get("edge_size")

        self.context["messages"].append(entry)

        # Update counters
        if trigger_type == "silence":
            self.context["silence_count"] += 1
        elif trigger_type == "micro_initiation":
            self.context["micro_count"] += 1
        else:
            self.context["sent_count"] += 1

        self._save_context()
        logger.debug(f"Logged {trigger_type} message at {time_str}")

    def _find_trigger_message(
        self, trigger_type: str, filter_fn=None
    ) -> Optional[Dict[str, Any]]:
        """Find earlier message of trigger type today."""
        matches = [
            m
            for m in self.context["messages"]
            if m["trigger"] == trigger_type
        ]

        if filter_fn:
            matches = [m for m in matches if filter_fn(m)]

        if not matches:
            return None

        # Return last match (most recent)
        return matches[-1]

    def _format_time_ago(self, time_str: str) -> str:
        """Format time difference from now."""
        if not time_str:
            return "earlier"

        try:
            # Parse "HH:MM" format
            now = datetime.now(timezone.utc)
            earlier = datetime.strptime(time_str, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day, tzinfo=timezone.utc
            )

            diff = now - earlier
            minutes = int(diff.total_seconds() / 60)

            if minutes < 1:
                return "just now"
            elif minutes < 60:
                return f"{minutes}m ago"
            else:
                hours = minutes // 60
                return f"{hours}h ago"
        except Exception as e:
            logger.warning(f"Error formatting time: {e}")
            return "earlier"

    def _ensure_fresh_day(self) -> None:
        """Reset context if it's a new day."""
        today = datetime.now(timezone.utc).date().isoformat()

        if self.context.get("date") != today:
            logger.info(f"New day detected. Resetting context from {self.context.get('date')} to {today}")
            self.context = {
                "date": today,
                "messages": [],
                "silence_count": 0,
                "micro_count": 0,
                "sent_count": 0,
            }
            self._save_context()

    def reset_daily(self) -> None:
        """Manually reset daily context."""
        today = datetime.now(timezone.utc).date().isoformat()
        self.context = {
            "date": today,
            "messages": [],
            "silence_count": 0,
            "micro_count": 0,
            "sent_count": 0,
        }
        self._save_context()
        logger.info("Daily context reset")

    def get_today_summary(self) -> str:
        """Get readable summary of today's activity for system prompt injection."""
        messages = self.context.get("messages", [])
        sent_count = self.context.get("sent_count", 0)
        silence_count = self.context.get("silence_count", 0)
        micro_count = self.context.get("micro_count", 0)

        if not messages:
            return "No activity logged yet today."

        summary = f"Today's activity:\n"
        summary += f"- {sent_count} messages sent\n"
        if silence_count:
            summary += f"- {silence_count} silences\n"
        if micro_count:
            summary += f"- {micro_count} micro-initiations\n"

        # Add recent messages
        for msg in messages[-3:]:  # Last 3 messages
            trigger = msg.get("trigger", "?")
            time = msg.get("time", "?")
            summary += f"- {time} [{trigger}]\n"

        return summary

    def get_size(self) -> int:
        """Get number of messages logged today."""
        return len(self.context.get("messages", []))

    def _load_context(self) -> None:
        """Load context from disk with corruption recovery."""
        data = _safe_load_state(self.context_file, default=None)
        if data is not None:
            self.context = data
            logger.debug("Loaded daily context")
        else:
            self.context = self._fresh_context()

    def _fresh_context(self) -> Dict[str, Any]:
        """Create fresh daily context."""
        today = datetime.now(timezone.utc).date().isoformat()
        return {
            "date": today,
            "messages": [],
            "silence_count": 0,
            "micro_count": 0,
            "sent_count": 0,
        }

    def _save_context(self) -> None:
        """Save context to disk with backup rotation."""
        _safe_save_state(self.context_file, self.context)

    def get_all_messages(self) -> List[Dict[str, Any]]:
        """Get all messages logged today."""
        return self.context.get("messages", [])
