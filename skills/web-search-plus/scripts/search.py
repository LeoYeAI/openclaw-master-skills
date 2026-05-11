#!/usr/bin/env python3
"""
Web Search Plus — Unified Multi-Provider Search with Intelligent Auto-Routing
Supports: Serper (Google), Tavily (Research), Exa (Neural), Perplexity (Direct Answers)

Smart Routing uses multi-signal analysis:
  - Query intent classification (shopping, research, discovery)
  - Linguistic pattern detection (how much vs how does)
  - Product/brand recognition
  - URL detection
  - Confidence scoring

Usage:
    python3 search.py --query "..."                    # Auto-route based on query
    python3 search.py --provider [serper|tavily|exa] --query "..." [options]

Examples:
    python3 search.py -q "iPhone 16 Pro price"              # → Serper (shopping intent)
    python3 search.py -q "how does quantum entanglement work"  # → Tavily (research intent)
    python3 search.py -q "startups similar to Notion"       # → Exa (discovery intent)
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse


# =============================================================================
# Result Caching
# =============================================================================

CACHE_DIR = Path(os.environ.get("WSP_CACHE_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".cache")))
PROVIDER_HEALTH_FILE = CACHE_DIR / "provider_health.json"
DEFAULT_CACHE_TTL = 3600  # 1 hour in seconds


def _build_cache_payload(query: str, provider: str, max_results: int, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Build normalized payload used for cache key hashing."""
    payload = {
        "query": query,
        "provider": provider,
        "max_results": max_results,
    }
    if params:
        payload.update(params)
    return payload


def _get_cache_key(query: str, provider: str, max_results: int, params: Optional[Dict[str, Any]] = None) -> str:
    """Generate a unique cache key from all relevant query parameters."""
    payload = _build_cache_payload(query, provider, max_results, params)
    key_string = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(key_string.encode("utf-8")).hexdigest()[:32]


def _get_cache_path(cache_key: str) -> Path:
    """Get the file path for a cache entry."""
    return CACHE_DIR / f"{cache_key}.json"


def _ensure_cache_dir() -> None:
    """Create cache directory if it doesn't exist."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def cache_get(query: str, provider: str, max_results: int, ttl: int = DEFAULT_CACHE_TTL, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    Retrieve cached search results if they exist and are not expired.
    
    Args:
        query: The search query
        provider: The search provider
        max_results: Maximum results requested
        ttl: Time-to-live in seconds (default: 1 hour)
    
    Returns:
        Cached result dict or None if not found/expired
    """
    cache_key = _get_cache_key(query, provider, max_results, params)
    cache_path = _get_cache_path(cache_key)
    
    if not cache_path.exists():
        return None
    
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            cached = json.load(f)
        
        cached_time = cached.get("_cache_timestamp", 0)
        if time.time() - cached_time > ttl:
            # Cache expired, remove it
            cache_path.unlink(missing_ok=True)
            return None
        
        return cached
    except (json.JSONDecodeError, IOError, KeyError):
        # Corrupted cache file, remove it
        cache_path.unlink(missing_ok=True)
        return None


def cache_put(query: str, provider: str, max_results: int, result: Dict[str, Any], params: Optional[Dict[str, Any]] = None) -> None:
    """
    Store search results in cache.
    
    Args:
        query: The search query
        provider: The search provider  
        max_results: Maximum results requested
        result: The search result to cache
    """
    _ensure_cache_dir()
    
    cache_key = _get_cache_key(query, provider, max_results, params)
    cache_path = _get_cache_path(cache_key)
    
    # Add cache metadata
    cached_result = result.copy()
    cached_result["_cache_timestamp"] = time.time()
    cached_result["_cache_key"] = cache_key
    cached_result["_cache_query"] = query
    cached_result["_cache_provider"] = provider
    cached_result["_cache_max_results"] = max_results
    cached_result["_cache_params"] = params or {}
    
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cached_result, f, ensure_ascii=False, indent=2)
    except IOError as e:
        # Non-fatal: log to stderr but don't fail
        print(json.dumps({"cache_write_error": str(e)}), file=sys.stderr)


def cache_clear() -> Dict[str, Any]:
    """
    Clear all cached results.
    
    Returns:
        Stats about what was cleared
    """
    if not CACHE_DIR.exists():
        return {"cleared": 0, "message": "Cache directory does not exist"}
    
    count = 0
    size_freed = 0
    
    for cache_file in CACHE_DIR.glob("*.json"):
        if cache_file.name == PROVIDER_HEALTH_FILE.name:
            continue
        try:
            size_freed += cache_file.stat().st_size
            cache_file.unlink()
            count += 1
        except IOError:
            pass
    
    return {
        "cleared": count,
        "size_freed_bytes": size_freed,
        "size_freed_kb": round(size_freed / 1024, 2),
        "message": f"Cleared {count} cached entries"
    }


def cache_stats() -> Dict[str, Any]:
    """
    Get statistics about the cache.
    
    Returns:
        Dict with cache statistics
    """
    if not CACHE_DIR.exists():
        return {
            "total_entries": 0,
            "total_size_bytes": 0,
            "total_size_kb": 0,
            "oldest": None,
            "newest": None,
            "cache_dir": str(CACHE_DIR),
            "exists": False
        }
    
    entries = [p for p in CACHE_DIR.glob("*.json") if p.name != PROVIDER_HEALTH_FILE.name]
    total_size = 0
    oldest_time = None
    newest_time = None
    oldest_query = None
    newest_query = None
    provider_counts = {}
    
    for cache_file in entries:
        try:
            stat = cache_file.stat()
            total_size += stat.st_size
            
            with open(cache_file, "r", encoding="utf-8") as f:
                cached = json.load(f)
            
            ts = cached.get("_cache_timestamp", 0)
            query = cached.get("_cache_query", "unknown")
            provider = cached.get("_cache_provider", "unknown")
            
            provider_counts[provider] = provider_counts.get(provider, 0) + 1
            
            if oldest_time is None or ts < oldest_time:
                oldest_time = ts
                oldest_query = query
            if newest_time is None or ts > newest_time:
                newest_time = ts
                newest_query = query
        except (json.JSONDecodeError, IOError):
            pass
    
    return {
        "total_entries": len(entries),
        "total_size_bytes": total_size,
        "total_size_kb": round(total_size / 1024, 2),
        "providers": provider_counts,
        "oldest": {
            "timestamp": oldest_time,
            "age_seconds": int(time.time() - oldest_time) if oldest_time else None,
            "query": oldest_query
        } if oldest_time else None,
        "newest": {
            "timestamp": newest_time,
            "age_seconds": int(time.time() - newest_time) if newest_time else None,
            "query": newest_query
        } if newest_time else None,
        "cache_dir": str(CACHE_DIR),
        "exists": True
    }


# =============================================================================
# Auto-load .env from skill directory (if exists)
# =============================================================================
def _load_env_file():
    """Load .env file from skill root directory if it exists."""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    # Handle export VAR=value or VAR=value
                    if line.startswith("export "):
                        line = line[7:]
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and key not in os.environ:
                        os.environ[key] = value

_load_env_file()


# =============================================================================
# Configuration
# =============================================================================

DEFAULT_CONFIG = {
    "defaults": {
        "provider": "serper",
        "max_results": 5
    },
    "auto_routing": {
        "enabled": True,
        "fallback_provider": "serper",
        "provider_priority": ["tavily", "exa", "perplexity", "serper", "you", "searxng"],
        "disabled_providers": [],
        "confidence_threshold": 0.3,  # Below this, note low confidence
    },
    "serper": {
        "country": "us",
        "language": "en",
        "type": "search"
    },
    "tavily": {
        "depth": "basic",
        "topic": "general"
    },
    "exa": {
        "type": "neural"
    },
    "perplexity": {
        "api_url": "https://api.kilo.ai/api/gateway/chat/completions",
        "model": "perplexity/sonar-pro"
    },
    "you": {
        "country": "us",
        "safesearch": "moderate"
    },
    "searxng": {
        "instance_url": None,  # Required - user must set their own instance
        "safesearch": 0,  # 0=off, 1=moderate, 2=strict
        "engines": None,  # Optional list of engines to use
        "language": "en"
    }
}


def load_config() -> Dict[str, Any]:
    """Load configuration from config.json if it exists, with defaults."""
    config = DEFAULT_CONFIG.copy()
    config_path = Path(__file__).parent.parent / "config.json"
    
    if config_path.exists():
        try:
            with open(config_path) as f:
                user_config = json.load(f)
                for key, value in user_config.items():
                    if isinstance(value, dict) and key in config:
                        config[key] = {**config.get(key, {}), **value}
                    else:
                        config[key] = value
        except (json.JSONDecodeError, IOError) as e:
            print(json.dumps({
                "warning": f"Could not load config.json: {e}",
                "using": "default configuration"
            }), file=sys.stderr)
    
    return config


def get_api_key(provider: str, config: Dict[str, Any] = None) -> Optional[str]:
    """Get API key for provider from config.json or environment.
    
    Priority: config.json > .env > environment variable
    
    Note: SearXNG doesn't require an API key, but returns instance_url if configured.
    """
    # Special case: SearXNG uses instance_url instead of API key
    if provider == "searxng":
        return get_searxng_instance_url(config)
    
    # Check config.json first
    if config:
        provider_config = config.get(provider, {})
        if isinstance(provider_config, dict):
            key = provider_config.get("api_key") or provider_config.get("apiKey")
            if key:
                return key
    
    # Then check environment
    key_map = {
        "serper": "SERPER_API_KEY",
        "tavily": "TAVILY_API_KEY",
        "exa": "EXA_API_KEY",
        "you": "YOU_API_KEY",
        "perplexity": "KILOCODE_API_KEY",
    }
    return os.environ.get(key_map.get(provider, ""))


def _validate_searxng_url(url: str) -> str:
    """Validate and sanitize SearXNG instance URL to prevent SSRF.
    
    Enforces http/https scheme and blocks requests to private/internal networks
    including cloud metadata endpoints, loopback, link-local, and RFC1918 ranges.
    """
    import ipaddress
    import socket
    from urllib.parse import urlparse

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"SearXNG URL must use http or https scheme, got: {parsed.scheme}")
    if not parsed.hostname:
        raise ValueError("SearXNG URL must include a hostname")

    hostname = parsed.hostname

    # Block cloud metadata endpoints by hostname
    BLOCKED_HOSTS = {
        "169.254.169.254",        # AWS/GCP/Azure metadata
        "metadata.google.internal",
        "metadata.internal",
    }
    if hostname in BLOCKED_HOSTS:
        raise ValueError(f"SearXNG URL blocked: {hostname} is a cloud metadata endpoint")

    # Resolve hostname and check for private/internal IPs
    # Operators who intentionally self-host on private networks can opt out
    allow_private = os.environ.get("SEARXNG_ALLOW_PRIVATE", "").strip() == "1"
    if not allow_private:
        try:
            resolved_ips = socket.getaddrinfo(hostname, parsed.port or 80, proto=socket.IPPROTO_TCP)
            for family, _type, _proto, _canonname, sockaddr in resolved_ips:
                ip = ipaddress.ip_address(sockaddr[0])
                if ip.is_loopback or ip.is_private or ip.is_link_local or ip.is_reserved:
                    raise ValueError(
                        f"SearXNG URL blocked: {hostname} resolves to private/internal IP {ip}. "
                        f"If this is intentional, set SEARXNG_ALLOW_PRIVATE=1 in your environment."
                    )
        except socket.gaierror:
            raise ValueError(f"SearXNG URL blocked: cannot resolve hostname {hostname}")

    return url


def get_searxng_instance_url(config: Dict[str, Any] = None) -> Optional[str]:
    """Get SearXNG instance URL from config or environment.
    
    SearXNG is self-hosted, so no API key needed - just the instance URL.
    Priority: config.json > SEARXNG_INSTANCE_URL environment variable
    
    Security: URL is validated to prevent SSRF via scheme enforcement.
    Both config sources (config.json, env var) are operator-controlled,
    not agent-controlled, so private IPs like localhost are permitted.
    """
    # Check config.json first
    if config:
        searxng_config = config.get("searxng", {})
        if isinstance(searxng_config, dict):
            url = searxng_config.get("instance_url")
            if url:
                return _validate_searxng_url(url)
    
    # Then check environment
    env_url = os.environ.get("SEARXNG_INSTANCE_URL")
    if env_url:
        return _validate_searxng_url(env_url)
    return None


# Backward compatibility alias
def get_env_key(provider: str) -> Optional[str]:
    """Get API key for provider from environment (legacy function)."""
    return get_api_key(provider)


def validate_api_key(provider: str, config: Dict[str, Any] = None) -> str:
    """Validate and return API key (or instance URL for SearXNG), with helpful error messages."""
    key = get_api_key(provider, config)
    
    # Special handling for SearXNG - it needs instance URL, not API key
    if provider == "searxng":
        if not key:
            error_msg = {
                "error": "Missing SearXNG instance URL",
                "env_var": "SEARXNG_INSTANCE_URL",
                "how_to_fix": [
                    "1. Set up your own SearXNG instance: https://docs.searxng.org/admin/installation.html",
                    "2. Add to config.json: \"searxng\": {\"instance_url\": \"https://your-instance.example.com\"}",
                    "3. Or set environment variable: export SEARXNG_INSTANCE_URL=\"https://your-instance.example.com\"",
                    "Note: SearXNG requires a self-hosted instance with JSON format enabled.",
                ],
                "provider": provider
            }
            print(json.dumps(error_msg, indent=2), file=sys.stderr)
            sys.exit(1)
        
        # Validate URL format
        if not key.startswith(("http://", "https://")):
            print(json.dumps({
                "error": "SearXNG instance URL must start with http:// or https://",
                "provided": key,
                "provider": provider
            }, indent=2), file=sys.stderr)
            sys.exit(1)
        
        return key
    
    if not key:
        env_var = {
            "serper": "SERPER_API_KEY",
            "tavily": "TAVILY_API_KEY", 
            "exa": "EXA_API_KEY",
            "you": "YOU_API_KEY",
            "perplexity": "KILOCODE_API_KEY"
        }[provider]
        
        urls = {
            "serper": "https://serper.dev",
            "tavily": "https://tavily.com",
            "exa": "https://exa.ai",
            "you": "https://api.you.com",
            "perplexity": "https://api.kilo.ai"
        }
        
        error_msg = {
            "error": f"Missing API key for {provider}",
            "env_var": env_var,
            "how_to_fix": [
                f"1. Get your API key from {urls[provider]}",
                f"2. Add to config.json: \"{provider}\": {{\"api_key\": \"your-key\"}}",
                f"3. Or set environment variable: export {env_var}=\"your-key\"",
            ],
            "provider": provider
        }
        print(json.dumps(error_msg, indent=2), file=sys.stderr)
        sys.exit(1)
    
    if len(key) < 10:
        print(json.dumps({
            "error": f"API key for {provider} appears invalid (too short)",
            "provider": provider
        }, indent=2), file=sys.stderr)
        sys.exit(1)
    
    return key


# =============================================================================
# Intelligent Auto-Routing Engine
# =============================================================================

class QueryAnalyzer:
    """
    Intelligent query analysis for smart provider routing.
    
    Uses multi-signal analysis:
    - Intent classification (shopping, research, discovery, local, news)
    - Linguistic patterns (question structure, phrase patterns)
    - Entity detection (products, brands, URLs, dates)
    - Complexity assessment
    """
    
    # Intent signal patterns with weights
    # Higher weight = stronger signal for that provider
    
    SHOPPING_SIGNALS = {
        # Price patterns (very strong)
        r'\bhow much\b': 4.0,
        r'\bprice of\b': 4.0,
        r'\bcost of\b': 4.0,
        r'\bprices?\b': 3.0,
        r'\$\d+|\d+\s*dollars?': 3.0,
        r'€\d+|\d+\s*euros?': 3.0,
        r'£\d+|\d+\s*pounds?': 3.0,
        
        # German price patterns (sehr stark)
        r'\bpreis(e)?\b': 3.5,
        r'\bkosten\b': 3.0,
        r'\bwieviel\b': 3.5,
        r'\bwie viel\b': 3.5,
        r'\bwas kostet\b': 4.0,
        
        # Purchase intent (strong)
        r'\bbuy\b': 3.5,
        r'\bpurchase\b': 3.5,
        r'\border\b(?!\s+by)': 3.0,  # "order" but not "order by"
        r'\bshopping\b': 3.5,
        r'\bshop for\b': 3.5,
        r'\bwhere to (buy|get|purchase)\b': 4.0,
        
        # German purchase intent (stark)
        r'\bkaufen\b': 3.5,
        r'\bbestellen\b': 3.5,
        r'\bwo kaufen\b': 4.0,
        r'\bhändler\b': 3.0,
        r'\bshop\b': 2.5,
        
        # Deal/discount signals
        r'\bdeal(s)?\b': 3.0,
        r'\bdiscount(s)?\b': 3.0,
        r'\bsale\b': 2.5,
        r'\bcheap(er|est)?\b': 3.0,
        r'\baffordable\b': 2.5,
        r'\bbudget\b': 2.5,
        r'\bbest price\b': 3.5,
        r'\bcompare prices\b': 3.5,
        r'\bcoupon\b': 3.0,
        
        # German deal/discount signals
        r'\bgünstig(er|ste)?\b': 3.0,
        r'\bbillig(er|ste)?\b': 3.0,
        r'\bangebot(e)?\b': 3.0,
        r'\brabatt\b': 3.0,
        r'\baktion\b': 2.5,
        r'\bschnäppchen\b': 3.0,
        
        # Product comparison
        r'\bvs\.?\b': 2.0,
        r'\bversus\b': 2.0,
        r'\bor\b.*\bwhich\b': 2.0,
        r'\bspecs?\b': 2.5,
        r'\bspecifications?\b': 2.5,
        r'\breview(s)?\b': 2.0,
        r'\brating(s)?\b': 2.0,
        r'\bunboxing\b': 2.5,
        
        # German product comparison
        r'\btest\b': 2.5,
        r'\bbewertung(en)?\b': 2.5,
        r'\btechnische daten\b': 3.0,
        r'\bspezifikationen\b': 2.5,
    }
    
    RESEARCH_SIGNALS = {
        # Explanation patterns (very strong)
        r'\bhow does\b': 4.0,
        r'\bhow do\b': 3.5,
        r'\bwhy does\b': 4.0,
        r'\bwhy do\b': 3.5,
        r'\bwhy is\b': 3.5,
        r'\bexplain\b': 4.0,
        r'\bexplanation\b': 4.0,
        r'\bwhat is\b': 3.0,
        r'\bwhat are\b': 3.0,
        r'\bdefine\b': 3.5,
        r'\bdefinition of\b': 3.5,
        r'\bmeaning of\b': 3.0,
        
        # Analysis patterns (strong)
        r'\banalyze\b': 3.5,
        r'\banalysis\b': 3.5,
        r'\bcompare\b(?!\s*prices?)': 3.0,  # compare but not "compare prices"
        r'\bcomparison\b': 3.0,
        r'\bstatus of\b': 3.5,
        r'\bstatus\b': 2.5,
        r'\bwhat happened with\b': 4.0,
        r'\bpros and cons\b': 4.0,
        r'\badvantages?\b': 3.0,
        r'\bdisadvantages?\b': 3.0,
        r'\bbenefits?\b': 2.5,
        r'\bdrawbacks?\b': 3.0,
        r'\bdifference between\b': 3.5,
        
        # Learning patterns
        r'\bunderstand\b': 3.0,
        r'\blearn(ing)?\b': 2.5,
        r'\btutorial\b': 3.0,
        r'\bguide\b': 2.5,
        r'\bhow to\b': 2.0,  # Lower weight - could be shopping too
        r'\bstep by step\b': 3.0,
        
        # Depth signals
        r'\bin[- ]depth\b': 3.0,
        r'\bdetailed\b': 2.5,
        r'\bcomprehensive\b': 3.0,
        r'\bthorough\b': 2.5,
        r'\bdeep dive\b': 3.5,
        r'\boverall\b': 2.0,
        r'\bsummary\b': 2.0,
        
        # Academic patterns
        r'\bstudy\b': 2.5,
        r'\bresearch shows\b': 3.5,
        r'\baccording to\b': 2.5,
        r'\bevidence\b': 3.0,
        r'\bscientific\b': 3.0,
        r'\bhistory of\b': 3.0,
        r'\bbackground\b': 2.5,
        r'\bcontext\b': 2.5,
        r'\bimplications?\b': 3.0,
        
        # German explanation patterns (sehr stark)
        r'\bwie funktioniert\b': 4.0,
        r'\bwarum\b': 3.5,
        r'\berklär(en|ung)?\b': 4.0,
        r'\bwas ist\b': 3.0,
        r'\bwas sind\b': 3.0,
        r'\bbedeutung\b': 3.0,
        
        # German analysis patterns
        r'\banalyse\b': 3.5,
        r'\bvergleich(en)?\b': 3.0,
        r'\bvor- und nachteile\b': 4.0,
        r'\bvorteile\b': 3.0,
        r'\bnachteile\b': 3.0,
        r'\bunterschied(e)?\b': 3.5,
        
        # German learning patterns
        r'\bverstehen\b': 3.0,
        r'\blernen\b': 2.5,
        r'\banleitung\b': 3.0,
        r'\bübersicht\b': 2.5,
        r'\bhintergrund\b': 2.5,
        r'\bzusammenfassung\b': 2.5,
    }
    
    DISCOVERY_SIGNALS = {
        # Similarity patterns (very strong)
        r'\bsimilar to\b': 5.0,
        r'\blike\s+\w+\.com': 4.5,  # "like notion.com"
        r'\balternatives? to\b': 5.0,
        r'\bcompetitors? (of|to)\b': 4.5,
        r'\bcompeting with\b': 4.0,
        r'\brivals? (of|to)\b': 4.0,
        r'\binstead of\b': 3.0,
        r'\breplacement for\b': 3.5,
        
        # Company/startup patterns (strong)
        r'\bcompanies (like|that|doing|building)\b': 4.5,
        r'\bstartups? (like|that|doing|building)\b': 4.5,
        r'\bwho else\b': 4.0,
        r'\bother (companies|startups|tools|apps)\b': 3.5,
        r'\bfind (companies|startups|tools|examples?)\b': 4.5,
        r'\bevents? in\b': 4.0,
        r'\bthings to do in\b': 4.5,
        
        # Funding/business patterns
        r'\bseries [a-d]\b': 4.0,
        r'\byc\b|y combinator': 4.0,
        r'\bfund(ed|ing|raise)\b': 3.5,
        r'\bventure\b': 3.0,
        r'\bvaluation\b': 3.0,
        
        # Category patterns
        r'\bresearch papers? (on|about)\b': 4.0,
        r'\barxiv\b': 4.5,
        r'\bgithub (projects?|repos?)\b': 4.5,
        r'\bopen source\b.*\bprojects?\b': 4.0,
        r'\btweets? (about|on)\b': 3.5,
        r'\bblogs? (about|on|like)\b': 3.0,
        
        # URL detection (very strong signal for Exa similar)
        r'https?://[^\s]+': 5.0,
        r'\b\w+\.(com|org|io|ai|co|dev)\b': 3.5,
    }
    
    LOCAL_NEWS_SIGNALS = {
        # Local patterns → Serper
        r'\bnear me\b': 4.0,
        r'\bnearby\b': 3.5,
        r'\blocal\b': 3.0,
        r'\bin (my )?(city|area|town|neighborhood)\b': 3.5,
        r'\brestaurants?\b': 2.5,
        r'\bhotels?\b': 2.5,
        r'\bcafes?\b': 2.5,
        r'\bstores?\b': 2.0,
        r'\bdirections? to\b': 3.5,
        r'\bmap of\b': 3.0,
        r'\bphone number\b': 3.0,
        r'\baddress of\b': 3.0,
        r'\bopen(ing)? hours\b': 3.0,
        
        # Weather/time
        r'\bweather\b': 4.0,
        r'\bforecast\b': 3.5,
        r'\btemperature\b': 3.0,
        r'\btime in\b': 3.0,
        
        # News/recency patterns → Serper (or Tavily for news depth)
        r'\blatest\b': 2.5,
        r'\brecent\b': 2.5,
        r'\btoday\b': 2.5,
        r'\bbreaking\b': 3.5,
        r'\bnews\b': 2.5,
        r'\bheadlines?\b': 3.0,
        r'\b202[4-9]\b': 2.0,  # Current year mentions
        r'\blast (week|month|year)\b': 2.0,
    }
    
    # RAG/AI signals → You.com
    # You.com excels at providing LLM-ready snippets and combined web+news
    RAG_SIGNALS = {
        # RAG/context patterns (strong signal for You.com)
        r'\brag\b': 4.5,
        r'\bcontext for\b': 4.0,
        r'\bsummarize\b': 3.5,
        r'\bbrief(ly)?\b': 3.0,
        r'\bquick overview\b': 3.5,
        r'\btl;?dr\b': 4.0,
        r'\bkey (points|facts|info)\b': 3.5,
        r'\bmain (points|takeaways)\b': 3.5,
        
        # Combined web + news queries
        r'\b(web|online)\s+and\s+news\b': 4.0,
        r'\ball sources\b': 3.5,
        r'\bcomprehensive (search|overview)\b': 3.5,
        r'\blatest\s+(news|updates)\b': 3.0,
        r'\bcurrent (events|situation|status)\b': 3.5,
        
        # Real-time information needs
        r'\bright now\b': 3.0,
        r'\bas of today\b': 3.5,
        r'\bup.to.date\b': 3.5,
        r'\breal.time\b': 4.0,
        r'\blive\b': 2.5,
        
        # Information synthesis
        r'\bwhat\'?s happening with\b': 3.5,
        r'\bwhat\'?s the latest\b': 4.0,
        r'\bupdates?\s+on\b': 3.5,
        r'\bstatus of\b': 3.0,
        r'\bsituation (in|with|around)\b': 3.5,
    }
    
    # Direct answer / synthesis signals → Perplexity via Kilo Gateway
    DIRECT_ANSWER_SIGNALS = {
        r'\bwhat is\b': 3.0,
        r'\bwhat are\b': 2.5,
        r'\bcurrent status\b': 4.0,
        r'\bstatus of\b': 3.5,
        r'\bstatus\b': 2.5,
        r'\bwhat happened with\b': 4.0,
        r"\bwhat'?s happening with\b": 4.0,
        r'\bas of (today|now)\b': 4.0,
        r'\bthis weekend\b': 3.5,
        r'\bevents? in\b': 3.5,
        r'\bthings to do in\b': 4.0,
        r'\bnear me\b': 3.0,
        r'\bcan you (tell me|summarize|explain)\b': 3.5,
    }

    # Privacy/Multi-source signals → SearXNG (self-hosted meta-search)
    # SearXNG is ideal for privacy-focused queries and aggregating multiple sources
    PRIVACY_SIGNALS = {
        # Privacy signals (very strong)
        r'\bprivate(ly)?\b': 4.0,
        r'\banonymous(ly)?\b': 4.0,
        r'\bwithout tracking\b': 4.5,
        r'\bno track(ing)?\b': 4.5,
        r'\bprivacy\b': 3.5,
        r'\bprivacy.?focused\b': 4.5,
        r'\bprivacy.?first\b': 4.5,
        r'\bduckduckgo alternative\b': 4.5,
        r'\bprivate search\b': 5.0,
        
        # German privacy signals
        r'\bprivat\b': 4.0,
        r'\banonym\b': 4.0,
        r'\bohne tracking\b': 4.5,
        r'\bdatenschutz\b': 4.0,
        
        # Multi-source aggregation signals
        r'\baggregate results?\b': 4.0,
        r'\bmultiple sources?\b': 4.0,
        r'\bdiverse (results|perspectives|sources)\b': 4.0,
        r'\bfrom (all|multiple|different) (engines?|sources?)\b': 4.5,
        r'\bmeta.?search\b': 5.0,
        r'\ball engines?\b': 4.0,
        
        # German multi-source signals
        r'\bverschiedene quellen\b': 4.0,
        r'\baus mehreren quellen\b': 4.0,
        r'\balle suchmaschinen\b': 4.5,
        
        # Budget/free signals (SearXNG is self-hosted = $0 API cost)
        r'\bfree search\b': 3.5,
        r'\bno api cost\b': 4.0,
        r'\bself.?hosted search\b': 5.0,
        r'\bzero cost\b': 3.5,
        r'\bbudget\b(?!\s*(laptop|phone|option))\b': 2.5,  # "budget" alone, not "budget laptop"
        
        # German budget signals
        r'\bkostenlos(e)?\s+suche\b': 3.5,
        r'\bkeine api.?kosten\b': 4.0,
    }
    
    # Brand/product patterns for shopping detection
    BRAND_PATTERNS = [
        # Tech brands
        r'\b(apple|iphone|ipad|macbook|airpods?)\b',
        r'\b(samsung|galaxy)\b',
        r'\b(google|pixel)\b',
        r'\b(microsoft|surface|xbox)\b',
        r'\b(sony|playstation)\b',
        r'\b(nvidia|geforce|rtx)\b',
        r'\b(amd|ryzen|radeon)\b',
        r'\b(intel|core i[3579])\b',
        r'\b(dell|hp|lenovo|asus|acer)\b',
        r'\b(lg|tcl|hisense)\b',
        
        # Product categories
        r'\b(laptop|phone|tablet|tv|monitor|headphones?|earbuds?)\b',
        r'\b(camera|lens|drone)\b',
        r'\b(watch|smartwatch|fitbit|garmin)\b',
        r'\b(router|modem|wifi)\b',
        r'\b(keyboard|mouse|gaming)\b',
    ]
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.auto_config = config.get("auto_routing", DEFAULT_CONFIG["auto_routing"])
    
    def _calculate_signal_score(
        self, 
        query: str, 
        signals: Dict[str, float]
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Calculate score for a signal category.
        Returns (total_score, list of matched signals with details).
        """
        query_lower = query.lower()
        matches = []
        total_score = 0.0
        
        for pattern, weight in signals.items():
            regex = re.compile(pattern, re.IGNORECASE)
            found = regex.findall(query_lower)
            if found:
                # Normalize found matches
                match_text = found[0] if isinstance(found[0], str) else found[0][0] if found[0] else pattern
                matches.append({
                    "pattern": pattern,
                    "matched": match_text,
                    "weight": weight
                })
                total_score += weight
        
        return total_score, matches
    
    def _detect_product_brand_combo(self, query: str) -> float:
        """
        Detect product + brand combinations which strongly indicate shopping intent.
        Returns a bonus score.
        """
        query_lower = query.lower()
        brand_found = False
        product_found = False
        
        for pattern in self.BRAND_PATTERNS:
            if re.search(pattern, query_lower, re.IGNORECASE):
                brand_found = True
                break
        
        # Check for product indicators
        product_indicators = [
            r'\b(buy|price|specs?|review|vs|compare)\b',
            r'\b(pro|max|plus|mini|ultra|lite)\b',  # Product tier names
            r'\b\d+\s*(gb|tb|inch|mm|hz)\b',  # Specifications
        ]
        for pattern in product_indicators:
            if re.search(pattern, query_lower, re.IGNORECASE):
                product_found = True
                break
        
        if brand_found and product_found:
            return 3.0  # Strong shopping signal
        elif brand_found:
            return 1.5  # Moderate shopping signal
        return 0.0
    
    def _detect_url(self, query: str) -> Optional[str]:
        """Detect URLs in query - strong signal for Exa similar search."""
        url_pattern = r'https?://[^\s]+'
        match = re.search(url_pattern, query)
        if match:
            return match.group()
        
        # Also check for domain-like patterns
        domain_pattern = r'\b(\w+\.(com|org|io|ai|co|dev|net|app))\b'
        match = re.search(domain_pattern, query, re.IGNORECASE)
        if match:
            return match.group()
        
        return None
    
    def _assess_query_complexity(self, query: str) -> Dict[str, Any]:
        """
        Assess query complexity - complex queries favor Tavily.
        """
        words = query.split()
        word_count = len(words)
        
        # Count question words
        question_words = len(re.findall(
            r'\b(what|why|how|when|where|which|who|whose|whom)\b', 
            query, re.IGNORECASE
        ))
        
        # Check for multiple clauses
        clause_markers = len(re.findall(
            r'\b(and|but|or|because|since|while|although|if|when)\b',
            query, re.IGNORECASE
        ))
        
        complexity_score = 0.0
        if word_count > 10:
            complexity_score += 1.5
        if word_count > 20:
            complexity_score += 1.0
        if question_words > 1:
            complexity_score += 1.0
        if clause_markers > 0:
            complexity_score += 0.5 * clause_markers
        
        return {
            "word_count": word_count,
            "question_words": question_words,
            "clause_markers": clause_markers,
            "complexity_score": complexity_score,
            "is_complex": complexity_score > 2.0
        }
    
    def _detect_recency_intent(self, query: str) -> Tuple[bool, float]:
        """
        Detect if query wants recent/timely information.
        Returns (is_recency_focused, score).
        """
        recency_patterns = [
            (r'\b(latest|newest|recent|current)\b', 2.5),
            (r'\b(today|yesterday|this week|this month)\b', 3.0),
            (r'\b(202[4-9]|2030)\b', 2.0),
            (r'\b(breaking|live|just|now)\b', 3.0),
            (r'\blast (hour|day|week|month)\b', 2.5),
        ]
        
        total = 0.0
        for pattern, weight in recency_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                total += weight
        
        return total > 2.0, total
    
    def analyze(self, query: str) -> Dict[str, Any]:
        """
        Perform comprehensive query analysis.
        Returns detailed analysis with scores for each provider.
        """
        # Calculate scores for each intent category
        shopping_score, shopping_matches = self._calculate_signal_score(
            query, self.SHOPPING_SIGNALS
        )
        research_score, research_matches = self._calculate_signal_score(
            query, self.RESEARCH_SIGNALS
        )
        discovery_score, discovery_matches = self._calculate_signal_score(
            query, self.DISCOVERY_SIGNALS
        )
        local_news_score, local_news_matches = self._calculate_signal_score(
            query, self.LOCAL_NEWS_SIGNALS
        )
        rag_score, rag_matches = self._calculate_signal_score(
            query, self.RAG_SIGNALS
        )
        privacy_score, privacy_matches = self._calculate_signal_score(
            query, self.PRIVACY_SIGNALS
        )
        direct_answer_score, direct_answer_matches = self._calculate_signal_score(
            query, self.DIRECT_ANSWER_SIGNALS
        )
        
        # Apply product/brand bonus to shopping
        brand_bonus = self._detect_product_brand_combo(query)
        if brand_bonus > 0:
            shopping_score += brand_bonus
            shopping_matches.append({
                "pattern": "product_brand_combo",
                "matched": "brand + product detected",
                "weight": brand_bonus
            })
        
        # Detect URL → strong Exa signal
        detected_url = self._detect_url(query)
        if detected_url:
            discovery_score += 5.0
            discovery_matches.append({
                "pattern": "url_detected",
                "matched": detected_url,
                "weight": 5.0
            })
        
        # Assess complexity → favors Tavily
        complexity = self._assess_query_complexity(query)
        if complexity["is_complex"]:
            research_score += complexity["complexity_score"]
            research_matches.append({
                "pattern": "query_complexity",
                "matched": f"complex query ({complexity['word_count']} words)",
                "weight": complexity["complexity_score"]
            })
        
        # Check recency intent
        is_recency, recency_score = self._detect_recency_intent(query)
        
        # Map intents to providers with final scores
        provider_scores = {
            "serper": shopping_score + local_news_score + (recency_score * 0.35),
            "tavily": research_score + (complexity["complexity_score"] if not complexity["is_complex"] else 0) + (0.2 * recency_score),
            "exa": discovery_score + (1.0 if re.search(r"\b(similar|alternatives?|examples?)\b", query, re.IGNORECASE) else 0.0),
            "perplexity": direct_answer_score + (local_news_score * 0.4) + (recency_score * 0.55),
            "you": rag_score + (recency_score * 0.25),  # You.com good for real-time + RAG
            "searxng": privacy_score,  # SearXNG for privacy/multi-source queries
        }
        
        # Build match details per provider
        provider_matches = {
            "serper": shopping_matches + local_news_matches,
            "tavily": research_matches,
            "exa": discovery_matches,
            "perplexity": direct_answer_matches,
            "you": rag_matches,
            "searxng": privacy_matches,
        }
        
        return {
            "query": query,
            "provider_scores": provider_scores,
            "provider_matches": provider_matches,
            "detected_url": detected_url,
            "complexity": complexity,
            "recency_focused": is_recency,
            "recency_score": recency_score,
        }
    
    def route(self, query: str) -> Dict[str, Any]:
        """
        Route query to optimal provider with confidence scoring.
        """
        analysis = self.analyze(query)
        scores = analysis["provider_scores"]
        
        # Filter to available providers
        disabled = set(self.auto_config.get("disabled_providers", []))
        available = {
            p: s for p, s in scores.items() 
            if p not in disabled and get_env_key(p)
        }
        
        if not available:
            # No providers available, use fallback
            fallback = self.auto_config.get("fallback_provider", "serper")
            return {
                "provider": fallback,
                "confidence": 0.0,
                "confidence_level": "low",
                "reason": "no_available_providers",
                "scores": scores,
                "top_signals": [],
                "analysis": analysis,
            }
        
        # Find the winner
        max_score = max(available.values())
        total_score = sum(available.values()) or 1.0
        
        # Handle ties using priority
        priority = self.auto_config.get("provider_priority", ["tavily", "exa", "perplexity", "serper", "you", "searxng"])
        winners = [p for p, s in available.items() if s == max_score]
        
        if len(winners) > 1:
            # Use priority to break tie
            for p in priority:
                if p in winners:
                    winner = p
                    break
            else:
                winner = winners[0]
        else:
            winner = winners[0]
        
        # Calculate confidence
        # High confidence = clear winner with good margin
        if max_score == 0:
            confidence = 0.0
            reason = "no_signals_matched"
        else:
            # Confidence based on:
            # 1. Absolute score (is it strong enough?)
            # 2. Relative margin (is there a clear winner?)
            second_best = sorted(available.values(), reverse=True)[1] if len(available) > 1 else 0
            margin = (max_score - second_best) / max_score if max_score > 0 else 0
            
            # Normalize score to 0-1 range (assuming max reasonable score ~15)
            normalized_score = min(max_score / 15.0, 1.0)
            
            # Confidence is combination of absolute strength and relative margin
            confidence = round((normalized_score * 0.6 + margin * 0.4), 3)
            
            if confidence >= 0.7:
                reason = "high_confidence_match"
            elif confidence >= 0.4:
                reason = "moderate_confidence_match"
            else:
                reason = "low_confidence_match"
        
        # Get top signals for the winning provider
        matches = analysis["provider_matches"].get(winner, [])
        top_signals = sorted(matches, key=lambda x: x["weight"], reverse=True)[:5]
        
        # Special case: URL detected and Exa available → strong recommendation
        if analysis["detected_url"] and "exa" in available:
            if winner != "exa":
                # Override if URL is present but didn't win
                # (user might want similar search)
                pass  # Keep current winner but note it
        
        # Build detailed routing result
        threshold = self.auto_config.get("confidence_threshold", 0.3)
        
        return {
            "provider": winner,
            "confidence": confidence,
            "confidence_level": "high" if confidence >= 0.7 else "medium" if confidence >= 0.4 else "low",
            "reason": reason,
            "scores": {p: round(s, 2) for p, s in available.items()},
            "winning_score": round(max_score, 2),
            "top_signals": [
                {"matched": s["matched"], "weight": s["weight"]} 
                for s in top_signals
            ],
            "below_threshold": confidence < threshold,
            "analysis_summary": {
                "query_length": len(query.split()),
                "is_complex": analysis["complexity"]["is_complex"],
                "has_url": analysis["detected_url"] is not None,
                "recency_focused": analysis["recency_focused"],
            }
        }


def auto_route_provider(query: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Intelligently route query to the best provider.
    Returns detailed routing decision with confidence.
    """
    analyzer = QueryAnalyzer(config)
    return analyzer.route(query)


def explain_routing(query: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Provide detailed explanation of routing decision for debugging.
    """
    analyzer = QueryAnalyzer(config)
    analysis = analyzer.analyze(query)
    routing = analyzer.route(query)
    
    return {
        "query": query,
        "routing_decision": {
            "provider": routing["provider"],
            "confidence": routing["confidence"],
            "confidence_level": routing["confidence_level"],
            "reason": routing["reason"],
        },
        "scores": routing["scores"],
        "top_signals": routing["top_signals"],
        "intent_breakdown": {
            "shopping_signals": len(analysis["provider_matches"]["serper"]),
            "research_signals": len(analysis["provider_matches"]["tavily"]),
            "discovery_signals": len(analysis["provider_matches"]["exa"]),
            "rag_signals": len(analysis["provider_matches"]["you"]),
        },
        "query_analysis": {
            "word_count": analysis["complexity"]["word_count"],
            "is_complex": analysis["complexity"]["is_complex"],
            "complexity_score": round(analysis["complexity"]["complexity_score"], 2),
            "has_url": analysis["detected_url"],
            "recency_focused": analysis["recency_focused"],
        },
        "all_matches": {
            provider: [
                {"matched": m["matched"], "weight": m["weight"]}
                for m in matches
            ]
            for provider, matches in analysis["provider_matches"].items()
            if matches
        },
        "available_providers": [
            p for p in ["serper", "tavily", "exa", "perplexity", "you", "searxng"] 
            if get_env_key(p) and p not in config.get("auto_routing", {}).get("disabled_providers", [])
        ]
    }




class ProviderRequestError(Exception):
    """Structured provider error with retry/cooldown metadata."""

    def __init__(self, message: str, status_code: Optional[int] = None, transient: bool = False):
        super().__init__(message)
        self.status_code = status_code
        self.transient = transient


TRANSIENT_HTTP_CODES = {429, 503}
COOLDOWN_STEPS_SECONDS = [60, 300, 1500, 3600]  # 1m -> 5m -> 25m -> 1h cap
RETRY_BACKOFF_SECONDS = [1, 3, 9]


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _load_provider_health() -> Dict[str, Any]:
    if not PROVIDER_HEALTH_FILE.exists():
        return {}
    try:
        with open(PROVIDER_HEALTH_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, IOError):
        return {}


def _save_provider_health(state: Dict[str, Any]) -> None:
    _ensure_parent(PROVIDER_HEALTH_FILE)
    with open(PROVIDER_HEALTH_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def provider_in_cooldown(provider: str) -> Tuple[bool, int]:
    state = _load_provider_health()
    pstate = state.get(provider, {})
    cooldown_until = int(pstate.get("cooldown_until", 0) or 0)
    remaining = cooldown_until - int(time.time())
    return (remaining > 0, max(0, remaining))


def mark_provider_failure(provider: str, error_message: str) -> Dict[str, Any]:
    state = _load_provider_health()
    now = int(time.time())
    pstate = state.get(provider, {})
    fail_count = int(pstate.get("failure_count", 0)) + 1
    cooldown_seconds = COOLDOWN_STEPS_SECONDS[min(fail_count - 1, len(COOLDOWN_STEPS_SECONDS) - 1)]
    state[provider] = {
        "failure_count": fail_count,
        "cooldown_until": now + cooldown_seconds,
        "cooldown_seconds": cooldown_seconds,
        "last_error": error_message,
        "last_failure_at": now,
    }
    _save_provider_health(state)
    return state[provider]


def reset_provider_health(provider: str) -> None:
    state = _load_provider_health()
    if provider in state:
        state.pop(provider, None)
        _save_provider_health(state)


def normalize_result_url(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url.strip())
    netloc = (parsed.netloc or "").lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    path = parsed.path.rstrip("/")
    return f"{netloc}{path}"


def deduplicate_results_across_providers(results_by_provider: List[Tuple[str, Dict[str, Any]]], max_results: int) -> Tuple[List[Dict[str, Any]], int]:
    deduped = []
    seen = set()
    dedup_count = 0
    for provider_name, data in results_by_provider:
        for item in data.get("results", []):
            norm = normalize_result_url(item.get("url", ""))
            if norm and norm in seen:
                dedup_count += 1
                continue
            if norm:
                seen.add(norm)
            item = item.copy()
            item.setdefault("provider", provider_name)
            deduped.append(item)
            if len(deduped) >= max_results:
                return deduped, dedup_count
    return deduped, dedup_count

# =============================================================================
# HTTP Client
# =============================================================================

def make_request(url: str, headers: dict, body: dict, timeout: int = 30) -> dict:
    """Make HTTP POST request and return JSON response."""
    # Ensure User-Agent is set (required by some APIs like Exa/Cloudflare)
    if "User-Agent" not in headers:
        headers["User-Agent"] = "ClawdBot-WebSearchPlus/2.1"
    data = json.dumps(body).encode("utf-8")
    req = Request(url, data=data, headers=headers, method="POST")
    
    try:
        with urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else str(e)
        try:
            error_json = json.loads(error_body)
            error_detail = error_json.get("error") or error_json.get("message") or error_body
        except json.JSONDecodeError:
            error_detail = error_body[:500]
        
        error_messages = {
            401: "Invalid or expired API key. Please check your credentials.",
            403: "Access forbidden. Your API key may not have permission for this operation.",
            429: "Rate limit exceeded. Please wait a moment and try again.",
            500: "Server error. The search provider is experiencing issues.",
            503: "Service unavailable. The search provider may be down."
        }
        
        friendly_msg = error_messages.get(e.code, f"API error: {error_detail}")
        raise ProviderRequestError(f"{friendly_msg} (HTTP {e.code})", status_code=e.code, transient=e.code in TRANSIENT_HTTP_CODES)
    except URLError as e:
        reason = str(getattr(e, "reason", e))
        is_timeout = "timed out" in reason.lower()
        raise ProviderRequestError(f"Network error: {reason}. Check your internet connection.", transient=is_timeout)
    except TimeoutError:
        raise ProviderRequestError(f"Request timed out after {timeout}s. Try again or reduce max_results.", transient=True)


# =============================================================================
# Serper (Google Search API)
# =============================================================================

def search_serper(
    query: str,
    api_key: str,
    max_results: int = 5,
    country: str = "us",
    language: str = "en",
    search_type: str = "search",
    time_range: Optional[str] = None,
    include_images: bool = False,
) -> dict:
    """Search using Serper (Google Search API)."""
    endpoint = f"https://google.serper.dev/{search_type}"
    
    body = {
        "q": query,
        "gl": country,
        "hl": language,
        "num": max_results,
        "autocorrect": True,
    }
    
    if time_range and time_range != "none":
        tbs_map = {
            "hour": "qdr:h",
            "day": "qdr:d",
            "week": "qdr:w",
            "month": "qdr:m",
            "year": "qdr:y",
        }
        if time_range in tbs_map:
            body["tbs"] = tbs_map[time_range]
    
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json",
    }
    
    data = make_request(endpoint, headers, body)
    
    results = []
    for i, item in enumerate(data.get("organic", [])[:max_results]):
        results.append({
            "title": item.get("title", ""),
            "url": item.get("link", ""),
            "snippet": item.get("snippet", ""),
            "score": round(1.0 - i * 0.1, 2),
            "date": item.get("date"),
        })
    
    answer = ""
    if data.get("answerBox", {}).get("answer"):
        answer = data["answerBox"]["answer"]
    elif data.get("answerBox", {}).get("snippet"):
        answer = data["answerBox"]["snippet"]
    elif data.get("knowledgeGraph", {}).get("description"):
        answer = data["knowledgeGraph"]["description"]
    elif results:
        answer = results[0]["snippet"]
    
    images = []
    if include_images:
        try:
            img_data = make_request(
                "https://google.serper.dev/images",
                headers,
                {"q": query, "gl": country, "hl": language, "num": 5},
            )
            images = [img.get("imageUrl", "") for img in img_data.get("images", [])[:5] if img.get("imageUrl")]
        except Exception:
            pass
    
    return {
        "provider": "serper",
        "query": query,
        "results": results,
        "images": images,
        "answer": answer,
        "knowledge_graph": data.get("knowledgeGraph"),
        "related_searches": [r.get("query") for r in data.get("relatedSearches", [])]
    }


# =============================================================================
# Tavily (Research Search)
# =============================================================================

def search_tavily(
    query: str,
    api_key: str,
    max_results: int = 5,
    depth: str = "basic",
    topic: str = "general",
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    include_images: bool = False,
    include_raw_content: bool = False,
) -> dict:
    """Search using Tavily (AI Research Search)."""
    endpoint = "https://api.tavily.com/search"
    
    body = {
        "api_key": api_key,
        "query": query,
        "max_results": max_results,
        "search_depth": depth,
        "topic": topic,
        "include_images": include_images,
        "include_answer": True,
        "include_raw_content": include_raw_content,
    }
    
    if include_domains:
        body["include_domains"] = include_domains
    if exclude_domains:
        body["exclude_domains"] = exclude_domains
    
    headers = {"Content-Type": "application/json"}
    
    data = make_request(endpoint, headers, body)
    
    results = []
    for item in data.get("results", [])[:max_results]:
        result = {
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "snippet": item.get("content", ""),
            "score": round(item.get("score", 0.0), 3),
        }
        if include_raw_content and item.get("raw_content"):
            result["raw_content"] = item["raw_content"]
        results.append(result)
    
    return {
        "provider": "tavily",
        "query": query,
        "results": results,
        "images": data.get("images", []),
        "answer": data.get("answer", ""),
    }


# =============================================================================
# Exa (Neural/Semantic Search)
# =============================================================================

def search_exa(
    query: str,
    api_key: str,
    max_results: int = 5,
    search_type: str = "neural",
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    similar_url: Optional[str] = None,
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
) -> dict:
    """Search using Exa (Neural/Semantic Search)."""
    if similar_url:
        endpoint = "https://api.exa.ai/findSimilar"
        body = {
            "url": similar_url,
            "numResults": max_results,
            "contents": {
                "text": {"maxCharacters": 1000},
                "highlights": True,
            },
        }
    else:
        endpoint = "https://api.exa.ai/search"
        body = {
            "query": query,
            "numResults": max_results,
            "type": search_type,
            "contents": {
                "text": {"maxCharacters": 1000},
                "highlights": True,
            },
        }
    
    if category:
        body["category"] = category
    if start_date:
        body["startPublishedDate"] = start_date
    if end_date:
        body["endPublishedDate"] = end_date
    if include_domains:
        body["includeDomains"] = include_domains
    if exclude_domains:
        body["excludeDomains"] = exclude_domains
    
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }
    
    data = make_request(endpoint, headers, body)
    
    results = []
    for item in data.get("results", [])[:max_results]:
        highlights = item.get("highlights", [])
        snippet = highlights[0] if highlights else (item.get("text", "") or "")[:500]
        
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "snippet": snippet,
            "score": round(item.get("score", 0.0), 3),
            "published_date": item.get("publishedDate"),
            "author": item.get("author"),
        })
    
    answer = results[0]["snippet"] if results else ""
    
    return {
        "provider": "exa",
        "query": query if not similar_url else f"Similar to: {similar_url}",
        "results": results,
        "images": [],
        "answer": answer,
    }


# =============================================================================
# Perplexity via Kilo Gateway (Synthesized Direct Answers)
# =============================================================================

def search_perplexity(
    query: str,
    api_key: str,
    max_results: int = 5,
    model: str = "perplexity/sonar-pro",
    api_url: str = "https://api.kilo.ai/api/gateway/chat/completions",
    freshness: Optional[str] = None,
) -> dict:
    """Search/answer using Perplexity Sonar Pro via Kilo Gateway.

    Args:
        query: Search query
        api_key: Kilo Gateway API key
        max_results: Maximum results to return
        model: Perplexity model to use
        api_url: Kilo Gateway endpoint
        freshness: Filter by recency — 'day', 'week', 'month', 'year' (maps to
                   Perplexity's search_recency_filter parameter)
    """
    # Map generic freshness values to Perplexity's search_recency_filter
    recency_map = {"day": "day", "pd": "day", "week": "week", "pw": "week", "month": "month", "pm": "month", "year": "year", "py": "year"}
    recency_filter = recency_map.get(freshness or "", None)

    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Answer with concise factual summary and include source URLs."},
            {"role": "user", "content": query},
        ],
        "temperature": 0.2,
    }
    if recency_filter:
        body["search_recency_filter"] = recency_filter

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = make_request(api_url, headers, body)
    choices = data.get("choices", [])
    message = choices[0].get("message", {}) if choices else {}
    answer = (message.get("content") or "").strip()

    urls = re.findall(r"https?://[^\s)\]}>\"']+", answer)
    unique_urls = []
    seen = set()
    for u in urls:
        if u not in seen:
            seen.add(u)
            unique_urls.append(u)

    results = []

    # Primary result: the synthesized answer itself
    if answer:
        # Clean citation markers [1][2] for the snippet
        clean_answer = re.sub(r'\[\d+\]', '', answer).strip()
        results.append({
            "title": f"Perplexity Answer: {query[:80]}",
            "url": "https://www.perplexity.ai",
            "snippet": clean_answer[:500],
            "score": 1.0,
        })

    # Additional results: extracted source URLs
    for i, u in enumerate(unique_urls[:max_results - 1]):
        results.append({
            "title": f"Source {i+1}",
            "url": u,
            "snippet": "Referenced source from Perplexity answer",
            "score": round(0.9 - i * 0.1, 3),
        })

    return {
        "provider": "perplexity",
        "query": query,
        "results": results,
        "images": [],
        "answer": answer,
        "metadata": {
            "model": model,
            "usage": data.get("usage", {}),
        }
    }



# =============================================================================
# You.com (LLM-Ready Web & News Search)
# =============================================================================

def search_you(
    query: str,
    api_key: str,
    max_results: int = 5,
    country: str = "US",
    language: str = "en",
    freshness: Optional[str] = None,
    safesearch: str = "moderate",
    include_news: bool = True,
    livecrawl: Optional[str] = None,
) -> dict:
    """Search using You.com (LLM-Ready Web & News Search).
    
    You.com excels at:
    - RAG applications with pre-extracted snippets
    - Combined web + news results in one call
    - Real-time information with automatic news classification
    - Clean, structured JSON optimized for AI consumption
    
    Args:
        query: Search query
        api_key: You.com API key
        max_results: Maximum results to return (default 5, max 100)
        country: ISO 3166-2 country code (e.g., US, GB, DE)
        language: BCP 47 language code (e.g., en, de, fr)
        freshness: Filter by recency: day, week, month, year, or YYYY-MM-DDtoYYYY-MM-DD
        safesearch: Content filter: off, moderate (default), strict
        include_news: Include news results when relevant (default True)
        livecrawl: Fetch full page content: "web", "news", or "all"
    """
    endpoint = "https://ydc-index.io/v1/search"
    
    # Build query parameters
    params = {
        "query": query,
        "count": max_results,
        "safesearch": safesearch,
    }
    
    if country:
        params["country"] = country.upper()
    if language:
        params["language"] = language.upper()
    if freshness:
        params["freshness"] = freshness
    if livecrawl:
        params["livecrawl"] = livecrawl
        params["livecrawl_formats"] = "markdown"
    
    # Build URL with query params (URL-encode values)
    query_string = "&".join(f"{k}={quote(str(v))}" for k, v in params.items())
    url = f"{endpoint}?{query_string}"
    
    headers = {
        "X-API-KEY": api_key,
        "Accept": "application/json",
        "User-Agent": "ClawdBot-WebSearchPlus/2.4",
    }
    
    # Make GET request (You.com uses GET, not POST)
    from urllib.request import Request, urlopen
    req = Request(url, headers=headers, method="GET")
    
    try:
        with urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else str(e)
        try:
            error_json = json.loads(error_body)
            error_detail = error_json.get("error") or error_json.get("message") or error_body
        except json.JSONDecodeError:
            error_detail = error_body[:500]
        
        error_messages = {
            401: "Invalid or expired API key. Get one at https://api.you.com",
            403: "Access forbidden. Check your API key permissions.",
            429: "Rate limit exceeded. Please wait and try again.",
            500: "You.com server error. Try again later.",
            503: "You.com service unavailable."
        }
        friendly_msg = error_messages.get(e.code, f"API error: {error_detail}")
        raise ProviderRequestError(f"{friendly_msg} (HTTP {e.code})", status_code=e.code, transient=e.code in TRANSIENT_HTTP_CODES)
    except URLError as e:
        reason = str(getattr(e, "reason", e))
        is_timeout = "timed out" in reason.lower()
        raise ProviderRequestError(f"Network error: {reason}. Check your internet connection.", transient=is_timeout)
    except TimeoutError:
        raise ProviderRequestError("You.com request timed out after 30s.", transient=True)
    
    # Parse results
    results_data = data.get("results", {})
    web_results = results_data.get("web", [])
    news_results = results_data.get("news", []) if include_news else []
    metadata = data.get("metadata", {})
    
    # Normalize web results
    results = []
    for i, item in enumerate(web_results[:max_results]):
        snippets = item.get("snippets", [])
        snippet = snippets[0] if snippets else item.get("description", "")
        
        result = {
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "snippet": snippet,
            "score": round(1.0 - i * 0.05, 3),  # Assign descending score
            "date": item.get("page_age"),
            "source": "web",
        }
        
        # Include additional snippets if available (great for RAG)
        if len(snippets) > 1:
            result["additional_snippets"] = snippets[1:3]
        
        # Include thumbnail and favicon for UI display
        if item.get("thumbnail_url"):
            result["thumbnail"] = item["thumbnail_url"]
        if item.get("favicon_url"):
            result["favicon"] = item["favicon_url"]
        
        # Include live-crawled content if available
        if item.get("contents"):
            result["raw_content"] = item["contents"].get("markdown") or item["contents"].get("html", "")
        
        results.append(result)
    
    # Add news results (if any)
    news = []
    for item in news_results[:5]:
        news.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "snippet": item.get("description", ""),
            "date": item.get("page_age"),
            "thumbnail": item.get("thumbnail_url"),
            "source": "news",
        })
    
    # Build answer from best snippets
    answer = ""
    if results:
        # Combine top snippets for LLM context
        top_snippets = []
        for r in results[:3]:
            if r.get("snippet"):
                top_snippets.append(r["snippet"])
        answer = " ".join(top_snippets)[:1000]
    
    return {
        "provider": "you",
        "query": query,
        "results": results,
        "news": news,
        "images": [],
        "answer": answer,
        "metadata": {
            "search_uuid": metadata.get("search_uuid"),
            "latency": metadata.get("latency"),
        }
    }


# =============================================================================
# SearXNG (Privacy-First Meta-Search)
# =============================================================================

def search_searxng(
    query: str,
    instance_url: str,
    max_results: int = 5,
    categories: Optional[List[str]] = None,
    engines: Optional[List[str]] = None,
    language: str = "en",
    time_range: Optional[str] = None,
    safesearch: int = 0,
) -> dict:
    """Search using SearXNG (self-hosted privacy-first meta-search).
    
    SearXNG excels at:
    - Privacy-preserving search (no tracking, no profiling)
    - Multi-source aggregation (70+ upstream engines)
    - $0 API cost (self-hosted)
    - Diverse perspectives from multiple search engines
    
    Args:
        query: Search query
        instance_url: URL of your SearXNG instance (required)
        max_results: Maximum results to return (default 5)
        categories: Search categories (general, images, news, videos, etc.)
        engines: Specific engines to use (google, bing, duckduckgo, etc.)
        language: Language code (e.g., en, de, fr)
        time_range: Filter by recency: day, week, month, year
        safesearch: Content filter: 0=off, 1=moderate, 2=strict
    
    Note:
        Requires a self-hosted SearXNG instance with JSON format enabled.
        See: https://docs.searxng.org/admin/installation.html
    """
    # Build URL with query parameters
    params = {
        "q": query,
        "format": "json",
        "language": language,
        "safesearch": str(safesearch),
    }
    
    if categories:
        params["categories"] = ",".join(categories)
    if engines:
        params["engines"] = ",".join(engines)
    if time_range:
        params["time_range"] = time_range
    
    # Build URL — instance_url comes from operator-controlled config/env only
    # (validated by _validate_searxng_url), not from agent/LLM input
    base_url = instance_url.rstrip("/")
    query_string = "&".join(f"{k}={quote(str(v))}" for k, v in params.items())
    url = f"{base_url}/search?{query_string}"
    
    headers = {
        "User-Agent": "ClawdBot-WebSearchPlus/2.5",
        "Accept": "application/json",
    }
    
    # Make GET request
    req = Request(url, headers=headers, method="GET")
    
    try:
        with urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else str(e)
        try:
            error_json = json.loads(error_body)
            error_detail = error_json.get("error") or error_json.get("message") or error_body
        except json.JSONDecodeError:
            error_detail = error_body[:500]
        
        error_messages = {
            403: "JSON API disabled on this SearXNG instance. Enable 'json' in search.formats in settings.yml",
            404: "SearXNG instance not found. Check your instance URL.",
            500: "SearXNG server error. Check instance health.",
            503: "SearXNG service unavailable."
        }
        friendly_msg = error_messages.get(e.code, f"SearXNG error: {error_detail}")
        raise ProviderRequestError(f"{friendly_msg} (HTTP {e.code})", status_code=e.code, transient=e.code in TRANSIENT_HTTP_CODES)
    except URLError as e:
        reason = str(getattr(e, "reason", e))
        is_timeout = "timed out" in reason.lower()
        raise ProviderRequestError(f"Cannot reach SearXNG instance at {instance_url}. Error: {reason}", transient=is_timeout)
    except TimeoutError:
        raise ProviderRequestError(f"SearXNG request timed out after 30s. Check instance health.", transient=True)
    
    # Parse results
    raw_results = data.get("results", [])
    
    # Normalize results to unified format
    results = []
    engines_used = set()
    for i, item in enumerate(raw_results[:max_results]):
        engine = item.get("engine", "unknown")
        engines_used.add(engine)
        
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "snippet": item.get("content", ""),
            "score": round(item.get("score", 1.0 - i * 0.05), 3),
            "engine": engine,
            "category": item.get("category", "general"),
            "date": item.get("publishedDate"),
        })
    
    # Build answer from answers, infoboxes, or first result
    answer = ""
    if data.get("answers"):
        answer = data["answers"][0] if isinstance(data["answers"][0], str) else str(data["answers"][0])
    elif data.get("infoboxes"):
        infobox = data["infoboxes"][0]
        answer = infobox.get("content", "") or infobox.get("infobox", "")
    elif results:
        answer = results[0]["snippet"]
    
    return {
        "provider": "searxng",
        "query": query,
        "results": results,
        "images": [],
        "answer": answer,
        "suggestions": data.get("suggestions", []),
        "corrections": data.get("corrections", []),
        "metadata": {
            "number_of_results": data.get("number_of_results"),
            "engines_used": list(engines_used),
            "instance_url": instance_url,
        }
    }


# =============================================================================
# CLI
# =============================================================================

def main():
    config = load_config()
    
    parser = argparse.ArgumentParser(
        description="Web Search Plus — Intelligent multi-provider search with smart auto-routing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Intelligent Auto-Routing:
  The query is analyzed using multi-signal detection to find the optimal provider:
  
  Shopping Intent → Serper (Google)
    "how much", "price of", "buy", product+brand combos, deals, specs
  
  Research Intent → Tavily  
    "how does", "explain", "what is", analysis, pros/cons, tutorials
  
  Discovery Intent → Exa (Neural)
    "similar to", "companies like", "alternatives", URLs, startups, papers

  Direct Answer Intent → Perplexity (via Kilo Gateway)
    "what is", "current status", local events, synthesized up-to-date answers

Examples:
  python3 search.py -q "iPhone 16 Pro Max price"          # → Serper (shopping)
  python3 search.py -q "how does HTTPS encryption work"   # → Tavily (research)
  python3 search.py -q "startups similar to Notion"       # → Exa (discovery)
  python3 search.py --explain-routing -q "your query"     # Debug routing

Full docs: See README.md and SKILL.md
        """,
    )
    
    # Common arguments
    parser.add_argument(
        "--provider", "-p", 
        choices=["serper", "tavily", "exa", "perplexity", "you", "searxng", "auto"],
        help="Search provider (auto=intelligent routing)"
    )
    parser.add_argument(
        "--query", "-q", 
        help="Search query"
    )
    parser.add_argument(
        "--max-results", "-n", 
        type=int, 
        default=config.get("defaults", {}).get("max_results", 5),
        help="Maximum results (default: 5)"
    )
    parser.add_argument(
        "--images", 
        action="store_true",
        help="Include images (Serper/Tavily)"
    )
    
    # Auto-routing options
    parser.add_argument(
        "--auto", "-a",
        action="store_true",
        help="Use intelligent auto-routing (default when no provider specified)"
    )
    parser.add_argument(
        "--explain-routing",
        action="store_true",
        help="Show detailed routing analysis (debug mode)"
    )
    
    # Serper-specific
    serper_config = config.get("serper", {})
    parser.add_argument("--country", default=serper_config.get("country", "us"))
    parser.add_argument("--language", default=serper_config.get("language", "en"))
    parser.add_argument(
        "--type", 
        dest="search_type", 
        default=serper_config.get("type", "search"),
        choices=["search", "news", "images", "videos", "places", "shopping"]
    )
    parser.add_argument(
        "--time-range", 
        choices=["hour", "day", "week", "month", "year"]
    )
    
    # Tavily-specific
    tavily_config = config.get("tavily", {})
    parser.add_argument(
        "--depth", 
        default=tavily_config.get("depth", "basic"), 
        choices=["basic", "advanced"]
    )
    parser.add_argument(
        "--topic", 
        default=tavily_config.get("topic", "general"), 
        choices=["general", "news"]
    )
    parser.add_argument("--raw-content", action="store_true")
    
    # Exa-specific
    exa_config = config.get("exa", {})
    parser.add_argument(
        "--exa-type", 
        default=exa_config.get("type", "neural"), 
        choices=["neural", "keyword"]
    )
    parser.add_argument(
        "--category",
        choices=[
            "company", "research paper", "news", "pdf", "github", 
            "tweet", "personal site", "linkedin profile"
        ]
    )
    parser.add_argument("--start-date")
    parser.add_argument("--end-date")
    parser.add_argument("--similar-url")
    
    # You.com-specific
    you_config = config.get("you", {})
    parser.add_argument(
        "--you-safesearch",
        default=you_config.get("safesearch", "moderate"),
        choices=["off", "moderate", "strict"],
        help="You.com SafeSearch filter"
    )
    parser.add_argument(
        "--freshness",
        choices=["day", "week", "month", "year"],
        help="Filter results by recency (You.com/Serper)"
    )
    parser.add_argument(
        "--livecrawl",
        choices=["web", "news", "all"],
        help="You.com: fetch full page content"
    )
    parser.add_argument(
        "--include-news",
        action="store_true",
        default=True,
        help="You.com: include news results (default: true)"
    )
    
    # SearXNG-specific
    searxng_config = config.get("searxng", {})
    parser.add_argument(
        "--searxng-url",
        default=searxng_config.get("instance_url"),
        help="SearXNG instance URL (e.g., https://searx.example.com)"
    )
    parser.add_argument(
        "--searxng-safesearch",
        type=int,
        default=searxng_config.get("safesearch", 0),
        choices=[0, 1, 2],
        help="SearXNG SafeSearch: 0=off, 1=moderate, 2=strict"
    )
    parser.add_argument(
        "--engines",
        nargs="+",
        default=searxng_config.get("engines"),
        help="SearXNG: specific engines to use (e.g., google bing duckduckgo)"
    )
    parser.add_argument(
        "--categories",
        nargs="+",
        help="SearXNG: search categories (general, images, news, videos, etc.)"
    )
    
    # Domain filters
    parser.add_argument("--include-domains", nargs="+")
    parser.add_argument("--exclude-domains", nargs="+")
    
    # Output
    parser.add_argument("--compact", action="store_true")
    
    # Caching options
    parser.add_argument(
        "--cache-ttl",
        type=int,
        default=DEFAULT_CACHE_TTL,
        help=f"Cache TTL in seconds (default: {DEFAULT_CACHE_TTL} = 1 hour)"
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Bypass cache (always fetch fresh results)"
    )
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear all cached results and exit"
    )
    parser.add_argument(
        "--cache-stats",
        action="store_true",
        help="Show cache statistics and exit"
    )
    
    args = parser.parse_args()
    
    # Handle cache management commands first (before query validation)
    if args.clear_cache:
        result = cache_clear()
        indent = None if args.compact else 2
        print(json.dumps(result, indent=indent, ensure_ascii=False))
        return
    
    if args.cache_stats:
        result = cache_stats()
        indent = None if args.compact else 2
        print(json.dumps(result, indent=indent, ensure_ascii=False))
        return
    
    if not args.query and not args.similar_url:
        parser.error("--query is required (unless using --similar-url with Exa)")
    
    # Handle --explain-routing
    if args.explain_routing:
        if not args.query:
            parser.error("--query is required for --explain-routing")
        explanation = explain_routing(args.query, config)
        indent = None if args.compact else 2
        print(json.dumps(explanation, indent=indent, ensure_ascii=False))
        return
    
    # Determine provider
    if args.provider == "auto" or (args.provider is None and not args.similar_url):
        if args.query:
            routing = auto_route_provider(args.query, config)
            provider = routing["provider"]
            routing_info = {
                "auto_routed": True,
                "provider": provider,
                "confidence": routing["confidence"],
                "confidence_level": routing["confidence_level"],
                "reason": routing["reason"],
                "top_signals": routing["top_signals"],
                "scores": routing["scores"],
            }
        else:
            provider = "exa"
            routing_info = {
                "auto_routed": True,
                "provider": "exa",
                "confidence": 1.0,
                "confidence_level": "high",
                "reason": "similar_url_specified",
            }
    else:
        provider = args.provider or "serper"
        routing_info = {"auto_routed": False, "provider": provider}
    
    # Build provider fallback list
    auto_config = config.get("auto_routing", {})
    provider_priority = auto_config.get("provider_priority", ["tavily", "exa", "perplexity", "serper"])
    disabled_providers = auto_config.get("disabled_providers", [])

    # Start with the selected provider, then try others in priority order
    providers_to_try = [provider]
    for p in provider_priority:
        if p not in providers_to_try and p not in disabled_providers:
            providers_to_try.append(p)

    # Skip providers currently in cooldown
    eligible_providers = []
    cooldown_skips = []
    for p in providers_to_try:
        in_cd, remaining = provider_in_cooldown(p)
        if in_cd:
            cooldown_skips.append({"provider": p, "cooldown_remaining_seconds": remaining})
        else:
            eligible_providers.append(p)

    if not eligible_providers:
        eligible_providers = providers_to_try[:1]

    # Helper function to execute search for a provider
    def execute_search(prov: str) -> Dict[str, Any]:
        key = validate_api_key(prov, config)
        if prov == "serper":
            return search_serper(
                query=args.query,
                api_key=key,
                max_results=args.max_results,
                country=args.country,
                language=args.language,
                search_type=args.search_type,
                time_range=args.time_range,
                include_images=args.images,
            )
        elif prov == "tavily":
            return search_tavily(
                query=args.query,
                api_key=key,
                max_results=args.max_results,
                depth=args.depth,
                topic=args.topic,
                include_domains=args.include_domains,
                exclude_domains=args.exclude_domains,
                include_images=args.images,
                include_raw_content=args.raw_content,
            )
        elif prov == "exa":
            return search_exa(
                query=args.query or "",
                api_key=key,
                max_results=args.max_results,
                search_type=args.exa_type,
                category=args.category,
                start_date=args.start_date,
                end_date=args.end_date,
                similar_url=args.similar_url,
                include_domains=args.include_domains,
                exclude_domains=args.exclude_domains,
            )
        elif prov == "perplexity":
            perplexity_config = config.get("perplexity", {})
            return search_perplexity(
                query=args.query,
                api_key=key,
                max_results=args.max_results,
                model=perplexity_config.get("model", "perplexity/sonar-pro"),
                api_url=perplexity_config.get("api_url", "https://api.kilo.ai/api/gateway/chat/completions"),
                freshness=getattr(args, "freshness", None),
            )
        elif prov == "you":
            return search_you(
                query=args.query,
                api_key=key,
                max_results=args.max_results,
                country=args.country,
                language=args.language,
                freshness=args.freshness,
                safesearch=args.you_safesearch,
                include_news=args.include_news,
                livecrawl=args.livecrawl,
            )
        elif prov == "searxng":
            # For SearXNG, 'key' is actually the instance URL
            instance_url = args.searxng_url or key
            if instance_url:
                instance_url = _validate_searxng_url(instance_url)
            return search_searxng(
                query=args.query,
                instance_url=instance_url,
                max_results=args.max_results,
                categories=args.categories,
                engines=args.engines,
                language=args.language,
                time_range=args.time_range,
                safesearch=args.searxng_safesearch,
            )
        else:
            raise ValueError(f"Unknown provider: {prov}")

    def execute_with_retry(prov: str) -> Dict[str, Any]:
        last_error = None
        for attempt in range(0, 3):
            try:
                return execute_search(prov)
            except ProviderRequestError as e:
                last_error = e
                if e.status_code in {401, 403}:
                    break
                if not e.transient:
                    break
                if attempt < 2:
                    time.sleep(RETRY_BACKOFF_SECONDS[attempt])
                    continue
                break
            except Exception as e:
                last_error = e
                break
        raise last_error if last_error else Exception("Unknown provider execution error")

    cache_context = {
        "locale": f"{args.country}:{args.language}",
        "freshness": args.freshness,
        "time_range": args.time_range,
        "topic": args.topic,
        "search_engines": sorted(args.engines) if args.engines else None,
        "include_news": bool(args.include_news),
        "search_type": args.search_type,
        "exa_type": args.exa_type,
        "category": args.category,
        "similar_url": args.similar_url,
    }

    # Check cache first (unless --no-cache is set)
    cached_result = None
    cache_hit = False
    if not args.no_cache and args.query:
        cached_result = cache_get(
            query=args.query,
            provider=provider,
            max_results=args.max_results,
            ttl=args.cache_ttl,
            params=cache_context,
        )
        if cached_result:
            cache_hit = True
            result = {k: v for k, v in cached_result.items() if not k.startswith("_cache_")}
            result["cached"] = True
            result["cache_age_seconds"] = int(time.time() - cached_result.get("_cache_timestamp", 0))

    errors = []
    successful_provider = None
    successful_results: List[Tuple[str, Dict[str, Any]]] = []
    result = None if not cache_hit else result

    for idx, current_provider in enumerate(eligible_providers):
        if cache_hit:
            successful_provider = provider
            break
        try:
            provider_result = execute_with_retry(current_provider)
            reset_provider_health(current_provider)
            successful_results.append((current_provider, provider_result))
            successful_provider = current_provider

            # If we have enough results, stop.
            if len(provider_result.get("results", [])) >= args.max_results:
                break

            # Only continue collecting from lower-priority providers when fallback was needed.
            if not errors:
                break
        except Exception as e:
            error_msg = str(e)
            cooldown_info = mark_provider_failure(current_provider, error_msg)
            errors.append({
                "provider": current_provider,
                "error": error_msg,
                "cooldown_seconds": cooldown_info.get("cooldown_seconds"),
            })
            if len(eligible_providers) > 1:
                remaining = eligible_providers[idx + 1:]
                if remaining:
                    print(json.dumps({
                        "fallback": True,
                        "failed_provider": current_provider,
                        "error": error_msg,
                        "trying_next": remaining[0],
                    }), file=sys.stderr)
            continue

    if successful_results:
        if len(successful_results) == 1:
            result = successful_results[0][1]
        else:
            primary = successful_results[0][1].copy()
            deduped_results, dedup_count = deduplicate_results_across_providers(successful_results, args.max_results)
            primary["results"] = deduped_results
            primary["deduplicated"] = dedup_count > 0
            primary.setdefault("metadata", {})
            primary["metadata"]["dedup_count"] = dedup_count
            primary["metadata"]["providers_merged"] = [p for p, _ in successful_results]
            result = primary

    if result is not None:
        if successful_provider != provider:
            routing_info["fallback_used"] = True
            routing_info["original_provider"] = provider
            routing_info["provider"] = successful_provider
            routing_info["fallback_errors"] = errors

        if cooldown_skips:
            routing_info["cooldown_skips"] = cooldown_skips

        result["routing"] = routing_info

        if not cache_hit and not args.no_cache and args.query:
            cache_put(
                query=args.query,
                provider=successful_provider or provider,
                max_results=args.max_results,
                result=result,
                params=cache_context,
            )

        result["cached"] = bool(cache_hit)
        if "deduplicated" not in result:
            result["deduplicated"] = False
            result.setdefault("metadata", {})
            result["metadata"].setdefault("dedup_count", 0)

        indent = None if args.compact else 2
        print(json.dumps(result, indent=indent, ensure_ascii=False))
    else:
        error_result = {
            "error": "All providers failed",
            "provider": provider,
            "query": args.query,
            "routing": routing_info,
            "provider_errors": errors,
            "cooldown_skips": cooldown_skips,
        }
        print(json.dumps(error_result, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
