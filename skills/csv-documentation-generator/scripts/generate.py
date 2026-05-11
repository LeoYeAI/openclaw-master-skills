#!/usr/bin/env python3
"""CSV Documentation Generator - Main Entry Point

Generate Computerized System Validation (CSV) documentation
for pharmaceutical and medical device industries.

Usage:
    python3 generate.py vp --project "Project" --system "System v1.0" --category 4 --output ./output/
    python3 generate.py urs --project "Project" --system "System" --category 4 --bilingual true
    python3 generate.py all --project "Project" --system "System" --category 4 --output ./validation/
"""

import argparse
import sys
import os
import subprocess
import venv
import json
import shutil
import hashlib
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config, get_gamp_category_description
from template_loader import TemplateLoader, process_markdown_table_bilingual
from word_generator import WordGenerator
from excel_generator import ExcelGenerator
from requirements.parser import STANDARD_MODULES, RequirementsParser
from requirements.versioning import (
    TEMPLATE_VERSION,
    check_template_compatibility,
    get_template_version,
    set_template_version,
    migrate_template_if_needed,
)
from compliance_checker import ComplianceChecker


def get_skill_root():
    """Get the skill root directory"""
    return Path(__file__).parent.parent


def is_in_venv():
    """Check if running in a virtual environment"""
    return hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )


def ensure_venv():
    """Ensure virtual environment exists and is activated"""
    skill_root = get_skill_root()
    venv_path = skill_root / ".venv"
    venv_python = venv_path / "bin" / "python"

    # Check if venv already exists
    if venv_path.exists() and venv_python.exists():
        return str(venv_path)

    print("\n" + "=" * 60)
    print("Setting up virtual environment...")
    print("=" * 60)

    # Create venv
    venv.create(skill_root / ".venv", with_pip=True)

    # Install dependencies
    print("\nInstalling dependencies...")
    pip_path = venv_path / "bin" / "pip"

    try:
        subprocess.run(
            [str(pip_path), "install", "-r", "requirements.txt"],
            cwd=skill_root,
            check=True,
        )
        print("Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Warning: Failed to install dependencies: {e}")
        print("You may need to install them manually:")
        print(f"  cd {skill_root}")
        print(f"  source {venv_path}/bin/activate")
        print(f"  pip install -r requirements.txt")

    return str(venv_path)


def get_python_executable():
    """Get the appropriate Python executable"""
    skill_root = get_skill_root()
    venv_python = skill_root / ".venv" / "bin" / "python"

    if venv_python.exists():
        return str(venv_python)

    # Fallback to system python
    return sys.executable


def prompt_gamp_category() -> int:
    """Prompt user to select GAMP category with bilingual guidance"""

    print("\n" + "=" * 60)
    print("GAMP 5 (Second Edition) Category Selection / GAMP 5 分类选择")
    print("=" * 60)

    categories = {
        1: {
            "name": "Infrastructure Software",
            "name_cn": "基础设施软件",
            "examples": "Operating systems, databases, middleware",
            "examples_cn": "操作系统、数据库、中间件",
            "approach": "Limited verification",
            "approach_cn": "有限验证",
        },
        2: {
            "name": "Firmware",
            "name_cn": "固件",
            "examples": "Firmware in industrial controllers",
            "examples_cn": "工业控制器中的固件",
            "approach": "Simplified approach",
            "approach_cn": "简化方法",
        },
        3: {
            "name": "Commercial Off-The-Shelf (COTS) - Non-configured",
            "name_cn": "商用现货软件 (不可配置)",
            "examples": "Standard software used as-is, no configuration",
            "examples_cn": "直接使用的标准软件，无配置",
            "approach": "Risk-based verification",
            "approach_cn": "基于风险的验证",
        },
        4: {
            "name": "Configured COTS",
            "name_cn": "配置型 COTS 软件",
            "examples": "EDC, CTMS, LIMS, MES configured for specific use",
            "examples_cn": "为特定用途配置的 EDC、CTMS、LIMS、MES",
            "approach": "Risk-based verification with focus on configuration",
            "approach_cn": "重点关注配置的基于风险验证",
        },
        5: {
            "name": "Custom / Critical Application",
            "name_cn": "定制/关键应用",
            "examples": "Custom-built systems, critical systems with patient impact",
            "examples_cn": "定制开发系统、影响患者的关键系统",
            "approach": "Full lifecycle validation",
            "approach_cn": "完整生命周期验证",
        },
    }

    print("\nPlease select the GAMP category for your system:")
    print("请为您的系统选择 GAMP 分类:\n")

    for cat_id, info in categories.items():
        print(f"  [{cat_id}] {info['name']} / {info['name_cn']}")
        print(f"       Examples / 示例: {info['examples']} / {info['examples_cn']}")
        print(f"       Approach / 方法: {info['approach']} / {info['approach_cn']}")
        print()

    while True:
        try:
            choice = input("Enter category number (1-5) / 输入分类编号 (1-5): ").strip()
            if choice in ["1", "2", "3", "4", "5"]:
                return int(choice)
            else:
                print(
                    "Invalid input. Please enter 1, 2, 3, 4, or 5 / 无效输入，请输入 1, 2, 3, 4 或 5"
                )
        except (KeyboardInterrupt, EOFError):
            print("\nUsing default category 4 / 使用默认分类 4")
            return 4


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="CSV Documentation Generator - Generate validation documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 generate.py vp --project "临床系统" --system "EDC v1.0" --category 4 --output ./output/
  python3 generate.py urs --system "CTMS" --bilingual true --output ./doc/
  python3 generate.py all --project "XX系统" --system "MES" --category 4 --output ./validation/
        """,
    )

    parser.add_argument(
        "doc_type",
        choices=[
            "vp",
            "urs",
            "fs",
            "ts",
            "ra",
            "iq",
            "oq",
            "pq",
            "rtm",
            "vsr",
            "checklist",
            "test-case",
            "all",
            "check",
        ],
        help="Document type to generate (or 'check' for compliance check)",
    )

    parser.add_argument(
        "--project", "-p", default="[Project Name]", help="Project name"
    )

    parser.add_argument(
        "--system", "-s", default="[System Name v1.0]", help="System name and version"
    )

    parser.add_argument(
        "--category",
        "-c",
        type=int,
        default=None,
        choices=[1, 2, 3, 4, 5],
        help="GAMP category (1-5). If not specified, interactive selection will be prompted.",
    )

    parser.add_argument(
        "--bilingual",
        "-b",
        type=lambda x: x.lower() == "true",
        default=True,
        help="Enable bilingual mode: 'true' or 'false' (default: True). When true, headers remain bilingual and content follows --language.",
    )

    parser.add_argument(
        "--language",
        "-l",
        choices=["zh", "en"],
        default="zh",
        help="Primary language for content: 'zh' (Chinese) or 'en' (English). Used when bilingual=false or for content in bilingual mode. (default: zh)",
    )

    parser.add_argument("--output", "-o", default="./output", help="Output directory")

    parser.add_argument(
        "--format",
        "-f",
        choices=["docx", "xlsx", "both"],
        default="both",
        help="Output format",
    )

    parser.add_argument("--doc-id", default="[DOC-XXX]", help="Document ID")

    parser.add_argument("--version", default="1.0", help="Document version")

    parser.add_argument("--author", default="[Author]", help="Document author")

    parser.add_argument("--reviewer", default="[Reviewer]", help="Document reviewer")

    parser.add_argument("--approver", default="[Approver]", help="Document approver")

    parser.add_argument(
        "--critical-functions",
        default="数据录入,审计追踪,权限控制",
        help="Critical functions (comma-separated)",
    )

    parser.add_argument(
        "--sync",
        action="store_true",
        help="Sync requirements from requirements.json to template before generating",
    )

    parser.add_argument(
        "--sync-direction",
        dest="sync_direction",
        choices=["to-json", "to-template", "both"],
        default="both",
        help="Sync direction for bidirectional sync (default: both)",
    )

    parser.add_argument(
        "--conflict-resolution",
        dest="conflict_resolution",
        choices=["newer", "template", "json", "ask"],
        default="newer",
        help="How to resolve conflicts (default: newer)",
    )

    parser.add_argument(
        "--sync-template-to-db",
        action="store_true",
        help="Sync template requirements to requirements.json (e.g., extract URS from urs.md template)",
    )

    parser.add_argument(
        "--db",
        dest="db_path",
        default=None,
        help="Path to requirements.json database file",
    )

    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Interactive step-by-step mode with confirmation prompts",
    )

    parser.add_argument(
        "--auto",
        action="store_true",
        default=True,
        help="Auto mode (default) - generate without confirmation",
    )

    parser.add_argument(
        "--diff-only",
        action="store_true",
        help="Skip regeneration if requirements unchanged (smart rebuild)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed progress information during generation",
    )

    parser.add_argument(
        "--project-root",
        dest="project_root",
        default=None,
        help="Project root for monorepo (auto-detected if not specified)",
    )

    parser.add_argument(
        "--template-version",
        dest="template_version",
        default=None,
        help=f"Set template version (default: {TEMPLATE_VERSION})",
    )

    parser.add_argument(
        "--requirements",
        "-r",
        dest="requirements",
        default="requirements.json",
        help="Path to requirements.json (for check command)",
    )

    parser.add_argument(
        "--test-results",
        "-t",
        dest="test_results",
        default="test_results.json",
        help="Path to test_results.json (for check command)",
    )

    parser.add_argument(
        "--output-format",
        dest="output_format",
        choices=["text", "json"],
        default="text",
        help="Output format for check command",
    )

    return parser.parse_args()


def generate_traceability_table_markdown(db: Dict[str, Any]) -> str:
    """Generate markdown table for VSR traceability section from database

    Returns markdown table string with headers: | 需求ID | 需求描述 | 验证方法 | 验证状态 | 测试用例ID |
    """
    requirements = db.get("requirements", [])
    test_results = db.get("test_results", [])

    if not requirements:
        return "| 需求ID | 需求描述 | 验证方法 | 验证状态 | 测试用例ID |\n|----|---------|---------|---------|-----------|\n| (无需求) | | | | |"

    # Create test results lookup
    test_results_by_req: Dict[str, List[Dict]] = {}
    for tr in test_results:
        req_id = tr.get("requirement_id")
        if req_id:
            if req_id not in test_results_by_req:
                test_results_by_req[req_id] = []
            test_results_by_req[req_id].append(tr)

    lines = [
        "| 需求ID | 需求描述 | 验证方法 | 验证状态 | 测试用例ID |",
        "|------|---------|---------|---------|-----------|",
    ]

    for req in requirements:
        req_id = req.get("id", "")
        desc = (
            req.get("description", "")[:50] + "..."
            if len(req.get("description", "")) > 50
            else req.get("description", "")
        )
        priority = req.get("priority", "")

        # Determine verification method
        verification = (
            "测试 / Test" if priority in ["必须", "应该"] else "审查 / Review"
        )

        # Get status and test cases
        req_results = test_results_by_req.get(req_id, [])
        if req_results:
            statuses = set(tr.get("status", "pending") for tr in req_results)
            status = (
                "通过 / Pass"
                if "pass" in statuses
                else "失败 / Fail"
                if "fail" in statuses
                else "待测 / Pending"
            )
            test_case_ids = ", ".join(tr.get("test_id", "") for tr in req_results[:3])
        else:
            status = "待测 / Pending"
            test_case_ids = (
                req.get("test_cases", [{}])[0].get("id", "")
                if req.get("test_cases")
                else ""
            )

        lines.append(
            f"| {req_id} | {desc} | {verification} | [{status}] | {test_case_ids} |"
        )

    return "\n".join(lines)


def generate_coverage_summary_markdown(db: Dict[str, Any]) -> str:
    """Generate markdown for requirements coverage summary"""
    requirements = db.get("requirements", [])
    test_results = db.get("test_results", [])

    total = len(requirements)
    verified = 0
    failed = 0
    pending = 0

    test_results_by_req = {tr.get("requirement_id"): tr for tr in test_results}

    for req in requirements:
        req_id = req.get("id")
        tr = test_results_by_req.get(req_id)
        if tr:
            if tr.get("status") == "pass":
                verified += 1
            elif tr.get("status") == "fail":
                failed += 1
        else:
            pending += 1

    coverage = f"{(verified / total * 100):.1f}%" if total > 0 else "0%"

    lines = [
        "| 需求来源 | 总需求数 | 已验证 | 覆盖率 |",
        "|----------|---------|--------|-------|",
        f"| URS | {total} | {verified} | {coverage} |",
        f"| FS | - | - | 100% |",
        f"| RA | - | - | 100% |",
    ]

    return "\n".join(lines)


def _compute_requirements_hash(db: Dict[str, Any]) -> str:
    """Compute hash of requirements for change detection"""
    reqs = json.dumps(db.get("requirements", []), sort_keys=True)
    return hashlib.sha256(reqs.encode()).hexdigest()[:16]


def _check_requirements_changed(db: Dict[str, Any], output_dir: Path) -> bool:
    """Check if requirements have changed since last generation

    Returns:
        True if requirements changed or no previous hash exists
    """
    hash_file = output_dir / ".requirements.hash"

    if not hash_file.exists():
        return True

    try:
        with open(hash_file, "r") as f:
            old_hash = f.read().strip()
    except Exception:
        return True

    new_hash = _compute_requirements_hash(db)
    return new_hash != old_hash


def _save_requirements_hash(db: Dict[str, Any], output_dir: Path) -> None:
    """Save requirements hash for incremental update tracking"""
    hash_file = output_dir / ".requirements.hash"
    hash_value = _compute_requirements_hash(db)
    try:
        with open(hash_file, "w") as f:
            f.write(hash_value)
    except Exception:
        pass


def generate_document(
    doc_type: str,
    config: Config,
    db: Optional[Dict[str, Any]] = None,
    diff_only: bool = False,
    verbose: bool = False,
):
    """Generate a single document"""

    verbose_print = print if verbose else lambda *args, **kwargs: None

    # Get template loader
    template_loader = TemplateLoader()

    # Get document info
    doc_info = Config.get_document_info(doc_type)
    variables = config.get_variables()
    variables["DOC_TYPE_NAME"] = doc_info["name"]
    variables["DOC_TYPE_NAME_CN"] = doc_info["name_cn"]
    variables["DOC_TYPE"] = doc_type.upper()

    verbose_print(f"[VERBOSE] Generating {doc_type}...")

    # Determine format
    format_type = doc_info.get("format", "docx")
    if config.format == "both":
        generate_formats = [format_type] if format_type != "both" else ["docx", "xlsx"]
    else:
        generate_formats = [config.format]

    verbose_print(f"[VERBOSE] Format: {generate_formats}")

    # Load requirements database for vsr and rtm
    if db is None and doc_type in ["vsr", "rtm", "ra"]:
        project_path = (
            Path(config.output).parent if config.output != "./output" else Path.cwd()
        )
        db_path = find_requirements_db(project_path)
        if db_path:
            verbose_print(f"[VERBOSE] Found requirements DB at: {db_path}")
            try:
                with open(db_path, "r", encoding="utf-8") as f:
                    db = json.load(f)
                if db:
                    compatibility = check_template_compatibility(db)
                    if not compatibility.compatible:
                        print(f"Warning: {compatibility.message}")
                        print("  Generation may produce unexpected results.")
                    if doc_type in ["rtm", "vsr"]:
                        db, was_migrated = migrate_template_if_needed(db)
                        if was_migrated:
                            print(f"[Version] Migrated template to {TEMPLATE_VERSION}")
                            with open(db_path, "w", encoding="utf-8") as f:
                                json.dump(db, f, indent=2, ensure_ascii=False)
            except Exception:
                pass

    # Smart rebuild: skip if requirements unchanged
    if diff_only and db and doc_type in ["vsr", "rtm", "ra"]:
        output_dir = Path(config.output)
        if not _check_requirements_changed(db, output_dir):
            print(f"Skipping {doc_type}: requirements unchanged since last generation")
            return []

    output_files = []

    for fmt in generate_formats:
        if fmt == "xlsx":
            # Excel generation
            excel_gen = ExcelGenerator(config.output)

            # Load requirements database for RTM
            rtm_db = None
            if doc_type == "rtm":
                rtm_db = db

            output_file = excel_gen.generate(
                doc_type=doc_type, variables=variables, db=rtm_db
            )
            output_files.append(output_file)
            print(f"Generated: {output_file}")
        else:
            # Word generation
            try:
                template_content = template_loader.load_template(doc_type)
                # Process bilingual content based on config
                template_content = process_markdown_table_bilingual(
                    template_content,
                    bilingual=config.bilingual,
                    language=config.language,
                )
            except FileNotFoundError:
                print(f"Warning: Template not found for {doc_type}, using default")
                template_content = f"# {doc_info['name']}\n\nDocument: {config.project}\nSystem: {config.system}"

            # Add traceability tables for VSR
            if doc_type == "vsr" and db:
                variables["TRACEABILITY_TABLE"] = generate_traceability_table_markdown(
                    db
                )
                variables["COVERAGE_SUMMARY"] = generate_coverage_summary_markdown(db)

            # Add change description placeholder for RA
            if doc_type == "ra":
                variables["CHANGE_DESCRIPTION"] = variables.get(
                    "CHANGE_DESCRIPTION", "[变更描述 / Change Description]"
                )

            word_gen = WordGenerator(config.output)
            output_file = word_gen.generate(
                doc_type=doc_type, content=template_content, variables=variables
            )
            output_files.append(output_file)
            print(f"Generated: {output_file}")

    # Save requirements hash after successful RTM generation for incremental updates
    if doc_type in ["vsr", "rtm", "ra"] and db:
        _save_requirements_hash(db, Path(config.output))

    return output_files


def generate_all(config: Config, diff_only: bool = False, verbose: bool = False):
    """Generate all documents"""

    verbose_print = print if verbose else lambda *args, **kwargs: None

    doc_types = [
        "vp",
        "urs",
        "fs",
        "ra",
        "iq",
        "oq",
        "pq",
        "vsr",
        "rtm",
        "checklist",
        "test-case",
    ]

    print(f"\nGenerating validation package for: {config.project}")
    print(f"System: {config.system}")
    print(f"Category: {config.category}")
    print(f"Output: {config.output}\n")

    all_files = []

    for i, doc_type in enumerate(doc_types, 1):
        verbose_print(f"[VERBOSE] [{i}/{len(doc_types)}] Processing {doc_type}...")
        try:
            files = generate_document(
                doc_type, config, diff_only=diff_only, verbose=verbose
            )
            verbose_print(f"[VERBOSE]   Generated {len(files)} file(s)")
            all_files.extend(files)
        except Exception as e:
            print(f"Error generating {doc_type}: {e}")

    print(f"\n{'=' * 50}")
    print(f"Generated {len(all_files)} documents:")
    for f in all_files:
        print(f"  - {f}")

    # Auto-run compliance check if requirements.json exists
    project_path = (
        Path(config.output).parent if config.output != "./output" else Path.cwd()
    )
    req_path = find_requirements_db(project_path)
    if req_path:
        verbose_print(f"\n[VERBOSE] Running compliance check...")
        try:
            from compliance_checker import ComplianceChecker

            checker = ComplianceChecker(req_path)
            checker.load_data()
            exit_code, issues = checker.check()
            if issues:
                print(f"\n⚠️  Compliance issues found ({len(issues)}):")
                for issue in issues[:5]:  # Show first 5 issues
                    print(f"  - {issue}")
                if len(issues) > 5:
                    print(f"  ... and {len(issues) - 5} more")
                print("  Run 'generate.py check' for full report")
            else:
                verbose_print("[VERBOSE] ✓ No compliance issues found")
        except Exception as e:
            verbose_print(f"[VERBOSE] Compliance check skipped: {e}")

    return all_files


def find_requirements_db(project_path: Path) -> Optional[Path]:
    """Find requirements.json in multiple possible locations

    Search order:
    1. project_path / "requirements.json"
    2. project_path.parent / "requirements.json" (parent directory)
    3. project_path.parent.parent / "requirements.json" (grandparent directory)
    4. project_path / "doc" / "requirements.json"
    5. project_path / "docs" / "requirements.json"
    6. project_path / "src" / "requirements.json"

    Returns path to requirements.json or None if not found.
    """
    search_paths = [
        project_path / "requirements.json",
        project_path.parent / "requirements.json",
        project_path.parent.parent / "requirements.json",
        project_path / "doc" / "requirements.json",
        project_path / "docs" / "requirements.json",
        project_path / "src" / "requirements.json",
    ]

    for path in search_paths:
        if path.exists() and path.is_file():
            print(f"  Found requirements.json at: {path}")
            return path

    return None


def find_monorepo_projects(root_path: Path) -> List[Dict[str, Any]]:
    """Find all projects within a monorepo structure

    Detects common monorepo layouts:
    - apps/ or packages/ directories with individual project folders
    - Each subproject has its own requirements.json

    Returns list of dicts with {name, path, requirements_path}
    """
    projects = []
    search_dirs = ["apps", "packages", "projects", "modules", "services", "src"]

    for search_dir in search_dirs:
        dir_path = root_path / search_dir
        if not dir_path.exists():
            continue

        for item in dir_path.iterdir():
            if not item.is_dir():
                continue

            req_path = item / "requirements.json"
            if req_path.exists():
                projects.append(
                    {"name": item.name, "path": item, "requirements_path": req_path}
                )
            else:
                nested_req = find_requirements_db(item)
                if nested_req:
                    projects.append(
                        {
                            "name": item.name,
                            "path": item,
                            "requirements_path": nested_req,
                        }
                    )

    return projects


def detect_monorepo_root(project_path: Path) -> Optional[Path]:
    """Detect if project is part of a monorepo and return root path

    Looks for monorepo indicators:
    - apps/, packages/, projects/ directories
    - root requirements.json with workspace config
    - package.json with workspaces field
    - rush.json, pnpm-workspace.yaml, lerna.json
    """
    monorepo_indicators = ["apps", "packages", "projects", "modules", "services"]

    indicators_found = []
    for indicator in monorepo_indicators:
        if (project_path / indicator).exists():
            indicators_found.append(indicator)

    if indicators_found:
        return project_path

    parent = project_path.parent
    for _ in range(3):
        for indicator in monorepo_indicators:
            if (parent / indicator).exists():
                return parent
        parent = parent.parent

    return None


def sync_requirements_to_template(
    doc_type: str, project_path: Optional[Path] = None
) -> bool:
    """Sync requirements from requirements.json to template

    Returns True if sync was performed, False otherwise.
    """
    if doc_type not in ["urs", "fs", "ts"]:
        return False

    if project_path is None:
        project_path = Path.cwd()

    db_path = find_requirements_db(project_path)
    if not db_path:
        print("  No requirements.json found, skipping sync")
        return False

    try:
        with open(db_path, "r", encoding="utf-8") as f:
            db = json.load(f)
    except Exception as e:
        print(f"  Error reading requirements.json: {e}")
        return False

    requirements = db.get("requirements", [])
    if not requirements:
        print("  No requirements found, skipping sync")
        return False

    # Group requirements by module
    by_module: Dict[str, List[Dict]] = {}
    for req in requirements:
        module = req.get("module", "business_func")
        if module not in by_module:
            by_module[module] = []
        by_module[module].append(req)

    # Get template path
    skill_root = get_skill_root()
    template_path = skill_root / "templates" / f"{doc_type}.md"

    if not template_path.exists():
        print(f"  Template not found: {template_path}, skipping sync")
        return False

    # Backup template
    backup_path = template_path.with_suffix(
        f".md.backup.{datetime.now().strftime('%Y%m%d%H%M%S')}"
    )
    shutil.copy2(template_path, backup_path)
    print(f"  Backed up template to: {backup_path.name}")

    # Read template
    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()

    # Check which modules need to be added
    modules_added = []

    # Iterate over all modules found in requirements.json
    for module_id, requirements_list in by_module.items():
        # Get module info (use STANDARD_MODULES if available, otherwise generate)
        if module_id in STANDARD_MODULES:
            module_info = STANDARD_MODULES[module_id]
        else:
            # Create info for custom module
            module_info = {
                "name": f"{module_id} / {module_id.replace('_', ' ').title()}",
                "prefix": module_id[:3].upper(),
            }

        # Check if section already exists in template
        # Look for patterns like "### 4.X Module Name" or "### 4.X 模块名"
        section_found = False
        for section_num in range(1, 20):
            section_patterns = [
                f"### 4.{section_num} ",
                f"### {section_num} ",
            ]
            for pattern in section_patterns:
                if pattern in template_content:
                    # Check if this is our module
                    module_name_cn = module_info["name"].split(" / ")[0]
                    if (
                        module_name_cn
                        in template_content.split(pattern)[1].split("\n")[0]
                    ):
                        section_found = True
                        break
            if section_found:
                break

        if section_found:
            print(f"  Module {module_id} section already exists, skipping")
            continue

        module_name = module_info["name"]
        module_prefix = module_info.get("prefix", module_id[:3].upper())
        reqs_list = by_module[module_id]

        # Generate new section
        new_section = _generate_module_section(
            module_id, module_name, module_prefix, reqs_list, template_content
        )

        # Find insertion point (before "## 5. 非功能需求" or similar)
        insert_marker = "## 5. 非功能需求"
        if insert_marker in template_content:
            template_content = template_content.replace(
                insert_marker, new_section + "\n\n" + insert_marker
            )
            modules_added.append(module_id)
            print(
                f"  Added section for module: {module_id} ({len(reqs_list)} requirements)"
            )
        else:
            # Append at end of functional requirements area
            template_content += "\n\n" + new_section
            modules_added.append(module_id)
            print(f"  Appended section for module: {module_id}")

    if modules_added:
        # Write updated template
        with open(template_path, "w", encoding="utf-8") as f:
            f.write(template_content)
        print(f"  Template updated with {len(modules_added)} new module sections")
        return True
    else:
        print("  No new modules to add")
        return False


def _get_next_section_number(template_content: str) -> str:
    """Calculate next available section number (4.X) in template dynamically

    Scans existing 4.X section headers in template and returns the next number.
    This ensures unique, consecutive numbering even for custom modules.
    """
    import re

    existing = re.findall(r"### 4\.(\d+)", template_content)
    if not existing:
        return "1"
    return str(max(int(n) for n in existing) + 1)


def _generate_module_section(
    module_id: str,
    module_name: str,
    module_prefix: str,
    requirements: List[Dict],
    template_content: str = "",
) -> str:
    """Generate a markdown section for a module with its requirements

    Args:
        module_id: Module identifier (e.g., 'pm_query', 'user_mgmt')
        module_name: Display name (e.g., 'PM查询 / PM Query')
        module_prefix: Prefix for requirement IDs (e.g., 'PM', 'UM')
        requirements: List of requirement dicts
        template_content: Current template content (for dynamic section numbering)
    """
    name_parts = module_name.split(" / ")
    cn_name = name_parts[0] if len(name_parts) > 0 else module_id
    en_name = name_parts[1].split("(")[0].strip() if len(name_parts) > 1 else module_id

    section_num = (
        _get_next_section_number(template_content) if template_content else "1"
    )

    lines = [
        f"### 4.{section_num} {cn_name} / {en_name}",
        "",
        f"| ID | 需求描述 / Requirement Description | 优先级 / Priority | 验证方法 / Verification |",
        f"|----|-----------------------------------|------------------|----------------------|",
    ]

    for req in requirements:
        req_id = req.get("id", f"URS-{module_prefix}-XXX")
        desc = req.get("description", "")
        priority = req.get("priority", "[应该]")

        lines.append(f"| {req_id} | {desc} | {priority} | 测试 / Test |")

    return "\n".join(lines)


def sync_template_to_db(doc_type: str, project_path: Optional[Path] = None) -> bool:
    """Sync requirements from template to requirements.json

    Extracts requirements from template (e.g., urs.md) and adds them to requirements.json.
    Existing requirements are preserved, new ones are added.

    Returns True if sync was performed, False otherwise.
    """
    if doc_type != "urs":
        return False

    if project_path is None:
        project_path = Path.cwd()

    # Get template path
    skill_root = get_skill_root()
    template_path = skill_root / "templates" / f"{doc_type}.md"

    if not template_path.exists():
        print(f"  Template not found: {template_path}, skipping sync")
        return False

    # Read template
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            template_content = f.read()
    except Exception as e:
        print(f"  Error reading template: {e}")
        return False

    # Find requirements in template (format: | URS-xxx | description | ...)
    import re

    pattern = r"\|\s*(URS-\d{3})\s*\|([^|]+)\|"
    matches = re.findall(pattern, template_content)

    if not matches:
        print("  No requirements found in template, skipping sync")
        return False

    print(f"  Found {len(matches)} requirements in template")

    # Load or create requirements.json
    db_path = find_requirements_db(project_path)
    if db_path is None:
        # Create new database in project root
        db_path = project_path / "requirements.json"
        db = {
            "version": "1.0",
            "requirements": [],
            "risks": [],
            "test_results": [],
            "commit_links": [],
        }
        print(f"  Creating new requirements.json at: {db_path}")
    else:
        try:
            with open(db_path, "r", encoding="utf-8") as f:
                db = json.load(f)
            print(f"  Loaded existing requirements.json from: {db_path}")
        except Exception as e:
            print(f"  Error reading requirements.json: {e}")
            return False

    # Get existing requirement IDs
    existing_ids = {r.get("id") for r in db.get("requirements", [])}

    # Add new requirements
    new_count = 0
    for req_id, desc in matches:
        if req_id in existing_ids:
            continue

        # Infer module from description keywords
        module = _infer_module_from_description(desc.strip())

        requirement = {
            "id": req_id,
            "type": "URS",
            "description": desc.strip(),
            "priority": "应该",
            "module": module,
            "source_file": str(template_path),
            "source_line": None,
            "esig_required": False,
            "esig_category": None,
            "fs_ref": None,
            "ts_ref": None,
            "test_cases": [],
            "tags": ["from_template"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "draft",
        }

        db.setdefault("requirements", []).append(requirement)
        existing_ids.add(req_id)
        new_count += 1

    if new_count > 0:
        try:
            with open(db_path, "w", encoding="utf-8") as f:
                json.dump(db, f, indent=2, ensure_ascii=False)
            print(f"  Added {new_count} new requirements to requirements.json")
            print(f"  Total requirements: {len(db.get('requirements', []))}")
            return True
        except Exception as e:
            print(f"  Error writing requirements.json: {e}")
            return False
    else:
        print("  No new requirements to add")
        return False


def sync_bidirectional(
    doc_type: str,
    project_path: Optional[Path] = None,
    direction: str = "both",
    conflict_resolution: str = "newer",
) -> bool:
    """Bidirectional sync between template and requirements.json

    Args:
        doc_type: Document type (urs, fs, ts)
        project_path: Project path
        direction: 'to-json', 'to-template', or 'both'
        conflict_resolution: 'newer', 'template', 'json', 'ask'

    Returns True if any sync was performed
    """
    if doc_type not in ["urs", "fs", "ts"]:
        return False

    if project_path is None:
        project_path = Path.cwd()

    db_path = find_requirements_db(project_path)

    local_template_path = project_path / "templates" / f"{doc_type}.md"
    skill_root = get_skill_root()
    skill_template_path = skill_root / "templates" / f"{doc_type}.md"

    if local_template_path.exists():
        template_path = local_template_path
    elif skill_template_path.exists():
        template_path = skill_template_path
    else:
        print(f"  Template not found: {doc_type}.md")
        return False

    print(f"  Using template: {template_path}")

    # Load database
    db = None
    if db_path and db_path.exists():
        try:
            with open(db_path, "r", encoding="utf-8") as f:
                db = json.load(f)
        except Exception:
            pass

    # Read template
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            template_content = f.read()
    except Exception as e:
        print(f"  Error reading template: {e}")
        return False

    # Parse requirements from template
    pattern = r"\|\s*(URS-\d{3})\s*\|([^|]+)\|"
    template_req_matches = re.findall(pattern, template_content)
    template_req_ids = {match[0] for match in template_req_matches}
    template_reqs = {match[0]: match[1].strip() for match in template_req_matches}

    # Get requirements from database
    json_req_ids = set()
    json_reqs = {}
    if db:
        for req in db.get("requirements", []):
            req_id = req.get("id")
            if req_id:
                json_req_ids.add(req_id)
                json_reqs[req_id] = req

    # Determine changes needed
    only_in_template = template_req_ids - json_req_ids
    only_in_json = json_req_ids - template_req_ids
    in_both = template_req_ids & json_req_ids

    # Check for conflicts (same ID, different description)
    conflicts = []
    for req_id in in_both:
        if template_reqs[req_id] != json_reqs[req_id].get("description", ""):
            conflicts.append(
                {
                    "id": req_id,
                    "template_desc": template_reqs[req_id],
                    "json_desc": json_reqs[req_id].get("description", ""),
                }
            )

    sync_performed = False

    # Sync template -> JSON
    if direction in ["to-json", "both"] and only_in_template:
        print(
            f"\n[Sync to JSON] Adding {len(only_in_template)} requirements from template..."
        )
        if db is None:
            db = {
                "version": "1.0",
                "requirements": [],
                "risks": [],
                "test_results": [],
                "commit_links": [],
            }

        new_count = 0
        for req_id in only_in_template:
            module = _infer_module_from_description(template_reqs[req_id])
            requirement = {
                "id": req_id,
                "type": doc_type.upper(),
                "description": template_reqs[req_id],
                "module": module,
                "priority": "应该",
                "source_file": str(template_path),
                "source_line": None,
                "esig_required": False,
                "esig_category": None,
                "tags": ["from_template"],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "status": "draft",
            }
            db.setdefault("requirements", []).append(requirement)
            new_count += 1

        if new_count > 0:
            try:
                with open(
                    db_path or (project_path / "requirements.json"),
                    "w",
                    encoding="utf-8",
                ) as f:
                    json.dump(db, f, indent=2, ensure_ascii=False)
                print(f"  Added {new_count} requirements to requirements.json")
                sync_performed = True
            except Exception as e:
                print(f"  Error writing requirements.json: {e}")

    # Sync JSON -> template
    if direction in ["to-template", "both"] and only_in_json:
        print(
            f"\n[Sync to Template] Adding {len(only_in_json)} requirements to template..."
        )

        # Group requirements by module
        by_module: Dict[str, List[Dict]] = {}
        for req_id in only_in_json:
            req = json_reqs[req_id]
            module = req.get("module", "business_func")
            by_module.setdefault(module, []).append(req)

        # Backup template
        backup_path = template_path.with_suffix(
            f".md.backup.{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        shutil.copy2(template_path, backup_path)
        print(f"  Backed up template to: {backup_path.name}")

        modules_added = []

        # Process each module: check if section exists, create if not
        for module_id, reqs in by_module.items():
            # Get module info
            if module_id in STANDARD_MODULES:
                module_info = STANDARD_MODULES[module_id]
            else:
                module_info = {
                    "name": f"{module_id} / {module_id.replace('_', ' ').title()}",
                    "prefix": module_id[:3].upper(),
                }

            # Check if section already exists
            module_name_cn = module_info["name"].split(" / ")[0]
            section_found = False
            for section_num in range(1, 20):
                pattern = f"### 4.{section_num} {module_name_cn}"
                if pattern in template_content:
                    section_found = True
                    break

            if section_found:
                print(f"  Module {module_id} section exists, skipping")
                continue

            # Generate module section
            new_section = _generate_module_section(
                module_id,
                module_info["name"],
                module_info.get("prefix", module_id[:3].upper()),
                reqs,
                template_content,
            )

            # Insert before "## 5. 非功能需求"
            insert_marker = "## 5. 非功能需求"
            if insert_marker in template_content:
                template_content = template_content.replace(
                    insert_marker, new_section + "\n\n" + insert_marker
                )
            else:
                template_content += "\n\n" + new_section

            modules_added.append(module_id)
            print(f"  Added section for module: {module_id} ({len(reqs)} requirements)")

        # Write updated template
        if modules_added:
            try:
                with open(template_path, "w", encoding="utf-8") as f:
                    f.write(template_content)
                print(
                    f"  Template updated with {len(modules_added)} new module sections"
                )
                sync_performed = True
            except Exception as e:
                print(f"  Error writing template: {e}")

    # Handle conflicts
    if conflicts:
        print(f"\n[Conflicts] Found {len(conflicts)} conflicting requirements")
        for conflict in conflicts:
            print(f"  {conflict['id']}:")
            print(f"    Template: {conflict['template_desc'][:50]}...")
            print(f"    JSON: {conflict['json_desc'][:50]}...")

        if conflict_resolution == "ask":
            print("\n  Use --conflict-resolution to specify how to resolve conflicts:")
            print("    --conflict-resolution template  : Keep template descriptions")
            print("    --conflict-resolution json       : Keep JSON descriptions")
            print(
                "    --conflict-resolution newer      : Keep newer (based on updated_at)"
            )
        elif conflict_resolution == "template":
            print("\n  Resolving conflicts: keeping template descriptions")
        elif conflict_resolution == "json":
            print("\n  Resolving conflicts: keeping JSON descriptions")

    return sync_performed


def _infer_module_from_description(description: str) -> str:
    """Infer module from requirement description"""
    desc_lower = description.lower()

    module_keywords = {
        "user_mgmt": [
            "用户",
            "user",
            "账户",
            "account",
            "登录",
            "login",
            "认证",
            "auth",
            "密码",
            "password",
            "角色",
            "role",
            "权限",
            "permission",
        ],
        "audit_trail": [
            "审计",
            "audit",
            "日志",
            "log",
            "追踪",
            "trace",
            "记录",
            "record",
        ],
        "data_mgmt": [
            "数据",
            "data",
            "数据库",
            "database",
            "存储",
            "storage",
            "备份",
            "backup",
            "恢复",
            "recovery",
        ],
        "business_func": [
            "业务",
            "business",
            "功能",
            "function",
            "流程",
            "process",
            "工作流",
            "workflow",
        ],
        "reporting": ["报告", "report", "导出", "export", "打印", "print", "报表"],
        "integration": ["接口", "api", "integration", "集成", "对接"],
        "security": [
            "安全",
            "security",
            "加密",
            "encrypt",
            "解密",
            "decrypt",
            "tls",
            "ssl",
            "防火墙",
            "firewall",
        ],
        "compliance": [
            "合规",
            "compliance",
            "法规",
            "regulation",
            "alcoa",
            "part 11",
            "annex 11",
            "gxp",
        ],
    }

    for module_id, keywords in module_keywords.items():
        for keyword in keywords:
            if keyword.lower() in desc_lower:
                return module_id

    return "business_func"


def run_interactive_workflow(config: Config, project_path: Path, args) -> None:
    """Interactive step-by-step document generation workflow

    For each step:
    - Press Enter to continue
    - Type 's' to skip
    - Type 'q' to quit
    """

    steps = [
        ("解析代码注释", "parse"),
        ("同步需求到数据库", "sync-template-to-db"),
        ("同步需求到模板", "sync"),
        ("生成 URS", "urs"),
        ("生成 FS", "fs"),
        ("生成 RA", "ra"),
        ("生成 IQ", "iq"),
        ("生成 OQ", "oq"),
        ("生成 PQ", "pq"),
        ("生成 RTM", "rtm"),
        ("生成 VSR", "vsr"),
    ]

    total = len(steps)
    generated_files = []

    print("\n" + "=" * 50)
    print("交互模式 - Interactive Mode")
    print("=" * 50)
    print(f"项目: {config.project}")
    print(f"系统: {config.system}")
    print(f"输出目录: {config.output}")
    print("=" * 50)

    for i, (step_name, step_action) in enumerate(steps, 1):
        print(f"\n[{i}/{total}] {step_name}...")

        response = input("  → 按 Enter 继续，'s' 跳过，'q' 退出: ").strip().lower()

        if response == "q":
            print("\n已退出。已生成的文件保留在 output/ 目录")
            if generated_files:
                print(f"\n已生成的 {len(generated_files)} 个文件:")
                for f in generated_files:
                    print(f"  - {f}")
            return
        elif response == "s":
            print("  [跳过]")
            continue

        try:
            if step_action == "parse":
                parser = RequirementsParser(project_path)
                requirements = parser.parse_directory(Path("."))
                print(f"  ✓ 完成 (发现 {len(requirements)} 个需求)")

            elif step_action == "sync-template-to-db":
                result = sync_template_to_db("urs", project_path)
                if result:
                    print("  ✓ 完成")
                else:
                    print("  ✓ 完成 (无需同步)")

            elif step_action == "sync":
                result = sync_bidirectional(
                    "urs",
                    project_path,
                    direction=args.sync_direction,
                    conflict_resolution=args.conflict_resolution,
                )
                if result:
                    print("  ✓ 完成")
                else:
                    print("  ✓ 完成 (无需同步)")

            elif step_action in ["urs", "fs", "ra", "iq", "oq", "pq", "rtm", "vsr"]:
                files = generate_document(step_action, config)
                generated_files.extend(files)
                for f in files:
                    print(f"  ✓ {f}")

            else:
                print("  [未知步骤]")

        except Exception as e:
            print(f"  ✗ 错误: {e}")
            continue

    print("\n" + "=" * 50)
    print(f"完成! 已生成 {len(generated_files)} 个文件")
    print("=" * 50)
    if generated_files:
        print("\n生成的文件:")
        for f in generated_files:
            print(f"  - {f}")


def run_compliance_check(args) -> None:
    """Run compliance check"""
    from compliance_checker import ComplianceChecker
    from pathlib import Path

    print("CSV Documentation Generator - Compliance Check")
    print("=" * 50)

    requirements_path = (
        Path(args.requirements)
        if hasattr(args, "requirements") and args.requirements
        else Path("requirements.json")
    )
    test_results_path = (
        Path(args.test_results)
        if hasattr(args, "test_results") and args.test_results
        else Path("test_results.json")
    )

    checker = ComplianceChecker(requirements_path, test_results_path)
    checker.load_data()
    exit_code, issues = checker.check()

    report = checker.generate_report(
        args.output_format if hasattr(args, "output_format") else "text"
    )
    print(report)

    sys.exit(exit_code)


def main():
    """Main entry point"""

    # Ensure virtual environment
    if not is_in_venv():
        ensure_venv()

    args = parse_args()

    # Prompt for GAMP category if not specified
    if args.category is None:
        args.category = prompt_gamp_category()

    # Create output directory
    Path(args.output).mkdir(parents=True, exist_ok=True)

    # Create config
    config = Config(
        project=args.project,
        system=args.system,
        category=args.category,
        bilingual=args.bilingual,
        language=args.language,
        output=args.output,
        format=args.format,
        doc_id=args.doc_id,
        version=args.version,
        author=args.author,
        reviewer=args.reviewer,
        approver=args.approver,
        critical_functions=args.critical_functions,
    )

    # Determine project path
    if args.project_root:
        project_path = Path(args.project_root)
    elif args.output != "./output":
        project_path = Path(args.output).parent
    else:
        project_path = Path.cwd()

    # Detect monorepo structure
    monorepo_root = detect_monorepo_root(project_path)
    if monorepo_root:
        print(f"[Monorepo] Detected root: {monorepo_root}")
        subprojects = find_monorepo_projects(monorepo_root)
        if subprojects:
            print(f"[Monorepo] Found {len(subprojects)} subprojects:")
            for p in subprojects:
                print(f"  - {p['name']}: {p['path']}")

    # Handle --sync-template-to-db first (before any document generation)
    if args.sync_template_to_db:
        print("\n[Sync Template to DB] Extracting requirements from template...")
        sync_template_to_db("urs", project_path)

    print(f"CSV Documentation Generator")
    print(f"{'=' * 50}")

    # Sync requirements to template if --sync is specified
    if args.sync:
        print("\n[Sync] Bidirectional sync between template and requirements.json...")
        doc_types_to_sync = (
            ["urs", "fs", "ts"] if args.doc_type == "all" else [args.doc_type]
        )
        for doc_type in doc_types_to_sync:
            sync_bidirectional(
                doc_type,
                project_path,
                direction=args.sync_direction,
                conflict_resolution=args.conflict_resolution,
            )

    # Generate documents
    verbose = getattr(args, "verbose", False)
    if args.interactive:
        run_interactive_workflow(config, project_path, args)
    elif args.doc_type == "check":
        run_compliance_check(args)
    elif args.doc_type == "all":
        generate_all(config, diff_only=args.diff_only, verbose=verbose)
    else:
        generate_document(
            args.doc_type, config, diff_only=args.diff_only, verbose=verbose
        )

    print(f"\nDone! Files saved to: {args.output}")


if __name__ == "__main__":
    main()


class SemanticActions:
    """
    Semantic Action Graph for CSV Documentation Generation.

    This class encapsulates the skill's capabilities as a semantic action graph,
    following the design philosophy that Skill = Tool's semantic encapsulation + reasoning trigger conditions.

    Each method represents a semantic action that can be dynamically invoked by an AI agent.
    """

    def __init__(self, skill_root: Optional[Path] = None):
        """Initialize SemanticActions with skill root path."""
        self.skill_root = skill_root or get_skill_root()
        self.venv_path = None
        self._ensure_environment()

    def _ensure_environment(self):
        """Ensure Python environment is set up."""
        if not is_in_venv():
            self.venv_path = ensure_venv()

    def parse_requirements(self, source_path: str) -> Dict[str, Any]:
        """
        Parse @URS, @FS, @TEST markers from source code.

        Args:
            source_path: Path to source code directory

        Returns:
            RequirementsDB dictionary with requirements, risks, test_results
        """
        parser = RequirementsParser()
        db = parser.parse_directory(source_path)
        return db

    def generate_vp(self, context: Dict[str, Any]) -> List[str]:
        """
        Create Validation Plan document.

        Args:
            context: Dict with project, system, category, output, etc.

        Returns:
            List of generated file paths
        """
        config = self._create_config(context)
        return generate_document("vp", config)

    def generate_urs(self, context: Dict[str, Any]) -> List[str]:
        """
        Create User Requirements Specification document.

        Args:
            context: Dict with project, system, category, output, etc.

        Returns:
            List of generated file paths
        """
        config = self._create_config(context)
        return generate_document("urs", config)

    def generate_fs(self, context: Dict[str, Any]) -> List[str]:
        """
        Create Functional Specification document.

        Args:
            context: Dict with project, system, category, output, etc.

        Returns:
            List of generated file paths
        """
        config = self._create_config(context)
        return generate_document("fs", config)

    def generate_ra(self, context: Dict[str, Any]) -> List[str]:
        """
        Create Risk Assessment document.

        Args:
            context: Dict with project, system, category, output, etc.
                  Optional: change_description for change-driven RA

        Returns:
            List of generated file paths
        """
        config = self._create_config(context)
        return generate_document("ra", config)

    def generate_ts(self, context: Dict[str, Any]) -> List[str]:
        """
        Create Technical Specification document.

        Args:
            context: Dict with project, system, category, output, etc.

        Returns:
            List of generated file paths
        """
        config = self._create_config(context)
        return generate_document("ts", config)

    def generate_iq(self, context: Dict[str, Any]) -> List[str]:
        """
        Create Installation Qualification protocol.

        Args:
            context: Dict with project, system, category, output, etc.

        Returns:
            List of generated file paths
        """
        config = self._create_config(context)
        return generate_document("iq", config)

    def generate_oq(self, context: Dict[str, Any]) -> List[str]:
        """
        Create Operational Qualification protocol.

        Args:
            context: Dict with project, system, category, output, etc.

        Returns:
            List of generated file paths
        """
        config = self._create_config(context)
        return generate_document("oq", config)

    def generate_pq(self, context: Dict[str, Any]) -> List[str]:
        """
        Create Performance Qualification protocol.

        Args:
            context: Dict with project, system, category, output, etc.

        Returns:
            List of generated file paths
        """
        config = self._create_config(context)
        return generate_document("pq", config)

    def generate_iq_oq_pq(self, context: Dict[str, Any]) -> List[str]:
        """
        Create all Qualification protocols (IQ, OQ, PQ).

        Args:
            context: Dict with project, system, category, output, etc.

        Returns:
            List of all generated file paths
        """
        config = self._create_config(context)
        files = []
        for doc_type in ["iq", "oq", "pq"]:
            files.extend(generate_document(doc_type, config))
        return files

    def generate_rtm(self, context: Dict[str, Any]) -> List[str]:
        """
        Create Requirements Traceability Matrix.

        Args:
            context: Dict with project, system, category, output, etc.

        Returns:
            List of generated file paths
        """
        config = self._create_config(context)
        return generate_document("rtm", config)

    def generate_vsr(self, context: Dict[str, Any]) -> List[str]:
        """
        Create Validation Summary Report.

        Args:
            context: Dict with project, system, category, output, etc.

        Returns:
            List of generated file paths
        """
        config = self._create_config(context)
        return generate_document("vsr", config)

    def generate_all(self, context: Dict[str, Any]) -> List[str]:
        """
        Generate complete validation package.

        Args:
            context: Dict with project, system, category, output, etc.

        Returns:
            List of all generated file paths
        """
        config = self._create_config(context)
        return generate_all(config)

    def sync_bidirectional(
        self,
        doc_type: str,
        project_path: str,
        direction: str = "both",
        conflict_resolution: str = "template",
    ) -> Dict[str, Any]:
        """
        Bidirectional sync between requirements.json and templates.

        Args:
            doc_type: Document type (urs, fs, ts)
            project_path: Path to project directory
            direction: Sync direction (to-json, to-template, both)
            conflict_resolution: How to resolve conflicts (template, json, newer)

        Returns:
            Dict with sync results
        """
        result = sync_bidirectional(
            doc_type,
            Path(project_path),
            direction=direction,
            conflict_resolution=conflict_resolution,
        )
        return {"status": "success", "result": result}

    def run_compliance_check(
        self,
        requirements_path: str,
        test_results_path: Optional[str] = None,
        output_format: str = "text",
    ) -> Dict[str, Any]:
        """
        Verify GxP compliance of requirements and test results.

        Args:
            requirements_path: Path to requirements.json
            test_results_path: Optional path to test_results.json
            output_format: Output format (text or json)

        Returns:
            Compliance report dictionary
        """
        checker = ComplianceChecker()

        with open(requirements_path, "r", encoding="utf-8") as f:
            requirements = json.load(f)

        test_results = None
        if test_results_path:
            with open(test_results_path, "r", encoding="utf-8") as f:
                test_results = json.load(f)

        report = checker.check(requirements, test_results)

        if output_format == "json":
            return {"status": "success", "report": report}

        checker.print_report(report)
        return {"status": "success", "report": report}

    def _create_config(self, context: Dict[str, Any]) -> Config:
        """Create Config object from context dictionary."""
        return Config(
            project=context.get("project"),
            system=context.get("system"),
            category=context.get("category", 4),
            bilingual=context.get("bilingual", True),
            language=context.get("language", "zh"),
            output=context.get("output", "./output"),
            format=context.get("format", "both"),
            doc_id=context.get("doc_id"),
            version=context.get("version"),
            author=context.get("author"),
            reviewer=context.get("reviewer"),
            approver=context.get("approver"),
            critical_functions=context.get("critical_functions"),
        )
