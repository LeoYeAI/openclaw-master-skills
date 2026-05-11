from ..types import (TypeHedgeFlag, TypeOffsetFlag, TypeOrderDirection, TypeOrderPriceType,
                     TypeOrderStatus)
from .common import ObjDataType


class BaseOrderData(object):
    """基础报单类"""

    def __init__(self, data: ObjDataType = {}) -> None:
        self._exchange = data.get("Exchange", "")
        self._instrument_id = data.get("InstrumentID", "")
        self._price = data.get("Price", 0.0)
        self._order_id = data.get("OrderID", -1)
        self._order_sys_id = data.get("OrderSysID", "")
        self._order_price_type = data.get("OrderPriceType", "")
        self._direction = data.get("Direction", "")
        self._offset = data.get("Offset", "")
        self._hedgeflag = data.get("Hedgeflag", "")
        self._cancel_volume = data.get("CancelVolume", 0)
        self._cancel_time = data.get("CancelTime", "")
        self._front_id = data.get("FrontID", 0)
        self._session_id = data.get("SessionID", 0)
        self._memo = data.get("Memo", "")
        self._order_time = data.get("OrderTime", "")

    @property
    def exchange(self) -> str:
        """交易所代码"""
        return self._exchange

    @property
    def instrument_id(self) -> str:
        """合约代码"""
        return self._instrument_id

    @property
    def price(self) -> float:
        """报单价格"""
        return self._price

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
    def order_price_type(self) -> TypeOrderPriceType:
        """
        报单价格类型

        Note:
            '1' 任意价, '2' 限价, '3' 最优价, '4' 五档价
        """
        return self._order_price_type

    @property
    def cancel_volume(self) -> int:
        """撤单数量"""
        return self._cancel_volume

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
    def front_id(self) -> int:
        """前置编号"""
        return self._front_id

    @property
    def session_id(self) -> int:
        """会话编号"""
        return self._session_id

    @property
    def cancel_time(self) -> str:
        """
        撤单时间

        Note:
            应该为空值，需要无限易判断
            sprintf(canceltime,"%s %s",pNewOrder->TradingDay,pNewOrder->CancelTime);
        """
        return self._cancel_time

    @property
    def memo(self) -> str:
        """报单备注"""
        return self._memo

    @property
    def order_time(self) -> str:
        """
        报单时间
        
        Note:
            格式为 `yyyymmdd hh:mm:ss`
        """
        return self._order_time

    def _as_dict(self) -> dict:
        return {
            "exchange": self._exchange,
            "instrument_id": self._instrument_id,
            "order_id": self._order_id,
            "order_sys_id": self.order_sys_id,
            "price": self._price,
            "order_price_type": self._order_price_type,
            "cancel_volume": self._cancel_volume,
            "direction": self._direction,
            "offset": self._offset,
            "hedgeflag": self._hedgeflag,
            "memo": self._memo,
            "front_id": self._front_id,
            "session_id": self._session_id,
            "cancel_time": self._cancel_time,
            "order_time": self._order_time,
        }

    def __repr__(self) -> str:
        return str(self._as_dict())


class OrderData(BaseOrderData):
    """报单数据类"""

    def __init__(self, data: ObjDataType = {}) -> None:
        super().__init__(data)
        self._total_volume = data.get("TotalVolume", 0)
        self._traded_volume = data.get("TradedVolume", 0)
        self._status = data.get("Status", "")

    @property
    def total_volume(self) -> int:
        """报单数量"""
        return self._total_volume

    @property
    def traded_volume(self) -> int:
        """已经成交数量"""
        return self._traded_volume

    @property
    def status(self) -> TypeOrderStatus:
        """报单状态"""
        return self._status

    def _as_dict(self) -> dict:
        parent_dict = super()._as_dict()

        parent_dict.update({
            "total_volume": self._total_volume,
            "traded_volume": self._traded_volume,
            "status": self._status
        })

        return parent_dict

class CancelOrderData(BaseOrderData):
    """撤单数据类"""

    def __init__(self, data: ObjDataType = {}) -> None:
        super().__init__(data)
