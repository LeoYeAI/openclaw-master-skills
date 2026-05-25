#!/usr/bin/env python3
"""ERPClaw Onboarding — profile-based module auto-installer.

Provides 18 business profiles that auto-install the right set of modules
for each business type. Users select a profile and the system handles
dependency resolution and installation.

Usage: python3 onboarding.py --action <action-name> [--flags ...]
Output: JSON to stdout, exit 0 on success, exit 1 on error.
"""
import argparse
import json
import os
import sys
from uuid import uuid4

# Shared library
sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
from erpclaw_lib.db import get_connection
from erpclaw_lib.response import ok, err

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Country → regional module mapping (used by --country flag on onboard)
COUNTRY_REGION_MAP = {
    "IN": "erpclaw-region-in", "India": "erpclaw-region-in",
    "CA": "erpclaw-region-ca", "Canada": "erpclaw-region-ca",
    "GB": "erpclaw-region-uk", "UK": "erpclaw-region-uk",
    "United Kingdom": "erpclaw-region-uk",
    "DE": "erpclaw-region-eu", "FR": "erpclaw-region-eu",
    "IT": "erpclaw-region-eu", "ES": "erpclaw-region-eu",
    "NL": "erpclaw-region-eu", "BE": "erpclaw-region-eu",
    "AT": "erpclaw-region-eu", "PT": "erpclaw-region-eu",
    "IE": "erpclaw-region-eu", "SE": "erpclaw-region-eu",
    "FI": "erpclaw-region-eu", "DK": "erpclaw-region-eu",
    "PL": "erpclaw-region-eu", "CZ": "erpclaw-region-eu",
    "GR": "erpclaw-region-eu",
    "Germany": "erpclaw-region-eu", "France": "erpclaw-region-eu",
    "Italy": "erpclaw-region-eu", "Spain": "erpclaw-region-eu",
    "Netherlands": "erpclaw-region-eu",
}

# ---------------------------------------------------------------------------
# Business Profiles: profile_name → list of module names to install
# ---------------------------------------------------------------------------
# Core (erpclaw) is always pre-installed. These are ADDITIONAL modules.
# Dependencies are resolved automatically by module_manager.

PROFILES = {
    "small-business": {
        "display_name": "Small Business",
        "description": "General small business: sales, purchasing, basic inventory, CRM",
        "modules": [
            "erpclaw-growth",
        ],
    },
    "retail": {
        "display_name": "Retail Business",
        "description": "Brick-and-mortar or e-commerce retail: POS, pricing, loyalty, merchandising",
        "modules": [
            "retailclaw",
            "erpclaw-growth",
        ],
    },
    "manufacturing": {
        "display_name": "Manufacturing",
        "description": "Production: BOMs, work orders, MRP, quality, advanced manufacturing",
        "modules": [
            "erpclaw-ops",
        ],
    },
    "professional-services": {
        "display_name": "Professional Services",
        "description": "Consulting, agencies: projects, timesheets, billing, CRM",
        "modules": [
            "erpclaw-ops",
            "erpclaw-growth",
        ],
    },
    "distribution": {
        "display_name": "Distribution / Wholesale",
        "description": "Distribution and wholesale: advanced inventory, buying, selling, logistics",
        "modules": [
            "retailclaw",
            "erpclaw-growth",
        ],
    },
    "saas": {
        "display_name": "SaaS / Subscription",
        "description": "Software-as-a-Service: usage billing, subscriptions, CRM, analytics",
        "modules": [
            "erpclaw-growth",
        ],
    },
    "property-management": {
        "display_name": "Property Management",
        "description": "Real estate: properties, leases, tenants, maintenance, accounting",
        "modules": [
            "propertyclaw",
        ],
    },
    "healthcare": {
        "display_name": "Healthcare",
        "description": "Medical practice: patients, appointments, clinical notes, billing, pharmacy",
        "modules": [
            "healthclaw",
        ],
    },
    "dental": {
        "display_name": "Dental Practice",
        "description": "Dental office: patients, treatments, dental charting, billing",
        "modules": [
            "healthclaw",
            "healthclaw-dental",
        ],
    },
    "veterinary": {
        "display_name": "Veterinary Practice",
        "description": "Animal healthcare: patients (pets), appointments, treatments, billing",
        "modules": [
            "healthclaw",
            "healthclaw-vet",
        ],
    },
    "mental-health": {
        "display_name": "Mental Health Practice",
        "description": "Therapy and counseling: sessions, treatment plans, progress notes",
        "modules": [
            "healthclaw",
            "healthclaw-mental",
        ],
    },
    "home-health": {
        "display_name": "Home Health Agency",
        "description": "Home health: visits, care plans, aides, scheduling, compliance",
        "modules": [
            "healthclaw",
            "healthclaw-homehealth",
        ],
    },
    "k12-school": {
        "display_name": "K-12 School",
        "description": "K-12 education: students, grades, attendance, staff, fees, state reporting",
        "modules": [
            "educlaw",
            "educlaw-k12",
            "educlaw-statereport",
        ],
    },
    "college-university": {
        "display_name": "College / University",
        "description": "Higher education: registrar, financial aid, admissions, alumni, faculty",
        "modules": [
            "educlaw",
            "educlaw-highered",
            "educlaw-finaid",
            "educlaw-lms",
        ],
    },
    "nonprofit": {
        "display_name": "Nonprofit / NGO",
        "description": "Nonprofit: donors, grants, fund accounting, programs, volunteer tracking, CRM",
        "modules": [
            "nonprofitclaw",
            "erpclaw-growth",
        ],
    },
    "construction": {
        "display_name": "Construction / Contracting",
        "description": "General contracting, subcontracting: job costing, AIA billing, change orders",
        "modules": [
            "constructclaw",
        ],
    },
    "agriculture": {
        "display_name": "Agriculture / Farming",
        "description": "Crop and livestock farming: field tracking, harvest, equipment, commodity sales",
        "modules": [
            "agricultureclaw",
        ],
    },
    "automotive": {
        "display_name": "Auto Repair / Dealership",
        "description": "Auto repair shops and dealerships: work orders, parts, vehicles, service history",
        "modules": [
            "automotiveclaw",
        ],
    },
    "food-service": {
        "display_name": "Restaurant / Food Service",
        "description": "Restaurants, catering, food production: menus, recipes, food cost, waste tracking",
        "modules": [
            "foodclaw",
        ],
    },
    "hospitality": {
        "display_name": "Hotel / Hospitality",
        "description": "Hotels, venues, resorts: reservations, rooms, housekeeping, events, F&B",
        "modules": [
            "hospitalityclaw",
        ],
    },
    "legal": {
        "display_name": "Law Firm / Legal Practice",
        "description": "Law firms: matters, time billing, trust accounting, IOLTA, client management",
        "modules": [
            "legalclaw",
        ],
    },
    "enterprise": {
        "display_name": "Enterprise",
        "description": "Full enterprise: all modules including advanced accounting, integrations",
        "modules": [
            "erpclaw-growth",
            "erpclaw-ops",
            "erpclaw-integrations",
            "erpclaw-alerts",
        ],
    },
    "full-erp": {
        "display_name": "Full ERP Suite",
        "description": "Everything: all expansion modules, all verticals, all regional packs",
        "modules": [
            "erpclaw-growth",
            "erpclaw-ops",
            "erpclaw-integrations",
            "erpclaw-alerts",
            "retailclaw",
            "propertyclaw",
            "healthclaw",
            "educlaw",
        ],
    },
    "custom": {
        "display_name": "Custom",
        "description": "Choose your own modules — start with core and add what you need",
        "modules": [],
    },
}


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

def list_profiles(conn, args):
    """List all available business profiles."""
    profiles = []
    for key, profile in PROFILES.items():
        profiles.append({
            "profile": key,
            "display_name": profile["display_name"],
            "description": profile["description"],
            "module_count": len(profile["modules"]),
            "modules": profile["modules"],
        })

    ok({
        "profiles": profiles,
        "total": len(profiles),
        "hint": "Use --action onboard --profile <name> to install modules for a profile",
    })


def onboard(conn, args):
    """Install all modules for a business profile.

    Resolves dependencies and installs modules in order. Skips already-installed
    modules. Reports progress for each module.
    """
    profile_name = getattr(args, "profile", None)
    if not profile_name:
        err(
            "Missing --profile flag",
            suggestion="Use --action list-profiles to see available profiles"
        )

    if profile_name not in PROFILES:
        err(
            f"Unknown profile: {profile_name}",
            suggestion=f"Available profiles: {', '.join(sorted(PROFILES.keys()))}"
        )

    profile = PROFILES[profile_name]
    modules_to_install = profile["modules"]

    if not modules_to_install:
        ok({
            "profile": profile_name,
            "display_name": profile["display_name"],
            "installed": [],
            "skipped": [],
            "failed": [],
            "note": "Custom profile selected — use --action install-module --module-name <name> to install individual modules",
        })
        return

    # Check which modules are already installed
    installed_rows = conn.execute(
        "SELECT name FROM erpclaw_module WHERE install_status = 'installed'"
    ).fetchall()
    already_installed = {row["name"] for row in installed_rows}

    installed = []
    skipped = []
    failed = []

    # Import module_manager for install functionality
    sys.path.insert(0, SCRIPT_DIR)
    from module_manager import _load_registry, _install_module_inner

    registry = _load_registry()
    # Handle dict-keyed registry
    modules_raw = registry.get("modules", {})
    if isinstance(modules_raw, dict):
        modules_by_name = {}
        for name, info in modules_raw.items():
            info_copy = dict(info)
            info_copy.setdefault("name", name)
            modules_by_name[name] = info_copy
    else:
        modules_by_name = {m["name"]: m for m in modules_raw}

    for module_name in modules_to_install:
        if module_name in already_installed:
            skipped.append({"module": module_name, "reason": "already installed"})
            continue

        if module_name not in modules_by_name:
            failed.append({"module": module_name, "error": "not found in registry"})
            continue

        try:
            install_args = argparse.Namespace(module_name=module_name)
            result = _install_module_inner(install_args, conn, modules_by_name, depth=0)
            installed.append(result)
            already_installed.add(module_name)
        except SystemExit:
            # ok()/err() in sub-calls trigger sys.exit — reconnect
            conn = get_connection()
            # Check if it actually succeeded
            check = conn.execute(
                "SELECT install_status FROM erpclaw_module WHERE name = ?",
                (module_name,)
            ).fetchone()
            if check and check["install_status"] == "installed":
                installed.append({"module": module_name, "note": "installed"})
                already_installed.add(module_name)
            else:
                failed.append({"module": module_name, "error": "installation interrupted"})
        except Exception as e:
            failed.append({"module": module_name, "error": str(e)})

    # Auto-install regional module if --country is provided
    country = getattr(args, "country", None)
    region_module = COUNTRY_REGION_MAP.get(country) if country else None
    if region_module:
        if region_module in already_installed:
            skipped.append({"module": region_module, "reason": "already installed"})
        elif region_module not in modules_by_name:
            failed.append({"module": region_module, "error": "not found in registry"})
        else:
            try:
                install_args = argparse.Namespace(module_name=region_module)
                result = _install_module_inner(install_args, conn, modules_by_name, depth=0)
                installed.append(result)
                already_installed.add(region_module)
            except SystemExit:
                conn = get_connection()
                check = conn.execute(
                    "SELECT install_status FROM erpclaw_module WHERE name = ?",
                    (region_module,)
                ).fetchone()
                if check and check["install_status"] == "installed":
                    installed.append({"module": region_module, "note": "installed (regional)"})
                    already_installed.add(region_module)
                else:
                    failed.append({"module": region_module, "error": "installation interrupted"})
            except Exception as e:
                failed.append({"module": region_module, "error": str(e)})

    ok({
        "profile": profile_name,
        "display_name": profile["display_name"],
        "installed": installed,
        "skipped": skipped,
        "failed": failed,
        "region_module": region_module,
        "summary": f"{len(installed)} installed, {len(skipped)} skipped, {len(failed)} failed",
    })


ACTIONS = {
    "list-profiles": list_profiles,
    "onboard": onboard,
}


def main():
    parser = argparse.ArgumentParser(description="ERPClaw Onboarding")
    parser.add_argument("--action", required=True, choices=sorted(ACTIONS.keys()))
    parser.add_argument("--profile", help="Business profile name")
    parser.add_argument("--country", default=None,
                        help="Country code (e.g. IN, CA, GB, DE) — auto-installs regional module")
    parser.add_argument("--db-path", default=None)

    args = parser.parse_args()

    conn = get_connection()

    try:
        handler = ACTIONS[args.action]
        handler(conn, args)
    except SystemExit:
        raise
    except Exception as e:
        err(f"Unexpected error in {args.action}: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
