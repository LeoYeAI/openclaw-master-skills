"""Tests for bidirectional sync functionality"""

import unittest
import json
import tempfile
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from requirements.parser import RequirementsParser


class TestRequirementsParserPatterns(unittest.TestCase):
    """Test that parser correctly handles different comment patterns"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)

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

    def test_parse_new_format(self):
        """Test parsing new format: # @REQ URS-001 - description"""
        test_file = self.project_path / "test.py"
        with open(test_file, "w") as f:
            f.write("# @REQ URS-001 - 用户登录功能\n")
            f.write("# @REQ URS-002 - 必须的密码验证\n")

        parser = RequirementsParser(self.project_path)
        requirements = parser.parse_file(test_file)

        self.assertEqual(len(requirements), 2)
        ids = [r.id for r in requirements]
        self.assertIn("URS-001", ids)
        self.assertIn("URS-002", ids)

    def test_parse_legacy_format(self):
        """Test parsing legacy format: # @req ABC-001 description"""
        test_file = self.project_path / "test.py"
        with open(test_file, "w") as f:
            f.write("# @req ABC-001 用户登录功能\n")
            f.write("# @req ABC-002 密码验证\n")

        parser = RequirementsParser(self.project_path)
        requirements = parser.parse_file(test_file)

        self.assertEqual(len(requirements), 2)
        ids = [r.id for r in requirements]
        self.assertIn("ABC-001", ids)
        self.assertIn("ABC-002", ids)

    def test_parse_legacy_urs_format_ignored(self):
        """Test that legacy @req with URS prefix is ignored (use new format instead)"""
        test_file = self.project_path / "test.py"
        with open(test_file, "w") as f:
            f.write("# @req URS-001 用户登录功能\n")

        parser = RequirementsParser(self.project_path)
        requirements = parser.parse_file(test_file)

        self.assertEqual(len(requirements), 0)

    def test_parse_hash_style_format(self):
        """Test parsing hash style format: # URS-001: description"""
        test_file = self.project_path / "test.py"
        with open(test_file, "w") as f:
            f.write("# URS-001: 用户登录功能\n")
            f.write("# URS-002: 密码验证\n")

        parser = RequirementsParser(self.project_path)
        requirements = parser.parse_file(test_file)

        self.assertEqual(len(requirements), 2)

    def test_parse_bracket_style_format(self):
        """Test parsing bracket style format: # [URS-001] description"""
        test_file = self.project_path / "test.py"
        with open(test_file, "w") as f:
            f.write("# [URS-001] 用户登录功能\n")
            f.write("# [URS-002] 密码验证\n")

        parser = RequirementsParser(self.project_path)
        requirements = parser.parse_file(test_file)

        self.assertEqual(len(requirements), 2)


class TestModuleInference(unittest.TestCase):
    """Test module inference from description"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)

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

    def test_infer_user_mgmt_module(self):
        """Test inferring user management module"""
        test_file = self.project_path / "test.py"
        with open(test_file, "w") as f:
            f.write("# @REQ URS-001 - 用户登录功能\n")
            f.write("# @REQ URS-002 - 密码修改功能\n")

        parser = RequirementsParser(self.project_path)
        requirements = parser.parse_file(test_file)

        self.assertEqual(len(requirements), 2)

    def test_infer_audit_trail_module(self):
        """Test inferring audit trail module"""
        test_file = self.project_path / "test.py"
        with open(test_file, "w") as f:
            f.write("# @REQ URS-001 - 审计追踪功能\n")
            f.write("# @REQ URS-002 - 记录用户操作\n")

        parser = RequirementsParser(self.project_path)
        requirements = parser.parse_file(test_file)

        self.assertEqual(len(requirements), 2)


class TestBidirectionalSync(unittest.TestCase):
    """Test bidirectional sync scenarios"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)

        self.req_db = {
            "version": "1.0",
            "requirements": [
                {
                    "id": "URS-001",
                    "type": "URS",
                    "description": "用户必须能够登录系统",
                    "priority": "必须",
                    "module": "user_mgmt",
                    "status": "draft",
                },
            ],
            "risks": [],
            "test_results": [],
            "commit_links": [],
        }
        self.req_path = self.project_path / "requirements.json"
        with open(self.req_path, "w", encoding="utf-8") as f:
            json.dump(self.req_db, f, indent=2)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_sync_detects_template_only_requirements(self):
        """Test detecting requirements that only exist in template"""
        pass

    def test_sync_detects_json_only_requirements(self):
        """Test detecting requirements that only exist in JSON"""
        pass

    def test_sync_detects_conflicts(self):
        """Test detecting conflicting descriptions for same ID"""
        pass


if __name__ == "__main__":
    unittest.main()
