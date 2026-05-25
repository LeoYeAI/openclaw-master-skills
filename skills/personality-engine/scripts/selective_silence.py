"""
Selective Silence — Knowing when NOT to talk.

Content quality checks per trigger. Deliberate silence messages.
Max 1 silence message per day.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class SelectiveSilence:
    """Determine if a trigger should be silenced due to low content quality."""

    # Content quality thresholds
    SILENCE_THRESHOLDS = {
        "vol_floor": 0.5,  # % vol for morning silence
        "divergence_age_limit": 3,  # hours
        "divergence_spread_movement": 0.5,  # % spread change required
        "signal_confidence_floor": 0.65,
        "edge_floor": 1.0,  # %
        "portfolio_flat_range": 2.0,  # % P&L range
    }

    def __init__(self, state_dir: Path):
        """Initialize SelectiveSilence."""
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.silence_state_file = self.state_dir / "silence_state.json"
        self._load_silence_state()
        logger.debug("SelectiveSilence initialized")

    def should_silence(self, trigger_type: str, data: Dict[str, Any]) -> bool:
        """
        Determine if trigger should be silenced.

        Args:
            trigger_type: Type of trigger
            data: Market/portfolio data

        Returns:
            True if should silence, False if should send
        """

        if trigger_type == "morning":
            return self._should_silence_morning(data)
        elif trigger_type == "cross_platform":
            return self._should_silence_divergence(data)
        elif trigger_type == "x_signals":
            return self._should_silence_signals(data)
        elif trigger_type == "edge":
            return self._should_silence_edge(data)
        elif trigger_type == "portfolio":
            return self._should_silence_portfolio(data)
        else:
            return False

    def _should_silence_morning(self, data: Dict[str, Any]) -> bool:
        """Silence morning brief if boring."""
        vol = data.get("vol", 0)
        divergence_count = data.get("divergence_count", 0)
        edge_count = data.get("edge_count", 0)

        # All three conditions must be met for silence
        boring = vol < self.SILENCE_THRESHOLDS["vol_floor"]
        no_divergences = divergence_count == 0
        no_edges = edge_count == 0

        if boring and no_divergences and no_edges:
            if self._can_send_silence_message("morning"):
                return True

        return False

    def _should_silence_divergence(self, data: Dict[str, Any]) -> bool:
        """Silence stale divergence."""
        age_hours = data.get("age_hours", 0)
        last_spread = data.get("last_spread", None)
        current_spread = data.get("current_spread", None)

        # Check if stale
        if age_hours >= self.SILENCE_THRESHOLDS["divergence_age_limit"]:
            # Check if spread has moved significantly
            if last_spread and current_spread:
                spread_change = abs(current_spread - last_spread)
                if spread_change < self.SILENCE_THRESHOLDS["divergence_spread_movement"]:
                    if self._can_send_silence_message("cross_platform"):
                        return True

        return False

    def _should_silence_signals(self, data: Dict[str, Any]) -> bool:
        """Silence if all signals are noise."""
        signals = data.get("signals", [])
        confidence_floor = self.SILENCE_THRESHOLDS["signal_confidence_floor"]

        if not signals:
            return False

        # Check if all signals are low confidence and no position matches
        all_low_confidence = all(s.get("confidence", 0) < confidence_floor for s in signals)
        no_position_matches = all(not s.get("position_match", False) for s in signals)

        if all_low_confidence and no_position_matches:
            if self._can_send_silence_message("x_signals"):
                return True

        return False

    def _should_silence_edge(self, data: Dict[str, Any]) -> bool:
        """Silence if all edges are thin."""
        edges = data.get("edges", [])
        edge_floor = self.SILENCE_THRESHOLDS["edge_floor"]

        if not edges:
            return False

        # Check if all edges are below floor
        all_thin = all(e.get("size", 0) < edge_floor for e in edges)

        if all_thin:
            if self._can_send_silence_message("edge"):
                return True

        return False

    def _should_silence_portfolio(self, data: Dict[str, Any]) -> bool:
        """Silence if portfolio is flat."""
        daily_pnl = data.get("daily_pnl", 0)
        position_changes = data.get("position_changes", 0)
        flat_range = self.SILENCE_THRESHOLDS["portfolio_flat_range"]

        # Flat if P&L is within range AND no major position changes
        is_flat = abs(daily_pnl) < flat_range
        no_position_changes = position_changes == 0

        if is_flat and no_position_changes:
            if self._can_send_silence_message("portfolio"):
                return True

        return False

    def _can_send_silence_message(self, trigger_type: str) -> bool:
        """
        Check if we can send silence message for this trigger today.

        Max 1 silence message per day per trigger type.
        """
        today = datetime.now(timezone.utc).date().isoformat()

        if today not in self.silence_state:
            self.silence_state[today] = {}

        if trigger_type in self.silence_state[today]:
            # Already sent silence for this trigger today
            return False

        # Mark as sent
        self.silence_state[today][trigger_type] = True
        self._save_silence_state()

        logger.debug(f"Silence message allowed for {trigger_type} today")
        return True

    def _load_silence_state(self) -> None:
        """Load silence state from disk."""
        if self.silence_state_file.exists():
            try:
                with open(self.silence_state_file) as f:
                    self.silence_state = json.load(f)
                logger.debug(f"Loaded silence state: {self.silence_state}")
            except Exception as e:
                logger.warning(f"Failed to load silence state: {e}")
                self.silence_state = {}
        else:
            self.silence_state = {}

        # Clean old dates (older than 7 days)
        today = datetime.now(timezone.utc).date().isoformat()
        from datetime import timedelta

        cutoff_date = (datetime.fromisoformat(today) - timedelta(days=7)).date().isoformat()
        self.silence_state = {
            date: data
            for date, data in self.silence_state.items()
            if date >= cutoff_date
        }

    def _save_silence_state(self) -> None:
        """Save silence state to disk."""
        try:
            with open(self.silence_state_file, "w") as f:
                json.dump(self.silence_state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save silence state: {e}")

    def reset_daily(self) -> None:
        """Reset daily silence counter (called at midnight)."""
        today = datetime.now(timezone.utc).date().isoformat()
        if today in self.silence_state:
            del self.silence_state[today]
        self._save_silence_state()
        logger.info("Daily silence state reset")

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of silence state."""
        return {
            "thresholds": self.SILENCE_THRESHOLDS,
            "silence_counts": {
                date: len(triggers)
                for date, triggers in self.silence_state.items()
            },
        }
