"""地面交通成本计算模块

用于计算出发地市区到机场、机场到目的地的地面交通成本。
支持地铁、机场大巴、高铁等方式。
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import logging

logger = logging.getLogger("flight-search")


@dataclass
class GroundTransport:
    """地面交通信息"""
    from_location: str  # 出发地
    to_location: str  # 目的地
    transport_type: str  # 交通方式：地铁/大巴/高铁/磁悬浮
    distance_km: float  # 距离(km)
    duration_minutes: int  # 耗时(分钟)
    cost_yuan: float  # 费用(元)
    note: str = ""  # 备注

    def to_dict(self) -> dict:
        return {
            "from": self.from_location,
            "to": self.to_location,
            "type": self.transport_type,
            "distance_km": self.distance_km,
            "duration_minutes": self.duration_minutes,
            "cost_yuan": self.cost_yuan,
            "note": self.note,
        }


# 主要城市市区到机场的交通数据
CITY_TO_AIRPORT: dict[str, dict[str, GroundTransport]] = {
    "重庆": {
        "CKG": GroundTransport("重庆市区", "重庆江北机场", "地铁3号线", 30, 40, 15, "机场直达"),
    },
    "北京": {
        "PEK": GroundTransport("北京市区", "首都机场", "机场快轨", 25, 40, 25, "东直门出发"),
        "PKX": GroundTransport("北京市区", "大兴机场", "机场快轨", 50, 60, 35, "草桥出发"),
    },
    "上海": {
        "SHA": GroundTransport("上海市区", "虹桥机场", "地铁2/10号线", 15, 30, 5, "人民广场出发"),
        "PVG": GroundTransport("上海市区", "浦东机场", "磁悬浮/地铁", 40, 25, 50, "龙阳路换乘磁悬浮"),
    },
    "广州": {
        "CAN": GroundTransport("广州市区", "白云机场", "地铁3号线", 30, 40, 8, "机场北直达"),
    },
    "深圳": {
        "SZX": GroundTransport("深圳市区", "宝安机场", "地铁11号线", 35, 45, 7, "福田出发"),
    },
    "成都": {
        "CTU": GroundTransport("成都市区", "双流机场", "地铁10号线", 18, 30, 5, "太平园换乘"),
        "TFU": GroundTransport("成都市区", "天府机场", "地铁18号线", 50, 50, 10, "火车南站出发"),
    },
    "杭州": {
        "HGH": GroundTransport("杭州市区", "萧山机场", "地铁1号线", 30, 45, 7, "城站出发"),
    },
    "南京": {
        "NKG": GroundTransport("南京市区", "禄口机场", "地铁S1号线", 40, 40, 7, "南京南站出发"),
    },
    "武汉": {
        "WUH": GroundTransport("武汉市区", "天河机场", "地铁2号线", 25, 35, 7, "汉口火车站出发"),
    },
    "西安": {
        "XIY": GroundTransport("西安市区", "咸阳机场", "地铁14号线", 40, 45, 8, "北客站出发"),
    },
    "昆明": {
        "KMG": GroundTransport("昆明市区", "长水机场", "地铁6号线", 30, 40, 6, "东部汽车站出发"),
    },
    "长沙": {
        "CSX": GroundTransport("长沙市区", "黄花机场", "磁浮快线", 25, 30, 20, "长沙南站换乘"),
    },
    "郑州": {
        "CGO": GroundTransport("郑州市区", "新郑机场", "城郊线", 35, 40, 7, "郑州东站出发"),
    },
    "天津": {
        "TSN": GroundTransport("天津市区", "滨海机场", "地铁2号线", 20, 30, 5, "天津站出发"),
    },
    "青岛": {
        "TAO": GroundTransport("青岛市区", "胶东机场", "地铁8号线", 50, 50, 8, "青岛北站出发"),
    },
    "厦门": {
        "XMN": GroundTransport("厦门市区", "高崎机场", "地铁1号线", 15, 25, 5, "莲坂出发"),
    },
    "大连": {
        "DLC": GroundTransport("大连市区", "周水子机场", "地铁2号线", 12, 20, 4, "西安路出发"),
    },
    "沈阳": {
        "SHE": GroundTransport("沈阳市区", "桃仙机场", "有轨电车", 20, 35, 5, "奥体中心出发"),
    },
    "哈尔滨": {
        "HRB": GroundTransport("哈尔滨市区", "太平机场", "机场大巴", 40, 50, 20, "火车站出发"),
    },
    "乌鲁木齐": {
        "URC": GroundTransport("乌鲁木齐市区", "地窝堡机场", "机场大巴", 20, 30, 15, "火车站出发"),
    },
    "三亚": {
        "SYX": GroundTransport("三亚市区", "凤凰机场", "高铁", 15, 15, 15, "三亚站出发"),
    },
    "海口": {
        "HAK": GroundTransport("海口市区", "美兰机场", "高铁", 25, 20, 15, "海口东站出发"),
    },
}

# 机场到附近城市的交通数据
AIRPORT_TO_CITY: dict[str, dict[str, GroundTransport]] = {
    # 唐山
    "TVS": {
        "秦皇岛": GroundTransport("唐山机场", "秦皇岛市区", "机场大巴", 100, 120, 50, "直达大巴"),
        "唐山": GroundTransport("唐山机场", "唐山市区", "机场大巴", 20, 30, 20, ""),
    },
    # 天津
    "TSN": {
        "北京": GroundTransport("天津机场", "北京市区", "高铁", 140, 45, 55, "天津站-北京南"),
        "天津": GroundTransport("天津机场", "天津市区", "地铁2号线", 20, 30, 5, ""),
    },
    # 北京
    "PEK": {
        "北京": GroundTransport("首都机场", "北京市区", "机场快轨", 25, 40, 25, ""),
        "天津": GroundTransport("首都机场", "天津市区", "高铁", 120, 50, 55, "北京站-天津"),
    },
    "PKX": {
        "北京": GroundTransport("大兴机场", "北京市区", "机场快轨", 50, 60, 35, ""),
        "天津": GroundTransport("大兴机场", "天津市区", "高铁", 100, 40, 50, "大兴机场站直达"),
    },
    # 石家庄
    "SJW": {
        "石家庄": GroundTransport("正定机场", "石家庄市区", "高铁", 50, 20, 25, "正定机场站"),
        "北京": GroundTransport("正定机场", "北京市区", "高铁", 280, 60, 128, "正定机场站-北京西"),
    },
    # 广州
    "CAN": {
        "广州": GroundTransport("白云机场", "广州市区", "地铁3号线", 30, 40, 8, ""),
        "深圳": GroundTransport("白云机场", "深圳市区", "高铁", 160, 50, 75, "广州南-深圳北"),
        "珠海": GroundTransport("白云机场", "珠海市区", "城际", 130, 70, 70, "广州南-珠海"),
        "佛山": GroundTransport("白云机场", "佛山市区", "地铁/城际", 50, 60, 20, ""),
    },
    # 深圳
    "SZX": {
        "深圳": GroundTransport("宝安机场", "深圳市区", "地铁11号线", 35, 45, 7, ""),
        "广州": GroundTransport("宝安机场", "广州市区", "高铁", 160, 50, 75, "深圳北-广州南"),
        "香港": GroundTransport("宝安机场", "香港市区", "跨境巴士", 50, 90, 150, ""),
        "东莞": GroundTransport("宝安机场", "东莞市区", "城际", 60, 50, 40, ""),
    },
    # 成都
    "CTU": {
        "成都": GroundTransport("双流机场", "成都市区", "地铁10号线", 18, 30, 5, ""),
        "重庆": GroundTransport("双流机场", "重庆市区", "高铁", 300, 90, 154, "成都东-重庆北"),
    },
    "TFU": {
        "成都": GroundTransport("天府机场", "成都市区", "地铁18号线", 50, 50, 10, ""),
        "重庆": GroundTransport("天府机场", "重庆市区", "高铁", 320, 100, 154, ""),
    },
    # 重庆
    "CKG": {
        "重庆": GroundTransport("江北机场", "重庆市内", "地铁3号线", 30, 40, 15, ""),
        "成都": GroundTransport("江北机场", "成都市内", "高铁", 300, 90, 154, "重庆北-成都东"),
    },
    # 杭州
    "HGH": {
        "杭州": GroundTransport("萧山机场", "杭州市区", "地铁1号线", 30, 45, 7, ""),
        "上海": GroundTransport("萧山机场", "上海市区", "高铁", 180, 60, 73, "杭州东-上海虹桥"),
        "绍兴": GroundTransport("萧山机场", "绍兴市区", "城际", 60, 40, 20, ""),
    },
    # 南京
    "NKG": {
        "南京": GroundTransport("禄口机场", "南京市区", "地铁S1号线", 40, 40, 7, ""),
        "上海": GroundTransport("禄口机场", "上海市区", "高铁", 300, 60, 134, "南京南-上海虹桥"),
        "扬州": GroundTransport("禄口机场", "扬州市区", "大巴", 100, 90, 40, ""),
    },
    # 西安
    "XIY": {
        "西安": GroundTransport("咸阳机场", "西安市区", "地铁14号线", 40, 45, 8, ""),
        "郑州": GroundTransport("咸阳机场", "郑州市区", "高铁", 500, 120, 240, "西安北-郑州东"),
    },
    # 武汉
    "WUH": {
        "武汉": GroundTransport("天河机场", "武汉市区", "地铁2号线", 25, 35, 7, ""),
        "长沙": GroundTransport("天河机场", "长沙市区", "高铁", 350, 90, 165, "武汉-长沙南"),
    },
}


def get_city_to_airport(city: str, airport_code: str) -> Optional[GroundTransport]:
    """获取城市市区到机场的交通信息"""
    city_data = CITY_TO_AIRPORT.get(city)
    if city_data:
        return city_data.get(airport_code)
    return None


def get_airport_to_city(airport_code: str, city: str) -> Optional[GroundTransport]:
    """获取机场到城市市区的交通信息"""
    airport_data = AIRPORT_TO_CITY.get(airport_code)
    if airport_data:
        return airport_data.get(city)
    return None


def estimate_ground_transport(
    from_city: str,
    to_airport_code: str,
    is_departure: bool = True
) -> GroundTransport:
    """
    估算地面交通成本

    Args:
        from_city: 城市名
        to_airport_code: 机场代码
        is_departure: True=出发地到机场, False=机场到目的地

    Returns:
        GroundTransport对象
    """
    if is_departure:
        # 出发地市区 → 起飞机场
        transport = get_city_to_airport(from_city, to_airport_code)
        if transport:
            return transport
        # 未找到数据，使用默认估算
        return GroundTransport(
            from_location=f"{from_city}市区",
            to_location=f"{to_airport_code}机场",
            transport_type="机场大巴",
            distance_km=30,
            duration_minutes=45,
            cost_yuan=25,
            note="估算值"
        )
    else:
        # 到达机场 → 目的地市区
        transport = get_airport_to_city(to_airport_code, from_city)
        if transport:
            return transport
        # 未找到数据，使用默认估算
        return GroundTransport(
            from_location=f"{to_airport_code}机场",
            to_location=f"{from_city}市区",
            transport_type="机场大巴",
            distance_km=30,
            duration_minutes=45,
            cost_yuan=25,
            note="估算值"
        )


def calculate_total_journey(
    departure_city: str,
    departure_airport_code: str,
    arrival_airport_code: str,
    destination_city: str,
    flight_price: float,
    flight_duration_minutes: int = 120,
) -> dict:
    """
    计算完整行程的总成本和总耗时

    Returns:
        dict: 包含各段交通信息和总成本
    """
    # 出发地市区 → 起飞机场
    to_airport = estimate_ground_transport(departure_city, departure_airport_code, is_departure=True)

    # 到达机场 → 目的地市区
    from_airport = estimate_ground_transport(destination_city, arrival_airport_code, is_departure=False)

    # 计算总成本和总耗时
    ground_cost = to_airport.cost_yuan + from_airport.cost_yuan
    ground_duration = to_airport.duration_minutes + from_airport.duration_minutes
    total_cost = ground_cost + flight_price
    total_duration = ground_duration + flight_duration_minutes + 90  # 加90分钟候机时间

    return {
        "to_airport": to_airport.to_dict(),
        "flight": {
            "from": departure_airport_code,
            "to": arrival_airport_code,
            "price": flight_price,
            "duration_minutes": flight_duration_minutes,
        },
        "from_airport": from_airport.to_dict(),
        "summary": {
            "ground_cost": ground_cost,
            "flight_cost": flight_price,
            "total_cost": total_cost,
            "ground_duration_minutes": ground_duration,
            "flight_duration_minutes": flight_duration_minutes,
            "total_duration_minutes": total_duration,
            "total_duration_hours": round(total_duration / 60, 1),
        }
    }


def format_journey_plan(plan: dict) -> str:
    """格式化行程规划为可读文本"""
    lines = []
    lines.append("=" * 50)
    lines.append("行程规划")
    lines.append("=" * 50)

    # 第一段：市区到机场
    to_airport = plan["to_airport"]
    lines.append(f"\n📍 第1段：{to_airport['from']} → {to_airport['to']}")
    lines.append(f"   交通：{to_airport['type']}")
    lines.append(f"   耗时：{to_airport['duration_minutes']}分钟")
    lines.append(f"   费用：¥{to_airport['cost_yuan']}")

    # 第二段：航班
    flight = plan["flight"]
    lines.append(f"\n✈️ 第2段：{flight['from']} → {flight['to']}")
    lines.append(f"   价格：¥{flight['price']}")
    lines.append(f"   飞行时间：{flight['duration_minutes']}分钟")

    # 第三段：机场到市区
    from_airport = plan["from_airport"]
    lines.append(f"\n📍 第3段：{from_airport['from']} → {from_airport['to']}")
    lines.append(f"   交通：{from_airport['type']}")
    lines.append(f"   耗时：{from_airport['duration_minutes']}分钟")
    lines.append(f"   费用：¥{from_airport['cost_yuan']}")

    # 汇总
    summary = plan["summary"]
    lines.append("\n" + "-" * 50)
    lines.append("📊 行程汇总")
    lines.append(f"   地面交通费用：¥{summary['ground_cost']}")
    lines.append(f"   机票费用：¥{summary['flight_cost']}")
    lines.append(f"   总费用：¥{summary['total_cost']}")
    lines.append(f"   总耗时：约{summary['total_duration_hours']}小时")

    return "\n".join(lines)
