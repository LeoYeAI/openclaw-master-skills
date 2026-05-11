from pythongo.types import TypeDateTime

from .common import ObjDataType


class KLineData(object):
    """K 线数据类"""

    def __init__(self, data: ObjDataType = {}) -> None:
        self._exchange = data.get("exchange", "")
        self._instrument_id = data.get("instrument_id", "")
        self._open = data.get("open", 0.0)
        self._close = data.get("close", 0.0)
        self._low = data.get("low", 0.0)
        self._high = data.get("high", 0.0)
        self._volume = data.get("volume", 0)
        self._open_interest = data.get("open_interest", 0)
        self._datetime = data.get("datetime", None)

    def __repr__(self) -> str:
        return str(self.to_json())

    @property
    def exchange(self) -> str:
        """交易所代码"""
        return self._exchange

    @property
    def instrument_id(self) -> str:
        """合约代码"""
        return self._instrument_id

    @property
    def open(self) -> float:
        """开盘价"""
        return self._open

    @property
    def close(self) -> float:
        """收盘价"""
        return self._close

    @property
    def low(self) -> float:
        """最低价"""
        return self._low

    @property
    def high(self) -> float:
        """最高价"""
        return self._high

    @property
    def volume(self) -> int:
        """成交量"""
        return self._volume

    @property
    def open_interest(self) -> int:
        """持仓量"""
        return self._open_interest

    @property
    def datetime(self) -> TypeDateTime:
        """时间"""
        return self._datetime

    def to_json(self) -> dict:
        """K 线对象转字典"""
        return {
            "open": self._open,
            "high": self._high,
            "low": self._low,
            "close": self._close,
            "volume": self._volume,
            "open_interest": self._open_interest,
            "datetime": self._datetime,
        }

    def update(self, **kwargs) -> None:
        """更新 K 线属性"""
        for key, value in kwargs.items():
            setattr(self, f"_{key}", value)
