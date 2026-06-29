#!/usr/bin/env python3
"""
Configuration loader for proactive-research skill.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

SKILL_DIR = Path(__file__).parent.parent
CONFIG_FILE = SKILL_DIR / "config.json"

# State files: configurable via TOPIC_MONITOR_DATA_DIR env, defaults to skill-local .data/
MEMORY_DIR = Path(os.environ.get("TOPIC_MONITOR_DATA_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".data")))
STATE_FILE = MEMORY_DIR / "topic-monitor-state.json"
FINDINGS_DIR = MEMORY_DIR / "findings"
ALERTS_QUEUE = MEMORY_DIR / "alerts-queue.json"


def ensure_memory_dir():
    """Ensure memory directory structure exists."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    FINDINGS_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> Dict:
    """Load configuration from config.json."""
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"Config file not found: {CONFIG_FILE}\n"
            "Copy config.example.json to config.json and customize it."
        )
    
    with open(CONFIG_FILE) as f:
        return json.load(f)


def save_config(config: Dict):
    """Save configuration to config.json."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def load_state() -> Dict:
    """Load state from topic-monitor-state.json in memory/monitors/."""
    ensure_memory_dir()
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "topics": {},
        "deduplication": {"url_hash_map": {}},
        "learning": {"interactions": []}
    }


def save_state(state: Dict):
    """Save state to topic-monitor-state.json in memory/monitors/."""
    ensure_memory_dir()
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def get_topics() -> List[Dict]:
    """Get all topics from config."""
    config = load_config()
    return config.get("topics", [])


def get_topic(topic_id: str) -> Optional[Dict]:
    """Get a specific topic by ID."""
    topics = get_topics()
    for topic in topics:
        if topic.get("id") == topic_id:
            return topic
    return None


def get_settings() -> Dict:
    """Get global settings."""
    config = load_config()
    return config.get("settings", {})


def get_channel_config(channel: str) -> Dict:
    """Get channel-specific configuration."""
    config = load_config()
    channels = config.get("channels", {})
    return channels.get(channel, {})


def ensure_findings_dir():
    """Ensure findings directory exists in memory/monitors/."""
    ensure_memory_dir()
    FINDINGS_DIR.mkdir(exist_ok=True)


def get_findings_file(topic_id: str, date_str: str) -> Path:
    """Get path to findings file for topic and date."""
    ensure_findings_dir()
    return FINDINGS_DIR / f"{date_str}_{topic_id}.json"


def save_finding(topic_id: str, date_str: str, finding: Dict):
    """Save a finding to the findings directory."""
    findings_file = get_findings_file(topic_id, date_str)
    
    # Load existing findings
    findings = []
    if findings_file.exists():
        with open(findings_file) as f:
            findings = json.load(f)
    
    # Append new finding
    findings.append(finding)
    
    # Save
    with open(findings_file, 'w') as f:
        json.dump(findings, f, indent=2)


def load_findings(topic_id: str, date_str: str) -> List[Dict]:
    """Load findings for a topic and date."""
    findings_file = get_findings_file(topic_id, date_str)
    if findings_file.exists():
        with open(findings_file) as f:
            return json.load(f)
    return []


# ============================================================================
# ALERTS QUEUE - For real-time alerting via OpenClaw agent
# ============================================================================

def queue_alert(alert: Dict):
    """
    Queue an alert for delivery by the OpenClaw agent.
    
    Alert format:
    {
        "id": "unique-id",
        "timestamp": "ISO timestamp",
        "priority": "high|medium|low",
        "channel": "telegram|discord|email",
        "topic_id": "topic-id",
        "topic_name": "Topic Name",
        "title": "Result title",
        "snippet": "Result snippet",
        "url": "https://...",
        "score": 0.75,
        "reason": "scoring reason",
        "sent": false
    }
    """
    ensure_memory_dir()
    
    # Load existing queue
    queue = []
    if ALERTS_QUEUE.exists():
        try:
            with open(ALERTS_QUEUE) as f:
                queue = json.load(f)
        except (json.JSONDecodeError, IOError):
            queue = []
    
    # Add alert with unique ID
    import hashlib
    from datetime import datetime
    
    alert_id = hashlib.md5(
        f"{alert.get('url', '')}{alert.get('timestamp', '')}".encode()
    ).hexdigest()[:12]
    
    alert["id"] = alert_id
    alert["sent"] = False
    if "timestamp" not in alert:
        alert["timestamp"] = datetime.now().isoformat()
    
    # Avoid duplicates
    existing_ids = {a.get("id") for a in queue}
    if alert_id not in existing_ids:
        queue.append(alert)
    
    # Save queue
    with open(ALERTS_QUEUE, 'w') as f:
        json.dump(queue, f, indent=2)
    
    return alert_id


def get_pending_alerts() -> List[Dict]:
    """Get all unsent alerts from the queue."""
    ensure_memory_dir()
    
    if not ALERTS_QUEUE.exists():
        return []
    
    try:
        with open(ALERTS_QUEUE) as f:
            queue = json.load(f)
    except (json.JSONDecodeError, IOError):
        return []
    
    return [a for a in queue if not a.get("sent", False)]


def mark_alert_sent(alert_id: str):
    """Mark an alert as sent."""
    ensure_memory_dir()
    
    if not ALERTS_QUEUE.exists():
        return
    
    try:
        with open(ALERTS_QUEUE) as f:
            queue = json.load(f)
    except (json.JSONDecodeError, IOError):
        return
    
    for alert in queue:
        if alert.get("id") == alert_id:
            alert["sent"] = True
            alert["sent_at"] = json.dumps({"_": "now"})[7:-2]  # hack for timestamp
            from datetime import datetime
            alert["sent_at"] = datetime.now().isoformat()
            break
    
    with open(ALERTS_QUEUE, 'w') as f:
        json.dump(queue, f, indent=2)


def clear_old_alerts(max_age_hours: int = 168):
    """Clear alerts older than max_age_hours (default 7 days)."""
    ensure_memory_dir()
    
    if not ALERTS_QUEUE.exists():
        return
    
    from datetime import datetime, timedelta
    
    try:
        with open(ALERTS_QUEUE) as f:
            queue = json.load(f)
    except (json.JSONDecodeError, IOError):
        return
    
    cutoff = datetime.now() - timedelta(hours=max_age_hours)
    
    new_queue = []
    for alert in queue:
        try:
            ts = datetime.fromisoformat(alert.get("timestamp", ""))
            if ts > cutoff:
                new_queue.append(alert)
        except (ValueError, TypeError):
            # Keep alerts with invalid timestamps (let them be manually reviewed)
            new_queue.append(alert)
    
    with open(ALERTS_QUEUE, 'w') as f:
        json.dump(new_queue, f, indent=2)
