"""Tests for openai_reddit module."""

import sys
import unittest
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib import http
from lib.openai_reddit import _is_model_access_error, MODEL_FALLBACK_ORDER


class TestIsModelAccessError(unittest.TestCase):
    """Tests for _is_model_access_error function."""

    def test_returns_false_for_non_400_error(self):
        """Non-400 errors should not trigger fallback."""
        error = http.HTTPError("Server error", status_code=500, body="Internal error")
        self.assertFalse(_is_model_access_error(error))

    def test_returns_false_for_400_without_body(self):
        """400 without body should not trigger fallback."""
        error = http.HTTPError("Bad request", status_code=400, body=None)
        self.assertFalse(_is_model_access_error(error))

    def test_returns_true_for_verification_error(self):
        """Verification error should trigger fallback."""
        error = http.HTTPError(
            "Bad request",
            status_code=400,
            body='{"error": {"message": "Your organization must be verified to use the model \'gpt-5.2\'"}}'
        )
        self.assertTrue(_is_model_access_error(error))

    def test_returns_true_for_access_error(self):
        """Access denied error should trigger fallback."""
        error = http.HTTPError(
            "Bad request",
            status_code=400,
            body='{"error": {"message": "Your account does not have access to this model"}}'
        )
        self.assertTrue(_is_model_access_error(error))

    def test_returns_true_for_model_not_found(self):
        """Model not found error should trigger fallback."""
        error = http.HTTPError(
            "Bad request",
            status_code=400,
            body='{"error": {"message": "The model gpt-5.2 was not found"}}'
        )
        self.assertTrue(_is_model_access_error(error))

    def test_returns_false_for_unrelated_400(self):
        """Unrelated 400 errors should not trigger fallback."""
        error = http.HTTPError(
            "Bad request",
            status_code=400,
            body='{"error": {"message": "Invalid JSON in request body"}}'
        )
        self.assertFalse(_is_model_access_error(error))


class TestModelFallbackOrder(unittest.TestCase):
    """Tests for MODEL_FALLBACK_ORDER constant."""

    def test_contains_gpt4o(self):
        """Fallback list should include gpt-4o."""
        self.assertIn("gpt-4o", MODEL_FALLBACK_ORDER)

    def test_gpt4o_is_first(self):
        """gpt-4o should be the first fallback option."""
        self.assertEqual(MODEL_FALLBACK_ORDER[0], "gpt-4o")


if __name__ == "__main__":
    unittest.main()
