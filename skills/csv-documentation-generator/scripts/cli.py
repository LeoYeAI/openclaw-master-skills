#!/usr/bin/env python3
"""CSV Documentation Generator - Unified CLI

Usage:
    csv-docs <command> [options]

Commands:
    init                    Initialize project configuration
    agent                   Detect and show current agent mode
    agent --set <mode>      Set agent mode (interactive/autonomous)
    parse <path>            Parse code for requirements
    status                  Show requirements status
    add <description>       Manually add a requirement
    link [--commit <hash>]  Link requirements to commit
    test [--results <path>] Parse and add test results
    risk                    Run risk analysis
    generate <doc>          Generate document (vp/urs/fs/iq/oq/pq/ra/vsr)
    audit                   Show audit log
    audit --export <path>   Export audit log
"""

import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from agent import AgentDetector, get_agent_mode, set_agent_mode
from requirements.parser import RequirementsParser
from requirements.risk_analyzer import RiskAnalyzer
from requirements.linker import GitLinker
from tests.parser import TestResultsParser
from fill.filler import DocumentFiller
from audit.log import AuditLogger


def print_banner():
    """Print CLI banner"""
    print("=" * 60)
    print("CSV Documentation Generator (csv-docs)")
    print("=" * 60)


def cmd_init(project_path):
    """Initialize project configuration"""
    config_path = project_path / ".csv-docs-config.json"
    req_path = project_path / "requirements.json"

    if config_path.exists():
        print(f"配置文件已存在: {config_path}")
    else:
        config = {
            "version": "1.0",
            "agent": {"default_mode": "interactive", "auto_detect": True},
            "autonomous": {"on_duplicate": "overwrite"},
        }
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"已创建配置文件: {config_path}")

    if req_path.exists():
        print(f"需求数据库已存在: {req_path}")
    else:
        req_db = {
            "version": "1.0",
            "requirements": [],
            "risks": [],
            "test_results": [],
            "commit_links": [],
        }
        with open(req_path, "w", encoding="utf-8") as f:
            json.dump(req_db, f, indent=2, ensure_ascii=False)
        print(f"已创建需求数据库: {req_path}")

    print("\n初始化完成！")


def cmd_agent(project_path, args):
    """Show or set agent mode"""
    detector = AgentDetector(project_path)

    if args.get("set"):
        mode = args["set"]
        if mode not in ["interactive", "autonomous"]:
            print(f"错误: 无效模式 '{mode}'")
            return 1

        success = detector.set_mode(mode)

        if success:
            print(f"已设置模式为: {mode} (保存到 .csv-docs-config.json)")
        else:
            print(f"设置失败")
            return 1
    else:
        info = detector.detect()
        print(f"检测到的 Agent: {info.name}")
        print(f"当前模式: {info.mode}")
        print(f"检测方式: {info.source}")
        print(f"置信度: {info.confidence:.0%}")


def cmd_parse(project_path, args, mode):
    """Parse code for requirements"""
    path = Path(args.get("<path>", "./src"))
    parser = RequirementsParser(project_path)
    audit = AuditLogger(project_path)
    auto_add = args.get("--auto-add", False)

    if path.is_file():
        requirements = parser.parse_file(path)
    else:
        requirements = parser.parse_directory(path)

    print(f"解析路径: {path}")
    print(f"发现需求: {len(requirements)} 个")

    if not requirements:
        print("未发现需求")
        return 0

    # Show preview in interactive mode (unless --auto-add is specified)
    if mode == "interactive" and not auto_add:
        print("\n发现的需求:")
        for i, req in enumerate(requirements, 1):
            print(f"\n  [{i}] {req.id}: {req.description[:60]}...")
            print(f"      类型: {req.type}, 优先级: {req.priority}")
            if req.esig_required:
                print(f"      ⚠️  可能涉及电子签名")

        print("\n请选择操作:")
        print("  [a] 添加全部")
        print("  [s] 选择性添加")
        print("  [c] 取消")

        try:
            choice = input("\n> ").strip().lower()
        except EOFError:
            print("\n检测到非交互式环境，自动切换到 autonomous 模式")
            choice = "a"

        if choice == "a":
            for req in requirements:
                parser.requirements_db.setdefault("requirements", []).append(
                    req.__dict__
                )
                audit.log_requirement_added(req.id, req.description, mode)
            parser._save_requirements_db()
            print(f"已添加 {len(requirements)} 个需求")
        elif choice == "s":
            print("请输入要添加的编号（逗号分隔）:")
            try:
                indices = input("> ").strip()
            except EOFError:
                print("非交互式环境，无法进行选择性添加，使用 autonomous 模式")
                choice = "a"
                for req in requirements:
                    parser.requirements_db.setdefault("requirements", []).append(
                        req.__dict__
                    )
                    audit.log_requirement_added(req.id, req.description, mode)
                parser._save_requirements_db()
                print(f"已添加 {len(requirements)} 个需求")
                return 0
            try:
                selected = [requirements[int(i) - 1] for i in indices.split(",")]
                for req in selected:
                    parser.requirements_db.setdefault("requirements", []).append(
                        req.__dict__
                    )
                    audit.log_requirement_added(req.id, req.description, mode)
                parser._save_requirements_db()
                print(f"已添加 {len(selected)} 个需求")
            except (ValueError, IndexError):
                print("输入无效")
                return 1
    else:
        # Autonomous mode - add all automatically
        for req in requirements:
            existing = [
                r
                for r in parser.requirements_db.get("requirements", [])
                if r.get("id") == req.id
            ]
            if existing:
                # Check on_duplicate setting
                config_path = project_path / ".csv-docs-config.json"
                if config_path.exists():
                    with open(config_path) as f:
                        config = json.load(f)
                    on_duplicate = config.get("autonomous", {}).get(
                        "on_duplicate", "skip"
                    )
                else:
                    on_duplicate = "skip"

                if on_duplicate == "overwrite":
                    parser.requirements_db["requirements"] = [
                        r
                        for r in parser.requirements_db.get("requirements", [])
                        if r.get("id") != req.id
                    ]
                    parser.requirements_db.setdefault("requirements", []).append(
                        req.__dict__
                    )

            parser.requirements_db.setdefault("requirements", []).append(req.__dict__)
            audit.log_requirement_added(req.id, req.description, mode)

        parser._save_requirements_db()
        print(f"✅ 自动添加了 {len(requirements)} 个需求")

        # Check for eSignature requirements
        esig_reqs = [r for r in requirements if r.esig_required]
        if esig_reqs:
            print(f"\n⚠️  检测到 {len(esig_reqs)} 个可能涉及电子签名的需求:")
            for req in esig_reqs:
                print(f"   - {req.id}: {req.description[:50]}...")


def cmd_status(project_path):
    """Show requirements status"""
    parser = RequirementsParser(project_path)
    risk_analyzer = RiskAnalyzer(project_path)

    requirements = parser.requirements_db.get("requirements", [])
    risks = parser.requirements_db.get("risks", [])
    test_results = parser.requirements_db.get("test_results", [])

    print("\n📋 需求状态:")
    print(f"   总数: {len(requirements)}")

    by_type = {}
    by_status = {}
    for r in requirements:
        by_type[r.get("type", "unknown")] = by_type.get(r.get("type"), 0) + 1
        by_status[r.get("status", "unknown")] = by_status.get(r.get("status"), 0) + 1

    print("   按类型:", ", ".join(f"{k}:{v}" for k, v in by_type.items()))
    print("   按状态:", ", ".join(f"{k}:{v}" for k, v in by_status.items()))

    esig = [r for r in requirements if r.get("esig_required")]
    if esig:
        print(f"\n⚠️  电子签名需求: {len(esig)} 个")

    print("\n📊 风险状态:")
    print(f"   总数: {len(risks)}")

    by_level = {}
    for r in risks:
        level = r.get("risk_level", "unknown")
        by_level[level] = by_level.get(level, 0) + 1

    if by_level:
        print("   按等级:", ", ".join(f"{k}:{v}" for k, v in by_level.items()))

    high_risks = [r for r in risks if r.get("risk_level") in ["high", "critical"]]
    if high_risks:
        print(f"\n🔴 高风险 ({len(high_risks)}):")
        for r in high_risks[:5]:
            print(
                f"   - {r.get('id')}: {r.get('risk_description', '')[:50]}... (RPN: {r.get('rpn')})"
            )

    print("\n🧪 测试结果:")
    print(f"   总数: {len(test_results)}")

    passed = len([t for t in test_results if t.get("status") == "pass"])
    failed = len([t for t in test_results if t.get("status") == "fail"])

    if test_results:
        print(
            f"   通过: {passed}, 失败: {failed}, 通过率: {passed / len(test_results) * 100:.1f}%"
        )


def cmd_add(project_path, args, mode):
    """Manually add a requirement"""
    description = args.get("<description>")
    if not description:
        print("错误: 请提供需求描述")
        return 1

    parser = RequirementsParser(project_path)
    audit = AuditLogger(project_path)

    req_type = args.get("--type", "URS")
    priority = args.get("--priority", "应该")

    requirement = parser.add_requirement(
        description=description, req_type=req_type, priority=priority
    )

    audit.log_requirement_added(requirement.id, requirement.description, mode)

    print(f"✅ 已添加: {requirement.id}")
    if requirement.esig_required:
        print(f"⚠️  检测到可能涉及电子签名")


def cmd_link(project_path, args, mode):
    """Link requirements to commit"""
    linker = GitLinker(project_path)
    audit = AuditLogger(project_path)

    if args.get("--commit"):
        commit_hash = args["--commit"]
    else:
        # Use last commit
        try:
            import subprocess

            result = subprocess.run(
                ["git", "rev-parse", "HEAD"], capture_output=True, text=True
            )
            commit_hash = result.stdout.strip()
        except Exception:
            print("错误: 无法获取提交hash")
            return 1

    # Extract requirements from commit message
    link = linker.link_commit(commit_hash)

    audit.log_commit_linked(link.commit_hash, link.requirements, mode)

    print(f"✅ 已关联提交 {commit_hash[:8]}")
    if link.requirements:
        print(f"   需求: {', '.join(link.requirements)}")
    else:
        print("   (未发现关联的需求ID)")


def cmd_test(project_path, args, mode):
    """Parse test results"""
    test_parser = TestResultsParser(project_path)
    audit = AuditLogger(project_path)

    if args.get("--results"):
        results_path = Path(args["--results"])
        if results_path.is_dir():
            results = test_parser.parse_directory(results_path)
        else:
            results = test_parser.parse_junit_xml(results_path)

        print(f"解析测试结果: {results_path}")
        print(f"发现测试: {len(results)} 个")

        passed = len([r for r in results if r.status == "pass"])
        failed = len([r for r in results if r.status == "fail"])

        print(f"通过: {passed}, 失败: {failed}")

        # Add to database
        for result in results:
            test_parser.requirements_db.setdefault("test_results", []).append(
                result.__dict__
            )
            audit.log_test_result_added(result.test_id, result.status, mode)

        test_parser._save_test_results()

    elif args.get("--case"):
        test_id = args["--case"]
        status = args.get("--result", "pass")
        test_type = args.get("--type", "OQ")

        result = test_parser.add_manual_result(
            test_id=test_id, test_name=test_id, status=status, test_type=test_type
        )

        audit.log_test_result_added(result.test_id, result.status, mode)

        print(f"✅ 已添加测试结果: {test_id} -> {status}")


def cmd_risk(project_path, args, mode):
    """Run risk analysis"""
    parser = RequirementsParser(project_path)
    risk_analyzer = RiskAnalyzer(project_path)
    audit = AuditLogger(project_path)

    requirements = parser.requirements_db.get("requirements", [])

    if not requirements:
        print("没有需求，跳过风险分析")
        return 0

    print(f"分析 {len(requirements)} 个需求...")

    risks = risk_analyzer.analyze_all()

    # Save risks
    risk_analyzer.requirements_db["risks"] = [r.__dict__ for r in risks]
    risk_analyzer._save_risks()

    # Log to audit
    for risk in risks:
        audit.log_risk_assessed(risk.id, risk.rpn, risk.risk_level, mode)

    print(f"✅ 生成 {len(risks)} 个风险项")

    # Show summary
    summary = risk_analyzer.get_risk_summary()
    print(f"\n风险分布:")
    for level, count in summary.get("by_level", {}).items():
        print(f"   {level}: {count}")

    high_risks = [r for r in risks if r.risk_level in ["high", "critical"]]
    if high_risks:
        print(f"\n🔴 高风险 ({len(high_risks)}):")
        for r in high_risks[:5]:
            print(f"   - {r.id}: RPN={r.rpn}, {r.risk_description[:40]}...")


def cmd_generate(project_path, args, mode):
    """Generate document"""
    doc_type = args.get("<doc>")

    if not doc_type:
        print("错误: 请指定文档类型 (vp/urs/fs/iq/oq/pq/ra/vsr)")
        return 1

    valid_docs = ["vp", "urs", "fs", "ts", "iq", "oq", "pq", "ra", "vsr"]
    if doc_type not in valid_docs:
        print(f"错误: 无效文档类型 '{doc_type}'")
        return 1

    # Import and run generator
    from word_generator import WordGenerator

    filler = DocumentFiller(project_path)
    variables = filler.get_variables(doc_type)

    # Check completeness
    completeness = filler.validate_completeness(doc_type)
    if not completeness["complete"]:
        print("\n⚠️  文档完整性检查:")
        for issue in completeness["issues"]:
            print(f"   - {issue}")
    if completeness["warnings"]:
        print("\n⚠️  警告:")
        for warning in completeness["warnings"]:
            print(f"   - {warning}")

    # Load template
    template_path = project_path / "templates" / f"{doc_type}.md"
    if not template_path.exists():
        print(f"错误: 模板不存在 {template_path}")
        return 1

    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace variables
    for key, value in variables.items():
        content = content.replace(key, value)

    # Generate document
    generator = WordGenerator(project_path / "output")
    output_path = generator.generate(doc_type, doc_type, variables)

    print(f"\n✅ 已生成文档: {output_path}")

    # Log to audit
    audit = AuditLogger(project_path)
    audit.log_document_generated(doc_type, True, mode)


def cmd_audit(project_path, args):
    """Show or export audit log"""
    audit = AuditLogger(project_path)

    if args.get("--export"):
        output_path = Path(args["--export"])
        exported_path = audit.export_to_pdf(output_path)
        print(f"✅ 已导出审计日志: {exported_path}")
    else:
        summary = audit.get_summary()
        print("\n📋 审计日志摘要:")
        print(f"   总条目: {summary['total_entries']}")
        print(f"   按操作: {json.dumps(summary['by_action'], ensure_ascii=False)}")
        print(f"   按模式: {json.dumps(summary['by_mode'], ensure_ascii=False)}")
        print(f"   首次: {summary['first_entry']}")
        print(f"   最近: {summary['last_entry']}")


def main():
    """Main CLI entry point"""
    print_banner()

    args = sys.argv[1:]

    if not args or args[0] in ["--help", "-h"]:
        print(__doc__)
        return 0

    project_path = Path.cwd()

    # Detect agent mode
    agent_info = get_agent_mode(project_path)
    mode = agent_info.mode

    # Check for explicit mode override
    if "--mode" in args:
        idx = args.index("--mode")
        if idx + 1 < len(args):
            mode = args[idx + 1]
            args = args[:idx] + args[idx + 2 :]

    # Parse command
    cmd = args[0] if args else "help"

    # Command routing
    if cmd == "init":
        cmd_init(project_path)

    elif cmd == "agent":
        parsed = {}
        if "--set" in args:
            idx = args.index("--set")
            parsed["set"] = args[idx + 1] if idx + 1 < len(args) else None
        cmd_agent(project_path, parsed)

    elif cmd == "parse":
        filtered_args = [a for a in args if a not in ("--auto-add", "--yes")]
        path = filtered_args[1] if len(filtered_args) > 1 else "./src"
        parsed = {"<path>": path}
        if "--auto-add" in args or "--yes" in args:
            parsed["--auto-add"] = True
        cmd_parse(project_path, parsed, mode)

    elif cmd == "status":
        cmd_status(project_path)

    elif cmd == "add":
        description = " ".join(args[1:]) if len(args) > 1 else ""
        parsed = {"<description>": description}
        if "--type" in args:
            idx = args.index("--type")
            parsed["--type"] = args[idx + 1]
        if "--priority" in args:
            idx = args.index("--priority")
            parsed["--priority"] = args[idx + 1]
        cmd_add(project_path, parsed, mode)

    elif cmd == "link":
        parsed = {}
        if "--commit" in args:
            idx = args.index("--commit")
            parsed["--commit"] = args[idx + 1]
        cmd_link(project_path, parsed, mode)

    elif cmd == "test":
        parsed = {}
        if "--results" in args:
            idx = args.index("--results")
            parsed["--results"] = args[idx + 1]
        if "--case" in args:
            idx = args.index("--case")
            parsed["--case"] = args[idx + 1]
        if "--result" in args:
            idx = args.index("--result")
            parsed["--result"] = args[idx + 1]
        if "--type" in args:
            idx = args.index("--type")
            parsed["--type"] = args[idx + 1]
        cmd_test(project_path, parsed, mode)

    elif cmd == "risk":
        cmd_risk(project_path, {}, mode)

    elif cmd == "generate":
        doc = args[1] if len(args) > 1 else None
        cmd_generate(project_path, {"<doc>": doc}, mode)

    elif cmd == "audit":
        parsed = {}
        if "--export" in args:
            idx = args.index("--export")
            parsed["--export"] = args[idx + 1]
        cmd_audit(project_path, parsed)

    else:
        print(f"未知命令: {cmd}")
        print(__doc__)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
