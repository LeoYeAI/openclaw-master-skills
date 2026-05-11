#!/usr/bin/env python3
"""
查询航班退改规则
从 flight_seat_items.json 读取舱位信息，调用 searchGuestRule API 查询退改规则
"""
import json
import sys
from common import call_api, check_api_response, get_temp_file_path


def display_guest_rule(response, seat_item):
    """格式化展示退改规则"""
    if not check_api_response(response, "查询退改规则失败"):
        return

    data = response.get("data", {})
    stipulate = data.get("stipulate", {})

    if not stipulate:
        print("未找到退改规则信息")
        return

    # 获取舱位基本信息
    cabin = stipulate.get("cabin", "")
    par_price = stipulate.get("par_price", 0)
    product_name = seat_item.get("product_name", "")
    discount = seat_item.get("discount", 0)

    print("\n" + "=" * 100)
    print(f"舱位信息: {product_name} | {cabin}舱 | 票面价 ¥{int(par_price)}")
    print("=" * 100)

    # 退票规则
    refund_stipulate = stipulate.get("refund_stipulate", "")
    if refund_stipulate:
        print("\n【退票规则】")
        print("-" * 100)
        try:
            rules = refund_stipulate.split(",")
            for rule in rules:
                rule = rule.strip()
                if rule and not rule.startswith("*"):
                    print(f"  • {rule}")
                elif rule.startswith("*"):
                    print(f"\n{rule}")
        except Exception:
            print(f"  {refund_stipulate}")

    # 改期规则
    change_stipulate = stipulate.get("change_stipulate", "")
    if change_stipulate:
        print("\n【改期规则】")
        print("-" * 100)
        try:
            rules = change_stipulate.split("。")
            for rule in rules:
                rule = rule.strip()
                if rule and not rule.startswith("*"):
                    print(f"  • {rule}")
                elif rule.startswith("*"):
                    print(f"\n{rule}")
        except Exception:
            print(f"  {change_stipulate}")

    # 签转规则
    modify_stipulate = stipulate.get("modify_stipulate", "")
    if modify_stipulate:
        print("\n【签转规则】")
        print("-" * 100)
        print(f"  {modify_stipulate}")

    # 行李额
    baggage_info = stipulate.get("baggage_info", {})
    if baggage_info:
        print("\n【行李额】")
        print("-" * 100)
        try:
            # 托运行李
            check_in = baggage_info.get("checkInBaggage", {})
            if check_in.get("flag"):
                context = check_in.get("context", "")
                if context:
                    for line in context.split("\n"):
                        if line.strip():
                            print(f"  • {line.strip()}")

            # 手提行李
            carry_on = baggage_info.get("carryOnBaggage", {})
            if carry_on.get("flag"):
                context = carry_on.get("context", "")
                if context:
                    for line in context.split("\n"):
                        if line.strip():
                            print(f"  • {line.strip()}")

        except Exception:
            # 兜底：展示原始行李额信息
            baggage_context = baggage_info.get("baggage_context", "")
            if baggage_context:
                print(f"  {baggage_context}")
            else:
                print(f"  {str(baggage_info)}")

    print("\n" + "=" * 100)

def load_seat_items():
    """从文件加载舱位信息"""
    seat_items_file = get_temp_file_path("flight_seat_items.json")

    try:
        with open(seat_items_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        print("错误: 未找到舱位信息文件")
        print("请先执行舱位详情查询（searchPrice）")
        return None
    except json.JSONDecodeError:
        print("错误: 舱位信息文件格式错误")
        return None


def main():
    if len(sys.argv) != 2:
        print("用法: python3 search_guest_rule.py <seat_index>")
        print("示例: python3 search_guest_rule.py 1")
        sys.exit(1)

    try:
        seat_index = int(sys.argv[1])
    except ValueError:
        print("错误: 舱位编号必须是数字")
        sys.exit(1)

    # 加载舱位信息
    data = load_seat_items()
    if not data:
        sys.exit(1)

    seat_items = data.get("seat_items", [])
    flight_info = data.get("flight_info", {})

    # 验证舱位编号
    if seat_index < 1 or seat_index > len(seat_items):
        print(f"错误: 舱位编号无效，请选择 1-{len(seat_items)} 之间的编号")
        sys.exit(1)

    # 获取选中的舱位
    selected_seat = seat_items[seat_index - 1]

    print(f"\n正在查询退改规则...")
    print(f"航班号: {flight_info.get('flight_no', '')}")
    print(f"舱位: {selected_seat.get('product_name', '')}")

    # 移除 display_index，避免传递到后端
    seat_item_copy = selected_seat.copy()
    if "display_index" in seat_item_copy:
        del seat_item_copy["display_index"]

    # 构建业务参数 - 使用舱位信息中的所有相关字段
    business_params = {
       **seat_item_copy,
    }

    # 调用 API
    response = call_api("searchGuestRule", business_params)

    # 格式化展示退改规则
    display_guest_rule(response, selected_seat)


if __name__ == "__main__":
    main()