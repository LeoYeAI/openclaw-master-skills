import asyncio
import csv
import os
from datetime import datetime
from uuid import uuid1

from ..base import BaseParams, BaseStrategy
from ..classdef import OrderData, TickData, TradeData
from ..const import OrderDirectionEnum, OrderOffsetEnum
from ..core import MarketCenter
from ..utils import Scheduler
from .ext import load_ticks
from .fake_class import INFINIGO, FakeQtGuiSupport, FakeWidget
from .logger import logger
from .models import (Account, BacktestingResult, Config, InstrumentData, Order,
                     OrderDetail, OrderReq, Tick)
from .tools import save_zip_stream

os.environ["PYTHONGO_MODE"] = "BACKTESTING"


class Engine(object):
    """
    回测引擎

    Args:
        account: 资金账户
        tick_start_date: 行情开始日期
        tick_end_date: 行情结束日期
        config: 回测配置
    """

    def __init__(
        self,
        account: Account,
        tick_start_date: str,
        tick_end_date: str,
        config: Config
    ) -> None:
        self.account: Account = account
        """资金账户"""

        self.config: Config = config
        """回测配置"""

        self.strategy: BaseStrategy = None
        """策略实例"""

        self.tick_start_date: str = tick_start_date
        """行情开始日期"""

        self.tick_end_date: str = tick_end_date
        """行情结束日期"""

        self.subscribe_instruments: list[dict[str, str]] = []
        """已订阅的合约"""

        self.play_ticks: dict[str, list[TickData]] = {}
        """播放的 Tick 队列"""

        self.current_ticks: dict[str, TickData] = {}
        """当前 Tick"""

        self.order_queue: list[OrderData] = []
        """报单队列"""

        self.order_details: list[OrderDetail] = []
        """实时持仓"""

        self.instruments_data: dict[str, InstrumentData] = {}
        """合约信息"""

        self.market_center = MarketCenter(
            key=self.config.access_key,
            sn=self.config.access_secret
        )

        self._order_id: int = 0

    def market_queue(self) -> list[Tick]:
        """行情队列"""
        market_queue: list[Tick] = []

        for ticks in self.play_ticks.values():
            market_queue.extend(ticks)

        market_queue.sort(key=lambda x: x.datetime)

        return market_queue

    def set_instrument_data(self, exchange: str, instrument_id: str) -> None:
        """设置合约信息

        Args:
            exchange: 交易所代码
            instrument_id: 合约代码
        """

        if self.instruments_data.get(instrument_id):
            return

        result = self.market_center.get_instrument_data(
            exchange=exchange,
            instrument_id=instrument_id
        )

        for instrement_data in result["data"]:
            instrement_data = InstrumentData(instrement_data)
            self.instruments_data[instrement_data.instrument_id] = instrement_data

    def make_order_id(self) -> int:
        """生成并设置报单编号"""
        order_id = self._order_id
        self._order_id += 1
        return order_id

    def found_order_detail(self, order_req: OrderReq) -> OrderDetail:
        """
        查找报单明细

        Args:
            order_req: 报单请求
        """

        for order_details in self.order_details:
            condition = (
                order_details.direction == order_req.direction
                if order_req.offset == "0"
                else order_details.direction != order_req.direction
            )

            if (
                order_details.exchange == order_req.exchange
                and order_details.instrument_id == order_req.instrument_id
                and order_details.hedgeflag == order_req.hedgeflag
                and condition
                and not order_details.closed
            ):
                return order_details

    def get_tick_time(self, instrument_id: str) -> datetime:
        """
        获取当前 Tick 时间

        Args:
            instrument_id: 合约代码
        """

        return self.current_ticks[instrument_id].datetime

    def get_volume_multiple(self, instrument_id: str) -> int:
        """
        获取合约乘数

        Args:
            instrument_id: 合约代码
        """

        instrument = self.instruments_data.get(instrument_id)

        if instrument:
            return instrument.volume_multiple

        raise ValueError(f"获取合约信息失败: {instrument_id}")

    def handle_tick_file(self, exchange: str, instrument_id: str):
        """
        处理 Tick 文件

        Args:
            exchange: 交易所代码
            instrument_id: 合约代码
        Note:
            如果 Tick 数据在本地存在，则优先使用本地的数据
        """

        self.set_instrument_data(exchange, instrument_id)

        result: list[dict] = self.market_center.get_tick_data(
            exchange=exchange,
            instrument_id=instrument_id,
            start_date=self.tick_start_date,
            end_date=self.tick_end_date
        )

        for data in result:
            date = datetime.strptime(data["date"], "%Y-%m-%d")

            tick_dir = os.path.join(self.config.cache_dir, "ticks", exchange, str(date.year), str(date.month).zfill(2))
            tick_filename = f"{instrument_id}_{date.strftime("%Y%m%d")}.csv"
            tick_file_full_path = os.path.join(tick_dir, tick_filename)

            if not os.path.exists(tick_file_full_path):
                if not (download_url := data.get("url")):
                    logger.error(f"下载 Tick 文件失败 {exchange}:{instrument_id} {data.get("hint")}")
                    continue

                logger.debug(f"开始下载 {data["date"]} 的 Tick 文件")
                save_zip_stream(download_url, self.config.cache_dir)

            logger.debug(f"开始处理 Tick 文件: {tick_filename}")

            ticks = load_ticks(
                exchange=exchange,
                path=tick_file_full_path,
                natural_day=data["date"]
            )

            self.play_ticks.setdefault(instrument_id, []).extend(ticks)

    def subscribe(self, exchange: str, instrument_id: str) -> None:
        """订阅合约"""
        self.subscribe_instruments.append(
            {
                "exchange": exchange,
                "instrument_id": instrument_id
            }
        )

        self.handle_tick_file(exchange, instrument_id)

    def unsubscribe(self, exchange: str, instrument_id: str) -> None:
        """取消订阅合约"""
        self.subscribe_instruments.remove(
            {
                "exchange": exchange,
                "instrument_id": instrument_id
            }
        )

        if self.play_ticks.get(instrument_id):
            self.play_ticks.pop(instrument_id)

    def _make_trade_data(
        self,
        price: float,
        order_id: int,
        order_sys_id: str,
        order_req: OrderReq
    ) -> TradeData:
        """
        生成成交信息

        Args:
            price: 成交价格
            order_id: 报单编号
            order_sys_id: 交易所报单编号
            order_req: 回测报单请求
        """

        return TradeData({
            "Exchange": order_req.exchange,
            "InstrumentID": order_req.instrument_id,
            "TradeID": "",
            "OrderID": order_id,
            "OrderSysID": order_sys_id,
            "TradeTime": self.get_tick_time(order_req.instrument_id),
            "Direction": order_req.direction,
            "Offset": order_req.offset,
            "Hedgeflag": order_req.hedgeflag,
            "Price": price,
            "Volume": order_req.volume,
            "Memo": order_req.memo
        })

    def _make_order_data(
        self,
        price: float,
        order_id: int,
        order_sys_id: str,
        order_req: OrderReq
    ) -> OrderData:
        """
        生成报单信息
        
        Args:
            price: 报单价格
            order_id: 报单编号
            order_sys_id: 交易所报单编号
            order_req: 报单请求
        """

        return OrderData({
            "Exchange": order_req.exchange,
            "InstrumentID": order_req.instrument_id,
            "OrderID": order_id,
            "OrderSysID": order_sys_id,
            "Price": price,
            "OrderPriceType": 1,
            "TotalVolume": order_req.volume,
            "TradedVolume": order_req.volume,
            "CancelVolume": 0,
            "Direction": order_req.direction,
            "Offset": order_req.offset,
            "Status": "全部成交",
            "Memo": order_req.memo,
            "CancelTime": "",
            "OrderTime": self.get_tick_time(order_req.instrument_id)
        })

    def make_strategy_response(
        self,
        price: float,
        order_id: int,
        order_sys_id: str,
        order_req: OrderReq,
    ) -> None:
        """
        推送策略回调

        Args:
            price: 报单和成交价格
            order_id: 报单编号
            order_sys_id: 交易所报单编号
            order_req: 报单请求
        """

        order_data = self._make_order_data(
            price=price,
            order_id=order_id,
            order_sys_id=order_sys_id,
            order_req=order_req
        )

        self.order_queue.append(order_data)

        self.strategy.on_order(order_data)

        self.strategy.on_trade(self._make_trade_data(
            price=price,
            order_id=order_id,
            order_sys_id=order_sys_id,
            order_req=order_req
        ))

    def make_order(self, **kwargs) -> int:
        """见价成交撮合"""
        order_req = OrderReq(kwargs)

        current_tick = self.current_ticks.get(order_req.instrument_id)

        is_buy = order_req.direction == OrderDirectionEnum.BUY.flag
        tick_price = current_tick.ask_price1 if is_buy else current_tick.bid_price1

        if (is_buy and order_req.price < tick_price) or \
           (not is_buy and order_req.price > tick_price):
            """价格无法成交"""
            return -1

        volume_multiple = self.get_volume_multiple(order_req.instrument_id)

        fee = (
            self.config.fee_rate
            * tick_price
            * volume_multiple
            + self.config.fee_extra
        ) * order_req.volume

        margin = (
            self.config.margin_rate
            * tick_price
            * order_req.volume
            * volume_multiple
        )

        order_sys_id = uuid1().hex

        match order_req.offset:
            case OrderOffsetEnum.OPEN:
                if (fee + margin) > self.account.available:
                    logger.info("资金不足")
                    return -1

                order = Order(
                    price=tick_price,
                    volume=order_req.volume,
                    fee=fee,
                    margin=margin
                )

                if (order_detail := self.found_order_detail(order_req)):
                    order_detail.volume += order_req.volume
                    order_detail.trade_volume += order_req.volume
                    order_detail.close_available += order_req.volume
                    order_detail.fee += fee
                    order_detail.margin += margin
                    order_detail.orders.append(order)
                else:
                    order_detail = OrderDetail(
                        order_sys_id=order_sys_id,
                        investor_id=order_req.investor or "0001",
                        exchange=order_req.exchange,
                        instrument_id=order_req.instrument_id,
                        direction=order_req.direction,
                        offset=order_req.offset,
                        hedgeflag=order_req.hedgeflag,
                        price=tick_price,
                        volume=order_req.volume,
                        trade_volume=order_req.volume,
                        close_available=order_req.volume,
                        fee=fee,
                        margin=margin,
                        trade_time=self.get_tick_time(order_req.instrument_id),
                        trading_day=current_tick.trading_day,
                        orders=[order]
                    )

                    self.order_details.append(order_detail)

                self.account.available -= margin + fee
                self.account.margin += margin
                self.account.fee += fee

                order_id = self.make_order_id()

                self.make_strategy_response(
                    price=tick_price,
                    order_id=order_id,
                    order_sys_id=order_sys_id,
                    order_req=order_req
                )

                return order_id

            case OrderOffsetEnum.CLOSE | OrderOffsetEnum.CLOSE_TODAY:
                order_detail = self.found_order_detail(order_req)

                if not order_detail:
                    """找不到持仓"""
                    return -1

                if order_req.volume > order_detail.close_available:
                    """平仓时持仓不足"""
                    return -1

                order_detail.close_available -= order_req.volume
                """根据报单数量减少可平量"""

                profit = 0
                """盈亏"""

                remaining_volume = order_req.volume
                """平仓单条报单后剩余的手数"""

                total_released_margin = 0
                """总需释放保证金"""

                for order in order_detail.orders:
                    """先开先平"""
                    if order.closed:
                        """报单成交跳过"""
                        continue

                    remaining_volume -=order.volume
                    """报单数量 - 单条报单数量，正数还需要继续平，负数或零则不用"""

                    volume = (order.volume if remaining_volume > 0 else (order.volume + remaining_volume))
                    """
                    如果剩余报单手数大于零，说明当前报单全平后还要继续平
                    如果小于等于零，说明当前报单能支持平掉所需的仓位
                    """

                    profit += (
                        (tick_price - order.price)
                        * volume_multiple
                        * volume
                    )
                    """计算盈亏"""

                    released_margin = (order.margin / order.volume) * volume
                    total_released_margin += released_margin
                    """按比例释放保证金"""

                    if order.volume - volume == 0:
                        """当前报单全部平掉"""
                        order.closed = True
                    else:
                        """部分平仓"""
                        order.volume -= volume
                        order.margin -= released_margin

                    if remaining_volume <= 0:
                        """无需再平仓"""
                        break

                if order_detail.direction == OrderDirectionEnum.SELL.flag and is_buy:
                    """卖方向利润反向"""
                    profit *= -1

                self.account.available += (total_released_margin + profit - fee)
                self.account.margin -= total_released_margin
                self.account.fee += fee

                order_detail.margin -= total_released_margin
                order_detail.fee += fee
                order_detail.closed_profit += profit

                if order_detail.close_available == 0:
                    order_detail.closed = True
                    order_detail.margin = 0.0

                order_id = self.make_order_id()

                self.make_strategy_response(
                    price=tick_price,
                    order_id=order_id,
                    order_sys_id=order_sys_id,
                    order_req=order_req
                )

                return order_id

        return -1


class BacktestingFrame(object):
    """
    回测框架
    
    Args:
        engine: 回测引擎
        strategy_cls: 实例化策略
        strategy_params: 实例化参数映射模型
    """

    def __init__(
        self,
        engine: Engine,
        strategy_cls: BaseStrategy,
        strategy_params: BaseParams
    ) -> None:
        self.engine = engine
        self.backtesting_result = BacktestingResult(engine.account)

        self.strategy = strategy_cls
        self.strategy.strategy_id = 0
        self.strategy.strategy_name = "backtesting"

        self.strategy.params_map = strategy_params

    @property
    def exchange(self) -> str:
        """交易所代码"""
        return self.strategy.params_map.exchange

    @property
    def instrument_id(self) -> str:
        """合约代码"""
        return self.strategy.params_map.instrument_id 

    def print_progress_bar(self, iteration: int, total: int, length: int = 25):
        """进度条"""
        if self.engine.config.show_progress:
            if iteration % 1000 != 0 and iteration != total:
                return

            percent = 100 * (iteration / total)
            filled_length = int(length * iteration // total)
            bar = "█" * filled_length + "-" * (length - filled_length)

            print(f"\r进度 |{bar}| {percent:.3f}% 完成", end="\r")

            if iteration == total:
                print()

    def init(self) -> None:
        """执行策略初始化操作"""
        self.strategy.qt_gui_support = FakeQtGuiSupport()
        self.strategy.on_init()

    def start(self) -> None:
        """执行策略启动操作"""
        self.strategy.widget = FakeWidget()
        self.strategy.on_start()

    def stop(self) -> None:
        """执行策略初停止操作"""
        self.strategy.on_stop()

    async def tick(self) -> None:
        """执行策略推送 Tick 操作"""
        self.engine.strategy = self.strategy

        pre_trading_day: str = None

        market_queue = self.engine.market_queue()
        total = len(market_queue)

        if total == 0:
            logger.warning("没有可用于回测的数据")
            return

        # 模拟定时器
        scheduler_warpper = Scheduler("PythonGO")
        inner_scheduler = scheduler_warpper.scheduler

        for i in range(total):
            tick = market_queue[i]

            if tick.instrument_id not in self.engine.play_ticks:
                continue

            if pre_trading_day != tick.trading_day:
                self.backtesting_result.trading_days.append(tick.trading_day)

                pre_trading_day = tick.trading_day

            self.engine.current_ticks[tick.instrument_id] = tick

            inner_scheduler.run_pending_jobs(tick.datetime)

            self.strategy.on_tick(tick.copy())

            self.print_progress_bar(i, total)

        self.finish()

    def finish(self) -> None:
        """策略结束"""
        closed_profit = 0
        position_profit = 0

        for order_detail in self.engine.order_details:
            volume_multiple = self.engine.get_volume_multiple(order_detail.instrument_id)

            self.backtesting_result.turnover += (
                order_detail.price * order_detail.volume * volume_multiple
            )
            self.backtesting_result.total_volume += order_detail.volume

            if order_detail.closed:
                """已成交"""
                self.backtesting_result.daily_pnl[order_detail.trading_day] += (
                    order_detail.closed_profit - order_detail.fee
                )
                closed_profit += order_detail.closed_profit
                continue

            current_tick = self.engine.current_ticks.get(order_detail.instrument_id)

            if not current_tick:
                logger.debug(f"找不到 Tick: {order_detail.instrument_id}")
                continue

            profit = (
                (current_tick.last_price - order_detail.price)
                * volume_multiple
                * order_detail.volume
            )

            if order_detail.direction == OrderDirectionEnum.SELL.flag:
                """卖方向利润反向"""
                profit *= -1

            position_profit += profit

            self.backtesting_result.daily_pnl[order_detail.trading_day] += (
                profit - order_detail.fee
            )

        self.engine.account.dynamic_rights = (
            self.engine.account.initial_capital
            + closed_profit
            + position_profit
            - self.engine.account.fee
        )

        self.backtesting_result.print()

        if self.engine.config.save_order_details:
            try:
                import pandas as pd

                df = pd.DataFrame([od.model_dump() for od in self.engine.order_details])

                df.to_csv("orders.csv", index=False)

                logger.debug("保存报单明细完成")
            except Exception as e:
                logger.error(f"报单明细保存失败：{e}")


def run(
    *,
    config: Config,
    strategy_cls: BaseStrategy,
    strategy_params: BaseParams,
    start_date: str,
    end_date: str,
    initial_capital: int | float = 100_10000,
) -> Account:
    """
    回测运行主函数

    Args:
        config: 回测配置
        strategy_cls: 实例化策略
        strategy_params: 实例化参数映射模型
        start_date: 回测开始日期
        end_date: 回测结束日期（不包括）
        initial_capital: 回测初始资金
    """

    account = Account(
        initial_capital=initial_capital,
        available=initial_capital
    )

    engine = Engine(
        account=account,
        tick_start_date=start_date,
        tick_end_date=end_date,
        config=config
    )

    INFINIGO.engine = engine

    loop = asyncio.new_event_loop()

    backtesting_frame = BacktestingFrame(
        engine=engine,
        strategy_cls=strategy_cls,
        strategy_params=strategy_params
    )
    backtesting_frame.init()
    backtesting_frame.start()

    try:
        loop.run_until_complete(backtesting_frame.tick())
        return account
    except KeyboardInterrupt:
        logger.debug("退出回测")
        os._exit(0)
