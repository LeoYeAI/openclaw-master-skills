#!/usr/bin/env python3
"""Tests for utils/disposition_ops.py"""

import unittest
import sys
import os
import tempfile
import json
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.disposition_ops import (
    get_disposition_settings,
    disposition_email,
    is_calendar_reply
)


class TestGetDispositionSettings(unittest.TestCase):
    """Tests for get_disposition_settings function."""

    def test_defaults_when_no_config(self):
        """Test that defaults are returned when config doesn't exist."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{}')
            f.flush()
            settings = get_disposition_settings(f.name)
            os.unlink(f.name)

        self.assertTrue(settings["mark_read"])
        self.assertTrue(settings["archive"])
        self.assertTrue(settings["auto_dispose_calendar_replies"])

    def test_reads_config_values(self):
        """Test that config values are read correctly."""
        config = {
            "email_handling": {
                "mark_read": False,
                "archive": True,
                "auto_dispose_calendar_replies": False
            }
        }
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            f.flush()
            settings = get_disposition_settings(f.name)
            os.unlink(f.name)

        self.assertFalse(settings["mark_read"])
        self.assertTrue(settings["archive"])
        self.assertFalse(settings["auto_dispose_calendar_replies"])

    def test_partial_config(self):
        """Test that missing keys use defaults."""
        config = {
            "email_handling": {
                "mark_read": False
            }
        }
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            f.flush()
            settings = get_disposition_settings(f.name)
            os.unlink(f.name)

        self.assertFalse(settings["mark_read"])
        self.assertTrue(settings["archive"])  # default
        self.assertTrue(settings["auto_dispose_calendar_replies"])  # default

    def test_missing_email_handling_section(self):
        """Test that missing email_handling section uses all defaults."""
        config = {"gmail_account": "test@gmail.com"}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            f.flush()
            settings = get_disposition_settings(f.name)
            os.unlink(f.name)

        self.assertTrue(settings["mark_read"])
        self.assertTrue(settings["archive"])
        self.assertTrue(settings["auto_dispose_calendar_replies"])


class TestDispositionEmail(unittest.TestCase):
    """Tests for disposition_email function."""

    @patch('utils.disposition_ops.modify_email')
    @patch('utils.disposition_ops.get_disposition_settings')
    def test_mark_read_and_archive(self, mock_settings, mock_modify):
        """Test disposition with both mark_read and archive enabled."""
        mock_settings.return_value = {"mark_read": True, "archive": True}
        mock_modify.return_value = {"success": True}

        result = disposition_email("test123")

        self.assertTrue(result["success"])
        self.assertIn("mark_read", result["actions"])
        self.assertIn("archive", result["actions"])
        mock_modify.assert_called_once()
        call_args = mock_modify.call_args
        self.assertEqual(call_args[0][0], "test123")
        self.assertIn("UNREAD", call_args[1]["remove_labels"])
        self.assertIn("INBOX", call_args[1]["remove_labels"])

    @patch('utils.disposition_ops.modify_email')
    @patch('utils.disposition_ops.get_disposition_settings')
    def test_mark_read_only(self, mock_settings, mock_modify):
        """Test disposition with only mark_read enabled."""
        mock_settings.return_value = {"mark_read": True, "archive": False}
        mock_modify.return_value = {"success": True}

        result = disposition_email("test123")

        self.assertTrue(result["success"])
        self.assertIn("mark_read", result["actions"])
        self.assertNotIn("archive", result["actions"])
        call_args = mock_modify.call_args
        self.assertIn("UNREAD", call_args[1]["remove_labels"])
        self.assertNotIn("INBOX", call_args[1]["remove_labels"])

    @patch('utils.disposition_ops.modify_email')
    @patch('utils.disposition_ops.get_disposition_settings')
    def test_archive_only(self, mock_settings, mock_modify):
        """Test disposition with only archive enabled."""
        mock_settings.return_value = {"mark_read": False, "archive": True}
        mock_modify.return_value = {"success": True}

        result = disposition_email("test123")

        self.assertTrue(result["success"])
        self.assertIn("archive", result["actions"])
        self.assertNotIn("mark_read", result["actions"])
        call_args = mock_modify.call_args
        self.assertIn("INBOX", call_args[1]["remove_labels"])
        self.assertNotIn("UNREAD", call_args[1]["remove_labels"])

    @patch('utils.disposition_ops.get_disposition_settings')
    def test_no_actions_configured(self, mock_settings):
        """Test disposition when both options are disabled."""
        mock_settings.return_value = {"mark_read": False, "archive": False}

        result = disposition_email("test123")

        self.assertTrue(result["success"])
        self.assertEqual(result["actions"], [])
        self.assertIn("No disposition actions configured", result.get("message", ""))

    def test_empty_email_id(self):
        """Test that empty email_id returns error."""
        result = disposition_email("")

        self.assertFalse(result["success"])
        self.assertIn("email_id is required", result["error"])

    @patch('utils.disposition_ops.modify_email')
    @patch('utils.disposition_ops.get_disposition_settings')
    def test_override_mark_read(self, mock_settings, mock_modify):
        """Test explicit override of mark_read setting."""
        mock_settings.return_value = {"mark_read": False, "archive": False}
        mock_modify.return_value = {"success": True}

        result = disposition_email("test123", mark_read=True)

        self.assertTrue(result["success"])
        self.assertIn("mark_read", result["actions"])
        call_args = mock_modify.call_args
        self.assertIn("UNREAD", call_args[1]["remove_labels"])

    @patch('utils.disposition_ops.modify_email')
    @patch('utils.disposition_ops.get_disposition_settings')
    def test_override_archive(self, mock_settings, mock_modify):
        """Test explicit override of archive setting."""
        mock_settings.return_value = {"mark_read": False, "archive": False}
        mock_modify.return_value = {"success": True}

        result = disposition_email("test123", archive=True)

        self.assertTrue(result["success"])
        self.assertIn("archive", result["actions"])
        call_args = mock_modify.call_args
        self.assertIn("INBOX", call_args[1]["remove_labels"])

    @patch('utils.disposition_ops.modify_email')
    @patch('utils.disposition_ops.get_disposition_settings')
    def test_modify_failure(self, mock_settings, mock_modify):
        """Test handling of modify_email failure."""
        mock_settings.return_value = {"mark_read": True, "archive": True}
        mock_modify.return_value = {"success": False, "error": "API error"}

        result = disposition_email("test123")

        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "API error")
        self.assertEqual(result["actions"], [])


class TestIsCalendarReply(unittest.TestCase):
    """Tests for is_calendar_reply function."""

    def test_accepted_reply(self):
        """Test accepted invitation detection."""
        self.assertTrue(is_calendar_reply("Accepted: Team Meeting"))
        self.assertTrue(is_calendar_reply("accepted: lowercase test"))

    def test_declined_reply(self):
        """Test declined invitation detection."""
        self.assertTrue(is_calendar_reply("Declined: Team Meeting"))

    def test_tentative_reply(self):
        """Test tentative invitation detection."""
        self.assertTrue(is_calendar_reply("Tentative: Team Meeting"))

    def test_updated_invitation(self):
        """Test updated invitation detection."""
        self.assertTrue(is_calendar_reply("Updated invitation: Team Meeting"))

    def test_cancelled_reply(self):
        """Test cancelled invitation detection (both spellings)."""
        self.assertTrue(is_calendar_reply("Cancelled: Team Meeting"))
        self.assertTrue(is_calendar_reply("Canceled: Team Meeting"))

    def test_non_calendar_email(self):
        """Test that regular emails are not detected as calendar replies."""
        self.assertFalse(is_calendar_reply("Meeting next week"))
        self.assertFalse(is_calendar_reply("Re: Team Meeting"))
        self.assertFalse(is_calendar_reply("Invitation to party"))

    def test_empty_subject(self):
        """Test that empty subject returns False."""
        self.assertFalse(is_calendar_reply(""))
        self.assertFalse(is_calendar_reply(None))


if __name__ == '__main__':
    unittest.main()
