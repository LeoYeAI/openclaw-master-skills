"""Claude Sonnet contrarian probability estimation for prediction markets.

CONTRARIAN MODE: Claude sees the market price and is asked to find reasons
the market is WRONG. This produces opinionated, directional recommendations
instead of consensus-matching estimates that yield zero edge.

Assumes limit orders (no spread penalty). Edge = |estimate - market price|.

Estimator chain: Claude CLI (Max subscription, $0) → Anthropic API → Qwen local.
"""

import json
import os
import subprocess
import time
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# ── Claude CLI Interface (Primary — uses Max subscription at $0) ──────────

def _claude_cli_estimate(prompt: str, system: str, timeout: int = 60) -> Optional[dict]:
    """Call Claude via CLI (claude -p) which uses Max subscription.

    Zero marginal cost. Primary estimator path.
    """
    try:
        # Combine system + user prompt for CLI
        full_prompt = f"{system}\n\n---\n\n{prompt}"

        result = subprocess.run(
            ["claude", "-p", full_prompt, "--output-format", "text"],
            capture_output=True,
            text=True,
            timeout=timeout,
            start_new_session=True,  # Prevent SIGTTOU when backgrounded
        )

        if result.returncode != 0:
            stderr = result.stderr.strip()[:200] if result.stderr else ""
            logger.warning(f"Claude CLI: non-zero exit ({result.returncode}): {stderr}")
            return None

        text = result.stdout.strip()
        if not text:
            logger.warning("Claude CLI: empty response")
            return None

        return _parse_json_response(text)

    except subprocess.TimeoutExpired:
        logger.warning("Claude CLI: timeout (%ds)", timeout)
        return None
    except FileNotFoundError:
        logger.warning("Claude CLI: 'claude' command not found — falling back to API")
        return None
    except Exception as e:
        logger.error(f"Claude CLI error: {str(e)[:200]}")
        return None


# ── Claude API Interface (Fallback — requires ANTHROPIC_API_KEY) ──────────

def _load_anthropic_key() -> Optional[str]:
    """Load ANTHROPIC_API_KEY from env or ~/.openclaw/.env file."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return key
    # Try loading from .env file
    env_path = Path.home() / ".openclaw" / ".env"
    if env_path.exists():
        try:
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if line.startswith("export ANTHROPIC_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if key:
                        os.environ["ANTHROPIC_API_KEY"] = key
                        logger.info("Loaded ANTHROPIC_API_KEY from ~/.openclaw/.env")
                        return key
                elif line.startswith("ANTHROPIC_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if key:
                        os.environ["ANTHROPIC_API_KEY"] = key
                        logger.info("Loaded ANTHROPIC_API_KEY from ~/.openclaw/.env")
                        return key
        except Exception as e:
            logger.warning(f"Failed to read .env: {e}")
    return None


def _claude_api_estimate(prompt: str, system: str, timeout: int = 45) -> Optional[dict]:
    """Call Claude Sonnet via Anthropic API. Fallback if CLI is unavailable.

    Requires ANTHROPIC_API_KEY in environment or ~/.openclaw/.env. Costs per-token.
    """
    if not _load_anthropic_key():
        logger.debug("Claude API: no ANTHROPIC_API_KEY found, skipping")
        return None

    try:
        import anthropic

        client = anthropic.Anthropic()

        message = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=512,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )

        text = ""
        for block in message.content:
            if hasattr(block, "text"):
                text += block.text

        if not text:
            logger.warning("Claude API: empty response")
            return None

        return _parse_json_response(text.strip())

    except Exception as e:
        error_str = str(e)
        if "api_key" in error_str.lower() or "auth" in error_str.lower():
            logger.error(f"Claude API: auth error (key may be invalid)")
        else:
            logger.error(f"Claude API error: {error_str[:200]}")
        return None


# ── JSON Parser ──────────────────────────────────────────────────────────

def _parse_json_response(text: str) -> Optional[dict]:
    """Extract JSON from Claude response text."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
    logger.warning("Claude: failed to parse JSON from response")
    return None


# ── Unified Estimator (CLI → API → Qwen) ─────────────────────────────────

def _claude_estimate(prompt: str, system: str, timeout: int = 60) -> Optional[dict]:
    """Call Claude with fallback chain: CLI (Max, $0) → API (per-token) → None.

    Qwen fallback is handled at the batch level, not here.
    """
    # 1. Try CLI first (Max subscription, zero cost)
    result = _claude_cli_estimate(prompt, system, timeout=timeout)
    if result:
        logger.debug("Claude CLI: success")
        return result

    # 2. Fall back to API (per-token cost)
    result = _claude_api_estimate(prompt, system, timeout=timeout)
    if result:
        logger.debug("Claude API: success (fallback)")
        return result

    return None


# ── System Prompt ──────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """You are a contrarian prediction market analyst. You look for reasons markets are WRONG.

Your job: given a prediction market and its current price, determine if there's a directional opportunity. You are advising a sophisticated trader who uses limit orders.

CRITICAL RULES:
1. You WILL be shown the current market price. Your job is to DISAGREE with it when you have reason to.
2. Don't just confirm the market. That's worthless. Look for what the market is MISSING or LAGGING on.
3. Consider: breaking news the market hasn't priced, political dynamics shifting, timing mismatches, crowd psychology errors, base rate neglect by the market.
4. Be opinionated. A 50% estimate on a 50% market is useless. Either find a reason it's wrong or say confidence is low.
5. Weight recent developments HEAVILY — markets are often slow to react to news in the last 24-48 hours.
6. Think about asymmetric upside: where is the cost of being wrong low but the payoff of being right high?

You must respond with ONLY a JSON object, no other text:
{
  "estimated_probability": <float 0.01-0.99>,
  "confidence": <float 0.0-1.0>,
  "reasoning": "<one sentence explaining WHY the market is wrong>",
  "key_factors": ["<factor 1>", "<factor 2>", "<factor 3>"],
  "conviction": "<strong|moderate|weak>"
}"""


def _load_system_prompt() -> str:
    """Load system prompt — premium from ~/prompt-lab/prompt.md, else built-in free tier."""
    premium_path = Path.home() / "prompt-lab" / "prompt.md"
    if premium_path.exists():
        try:
            prompt = premium_path.read_text().strip()
            if prompt:
                logger.info("Loaded premium prompt from %s (%d chars)", premium_path, len(prompt))
                return prompt
        except Exception as e:
            logger.warning("Failed to load premium prompt: %s", e)
    return _SYSTEM_PROMPT


_ACTIVE_PROMPT = _load_system_prompt()


# ── Probability Estimation ──────────────────────────────────────────────

def estimate_probability(
    market_title: str,
    days_to_close: Optional[float],
    news_context: Optional[list[dict]] = None,
    economic_context: Optional[dict] = None,
    x_signal: Optional[dict] = None,
    market_price_cents: Optional[int] = None,
) -> Optional[dict]:
    """Estimate true probability for a prediction market — CONTRARIAN (sees market price).

    Returns:
        {
            "estimated_probability": 0.0-1.0,
            "confidence": 0.0-1.0,
            "reasoning": "one line",
            "key_factors": [...],
            "conviction": "strong|moderate|weak",
            "estimator": "claude"
        }
    """
    # Build context blocks
    context_parts = []

    if news_context:
        news_block = "\n".join(
            f"  - [{n.get('source', '?')}] {n.get('title', '')} "
            f"({n.get('published_utc', '')[:10] if n.get('published_utc') else '?'})"
            for n in news_context[:8]
        )
        context_parts.append(f"RECENT NEWS:\n{news_block}")

    if economic_context:
        econ_lines = []
        if "sp500" in economic_context:
            sp = economic_context["sp500"]
            econ_lines.append(f"  S&P 500: ${sp.get('close', '?')} ({sp.get('change_pct', 0):+.1f}%)")
        if "btc" in economic_context:
            btc = economic_context["btc"]
            econ_lines.append(f"  Bitcoin: ${btc.get('price', '?'):,.0f} ({btc.get('change_pct', 0):+.1f}%)")
        if "vix_proxy" in economic_context:
            vix = economic_context["vix_proxy"]
            econ_lines.append(f"  VIX proxy (VIXY): ${vix.get('close', '?')} ({vix.get('change_pct', 0):+.1f}%)")
        if "gold_proxy" in economic_context:
            gold = economic_context["gold_proxy"]
            econ_lines.append(f"  Gold (GLD): ${gold.get('close', '?')} ({gold.get('change_pct', 0):+.1f}%)")
        if econ_lines:
            context_parts.append(f"ECONOMIC INDICATORS:\n" + "\n".join(econ_lines))

    if x_signal:
        sig_line = (
            f"  X/Twitter signal: {x_signal.get('direction', '?')} on "
            f"'{x_signal.get('topic', '?')}' — {x_signal.get('summary', '')}"
        )
        context_parts.append(f"SOCIAL SIGNAL:\n{sig_line}")

    context_block = "\n\n".join(context_parts) if context_parts else "(No additional context available — estimate from general knowledge)"

    days_str = f"{days_to_close:.0f} days" if days_to_close is not None else "unknown timeframe"

    # Show the market price — contrarian mode
    price_str = ""
    if market_price_cents is not None:
        market_pct = market_price_cents
        price_str = f"\nCURRENT MARKET PRICE: {market_pct}¢ (market implies {market_pct}% probability)"
        price_str += f"\nYour job: Is this price WRONG? If yes, in which direction and why?"

    prompt = f"""EVENT: {market_title}
TIME TO RESOLUTION: {days_str}{price_str}

{context_block}

Is the market mispricing this? Give your true probability estimate and explain why the market is wrong (or say confidence is low if you agree with the market). Respond with JSON only."""

    result = _claude_estimate(prompt, _ACTIVE_PROMPT)
    if not result:
        return None

    try:
        est_prob = float(result.get("estimated_probability", 0.5))
        confidence = float(result.get("confidence", 0.3))
        reasoning = result.get("reasoning", "")

        # Clamp values
        est_prob = max(0.01, min(0.99, est_prob))
        confidence = max(0.0, min(1.0, confidence))

        return {
            "estimated_probability": round(est_prob, 4),
            "confidence": round(confidence, 4),
            "reasoning": reasoning[:200],
            "key_factors": result.get("key_factors", [])[:3],
            "estimator": "claude",
        }

    except (ValueError, TypeError, KeyError) as e:
        logger.error(f"Claude parse error: {e}")
        return None


# ── Batch Estimation ──────────────────────────────────────────────────────

def estimate_batch(
    markets: list[dict],
    economic_context: Optional[dict] = None,
    max_markets: int = 50,
) -> list[dict]:
    """Run contrarian probability estimation on a batch of markets.

    Uses Claude Sonnet as primary estimator (sees price, finds disagreements).
    Falls back to local Qwen if Claude is unavailable (cooldown, network, auth).

    Each market dict should have: title, yes_price (cents), yes_bid, yes_ask,
    days_to_close, news (optional), x_signal (optional).

    Returns list of estimation results with edge calculations attached.
    """
    results = []
    claude_failures = 0
    claude_successes = 0
    max_consecutive_failures = 3

    for m in markets[:max_markets]:
        title = m.get("title", "?")
        price = m.get("yes_price", 50)
        days = m.get("days_to_close")
        news = m.get("news", [])
        x_sig = m.get("x_signal")
        yes_bid = m.get("yes_bid", 0)
        yes_ask = m.get("yes_ask", 0)
        spread = yes_ask - yes_bid if (yes_bid and yes_ask) else 0

        logger.info(f"  Claude analyzing: {title[:50]}...")
        est = estimate_probability(
            market_title=title,
            days_to_close=days,
            news_context=news if news else None,
            economic_context=economic_context,
            x_signal=x_sig,
            market_price_cents=price,
        )

        # Fallback to Qwen if Claude fails
        if not est:
            claude_failures += 1
            if claude_failures >= max_consecutive_failures and claude_successes == 0:
                logger.warning("Claude: switching to Qwen fallback (3 consecutive failures)")
                return _qwen_fallback_batch(markets, economic_context, max_markets)

            logger.warning(f"  Falling back to Qwen for: {title[:40]}")
            est = _qwen_estimate_single(title, price, days, news, economic_context, x_sig)

        if not est:
            continue

        claude_successes += 1 if est.get("estimator") == "claude" else 0

        # Calculate edge
        market_implied = price / 100.0
        est_prob = est["estimated_probability"]
        raw_edge_pct = abs(est_prob - market_implied) * 100
        spread_cost_pct = 0.0  # Limit orders
        effective_edge_pct = raw_edge_pct

        direction = (
            "underpriced" if est_prob > market_implied
            else "overpriced" if est_prob < market_implied
            else "fair"
        )

        if est["confidence"] > 0.2:
            results.append({
                **m,
                **est,
                "market_implied": round(market_implied, 4),
                "direction": direction,
                "edge_pct": round(raw_edge_pct, 1),
                "spread_cost_pct": round(spread_cost_pct, 1),
                "effective_edge_pct": round(effective_edge_pct, 1),
            })

        time.sleep(1.0)  # Rate limiting

    logger.info(f"Claude: {claude_successes} Claude / {claude_failures} fallback")
    return results


def _qwen_estimate_single(title, price, days, news, econ, x_sig) -> Optional[dict]:
    """Single-market Qwen fallback when Claude is unavailable."""
    try:
        from qwen_analyzer import estimate_probability as qwen_estimate
        est = qwen_estimate(
            market_title=title,
            market_price_cents=price,
            days_to_close=days,
            news_context=news,
            economic_context=econ,
            x_signal=x_sig,
        )
        if est:
            est["estimator"] = "qwen"
        return est
    except Exception as e:
        logger.error(f"Qwen fallback error: {e}")
        return None


def _qwen_fallback_batch(markets, econ_context, max_markets) -> list[dict]:
    """Full batch fallback to Qwen when Claude is completely unavailable."""
    logger.warning("Claude: full Qwen fallback mode")
    try:
        from qwen_analyzer import estimate_batch as qwen_batch
        results = qwen_batch(markets, economic_context=econ_context, max_markets=max_markets)

        enriched = []
        for r in results:
            raw_edge = r.get("edge_pct", 0)
            r["spread_cost_pct"] = 0.0
            r["effective_edge_pct"] = round(raw_edge, 1)
            r["estimator"] = "qwen"
            enriched.append(r)

        return enriched
    except Exception as e:
        logger.error(f"Qwen fallback batch error: {e}")
        return []
