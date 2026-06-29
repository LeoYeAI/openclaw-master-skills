#!/usr/bin/env python3
"""
分贝通酒店助手 - 格式化输出模块
固化展示逻辑，确保输出格式一致
"""

# ============================================================
# 展示配置（可调整）
# ============================================================

# 酒店列表展示数量
HOTEL_LIST_LIMIT = 5

# 房型展示数量
ROOM_LIST_LIMIT = 5

# 每个房型展示的产品数量
PLAN_LIST_LIMIT = 5

# ============================================================
# 酒店列表格式化
# ============================================================

def format_hotel_list(hotels, city_name=None):
    """
    格式化酒店列表展示
    
    Args:
        hotels: 酒店列表数据
        city_name: 城市名称（可选）
    
    Returns:
        格式化后的Markdown文本
    """
    lines = []
    
    if city_name:
        lines.append(f"## 🏨 {city_name}酒店搜索结果\n")
    else:
        lines.append("## 🏨 酒店搜索结果\n")
    
    lines.append(f"找到 **{len(hotels)}** 家酒店\n")
    
    for idx, hotel in enumerate(hotels[:HOTEL_LIST_LIMIT], 1):
        name = hotel.get("name", "-")
        score = hotel.get("score", "-")
        star = hotel.get("star_level_name", "-")
        address = hotel.get("address", "-")
        min_price = hotel.get("min_price", 0)
        
        lines.append(f"**【酒店{idx}】{name}**")
        lines.append(f"- ⭐ {score}分 | {star}")
        lines.append(f"- 📍 {address}")
        lines.append(f"- 💰 最低价 **¥{int(min_price)}**")
        lines.append("")
    
    lines.append("---")
    lines.append("💡 回复酒店序号查看房型价格，如 **1**")
    
    return "\n".join(lines)


# ============================================================
# 酒店房型价格格式化
# ============================================================

def format_hotel_rooms(hotel_info, rooms, check_in_date, check_out_date):
    """
    格式化酒店房型价格展示
    
    Args:
        hotel_info: 酒店基本信息
        rooms: 房型列表数据
        check_in_date: 入住日期
        check_out_date: 退房日期
    
    Returns:
        格式化后的Markdown文本
    """
    lines = []
    
    # 酒店信息头部
    name = hotel_info.get("name", "-")
    score = hotel_info.get("score", "-")
    star = hotel_info.get("star_level_name", "-")
    address = hotel_info.get("address", "-")
    
    lines.append(f"## 🏨 {name}\n")
    lines.append(f"⭐ {score}分 | {star}")
    lines.append(f"📍 {address}")
    lines.append(f"📅 入住：{check_in_date} → 退房：{check_out_date}")
    lines.append("")
    lines.append("---\n")
    
    # 房型列表
    room_count = 0
    for room in rooms[:ROOM_LIST_LIMIT]:
        if room_count >= ROOM_LIST_LIMIT:
            break
            
        room_name = room.get("room_name", "-")
        bed_type = room.get("bed_type", "-")
        area = room.get("area", "-")
        window_type = room.get("window_type", "-")
        
        plans = room.get("plan_list", [])
        if not plans:
            continue
        
        room_count += 1
        lines.append(f"### 房型{room_count}：{room_name}")
        lines.append(f"- 🛏️ 床型：{bed_type}")
        lines.append(f"- 📐 面积：{area}")
        lines.append(f"- 🪟 窗户：{window_type}")
        lines.append("")
        
        # 产品表格
        lines.append("| 序号 | 价格 | 早餐 | 取消政策 | 取消详情 |")
        lines.append("|:---:|---:|:---:|:---:|---|")
        
        plan_count = 0
        for plan in plans[:PLAN_LIST_LIMIT]:
            price = int(plan.get("total_price", 0))
            breakfast = plan.get("breakfast", {}).get("value", "无早")
            cancel_type = plan.get("cancel_type", {}).get("value", "-")
            cancel_rule = plan.get("cancel_rule", "-")
            
            # 截取取消详情（太长会换行）
            cancel_rule_short = cancel_rule[:30] + "..." if len(cancel_rule) > 30 else cancel_rule
            
            # 不可取消标红
            if cancel_type == "不可取消":
                cancel_type_display = f"⚠️{cancel_type}"
            else:
                cancel_type_display = f"✅{cancel_type}"
            
            plan_count += 1
            seq = f"{room_count}-{plan_count}"
            lines.append(f"| {seq} | ¥{price} | {breakfast} | {cancel_type_display} | {cancel_rule_short} |")
        
        lines.append("")
    
    lines.append("---")
    lines.append("💡 回复 **房型序号-产品序号** 预订，如 **1-1**")
    lines.append("⚠️ 注意：不可取消的订单确认后无法退款")
    
    return "\n".join(lines)


# ============================================================
# 订单创建结果格式化
# ============================================================

def format_order_result(order_data, hotel_info, room_info, plan_info):
    """
    格式化订单创建结果展示
    
    Args:
        order_data: 订单数据（包含order_id）
        hotel_info: 酒店信息
        room_info: 房型信息
        plan_info: 产品信息
    
    Returns:
        格式化后的Markdown文本
    """
    lines = []
    
    order_id = order_data.get("order_id", "-")
    
    # 酒店信息
    name = hotel_info.get("name", "-")
    score = hotel_info.get("score", "-")
    address = hotel_info.get("address", "-")
    
    # 房型信息
    room_name = room_info.get("room_name", "-")
    bed_type = room_info.get("bed_type", "-")
    area = room_info.get("area", "-")
    window_type = room_info.get("window_type", "-")
    
    # 产品信息
    price = int(plan_info.get("total_price", 0))
    breakfast = plan_info.get("breakfast", {}).get("value", "无早")
    cancel_type = plan_info.get("cancel_type", {}).get("value", "-")
    cancel_rule = plan_info.get("cancel_rule", "-")
    check_in = plan_info.get("check_in_date", "-")
    check_out = plan_info.get("check_out_date", "-")
    
    lines.append("## ✅ 酒店订单创建成功！\n")
    
    # 订单基本信息
    lines.append(f"**订单号**：{order_id}")
    lines.append("")
    
    lines.append("### 🏨 酒店信息")
    lines.append(f"- **酒店**：{name} ⭐{score}分")
    lines.append(f"- **地址**：{address}")
    lines.append("")
    
    lines.append("### 🛏️ 房型信息")
    lines.append(f"- **房型**：{room_name}")
    lines.append(f"- **床型**：{bed_type}")
    lines.append(f"- **面积**：{area}")
    lines.append(f"- **窗户**：{window_type}")
    lines.append(f"- **早餐**：{breakfast}")
    lines.append(f"- **入住**：{check_in} → {check_out}")
    lines.append(f"- **价格**：¥{price}")
    lines.append("")
    
    lines.append("### 📋 取消政策")
    lines.append(f"- **类型**：{cancel_type}")
    lines.append(f"- **详情**：{cancel_rule}")
    lines.append("")
    
    # 支付按钮
    pay_url = f"https://app-gate.fenbeitong.com/business/hotel/open/push/redirect?orderId={order_id}"
    lines.append(f"**[立即支付]({pay_url})**")
    lines.append("")
    lines.append("---")
    lines.append("⚠️ 请尽快完成支付，超时订单将自动取消！")
    
    return "\n".join(lines)


# ============================================================
# 行程规划格式化
# ============================================================

def format_trip_plan(flights_go, flights_return, hotels_shanghai, hotels_suzhou):
    """
    格式化行程规划展示
    
    Args:
        flights_go: 去程航班列表
        flights_return: 返程航班列表
        hotels_shanghai: 上海酒店列表（含房型）
        hotels_suzhou: 苏州酒店列表（含房型）
    
    Returns:
        格式化后的Markdown文本
    """
    lines = []
    
    lines.append("## 🧳 行程规划\n")
    lines.append("---\n")
    
    # 去程航班
    lines.append("### 📅 4月2日（周四）北京 → 上海\n")
    lines.append("**✈️ 去程航班**（需下午3点前到达静安寺商圈）\n")
    lines.append("| 序号 | 航班 | 时间 | 航线 | 最低价 |")
    lines.append("|:---:|------|------|------|-----:|")
    
    for idx, f in enumerate(flights_go[:5], 1):
        flight_no = f.get("flight_no", "-")
        airline = f.get("airline_name", "-")
        dep_time = f.get("dep_time", "-")
        arr_time = f.get("arr_time", "-")
        dep_port = f.get("starting_airport_short", "-")
        arr_port = f.get("destination_airport_short", "-")
        price = int(f.get("min_price", 0))
        
        lines.append(f"| {idx} | {flight_no} {airline} | {dep_time}-{arr_time} | {dep_port}→{arr_port} | ¥{price} |")
    
    lines.append("")
    
    # 上海酒店
    lines.append("**🏨 上海酒店**（静安寺商圈亚朵）\n")
    lines.append("| 序号 | 酒店 | 房型 | 床型 | 窗户 | 价格 | 早餐 | 取消政策 |")
    lines.append("|:---:|------|------|------|:---:|-----:|-----:|---------|")
    
    room_idx = 0
    for hotel in hotels_shanghai[:5]:
        hotel_name = hotel.get("name", "-")
        rooms = hotel.get("rooms", [])
        
        for room in rooms[:2]:
            if room_idx >= 10:  # 最多展示10个房型
                break
            room_idx += 1
            
            room_name = room.get("room_name", "-")
            bed_type = room.get("bed_type", "-")
            window = room.get("window_type", "-")
            
            plan = room.get("plans", [{}])[0] if room.get("plans") else {}
            price = int(plan.get("total_price", 0))
            breakfast = plan.get("breakfast", {}).get("value", "无早")
            cancel = plan.get("cancel_type", {}).get("value", "-")
            
            lines.append(f"| {room_idx} | {hotel_name[:10]}... | {room_name} | {bed_type} | {window} | ¥{price} | {breakfast} | {cancel} |")
    
    lines.append("")
    lines.append("📢 **发布会**：15:00-18:00 上海宏安瑞士大酒店（愚园路1号）")
    lines.append("")
    lines.append("---\n")
    
    # 苏州酒店
    lines.append("### 📅 4月3日（周五）上海 → 苏州\n")
    lines.append("🚗 **上海 → 苏州**（车程约1.5小时）\n")
    lines.append("**🏨 苏州酒店**（工业园区尼盛万丽附近亚朵）\n")
    lines.append("| 序号 | 酒店 | 房型 | 床型 | 窗户 | 价格 | 早餐 | 取消政策 |")
    lines.append("|:---:|------|------|------|:---:|-----:|-----:|---------|")
    
    room_idx = 0
    for hotel in hotels_suzhou[:5]:
        hotel_name = hotel.get("name", "-")
        rooms = hotel.get("rooms", [])
        
        for room in rooms[:2]:
            if room_idx >= 10:
                break
            room_idx += 1
            
            room_name = room.get("room_name", "-")
            bed_type = room.get("bed_type", "-")
            window = room.get("window_type", "-")
            
            plan = room.get("plans", [{}])[0] if room.get("plans") else {}
            price = int(plan.get("total_price", 0))
            breakfast = plan.get("breakfast", {}).get("value", "无早")
            cancel = plan.get("cancel_type", {}).get("value", "-")
            
            lines.append(f"| {room_idx} | {hotel_name[:10]}... | {room_name} | {bed_type} | {window} | ¥{price} | {breakfast} | {cancel} |")
    
    lines.append("")
    lines.append("📢 **发布会**：15:00-18:00 苏州尼盛万丽酒店（苏州大道西229号）")
    lines.append("")
    lines.append("---\n")
    
    # 返程航班
    lines.append("### 📅 4月4日（周六）苏州 → 上海 → 北京\n")
    lines.append("🚗 **苏州 → 上海机场**（车程约1.5小时）\n")
    lines.append("**✈️ 返程航班**\n")
    lines.append("| 序号 | 航班 | 时间 | 航线 | 最低价 |")
    lines.append("|:---:|------|------|------|-----:|")
    
    for idx, f in enumerate(flights_return[:5], 1):
        flight_no = f.get("flight_no", "-")
        airline = f.get("airline_name", "-")
        dep_time = f.get("dep_time", "-")
        arr_time = f.get("arr_time", "-")
        dep_port = f.get("starting_airport_short", "-")
        arr_port = f.get("destination_airport_short", "-")
        price = int(f.get("min_price", 0))
        
        lines.append(f"| {idx} | {flight_no} {airline} | {dep_time}-{arr_time} | {dep_port}→{arr_port} | ¥{price} |")
    
    lines.append("")
    lines.append("---\n")
    
    # 回复格式说明
    lines.append("**回复格式**：`去程序号-上海房型序号-苏州房型序号-返程序号`")
    lines.append("")
    lines.append("**示例**：`1-6-8-1`")
    lines.append("")
    lines.append("请选择！")
    
    return "\n".join(lines)


# ============================================================
# 订单确认格式化
# ============================================================

def format_order_confirmation(selection):
    """
    格式化订单确认展示
    
    Args:
        selection: 用户选择的数据
    
    Returns:
        格式化后的Markdown文本
    """
    lines = []
    
    lines.append("## ✅ 行程确认\n")
    lines.append("---\n")
    
    # 去程
    go_flight = selection.get("go_flight", {})
    lines.append("### 📅 4月2日（周四）北京 → 上海\n")
    lines.append("**✈️ 去程航班**")
    lines.append(f"- **{go_flight.get('flight_no', '-')} {go_flight.get('airline', '-')}**")
    lines.append(f"- 时间：{go_flight.get('dep_time', '-')}-{go_flight.get('arr_time', '-')}")
    lines.append(f"- 航线：{go_flight.get('dep_port', '-')}→{go_flight.get('arr_port', '-')}")
    lines.append(f"- 价格：¥{go_flight.get('price', 0)}（经济舱）")
    lines.append("")
    
    # 上海酒店
    shanghai_hotel = selection.get("shanghai_hotel", {})
    lines.append("**🏨 上海酒店**")
    lines.append(f"- **{shanghai_hotel.get('name', '-')}**")
    lines.append(f"- 房型：{shanghai_hotel.get('room_name', '-')}")
    lines.append(f"- 床型：{shanghai_hotel.get('bed_type', '-')} | 面积：{shanghai_hotel.get('area', '-')} | 窗户：{shanghai_hotel.get('window', '-')}")
    lines.append(f"- 价格：¥{shanghai_hotel.get('price', 0)}")
    lines.append(f"- 取消政策：{shanghai_hotel.get('cancel_rule', '-')}")
    lines.append("")
    lines.append("📢 **发布会**：15:00-18:00 上海宏安瑞士大酒店（愚园路1号）")
    lines.append("")
    lines.append("---\n")
    
    # 苏州酒店
    suzhou_hotel = selection.get("suzhou_hotel", {})
    lines.append("### 📅 4月3日（周五）上海 → 苏州\n")
    lines.append("🚗 **上海 → 苏州**（车程约1.5小时）\n")
    lines.append("**🏨 苏州酒店**")
    lines.append(f"- **{suzhou_hotel.get('name', '-')}**")
    lines.append(f"- 房型：{suzhou_hotel.get('room_name', '-')}")
    lines.append(f"- 床型：{suzhou_hotel.get('bed_type', '-')} | 面积：{suzhou_hotel.get('area', '-')} | 窗户：{suzhou_hotel.get('window', '-')}")
    lines.append(f"- 价格：¥{suzhou_hotel.get('price', 0)}")
    lines.append(f"- 取消政策：{suzhou_hotel.get('cancel_rule', '-')}")
    lines.append("")
    lines.append("📢 **发布会**：15:00-18:00 苏州尼盛万丽酒店（苏州大道西229号）")
    lines.append("")
    lines.append("---\n")
    
    # 返程
    return_flight = selection.get("return_flight", {})
    lines.append("### 📅 4月4日（周六）苏州 → 上海 → 北京\n")
    lines.append("🚗 **苏州 → 上海机场**（车程约1.5小时）\n")
    lines.append("**✈️ 返程航班**")
    lines.append(f"- **{return_flight.get('flight_no', '-')} {return_flight.get('airline', '-')}**")
    lines.append(f"- 时间：{return_flight.get('dep_time', '-')}-{return_flight.get('arr_time', '-')}")
    lines.append(f"- 航线：{return_flight.get('dep_port', '-')}→{return_flight.get('arr_port', '-')}")
    lines.append(f"- 价格：¥{return_flight.get('price', 0)}（经济舱）")
    lines.append("")
    lines.append("---\n")
    
    # 费用汇总
    total = go_flight.get('price', 0) + shanghai_hotel.get('price', 0) + suzhou_hotel.get('price', 0) + return_flight.get('price', 0)
    lines.append("## 💰 费用汇总\n")
    lines.append("| 项目 | 价格 |")
    lines.append("|-----|-----:|")
    lines.append(f"| 去程机票 | ¥{go_flight.get('price', 0)} |")
    lines.append(f"| 返程机票 | ¥{return_flight.get('price', 0)} |")
    lines.append(f"| 上海酒店 | ¥{shanghai_hotel.get('price', 0)} |")
    lines.append(f"| 苏州酒店 | ¥{suzhou_hotel.get('price', 0)} |")
    lines.append(f"| **总计** | **¥{total}** |")
    lines.append("")
    lines.append("---")
    lines.append("确认预订请回复 **确认**，我将为您创建订单！")
    
    return "\n".join(lines)


# ============================================================
# 订单详情格式化（创建成功后展示）
# ============================================================

def format_order_detail_full(orders):
    """
    格式化完整的订单详情展示（创建成功后）
    
    Args:
        orders: 订单列表，包含机票和酒店订单
    
    Returns:
        格式化后的Markdown文本
    """
    lines = []
    
    lines.append("## ✅ 订单创建成功！请尽快支付\n")
    lines.append("---\n")
    
    # 机票订单
    for order in orders.get("flights", []):
        lines.append("### ✈️ 机票订单\n")
        lines.append(f"| 项目 | 详情 |")
        lines.append("|-----|------|")
        lines.append(f"| **订单号** | {order.get('order_id', '-')} |")
        lines.append(f"| **航班** | {order.get('flight_no', '-')} {order.get('airline', '-')} |")
        lines.append(f"| **机型** | {order.get('plane_type', '-')} |")
        lines.append(f"| **时间** | {order.get('date', '-')} {order.get('dep_time', '-')}-{order.get('arr_time', '-')} |")
        lines.append(f"| **航线** | {order.get('dep_port', '-')} → {order.get('arr_port', '-')} |")
        lines.append(f"| **舱位** | {order.get('cabin', '-')} ({order.get('cabin_code', '-')}舱) |")
        lines.append(f"| **票价** | ¥{order.get('price', 0)} + ¥{order.get('tax', 0)}机建 + ¥{order.get('fuel', 0)}燃油 = **¥{order.get('total', 0)}** |")
        lines.append("")
        
        # 行李额
        baggage = order.get("baggage", {})
        if baggage:
            lines.append("**🧳 行李额**")
            checkin = baggage.get("checkin", {})
            carryon = baggage.get("carryon", {})
            lines.append(f"- 托运行李：免费{checkin.get('weight', '-')}KG，不限件数，单件≤{checkin.get('size', '-')}")
            lines.append(f"- 手提行李：免费{carryon.get('weight', '-')}KG，每人{carryon.get('piece', '-')}件，单件≤{carryon.get('size', '-')}")
            lines.append("")
        
        # 支付按钮
        pay_url = order.get("pay_url", "")
        if pay_url:
            lines.append(f"**[立即支付]({pay_url})**")
        
        lines.append("")
        lines.append("---\n")
    
    # 酒店订单
    for order in orders.get("hotels", []):
        lines.append("### 🏨 酒店订单\n")
        lines.append(f"| 项目 | 详情 |")
        lines.append("|-----|------|")
        lines.append(f"| **订单号** | {order.get('order_id', '-')} |")
        lines.append(f"| **酒店** | {order.get('hotel_name', '-')} ⭐{order.get('score', '-')}分 |")
        lines.append(f"| **地址** | {order.get('address', '-')} |")
        lines.append(f"| **房型** | {order.get('room_name', '-')} |")
        lines.append(f"| **床型** | {order.get('bed_type', '-')} |")
        lines.append(f"| **面积** | {order.get('area', '-')} |")
        lines.append(f"| **窗户** | {order.get('window', '-')} |")
        lines.append(f"| **早餐** | {order.get('breakfast', '-')} |")
        lines.append(f"| **入住** | {order.get('check_in', '-')} - {order.get('check_out', '-')} |")
        lines.append(f"| **价格** | ¥{order.get('price', 0)} |")
        lines.append("")
        
        # 取消政策
        lines.append("**📋 取消政策**")
        lines.append(f"- **类型**：{order.get('cancel_type', '-')}")
        lines.append(f"- **详情**：{order.get('cancel_rule', '-')}")
        lines.append("")
        
        # 支付按钮
        pay_url = order.get("pay_url", "")
        if pay_url:
            lines.append(f"**[立即支付]({pay_url})**")
        
        lines.append("")
        lines.append("---\n")
    
    # 费用汇总
    lines.append("## 💰 费用汇总\n")
    lines.append("| 项目 | 价格 |")
    lines.append("|-----|-----:|")
    
    total = 0
    for order in orders.get("flights", []):
        price = order.get("total", 0)
        total += price
        lines.append(f"| {order.get('type', '机票')} | ¥{price} |")
    
    for order in orders.get("hotels", []):
        price = order.get("price", 0)
        total += price
        lines.append(f"| {order.get('type', '酒店')} | ¥{price} |")
    
    lines.append(f"| **总计** | **¥{total}** |")
    lines.append("")
    lines.append("---")
    lines.append("⚠️ **请尽快完成支付，机票订单超时将自动取消！**")
    
    return "\n".join(lines)