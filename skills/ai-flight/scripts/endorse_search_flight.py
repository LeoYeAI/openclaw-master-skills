#!/usr/bin/env python3
import sys
import json
import unicodedata
from common import call_api, check_api_response, format_timestamp

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

def endorse_search_flight(order_id, dep_date, flight_no, ticket_ids):
    """改期航班搜索"""
    business_params = {
        "order_id": order_id,
        "dep_date": dep_date,
        "flight_no": flight_no,
        "ticket_ids": ticket_ids
    }
    return call_api("endorseSearchFlight", business_params)

def display_endorse_search_result(response):
    """格式化展示改期航班搜索结果"""
    if not check_api_response(response, "改期航班搜索失败"):
        return

    data = response.get("data", {})
    
    flight_list = data.get("flight_list", [])
    
    if not flight_list:
        print("\n" + "=" * 89)
        print("未找到可改期的航班")
        print("=" * 89)
        return
    
    flight_list = sorted(flight_list, key=lambda x: x.get("departure_time", 0))

    print("\n" + "=" * 72)
    print(f"{pad_string('航班号', 12)}{pad_string('航空公司', 12)}{pad_string('出发时间', 12)}{pad_string('到达时间', 12)}{pad_string('出发机场', 12)}{pad_string('到达机场', 12)}")
    print("=" * 72)

    for flight in flight_list:
        flight_no = flight.get("flight_no", "")
        airline_name = flight.get("airline_name", "")
        departure_time = format_timestamp(flight.get("departure_time", 0))
        arrived_time = format_timestamp(flight.get("arrived_time", 0))
        start_airport = flight.get("starting_airport_short", "")
        end_airport = flight.get("destination_airport_short", "")
        print(f"{pad_string(flight_no, 12)}{pad_string(airline_name, 12)}{pad_string(departure_time, 12)}{pad_string(arrived_time, 12)}{pad_string(start_airport, 12)}{pad_string(end_airport, 12)}")

    print("=" * 72)
    print(f"共找到 {len(flight_list)} 个航班")
    print("=" * 72)

def main():
    if len(sys.argv) != 3:
        print("用法: python3 endorse_search_flight.py <order_id> <dep_date>")
        print("示例: python3 endorse_search_flight.py 69a677bee4b0252bd532e35c 2026-03-20")
        sys.exit(1)

    order_id = sys.argv[1]
    dep_date = sys.argv[2]

    print(f"\n正在查询订单详情...")
    print(f"订单号: {order_id}")

    order_response = get_order_detail(order_id)

    if not check_api_response(order_response, "获取订单详情失败"):
        sys.exit(1)

    order_data = order_response.get("data", {})

    segment_info = order_data.get("segmentInfo", {})
    flight_no = segment_info.get("flight_no", "")

    passenger_list = order_data.get("passengerList", [])
    ticket_ids = passenger_list[0].get("productId", "")

    if not flight_no:
        print("错误: 订单中未找到航班号")
        sys.exit(1)

    if not ticket_ids:
        print("错误: 订单中未找到票号信息")
        sys.exit(1)

    print(f"\n正在搜索改期航班...")
    print(f"原航班号: {flight_no}")
    print(f"改期日期: {dep_date}")

    response = endorse_search_flight(order_id, dep_date, flight_no, ticket_ids)
    display_endorse_search_result(response)

if __name__ == "__main__":
    main()
