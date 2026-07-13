"""Click CLI entry point for discogs-sync."""

from __future__ import annotations

import sys

import click

from .exceptions import AuthenticationError, DiscogsSyncError


def _matches_search(item, query: str) -> bool:
    """Check if search query matches item's artist, title, or year (case-insensitive substring)."""
    q = query.lower()
    artist = (item.artist or "").lower()
    title = (item.title or "").lower()
    year = str(item.year) if getattr(item, "year", None) else ""
    return q in artist or q in title or q in year


@click.group()
@click.version_option(package_name="discogs-sync")
def main():
    """Discogs Sync - synchronize wantlists, collections, and search marketplace."""


# ── Auth commands ──────────────────────────────────────────────────────────


@main.command()
@click.option("--mode", type=click.Choice(["token", "oauth"]), default="token",
              help="Auth method: 'token' for personal access token (default), 'oauth' for OAuth 1.0a flow")
def auth(mode):
    """Authenticate with Discogs.

    Default mode uses a personal access token (generate at discogs.com/settings/developers).
    Use --mode oauth for the full OAuth 1.0a flow with consumer key/secret.
    """
    from .output import console, print_error

    try:
        if mode == "token":
            from .auth import run_token_auth_flow
            result = run_token_auth_flow()
        else:
            from .auth import run_auth_flow
            result = run_auth_flow()
        username = result.get("username", "unknown")
        console.print(f"[green]Authenticated successfully as {username}[/green]")
    except AuthenticationError as e:
        print_error(str(e))
        sys.exit(2)


@main.command()
@click.option("--output-format", type=click.Choice(["table", "json"]), default="table")
def whoami(output_format):
    """Show authenticated user."""
    from .client_factory import build_client
    from .output import output_user_info, print_error
    from .rate_limiter import get_rate_limiter
    from .search import _api_call_with_retry

    try:
        client = build_client()
        limiter = get_rate_limiter()
        identity = _api_call_with_retry(lambda: client.identity(), limiter)
        output_user_info(identity.username, output_format)
    except DiscogsSyncError as e:
        print_error(str(e))
        sys.exit(2)


# ── Wantlist commands ──────────────────────────────────────────────────────


@main.group()
def wantlist():
    """Manage Discogs wantlist."""


@wantlist.command("sync")
@click.argument("file", type=click.Path(exists=True))
@click.option("--remove-extras", is_flag=True, help="Remove wantlist items not in input file")
@click.option("--dry-run", is_flag=True, help="Show what would be done without making changes")
@click.option("--threshold", type=float, default=0.7, help="Match score threshold (0.0-1.0)")
@click.option("--verbose", is_flag=True, help="Print debug information during sync")
@click.option("--output-format", type=click.Choice(["table", "json"]), default="table")
def wantlist_sync(file, remove_extras, dry_run, threshold, verbose, output_format):
    """Batch sync wantlist from CSV/JSON file."""
    from .client_factory import build_client
    from .output import output_sync_report, print_error
    from .parsers import parse_file
    from .sync_wantlist import sync_wantlist

    try:
        records = parse_file(file)
        client = build_client()
        report = sync_wantlist(client, records, remove_extras=remove_extras, dry_run=dry_run, threshold=threshold, verbose=verbose)
        output_sync_report(report, output_format)
        from .cache import invalidate_cache
        invalidate_cache("wantlist")
        sys.exit(report.exit_code)
    except DiscogsSyncError as e:
        print_error(str(e))
        sys.exit(2)


@wantlist.command("add")
@click.option("--artist", help="Artist name")
@click.option("--album", help="Album title")
@click.option("--format", "fmt", help="Format (Vinyl, CD, Cassette)")
@click.option("--master-id", type=int, help="Discogs master ID")
@click.option("--release-id", type=int, help="Discogs release ID")
@click.option("--threshold", type=float, default=0.7, help="Match score threshold")
@click.option("--output-format", type=click.Choice(["table", "json"]), default="table")
def wantlist_add(artist, album, fmt, master_id, release_id, threshold, output_format):
    """Add a release to the wantlist."""
    from .client_factory import build_client
    from .output import output_sync_report, print_error
    from .models import SyncReport
    from .sync_wantlist import add_to_wantlist

    if not release_id and not master_id and not (artist and album):
        print_error("Provide --release-id, --master-id, or both --artist and --album")
        sys.exit(2)

    try:
        client = build_client()
        action = add_to_wantlist(
            client, release_id=release_id, master_id=master_id,
            artist=artist, album=album, format=fmt, threshold=threshold,
        )
        report = SyncReport(total_input=1)
        report.add_action(action)
        output_sync_report(report, output_format)
        from .cache import invalidate_cache
        invalidate_cache("wantlist")
        sys.exit(report.exit_code)
    except DiscogsSyncError as e:
        print_error(str(e))
        sys.exit(2)


@wantlist.command("remove")
@click.option("--artist", help="Artist name")
@click.option("--album", help="Album title")
@click.option("--release-id", type=int, help="Discogs release ID")
@click.option("--threshold", type=float, default=0.7, help="Match score threshold")
@click.option("--output-format", type=click.Choice(["table", "json"]), default="table")
def wantlist_remove(artist, album, release_id, threshold, output_format):
    """Remove a release from the wantlist."""
    from .client_factory import build_client
    from .output import output_sync_report, print_error
    from .models import SyncReport
    from .sync_wantlist import remove_from_wantlist

    if not release_id and not (artist and album):
        print_error("Provide --release-id or both --artist and --album")
        sys.exit(2)

    try:
        client = build_client()
        action = remove_from_wantlist(
            client, release_id=release_id, artist=artist, album=album, threshold=threshold,
        )
        report = SyncReport(total_input=1)
        report.add_action(action)
        output_sync_report(report, output_format)
        from .cache import invalidate_cache
        invalidate_cache("wantlist")
        sys.exit(report.exit_code)
    except DiscogsSyncError as e:
        print_error(str(e))
        sys.exit(2)


@wantlist.command("list")
@click.option("--search", default=None, help="Filter by artist or title (case-insensitive)")
@click.option("--format", "fmt", default=None, help="Filter by format (e.g., Vinyl, CD, Cassette)")
@click.option("--year", type=int, default=None, help="Filter by release year")
@click.option("--no-cache", is_flag=True, default=False, help="Bypass cache and fetch fresh data (cache is still updated)")
@click.option("--output-format", type=click.Choice(["table", "json"]), default="table")
def wantlist_list(search, fmt, year, no_cache, output_format):
    """List all wantlist items."""
    from .cache import read_cache, write_cache
    from .client_factory import build_client
    from .models import WantlistItem
    from .output import output_wantlist, print_error
    from .sync_wantlist import list_wantlist

    try:
        items = None
        if not no_cache:
            cached = read_cache("wantlist")
            if cached is not None:
                items = [WantlistItem.from_dict(d) for d in cached]
        if items is None:
            client = build_client()
            items = list_wantlist(client)
            write_cache("wantlist", [i.to_dict() for i in items])
        if search:
            items = [i for i in items if _matches_search(i, search)]
        if fmt:
            from .parsers import normalize_format
            normalized = normalize_format(fmt)
            items = [i for i in items if (i.format or "").lower() == normalized.lower()]
        if year:
            items = [i for i in items if i.year == year]
        items.sort(key=lambda i: ((i.artist or "").lower(), (i.title or "").lower()))
        output_wantlist(items, output_format)
    except DiscogsSyncError as e:
        print_error(str(e))
        sys.exit(2)


# ── Collection commands ────────────────────────────────────────────────────


@main.group()
def collection():
    """Manage Discogs collection."""


@collection.command("sync")
@click.argument("file", type=click.Path(exists=True))
@click.option("--folder-id", type=int, default=1, help="Target folder ID (default: 1 Uncategorized)")
@click.option("--remove-extras", is_flag=True, help="Remove collection items not in input file")
@click.option("--dry-run", is_flag=True, help="Show what would be done without making changes")
@click.option("--threshold", type=float, default=0.7, help="Match score threshold (0.0-1.0)")
@click.option("--verbose", is_flag=True, help="Print debug information during sync")
@click.option("--output-format", type=click.Choice(["table", "json"]), default="table")
def collection_sync(file, folder_id, remove_extras, dry_run, threshold, verbose, output_format):
    """Batch sync collection from CSV/JSON file."""
    from .client_factory import build_client
    from .output import output_sync_report, print_error
    from .parsers import parse_file
    from .sync_collection import sync_collection

    try:
        records = parse_file(file)
        client = build_client()
        report = sync_collection(
            client, records, folder_id=folder_id,
            remove_extras=remove_extras, dry_run=dry_run, threshold=threshold,
            verbose=verbose,
        )
        output_sync_report(report, output_format)
        from .cache import invalidate_cache
        invalidate_cache("collection")
        sys.exit(report.exit_code)
    except DiscogsSyncError as e:
        print_error(str(e))
        sys.exit(2)


@collection.command("add")
@click.option("--artist", help="Artist name")
@click.option("--album", help="Album title")
@click.option("--format", "fmt", help="Format (Vinyl, CD, Cassette)")
@click.option("--master-id", type=int, help="Discogs master ID")
@click.option("--release-id", type=int, help="Discogs release ID")
@click.option("--folder-id", type=int, default=1, help="Target folder ID")
@click.option("--allow-duplicate", is_flag=True, help="Allow adding duplicate copies")
@click.option("--threshold", type=float, default=0.7, help="Match score threshold")
@click.option("--output-format", type=click.Choice(["table", "json"]), default="table")
def collection_add(artist, album, fmt, master_id, release_id, folder_id, allow_duplicate, threshold, output_format):
    """Add a release to the collection."""
    from .client_factory import build_client
    from .output import output_sync_report, print_error
    from .models import SyncReport
    from .sync_collection import add_to_collection

    if not release_id and not master_id and not (artist and album):
        print_error("Provide --release-id, --master-id, or both --artist and --album")
        sys.exit(2)

    try:
        client = build_client()
        action = add_to_collection(
            client, release_id=release_id, master_id=master_id,
            artist=artist, album=album, format=fmt,
            folder_id=folder_id, allow_duplicate=allow_duplicate, threshold=threshold,
        )
        report = SyncReport(total_input=1)
        report.add_action(action)
        output_sync_report(report, output_format)
        from .cache import invalidate_cache
        invalidate_cache("collection")
        sys.exit(report.exit_code)
    except DiscogsSyncError as e:
        print_error(str(e))
        sys.exit(2)


@collection.command("remove")
@click.option("--artist", help="Artist name")
@click.option("--album", help="Album title")
@click.option("--release-id", type=int, help="Discogs release ID")
@click.option("--threshold", type=float, default=0.7, help="Match score threshold")
@click.option("--output-format", type=click.Choice(["table", "json"]), default="table")
def collection_remove(artist, album, release_id, threshold, output_format):
    """Remove a release from the collection."""
    from .client_factory import build_client
    from .output import output_sync_report, print_error
    from .models import SyncReport
    from .sync_collection import remove_from_collection

    if not release_id and not (artist and album):
        print_error("Provide --release-id or both --artist and --album")
        sys.exit(2)

    try:
        client = build_client()
        action = remove_from_collection(
            client, release_id=release_id, artist=artist, album=album, threshold=threshold,
        )
        report = SyncReport(total_input=1)
        report.add_action(action)
        output_sync_report(report, output_format)
        from .cache import invalidate_cache
        invalidate_cache("collection")
        sys.exit(report.exit_code)
    except DiscogsSyncError as e:
        print_error(str(e))
        sys.exit(2)


@collection.command("list")
@click.option("--search", default=None, help="Filter by artist or title (case-insensitive)")
@click.option("--format", "fmt", default=None, help="Filter by format (e.g., Vinyl, CD, Cassette)")
@click.option("--year", type=int, default=None, help="Filter by release year")
@click.option("--folder-id", type=int, default=0, help="Folder ID (default: 0 All)")
@click.option("--no-cache", is_flag=True, default=False, help="Bypass cache and fetch fresh data (cache is still updated)")
@click.option("--output-format", type=click.Choice(["table", "json"]), default="table")
def collection_list(search, fmt, year, folder_id, no_cache, output_format):
    """List collection items."""
    from .cache import read_cache, write_cache
    from .client_factory import build_client
    from .models import CollectionItem
    from .output import output_collection, print_error
    from .sync_collection import list_collection

    try:
        items = None
        is_cacheable = folder_id == 0
        if is_cacheable and not no_cache:
            cached = read_cache("collection")
            if cached is not None:
                items = [CollectionItem.from_dict(d) for d in cached]
        if items is None:
            client = build_client()
            items = list_collection(client, folder_id=folder_id)
            if is_cacheable:
                write_cache("collection", [i.to_dict() for i in items])
        if search:
            items = [i for i in items if _matches_search(i, search)]
        if fmt:
            from .parsers import normalize_format
            normalized = normalize_format(fmt)
            items = [i for i in items if (i.format or "").lower() == normalized.lower()]
        if year:
            items = [i for i in items if i.year == year]
        items.sort(key=lambda i: ((i.artist or "").lower(), (i.title or "").lower()))
        output_collection(items, output_format)
    except DiscogsSyncError as e:
        print_error(str(e))
        sys.exit(2)


# ── Marketplace commands ───────────────────────────────────────────────────


@main.group()
def marketplace():
    """Search Discogs marketplace."""


@marketplace.command("search")
@click.argument("file", required=False, type=click.Path(exists=True))
@click.option("--artist", help="Artist name")
@click.option("--album", help="Album title")
@click.option("--format", "fmt", help="Format filter (Vinyl, CD)")
@click.option("--country", help="Country filter (exact match: US, UK, Germany, etc.)")
@click.option("--master-id", type=int, help="Discogs master ID")
@click.option("--release-id", type=int, help="Discogs release ID (drill down to specific release)")
@click.option("--min-price", type=float, help="Minimum price filter")
@click.option("--max-price", type=float, help="Maximum price filter")
@click.option("--currency", default="USD", help="Currency code (default: USD)")
@click.option("--max-versions", type=int, default=25, help="Max versions to check per master")
@click.option("--threshold", type=float, default=0.7, help="Match score threshold")
@click.option("--details", is_flag=True, help="Include suggested prices by condition grade")
@click.option("--verbose", is_flag=True, help="Show detailed progress")
@click.option("--no-cache", is_flag=True, default=False, help="Bypass cache and fetch fresh data (cache is still updated)")
@click.option("--output-format", type=click.Choice(["table", "json"]), default="table")
def marketplace_search(file, artist, album, fmt, country, master_id, release_id, min_price, max_price, currency, max_versions, threshold, details, verbose, no_cache, output_format):
    """Search marketplace pricing.

    Provide a CSV/JSON file for batch search, or use --artist/--album, --master-id, or --release-id for individual search.
    Batch file mode always fetches live. Single-item searches are cached for 1 hour.
    """
    from .cache import marketplace_cache_name, read_cache, write_cache, read_resolve_cache, write_resolve_cache
    from .client_factory import build_client
    from .models import MarketplaceResult
    from .output import output_marketplace, print_error, print_warning
    from .marketplace import search_marketplace, search_marketplace_batch

    if not file and not master_id and not release_id and not (artist and album):
        print_error("Provide a file, --master-id, --release-id, or both --artist and --album")
        sys.exit(2)

    try:
        if file:
            # Batch mode — no caching
            client = build_client()
            from .parsers import parse_file
            records = parse_file(file)
            results, errors = search_marketplace_batch(
                client, records, format=fmt, country=country, min_price=min_price,
                max_price=max_price, currency=currency, max_versions=max_versions,
                threshold=threshold, details=details, verbose=verbose,
            )
            for err in errors:
                print_warning(f"{err['artist']} - {err['album']}: {err['error']}")
        else:
            # Single-item mode — cache is split into two layers:
            #   base_name   : results without price_suggestions (always written)
            #   details_name: results with price_suggestions (written when --details)
            # min_price/max_price are post-fetch filters and are not part of the key.
            #
            # For artist+album searches, the cache key is deferred: we first
            # check a lightweight resolution cache that maps (artist, album) →
            # master/release ID, then use the same key as a direct --master-id
            # or --release-id lookup.  This ensures both access patterns share
            # one cache entry.
            is_artist_album = not release_id and not master_id
            if release_id and not master_id:
                base_name = marketplace_cache_name("release", release_id, currency)
            elif master_id:
                base_name = marketplace_cache_name("master", master_id, fmt, country, currency, max_versions)
            else:
                # Artist+album: check resolution cache to get a master/release key
                base_name = None
                if not no_cache:
                    resolved = read_resolve_cache(artist, album, threshold)
                    if resolved:
                        mid = resolved.get("master_id")
                        rid = resolved.get("release_id")
                        if mid:
                            base_name = marketplace_cache_name("master", mid, fmt, country, currency, max_versions)
                        elif rid:
                            base_name = marketplace_cache_name("release", rid, currency)

            details_name = f"{base_name}_details" if base_name else None

            results = None
            client = None  # lazily initialised

            if not no_cache and base_name:
                if details:
                    # Try details cache first (has price_suggestions already merged)
                    cached = read_cache(details_name)
                    if cached is not None:
                        results = [MarketplaceResult.from_dict(d) for d in cached]

                if results is None:
                    # Try base cache
                    cached = read_cache(base_name)
                    if cached is not None:
                        results = [MarketplaceResult.from_dict(d) for d in cached]
                        if details:
                            # Fetch only price_suggestions for the cached releases
                            from .marketplace import fetch_price_suggestions_for_results
                            client = build_client()
                            ps_map = fetch_price_suggestions_for_results(client, results, verbose=verbose)
                            for r in results:
                                if r.release_id is not None:
                                    r.price_suggestions = ps_map.get(r.release_id)
                            write_cache(details_name, [r.to_dict() for r in results])

            if results is None:
                if client is None:
                    client = build_client()
                results = search_marketplace(
                    client, master_id=master_id, release_id=release_id, artist=artist, album=album,
                    format=fmt, country=country, min_price=min_price, max_price=max_price,
                    currency=currency, max_versions=max_versions, threshold=threshold,
                    details=details, verbose=verbose,
                )

                # Determine cache key post-hoc for artist+album searches
                if is_artist_album and base_name is None and results:
                    mid = results[0].master_id
                    rid = results[0].release_id
                    if mid:
                        base_name = marketplace_cache_name("master", mid, fmt, country, currency, max_versions)
                    elif rid:
                        base_name = marketplace_cache_name("release", rid, currency)
                    # Save resolution mapping for future lookups
                    write_resolve_cache(artist, album, threshold, mid, rid)
                    details_name = f"{base_name}_details" if base_name else None

                # Always save base results (price_suggestions stripped)
                if base_name:
                    base_dicts = [{k: v for k, v in r.to_dict().items() if k != "price_suggestions"} for r in results]
                    write_cache(base_name, base_dicts)
                    if details:
                        details_name = details_name or f"{base_name}_details"
                        write_cache(details_name, [r.to_dict() for r in results])

        output_marketplace(results, output_format, details=details)
    except DiscogsSyncError as e:
        print_error(str(e))
        sys.exit(2)


# ── Cache management ───────────────────────────────────────────────────────


@main.group()
def cache():
    """Manage local cache files."""


@cache.command("clean")
def cache_clean():
    """Remove expired cache files.

    Deletes any cache file whose TTL has elapsed, freeing disk space without
    discarding results that are still valid.
    """
    from .cache import cleanup_expired_caches
    from .output import error_console

    n = cleanup_expired_caches()
    if n:
        error_console.print(f"Removed {n} expired cache file(s).")
    else:
        error_console.print("No expired cache files found.")


@cache.command("purge")
def cache_purge():
    """Remove all cache files.

    Unconditionally deletes every cache file so the next command fetches
    fresh data from the Discogs API.
    """
    from .cache import purge_all_caches
    from .output import error_console

    n = purge_all_caches()
    if n:
        error_console.print(f"Removed {n} cache file(s).")
    else:
        error_console.print("No cache files found.")


if __name__ == "__main__":
    main()
