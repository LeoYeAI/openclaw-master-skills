#!/usr/bin/env python3
import json
import sys
import os
import time

from common import call_api, format_timestamp, check_api_response, get_temp_file_path

def load_seat_item_from_file(seat_index):
    """从文件中加载舱位信息"""
    seat_items_file = get_temp_file_path("endorse_seat_items.json")

    if not os.path.exists(seat_items_file):
        print(f"错误: 找不到舱位信息文件 {seat_items_file}")
        print("请先执行 endorse_search_price.py 查询改期舱位价格信息")
        return None

    try:
        with open(seat_items_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        seat_items = data.get("seat_items", [])

        if not seat_items:
            print("错误: 舱位信息为空")
            return None

        try:
            seat_index_int = int(seat_index)

            # 根据 display_index 查找对应的舱位
            seat_item = None
            for item in seat_items:
                if item.get("display_index") == seat_index_int:
                    seat_item = item
                    break

            if seat_item is None:
                print(f"错误: 舱位编号 {seat_index} 不存在，请选择 1-{len(seat_items)} 之间的编号")
                return None

            # 同时返回 flight_info
            flight_info = data.get("flight_info", {})
            return seat_item, flight_info
        except ValueError:
            print(f"错误: 舱位编号格式不正确，请输入数字")
            return None
    except json.JSONDecodeError:
        print(f"错误: 舱位信息文件格式不正确")
        return None
    except Exception as e:
        print(f"错误: 读取舱位信息文件失败 - {str(e)}")
        return None

def endorse_apply(order_data):
    """调用改期申请API"""
    return call_api("endorseApply", order_data)

def get_order_detail(order_id):
    """获取订单详情"""
    return call_api("orderDetail", order_id)

def display_endorse_result(response, flight_info):
    """格式化展示改期申请结果"""
    if not check_api_response(response, "改期申请失败"):
        return

    data = response.get("data", {})

    new_order_id = data.get("new_order_id", "")
    pay_url = data.get("payUrl", "")
    order_detail_url = data.get("orderDetailUrl", "")

    # 从 flight_info 中获取航班信息
    flight_no = flight_info.get("flight_no", "")
    departure_time = format_timestamp(flight_info.get("departure_time", 0))
    arrived_time = format_timestamp(flight_info.get("arrived_time", 0))

    print(f"\n改期航班信息:")
    print(f"- 航班号: {flight_no}")
    print(f"- 出发时间: {departure_time}")
    print(f"- 到达时间: {arrived_time}")

    print("\n✅ 改期申请成功！")
    print(f"\n改期单订单号: {new_order_id}")

    if pay_url:
        print(f"\n💳 [立即支付]({pay_url})")

def main():
    if len(sys.argv) != 3:
        print("用法: python3 endorse_apply.py <seat_index> <order_id>")
        print("示例: python3 endorse_apply.py 1 69b21e1ce4b0b89fdebddbd2")
        sys.exit(1)

    seat_index = sys.argv[1]
    order_id = sys.argv[2]

    print(f"\n正在提交改期申请...")
    print(f"舱位编号: {seat_index}")
    print(f"原订单号: {order_id}")

    # 从文件加载舱位信息
    result = load_seat_item_from_file(seat_index)
    if not result:
        sys.exit(1)

    seat_item, flight_info = result

    # 获取订单详情以提取 ticket_ids
    print(f"\n正在获取订单详情...")
    order_response = get_order_detail(order_id)

    if not check_api_response(order_response, "获取订单详情失败"):
        sys.exit(1)

    order_data_response = order_response.get("data", {})
    passenger_list = order_data_response.get("passengerList", [])

    # 提取所有乘客的 ticket_ids
    ticket_ids = []
    for passenger in passenger_list:
        product_id = passenger.get("productId", "")
        if product_id:
            ticket_ids.append(product_id)

    if not ticket_ids:
        print("错误: 订单中未找到票号信息")
        sys.exit(1)

    # 移除 display_index，避免传递到后端
    seat_item_copy = seat_item.copy()
    if "display_index" in seat_item_copy:
        del seat_item_copy["display_index"]

    seat_item_copy["segment_info"]["departure_timestamp"] = flight_info.get("departure_time", 0)
    seat_item_copy["segment_info"]["arrived_timestamp"] = flight_info.get("arrived_time", 0)

    # 构建改期申请数据
    order_data = {
        **seat_item_copy,
        "order_id": order_id,
        "ticket_ids": ticket_ids
    }

    print(order_data)

    response = endorse_apply(order_data)
    display_endorse_result(response, flight_info)

if __name__ == "__main__":
    main()
