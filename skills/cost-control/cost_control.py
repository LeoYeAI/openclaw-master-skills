"""
Cost Control System — 3-Tier API Spend Protection
==================================================
Real-time cost tracking with tiered responses (caution/emergency/cap).
Works for ANY expensive API (GPT-4, Claude, Gemini, cloud services).

Production-tested cost control, domain-agnostic.

Copyright © 2026 Shadow Rose
License: MIT
"""
import json
import os
import time
from collections import deque
from typing import Dict, Any, Tuple, Optional, Callable


class CostTracker:
    """Real-time cost tracker with 3-tier protection.
    
    Tier 1 (Caution):  Slow down operations
    Tier 2 (Emergency): Stop all API calls
    Tier 3 (Kill):      External watchdog kills process
    """
    
    def __init__(
        self,
        # Pricing (customize for your API)
        input_price_per_unit: float = 15.00,    # Default: Claude Opus input ($15/MTok)
        output_price_per_unit: float = 75.00,   # Default: Claude Opus output ($75/MTok)
        unit_size: int = 1_000_000,             # Default: per million tokens
        fixed_cost_per_call: Optional[float] = None,  # For non-token APIs
        
        # Thresholds
        cost_caution_15min: float = 3.00,
        cost_emergency_15min: float = 5.00,
        cost_daily_cap: float = 25.00,
        max_cost_per_call: float = 0.50,
        
        # Recovery
        caution_recovery_threshold: float = 2.00,
        caution_recovery_duration: int = 300,
        
        # State
        state_dir: str = "./state",
        cost_log_file: str = "cost_log.jsonl",
        tracker_file: str = "cost_tracker.json",
        emergency_flag_file: str = "cost_emergency.flag",
        
        # Alerting
        alert_callback: Optional[Callable[[str], None]] = None,
    ):
        """Initialize cost tracker.
        
        Args:
            input_price_per_unit: Cost per unit of input (e.g., $15 per million tokens)
            output_price_per_unit: Cost per unit of output (e.g., $75 per million tokens)
            unit_size: Units per pricing tier (e.g., 1_000_000 for per-million pricing)
            fixed_cost_per_call: Fixed cost per call (for non-token APIs)
            cost_caution_15min: Tier 1 threshold ($)
            cost_emergency_15min: Tier 2 threshold ($)
            cost_daily_cap: Absolute daily maximum ($)
            max_cost_per_call: Single-call sanity check ($)
            caution_recovery_threshold: Exit caution when cost drops below this
            caution_recovery_duration: Must stay below for this many seconds
            state_dir: Directory for state persistence
            cost_log_file: Filename for cost log (within state_dir)
            tracker_file: Filename for tracker state (within state_dir)
            emergency_flag_file: Filename for emergency flag (within state_dir)
            alert_callback: Function(message: str) called for alerts
        """
        # Pricing
        self.input_price_per_unit = input_price_per_unit
        self.output_price_per_unit = output_price_per_unit
        self.unit_size = unit_size
        self.fixed_cost_per_call = fixed_cost_per_call
        
        # Thresholds
        self.cost_caution_15min = cost_caution_15min
        self.cost_emergency_15min = cost_emergency_15min
        self.cost_daily_cap = cost_daily_cap
        self.max_cost_per_call = max_cost_per_call
        
        # Recovery
        self.caution_recovery_threshold = caution_recovery_threshold
        self.caution_recovery_duration = caution_recovery_duration
        
        # State files
        self.state_dir = state_dir
        self.cost_log_file = os.path.join(state_dir, cost_log_file)
        self.tracker_file = os.path.join(state_dir, tracker_file)
        self.emergency_flag_file = os.path.join(state_dir, emergency_flag_file)
        
        # Alerting
        self.alert_callback = alert_callback or self._default_alert
        
        # Rolling window of (timestamp, cost, request_id) tuples
        self._calls = deque(maxlen=5000)
        
        # Daily tracking
        self._daily_total = 0.0
        self._daily_date = time.strftime("%Y-%m-%d", time.gmtime())
        self._total_calls_session = 0
        
        # State
        self._caution_mode = False
        self._caution_since = None
        self._emergency_mode = False
        self._below_caution_since = None
        
        # Create state directory
        os.makedirs(state_dir, exist_ok=True)
        
        # Load existing state
        self._load_state()
        
        # Check for emergency flag from previous run
        if os.path.exists(self.emergency_flag_file):
            self._log("WARNING: Emergency flag found from previous run — calls blocked")
            self._emergency_mode = True
        
        self._log(f"CostTracker initialized: daily_total=${self._daily_total:.2f}, "
                  f"emergency={'YES' if self._emergency_mode else 'no'}")
    
    def _log(self, message: str):
        """Internal logging (override for custom logger)."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        print(f"{timestamp} [CostTracker] {message}")
    
    def _default_alert(self, message: str):
        """Default alert handler (just logs)."""
        self._log(f"ALERT: {message}")
    
    def set_pricing(
        self,
        input_price_per_unit: Optional[float] = None,
        output_price_per_unit: Optional[float] = None,
        unit_size: Optional[int] = None,
        fixed_cost_per_call: Optional[float] = None,
    ):
        """Update pricing configuration.
        
        Use this to configure pricing for your specific API.
        """
        if input_price_per_unit is not None:
            self.input_price_per_unit = input_price_per_unit
        if output_price_per_unit is not None:
            self.output_price_per_unit = output_price_per_unit
        if unit_size is not None:
            self.unit_size = unit_size
        if fixed_cost_per_call is not None:
            self.fixed_cost_per_call = fixed_cost_per_call
    
    def record_call(
        self,
        input_units: int,
        output_units: int,
        request_id: Optional[str] = None
    ) -> bool:
        """Record an API call with actual usage.
        
        Args:
            input_units: Input units consumed (e.g., tokens, requests)
            output_units: Output units consumed
            request_id: Optional identifier for logging
        
        Returns:
            True if within limits, False if emergency mode triggered
        """
        now = time.time()
        self._total_calls_session += 1
        
        # Reset daily counter at midnight UTC
        today = time.strftime("%Y-%m-%d", time.gmtime())
        if today != self._daily_date:
            self._log(f"Daily cost reset: {self._daily_date} total=${self._daily_total:.2f}")
            self._daily_total = 0.0
            self._daily_date = today
        
        # Calculate cost
        if self.fixed_cost_per_call is not None:
            call_cost = self.fixed_cost_per_call
        else:
            input_cost = (input_units / self.unit_size) * self.input_price_per_unit
            output_cost = (output_units / self.unit_size) * self.output_price_per_unit
            call_cost = input_cost + output_cost
        
        # Per-call sanity check
        if call_cost > self.max_cost_per_call:
            self._log(f"WARNING: Single call cost ${call_cost:.3f} exceeds "
                      f"${self.max_cost_per_call} limit (request_id={request_id})")
        
        # Record
        self._calls.append((now, call_cost, request_id or "unknown"))
        self._daily_total += call_cost
        
        # Write to cost log
        self._log_call(now, request_id, input_units, output_units, call_cost)
        
        # Evaluate thresholds
        self._evaluate_thresholds(now)
        
        # Write tracker state
        self._save_state()
        
        return not self._emergency_mode
    
    def is_call_allowed(self) -> Tuple[bool, str]:
        """Check if API calls are currently allowed.
        
        Returns:
            (allowed: bool, reason: str)
                - (True, "ok") if safe to proceed
                - (False, "cost_emergency_mode") if blocked by emergency
                - (False, "external_cost_emergency") if blocked by watchdog
        """
        if self._emergency_mode:
            return False, "cost_emergency_mode"
        
        # Check if emergency flag exists (may be set by external watchdog)
        if os.path.exists(self.emergency_flag_file):
            if not self._emergency_mode:
                self._emergency_mode = True
                self._log("External emergency flag detected — blocking calls")
            return False, "external_cost_emergency"
        
        # Check manual kill switch
        kill_switch_file = os.path.join(self.state_dir, "KILL_SWITCH")
        if os.path.exists(kill_switch_file):
            return False, "manual_kill_switch"
        
        return True, "ok"
    
    @property
    def caution_mode(self) -> bool:
        """Whether in Tier 1 caution mode."""
        return self._caution_mode
    
    @property
    def emergency_mode(self) -> bool:
        """Whether in Tier 2 emergency mode."""
        return self._emergency_mode
    
    def get_cost_15min(self) -> float:
        """Get rolling 15-minute cost."""
        cutoff = time.time() - 900
        return sum(cost for ts, cost, _ in self._calls if ts > cutoff)
    
    def get_cost_hourly(self) -> float:
        """Get rolling 60-minute cost."""
        cutoff = time.time() - 3600
        return sum(cost for ts, cost, _ in self._calls if ts > cutoff)
    
    def get_calls_hourly(self) -> int:
        """Get rolling 60-minute call count."""
        cutoff = time.time() - 3600
        return sum(1 for ts, _, _ in self._calls if ts > cutoff)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current cost statistics.
        
        Returns:
            Dict with keys: cost_5min, cost_15min, cost_1hour, cost_daily,
            calls_1hour, calls_session, caution_mode, emergency_mode
        """
        now = time.time()
        cost_5m = sum(cost for ts, cost, _ in self._calls if ts > now - 300)
        
        return {
            "cost_5min": round(cost_5m, 3),
            "cost_15min": round(self.get_cost_15min(), 3),
            "cost_1hour": round(self.get_cost_hourly(), 3),
            "cost_daily": round(self._daily_total, 3),
            "calls_1hour": self.get_calls_hourly(),
            "calls_session": self._total_calls_session,
            "caution_mode": self._caution_mode,
            "emergency_mode": self._emergency_mode,
        }
    
    def clear_emergency(self):
        """Clear emergency mode (manual intervention required)."""
        if os.path.exists(self.emergency_flag_file):
            os.remove(self.emergency_flag_file)
        self._emergency_mode = False
        self._log("Emergency mode cleared manually")
    
    def _evaluate_thresholds(self, now: float):
        """Check all cost thresholds and update mode accordingly."""
        cost_15m = self.get_cost_15min()
        
        # Daily cap check
        if self._daily_total >= self.cost_daily_cap:
            if not self._emergency_mode:
                self._log(f"EMERGENCY: Daily cap breached (${self._daily_total:.2f} >= "
                          f"${self.cost_daily_cap})")
                self._enter_emergency("daily_cap_exceeded", self._daily_total)
            return
        
        # Tier 2: Emergency check
        if cost_15m >= self.cost_emergency_15min:
            if not self._emergency_mode:
                self._log(f"EMERGENCY: 15-min cost ${cost_15m:.2f} >= "
                          f"${self.cost_emergency_15min}")
                self._enter_emergency("15min_threshold_exceeded", cost_15m)
            return
        
        # Tier 1: Caution check
        if cost_15m >= self.cost_caution_15min:
            if not self._caution_mode:
                self._log(f"CAUTION: 15-min cost ${cost_15m:.2f} >= "
                          f"${self.cost_caution_15min} — slowing down")
                self._caution_mode = True
                self._caution_since = now
                self._below_caution_since = None
            return
        
        # Recovery check
        if self._caution_mode:
            if cost_15m < self.caution_recovery_threshold:
                if self._below_caution_since is None:
                    self._below_caution_since = now
                elif now - self._below_caution_since >= self.caution_recovery_duration:
                    self._log(f"Caution cleared: ${cost_15m:.2f}/15min "
                              f"(below ${self.caution_recovery_threshold})")
                    self._caution_mode = False
                    self._caution_since = None
                    self._below_caution_since = None
            else:
                self._below_caution_since = None
    
    def _enter_emergency(self, reason: str, amount: float):
        """Enter emergency mode — stops all API calls."""
        self._emergency_mode = True
        
        # Write emergency flag file
        flag_data = {
            "triggered_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "triggered_epoch": time.time(),
            "reason": reason,
            "amount": round(amount, 3),
            "daily_total": round(self._daily_total, 3),
            "calls_last_hour": self.get_calls_hourly(),
            "calls_session": self._total_calls_session,
        }
        
        try:
            with open(self.emergency_flag_file, "w") as f:
                json.dump(flag_data, f, indent=2)
        except Exception as e:
            self._log(f"Failed to write emergency flag: {e}")
        
        # Send alert
        self.alert_callback(
            f"🚨 COST EMERGENCY — API CALLS PAUSED\n"
            f"Reason: {reason}\n"
            f"Amount: ${amount:.2f}\n"
            f"Daily total: ${self._daily_total:.2f}\n"
            f"Calls in last hour: {self.get_calls_hourly()}\n"
            f"Calls this session: {self._total_calls_session}\n\n"
            f"System is alive but NOT making API calls.\n"
            f"To resume: rm {self.emergency_flag_file}"
        )
    
    def _log_call(self, timestamp: float, request_id: Optional[str], 
                  input_units: int, output_units: int, cost: float):
        """Append to cost log (for external watchdog and auditing)."""
        try:
            entry = {
                "t": round(timestamp, 1),
                "request_id": request_id,
                "in": input_units,
                "out": output_units,
                "cost": round(cost, 5),
                "daily": round(self._daily_total, 3),
            }
            with open(self.cost_log_file, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            pass  # Non-fatal
    
    def _save_state(self):
        """Write current state to tracker file (for external watchdog)."""
        try:
            state = {
                "updated_at": time.time(),
                "updated_iso": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "cost_5min": round(sum(c for ts, c, _ in self._calls 
                                       if ts > time.time() - 300), 3),
                "cost_15min": round(self.get_cost_15min(), 3),
                "cost_1hour": round(self.get_cost_hourly(), 3),
                "cost_daily": round(self._daily_total, 3),
                "calls_1hour": self.get_calls_hourly(),
                "calls_session": self._total_calls_session,
                "caution_mode": self._caution_mode,
                "emergency_mode": self._emergency_mode,
                "daily_cap": self.cost_daily_cap,
            }
            
            # Atomic write
            tmp = self.tracker_file + ".tmp"
            with open(tmp, "w") as f:
                json.dump(state, f, indent=2)
            os.replace(tmp, self.tracker_file)
        except Exception:
            pass  # Non-fatal
    
    def _load_state(self):
        """Load state from previous run (handles restart continuity)."""
        if not os.path.exists(self.tracker_file):
            return
        
        try:
            with open(self.tracker_file) as f:
                state = json.load(f)
            
            # If same day (UTC), restore daily total
            if state.get("updated_iso", "").startswith(
                time.strftime("%Y-%m-%d", time.gmtime())
            ):
                self._daily_total = state.get("cost_daily", 0.0)
                self._log(f"Restored daily cost total: ${self._daily_total:.2f}")
        except Exception:
            pass
    
    def rotate_log(self, max_entries: int = 10000):
        """Rotate cost log to prevent unbounded growth."""
        if not os.path.exists(self.cost_log_file):
            return
        
        try:
            with open(self.cost_log_file) as f:
                lines = f.readlines()
            
            if len(lines) > max_entries:
                with open(self.cost_log_file, "w") as f:
                    f.writelines(lines[-max_entries:])
                self._log(f"Rotated cost log: {len(lines)} → {max_entries} entries")
        except Exception:
            pass
