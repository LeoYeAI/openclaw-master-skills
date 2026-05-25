#!/usr/bin/env python3
"""
VNClaw — Odoo 17 XML-RPC Core Library

Shared connection, security, and execution logic.
Imported by all module scripts. Can also be run directly for generic operations.
"""

import argparse
import json
import os
import sys
import xmlrpc.client
from datetime import datetime

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------
BLOCKED_MODELS = frozenset({
    "ir.rule", "ir.model.access", "ir.config_parameter", "ir.module.module",
    "res.groups", "base.module.upgrade", "base.module.uninstall",
    "ir.cron", "ir.actions.server", "ir.actions.act_window",
})

READ_ONLY_MODELS = frozenset({
    "res.users", "hr.employee", "project.task.type",
    "hr.leave.type", "helpdesk.team", "documents.folder",
})

ALLOWED_OPERATIONS = frozenset({"search_read", "read", "create", "write", "search", "fields_get"})


def log(msg: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}", file=sys.stderr)


def get_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        print(f"Error: Environment variable '{name}' is not set.", file=sys.stderr)
        sys.exit(1)
    return value


def connect():
    """Authenticate and return (uid, models_proxy, db, api_key)."""
    url = get_env("ODOO_URL").rstrip("/")
    db = get_env("ODOO_DB")
    username = get_env("ODOO_USERNAME")
    api_key = get_env("ODOO_API_KEY")

    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", allow_none=True, context=None)
    uid = common.authenticate(db, username, api_key, {})
    if not uid:
        print("Error: Authentication failed. Check your credentials.", file=sys.stderr)
        sys.exit(1)

    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", allow_none=True, context=None)
    log(f"Authenticated as uid={uid} on {url} (db={db})")
    return uid, models, db, api_key


def validate_operation(model: str, operation: str) -> None:
    if operation not in ALLOWED_OPERATIONS:
        print(f"Error: Operation '{operation}' is not allowed.", file=sys.stderr)
        sys.exit(1)
    if model in BLOCKED_MODELS:
        print(f"Error: Access to model '{model}' is blocked for security.", file=sys.stderr)
        sys.exit(1)
    if operation in ("create", "write") and model in READ_ONLY_MODELS:
        print(f"Error: Model '{model}' is read-only.", file=sys.stderr)
        sys.exit(1)


def execute(uid, models, db, api_key, model, operation, *args, **kwargs):
    validate_operation(model, operation)
    log(f"{model}.{operation}")
    return models.execute_kw(db, uid, api_key, model, operation, list(args), kwargs)


def output_json(data):
    print(json.dumps(data, indent=2, default=str))


# ---------------------------------------------------------------------------
# Name → ID Resolvers (so users never need to know IDs)
# ---------------------------------------------------------------------------
_user_cache = {}
_partner_cache = {}
_employee_cache = {}


def resolve_user(uid, models, db, api_key, name_or_email):
    """Resolve a user by name or email → user ID. Cached per session."""
    key = name_or_email.lower().strip()
    if key in _user_cache:
        return _user_cache[key]
    domain = ["|", ["name", "ilike", key], ["login", "ilike", key]]
    users = models.execute_kw(db, uid, api_key, "res.users", "search_read",
                              [domain], {"fields": ["id", "name", "login"], "limit": 5})
    if not users:
        print(f"Error: No user found matching '{name_or_email}'.", file=sys.stderr)
        sys.exit(1)
    if len(users) > 1:
        log(f"Multiple users match '{name_or_email}': {[u['name'] for u in users]}. Using first: {users[0]['name']} (id={users[0]['id']})")
    _user_cache[key] = users[0]["id"]
    return users[0]["id"]


def resolve_partner(uid, models, db, api_key, name_or_email):
    """Resolve a partner/contact by name or email → partner ID."""
    key = name_or_email.lower().strip()
    if key in _partner_cache:
        return _partner_cache[key]
    domain = ["|", ["name", "ilike", key], ["email", "ilike", key]]
    partners = models.execute_kw(db, uid, api_key, "res.partner", "search_read",
                                 [domain], {"fields": ["id", "name", "email"], "limit": 5})
    if not partners:
        print(f"Error: No partner found matching '{name_or_email}'.", file=sys.stderr)
        sys.exit(1)
    if len(partners) > 1:
        log(f"Multiple partners match '{name_or_email}': {[p['name'] for p in partners]}. Using first: {partners[0]['name']} (id={partners[0]['id']})")
    _partner_cache[key] = partners[0]["id"]
    return partners[0]["id"]


def resolve_employee(uid, models, db, api_key, name):
    """Resolve an employee by name → employee ID."""
    key = name.lower().strip()
    if key in _employee_cache:
        return _employee_cache[key]
    employees = models.execute_kw(db, uid, api_key, "hr.employee", "search_read",
                                  [[["name", "ilike", key]]], {"fields": ["id", "name"], "limit": 5})
    if not employees:
        print(f"Error: No employee found matching '{name}'.", file=sys.stderr)
        sys.exit(1)
    if len(employees) > 1:
        log(f"Multiple employees match '{name}': {[e['name'] for e in employees]}. Using first: {employees[0]['name']} (id={employees[0]['id']})")
    _employee_cache[key] = employees[0]["id"]
    return employees[0]["id"]


def resolve_project(uid, models, db, api_key, name):
    """Resolve a project by name → project ID."""
    projects = models.execute_kw(db, uid, api_key, "project.project", "search_read",
                                 [[["name", "ilike", name.strip()]]], {"fields": ["id", "name"], "limit": 5})
    if not projects:
        print(f"Error: No project found matching '{name}'.", file=sys.stderr)
        sys.exit(1)
    if len(projects) > 1:
        log(f"Multiple projects match '{name}': {[p['name'] for p in projects]}. Using first: {projects[0]['name']} (id={projects[0]['id']})")
    return projects[0]["id"]


def resolve_users_multi(uid, models, db, api_key, names_csv):
    """Resolve comma-separated user names → list of user IDs."""
    names = [n.strip() for n in names_csv.split(",") if n.strip()]
    return [resolve_user(uid, models, db, api_key, n) for n in names]


# ---------------------------------------------------------------------------
# Date Range Helpers
# ---------------------------------------------------------------------------
def date_range(shortcut):
    """Convert a shortcut to (date_from, date_to) strings (YYYY-MM-DD).
    Shortcuts: today, yesterday, this-week, last-week, this-month, last-month, this-year.
    """
    from datetime import date as _date, timedelta
    today = _date.today()

    if shortcut == "today":
        return str(today), str(today)
    elif shortcut == "yesterday":
        y = today - timedelta(days=1)
        return str(y), str(y)
    elif shortcut == "this-week":
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=6)
        return str(monday), str(sunday)
    elif shortcut == "last-week":
        monday = today - timedelta(days=today.weekday() + 7)
        sunday = monday + timedelta(days=6)
        return str(monday), str(sunday)
    elif shortcut == "this-month":
        first = today.replace(day=1)
        if today.month == 12:
            last = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            last = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        return str(first), str(last)
    elif shortcut == "last-month":
        first_this = today.replace(day=1)
        last_prev = first_this - timedelta(days=1)
        first_prev = last_prev.replace(day=1)
        return str(first_prev), str(last_prev)
    elif shortcut == "this-year":
        return f"{today.year}-01-01", f"{today.year}-12-31"
    else:
        print(f"Error: Unknown date shortcut '{shortcut}'. Use: today, yesterday, this-week, last-week, this-month, last-month, this-year.", file=sys.stderr)
        sys.exit(1)


def add_date_filter_args(parser):
    """Add standard date filter arguments to a subparser."""
    parser.add_argument("--today", action="store_const", const="today", dest="date_shortcut", help="Filter to today")
    parser.add_argument("--yesterday", action="store_const", const="yesterday", dest="date_shortcut", help="Filter to yesterday")
    parser.add_argument("--this-week", action="store_const", const="this-week", dest="date_shortcut", help="Filter to this week")
    parser.add_argument("--last-week", action="store_const", const="last-week", dest="date_shortcut", help="Filter to last week")
    parser.add_argument("--this-month", action="store_const", const="this-month", dest="date_shortcut", help="Filter to this month")
    parser.add_argument("--last-month", action="store_const", const="last-month", dest="date_shortcut", help="Filter to last month")
    parser.add_argument("--this-year", action="store_const", const="this-year", dest="date_shortcut", help="Filter to this year")
    parser.add_argument("--date-from", help="Custom start date (YYYY-MM-DD)")
    parser.add_argument("--date-to", help="Custom end date (YYYY-MM-DD)")


def get_date_bounds(args):
    """Extract (date_from, date_to) from parsed args. Returns (None, None) if no filter."""
    shortcut = getattr(args, "date_shortcut", None)
    if shortcut:
        return date_range(shortcut)
    df = getattr(args, "date_from", None)
    dt = getattr(args, "date_to", None)
    return df, dt


# ---------------------------------------------------------------------------
# Log Notes & Schedule Activities
# ---------------------------------------------------------------------------
def log_note(uid, models, db, api_key, model, record_id, body):
    """Post an internal note (log note) on a record."""
    log(f"Posting note on {model}/{record_id}")
    msg_id = models.execute_kw(db, uid, api_key, model, "message_post", [record_id], {
        "body": body,
        "message_type": "comment",
        "subtype_xmlid": "mail.mt_note",
    })
    return msg_id


def schedule_activity(uid, models, db, api_key, model, record_id, user_id, summary,
                      note="", date_deadline=None, activity_type="mail.mail_activity_data_todo"):
    """Schedule an activity on a record for a specific user."""
    from datetime import date as _date
    # Get model ID
    model_ids = models.execute_kw(db, uid, api_key, "ir.model", "search",
                                  [[["model", "=", model]]], {"limit": 1})
    if not model_ids:
        print(f"Error: Model '{model}' not found in ir.model.", file=sys.stderr)
        sys.exit(1)

    # Get activity type ID
    act_type_ids = models.execute_kw(db, uid, api_key, "ir.model.data", "search_read",
                                     [[["complete_name", "=", activity_type]]],
                                     {"fields": ["res_id"], "limit": 1})
    act_type_id = act_type_ids[0]["res_id"] if act_type_ids else False

    vals = {
        "res_model_id": model_ids[0],
        "res_id": record_id,
        "user_id": user_id,
        "summary": summary,
        "note": note or "",
        "date_deadline": date_deadline or str(_date.today()),
    }
    if act_type_id:
        vals["activity_type_id"] = act_type_id

    log(f"Scheduling activity on {model}/{record_id} for user_id={user_id}")
    activity_id = models.execute_kw(db, uid, api_key, "mail.activity", "create", [vals])
    return activity_id


def test_connection():
    uid, models, db, api_key = connect()
    url = get_env("ODOO_URL").rstrip("/")
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", allow_none=True)
    version = common.version()
    output_json({
        "status": "connected", "uid": uid,
        "server_version": version.get("server_version", "unknown"),
    })


# ---------------------------------------------------------------------------
# Generic CLI (for uncommon models)
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="VNClaw — Odoo 17 Generic Client")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("test-connection", help="Test connection to Odoo")

    p = sub.add_parser("search-read", help="Search and read any model")
    p.add_argument("model")
    p.add_argument("--domain", default="[]")
    p.add_argument("--fields", default="[]")
    p.add_argument("--limit", type=int, default=80)
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--order", default="")

    p = sub.add_parser("read", help="Read records by ID")
    p.add_argument("model")
    p.add_argument("--ids", required=True)
    p.add_argument("--fields", default="[]")

    p = sub.add_parser("create", help="Create a record")
    p.add_argument("model")
    p.add_argument("--values", required=True)

    p = sub.add_parser("write", help="Update records")
    p.add_argument("model")
    p.add_argument("--ids", required=True)
    p.add_argument("--values", required=True)

    p = sub.add_parser("search", help="Search for IDs")
    p.add_argument("model")
    p.add_argument("--domain", default="[]")
    p.add_argument("--limit", type=int, default=80)
    p.add_argument("--offset", type=int, default=0)

    p = sub.add_parser("fields", help="Get field definitions")
    p.add_argument("model")
    p.add_argument("--attributes", default='["string","type","required","readonly","relation"]')

    p = sub.add_parser("count", help="Count matching records")
    p.add_argument("model")
    p.add_argument("--domain", default="[]")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "test-connection":
        test_connection()
    elif args.command == "search-read":
        uid, m, db, key = connect()
        kw = {"fields": json.loads(args.fields), "limit": args.limit, "offset": args.offset}
        if args.order:
            kw["order"] = args.order
        output_json(execute(uid, m, db, key, args.model, "search_read", json.loads(args.domain), **kw))
    elif args.command == "read":
        uid, m, db, key = connect()
        output_json(execute(uid, m, db, key, args.model, "read", json.loads(args.ids), **{"fields": json.loads(args.fields)}))
    elif args.command == "create":
        uid, m, db, key = connect()
        rid = execute(uid, m, db, key, args.model, "create", json.loads(args.values))
        output_json({"created_id": rid, "model": args.model})
    elif args.command == "write":
        uid, m, db, key = connect()
        ok = execute(uid, m, db, key, args.model, "write", json.loads(args.ids), json.loads(args.values))
        output_json({"updated_ids": json.loads(args.ids), "model": args.model, "success": ok})
    elif args.command == "search":
        uid, m, db, key = connect()
        ids = execute(uid, m, db, key, args.model, "search", json.loads(args.domain), **{"limit": args.limit, "offset": args.offset})
        output_json({"ids": ids, "count": len(ids)})
    elif args.command == "fields":
        uid, m, db, key = connect()
        output_json(execute(uid, m, db, key, args.model, "fields_get", **{"attributes": json.loads(args.attributes)}))
    elif args.command == "count":
        uid, m, db, key = connect()
        validate_operation(args.model, "search_read")
        c = m.execute_kw(db, uid, key, args.model, "search_count", [json.loads(args.domain)])
        output_json({"model": args.model, "count": c})


if __name__ == "__main__":
    main()
