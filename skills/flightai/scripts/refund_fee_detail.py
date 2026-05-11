#!/usr/bin/env python3
import sys
from common import call_api, check_api_response, format_timestamp

def refund_fee_detail(order_id):
    """预估退票费查询"""
    return call_api("refundFeeDetail", order_id)

def display_refund_fee_result(response):
    """格式化展示退票费详情"""
    if not check_api_response(response, "查询退票费失败"):
        return

    data = response.get("data", {})

    # 获取退票费信息
    refund_amount = data.get("refundAmount", 0)

    print(f"预估退票费（单票）: ¥{refund_amount}")
    print("请确认是否同意退票费用，如同意，系统将自动提交退票申请")

    # 返回退款金额供后续使用
    return refund_amount

def main():
    if len(sys.argv) != 2:
        print("用法: python3 refund_fee_detail.py <order_id>")
        print("示例: python3 refund_fee_detail.py 69b21e1ce4b0b89fdebddbd2")
        sys.exit(1)

    order_id = sys.argv[1]

    print(f"\n正在查询退票费...")
    print(f"订单号: {order_id}")

    response = refund_fee_detail(order_id)
    display_refund_fee_result(response)
    

if __name__ == "__main__":
    main()
