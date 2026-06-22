import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pytest
import novada_search as ns


def test_missing_key_raises_config_error(monkeypatch):
    monkeypatch.delenv("NOVADA_API_KEY", raising=False)
    ns.CLI_API_KEY = None
    with pytest.raises(ns.NovadaConfigError):
        ns.novada_search("test", "google")


def test_ensure_success_error_code():
    with pytest.raises(ns.NovadaAPIError):
        ns.ensure_success({"data": {"code": 403, "msg": "forbidden"}})


def test_ensure_success_ok_200():
    ns.ensure_success({"data": {"code": 200, "msg": "ok"}})


def test_ensure_success_no_code():
    ns.ensure_success({"data": {"results": []}})


def test_exception_hierarchy():
    assert issubclass(ns.NovadaAPIError, ns.NovadaSearchError)
    assert issubclass(ns.NovadaConfigError, ns.NovadaSearchError)
    assert issubclass(ns.NovadaNetworkError, ns.NovadaSearchError)


def test_sdk_missing_key(monkeypatch):
    monkeypatch.delenv("NOVADA_API_KEY", raising=False)
    ns.CLI_API_KEY = None
    with pytest.raises(ns.NovadaConfigError):
        ns.NovadaSearch(api_key=None)


def test_ensure_success_ok_0():
    ns.ensure_success({"data": {"code": 0}})


def test_ensure_success_nested_data():
    with pytest.raises(ns.NovadaAPIError):
        ns.ensure_success({"data": {"code": 401, "msg": "unauthorized"}})


def test_network_error_retryable_flag():
    err = ns.NovadaNetworkError("timeout", retryable=True)
    assert err.retryable is True
    err2 = ns.NovadaNetworkError("bad cert", retryable=False)
    assert err2.retryable is False


def test_api_error_code_attribute():
    err = ns.NovadaAPIError("fail", code=429, engine="google")
    assert err.code == 429
    assert err.engine == "google"
