#!/usr/bin/env python3
"""ERPClaw OS — Suite Installation

Multi-module orchestrated installation with dependency resolution.
Takes a suite name or comma-separated module list, resolves dependencies,
and installs in correct order.
"""
import json
import os
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from dependency_resolver import (
    detect_circular_deps,
    detect_prefix_collisions,
    load_registry,
    resolve_install_order,
)

# ---------------------------------------------------------------------------
# Predefined Suites
# ---------------------------------------------------------------------------

SUITE_DEFINITIONS = {
    "healthcare-full": {
        "display_name": "Healthcare Full Stack",
        "description": "Complete healthcare suite: core health, dental, veterinary, mental health, home health",
        "modules": ["healthclaw", "healthclaw-dental", "healthclaw-vet",
                     "healthclaw-mental", "healthclaw-homehealth"],
    },
    "healthcare-dental": {
        "display_name": "Dental Practice",
        "description": "Dental practice: core health + dental",
        "modules": ["healthclaw", "healthclaw-dental"],
    },
    "healthcare-vet": {
        "display_name": "Veterinary Practice",
        "description": "Veterinary practice: core health + veterinary",
        "modules": ["healthclaw", "healthclaw-vet"],
    },
    "university": {
        "display_name": "University / Higher Education",
        "description": "Complete university suite: core education, higher ed, financial aid, scheduling, LMS, state reporting",
        "modules": ["educlaw", "educlaw-highered", "educlaw-finaid",
                     "educlaw-scheduling", "educlaw-lms", "educlaw-statereport"],
    },
    "k12": {
        "display_name": "K-12 School District",
        "description": "K-12 education: core education, K-12, scheduling, state reporting",
        "modules": ["educlaw", "educlaw-k12", "educlaw-scheduling",
                     "educlaw-statereport"],
    },
    "enterprise": {
        "display_name": "Enterprise ERP",
        "description": "Full enterprise: CRM, ops (manufacturing, projects, assets, quality, support), compliance, approvals, documents",
        "modules": ["erpclaw-growth", "erpclaw-ops", "erpclaw-compliance",
                     "erpclaw-approvals", "erpclaw-documents",
                     "erpclaw-alerts", "erpclaw-treasury"],
    },
    "retail": {
        "display_name": "Retail Business",
        "description": "Retail with POS and inventory management",
        "modules": ["retailclaw", "erpclaw-pos"],
    },
    "restaurant": {
        "display_name": "Restaurant / Food Service",
        "description": "Restaurant with POS, food management",
        "modules": ["foodclaw", "erpclaw-pos"],
    },
    "property-full": {
        "display_name": "Property Management Full",
        "description": "Residential and commercial property management",
        "modules": ["propertyclaw", "propertyclaw-commercial"],
    },
    "legal": {
        "display_name": "Legal Practice",
        "description": "Legal practice management with documents and e-sign",
        "modules": ["legalclaw", "erpclaw-documents", "erpclaw-esign"],
    },
    "nonprofit": {
        "display_name": "Nonprofit Organization",
        "description": "Nonprofit with compliance and CRM",
        "modules": ["nonprofitclaw", "erpclaw-compliance", "erpclaw-growth"],
    },
}


def list_suites():
    """List all available predefined suites.

    Returns:
        list of suite dicts with name, display_name, description, module_count
    """
    suites = []
    for name, info in sorted(SUITE_DEFINITIONS.items()):
        suites.append({
            "name": name,
            "display_name": info["display_name"],
            "description": info["description"],
            "module_count": len(info["modules"]),
            "modules": info["modules"],
        })
    return suites


def install_suite(suite_name=None, modules=None, registry_path=None, dry_run=False):
    """Orchestrate multi-module installation with dependency resolution.

    Args:
        suite_name: Name of a predefined suite (e.g., "healthcare-full")
        modules: Comma-separated string or list of module names
        registry_path: Path to module_registry.json
        dry_run: If True, only resolve and validate — don't install

    Returns:
        dict with install_order, validation, errors, etc.
    """
    start_time = time.time()

    # 1. Determine module list
    if suite_name:
        if suite_name not in SUITE_DEFINITIONS:
            available = sorted(SUITE_DEFINITIONS.keys())
            return {
                "result": "error",
                "error": f"Suite '{suite_name}' not found",
                "available_suites": available,
            }
        module_list = SUITE_DEFINITIONS[suite_name]["modules"]
    elif modules:
        if isinstance(modules, str):
            module_list = [m.strip() for m in modules.split(",") if m.strip()]
        else:
            module_list = modules
    else:
        return {
            "result": "error",
            "error": "Either --suite or --modules is required",
            "available_suites": sorted(SUITE_DEFINITIONS.keys()),
        }

    if not module_list:
        return {"result": "error", "error": "No modules specified"}

    # 2. Load registry
    registry = load_registry(registry_path)

    # 3. Check for circular dependencies
    cycles = detect_circular_deps(module_list, registry=registry)
    if cycles:
        return {
            "result": "error",
            "error": "Circular dependencies detected",
            "cycles": cycles,
        }

    # 4. Resolve installation order
    resolution = resolve_install_order(module_list, registry=registry)
    if resolution["errors"]:
        return {
            "result": "error",
            "error": "Dependency resolution failed",
            "errors": resolution["errors"],
        }

    # 5. Check for prefix collisions
    collisions = detect_prefix_collisions(resolution["order"], registry=registry)

    # 6. Build installation plan
    install_plan = []
    for mod_name in resolution["order"]:
        mod_info = registry.get(mod_name, {})
        install_plan.append({
            "module": mod_name,
            "display_name": mod_info.get("display_name", mod_name),
            "has_init_db": mod_info.get("has_init_db", False),
            "github": mod_info.get("github", ""),
            "is_dependency": mod_name in set(resolution["added_dependencies"]),
        })

    duration_ms = int((time.time() - start_time) * 1000)

    result = {
        "result": "planned" if dry_run else "ready",
        "suite": suite_name,
        "requested_modules": module_list,
        "install_order": resolution["order"],
        "install_plan": install_plan,
        "total_modules": len(resolution["order"]),
        "added_dependencies": resolution["added_dependencies"],
        "prefix_collisions": collisions,
        "duration_ms": duration_ms,
    }

    if dry_run:
        return result

    # In production, each module would be installed via module_manager.py.
    # For now, return the resolved plan for the caller to execute.
    return result


# ---------------------------------------------------------------------------
# CLI Handler
# ---------------------------------------------------------------------------

def handle_install_suite(args):
    """CLI handler for install-suite action."""
    suite_name = getattr(args, "suite", None)
    modules = getattr(args, "modules", None)
    dry_run = getattr(args, "dry_run", False)

    if not suite_name and not modules:
        # List available suites
        suites = list_suites()
        return {
            "result": "ok",
            "suites": suites,
            "count": len(suites),
            "hint": "Use --suite <name> or --modules mod1,mod2 to install",
        }

    result = install_suite(
        suite_name=suite_name,
        modules=modules,
        dry_run=dry_run,
    )
    return result
