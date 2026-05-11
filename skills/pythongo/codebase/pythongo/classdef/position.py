from typing import Literal

from .common import ObjDataType


class Position(object):
    """合约持仓数据"""

    _direction_map = {"多": "long", "空": "short"}

    def __init__(self, data: list[dict] = []) -> None:
        self._init_null()

        for position in data:
            setattr(self, self._direction_map[position["Direction"]], position)

    def __repr__(self) -> str:
        return str(
            {
                "long": self.long,
                "short": self.short,
                "net_position": self.net_position,
                "position": self.position
            }
        )

    def _init_null(self) -> None:
        """初始化空持仓"""
        self.long = {}
        self.short = {}

    def get_single_position(
        self,
        direction: Literal["long", "short"]
    ) -> "Position_p":
        """
        获取单边持仓

        Args:
            direction: 持仓方向
                long 多头持仓, short 空头持仓
        """
        return getattr(self, direction)

    @property
    def long(self) -> "Position_p":
        """合约多头持仓"""
        return self._long

    @long.setter
    def long(self, value: dict) -> None:
        self._long = Position_p(value)

    @property
    def short(self) -> "Position_p":
        """合约空头持仓"""
        return self._short

    @short.setter
    def short(self, value: dict) -> None:
        self._short = Position_p(value)

    @property
    def net_position(self) -> int:
        """合约净持仓"""
        return self.long.position - self.short.position

    @property
    def position(self) -> int:
        """合约总持仓"""
        return self.long.position + self.short.position


class Position_p(object):
    """单向持仓数据"""

    def __init__(self, data: ObjDataType = {}) -> None:
        self._exchange = data.get("Exchange", "")
        self._instrument_id = data.get("InstrumentID", "")
        self._position = data.get("Position", 0)
        self._position_close = data.get("PositionClose", 0)
        self._frozen_position = data.get("FrozenPosition", 0)
        self._frozen_closing = data.get("FrozenClosing", 0)
        self._yd_frozen_closing = data.get("YdFrozenClosing", 0)
        self._yd_position_close = data.get("YdPositionClose", 0)
        self._open_volume = data.get("OpenVolume", 0)
        self._close_volume = data.get("CloseVolume", 0)
        self._strike_frozen_position = data.get("StrikeFrozenPosition", 0)
        self._abandon_frozen_position = data.get("AbandonFrozenPosition", 0)
        self._position_cost = data.get("PositionCost", 0.0)
        self._yd_position_cost = data.get("YdPositionCost", 0.0)
        self._close_profit = data.get("CloseProfit", 0.0)
        self._position_profit = data.get("PositionProfit", 0.0)
        self._open_avg_price = data.get("OpenAvgPrice", 0.0)
        self._position_avg_price = data.get("PositionAvgPrice", 0.0)
        self._used_margin = data.get("UsedMargin", 0.0)
        self._close_available = data.get("CloseAvailable", 0)

    def __repr__(self) -> str:
        return str(
            {
                "exchange": self._exchange,
                "instrument_id": self._instrument_id,
                "position": self._position,
                "position_close": self._position_close,
                "frozen_position": self._frozen_position,
                "frozen_closing": self._frozen_closing,
                "td_frozen_closing": self.td_frozen_closing,
                "td_close_available": self.td_close_available,
                "td_position_close": self.td_position_close,
                "yd_frozen_closing": self._yd_frozen_closing,
                "yd_close_available": self.yd_close_available,
                "yd_position_close": self._yd_position_close,
                "open_volume": self._open_volume,
                "close_volume": self._close_volume,
                "strike_frozen_position": self._strike_frozen_position,
                "abandon_frozen_position": self._abandon_frozen_position,
                "position_cost": self._position_cost,
                "yd_position_cost": self._yd_position_cost,
                "close_profit": self._close_profit,
                "position_profit": self._position_profit,
                "open_avg_price": self._open_avg_price,
                "position_avg_price": self._position_avg_price,
                "used_margin": self._used_margin,
                "close_available": self._close_available
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
    def position(self) -> int:
        """总持仓量"""
        return self._position

    @property
    def position_close(self) -> int:
        """
        总持仓可平仓数量

        Note:
            包括平仓冻结持仓
        """
        return self._position_close

    @property
    def frozen_position(self) -> int:
        """总开仓冻结持仓"""
        return self._frozen_position

    @property
    def frozen_closing(self) -> int:
        """总平仓冻结持仓"""
        return self._frozen_closing

    @property
    def td_frozen_closing(self) -> int:
        """今持仓平仓冻结持仓"""
        return self.frozen_closing - self.yd_frozen_closing

    @property
    def td_close_available(self) -> int:
        """今持仓可平仓数量"""
        return self.td_position_close - self.td_frozen_closing

    @property
    def td_position_close(self) -> int:
        """
        今持仓可平仓数量

        Note:
            包括平仓冻结持仓
        """
        return self.position_close - self.yd_position_close

    @property
    def yd_frozen_closing(self) -> int:
        """昨持仓平仓冻结持仓"""
        return self._yd_frozen_closing

    @property
    def yd_close_available(self) -> int:
        """昨持仓可平仓数量"""
        return self.yd_position_close - self.yd_frozen_closing

    @property
    def yd_position_close(self) -> int:
        """
        昨持仓可平仓数量

        Note:
            包括平仓冻结持仓
        """
        return self._yd_position_close

    @property
    def open_volume(self) -> int:
        """
        今日开仓数量

        Note:
            不包括冻结
        """
        return self._open_volume

    @property
    def close_volume(self) -> int:
        """
        今日平仓数量

        Note:
            包括昨持仓的平仓, 不包括冻结
        """
        return self._close_volume

    @property
    def strike_frozen_position(self) -> int:
        """执行冻结持仓"""
        return self._strike_frozen_position

    @property
    def abandon_frozen_position(self) -> int:
        """放弃执行冻结持仓"""
        return self._abandon_frozen_position

    @property
    def position_cost(self) -> float | int:
        """总持仓成本"""
        return self._position_cost

    @property
    def yd_position_cost(self) -> float | int:
        """
        初始昨日持仓成本

        Note:
            当日不变
        """
        return self._yd_position_cost

    @property
    def close_profit(self) -> float | int:
        """平仓盈亏"""
        return self._close_profit

    @property
    def position_profit(self) -> float | int:
        """持仓盈亏"""
        return self._position_profit

    @property
    def open_avg_price(self) -> float | int:
        """开仓均价"""
        return self._open_avg_price

    @property
    def position_avg_price(self) -> float | int:
        """持仓均价"""
        return self._position_avg_price

    @property
    def used_margin(self) -> float | int:
        """占用保证金"""
        return self._used_margin

    @property
    def close_available(self) -> int:
        """当前总可平持仓数量"""
        return self._close_available
