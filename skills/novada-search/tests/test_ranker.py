import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import novada_search as ns


def test_unified_dedup_and_scoring():
    fixtures = Path(__file__).parent / "fixtures" / "engine_results.json"
    all_engine_results = json.loads(fixtures.read_text())

    items = []
    for er in all_engine_results:
        items.extend(er.get("organic_results", []))

    unified, dup_removed = ns.merge_unified_results(items, top_k=10)

    assert dup_removed >= 1
    urls = [u.get("url") for u in unified]
    assert sum(1 for u in urls if "example.com/a" in (u or "")) == 1
    assert unified[0].get("score") is not None


if __name__ == "__main__":
    test_unified_dedup_and_scoring()
    print("OK")
