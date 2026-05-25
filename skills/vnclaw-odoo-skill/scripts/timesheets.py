#!/usr/bin/env python3
"""VNClaw — Timesheets module (account.analytic.line)"""
import argparse, json, sys, os
from datetime import date, timedelta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from odoo_core import (connect, execute, output_json, resolve_user, resolve_employee,
                       resolve_project, add_date_filter_args, get_date_bounds, log)

MODEL = "account.analytic.line"
DEFAULT_FIELDS = ["id", "employee_id", "project_id", "task_id", "name", "date", "unit_amount"]


def cmd_list(args):
    uid, m, db, key = connect()
    domain = [["project_id", "!=", False]]

    # --my
    if args.my:
        domain.append(["user_id", "=", uid])

    # --user by name
    if args.user:
        user_id = resolve_user(uid, m, db, key, args.user)
        domain.append(["user_id", "=", user_id])

    # --employee by name
    if args.employee:
        emp_id = resolve_employee(uid, m, db, key, args.employee)
        domain.append(["employee_id", "=", emp_id])
    elif args.employee_id:
        domain.append(["employee_id", "=", args.employee_id])

    # --project by name / --project-id
    if args.project:
        pid = resolve_project(uid, m, db, key, args.project)
        domain.append(["project_id", "=", pid])
    elif args.project_id:
        domain.append(["project_id", "=", args.project_id])

    if args.task_id:
        domain.append(["task_id", "=", args.task_id])

    # Date filters
    df, dt = get_date_bounds(args)
    if df:
        domain.append(["date", ">=", df])
    if dt:
        domain.append(["date", "<=", dt])

    fields = json.loads(args.fields) if args.fields else DEFAULT_FIELDS
    records = execute(uid, m, db, key, MODEL, "search_read", domain,
                      fields=fields, limit=args.limit, offset=args.offset, order="date desc")
    output_json(records)


def cmd_summary(args):
    """Show total hours grouped by project (and optionally task)."""
    uid, m, db, key = connect()
    domain = [["project_id", "!=", False]]

    if args.my:
        domain.append(["user_id", "=", uid])
    if args.user:
        user_id = resolve_user(uid, m, db, key, args.user)
        domain.append(["user_id", "=", user_id])
    if args.project:
        pid = resolve_project(uid, m, db, key, args.project)
        domain.append(["project_id", "=", pid])
    elif args.project_id:
        domain.append(["project_id", "=", args.project_id])

    df, dt = get_date_bounds(args)
    if df:
        domain.append(["date", ">=", df])
    if dt:
        domain.append(["date", "<=", dt])

    records = execute(uid, m, db, key, MODEL, "search_read", domain,
                      fields=["project_id", "task_id", "unit_amount"], limit=500)

    # Aggregate
    by_project = {}
    for r in records:
        proj_name = r["project_id"][1] if r["project_id"] else "No Project"
        task_name = r["task_id"][1] if r["task_id"] else "No Task"
        by_project.setdefault(proj_name, {"total": 0, "tasks": {}})
        by_project[proj_name]["total"] += r["unit_amount"]
        by_project[proj_name]["tasks"].setdefault(task_name, 0)
        by_project[proj_name]["tasks"][task_name] += r["unit_amount"]

    grand_total = sum(p["total"] for p in by_project.values())
    output_json({"projects": by_project, "grand_total_hours": round(grand_total, 2)})


def cmd_log(args):
    uid, m, db, key = connect()

    # Resolve project
    if args.project:
        project_id = resolve_project(uid, m, db, key, args.project)
    else:
        project_id = args.project_id

    vals = {
        "project_id": project_id,
        "name": args.description,
        "date": args.date or str(date.today()),
        "unit_amount": args.hours,
    }
    if args.task_id:
        vals["task_id"] = args.task_id
    if args.extra:
        vals.update(json.loads(args.extra))
    rid = execute(uid, m, db, key, MODEL, "create", vals)
    output_json({"created_id": rid, "hours": args.hours, "date": vals["date"]})


def cmd_update(args):
    uid, m, db, key = connect()
    vals = {}
    if args.hours is not None:
        vals["unit_amount"] = args.hours
    if args.description:
        vals["name"] = args.description
    if args.date:
        vals["date"] = args.date
    if args.extra:
        vals.update(json.loads(args.extra))
    if not vals:
        print("Error: No fields to update.", file=sys.stderr)
        sys.exit(1)
    ok = execute(uid, m, db, key, MODEL, "write", [args.id], vals)
    output_json({"updated_id": args.id, "success": ok})


def main():
    p = argparse.ArgumentParser(description="VNClaw — Timesheet Management")
    sub = p.add_subparsers(dest="action")

    # list
    s = sub.add_parser("list", help="List timesheet entries")
    s.add_argument("--my", action="store_true", help="My timesheets only")
    s.add_argument("--user", help="Filter by user NAME")
    s.add_argument("--employee", help="Filter by employee NAME")
    s.add_argument("--employee-id", type=int)
    s.add_argument("--project", help="Filter by project NAME")
    s.add_argument("--project-id", type=int)
    s.add_argument("--task-id", type=int)
    add_date_filter_args(s)
    s.add_argument("--fields", help="JSON array of fields")
    s.add_argument("--limit", type=int, default=100)
    s.add_argument("--offset", type=int, default=0)

    # summary
    s = sub.add_parser("summary", help="Show hours summary grouped by project/task")
    s.add_argument("--my", action="store_true", help="My timesheets only")
    s.add_argument("--user", help="Filter by user NAME")
    s.add_argument("--project", help="Filter by project NAME")
    s.add_argument("--project-id", type=int)
    add_date_filter_args(s)

    # log
    s = sub.add_parser("log", help="Log a timesheet entry")
    s.add_argument("--project", help="Project NAME (resolved automatically)")
    s.add_argument("--project-id", type=int, help="Project ID (alternative to --project)")
    s.add_argument("--task-id", type=int, help="Task ID (optional)")
    s.add_argument("--description", required=True, help="Work description")
    s.add_argument("--hours", type=float, required=True, help="Hours spent")
    s.add_argument("--date", help="Date (YYYY-MM-DD, default: today)")
    s.add_argument("--extra", help="Additional fields as JSON")

    # update
    s = sub.add_parser("update", help="Update a timesheet entry")
    s.add_argument("id", type=int)
    s.add_argument("--hours", type=float)
    s.add_argument("--description")
    s.add_argument("--date")
    s.add_argument("--extra", help="Additional fields as JSON")

    args = p.parse_args()
    if not args.action:
        p.print_help()
        sys.exit(1)
    {"list": cmd_list, "summary": cmd_summary, "log": cmd_log, "update": cmd_update}[args.action](args)


if __name__ == "__main__":
    main()
