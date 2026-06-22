import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import novada_search as ns


INTENT_TEST_CASES = [
    ("buy Nike Air Max shoes", "shopping"),
    ("purchase iPhone 16 where to buy", "shopping"),
    ("paper towel bulk pack", None),
    ("toilet paper discount", "shopping"),
    ("best pizza near me", "local"),
    ("ramen nearby", "local"),
    ("transformer attention paper arxiv", "academic"),
    ("research paper about llm", "academic"),
    ("video game news today", "news"),
    ("latest AI news", "news"),
    ("breaking news germany", "news"),
    ("react hooks tutorial", "video"),
    ("watch video tutorial for blender", "video"),
    ("python developer job Berlin", "jobs"),
    ("hiring frontend engineer remote", "jobs"),
    ("flights from SFO to NRT", "travel"),
    ("book flight Berlin to Tokyo", "travel"),
    ("NVIDIA stock price", "finance"),
    ("tesla market cap", "finance"),
    ("logo image search", "images"),
    ("find photo reference", "images"),
    ("hello world", None),
    ("what is the weather today", None),
    ("coffee in Berlin", None),
    ("kaufen MacBook Pro günstig", "shopping"),
    ("附近的咖啡店", "local"),
    ("购买 iPhone 16 价格", "shopping"),
    ("学术论文 arxiv", "academic"),
    ("最新新闻", "news"),
    ("股票行情", "finance"),
]


def test_intent_detection_cases():
    for query, expected in INTENT_TEST_CASES:
        result = ns.detect_intent(query)
        assert result == expected, f"query={query} result={result} expected={expected}"
