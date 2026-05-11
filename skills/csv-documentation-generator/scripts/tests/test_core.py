"""Tests for CSV Documentation Generator"""

import unittest
import json
import tempfile
import shutil
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent import AgentDetector
from requirements.parser import RequirementsParser
from requirements.risk_analyzer import RiskAnalyzer
from audit.log import AuditLogger
from fill.filler import DocumentFiller


class TestAgentDetector(unittest.TestCase):
    """Test agent detection functionality"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_default_mode_is_interactive(self):
        """Test that default mode is interactive when no config exists"""
        detector = AgentDetector(self.project_path)
        info = detector.detect()

        self.assertEqual(info.mode, "interactive")

    def test_config_mode(self):
        """Test reading mode from config"""
        config = {"agent": {"default_mode": "autonomous", "auto_detect": False}}

        config_path = self.project_path / ".csv-docs-config.json"
        with open(config_path, "w") as f:
            json.dump(config, f)

        detector = AgentDetector(self.project_path)
        info = detector.detect()

        self.assertEqual(info.mode, "autonomous")
        self.assertIn(info.source, ["project_config", "config (auto_detect=false)"])


class TestRequirementsParser(unittest.TestCase):
    """Test requirements parser"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)

        # Create empty requirements db
        req_db = {
            "requirements": [],
            "risks": [],
            "test_results": [],
            "commit_links": [],
        }
        req_path = self.project_path / "requirements.json"
        with open(req_path, "w") as f:
            json.dump(req_db, f)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_add_requirement(self):
        """Test adding a requirement"""
        parser = RequirementsParser(self.project_path)

        req = parser.add_requirement(
            description="用户必须能够登录系统", req_type="URS", priority="必须"
        )

        self.assertEqual(req.type, "URS")
        self.assertEqual(req.priority, "必须")
        self.assertTrue(req.id.startswith("URS-"))

    def test_esig_detection(self):
        """Test electronic signature detection"""
        parser = RequirementsParser(self.project_path)

        req = parser.add_requirement(
            description="系统应支持电子签名审核功能", req_type="URS"
        )

        self.assertTrue(req.esig_required)

    def test_parse_file(self):
        """Test parsing requirements from file"""
        test_file = self.project_path / "test.py"
        with open(test_file, "w") as f:
            f.write("# @REQ URS-001 - 用户登录功能\n")
            f.write("# @REQ URS-002 - 必须的密码验证\n")

        parser = RequirementsParser(self.project_path)
        requirements = parser.parse_file(test_file)

        self.assertEqual(len(requirements), 2)
        self.assertTrue(any("登录" in r.description for r in requirements))


class TestRiskAnalyzer(unittest.TestCase):
    """Test risk analyzer"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)

        # Create requirements db with config
        req_db = {
            "requirements": [
                {
                    "id": "URS-001",
                    "type": "URS",
                    "description": "用户必须能够登录系统",
                    "priority": "必须",
                    "esig_required": False,
                    "status": "draft",
                },
                {
                    "id": "URS-002",
                    "type": "URS",
                    "description": "系统应支持电子签名审核",
                    "priority": "必须",
                    "esig_required": True,
                    "status": "draft",
                },
            ],
            "risks": [],
            "test_results": [],
            "commit_links": [],
        }

        req_path = self.project_path / "requirements.json"
        with open(req_path, "w") as f:
            json.dump(req_db, f)

        config = {
            "compliance": {"gamp_category": 4},
            "risk": {
                "rpn_thresholds": {"low": 25, "medium": 50, "high": 75, "critical": 125}
            },
        }

        config_path = self.project_path / ".csv-docs-config.json"
        with open(config_path, "w") as f:
            json.dump(config, f)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_analyze_requirement(self):
        """Test analyzing a requirement"""
        analyzer = RiskAnalyzer(self.project_path)

        req = analyzer.requirements_db["requirements"][0]
        risk = analyzer.analyze_requirement(req)

        self.assertIsNotNone(risk.rpn)
        self.assertIn(risk.risk_level, ["low", "medium", "high", "critical"])

    def test_esig_higher_severity(self):
        """Test that eSig requirements get higher severity"""
        analyzer = RiskAnalyzer(self.project_path)

        # Normal requirement
        req1 = analyzer.requirements_db["requirements"][0]
        risk1 = analyzer.analyze_requirement(req1)

        # eSig requirement
        req2 = analyzer.requirements_db["requirements"][1]
        risk2 = analyzer.analyze_requirement(req2)

        # eSig should have higher or equal severity
        self.assertGreaterEqual(risk2.severity, risk1.severity)


class TestAuditLogger(unittest.TestCase):
    """Test audit logger"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_log_entry(self):
        """Test adding audit log entry"""
        logger = AuditLogger(self.project_path)

        logger.log(
            action="requirement_added",
            mode="interactive",
            details={"id": "URS-001", "description": "Test"},
        )

        entries = logger.get_entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].action, "requirement_added")

    def test_get_summary(self):
        """Test getting audit summary"""
        logger = AuditLogger(self.project_path)

        logger.log("action1", "interactive")
        logger.log("action2", "autonomous")
        logger.log("action1", "interactive")

        summary = logger.get_summary()

        self.assertEqual(summary["total_entries"], 3)
        self.assertEqual(summary["by_action"]["action1"], 2)
        self.assertEqual(summary["by_mode"]["interactive"], 2)


class TestDocumentFiller(unittest.TestCase):
    """Test document filler"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)

        # Create requirements db
        req_db = {
            "requirements": [
                {
                    "id": "URS-001",
                    "type": "URS",
                    "description": "Test",
                    "priority": "必须",
                    "esig_required": False,
                    "status": "verified",
                },
                {
                    "id": "FS-001",
                    "type": "FS",
                    "description": "Test FS",
                    "priority": "应该",
                    "esig_required": False,
                    "status": "draft",
                },
            ],
            "risks": [
                {
                    "id": "RA-001",
                    "risk_level": "medium",
                    "rpn": 30,
                    "status": "identified",
                }
            ],
            "test_results": [
                {"test_id": "OQ-001", "test_type": "OQ", "status": "pass"}
            ],
            "commit_links": [],
        }

        req_path = self.project_path / "requirements.json"
        with open(req_path, "w") as f:
            json.dump(req_db, f)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_get_variables(self):
        """Test getting variables for document"""
        filler = DocumentFiller(self.project_path)
        variables = filler.get_variables("vp")

        self.assertIn("{DATE}", variables)
        self.assertIn("{GAMP_CATEGORY}", variables)
        self.assertEqual(variables["{TOTAL_REQUIREMENTS}"], "2")

    def test_validate_completeness(self):
        """Test document completeness validation"""
        filler = DocumentFiller(self.project_path)
        result = filler.validate_completeness("urs")

        self.assertTrue(result["complete"])


if __name__ == "__main__":
    unittest.main()
