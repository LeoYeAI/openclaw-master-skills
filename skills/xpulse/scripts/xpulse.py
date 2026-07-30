"""Xpulse — X/Twitter signal scanner for prediction markets.

Real-time social signal detection via DuckDuckGo + local Qwen LLM.
Three-stage pipeline: Signal Detection → Materiality Gate → Position Matching
"""

import json
import os
import subprocess
import sys
import time
import logging
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    yaml = None

# ──────────────────────────────────────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.DEBUG if os.environ.get("DEBUG") else logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
_log = logging.getLogger(__name__).debug


# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────

CONFIG_PATHS = [
    Path.home() / ".xpulse" / "config.yaml",
    Path.home() / ".openclaw" / "config.yaml",
    Path("/etc/xpulse/config.yaml"),
]

STATE_DIR = Path.home() / ".openclaw" / "state"
STATE_DIR.mkdir(parents=True, exist_ok=True)


def _load_config() -> dict:
    """Load config from first available path."""
    if yaml is None:
        logging.debug("PyYAML not installed — running with defaults")
        return {}
    for path in CONFIG_PATHS:
        if path.exists():
            with open(path) as f:
                return yaml.safe_load(f) or {}
    return {}


CONFIG = _load_config()
XPULSE_CFG = CONFIG.get("xpulse", {})
KALSHI_CFG = CONFIG.get("kalshi", {})
OLLAMA_CFG = CONFIG.get("ollama", {"enabled": True, "model": "qwen3:latest", "timeout_seconds": 15})

# qwen3 has a thinking/reasoning mode on by default that massively inflates latency.
# Prepend /no_think to all prompts to disable it and get fast JSON responses.
_QWEN3_NO_THINK = OLLAMA_CFG.get("model", "").startswith("qwen3")


# ──────────────────────────────────────────────────────────────────────────────
# Stage 1: Signal Detection
# ──────────────────────────────────────────────────────────────────────────────

def _search_x_posts(topic: str) -> list:
    """Search X/Twitter via DuckDuckGo for recent posts."""
    try:
        from ddgs import DDGS
        d = DDGS()
        results = list(d.text(f"site:x.com {topic}", max_results=5))
        return [r.get("body", "") for r in results if r.get("body")]
    except ImportError:
        pass
    except Exception:
        pass

    # Fallback to deprecated package
    try:
        from duckduckgo_search import DDGS as DDGS_OLD
        with DDGS_OLD() as ddgs:
            results = list(ddgs.text(f"site:x.com {topic}", max_results=5))
        return [r.get("body", "") for r in results if r.get("body")]
    except ImportError:
        pass
    except Exception:
        pass

    return []


def _check_ollama_model() -> bool:
    """Check if configured Ollama model is available. Warn if not."""
    model = OLLAMA_CFG.get("model", "qwen3:latest")
    try:
        import urllib.request
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            models = [m.get("name", "") for m in data.get("models", [])]
            if not any(model in m or m.startswith(model.split(":")[0]) for m in models):
                logging.warning(
                    f"Ollama model '{model}' not found. Available: {', '.join(models[:5])}. "
                    f"Try: ollama pull {model} — or set ollama.model to qwen2.5:7b in config."
                )
                return False
            return True
    except Exception as e:
        logging.warning(f"Ollama not reachable at localhost:11434: {e}")
        return False


# Ollama check is deferred to first use — avoids confusing warnings on unconfigured installs


def _call_ollama(prompt: str, timeout: int = 15) -> Optional[dict]:
    """Call Ollama via HTTP API (localhost:11434) for JSON responses.

    Uses the /api/generate endpoint which supports format: "json".
    Falls back to CLI if HTTP fails.
    """
    model = OLLAMA_CFG.get("model", "qwen3:latest")

    # Disable qwen3 thinking mode for fast responses
    if _QWEN3_NO_THINK:
        prompt = "/no_think\n" + prompt

    # Primary: HTTP API (supports JSON format natively)
    try:
        import urllib.request
        import urllib.error

        payload = json.dumps({
            "model": model,
            "prompt": prompt,
            "format": "json",
            "stream": False,
            "options": {"num_predict": 256},  # Cap output tokens — we only need short JSON
        }).encode("utf-8")

        req = urllib.request.Request(
            "http://localhost:11434/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            response_text = data.get("response", "").strip()
            return json.loads(response_text)

    except Exception as e:
        _log(f"Ollama HTTP API failed: {e}")

    # Fallback: CLI with stdin pipe
    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt,
            capture_output=True, timeout=timeout, text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            # Try to extract JSON from response
            text = result.stdout.strip()
            # Find first { and last } to extract JSON
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
        _log(f"Ollama CLI fallback failed: returncode={result.returncode}")
    except Exception as e:
        _log(f"Ollama CLI fallback error: {e}")

    return None


def _analyze_signals_local(topic: str, posts: list) -> dict:
    """Stage 1: Analyze posts for tradeable signals using local Qwen."""
    if not posts:
        return {"confidence": 0, "signal": None}

    try:
        combined = "\n".join(f"- {p}" for p in posts[:3])
        prompt = (
            f"You are a prediction market analyst. Given these recent X/Twitter posts about '{topic}', "
            f"determine if there's a tradeable signal.\n\n{combined}\n\n"
            f"Respond in JSON: {{\"has_signal\": true/false, \"confidence\": 0.0-1.0, "
            f"\"direction\": \"bullish/bearish/neutral\", \"summary\": \"one line\"}}"
        )

        timeout = min(OLLAMA_CFG.get("timeout_seconds", 15), 20)  # Cap at 20s per topic
        parsed = _call_ollama(prompt, timeout=timeout)

        if not parsed:
            _log(f"Qwen Stage 1 failed for {topic}")
            return {"confidence": 0, "signal": None}

        return {
            "confidence": float(parsed.get("confidence", 0)),
            "has_signal": parsed.get("has_signal", False),
            "direction": parsed.get("direction", "neutral"),
            "summary": parsed.get("summary", ""),
        }
    except Exception as e:
        _log(f"Stage 1 analysis error: {e}")
        return {"confidence": 0, "signal": None}


# ──────────────────────────────────────────────────────────────────────────────
# Stage 2: Materiality Gate
# ──────────────────────────────────────────────────────────────────────────────

def _load_signal_history() -> list:
    """Load history of previously sent X signal alerts."""
    history_path = STATE_DIR / "x_signal_history.json"
    try:
        with open(history_path) as f:
            data = json.load(f)
            # Only keep last 48h of history
            cutoff = time.time() - 48 * 3600
            return [h for h in data if h.get("timestamp", 0) > cutoff]
    except (OSError, json.JSONDecodeError):
        return []


def _save_signal_history(history: list):
    """Persist sent signal history."""
    history_path = STATE_DIR / "x_signal_history.json"
    try:
        # Keep max 200 entries
        with open(history_path, "w") as f:
            json.dump(history[-200:], f, indent=2)
    except OSError:
        pass


def _filter_novel_signals(signals: list, history: list) -> list:
    """Stage 2: Materiality gate — filter out noise and repeat signals."""
    if not signals:
        return []

    # Build history context for Qwen
    recent_summaries = []
    for h in history[-20:]:  # Last 20 sent signals
        ts = h.get("timestamp", 0)
        age_h = (time.time() - ts) / 3600
        recent_summaries.append(f"- [{age_h:.0f}h ago] {h.get('topic', '?')}: {h.get('summary', '')}")

    history_block = "\n".join(recent_summaries) if recent_summaries else "(No previous alerts sent)"

    # Build candidate signals block
    candidate_block = "\n".join(
        f"- [{s['topic']}] {s['summary']} (confidence: {s['confidence']:.0%}, direction: {s['direction']})"
        for s in signals
    )

    try:
        prompt = (
            "You are a personal alert filter for a prediction market trader. "
            "Your job is to PREVENT notification fatigue. Only let through signals that are genuinely NEW and MATERIAL.\n\n"
            "RECENTLY SENT ALERTS (what the user already knows):\n"
            f"{history_block}\n\n"
            "CANDIDATE NEW SIGNALS:\n"
            f"{candidate_block}\n\n"
            "RULES:\n"
            "- REJECT if the signal covers the same story/development as a recent alert (even with different wording)\n"
            "- REJECT if it's ongoing background noise (e.g. 'Trump discusses tariffs' when tariffs have been in the news for days)\n"
            "- REJECT if there's no concrete new event, just commentary or speculation\n"
            "- ACCEPT only if: (a) a genuinely new development occurred (vote, announcement, emergency, data release, market move), "
            "OR (b) a significant escalation/reversal of something previously reported\n"
            "- When in doubt, REJECT. The user prefers silence over noise.\n\n"
            "Respond in JSON: {\"keep\": [list of topic strings to keep], \"reasoning\": \"one line explaining why\"}"
        )

        timeout = min(OLLAMA_CFG.get("timeout_seconds", 15), 20)  # Cap at 20s
        parsed = _call_ollama(prompt, timeout=timeout)

        if not parsed:
            _log("Stage 2 filter: Qwen failed, dropping all signals (fail-closed)")
            return []  # Fail closed

        keep_topics = set(parsed.get("keep", []))
        reasoning = parsed.get("reasoning", "")

        filtered = [s for s in signals if s["topic"] in keep_topics]
        _log(f"Stage 2 filter: {len(signals)} candidates → {len(filtered)} kept. Reason: {reasoning}")
        return filtered

    except Exception as e:
        _log(f"Stage 2 filter error: {e}, dropping all signals (fail-closed)")
        return []  # Fail closed


# ──────────────────────────────────────────────────────────────────────────────
# Stage 3: Kalshi Position Matching
# ──────────────────────────────────────────────────────────────────────────────

def _get_active_kalshi_topics() -> list:
    """Fetch current Kalshi positions and extract keywords."""
    try:
        try:
            from kalshi_python_sync import Configuration, KalshiClient
        except ImportError:
            from kalshi_python import Configuration, KalshiClient

        if not KALSHI_CFG.get("enabled"):
            _log("Kalshi disabled in config")
            return []

        api_key_id = KALSHI_CFG.get("api_key_id")
        private_key_file = KALSHI_CFG.get("private_key_file")

        if not api_key_id or not private_key_file or api_key_id == "REPLACE_WITH_YOUR_KEY_ID":
            _log("Kalshi credentials missing or not configured")
            return []

        with open(private_key_file) as f:
            private_key = f.read()

        config = Configuration(
            host="https://api.elections.kalshi.com/trade-api/v2"
        )
        config.api_key_id = api_key_id
        config.private_key_pem = private_key

        client = KalshiClient(config)

        # Raw API call — avoids SDK v3 pydantic deserialization bug (Issue #9)
        resp = client._portfolio_api.get_positions_without_preload_content(limit=100)
        raw_data = json.loads(resp.read())
        _log(f"Raw positions API keys: {sorted(raw_data.keys())}")

        positions = (
            raw_data.get("event_positions")
            or raw_data.get("positions")
            or raw_data.get("market_positions")
            or []
        )

        # Filter to unsettled, non-zero positions locally
        filtered = []
        for p in positions:
            status = p.get("settlement_status")
            if status is not None and status != "unsettled":
                continue
            qty = int(float(p.get("position_fp") or p.get("position", 0) or 0))
            if qty != 0:
                filtered.append(p)
        positions = filtered

        if not positions:
            _log("Kalshi position gate: no active positions — suppressing all X signals")
            return []

        topics = []
        for pos in positions:
            # Handle both SDK objects (attributes) and dicts
            if isinstance(pos, dict):
                ticker = pos.get("ticker", "")
                title = pos.get("market_title", "") or pos.get("title", "")
                event_ticker = pos.get("event_ticker", "")
                side = pos.get("side", "")
                quantity = pos.get("total_traded", 0)
            else:
                ticker = getattr(pos, "ticker", "") or ""
                title = getattr(pos, "market_title", "") or getattr(pos, "title", "") or ""
                event_ticker = getattr(pos, "event_ticker", "") or ""
                side = getattr(pos, "side", "") or ""
                quantity = getattr(pos, "total_traded", 0) or 0

            keywords = set()
            for field in [ticker, title, event_ticker]:
                for word in field.lower().replace("-", " ").replace("_", " ").split():
                    if len(word) > 2:
                        keywords.add(word)

            topics.append({
                "ticker": ticker,
                "title": title,
                "keywords": keywords,
                "side": side,
                "quantity": quantity,
            })

        _log(f"Kalshi position gate: {len(topics)} active positions loaded")
        return topics

    except Exception as e:
        _log(f"Kalshi position gate error: {e}")
        return []


def _signal_matches_position(signal: dict, positions: list) -> Optional[dict]:
    """Check if signal matches any active Kalshi position (2+ keywords required)."""
    signal_topic = signal.get("topic", "").lower()
    signal_summary = signal.get("summary", "").lower()
    signal_words = set(signal_topic.replace("-", " ").replace("_", " ").split())
    signal_words |= set(w for w in signal_summary.split() if len(w) > 3)

    best_match = None
    best_overlap = 0

    for pos in positions:
        overlap = len(signal_words & pos["keywords"])
        if overlap >= 2 and overlap > best_overlap:
            best_overlap = overlap
            best_match = pos

    return best_match


# ──────────────────────────────────────────────────────────────────────────────
# Main Trigger
# ──────────────────────────────────────────────────────────────────────────────

def check_x_signals(state: dict, dry_run: bool = False, force: bool = False) -> bool:
    """Scan X/Twitter for market-relevant signals via DuckDuckGo + local Qwen."""
    if not XPULSE_CFG.get("enabled", True):
        return False

    interval = XPULSE_CFG.get("check_interval_minutes", 30)
    last_check = state.get("last_x_signal_check", 0)
    if not force and time.time() - last_check < interval * 60:
        return False

    state["last_x_signal_check"] = time.time()
    topics = XPULSE_CFG.get("topics", [])
    min_confidence = XPULSE_CFG.get("min_confidence", 0.7)

    if not topics:
        logging.info(
            "⚠️  Xpulse: no topics configured — nothing to scan.\n"
            "\n"
            "   Add topics to ~/.openclaw/config.yaml:\n"
            "     xpulse:\n"
            "       enabled: true\n"
            "       topics:\n"
            "         - tariffs\n"
            "         - federal reserve\n"
            "         - bitcoin\n"
            "\n"
            "   Then run again: python xpulse.py --dry-run --force"
        )
        return False

    # Check Ollama availability only when we have topics to scan
    _check_ollama_model()

    _log(f"X signal scanner starting... ({len(topics)} topics)")

    # ── Stage 1: Signal Detection (parallelized) ──────────────────────────────
    from concurrent.futures import ThreadPoolExecutor, as_completed

    def _scan_topic(topic):
        """Scan a single topic — called in parallel."""
        posts = _search_x_posts(topic)
        if not posts:
            return None
        _log(f"  {topic}: {len(posts)} posts found")
        analysis = _analyze_signals_local(topic, posts)
        if analysis.get("has_signal") and analysis.get("confidence", 0) >= min_confidence:
            return {
                "topic": topic,
                "confidence": analysis["confidence"],
                "direction": analysis.get("direction", "?"),
                "summary": analysis.get("summary", ""),
                "post_count": len(posts),
            }
        return None

    signals = []
    with ThreadPoolExecutor(max_workers=min(len(topics), 2)) as executor:  # 2 workers max on Mac Mini
        futures = {executor.submit(_scan_topic, t): t for t in topics}
        for future in as_completed(futures, timeout=30):  # 30s total for all topics
            try:
                result = future.result(timeout=10)
                if result:
                    signals.append(result)
            except Exception as e:
                _log(f"  Topic scan error: {e}")

    # Cache all Stage 1 signals for morning brief
    cache_path = STATE_DIR / "x_signal_cache.json"
    try:
        from datetime import datetime as _dt, timezone as _tz
        with open(cache_path, "w") as f:
            json.dump({
                "signals": signals,
                "topics_scanned": len(topics),
                "cached_at": _dt.now(_tz.utc).isoformat(),
                "timestamp": time.time(),
            }, f, indent=2)
    except OSError:
        pass

    _log(f"X scanner: {len(signals)} high-confidence signals from {len(topics)} topics")

    if not signals:
        return False

    signals_found = len(signals)

    # ── Stage 2: Materiality Gate ──────────────────────────────────────────────
    signal_history = _load_signal_history()
    use_materiality = XPULSE_CFG.get("materiality_gate", True)

    if use_materiality:
        signals = _filter_novel_signals(signals, signal_history)
        if not signals:
            _log("X scanner: all signals filtered by materiality gate (nothing new)")
            return False

    # ── Stage 3: Kalshi Position Gate ──────────────────────────────────────────
    kalshi_positions = _get_active_kalshi_topics()

    if not kalshi_positions:
        _log("X scanner: no active Kalshi positions — all signals suppressed (logged only)")
        state["last_x_signals_silent"] = [
            {"topic": s["topic"], "summary": s["summary"][:80], "confidence": s["confidence"]}
            for s in signals
        ]
        return False

    critical_signals = []
    silent_signals = []

    for s in signals:
        match = _signal_matches_position(s, kalshi_positions)
        if match:
            s["matched_position"] = match["ticker"]
            s["position_side"] = match["side"]
            critical_signals.append(s)
        else:
            silent_signals.append(s)

    if silent_signals:
        _log(f"X scanner: {len(silent_signals)} signals suppressed (no matching Kalshi position)")
        state["last_x_signals_silent"] = [
            {"topic": s["topic"], "summary": s["summary"][:80], "confidence": s["confidence"]}
            for s in silent_signals
        ]

    if not critical_signals:
        _log("X scanner: signals found but none match active Kalshi positions — silent")
        return False

    # ── Format Alert Message ───────────────────────────────────────────────────
    critical_signals.sort(key=lambda x: x["confidence"], reverse=True)
    parts = ["⚠️ X signal — affects your Kalshi positions:"]
    for s in critical_signals[:3]:
        icon = "📈" if s["direction"] == "bullish" else "📉" if s["direction"] == "bearish" else "➡️ "
        pos_info = f"[{s.get('matched_position', '?')}]"
        parts.append(f"  {icon} {s['topic']}: {s['summary'][:80]} ({int(s['confidence']*100)}% conf) {pos_info}")

    message = "\n".join(parts)

    # ── Send Alert (or dry-run) ────────────────────────────────────────────────
    if dry_run:
        _log(f"[DRY RUN] Would send: {message}")
        return False

    # In production, the agent/caller handles message routing
    # For standalone testing, just print
    print(message)
    _log(f"X signal CRITICAL alert: {len(critical_signals)} signals matching Kalshi positions")

    # ── Update History ─────────────────────────────────────────────────────────
    for s in critical_signals[:3]:
        signal_history.append({
            "topic": s["topic"],
            "summary": s["summary"],
            "direction": s["direction"],
            "confidence": s["confidence"],
            "matched_position": s.get("matched_position"),
            "timestamp": time.time(),
        })
    _save_signal_history(signal_history)

    return True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Xpulse — X/Twitter signal scanner")
    parser.add_argument("--dry-run", action="store_true", help="Log but don't send alerts")
    parser.add_argument("--force", action="store_true", help="Force run regardless of interval")
    args = parser.parse_args()

    state = {}
    try:
        result = check_x_signals(state, dry_run=args.dry_run, force=args.force)
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        _log("Interrupted")
        sys.exit(130)
    except Exception as e:
        _log(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
