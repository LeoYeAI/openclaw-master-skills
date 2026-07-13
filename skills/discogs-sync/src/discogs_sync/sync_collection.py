"""Collection sync operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .exceptions import SyncError
from .models import (
    CollectionItem,
    InputRecord,
    SearchResult,
    SyncAction,
    SyncActionType,
    SyncReport,
)
from .output import print_verbose
from .parsers import extract_artist_from_data
from .rate_limiter import get_rate_limiter
from .search import (
    _api_call_with_retry,
    _similarity,
    resolve_master_id,
    resolve_to_release_id,
    search_release,
)

if TYPE_CHECKING:
    import discogs_client

DEFAULT_ADD_FOLDER = 1   # "Uncategorized"
DEFAULT_READ_FOLDER = 0  # "All"
FUZZY_MATCH_THRESHOLD = 0.85


def sync_collection(
    client: discogs_client.Client,
    records: list[InputRecord],
    folder_id: int = DEFAULT_ADD_FOLDER,
    remove_extras: bool = False,
    dry_run: bool = False,
    threshold: float = 0.7,
    verbose: bool = False,
) -> SyncReport:
    """Sync a list of input records to the user's collection."""
    report = SyncReport(total_input=len(records))
    limiter = get_rate_limiter()

    if verbose:
        print_verbose(f"Starting collection sync: {len(records)} input records, folder_id={folder_id}, threshold={threshold}, dry_run={dry_run}, remove_extras={remove_extras}")

    # Step 1: Resolve all records
    resolved: list[tuple[InputRecord, SearchResult]] = []
    for i, record in enumerate(records, 1):
        if verbose:
            print_verbose(f"[{i}/{len(records)}] Searching: {record.artist} - {record.album}" + (f" [{record.format}]" if record.format else ""))
        try:
            result = search_release(client, record, threshold=threshold)
            if result.matched:
                if verbose:
                    print_verbose(f"  Matched: {result.artist} - {result.title} (score={result.score:.2f}, master_id={result.master_id}, release_id={result.release_id})")
                release_id = resolve_to_release_id(client, result)
                if release_id:
                    if verbose and release_id != result.release_id:
                        print_verbose(f"  Resolved to release_id={release_id}")
                    result.release_id = release_id
                    resolved.append((record, result))
                else:
                    if verbose:
                        print_verbose(f"  Failed to resolve to release ID")
                    report.add_action(SyncAction(
                        action=SyncActionType.ERROR,
                        input_record=record,
                        error="Could not resolve to release ID",
                    ))
            else:
                if verbose:
                    print_verbose(f"  No match: {result.error or 'below threshold'}")
                report.add_action(SyncAction(
                    action=SyncActionType.ERROR,
                    input_record=record,
                    error=result.error or "No match found",
                ))
        except Exception as e:
            if verbose:
                print_verbose(f"  Error: {e}")
            report.add_action(SyncAction(
                action=SyncActionType.ERROR,
                input_record=record,
                error=str(e),
            ))

    if verbose:
        print_verbose(f"Resolved {len(resolved)}/{len(records)} records")

    # Step 2: Fetch current collection
    if verbose:
        print_verbose("Fetching current collection...")
    current, current_masters, current_items = _get_collection_release_ids(client, DEFAULT_READ_FOLDER, limiter)
    if verbose:
        print_verbose(f"Current collection has {len(current)} unique releases, {len(current_masters)} unique masters")

    # Step 3: Diff
    target_ids = set()
    for record, result in resolved:
        release_id = result.release_id
        target_ids.add(release_id)

        if release_id in current:
            if verbose:
                print_verbose(f"  SKIP (release_id match): {result.artist} - {result.title} (release_id={release_id})")
            report.add_action(SyncAction(
                action=SyncActionType.SKIP,
                input_record=record,
                release_id=release_id,
                master_id=result.master_id,
                title=result.title,
                artist=result.artist,
                reason="Already in collection",
            ))
        elif result.master_id and result.master_id in current_masters:
            if verbose:
                print_verbose(f"  SKIP (master_id match): {result.artist} - {result.title} (master_id={result.master_id})")
            report.add_action(SyncAction(
                action=SyncActionType.SKIP,
                input_record=record,
                release_id=release_id,
                master_id=result.master_id,
                title=result.title,
                artist=result.artist,
                reason="Already in collection",
            ))
        elif _fuzzy_match_items(result.artist, result.title, current_items, verbose):
            report.add_action(SyncAction(
                action=SyncActionType.SKIP,
                input_record=record,
                release_id=release_id,
                master_id=result.master_id,
                title=result.title,
                artist=result.artist,
                reason="Already in collection (fuzzy match)",
            ))
        else:
            if verbose:
                print_verbose(f"  ADD: release_id={release_id} not in collection, master_id={result.master_id} not in masters, no fuzzy match")
            if not dry_run:
                try:
                    if verbose:
                        print_verbose(f"  ADD: {result.artist} - {result.title} (release_id={release_id}) to folder {folder_id}")
                    _add_to_collection(client, release_id, folder_id, limiter)
                except Exception as e:
                    if verbose:
                        print_verbose(f"  ERROR adding release_id={release_id}: {e}")
                    report.add_action(SyncAction(
                        action=SyncActionType.ERROR,
                        input_record=record,
                        release_id=release_id,
                        error=f"Failed to add: {e}",
                    ))
                    continue
            elif verbose:
                print_verbose(f"  ADD (dry run): {result.artist} - {result.title} (release_id={release_id})")

            report.add_action(SyncAction(
                action=SyncActionType.ADD,
                input_record=record,
                release_id=release_id,
                master_id=result.master_id,
                title=result.title,
                artist=result.artist,
                reason="Dry run" if dry_run else None,
            ))

    # Step 4: Remove extras
    if remove_extras:
        extras = set(current.keys()) - target_ids
        if verbose:
            print_verbose(f"Checking extras: {len(extras)} releases in collection not in input")
        for release_id in extras:
            instance_ids = current[release_id]
            for instance_id in instance_ids:
                if not dry_run:
                    try:
                        if verbose:
                            print_verbose(f"  REMOVE: release_id={release_id}, instance_id={instance_id}")
                        _remove_from_collection(client, release_id, instance_id, DEFAULT_READ_FOLDER, limiter)
                    except Exception as e:
                        if verbose:
                            print_verbose(f"  ERROR removing release_id={release_id} instance={instance_id}: {e}")
                        report.add_action(SyncAction(
                            action=SyncActionType.ERROR,
                            release_id=release_id,
                            error=f"Failed to remove instance {instance_id}: {e}",
                        ))
                        continue
                elif verbose:
                    print_verbose(f"  REMOVE (dry run): release_id={release_id}, instance_id={instance_id}")

                report.add_action(SyncAction(
                    action=SyncActionType.REMOVE,
                    release_id=release_id,
                    reason="Not in input file" + (" (dry run)" if dry_run else ""),
                ))

    return report


def add_to_collection(
    client: discogs_client.Client,
    release_id: int | None = None,
    master_id: int | None = None,
    artist: str | None = None,
    album: str | None = None,
    format: str | None = None,
    folder_id: int = DEFAULT_ADD_FOLDER,
    allow_duplicate: bool = False,
    threshold: float = 0.7,
) -> SyncAction:
    """Add a single item to the collection."""
    limiter = get_rate_limiter()

    release_id = _resolve_item(
        client, release_id=release_id, master_id=master_id,
        artist=artist, album=album, format=format, threshold=threshold,
    )

    # Check for duplicates unless allowed
    if not allow_duplicate:
        current, current_masters, current_items = _get_collection_release_ids(client, DEFAULT_READ_FOLDER, limiter)
        if release_id in current or (master_id and master_id in current_masters):
            return SyncAction(
                action=SyncActionType.SKIP,
                release_id=release_id,
                artist=artist,
                title=album,
                reason="Already in collection (use --allow-duplicate to add another copy)",
            )
        if artist and album and _fuzzy_match_items(artist, album, current_items):
            return SyncAction(
                action=SyncActionType.SKIP,
                release_id=release_id,
                artist=artist,
                title=album,
                reason="Already in collection (fuzzy match, use --allow-duplicate to add another copy)",
            )

    _add_to_collection(client, release_id, folder_id, limiter)

    return SyncAction(
        action=SyncActionType.ADD,
        release_id=release_id,
        artist=artist,
        title=album,
    )


def remove_from_collection(
    client: discogs_client.Client,
    release_id: int | None = None,
    artist: str | None = None,
    album: str | None = None,
    format: str | None = None,
    folder_id: int = DEFAULT_READ_FOLDER,
    threshold: float = 0.7,
) -> SyncAction:
    """Remove a single item from the collection."""
    limiter = get_rate_limiter()

    release_id = _resolve_item(
        client, release_id=release_id, artist=artist, album=album,
        format=format, threshold=threshold,
    )

    current, _, _ = _get_collection_release_ids(client, folder_id, limiter)
    if release_id not in current:
        return SyncAction(
            action=SyncActionType.SKIP,
            release_id=release_id,
            artist=artist,
            title=album,
            reason="Not in collection",
        )

    # Remove first instance
    instance_id = current[release_id][0]
    _remove_from_collection(client, release_id, instance_id, folder_id, limiter)

    return SyncAction(
        action=SyncActionType.REMOVE,
        release_id=release_id,
        artist=artist,
        title=album,
    )


def list_collection(
    client: discogs_client.Client,
    folder_id: int = DEFAULT_READ_FOLDER,
) -> list[CollectionItem]:
    """Fetch and return all collection items from a folder."""
    limiter = get_rate_limiter()
    me = _api_call_with_retry(lambda: client.identity(), limiter)
    folder = _api_call_with_retry(
        lambda: me.collection_folders[folder_id],
        limiter,
    )
    releases = _api_call_with_retry(lambda: folder.releases, limiter)

    items = []
    page_num = 1
    while True:
        try:
            page = _api_call_with_retry(lambda p=page_num: releases.page(p), limiter)
            if not page:
                break
            for item in page:
                release = item.release if hasattr(item, "release") else item
                data = release.data if hasattr(release, "data") else {}

                artist_name = extract_artist_from_data(data)
                album_name = data.get("title", "")

                fmt = None
                formats = data.get("formats", [])
                if formats and isinstance(formats, list):
                    fmt = formats[0].get("name", "") if isinstance(formats[0], dict) else str(formats[0])

                instance_id = getattr(item, "instance_id", None) or data.get("instance_id", 0)
                if hasattr(item, "data") and isinstance(item.data, dict):
                    instance_id = item.data.get("instance_id", instance_id)

                items.append(CollectionItem(
                    instance_id=instance_id,
                    release_id=data.get("id", getattr(release, "id", 0)),
                    master_id=data.get("master_id"),
                    folder_id=folder_id,
                    title=album_name,
                    artist=artist_name,
                    format=fmt,
                    year=data.get("year"),
                ))
            page_num += 1
        except Exception:
            break

    return items


def _resolve_item(
    client,
    release_id: int | None = None,
    master_id: int | None = None,
    artist: str | None = None,
    album: str | None = None,
    format: str | None = None,
    threshold: float = 0.7,
) -> int:
    """Resolve various input forms to a release_id."""
    if release_id:
        return release_id

    if master_id:
        return resolve_master_id(client, master_id, preferred_format=format)

    if not artist or not album:
        raise SyncError("Must provide --release-id, --master-id, or both --artist and --album")

    record = InputRecord(artist=artist, album=album, format=format)
    result = search_release(client, record, threshold=threshold)
    if not result.matched:
        raise SyncError(f"No match found for {record.display_name()}")

    resolved_id = resolve_to_release_id(client, result)
    if not resolved_id:
        raise SyncError(f"Could not resolve release ID for {record.display_name()}")

    return resolved_id


def _get_collection_release_ids(client, folder_id: int, limiter) -> tuple[dict[int, list[int]], set[int], list[tuple[str, str, int]]]:
    """Fetch release_id -> [instance_id] mapping, set of master_ids, and (artist, title, release_id) tuples from collection."""
    me = _api_call_with_retry(lambda: client.identity(), limiter)
    folder = _api_call_with_retry(
        lambda: me.collection_folders[folder_id],
        limiter,
    )
    releases = _api_call_with_retry(lambda: folder.releases, limiter)

    mapping: dict[int, list[int]] = {}
    master_ids: set[int] = set()
    items_info: list[tuple[str, str, int]] = []
    page_num = 1
    while True:
        try:
            page = _api_call_with_retry(lambda p=page_num: releases.page(p), limiter)
            if not page:
                break
            for item in page:
                release = item.release if hasattr(item, "release") else item
                data = release.data if hasattr(release, "data") else {}
                rid = data.get("id") or getattr(release, "id", None)
                instance_id = getattr(item, "instance_id", None) or 0
                if hasattr(item, "data") and isinstance(item.data, dict):
                    instance_id = item.data.get("instance_id", instance_id)
                if rid:
                    mapping.setdefault(rid, []).append(instance_id)
                    artist_name = extract_artist_from_data(data)
                    album_name = data.get("title", "")
                    items_info.append((artist_name, album_name, rid))
                mid = data.get("master_id")
                if mid:
                    master_ids.add(mid)
            page_num += 1
        except Exception:
            break

    return mapping, master_ids, items_info


def _fuzzy_match_items(
    artist: str | None,
    title: str | None,
    items: list[tuple[str, str, int]],
    verbose: bool = False,
) -> bool:
    """Check if artist+title fuzzy-matches any item in the list."""
    if not artist or not title:
        return False
    for item_artist, item_title, item_rid in items:
        a_sim = _similarity(artist, item_artist)
        t_sim = _similarity(title, item_title)
        if a_sim >= FUZZY_MATCH_THRESHOLD and t_sim >= FUZZY_MATCH_THRESHOLD:
            if verbose:
                print_verbose(
                    f"  SKIP (fuzzy match): '{artist} - {title}' matched '{item_artist} - {item_title}' "
                    f"(release_id={item_rid}, artist_sim={a_sim:.2f}, title_sim={t_sim:.2f})"
                )
            return True
    return False


def _add_to_collection(client, release_id: int, folder_id: int, limiter) -> None:
    """Add a release to a collection folder."""
    me = _api_call_with_retry(lambda: client.identity(), limiter)
    _api_call_with_retry(
        lambda: me.collection_folders[folder_id].add_release(release_id),
        limiter,
    )


def _remove_from_collection(client, release_id: int, instance_id: int, folder_id: int, limiter) -> None:
    """Remove a release instance from a collection folder."""
    me = _api_call_with_retry(lambda: client.identity(), limiter)
    _api_call_with_retry(
        lambda: me.collection_folders[folder_id].remove_release(release_id, instance_id),
        limiter,
    )
