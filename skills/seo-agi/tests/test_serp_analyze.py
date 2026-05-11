"""Tests for serp_analyze module."""

import sys
import os
import json
from pathlib import Path

# Add scripts dir to path
sys.path.insert(
    0, str(Path(__file__).parent.parent / "scripts")
)

from lib.serp_analyze import analyze_serp, detect_intent


def load_fixture(name: str):
    fixtures_dir = Path(__file__).parent.parent / "fixtures"
    with open(fixtures_dir / name) as f:
        return json.load(f)


def test_detect_intent_commercial():
    assert detect_intent("best project management tools", [], {}) == "commercial"
    assert detect_intent("X vs Y comparison", [], {}) == "commercial"
    assert detect_intent("slack alternatives", [], {}) == "commercial"


def test_detect_intent_informational():
    assert detect_intent("how to park at JFK", [], {}) == "informational"
    assert detect_intent("what is SEO", [], {}) == "informational"
    assert detect_intent("python tutorial for beginners", [], {}) == "informational"


def test_detect_intent_transactional():
    assert detect_intent("buy parking pass JFK", [], {}) == "transactional"
    assert detect_intent("JFK parking coupon discount", [], {}) == "transactional"
    assert detect_intent("cheap parking near me", [], {}) == "transactional"


def test_detect_intent_navigational():
    assert detect_intent("JFK airport official website", [], {}) == "navigational"
    assert detect_intent("parkingaccess.com login", [], {}) == "navigational"


def test_analyze_serp_with_fixtures():
    serp_data = load_fixture("serp_sample.json")

    # Build content_data from the fixture's embedded word_count/headings
    content_data = []
    for item in serp_data.get("organic", []):
        if item.get("word_count"):
            content_data.append({
                "word_count": item["word_count"],
                "headings": item.get("headings", []),
            })
        else:
            content_data.append(None)

    analysis = analyze_serp(serp_data, content_data, "airport parking JFK")

    assert analysis["keyword"] == "airport parking JFK"
    assert analysis["intent"] in (
        "informational", "commercial", "transactional", "navigational"
    )

    # Word count stats should reflect fixture data
    wc = analysis["word_count_stats"]
    assert wc["min"] > 0
    assert wc["max"] >= wc["min"]
    assert wc["median"] > 0
    assert wc["recommended_min"] > 0
    assert wc["recommended_max"] > wc["recommended_min"]

    # PAA should come through
    assert len(analysis["paa_questions"]) > 0

    # Topic frequency should have entries from headings
    assert len(analysis["topic_frequency"]) > 0

    # Heading patterns should be populated
    hp = analysis["heading_patterns"]
    assert hp["avg_h2_count"] > 0


def test_analyze_serp_empty():
    """Handle empty SERP data gracefully."""
    analysis = analyze_serp(
        {"organic": [], "paa": [], "featured_snippet": None},
        [],
        "nonexistent keyword",
    )
    assert analysis["keyword"] == "nonexistent keyword"
    assert analysis["word_count_stats"] == {}
    assert analysis["competitors_analyzed"] == 0


def test_analyze_serp_partial_content():
    """Handle mix of parsed and failed content parses."""
    serp_data = {
        "organic": [
            {"position": 1, "url": "https://a.com", "title": "A", "description": ""},
            {"position": 2, "url": "https://b.com", "title": "B", "description": ""},
        ],
        "paa": ["Question 1?"],
        "featured_snippet": None,
    }
    content_data = [
        {"word_count": 2000, "headings": ["H1: Title", "H2: Section One", "H2: Section Two"]},
        None,  # failed parse
    ]

    analysis = analyze_serp(serp_data, content_data, "test keyword")
    assert analysis["competitors_analyzed"] == 1
    assert analysis["word_count_stats"]["median"] == 2000


if __name__ == "__main__":
    test_detect_intent_commercial()
    test_detect_intent_informational()
    test_detect_intent_transactional()
    test_detect_intent_navigational()
    test_analyze_serp_with_fixtures()
    test_analyze_serp_empty()
    test_analyze_serp_partial_content()
    print("All tests passed.")
