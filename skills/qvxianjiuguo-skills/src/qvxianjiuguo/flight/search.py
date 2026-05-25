"""机票搜索核心模块

支持模糊搜索：根据出发地和目的地周围一定范围内的机场两两组合查询，
最终输出最低价前10的特价机票。
"""

from __future__ import annotations

import json
import logging
import os
from typing import Optional
from itertools import product
from datetime import datetime, timedelta

from .types import FlightInfo, SearchResult, SearchParams, AirportInfo
from .platforms import get_platform_handler, PLATFORMS

logger = logging.getLogger("flight-search")

# 数据文件路径
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "airports")
FLIGHT_MATRIX_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "flight-matrix")

# 缓存已加载的数据
_airports_cache: Optional[dict[str, AirportInfo]] = None
_nearby_cache: dict[int, dict] = {}
_flight_matrix_cache: Optional[dict] = None


def _load_airports() -> dict[str, AirportInfo]:
    """加载机场数据"""
    global _airports_cache
    if _airports_cache is not None:
        return _airports_cache

    airports_file = os.path.join(DATA_DIR, "airports.json")
    if not os.path.exists(airports_file):
        logger.warning(f"机场数据文件不存在: {airports_file}")
        return {}

    with open(airports_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    _airports_cache = {}
    for item in data:
        airport = AirportInfo(
            code=item.get("code", ""),
            name=item.get("name", ""),
            city=item.get("city", ""),
            province=item.get("province", ""),
            region=item.get("region", ""),
            latitude=item.get("latitude", 0),
            longitude=item.get("longitude", 0),
        )
        _airports_cache[airport.code] = airport
        # 同时支持城市名索引
        if airport.city not in _airports_cache:
            _airports_cache[airport.city] = airport

    logger.info(f"已加载 {len(_airports_cache)} 个机场数据")
    return _airports_cache


def _load_nearby_airports(range_km: int) -> dict:
    """加载指定范围的附近机场数据"""
    if range_km in _nearby_cache:
        return _nearby_cache[range_km]

    nearby_file = os.path.join(DATA_DIR, f"nearby-airports-{range_km}km.json")
    if not os.path.exists(nearby_file):
        logger.warning(f"附近机场数据文件不存在: {nearby_file}")
        return {}

    with open(nearby_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    _nearby_cache[range_km] = data
    logger.info(f"已加载 {range_km}km 范围附近机场数据")
    return data


def _load_flight_matrix() -> dict:
    """加载航班连接矩阵"""
    global _flight_matrix_cache
    if _flight_matrix_cache is not None:
        return _flight_matrix_cache

    matrix_file = os.path.join(FLIGHT_MATRIX_DIR, "flight-matrix.json")
    if not os.path.exists(matrix_file):
        logger.warning(f"航班矩阵数据文件不存在: {matrix_file}")
        return {}

    with open(matrix_file, "r", encoding="utf-8") as f:
        _flight_matrix_cache = json.load(f)

    logger.info(f"已加载航班矩阵数据")
    return _flight_matrix_cache


def lookup_airport(query: str) -> Optional[AirportInfo]:
    """根据城市名或机场代码查询机场信息"""
    airports = _load_airports()

    # 直接查找
    if query.upper() in airports:
        return airports[query.upper()]
    if query in airports:
        return airports[query]

    # 模糊匹配城市名
    query_lower = query.lower()
    for key, airport in airports.items():
        if isinstance(airport, AirportInfo):
            if query_lower in airport.city.lower() or query_lower in airport.name.lower():
                return airport

    return None


def get_nearby_airports(airport_code: str, range_km: int = 300) -> list[str]:
    """获取指定机场周围一定范围内的机场代码列表
    
    Args:
        airport_code: 机场代码（用户指定的主机场）
        range_km: 搜索范围（km），如果为0则只返回该机场本身
    
    Returns:
        机场代码列表（主机场在第一位）
    """
    airport_code = airport_code.upper()
    
    if range_km == 0:
        # 范围为0时只返回主机场
        return [airport_code]
    
    nearby_data = _load_nearby_airports(range_km)

    airport_info = nearby_data.get(airport_code)
    if airport_info:
        nearby_list = airport_info.get("nearby", [])
        # 确保主机场在第一位
        if airport_code in nearby_list:
            nearby_list.remove(airport_code)
        return [airport_code] + nearby_list

    return [airport_code]


def get_flight_matrix() -> dict:
    """获取航班连接矩阵"""
    return _load_flight_matrix()


def has_direct_flight(from_code: str, to_code: str) -> bool:
    """检查两个机场之间是否有直飞航班"""
    matrix = _load_flight_matrix()

    from_info = matrix.get(from_code.upper())
    if from_info:
        destinations = from_info.get("destinations", [])
        return to_code.upper() in destinations

    return True  # 如果没有数据，假设有航班


def filter_valid_combinations(
    departure_airports: list[str],
    arrival_airports: list[str],
    dates: list[str],
    max_combinations: int = 50,
) -> list[tuple[str, str, str]]:
    """
    过滤有效的航班组合
    
    根据航班矩阵数据：
    1. 只保留有航班连接的组合
    2. 按优先级排序（分数越高越优先）
    3. 取优先级最高的前 N 个组合
    
    优先级计算（分数越高越优先）：
    - 主机场：699（最优先）
    - 其他机场：航班数量
    
    组合分数 = 出发机场分数 + 到达机场分数
    
    Args:
        departure_airports: 出发机场列表（第一个是用户指定的主机场）
        arrival_airports: 到达机场列表（第一个是用户指定的主机场）
        dates: 日期列表
        max_combinations: 最大组合数
    
    Returns:
        排序后的有效组合列表 (dep, arr, date)
    """
    matrix = _load_flight_matrix()
    
    # 用户指定的主机场
    primary_dep = departure_airports[0].upper() if departure_airports else ""
    primary_arr = arrival_airports[0].upper() if arrival_airports else ""
    
    # 计算每个机场的优先级分数（越高越优先）
    def get_airport_score(code: str, primary_code: str) -> int:
        """获取机场优先级分数"""
        if code.upper() == primary_code:
            return 699  # 主机场最优先
        
        # 其他机场：航班数量
        airport_data = matrix.get(code.upper(), {})
        flight_count = airport_data.get('count', 0) or len(airport_data.get('destinations', []))
        return flight_count
    
    # 预计算所有机场的分数
    dep_scores = {code: get_airport_score(code, primary_dep) for code in departure_airports}
    arr_scores = {code: get_airport_score(code, primary_arr) for code in arrival_airports}
    
    valid_combos = []
    skipped_no_route = 0
    
    for dep in departure_airports:
        dep_info = matrix.get(dep.upper(), {})
        dep_dests = set(dep_info.get("destinations", []))
        
        for arr in arrival_airports:
            # 严格检查：没有航线数据 或 没有直飞航线 -> 跳过
            if dep_dests and arr.upper() not in dep_dests:
                skipped_no_route += 1
                continue
                
            for date in dates:
                # 组合优先级 = 出发分数 + 到达分数
                priority = dep_scores[dep] + arr_scores[arr]
                valid_combos.append((dep, arr, date, priority))
    
    # 按优先级降序排序（分数越高越优先）
    valid_combos.sort(key=lambda x: -x[3])
    
    # 限制组合数
    result = [(c[0], c[1], c[2]) for c in valid_combos[:max_combinations]]
    
    original_count = len(departure_airports) * len(arrival_airports) * len(dates)
    logger.info(f"航班矩阵过滤: 原始 {original_count} 组合 -> 有效 {len(valid_combos)} 组合（跳过 {skipped_no_route} 个无航线组合）")
    if len(valid_combos) > max_combinations:
        logger.info(f"按优先级取前 {max_combinations} 个组合")
    
    return result


def search_flights(
    page,
    params: SearchParams,
    skip_first_navigation: bool = False,
) -> SearchResult:
    """
    执行机票模糊搜索

    Args:
        page: CDP Page 对象
        params: 搜索参数
        skip_first_navigation: 是否跳过第一次导航（已在外部导航过）

    Returns:
        SearchResult: 搜索结果
    """
    # 1. 解析出发地和目的地
    departure_airport = lookup_airport(params.departure)
    destination_airport = lookup_airport(params.destination)

    if not departure_airport:
        return SearchResult(
            success=False,
            error=f"未找到出发地: {params.departure}",
        )

    if not destination_airport:
        return SearchResult(
            success=False,
            error=f"未找到目的地: {params.destination}",
        )

    # 2. 获取附近机场列表
    departure_airports = get_nearby_airports(departure_airport.code, params.departure_range)
    arrival_airports = get_nearby_airports(destination_airport.code, params.destination_range)

    logger.info(f"出发地 {params.departure} 附近 {params.departure_range}km 内机场: {departure_airports}")
    logger.info(f"目的地 {params.destination} 附近 {params.destination_range}km 内机场: {arrival_airports}")

    # 3. 生成日期列表
    dates = _get_date_range(params.date, params.date_end)

    # 4. 智能过滤有效组合（利用航班矩阵数据）
    combinations = filter_valid_combinations(
        departure_airports, 
        arrival_airports, 
        dates,
        max_combinations=50  # 最多50个组合
    )
    total_combinations = len(combinations)

    logger.info(f"总共 {total_combinations} 个搜索组合")

    # 5. 执行搜索
    all_flights: list[FlightInfo] = []
    searched = 0

    # 确定要搜索的平台
    if params.platform.lower() == "all":
        platform_names = list(PLATFORMS.keys())
    else:
        platform_names = [params.platform.lower()]

    first_search = True

    for platform_name in platform_names:
        handler = get_platform_handler(platform_name)
        if not handler:
            logger.warning(f"未知平台: {platform_name}")
            continue

        logger.info(f"使用平台: {handler.name}")

        for dep_code, arr_code, date in combinations:
            searched += 1

            # 获取机场对应的城市名称
            airports = _load_airports()
            dep_airport_info = airports.get(dep_code)
            arr_airport_info = airports.get(arr_code)
            
            dep_city = dep_airport_info.city if dep_airport_info else dep_code
            arr_city = arr_airport_info.city if arr_airport_info else arr_code

            logger.info(f"[{searched}/{total_combinations}] 搜索 {dep_city}({dep_code}) -> {arr_city}({arr_code}) ({date})")

            try:
                # 第一个搜索跳过导航（已在外部完成）
                if first_search and skip_first_navigation:
                    flights_data = handler.search_without_navigation(page, dep_city, arr_city, date)
                    first_search = False
                else:
                    # 传入城市名称而不是机场代码
                    flights_data = handler.search(page, dep_city, arr_city, date)

                for f in flights_data:
                    # 如果只要直飞，跳过中转航班
                    if params.direct_only and not f.get("is_direct", True):
                        continue
                    
                    flight = FlightInfo(
                        airline=f.get("airline", ""),
                        flight_no=f.get("flight_no", ""),
                        departure_code=dep_code,
                        departure_name=f.get("departure_airport", ""),
                        departure_city=dep_city,
                        arrival_code=arr_code,
                        arrival_name=f.get("arrival_airport", ""),
                        arrival_city=arr_city,
                        departure_time=f.get("departure_time", ""),
                        arrival_time=f.get("arrival_time", ""),
                        duration=f.get("duration", ""),
                        price=float(f.get("price", 0)),
                        is_direct=f.get("is_direct", True),
                        transfer_info=f.get("transfer_info", ""),
                        date=date,
                        platform=platform_name,
                    )
                    if flight.price > 0:
                        all_flights.append(flight)

            except Exception as e:
                logger.error(f"搜索 {dep_code} -> {arr_code} 失败: {e}")
                continue

            # 添加延迟避免频繁请求
            import time
            time.sleep(1.5)

    # 6. 排序并返回结果
    # 排序规则：直飞优先，然后按价格从低到高
    all_flights.sort(key=lambda x: (not x.is_direct, x.price))
    
    # 如果只要直飞，过滤掉中转航班
    if params.direct_only:
        all_flights = [f for f in all_flights if f.is_direct]
        logger.info(f"直飞筛选后剩余 {len(all_flights)} 个航班")
    
    top_flights = all_flights[:params.top_n]

    return SearchResult(
        success=True,
        flights=top_flights,
        departure_airports=departure_airports,
        arrival_airports=arrival_airports,
        total_combinations=total_combinations,
        searched_combinations=searched,
        platform=params.platform,
    )


def _get_date_range(start_date: str, end_date: str = "") -> list[str]:
    """生成日期范围列表"""
    dates = []

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")

        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d")
        else:
            end = start

        current = start
        while current <= end:
            dates.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)

    except ValueError as e:
        logger.error(f"日期格式错误: {e}")
        dates = [start_date]

    return dates


def format_search_result(result: SearchResult) -> str:
    """格式化搜索结果为可读文本"""
    if not result.success:
        return f"搜索失败: {result.error}"

    lines = []
    lines.append("=" * 60)
    lines.append("机票搜索结果（按价格排序）")
    lines.append("=" * 60)
    lines.append(f"出发地附近机场: {', '.join(result.departure_airports)}")
    lines.append(f"目的地附近机场: {', '.join(result.arrival_airports)}")
    lines.append(f"搜索组合数: {result.total_combinations}")
    lines.append(f"搜索平台: {result.platform}")
    lines.append("")

    if not result.flights:
        lines.append("未找到符合条件的航班")
        return "\n".join(lines)

    lines.append(f"=== 前 {len(result.flights)} 个最低价航班 ===")
    lines.append("")

    for i, flight in enumerate(result.flights, 1):
        direct_text = "直飞" if flight.is_direct else f"中转({flight.transfer_info})"
        lines.append(f"{i}. ¥{flight.price} | {flight.date} {flight.departure_time}")
        lines.append(f"   {flight.departure_code}→{flight.arrival_code} | {flight.airline} {flight.flight_no} | {direct_text}")
        lines.append(f"   飞行时长: {flight.duration}")
        lines.append("")

    return "\n".join(lines)


def smart_route_planning(
    result: SearchResult,
    departure_city: str,
    destination_city: str,
) -> dict:
    """
    智能路线规划

    根据搜索结果，结合地面交通成本，给出最优出行方案

    Args:
        result: 搜索结果
        departure_city: 出发城市
        destination_city: 目的地城市

    Returns:
        dict: 包含最优方案的规划结果
    """
    from .ground_transport import calculate_total_journey, format_journey_plan

    if not result.success or not result.flights:
        return {
            "success": False,
            "error": result.error or "没有可用的航班数据",
        }

    # 计算每个航班的完整行程成本
    plans = []
    for flight in result.flights:
        # 解析飞行时长
        duration_str = flight.duration
        flight_minutes = _parse_duration(duration_str)

        journey = calculate_total_journey(
            departure_city=departure_city,
            departure_airport_code=flight.departure_code,
            arrival_airport_code=flight.arrival_code,
            destination_city=destination_city,
            flight_price=flight.price,
            flight_duration_minutes=flight_minutes,
        )

        plans.append({
            "flight": flight,
            "journey": journey,
            "total_cost": journey["summary"]["total_cost"],
            "total_duration": journey["summary"]["total_duration_minutes"],
        })

    # 按总成本排序
    plans.sort(key=lambda x: x["total_cost"])

    # 找出最优方案
    cheapest = plans[0] if plans else None
    fastest = min(plans, key=lambda x: x["total_duration"]) if plans else None

    # 找出直飞方案（如果有）
    direct_plans = [p for p in plans if p["flight"].is_direct]
    best_direct = direct_plans[0] if direct_plans else None

    return {
        "success": True,
        "plans": plans,
        "cheapest": cheapest,
        "fastest": fastest,
        "best_direct": best_direct,
        "summary": {
            "total_plans": len(plans),
            "cheapest_cost": cheapest["total_cost"] if cheapest else 0,
            "fastest_duration": fastest["total_duration"] if fastest else 0,
        }
    }


def _parse_duration(duration_str: str) -> int:
    """解析飞行时长字符串，返回分钟数"""
    if not duration_str:
        return 120  # 默认2小时

    # 尝试解析 "2h30m" 或 "2小时30分" 格式
    import re

    # 匹配 "2h30m" 格式
    match = re.match(r"(\d+)h(\d+)m", duration_str)
    if match:
        return int(match.group(1)) * 60 + int(match.group(2))

    # 匹配 "2小时30分" 格式
    match = re.match(r"(\d+)小时(\d+)分", duration_str)
    if match:
        return int(match.group(1)) * 60 + int(match.group(2))

    # 匹配 "2小时" 格式
    match = re.match(r"(\d+)小时", duration_str)
    if match:
        return int(match.group(1)) * 60

    # 匹配 "150分钟" 格式
    match = re.match(r"(\d+)分钟", duration_str)
    if match:
        return int(match.group(1))

    return 120  # 默认2小时


def format_smart_planning(planning: dict, departure_city: str, destination_city: str) -> str:
    """格式化智能规划结果为可读文本"""
    if not planning.get("success"):
        return f"规划失败: {planning.get('error', '未知错误')}"

    lines = []
    lines.append("=" * 60)
    lines.append("智能出行规划")
    lines.append("=" * 60)
    lines.append(f"出发地: {departure_city}")
    lines.append(f"目的地: {destination_city}")
    lines.append("")

    cheapest = planning.get("cheapest")
    fastest = planning.get("fastest")
    best_direct = planning.get("best_direct")

    # 最省钱方案
    if cheapest:
        lines.append("💰 最省钱方案")
        lines.append("-" * 40)
        flight = cheapest["flight"]
        journey = cheapest["journey"]
        summary = journey["summary"]

        lines.append(f"  航班: {flight.airline} {flight.flight_no}")
        lines.append(f"  航线: {flight.departure_code}({flight.departure_name}) → {flight.arrival_code}({flight.arrival_name})")
        lines.append(f"  时间: {flight.date} {flight.departure_time} - {flight.arrival_time}")
        lines.append(f"  机票价格: ¥{flight.price}")
        lines.append(f"  地面交通: ¥{summary['ground_cost']}")
        lines.append(f"  总费用: ¥{summary['total_cost']}")
        lines.append(f"  总耗时: 约{summary['total_duration_hours']}小时")

        # 如果是最省钱的，显示相比直飞节省了多少
        if best_direct and cheapest != best_direct:
            save = best_direct["total_cost"] - cheapest["total_cost"]
            lines.append(f"  相比直飞节省: ¥{save}")
        lines.append("")

    # 最快方案
    if fastest and fastest != cheapest:
        lines.append("⏱️ 最快方案")
        lines.append("-" * 40)
        flight = fastest["flight"]
        journey = fastest["journey"]
        summary = journey["summary"]

        lines.append(f"  航班: {flight.airline} {flight.flight_no}")
        lines.append(f"  航线: {flight.departure_code} → {flight.arrival_code}")
        lines.append(f"  时间: {flight.date} {flight.departure_time} - {flight.arrival_time}")
        lines.append(f"  总费用: ¥{summary['total_cost']}")
        lines.append(f"  总耗时: 约{summary['total_duration_hours']}小时")
        lines.append("")

    # 直飞方案
    if best_direct and best_direct != cheapest:
        lines.append("✈️ 直飞方案")
        lines.append("-" * 40)
        flight = best_direct["flight"]
        journey = best_direct["journey"]
        summary = journey["summary"]

        lines.append(f"  航班: {flight.airline} {flight.flight_no}")
        lines.append(f"  航线: {flight.departure_code} → {flight.arrival_code}")
        lines.append(f"  时间: {flight.date} {flight.departure_time} - {flight.arrival_time}")
        lines.append(f"  总费用: ¥{summary['total_cost']}")
        lines.append("")

    # 推荐
    lines.append("🎯 推荐方案")
    lines.append("-" * 40)
    if cheapest and best_direct:
        save = best_direct["total_cost"] - cheapest["total_cost"]
        if save > 100:
            lines.append(f"  推荐「曲线方案」: 飞{cheapest['flight'].arrival_code}再转地面交通")
            lines.append(f"  理由: 节省¥{save}，性价比最高")
        else:
            lines.append("  推荐「直飞方案」: 省心省力，价格差距不大")
    elif cheapest:
        lines.append(f"  推荐方案: {cheapest['flight'].airline} {cheapest['flight'].flight_no}")
        lines.append(f"  总费用: ¥{cheapest['total_cost']}")

    return "\n".join(lines)
