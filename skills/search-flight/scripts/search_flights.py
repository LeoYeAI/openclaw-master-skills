#!/usr/bin/env python3
import sys
import unicodedata
from common import call_api, format_timestamp, check_api_response

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

def display_flights(response):
    """格式化展示航班信息 - 表格形式平铺展示"""
    if not check_api_response(response, "查询失败或无数据"):
        return

    data = response.get("data", {})
    flight_list = data.get("flight_list", [])

    if not flight_list:
        print("未找到航班信息")
        return

    # 按出发时间排序，过滤共享航班
    flight_list = sorted(flight_list, key=lambda x: x.get("departure_time", 0))
    flight_list = [flight for flight in flight_list if not flight.get("code_share", False)]

    print("\n" + "=" * 84)
    print(f"{pad_string('航班号', 12)}{pad_string('航空公司', 12)}{pad_string('出发时间', 12)}{pad_string('到达时间', 12)}{pad_string('出发机场', 12)}{pad_string('到达机场', 12)}{pad_string('最低价', 12)}")
    print("=" * 84)

    for flight in flight_list:
        flight_no = flight.get("flight_no", "")
        airline_name = flight.get("airline_name", "")

        departure_time = format_timestamp(flight.get("departure_time", 0))
        arrived_time = format_timestamp(flight.get("arrived_time", 0))

        starting_airport = flight.get("starting_airport_short", "")
        destination_airport = flight.get("destination_airport_short", "")

        min_price = flight.get("min_price", 0)
        # 去除 .0
        min_price_str = f"¥{int(min_price)}" if min_price == int(min_price) else f"¥{min_price}"

        print(f"{pad_string(flight_no, 12)}{pad_string(airline_name, 12)}{pad_string(departure_time, 12)}{pad_string(arrived_time, 12)}{pad_string(starting_airport, 10)}{pad_string(destination_airport, 10)}{pad_string(min_price_str, 12)}")

    print("=" * 84)
    print(f"共找到 {len(flight_list)} 个航班")
    print("=" * 84)

def main():
    if len(sys.argv) != 4:
        print("用法: python3 search_flights.py <start_code> <end_code> <date>")
        print("示例: python3 search_flights.py 北京 上海 2026-03-04")
        sys.exit(1)

    start_code = sys.argv[1]
    end_code = sys.argv[2]
    date = sys.argv[3]

    print(f"\n正在查询航班信息...")
    print(f"出发城市: {start_code}")
    print(f"到达城市: {end_code}")
    print(f"出发日期: {date}")

    # 构建业务参数
    business_params = {
        "start_code": start_code,
        "end_code": end_code,
        "date": date
    }

    response = call_api("searchFlight", business_params)
    display_flights(response)

if __name__ == "__main__":
    main()
