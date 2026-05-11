from pythongo.base import BaseParams, BaseState, Field
from pythongo.classdef import KLineData, OrderData, TickData, TradeData
from pythongo.core import KLineStyleType
from pythongo.ui import BaseStrategy
from pythongo.utils import KLineGenerator


class Params(BaseParams):
    exchange: str = Field(default="", title="交易所代码")
    instrument_id: str = Field(default="", title="合约代码")
    kline_style: KLineStyleType = Field(default="M5", title="K 线周期")
    entry_period: int = Field(default=20, title="突破周期", ge=5)
    exit_period: int = Field(default=10, title="退出周期", ge=3)
    order_volume: int = Field(default=1, title="下单手数", ge=1)
    pay_up: int | float = Field(default=0, title="超价")


class State(BaseState):
    upper: float = Field(default=0, title="突破上轨")
    lower: float = Field(default=0, title="突破下轨")
    exit_upper: float = Field(default=0, title="退出上轨")
    exit_lower: float = Field(default=0, title="退出下轨")


class DemoDonchianBreakout(BaseStrategy):
    """基于唐奇安通道的趋势突破策略示例（AI 编写）"""

    def __init__(self) -> None:
        super().__init__()

        self.params_map = Params()
        self.state_map = State()

        self.kline_generator: KLineGenerator = None
        self.order_id: int | None = None
        self.signal_price: float = 0

    @property
    def main_indicator_data(self) -> dict[str, float]:
        return {
            "DC_UP": self.state_map.upper,
            "DC_LOW": self.state_map.lower,
            "EXIT_UP": self.state_map.exit_upper,
            "EXIT_LOW": self.state_map.exit_lower,
        }

    def on_tick(self, tick: TickData) -> None:
        super().on_tick(tick)
        self.kline_generator.tick_to_kline(tick)

    def on_order_cancel(self, order: OrderData) -> None:
        super().on_order_cancel(order)
        self.order_id = None

    def on_trade(self, trade: TradeData, log: bool = False) -> None:
        super().on_trade(trade, log)
        self.order_id = None

    def on_start(self) -> None:
        self.kline_generator = KLineGenerator(
            callback=self.callback,
            real_time_callback=self.real_time_callback,
            exchange=self.params_map.exchange,
            instrument_id=self.params_map.instrument_id,
            style=self.params_map.kline_style
        )
        self.kline_generator.push_history_data()
        super().on_start()

    def on_stop(self) -> None:
        super().on_stop()

    def calc_indicator(self) -> bool:
        producer = self.kline_generator.producer
        high_array = producer.high
        low_array = producer.low
        required_period = max(self.params_map.entry_period, self.params_map.exit_period)

        if len(high_array) <= required_period or len(low_array) <= required_period:
            return False

        self.state_map.upper = float(max(high_array[-self.params_map.entry_period - 1:-1]))
        self.state_map.lower = float(min(low_array[-self.params_map.entry_period - 1:-1]))
        self.state_map.exit_upper = float(max(high_array[-self.params_map.exit_period - 1:-1]))
        self.state_map.exit_lower = float(min(low_array[-self.params_map.exit_period - 1:-1]))
        return True

    def callback(self, kline: KLineData) -> None:
        if self.order_id is not None:
            self.cancel_order(self.order_id)

        if not self.calc_indicator():
            return

        self.signal_price = 0
        position = self.get_position(self.params_map.instrument_id)
        price = 0.0

        if position.net_position == 0:
            if kline.close > self.state_map.upper:
                price = kline.close + self.params_map.pay_up
                self.signal_price = price

                if self.trading:
                    self.order_id = self.send_order(
                        exchange=self.params_map.exchange,
                        instrument_id=self.params_map.instrument_id,
                        volume=self.params_map.order_volume,
                        price=price,
                        order_direction="buy"
                    )
            elif kline.close < self.state_map.lower:
                price = kline.close - self.params_map.pay_up
                self.signal_price = -price

                if self.trading:
                    self.order_id = self.send_order(
                        exchange=self.params_map.exchange,
                        instrument_id=self.params_map.instrument_id,
                        volume=self.params_map.order_volume,
                        price=price,
                        order_direction="sell"
                    )
        elif position.net_position > 0 and kline.close < self.state_map.exit_lower:
            price = kline.close - self.params_map.pay_up
            self.signal_price = -price

            if self.trading:
                self.order_id = self.auto_close_position(
                    exchange=self.params_map.exchange,
                    instrument_id=self.params_map.instrument_id,
                    volume=position.net_position,
                    price=price,
                    order_direction="sell"
                )
        elif position.net_position < 0 and kline.close > self.state_map.exit_upper:
            price = kline.close + self.params_map.pay_up
            self.signal_price = price

            if self.trading:
                self.order_id = self.auto_close_position(
                    exchange=self.params_map.exchange,
                    instrument_id=self.params_map.instrument_id,
                    volume=abs(position.net_position),
                    price=price,
                    order_direction="buy"
                )

        self.widget.recv_kline({
            "kline": kline,
            "signal_price": self.signal_price,
            **self.main_indicator_data
        })

        if self.trading:
            self.update_status_bar()

    def real_time_callback(self, kline: KLineData) -> None:
        if not self.calc_indicator():
            return

        self.widget.recv_kline({
            "kline": kline,
            **self.main_indicator_data
        })
