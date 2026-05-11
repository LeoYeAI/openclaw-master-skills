
from ..types import TypeHedgeFlag, TypeOffsetFlag, TypeOrderDirection
from .common import ObjDataType


class TradeData(object):
    """成交数据类"""

    def __init__(self, data: ObjDataType = {}) -> None:
        self._exchange = data.get("Exchange", "")
        self._instrument_id = data.get("InstrumentID", "")
        self._trade_id = data.get("TradeID", "")
        self._order_id = data.get("OrderID", -1)
        self._order_sys_id = data.get("OrderSysID", "")
        self._trade_time = data.get("TradeTime", "")
        self._direction = data.get("Direction", "")
        self._offset = data.get("Offset", "")
        self._hedgeflag = data.get("Hedgeflag", "")
        self._price = data.get("Price", 0.0)
        self._volume = data.get("Volume", 0)
        self._memo = data.get("Memo", "")

    def __repr__(self) -> str:
        return str(
            {
                "exchange": self._exchange,
                "instrument_id": self._instrument_id,
                "trade_id": self.trade_id,
                "order_id": self._order_id,
                "order_sys_id": self.order_sys_id,
                "trade_time": self._trade_time,
                "direction": self._direction,
                "offset": self._offset,
                "hedgeflag": self._hedgeflag,
                "price": self._price,
                "volume": self._volume,
                "memo": self._memo,
            }
        )

    @property
    def exchange(self) -> str:
        """交易所代码"""
        return self._exchange

    @property
    def instrument_id(self) -> str:
        """合约代码"""
        return self._instrument_id

    @property
    def trade_id(self) -> str:
        """成交编号"""
        return self._trade_id.strip()

    @property
    def order_id(self) -> int:
        """
        报单编号

        Note:
            本地自增
        """
        return self._order_id

    @property
    def order_sys_id(self) -> str:
        """交易所报单编号"""
        return self._order_sys_id.replace(" ", "")

    @property
    def trade_time(self) -> str:
        """
        成交时间

        Note:
            格式为 `yyyymmdd hh:mm:ss`
        """
        return self._trade_time

    @property
    def direction(self) -> TypeOrderDirection:
        """买卖方向"""
        return self._direction

    @property
    def offset(self) -> TypeOffsetFlag:
        """开平标志"""
        return self._offset

    @property
    def hedgeflag(self) -> TypeHedgeFlag:
        """投机套保标志"""
        return self._hedgeflag

    @property
    def price(self) -> float:
        """成交价格"""
        return self._price

    @property
    def volume(self) -> int:
        """成交数量"""
        return self._volume

    @property
    def memo(self) -> str:
        """报单备注"""
        return self._memo
