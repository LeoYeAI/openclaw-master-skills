import sys
from pathlib import Path
from datetime import datetime, timedelta

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import novada_search as ns


def test_freshness_today():
    today = datetime.now().strftime("%Y-%m-%d")
    assert ns.classify_freshness(today) == "today"


def test_freshness_older():
    assert ns.classify_freshness("2020-01-01") == "older"


def test_freshness_unknown():
    assert ns.classify_freshness("not a date") == "unknown"


def test_freshness_this_week():
    recent = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
    assert ns.classify_freshness(recent) == "this_week"


def test_extract_organic_from_data_key():
    raw = {"data": {"organic_results": [{"title": "A", "url": "https://a.com", "snippet": "..."}]}}
    results = ns.extract_organic_results(raw, 10)
    assert len(results) == 1


def test_extract_shopping_results():
    data = {"shopping_results": [{"title": "iPhone", "price": "$999", "source": "Apple"}]}
    results = ns.extract_shopping_results(data)
    assert len(results) == 1
    assert results[0]["seller"] == "Apple"


def test_parse_local_rating_label():
    assert ns.extract_rating_from_label("4.5(1.2K)") == (4.5, 1200)
    assert ns.extract_rating_from_label("") == (None, None)


def test_extract_price_from_label():
    assert ns.extract_price_from_label("€10-20 · Restaurant") is not None


def test_normalize_url_for_dedup():
    assert ns.normalize_url_for_dedup("https://www.example.com/page?a=1#top") == "example.com/page"


def test_deduplicate_results():
    items = [
        {"url": "https://example.com/a", "title": "A"},
        {"url": "https://www.example.com/a", "title": "A dup"},
        {"url": "https://example.com/b", "title": "B"},
    ]
    unique = ns.deduplicate_results(items)
    assert len(unique) == 2


def test_freshness_empty():
    assert ns.classify_freshness("") == "unknown"


def test_freshness_this_month():
    recent = (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d")
    assert ns.classify_freshness(recent) == "this_month"


def test_extract_organic_empty():
    assert ns.extract_organic_results({}, 10) == []


def test_organic_skips_no_url():
    raw = {"organic_results": [{"title": "No URL"}, {"title": "Has URL", "url": "https://b.com"}]}
    results = ns.extract_organic_results(raw, 10)
    assert len(results) == 1


def test_organic_respects_max():
    raw = {"organic_results": [{"title": f"R{i}", "url": f"https://{i}.com"} for i in range(20)]}
    results = ns.extract_organic_results(raw, 3)
    assert len(results) == 3


def test_shopping_empty():
    assert ns.extract_shopping_results({}) == []


def test_shopping_from_products_key():
    data = {"products": [{"name": "Laptop", "price": "$500"}]}
    results = ns.extract_shopping_results(data)
    assert len(results) == 1
    assert results[0]["title"] == "Laptop"


def test_video_empty():
    assert ns.extract_video_results({}) == []


def test_video_basic():
    data = {"video_results": [{"title": "Tutorial", "url": "https://yt.com/1", "channel": "Dev"}]}
    results = ns.extract_video_results(data)
    assert len(results) == 1
    assert results[0]["channel"] == "Dev"


def test_news_empty():
    assert ns.extract_news_results({}) == []


def test_news_basic():
    data = {"news_results": [{"title": "Breaking", "url": "https://news.com", "source": "CNN"}]}
    results = ns.extract_news_results(data)
    assert len(results) == 1
    assert results[0]["source"] == "CNN"


def test_jobs_empty():
    assert ns.extract_jobs_results({}) == []


def test_jobs_basic():
    data = {"jobs_results": [{"title": "Engineer", "company_name": "Google", "location": "Berlin"}]}
    results = ns.extract_jobs_results(data)
    assert len(results) == 1
    assert results[0]["company"] == "Google"


def test_rating_none():
    assert ns.extract_rating_from_label(None) == (None, None)


def test_price_none():
    assert ns.extract_price_from_label(None) is None


def test_normalize_empty():
    assert ns.normalize_url_for_dedup("") == ""


def test_normalize_strips_trailing_slash():
    assert ns.normalize_url_for_dedup("https://example.com/page/") == "example.com/page"


def test_dedup_empty():
    assert ns.deduplicate_results([]) == []
