#!/usr/bin/env python3
"""Tests for utils/undo_ops.py"""

import unittest
import sys
import os
import json
import tempfile
import shutil
import io
from datetime import datetime, timedelta
from unittest.mock import patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils import undo_ops


class TestFindLastUndoable(unittest.TestCase):
    """Tests for find_last_undoable function."""

    def setUp(self):
        """Create temp directory and patch file path."""
        self.temp_dir = tempfile.mkdtemp()
        self.changelog_file = os.path.join(self.temp_dir, "changelog.json")
        self.patcher = patch.object(undo_ops, 'CHANGELOG_FILE', self.changelog_file)
        self.patcher.start()

    def tearDown(self):
        """Clean up temp directory and stop patcher."""
        self.patcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_finds_most_recent_undoable(self):
        """Test finding the most recent undoable change."""
        now = datetime.now()
        test_data = {
            "changes": [
                {"id": "chg_001", "timestamp": (now - timedelta(hours=2)).isoformat(), "can_undo": True},
                {"id": "chg_002", "timestamp": (now - timedelta(hours=1)).isoformat(), "can_undo": True},
                {"id": "chg_003", "timestamp": now.isoformat(), "can_undo": True}
            ]
        }
        with open(self.changelog_file, 'w') as f:
            json.dump(test_data, f)

        captured = io.StringIO()
        with patch('sys.stdout', captured):
            undo_ops.find_last_undoable()

        output = captured.getvalue().strip()
        self.assertEqual(output, "chg_003")

    def test_skips_non_undoable(self):
        """Test that non-undoable changes are skipped."""
        now = datetime.now()
        test_data = {
            "changes": [
                {"id": "chg_001", "timestamp": now.isoformat(), "can_undo": True},
                {"id": "chg_002", "timestamp": now.isoformat(), "can_undo": False}  # Already undone
            ]
        }
        with open(self.changelog_file, 'w') as f:
            json.dump(test_data, f)

        captured = io.StringIO()
        with patch('sys.stdout', captured):
            undo_ops.find_last_undoable()

        output = captured.getvalue().strip()
        self.assertEqual(output, "chg_001")

    def test_skips_old_changes(self):
        """Test that changes older than 24 hours are skipped."""
        now = datetime.now()
        test_data = {
            "changes": [
                {"id": "chg_001", "timestamp": (now - timedelta(hours=25)).isoformat(), "can_undo": True},
                {"id": "chg_002", "timestamp": (now - timedelta(hours=1)).isoformat(), "can_undo": True}
            ]
        }
        with open(self.changelog_file, 'w') as f:
            json.dump(test_data, f)

        captured = io.StringIO()
        with patch('sys.stdout', captured):
            undo_ops.find_last_undoable()

        output = captured.getvalue().strip()
        self.assertEqual(output, "chg_002")

    def test_exits_when_no_undoable(self):
        """Test that SystemExit raised when no undoable changes exist."""
        with open(self.changelog_file, 'w') as f:
            json.dump({"changes": []}, f)

        with self.assertRaises(SystemExit) as cm:
            undo_ops.find_last_undoable()

        self.assertEqual(cm.exception.code, 1)

    def test_exits_when_all_too_old(self):
        """Test that SystemExit raised when all changes are too old."""
        old_time = (datetime.now() - timedelta(hours=25)).isoformat()
        test_data = {
            "changes": [
                {"id": "chg_001", "timestamp": old_time, "can_undo": True}
            ]
        }
        with open(self.changelog_file, 'w') as f:
            json.dump(test_data, f)

        with self.assertRaises(SystemExit) as cm:
            undo_ops.find_last_undoable()

        self.assertEqual(cm.exception.code, 1)


class TestListUndoable(unittest.TestCase):
    """Tests for list_undoable function."""

    def setUp(self):
        """Create temp directory and patch file path."""
        self.temp_dir = tempfile.mkdtemp()
        self.changelog_file = os.path.join(self.temp_dir, "changelog.json")
        self.patcher = patch.object(undo_ops, 'CHANGELOG_FILE', self.changelog_file)
        self.patcher.start()

    def tearDown(self):
        """Clean up temp directory and stop patcher."""
        self.patcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_lists_all_undoable(self):
        """Test listing all undoable changes."""
        now = datetime.now()
        test_data = {
            "changes": [
                {"id": "chg_001", "timestamp": now.isoformat(), "action": "create",
                 "after": {"summary": "Event 1"}, "can_undo": True},
                {"id": "chg_002", "timestamp": now.isoformat(), "action": "update",
                 "before": {"summary": "Old"}, "after": {"summary": "New"}, "can_undo": True}
            ]
        }
        with open(self.changelog_file, 'w') as f:
            json.dump(test_data, f)

        captured = io.StringIO()
        with patch('sys.stdout', captured):
            undo_ops.list_undoable()

        output = captured.getvalue()
        self.assertIn("chg_001", output)
        self.assertIn("chg_002", output)
        self.assertIn("Created", output)
        self.assertIn("Updated", output)

    def test_empty_when_no_undoable(self):
        """Test message when no undoable changes."""
        with open(self.changelog_file, 'w') as f:
            json.dump({"changes": []}, f)

        captured = io.StringIO()
        with patch('sys.stdout', captured):
            undo_ops.list_undoable()

        output = captured.getvalue()
        self.assertIn("No undoable changes", output)

    def test_shows_delete_action(self):
        """Test that delete actions are shown correctly."""
        now = datetime.now()
        test_data = {
            "changes": [
                {"id": "chg_001", "timestamp": now.isoformat(), "action": "delete",
                 "before": {"summary": "Deleted Event"}, "can_undo": True}
            ]
        }
        with open(self.changelog_file, 'w') as f:
            json.dump(test_data, f)

        captured = io.StringIO()
        with patch('sys.stdout', captured):
            undo_ops.list_undoable()

        output = captured.getvalue()
        self.assertIn("Deleted", output)
        self.assertIn("Deleted Event", output)


class TestMarkUndone(unittest.TestCase):
    """Tests for mark_undone function."""

    def setUp(self):
        """Create temp directory and patch file path."""
        self.temp_dir = tempfile.mkdtemp()
        self.changelog_file = os.path.join(self.temp_dir, "changelog.json")
        self.patcher = patch.object(undo_ops, 'CHANGELOG_FILE', self.changelog_file)
        self.patcher.start()

    def tearDown(self):
        """Clean up temp directory and stop patcher."""
        self.patcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_sets_can_undo_false(self):
        """Test that mark_undone sets can_undo to False."""
        test_data = {
            "changes": [
                {"id": "chg_001", "can_undo": True}
            ]
        }
        with open(self.changelog_file, 'w') as f:
            json.dump(test_data, f)

        undo_ops.mark_undone("chg_001")

        with open(self.changelog_file, 'r') as f:
            data = json.load(f)

        self.assertFalse(data["changes"][0]["can_undo"])

    def test_sets_undone_at_timestamp(self):
        """Test that mark_undone sets undone_at timestamp."""
        test_data = {
            "changes": [
                {"id": "chg_001", "can_undo": True}
            ]
        }
        with open(self.changelog_file, 'w') as f:
            json.dump(test_data, f)

        undo_ops.mark_undone("chg_001")

        with open(self.changelog_file, 'r') as f:
            data = json.load(f)

        self.assertIn("undone_at", data["changes"][0])

    def test_nonexistent_change_no_error(self):
        """Test that marking nonexistent change doesn't crash."""
        test_data = {"changes": []}
        with open(self.changelog_file, 'w') as f:
            json.dump(test_data, f)

        # Should not raise
        undo_ops.mark_undone("nonexistent")

    def test_marks_only_specified_change(self):
        """Test that only the specified change is marked."""
        test_data = {
            "changes": [
                {"id": "chg_001", "can_undo": True},
                {"id": "chg_002", "can_undo": True},
                {"id": "chg_003", "can_undo": True}
            ]
        }
        with open(self.changelog_file, 'w') as f:
            json.dump(test_data, f)

        undo_ops.mark_undone("chg_002")

        with open(self.changelog_file, 'r') as f:
            data = json.load(f)

        self.assertTrue(data["changes"][0]["can_undo"])
        self.assertFalse(data["changes"][1]["can_undo"])
        self.assertTrue(data["changes"][2]["can_undo"])


if __name__ == '__main__':
    unittest.main()
