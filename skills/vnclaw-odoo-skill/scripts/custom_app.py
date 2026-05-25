#!/usr/bin/env python3
"""VNClaw — Custom App module

Generic interface for any Odoo model/app not covered by the dedicated scripts.
All security rules from odoo_core still apply (no delete, no blocked models).

Typical workflow:
  1. Discover the model technical name:   custom_app.py models --search "CRM"
  2. Inspect its fields:                  custom_app.py fields crm.lead
  3. List records:                        custom_app.py list crm.lead --search "Acme" --limit 20
  4. Read one record:                     custom_app.py get crm.lead 42
  5. Create a record:                     custom_app.py create crm.lead --values '{...}'
  6. Update a record:                     custom_app.py update crm.lead 42 --values '{...}'
  7. Count matching records:              custom_app.py count crm.lead --domain '[["stage_id.name","=","Won"]]'
  8. Log an internal note:               custom_app.py log-note crm.lead 42 --body "Called the client"
  9. Schedule an activity notification:  custom_app.py notify crm.lead 42 --user "Alice" --summary "Follow up"
"""

import argparse
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from odoo_core import (connect, execute, output_json, resolve_user,
                       add_date_filter_args, get_date_bounds,
                       log_note, schedule_activity, log, BLOCKED_MODELS)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_execute(uid, m, db, key, model, operation, *args, **kwargs):
    """Thin wrapper that surfaces friendly errors for unknown models."""
    try:
        return execute(uid, m, db, key, model, operation, *args, **kwargs)
    except Exception as exc:
        err = str(exc)
        if "Object" in err and "doesn't exist" in err:
            print(f"Error: Model '{model}' not found. "
                  "Run `custom_app.py models --search <keyword>` to discover the right model name.",
                  file=sys.stderr)
        else:
            print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)


def _get_name_field(uid, m, db, key, model):
    """Return the primary name field for a model (usually 'name', 'display_name', or 'subject')."""
    try:
        fields_info = m.execute_kw(db, uid, key, model, "fields_get",
                                   [], {"attributes": ["string", "type"]})
        for candidate in ("name", "display_name", "subject", "title", "ref"):
            if candidate in fields_info:
                return candidate
    except Exception:
        pass
    return "display_name"


def _build_default_fields(uid, m, db, key, model, extra=()):
    """Return a safe default field list for search_read by inspecting the model."""
    try:
        fields_info = m.execute_kw(db, uid, key, model, "fields_get",
                                   [], {"attributes": ["string", "type", "store"]})
    except Exception:
        return ["id", "display_name"]

    # Always include these if they exist
    priority = ["id", "name", "display_name", "create_date", "write_date",
                "user_id", "state", "active", "sequence"]
    result = [f for f in priority if f in fields_info and fields_info[f].get("store", True)]
    for f in extra:
        if f in fields_info and f not in result:
            result.append(f)
    # Pad to a reasonable set with other stored scalar fields
    SCALAR = {"char", "integer", "float", "monetary", "boolean", "selection",
               "date", "datetime", "text", "many2one"}
    for fname, fmeta in fields_info.items():
        if len(result) >= 12:
            break
        if (fname not in result and fmeta.get("store", True)
                and fmeta.get("type") in SCALAR):
            result.append(fname)
    return result


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_models(args):
    """List installed Odoo models, optionally filtered by name/description."""
    uid, m, db, key = connect()
    domain = [["transient", "=", False]]
    if args.search:
        domain.append("|")
        domain.append(["name", "ilike", args.search])
        domain.append(["model", "ilike", args.search])
    if args.module:
        # ir.model doesn't have a direct module field; use ir.model.data instead
        module_models = m.execute_kw(db, uid, key, "ir.model.data", "search_read",
                                     [[["module", "=", args.module], ["model", "=", "ir.model"]]],
                                     {"fields": ["res_id"], "limit": 500})
        if module_models:
            ids = [r["res_id"] for r in module_models]
            domain.append(["id", "in", ids])
    records = m.execute_kw(db, uid, key, "ir.model", "search_read",
                           [domain],
                           {"fields": ["id", "name", "model", "info"],
                            "limit": args.limit, "order": "model asc"})
    output_json(records)


def cmd_fields(args):
    """Return field definitions for a model — use this to find the right field names."""
    uid, m, db, key = connect()
    attrs = json.loads(args.attributes) if args.attributes else \
        ["string", "type", "required", "readonly", "store", "relation", "selection", "help"]
    try:
        fields_info = m.execute_kw(db, uid, key, args.model, "fields_get",
                                   [], {"attributes": attrs})
    except Exception as exc:
        print(f"Error fetching fields for '{args.model}': {exc}", file=sys.stderr)
        sys.exit(1)

    # Filter by type if requested
    if args.type:
        fields_info = {k: v for k, v in fields_info.items() if v.get("type") == args.type}
    if args.search:
        kw = args.search.lower()
        fields_info = {k: v for k, v in fields_info.items()
                       if kw in k.lower() or kw in v.get("string", "").lower()}

    # Sort by field name for readability
    ordered = dict(sorted(fields_info.items()))
    output_json(ordered)


def cmd_list(args):
    """Search and read records from any model."""
    uid, m, db, key = connect()

    domain = json.loads(args.domain) if args.domain else []

    # --my: filter by current user (tries user_id, create_uid, partner_id)
    if args.my:
        name_field = _get_name_field(uid, m, db, key, args.model)
        try:
            finfo = m.execute_kw(db, uid, key, args.model, "fields_get",
                                 [], {"attributes": ["type"]})
            if "user_id" in finfo:
                domain.append(["user_id", "=", uid])
            elif "create_uid" in finfo:
                domain.append(["create_uid", "=", uid])
        except Exception:
            pass

    # --user: resolve by name
    if args.user:
        user_id = resolve_user(uid, m, db, key, args.user)
        try:
            finfo = m.execute_kw(db, uid, key, args.model, "fields_get",
                                 [], {"attributes": ["type"]})
            if "user_id" in finfo:
                domain.append(["user_id", "=", user_id])
            elif "create_uid" in finfo:
                domain.append(["create_uid", "=", user_id])
        except Exception:
            pass

    # --search: ilike on the name field
    if args.search:
        name_f = _get_name_field(uid, m, db, key, args.model)
        domain.append([name_f, "ilike", args.search])

    # Date filters (applied to create_date by default, or --date-field)
    date_field = args.date_field or "create_date"
    df, dt = get_date_bounds(args)
    if df:
        domain.append([date_field, ">=", f"{df} 00:00:00"])
    if dt:
        domain.append([date_field, "<=", f"{dt} 23:59:59"])

    fields = json.loads(args.fields) if args.fields else \
        _build_default_fields(uid, m, db, key, args.model)
    order = args.order or "id desc"
    records = _safe_execute(uid, m, db, key, args.model, "search_read", domain,
                            fields=fields, limit=args.limit, offset=args.offset, order=order)
    output_json(records)


def cmd_get(args):
    """Read a single record by ID."""
    uid, m, db, key = connect()
    fields = json.loads(args.fields) if args.fields else []
    kw = {"fields": fields} if fields else {}
    try:
        records = m.execute_kw(db, uid, key, args.model, "read", [[args.id]], kw)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    output_json(records[0] if records else {"error": f"Record {args.id} not found in '{args.model}'"})


def cmd_create(args):
    """Create a record in any model."""
    uid, m, db, key = connect()
    vals = json.loads(args.values)
    rid = _safe_execute(uid, m, db, key, args.model, "create", vals)
    output_json({"created_id": rid, "model": args.model})


def cmd_update(args):
    """Update a record (or multiple records) in any model."""
    uid, m, db, key = connect()
    ids = json.loads(args.ids) if args.ids else [args.id]
    vals = json.loads(args.values)
    ok = _safe_execute(uid, m, db, key, args.model, "write", ids, vals)
    output_json({"updated_ids": ids, "success": ok, "model": args.model})


def cmd_count(args):
    """Count records matching a domain."""
    uid, m, db, key = connect()
    domain = json.loads(args.domain) if args.domain else []
    try:
        count = m.execute_kw(db, uid, key, args.model, "search_count", [domain])
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    output_json({"model": args.model, "count": count, "domain": domain})


def cmd_log_note(args):
    """Post an internal log note on any record."""
    uid, m, db, key = connect()
    msg_id = log_note(uid, m, db, key, args.model, args.id, args.body)
    output_json({"logged_note": True, "model": args.model, "record_id": args.id, "message_id": msg_id})


def cmd_notify(args):
    """Schedule an activity notification on any record, targeting a user by name."""
    uid, m, db, key = connect()
    user_id = resolve_user(uid, m, db, key, args.user)
    activity_id = schedule_activity(uid, m, db, key, args.model, args.id,
                                    user_id, args.summary, args.note or "")
    output_json({"activity_scheduled": True, "model": args.model,
                 "record_id": args.id, "for_user": args.user, "activity_id": activity_id})


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(
        description="VNClaw — Custom App: generic access to any Odoo model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="action")

    # models
    s = sub.add_parser("models", help="Discover installed Odoo models")
    s.add_argument("--search", help="Search by model name or technical name")
    s.add_argument("--module", help="Filter by Odoo module name (e.g. crm, sale)")
    s.add_argument("--limit", type=int, default=100)

    # fields
    s = sub.add_parser("fields", help="List fields of a model")
    s.add_argument("model", help="Model technical name (e.g. crm.lead)")
    s.add_argument("--search", help="Filter fields by name or label")
    s.add_argument("--type", help="Filter fields by type (char, many2one, selection, ...)")
    s.add_argument("--attributes", help="JSON array of field attributes to return")

    # list
    s = sub.add_parser("list", help="Search and read records from any model")
    s.add_argument("model", help="Model technical name (e.g. crm.lead)")
    s.add_argument("--domain", help="Odoo domain as JSON (e.g. '[[\\'stage_id.name\\',\\'=\\',\\'Won\\']]')")
    s.add_argument("--my", action="store_true", help="Records assigned to / created by me")
    s.add_argument("--user", help="Filter by user NAME (resolves via res.users)")
    s.add_argument("--search", help="ilike search on the primary name field")
    s.add_argument("--date-field", help="Field to apply date filters to (default: create_date)")
    add_date_filter_args(s)
    s.add_argument("--fields", help="JSON array of fields to return")
    s.add_argument("--limit", type=int, default=80)
    s.add_argument("--offset", type=int, default=0)
    s.add_argument("--order", help="Order by clause (e.g. 'create_date desc')")

    # get
    s = sub.add_parser("get", help="Read one record by ID")
    s.add_argument("model", help="Model technical name")
    s.add_argument("id", type=int, help="Record ID")
    s.add_argument("--fields", help="JSON array of fields to return (default: all)")

    # create
    s = sub.add_parser("create", help="Create a record")
    s.add_argument("model", help="Model technical name")
    s.add_argument("--values", required=True, help='Field values as JSON (e.g. \'{"name":"Test","user_id":2}\')')

    # update
    s = sub.add_parser("update", help="Update a record")
    s.add_argument("model", help="Model technical name")
    s.add_argument("id", type=int, nargs="?", help="Record ID (single record)")
    s.add_argument("--ids", help="Multiple record IDs as JSON array (e.g. '[1,2,3]')")
    s.add_argument("--values", required=True, help='Field values as JSON')

    # count
    s = sub.add_parser("count", help="Count records matching a domain")
    s.add_argument("model", help="Model technical name")
    s.add_argument("--domain", help="Odoo domain as JSON (default: [])")

    # log-note
    s = sub.add_parser("log-note", help="Post an internal note on a record")
    s.add_argument("model", help="Model technical name")
    s.add_argument("id", type=int, help="Record ID")
    s.add_argument("--body", required=True, help="Note body (HTML or plain text)")

    # notify
    s = sub.add_parser("notify", help="Schedule an activity notification on a record")
    s.add_argument("model", help="Model technical name")
    s.add_argument("id", type=int, help="Record ID")
    s.add_argument("--user", required=True, help="Target user NAME (resolved by name/email)")
    s.add_argument("--summary", required=True, help="Activity summary")
    s.add_argument("--note", help="Optional longer note")

    args = p.parse_args()
    if not args.action:
        p.print_help()
        sys.exit(1)

    dispatch = {
        "models": cmd_models,
        "fields": cmd_fields,
        "list": cmd_list,
        "get": cmd_get,
        "create": cmd_create,
        "update": cmd_update,
        "count": cmd_count,
        "log-note": cmd_log_note,
        "notify": cmd_notify,
    }
    dispatch[args.action](args)


if __name__ == "__main__":
    main()
