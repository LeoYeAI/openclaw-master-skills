#!/usr/bin/env python3
"""
Token usage tracker with budget alerts and dynamic pricing.
Monitors API usage and warns when approaching limits.
"""
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import urllib.request
import urllib.error

STATE_FILE = Path.home() / ".openclaw/workspace/memory/token-tracker-state.json"
PRICING_FILE = Path.home() / ".openclaw/workspace/skills/openclaw-token-optimizer/pricing.json"

# Import tier configuration (single source of truth)
sys.path.append(str(Path(__file__).parent.parent))
from config import TIER_MODELS

# Build set of all models we care about (tier models only)
ALL_INTERESTING_MODELS = set()
for models in TIER_MODELS.values():
    ALL_INTERESTING_MODELS.update(models)

# Full default pricing database (per 1M tokens) for reference
FULL_DEFAULT_PRICING = {
    "anthropic/claude-opus-4": 15.0,
    "anthropic/claude-sonnet-4-5": 3.0,
    "anthropic/claude-haiku-4": 0.25,
    "google/gemini-2.0-flash-exp": 0.075,
    "openai/gpt-4o": 2.5,
    "openai/gpt-4o-mini": 0.15,
    "openrouter/stepfun/step-3.5-flash:free": 0.0,
    "openrouter/minimax/minimax-m2.5": 0.5
}

# Default pricing limited to tier models only (used when pricing file missing)
DEFAULT_PRICING = {model: FULL_DEFAULT_PRICING.get(model, 0.0) for model in ALL_INTERESTING_MODELS}

# Build mapping from OpenRouter raw model IDs to our canonical prefixed IDs
RAW_TO_PREFIXED = {}
for cid in ALL_INTERESTING_MODELS:
    if cid.startswith("openrouter/"):
        raw = cid[len("openrouter/"):]
        RAW_TO_PREFIXED[raw] = cid
    else:
        RAW_TO_PREFIXED[cid] = cid
INTERESTING_RAW_IDS = set(RAW_TO_PREFIXED.keys())

def load_state():
    """Load tracking state from file."""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {
        "daily_usage": {},
        "alerts_sent": [],
        "last_reset": datetime.now().isoformat()
    }

def save_state(state):
    """Save tracking state to file."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def load_pricing():
    """Load model pricing from file, fall back to defaults."""
    if PRICING_FILE.exists():
        try:
            with open(PRICING_FILE, 'r') as f:
                pricing = json.load(f)
            # Ensure it's a dict
            if isinstance(pricing, dict):
                return pricing
        except Exception as e:
            print(f"Warning: Failed to load pricing file: {e}", file=sys.stderr)
    return DEFAULT_PRICING.copy()

def save_pricing(pricing):
    """Save pricing data to file."""
    PRICING_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PRICING_FILE, 'w') as f:
        json.dump(pricing, f, indent=2)

def fetch_openrouter_pricing():
    """Fetch model pricing from OpenRouter API.
    Uses OPENROUTER_API_KEY if set; otherwise attempts to read from
    ~/.openclaw/agents/main/agent/auth-profiles.json (OpenClaw default location).
    Returns dict mapping our canonical model IDs to cost per 1M tokens.
    Only includes models listed in TIER_MODELS (if found).
    """
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        # Try reading from OpenClaw auth-profiles.json
        auth_path = Path.home() / ".openclaw/agents/main/agent/auth-profiles.json"
        if auth_path.exists():
            try:
                with open(auth_path, 'r') as f:
                    data = json.load(f)
                profile = data.get("profiles", {}).get("openrouter:default", {})
                api_key = profile.get("key")
                if api_key:
                    print("Using OPENROUTER_API_KEY from auth-profiles.json", file=sys.stderr)
            except Exception as e:
                print(f"Warning: Could not read auth-profiles.json: {e}", file=sys.stderr)
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY not set and could not be read from auth-profiles.json")

    url = "https://openrouter.ai/api/v1/models"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {api_key}"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"OpenRouter API error: {e.code} {e.reason}")
    except Exception as e:
        raise RuntimeError(f"Failed to fetch pricing: {e}")

    # Extract pricing: average of input and output (if both present)
    pricing = {}
    for model in data.get("data", []):
        raw_id = model.get("id")
        if not raw_id:
            continue
        # Map raw OpenRouter ID to our canonical prefixed ID (if we track it)
        if raw_id not in INTERESTING_RAW_IDS:
            continue
        canonical_id = RAW_TO_PREFIXED[raw_id]
        p = model.get("pricing", {})
        # OpenRouter uses 'prompt' for input, 'completion' for output; values are strings representing per-token cost in USD
        def to_float(v):
            try:
                return float(v)
            except (TypeError, ValueError):
                return 0.0
        input_cost = to_float(p.get("prompt", 0))
        output_cost = to_float(p.get("completion", 0))
        # Use average of prompt+completion if both nonzero, else whichever exists
        if input_cost and output_cost:
            avg_per_token = (input_cost + output_cost) / 2
        elif input_cost:
            avg_per_token = input_cost
        else:
            avg_per_token = output_cost or 0.0
        # Convert to per-1M tokens for consistency with DEFAULT_PRICING
        cost_per_1M = avg_per_token * 1_000_000
        pricing[canonical_id] = round(cost_per_1M, 6)  # keep precision

    return pricing

def refresh_pricing():
    """Refresh pricing data from OpenRouter and save locally."""
    print("Fetching pricing from OpenRouter...")
    try:
        fetched = fetch_openrouter_pricing()
        # Load existing pricing; keep only interesting models
        existing = {}
        if PRICING_FILE.exists():
            try:
                with open(PRICING_FILE, 'r') as f:
                    existing = json.load(f)
            except:
                existing = {}
        # Filter existing to only models we care about
        existing_filtered = {k: v for k, v in existing.items() if k in ALL_INTERESTING_MODELS}
        # Merge with fresh data
        existing_filtered.update(fetched)
        # Ensure defaults for any missing interesting models
        for model in ALL_INTERESTING_MODELS:
            if model not in existing_filtered:
                existing_filtered[model] = DEFAULT_PRICING.get(model, 0.0)
        save_pricing(existing_filtered)
        print(f"Pricing updated: {len(fetched)} models fetched from OpenRouter, total {len(existing_filtered)} tier models cached.")
        return existing_filtered
    except Exception as e:
        print(f"Error refreshing pricing: {e}", file=sys.stderr)
        sys.exit(1)

def get_usage_from_session_status():
    """Parse session status to extract token usage.
    Returns dict with input_tokens, output_tokens, and cost.
    """
    # This would integrate with OpenClaw's session_status tool
    # For now, returns placeholder structure
    return {
        "input_tokens": 0,
        "output_tokens": 0,
        "total_cost": 0.0,
        "model": "anthropic/claude-sonnet-4-5"
    }

def check_budget(daily_limit_usd=5.0, warn_threshold=0.8):
    """Check if usage is approaching daily budget.
    
    Args:
        daily_limit_usd: Daily spending limit in USD
        warn_threshold: Fraction of limit to trigger warning (default 80%)
    
    Returns:
        dict with status, usage, limit, and alert message if applicable
    """
    state = load_state()
    today = datetime.now().date().isoformat()
    
    # Reset if new day
    if today not in state["daily_usage"]:
        state["daily_usage"] = {today: {"cost": 0.0, "tokens": 0}}
        state["alerts_sent"] = []
    
    usage = state["daily_usage"][today]
    percent_used = (usage["cost"] / daily_limit_usd) * 100
    
    result = {
        "date": today,
        "cost": usage["cost"],
        "tokens": usage["tokens"],
        "limit": daily_limit_usd,
        "percent_used": percent_used,
        "status": "ok"
    }
    
    # Check thresholds
    if percent_used >= 100:
        result["status"] = "exceeded"
        result["alert"] = f"⚠️ Daily budget exceeded! ${usage['cost']:.2f} / ${daily_limit_usd:.2f}"
    elif percent_used >= (warn_threshold * 100):
        result["status"] = "warning"
        result["alert"] = f"⚠️ Approaching daily limit: ${usage['cost']:.2f} / ${daily_limit_usd:.2f} ({percent_used:.0f}%)"
    
    return result

def suggest_cheaper_model(current_model, task_type="general", pricing=None):
    """Suggest cheaper alternative models based on task type.
    
    Args:
        current_model: Currently configured model
        task_type: Type of task (general, simple, complex)
        pricing: Dict of model costs (optional, loads default if None)
    
    Returns:
        dict with suggestion and cost savings
    """
    if pricing is None:
        pricing = load_pricing()

    # Use global tier definitions
    tiers = TIER_MODELS

    # Determine which tier the current model belongs to
    current_tier = None
    for tier, models in tiers.items():
        if current_model in models:
            current_tier = tier
            break
    if current_tier is None:
        current_tier = "standard"  # default

    # Suggest cheaper models from lower tiers
    suggestions = []
    current_cost = pricing.get(current_model, "unknown")

    if task_type in ["simple", "general"]:
        if current_tier != "quick":
            for m in tiers["quick"]:
                if m != current_model:
                    suggestions.append((m, "Cheaper tier, suitable for routine tasks"))
        if current_tier not in ["quick", "standard"]:
            for m in tiers["standard"]:
                if m != current_model and m not in tiers["quick"]:
                    suggestions.append((m, "Mid-tier, good balance"))
    elif task_type == "complex":
        if current_tier != "deep":
            for m in tiers["deep"]:
                if m != current_model:
                    suggestions.append((m, "Higher tier for complex reasoning"))

    return {
        "current": current_model,
        "current_cost": pricing.get(current_model, "unknown"),
        "current_tier": current_tier,
        "suggestions": suggestions
    }

def main():
    """CLI interface for token tracker."""
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: token_tracker.py [check|suggest|reset|pricing|refresh-pricing]")
        print("Commands:")
        print("  check [--limit USD]        Check daily budget")
        print("  suggest [task_type] [model] Suggest cheaper model")
        print("  reset                      Reset daily counters")
        print("  pricing                    Show current loaded pricing")
        print("  refresh-pricing            Fetch fresh prices from OpenRouter")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "check":
        limit = 5.0
        if len(sys.argv) > 2 and sys.argv[2] == "--limit" and len(sys.argv) > 3:
            try:
                limit = float(sys.argv[3])
            except:
                pass
        result = check_budget(daily_limit_usd=limit)
        print(json.dumps(result, indent=2))
    
    elif command == "suggest":
        task = sys.argv[2] if len(sys.argv) > 2 else "general"
        current = sys.argv[3] if len(sys.argv) > 3 else "anthropic/claude-sonnet-4-5"
        result = suggest_cheaper_model(current, task)
        print(json.dumps(result, indent=2))
    
    elif command == "reset":
        state = load_state()
        state["daily_usage"] = {}
        state["alerts_sent"] = []
        save_state(state)
        print("Token tracker state reset.")
    
    elif command == "pricing":
        pricing = load_pricing()
        # Show in a readable table
        print("{:<50} {:>10}".format("Model", "Cost ($/1M)"))
        print("-" * 62)
        for model, cost in sorted(pricing.items()):
            print("{:<50} {:>10.6f}".format(model, cost))
    
    elif command == "refresh-pricing":
        pricing = refresh_pricing()
        # Also show a summary
        print("\nCurrent pricing (top 10 by cost):")
        sorted_items = sorted(pricing.items(), key=lambda x: x[1], reverse=True)[:10]
        print("{:<50} {:>10}".format("Model", "Cost ($/1M)"))
        print("-" * 62)
        for model, cost in sorted_items:
            print("{:<50} {:>10.6f}".format(model, cost))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
