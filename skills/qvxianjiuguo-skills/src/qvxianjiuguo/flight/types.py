"""机票搜索相关数据类型"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AirportInfo:
    """机场信息"""
    code: str  # IATA代码，如 CKG
    name: str  # 机场全名，如 重庆江北国际机场
    city: str  # 城市名，如 重庆
    province: str  # 省份，如 重庆
    region: str  # 地区，如 西南地区
    latitude: float  # 纬度
    longitude: float  # 经度

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "name": self.name,
            "city": self.city,
            "province": self.province,
            "region": self.region,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }


@dataclass
class FlightInfo:
    """航班信息"""
    airline: str  # 航空公司
    flight_no: str  # 航班号
    departure_code: str  # 出发机场代码
    departure_name: str  # 出发机场名称
    departure_city: str  # 出发城市
    arrival_code: str  # 到达机场代码
    arrival_name: str  # 到达机场名称
    arrival_city: str  # 到达城市
    departure_time: str  # 出发时间
    arrival_time: str  # 到达时间
    duration: str  # 飞行时长
    price: float  # 价格
    is_direct: bool = True  # 是否直飞
    transfer_info: str = ""  # 中转信息
    date: str = ""  # 航班日期
    platform: str = ""  # 搜索平台
    url: str = ""  # 航班详情链接

    def to_dict(self) -> dict:
        return {
            "airline": self.airline,
            "flight_no": self.flight_no,
            "departure_code": self.departure_code,
            "departure_name": self.departure_name,
            "departure_city": self.departure_city,
            "arrival_code": self.arrival_code,
            "arrival_name": self.arrival_name,
            "arrival_city": self.arrival_city,
            "departure_time": self.departure_time,
            "arrival_time": self.arrival_time,
            "duration": self.duration,
            "price": self.price,
            "is_direct": self.is_direct,
            "transfer_info": self.transfer_info,
            "date": self.date,
            "platform": self.platform,
            "url": self.url,
        }


@dataclass
class SearchResult:
    """搜索结果"""
    success: bool
    flights: list[FlightInfo] = field(default_factory=list)
    error: str = ""
    departure_airports: list[str] = field(default_factory=list)
    arrival_airports: list[str] = field(default_factory=list)
    total_combinations: int = 0
    searched_combinations: int = 0
    platform: str = ""

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "flights": [f.to_dict() for f in self.flights],
            "error": self.error,
            "departure_airports": self.departure_airports,
            "arrival_airports": self.arrival_airports,
            "total_combinations": self.total_combinations,
            "searched_combinations": self.searched_combinations,
            "platform": self.platform,
        }


@dataclass
class SearchParams:
    """搜索参数"""
    departure: str  # 出发地（城市名或机场代码）
    destination: str  # 目的地（城市名或机场代码）
    date: str  # 出发日期 YYYY-MM-DD
    date_end: str = ""  # 结束日期（日期范围搜索）
    platform: str = "qunar"  # 平台：qunar, ctrip, fliggy, ly, all
    departure_range: int = 350  # 出发地搜索范围（km）
    destination_range: int = 300  # 目的地搜索范围（km）
    direct_only: bool = True  # 只搜索直飞（默认只看直飞）
    top_n: int = 10  # 返回前N个最低价航班

    def to_dict(self) -> dict:
        return {
            "departure": self.departure,
            "destination": self.destination,
            "date": self.date,
            "date_end": self.date_end,
            "platform": self.platform,
            "departure_range": self.departure_range,
            "destination_range": self.destination_range,
            "direct_only": self.direct_only,
            "top_n": self.top_n,
        }
