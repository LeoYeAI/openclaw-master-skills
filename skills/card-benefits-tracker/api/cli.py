#!/usr/bin/env python3
"""
Credit Card Tracker — CLI Controller

Safe, validated CRUD operations for credit card tracker JSON data files.
All mutations use atomic writes (temp file + os.replace) to prevent corruption.

Usage:
    python api/cli.py <resource> <action> [args...]

Resources: cards, benefits, cashback, tracking
Run with --help for full usage details.
"""

import argparse
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone

# --- Paths ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
CARDS_FILE = os.path.join(BASE_DIR, "cards.json")
DATA_DIR = os.path.join(BASE_DIR, "data")

VALID_FREQUENCIES = ("monthly", "quarterly", "yearly")
VALID_EXPIRY = ("use_it_or_lose_it", "rollover")
QUARTER_START_MONTHS = (1, 4, 7, 10)


# ============================================================
# Helpers
# ============================================================

def output(success, data=None, error=None):
    """Print JSON result to stdout and exit."""
    result = {"success": success}
    if data is not None:
        result["data"] = data
    if error is not None:
        result["error"] = error
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if success else 1)


def to_snake_case(name):
    """Convert a display name to a snake_case id."""
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = s.strip("_")
    return s


def read_cards():
    """Read and parse cards.json."""
    if not os.path.exists(CARDS_FILE):
        return {"cards": []}
    with open(CARDS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def write_cards(data):
    """Atomically write cards.json."""
    fd, tmp_path = tempfile.mkstemp(dir=BASE_DIR, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        os.replace(tmp_path, CARDS_FILE)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def tracking_path(period):
    """Return absolute path for a tracking file given period like 2026_02."""
    return os.path.join(DATA_DIR, f"{period}.json")


def read_tracking(period):
    """Read a tracking file, return None if it doesn't exist."""
    path = tracking_path(period)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_tracking(period, data):
    """Atomically write a tracking file."""
    os.makedirs(DATA_DIR, exist_ok=True)
    path = tracking_path(period)
    fd, tmp_path = tempfile.mkstemp(dir=DATA_DIR, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def find_card(cards_data, card_id):
    """Find a card by id, return (index, card) or (None, None)."""
    for i, card in enumerate(cards_data["cards"]):
        if card["id"] == card_id:
            return i, card
    return None, None


def find_benefit(card, benefit_id):
    """Find a benefit in a card, return (index, benefit) or (None, None)."""
    for i, b in enumerate(card.get("benefits", [])):
        if b["id"] == benefit_id:
            return i, b
    return None, None


def parse_period(period_str):
    """Parse YYYY_MM to (year, month). Returns None on invalid."""
    m = re.match(r"^(\d{4})_(\d{2})$", period_str)
    if not m:
        return None
    year, month = int(m.group(1)), int(m.group(2))
    if month < 1 or month > 12:
        return None
    return year, month


def generate_tracking_data(period_str):
    """Generate a tracking file from cards.json for the given period."""
    parsed = parse_period(period_str)
    if not parsed:
        output(False, error=f"Invalid period format: {period_str}. Use YYYY_MM.")
    year, month = parsed
    cards_data = read_cards()
    benefits = []

    for card in cards_data["cards"]:
        for benefit in card.get("benefits", []):
            freq = benefit.get("frequency", "monthly")
            include = False
            if freq == "monthly":
                include = True
            elif freq == "quarterly":
                include = month in QUARTER_START_MONTHS
            elif freq == "yearly":
                include = month == card.get("renewal_month", 1)

            if include:
                entry = {
                    "card_id": card["id"],
                    "card_name": card["name"],
                    "benefit_id": benefit["id"],
                    "benefit_name": benefit["name"],
                    "amount": benefit["amount"],
                    "frequency": freq,
                    "used": False,
                    "used_date": None,
                    "used_amount": None,
                    "notes": ""
                }
                benefits.append(entry)

    return {
        "period": f"{year}-{month:02d}",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "benefits": benefits
    }


# ============================================================
# Card commands
# ============================================================

def cmd_cards_list(_args):
    data = read_cards()
    summary = []
    for card in data["cards"]:
        summary.append({
            "id": card["id"],
            "name": card["name"],
            "annual_fee": card.get("annual_fee"),
            "benefits_count": len(card.get("benefits", [])),
            "renewal_month": card.get("renewal_month")
        })
    output(True, data=summary)


def cmd_cards_get(args):
    data = read_cards()
    _, card = find_card(data, args.card_id)
    if card is None:
        output(False, error=f"Card not found: {args.card_id}")
    output(True, data=card)


def cmd_cards_add(args):
    data = read_cards()
    card_id = args.id or to_snake_case(args.name)
    if not card_id:
        output(False, error="Could not generate a valid card ID. Provide --id explicitly.")

    _, existing = find_card(data, card_id)
    if existing is not None:
        output(False, error=f"Card already exists: {card_id}")

    card = {
        "id": card_id,
        "name": args.name,
        "annual_fee": args.annual_fee,
        "card_member_since": args.since,
        "renewal_month": args.renewal,
        "benefits": [],
        "cashback_rates": {}
    }
    data["cards"].append(card)
    write_cards(data)
    output(True, data=card)


def cmd_cards_update(args):
    data = read_cards()
    idx, card = find_card(data, args.card_id)
    if card is None:
        output(False, error=f"Card not found: {args.card_id}")

    if args.name is not None:
        card["name"] = args.name
    if args.annual_fee is not None:
        card["annual_fee"] = args.annual_fee
    if args.renewal is not None:
        card["renewal_month"] = args.renewal
    if args.since is not None:
        card["card_member_since"] = args.since

    data["cards"][idx] = card
    write_cards(data)
    output(True, data=card)


def cmd_cards_delete(args):
    data = read_cards()
    idx, card = find_card(data, args.card_id)
    if card is None:
        output(False, error=f"Card not found: {args.card_id}")

    data["cards"].pop(idx)
    write_cards(data)
    output(True, data={"deleted": args.card_id})


# ============================================================
# Benefit commands
# ============================================================

def cmd_benefits_list(args):
    data = read_cards()
    _, card = find_card(data, args.card_id)
    if card is None:
        output(False, error=f"Card not found: {args.card_id}")
    output(True, data=card.get("benefits", []))


def cmd_benefits_add(args):
    data = read_cards()
    idx, card = find_card(data, args.card_id)
    if card is None:
        output(False, error=f"Card not found: {args.card_id}")

    if args.frequency not in VALID_FREQUENCIES:
        output(False, error=f"Invalid frequency: {args.frequency}. Must be one of {VALID_FREQUENCIES}")

    benefit_id = args.id or to_snake_case(args.name)
    if not benefit_id:
        output(False, error="Could not generate a valid benefit ID. Provide --id explicitly.")

    _, existing = find_benefit(card, benefit_id)
    if existing is not None:
        output(False, error=f"Benefit already exists on card {args.card_id}: {benefit_id}")

    expiry = args.expiry_behavior or "use_it_or_lose_it"
    if expiry not in VALID_EXPIRY:
        output(False, error=f"Invalid expiry_behavior: {expiry}. Must be one of {VALID_EXPIRY}")

    benefit = {
        "id": benefit_id,
        "name": args.name,
        "amount": args.amount,
        "currency": args.currency or "USD",
        "frequency": args.frequency,
        "category": args.category,
        "notes": args.notes or "",
        "expiry_behavior": expiry
    }

    if "benefits" not in card:
        card["benefits"] = []
    card["benefits"].append(benefit)
    data["cards"][idx] = card
    write_cards(data)
    output(True, data=benefit)


def cmd_benefits_update(args):
    data = read_cards()
    card_idx, card = find_card(data, args.card_id)
    if card is None:
        output(False, error=f"Card not found: {args.card_id}")

    ben_idx, benefit = find_benefit(card, args.benefit_id)
    if benefit is None:
        output(False, error=f"Benefit not found: {args.benefit_id} on card {args.card_id}")

    if args.name is not None:
        benefit["name"] = args.name
    if args.amount is not None:
        benefit["amount"] = args.amount
    if args.frequency is not None:
        if args.frequency not in VALID_FREQUENCIES:
            output(False, error=f"Invalid frequency: {args.frequency}")
        benefit["frequency"] = args.frequency
    if args.category is not None:
        benefit["category"] = args.category
    if args.notes is not None:
        benefit["notes"] = args.notes
    if args.currency is not None:
        benefit["currency"] = args.currency
    if args.expiry_behavior is not None:
        if args.expiry_behavior not in VALID_EXPIRY:
            output(False, error=f"Invalid expiry_behavior: {args.expiry_behavior}")
        benefit["expiry_behavior"] = args.expiry_behavior

    card["benefits"][ben_idx] = benefit
    data["cards"][card_idx] = card
    write_cards(data)
    output(True, data=benefit)


def cmd_benefits_delete(args):
    data = read_cards()
    card_idx, card = find_card(data, args.card_id)
    if card is None:
        output(False, error=f"Card not found: {args.card_id}")

    ben_idx, _ = find_benefit(card, args.benefit_id)
    if ben_idx is None:
        output(False, error=f"Benefit not found: {args.benefit_id} on card {args.card_id}")

    card["benefits"].pop(ben_idx)
    data["cards"][card_idx] = card
    write_cards(data)
    output(True, data={"deleted": args.benefit_id, "card": args.card_id})


# ============================================================
# Cashback commands
# ============================================================

def cmd_cashback_get(args):
    data = read_cards()
    _, card = find_card(data, args.card_id)
    if card is None:
        output(False, error=f"Card not found: {args.card_id}")
    output(True, data=card.get("cashback_rates", {}))


def cmd_cashback_set(args):
    data = read_cards()
    idx, card = find_card(data, args.card_id)
    if card is None:
        output(False, error=f"Card not found: {args.card_id}")

    try:
        rates = json.loads(args.rates)
    except json.JSONDecodeError as e:
        output(False, error=f"Invalid JSON for --rates: {e}")

    if not isinstance(rates, dict):
        output(False, error="--rates must be a JSON object.")

    card["cashback_rates"] = rates
    data["cards"][idx] = card
    write_cards(data)
    output(True, data=rates)


def cmd_cashback_update(args):
    data = read_cards()
    idx, card = find_card(data, args.card_id)
    if card is None:
        output(False, error=f"Card not found: {args.card_id}")

    rates = card.get("cashback_rates", {})
    rates[args.category] = args.rate
    card["cashback_rates"] = rates
    data["cards"][idx] = card
    write_cards(data)
    output(True, data=rates)


def cmd_cashback_remove(args):
    data = read_cards()
    idx, card = find_card(data, args.card_id)
    if card is None:
        output(False, error=f"Card not found: {args.card_id}")

    rates = card.get("cashback_rates", {})
    if args.category not in rates:
        output(False, error=f"Category not found: {args.category}")

    del rates[args.category]
    card["cashback_rates"] = rates
    data["cards"][idx] = card
    write_cards(data)
    output(True, data=rates)


# ============================================================
# Tracking commands
# ============================================================

def cmd_tracking_get(args):
    existing = read_tracking(args.period)
    if existing is not None:
        output(True, data=existing)

    # Auto-generate
    data = generate_tracking_data(args.period)
    write_tracking(args.period, data)
    output(True, data=data)


def cmd_tracking_use(args):
    existing = read_tracking(args.period)
    if existing is None:
        # Auto-generate first
        existing = generate_tracking_data(args.period)
        write_tracking(args.period, existing)

    # Find the matching benefit entry
    found = False
    for entry in existing["benefits"]:
        if entry["card_id"] == args.card and entry["benefit_id"] == args.benefit:
            entry["used"] = True
            entry["used_date"] = args.date or datetime.now().strftime("%Y-%m-%d")
            entry["used_amount"] = args.amount if args.amount is not None else entry["amount"]
            if args.notes:
                entry["notes"] = args.notes
            found = True
            break

    if not found:
        output(False, error=f"Benefit entry not found: card={args.card}, benefit={args.benefit} in period {args.period}")

    write_tracking(args.period, existing)
    output(True, data=entry)


def cmd_tracking_unuse(args):
    existing = read_tracking(args.period)
    if existing is None:
        output(False, error=f"Tracking file not found for period: {args.period}")

    found = False
    for entry in existing["benefits"]:
        if entry["card_id"] == args.card and entry["benefit_id"] == args.benefit:
            entry["used"] = False
            entry["used_date"] = None
            entry["used_amount"] = None
            entry["notes"] = ""
            found = True
            break

    if not found:
        output(False, error=f"Benefit entry not found: card={args.card}, benefit={args.benefit} in period {args.period}")

    write_tracking(args.period, existing)
    output(True, data=entry)


def cmd_tracking_generate(args):
    if not args.force:
        existing = read_tracking(args.period)
        if existing is not None:
            output(False, error=f"Tracking file already exists for {args.period}. Use --force to overwrite.")

    data = generate_tracking_data(args.period)
    write_tracking(args.period, data)
    output(True, data=data)


def cmd_tracking_add_entry(args):
    existing = read_tracking(args.period)
    if existing is None:
        existing = generate_tracking_data(args.period)

    # Validate card exists
    cards_data = read_cards()
    _, card = find_card(cards_data, args.card)
    if card is None:
        output(False, error=f"Card not found: {args.card}")

    benefit_id = args.benefit_id or to_snake_case(args.benefit_name)

    entry = {
        "card_id": args.card,
        "card_name": card["name"],
        "benefit_id": benefit_id,
        "benefit_name": args.benefit_name,
        "amount": args.amount,
        "frequency": args.frequency or "monthly",
        "used": False,
        "used_date": None,
        "used_amount": None,
        "notes": args.notes or ""
    }

    existing["benefits"].append(entry)
    write_tracking(args.period, existing)
    output(True, data=entry)


def cmd_tracking_remove_entry(args):
    existing = read_tracking(args.period)
    if existing is None:
        output(False, error=f"Tracking file not found for period: {args.period}")

    original_len = len(existing["benefits"])
    existing["benefits"] = [
        e for e in existing["benefits"]
        if not (e["card_id"] == args.card and e["benefit_id"] == args.benefit)
    ]

    if len(existing["benefits"]) == original_len:
        output(False, error=f"Entry not found: card={args.card}, benefit={args.benefit} in period {args.period}")

    write_tracking(args.period, existing)
    output(True, data={"deleted": args.benefit, "card": args.card, "period": args.period})


# ============================================================
# Argument parser
# ============================================================

def build_parser():
    parser = argparse.ArgumentParser(
        prog="card-benefits-tracker",
        description="CLI controller for card benefits tracker data files"
    )
    subparsers = parser.add_subparsers(dest="resource", help="Resource type")

    # --- cards ---
    cards_parser = subparsers.add_parser("cards", help="Manage credit cards")
    cards_sub = cards_parser.add_subparsers(dest="action")

    cards_sub.add_parser("list", help="List all cards")

    cards_get = cards_sub.add_parser("get", help="Get card details")
    cards_get.add_argument("card_id", help="Card ID")

    cards_add = cards_sub.add_parser("add", help="Add a new card")
    cards_add.add_argument("--name", required=True, help="Card display name")
    cards_add.add_argument("--annual-fee", type=float, required=True, help="Annual fee in USD")
    cards_add.add_argument("--since", required=True, help="Card member since (YYYY-MM)")
    cards_add.add_argument("--renewal", type=int, required=True, help="Renewal month (1-12)")
    cards_add.add_argument("--id", default=None, help="Custom card ID (auto-generated from name if omitted)")

    cards_update = cards_sub.add_parser("update", help="Update card metadata")
    cards_update.add_argument("card_id", help="Card ID")
    cards_update.add_argument("--name", default=None, help="New name")
    cards_update.add_argument("--annual-fee", type=float, default=None, help="New annual fee")
    cards_update.add_argument("--renewal", type=int, default=None, help="New renewal month")
    cards_update.add_argument("--since", default=None, help="New card_member_since")

    cards_del = cards_sub.add_parser("delete", help="Delete a card")
    cards_del.add_argument("card_id", help="Card ID")

    # --- benefits ---
    benefits_parser = subparsers.add_parser("benefits", help="Manage card benefits")
    benefits_sub = benefits_parser.add_subparsers(dest="action")

    ben_list = benefits_sub.add_parser("list", help="List benefits for a card")
    ben_list.add_argument("card_id", help="Card ID")

    ben_add = benefits_sub.add_parser("add", help="Add a benefit to a card")
    ben_add.add_argument("card_id", help="Card ID")
    ben_add.add_argument("--name", required=True, help="Benefit name")
    ben_add.add_argument("--amount", type=float, required=True, help="Benefit amount")
    ben_add.add_argument("--frequency", required=True, choices=VALID_FREQUENCIES, help="Frequency")
    ben_add.add_argument("--category", required=True, help="Category label")
    ben_add.add_argument("--notes", default=None, help="Notes")
    ben_add.add_argument("--id", default=None, help="Custom benefit ID")
    ben_add.add_argument("--currency", default=None, help="Currency (default: USD)")
    ben_add.add_argument("--expiry-behavior", default=None, choices=VALID_EXPIRY, help="Expiry behavior")

    ben_update = benefits_sub.add_parser("update", help="Update a benefit")
    ben_update.add_argument("card_id", help="Card ID")
    ben_update.add_argument("benefit_id", help="Benefit ID")
    ben_update.add_argument("--name", default=None)
    ben_update.add_argument("--amount", type=float, default=None)
    ben_update.add_argument("--frequency", default=None, choices=VALID_FREQUENCIES)
    ben_update.add_argument("--category", default=None)
    ben_update.add_argument("--notes", default=None)
    ben_update.add_argument("--currency", default=None)
    ben_update.add_argument("--expiry-behavior", default=None, choices=VALID_EXPIRY)

    ben_del = benefits_sub.add_parser("delete", help="Delete a benefit")
    ben_del.add_argument("card_id", help="Card ID")
    ben_del.add_argument("benefit_id", help="Benefit ID")

    # --- cashback ---
    cb_parser = subparsers.add_parser("cashback", help="Manage cashback rates")
    cb_sub = cb_parser.add_subparsers(dest="action")

    cb_get = cb_sub.add_parser("get", help="Get cashback rates for a card")
    cb_get.add_argument("card_id", help="Card ID")

    cb_set = cb_sub.add_parser("set", help="Replace all cashback rates")
    cb_set.add_argument("card_id", help="Card ID")
    cb_set.add_argument("--rates", required=True, help='JSON object of rates, e.g. \'{"dining":"4x","other":"1x"}\'')

    cb_update = cb_sub.add_parser("update", help="Update a single cashback category")
    cb_update.add_argument("card_id", help="Card ID")
    cb_update.add_argument("--category", required=True, help="Category name")
    cb_update.add_argument("--rate", required=True, help="Rate value, e.g. 4x or 5%")

    cb_remove = cb_sub.add_parser("remove", help="Remove a cashback category")
    cb_remove.add_argument("card_id", help="Card ID")
    cb_remove.add_argument("--category", required=True, help="Category to remove")

    # --- tracking ---
    tr_parser = subparsers.add_parser("tracking", help="Manage monthly tracking files")
    tr_sub = tr_parser.add_subparsers(dest="action")

    tr_get = tr_sub.add_parser("get", help="Get tracking file (auto-generates if missing)")
    tr_get.add_argument("period", help="Period in YYYY_MM format")

    tr_use = tr_sub.add_parser("use", help="Mark a benefit as used")
    tr_use.add_argument("period", help="Period in YYYY_MM format")
    tr_use.add_argument("--card", required=True, help="Card ID")
    tr_use.add_argument("--benefit", required=True, help="Benefit ID")
    tr_use.add_argument("--amount", type=float, default=None, help="Used amount (defaults to benefit amount)")
    tr_use.add_argument("--date", default=None, help="Used date (YYYY-MM-DD, defaults to today)")
    tr_use.add_argument("--notes", default=None, help="Usage notes")

    tr_unuse = tr_sub.add_parser("unuse", help="Unmark a benefit (undo)")
    tr_unuse.add_argument("period", help="Period in YYYY_MM format")
    tr_unuse.add_argument("--card", required=True, help="Card ID")
    tr_unuse.add_argument("--benefit", required=True, help="Benefit ID")

    tr_gen = tr_sub.add_parser("generate", help="Generate/regenerate tracking file")
    tr_gen.add_argument("period", help="Period in YYYY_MM format")
    tr_gen.add_argument("--force", action="store_true", help="Overwrite existing file")

    tr_add = tr_sub.add_parser("add-entry", help="Add a custom benefit entry")
    tr_add.add_argument("period", help="Period in YYYY_MM format")
    tr_add.add_argument("--card", required=True, help="Card ID")
    tr_add.add_argument("--benefit-name", required=True, help="Benefit display name")
    tr_add.add_argument("--amount", type=float, required=True, help="Benefit amount")
    tr_add.add_argument("--frequency", default="monthly", choices=VALID_FREQUENCIES, help="Frequency")
    tr_add.add_argument("--notes", default=None, help="Notes")
    tr_add.add_argument("--benefit-id", default=None, help="Custom benefit ID")

    tr_remove = tr_sub.add_parser("remove-entry", help="Remove a benefit entry")
    tr_remove.add_argument("period", help="Period in YYYY_MM format")
    tr_remove.add_argument("--card", required=True, help="Card ID")
    tr_remove.add_argument("--benefit", required=True, help="Benefit ID")

    return parser


# ============================================================
# Dispatch
# ============================================================

DISPATCH = {
    ("cards", "list"): cmd_cards_list,
    ("cards", "get"): cmd_cards_get,
    ("cards", "add"): cmd_cards_add,
    ("cards", "update"): cmd_cards_update,
    ("cards", "delete"): cmd_cards_delete,
    ("benefits", "list"): cmd_benefits_list,
    ("benefits", "add"): cmd_benefits_add,
    ("benefits", "update"): cmd_benefits_update,
    ("benefits", "delete"): cmd_benefits_delete,
    ("cashback", "get"): cmd_cashback_get,
    ("cashback", "set"): cmd_cashback_set,
    ("cashback", "update"): cmd_cashback_update,
    ("cashback", "remove"): cmd_cashback_remove,
    ("tracking", "get"): cmd_tracking_get,
    ("tracking", "use"): cmd_tracking_use,
    ("tracking", "unuse"): cmd_tracking_unuse,
    ("tracking", "generate"): cmd_tracking_generate,
    ("tracking", "add-entry"): cmd_tracking_add_entry,
    ("tracking", "remove-entry"): cmd_tracking_remove_entry,
}


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.resource:
        parser.print_help()
        sys.exit(1)

    if not args.action:
        # Print subcommand help
        parser.parse_args([args.resource, "--help"])
        sys.exit(1)

    key = (args.resource, args.action)
    handler = DISPATCH.get(key)
    if handler is None:
        output(False, error=f"Unknown command: {args.resource} {args.action}")

    try:
        handler(args)
    except Exception as e:
        output(False, error=str(e))


if __name__ == "__main__":
    main()
