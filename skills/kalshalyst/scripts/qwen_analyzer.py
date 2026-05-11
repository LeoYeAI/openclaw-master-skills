"""
Qwen (Ollama) probability estimator for Kalshalyst.
Used as fallback when Claude is unavailable.

Contrarian mode: shows market price, asks Qwen to find disagreements.
"""

import json
import time
import logging
import urllib.request
import urllib.error
from typing import Optional

logger = logging.getLogger(__name__)

OLLAMA_BASE = "http://localhost:11434"
MODEL = "qwen3:latest"

_SYSTEM = """You are a contrarian prediction market analyst. You look for reasons markets are WRONG.

Given a prediction market and its current price, determine if there's a directional opportunity.

CRITICAL RULES:
1. You see the market price. Your job is to DISAGREE when you have reason to.
2. Don't confirm the market — that's worthless.
3. Consider: lagging news, crowd psychology errors, base rate neglect, timing mismatches.
4. Be opinionated. A 50% estimate on a 50% market is useless.

You MUST respond with ONLY a JSON object (no other text, no thinking tags):
{
  "estimated_probability": <float 0.01-0.99>,
  "confidence": <float 0.0-1.0>,
  "reasoning": "<one sentence explaining WHY the market is wrong>",
  "key_factors": ["<factor 1>", "<factor 2>", "<factor 3>"],
  "conviction": "<strong|moderate|weak>"
}"""


def _call_ollama(prompt: str, timeout: int = 60) -> Optional[dict]:
    """Call Ollama API for a single estimation."""
    payload = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 512,
        },
    }).encode()

    try:
        req = urllib.request.Request(
            f"{OLLAMA_BASE}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())

        text = data.get("message", {}).get("content", "")
        if not text:
            return None

        # Strip thinking tags if present (qwen3 sometimes outputs <think>...</think>)
        if "<think>" in text:
            end_think = text.find("</think>")
            if end_think >= 0:
                text = text[end_think + 8:].strip()

        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
        return None

    except Exception as e:
        logger.error(f"Ollama error: {e}")
        return None


def estimate_probability(
    market_title: str,
    market_price_cents: Optional[int],
    days_to_close: Optional[float],
    news_context=None,
    economic_context=None,
    x_signal=None,
) -> Optional[dict]:
    """Estimate true probability using local Qwen (contrarian mode)."""
    days_str = f"{days_to_close:.0f} days" if days_to_close is not None else "unknown timeframe"
    price_str = ""
    if market_price_cents is not None:
        price_str = (
            f"\nCURRENT MARKET PRICE: {market_price_cents}¢ "
            f"(market implies {market_price_cents}% probability)"
            f"\nIs this price WRONG? If yes, in which direction and why?"
        )

    context_parts = []
    if news_context:
        block = "\n".join(
            f"  - {n.get('title','')}" for n in news_context[:5]
        )
        context_parts.append(f"RECENT NEWS:\n{block}")
    if x_signal:
        context_parts.append(
            f"SOCIAL SIGNAL: {x_signal.get('direction','?')} on '{x_signal.get('topic','?')}'"
        )

    context = "\n\n".join(context_parts) if context_parts else "(No additional context)"

    prompt = f"""EVENT: {market_title}
TIME TO RESOLUTION: {days_str}{price_str}

{context}

Respond with JSON only."""

    result = _call_ollama(prompt)
    if not result:
        return None

    try:
        est_prob = float(result.get("estimated_probability", 0.5))
        confidence = float(result.get("confidence", 0.3))
        est_prob = max(0.01, min(0.99, est_prob))
        confidence = max(0.0, min(1.0, confidence))

        return {
            "estimated_probability": round(est_prob, 4),
            "confidence": round(confidence, 4),
            "reasoning": result.get("reasoning", "")[:200],
            "key_factors": result.get("key_factors", [])[:3],
            "estimator": "qwen",
        }
    except Exception as e:
        logger.error(f"Qwen parse error: {e}")
        return None


def estimate_batch(
    markets: list,
    economic_context=None,
    max_markets: int = 50,
) -> list:
    """Batch estimation using Qwen."""
    results = []
    successes = 0

    for m in markets[:max_markets]:
        title = m.get("title", "?")
        price = m.get("yes_price", 50)
        days = m.get("days_to_close")
        news = m.get("news", [])
        x_sig = m.get("x_signal")

        logger.info(f"  Qwen analyzing: {title[:50]}...")
        est = estimate_probability(
            market_title=title,
            market_price_cents=price,
            days_to_close=days,
            news_context=news if news else None,
            economic_context=economic_context,
            x_signal=x_sig,
        )

        if not est or est.get("confidence", 0) < 0.2:
            continue

        successes += 1
        market_implied = price / 100.0
        est_prob = est["estimated_probability"]
        raw_edge_pct = abs(est_prob - market_implied) * 100
        direction = (
            "underpriced" if est_prob > market_implied
            else "overpriced" if est_prob < market_implied
            else "fair"
        )

        results.append({
            **m,
            **est,
            "market_implied": round(market_implied, 4),
            "direction": direction,
            "edge_pct": round(raw_edge_pct, 1),
            "spread_cost_pct": 0.0,
            "effective_edge_pct": round(raw_edge_pct, 1),
        })

        time.sleep(0.5)

    logger.info(f"Qwen: {successes} estimates complete")
    return results
