from pythongo.base import BaseParams, BaseState, Field
from pythongo.classdef import KLineData, OrderData, TickData, TradeData
from pythongo.core import KLineStyleType
from pythongo.ui import BaseStrategy
from pythongo.utils import KLineGenerator


class Params(BaseParams):
    exchange: str = Field(default="", title="交易所代码")
    instrument_id: str = Field(default="", title="合约代码")
    kline_style: KLineStyleType = Field(default="M5", title="K 线周期")
    boll_period: int = Field(default=20, title="布林周期", ge=5)
    boll_dev: int | float = Field(default=2, title="布林倍数")
    order_volume: int = Field(default=1, title="下单手数", ge=1)
    pay_up: int | float = Field(default=0, title="超价")


class State(BaseState):
    mid: float = Field(default=0, title="中轨")
    upper: float = Field(default=0, title="上轨")
    lower: float = Field(default=0, title="下轨")


class DemoBollingerReversion(BaseStrategy):
    """基于布林带的均值回归策略示例（AI 编写）"""

    def __init__(self) -> None:
        super().__init__()

        self.params_map = Params()
        self.state_map = State()

        self.kline_generator: KLineGenerator = None
        self.order_id: int | None = None
        self.signal_price: float = 0

        self.pre_mid = 0.0
        self.pre_upper = 0.0
        self.pre_lower = 0.0
        self.pre_close = 0.0

    @staticmethod
    def _is_valid(value: float) -> bool:
        return value == value

    @property
    def main_indicator_data(self) -> dict[str, float]:
        return {
            "BOLL_MID": self.state_map.mid,
            "BOLL_UP": self.state_map.upper,
            "BOLL_LOW": self.state_map.lower,
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
        period = self.params_map.boll_period
        deviation = self.params_map.boll_dev
        producer = self.kline_generator.producer

        mid_array = producer.sma(period, array=True)
        std_array = producer.std(period, array=True)
        close_array = producer.close

        if len(mid_array) < 2 or len(std_array) < 2 or len(close_array) < 2:
            return False

        self.pre_mid = float(mid_array[-2])
        self.state_map.mid = float(mid_array[-1])
        self.pre_upper = self.pre_mid + float(std_array[-2]) * deviation
        self.state_map.upper = self.state_map.mid + float(std_array[-1]) * deviation
        self.pre_lower = self.pre_mid - float(std_array[-2]) * deviation
        self.state_map.lower = self.state_map.mid - float(std_array[-1]) * deviation
        self.pre_close = float(close_array[-2])

        return all(map(self._is_valid, [
            self.pre_mid,
            self.state_map.mid,
            self.pre_upper,
            self.state_map.upper,
            self.pre_lower,
            self.state_map.lower,
            self.pre_close,
        ]))

    def callback(self, kline: KLineData) -> None:
        if self.order_id is not None:
            self.cancel_order(self.order_id)

        if not self.calc_indicator():
            return

        self.signal_price = 0
        position = self.get_position(self.params_map.instrument_id)
        price = 0.0

        long_entry = self.pre_close >= self.pre_lower and kline.close < self.state_map.lower
        short_entry = self.pre_close <= self.pre_upper and kline.close > self.state_map.upper
        long_exit = position.net_position > 0 and kline.close >= self.state_map.mid
        short_exit = position.net_position < 0 and kline.close <= self.state_map.mid

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

