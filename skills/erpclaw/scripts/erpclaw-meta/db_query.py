#!/usr/bin/env python3
"""ERPClaw Meta-Package — db_query.py

Installation checker and onboarding guide for ERPClaw ERP.
This is the entry point skill — it must work standalone with zero dependencies
beyond the Python standard library.

Usage: python3 db_query.py --action <action-name> [--flags ...]
Output: JSON to stdout, exit 0 on success, exit 1 on error.
"""
import argparse
import json
import os
import re
import sqlite3
import sys
from pathlib import Path

# PyPika is optional — only available when erpclaw-setup has installed the shared lib.
# check-installation and install-guide work without it; seed-demo-data uses it for queries.
try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
    from erpclaw_lib.query import Q, P, Table, Field, fn, Order
    _HAS_PYPIKA = True
except ImportError:
    _HAS_PYPIKA = False


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_DB_PATH = os.path.expanduser("~/.openclaw/erpclaw/data.sqlite")
SKILLS_DIR = os.path.expanduser("~/clawd/skills")
SHARED_LIB_PATH = os.path.expanduser("~/.openclaw/erpclaw/lib/erpclaw_lib")

ALL_SKILLS = [
    "erpclaw-setup",
    "erpclaw-gl",
    "erpclaw-journals",
    "erpclaw-payments",
    "erpclaw-tax",
    "erpclaw-reports",
    "erpclaw-inventory",
    "erpclaw-selling",
    "erpclaw-buying",
    "erpclaw-manufacturing",
    "erpclaw-hr",
    "erpclaw-payroll",
    "erpclaw-projects",
    "erpclaw-assets",
    "erpclaw-quality",
    "erpclaw-crm",
    "erpclaw-support",
    "erpclaw-billing",
    "erpclaw-ai-engine",
    "erpclaw-analytics",
    "erpclaw-region-ca",
    "erpclaw-region-eu",
    "erpclaw-region-in",
    "erpclaw-region-uk",
    "erpclaw-integrations",
    "webclaw",
]

TIERS = [
    {
        "name": "Tier 1 — Foundation",
        "skills": ["erpclaw-setup", "erpclaw-gl"],
        "install_cmd": "clawhub install erpclaw-setup erpclaw-gl",
    },
    {
        "name": "Tier 2 — Core Accounting",
        "skills": ["erpclaw-journals", "erpclaw-payments", "erpclaw-tax", "erpclaw-reports"],
        "install_cmd": "clawhub install erpclaw-journals erpclaw-payments erpclaw-tax erpclaw-reports",
    },
    {
        "name": "Tier 3 — Supply Chain",
        "skills": ["erpclaw-inventory", "erpclaw-selling", "erpclaw-buying"],
        "install_cmd": "clawhub install erpclaw-inventory erpclaw-selling erpclaw-buying",
    },
    {
        "name": "Tier 4 — Operations",
        "skills": [
            "erpclaw-manufacturing", "erpclaw-hr", "erpclaw-payroll",
            "erpclaw-projects", "erpclaw-assets", "erpclaw-quality",
        ],
        "install_cmd": "clawhub install erpclaw-manufacturing erpclaw-hr erpclaw-payroll erpclaw-projects erpclaw-assets erpclaw-quality",
    },
    {
        "name": "Tier 5 — Extended",
        "skills": [
            "erpclaw-crm", "erpclaw-support", "erpclaw-billing",
            "erpclaw-ai-engine", "erpclaw-analytics",
        ],
        "install_cmd": "clawhub install erpclaw-crm erpclaw-support erpclaw-billing erpclaw-ai-engine erpclaw-analytics",
    },
    {
        "name": "Tier 6 — Regional",
        "skills": ["erpclaw-region-ca", "erpclaw-region-eu", "erpclaw-region-in", "erpclaw-region-uk"],
        "install_cmd": "clawhub install erpclaw-region-ca erpclaw-region-eu erpclaw-region-in erpclaw-region-uk",
    },
    {
        "name": "Tier 7 — Integrations",
        "skills": ["erpclaw-integrations"],
        "install_cmd": "clawhub install erpclaw-integrations",
    },
    {
        "name": "Web Dashboard",
        "skills": ["webclaw"],
        "install_cmd": "clawhub install webclaw",
    },
]

# Mapping of skill name to a representative set of tables it owns.
# Used to check whether the skill's tables are present in the database.
SKILL_TABLES = {
    "erpclaw-setup": ["company", "currency", "exchange_rate", "payment_terms", "uom", "audit_log"],
    "erpclaw-gl": ["account", "gl_entry", "fiscal_year", "cost_center", "budget", "naming_series"],
    "erpclaw-journals": ["journal_entry", "journal_entry_account"],
    "erpclaw-payments": ["payment_entry", "payment_entry_reference", "bank_reconciliation"],
    "erpclaw-tax": ["tax_template", "tax_template_detail", "tax_rule", "tax_withholding_category"],
    "erpclaw-reports": [],  # Reports skill reads from other tables, owns none
    "erpclaw-inventory": ["item", "warehouse", "stock_entry", "stock_ledger_entry", "item_price"],
    "erpclaw-selling": ["customer", "sales_order", "sales_order_item", "sales_invoice", "delivery_note"],
    "erpclaw-buying": ["supplier", "purchase_order", "purchase_order_item", "purchase_invoice", "purchase_receipt"],
    "erpclaw-manufacturing": ["bom", "bom_item", "work_order", "work_order_item"],
    "erpclaw-hr": ["employee", "leave_type", "leave_application", "attendance", "expense_claim"],
    "erpclaw-payroll": ["salary_structure", "salary_slip", "salary_component"],
    "erpclaw-projects": ["project", "task", "timesheet", "timesheet_detail"],
    "erpclaw-assets": ["asset", "asset_category", "asset_depreciation_schedule"],
    "erpclaw-quality": ["quality_inspection", "quality_inspection_reading"],
    "erpclaw-crm": ["crm_lead", "crm_opportunity", "crm_campaign"],
    "erpclaw-support": ["support_issue", "support_sla", "warranty_claim"],
    "erpclaw-billing": ["subscription", "subscription_plan", "billing_invoice"],
    "erpclaw-ai-engine": ["ai_anomaly", "ai_forecast"],
    "erpclaw-analytics": ["kpi_definition", "kpi_log"],
    "erpclaw-region-ca": [],
    "erpclaw-region-eu": [],
    "erpclaw-region-in": [],
    "erpclaw-region-uk": [],
    "erpclaw-integrations": ["plaid_config", "stripe_config", "s3_config"],
    "webclaw": [],
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def output_json(data):
    """Print JSON to stdout and exit 0."""
    print(json.dumps(data, indent=2, default=str))
    sys.exit(0)


def output_error(message):
    """Print error JSON to stdout and exit 1."""
    print(json.dumps({"status": "error", "error": message}))
    sys.exit(1)


def parse_version_from_skillmd(skill_dir):
    """Extract the version string from a SKILL.md YAML frontmatter.

    Uses a simple regex — no external YAML library required.
    Returns the version string or None if not found.
    """
    skillmd_path = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(skillmd_path):
        return None
    try:
        with open(skillmd_path, "r", encoding="utf-8") as f:
            content = f.read(4096)  # Frontmatter is always near the top
        # Match version: in YAML frontmatter (between --- delimiters)
        m = re.search(r"^---\s*\n(.*?)^---", content, re.MULTILINE | re.DOTALL)
        if not m:
            return None
        frontmatter = m.group(1)
        vm = re.search(r"^version:\s*[\"']?([^\s\"']+)[\"']?\s*$", frontmatter, re.MULTILINE)
        return vm.group(1) if vm else None
    except (OSError, UnicodeDecodeError):
        return None


def get_db_info(db_path):
    """Gather database information: existence, table list, company count.

    Returns a dict with database_exists, tables (set), table_count, company_count.
    """
    info = {
        "database_exists": False,
        "tables": set(),
        "table_count": 0,
        "company_count": 0,
    }
    if not os.path.isfile(db_path):
        return info

    info["database_exists"] = True
    try:
        conn = sqlite3.connect(db_path, timeout=5)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")

        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        info["tables"] = {row[0] for row in rows}
        info["table_count"] = len(info["tables"])

        if "company" in info["tables"]:
            if _HAS_PYPIKA:
                co = Table("company")
                q = Q.from_(co).select(fn.Count("*"))
                count = conn.execute(q.get_sql()).fetchone()[0]
            else:
                count = conn.execute("SELECT COUNT(*) FROM company").fetchone()[0]
            info["company_count"] = count

        conn.close()
    except sqlite3.Error:
        # Database exists but may be corrupt or locked — report what we can
        pass

    return info


def scan_installed_skills():
    """Scan ~/clawd/skills/ for installed erpclaw-* directories with SKILL.md.

    Returns a dict mapping skill name to its directory path.
    """
    installed = {}
    if not os.path.isdir(SKILLS_DIR):
        return installed

    for entry in os.listdir(SKILLS_DIR):
        if not (entry.startswith("erpclaw") or entry == "webclaw"):
            continue
        skill_dir = os.path.join(SKILLS_DIR, entry)
        if os.path.isdir(skill_dir) and os.path.isfile(os.path.join(skill_dir, "SKILL.md")):
            installed[entry] = skill_dir

    return installed


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

def check_installation(args):
    """Scan installed skills, database status, and shared library health."""
    db_path = args.db_path
    db_info = get_db_info(db_path)
    installed_dirs = scan_installed_skills()
    shared_lib_installed = os.path.isdir(SHARED_LIB_PATH)

    installed_skills = []
    missing_skills = []

    for skill_name in ALL_SKILLS:
        if skill_name in installed_dirs:
            version = parse_version_from_skillmd(installed_dirs[skill_name])
            expected_tables = SKILL_TABLES.get(skill_name, [])
            if expected_tables:
                tables_ok = all(t in db_info["tables"] for t in expected_tables)
            else:
                # Skills with no owned tables are always OK if installed
                tables_ok = True
            installed_skills.append({
                "name": skill_name,
                "version": version,
                "tables_ok": tables_ok,
            })
        else:
            missing_skills.append(skill_name)

    result = {
        "status": "ok",
        "total_skills_available": len(ALL_SKILLS),
        "installed_skills": installed_skills,
        "installed_count": len(installed_skills),
        "missing_skills": missing_skills,
        "missing_count": len(missing_skills),
        "database_exists": db_info["database_exists"],
        "database_tables": db_info["table_count"],
        "company_count": db_info["company_count"],
        "shared_library_installed": shared_lib_installed,
        "db_path": db_path,
        "skills_dir": SKILLS_DIR,
    }
    output_json(result)


def install_guide(args):
    """Recommend the next skills to install based on current state."""
    db_path = args.db_path
    db_info = get_db_info(db_path)
    installed_dirs = scan_installed_skills()
    installed_names = set(installed_dirs.keys())

    # Build tier status
    tier_results = []
    first_incomplete_tier = None

    for tier in TIERS:
        tier_skills = tier["skills"]
        installed_in_tier = [s for s in tier_skills if s in installed_names]
        missing_in_tier = [s for s in tier_skills if s not in installed_names]

        if len(missing_in_tier) == 0:
            status = "complete"
        elif len(installed_in_tier) == 0:
            status = "not_started"
        else:
            status = "partial"

        tier_obj = {
            "name": tier["name"],
            "skills": tier_skills,
            "installed": installed_in_tier,
            "missing": missing_in_tier,
            "status": status,
            "install_cmd": tier["install_cmd"],
        }
        tier_results.append(tier_obj)

        if first_incomplete_tier is None and status != "complete":
            first_incomplete_tier = tier_obj

    # Determine current tier and next recommendation
    total_installed = len(installed_names & set(ALL_SKILLS))
    total_available = len(ALL_SKILLS)
    pct = round(total_installed / total_available * 100) if total_available else 0
    progress = f"{total_installed} of {total_available} skills installed ({pct}%)"

    if first_incomplete_tier is None:
        # Everything is installed
        current_tier = "All tiers complete"
        next_recommendation = "All 29 skills are installed. You're fully set up!"
        install_command = ""
    elif total_installed == 0:
        current_tier = "Not started"
        next_recommendation = "Start with Tier 1 — Foundation: company setup and general ledger"
        install_command = TIERS[0]["install_cmd"]
    else:
        current_tier = first_incomplete_tier["name"]
        if first_incomplete_tier["status"] == "partial":
            # Some skills in the tier are missing — install just those
            missing_cmd = "clawhub install " + " ".join(first_incomplete_tier["missing"])
            next_recommendation = f"Complete {first_incomplete_tier['name']}: install remaining skills"
            install_command = missing_cmd
        else:
            next_recommendation = f"Install {first_incomplete_tier['name']}"
            install_command = first_incomplete_tier["install_cmd"]

    result = {
        "status": "ok",
        "current_tier": current_tier,
        "next_recommendation": next_recommendation,
        "install_command": install_command,
        "progress": progress,
        "database_exists": db_info["database_exists"],
        "company_count": db_info["company_count"],
        "tiers": tier_results,
    }
    output_json(result)


def seed_demo_data(args):
    """Create demo data for a company.

    If --company-id is provided, seeds demo data into that existing company.
    Otherwise, creates 'Stark Manufacturing Inc.' as the demo company.

    Uses subprocess calls to each skill's db_query.py to create:
    - Company (unless --company-id), chart of accounts, fiscal years, cost centers
    - 25 items (15 raw materials + 10 finished goods), 3 warehouses
    - 10 customers, 8 suppliers
    - Opening stock via stock entries
    - 5 journal entries, 5 sales orders + invoices, 3 purchase orders + invoices
    - 5 payment entries

    Idempotent: skips if demo data already exists for the target company.
    """
    import subprocess
    import traceback

    db_path = args.db_path
    use_existing_company = getattr(args, "company_id", None)

    # ------------------------------------------------------------------
    # Idempotency check — company exists AND demo data is populated
    # ------------------------------------------------------------------
    try:
        conn = sqlite3.connect(db_path, timeout=5)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")

        target_company_id = None
        if use_existing_company:
            # Check existing company
            row = conn.execute(
                "SELECT id FROM company WHERE id = ?", (use_existing_company,)
            ).fetchone()
            if row:
                target_company_id = row[0]
        else:
            if _HAS_PYPIKA:
                co = Table("company")
                q = Q.from_(co).select(co.id).where(co.name.like("Stark Manufacturing Inc%"))
                row = conn.execute(q.get_sql()).fetchone()
            else:
                row = conn.execute(
                    "SELECT id FROM company WHERE name LIKE 'Stark Manufacturing Inc%'"
                ).fetchone()
            if row:
                target_company_id = row[0]

        if target_company_id:
            # Company exists — check if demo data was also loaded
            if _HAS_PYPIKA:
                cu = Table("customer")
                q = Q.from_(cu).select(fn.Count("*")).where(cu.company_id == P())
                customer_count = conn.execute(q.get_sql(), (target_company_id,)).fetchone()[0]
            else:
                customer_count = conn.execute(
                    "SELECT COUNT(*) FROM customer WHERE company_id = ?", (target_company_id,)
                ).fetchone()[0]
            conn.close()
            if customer_count > 0:
                output_json({
                    "status": "ok",
                    "message": "Demo data already exists for this company",
                    "company_id": target_company_id,
                })
                return
            # Company exists but no demo data — fall through to seed
        else:
            conn.close()
            if use_existing_company:
                output_json({
                    "status": "error",
                    "error": f"Company {use_existing_company} not found",
                })
                return
    except sqlite3.Error:
        pass  # DB may not exist yet — that is fine, setup-company will create it

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _find_skill_script(skill_name):
        """Locate a skill's db_query.py — check v2 package subdirs first, then SKILLS_DIR."""
        # v2 consolidated: domain scripts live inside the erpclaw package
        v2_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", skill_name, "db_query.py")
        if os.path.isfile(v2_path):
            return os.path.abspath(v2_path)
        # Also check v2 sibling packages (erpclaw-ops, erpclaw-growth)
        v2_skill_map = {
            "erpclaw-manufacturing": "erpclaw-ops", "erpclaw-projects": "erpclaw-ops",
            "erpclaw-assets": "erpclaw-ops", "erpclaw-quality": "erpclaw-ops",
            "erpclaw-support": "erpclaw-ops",
            "erpclaw-crm": "erpclaw-growth", "erpclaw-analytics": "erpclaw-growth",
            "erpclaw-ai-engine": "erpclaw-growth",
        }
        if skill_name in v2_skill_map:
            pkg = v2_skill_map[skill_name]
            sibling = os.path.join(SKILLS_DIR, pkg, "scripts", skill_name, "db_query.py")
            if os.path.isfile(sibling):
                return sibling
        # Fallback: original location
        server_path = os.path.join(SKILLS_DIR, skill_name, "scripts", "db_query.py")
        if os.path.isfile(server_path):
            return server_path
        return None

    def _run_skill(skill_name, action_name, **kwargs):
        """Run a skill action via subprocess and return parsed JSON output.

        Keyword arguments are converted to CLI flags:
          key_name='val'  ->  --key-name val
          flag=True       ->  --flag
          skip=None       ->  (omitted)
        """
        script = _find_skill_script(skill_name)
        if not script:
            raise RuntimeError(
                f"Skill {skill_name} not found in {SKILLS_DIR}. Install it first: clawhub install {skill_name}"
            )

        cmd = [sys.executable, script, "--action", action_name, "--db-path", db_path]

        for key, val in kwargs.items():
            if val is None:
                continue
            flag = "--" + key.replace("_", "-")
            if val is True:
                cmd.append(flag)
            elif val is not False:
                cmd.extend([flag, str(val)])

        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120
        )

        stdout = result.stdout.strip()
        if not stdout:
            raise RuntimeError(
                f"{skill_name}/{action_name} produced no output. "
                f"stderr: {result.stderr.strip()}"
            )

        try:
            data = json.loads(stdout)
        except json.JSONDecodeError:
            raise RuntimeError(
                f"{skill_name}/{action_name} returned invalid JSON: {stdout[:500]}"
            )

        if result.returncode != 0:
            err_msg = data.get("error", stdout[:300])
            raise RuntimeError(f"{skill_name}/{action_name} failed: {err_msg}")

        return data

    def _progress(msg):
        """Print progress to stderr."""
        sys.stderr.write(f"[seed-demo-data] {msg}\n")
        sys.stderr.flush()

    def _get_account_id(conn, account_number, company_id):
        """Look up an account ID by account_number within a company."""
        if _HAS_PYPIKA:
            t = Table("account")
            q = (Q.from_(t).select(t.id)
                 .where(t.account_number == P())
                 .where(t.company_id == P()))
            row = conn.execute(q.get_sql(), (account_number, company_id)).fetchone()
        else:
            row = conn.execute(
                "SELECT id FROM account WHERE account_number = ? AND company_id = ?",
                (account_number, company_id),
            ).fetchone()
        return row[0] if row else None

    def _get_account_id_by_name(conn, name_pattern, company_id):
        """Look up an account ID by name LIKE pattern within a company."""
        if _HAS_PYPIKA:
            t = Table("account")
            q = (Q.from_(t).select(t.id)
                 .where(t.name.like(P()))
                 .where(t.company_id == P()))
            row = conn.execute(q.get_sql(), (name_pattern, company_id)).fetchone()
        else:
            row = conn.execute(
                "SELECT id FROM account WHERE name LIKE ? AND company_id = ?",
                (name_pattern, company_id),
            ).fetchone()
        return row[0] if row else None

    # Track what was created for the summary
    summary = {
        "customers": 0,
        "suppliers": 0,
        "items": 0,
        "item_groups": 0,
        "warehouses": 0,
        "stock_entries": 0,
        "journal_entries": 0,
        "sales_orders": 0,
        "sales_invoices": 0,
        "purchase_orders": 0,
        "purchase_receipts": 0,
        "purchase_invoices": 0,
        "payments": 0,
        "boms": 0,
        "work_orders": 0,
        "departments": 0,
        "employees": 0,
        "campaigns": 0,
        "leads": 0,
        "opportunities": 0,
        "asset_categories": 0,
        "assets": 0,
        "slas": 0,
        "support_issues": 0,
        "projects": 0,
        "tasks": 0,
    }
    errors = []
    company_id = None

    # ==================================================================
    # PHASE 1: Foundation
    # ==================================================================
    if use_existing_company:
        # Use the provided company — skip creating Stark Manufacturing
        company_id = use_existing_company
        _progress(f"Phase 1: Using existing company {company_id}...")
    else:
        try:
            _progress("Phase 1: Setting up company...")
            result = _run_skill("erpclaw-setup", "setup-company",
                                name="Stark Manufacturing Inc.",
                                currency="USD",
                                country="United States",
                                fiscal_year_start_month=1)
            company_id = result.get("company_id")
            _progress(f"  Company created: {company_id}")
        except Exception as e:
            errors.append(f"Phase 1 (setup-company): {e}")
            # Fall back: look for any existing company to use
            try:
                conn = sqlite3.connect(db_path, timeout=5)
                conn.row_factory = sqlite3.Row
                if _HAS_PYPIKA:
                    co = Table("company")
                    q = (Q.from_(co).select(co.id, co.name)
                         .orderby(co.created_at, order=Order.asc)
                         .limit(1))
                    row = conn.execute(q.get_sql()).fetchone()
                else:
                    row = conn.execute(
                        "SELECT id, name FROM company ORDER BY created_at LIMIT 1"
                    ).fetchone()
                conn.close()
                if row:
                    company_id = row[0]
                    _progress(f"  Using existing company: {row[1]} ({company_id})")
                    errors.pop()  # Remove the setup-company error since we recovered
            except sqlite3.Error:
                pass
        if not company_id:
            output_json({
                "status": "error",
                "error": f"Cannot create demo company: {e}",
                "errors": errors,
            })
            return

    try:
        _progress("  Seeding defaults (currencies, UoMs, payment terms)...")
        _run_skill("erpclaw-setup", "seed-defaults", company_id=company_id)
    except Exception as e:
        errors.append(f"Phase 1 (seed-defaults): {e}")

    try:
        _progress("  Setting up chart of accounts (US GAAP)...")
        _run_skill("erpclaw-gl", "setup-chart-of-accounts",
                    template="us_gaap", company_id=company_id)
    except Exception as e:
        errors.append(f"Phase 1 (chart-of-accounts): {e}")

    try:
        _progress("  Adding fiscal years 2025 and 2026...")
        _run_skill("erpclaw-gl", "add-fiscal-year",
                    name="FY 2025", start_date="2025-01-01",
                    end_date="2025-12-31", company_id=company_id)
        _run_skill("erpclaw-gl", "add-fiscal-year",
                    name="FY 2026", start_date="2026-01-01",
                    end_date="2026-12-31", company_id=company_id)
    except Exception as e:
        errors.append(f"Phase 1 (fiscal-years): {e}")

    try:
        _progress("  Seeding naming series...")
        _run_skill("erpclaw-gl", "seed-naming-series", company_id=company_id)
    except Exception as e:
        errors.append(f"Phase 1 (naming-series): {e}")

    # ==================================================================
    # PHASE 2: Look up key account IDs
    # ==================================================================
    _progress("Phase 2: Looking up account IDs...")
    accounts = {}
    try:
        conn = sqlite3.connect(db_path, timeout=5)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")

        account_map = {
            "cash":                  "1111",  # Petty Cash
            "accounts_receivable":   "1121",  # Trade Receivables
            "inventory":             "1131",  # Raw Materials
            "prepaid_expenses":      "1141",  # Prepaid Insurance
            "fixed_assets":          "1214",  # Office Equipment
            "accum_depreciation":    "1217",  # Accumulated Depreciation - FF&E
            "accounts_payable":      "2111",  # Trade Payables
            "sales_revenue":         "4110",  # Sales Revenue
            "cogs":                  "5110",  # COGS - Materials
            "operating_expenses":    "5240",  # Office Supplies
            "payroll_expense":       "5210",  # Salaries and Wages
            "rent_expense":          "5220",  # Rent Expense
            "utilities_expense":     "5230",  # Utilities
            "depreciation_expense":  "5260",  # Depreciation Expense
            "bank":                  "1112",  # Operating Checking Account
        }
        for key, acct_num in account_map.items():
            aid = _get_account_id(conn, acct_num, company_id)
            if aid:
                accounts[key] = aid
            else:
                _progress(f"  WARNING: Account {acct_num} ({key}) not found")

        conn.close()
        _progress(f"  Found {len(accounts)} of {len(account_map)} accounts")
    except Exception as e:
        errors.append(f"Phase 2 (account lookup): {e}")

    # ==================================================================
    # PHASE 3: Cost centers
    # ==================================================================
    cost_center_ids = {}
    try:
        _progress("Phase 3: Adding cost centers...")
        for cc_name in ("Main", "Sales", "Manufacturing", "Admin"):
            try:
                result = _run_skill("erpclaw-gl", "add-cost-center",
                                     name=cc_name, company_id=company_id)
                cost_center_ids[cc_name] = result.get("cost_center_id")
                _progress(f"  Cost center: {cc_name}")
            except Exception as e:
                if "duplicate" in str(e).lower() or "UNIQUE" in str(e):
                    _progress(f"  Cost center '{cc_name}' already exists, skipping")
                    # Look up existing
                    try:
                        conn_tmp = sqlite3.connect(db_path, timeout=5)
                        if _HAS_PYPIKA:
                            cc = Table("cost_center")
                            q = (Q.from_(cc).select(cc.id)
                                 .where(cc.name == P())
                                 .where(cc.company_id == P()))
                            row = conn_tmp.execute(q.get_sql(), (cc_name, company_id)).fetchone()
                        else:
                            row = conn_tmp.execute(
                                "SELECT id FROM cost_center WHERE name = ? AND company_id = ?",
                                (cc_name, company_id)).fetchone()
                        if row:
                            cost_center_ids[cc_name] = row[0]
                        conn_tmp.close()
                    except Exception:
                        pass
                else:
                    errors.append(f"Phase 3 (cost-center {cc_name}): {e}")
    except Exception as e:
        errors.append(f"Phase 3 (cost-centers): {e}")

    # ==================================================================
    # PHASE 5: Master Data — Warehouses, Item Groups, Items, Customers, Suppliers
    # ==================================================================
    _progress("Phase 5: Creating master data...")

    # --- Warehouses ---
    warehouse_ids = {}
    warehouse_defs = [
        ("Main Warehouse", "stores"),
        ("Raw Materials Store", "stores"),
        ("Finished Goods Store", "stores"),
    ]
    for wh_name, wh_type in warehouse_defs:
        try:
            result = _run_skill("erpclaw-inventory", "add-warehouse",
                                name=wh_name, company_id=company_id,
                                warehouse_type=wh_type)
            wh_id = result.get("warehouse_id")
            warehouse_ids[wh_name] = wh_id
            summary["warehouses"] += 1
            _progress(f"  Warehouse: {wh_name}")
        except Exception as e:
            errors.append(f"Phase 5 (warehouse {wh_name}): {e}")

    # --- Item Groups ---
    item_group_ids = {}
    for group_name in ("Raw Material", "Finished Good"):
        try:
            result = _run_skill("erpclaw-inventory", "add-item-group",
                                name=group_name)
            ig_id = result.get("item_group_id")
            item_group_ids[group_name] = ig_id
            summary["item_groups"] += 1
            _progress(f"  Item group: {group_name}")
        except Exception as e:
            if "duplicate" in str(e).lower() or "UNIQUE" in str(e):
                _progress(f"  Item group '{group_name}' already exists")
                # Try to retrieve existing
                try:
                    conn = sqlite3.connect(db_path, timeout=5)
                    conn.row_factory = sqlite3.Row
                    if _HAS_PYPIKA:
                        ig = Table("item_group")
                        q = Q.from_(ig).select(ig.id).where(ig.name == P())
                        row = conn.execute(q.get_sql(), (group_name,)).fetchone()
                    else:
                        row = conn.execute(
                            "SELECT id FROM item_group WHERE name = ?", (group_name,)
                        ).fetchone()
                    if row:
                        item_group_ids[group_name] = row[0]
                    conn.close()
                except Exception:
                    pass
            else:
                errors.append(f"Phase 5 (item-group {group_name}): {e}")

    # --- Items ---
    raw_group = item_group_ids.get("Raw Material")
    fg_group = item_group_ids.get("Finished Good")

    raw_materials = [
        ("RAW-001", "Steel Sheet",        "45.00",   "Kg"),
        ("RAW-002", "Aluminum Rod",        "32.00",   "Kg"),
        ("RAW-003", "Copper Wire",         "28.00",   "Meter"),
        ("RAW-004", "Plastic Pellets",     "12.00",   "Kg"),
        ("RAW-005", "Rubber Gasket",       "3.50",    "Nos"),
        ("RAW-006", "Stainless Bolt M8",   "0.85",    "Nos"),
        ("RAW-007", "Circuit Board",       "15.00",   "Nos"),
        ("RAW-008", "LED Module",          "8.50",    "Nos"),
        ("RAW-009", "Bearing 6205",        "6.25",    "Nos"),
        ("RAW-010", "Lubricant Oil",       "22.00",   "Liter"),
        ("RAW-011", "Packing Box Large",   "4.50",    "Nos"),
        ("RAW-012", "Safety Label",        "0.35",    "Nos"),
        ("RAW-013", "Welding Rod",         "18.00",   "Kg"),
        ("RAW-014", "Paint Primer",        "35.00",   "Liter"),
        ("RAW-015", "Insulation Tape",     "2.75",    "Roll"),
    ]

    finished_goods = [
        ("FG-001", "Industrial Widget A",      "125.00",  "Nos"),
        ("FG-002", "Heavy Duty Widget B",      "185.00",  "Nos"),
        ("FG-003", "Precision Gadget X",       "340.00",  "Nos"),
        ("FG-004", "Standard Assembly Kit",    "89.00",   "Nos"),
        ("FG-005", "Premium Assembly Kit",     "165.00",  "Nos"),
        ("FG-006", "Motor Housing Unit",       "210.00",  "Nos"),
        ("FG-007", "Control Panel CP-100",     "275.00",  "Nos"),
        ("FG-008", "Sensor Module SM-50",      "95.00",   "Nos"),
        ("FG-009", "Power Supply PS-200",      "130.00",  "Nos"),
        ("FG-010", "Maintenance Tool Set",     "55.00",   "Nos"),
    ]

    item_ids = {}  # item_code -> item_id

    for code, name, rate, uom in raw_materials:
        try:
            result = _run_skill("erpclaw-inventory", "add-item",
                                item_code=code, item_name=name,
                                item_group=raw_group, stock_uom=uom,
                                standard_rate=rate)
            item_ids[code] = result.get("item_id")
            summary["items"] += 1
        except Exception as e:
            errors.append(f"Phase 5 (item {code}): {e}")
    _progress(f"  Raw materials: {len([c for c in item_ids if c.startswith('RAW')])}/15")

    for code, name, rate, uom in finished_goods:
        try:
            result = _run_skill("erpclaw-inventory", "add-item",
                                item_code=code, item_name=name,
                                item_group=fg_group, stock_uom=uom,
                                standard_rate=rate)
            item_ids[code] = result.get("item_id")
            summary["items"] += 1
        except Exception as e:
            errors.append(f"Phase 5 (item {code}): {e}")
    _progress(f"  Finished goods: {len([c for c in item_ids if c.startswith('FG')])}/10")

    # --- Customers ---
    customer_names = [
        "Acme Corporation", "Wayne Industries", "Oscorp Industries",
        "Pied Piper Inc", "Hooli Technologies", "Stark Retail Outlets",
        "Parker Electronics", "Xavier Laboratories", "LexCorp",
        "Daily Planet Media",
    ]
    customer_ids = {}  # name -> id
    for cname in customer_names:
        try:
            result = _run_skill("erpclaw-selling", "add-customer",
                                name=cname, company_id=company_id)
            customer_ids[cname] = result.get("customer_id")
            summary["customers"] += 1
        except Exception as e:
            errors.append(f"Phase 5 (customer {cname}): {e}")
    _progress(f"  Customers: {summary['customers']}/10")

    # --- Suppliers ---
    supplier_names = [
        "Global Parts International", "Steel Supply Co",
        "Advanced Electronics Ltd", "Pacific Plastics",
        "Metro Fasteners Inc", "Precision Bearings Corp",
        "GreenChem Solutions", "TechWire Direct",
    ]
    supplier_ids = {}  # name -> id
    for sname in supplier_names:
        try:
            result = _run_skill("erpclaw-buying", "add-supplier",
                                name=sname, company_id=company_id)
            supplier_ids[sname] = result.get("supplier_id")
            summary["suppliers"] += 1
        except Exception as e:
            errors.append(f"Phase 5 (supplier {sname}): {e}")
    _progress(f"  Suppliers: {summary['suppliers']}/8")

    # ==================================================================
    # PHASE 6: Opening Stock
    # ==================================================================
    _progress("Phase 6: Creating opening stock entries...")

    raw_wh = warehouse_ids.get("Raw Materials Store")
    fg_wh = warehouse_ids.get("Finished Goods Store")

    # Raw material opening stock
    raw_stock = [
        ("RAW-001", "500"),
        ("RAW-002", "300"),
        ("RAW-003", "200"),
        ("RAW-004", "100"),
        ("RAW-005", "1000"),
        ("RAW-006", "5000"),
        ("RAW-007", "200"),
        ("RAW-008", "300"),
        ("RAW-009", "150"),
        ("RAW-010", "50"),
        ("RAW-011", "200"),
        ("RAW-012", "2000"),
        ("RAW-013", "80"),
        ("RAW-014", "30"),
        ("RAW-015", "500"),
    ]

    if raw_wh:
        raw_items_json = []
        for code, qty in raw_stock:
            iid = item_ids.get(code)
            if iid:
                raw_items_json.append({
                    "item_id": iid,
                    "qty": qty,
                    "to_warehouse_id": raw_wh,
                })
        if raw_items_json:
            try:
                result = _run_skill("erpclaw-inventory", "add-stock-entry",
                                    entry_type="receive",
                                    company_id=company_id,
                                    posting_date="2026-01-01",
                                    items=json.dumps(raw_items_json))
                se_id = result.get("stock_entry_id")
                _run_skill("erpclaw-inventory", "submit-stock-entry",
                            stock_entry_id=se_id)
                summary["stock_entries"] += 1
                _progress("  Raw materials opening stock submitted")
            except Exception as e:
                errors.append(f"Phase 6 (raw material stock entry): {e}")

    # Finished goods opening stock
    fg_stock = [
        ("FG-001", "50"),
        ("FG-002", "30"),
        ("FG-003", "20"),
        ("FG-004", "40"),
        ("FG-005", "25"),
        ("FG-006", "15"),
        ("FG-007", "10"),
        ("FG-008", "35"),
        ("FG-009", "20"),
        ("FG-010", "60"),
    ]

    if fg_wh:
        fg_items_json = []
        for code, qty in fg_stock:
            iid = item_ids.get(code)
            if iid:
                fg_items_json.append({
                    "item_id": iid,
                    "qty": qty,
                    "to_warehouse_id": fg_wh,
                })
        if fg_items_json:
            try:
                result = _run_skill("erpclaw-inventory", "add-stock-entry",
                                    entry_type="receive",
                                    company_id=company_id,
                                    posting_date="2026-01-01",
                                    items=json.dumps(fg_items_json))
                se_id = result.get("stock_entry_id")
                _run_skill("erpclaw-inventory", "submit-stock-entry",
                            stock_entry_id=se_id)
                summary["stock_entries"] += 1
                _progress("  Finished goods opening stock submitted")
            except Exception as e:
                errors.append(f"Phase 6 (finished goods stock entry): {e}")

    # ==================================================================
    # PHASE 7A: Journal Entries
    # ==================================================================
    _progress("Phase 7A: Creating journal entries...")

    cash_id = accounts.get("cash")
    rent_id = accounts.get("rent_expense")
    utilities_id = accounts.get("utilities_expense")
    prepaid_id = accounts.get("prepaid_expenses")
    opex_id = accounts.get("operating_expenses")
    dep_expense_id = accounts.get("depreciation_expense")
    accum_dep_id = accounts.get("accum_depreciation")

    journal_entries = [
        # (remark, debit_account, credit_account, amount, posting_date)
        ("Monthly rent payment - January 2026",
         rent_id, cash_id, "5000.00", "2026-01-15"),
        ("Utilities payment - January 2026",
         utilities_id, cash_id, "1200.00", "2026-01-20"),
        ("Insurance prepaid - annual premium",
         prepaid_id, cash_id, "12000.00", "2026-01-05"),
        ("Office supplies - January 2026",
         opex_id, cash_id, "800.00", "2026-01-25"),
        ("Depreciation - January 2026",
         dep_expense_id, accum_dep_id, "2500.00", "2026-01-31"),
    ]

    admin_cc = cost_center_ids.get("Admin")

    for remark, debit_acct, credit_acct, amount, pdate in journal_entries:
        if not debit_acct or not credit_acct:
            errors.append(f"Phase 7A (JE '{remark}'): missing account IDs")
            continue
        try:
            debit_line = {"account_id": debit_acct, "debit": amount, "credit": "0"}
            credit_line = {"account_id": credit_acct, "debit": "0", "credit": amount}
            # P&L accounts require cost_center_id (GL validation step 6)
            if admin_cc:
                debit_line["cost_center_id"] = admin_cc
                credit_line["cost_center_id"] = admin_cc
            lines = json.dumps([debit_line, credit_line])
            result = _run_skill("erpclaw-journals", "add-journal-entry",
                                company_id=company_id,
                                posting_date=pdate,
                                entry_type="journal",
                                remark=remark,
                                lines=lines)
            je_id = result.get("journal_entry_id")
            _run_skill("erpclaw-journals", "submit-journal-entry",
                        journal_entry_id=je_id)
            summary["journal_entries"] += 1
            _progress(f"  JE: {remark[:40]}...")
        except Exception as e:
            errors.append(f"Phase 7A (JE '{remark}'): {e}")

    # ==================================================================
    # PHASE 7B: Sales Orders + Invoices
    # ==================================================================
    _progress("Phase 7B: Creating sales orders and invoices...")

    # (customer_name, item_code, qty, rate)
    sales_orders = [
        ("Acme Corporation",  "FG-001", "20", "199.00"),
        ("Wayne Industries",  "FG-002", "10", "299.00"),
        ("Oscorp Industries", "FG-003", "5",  "549.00"),
        ("Pied Piper Inc",    "FG-004", "15", "149.00"),
        ("Hooli Technologies","FG-006", "8",  "349.00"),
    ]

    sales_invoice_ids = {}  # customer_name -> invoice_id
    for cust_name, item_code, qty, rate in sales_orders:
        cust_id = customer_ids.get(cust_name)
        iid = item_ids.get(item_code)
        if not cust_id or not iid:
            errors.append(
                f"Phase 7B (SO for {cust_name}): missing customer_id or item_id"
            )
            continue
        try:
            items_json = json.dumps([{
                "item_id": iid,
                "qty": qty,
                "rate": rate,
                "warehouse_id": fg_wh,
            }])
            result = _run_skill("erpclaw-selling", "add-sales-order",
                                customer_id=cust_id,
                                company_id=company_id,
                                posting_date="2026-01-15",
                                delivery_date="2026-02-15",
                                items=items_json)
            so_id = result.get("sales_order_id")

            _run_skill("erpclaw-selling", "submit-sales-order",
                        sales_order_id=so_id)
            summary["sales_orders"] += 1

            # Create sales invoice from SO
            si_result = _run_skill("erpclaw-selling", "create-sales-invoice",
                                    sales_order_id=so_id,
                                    posting_date="2026-01-20")
            si_id = si_result.get("sales_invoice_id")

            _run_skill("erpclaw-selling", "submit-sales-invoice",
                        sales_invoice_id=si_id)
            sales_invoice_ids[cust_name] = si_id
            summary["sales_invoices"] += 1

            _progress(f"  SO+SI: {cust_name} ({qty} x {item_code})")
        except Exception as e:
            errors.append(f"Phase 7B (SO/SI for {cust_name}): {e}")

    # ==================================================================
    # PHASE 7C: Purchase Orders + Receipts + Invoices
    # ==================================================================
    _progress("Phase 7C: Creating purchase orders, receipts, invoices...")

    # (supplier_name, item_code, qty, rate)
    purchase_orders = [
        ("Global Parts International", "RAW-001", "200", "45.00"),
        ("Advanced Electronics Ltd",   "RAW-007", "100", "15.00"),
        ("TechWire Direct",            "RAW-008", "500", "8.50"),
    ]

    purchase_invoice_ids = {}  # supplier_name -> invoice_id
    for supp_name, item_code, qty, rate in purchase_orders:
        supp_id = supplier_ids.get(supp_name)
        iid = item_ids.get(item_code)
        raw_wh_id = warehouse_ids.get("Raw Materials Store")
        if not supp_id or not iid:
            errors.append(
                f"Phase 7C (PO for {supp_name}): missing supplier_id or item_id"
            )
            continue
        try:
            items_json = json.dumps([{
                "item_id": iid,
                "qty": qty,
                "rate": rate,
                "warehouse_id": raw_wh_id,
            }])
            result = _run_skill("erpclaw-buying", "add-purchase-order",
                                supplier_id=supp_id,
                                company_id=company_id,
                                posting_date="2026-01-10",
                                items=items_json)
            po_id = result.get("purchase_order_id")

            _run_skill("erpclaw-buying", "submit-purchase-order",
                        purchase_order_id=po_id)
            summary["purchase_orders"] += 1

            # Create purchase receipt from PO
            pr_result = _run_skill("erpclaw-buying", "create-purchase-receipt",
                                    purchase_order_id=po_id,
                                    posting_date="2026-01-12")
            pr_id = pr_result.get("purchase_receipt_id")

            _run_skill("erpclaw-buying", "submit-purchase-receipt",
                        purchase_receipt_id=pr_id)
            summary["purchase_receipts"] += 1

            # Create purchase invoice from PO
            pi_result = _run_skill("erpclaw-buying", "create-purchase-invoice",
                                    purchase_order_id=po_id,
                                    posting_date="2026-01-15")
            pi_id = pi_result.get("purchase_invoice_id")

            _run_skill("erpclaw-buying", "submit-purchase-invoice",
                        purchase_invoice_id=pi_id)
            purchase_invoice_ids[supp_name] = pi_id
            summary["purchase_invoices"] += 1

            _progress(f"  PO+PR+PI: {supp_name} ({qty} x {item_code})")
        except Exception as e:
            errors.append(f"Phase 7C (PO/PR/PI for {supp_name}): {e}")

    # ==================================================================
    # PHASE 7D: Payments
    # ==================================================================
    _progress("Phase 7D: Creating payments...")

    ar_id = accounts.get("accounts_receivable")
    ap_id = accounts.get("accounts_payable")
    bank_id = accounts.get("bank") or cash_id

    # Customer payments (receive): money comes FROM customer, TO our bank
    # paid_from = AR (receivable), paid_to = bank/cash
    customer_payments = [
        ("Acme Corporation",  "3980.00"),
        ("Wayne Industries",  "2990.00"),
        ("Oscorp Industries", "1000.00"),  # partial
    ]

    for cust_name, amount in customer_payments:
        cust_id = customer_ids.get(cust_name)
        si_id = sales_invoice_ids.get(cust_name)
        if not cust_id or not ar_id or not bank_id:
            errors.append(f"Phase 7D (payment {cust_name}): missing IDs")
            continue
        try:
            alloc = None
            if si_id:
                alloc = json.dumps([{
                    "voucher_type": "sales_invoice",
                    "voucher_id": si_id,
                    "allocated_amount": amount,
                }])
            result = _run_skill("erpclaw-payments", "add-payment",
                                company_id=company_id,
                                payment_type="receive",
                                posting_date="2026-02-01",
                                party_type="customer",
                                party_id=cust_id,
                                paid_from_account=ar_id,
                                paid_to_account=bank_id,
                                paid_amount=amount,
                                allocations=alloc)
            pe_id = result.get("payment_entry_id")

            _run_skill("erpclaw-payments", "submit-payment",
                        payment_entry_id=pe_id)
            summary["payments"] += 1
            _progress(f"  Payment received: {cust_name} ${amount}")
        except Exception as e:
            errors.append(f"Phase 7D (customer payment {cust_name}): {e}")

    # Supplier payments (pay): money goes FROM our bank, TO supplier
    # paid_from = bank/cash, paid_to = AP (payable)
    supplier_payments = [
        ("Global Parts International", "9000.00"),
        ("Advanced Electronics Ltd",   "1500.00"),
    ]

    for supp_name, amount in supplier_payments:
        supp_id = supplier_ids.get(supp_name)
        pi_id = purchase_invoice_ids.get(supp_name)
        if not supp_id or not ap_id or not bank_id:
            errors.append(f"Phase 7D (payment {supp_name}): missing IDs")
            continue
        try:
            alloc = None
            if pi_id:
                alloc = json.dumps([{
                    "voucher_type": "purchase_invoice",
                    "voucher_id": pi_id,
                    "allocated_amount": amount,
                }])
            result = _run_skill("erpclaw-payments", "add-payment",
                                company_id=company_id,
                                payment_type="pay",
                                posting_date="2026-02-05",
                                party_type="supplier",
                                party_id=supp_id,
                                paid_from_account=bank_id,
                                paid_to_account=ap_id,
                                paid_amount=amount,
                                allocations=alloc)
            pe_id = result.get("payment_entry_id")

            _run_skill("erpclaw-payments", "submit-payment",
                        payment_entry_id=pe_id)
            summary["payments"] += 1
            _progress(f"  Payment sent: {supp_name} ${amount}")
        except Exception as e:
            errors.append(f"Phase 7D (supplier payment {supp_name}): {e}")

    # ==================================================================
    # PHASE 8: Manufacturing — BOMs and Work Orders
    # ==================================================================
    _progress("Phase 8: Manufacturing...")

    # Build item_code -> item_id map from DB (items were created in Phase 5)
    try:
        conn = sqlite3.connect(db_path, timeout=5)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        if _HAS_PYPIKA:
            it = Table("item")
            q = Q.from_(it).select(it.id, it.item_code)
            item_rows = conn.execute(q.get_sql()).fetchall()
        else:
            item_rows = conn.execute(
                "SELECT id, item_code FROM item"
            ).fetchall()
        item_map = {r["item_code"]: r["id"] for r in item_rows}
        conn.close()
        # Merge into item_ids (in case some were missed during creation)
        for code, iid in item_map.items():
            if code not in item_ids:
                item_ids[code] = iid
    except Exception as e:
        errors.append(f"Phase 8 (item lookup): {e}")

    bom_ids = {}  # label -> bom_id
    bom_defs = [
        # (label, fg_item_code, bom_items: [(item_code, qty, uom), ...])
        ("BOM-FG001", "FG-001", [
            ("RAW-001", "5", "Kg"),
            ("RAW-005", "2", "Nos"),
            ("RAW-006", "8", "Nos"),
        ]),
        ("BOM-FG002", "FG-002", [
            ("RAW-002", "3", "Kg"),
            ("RAW-009", "4", "Nos"),
            ("RAW-013", "2", "Kg"),
        ]),
        ("BOM-FG003", "FG-003", [
            ("RAW-003", "10", "Meter"),
            ("RAW-007", "2", "Nos"),
            ("RAW-008", "4", "Nos"),
        ]),
    ]

    for label, fg_code, bom_items_list in bom_defs:
        fg_id = item_ids.get(fg_code)
        if not fg_id:
            errors.append(f"Phase 8 (BOM {label}): finished good {fg_code} not found")
            continue
        items_json_list = []
        skip_bom = False
        for rm_code, rm_qty, rm_uom in bom_items_list:
            rm_id = item_ids.get(rm_code)
            if not rm_id:
                errors.append(f"Phase 8 (BOM {label}): raw material {rm_code} not found")
                skip_bom = True
                break
            # Look up the standard_rate from item_ids or use a fallback
            # We need the rate for BOM items; fetch from the item table
            rate = "0"
            try:
                conn_tmp = sqlite3.connect(db_path, timeout=5)
                conn_tmp.row_factory = sqlite3.Row
                if _HAS_PYPIKA:
                    it = Table("item")
                    q = Q.from_(it).select(it.standard_rate).where(it.id == P())
                    rate_row = conn_tmp.execute(q.get_sql(), (rm_id,)).fetchone()
                else:
                    rate_row = conn_tmp.execute(
                        "SELECT standard_rate FROM item WHERE id = ?", (rm_id,)
                    ).fetchone()
                if rate_row and rate_row["standard_rate"]:
                    rate = rate_row["standard_rate"]
                conn_tmp.close()
            except Exception:
                pass
            items_json_list.append({
                "item_id": rm_id,
                "quantity": rm_qty,
                "rate": rate,
            })
        if skip_bom:
            continue
        try:
            result = _run_skill("erpclaw-manufacturing", "add-bom",
                                item_id=fg_id,
                                quantity="1",
                                items=json.dumps(items_json_list),
                                company_id=company_id)
            bom_ids[label] = result.get("bom_id")
            _progress(f"  BOM: {label} ({fg_code})")
        except Exception as e:
            errors.append(f"Phase 8 (BOM {label}): {e}")

    summary["boms"] = len(bom_ids)

    # Create 2 work orders
    wo_count = 0
    wo_defs = [
        ("BOM-FG001", "50", "2026-02-01"),
        ("BOM-FG002", "30", "2026-02-10"),
    ]
    for bom_label, wo_qty, planned_date in wo_defs:
        bom_id = bom_ids.get(bom_label)
        if not bom_id:
            errors.append(f"Phase 8 (WO for {bom_label}): BOM not found")
            continue
        try:
            result = _run_skill("erpclaw-manufacturing", "add-work-order",
                                bom_id=bom_id,
                                quantity=wo_qty,
                                planned_start_date=planned_date,
                                company_id=company_id)
            wo_count += 1
            _progress(f"  Work order: {bom_label} x{wo_qty}")
        except Exception as e:
            errors.append(f"Phase 8 (WO for {bom_label}): {e}")

    summary["work_orders"] = wo_count

    # ==================================================================
    # PHASE 9: HR & Payroll
    # ==================================================================
    _progress("Phase 9: HR & Payroll...")

    dept_id = None
    desig_id = None

    # Create department
    try:
        result = _run_skill("erpclaw-hr", "add-department",
                            name="Engineering",
                            company_id=company_id)
        dept_id = result.get("department_id")
        _progress("  Department: Engineering")
    except Exception as e:
        errors.append(f"Phase 9 (department): {e}")

    # Create designation
    try:
        result = _run_skill("erpclaw-hr", "add-designation",
                            name="Software Engineer")
        desig_id = result.get("designation_id")
        _progress("  Designation: Software Engineer")
    except Exception as e:
        errors.append(f"Phase 9 (designation): {e}")

    # Create employees
    employee_defs = [
        ("Sarah", "Chen",    "2025-06-01"),
        ("Mike",  "Johnson", "2025-08-15"),
        ("Lisa",  "Park",    "2025-03-01"),
        ("James", "Wilson",  "2025-11-01"),
        ("Rachel","Adams",   "2026-01-15"),
    ]
    employee_ids_list = []
    emp_count = 0
    for first, last, join_date in employee_defs:
        try:
            kwargs = {
                "first_name": first,
                "last_name": last,
                "date_of_joining": join_date,
                "company_id": company_id,
            }
            if dept_id:
                kwargs["department_id"] = dept_id
            if desig_id:
                kwargs["designation_id"] = desig_id
            result = _run_skill("erpclaw-hr", "add-employee", **kwargs)
            emp_id = result.get("employee_id")
            if emp_id:
                employee_ids_list.append(emp_id)
            emp_count += 1
            _progress(f"  Employee: {first} {last}")
        except Exception as e:
            errors.append(f"Phase 9 (employee {first} {last}): {e}")

    summary["departments"] = 1 if dept_id else 0
    summary["employees"] = emp_count

    # Payroll: create salary components, structure, and assignments
    basic_comp_id = None
    hra_comp_id = None

    try:
        result = _run_skill("erpclaw-payroll", "add-salary-component",
                            name="Basic Salary",
                            component_type="earning")
        basic_comp_id = result.get("salary_component_id")
        _progress("  Salary component: Basic Salary")
    except Exception as e:
        errors.append(f"Phase 9 (salary component Basic): {e}")

    try:
        result = _run_skill("erpclaw-payroll", "add-salary-component",
                            name="HRA",
                            component_type="earning")
        hra_comp_id = result.get("salary_component_id")
        _progress("  Salary component: HRA")
    except Exception as e:
        errors.append(f"Phase 9 (salary component HRA): {e}")

    structure_id = None
    if basic_comp_id and hra_comp_id:
        try:
            components_json = json.dumps([
                {"salary_component_id": basic_comp_id, "amount": "6000"},
                {"salary_component_id": hra_comp_id, "amount": "1500"},
            ])
            result = _run_skill("erpclaw-payroll", "add-salary-structure",
                                name="Standard Engineer Package",
                                company_id=company_id,
                                components=components_json)
            structure_id = result.get("salary_structure_id")
            _progress("  Salary structure: Standard Engineer Package")
        except Exception as e:
            errors.append(f"Phase 9 (salary structure): {e}")

    # Assign structure to all employees
    if structure_id:
        for emp_id in employee_ids_list:
            try:
                _run_skill("erpclaw-payroll", "add-salary-assignment",
                           employee_id=emp_id,
                           salary_structure_id=structure_id,
                           base_amount="7500",
                           effective_from="2026-01-01")
            except Exception as e:
                errors.append(f"Phase 9 (salary assignment {emp_id[:8]}...): {e}")
        if employee_ids_list:
            _progress(f"  Salary assignments: {len(employee_ids_list)}")

    # ==================================================================
    # PHASE 10: CRM Pipeline
    # ==================================================================
    _progress("Phase 10: CRM Pipeline...")

    # Create campaign
    campaign_id = None
    try:
        result = _run_skill("erpclaw-crm", "add-campaign",
                            name="Q1 2026 Product Launch",
                            campaign_type="event",
                            start_date="2026-01-01",
                            end_date="2026-03-31")
        campaign_id = result.get("campaign_id")
        _progress("  Campaign: Q1 2026 Product Launch")
    except Exception as e:
        errors.append(f"Phase 10 (campaign): {e}")

    # Create leads
    lead_defs = [
        # (lead_name, source)
        ("Tony Stark",       "website"),
        ("Bruce Banner",     "referral"),
        ("Natasha Romanov",  "trade_show"),
        ("Steve Rogers",     "other"),
        ("Clint Barton",     "website"),
    ]
    lead_ids = {}  # lead_name -> lead_id
    lead_count = 0
    for lead_name, source in lead_defs:
        try:
            result = _run_skill("erpclaw-crm", "add-lead",
                                lead_name=lead_name,
                                source=source,
                                company_id=company_id)
            lid = result.get("lead", {}).get("id") if isinstance(result.get("lead"), dict) else result.get("lead_id")
            lead_ids[lead_name] = lid
            lead_count += 1
            _progress(f"  Lead: {lead_name}")
        except Exception as e:
            errors.append(f"Phase 10 (lead {lead_name}): {e}")

    # Update lead statuses (all leads start as 'new', update to desired status)
    lead_status_updates = [
        # (lead_name, desired_status)
        ("Bruce Banner",    "contacted"),
        ("Natasha Romanov", "qualified"),
        ("Steve Rogers",    "contacted"),  # will convert later
    ]
    for lead_name, desired_status in lead_status_updates:
        lid = lead_ids.get(lead_name)
        if not lid:
            continue
        try:
            _run_skill("erpclaw-crm", "update-lead",
                       lead_id=lid,
                       status=desired_status)
        except Exception as e:
            errors.append(f"Phase 10 (update lead {lead_name}): {e}")

    summary["campaigns"] = 1 if campaign_id else 0
    summary["leads"] = lead_count

    # Create opportunities
    opp_defs = [
        # (name, lead_name, expected_revenue, probability)
        ("Widget Supply Contract",   "Natasha Romanov", "25000", "60"),
        ("Annual Maintenance Deal",  "Steve Rogers",    "15000", "75"),
    ]
    opp_count = 0
    for opp_name, lead_name, revenue, prob in opp_defs:
        lid = lead_ids.get(lead_name)
        try:
            kwargs = {
                "opportunity_name": opp_name,
                "expected_revenue": revenue,
                "probability": prob,
                "company_id": company_id,
            }
            if lid:
                kwargs["lead_id"] = lid
            result = _run_skill("erpclaw-crm", "add-opportunity", **kwargs)
            opp_id = None
            if isinstance(result.get("opportunity"), dict):
                opp_id = result["opportunity"].get("id")
            else:
                opp_id = result.get("opportunity_id")

            # Update stage after creation (opportunities start as 'new')
            if opp_id:
                desired_stage = "proposal_sent" if opp_name == "Widget Supply Contract" else "negotiation"
                try:
                    _run_skill("erpclaw-crm", "update-opportunity",
                               opportunity_id=opp_id,
                               stage=desired_stage)
                except Exception:
                    pass  # Stage update is best-effort

            opp_count += 1
            _progress(f"  Opportunity: {opp_name}")
        except Exception as e:
            errors.append(f"Phase 10 (opportunity {opp_name}): {e}")

    summary["opportunities"] = opp_count

    # ==================================================================
    # PHASE 11: Assets
    # ==================================================================
    _progress("Phase 11: Assets...")

    asset_cat_ids = {}  # name -> id
    asset_cat_defs = [
        # (name, depreciation_method, useful_life_years)
        ("Office Equipment", "straight_line",       5),
        ("Vehicles",         "written_down_value",   8),
    ]
    for cat_name, dep_method, useful_life in asset_cat_defs:
        try:
            result = _run_skill("erpclaw-assets", "add-asset-category",
                                name=cat_name,
                                company_id=company_id,
                                depreciation_method=dep_method,
                                useful_life_years=useful_life)
            cat_id = result.get("asset_category_id")
            asset_cat_ids[cat_name] = cat_id
            _progress(f"  Asset category: {cat_name}")
        except Exception as e:
            errors.append(f"Phase 11 (asset category {cat_name}): {e}")

    summary["asset_categories"] = len(asset_cat_ids)

    # Create assets
    asset_defs = [
        # (name, category_name, purchase_date, gross_amount)
        ("Dell Latitude Laptop", "Office Equipment", "2026-01-10", "2500.00"),
        ("Ford Transit Van",     "Vehicles",         "2026-01-05", "35000.00"),
        ("Server Rack R740",     "Office Equipment", "2026-01-15", "12000.00"),
    ]
    asset_count = 0
    for asset_name, cat_name, pdate, amount in asset_defs:
        cat_id = asset_cat_ids.get(cat_name)
        if not cat_id:
            errors.append(f"Phase 11 (asset {asset_name}): category '{cat_name}' not found")
            continue
        try:
            result = _run_skill("erpclaw-assets", "add-asset",
                                name=asset_name,
                                asset_category_id=cat_id,
                                company_id=company_id,
                                gross_value=amount,
                                purchase_date=pdate)
            asset_count += 1
            _progress(f"  Asset: {asset_name}")
        except Exception as e:
            errors.append(f"Phase 11 (asset {asset_name}): {e}")

    summary["assets"] = asset_count

    # ==================================================================
    # PHASE 12: Support
    # ==================================================================
    _progress("Phase 12: Support...")

    # Create SLA
    sla_id = None
    try:
        priorities_json = json.dumps({
            "response_times": {"low": "48", "medium": "24", "high": "8", "critical": "4"},
            "resolution_times": {"low": "120", "medium": "72", "high": "24", "critical": "8"},
        })
        result = _run_skill("erpclaw-support", "add-sla",
                            name="Standard SLA",
                            priorities=priorities_json,
                            is_default="1")
        sla_id = result.get("sla_id")
        _progress("  SLA: Standard SLA")
    except Exception as e:
        errors.append(f"Phase 12 (SLA): {e}")

    summary["slas"] = 1 if sla_id else 0

    # Create support issues
    issue_defs = [
        # (subject, customer_name, priority, issue_type)
        ("Widget A delivery delayed",     "Acme Corporation",  "high",   "complaint"),
        ("Invoice discrepancy",           "Wayne Industries",  "medium", "question"),
        ("Product quality concern",       "Oscorp Industries", "high",   "complaint"),
        ("Warranty claim for Widget B",   "Pied Piper Inc",    "low",    "return"),
    ]
    issue_count = 0
    for subject, cust_name, priority, issue_type in issue_defs:
        cust_id = customer_ids.get(cust_name)
        try:
            kwargs = {
                "subject": subject,
                "priority": priority,
                "issue_type": issue_type,
                "company_id": company_id,
            }
            if cust_id:
                kwargs["customer_id"] = cust_id
            if sla_id:
                kwargs["sla_id"] = sla_id
            result = _run_skill("erpclaw-support", "add-issue", **kwargs)
            issue_id_val = None
            if isinstance(result.get("issue"), dict):
                issue_id_val = result["issue"].get("id")
            else:
                issue_id_val = result.get("issue_id")

            # Update status for specific issues
            if issue_id_val:
                if subject == "Product quality concern":
                    try:
                        _run_skill("erpclaw-support", "update-issue",
                                   issue_id=issue_id_val,
                                   status="in_progress")
                    except Exception:
                        pass
                elif subject == "Warranty claim for Widget B":
                    try:
                        _run_skill("erpclaw-support", "resolve-issue",
                                   issue_id=issue_id_val,
                                   resolution_notes="Warranty replacement shipped")
                    except Exception:
                        pass

            issue_count += 1
            _progress(f"  Issue: {subject}")
        except Exception as e:
            errors.append(f"Phase 12 (issue '{subject}'): {e}")

    summary["support_issues"] = issue_count

    # ==================================================================
    # PHASE 13: Projects
    # ==================================================================
    _progress("Phase 13: Projects...")

    project_id = None
    try:
        result = _run_skill("erpclaw-projects", "add-project",
                            name="ERP Migration Project",
                            company_id=company_id,
                            project_type="internal",
                            start_date="2026-01-01",
                            end_date="2026-06-30")
        project_id = result.get("project_id")
        _progress("  Project: ERP Migration Project")
    except Exception as e:
        errors.append(f"Phase 13 (project): {e}")

    summary["projects"] = 1 if project_id else 0

    # Create tasks
    task_defs = [
        # (name, start_date, end_date)
        ("Requirements gathering",  "2026-01-01", "2026-01-31"),
        ("Data migration",          "2026-02-01", "2026-03-31"),
        ("User training",           "2026-04-01", "2026-04-30"),
        ("Go-live preparation",     "2026-05-01", "2026-06-30"),
    ]
    task_count = 0
    if project_id:
        for task_name, start, end in task_defs:
            try:
                _run_skill("erpclaw-projects", "add-task",
                           project_id=project_id,
                           name=task_name,
                           start_date=start,
                           end_date=end)
                task_count += 1
                _progress(f"  Task: {task_name}")
            except Exception as e:
                errors.append(f"Phase 13 (task '{task_name}'): {e}")

    summary["tasks"] = task_count

    # ==================================================================
    # Final output
    # ==================================================================
    _progress("Seed complete!")

    result = {
        "status": "ok" if not errors else "partial",
        "message": f"Demo data seeded successfully for company {company_id}",
        "company_id": company_id,
        "summary": summary,
    }
    if errors:
        result["errors"] = errors
        result["error_count"] = len(errors)

    output_json(result)


# ---------------------------------------------------------------------------
# Action Router
# ---------------------------------------------------------------------------

ACTIONS = {
    "check-installation": check_installation,
    "install-guide": install_guide,
    "seed-demo-data": seed_demo_data,
}


def main():
    parser = argparse.ArgumentParser(
        description="ERPClaw meta-package — installation checker and onboarding guide"
    )
    parser.add_argument(
        "--action",
        required=True,
        choices=sorted(ACTIONS.keys()),
        help="Action to perform",
    )
    parser.add_argument(
        "--db-path",
        default=DEFAULT_DB_PATH,
        help=f"Path to the ERPClaw database (default: {DEFAULT_DB_PATH})",
    )
    parser.add_argument(
        "--company-id",
        help="Use an existing company instead of creating Stark Manufacturing (seed-demo-data)",
    )

    args = parser.parse_args()

    action_fn = ACTIONS.get(args.action)
    if action_fn is None:
        output_error(f"Unknown action: {args.action}")

    try:
        action_fn(args)
    except Exception as exc:
        output_error(f"{args.action} failed: {exc}")


if __name__ == "__main__":
    main()
