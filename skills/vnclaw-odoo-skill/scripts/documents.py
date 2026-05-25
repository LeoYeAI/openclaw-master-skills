#!/usr/bin/env python3
"""VNClaw — Documents module (documents.document)"""
import argparse, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from odoo_core import (connect, execute, output_json, resolve_user, resolve_partner,
                       add_date_filter_args, get_date_bounds, log)

MODEL = "documents.document"
DEFAULT_FIELDS = ["id", "name", "owner_id", "partner_id", "folder_id", "type",
                  "create_date", "write_date", "tag_ids", "mimetype"]


def _resolve_folder(uid, m, db, key, name):
    recs = execute(uid, m, db, key, "documents.folder", "search_read",
                   [["name", "ilike", name]], fields=["id", "name"])
    if not recs:
        print(f"Error: Folder '{name}' not found.", file=sys.stderr)
        sys.exit(1)
    return recs[0]["id"]


def cmd_list(args):
    uid, m, db, key = connect()
    domain = []

    if args.my:
        domain.append(["owner_id", "=", uid])
    if args.owner:
        owner_id = resolve_user(uid, m, db, key, args.owner)
        domain.append(["owner_id", "=", owner_id])
    if args.folder:
        folder_id = _resolve_folder(uid, m, db, key, args.folder)
        domain.append(["folder_id", "=", folder_id])
    if args.search:
        domain.append(["name", "ilike", args.search])
    if args.type:
        domain.append(["type", "=", args.type])
    if args.tag:
        tags = execute(uid, m, db, key, "documents.tag", "search_read",
                       [["name", "ilike", args.tag]], fields=["id"])
        if tags:
            domain.append(["tag_ids", "in", [t["id"] for t in tags]])

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
        "description", "res_model", "res_id", "url", "active"
    ]
    records = execute(uid, m, db, key, MODEL, "read", [args.id], fields=fields)
    output_json(records[0] if records else {"error": f"Document {args.id} not found"})


def cmd_create(args):
    uid, m, db, key = connect()
    vals = {"name": args.name}
    if args.folder:
        vals["folder_id"] = _resolve_folder(uid, m, db, key, args.folder)
    elif args.folder_id:
        vals["folder_id"] = args.folder_id
    if args.owner:
        vals["owner_id"] = resolve_user(uid, m, db, key, args.owner)
    if args.partner:
        vals["partner_id"] = resolve_partner(uid, m, db, key, args.partner)
    if args.url:
        vals["url"] = args.url
        vals["type"] = "url"
    if args.description:
        vals["description"] = args.description
    if args.extra:
        vals.update(json.loads(args.extra))
    rid = execute(uid, m, db, key, MODEL, "create", vals)
    output_json({"created_id": rid, "name": args.name})


def cmd_update(args):
    uid, m, db, key = connect()
    vals = {}
    if args.name:
        vals["name"] = args.name
    if args.folder:
        vals["folder_id"] = _resolve_folder(uid, m, db, key, args.folder)
    if args.owner:
        vals["owner_id"] = resolve_user(uid, m, db, key, args.owner)
    if args.partner:
        vals["partner_id"] = resolve_partner(uid, m, db, key, args.partner)
    if args.description:
        vals["description"] = args.description
    if args.extra:
        vals.update(json.loads(args.extra))
    if not vals:
        print("Error: No fields to update.", file=sys.stderr)
        sys.exit(1)
    ok = execute(uid, m, db, key, MODEL, "write", [args.id], vals)
    output_json({"updated_id": args.id, "success": ok})


def cmd_folders(args):
    uid, m, db, key = connect()
    recs = execute(uid, m, db, key, "documents.folder", "search_read", [],
                   fields=["id", "name", "parent_folder_id", "description"],
                   order="name asc")
    output_json(recs)


def main():
    p = argparse.ArgumentParser(description="VNClaw — Documents")
    sub = p.add_subparsers(dest="action")

    # list
    s = sub.add_parser("list", help="List documents")
    s.add_argument("--my", action="store_true", help="My documents only")
    s.add_argument("--owner", help="Filter by owner NAME")
    s.add_argument("--folder", help="Filter by folder NAME")
    s.add_argument("--search", help="Search document name")
    s.add_argument("--type", help="binary or url")
    s.add_argument("--tag", help="Filter by tag NAME")
    add_date_filter_args(s)
    s.add_argument("--fields", help="JSON array of fields")
    s.add_argument("--limit", type=int, default=50)

    # get
    s = sub.add_parser("get", help="Get document detail by ID")
    s.add_argument("id", type=int)
    s.add_argument("--fields", help="JSON array of fields")

    # create
    s = sub.add_parser("create", help="Create a document record")
    s.add_argument("--name", required=True, help="Document name")
    s.add_argument("--folder", help="Folder NAME")
    s.add_argument("--folder-id", type=int, help="Folder ID (alternative)")
    s.add_argument("--owner", help="Owner NAME")
    s.add_argument("--partner", help="Contact/partner NAME")
    s.add_argument("--url", help="URL (creates a URL-type document)")
    s.add_argument("--description")
    s.add_argument("--extra", help="Additional fields as JSON")

    # update
    s = sub.add_parser("update", help="Update a document")
    s.add_argument("id", type=int)
    s.add_argument("--name")
    s.add_argument("--folder", help="Folder NAME")
    s.add_argument("--owner", help="Owner NAME")
    s.add_argument("--partner", help="Contact/partner NAME")
    s.add_argument("--description")
    s.add_argument("--extra", help="Additional fields as JSON")

    # folders
    sub.add_parser("folders", help="List available folders")

    args = p.parse_args()
    if not args.action:
        p.print_help()
        sys.exit(1)
    {"list": cmd_list, "get": cmd_get, "create": cmd_create, "update": cmd_update,
     "folders": cmd_folders}[args.action](args)


if __name__ == "__main__":
    main()
