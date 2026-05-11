import threading # noqa
from copy import copy
from typing import ClassVar

from pythongo.types import TypeDateTime

from .common import ObjDataType


class TickData(object):
    """行情切片数据类"""
    _last_total_volume: ClassVar[dict[str, int]] = {}

    def __init__(self, data: ObjDataType = {}) -> None:
        self._exchange = data.get("Exchange", "")
        self._instrument_id = data.get("InstrumentID", "")
        self._last_price = data.get("LastPrice", 0.0)
        self._open_price = data.get("OpenPrice", 0.0)
        self._high_price = data.get("HighPrice", 0.0)
        self._low_price = data.get("LowPrice", 0.0)
        self._volume = data.get("Volume", 0)
        self._pre_close_price = data.get("PreClosePrice", 0.0)
        self._pre_settlement_price = data.get("PreSettlementPrice", 0.0)
        self._open_interest = data.get("OpenInterest", 0)
        self._upper_limit_price = data.get("UpperLimitPrice", 0.0)
        self._lower_limit_price = data.get("LowerLimitPrice", 0.0)
        self._turnover = data.get("Turnover", 0.0)
        self._bid_price1 = data.get("BidPrice1", 0.0)
        self._bid_price2 = data.get("BidPrice2", 0.0)
        self._bid_price3 = data.get("BidPrice3", 0.0)
        self._bid_price4 = data.get("BidPrice4", 0.0)
        self._bid_price5 = data.get("BidPrice5", 0.0)
        self._ask_price1 = data.get("AskPrice1", 0.0)
        self._ask_price2 = data.get("AskPrice2", 0.0)
        self._ask_price3 = data.get("AskPrice3", 0.0)
        self._ask_price4 = data.get("AskPrice4", 0.0)
        self._ask_price5 = data.get("AskPrice5", 0.0)
        self._bid_volume1 = data.get("BidVolume1", 0)
        self._bid_volume2 = data.get("BidVolume2", 0)
        self._bid_volume3 = data.get("BidVolume3", 0)
        self._bid_volume4 = data.get("BidVolume4", 0)
        self._bid_volume5 = data.get("BidVolume5", 0)
        self._ask_volume1 = data.get("AskVolume1", 0)
        self._ask_volume2 = data.get("AskVolume2", 0)
        self._ask_volume3 = data.get("AskVolume3", 0)
        self._ask_volume4 = data.get("AskVolume4", 0)
        self._ask_volume5 = data.get("AskVolume5", 0)
        self._trading_day = data.get("TradingDay", "")
        self._update_time = data.get("UpdateTime", "")
        self._datetime = data.get("Datetime", None)

        instrument_id = self._instrument_id
        previous_volume = self._last_total_volume.get(instrument_id, None)

        if previous_volume is None:
            self._last_volume = 0
        else:
            self._last_volume = self._volume - previous_volume

        self._last_total_volume[instrument_id] = self._volume

    def __repr__(self) -> str:
        return str(
            {
                "exchange": self._exchange,
                "instrument_id": self._instrument_id,
                "last_price": self._last_price,
                "open_price": self._open_price,
                "high_price": self._high_price,
                "low_price": self._low_price,
                "volume": self._volume,
                "last_volume": self.last_volume,
                "pre_close_price": self._pre_close_price,
                "pre_settlement_price": self._pre_settlement_price,
                "open_interest": self._open_interest,
                "upper_limit_price": self._upper_limit_price,
                "lower_limit_price": self._lower_limit_price,
                "turnover": self._turnover,
                "bid_price1": self._bid_price1,
                "bid_price2": self._bid_price2,
                "bid_price3": self._bid_price3,
                "bid_price4": self._bid_price4,
                "bid_price5": self._bid_price5,
                "ask_price1": self._ask_price1,
                "ask_price2": self._ask_price2,
                "ask_price3": self._ask_price3,
                "ask_price4": self._ask_price4,
                "ask_price5": self._ask_price5,
                "bid_volume1": self._bid_volume1,
                "bid_volume2": self._bid_volume2,
                "bid_volume3": self._bid_volume3,
                "bid_volume4": self._bid_volume4,
                "bid_volume5": self._bid_volume5,
                "ask_volume1": self._ask_volume1,
                "ask_volume2": self._ask_volume2,
                "ask_volume3": self._ask_volume3,
                "ask_volume4": self._ask_volume4,
                "ask_volume5": self._ask_volume5,
                "trading_day": self._trading_day,
                "update_time": self._update_time,
                "datetime": str(self._datetime),
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
    def last_price(self) -> float:
        """最新价"""
        return self._last_price

    @property
    def open_price(self) -> float:
        """今开盘价"""
        return self._open_price

    @property
    def high_price(self) -> float:
        """最高价"""
        return self._high_price

    @property
    def low_price(self) -> float:
        """最低价"""
        return self._low_price

    @property
    def volume(self) -> int:
        """总成交量"""
        return self._volume

    @property
    def pre_close_price(self) -> float:
        """昨收盘价"""
        return self._pre_close_price

    @property
    def pre_settlement_price(self) -> float:
        """昨结算价"""
        return self._pre_settlement_price

    @property
    def open_interest(self) -> int:
        """总持仓量"""
        return self._open_interest

    @property
    def upper_limit_price(self) -> float:
        """涨停板价"""
        return self._upper_limit_price

    @property
    def lower_limit_price(self) -> float:
        """跌停板价"""
        return self._lower_limit_price

    @property
    def turnover(self) -> float:
        """总成交金额"""
        return self._turnover

    @property
    def bid_price1(self) -> float:
        """申买价一"""
        return self._bid_price1

    @property
    def bid_price2(self) -> float:
        """申买价二"""
        return self._bid_price2

    @property
    def bid_price3(self) -> float:
        """申买价三"""
        return self._bid_price3

    @property
    def bid_price4(self) -> float:
        """申买价四"""
        return self._bid_price4

    @property
    def bid_price5(self) -> float:
        """申买价五"""
        return self._bid_price5

    @property
    def ask_price1(self) -> float:
        """申卖价一"""
        return self._ask_price1

    @property
    def ask_price2(self) -> float:
        """申卖价二"""
        return self._ask_price2

    @property
    def ask_price3(self) -> float:
        """申卖价三"""
        return self._ask_price3

    @property
    def ask_price4(self) -> float:
        """申卖价四"""
        return self._ask_price4

    @property
    def ask_price5(self) -> float:
        """申卖价五"""
        return self._ask_price5

    @property
    def bid_volume1(self) -> int:
        """申买量一"""
        return self._bid_volume1

    @property
    def bid_volume2(self) -> int:
        """申买量二"""
        return self._bid_volume2

    @property
    def bid_volume3(self) -> int:
        """申买量三"""
        return self._bid_volume3

    @property
    def bid_volume4(self) -> int:
        """申买量四"""
        return self._bid_volume4

    @property
    def bid_volume5(self) -> int:
        """申买量五"""
        return self._bid_volume5

    @property
    def ask_volume1(self) -> int:
        """申卖量一"""
        return self._ask_volume1

    @property
    def ask_volume2(self) -> int:
        """申卖量二"""
        return self._ask_volume2

    @property
    def ask_volume3(self) -> int:
        """申卖量三"""
        return self._ask_volume3

    @property
    def ask_volume4(self) -> int:
        """申卖量四"""
        return self._ask_volume4

    @property
    def ask_volume5(self) -> int:
        """申卖量五"""
        return self._ask_volume5

    @property
    def trading_day(self) -> str:
        """交易日"""
        return self._trading_day

    @property
    def update_time(self) -> str:
        """更新时间"""
        return self._update_time

    @property
    def datetime(self) -> TypeDateTime:
        """时间"""
        return self._datetime

    @property
    def last_volume(self) -> int:
        """最新成交量"""
        return self._last_volume

    def copy(self) -> "TickData":
        """浅拷贝自身"""
        return copy(self)

    def update(self, **kwargs) -> None:
        """更新属性"""
        for key, value in kwargs.items():
            setattr(self, f"_{key}", value)
