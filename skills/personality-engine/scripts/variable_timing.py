"""
Variable Timing — Urgency scoring 0.0-1.0 with time-of-day awareness.

Modifiers: weekend, clustering prevention, daily fatigue, random jitter.
"""

import logging
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)


class VariableTiming:
    """Score urgency and determine delivery timing."""

    # Time-of-day thresholds (hour: minimum urgency required to send)
    TIME_OF_DAY_THRESHOLDS = {
        (0, 7): 0.90,  # midnight - 7 AM (sleep time)
        (7, 9): 0.75,  # 7 - 9 AM (morning crunch)
        (9, 22): 0.45,  # 9 AM - 10 PM (daytime, lower bar)
        (22, 23): 0.35,  # 10 - 11 PM (wind-down)
        (23, 24): 0.85,  # 11 PM - midnight (late night, high bar)
    }

    # Urgency modifiers
    WEEKEND_MODIFIER = 0.10  # +0.10 on weekends
    CLUSTERING_PREVENTION = 0.20  # -0.20 if sent <10 min ago
    DAILY_FATIGUE_STEP = 0.20  # +0.20 threshold per 10 messages
    JITTER_RANGE = 0.05  # ±5% random variation

    def __init__(self, state_dir: Path):
        """Initialize VariableTiming."""
        self.state_dir = Path(state_dir)
        self.last_send_time = None
        logger.debug("VariableTiming initialized")

    def compute_base_urgency(self, trigger_type: str, data: Dict[str, Any]) -> float:
        """
        Compute base urgency (0.0-1.0) for trigger type.

        Args:
            trigger_type: Type of trigger
            data: Market/portfolio data

        Returns:
            Base urgency score 0.0-1.0
        """

        if trigger_type == "cross_platform":
            return self._urgency_cross_platform(data)
        elif trigger_type == "portfolio":
            return self._urgency_portfolio(data)
        elif trigger_type == "x_signals":
            return self._urgency_x_signals(data)
        elif trigger_type == "edge":
            return self._urgency_edge(data)
        elif trigger_type == "meeting":
            return self._urgency_meeting(data)
        else:
            return 0.5  # Default medium urgency

    def _urgency_cross_platform(self, data: Dict[str, Any]) -> float:
        """Urgency based on spread size."""
        spread = data.get("spread", 0)
        # 0% spread = 0.0, 5% spread = 0.3, 10%+ spread = 1.0
        urgency = min(1.0, (spread / 10.0) * 0.6)
        return max(0.0, urgency)

    def _urgency_portfolio(self, data: Dict[str, Any]) -> float:
        """Urgency based on portfolio P&L."""
        daily_pnl = data.get("daily_pnl", 0)
        # ±0% = 0.0, ±10% = 0.7, ±15%+ = 1.0
        urgency = min(1.0, (abs(daily_pnl) / 10.0) * 0.7)
        return max(0.0, urgency)

    def _urgency_x_signals(self, data: Dict[str, Any]) -> float:
        """Urgency based on signal confidence and position match."""
        confidence = data.get("confidence", 0.0)
        position_match = data.get("position_match", False)
        # Confidence 0.7-1.0 maps to 0.56-0.8, +0.2 if position match
        confidence_portion = confidence * 0.8
        match_bonus = 0.2 if position_match else 0.0
        urgency = confidence_portion + match_bonus
        return min(1.0, max(0.0, urgency))

    def _urgency_edge(self, data: Dict[str, Any]) -> float:
        """Urgency based on edge size."""
        edge_size = data.get("edge_size", 0)
        # 0% edge = 0.0, 2% edge = 0.32, 5%+ edge = 1.0
        urgency = min(1.0, (edge_size / 5.0) * 0.8)
        return max(0.0, urgency)

    def _urgency_meeting(self, data: Dict[str, Any]) -> float:
        """Urgency based on minutes until meeting."""
        minutes_away = data.get("minutes_away", 120)
        # 120 min away = 0.0, 30 min away = 0.75, 0 min away = 1.0
        urgency = max(0.0, 1.0 - (minutes_away / 120.0))
        return min(1.0, urgency)

    def should_send_now(
        self, adjusted_urgency: float
    ) -> Tuple[bool, int]:
        """
        Determine if we should send now and any delay.

        Args:
            adjusted_urgency: Urgency after engagement modifier

        Returns:
            (should_send_now, delay_seconds)
            If should_send_now=False and delay_seconds=0, hold for next trigger.
        """

        # Get current time-of-day threshold
        now = datetime.now(timezone.utc)
        threshold = self._get_time_of_day_threshold(now)

        # Apply modifiers
        final_threshold = threshold
        final_threshold = self._apply_weekend_modifier(final_threshold, now)
        final_threshold = self._apply_clustering_prevention(final_threshold)
        final_threshold = self._apply_daily_fatigue(final_threshold)

        # Apply jitter
        jitter = random.uniform(-self.JITTER_RANGE, self.JITTER_RANGE)
        final_urgency = adjusted_urgency + jitter

        logger.debug(
            f"Timing check: urgency={final_urgency:.2f} vs threshold={final_threshold:.2f}"
        )

        if final_urgency >= final_threshold:
            self.last_send_time = now
            return (True, 0)
        else:
            return (False, 0)

    def _get_time_of_day_threshold(self, dt: datetime) -> float:
        """Get threshold for current time of day."""
        hour = dt.hour

        for (start_hour, end_hour), threshold in self.TIME_OF_DAY_THRESHOLDS.items():
            if start_hour <= hour < end_hour:
                return threshold

        # Default fallback (shouldn't reach)
        return 0.75

    def _apply_weekend_modifier(self, threshold: float, dt: datetime) -> float:
        """Apply weekend modifier (lower threshold = send more)."""
        # 5 = Saturday, 6 = Sunday
        if dt.weekday() in (5, 6):
            logger.debug(f"Weekend detected, reducing threshold by {self.WEEKEND_MODIFIER}")
            return max(0.0, threshold - self.WEEKEND_MODIFIER)
        return threshold

    def _apply_clustering_prevention(self, threshold: float) -> float:
        """Apply clustering prevention (reduce if recent send)."""
        if self.last_send_time is None:
            return threshold

        now = datetime.now(timezone.utc)
        seconds_since_send = (now - self.last_send_time).total_seconds()

        if seconds_since_send < 600:  # 10 minutes
            adjustment = (600 - seconds_since_send) / 600 * self.CLUSTERING_PREVENTION
            logger.debug(f"Clustering prevention: raising threshold by {adjustment:.2f}")
            return threshold + adjustment

        return threshold

    def _apply_daily_fatigue(self, threshold: float) -> float:
        """Apply daily fatigue modifier (raise threshold if many messages sent today)."""
        # This would typically be passed in from engine tracking
        # For now, simple implementation: could be enhanced with actual message count
        # In real integration, pass message_count_today to engine.process_trigger
        return threshold

    def apply_daily_fatigue_modifier(
        self, threshold: float, message_count_today: int
    ) -> float:
        """Apply fatigue modifier based on today's message count."""
        if message_count_today >= 10:
            fatigue_steps = (message_count_today - 10) // 5
            adjustment = fatigue_steps * self.DAILY_FATIGUE_STEP
            logger.debug(
                f"Daily fatigue: {message_count_today} messages, "
                f"raising threshold by {adjustment:.2f}"
            )
            return threshold + adjustment
        return threshold

    def get_urgency_summary(self) -> Dict[str, Any]:
        """Get summary of current timing state."""
        return {
            "time_of_day_thresholds": self.TIME_OF_DAY_THRESHOLDS,
            "modifiers": {
                "weekend": self.WEEKEND_MODIFIER,
                "clustering_prevention": self.CLUSTERING_PREVENTION,
                "daily_fatigue_step": self.DAILY_FATIGUE_STEP,
                "jitter_range": self.JITTER_RANGE,
            },
        }
