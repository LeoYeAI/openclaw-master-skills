from dataclasses import dataclass
from enum import Enum, StrEnum

PRODUCT_MAP = {
    "1": "期货",
    "2": "期权",
    "3": "组合",
    "4": "即期",
    "5": "期转现",
    "6": "未知类型",
    "7": "证券",
    "8": "股票期权",
    "9": "金交所现货",
    "a": "金交所递延",
    "b": "金交所远期",
    "h": "现货期权"
}

OPTION_MAP = {"1": "CALL", "2": "PUT"}

ORDER_TYPE_MAP = {
    "GFD": "0",
    "FAK": "1",
    "FOK": "2"
}


@dataclass
class OrderDirectionDataMixin(object):
    """数据扩展"""
    flag: str
    """值"""

    match_direction: str
    """匹配持仓方向"""

class OrderDirectionEnum(OrderDirectionDataMixin, Enum):
    """买卖方向枚举值"""
    BUY = "0", "short"
    """买"""

    SELL = "1", "long"
    """卖"""


class OrderOffsetEnum(StrEnum):
    """开平标志"""
    OPEN = "0"
    """开仓"""

    CLOSE = "1"
    """平仓"""

    CLOSE_TODAY = "3"
    """平今仓"""


class StatusCode(object):
    """与无限易客户端交互状态码"""
    STOP = 20001
