#!/usr/bin/env python3
"""VNClaw — Tasks module (project.task)"""
import argparse, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from odoo_core import (connect, execute, output_json, resolve_user, resolve_project,
                       resolve_users_multi, add_date_filter_args, get_date_bounds,
                       log_note, schedule_activity, log)

MODEL = "project.task"
DEFAULT_FIELDS = ["id", "name", "project_id", "user_ids", "stage_id",
                  "date_deadline", "create_date", "priority", "tag_ids"]

# Map friendly --date-field values to actual Odoo field names
_DATE_FIELD_MAP = {
    "deadline": "date_deadline",
    "created":  "create_date",
    "updated":  "write_date",
}


def cmd_list(args):
    uid, m, db, key = connect()
    domain = []

    # --my: current user's tasks
    if args.my:
        domain.append(["user_ids", "in", [uid]])

    # --user: resolve by name
    if args.user:
        user_id = resolve_user(uid, m, db, key, args.user)
        domain.append(["user_ids", "in", [user_id]])

    # --project / --project-id
    if args.project:
        pid = resolve_project(uid, m, db, key, args.project)
        domain.append(["project_id", "=", pid])
    elif args.project_id:
        domain.append(["project_id", "=", args.project_id])

    # --stage
    if args.stage:
        domain.append(["stage_id.name", "ilike", args.stage])

    # --search
    if args.search:
        domain.append(["name", "ilike", args.search])

    # --overdue
    if args.overdue:
        from datetime import date
        domain.append(["date_deadline", "<", str(date.today())])
        domain.append(["stage_id.is_closed", "=", False])

    # --priority
    if args.priority:
        domain.append(["priority", "=", args.priority])

    # --tag
    if args.tag:
        domain.append(["tag_ids.name", "ilike", args.tag])

    # Date filters — field selected by --date-field (deadline / created / updated)
    date_field = _DATE_FIELD_MAP.get(getattr(args, "date_field", "deadline") or "deadline", "date_deadline")
    df, dt = get_date_bounds(args)
    if df:
        date_val_from = f"{df} 00:00:00" if date_field != "date_deadline" else df
        domain.append([date_field, ">=", date_val_from])
    if dt:
        date_val_to = f"{dt} 23:59:59" if date_field != "date_deadline" else dt
        domain.append([date_field, "<=", date_val_to])

    if args.active_only:
        domain.append(["active", "=", True])

    fields = json.loads(args.fields) if args.fields else DEFAULT_FIELDS
    records = execute(uid, m, db, key, MODEL, "search_read", domain,
                      fields=fields, limit=args.limit, offset=args.offset,
                      order=args.order or "priority desc, date_deadline asc")
    output_json(records)


def cmd_get(args):
    uid, m, db, key = connect()
    fields = json.loads(args.fields) if args.fields else DEFAULT_FIELDS + [
        "description", "child_ids", "parent_id", "activity_ids",
        "allocated_hours", "effective_hours", "remaining_hours",
        "timesheet_ids",
    ]
    # Fetch available fields first to avoid crashing on missing optional fields
    try:
        available = set(execute(uid, m, db, key, MODEL, "fields_get", [],
                                attributes=["type"]).keys())
        fields = [f for f in fields if f in available]
    except Exception:
        pass
    records = execute(uid, m, db, key, MODEL, "read", [args.id], fields=fields)
    output_json(records[0] if records else {"error": f"Task {args.id} not found"})


def cmd_create(args):
    uid, m, db, key = connect()

    # Resolve project by name or ID
    if args.project:
        project_id = resolve_project(uid, m, db, key, args.project)
    else:
        project_id = args.project_id

    vals = {"name": args.name, "project_id": project_id}

    # --assign: resolve user names
    if args.assign:
        user_ids = resolve_users_multi(uid, m, db, key, args.assign)
        vals["user_ids"] = [[6, 0, user_ids]]
    elif args.user_ids:
        vals["user_ids"] = [[6, 0, json.loads(args.user_ids)]]

    if args.deadline:
        vals["date_deadline"] = args.deadline
    if args.description:
        vals["description"] = args.description
    if args.priority:
        vals["priority"] = args.priority
    if args.planned_hours:
        vals["allocated_hours"] = args.planned_hours
    if args.parent_id:
        vals["parent_id"] = args.parent_id
    if args.extra:
        vals.update(json.loads(args.extra))
    rid = execute(uid, m, db, key, MODEL, "create", vals)
    output_json({"created_id": rid, "name": args.name})


def cmd_update(args):
    uid, m, db, key = connect()
    vals = {}
    if args.name:
        vals["name"] = args.name
    if args.stage_id:
        vals["stage_id"] = args.stage_id
    if args.stage:
        # Resolve stage by name
        stages = execute(uid, m, db, key, "project.task.type", "search_read",
                         [["name", "ilike", args.stage]], fields=["id", "name"], limit=1)
        if stages:
            vals["stage_id"] = stages[0]["id"]
        else:
            print(f"Error: No stage matching '{args.stage}'.", file=sys.stderr)
            sys.exit(1)
    if args.assign:
        user_ids = resolve_users_multi(uid, m, db, key, args.assign)
        vals["user_ids"] = [[6, 0, user_ids]]
    elif args.user_ids:
        vals["user_ids"] = [[6, 0, json.loads(args.user_ids)]]
    if args.priority:
        vals["priority"] = args.priority
    if args.deadline:
        vals["date_deadline"] = args.deadline
    if args.description:
        vals["description"] = args.description
    if args.extra:
        vals.update(json.loads(args.extra))
    if not vals:
        print("Error: No fields to update.", file=sys.stderr)
        sys.exit(1)
    ok = execute(uid, m, db, key, MODEL, "write", [args.id], vals)
    output_json({"updated_id": args.id, "success": ok, "fields_updated": list(vals.keys())})


def cmd_log_note(args):
    """Post an internal note on a task."""
    uid, m, db, key = connect()
    msg_id = log_note(uid, m, db, key, MODEL, args.id, args.message)
    output_json({"task_id": args.id, "message_id": msg_id, "status": "note posted"})


def cmd_notify(args):
    """Schedule an activity notification for a user on a task."""
    uid, m, db, key = connect()
    user_id = resolve_user(uid, m, db, key, args.user)
    act_id = schedule_activity(uid, m, db, key, MODEL, args.id, user_id,
                               summary=args.summary, note=args.note or "",
                               date_deadline=args.deadline)
    output_json({"task_id": args.id, "activity_id": act_id, "assigned_to": args.user, "summary": args.summary})


def cmd_stages(args):
    """List available task stages."""
    uid, m, db, key = connect()
    domain = []
    if args.project_id:
        domain.append(["project_ids", "in", [args.project_id]])
    records = execute(uid, m, db, key, "project.task.type", "search_read", domain,
                      fields=["id", "name", "sequence", "fold"], limit=100, order="sequence asc")
    output_json(records)


def main():
    p = argparse.ArgumentParser(description="VNClaw — Task Management")
    sub = p.add_subparsers(dest="action")

    # list
    s = sub.add_parser("list", help="List tasks")
    s.add_argument("--my", action="store_true", help="My tasks (current user)")
    s.add_argument("--user", help="Filter by user NAME (partial match)")
    s.add_argument("--project", help="Filter by project NAME (partial match)")
    s.add_argument("--project-id", type=int, help="Filter by project ID")
    s.add_argument("--stage", help="Filter by stage name (partial match)")
    s.add_argument("--search", help="Search task name (partial match)")
    s.add_argument("--overdue", action="store_true", help="Only overdue tasks")
    s.add_argument("--priority", choices=["0", "1"], help="Filter by priority")
    s.add_argument("--tag", help="Filter by tag name")
    add_date_filter_args(s)
    s.add_argument("--date-field", choices=["deadline", "created", "updated"], default="deadline",
                   help="Which date to filter on: deadline (default), created, or updated")
    s.add_argument("--active-only", action="store_true", default=True)
    s.add_argument("--fields", help="JSON array of fields")
    s.add_argument("--limit", type=int, default=50)
    s.add_argument("--offset", type=int, default=0)
    s.add_argument("--order", default="")

    # get
    s = sub.add_parser("get", help="Get task by ID")
    s.add_argument("id", type=int)
    s.add_argument("--fields", help="JSON array of fields")

    # create
    s = sub.add_parser("create", help="Create a task")
    s.add_argument("--name", required=True, help="Task name")
    s.add_argument("--project", help="Project NAME (resolved automatically)")
    s.add_argument("--project-id", type=int, help="Project ID (alternative to --project)")
    s.add_argument("--assign", help="Assignee names, comma-separated (e.g. 'Alice, Bob')")
    s.add_argument("--user-ids", help="Assignee IDs as JSON array (alternative to --assign)")
    s.add_argument("--deadline", help="Deadline (YYYY-MM-DD)")
    s.add_argument("--description", help="Task description")
    s.add_argument("--priority", choices=["0", "1"], help="0=Normal, 1=Important")
    s.add_argument("--planned-hours", type=float, help="Planned/allocated hours")
    s.add_argument("--parent-id", type=int, help="Parent task ID (sub-task)")
    s.add_argument("--extra", help="Additional fields as JSON object")

    # update
    s = sub.add_parser("update", help="Update a task")
    s.add_argument("id", type=int, help="Task ID")
    s.add_argument("--name", help="New name")
    s.add_argument("--stage-id", type=int, help="New stage ID")
    s.add_argument("--stage", help="New stage NAME (resolved automatically)")
    s.add_argument("--assign", help="New assignees by name, comma-separated")
    s.add_argument("--user-ids", help="New assignee IDs as JSON array")
    s.add_argument("--priority", choices=["0", "1"])
    s.add_argument("--deadline", help="New deadline (YYYY-MM-DD)")
    s.add_argument("--description")
    s.add_argument("--extra", help="Additional fields as JSON object")

    # log-note
    s = sub.add_parser("log-note", help="Post an internal note on a task")
    s.add_argument("id", type=int, help="Task ID")
    s.add_argument("--message", required=True, help="Note content (plain text or HTML)")

    # notify
    s = sub.add_parser("notify", help="Schedule an activity notification on a task")
    s.add_argument("id", type=int, help="Task ID")
    s.add_argument("--user", required=True, help="User NAME to notify")
    s.add_argument("--summary", required=True, help="Activity summary")
    s.add_argument("--note", help="Detailed note")
    s.add_argument("--deadline", help="Due date (YYYY-MM-DD, default: today)")

    # stages
    s = sub.add_parser("stages", help="List available task stages")
    s.add_argument("--project-id", type=int, help="Filter stages by project ID")

    args = p.parse_args()
    if not args.action:
        p.print_help()
        sys.exit(1)
    actions = {
        "list": cmd_list, "get": cmd_get, "create": cmd_create, "update": cmd_update,
        "log-note": cmd_log_note, "notify": cmd_notify, "stages": cmd_stages,
    }
    actions[args.action](args)


if __name__ == "__main__":
    main()
