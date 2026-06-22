#!/usr/bin/env python3
"""
Novada Search v2.0.0 — AI Agent Search Platform

Three-layer architecture:
  Layer 1: Full Engine Support (9 engines + Google 13 sub-types)
  Layer 2: Vertical Scenes (shopping, jobs, academic, local, video, news, travel)
  Layer 3: AI Agent Mode (auto, multi-engine, extract)

Designed to compete with Tavily as an AI-optimized search API.
"""

import argparse
import json
import math
import os
import pathlib
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from urllib.parse import urlparse
from typing import List, Dict, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

VERBOSE = False
CLI_API_KEY: Optional[str] = None

NOVADA_SEARCH_URL = "https://scraperapi.novada.com/search"
DEFAULT_FETCH_MODE = "static"


class NovadaSearchError(Exception):
    """Base exception for Novada Search."""


class NovadaAPIError(NovadaSearchError):
    """API returned an error."""

    def __init__(self, message: str, code: int = None, engine: str = None):
        self.code = code
        self.engine = engine
        super().__init__(message)


class NovadaConfigError(NovadaSearchError):
    """Configuration error (e.g., missing API key)."""


class NovadaNetworkError(NovadaSearchError):
    """Network-level error."""

    def __init__(self, message: str, retryable: bool = True):
        self.retryable = retryable
        super().__init__(message)

# ============================================================================
# Layer 1: Full Engine Registry
# ============================================================================

SUPPORTED_ENGINES = (
    "google", "bing", "yahoo", "duckduckgo",
    "yandex", "youtube", "ebay", "walmart", "yelp",
)

GOOGLE_TYPES = (
    "search", "shopping", "local", "videos", "news",
    "images", "flights", "jobs", "scholar", "finance",
    "patents", "play", "lens",
)

# Engine capabilities metadata — used by auto-search to pick the best engine
ENGINE_CAPABILITIES = {
    "google":      {"web": True, "local": True, "shopping": True, "news": True, "video": True, "images": True, "academic": True, "jobs": True, "travel": True, "finance": True},
    "bing":        {"web": True, "local": True, "shopping": True, "news": True, "video": True, "images": True},
    "yahoo":       {"web": True, "news": True, "finance": True},
    "duckduckgo":  {"web": True, "privacy": True},
    "yandex":      {"web": True, "local": True, "images": True},
    "youtube":     {"video": True},
    "ebay":        {"shopping": True, "ecommerce": True},
    "walmart":     {"shopping": True, "ecommerce": True},
    "yelp":        {"local": True, "reviews": True},
}

# Query parameter name per engine — Novada API uses different param names
ENGINE_QUERY_PARAM = {
    "google":      "q",
    "bing":        "q",
    "duckduckgo":  "q",
    "ebay":        "_nkw",
    "walmart":     "query",
    "youtube":     "search_query",
    "yandex":      "text",
    "yelp":        "find_desc",
    "yahoo":       "p",
}

# ============================================================================
# Layer 2: Vertical Scene Definitions
# ============================================================================

SCENES = {
    "shopping": {
        "description": "Cross-platform price comparison",
        "engines": [
            {"engine": "google", "google_type": "shopping", "fetch_mode": "dynamic"},
            {"engine": "ebay"},
            {"engine": "walmart"},
        ],
        "merge_strategy": "price_compare",
    },
    "local": {
        "description": "Local business discovery with reviews",
        "engines": [
            {"engine": "google", "google_type": "local", "fetch_mode": "dynamic"},
            {"engine": "yelp"},
        ],
        "merge_strategy": "rating_merge",
    },
    "jobs": {
        "description": "Job search across platforms",
        "engines": [
            {"engine": "google", "google_type": "jobs"},
        ],
        "merge_strategy": "jobs_format",
    },
    "academic": {
        "description": "Academic paper and research search",
        "engines": [
            {"engine": "google", "google_type": "scholar"},
        ],
        "merge_strategy": "academic_format",
    },
    "video": {
        "description": "Video content across platforms",
        "engines": [
            {"engine": "youtube"},
            {"engine": "google", "google_type": "videos"},
        ],
        "merge_strategy": "video_merge",
    },
    "news": {
        "description": "Latest news from multiple sources",
        "engines": [
            {"engine": "google", "google_type": "news"},
            {"engine": "bing"},
        ],
        "merge_strategy": "recency_merge",
    },
    "travel": {
        "description": "Flights and travel planning",
        "engines": [
            {"engine": "google", "google_type": "flights"},
        ],
        "merge_strategy": "travel_format",
    },
    "images": {
        "description": "Image search across engines",
        "engines": [
            {"engine": "google", "google_type": "images"},
        ],
        "merge_strategy": "image_format",
    },
    "finance": {
        "description": "Financial data and stock info",
        "engines": [
            {"engine": "google", "google_type": "finance"},
            {"engine": "yahoo"},
        ],
        "merge_strategy": "finance_format",
    },
}


# ============================================================================
# Layer 3: Auto-Search Intent Detection
# ============================================================================

INTENT_KEYWORDS_WEIGHTED = {
    "shopping": {
        "strong": ["buy", "purchase", "price compare", "how much does", "where to buy", "kaufen", "购买", "比价"],
        "medium": ["price", "cheap", "deal", "discount", "cost", "coupon", "sale", "preis", "价格", "便宜", "优惠"],
        "weak": ["order", "shop", "store", "offer", "bestellen", "商城"],
    },
    "local": {
        "strong": ["near me", "nearby", "in der nähe", "附近", "周边"],
        "medium": ["restaurant", "cafe", "café", "hotel", "gym", "hospital", "dentist", "pharmacy", "餐厅", "咖啡", "酒店"],
        "weak": ["bar", "coffee", "gas station"],
    },
    "jobs": {
        "strong": ["job opening", "hiring", "job vacancy", "招聘", "求职"],
        "medium": ["job", "career", "salary", "position", "vacancy", "internship", "stelle", "gehalt", "工作", "岗位", "职位"],
        "weak": ["remote work", "developer", "engineer"],
    },
    "academic": {
        "strong": ["research paper", "academic paper", "arxiv", "peer review", "学术论文", "研究论文"],
        "medium": ["journal", "citation", "thesis", "dissertation", "期刊", "引用"],
        "weak": ["study", "research"],
    },
    "video": {
        "strong": ["video tutorial", "watch video", "youtube tutorial", "视频教程"],
        "medium": ["tutorial", "watch", "youtube", "demo", "walkthrough", "unboxing", "教程", "演示", "评测"],
        "weak": ["video"],
    },
    "news": {
        "strong": ["breaking news", "latest news", "headline news", "今日新闻", "最新新闻"],
        "medium": ["news", "latest", "breaking", "headline", "nachrichten", "aktuell", "新闻", "快讯", "资讯", "最新"],
        "weak": ["update", "announcement", "today"],
    },
    "travel": {
        "strong": ["flight to", "flights to", "book flight", "book flights", "航班", "机票"],
        "medium": ["flight", "flights", "airline", "airport", "travel", "booking", "ticket", "flug", "reise", "旅行", "行程"],
        "weak": ["fly", "出行"],
    },
    "images": {
        "strong": ["image search", "photo reference", "图片搜索", "找图"],
        "medium": ["image", "photo", "picture", "wallpaper", "logo", "icon", "bild", "foto", "图片", "照片", "壁纸", "图标"],
        "weak": ["素材"],
    },
    "finance": {
        "strong": ["stock price", "market cap", "股价", "行情"],
        "medium": ["stock", "share", "trading", "invest", "dividend", "nasdaq", "aktie", "börse", "股票", "投资", "基金", "融资"],
        "weak": ["market"],
    },
}

INTENT_NEGATIVE_KEYWORDS = {
    "academic": ["paper towel", "paper bag", "paper plate", "paper cup", "toilet paper", "wallpaper", "wall paper", "newspaper", "news paper"],
    "video": ["video game", "video card", "video memory"],
    "jobs": ["nose job", "blow job", "paint job", "desk job description"],
}


def _has_cjk(text: str) -> bool:
    return any('\u4e00' <= c <= '\u9fff' for c in text)


def _keyword_matches(query_lower: str, keyword: str) -> bool:
    """Match keywords with boundaries for latin text and substring for CJK."""
    keyword = keyword.lower().strip()
    if not keyword:
        return False
    if _has_cjk(keyword):
        return keyword in query_lower
    pattern = r"\b" + re.escape(keyword) + r"\b"
    return bool(re.search(pattern, query_lower))


def detect_intent(query: str) -> Optional[str]:
    """Detect intent with weighted matching + negative filtering + confidence threshold."""
    query_lower = query.lower().strip()
    scores: Dict[str, float] = {}

    for scene, groups in INTENT_KEYWORDS_WEIGHTED.items():
        negatives = INTENT_NEGATIVE_KEYWORDS.get(scene, [])
        if any(neg in query_lower for neg in negatives):
            continue

        score = 0.0
        for kw in groups.get("strong", []):
            if _keyword_matches(query_lower, kw):
                score += 3.0
        for kw in groups.get("medium", []):
            if _keyword_matches(query_lower, kw):
                score += 1.5
        for kw in groups.get("weak", []):
            if _keyword_matches(query_lower, kw):
                score += 0.5

        if score > 0:
            scores[scene] = score

    if not scores:
        return None

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_scene, best_score = ranked[0]
    second_best = ranked[1][1] if len(ranked) > 1 else 0.0

    if best_score < 1.5:
        return None
    if second_best > 0 and (best_score / second_best) < 1.5:
        return None

    return best_scene


# ============================================================================
# Domain-specific hardcoded company DB removed in v1.0.7
# (kept intentionally generic for search quality and maintainability)
# ============================================================================


# ============================================================================
# API Key Loading
# ============================================================================

def load_key() -> Optional[str]:
    """Resolve NOVADA_API_KEY from CLI override, environment, or local .env"""
    global CLI_API_KEY
    if CLI_API_KEY:
        debug_log("Using NOVADA_API_KEY from --api-key flag")
        return CLI_API_KEY.strip()

    key = os.environ.get("NOVADA_API_KEY")
    if key:
        debug_log("Using NOVADA_API_KEY from environment")
        return key.strip()

    env_path = pathlib.Path.cwd() / ".env"
    if env_path.exists():
        try:
            txt = env_path.read_text(encoding="utf-8", errors="ignore")
            import re as _re
            match = _re.search(r'^\s*NOVADA_API_KEY\s*=\s*(.+?)\s*$', txt, _re.M)
            if match:
                value = match.group(1).strip().strip('"').strip("'")
                if value:
                    debug_log("Using NOVADA_API_KEY from local .env")
                    return value
        except Exception:
            pass

    return None


# ============================================================================
# Success Checks & Logging Helpers
# ============================================================================

def ensure_success(raw: dict, context: str = "") -> None:
    """Raise if Novada API returned a logical error code."""
    target = raw
    if isinstance(raw.get("data"), dict):
        target = raw["data"]
    code = target.get("code") if isinstance(target, dict) else None
    message = target.get("msg") or target.get("message") if isinstance(target, dict) else None
    if code is None:
        return
    try:
        code_int = int(code)
    except (TypeError, ValueError):
        return
    if code_int not in (0, 200):
        ctx = f" during {context}" if context else ""
        raise NovadaAPIError(
            f"Novada API logical error{ctx} (code {code_int}): {message or 'no message'}",
            code=code_int,
            engine=context or None,
        )


def debug_log(message: str) -> None:
    if VERBOSE:
        print(f"[novada-search] {message}")

# ============================================================================
# API Call — supports all engines + Google sub-types
# ============================================================================

def _request_with_retry(url: str, headers: dict, max_retries: int = 2, timeout: int = 30) -> str:
    """HTTP GET with exponential backoff retry."""
    last_error: Optional[Exception] = None
    for attempt in range(max_retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers, method="GET")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else ""
            if e.code in (429, 500, 502, 503, 504) and attempt < max_retries:
                wait = 2 ** attempt
                debug_log(f"HTTP {e.code}, retrying in {wait}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait)
                last_error = NovadaAPIError(f"HTTP {e.code}: {body[:200]}", code=e.code)
                continue
            raise NovadaAPIError(f"HTTP {e.code}: {body[:200]}", code=e.code)
        except urllib.error.URLError as e:
            if attempt < max_retries:
                wait = 2 ** attempt
                debug_log(f"Network error: {e}, retrying in {wait}s")
                time.sleep(wait)
                last_error = NovadaNetworkError(str(e))
                continue
            raise NovadaNetworkError(str(e))
        except Exception as e:
            raise NovadaNetworkError(str(e), retryable=False)
    raise last_error or NovadaNetworkError("Max retries exceeded")


def novada_search(query: str, engine: str, google_type: str = None,
                  max_results: int = 10, fetch_mode: str = DEFAULT_FETCH_MODE) -> dict:
    """Call Novada search endpoint. Supports all 9 engines + Google sub-types."""
    key = load_key()
    if not key:
        raise NovadaConfigError(
            "Missing NOVADA_API_KEY. Set env var, pass --api-key, or add NOVADA_API_KEY to a local .env"
        )

    query_param = ENGINE_QUERY_PARAM.get(engine, "q")
    params = {
        "engine": engine,
        query_param: query,
        "api_key": key,
        "fetch_mode": fetch_mode,
        "num": str(max_results),
    }

    # Yelp needs a location parameter if not embedded in query
    if engine == "yelp":
        params["find_loc"] = ""  # let provider auto-detect / use query context

    # Add Google sub-type if applicable
    if engine == "google" and google_type and google_type != "search":
        params["google_type"] = google_type

    url = NOVADA_SEARCH_URL + "?" + urllib.parse.urlencode(params)
    body = _request_with_retry(
        url,
        headers={"Accept": "application/json", "User-Agent": "NovadaSearch/2.0"},
        max_retries=2,
        timeout=30,
    )

    try:
        raw = json.loads(body)
    except json.JSONDecodeError:
        raise NovadaAPIError(f"Novada returned non-JSON: {body[:500]}")

    context = f"{engine}:{google_type}" if google_type else engine
    ensure_success(raw, context=context)
    debug_log(f"{context} returned data code OK")
    return raw


def novada_extract(url_to_extract: str, fetch_mode: str = "dynamic") -> dict:
    """Extract clean content from a URL using Novada API (Layer 3: Extract mode)."""
    key = load_key()
    if not key:
        raise NovadaConfigError("Missing NOVADA_API_KEY.")

    params = {
        "engine": "google",
        "q": "",
        "url": url_to_extract,
        "api_key": key,
        "fetch_mode": fetch_mode,
        "extract_mode": "content",
    }

    url = NOVADA_SEARCH_URL + "?" + urllib.parse.urlencode(params)
    try:
        body = _request_with_retry(
            url,
            headers={"Accept": "application/json", "User-Agent": "NovadaSearch/2.0"},
            max_retries=2,
            timeout=30,
        )
    except NovadaSearchError:
        raise

    try:
        raw = json.loads(body)
    except json.JSONDecodeError:
        return {"raw_content": body[:10000]}

    ensure_success(raw, context="extract")
    return raw


# ============================================================================
# Multi-Engine Search (Layer 3)
# ============================================================================

def multi_engine_search(query: str, engines: List[Dict], max_results: int = 10,
                        fetch_mode: str = DEFAULT_FETCH_MODE) -> List[Dict]:
    """
    Search across multiple engines concurrently and merge results.
    Each engine entry: {"engine": "google", "google_type": "shopping"} (google_type optional)
    """
    all_results = []

    def _search_one(eng_config):
        engine = eng_config["engine"]
        gtype = eng_config.get("google_type")
        try:
            eng_fetch_mode = eng_config.get("fetch_mode") or fetch_mode
            raw = novada_search(query, engine, google_type=gtype,
                                max_results=max_results, fetch_mode=eng_fetch_mode)
            data = raw.get("data") if isinstance(raw.get("data"), dict) else raw
            engine_label = f"{engine}:{gtype}" if gtype else engine
            result_payload = {
                "engine": engine,
                "google_type": gtype,
                "raw": raw,
                "data": data,
                "local_results": parse_local_results(data.get("local_results", [])),
                "organic_results": extract_organic_results(data, max_results),
                "shopping_results": extract_shopping_results(data),
                "video_results": extract_video_results(data),
                "news_results": extract_news_results(data),
                "jobs_results": extract_jobs_results(data),
            }
            annotate_result_sets(result_payload, engine_label, max_results)
            return result_payload
        except NovadaSearchError as e:
            return {"engine": engine, "google_type": gtype, "error": str(e),
                    "raw": {}, "data": {}, "local_results": [], "organic_results": [],
                    "shopping_results": [], "video_results": [], "news_results": [],
                    "jobs_results": []}

    with ThreadPoolExecutor(max_workers=min(len(engines), 5)) as pool:
        futures = {pool.submit(_search_one, eng): eng for eng in engines}
        for future in as_completed(futures):
            all_results.append(future.result())

    return all_results



def annotate_result_sets(result_payload: Dict, engine_label: str, max_results: int) -> None:
    """Attach source_engine and confidence metadata to each result set."""
    def _rank_confidence(rank: int) -> float:
        base = 1 - (rank / max(1, max_results))
        return round(max(0.1, base), 3)

    for idx, item in enumerate(result_payload.get("organic_results", [])):
        item["source_engine"] = engine_label
        item["_rank"] = idx
        item["confidence"] = _rank_confidence(idx)

    for idx, item in enumerate(result_payload.get("local_results", [])):
        item["source_engine"] = engine_label
        base_score = item.get("score") or 0
        if base_score and isinstance(base_score, (int, float)):
            item["confidence"] = round(min(1.0, base_score / 10), 3)
        else:
            item["confidence"] = _rank_confidence(idx)

    for idx, item in enumerate(result_payload.get("shopping_results", [])):
        item["source_engine"] = engine_label
        item["confidence"] = _rank_confidence(idx)

    for idx, item in enumerate(result_payload.get("video_results", [])):
        item["source_engine"] = engine_label
        item["confidence"] = _rank_confidence(idx)

    for idx, item in enumerate(result_payload.get("news_results", [])):
        item["source_engine"] = engine_label
        item["confidence"] = _rank_confidence(idx)

    for idx, item in enumerate(result_payload.get("jobs_results", [])):
        item["source_engine"] = engine_label
        item["confidence"] = _rank_confidence(idx)

def normalize_url_for_dedup(url: str) -> str:
    """Normalize URLs for stable deduplication across engines."""
    if not url:
        return ""
    u = url.strip().rstrip("/")
    u = re.sub(r'[?#].*$', '', u)
    u = re.sub(r'^https?://', '', u, flags=re.I)
    # collapse www.
    u = re.sub(r'^www\.', '', u, flags=re.I)
    return u.lower()


def result_dedup_key(item: Dict) -> str:
    """Best-effort key for dedup: normalized url, fallback to title+source."""
    u = normalize_url_for_dedup(item.get('url', '') or item.get('link', '') or '')
    if u:
        return u
    title = (item.get('title') or '').strip().lower()
    return re.sub(r'\s+', ' ', title)


def deduplicate_results(results: List[Dict], key_field: str = "url") -> List[Dict]:
    """Remove duplicate results based on normalized URL (and fallback title)."""
    seen = set()
    unique = []
    for r in results:
        # Prefer explicit key_field if present
        url = (r.get(key_field) or r.get('url') or '').strip()
        key = normalize_url_for_dedup(url) or result_dedup_key(r)
        if not key:
            continue
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)
    return unique


# ============================================================================
# URL Builders
# ============================================================================

def build_google_maps_url(name: str, address: str) -> str:
    search = f"{name} {address}".strip()
    return f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(search)}"

def build_website_search_url(name: str) -> str:
    return f"https://www.google.com/search?q={urllib.parse.quote(name + ' official website')}"

def build_youtube_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}" if video_id else ""

def build_ebay_item_url(item_id: str) -> str:
    return f"https://www.ebay.com/itm/{item_id}" if item_id else ""


# ============================================================================
# Data Extraction — Local Results (Google Maps / Yelp)
# ============================================================================

def extract_rating_from_label(label: str) -> Tuple[Optional[float], Optional[int]]:
    if not label:
        return None, None
    match = re.search(r'(\d+\.?\d*)\(([^)]+)\)', label)
    if match:
        rating = float(match.group(1))
        count_str = match.group(2)
        if 'K' in count_str:
            count = int(float(count_str.replace('K', '')) * 1000)
        elif 'M' in count_str:
            count = int(float(count_str.replace('M', '')) * 1000000)
        else:
            try:
                count = int(count_str)
            except ValueError:
                count = None
        return rating, count
    return None, None

def extract_price_from_label(label: str) -> Optional[str]:
    if not label:
        return None
    match = re.search(r'([€$£¥]\d+[\s\-–]+\d+)', label)
    if match:
        return match.group(1).replace('–', '-').replace(' ', '')
    return None

def extract_business_type_from_label(label: str) -> str:
    if not label:
        return "Business"
    parts = [p.strip() for p in label.split('·')]
    for part in reversed(parts):
        if part and not any(c in part for c in '€$£¥()0123456789'):
            return part
    return "Business"


def parse_local_results(local_data: List[Dict]) -> List[Dict]:
    """Parse Google Maps / Yelp local results."""
    businesses = []
    for item in local_data:
        label = item.get("label", "")
        business = {
            "name": item.get("title", "Unknown"),
            "address": item.get("address", ""),
            "rating": None, "review_count": 0,
            "price_range": None, "business_type": "",
            "score": 0.0,
            "maps_url": "", "website_search_url": "",
            "source": item.get("origin_site", "google"),
            "phone": item.get("phone", ""),
            "website": item.get("website", item.get("link", "")),
            "hours": item.get("hours", item.get("operating_hours", "")),
            "open_now": item.get("open_now"),
            "thumbnail": item.get("thumbnail", item.get("image", "")),
        }
        if label:
            rating, count = extract_rating_from_label(label)
            business["rating"] = rating
            business["review_count"] = count
            business["price_range"] = extract_price_from_label(label)
            business["business_type"] = extract_business_type_from_label(label)
            if rating and count:
                business["score"] = round(rating * math.log(count + 1), 2)
            elif rating:
                business["score"] = rating
        business["maps_url"] = build_google_maps_url(business["name"], business["address"])
        business["website_search_url"] = build_website_search_url(business["name"])
        businesses.append(business)
    businesses.sort(key=lambda x: x["score"], reverse=True)
    return businesses


# ============================================================================
# Data Extraction — Shopping Results (eBay, Walmart, Google Shopping)
# ============================================================================

def extract_numeric_price(price_str: str) -> Optional[float]:
    """Extract numeric value from price string like '$19.99', '€24,50', '¥1999'."""
    if not price_str:
        return None
    cleaned = re.sub(r'[^\d.,]', '', str(price_str))
    if not cleaned:
        return None
    if ',' in cleaned and '.' not in cleaned:
        cleaned = cleaned.replace(',', '.')
    elif ',' in cleaned and '.' in cleaned:
        cleaned = cleaned.replace(',', '')
    try:
        return round(float(cleaned), 2)
    except ValueError:
        return None


def extract_shopping_results(data: dict) -> List[Dict]:
    """Extract shopping/product results from any engine."""
    results = []
    # Try various keys that different engines may use
    candidates = (
        data.get("shopping_results") or data.get("product_results") or
        data.get("products") or data.get("inline_shopping") or []
    )
    for item in candidates:
        if not isinstance(item, dict):
            continue
        results.append({
            "title": item.get("title", item.get("name", "")),
            "price": item.get("price", item.get("extracted_price", "")),
            "currency": item.get("currency", ""),
            "url": item.get("url", item.get("link", item.get("product_link", ""))),
            "image": item.get("thumbnail", item.get("image", "")),
            "seller": item.get("source", item.get("seller", item.get("merchant", ""))),
            "rating": item.get("rating"),
            "reviews": item.get("reviews", item.get("review_count")),
            "condition": item.get("condition", ""),
        })
    return results


# ============================================================================
# Data Extraction — Video Results (YouTube, Google Videos)
# ============================================================================

def extract_video_results(data: dict) -> List[Dict]:
    """Extract video results."""
    results = []
    candidates = data.get("video_results") or data.get("videos") or []
    for item in candidates:
        if not isinstance(item, dict):
            continue
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", item.get("link", "")),
            "duration": item.get("duration", item.get("length", "")),
            "views": item.get("views", ""),
            "channel": item.get("channel", item.get("author", item.get("source", ""))),
            "published": item.get("date", item.get("published_date", "")),
            "thumbnail": item.get("thumbnail", item.get("image", "")),
            "platform": item.get("platform", item.get("origin_site", "")),
        })
    return results


# ============================================================================
# Data Extraction — News Results
# ============================================================================

def extract_news_results(data: dict) -> List[Dict]:
    """Extract news results."""
    results = []
    candidates = data.get("news_results") or data.get("top_stories") or data.get("news") or []
    for item in candidates:
        if not isinstance(item, dict):
            continue
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", item.get("link", "")),
            "source": item.get("source", item.get("origin_site", "")),
            "date": item.get("date", item.get("published_date", "")),
            "snippet": item.get("snippet", item.get("description", "")),
            "thumbnail": item.get("thumbnail", item.get("image", "")),
        })
    return results


# ============================================================================
# Data Extraction — Jobs Results
# ============================================================================

def extract_jobs_results(data: dict) -> List[Dict]:
    """Extract job listing results."""
    results = []
    candidates = data.get("jobs_results") or data.get("jobs") or []
    for item in candidates:
        if not isinstance(item, dict):
            continue
        results.append({
            "title": item.get("title", ""),
            "company": item.get("company_name", item.get("company", "")),
            "location": item.get("location", ""),
            "url": item.get("url", item.get("link", item.get("apply_link", ""))),
            "salary": item.get("salary", ""),
            "date": item.get("date", item.get("posted_at", "")),
            "description": item.get("description", item.get("snippet", ""))[:300],
            "source": item.get("via", item.get("source", "")),
        })
    return results


# ============================================================================
# Data Extraction — Organic Results
# ============================================================================

def extract_organic_results(raw: dict, max_results: int) -> List[Dict]:
    """Extract web search results."""
    results = []
    candidates = raw.get("organic_results") or []
    if not candidates:
        candidates = raw.get("results") or []
    if not candidates:
        candidates = raw.get("search_results") or []
    if not candidates and isinstance(raw.get("data"), dict):
        candidates = raw["data"].get("organic_results") or raw["data"].get("results") or []
    if not candidates and isinstance(raw, list):
        candidates = raw

    for item in candidates[:max_results]:
        if not isinstance(item, dict):
            continue
        url = (item.get("url") or item.get("link") or item.get("href") or "").strip()
        if not url:
            continue
        results.append({
            "title": (item.get("title") or item.get("name") or "(no title)").strip(),
            "url": url,
            "snippet": (item.get("snippet") or item.get("description") or item.get("text") or "").strip(),
            "source": item.get("origin_site", item.get("displayed_link", ""))
        })
    return results


# ============================================================================
# Analysis & Recommendation
# ============================================================================

def analyze_businesses(businesses: List[Dict], max_recommendations: int = 5) -> Dict:
    if not businesses:
        return {"total_found": 0, "top_recommendations": [], "highest_rated": None,
                "most_reviewed": None, "average_rating": 0}
    top = businesses[:max_recommendations]
    ratings = [b["rating"] for b in businesses if b["rating"]]
    avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0
    return {
        "total_found": len(businesses),
        "top_recommendations": top,
        "highest_rated": max(businesses, key=lambda x: x["rating"] or 0),
        "most_reviewed": max(businesses, key=lambda x: x["review_count"] or 0),
        "average_rating": avg_rating,
    }


# ============================================================================
# Output Formatters — Agent-Friendly JSON (Tavily-compatible)
# ============================================================================

ENGINE_WEIGHTS = {
    # Defaults; tune later. Goal: stable, explainable ordering.
    "google": 1.00,
    "bing": 0.85,
    "duckduckgo": 0.75,
    "yahoo": 0.80,
    "yandex": 0.70,
    "youtube": 0.80,
    "ebay": 0.90,
    "walmart": 0.85,
    "yelp": 0.95,
}


def engine_base(engine_label: str) -> str:
    return (engine_label.split(":", 1)[0] if engine_label else "").strip()


def rank_weight(rank: int) -> float:
    # rank 0 best → 1.0; then decays.
    return 1.0 / (1.0 + max(0, int(rank)))


def merge_unified_results(items: List[Dict], top_k: int = 10) -> Tuple[List[Dict], int]:
    """Merge duplicates across engines and produce a unified ranked list.

    Returns (unified_results, duplicates_removed)
    """
    bucket: Dict[str, Dict] = {}
    duplicates = 0
    for it in items:
        key = result_dedup_key(it)
        if not key:
            continue
        src_engine = it.get('source_engine') or it.get('engine') or ''
        base = engine_base(src_engine)
        ew = ENGINE_WEIGHTS.get(base, 0.7)
        r = it.get('_rank', 999)
        base_score = ew * rank_weight(r)

        if key not in bucket:
            merged = dict(it)
            merged['engines'] = [src_engine] if src_engine else []
            merged['agreement_count'] = len(merged['engines'])
            merged['domain'] = (urlparse(merged.get('url','')).netloc or '').lower().replace('www.','')
            merged['score'] = round(base_score, 4)
            merged['rationale'] = f"Top result from {src_engine} (rank {r})"
            bucket[key] = merged
        else:
            duplicates += 1
            b = bucket[key]
            if src_engine and src_engine not in b.get('engines', []):
                b['engines'].append(src_engine)
            # agreement boost
            b['agreement_count'] = len(b.get('engines', []))
            b['domain'] = (urlparse(b.get('url','')).netloc or '').lower().replace('www.','')
            b['score'] = round(float(b.get('score', 0)) + 0.15, 4)
            b['rationale'] = f"Matched by {b['agreement_count']} engines (agreement boost)"
            # keep better title/snippet if missing
            if not b.get('snippet') and it.get('snippet'):
                b['snippet'] = it.get('snippet')
            if not b.get('title') and it.get('title'):
                b['title'] = it.get('title')

    unified = list(bucket.values())
    for u in unified:
        u['agreement_count'] = int(u.get('agreement_count') or len(u.get('engines', [])) or 1)
        u['domain'] = (u.get('domain') or (urlparse(u.get('url','')).netloc or '')).lower().replace('www.','')
    unified.sort(key=lambda x: (x.get('score', 0), x.get('agreement_count', 1), x.get('confidence', 0)), reverse=True)
    # cleanup internal fields
    for u in unified:
        u.pop('_rank', None)
    return unified[:top_k], duplicates


def classify_freshness(date_str: str) -> str:
    """Classify result freshness from common date formats."""
    if not date_str:
        return "unknown"
    now = datetime.now()
    cleaned = date_str.strip()
    for fmt in ("%Y-%m-%d", "%b %d, %Y", "%d %b %Y", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.strptime(cleaned[:19], fmt)
            delta = now - dt
            if delta < timedelta(days=1):
                return "today"
            if delta < timedelta(days=7):
                return "this_week"
            if delta < timedelta(days=30):
                return "this_month"
            if delta < timedelta(days=365):
                return "this_year"
            return "older"
        except ValueError:
            continue
    return "unknown"


def to_agent_json(query: str, all_engine_results: List[Dict], scene: str = None,
                  response_time_ms: Optional[int] = None,
                  fetch_mode_used: Optional[str] = None) -> dict:
    """
    AI Agent optimized JSON output — designed to be consumed directly by LLMs.
    This is our answer to Tavily's search API format.
    """
    # Merge all results across engines
    all_organic = []
    all_local = []
    all_shopping = []
    all_video = []
    all_news = []
    all_jobs = []

    engines_used = []
    errors = []

    for er in all_engine_results:
        engine_label = er["engine"]
        if er.get("google_type"):
            engine_label += f":{er['google_type']}"
        engines_used.append(engine_label)

        if er.get("error"):
            errors.append({"engine": engine_label, "error": er["error"]})
            continue

        all_organic.extend(er.get("organic_results", []))
        all_local.extend(er.get("local_results", []))
        all_shopping.extend(er.get("shopping_results", []))
        all_video.extend(er.get("video_results", []))
        all_news.extend(er.get("news_results", []))
        all_jobs.extend(er.get("jobs_results", []))

    all_organic_raw = list(all_organic)

    # Deduplicate
    all_organic = deduplicate_results(all_organic, "url")

    unified_results, duplicates_removed = merge_unified_results(all_organic_raw, top_k=10)

    if scene:
        for collection in (all_organic, all_local, all_shopping, all_video, all_news, all_jobs):
            for item in collection:
                item.setdefault("scene", scene)

    for item in all_organic:
        u = item.get("url", "")
        item["domain"] = (urlparse(u).netloc or "").lower().replace("www.", "")
        if item.get("date"):
            item["freshness"] = classify_freshness(item.get("date", ""))

    output = {
        "query": query,
        "scene": scene,
        "engines_used": engines_used,
        "duplicates_removed": duplicates_removed,
        "unified_count": len(unified_results),
        "response_time_ms": response_time_ms,
        "result_counts": {
            "organic": len(all_organic),
            "local": len(all_local),
            "shopping": len(all_shopping),
            "video": len(all_video),
            "news": len(all_news),
            "jobs": len(all_jobs),
        },
        "search_metadata": {
            "total_raw_results": len(all_organic_raw),
            "after_dedup": len(all_organic),
            "duplicates_removed": duplicates_removed,
            "fetch_mode": fetch_mode_used,
        },
    }

    if unified_results:
        output["unified_results"] = unified_results

    # Include non-empty result sets
    if all_organic:
        output["organic_results"] = all_organic[:10]
    if all_local:
        analysis = analyze_businesses(all_local)
        output["local_results"] = {
            "businesses": all_local[:10],
            "average_rating": analysis["average_rating"],
            "highest_rated": analysis.get("highest_rated"),
            "total_found": analysis["total_found"],
            "open_now_count": sum(1 for b in all_local if b.get("open_now") is True),
        }
    if all_shopping:
        output["shopping_results"] = all_shopping[:10]
        if scene == "shopping":
            price_comparison = []
            for item in all_shopping[:15]:
                numeric = extract_numeric_price(item.get("price", ""))
                price_comparison.append({
                    "product": (item.get("title") or "")[:80],
                    "price": item.get("price", ""),
                    "price_numeric": numeric,
                    "seller": item.get("seller", ""),
                    "rating": item.get("rating"),
                    "url": item.get("url", ""),
                    "engine": item.get("source_engine", ""),
                })
            price_comparison.sort(key=lambda x: x.get("price_numeric") or float('inf'))
            output["price_comparison"] = price_comparison
            if price_comparison:
                prices = [p["price_numeric"] for p in price_comparison if p.get("price_numeric") is not None]
                output["lowest_price"] = price_comparison[0]
                output["price_range"] = {
                    "min": min(prices) if prices else None,
                    "max": max(prices) if prices else None,
                }
    if all_video:
        output["video_results"] = all_video[:10]
    if all_news:
        output["news_results"] = all_news[:10]
    if all_jobs:
        output["jobs_results"] = all_jobs[:10]

    if errors:
        output["errors"] = errors

    return output


# ============================================================================
# Output Formatters — Human-Readable
# ============================================================================

def to_ranked_markdown(query: str, all_engine_results: List[Dict], scene: str = None) -> str:
    """Readable ranked output, multi-engine aware."""
    all_organic = []
    all_local = []
    all_shopping = []
    all_video = []
    all_news = []
    all_jobs = []

    for er in all_engine_results:
        if er.get("error"):
            continue
        all_organic.extend(er.get("organic_results", []))
        all_local.extend(er.get("local_results", []))
        all_shopping.extend(er.get("shopping_results", []))
        all_video.extend(er.get("video_results", []))
        all_news.extend(er.get("news_results", []))
        all_jobs.extend(er.get("jobs_results", []))

    all_organic = deduplicate_results(all_organic, "url")
    analysis = analyze_businesses(all_local)

    scene_label = f" [{scene}]" if scene else ""
    engines_str = ", ".join(set(er["engine"] for er in all_engine_results if not er.get("error")))

    lines = [
        f"# Search Results: '{query}'{scene_label}",
        f"Engines: {engines_str}",
        "",
    ]

    # Local businesses
    if all_local:
        lines.append(f"## Local Businesses ({analysis['total_found']} found, avg {analysis['average_rating']}/5)")
        lines.append("")
        for i, biz in enumerate(analysis["top_recommendations"][:5], 1):
            price_str = f" · {biz['price_range']}" if biz.get('price_range') else ""
            type_str = f" · {biz['business_type']}" if biz.get('business_type') else ""
            lines.append(f"### {i}. {biz['name']}")
            lines.append(f"  {biz['rating']}/5 ({biz['review_count']} reviews){price_str}{type_str}")
            lines.append(f"  {biz['address']}")
            lines.append(f"  [Maps]({biz.get('maps_url', '#')}) · [Website]({biz.get('website_search_url', '#')})")
            lines.append("")

    # Shopping results
    if all_shopping:
        lines.append("## Shopping Results")
        lines.append("")
        lines.append("| # | Product | Price | Seller | Rating |")
        lines.append("|---|---------|-------|--------|--------|")
        for i, item in enumerate(all_shopping[:10], 1):
            name = (item.get('title') or '')[:40]
            price = item.get('price', 'N/A')
            seller = (item.get('seller') or '')[:15]
            rating = f"{item['rating']}*" if item.get('rating') else '-'
            lines.append(f"| {i} | {name} | {price} | {seller} | {rating} |")
        lines.append("")

    # Video results
    if all_video:
        lines.append("## Video Results")
        lines.append("")
        for i, v in enumerate(all_video[:5], 1):
            dur = f" ({v['duration']})" if v.get('duration') else ""
            chan = f" — {v['channel']}" if v.get('channel') else ""
            lines.append(f"{i}. [{v['title']}]({v.get('url', '#')}){dur}{chan}")
        lines.append("")

    # News results
    if all_news:
        lines.append("## News")
        lines.append("")
        for i, n in enumerate(all_news[:5], 1):
            src = f" [{n['source']}]" if n.get('source') else ""
            dt = f" · {n['date']}" if n.get('date') else ""
            lines.append(f"{i}. [{n['title']}]({n.get('url', '#')}){src}{dt}")
        lines.append("")

    # Jobs results
    if all_jobs:
        lines.append("## Job Listings")
        lines.append("")
        for i, j in enumerate(all_jobs[:5], 1):
            company = f" at {j['company']}" if j.get('company') else ""
            loc = f" ({j['location']})" if j.get('location') else ""
            sal = f" · {j['salary']}" if j.get('salary') else ""
            lines.append(f"{i}. **{j['title']}**{company}{loc}{sal}")
            if j.get('url'):
                lines.append(f"   [Apply]({j['url']})")
        lines.append("")

    # Organic results
    if all_organic:
        lines.append("## Web Results")
        lines.append("")
        for i, item in enumerate(all_organic[:5], 1):
            lines.append(f"{i}. [{item['title']}]({item['url']})")
            if item.get('snippet'):
                lines.append(f"   {item['snippet'][:150]}")
        lines.append("")

    return "\n".join(lines)


def to_enhanced_markdown(query: str, all_engine_results: List[Dict], scene: str = None) -> str:
    """Enhanced markdown with clickable action links."""
    all_local = []
    all_organic = []
    for er in all_engine_results:
        if not er.get("error"):
            all_local.extend(er.get("local_results", []))
            all_organic.extend(er.get("organic_results", []))
    all_organic = deduplicate_results(all_organic, "url")
    analysis = analyze_businesses(all_local)

    lines = [
        f"# Actionable Results: '{query}'",
        "",
        f"**Found {analysis['total_found']} businesses with direct links**",
        "",
        "## Top Ranked (Click to open)",
        "",
    ]
    for i, biz in enumerate(analysis["top_recommendations"][:5], 1):
        price_str = f" · {biz['price_range']}" if biz.get('price_range') else ""
        type_str = f" · {biz['business_type']}" if biz.get('business_type') else ""
        lines.append(f"### {i}. {biz['name']}")
        lines.append(f"  {biz['rating']}/5 ({biz['review_count']} reviews){price_str}{type_str}")
        lines.append("")
        lines.append("**Quick Actions:**")
        lines.append(f"- [Open in Google Maps]({biz.get('maps_url', '#')})")
        lines.append(f"- [Search for website]({biz.get('website_search_url', '#')})")
        if biz.get('address'):
            lines.append(f"- Address: {biz['address']}")
        lines.append("")

    if all_organic:
        lines.append("---")
        lines.append("## Direct Links to Sources")
        lines.append("")
        for item in all_organic[:5]:
            lines.append(f"[{item['title']}]({item['url']})")
            if item.get('snippet'):
                lines.append(f"  {item['snippet'][:120]}")
            lines.append("")

    return "\n".join(lines)


def to_comparison_table(all_engine_results: List[Dict]) -> str:
    """Markdown table for side-by-side comparison."""
    all_local = []
    all_shopping = []
    for er in all_engine_results:
        if not er.get("error"):
            all_local.extend(er.get("local_results", []))
            all_shopping.extend(er.get("shopping_results", []))

    lines = []

    if all_local:
        lines.append("## Local Businesses")
        lines.append("")
        lines.append("| # | Name | Rating | Reviews | Price | Type |")
        lines.append("|---|------|--------|---------|-------|------|")
        for i, biz in enumerate(all_local[:10], 1):
            name = biz['name'][:25]
            rating = f"{biz['rating']}*" if biz['rating'] else "N/A"
            reviews = str(biz['review_count']) if biz['review_count'] else "N/A"
            price = biz.get('price_range') or "?"
            btype = biz.get('business_type', '?')[:12]
            lines.append(f"| {i} | {name} | {rating} | {reviews} | {price} | {btype} |")
        lines.append("")

    if all_shopping:
        lines.append("## Products")
        lines.append("")
        lines.append("| # | Product | Price | Seller | Rating |")
        lines.append("|---|---------|-------|--------|--------|")
        for i, item in enumerate(all_shopping[:10], 1):
            name = (item.get('title') or '')[:35]
            price = item.get('price', 'N/A')
            seller = (item.get('seller') or '')[:15]
            rating = f"{item['rating']}*" if item.get('rating') else '-'
            lines.append(f"| {i} | {name} | {price} | {seller} | {rating} |")
        lines.append("")

    if not lines:
        lines.append("No structured results found for table view.")

    return "\n".join(lines)


def to_action_links(query: str, all_engine_results: List[Dict]) -> str:
    """Shell commands to open results directly."""
    all_local = []
    all_organic = []
    for er in all_engine_results:
        if not er.get("error"):
            all_local.extend(er.get("local_results", []))
            all_organic.extend(er.get("organic_results", []))
    analysis = analyze_businesses(all_local)

    lines = [f"# Action Commands for: '{query}'", "", "Copy and run any command:", ""]
    if analysis.get("top_recommendations"):
        lines.append("## Local Businesses")
        lines.append("")
        for biz in analysis["top_recommendations"][:5]:
            lines.append(f"# {biz['name']}")
            lines.append(f"open \"{biz.get('maps_url', '')}\"")
            lines.append("")
    if all_organic:
        lines.append("## Web Sources")
        lines.append("")
        for item in all_organic[:5]:
            lines.append(f"# {item['title'][:50]}")
            lines.append(f"open \"{item['url']}\"")
            lines.append("")
    return "\n".join(lines)


# ============================================================================
# Public SDK Interface
# ============================================================================

class NovadaSearch:
    """
    Novada Search SDK — multi-engine AI search.

    Usage::

        from novada_search import NovadaSearch
        client = NovadaSearch(api_key="your_key")
        results = client.search("coffee Berlin", scene="local")
    """

    def __init__(self, api_key: str = None, verbose: bool = False):
        """
        Initialize Novada Search client.

        Args:
            api_key: Novada API key. Falls back to NOVADA_API_KEY env var / local .env.
            verbose: Enable debug logging.

        Raises:
            NovadaConfigError: If no API key is available.
        """
        global VERBOSE, CLI_API_KEY
        VERBOSE = verbose
        if api_key:
            CLI_API_KEY = api_key.strip()
        if not load_key():
            raise NovadaConfigError(
                "Missing API key. Pass api_key= or set NOVADA_API_KEY env var. "
                "Get a free key at https://novada.com"
            )

    def search(
        self,
        query: str,
        scene: str = None,
        mode: str = None,
        engine: str = "google",
        google_type: str = None,
        engines: list = None,
        max_results: int = 10,
        fetch_mode: str = "static",
        format: str = "agent-json",
    ) -> dict:
        """
        Execute a search query across one or more engines.

        Args:
            query: Search query string.
            scene: Vertical scene. One of: shopping, local, jobs, academic,
                   video, news, travel, finance, images. Auto-selects best
                   engine combination for the scene.
            mode: Agent mode. "auto" detects intent and picks scene.
                  "multi" searches multiple engines in parallel.
                  "research" searches then extracts content from top results.
            engine: Single engine to use (default "google"). Ignored if
                    scene or mode is set.
            google_type: Google sub-type (shopping, news, scholar, jobs,
                         flights, finance, videos, images, patents, play, lens).
            engines: List of engines for multi mode. Strings like "google",
                     "bing", or "google:shopping" for sub-types.
            max_results: Maximum results per engine (1-20, default 10).
            fetch_mode: "static" (fast) or "dynamic" (renders JavaScript).
            format: Output format. "agent-json" (default) returns structured
                    dict. Also supports "raw", "enhanced", "ranked", "table",
                    "action-links".

        Returns:
            dict with keys depending on format. For "agent-json":
              query, scene, engines_used, response_time_ms,
              unified_results (merged + ranked across engines),
              organic_results, local_results, shopping_results,
              video_results, news_results, jobs_results,
              search_metadata, errors.
        """
        max_results = max(1, min(max_results, 20))
        engines_to_search = []

        if mode == "auto":
            detected = detect_intent(query)
            if detected and detected in SCENES:
                scene = detected
                engines_to_search = SCENES[scene]["engines"]
            else:
                engines_to_search = [{"engine": "google"}]

        elif mode == "multi":
            if engines:
                for eng in engines:
                    if isinstance(eng, dict):
                        engines_to_search.append(eng)
                    elif ":" in eng:
                        e, gt = eng.split(":", 1)
                        engines_to_search.append({"engine": e, "google_type": gt})
                    else:
                        engines_to_search.append({"engine": eng})
            if not engines_to_search:
                engines_to_search = [{"engine": "google"}, {"engine": "bing"}, {"engine": "duckduckgo"}]

        elif scene and scene in SCENES:
            engines_to_search = SCENES[scene]["engines"]

        else:
            eng_config = {"engine": engine}
            if google_type:
                eng_config["google_type"] = google_type
            engines_to_search = [eng_config]

        started = time.time()
        all_engine_results = multi_engine_search(
            query, engines_to_search,
            max_results=max_results, fetch_mode=fetch_mode
        )
        elapsed_ms = int((time.time() - started) * 1000)

        if format == "raw":
            return {"engines": [{"engine": er["engine"], "data": er.get("raw", {})} for er in all_engine_results]}
        if format in ("enhanced", "ranked", "table", "action-links"):
            formatters = {
                "enhanced": to_enhanced_markdown,
                "ranked": to_ranked_markdown,
                "table": to_comparison_table,
                "action-links": to_action_links,
            }
            fn = formatters[format]
            if format == "action-links":
                return {"markdown": fn(query, all_engine_results)}
            return {"markdown": fn(query, all_engine_results, scene=scene)}

        return to_agent_json(
            query,
            all_engine_results,
            scene=scene,
            response_time_ms=elapsed_ms,
            fetch_mode_used=fetch_mode,
        )

    def extract(self, url: str, fetch_mode: str = "dynamic") -> dict:
        """Extract clean content from a URL."""
        return novada_extract(url, fetch_mode=fetch_mode)

    def detect_intent(self, query: str) -> Optional[str]:
        """Detect search intent from query text."""
        return detect_intent(query)

    def research(
        self,
        query: str,
        max_sources: int = 5,
        scene: str = None,
        fetch_mode: str = "dynamic",
    ) -> dict:
        """
        Deep research: search + extract content from top results.

        Searches first, then extracts full content from top result URLs for RAG-like pipelines.
        """
        max_sources = max(1, min(max_sources, 10))

        search_result = self.search(
            query=query,
            scene=scene,
            max_results=10,
            fetch_mode=fetch_mode,
            format="agent-json",
        )

        urls_to_extract = []
        candidates = search_result.get("unified_results") or search_result.get("organic_results") or []
        for r in candidates[:max_sources]:
            url = (r.get("url") or "").strip()
            if url and url.startswith("http"):
                urls_to_extract.append(url)

        extracted = []

        def _extract_one(url: str):
            try:
                content = novada_extract(url, fetch_mode=fetch_mode)
                return {"url": url, "content": content, "error": None}
            except NovadaSearchError as e:
                return {"url": url, "content": None, "error": str(e)}

        if urls_to_extract:
            with ThreadPoolExecutor(max_workers=min(len(urls_to_extract), 5)) as pool:
                futures = {pool.submit(_extract_one, u): u for u in urls_to_extract}
                for future in as_completed(futures):
                    extracted.append(future.result())

        search_result["mode"] = "research"
        search_result["extracted_content"] = extracted
        search_result["sources_extracted"] = len([e for e in extracted if e.get("content")])
        search_result["sources_failed"] = len([e for e in extracted if e.get("error")])
        return search_result


# ============================================================================
# Main
# ============================================================================

def main():
    ap = argparse.ArgumentParser(
        description="Novada Search v2.0 — AI Agent Search Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
LAYER 1 — Direct engine search:
  %(prog)s --query "coffee Berlin" --engine google
  %(prog)s --query "iPhone 16" --engine ebay
  %(prog)s --query "ML tutorial" --engine youtube
  %(prog)s --query "python jobs" --engine google --google-type jobs
  %(prog)s --query "transformer paper" --engine google --google-type scholar

LAYER 2 — Vertical scenes (auto-selects best engines):
  %(prog)s --query "MacBook Pro" --scene shopping
  %(prog)s --query "ramen Tokyo" --scene local
  %(prog)s --query "react tutorial" --scene video
  %(prog)s --query "AI latest" --scene news
  %(prog)s --query "python developer Berlin" --scene jobs

LAYER 3 — AI Agent modes:
  %(prog)s --query "buy Nike shoes" --mode auto
  %(prog)s --query "coffee Berlin" --mode multi --engines google,yelp
  %(prog)s --url "https://example.com/article" --mode extract

Formats: ranked, enhanced, table, action-links, agent-json, brave, raw
        """
    )

    ap.add_argument("--query", help="Search query")
    ap.add_argument("--url", help="URL to extract content from (extract mode)")
    ap.add_argument(
        "--engine", default="google", choices=SUPPORTED_ENGINES,
        help="Search engine (default: google)",
    )
    ap.add_argument(
        "--google-type", default=None, choices=GOOGLE_TYPES,
        help="Google sub-type: shopping, news, scholar, jobs, videos, etc.",
    )
    ap.add_argument(
        "--scene", default=None, choices=list(SCENES.keys()),
        help="Vertical scene: shopping, local, jobs, academic, video, news, travel, images, finance",
    )
    ap.add_argument(
        "--mode", default=None, choices=["auto", "multi", "extract", "research"],
        help="AI Agent mode: auto (smart engine selection), multi (parallel multi-engine), extract (URL content), research (search+extract)",
    )
    ap.add_argument(
        "--engines", default=None,
        help="Comma-separated engines for multi mode (e.g., google,bing,yelp)",
    )
    ap.add_argument("--max-results", type=int, default=10, help="Max results (1-20)")
    ap.add_argument(
        "--fetch-mode", default="static", choices=["static", "dynamic"],
        help="static (fast) or dynamic (JS pages)",
    )
    ap.add_argument(
        "--format", default="enhanced",
        choices=["raw", "brave", "agent-json", "ranked", "table", "md", "enhanced", "action-links"],
        help="Output format (default: enhanced)",
    )
    ap.add_argument(
        "--api-key", default=None,
        help="Override NOVADA_API_KEY for this run",
    )
    ap.add_argument(
        "--verbose", action="store_true",
        help="Verbose logging (print engine + timing info)",
    )
    args = ap.parse_args()

    global VERBOSE, CLI_API_KEY
    VERBOSE = args.verbose
    CLI_API_KEY = args.api_key.strip() if args.api_key else None

    max_results = max(1, min(args.max_results, 20))

    # ---- Mode: Research ----
    if args.mode == "research":
        if not args.query:
            raise NovadaConfigError("Research mode requires --query")
        client = NovadaSearch(api_key=args.api_key, verbose=args.verbose)
        result = client.research(
            query=args.query,
            max_sources=min(max_results, 5),
            scene=args.scene,
            fetch_mode=args.fetch_mode,
        )
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return

    # ---- Mode: Extract ----
    if args.mode == "extract" or (args.url and not args.query):
        if not args.url:
            raise NovadaConfigError("Extract mode requires --url")
        result = novada_extract(args.url, fetch_mode=args.fetch_mode)
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return

    if not args.query:
        raise NovadaConfigError("--query is required (unless using --mode extract with --url)")

    # ---- Determine which engines to search ----
    engines_to_search = []
    scene = args.scene

    if args.mode == "auto":
        # Layer 3: Auto-detect intent and pick scene
        detected = detect_intent(args.query)
        if detected and detected in SCENES:
            scene = detected
            engines_to_search = SCENES[scene]["engines"]
        else:
            # Default: Google web search
            engines_to_search = [{"engine": "google"}]

    elif args.mode == "multi":
        # Layer 3: Multi-engine parallel search
        if args.engines:
            for eng in args.engines.split(","):
                eng = eng.strip()
                if ":" in eng:
                    engine, gtype = eng.split(":", 1)
                    engines_to_search.append({"engine": engine, "google_type": gtype})
                elif eng in SUPPORTED_ENGINES:
                    engines_to_search.append({"engine": eng})
        if not engines_to_search:
            engines_to_search = [{"engine": "google"}, {"engine": "bing"}, {"engine": "duckduckgo"}]

    elif scene:
        # Layer 2: Use scene's predefined engines
        engines_to_search = SCENES[scene]["engines"]

    else:
        # Layer 1: Direct single-engine search
        eng_config = {"engine": args.engine}
        if args.google_type:
            eng_config["google_type"] = args.google_type
        engines_to_search = [eng_config]

    # ---- Execute search ----
    started = time.time()
    all_engine_results = multi_engine_search(
        args.query, engines_to_search,
        max_results=max_results, fetch_mode=args.fetch_mode
    )
    elapsed_ms = int((time.time() - started) * 1000)

    # ---- Output ----
    if args.format == "raw":
        raw_output = {"engines": []}
        for er in all_engine_results:
            raw_output["engines"].append({
                "engine": er["engine"],
                "google_type": er.get("google_type"),
                "data": er.get("raw", {}),
            })
        json.dump(raw_output, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")

    elif args.format in ["brave", "agent-json"]:
        json.dump(
            to_agent_json(
                args.query,
                all_engine_results,
                scene=scene,
                response_time_ms=elapsed_ms,
                fetch_mode_used=args.fetch_mode,
            ),
            sys.stdout, ensure_ascii=False, indent=2
        )
        sys.stdout.write("\n")

    elif args.format == "enhanced":
        sys.stdout.write(to_enhanced_markdown(args.query, all_engine_results, scene=scene))

    elif args.format == "action-links":
        sys.stdout.write(to_action_links(args.query, all_engine_results))

    elif args.format in ["ranked", "md"]:
        sys.stdout.write(to_ranked_markdown(args.query, all_engine_results, scene=scene))

    elif args.format == "table":
        sys.stdout.write(to_comparison_table(all_engine_results))
        sys.stdout.write("\n")


if __name__ == "__main__":
    try:
        main()
    except NovadaConfigError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except NovadaAPIError as e:
        print(f"API error: {e}", file=sys.stderr)
        sys.exit(2)
    except NovadaNetworkError as e:
        print(f"Network error: {e}", file=sys.stderr)
        sys.exit(3)
