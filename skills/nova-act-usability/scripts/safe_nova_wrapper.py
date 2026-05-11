#!/usr/bin/env python3
"""
Robust wrapper for Nova Act calls with error handling and timeout protection.
"""

import time
import functools
from typing import Any, Callable, Optional, Tuple
from dataclasses import dataclass

# ============================================================================
# Configuration (Bug #15: Centralized defaults)
# ============================================================================

DEFAULT_TIMEOUT = 20  # seconds
DEFAULT_MAX_RETRIES = 1
SLOW_OPERATION_THRESHOLD = 15  # seconds
HEALTH_CHECK_TIMEOUT = 10  # seconds


# ============================================================================
# Result Types (Bug #12: Consistent error handling)
# ============================================================================

@dataclass
class ActResult:
    """Result of a Nova Act action."""
    success: bool
    observation: Optional[str] = None
    error: Optional[str] = None
    duration: float = 0.0


@dataclass
class QueryResult:
    """Result of a Nova Act query."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    duration: float = 0.0


# ============================================================================
# Exceptions
# ============================================================================

class NovaActTimeout(Exception):
    """Raised when a Nova Act operation times out."""
    pass


class NovaActError(Exception):
    """Raised when a Nova Act operation fails."""
    pass


# ============================================================================
# Timeout Decorator
# ============================================================================

def with_timeout(timeout_seconds: int = DEFAULT_TIMEOUT):
    """
    Decorator to add timeout protection to Nova Act calls.
    Uses threading for cross-platform support (Bug #7).
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import signal
            
            def timeout_handler(signum, frame):
                raise NovaActTimeout(f"Operation timed out after {timeout_seconds}s")
            
            # Set up timeout (Unix only - Windows falls back to no timeout)
            try:
                old_handler = signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(timeout_seconds)
                try:
                    result = func(*args, **kwargs)
                finally:
                    signal.alarm(0)
                    signal.signal(signal.SIGALRM, old_handler)
                return result
            except AttributeError:
                # Windows doesn't have SIGALRM, fall back to no timeout
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


# ============================================================================
# Safe Wrappers (Bug #8: Return observations)
# ============================================================================

def safe_act(nova, action: str, timeout: int = DEFAULT_TIMEOUT, 
             max_retries: int = DEFAULT_MAX_RETRIES) -> ActResult:
    """
    Safely execute a Nova Act action with error handling.
    
    Returns:
        ActResult with success, observation, error, and duration
    """
    for attempt in range(max_retries):
        try:
            start = time.time()
            result = nova.act(action)
            duration = time.time() - start
            
            # Extract observation from result if available
            observation = None
            if result is not None:
                if hasattr(result, 'response') and result.response:
                    observation = str(result.response)
                elif hasattr(result, 'matches_response') and result.matches_response:
                    observation = str(result.matches_response)
                elif isinstance(result, str):
                    observation = result
            
            # Detect if it took suspiciously long (possible loop)
            if duration > SLOW_OPERATION_THRESHOLD:
                return ActResult(
                    success=False,
                    observation=observation,
                    error=f"Action took {duration:.1f}s (possible scroll loop or hang)",
                    duration=duration
                )
            
            return ActResult(
                success=True,
                observation=observation or f"Action completed: {action[:50]}...",
                duration=duration
            )
            
        except Exception as e:
            error_msg = str(e)
            duration = time.time() - start if 'start' in dir() else 0
            
            # Check for common Nova Act errors
            if "timeout" in error_msg.lower():
                return ActResult(success=False, error="Nova Act timeout - page may be unresponsive", duration=duration)
            elif "element not found" in error_msg.lower():
                return ActResult(success=False, error="Element not found on page", duration=duration)
            elif "scroll" in error_msg.lower() and "loop" in error_msg.lower():
                return ActResult(success=False, error="Scroll loop detected", duration=duration)
            elif attempt < max_retries - 1:
                time.sleep(2)  # Brief pause before retry
                continue
            else:
                return ActResult(success=False, error=f"Nova Act error: {error_msg}", duration=duration)
    
    return ActResult(success=False, error="Max retries exceeded")


def safe_act_get(nova, query: str, schema: Any, timeout: int = DEFAULT_TIMEOUT,
                 max_retries: int = DEFAULT_MAX_RETRIES) -> QueryResult:
    """
    Safely execute a Nova Act query with error handling.
    
    Returns:
        QueryResult with success, data, error, and duration
    """
    for attempt in range(max_retries):
        try:
            start = time.time()
            result = nova.act_get(query, schema=schema)
            duration = time.time() - start
            
            # Detect if it took suspiciously long
            if duration > SLOW_OPERATION_THRESHOLD:
                return QueryResult(
                    success=False,
                    data=result.parsed_response if result else None,
                    error=f"Query took {duration:.1f}s (possible hang)",
                    duration=duration
                )
            
            return QueryResult(
                success=True,
                data=result.parsed_response,
                duration=duration
            )
            
        except Exception as e:
            error_msg = str(e)
            duration = time.time() - start if 'start' in dir() else 0
            
            if "timeout" in error_msg.lower():
                return QueryResult(success=False, error="Nova Act timeout", duration=duration)
            elif attempt < max_retries - 1:
                time.sleep(2)
                continue
            else:
                return QueryResult(success=False, error=f"Nova Act error: {error_msg}", duration=duration)
    
    return QueryResult(success=False, error="Max retries exceeded")


def safe_scroll(nova, direction: str = "down", max_attempts: int = 3) -> ActResult:
    """
    Safely scroll with loop detection.
    
    Args:
        nova: Nova Act session
        direction: "down" or "up"
        max_attempts: Max scroll attempts before declaring loop
    
    Returns:
        ActResult with success, observation, and error
    """
    for attempt in range(max_attempts):
        try:
            start = time.time()
            
            if direction == "down":
                nova.act("Scroll down to see more content")
            else:
                nova.act("Scroll up")
            
            duration = time.time() - start
            
            # If scroll takes too long, probably stuck
            if duration > 10:
                return ActResult(
                    success=False,
                    error="Scroll operation taking too long (possible loop)",
                    duration=duration
                )
            
            # Small delay to let page settle
            time.sleep(1)
            
            return ActResult(
                success=True,
                observation=f"Scrolled {direction}",
                duration=duration
            )
            
        except Exception as e:
            error_msg = str(e)
            if "scroll" in error_msg.lower() and "loop" in error_msg.lower():
                return ActResult(success=False, error="Scroll loop detected by Nova Act")
            elif attempt < max_attempts - 1:
                time.sleep(2)
                continue
            else:
                return ActResult(success=False, error=f"Scroll error: {error_msg}")
    
    return ActResult(success=False, error="Scroll stuck (max attempts)")


def is_session_healthy(nova) -> bool:
    """
    Quick health check to see if Nova Act session is still responsive.
    
    Returns:
        True if session is healthy, False otherwise
    """
    try:
        start = time.time()
        # Simple query that should always work
        result = nova.act_get(
            "Is there any text visible on the page?",
            schema={"type": "boolean"}
        )
        duration = time.time() - start
        
        # If it takes more than threshold for a simple check, session is degraded
        return duration < HEALTH_CHECK_TIMEOUT and result.parsed_response is not None
        
    except:
        return False


# ============================================================================
# Legacy Compatibility (tuple returns)
# ============================================================================

def safe_act_tuple(nova, action: str, timeout: int = DEFAULT_TIMEOUT,
                   max_retries: int = DEFAULT_MAX_RETRIES) -> Tuple[bool, Optional[str]]:
    """Legacy compatibility: returns (success, error_or_observation)."""
    result = safe_act(nova, action, timeout, max_retries)
    if result.success:
        return True, result.observation
    return False, result.error


def safe_act_get_tuple(nova, query: str, schema: Any, timeout: int = DEFAULT_TIMEOUT,
                       max_retries: int = DEFAULT_MAX_RETRIES) -> Tuple[bool, Any, Optional[str]]:
    """Legacy compatibility: returns (success, data, error)."""
    result = safe_act_get(nova, query, schema, timeout, max_retries)
    return result.success, result.data, result.error


def safe_scroll_tuple(nova, direction: str = "down", max_attempts: int = 3) -> Tuple[bool, Optional[str]]:
    """Legacy compatibility: returns (success, error_or_observation)."""
    result = safe_scroll(nova, direction, max_attempts)
    if result.success:
        return True, result.observation
    return False, result.error
