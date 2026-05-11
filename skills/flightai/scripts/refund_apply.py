#!/usr/bin/env python3
import sys
from common import call_api, check_api_response, format_timestamp

def get_order_detail(order_id):
    """获取订单详情"""
    return call_api("orderDetail", order_id)

def refund_apply(order_id, product_ids, refund_amount):
    """提交退票申请"""
    business_params = {
        "order_id": order_id,
        "product_ids": product_ids,
        "refund_amount": refund_amount
    }
    return call_api("refundApply", business_params)

def display_refund_result(response):
    """格式化展示退票申请结果"""
    if not check_api_response(response, "退票申请失败"):
        return

    data = response.get("data", {})
    refund_order_id = data.get("refundOrderId", "")

    print("\n" + "=" * 80)
    print("✅ 退票申请成功，请等待审核！")
    if refund_order_id:
        print(f"\n退票单号: {refund_order_id}")
        print()
    print("=" * 80)

    print("温馨提示：")
    print("- 退票审核通常需要1-3个工作日")
    print("- 退款到账时间取决于银行处理速度")
    print("- 您可以随时查询订单状态了解退票进度")
    print("=" * 80)

def main():
    if len(sys.argv) != 3:
        print("用法: python3 refund_apply.py <order_id> <refund_amount>")
        print("示例: python3 refund_apply.py 69b21e1ce4b0b89fdebddbd2 808")
        sys.exit(1)

    order_id = sys.argv[1]
    refund_amount = sys.argv[2]

    print(f"\n正在提交退票申请...")
    print(f"订单号: {order_id}")
    print(f"预估退票费（单票）: ¥{refund_amount}")

    # 获取订单详情以提取 product_ids
    print(f"\n正在获取订单详情...")
    order_response = get_order_detail(order_id)

    if not check_api_response(order_response, "获取订单详情失败"):
        sys.exit(1)

    order_data = order_response.get("data", {})
    passenger_list = order_data.get("passengerList", [])

    # 提取所有乘客的 product_ids，用逗号连接成字符串
    product_id_list = []
    for passenger in passenger_list:
        product_id = passenger.get("productId", "")
        if product_id:
            product_id_list.append(product_id)

    if not product_id_list:
        print("错误: 订单中未找到票号信息")
        sys.exit(1)

    # 将 product_ids 拼接成字符串
    product_ids = ",".join(product_id_list)

    print(f"找到 {len(product_id_list)} 个票号")

    response = refund_apply(order_id, product_ids, refund_amount)
    display_refund_result(response)

if __name__ == "__main__":
    main()
