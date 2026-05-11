#!/usr/bin/env python3
import sys
import json
import unicodedata
from common import call_api, check_api_response, format_timestamp, get_temp_file_path

def display_width(s):
    """计算字符串的显示宽度（中文2，英文1）"""
    width = 0
    for char in s:
        ea_width = unicodedata.east_asian_width(char)
        if ea_width in ('F', 'W'):  # Fullwidth, Wide
            width += 2
        else:
            width += 1
    return width

def pad_string(s, target_width):
    """根据显示宽度填充字符串"""
    current_width = display_width(s)
    padding = target_width - current_width
    return s + ' ' * max(0, padding)

def get_order_detail(order_id):
    """获取订单详情"""
    return call_api("orderDetail", order_id)

def endorse_search_price(order_id, dep_date, flight_no, ticket_ids):
    """改期舱位详情查询"""
    business_params = {
        "order_id": order_id,
        "dep_date": dep_date,
        "flight_no": flight_no,
        "ticket_ids": ticket_ids
    }
    return call_api("endorseSearchPrice", business_params)

def save_seat_items_to_file(seat_items, flight_info):
    """将舱位信息保存到文件，供改期下单时使用"""
    seat_items_file = get_temp_file_path("endorse_seat_items.json")

    # 为每个舱位添加显示编号，确保与展示顺序一一对应
    seat_items_with_index = []
    for idx, item in enumerate(seat_items, 1):
        item_with_index = item.copy()
        item_with_index["display_index"] = idx
        seat_items_with_index.append(item_with_index)

    data_to_save = {
        "flight_info": flight_info,
        "seat_items": seat_items_with_index
    }

    with open(seat_items_file, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=2)

    return seat_items_file

def display_price_info(response):
    """格式化展示改期舱位价格信息"""
    if not check_api_response(response, "查询失败或无数据"):
        return

    data = response.get("data", {})

    # 获取舱位列表
    seat_items = data.get("seatItems", [])
    if not seat_items:
        print("未找到舱位信息")
        return

    # 获取航班基本信息
    flight_no = data.get("flight_no", "")
    departure_time = format_timestamp(data.get("departure_time", 0))
    arrived_time = format_timestamp(data.get("arrived_time", 0))
    plane_type = data.get("plane_type_short", "")
    starting_terminal = data.get("starting_terminal", "")
    destination_terminal = data.get("destination_terminal", "")

    print("\n" + "=" * 72)
    print(f"航班信息: {flight_no} | {departure_time}-{arrived_time} | {plane_type} | {starting_terminal}-{destination_terminal}")
    print("=" * 72)

    # 按价格排序
    seat_items = sorted(seat_items, key=lambda x: x.get("price_info", {}).get("price", 0))

    # 表头
    print(f"{pad_string('编号', 8)}{pad_string('舱位', 12)}{pad_string('改期费', 12)}{pad_string('机票差价费', 14)}{pad_string('预估总改期费', 16)}{pad_string('座位状态', 12)}")
    print("=" * 72)

    # 展示舱位信息
    for idx, seat_item in enumerate(seat_items, 1):
        product_name = seat_item.get("product_name", "")

        price_info = seat_item.get("price_info", {})
        change_fee = price_info.get("change_fee", 0)
        upgrade_price = price_info.get("upgrade_price", 0)
        total_price = change_fee + upgrade_price

        # 去除 .0
        change_fee_str = f"¥{int(change_fee)}" if change_fee == int(change_fee) else f"¥{change_fee}"
        upgrade_price_str = f"¥{int(upgrade_price)}" if upgrade_price == int(upgrade_price) else f"¥{upgrade_price}"
        total_price_str = f"¥{int(total_price)}" if total_price == int(total_price) else f"¥{total_price}"

        # 余座状态
        seat_status_str = seat_item.get("seat_status", "0")
        try:
            seat_count = int(seat_status_str)
            if seat_count >= 9:
                seat_status = "余座充足"
            elif seat_count > 0:
                seat_status = f"余{seat_count}座"
            else:
                seat_status = "座位紧张"
        except:
            seat_status = "余座充足"

        idx_str = f"[{idx}]"
        print(f"{pad_string(idx_str, 8)}{pad_string(product_name, 12)}{pad_string(change_fee_str, 12)}{pad_string(upgrade_price_str, 14)}{pad_string(total_price_str, 14)}{pad_string(seat_status, 12)}")

    print("=" * 72)
    print(f"\n共找到 {len(seat_items)} 个舱位价格")
    print("=" * 72)

    # 保存舱位信息到文件
    flight_info = {
        "flight_no": flight_no,
        "departure_time": data.get("departure_time"),
        "arrived_time": data.get("arrived_time"),
        "plane_type": plane_type,
        "starting_terminal": starting_terminal,
        "destination_terminal": destination_terminal
    }
    seat_items_file = save_seat_items_to_file(seat_items, flight_info)
    print(f"\n舱位信息已保存到: {seat_items_file}")
    print("请选择舱位编号（如：1）进行改期")

def main():
    if len(sys.argv) != 4:
        print("用法: python3 endorse_search_price.py <order_id> <dep_date> <flight_no>")
        print("示例: python3 endorse_search_price.py 69b21e1ce4b0b89fdebddbd2 2026-03-20 HU7603")
        sys.exit(1)

    order_id = sys.argv[1]
    dep_date = sys.argv[2]
    flight_no = sys.argv[3]

    print(f"\n正在查询订单详情...")
    print(f"订单号: {order_id}")

    order_response = get_order_detail(order_id)

    if not check_api_response(order_response, "获取订单详情失败"):
        sys.exit(1)

    order_data = order_response.get("data", {})

    passenger_list = order_data.get("passengerList", [])
    # passenger_list取第一个的productId
    ticket_ids = passenger_list[0].get("productId", "")

    if not ticket_ids:
        print("错误: 订单中未找到票号信息")
        sys.exit(1)

    print(f"\n正在查询改期舱位价格...")
    print(f"改期日期: {dep_date}")
    print(f"选择航班号: {flight_no}")

    response = endorse_search_price(order_id, dep_date, flight_no, ticket_ids)
    display_price_info(response)

if __name__ == "__main__":
    main()
