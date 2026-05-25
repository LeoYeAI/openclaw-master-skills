#!/usr/bin/env python3
"""VNClaw — Helpdesk Tickets module (helpdesk.ticket)"""
import argparse, json, sys, os
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from odoo_core import (connect, execute, output_json, resolve_user, resolve_partner,
                       add_date_filter_args, get_date_bounds, log_note, schedule_activity, log)

MODEL = "helpdesk.ticket"
DEFAULT_FIELDS = ["id", "name", "partner_id", "user_id", "team_id", "stage_id",
                  "priority", "create_date", "description", "ticket_type_id", "tag_ids"]


def cmd_list(args):
    uid, m, db, key = connect()
    domain = []

    if args.my:
        domain.append(["user_id", "=", uid])
    if args.user:
        user_id = resolve_user(uid, m, db, key, args.user)
        domain.append(["user_id", "=", user_id])
    if args.customer:
        partner_id = resolve_partner(uid, m, db, key, args.customer)
        domain.append(["partner_id", "=", partner_id])
    if args.search:
        domain.append(["name", "ilike", args.search])
    if args.team:
        teams = execute(uid, m, db, key, "helpdesk.team", "search_read",
                        [["name", "ilike", args.team]], fields=["id"])
        if teams:
            domain.append(["team_id", "=", teams[0]["id"]])
        else:
            log(f"Warning: team '{args.team}' not found, ignoring filter")
    if args.stage:
        stages = execute(uid, m, db, key, "helpdesk.stage", "search_read",
                         [["name", "ilike", args.stage]], fields=["id"])
        if stages:
            domain.append(["stage_id", "in", [s["id"] for s in stages]])
        else:
            log(f"Warning: stage '{args.stage}' not found, ignoring filter")
    if args.priority:
        domain.append(["priority", "=", args.priority])

    # Date filters on create_date
    df, dt = get_date_bounds(args)
    if df:
        domain.append(["create_date", ">=", f"{df} 00:00:00"])
    if dt:
        domain.append(["create_date", "<=", f"{dt} 23:59:59"])

    fields = json.loads(args.fields) if args.fields else DEFAULT_FIELDS
    records = execute(uid, m, db, key, MODEL, "search_read", domain,
                      fields=fields, limit=args.limit, order="create_date desc")
    output_json(records)


def cmd_get(args):
    uid, m, db, key = connect()
    fields = json.loads(args.fields) if args.fields else DEFAULT_FIELDS + [
        "kanban_state", "sla_status_ids", "message_ids"
    ]
    records = execute(uid, m, db, key, MODEL, "read", [args.id], fields=fields)
    output_json(records[0] if records else {"error": f"Ticket {args.id} not found"})


def cmd_create(args):
    uid, m, db, key = connect()
    vals = {"name": args.name}
    if args.description:
        vals["description"] = args.description
    if args.assign:
        vals["user_id"] = resolve_user(uid, m, db, key, args.assign)
    if args.customer:
        vals["partner_id"] = resolve_partner(uid, m, db, key, args.customer)
    if args.team:
        teams = execute(uid, m, db, key, "helpdesk.team", "search_read",
                        [["name", "ilike", args.team]], fields=["id"])
        if teams:
            vals["team_id"] = teams[0]["id"]
    if args.priority:
        vals["priority"] = args.priority
    if args.ticket_type:
        types = execute(uid, m, db, key, "helpdesk.ticket.type", "search_read",
                        [["name", "ilike", args.ticket_type]], fields=["id"])
        if types:
            vals["ticket_type_id"] = types[0]["id"]
    if args.extra:
        vals.update(json.loads(args.extra))
    rid = execute(uid, m, db, key, MODEL, "create", vals)
    output_json({"created_id": rid, "name": args.name})


def cmd_update(args):
    uid, m, db, key = connect()
    vals = {}
    if args.name:
        vals["name"] = args.name
    if args.description:
        vals["description"] = args.description
    if args.assign:
        vals["user_id"] = resolve_user(uid, m, db, key, args.assign)
    if args.customer:
        vals["partner_id"] = resolve_partner(uid, m, db, key, args.customer)
    if args.stage:
        stages = execute(uid, m, db, key, "helpdesk.stage", "search_read",
                         [["name", "ilike", args.stage]], fields=["id"])
        if stages:
            vals["stage_id"] = stages[0]["id"]
    if args.priority:
        vals["priority"] = args.priority
    if args.team:
        teams = execute(uid, m, db, key, "helpdesk.team", "search_read",
                        [["name", "ilike", args.team]], fields=["id"])
        if teams:
            vals["team_id"] = teams[0]["id"]
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
    output_json({"logged_note": True, "ticket_id": args.id})


def cmd_notify(args):
    uid, m, db, key = connect()
    user_id = resolve_user(uid, m, db, key, args.user)
    schedule_activity(uid, m, db, key, MODEL, args.id, user_id, args.summary, args.note or "")
    output_json({"activity_scheduled": True, "ticket_id": args.id, "for_user": args.user})


def cmd_stages(args):
    uid, m, db, key = connect()
    stages = execute(uid, m, db, key, "helpdesk.stage", "search_read", [],
                     fields=["id", "name", "sequence"], order="sequence asc")
    output_json(stages)


def main():
    p = argparse.ArgumentParser(description="VNClaw — Helpdesk Tickets")
    sub = p.add_subparsers(dest="action")

    # list
    s = sub.add_parser("list", help="List helpdesk tickets")
    s.add_argument("--my", action="store_true", help="My assigned tickets only")
    s.add_argument("--user", help="Filter by assigned user NAME")
    s.add_argument("--customer", help="Filter by customer NAME")
    s.add_argument("--search", help="Search ticket name")
    s.add_argument("--team", help="Filter by team NAME")
    s.add_argument("--stage", help="Filter by stage NAME")
    s.add_argument("--priority", help="Priority: 0=Low, 1=Medium, 2=High, 3=Urgent")
    add_date_filter_args(s)
    s.add_argument("--fields", help="JSON array of fields")
    s.add_argument("--limit", type=int, default=50)

    # get
    s = sub.add_parser("get", help="Get ticket detail by ID")
    s.add_argument("id", type=int)
    s.add_argument("--fields", help="JSON array of fields")

    # create
    s = sub.add_parser("create", help="Create a helpdesk ticket")
    s.add_argument("--name", required=True, help="Ticket title")
    s.add_argument("--description")
    s.add_argument("--assign", help="Assign to user NAME")
    s.add_argument("--customer", help="Customer NAME")
    s.add_argument("--team", help="Team NAME")
    s.add_argument("--priority", help="0=Low, 1=Medium, 2=High, 3=Urgent")
    s.add_argument("--ticket-type", help="Ticket type NAME")
    s.add_argument("--extra", help="Additional fields as JSON")

    # update
    s = sub.add_parser("update", help="Update a helpdesk ticket")
    s.add_argument("id", type=int)
    s.add_argument("--name")
    s.add_argument("--description")
    s.add_argument("--assign", help="Assign to user NAME")
    s.add_argument("--customer", help="Customer NAME")
    s.add_argument("--stage", help="Stage NAME")
    s.add_argument("--priority")
    s.add_argument("--team", help="Team NAME")
    s.add_argument("--extra", help="Additional fields as JSON")

    # log-note
    s = sub.add_parser("log-note", help="Log internal note on a ticket")
    s.add_argument("id", type=int)
    s.add_argument("--body", required=True, help="Note body (HTML or plain text)")

    # notify
    s = sub.add_parser("notify", help="Schedule activity notification")
    s.add_argument("id", type=int)
    s.add_argument("--user", required=True, help="Target user NAME")
    s.add_argument("--summary", required=True, help="Activity summary")
    s.add_argument("--note", help="Activity note")

    # stages
    sub.add_parser("stages", help="List available stages")

    args = p.parse_args()
    if not args.action:
        p.print_help()
        sys.exit(1)
    {"list": cmd_list, "get": cmd_get, "create": cmd_create, "update": cmd_update,
     "log-note": cmd_log_note, "notify": cmd_notify, "stages": cmd_stages}[args.action](args)


if __name__ == "__main__":
    main()
