from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from pythongo.base import BaseParams, BaseState, BaseStrategy, Field
from pythongo.classdef import OrderData, TickData, TradeData
from pythongo.types import TypeOrderDIR
from pythongo.utils import Scheduler


def get_uuid() -> str:
    return str(uuid4()).split("-")[0]


@dataclass
class Order(object):
    """单个报单状态"""

    memo: str
    """报单备注"""

    volume: int
    """报单手数"""

    remaining_volume: int = 0
    """剩余报单手数"""

    order_id: int = None
    """报单 ID"""

    price: float | int = None
    """报单价格"""

    closed: bool = False
    """报单关闭"""


class Params(BaseParams):
    """参数映射模型"""
    exchange: str = Field(default="", title="交易所代码")
    instrument_id: str = Field(default="", title="合约代码")
    total_time: int = Field(default=300, title="算法总时长(秒)")
    interval: int = Field(default=10, title="价格检查间隔(秒)")
    order_volume: int = Field(default=4, title="单笔委托数量")
    total_volume: int = Field(default=50, title="总委托手数")
    order_direction: TypeOrderDIR = Field(default="buy", title="买卖方向")

    @property
    def job_interval(self) -> int:
        """任务间隔时间"""
        return self.total_time / (self.total_volume / self.order_volume)

    @property
    def split_number(self) -> list[int]:
        """拆分任务"""
        return (
            [self.order_volume]
            * (self.total_volume // self.order_volume)
            + ([_v] if (_v := self.total_volume % self.order_volume) else [])
        )


class State(BaseState):
    """状态映射模型"""
    remaining_job: int = Field(default=0, title="剩余任务数量")


class DemoTWAP(BaseStrategy):
    """TWAP 策略 - 仅供测试"""
    def __init__(self) -> None:
        super().__init__()
        self.params_map = Params()
        """参数表"""

        self.state_map = State()
        """状态表"""

        self.scheduler = Scheduler()
        """定时器"""

        self.scheduler.start()

        self.order_list: list[Order] = []
        """总报单列表"""

        self.order_jobstore: list[Order] = []
        """报单任务列表"""

        self.check_job: bool = False
        """判断是否需要检查价格"""

        self.tick: TickData = None
        """缓存的 tick"""

    def get_order_price(self, best_price: bool = False) -> float | int:
        """
        获取报单价格

        Args:
            best_price: 是否获取最优价(对手价)
        Note:
            如无价格, 则返回默认值 `0.0`
        """

        if self.tick:
            bid_price, ask_price = self.tick.bid_price1, self.tick.ask_price1

            if best_price:
                bid_price, ask_price = ask_price, bid_price

            return bid_price if self.params_map.order_direction == "buy" else ask_price

        return 0.0

    def find_order(self, memo: str) -> Order:
        """
        通过报单 memo 查找报单状态

        Args:
            memo: 报单备注
        """

        for order in self.order_jobstore:
            if order.memo == memo:
                return order

        raise Exception(f"无法找到 memo 为 {memo} 的报单")

    def remove_all_job(self) -> None:
        """移除所有的任务"""
        for job in ["twap_job", "check_price_job"]:
            self.scheduler.remove_job(job)

    def split_order(self) -> None:
        """根据总委托手数和单笔委托手数分割报单"""
        for volume in self.params_map.split_number:
            self.order_list.append(Order(memo=get_uuid(), volume=volume))

    def chase(self, order: Order) -> None:
        """
        如果上一笔还有未成交手数, 则以对手价追单

        Args:
            order: 单个报单状态
        Note:
            本示例中使用 GFD 追单, 所以显式的指定了 `order_type`
        """

        if order.remaining_volume and order.closed is False:
            if order.volume == order.remaining_volume:
                self.cancel_order(order.order_id)

            self.output(f"chase {order}")

            self.send_order(
                exchange=self.params_map.exchange,
                instrument_id=self.params_map.instrument_id,
                volume=order.remaining_volume,
                price=self.get_order_price(best_price=True),
                order_direction=self.params_map.order_direction,
                order_type="GFD",
                memo=order.memo
            )

    def twap(self) -> None:
        """TWAP 主任务"""
        if self.order_jobstore:
            self.chase(self.order_jobstore[-1])

        if len(self.order_list) == 0:
            self.output("TWAP 任务结束, 将自动暂停策略")
            self.scheduler.remove_job("twap_job")
            self.pause_strategy()
            return

        order = self.order_list.pop(0)
        self.order_jobstore.append(order)

        self.state_map.remaining_job = len(self.order_list)
        self.update_status_bar()

        self.output(f"twap {order}")

        if self.check_job:
            _job_name = "check_price_job"

            self.scheduler.remove_job(_job_name)
    
            self.scheduler.add_job(
                self.check_price,
                trigger="interval",
                id=_job_name,
                seconds=self.params_map.interval,
                kwargs={"order": order}
            )

        order.order_id = self.send_order(
            exchange=self.params_map.exchange,
            instrument_id=self.params_map.instrument_id,
            volume=order.volume,
            price=self.get_order_price(),
            order_direction=self.params_map.order_direction,
            memo=order.memo
        )

    def check_price(self, order: Order) -> None:
        """
        检查价格是否成交

        Args:
            order: 单个报单状态
        Note:
            如果未成交则撤单后重新报单
        """

        self.output(f"check_price {order}")

        if order.closed:
            """报单已成交, 移除该报单的检查价格任务"""
            self.scheduler.remove_job("check_price_job")
            return

        if order.price != self.get_order_price():
            self.output("check_price", order.price, self.get_order_price(), "价格不一致")
            self.cancel_order(order.order_id)
            order.order_id = self.send_order(
                exchange=self.params_map.exchange,
                instrument_id=self.params_map.instrument_id,
                volume=order.volume,
                price=self.get_order_price(),
                order_direction=self.params_map.order_direction,
                memo=order.memo
            )

    def set_timer(self) -> None:
        """设置定时器并运行"""
        job_interval = self.params_map.job_interval

        self.check_job = job_interval > self.params_map.interval

        self.scheduler.add_job(
            self.twap,
            trigger="interval",
            id="twap_job",
            seconds=job_interval,
            next_run_time=datetime.now()
        )

    def on_tick(self, tick: TickData) -> None:
        super().on_tick(tick)
        self.tick = tick

    def on_order(self, order: OrderData) -> None:
        super().on_order(order)

        order_job = self.find_order(order.memo)

        if order.status in ["未成交", "部分成交", "部成部撤"]:
            order_job.remaining_volume = order.total_volume - order.traded_volume
            order_job.price = order.price
        elif order.status in ["全部成交"]:
            order_job.remaining_volume = 0
            order_job.closed = True

    def on_trade(self, trade: TradeData, log: bool = False) -> None:
        super().on_trade(trade, log)

    def on_start(self) -> None:
        super().on_start()
        self.split_order()
        self.set_timer()

    def on_stop(self) -> None:
        super().on_stop()
        self.remove_all_job()
