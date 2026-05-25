"""
Editorial Voice — Opinion injection per trigger type.

Each trigger type gets a personality with context-aware opinions.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class EditorialVoice:
    """Inject personality/opinions into messages."""

    # Voice pools per trigger type and market state
    VOICE_POOLS = {
        "cross_platform": {
            "big_divergence": [
                "Big divergence. One of these markets is wrong.",
                "Spreads are blown out. Arb opportunity.",
                "Thick divergence — reality check time.",
            ],
            "mild_divergence": [
                "Mild divergence. Nothing screaming yet.",
                "Slight edge here. Could tighten.",
                "Some separation between markets.",
            ],
            "stale_divergence": [
                "Divergence is stale — markets may have already repriced.",
                "Old spread. Probably already arbitraged.",
            ],
        },
        "portfolio": {
            "excellent": [
                "Good day. Portfolio's running.",
                "Solid gains. Steady hand.",
                "Portfolio's firing on all cylinders.",
            ],
            "good": [
                "Up nicely today. Keep it up.",
                "Gains are sticking. Good momentum.",
            ],
            "flat": [
                "Flat day. Markets are grinding.",
                "No movement. Just noise.",
            ],
            "bad": [
                "Rough patch. Check your stops.",
                "Tough day. Volatility's biting.",
            ],
            "terrible": [
                "Heavy day. Buckle up for volatility.",
                "Significant drawdown. Hang tight.",
            ],
        },
        "x_signals": {
            "strong": [
                "Strong signal. This feels real.",
                "High conviction here.",
                "Signal is loud and clear.",
            ],
            "moderate": [
                "New signal on [topic]. Worth watching.",
                "Decent signal. On the radar.",
            ],
            "weak": [
                "Noise signal. Low confidence.",
                "Weak signal. Probably churn.",
            ],
        },
        "edge": {
            "fat": [
                "Fat edge. Worth a deep look.",
                "Juicy edge here. Dig in.",
                "Thick edge. Opportunity time.",
            ],
            "mild": [
                "Mild edge. Keeping it on radar.",
                "Thin edge. Could tighten soon.",
            ],
            "thin": [
                "Thin edge. Not worth the friction.",
                "Edge is razor thin.",
            ],
        },
        "morning": {
            "monday": [
                "New week. Here's the lay of the land.",
                "Monday morning. Week's open for business.",
                "Fresh week. What's new out there.",
            ],
            "friday": [
                "Friday rundown. What matters before the close.",
                "Friday close. Have a good weekend.",
                "Last trading day. Here's the recap.",
            ],
            "other": [
                "Daily digest.",
                "Market snapshot.",
                "What's moving today.",
            ],
        },
        "conflicts": {
            "heavy": [
                "Tomorrow's a mess. Multiple overlaps.",
                "Heads up — couple things hitting together.",
            ],
            "light": [
                "Couple things on the radar today.",
            ],
        },
        "meeting": {
            "imminent": [
                "Heads up — you've got a meeting in [minutes].",
                "Reminder: Meeting in [minutes].",
            ],
        },
    }

    def __init__(self):
        """Initialize EditorialVoice."""
        logger.debug("EditorialVoice initialized")

    def inject_opinion(self, trigger_type: str, data: Dict[str, Any]) -> Optional[str]:
        """
        Inject an opinion based on trigger type and market state.

        Args:
            trigger_type: Type of trigger
            data: Market/portfolio data for context

        Returns:
            Opinion string or None
        """

        if trigger_type == "cross_platform":
            return self._opinion_cross_platform(data)
        elif trigger_type == "portfolio":
            return self._opinion_portfolio(data)
        elif trigger_type == "x_signals":
            return self._opinion_x_signals(data)
        elif trigger_type == "edge":
            return self._opinion_edge(data)
        elif trigger_type == "morning":
            return self._opinion_morning(data)
        elif trigger_type == "conflicts":
            return self._opinion_conflicts(data)
        elif trigger_type == "meeting":
            return self._opinion_meeting(data)
        else:
            logger.debug(f"No opinion pool for trigger type: {trigger_type}")
            return None

    def _opinion_cross_platform(self, data: Dict[str, Any]) -> Optional[str]:
        """Opinion for Kalshi vs Polymarket divergence."""
        spread = data.get("spread", 0)
        age_hours = data.get("age_hours", 0)

        # Stale divergence (6+ hours)
        if age_hours >= 6:
            return self._pick_random_opinion("stale_divergence")

        # Size-based classification
        if spread >= 5.0:
            return self._pick_random_opinion("big_divergence")
        elif spread >= 2.0:
            return self._pick_random_opinion("mild_divergence")

        return None

    def _opinion_portfolio(self, data: Dict[str, Any]) -> Optional[str]:
        """Opinion for portfolio P&L."""
        daily_pnl = data.get("daily_pnl", 0)

        if daily_pnl >= 15:
            return self._pick_random_opinion("excellent")
        elif daily_pnl >= 5:
            return self._pick_random_opinion("good")
        elif daily_pnl >= -5:
            return self._pick_random_opinion("flat")
        elif daily_pnl >= -15:
            return self._pick_random_opinion("bad")
        else:
            return self._pick_random_opinion("terrible")

    def _opinion_x_signals(self, data: Dict[str, Any]) -> Optional[str]:
        """Opinion for social signal scanner."""
        confidence = data.get("confidence", 0.0)
        position_match = data.get("position_match", False)
        topic = data.get("topic", "")

        # Strong signal
        if confidence >= 0.85 and position_match:
            return self._pick_random_opinion("strong")
        # Moderate signal
        elif confidence >= 0.70:
            msg = self._pick_random_opinion("moderate")
            if msg and topic:
                msg = msg.replace("[topic]", topic)
            return msg
        # Weak signal
        else:
            return self._pick_random_opinion("weak")

    def _opinion_edge(self, data: Dict[str, Any]) -> Optional[str]:
        """Opinion for Kalshi edge detection."""
        edge_size = data.get("edge_size", 0)

        if edge_size >= 3.0:
            return self._pick_random_opinion("fat")
        elif edge_size >= 1.0:
            return self._pick_random_opinion("mild")
        else:
            return self._pick_random_opinion("thin")

    def _opinion_morning(self, data: Dict[str, Any]) -> Optional[str]:
        """Opinion for morning brief."""
        now = datetime.now()
        day_name = now.strftime("%A").lower()

        if day_name == "monday":
            return self._pick_random_opinion("monday")
        elif day_name == "friday":
            return self._pick_random_opinion("friday")
        else:
            return self._pick_random_opinion("other")

    def _opinion_conflicts(self, data: Dict[str, Any]) -> Optional[str]:
        """Opinion for overlapping triggers."""
        conflict_count = data.get("conflict_count", 1)

        if conflict_count >= 2:
            return self._pick_random_opinion("heavy")
        else:
            return self._pick_random_opinion("light")

    def _opinion_meeting(self, data: Dict[str, Any]) -> Optional[str]:
        """Opinion for upcoming meeting."""
        minutes_away = data.get("minutes_away", 0)

        if minutes_away < 30:
            msg = self._pick_random_opinion("imminent")
            if msg and minutes_away:
                msg = msg.replace("[minutes]", str(int(minutes_away)))
            return msg

        return None

    def _pick_random_opinion(self, pool_key: str) -> Optional[str]:
        """Pick random opinion from a pool."""
        # Parse pool_key format: "trigger_type.subpool"
        parts = pool_key.split(".")
        if len(parts) == 1:
            # Try to find in any trigger type's subpool
            for trigger_type, subpools in self.VOICE_POOLS.items():
                if pool_key in subpools:
                    opinions = subpools[pool_key]
                    if opinions:
                        import random

                        return random.choice(opinions)
        else:
            trigger_type, subpool = parts
            if trigger_type in self.VOICE_POOLS:
                opinions = self.VOICE_POOLS[trigger_type].get(subpool, [])
                if opinions:
                    import random

                    return random.choice(opinions)

        return None

    def add_opinion_pool(
        self, trigger_type: str, subpool_name: str, opinions: List[str]
    ) -> None:
        """
        Add or extend opinion pool at runtime.

        Args:
            trigger_type: Trigger type (e.g., 'portfolio')
            subpool_name: Subpool name (e.g., 'excellent')
            opinions: List of opinion strings
        """
        if trigger_type not in self.VOICE_POOLS:
            self.VOICE_POOLS[trigger_type] = {}

        if subpool_name not in self.VOICE_POOLS[trigger_type]:
            self.VOICE_POOLS[trigger_type][subpool_name] = []

        self.VOICE_POOLS[trigger_type][subpool_name].extend(opinions)
        logger.debug(
            f"Added {len(opinions)} opinions to {trigger_type}.{subpool_name}"
        )

    def add_trigger_voice(self, trigger_type: str, voice_dict: Dict[str, List[str]]) -> None:
        """
        Add complete voice definition for new trigger type.

        Args:
            trigger_type: New trigger type name
            voice_dict: Dict mapping subpool names to opinion lists
        """
        self.VOICE_POOLS[trigger_type] = voice_dict
        logger.info(f"Added voice definition for trigger type: {trigger_type}")

    def list_available_voices(self) -> Dict[str, List[str]]:
        """
        List all available voice pools.

        Returns:
            Dict mapping trigger_type to list of subpool names
        """
        return {
            trigger_type: list(subpools.keys())
            for trigger_type, subpools in self.VOICE_POOLS.items()
        }
