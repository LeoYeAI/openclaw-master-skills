#!/usr/bin/env python3
"""
Thin wrapper for Nova Act session management.
Provides primitives for AI orchestration.
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from contextlib import contextmanager
import glob


def load_config() -> Dict[str, Any]:
    """Load Nova Act configuration."""
    config_path = Path.home() / ".openclaw" / "config" / "nova-act.json"
    if not config_path.exists():
        raise FileNotFoundError(
            "Nova Act config not found at ~/.openclaw/config/nova-act.json"
        )
    
    with open(config_path, 'r') as f:
        return json.load(f)


@contextmanager
def nova_session(starting_page: str, headless: bool = True, logs_dir: Optional[str] = None):
    """
    Create a Nova Act session context.
    
    Args:
        starting_page: URL to start from
        headless: Run in headless mode (default True)
        logs_dir: Directory to store Nova Act trace files (optional)
    
    Yields:
        NovaAct instance for orchestration
    
    Example:
        with nova_session("https://example.com", logs_dir="/path/to/logs") as nova:
            nova.act("Navigate to pricing")
            result = nova.act_get("Extract pricing", schema=PricingSchema)
    """
    try:
        from nova_act import NovaAct
    except ImportError:
        raise ImportError("Nova Act SDK not installed. Run: pip install nova-act")
    
    # Load API key and set as environment variable
    config = load_config()
    os.environ['NOVA_ACT_API_KEY'] = config['apiKey']
    
    # Set up logs directory (default to current working directory)
    if logs_dir is None:
        logs_dir = os.path.join(os.getcwd(), "nova_act_logs")
    
    # Create logs directory if it doesn't exist
    os.makedirs(logs_dir, exist_ok=True)
    
    # Use NovaAct directly with API key (no Workflow needed)
    with NovaAct(
        starting_page=starting_page,
        tty=not headless,
        logs_directory=logs_dir
    ) as nova:
        yield nova


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: nova_session.py <url>")
        sys.exit(1)
    
    url = sys.argv[1]
    
    with nova_session(url, headless=False) as nova:
        print(f"Session started at {url}")
        print("Nova Act instance ready for commands")
        print("Use nova.act() for actions and nova.act_get() for extraction")
