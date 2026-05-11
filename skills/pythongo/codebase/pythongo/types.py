from datetime import datetime
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from .classdef import InstrumentData

type TypeDateTime = datetime
"""时间类型"""

type TypeProduct = Literal["1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "h"]
"""
品种类型

Note:
    https://infinitrader.quantdo.com.cn/pythongo_v2/faq/mapping#productclasstype
"""

type TypeInstResult = dict[TypeProduct, list["InstrumentData" | str]]
"""合约信息数据类型"""

type TypeOrderDIR = Literal["buy", "sell"]
"""报单方向"""

type TypeHedgeFlag = Literal["1", "2", "3", "4", "5"]
"""
投机套保标志

Note:
    https://infinitrader.quantdo.com.cn/pythongo_v2/faq/mapping#hedgeflagtype
"""

type TypeOrderFlag = Literal["GFD", "FAK", "FOK"]
"""报单指令"""

type TypeOffsetFlag = Literal["0", "1", "3"]
"""
开平标志

Note:
    https://infinitrader.quantdo.com.cn/pythongo_v2/faq/mapping#offsetflagtype
"""

type TypeOrderPriceType = Literal["1", "2", "3", "4"]
"""
报单价格类型

Note:
    https://infinitrader.quantdo.com.cn/pythongo_v2/faq/mapping#orderpricetype
"""

type TypeOrderStatus = Literal[
    "未知",
    "未成交",
    "全部成交",
    "部分成交",
    "部成部撤",
    "已撤销",
    "已报入未应答",
    "部分撤单还在队列中",
    "部成部撤还在队列中",
    "待报入",
    "投顾报单",
    "投资经理驳回",
    "投资经理通过",
    "交易员已报入",
    "交易员驳回"
]
"""报单状态"""

type TypeOrderDirection = Literal["0", "1"]
"""
买卖方向类型

Note:
    https://infinitrader.quantdo.com.cn/pythongo_v2/faq/mapping#directiontype
"""
