from pythongo.base import BaseParams, BaseState, Field
from pythongo.classdef import KLineData, OrderData, TickData, TradeData
from pythongo.core import KLineStyleType
from pythongo.ui import BaseStrategy
from pythongo.utils import KLineGenerator


class Params(BaseParams):
    exchange: str = Field(default="", title="交易所代码")
    instrument_id: str = Field(default="", title="合约代码")
    kline_style: KLineStyleType = Field(default="M5", title="K 线周期")
    ma_period: int = Field(default=20, title="中轴均线周期", ge=5)
    atr_period: int = Field(default=14, title="ATR 周期", ge=5)
    atr_multiplier: int | float = Field(default=1.5, title="ATR 倍数")
    order_volume: int = Field(default=1, title="下单手数", ge=1)
    pay_up: int | float = Field(default=0, title="超价")


class State(BaseState):
    mid: float = Field(default=0, title="中轴均线")
    atr: float = Field(default=0, title="ATR")
    upper: float = Field(default=0, title="波动上轨")
    lower: float = Field(default=0, title="波动下轨")


class DemoATRVolatilityBreakout(BaseStrategy):
    """基于 ATR 波动通道的突破策略示例（AI 编写）"""

    def __init__(self) -> None:
        super().__init__()

        self.params_map = Params()
        self.state_map = State()

        self.kline_generator: KLineGenerator = None
        self.order_id: int | None = None
        self.signal_price: float = 0

        self.pre_upper = 0.0
        self.pre_lower = 0.0
        self.pre_close = 0.0

    @staticmethod
    def _is_valid(value: float) -> bool:
        return value == value

    @property
    def main_indicator_data(self) -> dict[str, float]:
        return {
            "ATR_MID": self.state_map.mid,
            "ATR_UP": self.state_map.upper,
            "ATR_LOW": self.state_map.lower,
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
        ma_array = producer.sma(self.params_map.ma_period, array=True)
        atr_array, _ = producer.atr(self.params_map.atr_period, array=True)
        close_array = producer.close

        if len(ma_array) < 2 or len(atr_array) < 2 or len(close_array) < 2:
            return False

        current_mid = float(ma_array[-1])
        current_atr = float(atr_array[-1])
        previous_mid = float(ma_array[-2])
        previous_atr = float(atr_array[-2])

        if not all(map(self._is_valid, [current_mid, current_atr, previous_mid, previous_atr])):
            return False

        self.state_map.mid = current_mid
        self.state_map.atr = current_atr
        self.state_map.upper = current_mid + current_atr * self.params_map.atr_multiplier
        self.state_map.lower = current_mid - current_atr * self.params_map.atr_multiplier
        self.pre_upper = previous_mid + previous_atr * self.params_map.atr_multiplier
        self.pre_lower = previous_mid - previous_atr * self.params_map.atr_multiplier
        self.pre_close = float(close_array[-2])

        return self._is_valid(self.pre_close)

    def callback(self, kline: KLineData) -> None:
        if self.order_id is not None:
            self.cancel_order(self.order_id)

        if not self.calc_indicator():
            return

        self.signal_price = 0
        position = self.get_position(self.params_map.instrument_id)
        price = 0.0

        long_entry = self.pre_close <= self.pre_upper and kline.close > self.state_map.upper
        short_entry = self.pre_close >= self.pre_lower and kline.close < self.state_map.lower
        long_exit = position.net_position > 0 and kline.close < self.state_map.mid
        short_exit = position.net_position < 0 and kline.close > self.state_map.mid

        if position.net_position == 0:
            if long_entry:
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
            elif short_entry:
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
        elif long_exit:
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
        elif short_exit:
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
