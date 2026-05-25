"""
Integration Example — How to hook Personality Engine into your proactive agent.

Copy this pattern into your agent's trigger handler and engagement loop.
"""

import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path

from personality_engine.engine import PersonalityEngine

logger = logging.getLogger(__name__)


class ProactiveAgent:
    """Example agent with Personality Engine integration."""

    def __init__(self, user_id: str, state_dir: str = None):
        """Initialize agent with personality engine."""
        self.user_id = user_id
        self.engine = PersonalityEngine(user_id, state_dir=state_dir)
        self.message_tracker = {}  # Track sends for engagement

    async def trigger_cross_platform(self):
        """Example: Cross-platform divergence trigger."""
        # Your normal trigger logic: get current market data
        market_data = {
            "spread": 7.5,
            "markets": ["kalshi", "polymarket"],
            "age_hours": 1,
            "last_spread": 7.0,
            "current_spread": 7.5,
        }

        # Generate base message
        base_message = (
            f"Divergence detected:\n"
            f"Kalshi: 52% | Polymarket: 48%\n"
            f"Spread: {market_data['spread']}%"
        )

        # Pass through personality engine
        should_send, scheduled_message = await self.engine.process_trigger(
            trigger_type="cross_platform",
            raw_message=base_message,
            market_data=market_data,
            urgency_context={},
        )

        if should_send:
            # Send message (via iMessage, email, Slack, etc.)
            message_id = await self._send_message(scheduled_message.content)

            # Track for engagement monitoring
            self.message_tracker[message_id] = {
                "trigger_type": "cross_platform",
                "send_time": datetime.now(timezone.utc),
            }

            logger.info(
                f"Sent message {message_id} "
                f"(urgency={scheduled_message.urgency:.2f})"
            )

            # Log in context buffer
            self.engine.context_buffer.log_message(
                "cross_platform",
                market_data,
                scheduled_message.content,
            )
        else:
            logger.info("Trigger held for next cycle")

    async def trigger_portfolio(self):
        """Example: Portfolio P&L trigger."""
        # Get portfolio data
        portfolio_data = {
            "daily_pnl": 12.5,
            "position_changes": 2,
            "daily_return_pct": 2.5,
        }

        base_message = f"Portfolio update: +{portfolio_data['daily_pnl']}% today"

        should_send, scheduled_message = await self.engine.process_trigger(
            trigger_type="portfolio",
            raw_message=base_message,
            market_data=portfolio_data,
            urgency_context={},
        )

        if should_send:
            message_id = await self._send_message(scheduled_message.content)
            self.message_tracker[message_id] = {
                "trigger_type": "portfolio",
                "send_time": datetime.now(timezone.utc),
            }
            self.engine.context_buffer.log_message(
                "portfolio",
                portfolio_data,
                scheduled_message.content,
            )

    async def trigger_x_signals(self):
        """Example: Social signal scanner."""
        # Get signals from your scanner
        signals_data = {
            "topic": "TSLA",
            "confidence": 0.82,
            "position_match": True,
            "mention_count": 45,
        }

        base_message = (
            f"Signal detected: {signals_data['topic']}\n"
            f"Confidence: {signals_data['confidence']:.0%}\n"
            f"Mentions: {signals_data['mention_count']}"
        )

        should_send, scheduled_message = await self.engine.process_trigger(
            trigger_type="x_signals",
            raw_message=base_message,
            market_data=signals_data,
            urgency_context={},
        )

        if should_send:
            message_id = await self._send_message(scheduled_message.content)
            self.message_tracker[message_id] = {
                "trigger_type": "x_signals",
                "send_time": datetime.now(timezone.utc),
            }
            self.engine.context_buffer.log_message(
                "x_signals",
                signals_data,
                scheduled_message.content,
            )

    async def trigger_edge(self):
        """Example: Market edge detection."""
        edge_data = {
            "market": "TSLA Call",
            "edge_size": 2.5,
            "fair_value": 250,
            "market_price": 245,
        }

        base_message = (
            f"Edge detected: {edge_data['market']}\n"
            f"Edge size: {edge_data['edge_size']}%"
        )

        should_send, scheduled_message = await self.engine.process_trigger(
            trigger_type="edge",
            raw_message=base_message,
            market_data=edge_data,
            urgency_context={},
        )

        if should_send:
            message_id = await self._send_message(scheduled_message.content)
            self.message_tracker[message_id] = {
                "trigger_type": "edge",
                "send_time": datetime.now(timezone.utc),
            }
            self.engine.context_buffer.log_message(
                "edge",
                edge_data,
                scheduled_message.content,
            )

    async def trigger_morning_brief(self):
        """Example: Daily morning brief."""
        market_data = {
            "vol": 0.65,
            "divergence_count": 2,
            "edge_count": 3,
            "top_signals": ["AAPL", "TSLA"],
        }

        base_message = "Good morning. Here's today's market brief."

        should_send, scheduled_message = await self.engine.process_trigger(
            trigger_type="morning",
            raw_message=base_message,
            market_data=market_data,
            urgency_context={},
        )

        if should_send:
            message_id = await self._send_message(scheduled_message.content)
            self.message_tracker[message_id] = {
                "trigger_type": "morning",
                "send_time": datetime.now(timezone.utc),
            }
            self.engine.context_buffer.log_message(
                "morning",
                market_data,
                scheduled_message.content,
            )

    async def check_micro_initiations(self):
        """Run micro-initiations check every 30 minutes."""
        # Collect context
        context = {
            "vol": 0.45,
            "trade_count": 120,
            "user_absence_hours": 2,
            "consecutive_positive_days": 3,
            "consecutive_negative_days": 0,
            "has_meetings": False,
        }

        # Evaluate
        micro_message = await self.engine.check_micro_initiations(context)

        if micro_message:
            message_id = await self._send_message(micro_message.content)
            self.message_tracker[message_id] = {
                "trigger_type": "micro_initiation",
                "send_time": datetime.now(timezone.utc),
            }
            self.engine.micro_initiations.log_send("ambient", micro_message.content)

    async def on_user_response(self, message_id: str):
        """Called when user responds to a message."""
        if message_id not in self.message_tracker:
            return

        tracked = self.message_tracker[message_id]
        trigger_type = tracked["trigger_type"]
        send_time = tracked["send_time"]
        response_time = (datetime.now(timezone.utc) - send_time).total_seconds()

        # Log engagement
        self.engine.log_user_engagement(trigger_type, int(response_time))
        self.engine.response_tracker.log_send(trigger_type)

        logger.info(
            f"User engaged with {trigger_type} after {response_time:.0f}s"
        )

    async def on_message_ignored(self, message_id: str):
        """Called after 1+ hour with no response."""
        if message_id not in self.message_tracker:
            return

        tracked = self.message_tracker[message_id]
        trigger_type = tracked["trigger_type"]

        # Log ignore
        self.engine.log_user_ignore(trigger_type)

        logger.info(f"User ignored {trigger_type} message")

    async def _send_message(self, content: str) -> str:
        """
        Send message via iMessage, Slack, email, etc.

        In real implementation, integrate with your transport layer.
        """
        import uuid

        message_id = str(uuid.uuid4())

        # TODO: Implement your transport
        # await imessage_client.send(content)
        # await slack_client.send(content)
        # etc.

        print(f"[{message_id}] Sending: {content[:100]}...")
        return message_id

    def get_status(self):
        """Get current engine status."""
        return self.engine.get_engine_summary()


# ============================================================================
# Main loop / event handlers
# ============================================================================


async def main():
    """Example main loop."""
    agent = ProactiveAgent(user_id="user@example.com")

    # Example: Fire triggers at different times
    print("=== Personality Engine Integration Example ===\n")

    # Morning brief
    await agent.trigger_morning_brief()
    print()

    # Some alerts throughout the day
    await agent.trigger_cross_platform()
    print()

    await agent.trigger_portfolio()
    print()

    await agent.trigger_x_signals()
    print()

    # Micro-initiation check
    await agent.check_micro_initiations()
    print()

    # Simulate user engagement
    print("\n=== Simulating user engagement ===\n")

    # Get message IDs from tracker
    message_ids = list(agent.message_tracker.keys())

    if message_ids:
        # User engages with first message
        first_msg = message_ids[0]
        print(f"User responded to message: {first_msg}")
        await agent.on_user_response(first_msg)
        print()

        # User ignores second message
        if len(message_ids) > 1:
            second_msg = message_ids[1]
            print(f"User ignored message: {second_msg}")
            await agent.on_message_ignored(second_msg)
            print()

    # Print status
    print("\n=== Engine Status ===\n")
    status = agent.get_status()
    import json

    print(json.dumps(status, indent=2))

    # Print engagement metrics
    print("\n=== Engagement Metrics ===\n")
    metrics = agent.engine.response_tracker.get_summary()
    for trigger, data in metrics.items():
        print(f"{trigger}: {data}")


# ============================================================================
# Proactive agent loop (runs continuously)
# ============================================================================


class ContinuousProactiveAgent:
    """Example continuous agent with triggers and micro-initiations."""

    def __init__(self, user_id: str):
        self.agent = ProactiveAgent(user_id)
        self.running = False

    async def run(self):
        """Run agent continuously."""
        self.running = True

        # Your trigger checks (in real impl, these would be event-driven or scheduled)
        tasks = [
            self._morning_brief_cron(),
            self._portfolio_cron(),
            self._micro_initiations_cron(),
        ]

        try:
            await asyncio.gather(*tasks)
        finally:
            self.running = False

    async def _morning_brief_cron(self):
        """Run morning brief at 7 AM daily."""
        # TODO: Use APScheduler or similar
        while self.running:
            await self.agent.trigger_morning_brief()
            await asyncio.sleep(86400)  # Daily

    async def _portfolio_cron(self):
        """Check portfolio every 15 minutes during market hours."""
        while self.running:
            await self.agent.trigger_portfolio()
            await asyncio.sleep(900)  # Every 15 min

    async def _micro_initiations_cron(self):
        """Run micro-initiations every 30 minutes."""
        while self.running:
            await self.agent.check_micro_initiations()
            await asyncio.sleep(1800)  # Every 30 min


# ============================================================================
# Customization example
# ============================================================================


def customize_for_user(agent: ProactiveAgent, user_profile: str):
    """Customize engine for different user types."""

    if user_profile == "aggressive_trader":
        # Low silence threshold (send more)
        agent.engine.selective_silence.SILENCE_THRESHOLDS["vol_floor"] = 0.2
        # Low time-of-day thresholds (send even during quiet hours)
        agent.engine.variable_timing.TIME_OF_DAY_THRESHOLDS[(9, 22)] = 0.3
        # More micro-initiations
        agent.engine.micro_initiations.MICRO_CADENCE["max_per_week"] = 5

    elif user_profile == "conservative_investor":
        # High silence threshold (send less)
        agent.engine.selective_silence.SILENCE_THRESHOLDS["vol_floor"] = 1.5
        # High time-of-day thresholds (quiet hours)
        agent.engine.variable_timing.TIME_OF_DAY_THRESHOLDS[(9, 22)] = 0.7
        # Fewer micro-initiations
        agent.engine.micro_initiations.MICRO_CADENCE["max_per_week"] = 1

    elif user_profile == "email_focused":
        # Add custom pool for email volume
        agent.engine.editorial_voice.add_trigger_voice("email_volume", {
            "high": ["Your inbox is on fire."],
            "moderate": ["Normal email day."],
            "low": ["Quiet inbox."],
        })


if __name__ == "__main__":
    asyncio.run(main())
