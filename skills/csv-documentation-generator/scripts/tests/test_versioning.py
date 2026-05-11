"""Tests for template versioning"""

import unittest
import json
import tempfile
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from requirements.versioning import (
    TEMPLATE_VERSION,
    VersionInfo,
    CompatibilityResult,
    get_template_version,
    set_template_version,
    check_template_compatibility,
    migrate_template_if_needed,
    detect_template_version_from_file,
    load_requirements_with_version,
)


class TestVersionInfo(unittest.TestCase):
    """Test VersionInfo class"""

    def test_from_string(self):
        """Test creating VersionInfo from string"""
        v = VersionInfo.from_string("1.2.3")
        self.assertEqual(v.major, 1)
        self.assertEqual(v.minor, 2)
        self.assertEqual(v.patch, 3)

    def test_from_string_partial(self):
        """Test creating VersionInfo with partial version"""
        v = VersionInfo.from_string("1.2")
        self.assertEqual(v.major, 1)
        self.assertEqual(v.minor, 2)
        self.assertEqual(v.patch, 0)

    def test_str_representation(self):
        """Test string representation"""
        v = VersionInfo.from_string("1.2.3")
        self.assertEqual(str(v), "1.2.3")

    def test_comparison_greater(self):
        """Test greater than comparison"""
        v1 = VersionInfo.from_string("2.0.0")
        v2 = VersionInfo.from_string("1.9.9")
        self.assertTrue(v1 > v2)

    def test_comparison_equal(self):
        """Test equal comparison"""
        v1 = VersionInfo.from_string("1.2.3")
        v2 = VersionInfo.from_string("1.2.3")
        self.assertTrue(v1 == v2)

    def test_comparison_greater_equal(self):
        """Test greater than or equal comparison"""
        v1 = VersionInfo.from_string("1.2.3")
        v2 = VersionInfo.from_string("1.2.3")
        v3 = VersionInfo.from_string("1.2.2")
        self.assertTrue(v1 >= v2)
        self.assertTrue(v1 >= v3)

    def test_comparison_less(self):
        """Test less than comparison"""
        v1 = VersionInfo.from_string("1.0.0")
        v2 = VersionInfo.from_string("1.0.1")
        self.assertTrue(v1 < v2)


class TestGetSetTemplateVersion(unittest.TestCase):
    """Test get/set template version functions"""

    def test_get_template_version_exists(self):
        """Test getting existing template version"""
        db = {"template_version": "1.1.0"}
        version = get_template_version(db)
        self.assertEqual(version, "1.1.0")

    def test_get_template_version_fallback(self):
        """Test getting version from fallback field"""
        db = {"version": "1.0.0"}
        version = get_template_version(db)
        self.assertEqual(version, "1.0.0")

    def test_get_template_version_none(self):
        """Test getting version when none exists"""
        db = {}
        version = get_template_version(db)
        self.assertIsNone(version)

    def test_set_template_version(self):
        """Test setting template version"""
        db = {}
        updated = set_template_version(db, "1.2.0")
        self.assertEqual(updated["template_version"], "1.2.0")


class TestCheckCompatibility(unittest.TestCase):
    """Test template compatibility checking"""

    def test_compatible_current_version(self):
        """Test compatible when using current version"""
        db = {"template_version": TEMPLATE_VERSION}
        result = check_template_compatibility(db)

        self.assertTrue(result.compatible)

    def test_compatible_no_version(self):
        """Test compatible when no version specified"""
        db = {}
        result = check_template_compatibility(db)

        self.assertTrue(result.compatible)
        self.assertIn("assuming compatible", result.message)

    def test_incompatible_future_version(self):
        """Test incompatible when template requires newer generator"""
        db = {"template_version": "99.0.0"}
        result = check_template_compatibility(db)

        self.assertFalse(result.compatible)
        self.assertIsNotNone(result.required_version)


class TestMigration(unittest.TestCase):
    """Test template migration"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_migrate_no_version(self):
        """Test migration from no version"""
        db = {"requirements": []}
        updated, was_migrated = migrate_template_if_needed(db)

        self.assertTrue(was_migrated)
        self.assertEqual(get_template_version(updated), TEMPLATE_VERSION)

    def test_migrate_same_version(self):
        """Test migration when already at current version"""
        db = {"template_version": TEMPLATE_VERSION, "requirements": []}
        updated, was_migrated = migrate_template_if_needed(db)

        self.assertFalse(was_migrated)

    def test_migrate_adds_risk_level(self):
        """Test migration adds risk_level to requirements"""
        db = {
            "template_version": "1.0.0",
            "requirements": [{"id": "URS-001", "description": "Test"}],
        }
        updated, was_migrated = migrate_template_if_needed(db)

        self.assertTrue(was_migrated)
        self.assertEqual(updated["requirements"][0].get("risk_level"), None)


class TestDetectTemplateVersion(unittest.TestCase):
    """Test template version detection from file"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.template_path = Path(self.temp_dir) / "test_template.md"

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_detect_from_comment(self):
        """Test detecting version from HTML comment"""
        content = """# Test Template
<!-- template-version: 1.2.0 -->
Some content here
"""
        with open(self.template_path, "w") as f:
            f.write(content)

        version = detect_template_version_from_file(self.template_path)
        self.assertEqual(version, "1.2.0")

    def test_detect_from_jinja(self):
        """Test detecting version from Jinja variable"""
        content = """# Test Template
{% set template_version = "1.1.0" %}
Some content here
"""
        with open(self.template_path, "w") as f:
            f.write(content)

        version = detect_template_version_from_file(self.template_path)
        self.assertEqual(version, "1.1.0")

    def test_detect_not_found(self):
        """Test when no version found"""
        content = """# Test Template
Some content here
"""
        with open(self.template_path, "w") as f:
            f.write(content)

        version = detect_template_version_from_file(self.template_path)
        self.assertIsNone(version)

    def test_detect_nonexistent_file(self):
        """Test detection on non-existent file"""
        version = detect_template_version_from_file(Path("/nonexistent/file.md"))
        self.assertIsNone(version)


class TestLoadRequirementsWithVersion(unittest.TestCase):
    """Test loading requirements with version checking"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.req_path = Path(self.temp_dir) / "requirements.json"

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_load_valid(self):
        """Test loading valid requirements"""
        db = {"template_version": TEMPLATE_VERSION, "requirements": []}
        with open(self.req_path, "w") as f:
            json.dump(db, f)

        loaded, compatibility = load_requirements_with_version(self.req_path)
        self.assertTrue(compatibility.compatible)

    def test_load_invalid_json(self):
        """Test loading invalid JSON"""
        with open(self.req_path, "w") as f:
            f.write("invalid json")

        loaded, compatibility = load_requirements_with_version(self.req_path)
        self.assertFalse(compatibility.compatible)
        self.assertIn("Failed to parse", compatibility.message)


if __name__ == "__main__":
    unittest.main()
