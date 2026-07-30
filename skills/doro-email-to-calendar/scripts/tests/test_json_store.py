#!/usr/bin/env python3
"""Tests for utils/json_store.py"""

import unittest
import sys
import os
import json
import tempfile
import shutil

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.json_store import load_json, save_json, ensure_dir


class TestEnsureDir(unittest.TestCase):
    """Tests for ensure_dir function."""

    def setUp(self):
        """Create temp directory for test files."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_creates_parent_dirs(self):
        """Test that parent directories are created."""
        filepath = os.path.join(self.temp_dir, "a", "b", "c", "file.json")
        ensure_dir(filepath)
        parent_dir = os.path.dirname(filepath)
        self.assertTrue(os.path.isdir(parent_dir))

    def test_existing_dir_ok(self):
        """Test that existing directory doesn't cause error."""
        filepath = os.path.join(self.temp_dir, "file.json")
        ensure_dir(filepath)  # Should not raise


class TestLoadJson(unittest.TestCase):
    """Tests for load_json function."""

    def setUp(self):
        """Create temp directory for test files."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_valid_json(self):
        """Test loading a valid JSON file."""
        filepath = os.path.join(self.temp_dir, "data.json")
        test_data = {"key": "value", "number": 42}
        with open(filepath, 'w') as f:
            json.dump(test_data, f)

        result = load_json(filepath)
        self.assertEqual(result, test_data)

    def test_load_missing_file_returns_default(self):
        """Test that missing file returns default value."""
        filepath = os.path.join(self.temp_dir, "nonexistent.json")
        result = load_json(filepath, default={"default": True})
        self.assertEqual(result, {"default": True})

    def test_load_missing_file_default_empty_dict(self):
        """Test that missing file with no default returns empty dict."""
        filepath = os.path.join(self.temp_dir, "nonexistent.json")
        result = load_json(filepath)
        self.assertEqual(result, {})

    def test_load_malformed_json_returns_default(self):
        """Test that malformed JSON returns default value."""
        filepath = os.path.join(self.temp_dir, "bad.json")
        with open(filepath, 'w') as f:
            f.write("{invalid json")

        result = load_json(filepath, default={"fallback": True})
        self.assertEqual(result, {"fallback": True})

    def test_load_empty_file_returns_default(self):
        """Test that empty file returns default value."""
        filepath = os.path.join(self.temp_dir, "empty.json")
        with open(filepath, 'w') as f:
            pass  # Create empty file

        result = load_json(filepath, default={"empty": True})
        self.assertEqual(result, {"empty": True})

    def test_load_with_list_default(self):
        """Test loading with a list as default."""
        filepath = os.path.join(self.temp_dir, "nonexistent.json")
        result = load_json(filepath, default=[])
        self.assertEqual(result, [])

    def test_load_complex_nested_json(self):
        """Test loading complex nested JSON structure."""
        filepath = os.path.join(self.temp_dir, "complex.json")
        test_data = {
            "events": [
                {"id": 1, "name": "Event 1"},
                {"id": 2, "name": "Event 2"}
            ],
            "metadata": {
                "version": "1.0",
                "nested": {"deep": True}
            }
        }
        with open(filepath, 'w') as f:
            json.dump(test_data, f)

        result = load_json(filepath)
        self.assertEqual(result, test_data)


class TestSaveJson(unittest.TestCase):
    """Tests for save_json function."""

    def setUp(self):
        """Create temp directory for test files."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_creates_file(self):
        """Test that save_json creates a new file."""
        filepath = os.path.join(self.temp_dir, "new.json")
        test_data = {"created": True}
        save_json(filepath, test_data)

        self.assertTrue(os.path.exists(filepath))
        with open(filepath, 'r') as f:
            loaded = json.load(f)
        self.assertEqual(loaded, test_data)

    def test_save_creates_parent_dirs(self):
        """Test that save_json creates parent directories."""
        filepath = os.path.join(self.temp_dir, "deep", "nested", "file.json")
        test_data = {"nested": True}
        save_json(filepath, test_data)

        self.assertTrue(os.path.exists(filepath))

    def test_save_overwrites_existing(self):
        """Test that save_json overwrites existing file."""
        filepath = os.path.join(self.temp_dir, "existing.json")
        with open(filepath, 'w') as f:
            json.dump({"old": "data"}, f)

        new_data = {"new": "data"}
        save_json(filepath, new_data)

        with open(filepath, 'r') as f:
            loaded = json.load(f)
        self.assertEqual(loaded, new_data)

    def test_save_with_custom_indent(self):
        """Test that save_json uses custom indentation."""
        filepath = os.path.join(self.temp_dir, "indented.json")
        test_data = {"key": "value"}
        save_json(filepath, test_data, indent=4)

        with open(filepath, 'r') as f:
            content = f.read()
        # Check for 4-space indentation
        self.assertIn("    ", content)

    def test_save_list(self):
        """Test saving a list."""
        filepath = os.path.join(self.temp_dir, "list.json")
        test_data = [1, 2, 3, {"nested": True}]
        save_json(filepath, test_data)

        with open(filepath, 'r') as f:
            loaded = json.load(f)
        self.assertEqual(loaded, test_data)

    def test_roundtrip(self):
        """Test that save followed by load returns same data."""
        filepath = os.path.join(self.temp_dir, "roundtrip.json")
        test_data = {
            "string": "value",
            "number": 42,
            "float": 3.14,
            "boolean": True,
            "null": None,
            "array": [1, 2, 3],
            "object": {"nested": "value"}
        }
        save_json(filepath, test_data)
        loaded = load_json(filepath)
        self.assertEqual(loaded, test_data)


if __name__ == '__main__':
    unittest.main()
