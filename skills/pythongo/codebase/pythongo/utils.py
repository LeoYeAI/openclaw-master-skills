import logging
import os
import re
import threading
from datetime import datetime, timedelta
from typing import Any, Callable, Literal

import numpy as np
from apscheduler.job import Job
from apscheduler.schedulers.background import BackgroundScheduler

from pythongo.backtesting.scheduler import BacktestScheduler
from pythongo.classdef import KLineData, TickData
from pythongo.core import KLineStyle, KLineStyleType, MarketCenter
from pythongo.indicator import Indicators
from pythongo.infini import write_log
from pythongo.types import TypeDateTime


class CustomLogHandler(logging.Handler):
    """自定义日志 Handler"""
    def emit(self, record):
        write_log(self.format(record))


class Scheduler(object):
    """
    简易定时器

    Args:
        scheduler_name: 定时器名称
    Note:
        如果传入定时器名称, 则后续实例化同一定时器名称的类时, 都将返回同一内存地址的实例
        此为单例模式 
    """

    _lock_1 = threading.Lock()
    _lock_2 = threading.Lock()
    _cache_instance: dict[str, "Scheduler"] = {}

    def __new__(cls, *args, **kwargs) -> "Scheduler":
        with cls._lock_1:
            if scheduler_name := (
                (args and args[0])
                or kwargs.get("scheduler_name")
            ):
                if _cls := cls._cache_instance.get(scheduler_name):
                    return _cls

                cls._cache_instance[scheduler_name] = super().__new__(cls)
                return cls._cache_instance[scheduler_name]

            return super().__new__(cls)

    def __init__(self, scheduler_name: str = None) -> None:
        with self._lock_2:
            if hasattr(self, "scheduler") and scheduler_name in self._cache_instance:
                return

        self.scheduler_name = scheduler_name

        if is_backtesting():
            self.scheduler = BacktestScheduler()
        else:
            self.scheduler = BackgroundScheduler()

        custom_handler = CustomLogHandler()
        logger = logging.getLogger("apscheduler")
        logger.addHandler(custom_handler)

    def add_job(
        self,
        func: Callable,
        trigger: Literal["date", "interval", "cron"],
        id: str = None,
        **kwargs
    ) -> None:
        """
        添加定时任务
        
        Args:
            func: 定时任务函数
            trigger: 触发器
                date: 在某个确定的时间点运行你的 job (只运行一次)
                interval: 在固定的时间间隔周期性地运行你的 job
                cron: 在一天的某些固定时间点周期性地运行你的 job
            id: 任务 ID, 任意字符串
        Note:
            建议添加 id 参数, 指定任务 ID
        """

        self.scheduler.add_job(func=func, trigger=trigger, id=id, **kwargs)

    def get_job(self, job_id: str) -> Job:
        """
        根据 `job_id` 获取对应的定时任务

        Args:
            job_id: 任务 ID
        """

        return self.scheduler.get_job(job_id=job_id, jobstore=None)

    def get_jobs(self) -> list[Job]:
        """返回所有定时任务"""
        return self.scheduler.get_jobs()

    def remove_job(self, job_id: str) -> None:
        """
        根据 `job_id` 移除定时任务

        Args:
            job_id: 任务 ID
        """

        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id=job_id, jobstore=None)

    def start(self) -> None:
        """启动定时器"""
        if self.scheduler.running is False:
            self.scheduler.start()

    def stop(self) -> None:
        """停止定时器"""
        if self.scheduler_name in self._cache_instance:
            for job in self.get_jobs():
                job.remove()
            return

        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)


class KLineGeneratorSec(object):
    """秒级 K 线生成器

    Args:
        callback: 推送 K 线回调, 也可以是任何接受一根 K 线然后返回 None 的函数
        seconds: 合成秒数
    """

    def __init__(self, callback: Callable[[KLineData], None], seconds: int = 1) -> None:
        self.callback = callback
        self.seconds = seconds

        self.cache_kline: KLineData = None
        self.last_tick: TickData = None
        self.is_new: bool = True
        self.timekeeper: list[datetime] = []

    @property
    def seconds(self) -> int:
        return self._seconds

    @seconds.setter
    def seconds(self, value: int) -> None:
        if not isinstance(value, int):
            raise ValueError("秒数必须为 int 类型")
        self._seconds: int = value

    @property
    def first_time(self) -> datetime:
        """获取第一条 tick 的时间"""
        return self.timekeeper[0]

    @property
    def last_k_time(self) -> datetime:
        """获取上一条 K 线的时间"""
        return self.get_unique_sorted_timekeeper()[self.seconds - 1]

    def get_unique_sorted_timekeeper(self) -> list[datetime]:
        """对时间线去重"""
        return list(dict.fromkeys(self.timekeeper))

    @staticmethod
    def _ts(_datetime: datetime) -> int:
        """获取 datetime 对象的时间戳"""
        return int(_datetime.timestamp())

    def save_time(self, _time: datetime) -> None:
        """对时间去除毫秒数并保存至时间线"""
        self.timekeeper.append(_time.replace(microsecond=0))

    def fix_timeline(self, tick: TickData) -> None:
        """修复时间线中缺失的时间"""
        lost_seconds: int = self._ts(tick.datetime) - self._ts(self.last_tick.datetime)
        if (lost_ticks := (lost_seconds - 1)) > 0:
            # 如果少了 tick，则手动补全 timekeeper
            for j in range(lost_ticks, 0, -1):
                self.timekeeper.insert(-1, (tick.datetime - timedelta(seconds=j)).replace(microsecond=0))

    def new_kline_cycle(self, tick: TickData) -> bool:
        """判断该 tick 是否进入新的 K 线周期"""
        if not self.cache_kline:
            # 首次运行
            return False

        diff_seconds: int = self._ts(tick.datetime) - self._ts(self.first_time)

        self.fix_timeline(tick)

        if diff_seconds >= self.seconds:
            # 新 tick 时间和时间容器中第一根 tick 时间秒数对比
            # 如果大于等于设置的秒数，则表示进入新的 K 线周期
            # 然后要修复时间线，在把时间线中正确的时间赋予当前缓存 K 线
            # 最后把该 K 线时间之后的时间重新赋值给时间线，成为新的时间线

            self.cache_kline.update(datetime=self.last_k_time)

            self.timekeeper = self.get_unique_sorted_timekeeper()[self.seconds:]

            return True

    def tick_to_kline(self, tick: TickData) -> None:
        """合成秒级 K 线"""
        if self.is_new and tick.datetime.microsecond >= 500000:
            # 第一次运行，要毫秒数要小于 500ms，并且 self.seconds 能被 tick 的秒数整除
            return

        self.save_time(tick.datetime)

        if self.new_kline_cycle(tick):
            self.is_new = True
            self.callback(self.cache_kline)

        if self.is_new:
            self.is_new = False
            self.cache_kline = KLineData()

            self.cache_kline.update(
                open=tick.last_price,
                close=tick.last_price,
                high=tick.last_price,
                low=tick.last_price,
                datetime=tick.datetime,
                open_interest=tick.open_interest
            )
        else:
            self.cache_kline.update(
                close=tick.last_price,
                high=max(self.cache_kline.high, tick.last_price),
                low=min(self.cache_kline.low, tick.last_price),
                volume=self.cache_kline.volume + (tick.volume - self.last_tick.volume)
            )

        self.last_tick = tick


class KLineGenerator(object):
    """分钟级 K 线合成
    ----
    Args:
        callback: 推送 K 线回调, 也可以是任何接受一根 K 线然后返回 None 的函数
        exchange: 交易所代码
        instrument_id: 合约代码
        style: 合成 K 线周期, 默认 M1 即 1 分钟 K 线, 必须使用 KLineStyle 的枚举值
        real_time_callback: 实时推送 K 线回调, 推送频率和 tick 相同
    """

    def __init__(
        self,
        exchange: str,
        instrument_id: str,
        callback: Callable[[KLineData], None],
        style: KLineStyleType = KLineStyle.M1,
        real_time_callback: Callable[[KLineData], None] = None
    ) -> None:
        self.callback = callback
        self.exchange = exchange
        self.instrument_id = instrument_id
        self.style = style
        self.real_time_callback = real_time_callback

        self.scheduler = Scheduler("PythonGO")
        self.market_center = MarketCenter()
        self.producer = KLineProducer(
            exchange=self.exchange,
            instrument_id=self.instrument_id,
            style=style,
            callback=callback
        )

        self.close_time: list[str] = []
        self.next_gen_time: datetime = None

        self._first_run: bool = True
        self._is_new: bool = True
        self._lose_kline: bool = False
        self._cache_kline: KLineData = None
        self._last_tick: TickData = None
        self._min_last_tick: TickData = None
        self._min_last_volume: int = 0
        self._dirty_time: datetime = None
        self._kline_snapshot: dict = {}

        if not is_backtesting():
            """在实例化的时候就获取快照, 防止后续代码阻塞导致 tick 和快照错位"""
            self._kline_snapshot = self.get_kline_snapshot()

    @property
    def style(self) -> KLineStyleType:
        return self._style

    @style.setter
    def style(self, value: KLineStyleType) -> None:
        if value in KLineStyle.__members__:
            self._style: KLineStyleType = KLineStyle[value]
        elif isinstance(value, KLineStyle):
            self._style: KLineStyleType = value
        else:
            raise ValueError(f"合成分钟必须为 KLineStyle 的枚举值")

    def push_history_data(self) -> None:
        """推送历史 K 线数据"""
        self.producer.worker()

    def stop_push_scheduler(self) -> None:
        """停止定时器"""
        self.scheduler.stop()

    def _ts_to_datetime(self, ts: int, full_date: bool = False) -> datetime:
        """
        毫秒时间戳转时间类型, 默认去除秒和毫秒

        Args:
            ts: 毫秒时间戳
            full_date: 是否返回完整时间
        """
        _datetime = datetime.fromtimestamp(ts / 1000)
        if full_date:
            return _datetime
        return _datetime.replace(second=0, microsecond=0)

    def _init_kline(self, tick: TickData) -> None:
        """使用 K 线快照和第一个 tick 初始化第一根 K 线"""
        self._first_run = False

        if is_backtesting():
            return

        self._cache_kline = KLineData()

        if not (snapshot := self._kline_snapshot):
            return

        head_ts: int = snapshot["timestampHead"]
        tail_ts: int = snapshot["timestampTail"]
        tick_ts: int = int(tick.datetime.timestamp() * 1000)

        head_time = self._ts_to_datetime(head_ts)
        tail_time = self._ts_to_datetime(tail_ts)
        tick_time = tick.datetime.replace(second=0, microsecond=0)

        if tick.trading_day != snapshot["tradingDay"]:
            """tick 和快照交易日不同"""
            return

        self._is_new = False

        self._cache_kline.update(
            exchange=self.exchange,
            instrument_id=self.instrument_id,
            open=snapshot["openPrice"],
            high=snapshot["highestPrice"],
            low=snapshot["lowestPrice"],
            close=snapshot["closePrice"],
            volume=snapshot["volume"],
            open_interest=snapshot["openInterest"],
            datetime=self.next_gen_time
        )

        if head_time == tick_time:
            """tick 和快照在同一交易分钟"""
            self._min_last_volume = snapshot["totalVolume"] - snapshot["volume"]

            if (
                tick_ts < head_ts
                or head_ts < tick_ts < tail_ts
                or tick_ts == tail_ts
            ):
                """
                tick 在快照之前
                tick 在快照中间
                tick 是快照的最后一个 tick
                """
                if tick_ts < head_ts:
                    self._cache_kline.update(
                        open=tick.last_price,
                        high=max(self._cache_kline.high, tick.last_price),
                        low=min(self._cache_kline.low, tick.last_price)
                    )

                self._dirty_time = self._ts_to_datetime(tail_ts, full_date=True)
            elif tick_ts > tail_ts:
                """tick 在快照之后"""
                self._cache_kline.update(
                    high=max(self._cache_kline.high, tick.last_price),
                    low=min(self._cache_kline.low, tick.last_price),
                    close=tick.last_price,
                    volume=tick.volume - self._min_last_volume,
                    open_interest=tick.open_interest
                )
        elif tick_time < head_time:
            """
            tick 在快照之前, 不在同一交易分钟,
            需要丢掉快照之前的 tick, 所以要用快照的时间来获取下一根 K 线的时间,
            然后用总成交量减快照成交量得到上一分钟的成交量
            """
            self.next_gen_time = self.get_next_gen_time(tail_time)
            self._dirty_time = self._ts_to_datetime(tail_ts, full_date=True)
            self._min_last_volume = snapshot["totalVolume"] - snapshot["volume"]
        elif tail_time < tick_time:
            """
            tick 在快照之后，不在同一交易分钟,
            此时如果 `tick.volume == snapshot["totalVolume"]`,
            说明最新交易分钟没有发生成交, 需要把当 tick 设置为上一周期的最后一个 tick,
            以便后面根据成交量设置开盘价

            Note:
                目前默认当作没有成交的情况
            """
            self._min_last_tick = tick
            self._cache_kline.update(
                open=tick.last_price,
                high=tick.last_price,
                low=tick.last_price,
                close=tick.last_price,
                volume=0,
                open_interest=tick.open_interest
            )

    def get_next_gen_time(self, tick_time: datetime) -> None:
        """获取下一根 K 线合成时间"""
        return self.market_center.get_next_gen_time(
            exchange=self.exchange,
            instrument_id=self.instrument_id,
            tick_time=tick_time,
            style=self.style
        )

    def get_kline_snapshot(self) -> dict:
        """获取 K 线快照"""
        return self.market_center.get_kline_snapshot(
            exchange=self.exchange,
            instrument_id=self.instrument_id
        )

    def save_kline(self, data: list[dict]) -> None:
        """保存 K 线数据到 KLineContainer"""
        self.producer.kline_container.set(
            exchange=self.exchange,
            instrument_id=self.instrument_id,
            style=self.style,
            data=data
        )

    def _push_kline(self) -> None:
        """推送 K 线"""
        if not is_backtesting() and self._lose_kline:
            """缺少 K 线，需要在第一次推送的时候补上"""
            self._lose_kline = False

            if isinstance(self.producer.datetime[-1], datetime):
                kline_data = self.market_center.get_kline_data(
                    exchange=self.exchange,
                    instrument_id=self.instrument_id,
                    style=self.style,
                    start_time=self.producer.datetime[-1],
                    end_time=self.next_gen_time
                )

                for kline in kline_data:
                    if kline["datetime"] in self.producer.datetime:
                        continue

                    self.save_kline([kline])

                    kline_obj = KLineData({
                        **kline,
                        "exchange": self.exchange,
                        "instrument_id": self.instrument_id
                    })

                    self.producer.update(kline_obj)
                    self.callback(kline_obj)

        if self._cache_kline:
            """
            当合约成交量长时间没变化，在进入下一个周期时由于判断推送 K 线条件成立
            会导致缓存 K 线没有实例化，从而导致报错
            """

            self._cache_kline.update(
                volume=self._last_tick.volume - self._min_last_volume,
                datetime=self.next_gen_time
            )

            self.save_kline([self._cache_kline.to_json()])

            self.producer.update(self._cache_kline)
            self.callback(self._cache_kline)

        self._is_new = True
        self._min_last_tick = self._last_tick
        self._min_last_volume = self._last_tick.volume

    def tick_to_kline(self, tick: TickData, push: bool = False) -> None:
        """
        合成 K 线

        Args:
            tick: tick 对象
            push: 直接推送 K 线
        """

        if push:
            """定时推送, 以保证在收盘后能收到最后一根 K 线, 之后需要清空下一次的生成时间"""
            if self.next_gen_time == datetime.now().replace(second=0, microsecond=0):
                # TODO: 可能需要使用 `<=`
                self._push_kline()
                self.next_gen_time = None

            return

        if (
            tick.instrument_id != self.instrument_id
            or not tick.volume
            or (
                self._last_tick
                and self._last_tick.volume == tick.volume
            )
        ):
            """合约不对或没有成交量或当前成交量和上一个 tick 成交量相等"""
            if hasattr(self, "instruments") is False:
                """不是套利合约"""
                return

        if self._first_run:
            """首次开始合成, 用当前 tick 的成交量作为上一分钟最后一个 tick 的成交量"""
            self._min_last_volume = tick.volume

            if (tick.datetime.timestamp() - datetime.now().timestamp()) > 600:
                """tick 时间大于当前时间"""
                return

            self.next_gen_time = self.get_next_gen_time(tick.datetime)

            self._init_kline(tick)

            if not is_backtesting():
                if isinstance(self.producer.datetime[-1], datetime):
                    self._lose_kline = (
                        self.get_next_gen_time(self.producer.datetime[-1]) != self.next_gen_time
                    )
                    """判断是否缺失 K 线

                    使用历史数据的最后一个时间来生成下一根 K 线的时间,
                    然后和当前的正在合成的的 K 线时间做对比
                    """

                for run_date in self.market_center.get_avl_close_time(tick.instrument_id):
                    """添加推送任务"""
                    self.scheduler.add_job(
                        func=self.tick_to_kline,
                        trigger="date",
                        run_date=run_date + timedelta(seconds=2),
                        args=[None, True]
                    )

                if self.scheduler.get_jobs():
                    self.scheduler.start()

            self.close_time = self.market_center.get_close_time(tick.instrument_id)
            self._last_tick = tick

            return

        if self._dirty_time and tick.datetime < self._dirty_time:
            """脏数据"""
            return

        if not self.next_gen_time:
            """下一次生成时间为空, 说明上一个 tick 是在盘后收到的"""
            self.next_gen_time = self.get_next_gen_time(tick.datetime)
            if not self.next_gen_time:
                return
        
        if tick.datetime.replace(microsecond=0) >= self.next_gen_time:
            """tick 时间大于等于下一次生成时间则开始合成 K 线"""
            if tick.datetime.strftime("%X") not in self.close_time:
                """每个交易时段结束后的两个 tick 不驱动 K 线合成"""
                if tick.datetime.strftime("%H:00:00") != self.close_time[-1]:
                    """针对回测中的切交易日的情况，要等到下一个有效 tick 才做推送"""

                    self._push_kline()
                    self.next_gen_time = self.get_next_gen_time(tick.datetime)

                    if self._last_tick.trading_day != tick.trading_day:
                        """切换交易日需要将上一分钟的成交量置为 0"""
                        self._min_last_volume = 0

        if self._is_new:
            """新 K 线开始"""
            self._is_new = False
            self._cache_kline = KLineData()

            self._cache_kline.update(
                exchange=self.exchange,
                instrument_id=self.instrument_id,
                open=tick.last_price,
                high=tick.last_price,
                low=tick.last_price
            )
        else:
            self._cache_kline.update(
                high=max(self._cache_kline.high, tick.last_price),
                low=min(self._cache_kline.low, tick.last_price)
            )

        #: 由于切片 tick 的 `last_price` 可能不包含正确的最高价和最低价，所以需要判断

        if tick.high_price > self._last_tick.high_price:
            """当日最高价在当前周期有变动，优先使用当日最高价"""
            self._cache_kline.update(high=tick.high_price)

        if tick.low_price < self._last_tick.low_price:
            """当日最低价在当前周期有变动，优先使用当日最低价"""
            self._cache_kline.update(low=tick.low_price)

        if self._min_last_tick and self._min_last_tick.volume < tick.volume:
            """针对新的周期开始的几个 tick 没有发生成交，则等待有成交后重新设置开盘价"""
            if self._min_last_tick.trading_day == tick.trading_day:
                """必须为同一交易日才重新设置开盘价"""
                self._cache_kline.update(open=tick.last_price)

            self._min_last_tick = None

        self._cache_kline.update(
            close=tick.last_price,
            open_interest=tick.open_interest,
            volume=tick.volume - self._min_last_volume,
            datetime=self.next_gen_time
        )

        if callable(self.real_time_callback) and self.next_gen_time:
            """实时推送合成数据"""
            self.producer.update(self._cache_kline)
            self.real_time_callback(self._cache_kline)

        self._last_tick = tick


class KLineContainer(object):
    """
    K 线容器
    ----

    Args:
        exchange: 交易所代码
        instrument_id: 合约代码
        style: K 线周期
    """

    def __init__(
        self,
        exchange: str,
        instrument_id: str,
        style: KLineStyleType
    ) -> None:
        super().__init__()

        self.all_kline: dict[str, dict[str, dict[str, list[dict]]]] = {}

        self.market_center = MarketCenter()

        self.init(exchange, instrument_id, style)

    def get(self, exchange: str, instrument_id: str, style: KLineStyleType) -> list[dict]:
        """
        根据交易所, 合约和 K 线分钟获取缓存的 K 线

        Args:
            exchange: 交易所代码
            instrument_id: 合约代码
            style: K 线周期
        """

        if isinstance(style, KLineStyle):
            return self.all_kline.get(exchange, {}).get(instrument_id, {}).get(style.name, [])
        return []

    def set(
        self,
        exchange: str,
        instrument_id: str,
        style: KLineStyleType,
        data: list[dict]
    ) -> None:
        """
        根据交易所, 合约和 K 线分钟缓存 K 线

        Args:
            exchange: 交易所代码
            instrument_id: 合约代码
            style: K 线周期
            data: K 线数据
        """

        if isinstance(style, KLineStyle):
            self.all_kline.setdefault(exchange, {}).setdefault(
                instrument_id, {}).setdefault(style.name, []).extend(data)

    def init(self, exchange: str, instrument_id: str, style: KLineStyleType) -> None:
        """
        获取合约 K 线并缓存

        Args:
            exchange: 交易所代码
            instrument_id: 合约代码
            style: K 线周期
        """

        if is_backtesting():
            return

        if not all([exchange, instrument_id]):
            raise ValueError("交易所或合约代码为空")

        if not (data := self.market_center.get_kline_data(
            exchange=exchange,
            instrument_id=instrument_id,
            style=style
        )):
            raise ValueError(f"获取到空数据, 请检查交易所 {exchange} 或者合约代码 {instrument_id} 是否填写错误")

        self.set(
            exchange=exchange,
            instrument_id=instrument_id,
            style=style,
            data=data
        )


class KLineProducer(Indicators):
    """
    K 线生产器
    ----
        内置指标
        
    Args:
        exchange: 交易所代码
        instrument_id: 合约代码
        style: K 线周期
        callback: 推送 K 线回调
    """

    def __init__(
        self,
        exchange: str,
        instrument_id: str,
        style: KLineStyleType = "M1",
        callback: Callable[[KLineData], None] = None
    ) -> None:
        super().__init__()
        self.style = style
        self.exchange = exchange
        self.instrument_id = instrument_id
        self.callback = callback

        self.kline_container = KLineContainer(
            exchange=exchange,
            instrument_id=instrument_id,
            style=self.style
        )

        self._open = np.zeros(10)
        self._close = np.zeros(10)
        self._high = np.zeros(10)
        self._low = np.zeros(10)
        self._volume = np.zeros(10)
        self._datetime = np.arange(
            start="1999-11-20 00",
            stop="1999-11-20 10",
            dtype="datetime64[h]"
        )

    @property
    def style(self) -> KLineStyleType:
        return self._style

    @style.setter
    def style(self, value: KLineStyleType) -> None:
        if value in KLineStyle.__members__:
            self._style: KLineStyleType = KLineStyle[value]
        elif isinstance(value, KLineStyle):
            self._style: KLineStyleType = value
        else:
            raise ValueError(f"合成分钟必须为 KLineStyle 的枚举值")

    def _get_data(self) -> list[dict]:
        """根据 K 线类型获取对应的 K 线"""
        return self.kline_container.get(self.exchange, self.instrument_id, self.style)

    @property
    def open(self) -> list[np.float64]:
        """开盘价序列"""
        return self._open

    @open.setter
    def open(self, value: list[np.float64]) -> None:
        self._open = value

    @property
    def close(self) -> list[np.float64]:
        """收盘价序列"""
        return self._close

    @close.setter
    def close(self, value: list[np.float64]) -> None:
        self._close = value

    @property
    def high(self) -> list[np.float64]:
        """最高价序列"""
        return self._high

    @high.setter
    def high(self, value: list[np.float64]) -> None:
        self._high = value

    @property
    def low(self) -> list[np.float64]:
        """最低价序列"""
        return self._low

    @low.setter
    def low(self, value: list[np.float64]) -> None:
        self._low = value

    @property
    def volume(self) -> list[np.float64]:
        """成交量序列"""
        return self._volume

    @volume.setter
    def volume(self, value: list[np.float64]) -> None:
        self._volume = value

    @property
    def datetime(self) -> list[TypeDateTime]:
        """时间序列"""
        return self._datetime

    @datetime.setter
    def datetime(self, value: list[TypeDateTime]) -> None:
        self._datetime = value

    def update(self, kline: KLineData) -> None:
        """
        更新数据序列
        
        Args:
            kline: K 线对象
        """

        if self.datetime[-2] < kline.datetime < self.datetime[-1]:
            self.insert_data(kline)
        elif self.datetime[-1] != kline.datetime:
            self.append_data(kline)
        else:
            self.update_last_kline(kline)

    def append_data(self, kline: KLineData) -> None:
        """
        添加 K 线数据

        Args:
            kline: K 线对象
        """

        self.open = np.append(self.open, kline.open)
        self.close = np.append(self.close, kline.close)
        self.high = np.append(self.high, kline.high)
        self.low = np.append(self.low, kline.low)
        self.volume = np.append(self.volume, kline.volume)
        self.datetime = np.append(self.datetime, kline.datetime)

    def insert_data(self, kline: KLineData, index: int = -1) -> None:
        """
        插入 K 线数据

        Args:
            kline: K 线对象
            index: K 线插入的位置
        """

        self.open = np.insert(self.open, index, kline.open, axis=0)
        self.close = np.insert(self.close, index, kline.close, axis=0)
        self.high = np.insert(self.high, index, kline.high, axis=0)
        self.low = np.insert(self.low, index, kline.low, axis=0)
        self.volume = np.insert(self.volume, index, kline.volume, axis=0)
        self.datetime = np.insert(self.datetime, index, kline.datetime, axis=0)

    def update_last_kline(self, kline: KLineData) -> None:
        """
        更新最后一根 K 线数据

        Args:
            kline: K 线对象
        """

        self.open[-1] = kline.open
        self.close[-1] = kline.close
        self.high[-1] = kline.high
        self.low[-1] = kline.low
        self.volume[-1] = kline.volume
        self.datetime[-1] = kline.datetime

    def _push(self, kline: KLineData) -> None:
        """
        更新 K 线数组, 并推送历史 K 线

        Args:
            kline: K 线对象
        """

        self.update(kline)

        if callable(self.callback):
            """如果回调可用, 则使用回调"""
            self.callback(kline)

    def worker(self) -> None:
        """将 K 线数据转成 K 线对象后推送"""
        if not (data := self._get_data()):
            return

        for kline in data:
            if kline.get("open"):
                self._push(KLineData(
                    {
                        **kline,
                        "instrument_id": self.instrument_id,
                        "exchange": self.exchange
                    }
                ))


class KLineGeneratorArb(KLineGenerator):
    """标准套利合约的分钟级 K 线合成器"""

    def __init__(
        self,
        callback: Callable[[KLineData], None],
        exchange: str,
        instrument_id: str,
        style: KLineStyleType = KLineStyle.M1,
        real_time_callback: Callable[[KLineData], None] = None
    ) -> None:
        super().__init__(
            exchange=exchange,
            instrument_id=instrument_id,
            callback=callback,
            style=style,
            real_time_callback=real_time_callback
        )

        self.instruments: tuple[str] = split_arbitrage_code(self.instrument_id)
        self.tick_arbitrage: TickData = None
        self.tick_leg1: TickData = None
        self.tick_leg2: TickData = None

    def get_next_gen_time(self, tick_time: datetime) -> None:
        return self.market_center.get_next_gen_time(
            exchange=self.exchange,
            instrument_id=self.tick_leg1.instrument_id,
            tick_time=tick_time,
            style=self.style
        )

    def combine_tick(self) -> TickData:
        """组合 tick"""
        imply_bid_price1 = self.tick_leg1.bid_price1 - self.tick_leg2.ask_price1
        imply_ask_price1 = self.tick_leg1.ask_price1 - self.tick_leg2.bid_price1
        imply_bid_volume1 = min(self.tick_leg1.bid_volume1, self.tick_leg2.ask_volume1)
        imply_ask_volume1 =  min(self.tick_leg1.ask_volume1, self.tick_leg2.bid_volume1)

        if self.tick_arbitrage.bid_volume1:
            self.tick_arbitrage.imply_bid_price1 = max(imply_bid_price1, self.tick_arbitrage.bid_price1)
            self.tick_arbitrage.imply_bid_volume1 = (
                imply_bid_volume1 + self.tick_arbitrage.bid_volume1
                if imply_bid_price1 == self.tick_arbitrage.bid_price1
                else (
                    imply_bid_volume1
                    if imply_bid_price1 > self.tick_arbitrage.bid_price1
                    else self.tick_arbitrage.bid_volume1
                )
            )
        else:
            self.tick_arbitrage.imply_bid_price1 = imply_bid_price1
            self.tick_arbitrage.imply_bid_volume1 = imply_bid_volume1

        if self.tick_arbitrage.ask_volume1:
            self.tick_arbitrage.imply_ask_price1 = min(imply_ask_price1, self.tick_arbitrage.ask_price1)
            self.tick_arbitrage.imply_ask_volume1 = (
                imply_ask_volume1 + self.tick_arbitrage.ask_volume1
                if imply_ask_price1 == self.tick_arbitrage.ask_price1
                else (
                    imply_ask_volume1
                    if imply_ask_price1 < self.tick_arbitrage.ask_price1
                    else self.tick_arbitrage.ask_volume1
                )
            )
        else:
            self.tick_arbitrage.imply_ask_price1 = imply_ask_price1
            self.tick_arbitrage.imply_ask_volume1 = imply_ask_volume1

        self.tick_arbitrage.update(
            last_price=self.tick_leg1.last_price - self.tick_leg2.last_price,
            pre_settlement_price=self.tick_leg1.pre_settlement_price - self.tick_leg2.pre_settlement_price,
            pre_close_price=self.tick_leg1.pre_close_price - self.tick_leg2.pre_close_price,
            open_price=self.tick_leg1.open_price - self.tick_leg2.open_price
        )

        tick = self.tick_arbitrage.copy()

        tick.update(
            bid_price1=tick.imply_bid_price1,
            ask_price1=tick.imply_ask_price1,
            bid_volume1=tick.imply_bid_volume1,
            ask_volume1=tick.imply_ask_volume1
        )

        return tick

    def tick_to_kline(self, tick: TickData, push: bool = False) -> TickData | None:
        """合成套利 K 线"""
        if tick.instrument_id in self.instruments:
            _tick_index = self.instruments.index(tick.instrument_id)

            if _tick_index == 0:
                self.tick_leg1 = tick
            else:
                self.tick_leg2 = tick
        else:
            self.tick_arbitrage = tick

        if not self.tick_arbitrage:
            return

        if self.tick_leg1 and self.tick_leg2:
            new_tick = self.combine_tick()
            new_tick_time = max([
                self.tick_leg1.datetime,
                self.tick_leg2.datetime,
                self.tick_arbitrage.datetime
            ])
            new_tick.update(datetime=new_tick_time)
            super().tick_to_kline(new_tick, push)
            return new_tick


def isdigit(value: str) -> bool:
    """
    判断字符串是否整数或小数

    Args:
        value: 任意字符串
    """

    value: str = value.lstrip('-')

    if value.isdigit():
        return True

    if (
        value.count(".") == 1
        and not value.startswith(".")
        and not value.endswith(".")
        and value.replace(".", "").isdigit()
    ):
        return True

    return False

def deprecated(new_func_name: str, log_func: Callable[[str], None]) -> Callable:
    """函数弃用提示装饰器"""
    def decorator(func: Callable[[], Any]) -> Callable:
        def wrap_func(*args, **kwargs) -> Any:
            log_func(f"[函数弃用提示] {func.__name__} 方法即将在后续版本弃用, " +
                f"请尽快改用新方法: {new_func_name}, 具体使用方法请看官网文档说明")
            return func(*args, **kwargs)
        return wrap_func
    return decorator

def split_arbitrage_code(instrument_id: str) -> tuple[str | None, str | None]:
    """
    分割套利合约代码

    Args:
        instrument_id: 标准套利合约代码
    """

    pattern = re.compile(r"[a-zA-Z]+\s(\w+)&(\w+)")
    re_match = pattern.search(instrument_id)

    if re_match:
        return re_match.group(1), re_match.group(2)

    return None, None

def is_backtesting() -> bool:
    """判断是否回测环境"""
    return os.getenv("PYTHONGO_MODE") == "BACKTESTING"
