from datetime import time as dtime

from pythongo.base import BaseParams, BaseState, Field
from pythongo.classdef import KLineData, OrderData, TickData, TradeData
from pythongo.core import KLineStyleType
from pythongo.ui import BaseStrategy
from pythongo.utils import KLineGeneratorArb


class Params(BaseParams):
    """参数映射模型"""
    exchange: str = Field(default="", title="交易所代码")
    instrument_id: str = Field(default="", title="合约代码")
    fast_period: int = Field(default=5, title="快均线周期", ge=2)
    slow_period: int = Field(default=20, title="慢均线周期")
    order_volume: int = Field(default=1, title="下单手数", ge=1)
    kline_style: KLineStyleType = Field(default="M1", title="K 线周期")
    pay_up: int | float = Field(default=0, title="超价")


class State(BaseState):
    """状态映射模型"""
    slow_ma: float = Field(default=0, title="慢均线")
    fast_ma: float = Field(default=0, title="快均线")


class DemoArbitrageDMA(BaseStrategy):
    """交易所标准套利合约的的双均线交易策略 - 仅供测试"""
    def __init__(self):
        super().__init__()
        self.params_map = Params()
        """参数表"""

        self.state_map = State()
        """状态表"""

        self.pre_fast_ma = 0
        """上一根 K 线快均线数值"""

        self.pre_slow_ma = 0
        """上一根 K 线慢均线数值"""

        self.long_price: int | float = 0.0
        """多仓价格"""

        self.short_price: int | float = 0.0
        """空仓价格"""

        self.buy_signal = False
        """买信号"""

        self.sell_signal = False
        """卖信号"""

        self.signal_price = 0
        """买卖信号标志"""

        self.order_id = None
        """报单 ID"""

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
        self.order_id = None

    def on_trade(self, trade: TradeData, log: bool = False) -> None:
        """成交回调"""
        super().on_trade(trade, log)
        self.order_id = None

    def on_start(self):
        self.kline_generator = KLineGeneratorArb(
            callback=self.callback,
            exchange=self.params_map.exchange,
            instrument_id=self.params_map.instrument_id,
            style=self.params_map.kline_style,
            real_time_callback=self.real_time_callback
        )
        self.kline_generator.push_history_data()

        super().on_start()

        for instrument_id in self.kline_generator.instruments:
            """订阅单腿合约"""
            self.sub_market_data(
                exchange=self.params_map.exchange,
                instrument_id=instrument_id
            )

    def on_stop(self):
        super().on_stop()

        for instrument_id in self.kline_generator.instruments:
            """取消订阅单腿合约"""
            self.unsub_market_data(
                exchange=self.params_map.exchange,
                instrument_id=instrument_id
            )

    def callback(self, kline: KLineData):
        """接受 K 线回调"""
        self.calc_indicator()

        self.calc_signal(kline)

        self.exec_signal()

        self.widget.recv_kline({
            "kline": kline,
            "signal_price": self.signal_price,
            **self.main_indicator_data
        })

        if self.trading:
            self.update_status_bar()

    def real_time_callback(self, kline: KLineData) -> None:
        """使用收到的实时推送 K 线来计算指标并更新线图"""
        self.calc_indicator()

        self.widget.recv_kline({
            "kline": kline,
            **self.main_indicator_data
        })

    def calc_indicator(self):
        """计算指标数据"""
        slow_ma = self.kline_generator.producer.sma(self.params_map.slow_period, array=True)
        fast_ma = self.kline_generator.producer.sma(self.params_map.fast_period, array=True)

        self.state_map.slow_ma, self.pre_slow_ma = slow_ma[-1], slow_ma[-2]
        self.state_map.fast_ma, self.pre_fast_ma = fast_ma[-1], fast_ma[-2]

    def calc_signal(self, kline: KLineData):
        """计算交易信号"""

        # 定义尾盘, 尾盘不交易并且空仓
        self.end_of_day = kline.datetime.time() >= dtime(14, 40)

        # 判断信号
        self.buy_signal = (
            self.state_map.fast_ma > self.state_map.slow_ma
            and self.pre_fast_ma < self.pre_slow_ma
        )

        self.sell_signal = (
            self.state_map.fast_ma < self.state_map.slow_ma
            and self.pre_fast_ma > self.pre_slow_ma
        )

        self.long_price = self.short_price = kline.close

    def exec_signal(self):
        """交易信号执行"""
        position = self.get_position(self.params_map.instrument_id)

        # 挂单未成交
        if self.order_id is not None:
            self.cancel_order(self.order_id)

        self.signal_price = 0

        if position.net_position == 0 and not self.end_of_day:  #: 当前无仓位
            # 买开，卖开
            if self.sell_signal:
                self.signal_price = -self.short_price

                if self.trading is False:   
                    return

                self.order_id = self.send_order(
                    exchange=self.params_map.exchange,
                    instrument_id=self.params_map.instrument_id,
                    volume=self.params_map.order_volume,
                    price=(price := self.short_price - self.params_map.pay_up),
                    order_direction="sell"
                )

                self.output(f"卖出开仓信号价格: {price}")
            elif self.buy_signal:
                self.signal_price = self.long_price

                if self.trading is False:
                    return

                self.order_id = self.send_order(
                    exchange=self.params_map.exchange,
                    instrument_id=self.params_map.instrument_id,
                    volume=self.params_map.order_volume,
                    price=(price := self.long_price + self.params_map.pay_up),
                    order_direction="buy"
                )
                self.output(f"买入开仓信号价格: {price}")

        elif position.net_position > 0 and self.sell_signal:  #: 持有多头仓位
            self.signal_price = -self.short_price

            if self.trading is False:
                return

            self.order_id = self.auto_close_position(
                exchange=self.params_map.exchange,
                instrument_id=self.params_map.instrument_id,
                price=(price := self.short_price - self.params_map.pay_up),
                volume=position.net_position,
                order_direction="sell"
            )
            self.output(f"卖出平仓信号价格: {price}")

        elif position.net_position < 0 and self.buy_signal:  #: 持有空头仓位
            self.signal_price = self.long_price
    
            if self.trading is False:
                return

            self.order_id = self.auto_close_position(
                exchange=self.params_map.exchange,
                instrument_id=self.params_map.instrument_id,
                price=(price := self.long_price + self.params_map.pay_up),
                volume=abs(position.net_position),
                order_direction="buy"
            )
            self.output(f"买入平仓信号价格: {price}")
