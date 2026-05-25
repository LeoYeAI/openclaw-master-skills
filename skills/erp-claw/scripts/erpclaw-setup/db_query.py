#!/usr/bin/env python3
"""ERPClaw Setup Skill — db_query.py

System administration actions for ERPClaw ERP.
Manages companies, currencies, payment terms, UoMs, seed data, and backups.

Usage: python3 db_query.py --action <action-name> [--flags ...]
Output: JSON to stdout, exit 0 on success, exit 1 on error.
"""
import argparse
import glob as glob_mod
import json
import os
import re
import shutil
import sqlite3
import sys
import urllib.error
import urllib.request
import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

# Add shared lib to path — try installed location first, fall back to bundled copy
_LIB_INSTALLED = os.path.expanduser("~/.openclaw/erpclaw/lib")
_LIB_BUNDLED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib")

_lib_found = False
for _lib_path in [_LIB_INSTALLED, _LIB_BUNDLED]:
    if os.path.isdir(os.path.join(_lib_path, "erpclaw_lib")):
        sys.path.insert(0, _lib_path)
        _lib_found = True
        break

if not _lib_found:
    print(json.dumps({
        "status": "error",
        "error": "erpclaw_lib not found. Re-install erpclaw: clawhub install erpclaw"
    }))
    sys.exit(1)

from erpclaw_lib.db import get_connection, ensure_db_exists, DEFAULT_DB_PATH
from erpclaw_lib.decimal_utils import to_decimal
from erpclaw_lib.validation import check_input_lengths
from erpclaw_lib.response import ok, err, row_to_dict
from erpclaw_lib.audit import audit
from erpclaw_lib.query import Q, P, Table, Field, fn
from erpclaw_lib.args import SafeArgumentParser, check_unknown_args
from erpclaw_lib.vendor.pypika import Order
from erpclaw_lib.vendor.pypika.terms import LiteralValue

# Convenience alias for datetime('now') SQLite expression
_NOW = LiteralValue("datetime('now')")

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SKILL_DIR, "assets")
BACKUP_DIR = os.path.expanduser("~/.openclaw/erpclaw/backups")

INDUSTRY_PROFILE_MAP = {
    "retail": "retail", "store": "retail", "shop": "retail", "ecommerce": "retail",
    "restaurant": "food-service", "food": "food-service", "catering": "food-service", "cafe": "food-service",
    "healthcare": "healthcare", "medical": "healthcare", "clinic": "healthcare", "hospital": "healthcare",
    "dental": "dental", "dentist": "dental",
    "veterinary": "veterinary", "vet": "veterinary", "animal": "veterinary",
    "construction": "construction", "contractor": "construction", "builder": "construction",
    "manufacturing": "manufacturing", "factory": "manufacturing", "production": "manufacturing",
    "law": "legal", "legal": "legal", "attorney": "legal", "law-firm": "legal",
    "farm": "agriculture", "agriculture": "agriculture", "ranch": "agriculture", "farming": "agriculture",
    "hotel": "hospitality", "hospitality": "hospitality", "resort": "hospitality", "motel": "hospitality",
    "property": "property-management", "real-estate": "property-management", "landlord": "property-management",
    "school": "k12-school", "k12": "k12-school", "education": "k12-school",
    "university": "college-university", "college": "college-university", "higher-ed": "college-university",
    "nonprofit": "nonprofit", "charity": "nonprofit", "foundation": "nonprofit", "ngo": "nonprofit",
    "auto-repair": "automotive", "mechanic": "automotive", "dealership": "automotive", "automotive": "automotive",
    "therapy": "mental-health", "therapist": "mental-health", "counseling": "mental-health", "psychiatry": "mental-health",
    "home-health": "home-health", "home-care": "home-health",
    "consulting": "professional-services", "agency": "professional-services",
    "distribution": "distribution", "wholesale": "distribution",
    "saas": "saas", "subscription": "saas", "software": "saas",
}


# ---------------------------------------------------------------------------
# Company Management
# ---------------------------------------------------------------------------

def setup_company(conn, args):
    """Create a new company."""
    name = args.name
    if not name:
        err("--name is required")

    # Generate abbreviation from name initials
    abbr = args.abbr or "".join(w[0].upper() for w in name.split() if w)
    if not abbr:
        abbr = name[:3].upper()

    company_id = str(uuid.uuid4())
    try:
        t = Table("company")
        q = Q.into(t).columns(
            "id", "name", "abbr", "default_currency", "country",
            "fiscal_year_start_month",
        ).insert(P(), P(), P(), P(), P(), P())
        conn.execute(
            q.get_sql(),
            (company_id, name, abbr,
             args.currency or "USD",
             args.country or "United States",
             args.fiscal_year_start_month or 1),
        )
        audit(conn, "erpclaw-setup", "create", "company", company_id,
               new_values={"name": name, "abbr": abbr},
               description=f"Created company '{name}'")
        conn.commit()
    except sqlite3.IntegrityError as e:
        sys.stderr.write(f"[erpclaw-setup] {e}\n")
        err("Company creation failed — check for duplicates or invalid data")

    # Auto-create fiscal year for the company
    fy_id = str(uuid.uuid4())
    fiscal_month = int(args.fiscal_year_start_month or 1)
    today = date.today()
    fy_start_year = today.year if today.month >= fiscal_month else today.year - 1
    fy_start = date(fy_start_year, fiscal_month, 1)
    if fiscal_month == 1:
        fy_end = date(fy_start_year, 12, 31)
    else:
        fy_end = date(fy_start_year + 1, fiscal_month, 1) - timedelta(days=1)
    fy_name = f"{abbr} FY {fy_start.strftime('%Y-%m-%d')} to {fy_end.strftime('%Y-%m-%d')}"
    try:
        t_fy = Table("fiscal_year")
        q_fy = (Q.into(t_fy)
                .columns("id", "name", "start_date", "end_date", "company_id")
                .insert(P(), P(), P(), P(), P()))
        conn.execute(q_fy.get_sql(),
                     (fy_id, fy_name, fy_start.isoformat(), fy_end.isoformat(), company_id))
        conn.commit()
    except Exception as e:
        sys.stderr.write(f"[erpclaw-setup] Fiscal year creation failed: {e}\n")
        pass  # Non-fatal — user can create manually

    # Auto-create default cost center
    cc_id = str(uuid.uuid4())
    cc_name = f"{name} - Main"
    try:
        t_cc = Table("cost_center")
        q_cc = (Q.into(t_cc)
                .columns("id", "name", "company_id", "is_group")
                .insert(P(), P(), P(), P()))
        conn.execute(q_cc.get_sql(), (cc_id, cc_name, company_id, 0))
        # Set as company default
        t_co = Table("company")
        q_co = (Q.update(t_co).set(Field("default_cost_center_id"), P()).where(t_co.id == P()))
        conn.execute(q_co.get_sql(), (cc_id, company_id))
        conn.commit()
    except Exception as e:
        sys.stderr.write(f"[erpclaw-setup] Cost center creation failed: {e}\n")
        pass  # Non-fatal — user can create manually

    # Auto-create default warehouse
    wh_id = str(uuid.uuid4())
    wh_name = f"{name} - Main Warehouse"
    try:
        t_wh = Table("warehouse")
        q_wh = (Q.into(t_wh)
                .columns("id", "name", "company_id", "warehouse_type", "is_group")
                .insert(P(), P(), P(), P(), P()))
        conn.execute(q_wh.get_sql(), (wh_id, wh_name, company_id, "stores", 0))
        # Set as company default
        t_co2 = Table("company")
        q_co2 = (Q.update(t_co2).set(Field("default_warehouse_id"), P()).where(t_co2.id == P()))
        conn.execute(q_co2.get_sql(), (wh_id, company_id))
        conn.commit()
    except Exception as e:
        sys.stderr.write(f"[erpclaw-setup] Warehouse creation failed: {e}\n")
        pass  # Non-fatal — user can create manually

    # Auto-onboard if --industry is provided
    modules_installed = []
    onboard_profile = None
    region_module = None
    if getattr(args, "industry", None):
        industry_key = args.industry.lower().replace(" ", "-")
        onboard_profile = INDUSTRY_PROFILE_MAP.get(industry_key)
        if onboard_profile:
            try:
                # Import onboarding module and call onboard programmatically
                sys.path.insert(0, os.path.join(SKILL_DIR, ".."))
                from onboarding import PROFILES, COUNTRY_REGION_MAP
                from module_manager import _load_registry, _install_module_inner, _registry_to_dict, build_action_cache

                profile = PROFILES.get(onboard_profile)
                if profile:
                    registry = _load_registry()
                    modules_by_name = _registry_to_dict(registry)
                    installed_rows = conn.execute(
                        "SELECT name FROM erpclaw_module WHERE install_status = 'installed'"
                    ).fetchall()
                    already_installed = {row["name"] for row in installed_rows}

                    for module_name in profile["modules"]:
                        if module_name in already_installed:
                            continue
                        if module_name not in modules_by_name:
                            continue
                        try:
                            install_args = argparse.Namespace(module_name=module_name)
                            _install_module_inner(install_args, conn, modules_by_name, depth=0)
                            modules_installed.append(module_name)
                            already_installed.add(module_name)
                        except SystemExit:
                            conn = get_connection()
                            check = conn.execute(
                                "SELECT install_status FROM erpclaw_module WHERE name = ?",
                                (module_name,)
                            ).fetchone()
                            if check and check["install_status"] == "installed":
                                modules_installed.append(module_name)
                                already_installed.add(module_name)
                        except Exception:
                            pass

                    # Also install regional module based on country
                    country_val = args.country or "United States"
                    region_module = COUNTRY_REGION_MAP.get(country_val)
                    if region_module and region_module not in already_installed:
                        if region_module in modules_by_name:
                            try:
                                install_args = argparse.Namespace(module_name=region_module)
                                _install_module_inner(install_args, conn, modules_by_name, depth=0)
                                modules_installed.append(region_module)
                            except SystemExit:
                                conn = get_connection()
                                check = conn.execute(
                                    "SELECT install_status FROM erpclaw_module WHERE name = ?",
                                    (region_module,)
                                ).fetchone()
                                if check and check["install_status"] == "installed":
                                    modules_installed.append(region_module)
                            except Exception:
                                pass
            except ImportError:
                pass  # Onboarding not available — skip silently

    result = {"company_id": company_id, "name": name, "abbr": abbr,
              "fiscal_year_id": fy_id, "cost_center_id": cc_id, "warehouse_id": wh_id}
    if onboard_profile:
        result["onboard_profile"] = onboard_profile
    if modules_installed:
        result["modules_installed"] = modules_installed
    if region_module:
        result["region_module"] = region_module
    ok(result)


def update_company(conn, args):
    """Update company fields."""
    company_id = args.company_id
    if not company_id:
        # Default to first company
        t = Table("company")
        q = Q.from_(t).select(t.id).limit(1)
        row = conn.execute(q.get_sql()).fetchone()
        if not row:
            err("No company found",
                 suggestion="Run 'tutorial' to create a demo company, or 'setup company' to create your own.")
        company_id = row["id"]

    t = Table("company")
    q = Q.from_(t).select(t.star).where(t.id == P())
    old = row_to_dict(conn.execute(q.get_sql(), (company_id,)).fetchone())
    if not old:
        err(f"Company {company_id} not found")

    updatable = [
        "name", "abbr", "default_currency", "country", "tax_id",
        "default_receivable_account_id", "default_payable_account_id",
        "default_income_account_id", "default_expense_account_id",
        "default_cost_center_id", "default_warehouse_id",
        "default_bank_account_id", "default_cash_account_id",
        "round_off_account_id", "exchange_gain_loss_account_id",
        "perpetual_inventory", "enable_negative_stock",
        "accounts_frozen_till_date", "role_allowed_for_frozen_entries",
        "fiscal_year_start_month",
    ]

    updates = {}
    for field in updatable:
        val = getattr(args, field.replace("-", "_"), None)
        if val is not None:
            updates[field] = val

    if not updates:
        err("No fields to update. Use --field-name value flags.")

    # Validate that default account IDs are not group accounts
    account_fields = [
        "default_receivable_account_id", "default_payable_account_id",
        "default_income_account_id", "default_expense_account_id",
        "default_bank_account_id", "default_cash_account_id",
        "round_off_account_id", "exchange_gain_loss_account_id",
    ]
    for field in account_fields:
        if field in updates and updates[field]:
            ta = Table("account")
            qa = Q.from_(ta).select(ta.name, ta.account_number, ta.is_group).where(ta.id == P())
            acct = conn.execute(qa.get_sql(), (updates[field],)).fetchone()
            if acct and acct["is_group"]:
                err(
                    f"Cannot set {field} to group account "
                    f"'{acct['name']}' ({acct['account_number']}). "
                    f"Use a leaf account (is_group=0) instead."
                )

    tc = Table("company")
    qu = Q.update(tc)
    for k in updates:
        qu = qu.set(Field(k), P())
    qu = qu.set(Field("updated_at"), _NOW)
    qu = qu.where(tc.id == P())
    values = list(updates.values()) + [company_id]
    conn.execute(qu.get_sql(), values)
    audit(conn, "erpclaw-setup", "update", "company", company_id,
           old_values={k: old.get(k) for k in updates},
           new_values=updates,
           description=f"Updated company fields: {list(updates.keys())}")
    conn.commit()

    ok({"company_id": company_id, "updated_fields": list(updates.keys())})


def get_company(conn, args):
    """Get a single company record."""
    company_id = args.company_id
    t = Table("company")
    if not company_id:
        q = Q.from_(t).select(t.star).limit(1)
        row = conn.execute(q.get_sql()).fetchone()
    else:
        q = Q.from_(t).select(t.star).where(t.id == P())
        row = conn.execute(q.get_sql(), (company_id,)).fetchone()
    if not row:
        err("No company found",
             suggestion="Run 'tutorial' to create a demo company, or 'setup company' to create your own.")
    ok({"company": row_to_dict(row)})


def list_companies(conn, args):
    """List all companies."""
    limit = int(args.limit or 20)
    offset = int(args.offset or 0)
    t = Table("company")
    qc = Q.from_(t).select(fn.Count("*").as_("cnt"))
    total_count = conn.execute(qc.get_sql()).fetchone()["cnt"]
    q = Q.from_(t).select(t.star).orderby(t.name).limit(limit).offset(offset)
    rows = conn.execute(q.get_sql()).fetchall()
    ok({"companies": [row_to_dict(r) for r in rows],
         "total_count": total_count, "limit": limit, "offset": offset,
         "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# Currency Management
# ---------------------------------------------------------------------------

def add_currency(conn, args):
    """Add a currency."""
    code = args.code
    if not code:
        err("--code is required")
    name = args.name or code
    try:
        t = Table("currency")
        q = Q.into(t).columns("code", "name", "symbol", "decimal_places", "enabled").insert(
            P(), P(), P(), P(), P()
        )
        conn.execute(
            q.get_sql(),
            (code.upper(), name, args.symbol or "", args.decimal_places or 2,
             1 if args.enabled else 0),
        )
        audit(conn, "erpclaw-setup", "create", "currency", code,
               new_values={"code": code, "name": name})
        conn.commit()
    except sqlite3.IntegrityError:
        err(f"Currency '{code}' already exists")
    ok({"code": code.upper(), "name": name})


def list_currencies(conn, args):
    """List currencies, optionally only enabled."""
    limit = int(args.limit or 20)
    offset = int(args.offset or 0)
    t = Table("currency")
    if args.enabled_only:
        qc = Q.from_(t).select(fn.Count("*").as_("cnt")).where(t.enabled == 1)
        total_count = conn.execute(qc.get_sql()).fetchone()["cnt"]
        q = Q.from_(t).select(t.star).where(t.enabled == 1).orderby(t.code).limit(limit).offset(offset)
        rows = conn.execute(q.get_sql()).fetchall()
    else:
        qc = Q.from_(t).select(fn.Count("*").as_("cnt"))
        total_count = conn.execute(qc.get_sql()).fetchone()["cnt"]
        q = Q.from_(t).select(t.star).orderby(t.code).limit(limit).offset(offset)
        rows = conn.execute(q.get_sql()).fetchall()
    ok({"currencies": [row_to_dict(r) for r in rows],
         "total_count": total_count, "limit": limit, "offset": offset,
         "has_more": offset + limit < total_count})


def add_exchange_rate(conn, args):
    """Add an exchange rate."""
    if not args.from_currency or not args.to_currency or not args.rate:
        err("--from-currency, --to-currency, and --rate are required")

    rate_id = str(uuid.uuid4())
    effective_date = args.effective_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    source = args.source or "manual"

    try:
        t = Table("exchange_rate")
        q = Q.into(t).columns(
            "id", "from_currency", "to_currency", "rate", "effective_date", "source"
        ).insert(P(), P(), P(), P(), P(), P())
        conn.execute(
            q.get_sql(),
            (rate_id, args.from_currency.upper(), args.to_currency.upper(),
             args.rate, effective_date, source),
        )
        audit(conn, "erpclaw-setup", "create", "exchange_rate", rate_id,
               new_values={"from": args.from_currency, "to": args.to_currency,
                           "rate": args.rate, "date": effective_date})
        conn.commit()
    except sqlite3.IntegrityError as e:
        sys.stderr.write(f"[erpclaw-setup] {e}\n")
        err("Exchange rate creation failed — check for duplicates or invalid data")

    ok({"exchange_rate_id": rate_id, "effective_date": effective_date})


def get_exchange_rate(conn, args):
    """Get exchange rate for a currency pair on a date (or most recent before)."""
    if not args.from_currency or not args.to_currency:
        err("--from-currency and --to-currency are required")

    date = args.effective_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    t = Table("exchange_rate")
    q = (Q.from_(t).select(t.star)
         .where(t.from_currency == P())
         .where(t.to_currency == P())
         .where(t.effective_date <= P())
         .orderby(t.effective_date, order=Order.desc)
         .limit(1))
    row = conn.execute(
        q.get_sql(),
        (args.from_currency.upper(), args.to_currency.upper(), date),
    ).fetchone()

    if not row:
        err(f"No exchange rate found for {args.from_currency}/{args.to_currency} on or before {date}")
    ok({"rate": row["rate"], "effective_date": row["effective_date"],
         "source": row["source"]})


def list_exchange_rates(conn, args):
    """List exchange rates with optional filters."""
    limit = int(args.limit or 20)
    offset = int(args.offset or 0)
    t = Table("exchange_rate")
    params = []
    qc = Q.from_(t).select(fn.Count("*").as_("cnt"))
    q = Q.from_(t).select(t.star)
    if args.from_currency:
        qc = qc.where(t.from_currency == P())
        q = q.where(t.from_currency == P())
        params.append(args.from_currency.upper())
    if args.to_currency:
        qc = qc.where(t.to_currency == P())
        q = q.where(t.to_currency == P())
        params.append(args.to_currency.upper())
    if args.from_date:
        qc = qc.where(t.effective_date >= P())
        q = q.where(t.effective_date >= P())
        params.append(args.from_date)
    if args.to_date:
        qc = qc.where(t.effective_date <= P())
        q = q.where(t.effective_date <= P())
        params.append(args.to_date)

    total_count = conn.execute(qc.get_sql(), params).fetchone()["cnt"]

    q = q.orderby(t.effective_date, order=Order.desc).limit(limit).offset(offset)
    rows = conn.execute(q.get_sql(), params + []).fetchall()
    ok({"rates": [row_to_dict(r) for r in rows],
         "total_count": total_count, "limit": limit, "offset": offset,
         "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# Payment Terms
# ---------------------------------------------------------------------------

def add_payment_terms(conn, args):
    """Add payment terms."""
    name = args.name
    if not name:
        err("--name is required")

    pt_id = str(uuid.uuid4())
    try:
        t = Table("payment_terms")
        q = Q.into(t).columns(
            "id", "name", "due_days", "discount_percentage", "discount_days", "description"
        ).insert(P(), P(), P(), P(), P(), P())
        conn.execute(
            q.get_sql(),
            (pt_id, name, args.due_days or 30,
             args.discount_percentage, args.discount_days,
             args.description),
        )
        audit(conn, "erpclaw-setup", "create", "payment_terms", pt_id,
               new_values={"name": name})
        conn.commit()
    except sqlite3.IntegrityError:
        err(f"Payment terms '{name}' already exists")
    ok({"payment_terms_id": pt_id, "name": name})


def list_payment_terms(conn, args):
    """List all payment terms."""
    limit = int(args.limit or 20)
    offset = int(args.offset or 0)
    t = Table("payment_terms")
    qc = Q.from_(t).select(fn.Count("*").as_("cnt"))
    total_count = conn.execute(qc.get_sql()).fetchone()["cnt"]
    q = Q.from_(t).select(t.star).orderby(t.due_days).orderby(t.name).limit(limit).offset(offset)
    rows = conn.execute(q.get_sql()).fetchall()
    ok({"terms": [row_to_dict(r) for r in rows],
         "total_count": total_count, "limit": limit, "offset": offset,
         "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# Units of Measure
# ---------------------------------------------------------------------------

def add_uom(conn, args):
    """Add a unit of measure."""
    name = args.name
    if not name:
        err("--name is required")

    uom_id = str(uuid.uuid4())
    try:
        t = Table("uom")
        q = Q.into(t).columns("id", "name", "must_be_whole_number").insert(P(), P(), P())
        conn.execute(
            q.get_sql(),
            (uom_id, name, 1 if args.must_be_whole_number else 0),
        )
        audit(conn, "erpclaw-setup", "create", "uom", uom_id, new_values={"name": name})
        conn.commit()
    except sqlite3.IntegrityError:
        err(f"UoM '{name}' already exists")
    ok({"uom_id": uom_id, "name": name})


def list_uoms(conn, args):
    """List all units of measure."""
    limit = int(args.limit or 20)
    offset = int(args.offset or 0)
    t = Table("uom")
    qc = Q.from_(t).select(fn.Count("*").as_("cnt"))
    total_count = conn.execute(qc.get_sql()).fetchone()["cnt"]
    q = Q.from_(t).select(t.star).orderby(t.name).limit(limit).offset(offset)
    rows = conn.execute(q.get_sql()).fetchall()
    ok({"uoms": [row_to_dict(r) for r in rows],
         "total_count": total_count, "limit": limit, "offset": offset,
         "has_more": offset + limit < total_count})


def add_uom_conversion(conn, args):
    """Add a UoM conversion factor."""
    if not args.from_uom or not args.to_uom or not args.conversion_factor:
        err("--from-uom, --to-uom, and --conversion-factor are required")

    conv_id = str(uuid.uuid4())
    try:
        t = Table("uom_conversion")
        q = Q.into(t).columns(
            "id", "from_uom", "to_uom", "conversion_factor", "item_id"
        ).insert(P(), P(), P(), P(), P())
        conn.execute(
            q.get_sql(),
            (conv_id, args.from_uom, args.to_uom,
             args.conversion_factor, args.item_id),
        )
        audit(conn, "erpclaw-setup", "create", "uom_conversion", conv_id,
               new_values={"from": args.from_uom, "to": args.to_uom,
                           "factor": args.conversion_factor})
        conn.commit()
    except sqlite3.IntegrityError as e:
        sys.stderr.write(f"[erpclaw-setup] {e}\n")
        err("UoM conversion creation failed — check for duplicates or invalid data")
    ok({"uom_conversion_id": conv_id})


# ---------------------------------------------------------------------------
# System Operations
# ---------------------------------------------------------------------------

def seed_defaults(conn, args):
    """Load standard seed data (currencies, UoMs, payment terms). Idempotent."""
    company_id = args.company_id
    if not company_id:
        t = Table("company")
        q = Q.from_(t).select(t.id).limit(1)
        row = conn.execute(q.get_sql()).fetchone()
        if not row:
            err("No company found. Run setup-company first.",
                 suggestion="Run 'tutorial' to create a demo company, or 'setup company' to create your own.")
        company_id = row["id"]

    counts = {"currencies_seeded": 0, "uoms_seeded": 0, "payment_terms_seeded": 0}

    # Seed currencies
    currencies_file = os.path.join(ASSETS_DIR, "currencies.json")
    if os.path.exists(currencies_file):
        with open(currencies_file) as f:
            currencies = json.load(f)
        for c in currencies:
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO currency (code, name, symbol, decimal_places, enabled) VALUES (?, ?, ?, ?, ?)",
                    (c["code"], c["name"], c.get("symbol", ""),
                     c.get("decimal_places", 2), c.get("enabled", 0)),
                )
                counts["currencies_seeded"] += 1
            except sqlite3.IntegrityError:
                pass

    # Seed UoMs
    uom_file = os.path.join(ASSETS_DIR, "default_uom.json")
    if os.path.exists(uom_file):
        with open(uom_file) as f:
            uoms = json.load(f)
        for u in uoms:
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO uom (id, name, must_be_whole_number) VALUES (?, ?, ?)",
                    (str(uuid.uuid4()), u["name"], u.get("must_be_whole_number", 0)),
                )
                counts["uoms_seeded"] += 1
            except sqlite3.IntegrityError:
                pass

    # Seed payment terms
    pt_file = os.path.join(ASSETS_DIR, "default_payment_terms.json")
    if os.path.exists(pt_file):
        with open(pt_file) as f:
            terms = json.load(f)
        for t in terms:
            try:
                conn.execute(
                    """INSERT OR IGNORE INTO payment_terms
                       (id, name, due_days, discount_percentage, discount_days, description)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (str(uuid.uuid4()), t["name"], t.get("due_days", 30),
                     t.get("discount_percentage"), t.get("discount_days"),
                     t.get("description")),
                )
                counts["payment_terms_seeded"] += 1
            except sqlite3.IntegrityError:
                pass

    audit(conn, "erpclaw-setup", "seed", "system", company_id,
           new_values=counts, description="Seeded default data")
    conn.commit()
    ok(counts)


def get_audit_log(conn, args):
    """Query audit log with optional filters."""
    t = Table("audit_log")
    q = Q.from_(t).select(t.star)
    params = []
    if args.entity_type:
        q = q.where(t.entity_type == P())
        params.append(args.entity_type)
    if args.entity_id:
        q = q.where(t.entity_id == P())
        params.append(args.entity_id)
    if args.audit_action:
        q = q.where(t.action == P())
        params.append(args.audit_action)
    if args.from_date:
        q = q.where(t.timestamp >= P())
        params.append(args.from_date)
    if args.to_date:
        q = q.where(t.timestamp <= P())
        params.append(args.to_date)
    limit = int(args.limit or 50)
    q = q.orderby(t.timestamp, order=Order.desc).limit(limit)

    rows = conn.execute(q.get_sql(), params).fetchall()
    entries = []
    for r in rows:
        entry = row_to_dict(r)
        # Parse JSON fields
        if entry.get("old_values"):
            entry["old_values"] = json.loads(entry["old_values"])
        if entry.get("new_values"):
            entry["new_values"] = json.loads(entry["new_values"])
        entries.append(entry)
    ok({"entries": entries})


def get_schema_version(conn, args):
    """Read schema version for a module."""
    module = args.module or "erpclaw-setup"
    t = Table("schema_version")
    q = Q.from_(t).select(t.star).where(t.module == P())
    row = conn.execute(q.get_sql(), (module,)).fetchone()
    if not row:
        err(f"No schema version found for module '{module}'")
    ok({"module": row["module"], "version": row["version"],
         "updated_at": row["updated_at"]})


def update_regional_settings(conn, args):
    """Set company-level regional settings."""
    company_id = args.company_id
    if not company_id:
        t = Table("company")
        q = Q.from_(t).select(t.id).limit(1)
        row = conn.execute(q.get_sql()).fetchone()
        if not row:
            err("No company found",
                 suggestion="Run 'tutorial' to create a demo company, or 'setup company' to create your own.")
        company_id = row["id"]

    settings = {}
    if args.date_format:
        settings["date_format"] = args.date_format
    if args.number_format:
        settings["number_format"] = args.number_format
    if args.default_tax_template_id:
        settings["default_tax_template_id"] = args.default_tax_template_id

    if not settings:
        err("No settings to update. Use --date-format, --number-format, etc.")

    for key, value in settings.items():
        conn.execute(
            """INSERT INTO regional_settings (id, company_id, key, value)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(company_id, key) DO UPDATE SET value = ?, updated_at = datetime('now')""",
            (str(uuid.uuid4()), company_id, key, value, value),
        )

    audit(conn, "erpclaw-setup", "update", "regional_settings", company_id,
           new_values=settings)
    conn.commit()
    ok({"updated": list(settings.keys())})


def backup_database(conn, args):
    """Create a backup of the database.

    Supports optional encryption with --encrypt --passphrase flags.
    Encrypted backups use AES-256 + HMAC-SHA256 authentication.
    """
    db_path = args.db_path or DEFAULT_DB_PATH
    backup_path = args.backup_path
    encrypt = getattr(args, "encrypt", False)
    passphrase = getattr(args, "passphrase", None)

    if encrypt and not passphrase:
        err("--passphrase is required when using --encrypt")

    if not backup_path:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        ext = ".sqlite.enc" if encrypt else ".sqlite"
        backup_path = os.path.join(BACKUP_DIR, f"erpclaw_backup_{ts}{ext}")

    os.makedirs(os.path.dirname(backup_path), exist_ok=True)

    if encrypt:
        # First create unencrypted backup to temp file, then encrypt
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            src = sqlite3.connect(db_path)
            dst = sqlite3.connect(tmp_path)
            src.backup(dst)
            dst.close()
            src.close()

            from erpclaw_lib.crypto import encrypt_file
            enc_result = encrypt_file(tmp_path, backup_path, passphrase)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

        size = os.path.getsize(backup_path)
        ok({"backup_path": backup_path, "size_bytes": size,
             "encrypted": True,
             "original_size": enc_result["original_size"],
             "timestamp": datetime.now(timezone.utc).isoformat()})
    else:
        # Standard unencrypted backup
        src = sqlite3.connect(db_path)
        dst = sqlite3.connect(backup_path)
        src.backup(dst)
        dst.close()
        src.close()

        size = os.path.getsize(backup_path)
        ok({"backup_path": backup_path, "size_bytes": size,
             "encrypted": False,
             "timestamp": datetime.now(timezone.utc).isoformat()})


def list_backups(conn, args):
    """List all backup files with size, date, and validity."""
    backup_dir = BACKUP_DIR
    if not os.path.exists(backup_dir):
        ok({"backups": [], "count": 0, "total_size_bytes": 0})

    # Match both plain (.sqlite) and encrypted (.enc) backups
    sqlite_files = glob_mod.glob(os.path.join(backup_dir, "erpclaw_*.sqlite"))
    enc_files = glob_mod.glob(os.path.join(backup_dir, "erpclaw_*.enc"))
    files = sorted(sqlite_files + enc_files, reverse=True)

    backups = []
    total_size = 0
    for f in files:
        size = os.path.getsize(f)
        total_size += size
        # Parse timestamp from filename
        basename = os.path.basename(f)
        encrypted = basename.endswith(".enc")
        timestamp = None
        try:
            parts = basename.split("_", 2)
            if len(parts) >= 3:
                ts_str = parts[2].replace(".sqlite", "").replace(".enc", "")
                timestamp = datetime.strptime(ts_str, "%Y%m%d_%H%M%S").isoformat()
        except (ValueError, IndexError):
            pass

        backups.append({
            "path": f,
            "filename": basename,
            "size_bytes": size,
            "timestamp": timestamp,
            "encrypted": encrypted,
        })

    ok({"backups": backups, "count": len(backups),
         "total_size_bytes": total_size})


def verify_backup(conn, args):
    """Verify a backup file is a valid ERPClaw database without restoring.

    Auto-detects encrypted backups. Requires --passphrase for encrypted files.

    Checks:
    1. File exists and is valid SQLite (or encrypted backup)
    2. Contains schema_version table (ERPClaw signature)
    3. Passes PRAGMA integrity_check
    4. Reports table count and schema version
    """
    backup_path = args.backup_path
    passphrase = getattr(args, "passphrase", None)
    if not backup_path:
        err("--backup-path is required")
    if not os.path.exists(backup_path):
        err(f"File not found: {backup_path}")

    from erpclaw_lib.crypto import is_encrypted_backup, decrypt_file as crypto_decrypt
    encrypted = is_encrypted_backup(backup_path)
    verify_path = backup_path
    decrypted_tmp = None

    if encrypted:
        if not passphrase:
            ok({"encrypted": True, "valid": None,
                 "message": "Encrypted backup — provide --passphrase to verify contents"})
        import tempfile
        decrypted_tmp = tempfile.mktemp(suffix=".sqlite")
        try:
            crypto_decrypt(backup_path, decrypted_tmp, passphrase)
        except ValueError as e:
            if os.path.exists(decrypted_tmp):
                os.unlink(decrypted_tmp)
            err(str(e))
        verify_path = decrypted_tmp

    try:
        test_conn = sqlite3.connect(verify_path)
        test_conn.row_factory = sqlite3.Row

        tables = test_conn.execute(
            "SELECT COUNT(*) as cnt FROM sqlite_master WHERE type='table'"
        ).fetchone()["cnt"]

        has_schema = test_conn.execute(
            "SELECT COUNT(*) as cnt FROM sqlite_master "
            "WHERE type='table' AND name='schema_version'"
        ).fetchone()["cnt"]
        if has_schema == 0:
            test_conn.close()
            err("Not a valid ERPClaw database (missing schema_version table)")

        sv = test_conn.execute(
            "SELECT module, version FROM schema_version ORDER BY updated_at DESC LIMIT 1"
        ).fetchone()

        integrity = test_conn.execute("PRAGMA integrity_check").fetchone()[0]

        size = os.path.getsize(backup_path)
        test_conn.close()

        ok({
            "valid": integrity == "ok",
            "integrity": integrity,
            "tables": tables,
            "schema_module": sv["module"] if sv else None,
            "schema_version": sv["version"] if sv else None,
            "size_bytes": size,
            "encrypted": encrypted,
        })

    except sqlite3.DatabaseError as e:
        err(f"Not a valid SQLite file: {e}")
    finally:
        if decrypted_tmp and os.path.exists(decrypted_tmp):
            os.unlink(decrypted_tmp)


def restore_database(conn, args):
    """Restore the database from a backup file.

    Auto-detects encrypted backups. Requires --passphrase for encrypted files.

    Steps:
    1. Detect encrypted backup, decrypt if needed
    2. Validate backup is valid SQLite + ERPClaw schema
    3. Create safety backup of current DB
    4. Copy backup over current DB
    5. Verify integrity
    If any step fails, rollback to safety backup.
    """
    backup_path = args.backup_path
    passphrase = getattr(args, "passphrase", None)
    if not backup_path:
        err("--backup-path is required")
    if not os.path.exists(backup_path):
        err(f"Backup file not found: {backup_path}")

    # Step 0: Auto-detect encrypted backup
    from erpclaw_lib.crypto import is_encrypted_backup, decrypt_file as crypto_decrypt
    encrypted = is_encrypted_backup(backup_path)
    decrypted_tmp = None

    if encrypted:
        if not passphrase:
            err("Backup is encrypted — --passphrase is required",
                 suggestion="Use --passphrase to provide the encryption passphrase")
        import tempfile
        decrypted_tmp = tempfile.mktemp(suffix=".sqlite")
        try:
            crypto_decrypt(backup_path, decrypted_tmp, passphrase)
        except ValueError as e:
            if os.path.exists(decrypted_tmp):
                os.unlink(decrypted_tmp)
            err(str(e))
        restore_source = decrypted_tmp
    else:
        restore_source = backup_path

    # Step 1: Validate backup is a valid SQLite database
    try:
        test_conn = sqlite3.connect(restore_source)
        test_conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        sv = test_conn.execute(
            "SELECT COUNT(*) as cnt FROM sqlite_master WHERE type='table' AND name='schema_version'"
        ).fetchone()[0]
        if sv == 0:
            test_conn.close()
            err("Backup is not a valid ERPClaw database (missing schema_version table)")
        test_conn.close()
    except sqlite3.DatabaseError as e:
        if decrypted_tmp and os.path.exists(decrypted_tmp):
            os.unlink(decrypted_tmp)
        err(f"Backup is not a valid SQLite file: {e}")

    # Determine target DB path
    db_path = args.db_path or DEFAULT_DB_PATH

    # Step 2: Create safety backup of current DB
    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safety_path = os.path.join(BACKUP_DIR, f"erpclaw_pre_restore_{ts}.sqlite")

    try:
        # Close the passed-in connection so we can safely copy the file
        conn.close()

        if os.path.exists(db_path):
            shutil.copy2(db_path, safety_path)

        # Step 3: Copy backup over current DB
        shutil.copy2(restore_source, db_path)

        # Step 4 & 5: Verify restored DB
        verify_conn = sqlite3.connect(db_path)
        verify_conn.row_factory = sqlite3.Row

        # Integrity check
        result = verify_conn.execute("PRAGMA integrity_check").fetchone()
        if result[0] != "ok":
            verify_conn.close()
            raise ValueError(f"Integrity check failed: {result[0]}")

        # Verify schema_version exists
        sv_count = verify_conn.execute(
            "SELECT COUNT(*) as cnt FROM schema_version"
        ).fetchone()["cnt"]

        size = os.path.getsize(db_path)
        verify_conn.close()

        # Clean up decrypted temp file
        if decrypted_tmp and os.path.exists(decrypted_tmp):
            os.unlink(decrypted_tmp)

        ok({
            "restored_from": backup_path,
            "safety_backup": safety_path,
            "size_bytes": size,
            "schema_versions": sv_count,
            "integrity": "ok",
            "was_encrypted": encrypted,
        })

    except (ValueError, sqlite3.Error, OSError) as e:
        # Clean up decrypted temp file
        if decrypted_tmp and os.path.exists(decrypted_tmp):
            os.unlink(decrypted_tmp)
        # Rollback: restore safety backup
        if os.path.exists(safety_path):
            shutil.copy2(safety_path, db_path)
        err(f"Restore failed (rolled back to previous state): {e}")


def status(conn, args):
    """Overall system status."""
    tc = Table("company")
    tcu = Table("currency")
    tu = Table("uom")
    tpt = Table("payment_terms")
    tsv = Table("schema_version")
    companies = conn.execute(
        Q.from_(tc).select(fn.Count("*").as_("cnt")).get_sql()
    ).fetchone()["cnt"]
    currencies = conn.execute(
        Q.from_(tcu).select(fn.Count("*").as_("cnt")).where(tcu.enabled == 1).get_sql()
    ).fetchone()["cnt"]
    uoms = conn.execute(
        Q.from_(tu).select(fn.Count("*").as_("cnt")).get_sql()
    ).fetchone()["cnt"]
    payment_terms = conn.execute(
        Q.from_(tpt).select(fn.Count("*").as_("cnt")).get_sql()
    ).fetchone()["cnt"]

    versions = {}
    q = Q.from_(tsv).select(tsv.module, tsv.version)
    for row in conn.execute(q.get_sql()).fetchall():
        versions[row["module"]] = row["version"]

    ok({
        "companies": companies,
        "currencies": currencies,
        "uoms": uoms,
        "payment_terms": payment_terms,
        "schema_versions": versions,
    })


# ---------------------------------------------------------------------------
# Database Initialization
# ---------------------------------------------------------------------------

def install_shared_library():
    """Copy bundled erpclaw_lib to the shared location (~/.openclaw/erpclaw/lib/).

    Called automatically during initialize-database. Ensures every other
    ERPClaw skill can import from the standard shared lib path.
    Recursively copies all .py files including vendor/ subdirectories.
    """
    target_dir = os.path.expanduser("~/.openclaw/erpclaw/lib/erpclaw_lib")
    bundled_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "lib", "erpclaw_lib"
    )
    if not os.path.isdir(bundled_dir):
        return  # Not bundled (dev environment) — skip
    copied = 0
    for root, dirs, files in os.walk(bundled_dir):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        rel_path = os.path.relpath(root, bundled_dir)
        dest_dir = os.path.join(target_dir, rel_path) if rel_path != "." else target_dir
        os.makedirs(dest_dir, exist_ok=True)
        for fname in files:
            if fname.endswith(".py"):
                shutil.copy2(os.path.join(root, fname),
                             os.path.join(dest_dir, fname))
                copied += 1
    return copied


def initialize_database(conn, args):
    """Initialize (or re-initialize) the ERPClaw database schema.

    Creates all tables, indexes, and constraints. Safe to run on an existing
    database — uses CREATE TABLE IF NOT EXISTS throughout.

    If --force is passed, drops and recreates the database from scratch.

    Also installs the shared library to ~/.openclaw/erpclaw/lib/erpclaw_lib/.
    """
    # Step 1: Install shared library (before anything else)
    lib_count = install_shared_library()

    db_path = args.db_path or DEFAULT_DB_PATH

    # Import the schema module (co-located in the same scripts/ directory)
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, scripts_dir)
    from init_schema import init_db, ALL_DDL_BLOCKS

    force = getattr(args, "force", False) or getattr(args, "force_reinit", False)

    if force and os.path.exists(db_path):
        # Close existing connection before deleting
        if conn:
            conn.close()
        os.remove(db_path)

    # Run full schema initialization
    init_db(db_path)

    # Verify by reconnecting and counting
    verify_conn = sqlite3.connect(db_path)
    try:
        table_count = verify_conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
        ).fetchone()[0]
        index_count = verify_conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='index'"
        ).fetchone()[0]
        skill_count = verify_conn.execute(
            "SELECT COUNT(*) FROM schema_version"
        ).fetchone()[0]
    finally:
        verify_conn.close()

    ok({
        "message": "Database initialized successfully",
        "db_path": db_path,
        "tables": table_count,
        "indexes": index_count,
        "skills_registered": skill_count,
        "shared_library_files": lib_count or 0,
        "shared_library_path": os.path.expanduser("~/.openclaw/erpclaw/lib/erpclaw_lib"),
        "journal_mode": "WAL",
        "foreign_keys": "ON",
        "reinitialized": force,
    })


# ---------------------------------------------------------------------------
# Tutorial — demo company with guided next-steps
# ---------------------------------------------------------------------------

def tutorial(conn, args):
    """Create a demo company 'Acme Corp' with essential accounts and a fiscal year.

    Idempotent: if Acme Corp already exists, returns existing data with next-steps.
    This gives new users a working starting point for all skills.
    """
    now_year = datetime.now(timezone.utc).strftime("%Y")

    # Check if Acme Corp already exists
    tco = Table("company")
    q_existing = Q.from_(tco).select(tco.id).where(tco.name == "Acme Corp")
    existing = conn.execute(q_existing.get_sql()).fetchone()
    if existing:
        company_id = existing["id"]
        ta = Table("account")
        q_accts = Q.from_(ta).select(ta.id, ta.name, ta.account_type).where(ta.company_id == P())
        accounts = conn.execute(q_accts.get_sql(), (company_id,)).fetchall()
        ok({
            "message": "Acme Corp already exists. Demo data is ready.",
            "company_id": company_id,
            "accounts": len(accounts),
            "next_steps": _tutorial_next_steps(),
        })

    company_id = str(uuid.uuid4())

    # 1. Create Acme Corp
    tco2 = Table("company")
    q_ins_co = Q.into(tco2).columns(
        "id", "name", "abbr", "default_currency", "country", "fiscal_year_start_month"
    ).insert(P(), "Acme Corp", "AC", "USD", "United States", 1)
    conn.execute(q_ins_co.get_sql(), (company_id,))

    # 2. Create chart of accounts (minimal but functional)
    account_map = {}
    acct_defs = [
        # (name, account_number, account_type, root_type, is_group)
        ("Assets", "1000", None, "asset", 1),
        ("Bank Account", "1100", "bank", "asset", 0),
        ("Cash Account", "1200", "cash", "asset", 0),
        ("Accounts Receivable", "1300", "receivable", "asset", 0),
        ("Inventory", "1400", "stock", "asset", 0),
        ("Liabilities", "2000", None, "liability", 1),
        ("Accounts Payable", "2100", "payable", "liability", 0),
        ("Stock Received Not Billed", "2150", "stock_received_not_billed", "liability", 0),
        ("Sales Tax Payable", "2200", "tax", "liability", 0),
        ("Payroll Payable", "2300", "payroll_payable", "liability", 0),
        ("Federal Tax Payable", "2310", "tax", "liability", 0),
        ("Social Security Payable", "2320", "tax", "liability", 0),
        ("Income", "4000", None, "income", 1),
        ("Sales Revenue", "4100", "revenue", "income", 0),
        ("Expenses", "5000", None, "expense", 1),
        ("Cost of Goods Sold", "5100", "cost_of_goods_sold", "expense", 0),
        ("Operating Expenses", "5200", "expense", "expense", 0),
        ("Salary Expense", "5300", "expense", "expense", 0),
        ("Equity", "3000", None, "equity", 1),
        ("Retained Earnings", "3100", "equity", "equity", 0),
    ]
    tacct = Table("account")
    q_ins_acct = Q.into(tacct).columns(
        "id", "name", "account_number", "account_type", "root_type",
        "is_group", "company_id", "balance_direction"
    ).insert(P(), P(), P(), P(), P(), P(), P(), P())
    for name, acct_num, acct_type, root_type, is_group in acct_defs:
        acct_id = str(uuid.uuid4())
        conn.execute(
            q_ins_acct.get_sql(),
            (acct_id, name, acct_num, acct_type, root_type,
             is_group, company_id,
             "debit_normal" if root_type in ("asset", "expense") else "credit_normal"),
        )
        account_map[acct_num] = acct_id

    # 3. Set company default accounts
    tco3 = Table("company")
    q_upd_co = (Q.update(tco3)
                .set(Field("default_receivable_account_id"), P())
                .set(Field("default_payable_account_id"), P())
                .set(Field("default_income_account_id"), P())
                .set(Field("default_expense_account_id"), P())
                .set(Field("default_bank_account_id"), P())
                .set(Field("default_cash_account_id"), P())
                .where(tco3.id == P()))
    conn.execute(
        q_upd_co.get_sql(),
        (account_map["1300"], account_map["2100"], account_map["4100"],
         account_map["5200"], account_map["1100"], account_map["1200"],
         company_id),
    )

    # 4. Create cost center
    cc_id = str(uuid.uuid4())
    tcc = Table("cost_center")
    q_ins_cc = Q.into(tcc).columns("id", "name", "company_id", "is_group").insert(P(), "Main", P(), 0)
    conn.execute(q_ins_cc.get_sql(), (cc_id, company_id))
    tco4 = Table("company")
    q_upd_cc = Q.update(tco4).set(Field("default_cost_center_id"), P()).where(tco4.id == P())
    conn.execute(q_upd_cc.get_sql(), (cc_id, company_id))

    # 5. Create fiscal year
    fy_id = str(uuid.uuid4())
    tfy = Table("fiscal_year")
    q_ins_fy = Q.into(tfy).columns(
        "id", "name", "start_date", "end_date", "company_id", "is_closed"
    ).insert(P(), P(), P(), P(), P(), 0)
    conn.execute(
        q_ins_fy.get_sql(),
        (fy_id, f"FY {now_year}", f"{now_year}-01-01", f"{now_year}-12-31", company_id),
    )

    audit(conn, "erpclaw-setup", "create", "company", company_id,
           new_values={"name": "Acme Corp", "accounts": len(acct_defs),
                       "fiscal_year": f"FY {now_year}"},
           description="Tutorial: created Acme Corp with demo data")
    conn.commit()

    ok({
        "message": "Acme Corp created with 15 accounts, 1 cost center, and a fiscal year.",
        "company_id": company_id,
        "company_name": "Acme Corp",
        "accounts_created": len(acct_defs),
        "fiscal_year": f"FY {now_year}",
        "cost_center": "Main",
        "next_steps": _tutorial_next_steps(),
    })


def _tutorial_next_steps():
    """Return guided next-steps for the tutorial."""
    return [
        {"step": 1, "skill": "erpclaw-gl",
         "action": "Your chart of accounts is ready. Try 'show my account balances' or 'list accounts'."},
        {"step": 2, "skill": "erpclaw-inventory",
         "action": "Add items and a warehouse: 'add item Widget, price $25' and 'add warehouse Main Warehouse'."},
        {"step": 3, "skill": "erpclaw-selling",
         "action": "Add a customer and create an invoice: 'add customer Stark Industries' then 'create invoice'."},
        {"step": 4, "skill": "erpclaw-payments",
         "action": "Record a payment: 'record payment from Stark Industries for $500'."},
        {"step": 5, "skill": "erpclaw-analytics",
         "action": "See the big picture: 'show me the executive dashboard' or 'how is business?'."},
    ]


# ---------------------------------------------------------------------------
# Cron / Maintenance Actions
# ---------------------------------------------------------------------------

def cleanup_backups(conn, args):
    """Clean up old database backups using a retention policy.

    Retention rules:
      - Keep the 7 most recent daily backups
      - Keep 4 weekly backups (oldest per week beyond the daily window)
      - Keep 12 monthly backups (oldest per month beyond the weekly window)
      - Delete everything else
    """
    backup_dir = BACKUP_DIR
    pattern = os.path.join(backup_dir, "erpclaw_backup_*.sqlite")
    files = sorted(glob_mod.glob(pattern), reverse=True)  # newest first

    if not files:
        ok({"kept": 0, "deleted": 0, "freed_bytes": 0})

    # Parse timestamps from filenames and build records
    backups = []
    for f in files:
        basename = os.path.basename(f)
        # erpclaw_backup_YYYYMMDD_HHMMSS.sqlite
        try:
            parts = basename.replace("erpclaw_backup_", "").replace(".sqlite", "")
            dt = datetime.strptime(parts, "%Y%m%d_%H%M%S")
            backups.append({"path": f, "dt": dt, "date": dt.date(),
                            "size": os.path.getsize(f)})
        except (ValueError, OSError):
            continue  # skip files that don't match expected format

    if not backups:
        ok({"kept": 0, "deleted": 0, "freed_bytes": 0})

    keep_set = set()

    # --- Daily: keep the 7 most recent unique dates ---
    seen_dates = set()
    daily_kept = 0
    for b in backups:
        if b["date"] not in seen_dates:
            seen_dates.add(b["date"])
            daily_kept += 1
        if daily_kept <= 7:
            keep_set.add(b["path"])

    # --- Weekly: 4 oldest-per-week beyond the daily window ---
    # Group remaining (not yet kept) by ISO week
    weekly_candidates = [b for b in backups if b["path"] not in keep_set]
    weeks_seen = {}  # (iso_year, iso_week) -> oldest backup
    for b in weekly_candidates:
        iso_year, iso_week, _ = b["date"].isocalendar()
        key = (iso_year, iso_week)
        if key not in weeks_seen or b["dt"] < weeks_seen[key]["dt"]:
            weeks_seen[key] = b

    # Sort weeks newest first and keep 4
    sorted_weeks = sorted(weeks_seen.keys(), reverse=True)
    for wk in sorted_weeks[:4]:
        keep_set.add(weeks_seen[wk]["path"])

    # --- Monthly: 12 oldest-per-month beyond daily+weekly ---
    monthly_candidates = [b for b in backups if b["path"] not in keep_set]
    months_seen = {}  # (year, month) -> oldest backup
    for b in monthly_candidates:
        key = (b["date"].year, b["date"].month)
        if key not in months_seen or b["dt"] < months_seen[key]["dt"]:
            months_seen[key] = b

    sorted_months = sorted(months_seen.keys(), reverse=True)
    for mo in sorted_months[:12]:
        keep_set.add(months_seen[mo]["path"])

    # --- Delete everything not in keep_set ---
    deleted = 0
    freed = 0
    for b in backups:
        if b["path"] not in keep_set:
            try:
                freed += b["size"]
                os.remove(b["path"])
                deleted += 1
            except OSError:
                pass  # file already gone or permission issue

    kept = len(backups) - deleted
    audit(conn, "erpclaw-setup", "cleanup", "backup", "system",
           new_values={"kept": kept, "deleted": deleted, "freed_bytes": freed},
           description=f"Backup cleanup: kept {kept}, deleted {deleted}")
    conn.commit()
    ok({"kept": kept, "deleted": deleted, "freed_bytes": freed})


def fetch_exchange_rates(conn, args):
    """Fetch latest exchange rates from frankfurter.dev (base=USD).

    For each rate returned, inserts or updates a row in exchange_rate with
    from_currency='USD', effective_date=today, source='api'.
    """
    url = "https://api.frankfurter.dev/latest?from=USD"
    today = date.today().isoformat()

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "erpclaw/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        err(f"Failed to fetch exchange rates: {e}",
             suggestion="Check internet connection or try again later.")

    rates = data.get("rates", {})
    if not rates:
        err("API returned no rates",
             suggestion="The API may be temporarily unavailable. Try again later.")

    count = 0
    for currency_code, rate_value in rates.items():
        rate_str = str(Decimal(str(rate_value)))

        # Check if a rate already exists for this pair + date
        ter = Table("exchange_rate")
        q_check = (Q.from_(ter).select(ter.id)
                   .where(ter.from_currency == "USD")
                   .where(ter.to_currency == P())
                   .where(ter.effective_date == P()))
        existing = conn.execute(q_check.get_sql(), (currency_code, today)).fetchone()

        if existing:
            q_upd = (Q.update(ter)
                     .set(ter.rate, P())
                     .set(ter.source, "api")
                     .set(Field("updated_at"), _NOW)
                     .where(ter.id == P()))
            conn.execute(q_upd.get_sql(), (rate_str, existing["id"]))
        else:
            rate_id = str(uuid.uuid4())
            q_ins = Q.into(ter).columns(
                "id", "from_currency", "to_currency", "rate", "effective_date", "source"
            ).insert(P(), "USD", P(), P(), P(), "api")
            conn.execute(q_ins.get_sql(), (rate_id, currency_code, rate_str, today))
        count += 1

    audit(conn, "erpclaw-setup", "fetch", "exchange_rate", "system",
           new_values={"rates_updated": count, "source": "frankfurter.dev",
                       "date": today},
           description=f"Fetched {count} exchange rates from frankfurter.dev")
    conn.commit()
    ok({"rates_updated": count, "source": "frankfurter.dev",
         "base": "USD", "date": today})


# ---------------------------------------------------------------------------
# RBAC: Users, Roles, Permissions
# ---------------------------------------------------------------------------

def add_user(conn, args):
    """Create a new ERP user."""
    username = args.name  # reuse --name flag for username
    if not username:
        err("--name (username) is required", suggestion="Provide a unique username")
    email = getattr(args, "email", None)
    full_name = getattr(args, "full_name", None)
    company_id = args.company_id

    # Validate email format if provided
    _EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    if email and not _EMAIL_RE.match(email):
        err(f"Invalid email format for --email: '{email}'")

    # Check uniqueness
    tu = Table("erp_user")
    q_check = Q.from_(tu).select(tu.id).where(tu.username == P())
    existing = conn.execute(q_check.get_sql(), (username,)).fetchone()
    if existing:
        err(f"Username '{username}' already exists",
             suggestion="Choose a different username")

    user_id = str(uuid.uuid4())
    company_ids = json.dumps([company_id]) if company_id else None

    q_ins = Q.into(tu).columns(
        "id", "username", "email", "full_name", "company_ids"
    ).insert(P(), P(), P(), P(), P())
    conn.execute(
        q_ins.get_sql(),
        (user_id, username, email, full_name, company_ids),
    )
    audit(conn, "erpclaw-setup", "add-user", "erp_user", user_id,
           new_values={"username": username, "email": email})
    conn.commit()
    ok({"user_id": user_id, "username": username})


def update_user(conn, args):
    """Update an existing ERP user."""
    user_id = getattr(args, "user_id", None)
    if not user_id:
        err("--user-id is required")

    tu = Table("erp_user")
    q_get = Q.from_(tu).select(tu.star).where(tu.id == P())
    user = conn.execute(q_get.get_sql(), (user_id,)).fetchone()
    if not user:
        err("User not found")

    updates = {}
    if args.name:
        updates["username"] = args.name
    if getattr(args, "email", None):
        updates["email"] = args.email
    if getattr(args, "full_name", None):
        updates["full_name"] = args.full_name
    if getattr(args, "user_status", None):
        if args.user_status not in ("active", "disabled", "locked"):
            err("--user-status must be active, disabled, or locked")
        updates["status"] = args.user_status
    if args.company_id:
        # Append company to existing list
        existing = json.loads(user["company_ids"] or "[]")
        if args.company_id not in existing:
            existing.append(args.company_id)
        updates["company_ids"] = json.dumps(existing)

    if not updates:
        err("No fields to update")

    tu2 = Table("erp_user")
    qu = Q.update(tu2)
    for k in updates:
        qu = qu.set(Field(k), P())
    qu = qu.set(Field("updated_at"), _NOW)
    qu = qu.where(tu2.id == P())
    vals = list(updates.values()) + [user_id]
    conn.execute(qu.get_sql(), vals)
    audit(conn, "erpclaw-setup", "update-user", "erp_user", user_id,
           old_values=dict(user), new_values=updates)
    conn.commit()
    ok({"user_id": user_id, "updated_fields": list(updates.keys())})


def list_users(conn, args):
    """List all ERP users."""
    limit = args.limit or 50
    offset = args.offset or 0
    tu = Table("erp_user")
    q = (Q.from_(tu)
         .select(tu.id, tu.username, tu.email, tu.full_name, tu.status, tu.company_ids, tu.created_at)
         .orderby(tu.username)
         .limit(limit + 1)
         .offset(offset))
    rows = conn.execute(q.get_sql()).fetchall()
    users = [dict(r) for r in rows[:limit]]
    ok({"users": users, "count": len(users),
         "has_more": len(rows) > limit})


def get_user(conn, args):
    """Get details of a specific ERP user including roles."""
    user_id = getattr(args, "user_id", None)
    if not user_id:
        err("--user-id is required")

    tu = Table("erp_user")
    q_user = Q.from_(tu).select(tu.star).where(tu.id == P())
    user = conn.execute(q_user.get_sql(), (user_id,)).fetchone()
    if not user:
        err("User not found")

    tur = Table("user_role").as_("ur")
    tr = Table("role").as_("r")
    tco = Table("company").as_("c")
    q_roles = (Q.from_(tur)
               .join(tr).on(tr.id == tur.role_id)
               .left_join(tco).on(tco.id == tur.company_id)
               .select(
                   tr.name.as_("role_name"),
                   tur.company_id,
                   tco.name.as_("company_name"),
               )
               .where(tur.user_id == P())
               .orderby(tr.name))
    roles = conn.execute(q_roles.get_sql(), (user_id,)).fetchall()

    result = dict(user)
    result["roles"] = [dict(r) for r in roles]
    ok(result)


def add_role(conn, args):
    """Create a custom (non-system) role."""
    role_name = args.name
    if not role_name:
        err("--name is required")

    tr = Table("role")
    q_check = Q.from_(tr).select(tr.id).where(tr.name == P())
    existing = conn.execute(q_check.get_sql(), (role_name,)).fetchone()
    if existing:
        err(f"Role '{role_name}' already exists")

    role_id = str(uuid.uuid4())
    q_ins = Q.into(tr).columns("id", "name", "description", "is_system").insert(P(), P(), P(), 0)
    conn.execute(q_ins.get_sql(), (role_id, role_name, args.description))
    audit(conn, "erpclaw-setup", "add-role", "role", role_id,
           new_values={"name": role_name})
    conn.commit()
    ok({"role_id": role_id, "name": role_name})


def list_roles(conn, args):
    """List all roles."""
    tr = Table("role").as_("r")
    tur = Table("user_role").as_("ur")
    q = (Q.from_(tr)
         .left_join(tur).on(tur.role_id == tr.id)
         .select(tr.id, tr.name, tr.description, tr.is_system,
                 fn.Count(tur.id).as_("user_count"))
         .groupby(tr.id)
         .orderby(tr.is_system, order=Order.desc)
         .orderby(tr.name))
    rows = conn.execute(q.get_sql()).fetchall()
    ok({"roles": [dict(r) for r in rows], "count": len(rows)})


def assign_role(conn, args):
    """Assign a role to a user (optionally company-scoped)."""
    user_id = getattr(args, "user_id", None)
    role_name = getattr(args, "role_name", None)
    if not user_id:
        err("--user-id is required")
    if not role_name:
        err("--role-name is required")

    tu = Table("erp_user")
    q_user = Q.from_(tu).select(tu.id).where(tu.id == P())
    user = conn.execute(q_user.get_sql(), (user_id,)).fetchone()
    if not user:
        err("User not found")

    tr = Table("role")
    q_role = Q.from_(tr).select(tr.id).where(tr.name == P())
    role = conn.execute(q_role.get_sql(), (role_name,)).fetchone()
    if not role:
        err(f"Role '{role_name}' not found",
             suggestion="Use list-roles to see available roles")

    role_id = role["id"]
    company_id = args.company_id  # None = global assignment

    # Check if already assigned — use raw SQL for IS ? (NULL-safe comparison)
    existing = conn.execute(
        "SELECT id FROM user_role WHERE user_id = ? AND role_id = ? AND company_id IS ?",
        (user_id, role_id, company_id),
    ).fetchone()
    if existing:
        err(f"Role '{role_name}' already assigned to this user")

    ur_id = str(uuid.uuid4())
    tur = Table("user_role")
    q_ins = Q.into(tur).columns("id", "user_id", "role_id", "company_id").insert(P(), P(), P(), P())
    conn.execute(q_ins.get_sql(), (ur_id, user_id, role_id, company_id))
    audit(conn, "erpclaw-setup", "assign-role", "user_role", ur_id,
           new_values={"user_id": user_id, "role_name": role_name,
                       "company_id": company_id})
    conn.commit()
    ok({"user_role_id": ur_id, "role_name": role_name,
         "company_id": company_id})


def revoke_role(conn, args):
    """Remove a role from a user."""
    user_id = getattr(args, "user_id", None)
    role_name = getattr(args, "role_name", None)
    if not user_id:
        err("--user-id is required")
    if not role_name:
        err("--role-name is required")

    tr = Table("role")
    q_role = Q.from_(tr).select(tr.id).where(tr.name == P())
    role = conn.execute(q_role.get_sql(), (role_name,)).fetchone()
    if not role:
        err(f"Role '{role_name}' not found")

    company_id = args.company_id
    # Use raw SQL for IS ? (NULL-safe comparison not supported by PyPika for SQLite)
    deleted = conn.execute(
        "DELETE FROM user_role WHERE user_id = ? AND role_id = ? AND company_id IS ?",
        (user_id, role["id"], company_id),
    )
    if deleted.rowcount == 0:
        err(f"Role '{role_name}' not assigned to this user")

    audit(conn, "erpclaw-setup", "revoke-role", "user_role", user_id,
           old_values={"role_name": role_name, "company_id": company_id})
    conn.commit()
    ok({"revoked": role_name, "user_id": user_id})


def set_password(conn, args):
    """Set web login password for a user."""
    user_id = getattr(args, "user_id", None)
    password = getattr(args, "password", None)
    if not user_id:
        err("--user-id is required")
    if not password:
        err("--password is required")
    if len(password) < 8:
        err("Password must be at least 8 characters")

    tu = Table("erp_user")
    q_get = Q.from_(tu).select(tu.id, tu.username).where(tu.id == P())
    user = conn.execute(q_get.get_sql(), (user_id,)).fetchone()
    if not user:
        err("User not found")

    from erpclaw_lib.passwords import hash_password
    pw_hash = hash_password(password)
    q_upd = (Q.update(tu)
             .set(Field("password_hash"), P())
             .set(Field("updated_at"), _NOW)
             .where(tu.id == P()))
    conn.execute(q_upd.get_sql(), (pw_hash, user_id))
    audit(conn, "erpclaw-setup", "set-password", "erp_user", user_id,
           description="Web password set")
    conn.commit()
    username = user["username"] if isinstance(user, dict) else user[1]
    ok({"user_id": user_id, "username": username, "message": "Password set successfully"})


def link_telegram_user(conn, args):
    """Link a Telegram user ID to an ERP user account."""
    user_id = getattr(args, "user_id", None)
    telegram_user_id = getattr(args, "telegram_user_id", None)
    if not user_id:
        err("--user-id is required")
    if not telegram_user_id:
        err("--telegram-user-id is required")

    tu = Table("erp_user")
    q_get = Q.from_(tu).select(tu.id, tu.username).where(tu.id == P())
    user = conn.execute(q_get.get_sql(), (user_id,)).fetchone()
    if not user:
        err("User not found")

    # Check if telegram_user_id already linked to another user
    q_check = Q.from_(tu).select(tu.id, tu.username).where(tu.telegram_user_id == P())
    existing = conn.execute(q_check.get_sql(), (str(telegram_user_id),)).fetchone()
    if existing:
        ex_id = existing["id"] if isinstance(existing, dict) else existing[0]
        if ex_id != user_id:
            err(f"Telegram user {telegram_user_id} is already linked to another account")

    q_upd = (Q.update(tu)
             .set(Field("telegram_user_id"), P())
             .set(Field("updated_at"), _NOW)
             .where(tu.id == P()))
    conn.execute(q_upd.get_sql(), (str(telegram_user_id), user_id))
    audit(conn, "erpclaw-setup", "link-telegram-user", "erp_user", user_id,
          new_values={"telegram_user_id": str(telegram_user_id)})
    conn.commit()

    username = user["username"] if isinstance(user, dict) else user[1]
    ok({"user_id": user_id, "username": username,
        "telegram_user_id": str(telegram_user_id), "linked": True})


def unlink_telegram_user(conn, args):
    """Remove Telegram user ID link from an ERP user account."""
    telegram_user_id = getattr(args, "telegram_user_id", None)
    if not telegram_user_id:
        err("--telegram-user-id is required")

    tu = Table("erp_user")
    q_get = Q.from_(tu).select(tu.id, tu.username).where(tu.telegram_user_id == P())
    user = conn.execute(q_get.get_sql(), (str(telegram_user_id),)).fetchone()
    if not user:
        err(f"No user linked to Telegram user {telegram_user_id}")

    user_id = user["id"] if isinstance(user, dict) else user[0]
    q_upd = (Q.update(tu)
             .set(Field("telegram_user_id"), None)
             .set(Field("updated_at"), _NOW)
             .where(tu.id == P()))
    conn.execute(q_upd.get_sql(), (user_id,))
    audit(conn, "erpclaw-setup", "unlink-telegram-user", "erp_user", user_id,
          old_values={"telegram_user_id": str(telegram_user_id)})
    conn.commit()

    ok({"user_id": user_id, "telegram_user_id": str(telegram_user_id), "unlinked": True})


def check_telegram_permission(conn, args):
    """Check if a Telegram user has permission for a specific skill action."""
    telegram_user_id = getattr(args, "telegram_user_id", None)
    skill = getattr(args, "skill", None)
    action_name = getattr(args, "check_action", None)
    if not telegram_user_id:
        err("--telegram-user-id is required")
    if not skill:
        err("--skill is required")
    if not action_name:
        err("--check-action is required")

    from erpclaw_lib.rbac import resolve_telegram_user_id, check_permission

    user_id = resolve_telegram_user_id(conn, telegram_user_id)
    if not user_id:
        ok({"allowed": False, "reason": "not_linked",
            "telegram_user_id": str(telegram_user_id)})
        return

    allowed = check_permission(conn, user_id, skill, action_name)
    ok({"allowed": allowed, "user_id": user_id,
        "skill": skill, "action": action_name,
        "telegram_user_id": str(telegram_user_id)})


def seed_permissions(conn, args):
    """Seed default role permissions from the shared RBAC library."""
    from erpclaw_lib.rbac import seed_role_permissions
    from erpclaw_lib.args import SafeArgumentParser, check_unknown_args
    seed_role_permissions(conn)
    t = Table("role_permission")
    q = Q.from_(t).select(fn.Count("*").as_("cnt"))
    count = conn.execute(q.get_sql()).fetchone()
    ok({"permissions_seeded": count["cnt"]})


# ---------------------------------------------------------------------------
# Onboarding Wizard
# ---------------------------------------------------------------------------

ONBOARDING_STATE_DIR = os.path.expanduser("~/.openclaw/erpclaw")
ONBOARDING_STATE_FILE = os.path.join(ONBOARDING_STATE_DIR, "onboarding_state.json")

VALID_CURRENCIES = ["USD", "CAD", "GBP", "EUR", "INR"]


def _load_onboarding_state():
    """Load onboarding state from file, return default if not found."""
    if os.path.exists(ONBOARDING_STATE_FILE):
        try:
            with open(ONBOARDING_STATE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"step": 1, "data": {}, "completed": False}


def _save_onboarding_state(state):
    """Save onboarding state to file."""
    os.makedirs(ONBOARDING_STATE_DIR, exist_ok=True)
    with open(ONBOARDING_STATE_FILE, "w") as f:
        json.dump(state, f)


def _clear_onboarding_state():
    """Remove onboarding state file."""
    if os.path.exists(ONBOARDING_STATE_FILE):
        os.remove(ONBOARDING_STATE_FILE)


def onboarding_step(conn, args):
    """Interactive onboarding wizard — state-machine driven.

    Each call advances one step. Pass --answer with the user's response.
    Pass --reset to restart the wizard from step 1.
    """
    if args.reset:
        _clear_onboarding_state()
        state = {"step": 1, "data": {}, "completed": False}
        _save_onboarding_state(state)
        ok({"step": 1, "completed": False,
            "prompt": "Welcome to ERPClaw! Let's set up your company.\n\nWhat's your company name?",
            "options": [], "field": "company_name"})
        return

    state = _load_onboarding_state()

    # If already completed, report that
    if state.get("completed"):
        ok({"step": 5, "completed": True,
            "prompt": "Onboarding already completed! Your company is set up and ready to use.",
            "company_name": state["data"].get("company_name", ""),
            "suggestion": "Try 'list companies' or 'show status' to see your setup."})
        return

    answer = (args.answer or "").strip()
    step = state["step"]

    # Step 1: Company name
    if step == 1:
        if not answer:
            ok({"step": 1, "completed": False,
                "prompt": "What's your company name?",
                "options": [], "field": "company_name"})
            return
        state["data"]["company_name"] = answer
        state["step"] = 2
        _save_onboarding_state(state)
        ok({"step": 2, "completed": False,
            "prompt": f"Great! Company name: {answer}\n\nWhat currency? (USD/CAD/GBP/EUR/INR)",
            "options": VALID_CURRENCIES, "field": "currency"})
        return

    # Step 2: Currency
    if step == 2:
        if not answer:
            ok({"step": 2, "completed": False,
                "prompt": "What currency? (USD/CAD/GBP/EUR/INR)",
                "options": VALID_CURRENCIES, "field": "currency"})
            return
        currency = answer.upper().strip()
        if currency not in VALID_CURRENCIES:
            ok({"step": 2, "completed": False,
                "prompt": f"'{answer}' is not a supported currency. Please choose one of: {', '.join(VALID_CURRENCIES)}",
                "options": VALID_CURRENCIES, "field": "currency",
                "error": "invalid_currency"})
            return
        state["data"]["currency"] = currency
        state["step"] = 3
        _save_onboarding_state(state)
        ok({"step": 3, "completed": False,
            "prompt": f"Currency set to {currency}.\n\nFiscal year start month? (1-12, default: 1 for January)",
            "options": ["1", "4", "7", "10"], "field": "fiscal_month"})
        return

    # Step 3: Fiscal year start month
    if step == 3:
        if not answer:
            ok({"step": 3, "completed": False,
                "prompt": "Fiscal year start month? (1-12, default: 1 for January)",
                "options": ["1", "4", "7", "10"], "field": "fiscal_month"})
            return
        try:
            month = int(answer)
            if month < 1 or month > 12:
                raise ValueError()
        except ValueError:
            ok({"step": 3, "completed": False,
                "prompt": f"'{answer}' is not a valid month. Please enter a number from 1 to 12.",
                "options": ["1", "4", "7", "10"], "field": "fiscal_month",
                "error": "invalid_month"})
            return
        state["data"]["fiscal_month"] = month
        state["step"] = 4
        _save_onboarding_state(state)
        ok({"step": 4, "completed": False,
            "prompt": "Load demo data? This creates sample customers, items, invoices, and more. (yes/no)",
            "options": ["yes", "no"], "field": "load_demo"})
        return

    # Step 4: Demo data
    if step == 4:
        if not answer:
            ok({"step": 4, "completed": False,
                "prompt": "Load demo data? (yes/no)",
                "options": ["yes", "no"], "field": "load_demo"})
            return
        load_demo = answer.lower().strip() in ("yes", "y", "true", "1")
        state["data"]["load_demo"] = load_demo
        state["step"] = 5

        # Execute: create company, seed defaults, setup chart of accounts
        data = state["data"]
        company_name = data["company_name"]
        currency = data.get("currency", "USD")
        fiscal_month = data.get("fiscal_month", 1)
        results = {"steps_completed": []}

        # Step A: Create company
        import subprocess
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db_query.py")

        try:
            result = subprocess.run(
                [sys.executable, script_path,
                 "--action", "setup-company",
                 "--name", company_name,
                 "--currency", currency,
                 "--fiscal-year-start-month", str(fiscal_month)],
                capture_output=True, text=True, timeout=30
            )
            company_result = json.loads(result.stdout) if result.stdout.strip() else {}
            if "error" in company_result:
                _save_onboarding_state(state)
                ok({"step": 5, "completed": False,
                    "error": f"Company creation failed: {company_result['error']}",
                    "prompt": "There was an error creating your company. Try again with 'onboarding-step --reset'."})
                return
            company_id = company_result.get("company_id", "")
            results["steps_completed"].append("setup-company")
            results["company_id"] = company_id
        except Exception as e:
            _save_onboarding_state(state)
            ok({"step": 5, "completed": False,
                "error": f"Company creation failed: {str(e)}",
                "prompt": "There was an error. Try again with 'onboarding-step --reset'."})
            return

        # Step B: Seed defaults
        try:
            result = subprocess.run(
                [sys.executable, script_path,
                 "--action", "seed-defaults",
                 "--company-id", company_id],
                capture_output=True, text=True, timeout=30
            )
            results["steps_completed"].append("seed-defaults")
        except Exception:
            pass  # Non-critical

        # Step C: Setup chart of accounts (via erpclaw-gl if available)
        gl_script = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "erpclaw-gl", "scripts", "db_query.py"
        )
        if os.path.exists(gl_script):
            try:
                result = subprocess.run(
                    [sys.executable, gl_script,
                     "--action", "setup-chart-of-accounts",
                     "--company-id", company_id,
                     "--standard", "us_gaap"],
                    capture_output=True, text=True, timeout=30
                )
                results["steps_completed"].append("setup-chart-of-accounts")
            except Exception:
                pass  # Non-critical

        # Step D: Load demo data if requested (via erpclaw meta-package)
        if load_demo:
            erpclaw_script = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "erpclaw", "scripts", "db_query.py"
            )
            if os.path.exists(erpclaw_script):
                try:
                    result = subprocess.run(
                        [sys.executable, erpclaw_script,
                         "--action", "seed-demo-data"],
                        capture_output=True, text=True, timeout=120
                    )
                    results["steps_completed"].append("seed-demo-data")
                except Exception:
                    pass  # Non-critical

        state["completed"] = True
        _save_onboarding_state(state)

        month_names = ["January", "February", "March", "April", "May", "June",
                       "July", "August", "September", "October", "November", "December"]
        fiscal_name = month_names[fiscal_month - 1]

        summary = (
            f"Setup complete! Here's your configuration:\n\n"
            f"  Company: {company_name}\n"
            f"  Currency: {currency}\n"
            f"  Fiscal Year Start: {fiscal_name}\n"
            f"  Demo Data: {'Loaded' if load_demo else 'Skipped'}\n\n"
            f"Steps completed: {', '.join(results['steps_completed'])}\n\n"
            f"You're ready to go! Try:\n"
            f"  - 'list customers' to see your customer data\n"
            f"  - 'show trial balance' to view your financials\n"
            f"  - 'create an invoice' to start selling"
        )

        ok({"step": 5, "completed": True,
            "prompt": summary,
            "company_name": company_name,
            "company_id": company_id,
            "currency": currency,
            "fiscal_month": fiscal_month,
            "load_demo": load_demo,
            "results": results})
        return

    # Shouldn't reach here
    ok({"step": step, "completed": False,
        "prompt": "Unknown state. Use 'onboarding-step --reset' to restart.",
        "error": "invalid_state"})


# ---------------------------------------------------------------------------
# Action Router
# ---------------------------------------------------------------------------

ACTIONS = {
    "initialize-database": initialize_database,
    "setup-company": setup_company,
    "update-company": update_company,
    "get-company": get_company,
    "list-companies": list_companies,
    "add-currency": add_currency,
    "list-currencies": list_currencies,
    "add-exchange-rate": add_exchange_rate,
    "get-exchange-rate": get_exchange_rate,
    "list-exchange-rates": list_exchange_rates,
    "add-payment-terms": add_payment_terms,
    "list-payment-terms": list_payment_terms,
    "add-uom": add_uom,
    "list-uoms": list_uoms,
    "add-uom-conversion": add_uom_conversion,
    "seed-defaults": seed_defaults,
    "get-audit-log": get_audit_log,
    "get-schema-version": get_schema_version,
    "update-regional-settings": update_regional_settings,
    "backup-database": backup_database,
    "list-backups": list_backups,
    "verify-backup": verify_backup,
    "restore-database": restore_database,
    "cleanup-backups": cleanup_backups,
    "fetch-exchange-rates": fetch_exchange_rates,
    "status": status,
    "tutorial": tutorial,
    "add-user": add_user,
    "update-user": update_user,
    "list-users": list_users,
    "get-user": get_user,
    "add-role": add_role,
    "list-roles": list_roles,
    "assign-role": assign_role,
    "revoke-role": revoke_role,
    "set-password": set_password,
    "seed-permissions": seed_permissions,
    "link-telegram-user": link_telegram_user,
    "unlink-telegram-user": unlink_telegram_user,
    "check-telegram-permission": check_telegram_permission,
    "onboarding-step": onboarding_step,
}


def main():
    parser = SafeArgumentParser(description="ERPClaw Setup Skill")
    parser.add_argument("--action", required=True, choices=sorted(ACTIONS.keys()))
    parser.add_argument("--db-path", default=None,
                        help="SQLite database path (default: ~/.openclaw/erpclaw/data.sqlite)")

    # Company flags
    parser.add_argument("--name", default=None)
    parser.add_argument("--abbr", default=None)
    parser.add_argument("--currency", default=None)
    parser.add_argument("--country", default=None)
    parser.add_argument("--industry", default=None)
    parser.add_argument("--company-id", default=None)
    parser.add_argument("--tax-id", default=None)
    parser.add_argument("--fiscal-year-start-month", type=int, default=None)
    parser.add_argument("--default-receivable-account-id", default=None)
    parser.add_argument("--default-payable-account-id", default=None)
    parser.add_argument("--default-income-account-id", default=None)
    parser.add_argument("--default-expense-account-id", default=None)
    parser.add_argument("--default-cost-center-id", default=None)
    parser.add_argument("--default-warehouse-id", default=None)
    parser.add_argument("--default-bank-account-id", default=None)
    parser.add_argument("--default-cash-account-id", default=None)
    parser.add_argument("--round-off-account-id", default=None)
    parser.add_argument("--exchange-gain-loss-account-id", default=None)
    parser.add_argument("--perpetual-inventory", type=int, default=None)
    parser.add_argument("--enable-negative-stock", type=int, default=None)
    parser.add_argument("--accounts-frozen-till-date", default=None)
    parser.add_argument("--role-allowed-for-frozen-entries", default=None)

    # Currency flags
    parser.add_argument("--code", default=None)
    parser.add_argument("--symbol", default=None)
    parser.add_argument("--decimal-places", type=int, default=None)
    parser.add_argument("--enabled", action="store_true", default=False)
    parser.add_argument("--enabled-only", action="store_true", default=False)
    parser.add_argument("--from-currency", default=None)
    parser.add_argument("--to-currency", default=None)
    parser.add_argument("--rate", default=None)
    parser.add_argument("--effective-date", default=None)
    parser.add_argument("--source", default=None)

    # Payment terms flags
    parser.add_argument("--due-days", type=int, default=None)
    parser.add_argument("--discount-percentage", default=None)
    parser.add_argument("--discount-days", type=int, default=None)
    parser.add_argument("--description", default=None)

    # UoM flags
    parser.add_argument("--must-be-whole-number", action="store_true", default=False)
    parser.add_argument("--from-uom", default=None)
    parser.add_argument("--to-uom", default=None)
    parser.add_argument("--conversion-factor", default=None)
    parser.add_argument("--item-id", default=None)

    # Audit log flags
    parser.add_argument("--entity-type", default=None)
    parser.add_argument("--entity-id", default=None)
    parser.add_argument("--audit-action", default=None)
    parser.add_argument("--from-date", default=None)
    parser.add_argument("--to-date", default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--offset", type=int, default=None)

    # Schema version flags
    parser.add_argument("--module", default=None)

    # Regional settings flags
    parser.add_argument("--date-format", default=None)
    parser.add_argument("--number-format", default=None)
    parser.add_argument("--default-tax-template-id", default=None)

    # RBAC flags
    parser.add_argument("--user-id", default=None)
    parser.add_argument("--email", default=None)
    parser.add_argument("--full-name", default=None)
    parser.add_argument("--user-status", default=None)
    parser.add_argument("--role-name", default=None)
    parser.add_argument("--password", default=None,
                        help="Password for set-password action")
    parser.add_argument("--telegram-user-id", default=None,
                        help="Telegram numeric user ID for link/check actions")
    parser.add_argument("--skill", default=None,
                        help="Skill name for permission check")
    parser.add_argument("--check-action", default=None,
                        help="Action name for permission check")

    # Backup flags
    parser.add_argument("--backup-path", default=None)
    parser.add_argument("--encrypt", action="store_true", default=False,
                        help="Encrypt the backup with AES-256")
    parser.add_argument("--passphrase", default=None,
                        help="Passphrase for encrypted backup/restore")

    # Onboarding wizard flags
    parser.add_argument("--answer", default=None,
                        help="User's answer for the current onboarding step")
    parser.add_argument("--reset", action="store_true", default=False,
                        help="Reset onboarding wizard to step 1")

    # Initialize-database flags
    parser.add_argument("--force", action="store_true", default=False,
                        help="Force re-initialize: drop and recreate the database")

    args, unknown = parser.parse_known_args()
    check_unknown_args(parser, unknown)
    check_input_lengths(args)

    # initialize-database handles its own connection lifecycle
    if args.action == "initialize-database":
        try:
            initialize_database(None, args)
        except Exception as e:
            err(str(e))
        return

    # Connect to database
    db_path = args.db_path or DEFAULT_DB_PATH
    ensure_db_exists(db_path)
    conn = get_connection(db_path)

    try:
        ACTIONS[args.action](conn, args)
    except Exception as e:
        err(str(e))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
