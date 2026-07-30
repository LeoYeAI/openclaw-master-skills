import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from quote_service import close_quote_service, get_cur_kline, get_market_snapshot, get_rt_ticker, request_history_kline


def _preview(result, name):
    ok = result.get("success")
    data = result.get("data") or []
    sample = data[0] if isinstance(data, list) and data else data
    print(f"{name}: success={ok}, size={len(data) if isinstance(data, list) else 'N/A'}")
    print(f"{name} sample:", sample)
    if not ok:
        print(f"{name} message:", result.get("message"))


def run():
    code = "HK.00700"
    _preview(get_market_snapshot([code]), "market_snapshot")
    _preview(get_cur_kline(code=code, num=5, ktype="K_DAY", autype="QFQ"), "cur_kline")
    _preview(request_history_kline(code=code, start="2026-02-20", end="2026-03-06", ktype="K_DAY", autype="QFQ", max_count=10), "history_kline")
    _preview(get_rt_ticker(code=code, num=10), "rt_ticker")
    close_quote_service()


if __name__ == "__main__":
    run()
