#!/usr/bin/env python3
"""ERPClaw OS — db_query.py

Action router for the ERPClaw OS domain. Handles module validation
against the ERPClaw Constitution (18 articles), module generation,
and industry-specific configuration.

Usage: python3 db_query.py --action <action-name> [--flags ...]
Output: JSON to stdout, exit 0 on success, exit 1 on error.
"""
import json
import os
import sys
import time
import uuid

# Add shared lib to path
try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
    from erpclaw_lib.response import ok, err
    from erpclaw_lib.args import SafeArgumentParser, check_unknown_args
except ImportError:
    # Fallback: define minimal ok/err if shared lib not installed
    def ok(data):
        data["status"] = "ok"
        print(json.dumps(data, indent=2, default=str))
        sys.exit(0)

    def err(message, suggestion=None):
        data = {"status": "error", "message": message}
        if suggestion:
            data["suggestion"] = suggestion
        print(json.dumps(data, indent=2))
        sys.exit(1)

    from argparse import ArgumentParser as SafeArgumentParser

    def check_unknown_args(parser, unknown):
        if unknown:
            print(json.dumps({"status": "error", "message": f"Unknown flags: {', '.join(unknown)}"}))
            sys.exit(1)

# Import validator (same package)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from validate_module import validate_module_static, validate_module_runtime, build_table_ownership_registry
from constitution import ARTICLES, get_static_articles, get_runtime_articles
from generate_module import generate_module
from configure_module import configure_module
from industry_configs import list_industries
from tier_classifier import handle_classify_operation
from schema_migrator import (
    handle_schema_plan, handle_schema_apply,
    handle_schema_rollback, handle_schema_drift,
)
from deploy_pipeline import handle_deploy_module
from deploy_audit import handle_deploy_audit_log
from install_suite import handle_install_suite
from adversarial_audit import handle_run_audit
from compliance_weather import handle_compliance_weather_status
from improvement_log import (
    handle_log_improvement,
    handle_list_improvements,
    handle_review_improvement,
)
from semantic_engine import handle_semantic_check, handle_semantic_rules_list
from dgm_engine import (
    handle_dgm_run_variant,
    handle_dgm_list_variants,
    handle_dgm_select_best,
)
from gap_detector import (
    handle_detect_gaps,
    handle_suggest_modules,
    handle_detect_schema_divergence,
    handle_detect_stubs,
)
from heartbeat_analysis import (
    handle_heartbeat_analyze,
    handle_heartbeat_report,
    handle_heartbeat_suggest,
)
from in_module_generator import handle_add_feature_to_module
from research_engine import handle_research_rule, handle_get_implementation_guide
from feature_matrix import handle_check_feature_completeness, handle_list_feature_matrix


# ---------------------------------------------------------------------------
# Action: validate-module
# ---------------------------------------------------------------------------

def handle_validate_module(args):
    """Validate a module against the ERPClaw Constitution."""
    module_path = args.module_path
    validation_type = args.validation_type
    db_path = getattr(args, "db_path", None)

    if not os.path.isdir(module_path):
        err(f"Module path does not exist or is not a directory: {module_path}")

    start_time = time.time()

    result = {}

    if validation_type in ("static", "full"):
        static_result = validate_module_static(module_path)
        result.update(static_result)

    if validation_type in ("runtime", "full"):
        runtime_result = validate_module_runtime(module_path, db_path)
        if validation_type == "full":
            # Merge runtime into existing result
            result["runtime"] = runtime_result
            if runtime_result["result"] == "fail":
                result["result"] = "fail"
                result["articles"][9] = "fail"
            else:
                result["articles"][9] = "pass"
        else:
            result = runtime_result

    duration_ms = int((time.time() - start_time) * 1000)
    result["duration_ms"] = duration_ms
    result["validation_type"] = validation_type

    ok(result)


# ---------------------------------------------------------------------------
# Action: list-articles
# ---------------------------------------------------------------------------

def handle_list_articles(args):
    """List all Constitution articles."""
    article_type = getattr(args, "article_type", "all")

    if article_type == "static":
        articles = get_static_articles()
    elif article_type == "runtime":
        articles = get_runtime_articles()
    else:
        articles = ARTICLES

    ok({
        "articles": articles,
        "count": len(articles),
    })


# ---------------------------------------------------------------------------
# Action: build-table-registry
# ---------------------------------------------------------------------------

def handle_build_table_registry(args):
    """Build and display the table ownership registry."""
    src_root = args.src_root

    if not os.path.isdir(src_root):
        err(f"Source root does not exist or is not a directory: {src_root}")

    registry = build_table_ownership_registry(src_root)

    # Group by module for readability
    by_module = {}
    for table, module in sorted(registry.items()):
        by_module.setdefault(module, []).append(table)

    ok({
        "total_tables": len(registry),
        "total_modules": len(by_module),
        "registry": registry,
        "by_module": by_module,
    })


# ---------------------------------------------------------------------------
# Action: generate-module
# ---------------------------------------------------------------------------

def handle_generate_module(args):
    """Generate a new ERPClaw module from structured input."""
    module_name = args.module_name
    prefix = args.prefix
    business_description = args.business_description

    if not module_name:
        err("--module-name is required")
    if not prefix:
        err("--prefix is required")
    if not business_description:
        err("--business-description is required")

    # Parse entities JSON
    entities_raw = getattr(args, "entities", None)
    if not entities_raw:
        err("--entities is required (JSON string)")

    try:
        entities = json.loads(entities_raw)
    except (json.JSONDecodeError, TypeError):
        err("--entities must be valid JSON")

    if not isinstance(entities, list):
        err("--entities must be a JSON array")

    output_dir = getattr(args, "output_dir", None)
    src_root = getattr(args, "src_root", None)

    start_time = time.time()
    result = generate_module(
        module_name=module_name,
        prefix=prefix,
        business_description=business_description,
        entities=entities,
        output_dir=output_dir,
        src_root=src_root,
    )
    duration_ms = int((time.time() - start_time) * 1000)
    result["duration_ms"] = duration_ms

    ok(result)


# ---------------------------------------------------------------------------
# Action: configure-module
# ---------------------------------------------------------------------------

def handle_configure_module(args):
    """Configure installed modules for a specific industry."""
    industry = getattr(args, "industry", None)
    company_id = getattr(args, "company_id", None)
    size_tier = getattr(args, "size_tier", "small")
    db_path = getattr(args, "db_path", None)

    if not industry:
        err("--industry is required", suggestion="Use --action list-industries to see available industries")
    if not company_id:
        err("--company-id is required")

    start_time = time.time()
    result = configure_module(
        industry=industry,
        company_id=company_id,
        size_tier=size_tier,
        db_path=db_path,
    )
    duration_ms = int((time.time() - start_time) * 1000)
    result["duration_ms"] = duration_ms

    if result["result"] == "fail":
        err(result.get("error", "Configuration failed"),
            suggestion=result.get("available_industries"))
    else:
        ok(result)


# ---------------------------------------------------------------------------
# Action: list-industries
# ---------------------------------------------------------------------------

def handle_list_industries(args):
    """List all available industry configurations."""
    industries = list_industries()
    ok({
        "industries": industries,
        "count": len(industries),
        "hint": "Use --action configure-module --industry <name> --company-id <id> to apply",
    })


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

def main():
    parser = SafeArgumentParser(description="ERPClaw OS — Module Validator, Generator & Configurator")
    parser.add_argument("--action", required=True, choices=[
        "validate-module",
        "list-articles",
        "build-table-registry",
        "generate-module",
        "configure-module",
        "list-industries",
        "classify-operation",
        "schema-plan",
        "schema-apply",
        "schema-rollback",
        "schema-drift",
        "deploy-module",
        "deploy-audit-log",
        "install-suite",
        "run-audit",
        "compliance-weather-status",
        "log-improvement",
        "list-improvements",
        "review-improvement",
        "semantic-check",
        "semantic-rules-list",
        "dgm-run-variant",
        "dgm-list-variants",
        "dgm-select-best",
        "detect-gaps",
        "detect-schema-divergence",
        "detect-stubs",
        "suggest-modules",
        "heartbeat-analyze",
        "heartbeat-report",
        "heartbeat-suggest",
        "add-feature-to-module",
        "check-feature-completeness",
        "list-feature-matrix",
        "research-business-rule",
        "get-implementation-guide",
    ])
    parser.add_argument("--module-path", help="Path to the module directory to validate")
    parser.add_argument("--validation-type", default="static",
                        choices=["static", "runtime", "full"],
                        help="Type of validation to perform (default: static)")
    parser.add_argument("--db-path", help="Path to test database (for runtime validation)")
    parser.add_argument("--src-root", help="Path to the src/ directory (for table registry)")
    parser.add_argument("--article-type", default="all",
                        choices=["all", "static", "runtime"],
                        help="Filter articles by enforcement type")
    # generate-module flags
    parser.add_argument("--module-name", help="Name of the module to generate")
    parser.add_argument("--prefix", help="Table/action prefix for the module")
    parser.add_argument("--business-description", help="Natural language business description")
    parser.add_argument("--entities", help="JSON string of entity definitions")
    parser.add_argument("--output-dir", help="Output directory for generated module")
    # configure-module flags
    parser.add_argument("--industry", help="Industry type for configuration (e.g., dental_practice)")
    parser.add_argument("--company-id", help="Company UUID to configure")
    parser.add_argument("--size-tier", default="small",
                        choices=["small", "medium", "large", "enterprise"],
                        help="Business size tier (default: small)")
    # classify-operation flags
    parser.add_argument("--action-name", help="Action name to classify (e.g., add-customer)")
    parser.add_argument("--classify-all", action="store_true",
                        help="Classify all actions in ACTION_MAP")
    parser.add_argument("--override-tier", type=int, choices=[0, 1, 2, 3],
                        help="Override tier for an action (requires --action-name)")
    parser.add_argument("--override-by", help="Who is setting the override")
    parser.add_argument("--override-reason", help="Why the override is being set")
    # schema-migration flags
    parser.add_argument("--migration-id", help="Migration UUID (for schema-apply/schema-rollback)")
    # deploy flags
    parser.add_argument("--skip-sandbox", action="store_true",
                        help="Skip sandbox testing (for pre-tested modules)")
    parser.add_argument("--limit", type=int, default=50,
                        help="Limit for audit log queries (default: 50)")
    # install-suite flags
    parser.add_argument("--suite", help="Predefined suite name (e.g., healthcare-full)")
    parser.add_argument("--modules", help="Comma-separated module list")
    # improvement-log flags
    parser.add_argument("--category",
                        choices=["performance", "usability", "coverage", "semantic", "structural"],
                        help="Improvement category")
    parser.add_argument("--description", help="Description of the proposed improvement")
    parser.add_argument("--source",
                        choices=["heartbeat", "dgm", "semantic", "manual", "gap_detector"],
                        help="Source system that detected the improvement")
    parser.add_argument("--evidence", help="JSON evidence supporting the improvement")
    parser.add_argument("--expected-impact", dest="expected_impact",
                        help="JSON expected impact of the improvement")
    parser.add_argument("--proposed-diff", dest="proposed_diff",
                        help="JSON proposed code/config diff")
    parser.add_argument("--improvement-id", dest="improvement_id",
                        help="Improvement UUID (for review-improvement)")
    parser.add_argument("--status", dest="new_status",
                        choices=["approved", "rejected", "deferred"],
                        help="Review status (for review-improvement)")
    parser.add_argument("--status-filter", dest="status_filter",
                        choices=["proposed", "approved", "rejected", "deferred", "deployed"],
                        help="Filter by status (for list-improvements)")
    parser.add_argument("--review-notes", dest="review_notes",
                        help="Notes from the reviewer")
    parser.add_argument("--reviewed-by", dest="reviewed_by",
                        help="Who reviewed the improvement (default: system)")
    parser.add_argument("--from-date", dest="from_date",
                        help="Filter improvements proposed on or after this date (ISO 8601)")
    parser.add_argument("--to-date", dest="to_date",
                        help="Filter improvements proposed on or before this date (ISO 8601)")
    parser.add_argument("--offset", type=int, default=0,
                        help="Offset for pagination (default: 0)")
    parser.add_argument("--deploy", action="store_true",
                        help="Create deploy_audit entry when approving")
    # DGM variant engine flags
    parser.add_argument("--variant-count", dest="variant_count", type=int, default=3,
                        help="Number of variants to generate (default: 3)")
    parser.add_argument("--run-id", dest="run_id",
                        help="DGM run UUID (for dgm-list-variants, dgm-select-best)")
    # gap-detector flags
    parser.add_argument("--registry-path", dest="registry_path",
                        help="Path to module_registry.json (for detect-gaps, suggest-modules)")
    # add-feature-to-module flags
    parser.add_argument("--feature-spec-json", dest="feature_spec_json",
                        help="JSON string with feature specification (for add-feature-to-module)")
    # feature-matrix flags
    parser.add_argument("--domain",
                        help="Domain name for feature matrix or research engine (e.g., selling, buying, inventory)")
    # research-engine flags
    parser.add_argument("--topic",
                        help="Business rule topic to research (for research-business-rule)")
    parser.add_argument("--feature-name", dest="feature_name",
                        help="Feature name for implementation guide (for get-implementation-guide)")

    args, unknown = parser.parse_known_args()
    check_unknown_args(parser, unknown)

    action = args.action

    if action == "validate-module":
        if not args.module_path:
            err("--module-path is required for validate-module")
        handle_validate_module(args)

    elif action == "list-articles":
        handle_list_articles(args)

    elif action == "build-table-registry":
        if not args.src_root:
            err("--src-root is required for build-table-registry")
        handle_build_table_registry(args)

    elif action == "generate-module":
        handle_generate_module(args)

    elif action == "configure-module":
        handle_configure_module(args)

    elif action == "list-industries":
        handle_list_industries(args)

    elif action == "classify-operation":
        handle_classify_operation(args)

    elif action == "schema-plan":
        result = handle_schema_plan(args)
        if "error" in result:
            err(result["error"])
        else:
            ok(result)

    elif action == "schema-apply":
        result = handle_schema_apply(args)
        if "error" in result:
            err(result["error"])
        else:
            ok(result)

    elif action == "schema-rollback":
        result = handle_schema_rollback(args)
        if "error" in result:
            err(result["error"])
        else:
            ok(result)

    elif action == "schema-drift":
        result = handle_schema_drift(args)
        if "error" in result:
            err(result["error"])
        else:
            ok(result)

    elif action == "deploy-module":
        result = handle_deploy_module(args)
        if "error" in result:
            err(result["error"])
        else:
            ok(result)

    elif action == "deploy-audit-log":
        result = handle_deploy_audit_log(args)
        if "error" in result:
            err(result["error"])
        else:
            ok(result)

    elif action == "install-suite":
        result = handle_install_suite(args)
        if "error" in result and result.get("result") == "error":
            err(result["error"])
        else:
            ok(result)

    elif action == "run-audit":
        result = handle_run_audit(args)
        if "error" in result:
            err(result["error"])
        else:
            ok(result)

    elif action == "compliance-weather-status":
        result = handle_compliance_weather_status(args)
        if "error" in result:
            err(result["error"])
        else:
            ok(result)

    elif action == "log-improvement":
        result = handle_log_improvement(args)
        if "error" in result:
            err(result["error"])
        else:
            ok(result)

    elif action == "list-improvements":
        result = handle_list_improvements(args)
        if "error" in result:
            err(result["error"])
        else:
            ok(result)

    elif action == "review-improvement":
        result = handle_review_improvement(args)
        if "error" in result:
            err(result["error"])
        else:
            ok(result)

    elif action == "semantic-check":
        result = handle_semantic_check(args)
        if "error" in result:
            err(result["error"])
        else:
            ok(result)

    elif action == "semantic-rules-list":
        result = handle_semantic_rules_list(args)
        if "error" in result:
            err(result["error"])
        else:
            ok(result)

    elif action == "dgm-run-variant":
        result = handle_dgm_run_variant(args)
        if "error" in result:
            err(result["error"])
        else:
            ok(result)

    elif action == "dgm-list-variants":
        result = handle_dgm_list_variants(args)
        if "error" in result:
            err(result["error"])
        else:
            ok(result)

    elif action == "dgm-select-best":
        result = handle_dgm_select_best(args)
        if "error" in result:
            err(result["error"])
        else:
            ok(result)

    elif action == "detect-gaps":
        result = handle_detect_gaps(args)
        if "error" in result:
            err(result["error"])
        else:
            ok(result)

    elif action == "detect-schema-divergence":
        result = handle_detect_schema_divergence(args)
        if "error" in result:
            err(result["error"])
        else:
            ok(result)

    elif action == "detect-stubs":
        result = handle_detect_stubs(args)
        if "error" in result:
            err(result["error"])
        else:
            ok(result)

    elif action == "suggest-modules":
        result = handle_suggest_modules(args)
        if "error" in result:
            err(result["error"])
        else:
            ok(result)

    elif action == "heartbeat-analyze":
        result = handle_heartbeat_analyze(args)
        if "error" in result:
            err(result["error"])
        else:
            ok(result)

    elif action == "heartbeat-report":
        result = handle_heartbeat_report(args)
        if "error" in result:
            err(result["error"])
        else:
            ok(result)

    elif action == "heartbeat-suggest":
        result = handle_heartbeat_suggest(args)
        if "error" in result:
            err(result["error"])
        else:
            ok(result)

    elif action == "add-feature-to-module":
        if not args.module_path:
            err("--module-path is required for add-feature-to-module")
        if not args.action_name:
            err("--action-name is required for add-feature-to-module")
        result = handle_add_feature_to_module(args)
        if "error" in result:
            err(result["error"])
        else:
            ok(result)

    elif action == "check-feature-completeness":
        if not args.src_root:
            err("--src-root is required for check-feature-completeness")
        result = handle_check_feature_completeness(args)
        if "error" in result:
            err(result["error"])
        else:
            ok(result)

    elif action == "list-feature-matrix":
        result = handle_list_feature_matrix(args)
        if "error" in result:
            err(result["error"])
        else:
            ok(result)

    elif action == "research-business-rule":
        if not args.topic:
            err("--topic is required for research-business-rule")
        result = handle_research_rule(args)
        if "error" in result:
            err(result["error"])
        else:
            ok(result)

    elif action == "get-implementation-guide":
        if not args.feature_name:
            err("--feature-name is required for get-implementation-guide")
        result = handle_get_implementation_guide(args)
        if "error" in result:
            err(result["error"])
        else:
            ok(result)


if __name__ == "__main__":
    main()
