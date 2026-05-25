"""
Response Tracker — Engagement adaptation.

Tracks sends, engagements, ignores, avg_response_time per trigger.
Urgency modifier based on engagement rate.
Auto-suggests adjustments if engagement is low.
"""

import json
import logging
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Any, Optional

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


class ResponseTracker:
    """Track user engagement and adapt urgency/suggestions."""

    # Engagement thresholds
    ENGAGEMENT_THRESHOLDS = {
        "high": 0.70,  # ≥70% → 1.3x urgency
        "low": 0.10,   # <10% → 0.5x urgency
    }

    URGENCY_MULTIPLIERS = {
        "high": 1.3,   # High engagement
        "baseline": 1.0,  # 40-70% engagement
        "low": 0.5,    # Low engagement
    }

    # Engagement window
    ENGAGEMENT_WINDOW_MINUTES = 60

    # Auto-suggestion thresholds
    SUGGESTION_TRIGGERS = {
        "min_sends": 10,
        "max_engagement_for_suggestion": 0.20,  # <20% engagement
    }

    def __init__(self, state_dir: Path):
        """Initialize ResponseTracker."""
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.tracker_file = self.state_dir / "response_tracker.json"
        self._load_tracker()
        logger.debug("ResponseTracker initialized")

    def log_send(self, trigger_type: str) -> None:
        """Log a message send."""
        if trigger_type not in self.tracker:
            self.tracker[trigger_type] = self._fresh_trigger_state()

        self.tracker[trigger_type]["sends"] += 1
        self.tracker[trigger_type]["last_send_time"] = (
            datetime.now(timezone.utc).isoformat()
        )
        self._save_tracker()
        logger.debug(f"[{trigger_type}] Send logged")

    def log_engagement(self, trigger_type: str, response_time_seconds: int) -> None:
        """Log user engagement with a message."""
        if trigger_type not in self.tracker:
            self.tracker[trigger_type] = self._fresh_trigger_state()

        tracker = self.tracker[trigger_type]
        tracker["engagements"] += 1
        tracker["last_engagement"] = datetime.now(timezone.utc).isoformat()

        # Update average response time
        prev_avg = tracker.get("avg_response_time") or 0
        prev_count = max(1, tracker["engagements"] - 1)
        new_avg = (prev_avg * prev_count + response_time_seconds) / tracker["engagements"]
        tracker["avg_response_time"] = round(new_avg, 1)

        self._save_tracker()
        logger.debug(
            f"[{trigger_type}] Engagement logged "
            f"(response: {response_time_seconds}s, avg: {new_avg:.1f}s)"
        )

    def log_ignore(self, trigger_type: str) -> None:
        """Log user ignoring a message (1+ hour passed)."""
        if trigger_type not in self.tracker:
            self.tracker[trigger_type] = self._fresh_trigger_state()

        self.tracker[trigger_type]["ignores"] += 1
        self._save_tracker()
        logger.debug(f"[{trigger_type}] Ignore logged")

    def get_urgency_multiplier(self, trigger_type: str) -> float:
        """
        Get urgency multiplier based on engagement rate.

        Returns:
            Multiplier 0.5x - 1.3x
        """
        if trigger_type not in self.tracker:
            return self.URGENCY_MULTIPLIERS["baseline"]

        tracker = self.tracker[trigger_type]
        engagement_rate = self._calculate_engagement_rate(tracker)

        if engagement_rate >= self.ENGAGEMENT_THRESHOLDS["high"]:
            return self.URGENCY_MULTIPLIERS["high"]
        elif engagement_rate < self.ENGAGEMENT_THRESHOLDS["low"]:
            return self.URGENCY_MULTIPLIERS["low"]
        else:
            return self.URGENCY_MULTIPLIERS["baseline"]

    def get_adjustment_suggestion(self, trigger_type: str) -> Optional[str]:
        """
        Get adjustment suggestion if engagement is low.

        Returns:
            Suggestion string or None
        """
        if trigger_type not in self.tracker:
            return None

        tracker = self.tracker[trigger_type]
        sends = tracker.get("sends", 0)
        engagement_rate = self._calculate_engagement_rate(tracker)

        # Only suggest if enough data and low engagement
        if (sends >= self.SUGGESTION_TRIGGERS["min_sends"] and
            engagement_rate <= self.SUGGESTION_TRIGGERS["max_engagement_for_suggestion"]):

            suggestion = f"""
⚠️ ADJUSTMENT SUGGESTION:
Trigger: {trigger_type}
Sends: {sends} | Engagement: {engagement_rate:.1%} | Avg response: {tracker.get('avg_response_time') or 'N/A'}s

Consider:
→ Lower signal confidence floor (currently 0.65)
→ Reduce frequency (increase silence thresholds)
→ Check if message editorial voice is mismatched to user preference
→ Verify data quality (may be false positives)
"""
            return suggestion.strip()

        return None

    def _calculate_engagement_rate(self, tracker: Dict[str, Any]) -> float:
        """Calculate engagement rate (0.0-1.0)."""
        sends = tracker.get("sends", 0)
        if sends == 0:
            return 0.0

        engagements = tracker.get("engagements", 0)
        ignores = tracker.get("ignores", 0)

        # Only count engagements + ignores (exclude pending)
        responded = engagements + ignores
        if responded == 0:
            return 0.0

        return engagements / responded

    def _can_count_as_engagement(self, send_time: str) -> bool:
        """Check if send is within engagement window."""
        try:
            send_dt = datetime.fromisoformat(send_time)
            now = datetime.now(timezone.utc)
            diff = (now - send_dt).total_seconds() / 60
            return diff <= self.ENGAGEMENT_WINDOW_MINUTES
        except Exception:
            return False

    def purge_old_sends(self, days: int = 30) -> None:
        """
        Purge engagement tracking older than N days (keep sends/engagements counts).

        Args:
            days: Days to retain
        """
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

        for trigger_type, tracker in self.tracker.items():
            # Keep aggregate counts, reset timestamp tracking
            if tracker.get("last_send_time", "") < cutoff:
                tracker["last_send_time"] = None
            if tracker.get("last_engagement", "") < cutoff:
                tracker["last_engagement"] = None

        self._save_tracker()
        logger.info(f"Purged tracking data older than {days} days")

    def get_summary(self) -> Dict[str, Any]:
        """Get engagement summary for all triggers."""
        summary = {}
        for trigger_type, tracker in self.tracker.items():
            sends = tracker.get("sends", 0)
            if sends == 0:
                continue

            engagement_rate = self._calculate_engagement_rate(tracker)
            multiplier = self.get_urgency_multiplier(trigger_type)

            summary[trigger_type] = {
                "sends": sends,
                "engagements": tracker.get("engagements", 0),
                "ignores": tracker.get("ignores", 0),
                "engagement_rate": f"{engagement_rate:.1%}",
                "avg_response_time_s": tracker.get("avg_response_time"),
                "urgency_multiplier": f"{multiplier:.1f}x",
            }

        return summary

    def export_metrics(self, output_file: Optional[Path] = None) -> str:
        """
        Export metrics as CSV for analysis.

        Returns:
            CSV string
        """
        import csv
        from io import StringIO

        output = StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "trigger_type",
                "sends",
                "engagements",
                "ignores",
                "engagement_rate",
                "avg_response_time_s",
                "urgency_multiplier",
            ],
        )
        writer.writeheader()

        for trigger_type, tracker in self.tracker.items():
            engagement_rate = self._calculate_engagement_rate(tracker)
            multiplier = self.get_urgency_multiplier(trigger_type)

            writer.writerow({
                "trigger_type": trigger_type,
                "sends": tracker.get("sends", 0),
                "engagements": tracker.get("engagements", 0),
                "ignores": tracker.get("ignores", 0),
                "engagement_rate": f"{engagement_rate:.1%}",
                "avg_response_time_s": tracker.get("avg_response_time", "N/A"),
                "urgency_multiplier": f"{multiplier:.1f}x",
            })

        csv_content = output.getvalue()

        if output_file:
            with open(output_file, "w") as f:
                f.write(csv_content)
            logger.info(f"Exported metrics to {output_file}")

        return csv_content

    def _fresh_trigger_state(self) -> Dict[str, Any]:
        """Create fresh tracker state for trigger."""
        return {
            "sends": 0,
            "engagements": 0,
            "ignores": 0,
            "avg_response_time": None,
            "last_send_time": None,
            "last_engagement": None,
        }

    def _load_tracker(self) -> None:
        """Load tracker from disk with corruption recovery."""
        data = _safe_load_state(self.tracker_file, default=None)
        if data is not None:
            self.tracker = data
            logger.debug("Loaded response tracker")
        else:
            self.tracker = {}

    def _save_tracker(self) -> None:
        """Save tracker to disk with backup rotation."""
        _safe_save_state(self.tracker_file, self.tracker)

    def reset_tracker(self) -> None:
        """Reset all tracking (use with caution)."""
        self.tracker = {}
        self._save_tracker()
        logger.warning("Response tracker reset")
