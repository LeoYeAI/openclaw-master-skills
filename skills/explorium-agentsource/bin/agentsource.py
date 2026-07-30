#!/usr/bin/env python3
"""
AgentSource CLI — wraps the Explorium REST API at api.explorium.ai.

All results are written to temporary files in /tmp/.
The CLI prints ONLY the temp-file path to stdout so that large payloads
never enter the conversation context window.

Usage:
    python agentsource.py <command> [options]

Authentication:
    Set EXPLORIUM_API_KEY environment variable, or run:
        python agentsource.py config --api-key <key>
"""

import argparse
import csv
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_URL = "https://api.explorium.ai/v1"
INSTALL_DIR = pathlib.Path.home() / ".agentsource"
# API key is stored only at this single location (mode 600, owner read-only)
CONFIG_FILE = INSTALL_DIR / "config.json"
TEMP_DIR = pathlib.Path("/tmp")

# Max IDs per bulk enrichment request (API limit)
BULK_ENRICH_BATCH = 50
# Max IDs per events request (API limit)
EVENTS_BATCH = 40
# Max page size (API limit)
MAX_PAGE_SIZE = 500
# Max entities per match request (API limit)
MATCH_BATCH = 50

# Column alias maps: CSV column name (lowercased, underscored) → API match field
BUSINESS_MATCH_ALIASES = {
    "name": "name", "company_name": "name", "company": "name",
    "organization": "name", "account": "name", "account_name": "name",
    "domain": "domain", "website": "domain", "url": "domain",
    "web": "domain", "homepage": "domain",
}

PROSPECT_MATCH_ALIASES = {
    "full_name": "full_name", "name": "full_name",
    "first_name": "first_name", "last_name": "last_name",
    "company_name": "company_name", "company": "company_name",
    "organization": "company_name", "employer": "company_name",
    "email": "email", "email_address": "email",
    "linkedin": "linkedin", "linkedin_url": "linkedin",
    "linkedin_profile": "linkedin",
}

# Bulk enrichment endpoint path fragments (relative to BASE_URL)
BUSINESS_ENRICHMENT_PATHS = {
    "firmographics": "businesses/firmographics",
    "technographics": "businesses/technographics",
    "funding_and_acquisition": "businesses/funding_and_acquisition",
    "company_ratings": "businesses/company_ratings",
    "financial_metrics": "businesses/financial_metrics",
    "challenges": "businesses/challenges",
    "competitive_landscape": "businesses/competitive_landscape",
    "strategic_insights": "businesses/strategic_insights",
    "workforce_trends": "businesses/workforce_trends",
    "social_media": "businesses/company_social_media",
    "website_content_changes": "businesses/website_content_changes",
    "webstack": "businesses/webstack",
    "keyword_search_on_websites": "businesses/keyword_search_on_websites",
    "company_hierarchy": "businesses/company_hierarchy",
}

PROSPECT_ENRICHMENT_PATHS = {
    "contacts_information": "prospects/contacts_information",
    "profiles": "prospects/profiles",
}

# ---------------------------------------------------------------------------
# Helpers — API key
# ---------------------------------------------------------------------------

def get_api_key() -> str:
    key = os.environ.get("EXPLORIUM_API_KEY", "").strip()
    if key:
        return key
    if CONFIG_FILE.exists():
        try:
            key = json.loads(CONFIG_FILE.read_text()).get("api_key", "").strip()
            if key:
                return key
        except (json.JSONDecodeError, OSError):
            pass
    write_error("get_api_key", (
        "EXPLORIUM_API_KEY is not set. "
        "Export it as an environment variable or run: "
        "python agentsource.py config --api-key <your_key>"
    ), "AUTH_MISSING")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Helpers — temp file output
# ---------------------------------------------------------------------------

def make_temp_path(command: str) -> pathlib.Path:
    ts = int(time.time())
    return TEMP_DIR / f"agentsource_{ts}_{command}.json"


def write_result(command: str, data: dict) -> pathlib.Path:
    path = make_temp_path(command)
    path.write_text(json.dumps(data, indent=2, default=str))
    print(str(path))
    return path


def write_error(command: str, error_msg: str, error_code: str = None,
                http_status: int = None) -> pathlib.Path:
    data = {
        "success": False,
        "error": error_msg,
        "error_code": error_code,
        "http_status": http_status,
        "command": command,
        "timestamp": int(time.time()),
    }
    path = make_temp_path(f"{command}_error")
    path.write_text(json.dumps(data, indent=2))
    print(str(path))
    return path


# ---------------------------------------------------------------------------
# Helpers — HTTP REST calls
# ---------------------------------------------------------------------------

def _request(api_key: str, method: str, path: str,
             params: dict = None, body: dict = None,
             retry: int = 1) -> dict:
    """
    Make an authenticated call to the AgentSource REST API.
    Returns the parsed JSON response dict.
    Raises ValueError with structured info on failure.
    """
    url = f"{BASE_URL}/{path}"
    if params:
        url = url + "?" + urllib.parse.urlencode(params)

    data = json.dumps(body).encode() if body is not None else None
    headers = {
        "api_key": api_key,
        "Content-Type": "application/json",
        "accept": "application/json",
        "User-Agent": "agentsource-cli/1.0",
    }
    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    for attempt in range(retry + 1):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            status = exc.code
            body_text = exc.read().decode("utf-8", errors="replace")
            if status == 429 and attempt < retry:
                retry_after = int(exc.headers.get("Retry-After", "10"))
                time.sleep(retry_after)
                continue
            if status in (500, 502, 503) and attempt < retry:
                time.sleep(5)
                continue
            code_map = {401: "AUTH_FAILED", 403: "FORBIDDEN", 400: "BAD_REQUEST",
                        404: "NOT_FOUND", 422: "VALIDATION_ERROR", 429: "RATE_LIMIT"}
            raise ValueError(json.dumps({
                "error_code": code_map.get(status, "SERVER_ERROR"),
                "http_status": status,
                "error": body_text[:500],
            }))
        except (urllib.error.URLError, OSError) as exc:
            if attempt < retry:
                time.sleep(3)
                continue
            raise ValueError(json.dumps({
                "error_code": "NETWORK_ERROR", "http_status": None, "error": str(exc)
            }))


def safe_request(command: str, api_key: str, method: str, path: str,
                 params: dict = None, body: dict = None) -> dict:
    """Wrapper that writes an error temp file and exits on failure."""
    try:
        return _request(api_key, method, path, params=params, body=body)
    except ValueError as exc:
        try:
            info = json.loads(str(exc))
        except json.JSONDecodeError:
            info = {"error_code": "UNKNOWN", "http_status": None, "error": str(exc)}
        write_error(command, info.get("error", str(exc)),
                    info.get("error_code"), info.get("http_status"))
        sys.exit(1)


# ---------------------------------------------------------------------------
# Helpers — request context (usage tracking)
# ---------------------------------------------------------------------------

def _add_tracking_args(parser) -> None:
    """Add optional request-context tracking args to any API-calling subcommand."""
    parser.add_argument(
        "--call-reasoning", default=None, metavar="TEXT",
        help="The user query that triggered this call (e.g. 'find 500 healthcare PMs')",
    )
    parser.add_argument(
        "--plan-id", default=None, metavar="UUID",
        help="Unique ID grouping all CLI calls made to answer a single user query",
    )


def _request_context(args):
    """Build the optional request_context payload for server-side call grouping.

    Privacy note: when --call-reasoning is supplied, the user's query text is
    sent to api.explorium.ai as part of the request metadata. This is opt-in —
    omit --call-reasoning if the user has not consented to query logging.
    """
    reasoning = getattr(args, "call_reasoning", None)
    plan_id = getattr(args, "plan_id", None)
    if not reasoning and not plan_id:
        return None
    return {
        "type": "vibe-prospecting-plugin",
        "call_reasoning": reasoning,
        "plan_id": plan_id,
    }


# ---------------------------------------------------------------------------
# Helpers — data utilities
# ---------------------------------------------------------------------------

def _flatten(obj: dict, prefix: str = "") -> dict:
    """Recursively flatten a nested dict, joining keys with '.'."""
    result = {}
    for k, v in obj.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            result.update(_flatten(v, key))
        elif isinstance(v, list):
            result[key] = json.dumps(v, ensure_ascii=False)
        else:
            result[key] = v
    return result


def _extract_match_fields(row: dict, aliases: dict, column_map: dict = None) -> dict:
    """Map a CSV row's columns to the API's expected match field names.

    If column_map is provided ({"CSV Column": "api_field", ...}), it is used
    directly (exact column names, case-sensitive).  Otherwise the alias table
    is used as a fallback (lowercased/underscored column names).
    """
    out = {}
    if column_map:
        for csv_col, api_field in column_map.items():
            val = row.get(csv_col, "")
            if val and str(val).strip():
                out[api_field] = str(val).strip()
    else:
        for col, val in row.items():
            key = col.lower().strip().replace(" ", "_").replace("-", "_")
            if key in aliases and val and str(val).strip():
                out[aliases[key]] = str(val).strip()

    # Normalize linkedin URL fields: ensure they start with https://www.
    for li_field in ("linkedin_url", "linkedin"):
        if li_field in out:
            url = out[li_field]
            if url.startswith("linkedin.com"):
                url = "https://www." + url
            elif url.startswith("www.linkedin.com"):
                url = "https://" + url
            out[li_field] = url

    # Construct full_name from first_name + last_name if not already present
    if "full_name" not in out and ("first_name" in out or "last_name" in out):
        parts = [out.pop("first_name", ""), out.pop("last_name", "")]
        out["full_name"] = " ".join(p for p in parts if p)
    return out


def _load_input_file(path_str: str, command: str) -> dict:
    """Load a JSON temp file produced by a previous CLI command."""
    p = pathlib.Path(path_str)
    if not p.exists():
        write_error(command, f"Input file not found: {path_str}", "FILE_NOT_FOUND")
        sys.exit(1)
    try:
        data = json.loads(p.read_text())
    except json.JSONDecodeError as exc:
        write_error(command, f"Cannot parse input file: {exc}", "PARSE_ERROR")
        sys.exit(1)
    if not data.get("success"):
        write_error(command,
                    f"Input file contains a failed result: {data.get('error', 'unknown')}",
                    "BAD_INPUT")
        sys.exit(1)
    return data


# ---------------------------------------------------------------------------
# Command implementations
# ---------------------------------------------------------------------------

def cmd_config(args):
    INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    cfg = {}
    if CONFIG_FILE.exists():
        try:
            cfg = json.loads(CONFIG_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    if args.api_key:
        cfg["api_key"] = args.api_key.strip()
    # API key is stored only in a single location with restrictive permissions
    INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))
    CONFIG_FILE.chmod(0o600)
    write_result("config", {"success": True, "saved_to": str(CONFIG_FILE)})


def cmd_from_csv(args):
    """Convert an existing CSV file to a JSON temp file without loading it into context."""
    p = pathlib.Path(args.input).expanduser()
    if not p.exists():
        write_error("from_csv", f"CSV file not found: {args.input}", "FILE_NOT_FOUND")
        sys.exit(1)

    rows = []
    columns = []
    try:
        with p.open(newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            columns = list(reader.fieldnames or [])
            for row in reader:
                rows.append(dict(row))
    except (OSError, csv.Error) as exc:
        write_error("from_csv", f"Cannot read CSV: {exc}", "PARSE_ERROR")
        sys.exit(1)

    write_result("from_csv", {
        "success": True,
        "source_csv": str(p),
        "total_rows": len(rows),
        "columns": columns,
        "data": rows,
        "sample": rows[:5],
    })


def cmd_autocomplete(args):
    api_key = get_api_key()
    entity = args.entity_type  # "businesses" or "prospects"
    params = {"field": args.field, "query": args.query}
    if args.semantic:
        params["semantic_search"] = "true"

    raw = safe_request("autocomplete", api_key, "GET",
                       f"{entity}/autocomplete", params=params)

    # Response is a list of {query, label, value}
    results = raw if isinstance(raw, list) else raw.get("data", raw)
    write_result("autocomplete", {
        "success": True,
        "entity_type": entity,
        "field": args.field,
        "query": args.query,
        "results": results,
    })


def cmd_statistics(args):
    api_key = get_api_key()
    try:
        filters = json.loads(args.filters) if args.filters else {}
    except json.JSONDecodeError as exc:
        write_error("statistics", f"Invalid --filters JSON: {exc}", "BAD_REQUEST")
        sys.exit(1)

    entity = args.entity_type
    body: dict = {"filters": filters}
    ctx = _request_context(args)
    if ctx:
        body["request_context"] = ctx
    raw = safe_request("statistics", api_key, "POST", f"{entity}/stats", body=body)

    write_result("statistics", {
        "success": True,
        "entity_type": entity,
        "total_results": raw.get("total_results"),
        "stats": raw.get("stats", raw),
    })


def cmd_fetch(args):
    api_key = get_api_key()
    try:
        filters = json.loads(args.filters) if args.filters else {}
    except json.JSONDecodeError as exc:
        write_error("fetch", f"Invalid --filters JSON: {exc}", "BAD_REQUEST")
        sys.exit(1)

    entity = args.entity_type
    total_limit = args.limit
    page_size = min(total_limit, MAX_PAGE_SIZE)
    all_data = []
    page = 1
    total_results = None
    total_pages = None

    while len(all_data) < total_limit:
        want = min(page_size, total_limit - len(all_data))
        body = {
            "mode": "full",
            "size": total_limit,
            "page_size": want,
            "page": page,
            "filters": filters,
        }
        ctx = _request_context(args)
        if ctx:
            body["request_context"] = ctx
        if getattr(args, "exclude", None):
            try:
                body["exclude"] = json.loads(args.exclude)
            except (json.JSONDecodeError, TypeError):
                pass

        try:
            raw = _request(api_key, "POST", entity, body=body)
        except ValueError as exc:
            try:
                info = json.loads(str(exc))
            except json.JSONDecodeError:
                info = {"error_code": "UNKNOWN", "http_status": None, "error": str(exc)}
            write_error("fetch", info.get("error", str(exc)),
                        info.get("error_code"), info.get("http_status"))
            sys.exit(1)

        page_data = raw.get("data", [])
        all_data.extend(page_data)

        if total_results is None:
            total_results = raw.get("total_results")
        total_pages = raw.get("total_pages", 1)

        if page >= total_pages or len(page_data) < want:
            break
        page += 1

    write_result("fetch", {
        "success": True,
        "entity_type": entity,
        "total_results": total_results,
        "total_fetched": len(all_data),
        "pages_fetched": page,
        "data": all_data,
        "sample": all_data[:10],
    })


def cmd_enrich(args):
    api_key = get_api_key()
    input_data = _load_input_file(args.input_file, "enrich")
    entity_type = input_data.get("entity_type")
    entities = input_data.get("data", [])

    enrichments = [e.strip() for e in args.enrichments.split(",") if e.strip()]

    if entity_type == "businesses":
        id_field = "business_id"
        enrich_map = BUSINESS_ENRICHMENT_PATHS
        batch_key = "business_ids"
    elif entity_type == "prospects":
        id_field = "prospect_id"
        enrich_map = PROSPECT_ENRICHMENT_PATHS
        batch_key = "prospect_ids"
    else:
        write_error("enrich",
                    f"Unknown entity_type '{entity_type}' in input file. Expected 'businesses' or 'prospects'.",
                    "BAD_INPUT")
        sys.exit(1)

    # Validate enrichment names
    for e in enrichments:
        if e not in enrich_map:
            valid = ", ".join(sorted(enrich_map))
            write_error("enrich",
                        f"Unknown enrichment '{e}' for {entity_type}. Valid: {valid}",
                        "BAD_REQUEST")
            sys.exit(1)

    # Build id → entity dict
    id_to_entity = {}
    for ent in entities:
        eid = ent.get(id_field)
        if eid:
            id_to_entity[eid] = dict(ent)

    all_ids = list(id_to_entity.keys())

    for enrichment in enrichments:
        path = f"{enrich_map[enrichment]}/bulk_enrich"
        for i in range(0, len(all_ids), BULK_ENRICH_BATCH):
            batch = all_ids[i:i + BULK_ENRICH_BATCH]
            body = {batch_key: batch}
            ctx = _request_context(args)
            if ctx:
                body["request_context"] = ctx
            if getattr(args, "parameters", None):
                try:
                    body["parameters"] = json.loads(args.parameters)
                except (json.JSONDecodeError, TypeError):
                    pass

            try:
                raw = _request(api_key, "POST", path, body=body)
            except ValueError as exc:
                try:
                    info = json.loads(str(exc))
                except json.JSONDecodeError:
                    info = {"error_code": "UNKNOWN", "http_status": None, "error": str(exc)}
                write_error("enrich", info.get("error", str(exc)),
                            info.get("error_code"), info.get("http_status"))
                sys.exit(1)

            for row in raw.get("data", []):
                eid = row.get(id_field)
                if eid and eid in id_to_entity:
                    id_to_entity[eid][enrichment] = row.get("data", row)

    enriched = list(id_to_entity.values())
    write_result("enrich", {
        "success": True,
        "entity_type": entity_type,
        "enrichments_applied": enrichments,
        "total_fetched": len(enriched),
        "data": enriched,
        "sample": enriched[:5],
    })


def cmd_events(args):
    api_key = get_api_key()
    input_data = _load_input_file(args.input_file, "events")
    entities = input_data.get("data", [])
    event_types = [e.strip() for e in args.event_types.split(",") if e.strip()]

    # Extract business_ids from the result set
    business_ids = [e.get("business_id") for e in entities if e.get("business_id")]
    if not business_ids:
        write_error("events", "No business_ids found in input file.", "BAD_INPUT")
        sys.exit(1)

    all_events = []
    for i in range(0, len(business_ids), EVENTS_BATCH):
        batch = business_ids[i:i + EVENTS_BATCH]
        body = {"event_types": event_types, "business_ids": batch}
        if args.since:
            body["timestamp_from"] = args.since
        if getattr(args, "until", None):
            body["timestamp_to"] = args.until
        ctx = _request_context(args)
        if ctx:
            body["request_context"] = ctx

        try:
            raw = _request(api_key, "POST", "businesses/events", body=body)
        except ValueError as exc:
            try:
                info = json.loads(str(exc))
            except json.JSONDecodeError:
                info = {"error_code": "UNKNOWN", "http_status": None, "error": str(exc)}
            write_error("events", info.get("error", str(exc)),
                        info.get("error_code"), info.get("http_status"))
            sys.exit(1)

        all_events.extend(raw.get("output_events", raw.get("data", [])))

    write_result("events", {
        "success": True,
        "entity_type": "businesses",
        "event_types": event_types,
        "total_events": len(all_events),
        "data": all_events,
        "sample": all_events[:10],
    })


def cmd_to_csv(args):
    input_data = _load_input_file(args.input_file, "to_csv")
    entities = input_data.get("data", [])

    if not entities:
        write_error("to_csv", "No data found in input file.", "EMPTY_DATA")
        sys.exit(1)

    # Flatten all records
    flat = [_flatten(e) for e in entities]

    # Collect all keys in order of first appearance
    all_keys: list = []
    seen: set = set()
    for row in flat:
        for k in row:
            if k not in seen:
                all_keys.append(k)
                seen.add(k)

    output_path = pathlib.Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_keys, extrasaction="ignore",
                                 quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(flat)

    write_result("to_csv", {
        "success": True,
        "csv_path": str(output_path),
        "row_count": len(flat),
        "columns": all_keys,
    })


def cmd_match_business(args):
    api_key = get_api_key()

    if getattr(args, "input_file", None):
        # --- CSV-originated flow: read JSON file, extract + batch ---
        input_data = _load_input_file(args.input_file, "match_business")
        rows = input_data.get("data", [])

        column_map = None
        if getattr(args, "column_map", None):
            try:
                column_map = json.loads(args.column_map)
            except json.JSONDecodeError as exc:
                write_error("match_business", f"Invalid --column-map JSON: {exc}", "BAD_REQUEST")
                sys.exit(1)

        candidates = [_extract_match_fields(r, BUSINESS_MATCH_ALIASES, column_map) for r in rows]
        candidates = [c for c in candidates if c]  # drop rows with no mappable fields
        if not candidates:
            write_error("match_business",
                        "No mappable columns found. Pass --column-map to specify the mapping "
                        "explicitly, e.g. '{\"Company\": \"name\", \"Website\": \"domain\"}'.",
                        "BAD_INPUT")
            sys.exit(1)

        all_matched = []
        ctx = _request_context(args)
        for i in range(0, len(candidates), MATCH_BATCH):
            batch = candidates[i:i + MATCH_BATCH]
            body: dict = {"businesses_to_match": batch}
            if ctx:
                body["request_context"] = ctx
            try:
                raw = _request(api_key, "POST", "businesses/match", body=body)
            except ValueError as exc:
                try:
                    info = json.loads(str(exc))
                except json.JSONDecodeError:
                    info = {"error_code": "UNKNOWN", "http_status": None, "error": str(exc)}
                write_error("match_business", info.get("error", str(exc)),
                            info.get("error_code"), info.get("http_status"))
                sys.exit(1)
            all_matched.extend(raw.get("matched_businesses", []))

        write_result("match_business", {
            "success": True,
            "entity_type": "businesses",
            "total_input": len(candidates),
            "total_matched": len(all_matched),
            "data": all_matched,
            "sample": all_matched[:10],
        })

    else:
        # --- Inline JSON flow ---
        if not getattr(args, "businesses", None):
            write_error("match_business",
                        "Provide either --businesses JSON or --input-file PATH.", "BAD_REQUEST")
            sys.exit(1)
        try:
            businesses = json.loads(args.businesses)
        except json.JSONDecodeError as exc:
            write_error("match_business", f"Invalid --businesses JSON: {exc}", "BAD_REQUEST")
            sys.exit(1)

        body: dict = {"businesses_to_match": businesses}
        ctx = _request_context(args)
        if ctx:
            body["request_context"] = ctx
        raw = safe_request("match_business", api_key, "POST", "businesses/match", body=body)

        write_result("match_business", {
            "success": True,
            "entity_type": "businesses",
            "total_input": len(businesses),
            "total_matched": raw.get("total_matches", len(raw.get("matched_businesses", []))),
            "data": raw.get("matched_businesses", []),
            "sample": raw.get("matched_businesses", [])[:10],
        })


def cmd_match_prospect(args):
    api_key = get_api_key()

    if getattr(args, "input_file", None):
        # --- CSV-originated flow: read JSON file, extract + batch ---
        input_data = _load_input_file(args.input_file, "match_prospect")
        rows = input_data.get("data", [])

        column_map = None
        if getattr(args, "column_map", None):
            try:
                column_map = json.loads(args.column_map)
            except json.JSONDecodeError as exc:
                write_error("match_prospect", f"Invalid --column-map JSON: {exc}", "BAD_REQUEST")
                sys.exit(1)

        candidates = [_extract_match_fields(r, PROSPECT_MATCH_ALIASES, column_map) for r in rows]
        candidates = [c for c in candidates if c]
        if not candidates:
            write_error("match_prospect",
                        "No mappable columns found. Pass --column-map to specify the mapping "
                        "explicitly, e.g. '{\"Full Name\": \"full_name\", \"Company\": \"company_name\"}'.",
                        "BAD_INPUT")
            sys.exit(1)

        all_matched = []
        ctx = _request_context(args)
        for i in range(0, len(candidates), MATCH_BATCH):
            batch = candidates[i:i + MATCH_BATCH]
            body: dict = {"prospects_to_match": batch}
            if ctx:
                body["request_context"] = ctx
            try:
                raw = _request(api_key, "POST", "prospects/match", body=body)
            except ValueError as exc:
                try:
                    info = json.loads(str(exc))
                except json.JSONDecodeError:
                    info = {"error_code": "UNKNOWN", "http_status": None, "error": str(exc)}
                write_error("match_prospect", info.get("error", str(exc)),
                            info.get("error_code"), info.get("http_status"))
                sys.exit(1)
            all_matched.extend(raw.get("matched_prospects", []))

        write_result("match_prospect", {
            "success": True,
            "entity_type": "prospects",
            "total_input": len(candidates),
            "total_matched": len(all_matched),
            "data": all_matched,
            "sample": all_matched[:10],
        })

    else:
        # --- Inline JSON flow ---
        if not getattr(args, "prospects", None):
            write_error("match_prospect",
                        "Provide either --prospects JSON or --input-file PATH.", "BAD_REQUEST")
            sys.exit(1)
        try:
            prospects = json.loads(args.prospects)
        except json.JSONDecodeError as exc:
            write_error("match_prospect", f"Invalid --prospects JSON: {exc}", "BAD_REQUEST")
            sys.exit(1)

        body: dict = {"prospects_to_match": prospects}
        ctx = _request_context(args)
        if ctx:
            body["request_context"] = ctx
        raw = safe_request("match_prospect", api_key, "POST", "prospects/match", body=body)

        write_result("match_prospect", {
            "success": True,
            "entity_type": "prospects",
            "total_input": len(prospects),
            "total_matched": raw.get("total_matches", len(raw.get("matched_prospects", []))),
            "data": raw.get("matched_prospects", []),
            "sample": raw.get("matched_prospects", [])[:10],
        })


# ---------------------------------------------------------------------------
# CLI argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agentsource",
        description=(
            "AgentSource CLI — B2B prospecting via the Explorium REST API.\n"
            "All results are written to /tmp temp files; only the path is printed."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True, metavar="<command>")

    # --- config ---
    p = sub.add_parser("config", help="Save API key to ~/.agentsource/config.json")
    p.add_argument("--api-key", metavar="KEY")
    p.set_defaults(func=cmd_config)

    # --- from-csv ---
    p = sub.add_parser(
        "from-csv",
        help="Convert an existing CSV file to a JSON temp file for use with match-business/match-prospect",
    )
    p.add_argument("--input", required=True, metavar="CSV_PATH",
                   help="Path to the source CSV file")
    _add_tracking_args(p)
    p.set_defaults(func=cmd_from_csv)

    # --- autocomplete ---
    p = sub.add_parser(
        "autocomplete",
        help="Get standardized filter values (required before using certain filter fields)",
    )
    p.add_argument("--entity-type", required=True, choices=["businesses", "prospects"],
                   help="Entity type to autocomplete for")
    p.add_argument("--field", required=True,
                   help="Filter field name (e.g. linkedin_category, job_title, country_code)")
    p.add_argument("--query", required=True, help="Search string")
    p.add_argument("--semantic", action="store_true",
                   help="Enable semantic (broader) search")
    _add_tracking_args(p)
    p.set_defaults(func=cmd_autocomplete)

    # --- statistics ---
    p = sub.add_parser("statistics",
                       help="Get market sizing stats for a filter set (free — no credits consumed)")
    p.add_argument("--entity-type", required=True, choices=["businesses", "prospects"])
    p.add_argument("--filters", default="{}", metavar="JSON",
                   help='Filters as JSON, e.g. \'{"company_size":{"values":["51-200"]}}\'')
    _add_tracking_args(p)
    p.set_defaults(func=cmd_statistics)

    # --- fetch ---
    p = sub.add_parser(
        "fetch",
        help="Fetch entities. Paginates automatically when --limit > 500.",
    )
    p.add_argument("--entity-type", required=True, choices=["businesses", "prospects"])
    p.add_argument("--filters", default="{}", metavar="JSON",
                   help='Filters as JSON, e.g. \'{"country_code":{"values":["us"]}}\'')
    p.add_argument("--limit", type=int, default=10,
                   help="Total results to fetch (default: 10; paginates automatically in batches of 500)")
    p.add_argument("--exclude", default=None, metavar="JSON",
                   help="JSON array of entity IDs to exclude from results")
    _add_tracking_args(p)
    p.set_defaults(func=cmd_fetch)

    # --- enrich ---
    p = sub.add_parser(
        "enrich",
        help="Bulk-enrich entities from a fetch result file",
    )
    p.add_argument("--input-file", required=True, metavar="PATH",
                   help="Path to a temp file produced by the `fetch` command")
    p.add_argument(
        "--enrichments", required=True,
        help=(
            "Comma-separated enrichment types.\n"
            "Business: firmographics, technographics, funding_and_acquisition, "
            "company_ratings, financial_metrics, challenges, competitive_landscape, "
            "strategic_insights, workforce_trends, social_media, "
            "website_content_changes, webstack, keyword_search_on_websites, company_hierarchy\n"
            "Prospect: contacts_information, profiles"
        ),
    )
    p.add_argument("--parameters", default=None, metavar="JSON",
                   help="Optional parameters JSON passed to each enrichment call")
    _add_tracking_args(p)
    p.set_defaults(func=cmd_enrich)

    # --- events ---
    p = sub.add_parser(
        "events",
        help="Fetch business trigger events for all business_ids in a fetch result file",
    )
    p.add_argument("--input-file", required=True, metavar="PATH",
                   help="Path to a temp file produced by `fetch --entity-type businesses`")
    p.add_argument("--event-types", required=True,
                   help="Comma-separated event types (see references/events.md)")
    p.add_argument("--since", default=None, metavar="YYYY-MM-DD",
                   help="Fetch events from this date onwards")
    p.add_argument("--until", default=None, metavar="YYYY-MM-DD",
                   help="Fetch events up to this date")
    _add_tracking_args(p)
    p.set_defaults(func=cmd_events)

    # --- to-csv ---
    p = sub.add_parser(
        "to-csv",
        help="Convert a fetch or enrich result file to a CSV file",
    )
    p.add_argument("--input-file", required=True, metavar="PATH",
                   help="Path to a temp file produced by `fetch` or `enrich`")
    p.add_argument("--output", required=True, metavar="CSV_PATH",
                   help="Path to write the CSV output (e.g. ~/results/companies.csv)")
    _add_tracking_args(p)
    p.set_defaults(func=cmd_to_csv)

    # --- match-business ---
    p = sub.add_parser(
        "match-business",
        help="Match businesses by name/domain to get Explorium business_ids. "
             "Use --input-file with a from-csv result to start from an existing CSV.",
    )
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--businesses", metavar="JSON",
                   help='Inline JSON array, e.g. \'[{"name":"Acme","domain":"acme.com"}]\'')
    g.add_argument("--input-file", metavar="PATH",
                   help="Path to a from-csv result file (auto-maps columns to match fields)")
    p.add_argument("--column-map", default=None, metavar="JSON",
                   help='Explicit CSV→API column mapping, e.g. \'{"Company Name":"name","Website":"domain"}\'. '
                        'Use after inspecting from-csv columns+sample. Overrides auto-alias matching.')
    _add_tracking_args(p)
    p.set_defaults(func=cmd_match_business)

    # --- match-prospect ---
    p = sub.add_parser(
        "match-prospect",
        help="Match prospects by name/company to get Explorium prospect_ids. "
             "Use --input-file with a from-csv result to start from an existing CSV.",
    )
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--prospects", metavar="JSON",
                   help='Inline JSON array, e.g. \'[{"full_name":"Jane Doe","company_name":"Acme"}]\'')
    g.add_argument("--input-file", metavar="PATH",
                   help="Path to a from-csv result file (auto-maps columns to match fields)")
    p.add_argument("--column-map", default=None, metavar="JSON",
                   help='Explicit CSV→API column mapping, e.g. \'{"Full Name":"full_name","Employer":"company_name","Email":"email"}\'. '
                        'Use after inspecting from-csv columns+sample. Overrides auto-alias matching.')
    _add_tracking_args(p)
    p.set_defaults(func=cmd_match_prospect)

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
