"""Sports market probability estimation — data-driven model.

EXPERIMENTAL — NOT PRODUCTION-READY. Corrected eval (March 13, 2026) shows
model does NOT beat market overall (Brier 0.1984 vs 0.1979, model WORSE).
Only soccer ELO has demonstrated edge (-0.006 delta). Previous "beating"
claims were artifact of P1-A bug (eval scored wrong side for ~80% of entries).

CORE INSIGHT (corrected eval on 8,983 enriched markets across 9 sports):
    Raw model predictions (ELO, etc.) are WORSE than market prices.
    Market-anchored prediction (nudge market price, don't replace it) is the
    only viable approach. Even then, only soccer ELO shows real edge.

CORRECTED RESULTS (March 13, 2026):
    1. SOCCER ELO — Brier 0.1753 vs market 0.1815 (-0.006 delta, BEATING)
    2. BASKETBALL ELO — Brier 0.1955 vs market 0.1906 (+0.005, WORSE)
    3. HOCKEY ELO — Brier 0.2356 vs market 0.2357 (wash)
    4. CENTER-NUDGE — Brier 0.1980 vs ~0.198 market (wash)

ARCHITECTURE:
    The estimator outputs the same schema as claude_estimator.py so it plugs
    directly into kalshalyst's calculate_edges() without changes downstream.

PREMIUM GATE:
    This module is PREMIUM ONLY. The sports filter in _SPORTS_TOKENS blocks all
    sports markets from reaching the free-tier Claude estimator. Auto_trader
    sports routing is DISABLED until model demonstrates consistent edge.
    Config file acts as the license gate:
      ~/sports_estimator_config.json

DATA PIPELINES:
    - Soccer: ~/prompt-lab/soccer_data.py (openfootball, 5 leagues, ONLY PIPELINE WITH EDGE)
    - Hockey: ~/prompt-lab/hockey_data.py (NHL API → team ELO, NO DEMONSTRATED EDGE)
    - Basketball: ~/prompt-lab/basketball_data.py (hardcoded baseline, WORSE THAN MARKET)
    - Tennis: ~/prompt-lab/tennis_data.py (DISABLED — stale 2024 Sackmann data)

AUTORESEARCH TARGET:
    Editable file: ~/prompt-lab/sports_model_weights.json
    Eval metric: Brier score on resolved sports markets
    Backtest: ~/prompt-lab/sports_backtest.json (9,107 entries, 8,983 enriched, 9 sports)

USAGE:
    from sports_estimator import estimate_sports_market

    result = estimate_sports_market(
        ticker="KXNHL-26MAR11-BOSTOR-BOS",
        title="Boston Bruins at Toronto Maple Leafs",
        market_price_cents=55,
        sport="hockey",
    )
    # Returns same schema as claude_estimator output:
    # {"probability": 0.52, "confidence": 0.40, "reasoning": "...", "estimator": "sports_v1"}
"""

import json
import logging
import re
import sys
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────────────────

SPORTS_CONFIG_PATH = Path.home() / "sports_estimator_config.json"
SPORTS_WEIGHTS_PATH = Path.home() / "prompt-lab" / "sports_model_weights.json"
HOCKEY_DATA_DIR = Path.home() / "prompt-lab"

# Sport detection from Kalshi ticker prefixes
SPORT_ROUTING = {
    # Ticker prefix → sport key
    "kxatp": "tennis",
    "kxwta": "tennis",
    "challengermatch": "tennis",
    "kxnba": "basketball",
    "nbaspread": "basketball",
    "nbagame": "basketball",
    "kxnfl": "football",
    "nflspread": "football",
    "nflgame": "football",
    "kxmlb": "baseball",
    "mlbgame": "baseball",
    "kxnhl": "hockey",
    "nhlgame": "hockey",
    "kxncaa": "college",
    "ncaambgame": "college",
    "ncaafbgame": "college",
    "kxufc": "mma",
    "kxmma": "mma",
    "kxlol": "esports",
    "lolgame": "esports",
    "kxvalorant": "esports",
    "kxcsgo": "esports",
    "kxdota": "esports",
    "kxnascar": "motorsport",
    "kxf1": "motorsport",
}

# ── Default weights ──────────────────────────────────────────────────────

DEFAULT_WEIGHTS = {
    "hockey_nudge": 0.10,          # How much to nudge market toward ELO (hockey)
    "basketball_nudge": 0.10,      # How much to nudge market toward ELO (basketball)
    "soccer_nudge": 0.10,          # How much to nudge market toward ELO (soccer)
    "center_nudge": 0.10,          # How much to nudge market toward 0.50 (all other)
    "hockey_confidence": 0.40,     # Confidence for hockey ELO predictions
    "basketball_confidence": 0.42, # Confidence for basketball ELO predictions
    "soccer_confidence": 0.38,     # Confidence for soccer ELO predictions
    "center_confidence": 0.30,     # Confidence for center-nudge predictions
    "max_confidence": 0.70,        # Confidence cap
    "version": "1.1.0",
}


def _load_config() -> Optional[dict]:
    """Load sports estimator config. Returns None if not configured (free tier)."""
    if not SPORTS_CONFIG_PATH.exists():
        return None
    try:
        with open(SPORTS_CONFIG_PATH) as f:
            cfg = json.load(f)
        if not cfg.get("enabled", False):
            return None
        return cfg
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Sports config load error: {e}")
        return None


def _load_weights() -> dict:
    """Load model weights from autoresearch-tunable config."""
    if not SPORTS_WEIGHTS_PATH.exists():
        return DEFAULT_WEIGHTS.copy()
    try:
        with open(SPORTS_WEIGHTS_PATH) as f:
            loaded = json.load(f)
        # Merge with defaults so new keys are always present
        merged = DEFAULT_WEIGHTS.copy()
        merged.update(loaded)
        return merged
    except (json.JSONDecodeError, OSError):
        return DEFAULT_WEIGHTS.copy()


# ── Sport Detection ───────────────────────────────────────────────────────

def detect_sport(ticker: str) -> Optional[str]:
    """Detect sport from Kalshi ticker prefix.

    Returns sport key (tennis, basketball, etc.) or None if not a sports market.
    """
    ticker_lower = ticker.lower()
    for prefix, sport in SPORT_ROUTING.items():
        if prefix in ticker_lower:
            return sport
    return None


# ── Hockey Pipeline (lazy-loaded) ────────────────────────────────────────

_hockey_pipeline = None
_hockey_pipeline_attempted = False


def _get_hockey_pipeline():
    """Lazy-load the hockey data pipeline from ~/prompt-lab/hockey_data.py.

    Returns the pipeline object or None if unavailable.
    Caches the result so we only attempt loading once.
    """
    global _hockey_pipeline, _hockey_pipeline_attempted
    if _hockey_pipeline_attempted:
        return _hockey_pipeline

    _hockey_pipeline_attempted = True

    try:
        # Add hockey_data.py location to path
        hockey_path = str(HOCKEY_DATA_DIR)
        if hockey_path not in sys.path:
            sys.path.insert(0, hockey_path)

        from hockey_data import HockeyDataPipeline
        pipe = HockeyDataPipeline()
        if pipe.ensure_data():
            _hockey_pipeline = pipe
            logger.info("Hockey data pipeline loaded successfully")
        else:
            logger.warning("Hockey data pipeline failed to load data")
            _hockey_pipeline = None
    except Exception as e:
        logger.warning(f"Hockey pipeline import failed: {e}")
        _hockey_pipeline = None

    return _hockey_pipeline


# ── Basketball Pipeline (lazy-loaded) ────────────────────────────────────

_basketball_pipeline = None
_basketball_pipeline_attempted = False


def _get_basketball_pipeline():
    """Lazy-load the basketball data pipeline from ~/prompt-lab/basketball_data.py.

    Returns the pipeline object or None if unavailable.
    Caches the result so we only attempt loading once.
    """
    global _basketball_pipeline, _basketball_pipeline_attempted
    if _basketball_pipeline_attempted:
        return _basketball_pipeline

    _basketball_pipeline_attempted = True

    try:
        # Add basketball_data.py location to path
        basketball_path = str(HOCKEY_DATA_DIR)
        if basketball_path not in sys.path:
            sys.path.insert(0, basketball_path)

        from basketball_data import BasketballDataPipeline
        pipe = BasketballDataPipeline()
        if pipe.ensure_data():
            _basketball_pipeline = pipe
            logger.info("Basketball data pipeline loaded successfully")
        else:
            logger.warning("Basketball data pipeline failed to load data")
            _basketball_pipeline = None
    except Exception as e:
        logger.warning(f"Basketball pipeline import failed: {e}")
        _basketball_pipeline = None

    return _basketball_pipeline


# ── Soccer Pipeline (lazy-loaded) ────────────────────────────────────────

_soccer_pipeline = None
_soccer_pipeline_attempted = False


def _get_soccer_pipeline():
    """Lazy-load the soccer data pipeline from ~/prompt-lab/soccer_data.py.

    Returns the pipeline object or None if unavailable.
    Caches the result so we only attempt loading once.
    """
    global _soccer_pipeline, _soccer_pipeline_attempted
    if _soccer_pipeline_attempted:
        return _soccer_pipeline

    _soccer_pipeline_attempted = True

    try:
        # Add soccer_data.py location to path
        soccer_path = str(HOCKEY_DATA_DIR)
        if soccer_path not in sys.path:
            sys.path.insert(0, soccer_path)

        from soccer_data import SoccerDataPipeline
        pipe = SoccerDataPipeline()
        if pipe.ensure_data():
            _soccer_pipeline = pipe
            logger.info("Soccer data pipeline loaded successfully")
        else:
            logger.warning("Soccer data pipeline failed to load data")
            _soccer_pipeline = None
    except Exception as e:
        logger.warning(f"Soccer pipeline import failed: {e}")
        _soccer_pipeline = None

    return _soccer_pipeline


# ── Competitor Parsing ───────────────────────────────────────────────────

def _parse_competitors(title: str, sport: str) -> Optional[tuple]:
    """Parse competitor names from market title.

    Kalshi title formats:
      Team sports: "Boston Bruins at Toronto Maple Leafs"
                   "Houston vs Denver NBA spread"
      Tennis:      "Will Navone win the Navone vs Hardt : Round of 32"

    CRITICAL: Kalshi "X at Y" format → X is AWAY, Y is HOME.

    Returns (competitor_a, competitor_b) or None.
    """
    # Pattern 1: "X at Y" (team sports — Kalshi standard)
    at_match = re.search(
        r'([\w][\w\s.]*?)\s+at\s+([\w][\w\s.]*?)(?:\s*[:\-|,]|\s*$)',
        title, re.IGNORECASE
    )
    if at_match:
        return (at_match.group(1).strip(), at_match.group(2).strip())

    # Pattern 2: "X vs Y" or "X vs. Y"
    vs_match = re.search(
        r'([\w][\w\s]*?)\s+vs\.?\s+([\w][\w\s]*?)(?:\s*[:\-|]|\s*$)',
        title, re.IGNORECASE
    )
    if vs_match:
        return (vs_match.group(1).strip(), vs_match.group(2).strip())

    # Pattern 3: "Will X win the X vs Y"
    will_match = re.search(
        r'will\s+(.+?)\s+win\s+the\s+(.+?)\s+vs\.?\s+(.+?)(?:\s*[:\-|]|\s*$)',
        title, re.IGNORECASE
    )
    if will_match:
        return (will_match.group(2).strip(), will_match.group(3).strip())

    return None


# ── Core Estimator ────────────────────────────────────────────────────────

def estimate_sports_market(
    ticker: str,
    title: str,
    market_price_cents: int,
    sport: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> Optional[dict]:
    """Estimate probability for a sports market using structured data.

    Returns same schema as claude_estimator for seamless pipeline integration:
        {
            "probability": float,      # 0-1, estimated true probability of YES
            "confidence": float,       # 0-1, model confidence in estimate
            "reasoning": str,          # Human-readable explanation
            "estimator": str,          # "sports_v1.0.0"
            "sport": str,             # Detected sport
        }

    Returns None if:
        - Sports estimator not configured (free tier)
        - Sport not detected
        - No market price available (can't anchor without it)
    """
    # ── Premium gate ──
    cfg = _load_config()
    if cfg is None:
        logger.debug("Sports estimator not configured (free tier or disabled)")
        return None

    # ── Detect sport ──
    if sport is None:
        sport = detect_sport(ticker)
    if sport is None:
        logger.debug(f"Cannot detect sport for ticker: {ticker}")
        return None

    # ── Market price as anchor ──
    if market_price_cents is None or market_price_cents <= 0:
        logger.debug(f"No market price for {ticker} — cannot anchor prediction")
        return None

    market_prob = market_price_cents / 100.0

    # ── Parse competitors from title ──
    competitors = _parse_competitors(title, sport)
    comp_a = competitors[0] if competitors else "Unknown"
    comp_b = competitors[1] if competitors else "Unknown"

    weights = _load_weights()

    # ── Route to sport-specific estimator ──
    if sport == "hockey":
        result = _estimate_hockey(
            ticker, title, market_prob, comp_a, comp_b, weights
        )
        if result:
            return result

    if sport == "basketball":
        result = _estimate_basketball(
            ticker, title, market_prob, comp_a, comp_b, weights
        )
        if result:
            return result

    if sport == "soccer":
        result = _estimate_soccer(
            ticker, title, market_prob, comp_a, comp_b, weights
        )
        if result:
            return result

    # ── Fallback: Center-nudge (favorite-longshot bias correction) ──
    return _estimate_center_nudge(
        ticker, title, market_prob, sport, comp_a, comp_b, weights
    )


# ── Sport-Specific Estimators ────────────────────────────────────────────

def _estimate_hockey(
    ticker: str,
    title: str,
    market_prob: float,
    comp_a: str,
    comp_b: str,
    weights: dict,
) -> Optional[dict]:
    """Hockey estimation: market-anchored with team ELO.

    Strategy: nudge market price toward ELO probability.
    Formula: adjusted = market + nudge * (elo_prob - market)

    Kalshi format: "X at Y" → comp_a is AWAY, comp_b is HOME.
    """
    pipe = _get_hockey_pipeline()
    if pipe is None:
        logger.debug("Hockey pipeline not available, falling through to center-nudge")
        return None

    # is_a_home=False because Kalshi "X at Y" means X is AWAY
    est = pipe.estimate_game_probability(comp_a, comp_b, is_a_home=False)
    if est is None:
        logger.debug(f"Hockey pipeline couldn't estimate: {comp_a} vs {comp_b}")
        return None

    elo_prob = est["probability"]
    nudge = weights.get("hockey_nudge", 0.10)

    # Market-anchored blend: nudge market toward ELO
    blended = market_prob + nudge * (elo_prob - market_prob)
    blended = max(0.02, min(0.98, blended))

    confidence = min(
        weights.get("hockey_confidence", 0.40),
        weights.get("max_confidence", 0.70),
    )

    reasoning = (
        f"Hockey: {comp_a} (away) at {comp_b} (home) | "
        f"Market: {market_prob:.2f} | ELO prob: {elo_prob:.3f} | "
        f"Blended: {blended:.3f} (nudge={nudge})"
    )

    if est.get("details"):
        details = est["details"]
        reasoning += (
            f" | ELO: {details.get('elo_a', '?')}/{details.get('elo_b', '?')}"
        )

    return {
        "probability": round(blended, 4),
        "confidence": round(confidence, 4),
        "reasoning": reasoning,
        "estimator": f"sports_v{weights.get('version', '1.0.0')}",
        "sport": "hockey",
    }


def _estimate_basketball(
    ticker: str,
    title: str,
    market_prob: float,
    comp_a: str,
    comp_b: str,
    weights: dict,
) -> Optional[dict]:
    """Basketball estimation: market-anchored with team ELO.

    Strategy: nudge market price toward ELO probability.
    Formula: adjusted = market + nudge * (elo_prob - market)

    Kalshi format: "X at Y" → comp_a is AWAY, comp_b is HOME.
    """
    pipe = _get_basketball_pipeline()
    if pipe is None:
        logger.debug("Basketball pipeline not available, falling through to center-nudge")
        return None

    # is_a_home=False because Kalshi "X at Y" means X is AWAY
    est = pipe.estimate_game_probability(comp_a, comp_b, is_a_home=False)
    if est is None:
        logger.debug(f"Basketball pipeline couldn't estimate: {comp_a} vs {comp_b}")
        return None

    elo_prob = est["probability"]
    nudge = weights.get("basketball_nudge", 0.10)

    # Market-anchored blend: nudge market toward ELO
    blended = market_prob + nudge * (elo_prob - market_prob)
    blended = max(0.02, min(0.98, blended))

    confidence = min(
        weights.get("basketball_confidence", 0.42),
        weights.get("max_confidence", 0.70),
    )

    reasoning = (
        f"Basketball: {comp_a} (away) at {comp_b} (home) | "
        f"Market: {market_prob:.2f} | ELO prob: {elo_prob:.3f} | "
        f"Blended: {blended:.3f} (nudge={nudge})"
    )

    if est.get("elo_a") and est.get("elo_b"):
        reasoning += f" | ELO: {est.get('elo_a')}/{est.get('elo_b')}"

    return {
        "probability": round(blended, 4),
        "confidence": round(confidence, 4),
        "reasoning": reasoning,
        "estimator": f"sports_v{weights.get('version', '1.0.0')}",
        "sport": "basketball",
    }


def _estimate_soccer(
    ticker: str,
    title: str,
    market_prob: float,
    comp_a: str,
    comp_b: str,
    weights: dict,
) -> Optional[dict]:
    """Soccer estimation: market-anchored with team ELO.

    Strategy: nudge market price toward ELO probability.
    Formula: adjusted = market + nudge * (elo_prob - market)

    Kalshi format: "X at Y" → comp_a is AWAY, comp_b is HOME.

    NOTE: Returns probability that comp_a WINS (not draw/loss).
    Only use for "team_a wins" markets in Kalshi.
    """
    pipe = _get_soccer_pipeline()
    if pipe is None:
        logger.debug("Soccer pipeline not available, falling through to center-nudge")
        return None

    # is_a_home=False because Kalshi "X at Y" means X is AWAY
    est = pipe.estimate_game_probability(comp_a, comp_b, is_a_home=False)
    if est is None:
        logger.debug(f"Soccer pipeline couldn't estimate: {comp_a} vs {comp_b}")
        return None

    elo_prob = est["probability"]
    nudge = weights.get("soccer_nudge", 0.10)

    # Market-anchored blend: nudge market toward ELO
    blended = market_prob + nudge * (elo_prob - market_prob)
    blended = max(0.02, min(0.98, blended))

    confidence = min(
        weights.get("soccer_confidence", 0.38),
        weights.get("max_confidence", 0.70),
    )

    reasoning = (
        f"Soccer: {comp_a} (away) at {comp_b} (home) | "
        f"Market: {market_prob:.2f} | ELO prob: {elo_prob:.3f} | "
        f"Blended: {blended:.3f} (nudge={nudge})"
    )

    if est.get("elo_a") and est.get("elo_b"):
        reasoning += f" | ELO: {est.get('elo_a')}/{est.get('elo_b')}"

    return {
        "probability": round(blended, 4),
        "confidence": round(confidence, 4),
        "reasoning": reasoning,
        "estimator": f"sports_v{weights.get('version', '1.0.0')}",
        "sport": "soccer",
    }


def _estimate_center_nudge(
    ticker: str,
    title: str,
    market_prob: float,
    sport: str,
    comp_a: str,
    comp_b: str,
    weights: dict,
) -> dict:
    """Center-nudge estimation: correct favorite-longshot bias.

    Strategy: nudge market price 10% toward 0.50.
    Formula: adjusted = market + nudge * (0.50 - market)

    This exploits the well-documented favorite-longshot bias where
    prediction markets systematically overweight favorites.
    Corrected eval (March 13): Brier 0.1980 vs market ~0.198 (no demonstrated edge).
    """
    nudge = weights.get("center_nudge", 0.10)
    adjusted = market_prob + nudge * (0.50 - market_prob)
    adjusted = max(0.01, min(0.99, adjusted))

    confidence = min(
        weights.get("center_confidence", 0.30),
        weights.get("max_confidence", 0.70),
    )

    reasoning = (
        f"{sport.title()}: {comp_a} vs {comp_b} | "
        f"Market: {market_prob:.2f} | Center-nudge: {adjusted:.3f} "
        f"(nudge={nudge}, bias correction)"
    )

    return {
        "probability": round(adjusted, 4),
        "confidence": round(confidence, 4),
        "reasoning": reasoning,
        "estimator": f"sports_v{weights.get('version', '1.0.0')}",
        "sport": sport,
    }


# ── Pipeline Integration ──────────────────────────────────────────────────

def is_sports_estimator_available() -> bool:
    """Check if sports estimator is configured and available.

    Used by auto_trader to decide routing:
      if is_sports_estimator_available() and is_sports(ticker, title):
          result = estimate_sports_market(...)
      else:
          # Skip (sports blocked by filter)
    """
    cfg = _load_config()
    return cfg is not None and cfg.get("enabled", False)


# ── Market Scope Descriptor ──────────────────────────────────────────────

def get_market_scope_description(include_sports: bool = False) -> str:
    """Return human-readable description of what markets the system trades.

    Used in morning briefs, alerts, and scan summaries so users understand
    the system's focus areas.
    """
    base_scope = (
        "Policy, politics, technology, economics, and macro markets — "
        "categories where the AI estimation model focuses its analysis "
        "based on backtesting across resolved markets."
    )

    if include_sports:
        return (
            f"{base_scope}\n\n"
            "Sports markets — estimated using market-anchored predictions.\n"
            "Hockey: Team ELO (3 seasons, home advantage) — beats market baseline.\n"
            "All other sports: Center-nudge (favorite-longshot bias correction).\n"
            "(Premium feature)"
        )

    return (
        f"{base_scope}\n\n"
        "Sports & esports markets are currently excluded — our estimation model "
        "is trained on information-advantage categories (policy, tech, macro), not "
        "sports matchups. A dedicated sports model is available for premium users."
    )


MARKET_SCOPE_SHORT = (
    "📊 Scanning: policy | politics | tech | economics | macro\n"
    "🚫 Excluded: sports & esports (premium feature — dedicated model required)"
)

MARKET_SCOPE_PREMIUM_SHORT = (
    "📊 Scanning: policy | politics | tech | economics | macro | sports\n"
    "🏒 Hockey: ELO-anchored model (beats market baseline)\n"
    "🏆 Other sports: center-nudge (favorite-longshot bias correction)"
)
