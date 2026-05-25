#!/usr/bin/env python3
"""VNClaw — Knowledge Articles module (knowledge.article)"""
import argparse, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from odoo_core import (connect, execute, output_json, resolve_user, log)

MODEL = "knowledge.article"
DEFAULT_FIELDS = ["id", "name", "create_uid", "write_date", "is_published",
                  "parent_id", "sequence", "category"]


def cmd_list(args):
    uid, m, db, key = connect()
    domain = []

    if args.my:
        domain.append(["create_uid", "=", uid])
    if args.author:
        author_id = resolve_user(uid, m, db, key, args.author)
        domain.append(["create_uid", "=", author_id])
    if args.published:
        domain.append(["is_published", "=", True])
    if args.search:
        domain.append(["name", "ilike", args.search])
    if args.parent_id:
        domain.append(["parent_id", "=", args.parent_id])
    if args.root_only:
        domain.append(["parent_id", "=", False])
    if args.category:
        domain.append(["category", "=", args.category])

    fields = json.loads(args.fields) if args.fields else DEFAULT_FIELDS
    records = execute(uid, m, db, key, MODEL, "search_read", domain,
                      fields=fields, limit=args.limit, order="sequence asc, write_date desc")
    output_json(records)


def cmd_get(args):
    uid, m, db, key = connect()
    fields = json.loads(args.fields) if args.fields else DEFAULT_FIELDS + [
        "body", "icon", "child_ids", "is_article_item", "article_member_ids"
    ]
    records = execute(uid, m, db, key, MODEL, "read", [args.id], fields=fields)
    output_json(records[0] if records else {"error": f"Article {args.id} not found"})


def cmd_create(args):
    uid, m, db, key = connect()
    vals = {"name": args.name}
    if args.body:
        vals["body"] = args.body
    if args.parent_id:
        vals["parent_id"] = args.parent_id
    if args.parent_name:
        parents = execute(uid, m, db, key, MODEL, "search_read",
                          [["name", "ilike", args.parent_name]], fields=["id"], limit=1)
        if parents:
            vals["parent_id"] = parents[0]["id"]
        else:
            log(f"Warning: parent article '{args.parent_name}' not found, creating as root")
    if args.is_published:
        vals["is_published"] = True
    if args.icon:
        vals["icon"] = args.icon
    if args.extra:
        vals.update(json.loads(args.extra))
    rid = execute(uid, m, db, key, MODEL, "create", vals)
    output_json({"created_id": rid, "name": args.name})


def cmd_update(args):
    uid, m, db, key = connect()
    vals = {}
    if args.name:
        vals["name"] = args.name
    if args.body:
        vals["body"] = args.body
    if args.parent_id is not None:
        vals["parent_id"] = args.parent_id if args.parent_id > 0 else False
    if args.is_published is not None:
        vals["is_published"] = args.is_published
    if args.icon:
        vals["icon"] = args.icon
    if args.extra:
        vals.update(json.loads(args.extra))
    if not vals:
        print("Error: No fields to update.", file=sys.stderr)
        sys.exit(1)
    ok = execute(uid, m, db, key, MODEL, "write", [args.id], vals)
    output_json({"updated_id": args.id, "success": ok})


def main():
    p = argparse.ArgumentParser(description="VNClaw — Knowledge Articles")
    sub = p.add_subparsers(dest="action")

    # list
    s = sub.add_parser("list", help="List knowledge articles")
    s.add_argument("--my", action="store_true", help="My articles only")
    s.add_argument("--author", help="Filter by author NAME")
    s.add_argument("--published", action="store_true", help="Published articles only")
    s.add_argument("--search", help="Search title")
    s.add_argument("--parent-id", type=int, help="Filter by parent article ID")
    s.add_argument("--root-only", action="store_true", help="Only root-level articles")
    s.add_argument("--category", help="Filter by category: workspace, private, shared")
    s.add_argument("--fields", help="JSON array of fields")
    s.add_argument("--limit", type=int, default=50)

    # get
    s = sub.add_parser("get", help="Get article by ID (includes body)")
    s.add_argument("id", type=int)
    s.add_argument("--fields", help="JSON array of fields")

    # create
    s = sub.add_parser("create", help="Create a knowledge article")
    s.add_argument("--name", required=True, help="Article title")
    s.add_argument("--body", help="Article content (HTML)")
    s.add_argument("--parent-id", type=int, help="Parent article ID")
    s.add_argument("--parent-name", help="Parent article NAME (alternative)")
    s.add_argument("--is-published", action="store_true")
    s.add_argument("--icon", help="Emoji icon")
    s.add_argument("--extra", help="Additional fields as JSON")

    # update
    s = sub.add_parser("update", help="Update a knowledge article")
    s.add_argument("id", type=int)
    s.add_argument("--name")
    s.add_argument("--body", help="New content (HTML)")
    s.add_argument("--parent-id", type=int, help="New parent ID (0 = root)")
    s.add_argument("--is-published", type=bool, help="true/false")
    s.add_argument("--icon")
    s.add_argument("--extra", help="Additional fields as JSON")

    args = p.parse_args()
    if not args.action:
        p.print_help()
        sys.exit(1)
    {"list": cmd_list, "get": cmd_get, "create": cmd_create, "update": cmd_update}[args.action](args)


if __name__ == "__main__":
    main()
