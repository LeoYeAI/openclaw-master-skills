"""Document filler module for CSV Documentation Generator

Automatically fills template variables from requirements database.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class DocumentFiller:
    """Fill template variables from requirements database"""

    def __init__(self, project_path: Optional[Path] = None):
        self.project_path = project_path or Path.cwd()
        self.requirements_db = self._load_requirements_db()
        self.config = self._load_config()

    def _load_requirements_db(self) -> Dict[str, Any]:
        """Load requirements database"""
        db_path = self.project_path / "requirements.json"
        if db_path.exists():
            with open(db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"requirements": [], "risks": [], "test_results": [], "commit_links": []}

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        config_path = self.project_path / ".csv-docs-config.json"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def get_variables(self, doc_type: str) -> Dict[str, str]:
        """Generate variables for a document type"""
        variables = {}

        # Metadata
        variables["{DATE}"] = datetime.now().strftime("%Y-%m-%d")
        variables["{VERSION}"] = "1.0"
        variables["{DOC_ID}"] = f"{doc_type.upper()}-001"
        variables["{AUTHOR}"] = self.requirements_db.get("metadata", {}).get(
            "author", "TBD"
        )
        variables["{REVIEWER}"] = self.requirements_db.get("metadata", {}).get(
            "reviewer", "TBD"
        )
        variables["{APPROVER}"] = self.requirements_db.get("metadata", {}).get(
            "approver", "TBD"
        )
        variables["{PROJECT_NAME}"] = self.requirements_db.get("metadata", {}).get(
            "project", "TBD"
        )
        variables["{SYSTEM_NAME}"] = self.requirements_db.get("metadata", {}).get(
            "system", "TBD"
        )
        variables["{SYSTEM_VERSION}"] = self.requirements_db.get("metadata", {}).get(
            "version", "1.0"
        )

        # GAMP category
        gamp_category = (
            self.requirements_db.get("gamp_category")
            or self.config.get("compliance", {}).get("gamp_category")
            or 4
        )
        variables["{GAMP_CATEGORY}"] = str(gamp_category)

        # Requirements statistics
        requirements = self.requirements_db.get("requirements", [])
        risks = self.requirements_db.get("risks", [])
        test_results = self.requirements_db.get("test_results", [])

        variables["{TOTAL_REQUIREMENTS}"] = str(len(requirements))
        variables["{VERIFIED_REQUIREMENTS}"] = str(
            len([r for r in requirements if r.get("status") == "verified"])
        )
        variables["{ESIG_REQUIREMENTS}"] = str(
            len([r for r in requirements if r.get("esig_required")])
        )
        variables["{TOTAL_RISKS}"] = str(len(risks))
        variables["{HIGH_RISKS}"] = str(
            len([r for r in risks if r.get("risk_level") in ["high", "critical"]])
        )
        variables["{TOTAL_TESTS}"] = str(len(test_results))
        variables["{PASSED_TESTS}"] = str(
            len([t for t in test_results if t.get("status") == "pass"])
        )

        # Test results by type
        iq_tests = [t for t in test_results if t.get("test_type") == "IQ"]
        oq_tests = [t for t in test_results if t.get("test_type") == "OQ"]
        pq_tests = [t for t in test_results if t.get("test_type") == "PQ"]

        variables["{IQ_TOTAL}"] = str(len(iq_tests))
        variables["{IQ_PASSED}"] = str(
            len([t for t in iq_tests if t.get("status") == "pass"])
        )
        variables["{OQ_TOTAL}"] = str(len(oq_tests))
        variables["{OQ_PASSED}"] = str(
            len([t for t in oq_tests if t.get("status") == "pass"])
        )
        variables["{PQ_TOTAL}"] = str(len(pq_tests))
        variables["{PQ_PASSED}"] = str(
            len([t for t in pq_tests if t.get("status") == "pass"])
        )

        return variables

    def get_requirement_table(self, doc_type: str = None) -> str:
        """Generate markdown table of requirements"""
        requirements = self.requirements_db.get("requirements", [])

        if doc_type:
            requirements = [r for r in requirements if r.get("type") == doc_type]

        lines = [
            "| ID | 类型 | 描述 | 优先级 | eSig | 状态 |",
            "|----|------|------|--------|------|------|",
        ]

        for r in requirements:
            esig = "是" if r.get("esig_required") else "否"
            lines.append(
                f"| {r.get('id')} | {r.get('type')} | "
                f"{r.get('description', '')[:50]}... | "
                f"{r.get('priority')} | {esig} | "
                f"{r.get('status')} |"
            )

        return "\n".join(lines)

    def get_risk_table(self) -> str:
        """Generate markdown table of risks"""
        risks = self.requirements_db.get("risks", [])

        lines = [
            "| ID | 风险描述 | 严重性 | 可能性 | 可检测性 | RPN | 等级 | 状态 |",
            "|----|----------|--------|--------|----------|-----|------|------|",
        ]

        for r in risks:
            lines.append(
                f"| {r.get('id')} | {r.get('risk_description', '')[:40]}... | "
                f"{r.get('severity')} | {r.get('likelihood')} | {r.get('detectability')} | "
                f"{r.get('rpn')} | {r.get('risk_level')} | {r.get('status')} |"
            )

        return "\n".join(lines)

    def get_test_results_table(self, test_type: str = None) -> str:
        """Generate markdown table of test results"""
        test_results = self.requirements_db.get("test_results", [])

        if test_type:
            test_results = [t for t in test_results if t.get("test_type") == test_type]

        lines = [
            "| 测试ID | 测试名称 | 类型 | 状态 | 执行时间 |",
            "|--------|----------|------|------|----------|",
        ]

        for t in test_results:
            duration = f"{t.get('duration', 0):.2f}s" if t.get("duration") else "N/A"
            lines.append(
                f"| {t.get('test_id')} | {t.get('test_name', '')[:30]}... | "
                f"{t.get('test_type')} | {t.get('status')} | {duration} |"
            )

        return "\n".join(lines)

    def get_summary_statistics(self) -> Dict[str, Any]:
        """Get summary statistics for documents"""
        requirements = self.requirements_db.get("requirements", [])
        risks = self.requirements_db.get("risks", [])
        test_results = self.requirements_db.get("test_results", [])

        return {
            "requirements": {
                "total": len(requirements),
                "by_type": self._count_by(requirements, "type"),
                "by_priority": self._count_by(requirements, "priority"),
                "by_status": self._count_by(requirements, "status"),
                "esig_count": len([r for r in requirements if r.get("esig_required")]),
            },
            "risks": {
                "total": len(risks),
                "by_level": self._count_by(risks, "risk_level"),
                "by_status": self._count_by(risks, "status"),
            },
            "tests": {
                "total": len(test_results),
                "by_type": self._count_by(test_results, "test_type"),
                "by_status": self._count_by(test_results, "status"),
            },
        }

    def _count_by(self, items: list, key: str) -> Dict[str, int]:
        """Count items by a specific key"""
        counts = {}
        for item in items:
            value = item.get(key, "unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts

    def validate_completeness(self, doc_type: str) -> Dict[str, Any]:
        """Check document completeness"""
        requirements = self.requirements_db.get("requirements", [])
        test_results = self.requirements_db.get("test_results", [])

        issues = []
        warnings = []

        # Check if requirements exist
        if len(requirements) == 0:
            issues.append("没有需求数据，请先添加或解析需求")

        # Check if requirements are linked to tests
        req_ids = {r.get("id") for r in requirements}
        tested_req_ids = {
            t.get("requirement_id") for t in test_results if t.get("requirement_id")
        }

        untested = req_ids - tested_req_ids
        if untested:
            warnings.append(f"以下需求未关联测试: {', '.join(list(untested)[:5])}")

        # Check risk assessment
        risks = self.requirements_db.get("risks", [])
        if len(risks) == 0 and len(requirements) > 0:
            warnings.append("没有风险评估数据，请运行风险分析")

        return {"complete": len(issues) == 0, "issues": issues, "warnings": warnings}
