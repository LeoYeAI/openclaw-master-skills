#!/usr/bin/env python3
import json
import sys
import unicodedata
from common import call_api, format_timestamp, check_api_response, get_temp_file_path

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

def save_seat_items_to_file(seat_items, flight_info):
    """将舱位信息保存到文件，供下单时使用"""
    seat_items_file = get_temp_file_path("flight_seat_items.json")

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
    """格式化展示价格信息"""
    if not check_api_response(response, "查询失败或无数据"):
        return

    data = response.get("data", {})

    # 获取舱位列表
    seat_items = data.get("seatItems", [])
    if not seat_items:
        print("未找到舱位信息")
        return

    # 从第一个舱位获取航班基本信息
    first_seat = seat_items[0]
    segment_info = first_seat.get("segment_info", {})

    flight_no = data.get("flight_no", "")
    departure_time = format_timestamp(data.get("departure_time", 0))
    arrived_time = format_timestamp(data.get("arrived_time", 0))
    plane_type = data.get("plane_type_short", "")
    starting_terminal = data.get("starting_terminal", "")
    destination_terminal = data.get("destination_terminal", "")

    print("\n" + "=" * 80)
    print(f"航班信息: {flight_no} | {departure_time}-{arrived_time} | {plane_type} | {starting_terminal}-{destination_terminal}")
    print("=" * 80)

    # 按价格排序
    seat_items = sorted(seat_items, key=lambda x: x.get("price_info", {}).get("sale_price", 0))

    # 表头
    print(f"{pad_string('编号', 8)}{pad_string('舱位', 12)}{pad_string('价格', 12)}{pad_string('机建费', 12)}{pad_string('燃油费', 14)}{pad_string('总票价', 12)}{pad_string('座位状态', 12)}")
    print("=" * 80)

    # 展示舱位信息
    for idx, seat_item in enumerate(seat_items, 1):
        product_name = seat_item.get("product_name", "")

        price_info = seat_item.get("price_info", {})
        price = price_info.get("sale_price", 0)
        discount = price_info.get("discount", 0)
        airport_tax = price_info.get("airport_tax", 0)
        fuel_tax = price_info.get("fuel_tax", 0)
        total_price = price + airport_tax + fuel_tax

        # 去除 .0
        price_str = f"¥{int(price)}" if price == int(price) else f"¥{price}"
        airport_tax_str = f"¥{int(airport_tax)}" if airport_tax == int(airport_tax) else f"¥{airport_tax}"
        fuel_tax_str = f"¥{int(fuel_tax)}" if fuel_tax == int(fuel_tax) else f"¥{fuel_tax}"
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
        print(f"{pad_string(idx_str, 8)}{pad_string(product_name, 12)}{pad_string(price_str, 12)}{pad_string(airport_tax_str, 12)}{pad_string(fuel_tax_str, 12)}{pad_string(total_price_str, 10)}{pad_string(seat_status, 10)}")

    print("=" * 80)
    print(f"\n共找到 {len(seat_items)} 个舱位价格")
    print("=" * 80)

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
    print("请选择舱位编号（如：1）进行下单")

def main():
    if len(sys.argv) != 5:
        print("用法: python3 search_price.py <start_code> <end_code> <date> <flight_no>")
        print("示例: python3 search_price.py PEK PVG 2026-03-04 CA1501")
        sys.exit(1)

    start_code = sys.argv[1]
    end_code = sys.argv[2]
    date = sys.argv[3]
    flight_no = sys.argv[4]

    print(f"\n正在查询航班价格信息...")
    print(f"出发城市: {start_code}")
    print(f"到达城市: {end_code}")
    print(f"出发日期: {date}")
    print(f"航班号: {flight_no}")

    # 构建业务参数
    business_params = {
        "start_code": start_code,
        "end_code": end_code,
        "date": date,
        "flight_no": flight_no
    }

    response = call_api("searchPrice", business_params)
    display_price_info(response)

if __name__ == "__main__":
    main()
