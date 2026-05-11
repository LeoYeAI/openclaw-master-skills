#!/usr/bin/env python3
import sys
import json
from common import call_api, check_api_response, format_timestamp

def get_order_detail(order_id):
    return call_api("orderDetail", order_id)

def display_order_detail(response):
    if not check_api_response(response, "查询订单详情失败"):
        return

    data = response.get("data", {})
    
    order_id = data.get("orderId", "")
    status_obj = data.get("status", {})
    order_status_key = status_obj.get("key", "") if status_obj else ""
    order_status_text = status_obj.get("value", "") if status_obj else ""
    create_time = data.get("createTime", "")
    pay_deadline = data.get("payDeadline", "")
    
    segment_info = data.get("segmentInfo", {})
    flight_no = segment_info.get("flight_no", "")
    departure_timestamp = segment_info.get("departure_timestamp", 0)
    arrived_timestamp = segment_info.get("arrived_timestamp", 0)
    starting_airport = segment_info.get("starting_airport", "")
    destination_airport = segment_info.get("destination_airport", "")
    starting_terminal = segment_info.get("starting_terminal", "")
    destination_terminal = segment_info.get("destination_terminal", "")
    seat_msg = segment_info.get("seat_msg", "")
    airline_name = segment_info.get("airline_name", "")
    plane_type = segment_info.get("plane_type", "")
    
    passenger_list = data.get("passengerList", [])
    
    price_detail = data.get("priceDetail", [])
    change_refund_price_detail = data.get("changeRefundPriceDetail", [])
    
    if change_refund_price_detail:
        final_price_detail = change_refund_price_detail
    else:
        final_price_detail = price_detail
    
    order_total_price = data.get("orderTotalPrice", 0)
    
    def format_price(price):
        return f"¥{int(price)}" if price == int(price) else f"¥{price}"
    
    print("\n" + "=" * 80)
    print("订单详情")
    print("=" * 80)
    
    print(f"\n订单号: {order_id}")
    if order_status_text or order_status_key:
        print(f"订单状态: {order_status_text}")
    if create_time:
        print(f"创建时间: {create_time}")
    if pay_deadline:
        print(f"支付截止时间: {pay_deadline}")
    
    print(f"\n航班信息:")
    if airline_name:
        print(f"- 航空公司: {airline_name}")
    if flight_no:
        print(f"- 航班号: {flight_no}")
    if departure_timestamp:
        print(f"- 出发时间: {format_timestamp(departure_timestamp, '%Y-%m-%d %H:%M')}")
    if arrived_timestamp:
        print(f"- 到达时间: {format_timestamp(arrived_timestamp, '%Y-%m-%d %H:%M')}")
    if starting_airport:
        airport_info = starting_airport
        if starting_terminal:
            airport_info += f" {starting_terminal}航站楼"
        print(f"- 出发机场: {airport_info}")
    if destination_airport:
        airport_info = destination_airport
        if destination_terminal:
            airport_info += f" {destination_terminal}航站楼"
        print(f"- 到达机场: {airport_info}")
    if seat_msg:
        print(f"- 舱位: {seat_msg}")
    if plane_type:
        print(f"- 机型: {plane_type}")
    
    if passenger_list:
        print(f"\n乘客信息:")
        for idx, passenger in enumerate(passenger_list, 1):
            passenger_info = passenger.get("passengerInfo", {})
            name = passenger_info.get("name", "")
            phone = passenger_info.get("phone", "")
            id_card = passenger_info.get("identity_no", "")
            id_type_name = passenger_info.get("identity_type_name", {}).get("value", "")
            ticket_no = passenger.get("ticketNo", "")
            
            if name:
                print(f"  - 姓名: {name}")
            if phone:
                print(f"  - 联系电话: {phone}")
            if id_card and id_type_name:
                print(f"  - 证件类型: {id_type_name}")
                print(f"  - 证件号: {id_card}")
            if ticket_no:
                print(f"  - 票号: {ticket_no}")
    
    if final_price_detail:
        print(f"\n价格信息:")
        for item in final_price_detail:
            key = item.get("key", "")
            price = item.get("price", 0)
            amount_desc = item.get("amountDesc", "")
            if key and price is not None:
                desc = f" ({amount_desc})" if amount_desc else ""
                print(f"- {key}: {format_price(price)}{desc}")
        if order_total_price > 0:
            print(f"- 总金额: {format_price(order_total_price)}")
    
    print("\n" + "=" * 80)

def main():
    if len(sys.argv) != 2:
        print("用法: python3 order_detail.py <order_id>")
        print("示例: python3 order_detail.py 69a677bee4b0252bd532e35c")
        sys.exit(1)

    order_id = sys.argv[1]

    print(f"\n正在查询订单详情...")
    print(f"订单号: {order_id}")

    response = get_order_detail(order_id)
    display_order_detail(response)

if __name__ == "__main__":
    main()
