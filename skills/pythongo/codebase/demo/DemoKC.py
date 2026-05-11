from typing import Literal

import numpy as np

from pythongo.base import BaseParams, BaseState, Field
from pythongo.classdef import KLineData, OrderData, TickData, TradeData
from pythongo.ui import BaseStrategy
from pythongo.utils import KLineGenerator


class Params(BaseParams):
    """参数映射模型"""
    exchange: str = Field(default="", title="交易所代码")
    instrument_id: str = Field(default="", title="合约代码")
    kline_style: str = Field(default="M1", title="K 线周期")
    tech_type: Literal["KC", "MA", "KDJ", "ATR", "MACD"] = Field(default="KC", title="技术指标")
    trade_direction: Literal["buy", "sell"] = Field(default="buy", title="交易方向")
    price_type: Literal["D1", "D2"] = Field(default="D1", title="价格档位")
    order_volume: int = Field(default=1, title="报单数量")
    N: int = Field(default=9, title="KDJ 参数1")
    M1: int = Field(default=3, title="KDJ 参数2")
    M2: int = Field(default=3, title="KDJ 参数3")
    N2: int = Field(default=26, title="ATR 指标参数")
    N1: int = Field(default=5, title="快均线周期")
    P1: int = Field(default=10, title="慢均线周期")


class State(BaseState):
    """状态映射模型"""
    macd: float = Field(default=0, title="DIFF")
    signall: float = Field(default=0, title="DEA")
    hist: float = Field(default=0, title="MACD")
    bup: float = Field(default=0, title="KC 上轨")
    bdn: float = Field(default=0, title="KC 下轨")
    ma0: float = Field(default=0, title="慢均线")
    ma1: float = Field(default=0, title="快均线")
    k: float = Field(default=0, title="K")
    d: float = Field(default=0, title="D")
    j: float = Field(default=0, title="J")
    atr: float = Field(default=0, title="真实波幅")


class DemoKC(BaseStrategy):
    """肯特纳通道策略 - 仅供测试"""
    def __init__(self):
        super().__init__()
        self.params_map = Params()
        """参数表"""

        self.state_map = State()
        """状态表"""

        self.buy_signal: bool = False
        self.sell_signal: bool = False
        self.cover_signal: bool = False
        self.short_signal: bool = False

        self.tick: TickData = None

        self.ma00 = 0
        self.ma10 = 0
        self.kk = 0
        self.dd = 0
        self.jj = 0
        self.tr = 0
        self.macd1 = 0
        self.signall1 = 0

        self.order_id = None
        self.signal_price = 0

    @property
    def main_indicator_data(self) -> dict[str, float]:
        """主图指标"""
        return {
            f"MA{self.params_map.N1}": self.state_map.ma1,
            f"MA{self.params_map.P1}": self.state_map.ma0,
            "BUP": self.state_map.bup,
            "BDN": self.state_map.bdn
        }

    @property
    def sub_indicator_data(self) -> dict[str, float]:
        """副图指标"""
        return {
            "K": self.state_map.k,
            "D": self.state_map.d,
            "J": self.state_map.j,
        }

    def on_tick(self, tick: TickData):
        super().on_tick(tick)

        self.tick = tick

        self.kline_generator.tick_to_kline(tick)

    def on_order_cancel(self, order: OrderData) -> None:
        """撤单推送回调"""
        super().on_order_cancel(order)
        self.order_id = None

    def on_trade(self, trade: TradeData, log: bool = False) -> None:
        super().on_trade(trade, log)
        self.order_id = None

    def on_start(self):
        self.kline_generator = KLineGenerator(
            callback=self.callback,
            real_time_callback=self.real_time_callback,
            exchange=self.params_map.exchange,
            instrument_id=self.params_map.instrument_id,
            style=self.params_map.kline_style
        )
        self.kline_generator.push_history_data()

        super().on_start()

        self.signal_price = 0

        self.buy_signal = False
        self.sell_signal = False
        self.cover_signal = False
        self.short_signal = False

        self.tick = None

        self.update_status_bar()

    def on_stop(self):
        super().on_stop()

    def callback(self, kline: KLineData) -> None:
        """接受 K 线回调"""
        # 计算指标
        self.calc_indicator()

        # 计算信号
        self.calc_signal(kline)

        # 信号执行
        self.exec_signal()

        # 线图更新
        self.widget.recv_kline({
            "kline": kline,
            "signal_price": self.signal_price,
            **self.main_indicator_data,
            **self.sub_indicator_data
        })

        if self.trading:
            self.update_status_bar()

    def real_time_callback(self, kline: KLineData) -> None:
        """使用收到的实时推送 K 线来计算指标并更新线图"""
        self.calc_indicator()

        self.widget.recv_kline({
            "kline": kline,
            **self.main_indicator_data,
            **self.sub_indicator_data
        })

        self.update_status_bar()

    def calc_keltner_signal(self, kline: KLineData):
        self.buy_signal = kline.close < kline.open and kline.close < self.state_map.bdn
        self.sell_signal = kline.close > kline.open and kline.close > self.state_map.bup

        if self.params_map.trade_direction == "buy":
            self.buy_signal, self.sell_signal = self.sell_signal, self.buy_signal

        self.short_signal = self.sell_signal
        self.cover_signal = self.buy_signal

    def calc_ma_signal(self):
        self.buy_signal = self.state_map.ma1 <= self.state_map.ma0 and self.ma10 >= self.ma00
        self.short_signal = self.state_map.ma1 >= self.state_map.ma0 and self.ma10 <= self.ma00

        if self.params_map.trade_direction == "buy":
            self.buy_signal, self.short_signal = self.short_signal, self.buy_signal

        self.cover_signal = self.buy_signal
        self.sell_signal = self.short_signal

    def calc_kdj_signal(self):
        # 20以内金叉
        self.buy_signal = (
            80 <= self.state_map.j <= self.state_map.k <= self.state_map.d
            and self.jj >= self.kk >= self.dd
        )
        # 80以上死叉
        self.short_signal = (
            20 >= self.state_map.j >= self.state_map.k >= self.state_map.d
            and self.jj <= self.kk <= self.dd
        )

        if self.params_map.trade_direction == "buy":
            self.buy_signal, self.short_signal = self.short_signal, self.buy_signal

        self.cover_signal = self.buy_signal
        self.sell_signal = self.short_signal

    def calc_atr_signal(self):
        self.buy_signal = self.state_map.atr < 5
        self.short_signal = self.state_map.atr >= 20

        if self.params_map.trade_direction == "buy":
            self.buy_signal, self.short_signal = self.short_signal, self.buy_signal

            self.cover_signal = self.buy_signal
            self.sell_signal = self.short_signal

    def calc_macd_signal(self):
        if self.params_map.trade_direction == "buy":
            # 0位以下金叉
            self.buy_signal = (
                self.state_map.hist <= 0
                and self.state_map.macd >= self.state_map.signall
                and self.macd1 < self.signall1
            )
            # 0位以下死叉
            self.short_signal = (
                self.state_map.hist <= 0
                and self.state_map.macd <= self.state_map.signall
                and self.macd1 > self.signall1
            )
            # 0位上金叉
            self.sell_signal = (
                self.state_map.hist >= 0
                and self.state_map.macd >= self.state_map.signall
                and self.macd1 < self.signall1
            )
            # 0位上死叉
            self.cover_signal = (
                self.state_map.hist >= 0
                and self.state_map.macd <= self.state_map.signall
                and self.macd1 > self.signall1
            )

    def calc_indicator(self) -> None:
        macd, signal, hist = self.kline_generator.producer.macdext(array=True)

        (
            (self.macd1, self.state_map.macd),
            (self.signall1, self.state_map.signall),
            (_, self.state_map.hist)
        ) = np.round((macd[-2:], signal[-2:], hist[-2:]), 2)

        self.state_map.atr, self.tr = self.kline_generator.producer.atr(self.params_map.N2)

        k, d, j = self.kline_generator.producer.kdj(
            fastk_period=self.params_map.N,
            slowk_period=self.params_map.M1,
            slowd_period=self.params_map.M2,
            array=True
        )

        (
            (self.kk, self.state_map.k),
            (self.dd, self.state_map.d),
            (self.jj, self.state_map.j)
        ) = np.round((k[-2:], d[-2:], j[-2:]), 2)

        ma = self.kline_generator.producer.sma(self.params_map.P1, array=True)
        ma1 = self.kline_generator.producer.sma(self.params_map.N1, array=True)

        self.ma00, self.state_map.ma0 = np.round(ma[-2:], 2)
        self.ma10, self.state_map.ma1 = np.round(ma1[-2:], 2)

        upper_envelope, lower_envelope = self.kline_generator.producer.keltner(self.params_map.N)
        self.state_map.bup, self.state_map.bdn = round(upper_envelope, 2), round(lower_envelope, 2)

    def calc_signal(self, kline: KLineData):
        """计算交易信号"""

        match self.params_map.tech_type:
            case "KC":
                self.calc_keltner_signal(kline)
            case "MA":
                self.calc_ma_signal()
            case "KDJ":
                self.calc_kdj_signal()
            case "ATR":
                self.calc_atr_signal()
            case "MACD":
                self.calc_macd_signal()

        self.long_price = self.short_price = kline.close

        if self.tick:
            self.long_price = self.tick.ask_price1
            self.short_price = self.tick.bid_price1

            if self.params_map.price_type == "D2":
                self.long_price = self.tick.ask_price2
                self.short_price = self.tick.bid_price2

    def exec_signal(self):
        """简易交易信号执行"""
        self.signal_price = 0

        position = self.get_position(self.params_map.instrument_id)

        if self.order_id is not None:
            # 挂单未成交
            self.cancel_order(self.order_id)

        if position.net_position > 0 and self.sell_signal:
            self.signal_price = -self.short_price

            if self.trading:
                self.order_id = self.auto_close_position(
                    exchange=self.params_map.exchange,
                    instrument_id=self.params_map.instrument_id,
                    price=self.short_price,
                    volume=position.net_position,
                    order_direction="sell"
                )
        elif position.net_position < 0 and self.cover_signal:
            self.signal_price = self.long_price

            if self.trading:
                self.order_id = self.auto_close_position(
                    exchange=self.params_map.exchange,
                    instrument_id=self.params_map.instrument_id,
                    price=self.long_price,
                    volume=abs(position.net_position),
                    order_direction="buy"
                )

        # 买开，卖开
        if self.short_signal:
            self.signal_price = -self.short_price

            if self.trading:
                self.order_id = self.send_order(
                    exchange=self.params_map.exchange,
                    instrument_id=self.params_map.instrument_id,
                    volume=self.params_map.order_volume,
                    price=self.short_price,
                    order_direction="sell"
                )
        elif self.buy_signal:
            self.signal_price = self.long_price

            if self.trading:
                self.order_id = self.send_order(
                    exchange=self.params_map.exchange,
                    instrument_id=self.params_map.instrument_id,
                    volume=self.params_map.order_volume,
                    price=self.long_price,
                    order_direction="buy"
                )
