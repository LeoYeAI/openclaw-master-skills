#!/usr/bin/env python3
"""Tests for utils/changelog_ops.py"""

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

from utils import changelog_ops


class TestLogCreate(unittest.TestCase):
    """Tests for log_create function."""

    def setUp(self):
        """Create temp directory and patch file path."""
        self.temp_dir = tempfile.mkdtemp()
        self.changelog_file = os.path.join(self.temp_dir, "changelog.json")
        self.patcher = patch.object(changelog_ops, 'CHANGELOG_FILE', self.changelog_file)
        self.patcher.start()

    def tearDown(self):
        """Clean up temp directory and stop patcher."""
        self.patcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_log_create_adds_entry(self):
        """Test that log_create adds a create entry."""
        change_id = changelog_ops.log_create(
            event_id="evt123",
            calendar_id="primary",
            summary="Team Meeting",
            start_time="2026-02-11T14:00:00",
            end_time="2026-02-11T15:00:00",
            email_id="email456"
        )

        with open(self.changelog_file, 'r') as f:
            data = json.load(f)

        self.assertEqual(len(data["changes"]), 1)
        change = data["changes"][0]
        self.assertEqual(change["action"], "create")
        self.assertEqual(change["event_id"], "evt123")
        self.assertEqual(change["calendar_id"], "primary")
        self.assertIsNone(change["before"])
        self.assertEqual(change["after"]["summary"], "Team Meeting")
        self.assertEqual(change["after"]["start"], "2026-02-11T14:00:00")
        self.assertTrue(change["can_undo"])
        self.assertTrue(change_id.startswith("chg_"))

    def test_log_create_returns_change_id(self):
        """Test that log_create returns a valid change ID."""
        change_id = changelog_ops.log_create(
            event_id="evt123",
            calendar_id="primary",
            summary="Test"
        )

        self.assertIsNotNone(change_id)
        self.assertTrue(change_id.startswith("chg_"))


class TestLogUpdate(unittest.TestCase):
    """Tests for log_update function."""

    def setUp(self):
        """Create temp directory and patch file path."""
        self.temp_dir = tempfile.mkdtemp()
        self.changelog_file = os.path.join(self.temp_dir, "changelog.json")
        self.patcher = patch.object(changelog_ops, 'CHANGELOG_FILE', self.changelog_file)
        self.patcher.start()

    def tearDown(self):
        """Clean up temp directory and stop patcher."""
        self.patcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_log_update_stores_before_after(self):
        """Test that log_update stores before and after states."""
        before = json.dumps({"summary": "Old Title", "start": "2026-02-11T10:00:00"})
        after = json.dumps({"summary": "New Title", "start": "2026-02-11T14:00:00"})

        change_id = changelog_ops.log_update(
            event_id="evt123",
            calendar_id="primary",
            before_json=before,
            after_json=after
        )

        with open(self.changelog_file, 'r') as f:
            data = json.load(f)

        change = data["changes"][0]
        self.assertEqual(change["action"], "update")
        self.assertEqual(change["before"]["summary"], "Old Title")
        self.assertEqual(change["after"]["summary"], "New Title")
        self.assertTrue(change["can_undo"])

    def test_log_update_handles_invalid_json(self):
        """Test that log_update handles invalid JSON gracefully."""
        change_id = changelog_ops.log_update(
            event_id="evt123",
            calendar_id="primary",
            before_json="not json",
            after_json="also not json"
        )

        with open(self.changelog_file, 'r') as f:
            data = json.load(f)

        change = data["changes"][0]
        self.assertIsNone(change["before"])
        self.assertIsNone(change["after"])


class TestLogDelete(unittest.TestCase):
    """Tests for log_delete function."""

    def setUp(self):
        """Create temp directory and patch file path."""
        self.temp_dir = tempfile.mkdtemp()
        self.changelog_file = os.path.join(self.temp_dir, "changelog.json")
        self.patcher = patch.object(changelog_ops, 'CHANGELOG_FILE', self.changelog_file)
        self.patcher.start()

    def tearDown(self):
        """Clean up temp directory and stop patcher."""
        self.patcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_log_delete_stores_before_state(self):
        """Test that log_delete stores the before state."""
        before = json.dumps({"summary": "Deleted Event", "start": "2026-02-11T10:00:00"})

        change_id = changelog_ops.log_delete(
            event_id="evt123",
            calendar_id="primary",
            before_json=before
        )

        with open(self.changelog_file, 'r') as f:
            data = json.load(f)

        change = data["changes"][0]
        self.assertEqual(change["action"], "delete")
        self.assertEqual(change["before"]["summary"], "Deleted Event")
        self.assertIsNone(change["after"])


class TestListChanges(unittest.TestCase):
    """Tests for list_changes function."""

    def setUp(self):
        """Create temp directory and patch file path."""
        self.temp_dir = tempfile.mkdtemp()
        self.changelog_file = os.path.join(self.temp_dir, "changelog.json")
        self.patcher = patch.object(changelog_ops, 'CHANGELOG_FILE', self.changelog_file)
        self.patcher.start()

    def tearDown(self):
        """Clean up temp directory and stop patcher."""
        self.patcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_list_changes_empty(self):
        """Test list_changes when no changes recorded."""
        with open(self.changelog_file, 'w') as f:
            json.dump({"changes": []}, f)

        captured = io.StringIO()
        with patch('sys.stdout', captured):
            changelog_ops.list_changes()

        output = captured.getvalue()
        self.assertIn("No changes recorded", output)

    def test_list_changes_shows_entries(self):
        """Test list_changes shows recent entries."""
        test_data = {
            "changes": [{
                "id": "chg_001",
                "timestamp": datetime.now().isoformat(),
                "action": "create",
                "event_id": "evt123",
                "after": {"summary": "Test Meeting"},
                "can_undo": True
            }]
        }
        with open(self.changelog_file, 'w') as f:
            json.dump(test_data, f)

        captured = io.StringIO()
        with patch('sys.stdout', captured):
            changelog_ops.list_changes()

        output = captured.getvalue()
        self.assertIn("CREATE", output)
        self.assertIn("Test Meeting", output)
        self.assertIn("can undo", output)


class TestCanUndo(unittest.TestCase):
    """Tests for can_undo function."""

    def setUp(self):
        """Create temp directory and patch file path."""
        self.temp_dir = tempfile.mkdtemp()
        self.changelog_file = os.path.join(self.temp_dir, "changelog.json")
        self.patcher = patch.object(changelog_ops, 'CHANGELOG_FILE', self.changelog_file)
        self.patcher.start()

    def tearDown(self):
        """Clean up temp directory and stop patcher."""
        self.patcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_can_undo_recent_change(self):
        """Test can_undo returns true for recent change."""
        test_data = {
            "changes": [{
                "id": "chg_001",
                "timestamp": datetime.now().isoformat(),
                "action": "create",
                "can_undo": True
            }]
        }
        with open(self.changelog_file, 'w') as f:
            json.dump(test_data, f)

        captured = io.StringIO()
        with patch('sys.stdout', captured):
            changelog_ops.can_undo("chg_001")

        output = captured.getvalue().strip()
        self.assertEqual(output, "true")

    def test_can_undo_old_change(self):
        """Test can_undo returns false for old change (outside 24h window)."""
        old_time = (datetime.now() - timedelta(hours=25)).isoformat()
        test_data = {
            "changes": [{
                "id": "chg_001",
                "timestamp": old_time,
                "action": "create",
                "can_undo": True
            }]
        }
        with open(self.changelog_file, 'w') as f:
            json.dump(test_data, f)

        captured = io.StringIO()
        with patch('sys.stdout', captured):
            changelog_ops.can_undo("chg_001")

        output = captured.getvalue().strip()
        self.assertEqual(output, "false")

    def test_can_undo_already_undone(self):
        """Test can_undo returns false for already undone change."""
        test_data = {
            "changes": [{
                "id": "chg_001",
                "timestamp": datetime.now().isoformat(),
                "action": "create",
                "can_undo": False  # Already undone
            }]
        }
        with open(self.changelog_file, 'w') as f:
            json.dump(test_data, f)

        captured = io.StringIO()
        with patch('sys.stdout', captured):
            changelog_ops.can_undo("chg_001")

        output = captured.getvalue().strip()
        self.assertEqual(output, "false")

    def test_can_undo_not_found(self):
        """Test can_undo exits with error for nonexistent change."""
        with open(self.changelog_file, 'w') as f:
            json.dump({"changes": []}, f)

        captured = io.StringIO()
        with self.assertRaises(SystemExit) as cm:
            with patch('sys.stdout', captured):
                changelog_ops.can_undo("nonexistent")

        self.assertEqual(cm.exception.code, 1)


class TestGetChange(unittest.TestCase):
    """Tests for get_change function."""

    def setUp(self):
        """Create temp directory and patch file path."""
        self.temp_dir = tempfile.mkdtemp()
        self.changelog_file = os.path.join(self.temp_dir, "changelog.json")
        self.patcher = patch.object(changelog_ops, 'CHANGELOG_FILE', self.changelog_file)
        self.patcher.start()

    def tearDown(self):
        """Clean up temp directory and stop patcher."""
        self.patcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_change_returns_json(self):
        """Test get_change returns change as JSON."""
        test_data = {
            "changes": [{
                "id": "chg_001",
                "action": "create",
                "event_id": "evt123"
            }]
        }
        with open(self.changelog_file, 'w') as f:
            json.dump(test_data, f)

        captured = io.StringIO()
        with patch('sys.stdout', captured):
            changelog_ops.get_change("chg_001")

        output = captured.getvalue()
        result = json.loads(output)
        self.assertEqual(result["id"], "chg_001")
        self.assertEqual(result["action"], "create")

    def test_get_change_not_found(self):
        """Test get_change exits with error for nonexistent change."""
        with open(self.changelog_file, 'w') as f:
            json.dump({"changes": []}, f)

        with self.assertRaises(SystemExit) as cm:
            changelog_ops.get_change("nonexistent")

        self.assertEqual(cm.exception.code, 1)


class TestMaxChangesLimit(unittest.TestCase):
    """Tests for MAX_CHANGES limit enforcement."""

    def setUp(self):
        """Create temp directory and patch file path."""
        self.temp_dir = tempfile.mkdtemp()
        self.changelog_file = os.path.join(self.temp_dir, "changelog.json")
        self.patcher = patch.object(changelog_ops, 'CHANGELOG_FILE', self.changelog_file)
        self.patcher.start()

    def tearDown(self):
        """Clean up temp directory and stop patcher."""
        self.patcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_limits_to_max_changes(self):
        """Test that changelog is limited to MAX_CHANGES entries."""
        # Create changelog with MAX_CHANGES entries
        changes = [{"id": f"chg_{i:03d}"} for i in range(100)]
        with open(self.changelog_file, 'w') as f:
            json.dump({"changes": changes}, f)

        # Add one more
        changelog_ops.log_create(
            event_id="evt_new",
            calendar_id="primary",
            summary="New Event"
        )

        with open(self.changelog_file, 'r') as f:
            data = json.load(f)

        self.assertEqual(len(data["changes"]), 100)
        # Oldest should be removed
        self.assertNotEqual(data["changes"][0]["id"], "chg_000")


if __name__ == '__main__':
    unittest.main()
