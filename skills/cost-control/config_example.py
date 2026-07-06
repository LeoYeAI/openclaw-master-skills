"""
Cost Control System — Configuration Examples
=============================================
Copy this file to config.py and customize for your API pricing.
"""
from cost_control import CostTracker


# ═══════════════════════════════════════════════════════════════
# EXAMPLE 1: Claude Opus API (Token-Based Pricing)
# ═══════════════════════════════════════════════════════════════

def example_claude_opus():
    """Example: Anthropic Claude Opus 4 API."""
    
    tracker = CostTracker(
        # Pricing (as of Feb 2026)
        input_price_per_unit=15.00,    # $15 per million input tokens
        output_price_per_unit=75.00,   # $75 per million output tokens
        unit_size=1_000_000,           # Per million tokens
        
        # Thresholds
        cost_caution_15min=3.00,       # Slow down at $3/15min
        cost_emergency_15min=5.00,     # Stop at $5/15min
        cost_daily_cap=25.00,          # Hard cap at $25/day
        max_cost_per_call=0.50,        # Alert if single call > $0.50
    )
    
    # Example: Record an API call
    # response = anthropic_client.messages.create(...)
    # input_tokens = response.usage.input_tokens
    # output_tokens = response.usage.output_tokens
    # tracker.record_call(input_tokens, output_tokens, request_id=response.id)
    
    return tracker


# ═══════════════════════════════════════════════════════════════
# EXAMPLE 2: OpenAI GPT-4 API (Token-Based Pricing)
# ═══════════════════════════════════════════════════════════════

def example_gpt4():
    """Example: OpenAI GPT-4 Turbo API."""
    
    tracker = CostTracker(
        # Pricing (as of Feb 2026)
        input_price_per_unit=10.00,    # $10 per million input tokens
        output_price_per_unit=30.00,   # $30 per million output tokens
        unit_size=1_000_000,
        
        # Thresholds (adjust for your budget)
        cost_caution_15min=2.00,
        cost_emergency_15min=4.00,
        cost_daily_cap=20.00,
    )
    
    return tracker


# ═══════════════════════════════════════════════════════════════
# EXAMPLE 3: Google Gemini API (Token-Based Pricing)
# ═══════════════════════════════════════════════════════════════

def example_gemini():
    """Example: Google Gemini 2.5 Pro API."""
    
    tracker = CostTracker(
        # Pricing (as of Feb 2026 — check current rates)
        input_price_per_unit=1.25,     # $1.25 per million input tokens
        output_price_per_unit=5.00,    # $5.00 per million output tokens
        unit_size=1_000_000,
        
        # Thresholds (Gemini is cheaper, adjust accordingly)
        cost_caution_15min=1.00,
        cost_emergency_15min=2.00,
        cost_daily_cap=10.00,
    )
    
    return tracker


# ═══════════════════════════════════════════════════════════════
# EXAMPLE 4: Fixed-Cost API (Per-Request Pricing)
# ═══════════════════════════════════════════════════════════════

def example_twilio():
    """Example: Twilio SMS API (fixed cost per message)."""
    
    tracker = CostTracker(
        # Pricing: $0.0075 per SMS
        fixed_cost_per_call=0.0075,
        
        # Thresholds
        cost_caution_15min=0.50,       # 67 messages
        cost_emergency_15min=1.00,     # 133 messages
        cost_daily_cap=5.00,           # 667 messages
        max_cost_per_call=0.01,        # Sanity check (normal SMS < $0.01)
    )
    
    # Example: Record an SMS send
    # sms = twilio_client.messages.create(to="+1234567890", ...)
    # tracker.record_call(1, 0, request_id=sms.sid)  # 1 "unit" = 1 SMS
    
    return tracker


# ═══════════════════════════════════════════════════════════════
# EXAMPLE 5: AWS Lambda (Compute-Based Pricing)
# ═══════════════════════════════════════════════════════════════

def example_aws_lambda():
    """Example: AWS Lambda (per-invocation + compute time)."""
    
    tracker = CostTracker(
        # Pricing: $0.20 per million requests + $0.0000166667 per GB-second
        # Simplified: track invocations only (ignore compute for now)
        input_price_per_unit=0.20,     # $0.20 per million invocations
        output_price_per_unit=0.0,     # No output pricing
        unit_size=1_000_000,
        
        # Thresholds
        cost_caution_15min=1.00,
        cost_emergency_15min=2.00,
        cost_daily_cap=10.00,
    )
    
    # Example: Record a Lambda invocation
    # response = lambda_client.invoke(FunctionName="my-function", ...)
    # tracker.record_call(1, 0, request_id=response["RequestId"])
    
    return tracker


# ═══════════════════════════════════════════════════════════════
# EXAMPLE 6: Custom Alert Handler
# ═══════════════════════════════════════════════════════════════

def example_with_alerts():
    """Example: Custom alert handler (send to Slack, Discord, email)."""
    
    def my_alert_handler(message: str):
        """Custom alert handler — send to multiple channels."""
        print(f"🚨 ALERT: {message}")
        
        # Send to Slack
        # slack_client.chat_postMessage(channel="#alerts", text=message)
        
        # Send to Discord
        # discord_webhook.send(content=message)
        
        # Send email
        # smtp_client.send(to="admin@example.com", subject="Cost Alert", body=message)
    
    tracker = CostTracker(
        input_price_per_unit=15.00,
        output_price_per_unit=75.00,
        unit_size=1_000_000,
        cost_caution_15min=3.00,
        cost_emergency_15min=5.00,
        cost_daily_cap=25.00,
        alert_callback=my_alert_handler,  # Custom alerting
    )
    
    return tracker


# ═══════════════════════════════════════════════════════════════
# EXAMPLE 7: Integration Pattern (Before/After API Call)
# ═══════════════════════════════════════════════════════════════

def integration_pattern():
    """Production pattern: wrap API calls with cost tracking."""
    
    tracker = CostTracker(
        input_price_per_unit=15.00,
        output_price_per_unit=75.00,
        unit_size=1_000_000,
        cost_caution_15min=3.00,
        cost_emergency_15min=5.00,
        cost_daily_cap=25.00,
    )
    
    def call_expensive_api(prompt: str):
        """Wrapper for expensive API calls with cost protection."""
        
        # Pre-call: Check if allowed
        allowed, reason = tracker.is_call_allowed()
        if not allowed:
            raise RuntimeError(f"API call blocked: {reason}")
        
        # Make API call
        response = your_expensive_api_client.generate(prompt=prompt)
        
        # Post-call: Record cost
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        tracker.record_call(input_tokens, output_tokens, request_id=response.id)
        
        return response
    
    # Usage
    try:
        result = call_expensive_api("Explain quantum computing")
        print(result.text)
    except RuntimeError as e:
        print(f"API call failed: {e}")
        # Handle emergency mode (alert, exit, etc.)


# ═══════════════════════════════════════════════════════════════
# EXAMPLE 8: Multi-API Tracking (Separate Trackers)
# ═══════════════════════════════════════════════════════════════

def example_multi_api():
    """Example: Track multiple APIs separately."""
    
    # Separate tracker for each API
    opus_tracker = CostTracker(
        input_price_per_unit=15.00,
        output_price_per_unit=75.00,
        unit_size=1_000_000,
        cost_caution_15min=3.00,
        cost_emergency_15min=5.00,
        cost_daily_cap=25.00,
        state_dir="./state/opus",  # Separate state directory
    )
    
    gpt4_tracker = CostTracker(
        input_price_per_unit=10.00,
        output_price_per_unit=30.00,
        unit_size=1_000_000,
        cost_caution_15min=2.00,
        cost_emergency_15min=4.00,
        cost_daily_cap=20.00,
        state_dir="./state/gpt4",  # Separate state directory
    )
    
    return opus_tracker, gpt4_tracker


# ═══════════════════════════════════════════════════════════════
# EXAMPLE 9: Calibrating Thresholds from Historical Data
# ═══════════════════════════════════════════════════════════════

def calibrate_thresholds():
    """Example: Calculate thresholds from historical cost data.
    
    1. Run your app for 1 day with tracking enabled (no blocking)
    2. Analyze cost_log.jsonl to find 95th percentile cost per 15-min window
    3. Set thresholds based on percentiles
    """
    
    import json
    from collections import defaultdict
    
    # Read historical cost log
    costs_by_15min_window = defaultdict(float)
    
    with open("state/cost_log.jsonl") as f:
        for line in f:
            entry = json.loads(line)
            timestamp = entry["t"]
            cost = entry["cost"]
            
            # Group by 15-minute windows
            window = int(timestamp // 900) * 900  # Floor to 15-min
            costs_by_15min_window[window] += cost
    
    # Calculate percentiles
    window_costs = sorted(costs_by_15min_window.values())
    p50 = window_costs[len(window_costs) // 2]
    p95 = window_costs[int(len(window_costs) * 0.95)]
    p99 = window_costs[int(len(window_costs) * 0.99)]
    
    print(f"Historical 15-min cost distribution:")
    print(f"  50th percentile (median): ${p50:.2f}")
    print(f"  95th percentile: ${p95:.2f}")
    print(f"  99th percentile: ${p99:.2f}")
    print()
    print(f"Recommended thresholds:")
    print(f"  cost_caution_15min: ${p95 * 1.5:.2f}  (1.5x p95)")
    print(f"  cost_emergency_15min: ${p99 * 2:.2f}  (2x p99)")
    
    # Create tracker with calibrated thresholds
    tracker = CostTracker(
        input_price_per_unit=15.00,
        output_price_per_unit=75.00,
        unit_size=1_000_000,
        cost_caution_15min=p95 * 1.5,
        cost_emergency_15min=p99 * 2,
        cost_daily_cap=p99 * 2 * 96,  # 96 = 15-min windows per day
    )
    
    return tracker


# ═══════════════════════════════════════════════════════════════
# Run Examples
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Cost Control System — Configuration Examples")
    print("=" * 50)
    print()
    print("Available examples:")
    print("1. Claude Opus API (token-based)")
    print("2. OpenAI GPT-4 API (token-based)")
    print("3. Google Gemini API (token-based)")
    print("4. Twilio SMS API (fixed-cost)")
    print("5. AWS Lambda (compute-based)")
    print("6. Custom alert handler")
    print("7. Integration pattern")
    print("8. Multi-API tracking")
    print("9. Calibrate thresholds from historical data")
    print()
    print("Edit this file to customize for your API pricing.")
