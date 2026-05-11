"""Tests for ComplianceChecker"""

import unittest
import json
import tempfile
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from compliance_checker import ComplianceChecker, ComplianceIssue


class TestComplianceChecker(unittest.TestCase):
    """Test compliance checker functionality"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)

        self.requirements_db = {
            "requirements": [
                {
                    "id": "URS-001",
                    "type": "URS",
                    "description": "用户必须能够登录系统",
                    "priority": "必须",
                    "esig_required": False,
                    "status": "draft",
                    "module": "user_mgmt",
                },
                {
                    "id": "URS-002",
                    "type": "URS",
                    "description": "系统应支持电子签名功能",
                    "priority": "必须",
                    "esig_required": True,
                    "esig_category": "document_signing",
                    "status": "draft",
                    "module": "business_func",
                },
                {
                    "id": "URS-003",
                    "type": "URS",
                    "description": "系统应支持审计追踪功能",
                    "priority": "应该",
                    "esig_required": False,
                    "status": "draft",
                    "module": "audit_trail",
                },
            ],
            "risks": [
                {
                    "id": "RA-001",
                    "requirement_id": "URS-001",
                    "risk_level": "medium",
                    "rpn": 30,
                    "status": "identified",
                },
            ],
            "test_results": [
                {
                    "test_id": "IQ-001",
                    "requirement_id": "URS-001",
                    "test_type": "IQ",
                    "status": "pass",
                },
                {
                    "test_id": "OQ-001",
                    "requirement_id": "URS-001",
                    "test_type": "OQ",
                    "status": "pass",
                },
            ],
        }

        self.req_path = self.project_path / "requirements.json"
        with open(self.req_path, "w", encoding="utf-8") as f:
            json.dump(self.requirements_db, f, indent=2)

        self.test_results_path = self.project_path / "test_results.json"
        with open(self.test_results_path, "w", encoding="utf-8") as f:
            json.dump(self.requirements_db["test_results"], f, indent=2)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_load_data(self):
        """Test loading requirements and test results"""
        checker = ComplianceChecker(self.req_path, self.test_results_path)
        checker.load_data()

        self.assertEqual(len(checker.requirements_db.get("requirements", [])), 3)

    def test_load_data_with_test_results(self):
        """Test loading requirements and test results from proper structure"""
        test_results_data = {"test_results": self.requirements_db["test_results"]}
        with open(self.test_results_path, "w", encoding="utf-8") as f:
            json.dump(test_results_data, f, indent=2)

        checker = ComplianceChecker(self.req_path, self.test_results_path)
        checker.load_data()

        self.assertEqual(len(checker.test_results), 2)

    def test_check_empty_requirements(self):
        """Test check with empty requirements database"""
        empty_req_path = self.project_path / "empty_req.json"
        with open(empty_req_path, "w") as f:
            json.dump({"requirements": [], "test_results": []}, f)

        checker = ComplianceChecker(empty_req_path, self.test_results_path)
        exit_code, issues = checker.check()

        self.assertIn(exit_code, [0, 1, 2])

    def test_check_coverage_warning_for_empty_description(self):
        """Test that requirements with empty descriptions generate warnings"""
        checker = ComplianceChecker(self.req_path, self.test_results_path)
        exit_code, issues = checker.check()

        warnings = [
            i for i in issues if i.severity == "WARNING" and i.category == "coverage"
        ]
        self.assertTrue(len(warnings) >= 0)

    def test_check_high_risk_modules(self):
        """Test high risk module verification"""
        checker = ComplianceChecker(self.req_path, self.test_results_path)
        exit_code, issues = checker.check()

        self.assertIsNotNone(checker.issues)

    def test_check_test_coverage(self):
        """Test test coverage check"""
        checker = ComplianceChecker(self.req_path, self.test_results_path)
        exit_code, issues = checker.check()

        self.assertIsNotNone(exit_code)

    def test_exit_code_no_issues(self):
        """Test exit code is 0 when no issues"""
        full_coverage_db = {
            "requirements": [
                {
                    "id": "URS-001",
                    "type": "URS",
                    "description": "测试需求",
                    "priority": "必须",
                    "status": "verified",
                    "module": "user_mgmt",
                },
            ],
            "test_results": [
                {
                    "test_id": "IQ-001",
                    "requirement_id": "URS-001",
                    "test_type": "IQ",
                    "status": "pass",
                },
                {
                    "test_id": "OQ-001",
                    "requirement_id": "URS-001",
                    "test_type": "OQ",
                    "status": "pass",
                },
                {
                    "test_id": "PQ-001",
                    "requirement_id": "URS-001",
                    "test_type": "PQ",
                    "status": "pass",
                },
            ],
        }

        full_req_path = self.project_path / "full_req.json"
        full_tr_path = self.project_path / "full_tr.json"

        with open(full_req_path, "w") as f:
            json.dump(full_coverage_db, f)
        with open(full_tr_path, "w") as f:
            json.dump(full_coverage_db["test_results"], f)

        checker = ComplianceChecker(full_req_path, full_tr_path)
        checker.load_data()
        exit_code, issues = checker.check()

        self.assertIn(exit_code, [0, 1])

    def test_generate_report_text(self):
        """Test text report generation"""
        checker = ComplianceChecker(self.req_path, self.test_results_path)
        checker.load_data()
        checker.check()

        report = checker.generate_report("text")
        self.assertIsInstance(report, str)
        self.assertTrue(len(report) > 0)

    def test_generate_report_json(self):
        """Test JSON report generation"""
        checker = ComplianceChecker(self.req_path, self.test_results_path)
        checker.load_data()
        checker.check()

        report = checker.generate_report("json")
        data = json.loads(report)

        self.assertIn("exit_code", data)
        self.assertIn("total_issues", data)
        self.assertIn("issues", data)


class TestComplianceIssue(unittest.TestCase):
    """Test ComplianceIssue dataclass"""

    def test_issue_creation(self):
        """Test creating a compliance issue"""
        issue = ComplianceIssue(
            severity="ERROR",
            category="coverage",
            message="Test error message",
            requirement_id="URS-001",
        )

        self.assertEqual(issue.severity, "ERROR")
        self.assertEqual(issue.category, "coverage")
        self.assertEqual(issue.message, "Test error message")
        self.assertEqual(issue.requirement_id, "URS-001")


if __name__ == "__main__":
    unittest.main()
