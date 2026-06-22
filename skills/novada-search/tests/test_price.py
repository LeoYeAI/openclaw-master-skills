import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import novada_search as ns


def test_price_usd():
    assert ns.extract_numeric_price("$19.99") == 19.99


def test_price_euro_comma():
    assert ns.extract_numeric_price("€24,50") == 24.50


def test_price_yen():
    assert ns.extract_numeric_price("¥1999") == 1999.0


def test_price_with_thousands():
    assert ns.extract_numeric_price("$1,299.99") == 1299.99


def test_price_empty():
    assert ns.extract_numeric_price("") is None
