"""Tests for env module."""

import sys
import os
import json
import tempfile
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).parent.parent / "scripts")
)

from lib.env import load_config, _determine_mode, DEFAULT_CONFIG


def test_default_config():
    config = DEFAULT_CONFIG.copy()
    assert config["default_location"] == 2840
    assert config["default_language"] == "en"
    assert config["serp_depth"] == 10
    assert config["save_research"] is True


def test_determine_mode_full():
    creds = {"has_dataforseo": True, "has_gsc": True, "has_ahrefs": False, "has_semrush": False}
    assert _determine_mode(creds) == "full"


def test_determine_mode_dataforseo_only():
    creds = {"has_dataforseo": True, "has_gsc": False, "has_ahrefs": False, "has_semrush": False}
    assert _determine_mode(creds) == "dataforseo-only"


def test_determine_mode_gsc_only():
    creds = {"has_dataforseo": False, "has_gsc": True, "has_ahrefs": False, "has_semrush": False}
    assert _determine_mode(creds) == "gsc-only"


def test_determine_mode_fallback():
    creds = {"has_dataforseo": False, "has_gsc": False, "has_ahrefs": False, "has_semrush": False}
    assert _determine_mode(creds) == "fallback"


if __name__ == "__main__":
    test_default_config()
    test_determine_mode_full()
    test_determine_mode_dataforseo_only()
    test_determine_mode_gsc_only()
    test_determine_mode_fallback()
    print("All tests passed.")
