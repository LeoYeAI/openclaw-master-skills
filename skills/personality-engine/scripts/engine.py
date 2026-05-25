"""
Personality Engine — Main orchestrator.

Pipeline:
    trigger fires
    → selective_silence (should we stay silent?)
    → urgency_compute (base urgency 0.0-1.0)
    → engagement_modifier (adjust for user response patterns)
    → variable_timing (schedule based on urgency + time of day)
    → context_buffer (add back-references to earlier messages today)
    → editorial_voice (inject personality / opinions)
    → dedup (avoid repeats within rolling window)
    → send

Plus ambient systems:
    - micro_initiations: Unprompted pings when conditions met
    - response_tracker: Monitor engagement; adjust urgency + suggest tuning
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

from .selective_silence import SelectiveSilence
from .variable_timing import VariableTiming
from .editorial_voice import EditorialVoice
from .context_buffer import ContextBuffer
from .response_tracker import ResponseTracker
from .micro_initiations import MicroInitiations

logger = logging.getLogger(__name__)


@dataclass
class ScheduledMessage:
    """Message ready for send with optional delay."""

    content: str
    trigger_type: str
    urgency: float
    delayed: bool = False
    delay_seconds: int = 0
    back_reference: Optional[str] = None
    micro_initiated: bool = False


class PersonalityEngine:
    """Main orchestrator for 6-system personality pipeline."""

    def __init__(self, user_id: str, state_dir: Optional[str] = None):
        """
        Initialize engine.

        Args:
            user_id: User identifier (e.g., email or handle)
            state_dir: Override state directory (default: ~/.openclaw/state/)
        """
        self.user_id = user_id

        # Set state directory
        if state_dir is None:
            state_dir = os.path.expanduser("~/.openclaw/state")
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # Initialize all 6 systems
        self.selective_silence = SelectiveSilence(self.state_dir)
        self.variable_timing = VariableTiming(self.state_dir)
        self.editorial_voice = EditorialVoice()
        self.context_buffer = ContextBuffer(self.state_dir)
        self.response_tracker = ResponseTracker(self.state_dir)
        self.micro_initiations = MicroInitiations(self.state_dir)

        # Dedup tracking (in-memory, rolling 6-hour window)
        self.recent_sends = []  # (trigger_type, timestamp, hash)
        self.dedup_window_seconds = 6 * 3600

        logger.info(f"PersonalityEngine initialized for user {user_id}")

    async def process_trigger(
        self,
        trigger_type: str,
        raw_message: str,
        market_data: Dict[str, Any],
        urgency_context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Optional[ScheduledMessage]]:
        """
        Process a trigger through the full pipeline.

        Args:
            trigger_type: Type of trigger (e.g., 'cross_platform', 'portfolio', 'x_signals')
            raw_message: Base message content from upstream
            market_data: Market/portfolio/context data for enrichment
            urgency_context: Additional context for urgency scoring

        Returns:
            (should_send, ScheduledMessage or None)
        """

        # System 1: Selective Silence
        if self.selective_silence.should_silence(trigger_type, market_data):
            silence_msg = f"Skipped the brief — nothing worth your attention."
            logger.info(f"[{trigger_type}] Silenced by selective_silence")
            return (
                True,
                ScheduledMessage(
                    content=silence_msg,
                    trigger_type=trigger_type,
                    urgency=0.1,
                    micro_initiated=False,
                ),
            )

        # System 2: Urgency Compute
        base_urgency = self.variable_timing.compute_base_urgency(
            trigger_type, market_data
        )
        logger.debug(f"[{trigger_type}] Base urgency: {base_urgency:.2f}")

        # System 3: Engagement Modifier
        engagement_multiplier = self.response_tracker.get_urgency_multiplier(
            trigger_type
        )
        adjusted_urgency = base_urgency * engagement_multiplier
        logger.debug(
            f"[{trigger_type}] Engagement modifier: {engagement_multiplier:.2f} "
            f"→ adjusted urgency: {adjusted_urgency:.2f}"
        )

        # System 4: Variable Timing
        should_send_now, delay_seconds = self.variable_timing.should_send_now(
            adjusted_urgency
        )

        if not should_send_now and delay_seconds == 0:
            logger.info(f"[{trigger_type}] Held for next trigger cycle")
            return (False, None)

        # System 5: Context Buffer (back-references)
        back_reference = self.context_buffer.generate_backreference(
            trigger_type, market_data
        )

        # Enrich message with back-reference
        enriched_message = raw_message
        if back_reference:
            enriched_message = f"{raw_message}\n\n{back_reference}"
            logger.debug(f"[{trigger_type}] Added back-reference: {back_reference[:50]}...")

        # System 6: Editorial Voice
        opinion = self.editorial_voice.inject_opinion(trigger_type, market_data)
        if opinion:
            enriched_message = f"{enriched_message}\n\n{opinion}"
            logger.debug(f"[{trigger_type}] Injected opinion: {opinion[:50]}...")

        # System 7: Dedup
        if self._is_duplicate(trigger_type, enriched_message):
            logger.info(f"[{trigger_type}] Duplicate detected, skipping send")
            return (False, None)

        # Track send
        self._record_send(trigger_type, enriched_message)

        # Log adjustment suggestions if needed
        suggestion = self.response_tracker.get_adjustment_suggestion(trigger_type)
        if suggestion:
            logger.warning(f"[{trigger_type}] Adjustment suggestion:\n{suggestion}")

        # Return scheduled message
        scheduled = ScheduledMessage(
            content=enriched_message,
            trigger_type=trigger_type,
            urgency=adjusted_urgency,
            delayed=delay_seconds > 0,
            delay_seconds=delay_seconds,
            back_reference=back_reference,
            micro_initiated=False,
        )

        logger.info(
            f"[{trigger_type}] Message scheduled "
            f"(urgency={adjusted_urgency:.2f}, delay={delay_seconds}s)"
        )
        return (True, scheduled)

    async def check_micro_initiations(
        self, context: Dict[str, Any]
    ) -> Optional[ScheduledMessage]:
        """
        Check if any micro-initiation conditions are met.

        Args:
            context: Market/user state (vol, trade_count, user_absence_hours, etc.)

        Returns:
            ScheduledMessage or None
        """

        micro_message = self.micro_initiations.evaluate_pools(context)

        if not micro_message:
            return None

        # Check if we've hit cadence limits
        if not self.micro_initiations.should_send_micro_initiation():
            logger.debug("Micro-initiation cadence limit reached")
            return None

        logger.info(f"Micro-initiation triggered: {micro_message[:50]}...")

        scheduled = ScheduledMessage(
            content=micro_message,
            trigger_type="micro_initiation",
            urgency=0.5,
            delayed=False,
            micro_initiated=True,
        )

        # Track in context buffer
        self.context_buffer.log_message("micro_initiation", {}, micro_message)

        return scheduled

    def log_user_engagement(
        self, trigger_type: str, response_time_seconds: int
    ) -> None:
        """
        Log user engagement with a message.

        Args:
            trigger_type: Type of trigger that was engaged
            response_time_seconds: Time from send to engagement
        """
        self.response_tracker.log_engagement(trigger_type, response_time_seconds)
        logger.info(
            f"[{trigger_type}] Engagement logged "
            f"(response time: {response_time_seconds}s)"
        )

    def log_user_ignore(self, trigger_type: str) -> None:
        """
        Log user ignoring a message (1+ hour passed).

        Args:
            trigger_type: Type of trigger that was ignored
        """
        self.response_tracker.log_ignore(trigger_type)
        logger.info(f"[{trigger_type}] Message ignored")

    def _is_duplicate(self, trigger_type: str, message: str) -> bool:
        """Check if message is duplicate within rolling window."""
        import hashlib

        msg_hash = hashlib.md5(message.encode()).hexdigest()
        now = datetime.now(timezone.utc).timestamp()

        # Clean old sends
        self.recent_sends = [
            (t, ts, h)
            for t, ts, h in self.recent_sends
            if now - ts < self.dedup_window_seconds
        ]

        # Check for duplicate
        for t, ts, h in self.recent_sends:
            if t == trigger_type and h == msg_hash:
                return True

        return False

    def _record_send(self, trigger_type: str, message: str) -> None:
        """Record a send for dedup tracking."""
        import hashlib

        msg_hash = hashlib.md5(message.encode()).hexdigest()
        now = datetime.now(timezone.utc).timestamp()
        self.recent_sends.append((trigger_type, now, msg_hash))

    def reset_daily_context(self) -> None:
        """Manually reset daily context (auto-resets at midnight)."""
        self.context_buffer.reset_daily()
        logger.info("Daily context reset")

    def get_engine_summary(self) -> Dict[str, Any]:
        """
        Get summary of current engine state.

        Returns:
            Dict with per-system metrics
        """
        return {
            "user_id": self.user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "response_tracker": self.response_tracker.get_summary(),
            "recent_sends_count": len(self.recent_sends),
            "context_buffer_size": self.context_buffer.get_size(),
        }
