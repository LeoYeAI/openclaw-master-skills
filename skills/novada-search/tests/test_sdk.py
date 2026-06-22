import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import novada_search as ns


def test_sdk_requires_key(monkeypatch):
    monkeypatch.delenv("NOVADA_API_KEY", raising=False)
    try:
        ns.NovadaSearch(api_key=None)
        assert False, "Expected NovadaConfigError"
    except ns.NovadaConfigError:
        assert True


def test_sdk_detect_intent(monkeypatch):
    monkeypatch.setenv("NOVADA_API_KEY", "dummy")
    client = ns.NovadaSearch()
    assert client.detect_intent("buy shoes") == "shopping"
