#!/usr/bin/env python3
"""Didit Workflows - Create, list, update, and delete verification workflows.

Usage:
    python scripts/manage_workflows.py list
    python scripts/manage_workflows.py create [--label NAME] [--type TYPE] [--liveness] [--face-match] [--aml]
    python scripts/manage_workflows.py get <uuid>
    python scripts/manage_workflows.py update <uuid> [--enable-aml] [--aml-threshold N]
    python scripts/manage_workflows.py delete <uuid>

Environment:
    DIDIT_API_KEY - Required. Your Didit API key.

Examples:
    python scripts/manage_workflows.py list
    python scripts/manage_workflows.py create --label "Standard KYC" --type kyc --liveness --face-match
    python scripts/manage_workflows.py update abc-123 --enable-aml --aml-threshold 75
    python scripts/manage_workflows.py delete abc-123
"""
import argparse
import json
import os
import sys

import requests

BASE_URL = "https://verification.didit.me/v3/workflows"


def get_headers(content_type=False) -> dict:
    api_key = os.environ.get("DIDIT_API_KEY")
    if not api_key:
        print("Error: DIDIT_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    h = {"x-api-key": api_key}
    if content_type:
        h["Content-Type"] = "application/json"
    return h


def list_workflows() -> list:
    r = requests.get(f"{BASE_URL}/", headers=get_headers(), timeout=30)
    if r.status_code != 200:
        print(f"Error {r.status_code}: {r.text}", file=sys.stderr)
        sys.exit(1)
    return r.json()


def create_workflow(label=None, wf_type="kyc", liveness=False, face_match=False, aml=False) -> dict:
    payload = {"workflow_type": wf_type}
    if label:
        payload["workflow_label"] = label
    if liveness:
        payload["is_liveness_enabled"] = True
    if face_match:
        payload["is_face_match_enabled"] = True
    if aml:
        payload["is_aml_enabled"] = True
    r = requests.post(f"{BASE_URL}/", headers=get_headers(content_type=True), json=payload, timeout=30)
    if r.status_code not in (200, 201):
        print(f"Error {r.status_code}: {r.text}", file=sys.stderr)
        sys.exit(1)
    return r.json()


def get_workflow(uuid: str) -> dict:
    r = requests.get(f"{BASE_URL}/{uuid}/", headers=get_headers(), timeout=30)
    if r.status_code != 200:
        print(f"Error {r.status_code}: {r.text}", file=sys.stderr)
        sys.exit(1)
    return r.json()


def update_workflow(uuid: str, changes: dict) -> dict:
    r = requests.patch(f"{BASE_URL}/{uuid}/", headers=get_headers(content_type=True), json=changes, timeout=30)
    if r.status_code != 200:
        print(f"Error {r.status_code}: {r.text}", file=sys.stderr)
        sys.exit(1)
    return r.json()


def delete_workflow(uuid: str) -> bool:
    r = requests.delete(f"{BASE_URL}/{uuid}/", headers=get_headers(), timeout=30)
    if r.status_code not in (200, 204):
        print(f"Error {r.status_code}: {r.text}", file=sys.stderr)
        sys.exit(1)
    return True


def main():
    parser = argparse.ArgumentParser(description="Manage Didit verification workflows")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List all workflows")

    create_p = sub.add_parser("create", help="Create a new workflow")
    create_p.add_argument("--label", help="Workflow display name")
    create_p.add_argument("--type", dest="wf_type", default="kyc",
                          choices=["kyc", "adaptive_age_verification", "biometric_authentication",
                                   "address_verification", "questionnaire_verification",
                                   "email_verification", "phone_verification"],
                          help="Workflow type (default: kyc)")
    create_p.add_argument("--liveness", action="store_true", help="Enable liveness detection")
    create_p.add_argument("--face-match", action="store_true", help="Enable face match")
    create_p.add_argument("--aml", action="store_true", help="Enable AML screening")

    get_p = sub.add_parser("get", help="Get workflow details")
    get_p.add_argument("uuid", help="Workflow UUID")

    update_p = sub.add_parser("update", help="Update a workflow")
    update_p.add_argument("uuid", help="Workflow UUID")
    update_p.add_argument("--enable-aml", action="store_true", help="Enable AML screening")
    update_p.add_argument("--disable-aml", action="store_true", help="Disable AML screening")
    update_p.add_argument("--aml-threshold", type=int, help="AML decline threshold (0-100)")
    update_p.add_argument("--label", help="Update workflow label")

    del_p = sub.add_parser("delete", help="Delete a workflow")
    del_p.add_argument("uuid", help="Workflow UUID")

    args = parser.parse_args()

    if args.command == "list":
        workflows = list_workflows()
        print(json.dumps(workflows, indent=2))
        print(f"\n--- {len(workflows)} workflow(s) ---")
        for wf in workflows:
            default = " (default)" if wf.get("is_default") else ""
            print(f"  {wf['uuid']} — {wf.get('workflow_label', 'Untitled')} [{wf.get('workflow_type')}]{default}")

    elif args.command == "create":
        result = create_workflow(args.label, args.wf_type, args.liveness, args.face_match, args.aml)
        print(json.dumps(result, indent=2))
        print(f"\n--- Created workflow: {result.get('uuid')} ---")

    elif args.command == "get":
        result = get_workflow(args.uuid)
        print(json.dumps(result, indent=2))

    elif args.command == "update":
        changes = {}
        if args.enable_aml:
            changes["is_aml_enabled"] = True
        if args.disable_aml:
            changes["is_aml_enabled"] = False
        if args.aml_threshold is not None:
            changes["aml_decline_threshold"] = args.aml_threshold
        if args.label:
            changes["workflow_label"] = args.label
        if not changes:
            print("No changes specified. Use --enable-aml, --label, etc.", file=sys.stderr)
            sys.exit(1)
        result = update_workflow(args.uuid, changes)
        print(json.dumps(result, indent=2))
        print(f"\n--- Updated workflow: {args.uuid} ---")

    elif args.command == "delete":
        delete_workflow(args.uuid)
        print(f"--- Deleted workflow: {args.uuid} ---")


if __name__ == "__main__":
    main()
