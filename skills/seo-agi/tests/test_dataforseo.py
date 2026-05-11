"""Tests for DataForSEO client response parsing."""

import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).parent.parent / "scripts")
)

from lib.dataforseo import DataForSEOClient


def test_extract_serp_empty():
    client = DataForSEOClient("test", "test")
    result = client._extract_serp({"tasks": []})
    assert result["organic"] == []
    assert result["paa"] == []
    assert result["featured_snippet"] is None


def test_extract_serp_with_organic():
    raw = {
        "tasks": [{
            "result": [{
                "se_results_count": 1000000,
                "items": [
                    {
                        "type": "organic",
                        "rank_absolute": 1,
                        "url": "https://example.com/page",
                        "domain": "example.com",
                        "title": "Test Page",
                        "description": "A test description",
                    },
                    {
                        "type": "organic",
                        "rank_absolute": 2,
                        "url": "https://other.com/page",
                        "domain": "other.com",
                        "title": "Other Page",
                        "description": "Another description",
                    },
                    {
                        "type": "people_also_ask",
                        "items": [
                            {"title": "What is a test?"},
                            {"title": "How do tests work?"},
                        ],
                    },
                ]
            }]
        }]
    }

    client = DataForSEOClient("test", "test")
    result = client._extract_serp(raw)

    assert len(result["organic"]) == 2
    assert result["organic"][0]["position"] == 1
    assert result["organic"][0]["url"] == "https://example.com/page"
    assert result["organic"][1]["title"] == "Other Page"

    assert len(result["paa"]) == 2
    assert result["paa"][0] == "What is a test?"

    assert result["total_results"] == 1000000


def test_extract_keywords_empty():
    client = DataForSEOClient("test", "test")
    result = client._extract_keywords({"tasks": []})
    assert result == []


def test_extract_keywords_with_data():
    raw = {
        "tasks": [{
            "result": [{
                "items": [
                    {
                        "keyword_data": {
                            "keyword": "test keyword one",
                            "keyword_info": {
                                "search_volume": 5000,
                                "cpc": 1.50,
                                "competition": 0.7,
                            },
                            "keyword_properties": {
                                "keyword_difficulty": 42,
                            },
                        }
                    },
                    {
                        "keyword_data": {
                            "keyword": "test keyword two",
                            "keyword_info": {
                                "search_volume": 8000,
                                "cpc": 2.10,
                                "competition": 0.85,
                            },
                            "keyword_properties": {
                                "keyword_difficulty": 55,
                            },
                        }
                    },
                ]
            }]
        }]
    }

    client = DataForSEOClient("test", "test")
    result = client._extract_keywords(raw)

    # Should be sorted by volume descending
    assert len(result) == 2
    assert result[0]["keyword"] == "test keyword two"
    assert result[0]["volume"] == 8000
    assert result[1]["keyword"] == "test keyword one"
    assert result[1]["volume"] == 5000
    assert result[1]["difficulty"] == 42


def test_extract_headings():
    page_content = {
        "h1": ["Main Title"],
        "h2": ["Section One", "Section Two"],
        "h3": ["Subsection A", "Subsection B"],
    }
    headings = DataForSEOClient._extract_headings(page_content)
    assert "H1: Main Title" in headings
    assert "H2: Section One" in headings
    assert "H3: Subsection A" in headings
    assert len(headings) == 5


def test_auth_header():
    client = DataForSEOClient("user@test.com", "mypassword")
    assert client._auth_header.startswith("Basic ")
    assert len(client._auth_header) > 10


if __name__ == "__main__":
    test_extract_serp_empty()
    test_extract_serp_with_organic()
    test_extract_keywords_empty()
    test_extract_keywords_with_data()
    test_extract_headings()
    test_auth_header()
    print("All tests passed.")
