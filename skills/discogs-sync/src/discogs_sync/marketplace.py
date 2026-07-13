"""Marketplace stats lookup via master versions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .exceptions import SyncError
from .models import InputRecord, MarketplaceResult
from .output import print_verbose
from .parsers import extract_artist_from_data
from .rate_limiter import get_rate_limiter
from .search import (
    _api_call_with_retry,
    resolve_to_release_id,
    search_release,
)

if TYPE_CHECKING:
    import discogs_client

DEFAULT_MAX_VERSIONS = 25


def _extract_lowest_price(stats) -> float | None:
    """Extract lowest_price as a float from marketplace stats.

    Handles the various forms the Discogs API may return:
    - MarketplaceStats object with a Price object (has .value)
    - Price object wrapping a raw numeric .data (no .value)
    - Plain dict
    - Raw number
    """
    lp = None
    if hasattr(stats, "lowest_price"):
        lp = stats.lowest_price
    elif isinstance(stats, dict):
        lp = stats.get("lowest_price")

    if lp is None:
        return None

    if hasattr(lp, "value"):
        return float(lp.value)
    if isinstance(lp, dict):
        return float(lp.get("value", 0))
    if isinstance(lp, (int, float)):
        return float(lp)
    if hasattr(lp, "data") and isinstance(lp.data, (int, float)):
        return float(lp.data)
    return float(str(lp))

# Module-level flag to skip price_suggestions after a "seller settings" 404.
# Reset at the start of each search_marketplace call.
_skip_price_suggestions = False


def _extract_price_suggestions(release, limiter, verbose: bool = False) -> dict[str, float] | None:
    """Fetch price suggestions by condition grade for a release.

    Returns dict like {"Mint (M)": 50.0, "Near Mint (NM or M-)": 40.0, ...}
    or None on failure. Keys match the Discogs API condition grade names.
    """
    # Map from PriceSuggestions property names to API key names
    _GRADE_ATTRS = {
        "mint": "Mint (M)",
        "near_mint": "Near Mint (NM or M-)",
        "very_good_plus": "Very Good Plus (VG+)",
        "very_good": "Very Good (VG)",
        "good_plus": "Good Plus (G+)",
        "good": "Good (G)",
        "fair": "Fair (F)",
        "poor": "Poor (P)",
    }

    global _skip_price_suggestions

    release_id = getattr(release, "id", None) or (release.data.get("id") if hasattr(release, "data") else "?")

    if _skip_price_suggestions:
        if verbose:
            print_verbose(f"  price_suggestions for release {release_id}: skipped (seller settings not configured)")
        return None

    try:
        suggestions = _api_call_with_retry(lambda: release.price_suggestions, limiter, verbose=verbose, description=f"release({release_id}).price_suggestions")
        if not suggestions:
            if verbose:
                print_verbose(f"  price_suggestions for release {release_id}: returned empty/None")
            return None

        if verbose:
            print_verbose(f"  price_suggestions for release {release_id}: type={type(suggestions).__name__}")

        result: dict[str, float] = {}

        # PriceSuggestions object: access via named properties
        for attr, grade_key in _GRADE_ATTRS.items():
            price_obj = getattr(suggestions, attr, None)
            if price_obj is not None:
                if hasattr(price_obj, "value") and price_obj.value is not None:
                    result[grade_key] = float(price_obj.value)
                elif isinstance(price_obj, (int, float)):
                    result[grade_key] = float(price_obj)

        # Fallback: if it's a plain dict (e.g. from mocks)
        if not result and isinstance(suggestions, dict):
            for grade, price_obj in suggestions.items():
                if isinstance(price_obj, dict):
                    val = price_obj.get("value")
                    if val is not None:
                        result[grade] = float(val)
                elif hasattr(price_obj, "value") and price_obj.value is not None:
                    result[grade] = float(price_obj.value)
                elif isinstance(price_obj, (int, float)):
                    result[grade] = float(price_obj)

        if verbose:
            if result:
                print_verbose(f"  price_suggestions for release {release_id}: {len(result)} grades extracted")
            else:
                print_verbose(f"  price_suggestions for release {release_id}: no grades could be extracted from {type(suggestions).__name__}")

        return result if result else None
    except Exception as e:
        if verbose:
            print_verbose(f"  price_suggestions for release {release_id}: error - {e}")
        if "seller settings" in str(e).lower():
            _skip_price_suggestions = True
            if verbose:
                print_verbose("  Disabling price_suggestions for remaining releases (seller settings not configured)")
        return None


def search_marketplace(
    client: discogs_client.Client,
    master_id: int | None = None,
    release_id: int | None = None,
    artist: str | None = None,
    album: str | None = None,
    format: str | None = None,
    country: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    currency: str = "USD",
    max_versions: int = DEFAULT_MAX_VERSIONS,
    threshold: float = 0.7,
    details: bool = False,
    verbose: bool = False,
) -> list[MarketplaceResult]:
    """Search marketplace stats for a single item.

    Resolves to master_id, fetches versions, gets stats for each.
    """
    global _skip_price_suggestions
    _skip_price_suggestions = False
    limiter = get_rate_limiter()

    # If release_id explicitly provided (without master_id), show only that release
    if release_id and not master_id:
        return _get_stats_for_release(client, release_id, currency, min_price, max_price, limiter, details=details, verbose=verbose)

    # Resolve to master_id
    if not master_id:
        if artist and album:
            record = InputRecord(artist=artist, album=album, format=format)
            result = search_release(client, record, threshold=threshold)
            if not result.matched:
                raise SyncError(f"No match found for {artist} - {album}")
            master_id = result.master_id
            if not master_id and result.release_id:
                release = _api_call_with_retry(lambda: client.release(result.release_id), limiter, verbose=verbose, description=f"release({result.release_id})")
                _api_call_with_retry(lambda: release.refresh(), limiter, verbose=verbose, description=f"release({result.release_id}).refresh()")
                data = release.data if hasattr(release, "data") else {}
                if verbose:
                    print_verbose(f"Fetched release {result.release_id}: keys={list(data.keys())}")
                master_id = data.get("master_id")
            if not master_id:
                # Fall back to single release stats
                rid = resolve_to_release_id(client, result)
                if rid:
                    return _get_stats_for_release(client, rid, currency, min_price, max_price, limiter, details=details, verbose=verbose)
                raise SyncError(f"Could not resolve master or release for {artist} - {album}")
        else:
            raise SyncError("Must provide --master-id, --release-id, or both --artist and --album")

    # Fetch master versions
    if verbose:
        print_verbose(f"Fetching versions for master_id={master_id}")
    master = _api_call_with_retry(lambda: client.master(master_id), limiter, verbose=verbose, description=f"master({master_id})")
    if verbose:
        print_verbose(f"Fetching versions list for master_id={master_id}")
    versions = _api_call_with_retry(lambda: master.versions, limiter, verbose=verbose, description=f"master({master_id}).versions")
    if verbose:
        # Try to get total count from the versions object
        total_versions = None
        if hasattr(versions, 'pages'):
            total_versions = getattr(versions, 'pages', None)
        if hasattr(versions, 'count'):
            total_versions = getattr(versions, 'count', None)
        print_verbose(f"Versions object: type={type(versions).__name__}, total={total_versions}, max_to_check={max_versions}")

    results: list[MarketplaceResult] = []
    count = 0
    page_num = 1

    while count < max_versions:
        if verbose:
            print_verbose(f"Fetching versions page {page_num} (matched {count}/{max_versions} so far)")
        try:
            page = _api_call_with_retry(lambda p=page_num: versions.page(p), limiter, verbose=verbose, description=f"versions.page({page_num})")
            if not page:
                if verbose:
                    print_verbose(f"Page {page_num} returned empty, stopping")
                break
        except Exception as e:
            if verbose:
                print_verbose(f"Page {page_num} fetch failed: {e}, stopping")
            break

        if verbose:
            page_len = len(page) if hasattr(page, '__len__') else '?'
            print_verbose(f"Page {page_num} returned {page_len} versions")

        for version in page:
            if count >= max_versions:
                break

            data = version.data if hasattr(version, "data") else {}
            version_id = data.get("id") or getattr(version, "id", None)
            if not version_id:
                continue

            # Filter by format if specified
            if format:
                version_formats = data.get("major_formats", [])
                if not version_formats:
                    fmt_str = data.get("format", "")
                    version_formats = [fmt_str] if fmt_str else []
                if not any(format.lower() in str(f).lower() for f in version_formats):
                    if verbose:
                        print_verbose(f"  Skipping version {version_id}: formats {version_formats} don't match '{format}'")
                    continue

            # Filter by country if specified
            if country:
                version_country = data.get("country", "")
                if not version_country or country.lower() != version_country.lower():
                    if verbose:
                        print_verbose(f"  Skipping version {version_id}: country '{version_country}' doesn't match '{country}'")
                    continue

            # Get marketplace stats
            try:
                if verbose:
                    print_verbose(f"  Fetching release {version_id}...")
                release = _api_call_with_retry(lambda vid=version_id: client.release(vid), limiter, verbose=verbose, description=f"release({version_id})")
                # Force full data load — client.release() creates a lazy object
                _api_call_with_retry(lambda r=release: r.refresh(), limiter, verbose=verbose, description=f"release({version_id}).refresh()")
                release_data = release.data if hasattr(release, "data") else {}
                if verbose:
                    print_verbose(f"  Release {version_id}: data keys={list(release_data.keys())}, "
                                  f"artist={'artists' in release_data}, country={release_data.get('country', '<missing>')}")
                stats = _api_call_with_retry(lambda r=release: r.marketplace_stats, limiter, verbose=verbose, description=f"release({version_id}).marketplace_stats")

                num_for_sale = 0
                if hasattr(stats, "num_for_sale"):
                    num_for_sale = stats.num_for_sale or 0
                elif isinstance(stats, dict):
                    num_for_sale = stats.get("num_for_sale", 0)

                lowest_price = _extract_lowest_price(stats)

                # Apply price filters
                if min_price is not None and (lowest_price is None or lowest_price < min_price):
                    continue
                if max_price is not None and (lowest_price is None or lowest_price > max_price):
                    continue

                # Parse artist and title
                artist_name = extract_artist_from_data(release_data)
                album_name = release_data.get("title", data.get("title", ""))
                if not artist_name and " - " in album_name:
                    artist_name, album_name = album_name.split(" - ", 1)

                # Parse format
                fmt = None
                formats = release_data.get("formats", [])
                if formats and isinstance(formats, list):
                    fmt = formats[0].get("name", "") if isinstance(formats[0], dict) else str(formats[0])
                if not fmt:
                    fmt = data.get("format", "")

                # Fetch price suggestions if details requested
                price_suggestions = None
                if details:
                    price_suggestions = _extract_price_suggestions(release, limiter, verbose=verbose)

                results.append(MarketplaceResult(
                    master_id=master_id,
                    release_id=version_id,
                    title=album_name,
                    artist=artist_name,
                    format=fmt,
                    country=release_data.get("country", data.get("country")),
                    year=release_data.get("year", data.get("year")),
                    num_for_sale=num_for_sale,
                    lowest_price=lowest_price,
                    currency=currency,
                    price_suggestions=price_suggestions,
                ))

                count += 1

            except Exception as e:
                if verbose:
                    print_verbose(f"  Release {version_id}: error fetching stats - {e}")
                continue

        page_num += 1

    if verbose:
        print_verbose(f"Version scan complete: {count} versions matched across {page_num - 1} pages")

    # Sort by lowest_price ascending (None values at end)
    results.sort(key=lambda r: (r.lowest_price is None, r.lowest_price or 0))

    return results


def fetch_price_suggestions_for_results(
    client: discogs_client.Client,
    results: list[MarketplaceResult],
    verbose: bool = False,
) -> dict[int, dict | None]:
    """Fetch price suggestions for an already-resolved list of marketplace results.

    Used when base results are available from cache but ``price_suggestions``
    have not been fetched yet (i.e. the details cache is cold).

    Args:
        client: Authenticated Discogs client.
        results: List of :class:`MarketplaceResult` whose ``release_id`` values
            are used to look up price suggestions.
        verbose: If ``True``, print progress messages.

    Returns:
        Mapping of ``release_id`` → price-suggestions dict (or ``None`` on
        failure).  Release IDs with no ``release_id`` value are skipped.
    """
    global _skip_price_suggestions
    _skip_price_suggestions = False
    limiter = get_rate_limiter()
    suggestions: dict[int, dict | None] = {}
    for result in results:
        if result.release_id is None:
            continue
        try:
            release = _api_call_with_retry(
                lambda rid=result.release_id: client.release(rid),
                limiter, verbose=verbose, description=f"release({result.release_id})",
            )
            _api_call_with_retry(
                lambda r=release: r.refresh(),
                limiter, verbose=verbose, description=f"release({result.release_id}).refresh()",
            )
            suggestions[result.release_id] = _extract_price_suggestions(release, limiter, verbose=verbose)
        except Exception:
            suggestions[result.release_id] = None
    return suggestions


def search_marketplace_batch(
    client: discogs_client.Client,
    records: list[InputRecord],
    format: str | None = None,
    country: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    currency: str = "USD",
    max_versions: int = DEFAULT_MAX_VERSIONS,
    threshold: float = 0.7,
    details: bool = False,
    verbose: bool = False,
) -> tuple[list[MarketplaceResult], list[dict]]:
    """Search marketplace for a batch of records.

    Returns (results, errors) where errors is a list of error dicts.
    """
    all_results: list[MarketplaceResult] = []
    errors: list[dict] = []

    for record in records:
        try:
            if verbose:
                print_verbose(f"Searching marketplace: {record.artist} - {record.album}")
            results = search_marketplace(
                client,
                artist=record.artist,
                album=record.album,
                format=format or record.format,
                country=country,
                min_price=min_price,
                max_price=max_price,
                currency=currency,
                max_versions=max_versions,
                threshold=threshold,
                details=details,
                verbose=verbose,
            )
            all_results.extend(results)
        except Exception as e:
            errors.append({
                "artist": record.artist,
                "album": record.album,
                "error": str(e),
            })

    return all_results, errors


def _get_stats_for_release(
    client,
    release_id: int,
    currency: str,
    min_price: float | None,
    max_price: float | None,
    limiter,
    details: bool = False,
    verbose: bool = False,
) -> list[MarketplaceResult]:
    """Get marketplace stats for a single release."""
    release = _api_call_with_retry(lambda: client.release(release_id), limiter, verbose=verbose, description=f"release({release_id})")
    # Force full data load — client.release() creates a lazy object
    _api_call_with_retry(lambda: release.refresh(), limiter, verbose=verbose, description=f"release({release_id}).refresh()")
    data = release.data if hasattr(release, "data") else {}
    if verbose:
        print_verbose(f"Fetched release {release_id}: keys={list(data.keys())}, "
                      f"artist={'artists' in data}, country={data.get('country', '<missing>')}")
    stats = _api_call_with_retry(lambda: release.marketplace_stats, limiter, verbose=verbose, description=f"release({release_id}).marketplace_stats")

    num_for_sale = 0
    if hasattr(stats, "num_for_sale"):
        num_for_sale = stats.num_for_sale or 0
    elif isinstance(stats, dict):
        num_for_sale = stats.get("num_for_sale", 0)

    lowest_price = _extract_lowest_price(stats)

    if min_price is not None and (lowest_price is None or lowest_price < min_price):
        return []
    if max_price is not None and (lowest_price is None or lowest_price > max_price):
        return []

    artist_name = extract_artist_from_data(data)
    album_name = data.get("title", "")
    if not artist_name and " - " in album_name:
        artist_name, album_name = album_name.split(" - ", 1)

    fmt = None
    format_details = None
    formats = data.get("formats", [])
    if formats and isinstance(formats, list):
        fmt = formats[0].get("name", "") if isinstance(formats[0], dict) else str(formats[0])
        if isinstance(formats[0], dict):
            descriptions = formats[0].get("descriptions", [])
            if descriptions:
                format_details = ", ".join(descriptions)

    # Extract label and catalog number
    label = None
    catno = None
    labels = data.get("labels", [])
    if labels and isinstance(labels, list) and isinstance(labels[0], dict):
        label = labels[0].get("name")
        catno = labels[0].get("catno")

    # Extract community stats
    community_have = None
    community_want = None
    community = data.get("community", {})
    if isinstance(community, dict):
        community_have = community.get("have")
        community_want = community.get("want")

    price_suggestions = None
    if details:
        price_suggestions = _extract_price_suggestions(release, limiter, verbose=verbose)

    return [MarketplaceResult(
        master_id=data.get("master_id"),
        release_id=release_id,
        title=album_name,
        artist=artist_name,
        format=fmt,
        country=data.get("country"),
        year=data.get("year"),
        num_for_sale=num_for_sale,
        lowest_price=lowest_price,
        currency=currency,
        price_suggestions=price_suggestions,
        label=label,
        catno=catno,
        format_details=format_details,
        community_have=community_have,
        community_want=community_want,
    )]
