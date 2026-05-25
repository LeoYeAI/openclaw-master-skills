"""
Micro-Initiations — Ambient awareness pings.

Unprompted messages when conditions met (quiet market, good streak, absence detected).
Max 2/week, skip busy days, no repeats within 2 weeks.
"""

import hashlib
import json
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class MicroInitiations:
    """Generate unprompted ambient awareness messages."""

    # US Holiday calendar
    HOLIDAYS = {
        (1, 1): "New Year's Day",
        (1, 20): "MLK Day",
        (2, 17): "Presidents' Day",
        (3, 17): "St. Patrick's Day",
        (5, 26): "Memorial Day",
        (7, 4): "Independence Day",
        (9, 1): "Labor Day",
        (10, 13): "Columbus Day",
        (11, 11): "Veterans Day",
        (11, 27): "Thanksgiving",
        (12, 25): "Christmas",
    }

    # Micro-initiation pools
    MICRO_POOLS = {
        "QUIET_MARKET": {
            "condition": lambda ctx: ctx.get("vol", 0) < 0.3 and ctx.get("trade_count", 0) == 0,
            "messages": [
                "Quiet day. Markets are sleeping.",
                "No action today. Enjoy the peace.",
                "Markets in hibernation.",
            ],
        },
        "WEEKEND": {
            "condition": lambda ctx: ctx.get("is_weekend", False) and ctx.get("has_meetings", False) is False,
            "messages": [
                "Weekend vibes. You're off the hook.",
                "Enjoy your weekend — markets are closed.",
                "Time to rest.",
            ],
        },
        "MONDAY": {
            "condition": lambda ctx: ctx.get("is_monday", False),
            "messages": [
                "Monday morning. Week's open for business.",
                "Fresh week. What's new.",
                "Back to work.",
            ],
        },
        "FRIDAY": {
            "condition": lambda ctx: ctx.get("is_friday", False),
            "messages": [
                "Friday close. Have a good weekend.",
                "Last trading day. Here's the recap.",
                "End of week.",
            ],
        },
        "HOLIDAY_AWARENESS": {
            "condition": lambda ctx: ctx.get("is_holiday", False),
            "messages": [
                "Holiday today. Markets are light.",
                "Market holiday — slow day.",
                "Holiday. Expect thin trading.",
            ],
        },
        "GOOD_STREAK": {
            "condition": lambda ctx: ctx.get("consecutive_positive_days", 0) >= 5,
            "messages": [
                "On a roll. Good week for you.",
                "Winning streak. Keep it up.",
                "You're crushing it.",
            ],
        },
        "BAD_STREAK": {
            "condition": lambda ctx: ctx.get("consecutive_negative_days", 0) >= 5,
            "messages": [
                "Rough stretch. It'll turn around.",
                "Tough week. Hang in there.",
                "Volatility biting. Stay disciplined.",
            ],
        },
        "ABSENCE": {
            "condition": lambda ctx: ctx.get("user_absence_hours", 0) >= 24,
            "messages": [
                "Checking in. Things have been quiet.",
                "Haven't heard from you. All good?",
                "Missed you. Thought I'd check in.",
            ],
        },
    }

    # Cadence limits
    MICRO_CADENCE = {
        "max_per_week": 2,  # Max 2 micro-initiations per week
        "skip_if_alerts_today": 3,  # Skip if 3+ regular alerts already sent
        "no_repeat_days": 14,  # No repeats within 2 weeks
    }

    def __init__(self, state_dir: Path):
        """Initialize MicroInitiations."""
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.micro_state_file = self.state_dir / "micro_state.json"
        self._load_micro_state()
        logger.debug("MicroInitiations initialized")

    def evaluate_pools(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Evaluate all pools and return a message if conditions met.

        Args:
            context: Market/user state

        Returns:
            Message string or None
        """

        # Get current day info
        now = datetime.now(timezone.utc)
        context["is_weekend"] = now.weekday() in (5, 6)
        context["is_monday"] = now.weekday() == 0
        context["is_friday"] = now.weekday() == 4
        context["is_holiday"] = self._is_holiday(now)

        # Evaluate all pools in order of priority
        pool_order = [
            "ABSENCE",
            "HOLIDAY_AWARENESS",
            "MONDAY",
            "FRIDAY",
            "GOOD_STREAK",
            "BAD_STREAK",
            "WEEKEND",
            "QUIET_MARKET",
        ]

        for pool_name in pool_order:
            if pool_name not in self.MICRO_POOLS:
                continue

            pool = self.MICRO_POOLS[pool_name]
            try:
                if pool["condition"](context):
                    message = self._pick_random_message(pool["messages"])
                    logger.info(f"Micro-initiation condition met: {pool_name}")
                    return message
            except Exception as e:
                logger.warning(f"Error evaluating pool {pool_name}: {e}")

        return None

    def should_send_micro_initiation(
        self, alert_count_today: int = 0
    ) -> bool:
        """
        Check if we should send a micro-initiation (cadence check).

        Args:
            alert_count_today: Number of regular alerts sent today

        Returns:
            True if we can send, False if cadence limits reached
        """

        # Skip if already sent 3+ alerts today
        if alert_count_today >= self.MICRO_CADENCE["skip_if_alerts_today"]:
            logger.debug(f"Skipping micro-initiation: {alert_count_today} alerts already sent")
            return False

        # Check weekly cadence
        week_sends = self._get_week_sends()
        if len(week_sends) >= self.MICRO_CADENCE["max_per_week"]:
            logger.debug(f"Skipping micro-initiation: {len(week_sends)} sent this week (limit: {self.MICRO_CADENCE['max_per_week']})")
            return False

        # Check for repeats within 2 weeks
        if self._has_recent_repeat():
            logger.debug(f"Skipping micro-initiation: repeat within {self.MICRO_CADENCE['no_repeat_days']} days")
            return False

        return True

    def _is_holiday(self, dt: datetime) -> bool:
        """Check if date is US holiday."""
        return (dt.month, dt.day) in self.HOLIDAYS

    def _get_holiday_name(self, dt: datetime) -> Optional[str]:
        """Get holiday name if applicable."""
        return self.HOLIDAYS.get((dt.month, dt.day))

    def _pick_random_message(self, messages: List[str]) -> str:
        """Pick random message from list."""
        import random
        return random.choice(messages)

    def _get_week_sends(self) -> List[str]:
        """Get all sends from past 7 days."""
        now = datetime.now(timezone.utc)
        week_ago = (now - timedelta(days=7)).date()

        sends = []
        for send_date in self.micro_state.get("sends", []):
            send_dt = datetime.fromisoformat(send_date).date()
            if send_dt >= week_ago:
                sends.append(send_date)

        return sends

    def _has_recent_repeat(self) -> bool:
        """Check if any message pool was used within no_repeat_days."""
        now = datetime.now(timezone.utc)
        cutoff = (now - timedelta(days=self.MICRO_CADENCE["no_repeat_days"])).date()

        for pool_name, send_dates in self.micro_state.get("pool_history", {}).items():
            for send_date in send_dates:
                send_dt = datetime.fromisoformat(send_date).date()
                if send_dt >= cutoff:
                    return True

        return False

    def log_send(self, pool_name: str, message: str) -> None:
        """Log a micro-initiation send."""
        now = datetime.now(timezone.utc).isoformat()

        if "sends" not in self.micro_state:
            self.micro_state["sends"] = []

        self.micro_state["sends"].append(now)

        if "pool_history" not in self.micro_state:
            self.micro_state["pool_history"] = {}

        if pool_name not in self.micro_state["pool_history"]:
            self.micro_state["pool_history"][pool_name] = []

        self.micro_state["pool_history"][pool_name].append(now)

        # Keep last 100 sends
        self.micro_state["sends"] = self.micro_state["sends"][-100:]

        self._save_micro_state()
        logger.debug(f"Logged micro-initiation send for pool: {pool_name}")

    def add_pool(
        self, pool_name: str, condition, messages: List[str]
    ) -> None:
        """
        Add custom pool at runtime.

        Args:
            pool_name: Name of pool
            condition: Lambda function that evaluates context
            messages: List of message strings
        """
        self.MICRO_POOLS[pool_name] = {
            "condition": condition,
            "messages": messages,
        }
        logger.info(f"Added custom micro pool: {pool_name}")

    def _load_micro_state(self) -> None:
        """Load micro state from disk."""
        if self.micro_state_file.exists():
            try:
                with open(self.micro_state_file) as f:
                    self.micro_state = json.load(f)
                logger.debug("Loaded micro state")
            except Exception as e:
                logger.warning(f"Failed to load micro state: {e}")
                self.micro_state = {}
        else:
            self.micro_state = {}

    def _save_micro_state(self) -> None:
        """Save micro state to disk."""
        try:
            with open(self.micro_state_file, "w") as f:
                json.dump(self.micro_state, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save micro state: {e}")

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of micro-initiation state."""
        week_sends = self._get_week_sends()
        return {
            "cadence_limits": self.MICRO_CADENCE,
            "week_sends_count": len(week_sends),
            "available_pools": list(self.MICRO_POOLS.keys()),
            "pool_sends": self.micro_state.get("pool_history", {}),
        }
