import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import novada_search as ns


def test_engine_query_param_mapping_exists():
    for engine in ns.SUPPORTED_ENGINES:
        assert engine in ns.ENGINE_QUERY_PARAM, f"Missing param mapping for {engine}"


def test_google_uses_q():
    assert ns.ENGINE_QUERY_PARAM["google"] == "q"


def test_ebay_uses_nkw():
    assert ns.ENGINE_QUERY_PARAM["ebay"] == "_nkw"


def test_walmart_uses_query():
    assert ns.ENGINE_QUERY_PARAM["walmart"] == "query"


def test_youtube_uses_search_query():
    assert ns.ENGINE_QUERY_PARAM["youtube"] == "search_query"


def test_yandex_uses_text():
    assert ns.ENGINE_QUERY_PARAM["yandex"] == "text"


def test_yelp_uses_find_desc():
    assert ns.ENGINE_QUERY_PARAM["yelp"] == "find_desc"
