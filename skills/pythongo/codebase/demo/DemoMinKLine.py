from pythongo.base import BaseParams, Field
from pythongo.classdef import KLineData, TickData
from pythongo.core import KLineStyleType
from pythongo.ui import BaseStrategy
from pythongo.utils import KLineGenerator


class Params(BaseParams):
    """参数映射模型"""
    exchange: str = Field(default="", title="交易所代码")
    instrument_id: str = Field(default="", title="合约代码")
    kline_style: KLineStyleType = Field(default="M1", title="K 线周期")


class DemoMinKLine(BaseStrategy):
    """分钟级 K 线图示例 - 仅供测试"""
    def __init__(self):
        super().__init__()

        self.params_map = Params()
        """参数表"""

    def on_tick(self, tick: TickData) -> None:
        super().on_tick(tick)
        self.kline_generator.tick_to_kline(tick)

    def on_start(self) -> None:
        """
        这里默认合成 M1 的 K 线, 即 1 分钟 K 线

        具体可使用的合成分钟, 请看 `KLineStyle` 枚举类

        `push_history_data` 需要写在 `super().on_start()` 之前

        因为执行父类的 `on_start()` 会对 `self.trading` 赋值为 `True`

        从而导致在推送历史数据的时候可能会触发程序下单
        """

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

    def callback(self, kline: KLineData) -> None:
        """
        推送 K 线回调
    
        当新的分钟线合成后, 会调用本函数, 这是因为在 `KLineGenerator` 设置了回调函数

        你可以把计算信号的方法写在这
        """

        self.widget.recv_kline({"kline": kline})

    def real_time_callback(self, kline: KLineData) -> None:
        """实时推送 K 线回调"""
        self.callback(kline)
