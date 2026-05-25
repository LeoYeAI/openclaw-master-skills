#!/usr/bin/env python3
"""VNClaw — Calendar Events module (calendar.event)"""
import argparse, json, sys, os
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from odoo_core import (connect, execute, output_json, resolve_user, resolve_partner,
                       resolve_users_multi, add_date_filter_args, get_date_bounds,
                       log_note, schedule_activity, log)

MODEL = "calendar.event"
DEFAULT_FIELDS = ["id", "name", "start", "stop", "allday", "location", "partner_ids", "user_id", "description"]


def cmd_list(args):
    uid, m, db, key = connect()
    domain = []

    # --my: events where I'm an attendee or organizer
    if args.my:
        # Get current user's partner_id
        user_rec = execute(uid, m, db, key, "res.users", "read", [uid], fields=["partner_id"])
        if user_rec:
            partner_id = user_rec[0]["partner_id"][0]
            domain.append(["partner_ids", "in", [partner_id]])

    # --attendee: filter by attendee name
    if args.attendee:
        partner_id = resolve_partner(uid, m, db, key, args.attendee)
        domain.append(["partner_ids", "in", [partner_id]])

    # --organizer: filter by organizer name
    if args.organizer:
        org_id = resolve_user(uid, m, db, key, args.organizer)
        domain.append(["user_id", "=", org_id])

    # --search
    if args.search:
        domain.append(["name", "ilike", args.search])

    # Date filters
    df, dt = get_date_bounds(args)
    if df:
        domain.append(["start", ">=", f"{df} 00:00:00"])
    if dt:
        domain.append(["start", "<=", f"{dt} 23:59:59"])

    fields = json.loads(args.fields) if args.fields else DEFAULT_FIELDS
    records = execute(uid, m, db, key, MODEL, "search_read", domain,
                      fields=fields, limit=args.limit, order="start asc")
    output_json(records)


def cmd_get(args):
    uid, m, db, key = connect()
    fields = json.loads(args.fields) if args.fields else DEFAULT_FIELDS + [
        "duration", "privacy", "show_as", "alarm_ids", "categ_ids",
        "videocall_location", "recurrency"
    ]
    records = execute(uid, m, db, key, MODEL, "read", [args.id], fields=fields)
    output_json(records[0] if records else {"error": f"Event {args.id} not found"})


def cmd_create(args):
    uid, m, db, key = connect()
    vals = {"name": args.name, "start": args.start, "stop": args.stop}
    if args.location:
        vals["location"] = args.location
    if args.description:
        vals["description"] = args.description

    # --attendees: resolve names
    if args.attendees:
        names = [n.strip() for n in args.attendees.split(",") if n.strip()]
        partner_ids = [resolve_partner(uid, m, db, key, n) for n in names]
        vals["partner_ids"] = [[6, 0, partner_ids]]
    elif args.partner_ids:
        vals["partner_ids"] = [[6, 0, json.loads(args.partner_ids)]]

    if args.allday:
        vals["allday"] = True
    if args.extra:
        vals.update(json.loads(args.extra))
    rid = execute(uid, m, db, key, MODEL, "create", vals)
    output_json({"created_id": rid, "name": args.name, "start": args.start})


def cmd_update(args):
    uid, m, db, key = connect()
    vals = {}
    if args.name:
        vals["name"] = args.name
    if args.start:
        vals["start"] = args.start
    if args.stop:
        vals["stop"] = args.stop
    if args.location:
        vals["location"] = args.location
    if args.description:
        vals["description"] = args.description
    if args.attendees:
        names = [n.strip() for n in args.attendees.split(",") if n.strip()]
        partner_ids = [resolve_partner(uid, m, db, key, n) for n in names]
        vals["partner_ids"] = [[6, 0, partner_ids]]
    elif args.partner_ids:
        vals["partner_ids"] = [[6, 0, json.loads(args.partner_ids)]]
    if args.extra:
        vals.update(json.loads(args.extra))
    if not vals:
        print("Error: No fields to update.", file=sys.stderr)
        sys.exit(1)
    ok = execute(uid, m, db, key, MODEL, "write", [args.id], vals)
    output_json({"updated_id": args.id, "success": ok})


def main():
    p = argparse.ArgumentParser(description="VNClaw — Calendar Events")
    sub = p.add_subparsers(dest="action")

    # list
    s = sub.add_parser("list", help="List calendar events")
    s.add_argument("--my", action="store_true", help="My events only")
    s.add_argument("--attendee", help="Filter by attendee NAME")
    s.add_argument("--organizer", help="Filter by organizer NAME")
    s.add_argument("--search", help="Search event name")
    add_date_filter_args(s)
    s.add_argument("--fields", help="JSON array of fields")
    s.add_argument("--limit", type=int, default=50)

    # get
    s = sub.add_parser("get", help="Get event by ID")
    s.add_argument("id", type=int)
    s.add_argument("--fields", help="JSON array of fields")

    # create
    s = sub.add_parser("create", help="Create a calendar event")
    s.add_argument("--name", required=True, help="Event title")
    s.add_argument("--start", required=True, help="Start datetime (YYYY-MM-DD HH:MM:SS)")
    s.add_argument("--stop", required=True, help="End datetime (YYYY-MM-DD HH:MM:SS)")
    s.add_argument("--location")
    s.add_argument("--description")
    s.add_argument("--attendees", help="Attendee names, comma-separated (e.g. 'Alice, Bob')")
    s.add_argument("--partner-ids", help="Attendee partner IDs as JSON array (alternative)")
    s.add_argument("--allday", action="store_true")
    s.add_argument("--extra", help="Additional fields as JSON")

    # update
    s = sub.add_parser("update", help="Update a calendar event")
    s.add_argument("id", type=int)
    s.add_argument("--name")
    s.add_argument("--start")
    s.add_argument("--stop")
    s.add_argument("--location")
    s.add_argument("--description")
    s.add_argument("--attendees", help="New attendee names, comma-separated")
    s.add_argument("--partner-ids", help="New attendee IDs as JSON array")
    s.add_argument("--extra", help="Additional fields as JSON")

    args = p.parse_args()
    if not args.action:
        p.print_help()
        sys.exit(1)
    {"list": cmd_list, "get": cmd_get, "create": cmd_create, "update": cmd_update}[args.action](args)


if __name__ == "__main__":
    main()
