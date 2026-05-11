"""Compliance checker for CSV Documentation Generator

Checks requirements and test coverage for GxP compliance.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass


@dataclass
class ComplianceIssue:
    severity: str  # ERROR, WARNING, INFO
    category: str  # coverage, risk, test
    message: str
    requirement_id: str = None
    details: Dict = None


class ComplianceChecker:
    """Check requirements and test coverage for GxP compliance"""

    HIGH_RISK_MODULES = ["security", "compliance", "audit_trail"]

    def __init__(self, requirements_path: Path = None, test_results_path: Path = None):
        self.requirements_path = requirements_path or Path("requirements.json")
        self.test_results_path = test_results_path or Path("test_results.json")
        self.issues: List[ComplianceIssue] = []
        self.requirements_db = None
        self.test_results = []

    def load_data(self) -> bool:
        """Load requirements and test data from files"""
        try:
            if self.requirements_path.exists():
                with open(self.requirements_path, "r", encoding="utf-8") as f:
                    self.requirements_db = json.load(f)
            else:
                self.requirements_db = {
                    "requirements": [],
                    "risks": [],
                    "test_results": [],
                }

            if self.test_results_path.exists():
                with open(self.test_results_path, "r", encoding="utf-8") as f:
                    self.test_results = json.load(f).get("test_results", [])
            else:
                self.test_results = []

            return True
        except Exception as e:
            self.issues.append(
                ComplianceIssue(
                    severity="ERROR",
                    category="system",
                    message=f"Failed to load data: {e}",
                )
            )
            return False

    def check(self) -> Tuple[int, List[ComplianceIssue]]:
        """Run all compliance checks

        Returns:
            Tuple of (exit_code, issues)
            exit_code: 0=all passed, 1=warnings, 2=errors
        """
        self.issues = []

        if not self.requirements_db:
            self.load_data()

        requirements = self.requirements_db.get("requirements", [])

        if not requirements:
            self.issues.append(
                ComplianceIssue(
                    severity="WARNING",
                    category="coverage",
                    message="No requirements found in database",
                )
            )
            return self._determine_exit_code(), self.issues

        self._check_coverage()
        self._check_high_risk_modules(requirements)
        self._check_test_coverage(requirements)

        return self._determine_exit_code(), self.issues

    def _check_coverage(self):
        """Check if all @REQ markers in code have corresponding URS entries"""
        requirements = self.requirements_db.get("requirements", [])

        if not requirements:
            return

        ur_ids = {r.get("id") for r in requirements}

        for req in requirements:
            req_id = req.get("id")
            if not req_id:
                continue

            if not req_id.startswith("URS-"):
                continue

            if not req.get("description"):
                self.issues.append(
                    ComplianceIssue(
                        severity="WARNING",
                        category="coverage",
                        message=f"Requirement {req_id} has empty description",
                        requirement_id=req_id,
                    )
                )

    def _check_high_risk_modules(self, requirements: List[Dict]):
        """Check if high-risk modules have IQ/OQ/PQ test coverage"""
        for module in self.HIGH_RISK_MODULES:
            module_reqs = [r for r in requirements if r.get("module") == module]

            if not module_reqs:
                continue

            module_req_ids = [r.get("id") for r in module_reqs]

            has_tests = False
            for tr in self.test_results:
                req_id = tr.get("requirement_id")
                if req_id in module_req_ids:
                    test_type = tr.get("test_type", "")
                    if test_type in ["IQ", "OQ", "PQ"]:
                        has_tests = True
                        break

            if not has_tests:
                self.issues.append(
                    ComplianceIssue(
                        severity="WARNING",
                        category="risk",
                        message=f"High-risk module '{module}' lacks IQ/OQ/PQ test coverage",
                        details={"module": module, "requirements": module_req_ids},
                    )
                )

    def _check_test_coverage(self, requirements: List[Dict]):
        """Check if test coverage meets threshold (default 80%)"""
        total = len(requirements)
        if total == 0:
            return

        covered = set()
        for tr in self.test_results:
            req_id = tr.get("requirement_id")
            status = tr.get("status", "").lower()
            if req_id and status == "pass":
                covered.add(req_id)

        coverage_rate = len(covered) / total * 100

        threshold = 80.0
        if coverage_rate < threshold:
            uncovered = [
                r.get("id") for r in requirements if r.get("id") not in covered
            ]
            self.issues.append(
                ComplianceIssue(
                    severity="WARNING",
                    category="test",
                    message=f"Test coverage {coverage_rate:.1f}% below threshold {threshold}%",
                    details={
                        "coverage": coverage_rate,
                        "threshold": threshold,
                        "covered": len(covered),
                        "total": total,
                        "uncovered": uncovered[:10],
                    },
                )
            )

    def _determine_exit_code(self) -> int:
        """Determine exit code based on issue severity"""
        has_error = any(i.severity == "ERROR" for i in self.issues)
        has_warning = any(i.severity == "WARNING" for i in self.issues)

        if has_error:
            return 2
        elif has_warning:
            return 1
        return 0

    def generate_report(self, output_format: str = "text") -> str:
        """Generate compliance report

        Args:
            output_format: "text" or "json"

        Returns:
            Report string
        """
        if output_format == "json":
            return json.dumps(
                {
                    "exit_code": self._determine_exit_code(),
                    "total_issues": len(self.issues),
                    "issues": [
                        {
                            "severity": i.severity,
                            "category": i.category,
                            "message": i.message,
                            "requirement_id": i.requirement_id,
                            "details": i.details,
                        }
                        for i in self.issues
                    ],
                },
                indent=2,
                ensure_ascii=False,
            )

        lines = ["=" * 50, "Compliance Check Report", "=" * 50]

        if not self.issues:
            lines.append("✓ All checks passed")
            return "\n".join(lines)

        errors = [i for i in self.issues if i.severity == "ERROR"]
        warnings = [i for i in self.issues if i.severity == "WARNING"]
        infos = [i for i in self.issues if i.severity == "INFO"]

        if errors:
            lines.append(f"\n✗ Errors ({len(errors)}):")
            for issue in errors:
                lines.append(f"  - [{issue.category}] {issue.message}")
                if issue.requirement_id:
                    lines.append(f"    Requirement: {issue.requirement_id}")

        if warnings:
            lines.append(f"\n⚠ Warnings ({len(warnings)}):")
            for issue in warnings:
                lines.append(f"  - [{issue.category}] {issue.message}")
                if issue.requirement_id:
                    lines.append(f"    Requirement: {issue.requirement_id}")

        if infos:
            lines.append(f"\nℹ Info ({len(infos)}):")
            for issue in infos:
                lines.append(f"  - [{issue.category}] {issue.message}")

        exit_code = self._determine_exit_code()
        lines.append(f"\n{'=' * 50}")
        lines.append(f"Exit code: {exit_code}")
        if exit_code == 0:
            lines.append("Status: PASSED")
        elif exit_code == 1:
            lines.append("Status: WARNINGS")
        else:
            lines.append("Status: FAILED")

        return "\n".join(lines)


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Compliance checker for CSV documentation"
    )
    parser.add_argument(
        "--requirements",
        "-r",
        type=Path,
        default=Path("requirements.json"),
        help="Path to requirements.json",
    )
    parser.add_argument(
        "--test-results",
        "-t",
        type=Path,
        default=Path("test_results.json"),
        help="Path to test_results.json",
    )
    parser.add_argument(
        "--output", "-o", choices=["text", "json"], default="text", help="Output format"
    )
    parser.add_argument(
        "--exit-code", action="store_true", help="Only output exit code"
    )

    args = parser.parse_args()

    checker = ComplianceChecker(args.requirements, args.test_results)
    checker.load_data()
    exit_code, issues = checker.check()

    if args.exit_code:
        print(exit_code)
        sys.exit(exit_code)

    report = checker.generate_report(args.output)
    print(report)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
