#!/usr/bin/env python3
"""Tests for utils/invite_ops.py"""

import unittest
import sys
import os
import json
import tempfile
import shutil
import io
from unittest.mock import patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils import invite_ops


class TestUpdateInviteStatus(unittest.TestCase):
    """Tests for update_invite_status function."""

    def setUp(self):
        """Create temp directory and patch file path."""
        self.temp_dir = tempfile.mkdtemp()
        self.pending_file = os.path.join(self.temp_dir, "pending_invites.json")
        self.patcher = patch.object(invite_ops, 'PENDING_FILE', self.pending_file)
        self.patcher.start()

    def tearDown(self):
        """Clean up temp directory and stop patcher."""
        self.patcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_update_status_by_email_id(self):
        """Test updating invite status by email_id."""
        test_data = {
            "invites": [{
                "id": "inv1",
                "email_id": "email123",
                "events": [
                    {"title": "Team Meeting", "status": "pending"}
                ]
            }]
        }
        with open(self.pending_file, 'w') as f:
            json.dump(test_data, f)

        captured = io.StringIO()
        with patch('sys.stdout', captured):
            invite_ops.update_invite_status(
                email_id="email123",
                event_title="Team Meeting",
                new_status="created",
                calendar_event_id="cal_evt_123"
            )

        with open(self.pending_file, 'r') as f:
            data = json.load(f)

        event = data["invites"][0]["events"][0]
        self.assertEqual(event["status"], "created")
        self.assertEqual(event["event_id"], "cal_evt_123")
        self.assertIn("updated_at", event)

    def test_update_status_by_invite_id(self):
        """Test updating invite status by invite_id."""
        test_data = {
            "invites": [{
                "id": "inv1",
                "email_id": "email123",
                "events": [
                    {"title": "Project Review", "status": "pending"}
                ]
            }]
        }
        with open(self.pending_file, 'w') as f:
            json.dump(test_data, f)

        captured = io.StringIO()
        with patch('sys.stdout', captured):
            invite_ops.update_invite_status(
                invite_id="inv1",
                event_title="Project Review",
                new_status="dismissed"
            )

        with open(self.pending_file, 'r') as f:
            data = json.load(f)

        event = data["invites"][0]["events"][0]
        self.assertEqual(event["status"], "dismissed")

    def test_update_status_partial_title_match(self):
        """Test updating invite status with partial title match."""
        test_data = {
            "invites": [{
                "id": "inv1",
                "email_id": "email123",
                "events": [
                    {"title": "Weekly Team Meeting", "status": "pending"}
                ]
            }]
        }
        with open(self.pending_file, 'w') as f:
            json.dump(test_data, f)

        captured = io.StringIO()
        with patch('sys.stdout', captured):
            invite_ops.update_invite_status(
                email_id="email123",
                event_title="team meeting",  # Partial, lowercase
                new_status="created"
            )

        with open(self.pending_file, 'r') as f:
            data = json.load(f)

        event = data["invites"][0]["events"][0]
        self.assertEqual(event["status"], "created")

    def test_update_status_not_found_exits(self):
        """Test that update_invite_status raises SystemExit when event not found."""
        test_data = {
            "invites": [{
                "id": "inv1",
                "email_id": "email123",
                "events": [
                    {"title": "Team Meeting", "status": "pending"}
                ]
            }]
        }
        with open(self.pending_file, 'w') as f:
            json.dump(test_data, f)

        with self.assertRaises(SystemExit) as cm:
            invite_ops.update_invite_status(
                email_id="email123",
                event_title="Nonexistent Event",
                new_status="created"
            )
        self.assertEqual(cm.exception.code, 1)

    def test_update_status_wrong_email_id_exits(self):
        """Test that wrong email_id causes SystemExit."""
        test_data = {
            "invites": [{
                "id": "inv1",
                "email_id": "email123",
                "events": [
                    {"title": "Team Meeting", "status": "pending"}
                ]
            }]
        }
        with open(self.pending_file, 'w') as f:
            json.dump(test_data, f)

        with self.assertRaises(SystemExit) as cm:
            invite_ops.update_invite_status(
                email_id="wrong_email",
                event_title="Team Meeting",
                new_status="created"
            )
        self.assertEqual(cm.exception.code, 1)

    def test_update_multiple_events_in_invite(self):
        """Test updating specific event when invite has multiple events."""
        test_data = {
            "invites": [{
                "id": "inv1",
                "email_id": "email123",
                "events": [
                    {"title": "Event A", "status": "pending"},
                    {"title": "Event B", "status": "pending"},
                    {"title": "Event C", "status": "pending"}
                ]
            }]
        }
        with open(self.pending_file, 'w') as f:
            json.dump(test_data, f)

        captured = io.StringIO()
        with patch('sys.stdout', captured):
            invite_ops.update_invite_status(
                email_id="email123",
                event_title="Event B",
                new_status="created"
            )

        with open(self.pending_file, 'r') as f:
            data = json.load(f)

        events = data["invites"][0]["events"]
        self.assertEqual(events[0]["status"], "pending")
        self.assertEqual(events[1]["status"], "created")
        self.assertEqual(events[2]["status"], "pending")

    def test_update_prints_confirmation(self):
        """Test that update prints confirmation message."""
        test_data = {
            "invites": [{
                "id": "inv1",
                "email_id": "email123",
                "events": [
                    {"title": "Team Meeting", "status": "pending"}
                ]
            }]
        }
        with open(self.pending_file, 'w') as f:
            json.dump(test_data, f)

        captured = io.StringIO()
        with patch('sys.stdout', captured):
            invite_ops.update_invite_status(
                email_id="email123",
                event_title="Team Meeting",
                new_status="created"
            )

        output = captured.getvalue()
        self.assertIn("Updated", output)
        self.assertIn("Team Meeting", output)
        self.assertIn("created", output)


if __name__ == '__main__':
    unittest.main()
