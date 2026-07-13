"""Multi-pass release matching: map (artist, album) to Discogs release_id/master_id."""

from __future__ import annotations

import difflib
import time
from typing import TYPE_CHECKING

from .exceptions import NetworkError, SearchError
from .models import InputRecord, SearchResult
from .output import print_info
from .rate_limiter import get_rate_limiter

if TYPE_CHECKING:
    import discogs_client


DEFAULT_THRESHOLD = 0.7
MAX_RETRIES = 3
RETRY_DELAY = 5.0


def search_release(
    client: discogs_client.Client,
    record: InputRecord,
    threshold: float = DEFAULT_THRESHOLD,
) -> SearchResult:
    """Search Discogs for a release matching the input record.

    Uses multi-pass search:
    1. Structured search with all fields
    2. Relaxed search (drop format/year)
    3. Free text search

    Returns the best matching SearchResult.
    """
    limiter = get_rate_limiter()

    # Pass 1: Structured search
    result = _structured_search(client, record, limiter, threshold)
    if result and result.matched:
        return result

    # Pass 2: Relaxed search (drop format and year)
    result = _relaxed_search(client, record, limiter, threshold)
    if result and result.matched:
        return result

    # Pass 3: Free text search
    result = _freetext_search(client, record, limiter, threshold)
    if result and result.matched:
        return result

    return SearchResult(
        input_record=record,
        matched=False,
        error=f"No match found above threshold {threshold}",
    )


def resolve_to_release_id(
    client: discogs_client.Client,
    search_result: SearchResult,
    preferred_format: str | None = None,
) -> int | None:
    """Resolve a SearchResult to a specific release_id.

    If master_id found + format specified: find matching version.
    If master_id found + no format: use main_release.
    If release_id only: return it directly.
    """
    if search_result.release_id and not search_result.master_id:
        return search_result.release_id

    if not search_result.master_id:
        return search_result.release_id

    limiter = get_rate_limiter()
    master = _api_call_with_retry(lambda: client.master(search_result.master_id), limiter)

    fmt = preferred_format or search_result.input_record.format
    if fmt:
        # Try to find a version matching the format
        release_id = _find_version_by_format(client, master, fmt, limiter)
        if release_id:
            return release_id

    # Fall back to main release
    try:
        return master.main_release.id
    except Exception:
        return search_result.release_id


def resolve_master_id(
    client: discogs_client.Client,
    master_id: int,
    preferred_format: str | None = None,
) -> int:
    """Resolve a master_id to a release_id."""
    limiter = get_rate_limiter()
    master = _api_call_with_retry(lambda: client.master(master_id), limiter)

    if preferred_format:
        release_id = _find_version_by_format(client, master, preferred_format, limiter)
        if release_id:
            return release_id

    return master.main_release.id


def _structured_search(
    client: discogs_client.Client,
    record: InputRecord,
    limiter,
    threshold: float,
) -> SearchResult | None:
    """Pass 1: Structured search with all available fields."""
    kwargs: dict = {
        "release_title": record.album,
        "artist": record.artist,
        "type": "master",
    }
    if record.format:
        kwargs["format"] = record.format
    if record.year:
        kwargs["year"] = str(record.year)

    results = _api_call_with_retry(lambda: client.search(**kwargs), limiter)
    return _score_results(results, record, threshold)


def _relaxed_search(
    client: discogs_client.Client,
    record: InputRecord,
    limiter,
    threshold: float,
) -> SearchResult | None:
    """Pass 2: Drop format and year constraints."""
    results = _api_call_with_retry(
        lambda: client.search(
            release_title=record.album,
            artist=record.artist,
            type="master",
        ),
        limiter,
    )
    return _score_results(results, record, threshold)


def _freetext_search(
    client: discogs_client.Client,
    record: InputRecord,
    limiter,
    threshold: float,
) -> SearchResult | None:
    """Pass 3: Free text search as last resort."""
    query = f"{record.artist} {record.album}"
    results = _api_call_with_retry(
        lambda: client.search(query, type="release"),
        limiter,
    )
    return _score_results(results, record, threshold)


def _score_results(results, record: InputRecord, threshold: float) -> SearchResult | None:
    """Score search results and return the best match above threshold."""
    if not results:
        return None

    best_score = 0.0
    best_result = None

    # Only check first page of results (typically 50 items)
    try:
        page = results.page(1)
    except Exception:
        return None

    for item in page:
        score = _compute_score(item, record)
        if score > best_score:
            best_score = score
            best_result = item

    if best_result is None or best_score < threshold:
        return None

    # Extract fields from result
    try:
        artist_name = _get_artist_name(best_result)
        title = getattr(best_result, "title", "") or ""
        # title is often "Artist - Album", extract album part
        if " - " in title:
            title = title.split(" - ", 1)[1]

        master_id = None
        release_id = None

        # Determine IDs based on result type
        if hasattr(best_result, "data"):
            data = best_result.data
            if data.get("type") == "master":
                master_id = data.get("id") or getattr(best_result, "id", None)
            else:
                release_id = data.get("id") or getattr(best_result, "id", None)
                master_id = data.get("master_id")
        else:
            release_id = getattr(best_result, "id", None)

        year = None
        if hasattr(best_result, "data"):
            year = best_result.data.get("year")
        if not year:
            year = getattr(best_result, "year", None)
        if year:
            try:
                year = int(year)
            except (ValueError, TypeError):
                year = None

        fmt = None
        if hasattr(best_result, "data"):
            formats = best_result.data.get("format", [])
            if formats:
                fmt = formats[0] if isinstance(formats, list) else str(formats)

        country = None
        if hasattr(best_result, "data"):
            country = best_result.data.get("country")

        return SearchResult(
            input_record=record,
            release_id=release_id,
            master_id=master_id,
            title=title,
            artist=artist_name,
            year=year,
            format=fmt,
            country=country,
            score=best_score,
            matched=True,
        )
    except Exception as e:
        return SearchResult(
            input_record=record,
            matched=False,
            error=f"Error processing search result: {e}",
        )


def _compute_score(result, record: InputRecord) -> float:
    """Compute a match score (0.0-1.0) for a search result against an input record."""
    score = 0.0

    # Get result artist and title
    result_artist = _get_artist_name(result)
    result_title = getattr(result, "title", "") or ""
    if " - " in result_title:
        result_title = result_title.split(" - ", 1)[1]

    # Artist similarity (40%)
    artist_sim = _similarity(record.artist, result_artist)
    score += 0.4 * artist_sim

    # Album title similarity (40%)
    title_sim = _similarity(record.album, result_title)
    score += 0.4 * title_sim

    # Year match (10%)
    if record.year:
        result_year = None
        if hasattr(result, "data"):
            result_year = result.data.get("year")
        if not result_year:
            result_year = getattr(result, "year", None)
        if result_year:
            try:
                result_year = int(result_year)
                if result_year == record.year:
                    score += 0.1
            except (ValueError, TypeError):
                pass

    # Format match (10%)
    if record.format:
        result_formats = []
        if hasattr(result, "data"):
            fmt_data = result.data.get("format", [])
            if isinstance(fmt_data, list):
                result_formats = [str(f).lower() for f in fmt_data]
            elif fmt_data:
                result_formats = [str(fmt_data).lower()]
        if any(record.format.lower() in f for f in result_formats):
            score += 0.1

    return score


def _get_artist_name(result) -> str:
    """Extract artist name from a search result."""
    if hasattr(result, "data"):
        # Try title field which is "Artist - Album"
        title = result.data.get("title", "")
        if " - " in title:
            return title.split(" - ", 1)[0]
    # Fallback
    title = getattr(result, "title", "") or ""
    if " - " in title:
        return title.split(" - ", 1)[0]
    return ""


def _similarity(a: str, b: str) -> float:
    """Compute normalized string similarity using SequenceMatcher."""
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


def _find_version_by_format(client, master, format_name: str, limiter) -> int | None:
    """Find a version of a master release matching the given format."""
    try:
        versions = _api_call_with_retry(lambda: master.versions, limiter)
        # Check first page of versions
        page = versions.page(1)
        for version in page:
            data = version.data if hasattr(version, "data") else {}
            formats = data.get("major_formats", [])
            if not formats:
                formats = data.get("format", "")
                if isinstance(formats, str):
                    formats = [formats]
            for fmt in formats:
                if format_name.lower() in str(fmt).lower():
                    return data.get("id") or getattr(version, "id", None)
    except Exception:
        pass
    return None


def _api_call_with_retry(call, limiter, retries: int = MAX_RETRIES, verbose: bool = False, description: str = ""):
    """Execute an API call with rate limiting and retries."""
    last_error = None
    desc = f" ({description})" if description else ""
    for attempt in range(retries):
        wait_info = limiter.wait_if_needed(verbose=verbose, description=description)
        try:
            t0 = time.monotonic()
            result = call()
            elapsed = time.monotonic() - t0
            # Try to extract headers for rate limit tracking
            if hasattr(result, "_response") and hasattr(result._response, "headers"):
                limiter.update_from_headers(dict(result._response.headers))
            if verbose and (elapsed > 2.0 or description):
                remaining = limiter.remaining
                from .output import print_verbose
                print_verbose(f"API call{desc}: {elapsed:.1f}s (remaining={remaining})")
            return result
        except Exception as e:
            last_error = e
            if verbose:
                from .output import print_verbose
                print_verbose(f"API call{desc} attempt {attempt + 1}/{retries} failed: {e}")
            if attempt < retries - 1:
                if verbose:
                    from .output import print_verbose
                    print_verbose(f"  Retrying in {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
    raise NetworkError(f"API call failed after {retries} retries: {last_error}") from last_error
