#!/usr/bin/env python3
import sys
from common import call_api, check_api_response

def cancel_order(order_id):
    return call_api("cancelOrder", order_id)

def display_cancel_result(response):
    if not check_api_response(response, "取消订单失败"):
        return

    print("\n" + "=" * 80)
    print("✅ 订单取消成功！")
    print("=" * 80)

def main():
    if len(sys.argv) != 2:
        print("用法: python3 cancel_order.py <order_id>")
        print("示例: python3 cancel_order.py 69a677bee4b0252bd532e35c")
        sys.exit(1)

    order_id = sys.argv[1]

    print(f"\n正在取消订单...")
    print(f"订单号: {order_id}")

    response = cancel_order(order_id)
    display_cancel_result(response)

if __name__ == "__main__":
    main()
