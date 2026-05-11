from pythongo.base import BaseParams, Field
from pythongo.classdef import KLineData, TickData
from pythongo.ui import BaseStrategy
from pythongo.utils import KLineGeneratorSec


class Params(BaseParams):
    """参数映射模型"""
    exchange: str = Field(default="", title="交易所代码")
    instrument_id: str = Field(default="", title="合约代码")
    seconds: int = Field(default=5, title="秒数", ge=0)


class DemoSecondKLine(BaseStrategy):
    """秒级 K 线图示例"""
    def __init__(self):
        super().__init__()
        self.params_map = Params()
        """参数表"""

    def on_tick(self, tick: TickData) -> None:
        super().on_tick(tick)
        self.kline_generator.tick_to_kline(tick)

    def on_start(self) -> None:
        #: 由于秒级 K 线没有历史数据，所以需要在这里手动设置线图横坐标事件
        self.widget.set_xrange_event_signal.emit()

        self.kline_generator = KLineGeneratorSec(
            callback=self.on_second_kline,
            seconds=self.params_map.seconds
        )

        super().on_start()

    def on_stop(self) -> None:
        super().on_stop()
        self.widget.kline_widget.cancel_xrange_event()

    def on_second_kline(self, kline: KLineData) -> None:
        """推送 K 线回调"""
        self.widget.recv_kline({"kline": kline})
