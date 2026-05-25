#!/usr/bin/env python3
"""
Pangolin Amazon Scrape API Client

Zero-dependency Python client for Pangolin's Amazon Scrape APIs.
Supports product detail lookup, keyword search, bestsellers, new releases,
category browsing, seller products, variant options, and product reviews.

Semantic usage (no URL required):
    pangolin.py --content B0DYTF8L2W --mode amazon --site amz_us
    pangolin.py --q "wireless mouse" --mode amazon --site amz_us
    pangolin.py --content B00163U4LK --mode review --site amz_us

Legacy usage (URL-based):
    pangolin.py --url "https://amazon.com/dp/..." --mode amazon

Environment:
    PANGOLIN_API_KEY  - API key (skips login)
    PANGOLIN_EMAIL    - Account email (for login)
    PANGOLIN_PASSWORD - Account password (for login)
"""

import argparse
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------------------
# Fix Windows / macOS console encoding for Unicode output
# ---------------------------------------------------------------------------
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace"
    )
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr = io.TextIOWrapper(
        sys.stderr.buffer, encoding="utf-8", errors="replace"
    )

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
API_BASE = "https://scrapeapi.pangolinfo.com"
AUTH_ENDPOINT = f"{API_BASE}/api/v1/auth"
SCRAPE_V1_ENDPOINT = f"{API_BASE}/api/v1/scrape"
FOLLOW_SELLER_ENDPOINT = f"{API_BASE}/api/v1/scrape/follow-seller"
API_KEY_CACHE_PATH = Path.home() / ".pangolin_api_key"

EXIT_SUCCESS = 0
EXIT_API_ERROR = 1
EXIT_USAGE_ERROR = 2
EXIT_NETWORK_ERROR = 3
EXIT_AUTH_ERROR = 4

AMAZON_PARSERS = [
    "amzProductDetail",
    "amzKeyword",
    "amzProductOfCategory",
    "amzProductOfSeller",
    "amzBestSellers",
    "amzNewReleases",
    "amzFollowSeller",
    "amzReviewV2",
]

# Review filter and sort options
REVIEW_STAR_FILTERS = [
    "all_stars",
    "five_star",
    "four_star",
    "three_star",
    "two_star",
    "one_star",
    "positive",
    "critical",
]

REVIEW_SORT_OPTIONS = [
    "recent",
    "helpful",
]

# Amazon site codes mapped to region domains
AMAZON_SITES = {
    "amz_us": "amazon.com",
    "amz_uk": "amazon.co.uk",
    "amz_ca": "amazon.ca",
    "amz_de": "amazon.de",
    "amz_fr": "amazon.fr",
    "amz_jp": "amazon.co.jp",
    "amz_it": "amazon.it",
    "amz_es": "amazon.es",
    "amz_au": "amazon.com.au",
    "amz_mx": "amazon.com.mx",
    "amz_sa": "amazon.sa",
    "amz_ae": "amazon.ae",
    "amz_br": "amazon.com.br",
}

# Regex to detect ASIN pattern (10-character alphanumeric, uppercase)
ASIN_PATTERN = re.compile(r"^[A-Z0-9]{10}$", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Unified error helpers
# ---------------------------------------------------------------------------
def _error_exit(code, message, hint=None, exit_code=EXIT_API_ERROR):
    """Print a structured error envelope to stderr and exit."""
    err = {"success": False, "error": {"code": code, "message": message}}
    if hint:
        err["error"]["hint"] = hint
    print(json.dumps(err, ensure_ascii=False), file=sys.stderr)
    sys.exit(exit_code)


# ---------------------------------------------------------------------------
# API key management
# ---------------------------------------------------------------------------
def load_cached_api_key():
    """Load API key from cache file if it exists."""
    if API_KEY_CACHE_PATH.exists():
        api_key = API_KEY_CACHE_PATH.read_text().strip()
        if api_key and len(api_key.split(".")) == 3:  # Basic JWT format check
            return api_key
    return None


def save_cached_api_key(api_key):
    """Save API key to cache file."""
    API_KEY_CACHE_PATH.write_text(api_key)
    try:
        API_KEY_CACHE_PATH.chmod(0o600)
    except OSError:
        pass
    # Windows: restrict file access to current user
    if sys.platform == "win32":
        try:
            import subprocess
            subprocess.run(
                ["icacls", str(API_KEY_CACHE_PATH), "/inheritance:r",
                 "/grant:r", f"{os.environ.get('USERNAME', '')}:F"],
                capture_output=True, check=False,
            )
        except Exception:
            pass


def authenticate(email, password):
    """Authenticate with Pangolin API and return an API key."""
    body = json.dumps({"email": email, "password": password}).encode()
    req = urllib.request.Request(
        AUTH_ENDPOINT,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
    except urllib.error.URLError as e:
        # Improvement 1: macOS SSL certificate handling
        if "CERTIFICATE_VERIFY_FAILED" in str(e) or "SSL" in str(e):
            _error_exit(
                "SSL_CERT",
                "SSL certificate verification failed",
                hint=(
                    "macOS users: run '/Applications/Python 3.x/Install Certificates.command' "
                    "or set SSL_CERT_FILE env var. "
                    "See: python3 -c \"import certifi; print(certifi.where())\""
                ),
                exit_code=EXIT_NETWORK_ERROR,
            )
        _error_exit(
            "NETWORK",
            f"Network error during authentication: {e.reason if hasattr(e, 'reason') else e}",
            hint="Check your internet connection and try again.",
            exit_code=EXIT_NETWORK_ERROR,
        )

    if result.get("code") != 0:
        _error_exit(
            "AUTH_FAILED",
            result.get("message", "Authentication failed"),
            hint="Verify PANGOLIN_EMAIL and PANGOLIN_PASSWORD are correct.",
            exit_code=EXIT_AUTH_ERROR,
        )

    api_key = result["data"]
    save_cached_api_key(api_key)
    return api_key


def get_api_key():
    """Resolve API key from env var, cache file, or fresh login."""
    api_key = os.environ.get("PANGOLIN_API_KEY")
    if api_key:
        save_cached_api_key(api_key)  # Cache for future calls without env var
        return api_key

    api_key = load_cached_api_key()
    if api_key:
        return api_key

    email = os.environ.get("PANGOLIN_EMAIL")
    password = os.environ.get("PANGOLIN_PASSWORD")
    if not email or not password:
        _error_exit(
            "MISSING_ENV",
            "No authentication credentials found.",
            hint=(
                "Set PANGOLIN_API_KEY, or both PANGOLIN_EMAIL and PANGOLIN_PASSWORD "
                "environment variables."
            ),
            exit_code=EXIT_AUTH_ERROR,
        )

    return authenticate(email, password)


def refresh_api_key():
    """Force re-authentication using email/password."""
    email = os.environ.get("PANGOLIN_EMAIL")
    password = os.environ.get("PANGOLIN_PASSWORD")
    if not email or not password:
        _error_exit(
            "MISSING_ENV",
            "Cannot refresh API key without credentials.",
            hint="Set PANGOLIN_EMAIL and PANGOLIN_PASSWORD environment variables.",
            exit_code=EXIT_AUTH_ERROR,
        )
    return authenticate(email, password)


# ---------------------------------------------------------------------------
# Amazon-specific helpers
# ---------------------------------------------------------------------------
def infer_amazon_parser(content):
    """Infer the best Amazon parser based on content pattern."""
    if not content:
        return None
    if ASIN_PATTERN.match(content):
        return "amzProductDetail"
    return "amzKeyword"


def infer_site_from_url(url):
    """Extract Amazon site code from a URL."""
    # Sort by domain length descending to avoid amazon.com matching amazon.com.au
    for site_code, domain in sorted(AMAZON_SITES.items(), key=lambda x: len(x[1]), reverse=True):
        if domain in url:
            return site_code
    return None


def build_review_body(asin, site, filter_by_star, sort_by, page_count, fmt):
    """Build request body for Amazon Review API.

    Uses bizContext with bizKey=review to fetch product reviews.
    """
    if not asin:
        _error_exit(
            "USAGE_ERROR",
            "Review mode requires an ASIN.",
            hint="Provide --content <ASIN> or --q <ASIN>.",
            exit_code=EXIT_USAGE_ERROR,
        )

    domain = AMAZON_SITES.get(site or "amz_us", "amazon.com")

    body = {
        "url": f"https://www.{domain}",
        "format": fmt,
        "parserName": "amzReviewV2",
        "bizContext": {
            "bizKey": "review",
            "asin": asin,
            "pageCount": page_count,
            "filterByStar": filter_by_star,
            "sortBy": sort_by,
        },
    }
    return body


def build_follow_seller_body(asin, site, zipcode):
    """Build request body for Amazon Follow Seller API."""
    if not asin:
        _error_exit(
            "USAGE_ERROR",
            "Follow Seller mode requires an ASIN.",
            hint="Provide --content <ASIN> or --asin <ASIN>.",
            exit_code=EXIT_USAGE_ERROR,
        )
    domain = AMAZON_SITES.get(site or "amz_us", "amazon.com")
    return {
        "url": f"https://www.{domain}",
        "bizContext": {
            "zipcode": zipcode,
            "asin": asin,
        },
    }


def build_amazon_body(url, query, content, site, parser, zipcode, fmt):
    """Build request body for Amazon Scrape API.

    Supports three input modes:
    1. URL mode: provide url directly (legacy)
    2. Content mode: provide site + content (no URL needed)
    3. Query mode: provide query, auto-infer content and parser
    """
    body = {
        "format": fmt,
        "parserName": parser,
        "bizContext": {
            "zipcode": zipcode,
        },
    }

    # Mode 1: URL provided directly
    if url:
        body["url"] = url
        if site:
            body["site"] = site
        else:
            inferred = infer_site_from_url(url)
            if inferred:
                body["site"] = inferred
        if content:
            body["content"] = content
        return body

    # Mode 2: content + site (semantic mode)
    if content:
        if not site:
            site = "amz_us"
        body["site"] = site
        body["content"] = content
        # Auto-detect parser if user didn't override
        if parser == "amzProductDetail":
            inferred = infer_amazon_parser(content)
            if inferred:
                body["parserName"] = inferred
        return body

    # Mode 3: query as content (most semantic)
    if query:
        if not site:
            site = "amz_us"
        body["site"] = site
        body["content"] = query
        # Query implies keyword search unless parser was explicitly set
        if parser == "amzProductDetail":
            inferred = infer_amazon_parser(query)
            if inferred:
                body["parserName"] = inferred
        return body

    _error_exit(
        "USAGE_ERROR",
        "Amazon mode requires --url, --content, or --q.",
        hint="Provide at least one of: --url <URL>, --content <ASIN/keyword>, --q <keyword>.",
        exit_code=EXIT_USAGE_ERROR,
    )


# ---------------------------------------------------------------------------
# API call with retry
# ---------------------------------------------------------------------------
def call_api(api_key, body, endpoint, max_retries=3, timeout=120):
    """Call the scrape API with retry and exponential backoff."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "Pangolin-CLI/1.0",
    }
    payload = json.dumps(body).encode()

    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(
                endpoint,
                data=payload,
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read())

        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if e.fp else ""
            if e.code == 429:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                _error_exit(
                    "RATE_LIMIT",
                    "Too many requests. Rate limited by the API.",
                    hint="Wait a moment and retry, or reduce request frequency.",
                    exit_code=EXIT_NETWORK_ERROR,
                )
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            _error_exit(
                "NETWORK",
                f"HTTP {e.code} error from API.",
                hint="Check your request parameters and try again.",
                exit_code=EXIT_NETWORK_ERROR,
            )

        except urllib.error.URLError as e:
            # Improvement 1: macOS SSL certificate handling
            if "CERTIFICATE_VERIFY_FAILED" in str(e) or "SSL" in str(e):
                _error_exit(
                    "SSL_CERT",
                    "SSL certificate verification failed",
                    hint=(
                        "macOS users: run '/Applications/Python 3.x/Install Certificates.command' "
                        "or set SSL_CERT_FILE env var. "
                        "See: python3 -c \"import certifi; print(certifi.where())\""
                    ),
                    exit_code=EXIT_NETWORK_ERROR,
                )
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            _error_exit(
                "NETWORK",
                f"Network error: {e.reason if hasattr(e, 'reason') else e}",
                hint="Check your internet connection and try again.",
                exit_code=EXIT_NETWORK_ERROR,
            )

    return None


def handle_response(result, api_key, body, endpoint, timeout=120):
    """Handle API response, retrying auth on 1004 error."""
    if result.get("code") == 1004:
        new_api_key = refresh_api_key()
        return call_api(new_api_key, body, endpoint, timeout=timeout)
    return result


# ---------------------------------------------------------------------------
# Output extraction
# ---------------------------------------------------------------------------
def extract_amazon_output(result):
    """Extract structured output from Amazon Scrape API response.

    Handles both legacy flat format and new nested format:
    New: data.json[].metadata + data.json[].data.results[]
    Legacy: data.json as flat list/dict
    """
    code = result.get("code")
    if code != 0:
        msg = result.get("message", "Unknown error")
        # Map known API error codes
        if code == 2001:
            return {
                "success": False,
                "error": {
                    "code": "API_ERROR",
                    "message": f"Insufficient credits (code {code})",
                    "hint": "Top up credits at pangolinfo.com.",
                },
            }
        if code == 2007:
            return {
                "success": False,
                "error": {
                    "code": "API_ERROR",
                    "message": f"Account expired (code {code})",
                    "hint": "Renew your subscription at pangolinfo.com.",
                },
            }
        return {
            "success": False,
            "error": {
                "code": "API_ERROR",
                "message": f"API error (code {code}): {msg}",
                "hint": "Retry the request. If persistent, check query/URL format.",
            },
        }

    data = result.get("data", {})
    output = {
        "success": True,
        "task_id": data.get("taskId"),
        "url": data.get("url"),
    }

    json_data = data.get("json")

    if isinstance(json_data, list) and len(json_data) > 0:
        first = json_data[0]
        # New nested format: {metadata, code, data: {results: [...]}}
        if isinstance(first, dict) and "metadata" in first:
            output["metadata"] = first["metadata"]
            inner_data = first.get("data", {})
            results = inner_data.get("results", [])
            output["results"] = results
            output["results_count"] = len(results)
        else:
            # Legacy flat format
            output["results"] = json_data
            output["results_count"] = len(json_data)
    elif isinstance(json_data, dict):
        output["results"] = [json_data]
        output["results_count"] = 1
    else:
        output["results"] = []
        output["results_count"] = 0

    return output


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Pangolin Amazon Scrape API Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  # Product detail by ASIN\n"
            "  python3 scripts/pangolin.py --content B0DYTF8L2W --mode amazon --site amz_us\n"
            "\n"
            "  # Keyword search\n"
            '  python3 scripts/pangolin.py --q "wireless mouse" --mode amazon --site amz_us\n'
            "\n"
            "  # Bestsellers\n"
            '  python3 scripts/pangolin.py --content "electronics" --mode amazon --parser amzBestSellers --site amz_us\n'
            "\n"
            "  # Critical reviews\n"
            "  python3 scripts/pangolin.py --content B00163U4LK --mode review --site amz_us --filter-star critical\n"
            "\n"
            "  # Auth check\n"
            "  python3 scripts/pangolin.py --auth-only\n"
            "\n"
            "Environment variables:\n"
            "  PANGOLIN_API_KEY    API key (skips login)\n"
            "  PANGOLIN_EMAIL      Account email\n"
            "  PANGOLIN_PASSWORD   Account password\n"
            "\n"
            "Amazon parsers:\n"
            "  amzProductDetail       Product detail page\n"
            "  amzKeyword             Keyword search results\n"
            "  amzProductOfCategory   Category listing\n"
            "  amzProductOfSeller     Seller's products\n"
            "  amzBestSellers         Best sellers ranking\n"
            "  amzNewReleases         New releases ranking\n"
            "  amzFollowSeller        Product variants/seller options\n"
            "\n"
            "Amazon sites:\n"
            "  amz_us  amz_uk  amz_ca  amz_de  amz_fr  amz_jp\n"
            "  amz_it  amz_es  amz_au  amz_mx  amz_sa  amz_ae  amz_br"
        ),
    )
    parser.add_argument("--q", dest="query", help="Search query or keyword")
    parser.add_argument(
        "--url",
        dest="target_url",
        help="Target Amazon URL (optional if --site + --content provided)",
    )
    parser.add_argument(
        "--content",
        dest="content",
        help="Content identifier: ASIN, keyword, category Node ID, seller ID, etc.",
    )
    parser.add_argument(
        "--site", "--region",
        dest="site",
        choices=list(AMAZON_SITES.keys()),
        help="Amazon site/region code (e.g. amz_us, amz_uk). Default: amz_us",
    )
    parser.add_argument(
        "--mode",
        choices=["amazon", "review"],
        default="amazon",
        help="API mode: amazon (default) | review",
    )
    parser.add_argument(
        "--parser",
        choices=AMAZON_PARSERS,
        default="amzProductDetail",
        help="Amazon parser name (default: amzProductDetail, auto-inferred when possible)",
    )
    parser.add_argument(
        "--zipcode",
        default="10041",
        help="Amazon zipcode for localized pricing (default: 10041)",
    )
    parser.add_argument(
        "--format",
        dest="fmt",
        choices=["json", "rawHtml", "markdown"],
        default="json",
        help="Amazon response format (default: json)",
    )
    parser.add_argument(
        "--filter-star",
        dest="filter_star",
        choices=REVIEW_STAR_FILTERS,
        default="all_stars",
        help="Review star filter (review mode only): all_stars, critical, positive, five_star, etc.",
    )
    parser.add_argument(
        "--sort-by",
        dest="sort_by",
        choices=REVIEW_SORT_OPTIONS,
        default="recent",
        help="Review sort order (review mode only): recent | helpful",
    )
    parser.add_argument(
        "--pages",
        dest="page_count",
        type=int,
        default=1,
        help="Number of review pages to fetch (review mode only, 5 credits per page)",
    )
    parser.add_argument(
        "--auth-only",
        action="store_true",
        help="Only authenticate and print API key info",
    )
    parser.add_argument(
        "--asin",
        dest="asin",
        help="Amazon ASIN (shortcut for --content <ASIN> --parser amzProductDetail)",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Output raw API response instead of extracted data",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="API request timeout in seconds (default: 120)",
    )

    args = parser.parse_args()

    # --asin is a convenience shortcut
    if args.asin:
        args.content = args.asin.upper()
        if args.parser == "amzProductDetail":
            pass  # already default
        if not args.mode or args.mode == "amazon":
            args.mode = "amazon"

    if args.page_count < 1:
        parser.error("--pages must be at least 1")

    # Auto-detect review mode from input signals
    if args.mode == "amazon":
        if args.parser == "amzReviewV2" or args.filter_star != "all_stars":
            args.mode = "review"

    if not args.query and not args.target_url and not args.content and not args.auth_only:
        parser.error("--q, --url, or --content is required unless using --auth-only")

    api_key = get_api_key()

    if args.auth_only:
        print(
            json.dumps(
                {
                    "success": True,
                    "message": "Authentication successful",
                    "api_key_preview": (
                        f"{api_key[:8]}...{api_key[-4:]}"
                        if len(api_key) > 12
                        else "***"
                    ),
                },
                indent=2,
            )
        )
        sys.exit(EXIT_SUCCESS)

    if args.parser == "amzFollowSeller":
        asin = args.content or args.query
        body = build_follow_seller_body(asin, args.site, args.zipcode)
        endpoint = FOLLOW_SELLER_ENDPOINT
    elif args.mode == "review":
        asin = args.content or args.query
        body = build_review_body(
            asin,
            args.site,
            args.filter_star,
            args.sort_by,
            args.page_count,
            args.fmt,
        )
        endpoint = SCRAPE_V1_ENDPOINT
    else:
        body = build_amazon_body(
            args.target_url,
            args.query,
            args.content,
            args.site,
            args.parser,
            args.zipcode,
            args.fmt,
        )
        endpoint = SCRAPE_V1_ENDPOINT
    result = call_api(api_key, body, endpoint, timeout=args.timeout)

    if result is None:
        _error_exit(
            "NETWORK",
            "API call failed after all retries.",
            hint="Check your internet connection and try again.",
            exit_code=EXIT_NETWORK_ERROR,
        )

    result = handle_response(result, api_key, body, endpoint, timeout=args.timeout)

    if result is None:
        _error_exit(
            "NETWORK",
            "API call failed after API key refresh.",
            hint="Check your internet connection and try again.",
            exit_code=EXIT_NETWORK_ERROR,
        )

    if args.raw:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        output = extract_amazon_output(result)
        print(json.dumps(output, indent=2, ensure_ascii=False))

    if result.get("code") != 0:
        sys.exit(EXIT_API_ERROR)

    sys.exit(EXIT_SUCCESS)


if __name__ == "__main__":
    main()
