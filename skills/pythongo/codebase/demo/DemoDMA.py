from typing import Literal

from pythongo.base import BaseParams, BaseState, Field
from pythongo.classdef import KLineData, OrderData, TickData, TradeData
from pythongo.core import KLineStyleType
from pythongo.ui import BaseStrategy
from pythongo.utils import KLineGenerator


class Params(BaseParams):
    """参数映射模型"""
    exchange: str = Field(default="", title="交易所代码")
    instrument_id: str = Field(default="", title="合约代码")
    fast_period: int = Field(default=5, title="短均线周期", ge=2)
    slow_period: int = Field(default=20, title="长均线周期")
    order_volume: int = Field(default=1, title="下单手数", ge=1)
    kline_style: KLineStyleType = Field(default="M1", title="K 线周期")
    pay_up: int | float = Field(default=0, title="超价")


class State(BaseState):
    """状态映射模型"""
    fast_ma: float = Field(default=0, title="短均线")
    slow_ma: float = Field(default=0, title="长均线")


class DemoDMA(BaseStrategy):
    """可调节 K 线周期的双均线交易策略 - 仅供测试"""
    def __init__(self) -> None:
        super().__init__()

        self.params_map = Params()
        """参数表"""

        self.state_map = State()
        """状态表"""

        self.kline_generator: KLineGenerator = None
        """K 线合成器"""

        self.pre_fast_ma = 0
        """上一根 K 线快均线数值"""

        self.pre_slow_ma = 0
        """上一根 K 线慢均线数值"""

        self.signal_price = 0
        """买卖信号标志"""

        self.order_id: set[int] = set()
        """报单 ID 列表"""

    @property
    def main_indicator_data(self) -> dict[str, float]:
        """主图指标"""
        return {
            f"MA{self.params_map.fast_period}": self.state_map.fast_ma,
            f"MA{self.params_map.slow_period}": self.state_map.slow_ma
        }

    def on_tick(self, tick: TickData) -> None:
        """收到行情 tick 推送"""
        super().on_tick(tick)

        self.kline_generator.tick_to_kline(tick)

    def on_order_cancel(self, order: OrderData) -> None:
        """撤单推送回调"""
        super().on_order_cancel(order)
        self.remove_order_id(order.order_id)

    def on_trade(self, trade: TradeData, log: bool = False) -> None:
        """成交回调"""
        super().on_trade(trade, log)
        self.remove_order_id(trade.order_id)

    def on_start(self) -> None:
        self.kline_generator = KLineGenerator(
            real_time_callback=self.real_time_callback,
            callback=self.callback,
            exchange=self.params_map.exchange,
            instrument_id=self.params_map.instrument_id,
            style=self.params_map.kline_style
        )

        self.kline_generator.push_history_data()

        super().on_start()

    def on_stop(self) -> None:
        super().on_stop()

    def remove_order_id(self, order_id: int) -> None:
        """从报单编号列表中移除对应的报单编号"""
        if order_id in self.order_id:
            self.order_id.remove(order_id)

    def is_cross(self) -> Literal[1, 2, 3]:
        """判断交叉"""
        if (
            self.pre_fast_ma < self.pre_slow_ma
            and self.state_map.fast_ma < self.state_map.slow_ma
        ) or (
            self.pre_fast_ma > self.pre_slow_ma
            and self.state_map.fast_ma > self.state_map.slow_ma
        ):
            """无信号"""
            return 1

        if (
            self.pre_fast_ma <= self.pre_slow_ma
            and self.state_map.fast_ma > self.state_map.slow_ma
        ):
            """金叉"""
            return 2

        if (
            self.pre_fast_ma >= self.pre_slow_ma
            and self.state_map.fast_ma < self.state_map.slow_ma
        ):
            """死叉"""
            return 3


    def callback(self, kline: KLineData) -> None:
        """接受 K 线回调"""
        if len(self.order_id) > 0:
            for order_id in self.order_id:
                self.cancel_order(order_id)

        self.calc_indicator()

        position = self.get_position(self.params_map.instrument_id)

        price = 0
        signal_price = 0

        match self.is_cross():
            case 1:
                ...
            case 2:
                """金叉"""
                price = signal_price = kline.close + self.params_map.pay_up

                if position.net_position < 0:
                    """清空仓"""
                    self.order_id.add(self.auto_close_position(
                        exchange=self.params_map.exchange,
                        instrument_id=self.params_map.instrument_id,
                        volume=abs(position.net_position),
                        price=price,
                        order_direction="buy"
                    ))

                self.order_id.add(self.send_order(
                    exchange=self.params_map.exchange,
                    instrument_id=self.params_map.instrument_id,
                    volume=self.params_map.order_volume,
                    price=price,
                    order_direction="buy"
                ))
            case 3:
                """死叉"""
                price = kline.close - self.params_map.pay_up
                signal_price = -price

                if position.net_position > 0:
                    """清多仓"""
                    self.order_id.add(self.auto_close_position(
                        exchange=self.params_map.exchange,
                        instrument_id=self.params_map.instrument_id,
                        volume=position.net_position,
                        price=price,
                        order_direction="sell"
                    ))

                self.order_id.add(self.send_order(
                    exchange=self.params_map.exchange,
                    instrument_id=self.params_map.instrument_id,
                    volume=self.params_map.order_volume,
                    price=price,
                    order_direction="sell"
                ))
        
        self.widget.recv_kline({
            "kline": kline,
            "signal_price": signal_price,
            **self.main_indicator_data
        })

    def real_time_callback(self, kline: KLineData) -> None:
        """使用收到的实时推送 K 线来计算指标并更新线图"""
        self.calc_indicator()

        self.widget.recv_kline({
            "kline": kline,
            **self.main_indicator_data
        })

    def calc_indicator(self) -> None:
        """计算指标数据"""
        slow_ma = self.kline_generator.producer.sma(self.params_map.slow_period, array=True)
        fast_ma = self.kline_generator.producer.sma(self.params_map.fast_period, array=True)

        self.pre_slow_ma, self.state_map.slow_ma = slow_ma[-2:]
        self.pre_fast_ma, self.state_map.fast_ma = fast_ma[-2:]
