#!/usr/bin/env python3
"""VNClaw — Projects module (project.project)"""
import argparse, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from odoo_core import (connect, execute, output_json, resolve_user,
                       add_date_filter_args, get_date_bounds, log_note, schedule_activity, log)

MODEL = "project.project"
DEFAULT_FIELDS = ["id", "name", "user_id", "partner_id", "date_start", "date",
                  "task_count", "tag_ids", "stage_id", "active"]


def cmd_list(args):
    uid, m, db, key = connect()
    domain = []

    if args.my:
        domain.append(["user_id", "=", uid])
    if args.manager:
        manager_id = resolve_user(uid, m, db, key, args.manager)
        domain.append(["user_id", "=", manager_id])
    if args.search:
        domain.append(["name", "ilike", args.search])
    if args.stage:
        stages = execute(uid, m, db, key, "project.project.stage", "search_read",
                         [["name", "ilike", args.stage]], fields=["id"])
        if stages:
            domain.append(["stage_id", "in", [s["id"] for s in stages]])
    if args.active_only:
        domain.append(["active", "=", True])
    if args.favorites:
        domain.append(["is_favorite", "=", True])

    # Date filters on date_start or create_date
    df, dt = get_date_bounds(args)
    if df:
        domain.append(["create_date", ">=", f"{df} 00:00:00"])
    if dt:
        domain.append(["create_date", "<=", f"{dt} 23:59:59"])

    fields = json.loads(args.fields) if args.fields else DEFAULT_FIELDS
    records = execute(uid, m, db, key, MODEL, "search_read", domain,
                      fields=fields, limit=args.limit, order="name asc")
    output_json(records)


def cmd_get(args):
    uid, m, db, key = connect()
    fields = json.loads(args.fields) if args.fields else DEFAULT_FIELDS + [
        "description", "label_tasks", "allow_timesheets", "privacy_visibility",
        "analytic_account_id", "date_start", "date"
    ]
    records = execute(uid, m, db, key, MODEL, "read", [args.id], fields=fields)
    output_json(records[0] if records else {"error": f"Project {args.id} not found"})


def cmd_create(args):
    uid, m, db, key = connect()
    vals = {"name": args.name}
    if args.manager:
        vals["user_id"] = resolve_user(uid, m, db, key, args.manager)
    if args.description:
        vals["description"] = args.description
    if args.privacy:
        vals["privacy_visibility"] = args.privacy
    if args.allow_timesheets:
        vals["allow_timesheets"] = True
    if args.date_start:
        vals["date_start"] = args.date_start
    if args.date_end:
        vals["date"] = args.date_end
    if args.extra:
        vals.update(json.loads(args.extra))
    rid = execute(uid, m, db, key, MODEL, "create", vals)
    output_json({"created_id": rid, "name": args.name})


def cmd_update(args):
    uid, m, db, key = connect()
    vals = {}
    if args.name:
        vals["name"] = args.name
    if args.manager:
        vals["user_id"] = resolve_user(uid, m, db, key, args.manager)
    if args.description:
        vals["description"] = args.description
    if args.stage:
        stages = execute(uid, m, db, key, "project.project.stage", "search_read",
                         [["name", "ilike", args.stage]], fields=["id"])
        if stages:
            vals["stage_id"] = stages[0]["id"]
    if args.privacy:
        vals["privacy_visibility"] = args.privacy
    if args.date_start:
        vals["date_start"] = args.date_start
    if args.date_end:
        vals["date"] = args.date_end
    if args.extra:
        vals.update(json.loads(args.extra))
    if not vals:
        print("Error: No fields to update.", file=sys.stderr)
        sys.exit(1)
    ok = execute(uid, m, db, key, MODEL, "write", [args.id], vals)
    output_json({"updated_id": args.id, "success": ok})


def cmd_log_note(args):
    uid, m, db, key = connect()
    log_note(uid, m, db, key, MODEL, args.id, args.body)
    output_json({"logged_note": True, "project_id": args.id})


def cmd_notify(args):
    uid, m, db, key = connect()
    user_id = resolve_user(uid, m, db, key, args.user)
    schedule_activity(uid, m, db, key, MODEL, args.id, user_id, args.summary, args.note or "")
    output_json({"activity_scheduled": True, "project_id": args.id, "for_user": args.user})


def cmd_stages(args):
    uid, m, db, key = connect()
    recs = execute(uid, m, db, key, "project.project.stage", "search_read", [],
                   fields=["id", "name"], order="id asc")
    output_json(recs)


def main():
    p = argparse.ArgumentParser(description="VNClaw — Projects")
    sub = p.add_subparsers(dest="action")

    # list
    s = sub.add_parser("list", help="List projects")
    s.add_argument("--my", action="store_true", help="Projects I manage")
    s.add_argument("--manager", help="Filter by manager NAME")
    s.add_argument("--search", help="Search project name")
    s.add_argument("--stage", help="Filter by stage NAME")
    s.add_argument("--active-only", action="store_true", help="Active projects only")
    s.add_argument("--favorites", action="store_true", help="Favorites only")
    add_date_filter_args(s)
    s.add_argument("--fields", help="JSON array of fields")
    s.add_argument("--limit", type=int, default=50)

    # get
    s = sub.add_parser("get", help="Get project detail by ID")
    s.add_argument("id", type=int)
    s.add_argument("--fields", help="JSON array of fields")

    # create
    s = sub.add_parser("create", help="Create a project")
    s.add_argument("--name", required=True, help="Project name")
    s.add_argument("--manager", help="Manager NAME")
    s.add_argument("--description")
    s.add_argument("--privacy", help="portal, employees, followers")
    s.add_argument("--allow-timesheets", action="store_true")
    s.add_argument("--date-start", help="Start date (YYYY-MM-DD)")
    s.add_argument("--date-end", help="End date (YYYY-MM-DD)")
    s.add_argument("--extra", help="Additional fields as JSON")

    # update
    s = sub.add_parser("update", help="Update a project")
    s.add_argument("id", type=int)
    s.add_argument("--name")
    s.add_argument("--manager", help="Manager NAME")
    s.add_argument("--description")
    s.add_argument("--stage", help="Stage NAME")
    s.add_argument("--privacy", help="portal, employees, followers")
    s.add_argument("--date-start")
    s.add_argument("--date-end")
    s.add_argument("--extra", help="Additional fields as JSON")

    # log-note
    s = sub.add_parser("log-note", help="Log internal note on project")
    s.add_argument("id", type=int)
    s.add_argument("--body", required=True, help="Note body (HTML or plain text)")

    # notify
    s = sub.add_parser("notify", help="Schedule activity notification")
    s.add_argument("id", type=int)
    s.add_argument("--user", required=True, help="Target user NAME")
    s.add_argument("--summary", required=True, help="Activity summary")
    s.add_argument("--note", help="Activity note")

    # stages
    sub.add_parser("stages", help="List project stages")

    args = p.parse_args()
    if not args.action:
        p.print_help()
        sys.exit(1)
    {"list": cmd_list, "get": cmd_get, "create": cmd_create, "update": cmd_update,
     "log-note": cmd_log_note, "notify": cmd_notify, "stages": cmd_stages}[args.action](args)


if __name__ == "__main__":
    main()
