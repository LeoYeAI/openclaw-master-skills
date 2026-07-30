#!/usr/bin/env python3
"""Tests for utils/event_tracking.py"""

import unittest
import sys
import os
import json
import tempfile
import shutil
from unittest.mock import patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils import event_tracking


class TestTrackEvent(unittest.TestCase):
    """Tests for track_event function."""

    def setUp(self):
        """Create temp directory and patch file path."""
        self.temp_dir = tempfile.mkdtemp()
        self.events_file = os.path.join(self.temp_dir, "events.json")
        self.patcher = patch.object(event_tracking, 'EVENTS_FILE', self.events_file)
        self.patcher.start()

    def tearDown(self):
        """Clean up temp directory and stop patcher."""
        self.patcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_track_new_event(self):
        """Test tracking a new event."""
        event_tracking.track_event(
            event_id="evt123",
            calendar_id="primary",
            email_id="email456",
            summary="Test Meeting",
            start="2026-02-11T14:00:00"
        )

        with open(self.events_file, 'r') as f:
            data = json.load(f)

        self.assertEqual(len(data["events"]), 1)
        event = data["events"][0]
        self.assertEqual(event["event_id"], "evt123")
        self.assertEqual(event["calendar_id"], "primary")
        self.assertEqual(event["email_id"], "email456")
        self.assertEqual(event["summary"], "Test Meeting")
        self.assertEqual(event["start"], "2026-02-11T14:00:00")
        self.assertIsNotNone(event["created_at"])
        self.assertIsNone(event["updated_at"])

    def test_track_updates_existing(self):
        """Test that tracking same event_id updates existing entry."""
        # First track
        event_tracking.track_event(
            event_id="evt123",
            summary="Original Title",
            start="2026-02-11T14:00:00"
        )
        # Track again with same event_id
        event_tracking.track_event(
            event_id="evt123",
            summary="Updated Title",
            start="2026-02-12T15:00:00"
        )

        with open(self.events_file, 'r') as f:
            data = json.load(f)

        self.assertEqual(len(data["events"]), 1)
        event = data["events"][0]
        self.assertEqual(event["summary"], "Updated Title")
        self.assertEqual(event["start"], "2026-02-12T15:00:00")
        self.assertIsNotNone(event["updated_at"])

    def test_track_multiple_events(self):
        """Test tracking multiple different events."""
        event_tracking.track_event(event_id="evt1", summary="Event 1")
        event_tracking.track_event(event_id="evt2", summary="Event 2")
        event_tracking.track_event(event_id="evt3", summary="Event 3")

        with open(self.events_file, 'r') as f:
            data = json.load(f)

        self.assertEqual(len(data["events"]), 3)
        event_ids = [e["event_id"] for e in data["events"]]
        self.assertEqual(event_ids, ["evt1", "evt2", "evt3"])


class TestUpdateTrackedEvent(unittest.TestCase):
    """Tests for update_tracked_event function."""

    def setUp(self):
        """Create temp directory and patch file path."""
        self.temp_dir = tempfile.mkdtemp()
        self.events_file = os.path.join(self.temp_dir, "events.json")
        self.patcher = patch.object(event_tracking, 'EVENTS_FILE', self.events_file)
        self.patcher.start()

    def tearDown(self):
        """Clean up temp directory and stop patcher."""
        self.patcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_update_existing_event(self):
        """Test updating an existing tracked event."""
        # Create initial event
        event_tracking.track_event(
            event_id="evt123",
            summary="Original",
            start="2026-02-11T14:00:00"
        )

        # Update it
        event_tracking.update_tracked_event(
            event_id="evt123",
            summary="Updated",
            start="2026-02-12T15:00:00"
        )

        with open(self.events_file, 'r') as f:
            data = json.load(f)

        event = data["events"][0]
        self.assertEqual(event["summary"], "Updated")
        self.assertEqual(event["start"], "2026-02-12T15:00:00")

    def test_update_nonexistent_event_exits(self):
        """Test that updating nonexistent event raises SystemExit."""
        # Create empty events file
        with open(self.events_file, 'w') as f:
            json.dump({"events": []}, f)

        with self.assertRaises(SystemExit) as cm:
            event_tracking.update_tracked_event(
                event_id="nonexistent",
                summary="Test"
            )
        self.assertEqual(cm.exception.code, 1)


class TestDeleteTrackedEvent(unittest.TestCase):
    """Tests for delete_tracked_event function."""

    def setUp(self):
        """Create temp directory and patch file path."""
        self.temp_dir = tempfile.mkdtemp()
        self.events_file = os.path.join(self.temp_dir, "events.json")
        self.patcher = patch.object(event_tracking, 'EVENTS_FILE', self.events_file)
        self.patcher.start()

    def tearDown(self):
        """Clean up temp directory and stop patcher."""
        self.patcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_delete_existing_event(self):
        """Test deleting an existing event."""
        # Create events
        event_tracking.track_event(event_id="evt1", summary="Event 1")
        event_tracking.track_event(event_id="evt2", summary="Event 2")

        # Delete one
        event_tracking.delete_tracked_event("evt1")

        with open(self.events_file, 'r') as f:
            data = json.load(f)

        self.assertEqual(len(data["events"]), 1)
        self.assertEqual(data["events"][0]["event_id"], "evt2")

    def test_delete_nonexistent_event_warns(self):
        """Test that deleting nonexistent event prints warning but doesn't crash."""
        with open(self.events_file, 'w') as f:
            json.dump({"events": []}, f)

        # Should not raise, just warn
        event_tracking.delete_tracked_event("nonexistent")


class TestLookupEvents(unittest.TestCase):
    """Tests for lookup_events function."""

    def setUp(self):
        """Create temp directory and patch file path."""
        self.temp_dir = tempfile.mkdtemp()
        self.events_file = os.path.join(self.temp_dir, "events.json")
        self.patcher = patch.object(event_tracking, 'EVENTS_FILE', self.events_file)
        self.patcher.start()

        # Create test events
        test_data = {
            "events": [
                {"event_id": "evt1", "email_id": "email1", "summary": "Team Meeting", "start": "2026-02-11T10:00:00"},
                {"event_id": "evt2", "email_id": "email2", "summary": "Project Review", "start": "2026-02-12T14:00:00"},
                {"event_id": "evt3", "email_id": "email1", "summary": "Follow-up Meeting", "start": "2026-02-13T09:00:00"}
            ]
        }
        with open(self.events_file, 'w') as f:
            json.dump(test_data, f)

    def tearDown(self):
        """Clean up temp directory and stop patcher."""
        self.patcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('sys.stdout')
    def test_lookup_by_email_id(self, mock_stdout):
        """Test looking up events by email_id."""
        import io
        captured = io.StringIO()
        with patch('sys.stdout', captured):
            event_tracking.lookup_events(search_type="email_id", search_value="email1")

        output = captured.getvalue()
        results = json.loads(output)
        self.assertEqual(len(results), 2)
        self.assertTrue(all(e["email_id"] == "email1" for e in results))

    @patch('sys.stdout')
    def test_lookup_by_event_id(self, mock_stdout):
        """Test looking up events by event_id."""
        import io
        captured = io.StringIO()
        with patch('sys.stdout', captured):
            event_tracking.lookup_events(search_type="event_id", search_value="evt2")

        output = captured.getvalue()
        results = json.loads(output)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["event_id"], "evt2")

    @patch('sys.stdout')
    def test_lookup_by_summary_partial(self, mock_stdout):
        """Test looking up events by partial summary match."""
        import io
        captured = io.StringIO()
        with patch('sys.stdout', captured):
            event_tracking.lookup_events(search_type="summary", search_value="meeting")

        output = captured.getvalue()
        results = json.loads(output)
        self.assertEqual(len(results), 2)  # "Team Meeting" and "Follow-up Meeting"

    @patch('sys.stdout')
    def test_lookup_list_all(self, mock_stdout):
        """Test listing all events."""
        import io
        captured = io.StringIO()
        with patch('sys.stdout', captured):
            event_tracking.lookup_events(search_type="list")

        output = captured.getvalue()
        results = json.loads(output)
        self.assertEqual(len(results), 3)

    @patch('sys.stdout')
    def test_lookup_no_results(self, mock_stdout):
        """Test lookup with no matching results."""
        import io
        captured = io.StringIO()
        with patch('sys.stdout', captured):
            event_tracking.lookup_events(search_type="email_id", search_value="nonexistent")

        output = captured.getvalue()
        results = json.loads(output)
        self.assertEqual(len(results), 0)


if __name__ == '__main__':
    unittest.main()
