#!/usr/bin/env python3
"""VNClaw — Time Off module (hr.leave)"""
import argparse, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from odoo_core import (connect, execute, output_json, resolve_user, resolve_employee,
                       add_date_filter_args, get_date_bounds, log)

MODEL = "hr.leave"
DEFAULT_FIELDS = ["id", "name", "employee_id", "holiday_status_id", "state",
                  "date_from", "date_to", "number_of_days", "user_id"]


def _resolve_leave_type(uid, m, db, key, name):
    recs = execute(uid, m, db, key, "hr.leave.type", "search_read",
                   [["name", "ilike", name]], fields=["id", "name"])
    if not recs:
        print(f"Error: Leave type '{name}' not found.", file=sys.stderr)
        sys.exit(1)
    return recs[0]["id"]


def cmd_list(args):
    uid, m, db, key = connect()
    domain = []

    if args.my:
        domain.append(["user_id", "=", uid])
    if args.user:
        user_id = resolve_user(uid, m, db, key, args.user)
        domain.append(["user_id", "=", user_id])
    if args.employee:
        emp_id = resolve_employee(uid, m, db, key, args.employee)
        domain.append(["employee_id", "=", emp_id])
    if args.state:
        domain.append(["state", "=", args.state])
    if args.leave_type:
        lt_id = _resolve_leave_type(uid, m, db, key, args.leave_type)
        domain.append(["holiday_status_id", "=", lt_id])

    # Date filters on date_from
    df, dt = get_date_bounds(args)
    if df:
        domain.append(["date_from", ">=", f"{df} 00:00:00"])
    if dt:
        domain.append(["date_from", "<=", f"{dt} 23:59:59"])

    fields = json.loads(args.fields) if args.fields else DEFAULT_FIELDS
    records = execute(uid, m, db, key, MODEL, "search_read", domain,
                      fields=fields, limit=args.limit, order="date_from desc")
    output_json(records)


def cmd_get(args):
    uid, m, db, key = connect()
    fields = json.loads(args.fields) if args.fields else DEFAULT_FIELDS + [
        "notes", "department_id", "category_id", "payslip_status"
    ]
    records = execute(uid, m, db, key, MODEL, "read", [args.id], fields=fields)
    output_json(records[0] if records else {"error": f"Leave {args.id} not found"})


def cmd_create(args):
    uid, m, db, key = connect()
    vals = {
        "date_from": args.date_from,
        "date_to": args.date_to,
    }
    if args.name:
        vals["name"] = args.name
    if args.employee:
        vals["employee_id"] = resolve_employee(uid, m, db, key, args.employee)
    if args.leave_type:
        vals["holiday_status_id"] = _resolve_leave_type(uid, m, db, key, args.leave_type)
    if args.extra:
        vals.update(json.loads(args.extra))
    rid = execute(uid, m, db, key, MODEL, "create", vals)
    output_json({"created_id": rid, "date_from": args.date_from, "date_to": args.date_to})


def cmd_update(args):
    uid, m, db, key = connect()
    vals = {}
    if args.name:
        vals["name"] = args.name
    if args.date_from:
        vals["date_from"] = args.date_from
    if args.date_to:
        vals["date_to"] = args.date_to
    if args.leave_type:
        vals["holiday_status_id"] = _resolve_leave_type(uid, m, db, key, args.leave_type)
    if args.extra:
        vals.update(json.loads(args.extra))
    if not vals:
        print("Error: No fields to update.", file=sys.stderr)
        sys.exit(1)
    ok = execute(uid, m, db, key, MODEL, "write", [args.id], vals)
    output_json({"updated_id": args.id, "success": ok})


def cmd_leave_types(args):
    uid, m, db, key = connect()
    recs = execute(uid, m, db, key, "hr.leave.type", "search_read", [],
                   fields=["id", "name", "requires_allocation", "leave_validation_type"],
                   order="name asc")
    output_json(recs)


def main():
    p = argparse.ArgumentParser(description="VNClaw — Time Off (Leave Requests)")
    sub = p.add_subparsers(dest="action")

    # list
    s = sub.add_parser("list", help="List leave requests")
    s.add_argument("--my", action="store_true", help="My leave requests only")
    s.add_argument("--user", help="Filter by user NAME")
    s.add_argument("--employee", help="Filter by employee NAME")
    s.add_argument("--state", help="confirm, validate, refuse, draft, cancel")
    s.add_argument("--leave-type", help="Leave type NAME (e.g. 'Sick Time Off')")
    add_date_filter_args(s)
    s.add_argument("--fields", help="JSON array of fields")
    s.add_argument("--limit", type=int, default=50)

    # get
    s = sub.add_parser("get", help="Get leave request detail by ID")
    s.add_argument("id", type=int)
    s.add_argument("--fields", help="JSON array of fields")

    # create
    s = sub.add_parser("create", help="Create a leave request")
    s.add_argument("--name", help="Description/reason")
    s.add_argument("--date-from", required=True, help="Start (YYYY-MM-DD HH:MM:SS)")
    s.add_argument("--date-to", required=True, help="End (YYYY-MM-DD HH:MM:SS)")
    s.add_argument("--employee", help="Employee NAME (defaults to current user's employee)")
    s.add_argument("--leave-type", help="Leave type NAME")
    s.add_argument("--extra", help="Additional fields as JSON")

    # update
    s = sub.add_parser("update", help="Update a leave request (only in draft state)")
    s.add_argument("id", type=int)
    s.add_argument("--name")
    s.add_argument("--date-from")
    s.add_argument("--date-to")
    s.add_argument("--leave-type", help="Leave type NAME")
    s.add_argument("--extra", help="Additional fields as JSON")

    # leave-types
    sub.add_parser("leave-types", help="List available leave types")

    args = p.parse_args()
    if not args.action:
        p.print_help()
        sys.exit(1)
    {"list": cmd_list, "get": cmd_get, "create": cmd_create, "update": cmd_update,
     "leave-types": cmd_leave_types}[args.action](args)


if __name__ == "__main__":
    main()
