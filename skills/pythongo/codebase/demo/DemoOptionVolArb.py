from datetime import datetime

from pythongo.base import BaseParams, BaseState, Field
from pythongo.classdef import KLineData, InstrumentData, OrderData, TickData, TradeData
from pythongo.option import Option
from pythongo.ui import BaseStrategy


class Params(BaseParams):
    exchange: str = Field(default="", title="期权交易所代码")
    instrument_id: str = Field(default="", title="期权合约代码")
    underlying_exchange: str = Field(default="", title="标的交易所代码")
    underlying_instrument_id: str = Field(default="", title="标的合约代码")
    order_volume: int = Field(default=1, title="下单手数", ge=1)
    fair_volatility: float = Field(default=0.22, title="公平波动率", gt=0)
    entry_deviation: float = Field(default=0.12, title="开仓偏离阈值", gt=0)
    exit_deviation: float = Field(default=0.04, title="平仓偏离阈值", gt=0)
    risk_free_rate: float = Field(default=0.015, title="无风险利率")
    dividend_rate: float = Field(default=0.0, title="股息率")
    pay_up: int | float = Field(default=0, title="超价")


class State(BaseState):
    underlying_price: float = Field(default=0, title="标的最新价")
    option_price: float = Field(default=0, title="期权最新价")
    theo_price: float = Field(default=0, title="理论价格")
    implied_vol: float = Field(default=0, title="隐含波动率")
    delta: float = Field(default=0, title="Delta")
    gamma: float = Field(default=0, title="Gamma")
    deviation: float = Field(default=0, title="价格偏离")
    days_to_expire: int = Field(default=0, title="剩余天数")


class DemoOptionVolArb(BaseStrategy):
    """基于理论波动率的单腿期权偏离回归策略示例"""

    def __init__(self) -> None:
        super().__init__()

        self.params_map = Params()
        self.state_map = State()

        self.option_tick: TickData | None = None
        self.underlying_tick: TickData | None = None
        self.option_info: InstrumentData | None = None
        self.order_id: int | None = None
        self.signal_price: float = 0

    @property
    def main_indicator_data(self) -> dict[str, float]:
        return {
            "THEO": self.state_map.theo_price,
            "DEV": self.state_map.deviation,
        }

    @property
    def sub_indicator_data(self) -> dict[str, float]:
        return {
            "IV": self.state_map.implied_vol,
            "DELTA": self.state_map.delta,
            "GAMMA": self.state_map.gamma,
        }

    @staticmethod
    def _is_valid(value: float) -> bool:
        return value == value

    @staticmethod
    def _safe_price(*prices: float) -> float:
        for price in prices:
            if price and price > 0:
                return float(price)
        return 0.0

    def _parse_expire_date(self, expire_date: str) -> datetime | None:
        for fmt in ("%Y%m%d", "%Y-%m-%d", "%Y/%m/%d"):
            try:
                return datetime.strptime(expire_date, fmt)
            except ValueError:
                continue
        return None

    def _get_option_type(self) -> str:
        option_type = (self.option_info.options_type or "").upper()
        if option_type not in {"CALL", "PUT"}:
            raise ValueError(f"无法识别期权类型: {option_type}")
        return option_type

    def _round_price(self, price: float, direction: str) -> float:
        if not self.option_info:
            return price

        tick = self.option_info.price_tick
        if tick <= 0:
            return price

        steps = int(price / tick)
        rounded = steps * tick

        if direction == "buy" and rounded < price:
            rounded += tick

        return round(rounded, 10)

    def _entry_order_price(self, direction: str) -> float:
        if not self.option_tick:
            return 0.0

        if direction == "buy":
            base_price = self._safe_price(
                self.option_tick.ask_price1,
                self.option_tick.last_price
            )
            return self._round_price(base_price + self.params_map.pay_up, direction)

        base_price = self._safe_price(
            self.option_tick.bid_price1,
            self.option_tick.last_price
        )
        return self._round_price(max(base_price - self.params_map.pay_up, 0), direction)

    def _close_order_price(self, direction: str) -> float:
        return self._entry_order_price(direction)

    def _load_option_info(self) -> None:
        self.option_info = self.get_instrument_data(
            self.params_map.exchange,
            self.params_map.instrument_id
        )

        if not self.params_map.underlying_instrument_id:
            self.params_map.underlying_instrument_id = self.option_info.underlying_symbol

        if not self.params_map.underlying_exchange:
            self.params_map.underlying_exchange = self.params_map.exchange

    def on_start(self) -> None:
        self._load_option_info()

        super().on_start()

        if self.params_map.underlying_instrument_id:
            self.sub_market_data(
                exchange=self.params_map.underlying_exchange,
                instrument_id=self.params_map.underlying_instrument_id
            )

    def on_stop(self) -> None:
        if self.params_map.underlying_instrument_id:
            self.unsub_market_data(
                exchange=self.params_map.underlying_exchange,
                instrument_id=self.params_map.underlying_instrument_id
            )

        super().on_stop()

    def on_tick(self, tick: TickData) -> None:
        super().on_tick(tick)

        if tick.instrument_id == self.params_map.instrument_id:
            self.option_tick = tick
        elif tick.instrument_id == self.params_map.underlying_instrument_id:
            self.underlying_tick = tick
        else:
            return

        self.evaluate_signal()

    def on_order_cancel(self, order: OrderData) -> None:
        super().on_order_cancel(order)
        self.order_id = None

    def on_trade(self, trade: TradeData, log: bool = False) -> None:
        super().on_trade(trade, log)
        self.order_id = None

    def calc_option_snapshot(self) -> Option | None:
        if not self.option_tick or not self.underlying_tick or not self.option_info:
            return None

        underlying_price = self._safe_price(self.underlying_tick.last_price)
        option_price = self._safe_price(
            self.option_tick.last_price,
            self.option_tick.ask_price1,
            self.option_tick.bid_price1
        )

        if underlying_price <= 0 or option_price <= 0:
            return None

        expire_dt = self._parse_expire_date(self.option_info.expire_date)
        if expire_dt is None:
            return None

        reference_dt = self.option_tick.datetime or datetime.now()
        seconds_to_expire = (expire_dt - reference_dt).total_seconds()
        if seconds_to_expire <= 0:
            return None

        time_to_expire = seconds_to_expire / (365 * 24 * 60 * 60)
        option_model = Option(
            option_type=self._get_option_type(),
            underlying_price=underlying_price,
            strike_price=self.option_info.strike_price,
            time_to_expire=time_to_expire,
            risk_free=self.params_map.risk_free_rate,
            market_price=option_price,
            dividend_rate=self.params_map.dividend_rate,
            init_sigma=self.params_map.fair_volatility
        )

        market_model = Option(
            option_type=self._get_option_type(),
            underlying_price=underlying_price,
            strike_price=self.option_info.strike_price,
            time_to_expire=time_to_expire,
            risk_free=self.params_map.risk_free_rate,
            market_price=option_price,
            dividend_rate=self.params_map.dividend_rate
        )

        self.state_map.underlying_price = underlying_price
        self.state_map.option_price = option_price
        self.state_map.theo_price = option_model.bs_price()
        self.state_map.implied_vol = market_model.sigma
        self.state_map.delta = option_model.bs_delta()
        self.state_map.gamma = option_model.bs_gamma()
        self.state_map.days_to_expire = max(int(seconds_to_expire // (24 * 60 * 60)), 0)

        if self.state_map.theo_price <= 0 or not self._is_valid(self.state_map.theo_price):
            return None

        self.state_map.deviation = (
            self.state_map.option_price - self.state_map.theo_price
        ) / self.state_map.theo_price

        if not all(map(self._is_valid, [
            self.state_map.implied_vol,
            self.state_map.delta,
            self.state_map.gamma,
            self.state_map.deviation,
        ])):
            return None

        return option_model

    def evaluate_signal(self) -> None:
        if self.order_id is not None:
            self.cancel_order(self.order_id)

        if self.calc_option_snapshot() is None:
            return

        position = self.get_position(self.params_map.instrument_id)
        deviation = self.state_map.deviation
        self.signal_price = 0

        if position.net_position == 0:
            if deviation <= -self.params_map.entry_deviation:
                price = self._entry_order_price("buy")
                self.signal_price = price

                if self.trading and price > 0:
                    self.order_id = self.send_order(
                        exchange=self.params_map.exchange,
                        instrument_id=self.params_map.instrument_id,
                        volume=self.params_map.order_volume,
                        price=price,
                        order_direction="buy"
                    )
            elif deviation >= self.params_map.entry_deviation:
                price = self._entry_order_price("sell")
                self.signal_price = -price

                if self.trading and price > 0:
                    self.order_id = self.send_order(
                        exchange=self.params_map.exchange,
                        instrument_id=self.params_map.instrument_id,
                        volume=self.params_map.order_volume,
                        price=price,
                        order_direction="sell"
                    )
        elif position.net_position > 0 and deviation >= -self.params_map.exit_deviation:
            price = self._close_order_price("sell")
            self.signal_price = -price

            if self.trading and price > 0:
                self.order_id = self.auto_close_position(
                    exchange=self.params_map.exchange,
                    instrument_id=self.params_map.instrument_id,
                    volume=position.net_position,
                    price=price,
                    order_direction="sell"
                )
        elif position.net_position < 0 and deviation <= self.params_map.exit_deviation:
            price = self._close_order_price("buy")
            self.signal_price = price

            if self.trading and price > 0:
                self.order_id = self.auto_close_position(
                    exchange=self.params_map.exchange,
                    instrument_id=self.params_map.instrument_id,
                    volume=abs(position.net_position),
                    price=price,
                    order_direction="buy"
                )

        kline = KLineData({
            "datetime": self.option_tick.datetime,
            "open": self.state_map.option_price,
            "high": self.state_map.option_price,
            "low": self.state_map.option_price,
            "close": self.state_map.option_price,
            "volume": self.option_tick.last_volume,
            "open_interest": self.option_tick.open_interest,
            "exchange": self.params_map.exchange,
            "instrument_id": self.params_map.instrument_id,
        })

        self.widget.recv_kline({
            "kline": kline,
            "signal_price": self.signal_price,
            **self.main_indicator_data,
            **self.sub_indicator_data
        })

        if self.trading:
            self.update_status_bar()
