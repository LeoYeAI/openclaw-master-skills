import threading
import time
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from quote_service import (
    close_quote_service,
    get_market_state,
    get_stock_basicinfo,
    query_subscription,
    set_orderbook_callback,
    set_quote_callback,
    subscribe,
    unsubscribe_all,
)


def run():
    code = "HK.00700"
    quote_event = threading.Event()
    orderbook_event = threading.Event()

    def quote_cb(payload):
        if payload.get("success"):
            rows = payload.get("data") or []
            if rows:
                print("[QUOTE CALLBACK]", rows[0])
                quote_event.set()
        else:
            print("[QUOTE CALLBACK ERROR]", payload)

    def orderbook_cb(payload):
        if payload.get("success"):
            print("[ORDERBOOK CALLBACK]", payload.get("data"))
            orderbook_event.set()
        else:
            print("[ORDERBOOK CALLBACK ERROR]", payload)

    print("1) basicinfo:", get_stock_basicinfo(market="HK", sec_type="STOCK", code_list=[code]))
    print("2) market_state:", get_market_state([code]))
    print("3) set_quote_callback:", set_quote_callback(quote_cb))
    print("4) subscribe quote:", subscribe([code], ["QUOTE"], is_first_push=True, subscribe_push=True))
    got_quote = quote_event.wait(10)
    print("4.1) quote callback received:", got_quote)
    print("5) set_orderbook_callback:", set_orderbook_callback(orderbook_cb))
    print("6) subscribe order_book:", subscribe([code], ["ORDER_BOOK"], is_first_push=True, subscribe_push=True))
    got_orderbook = orderbook_event.wait(10)
    print("6.1) orderbook callback received:", got_orderbook)
    print("7) query_subscription:", query_subscription())
    print("7.1) wait 61s to satisfy futu unsubscribe minimum duration")
    time.sleep(61)
    print("8) unsubscribe_all:", unsubscribe_all())
    time.sleep(1)
    close_quote_service()


if __name__ == "__main__":
    run()
