#!/usr/bin/env python3
import json
import sys
import os
from common import call_api, format_timestamp, check_api_response, get_temp_file_path

def load_seat_item_from_file(seat_index):
    """从文件中加载舱位信息"""
    seat_items_file = get_temp_file_path("flight_seat_items.json")

    if not os.path.exists(seat_items_file):
        print(f"错误: 找不到舱位信息文件 {seat_items_file}")
        print("请先执行 search_price.py 查询航班价格信息")
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

            return seat_item
        except ValueError:
            print(f"错误: 舱位编号格式不正确，请输入数字")
            return None
    except json.JSONDecodeError:
        print(f"错误: 舱位信息文件格式不正确")
        return None
    except Exception as e:
        print(f"错误: 读取舱位信息文件失败 - {str(e)}")
        return None

def create_order(order_data, passenger_name, passenger_phone, passenger_id):
    """调用航班下单API"""
    return call_api("createOrder", order_data, name=passenger_name, phone=passenger_phone, idCard=passenger_id)

def display_order_result(response):
    """格式化展示订单结果"""
    if not check_api_response(response, "订单创建失败"):
        return

    data = response.get("data", {})
    outbound = data.get("outbound", {})
    outbound_data = outbound.get("data", {})

    order_id = outbound_data.get("orderId", "")
    pay_deadline = outbound_data.get("overTime", 0)
    pay_url = data.get("payUrl", "")
    order_detail_url = data.get("orderDetailUrl", "")

    # 航班信息
    flight_info = outbound_data.get("segmentInfo", {})
    flight_no = flight_info.get("flight_no", "")
    departure_time = format_timestamp(flight_info.get("departure_timestamp", 0))
    arrived_time = format_timestamp(flight_info.get("arrived_timestamp", 0))
    cabin_name = flight_info.get("seat_msg", "")

    print(f"\n航班信息:")
    print(f"- 航班号: {flight_no}")
    print(f"- 出发时间: {departure_time}")
    print(f"- 到达时间: {arrived_time}")
    print(f"- 舱位: {cabin_name}")

    print("\n✅ 订单创建成功！")
    print(f"\n订单号: {order_id}")
    print(f"支付截止时间: {pay_deadline}")

    if pay_url:
        print(f"\n💳 [立即支付]({pay_url})")

def main():
    if len(sys.argv) != 5:
        print("用法: python3 create_order.py <seat_index> <passenger_name> <passenger_phone> <passenger_id>")
        print("示例: python3 create_order.py 1 \"张三\" \"13800138000\" \"110101199001011234\"")
        sys.exit(1)

    seat_index = sys.argv[1]
    passenger_name = sys.argv[2]
    passenger_phone = sys.argv[3]
    passenger_id = sys.argv[4]

    print(f"\n正在创建订单...")
    print(f"舱位编号: {seat_index}")
    print(f"乘客姓名: {passenger_name}")
    print(f"乘客手机号: {passenger_phone}")
    print(f"乘客证件号: {passenger_id}")

    # 从文件加载舱位信息
    seat_item = load_seat_item_from_file(seat_index)
    if not seat_item:
        sys.exit(1)

    # 移除 display_index，避免传递到后端
    seat_item_copy = seat_item.copy()
    if "display_index" in seat_item_copy:
        del seat_item_copy["display_index"]

    # 构建订单数据
    order_data = {
        **seat_item_copy,
    }

    response = create_order(order_data, passenger_name, passenger_phone, passenger_id)
    display_order_result(response)

if __name__ == "__main__":
    main()
